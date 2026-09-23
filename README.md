# Multi-Tool MCP Server

A Python MCP client with a Streamlit chat interface. Google Gemini can choose and call tools from the bundled math, expense tracker, and Manim MCP servers.

The client launches the bundled server projects from `servers/` using the shared configuration in `server_config.py`.

## Features

- Chat interface built with Streamlit (client2.py)
- Gemini-powered tool selection
- Connects to MCP servers over standard input/output (stdio)
- Math tools: addition, subtraction, multiplication, division, power, and modulo
- Expense tracking: add, list, summarize, and delete expenses
- Manim operations: start a render and check its status
- A command-line example (client1.py) that sends a sample Manim request

## Requirements

- Windows
- Python 3.12 or newer
- uv
- A Google Gemini API key
- Manim's platform prerequisites for rendering animations

## Setup

1. Clone this repository and open a terminal in its folder.

   ```powershell
   git clone https://github.com/Anushka2670/Multi-Tool-MCP-Server.git
   cd Multi-Tool-MCP-Server
   ```

2. Create and activate a virtual environment, then install the client dependencies.

   ```powershell
   uv venv
   .\.venv\Scripts\Activate.ps1
   uv pip install langchain langchain-mcp-adapters langchain-google-genai python-dotenv streamlit
   ```

3. Create a `.env` file in the repository root with your Gemini API key:

   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

   Keep `.env` private; it is excluded by `.gitignore`.

4. Keep `uv` available on your PATH. On first use, `uv run` prepares the environment for each bundled server from its `pyproject.toml`.

5. Start the Streamlit chat interface:

   ```powershell
   streamlit run client2.py
   ```

   To run the command-line Manim example instead:

   ```powershell
   python client1.py
   ```

## Configured MCP servers

|     Server     |                            Purpose                                   |
|----------------|----------------------------------------------------------------------|
| `math`         | Arithmetic tools: add, subtract, multiply, divide, power, and modulo |
| `expense`      | Expense tracking tools                                               |
| `manim-server` | Manim-powered animation operations                                   |

The expense server creates `servers/expense/expense.db` locally. The database and Manim render output are excluded by `.gitignore`.

The Manim server's license and attribution are included in `servers/manim/LICENSE.txt` and `servers/manim/README.md`.
