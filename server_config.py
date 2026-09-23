"""Local paths and launch commands for the bundled MCP servers."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SERVERS_DIR = ROOT / "servers"


def _stdio(directory: Path, *command: str) -> dict:
    return {
        "transport": "stdio",
        "command": "uv",
        "args": ["run", "--directory", str(directory), *command],
    }


SERVERS = {
    "math": _stdio(SERVERS_DIR / "math", "fastmcp", "run", "main.py"),
    "expense": _stdio(SERVERS_DIR / "expense", "fastmcp", "run", "main.py"),
    "manim-server": {
        **_stdio(SERVERS_DIR / "manim", "python", "src/manim_server.py"),
        "env": {"MANIM_EXECUTABLE": "manim"},
    },
}
