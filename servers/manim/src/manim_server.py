import os
import glob
import uuid
import threading
import time
import subprocess

from mcp.server.fastmcp import FastMCP


mcp = FastMCP()

MANIM_EXECUTABLE = os.getenv("MANIM_EXECUTABLE", "manim")

BASE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "media"
)

os.makedirs(BASE_DIR, exist_ok=True)


# Store information about running/completed Manim jobs
JOBS = {}
JOBS_LOCK = threading.Lock()


def _run_job(job_id: str, manim_code: str, tmpdir: str):
    """Run Manim in the background."""

    script_path = os.path.join(tmpdir, "scene.py")

    try:
        # Write the Manim code to scene.py
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(manim_code)

        # Run Manim
        result = subprocess.run(
            [
                MANIM_EXECUTABLE,
                "-ql",
                script_path
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=600,
        )

        # Find generated MP4 file
        video_path = None

        if result.returncode == 0:
            matches = glob.glob(
                os.path.join(
                    tmpdir,
                    "media",
                    "videos",
                    "**",
                    "*.mp4"
                ),
                recursive=True
            )

            if matches:
                video_path = max(
                    matches,
                    key=os.path.getmtime
                )

        # Update job information
        with JOBS_LOCK:
            JOBS[job_id].update(
                status="success" if result.returncode == 0 else "failed",
                returncode=result.returncode,
                stdout=result.stdout[-4000:],
                stderr=result.stderr[-4000:],
                finished_at=time.time(),
                video_path=video_path,
            )

    except subprocess.TimeoutExpired as e:

        with JOBS_LOCK:
            JOBS[job_id].update(
                status="failed",
                returncode=-1,
                stdout=str(e.stdout)[-4000:] if e.stdout else "",
                stderr="Manim process timed out after 600 seconds.",
                finished_at=time.time(),
                video_path=None,
            )

    except Exception as e:

        with JOBS_LOCK:
            JOBS[job_id].update(
                status="failed",
                returncode=-1,
                stdout="",
                stderr=str(e),
                finished_at=time.time(),
                video_path=None,
            )


@mcp.tool()
def execute_manim_code(manim_code: str) -> str:
    """
    Start a Manim rendering job in the background.

    Returns a job ID that can be used with check_manim_job().
    """

    # Create a unique job ID
    job_id = uuid.uuid4().hex[:8]

    # Give every job its own directory
    tmpdir = os.path.join(
        BASE_DIR,
        f"manim_tmp_{job_id}"
    )

    os.makedirs(tmpdir, exist_ok=True)

    # Register the job
    with JOBS_LOCK:
        JOBS[job_id] = {
            "status": "running",
            "tmpdir": tmpdir,
            "started_at": time.time(),
            "video_path": None,
        }

    # Start Manim in a background thread
    thread = threading.Thread(
        target=_run_job,
        args=(job_id, manim_code, tmpdir),
        daemon=True,
    )

    thread.start()

    # Return immediately to Claude
    return (
        f"Job started. job_id={job_id}\n"
        f"Output directory: {tmpdir}\n"
        f"Call check_manim_job('{job_id}') to check the status."
    )


@mcp.tool()
def check_manim_job(job_id: str) -> str:
    """
    Check the status of a Manim rendering job.
    """

    with JOBS_LOCK:
        job = JOBS.get(job_id)

    if not job:
        return f"No job found with id: {job_id}"

    # Still rendering
    if job["status"] == "running":

        elapsed = int(
            time.time() - job["started_at"]
        )

        return (
            f"Job {job_id} is still running "
            f"({elapsed}s elapsed)."
        )

    # Successfully completed
    if job["status"] == "success":

        if job.get("video_path"):

            return (
                f"Job {job_id} succeeded.\n"
                f"VIDEO_FILE: {job['video_path']}"
            )

        return (
            f"Job {job_id} succeeded, "
            f"but no .mp4 file was found.\n"
            f"Output directory: {job['tmpdir']}"
        )

    # Failed
    return (
        f"Job {job_id} failed "
        f"(exit code {job['returncode']}).\n"
        f"STDERR:\n{job['stderr']}\n"
        f"STDOUT:\n{job['stdout']}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")