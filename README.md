A Python MCP client with a Streamlit chat interface. It connects to local MCP servers for math and expense tools, plus a Manim server, and uses Google Gemini to choose and call tools from natural-language requests.

The client repository does not include the MCP server implementations. The server projects must be installed separately and the paths in the client configuration must be updated for your computer.

## Features

- Chat interface built with Streamlit (client2.py)
- Gemini-powered tool selection
- Connects to MCP servers over standard input/output (stdio)
- Math tools: addition, subtraction, multiplication, division, power, and modulo (provided by the configured math server)
- Expense tracking (provided by the configured expense server)
- Manim operations (provided by the configured Manim server)
- A command-line example (client1.py) that sends a sample Manim request

## Requirements

- Windows (the current server configuration uses Windows paths)
- Python 3.12 or newer
- uv
- A Google Gemini API key
- The math, expense, and Manim MCP server projects, installed and runnable locally

## Setup

1. Clone this repository and open a terminal in its folder.

   ```powershell
   git clone https://github.com/<your-github-username>/Multi-Tool-MCP-Server.git
   cd Multi-Tool-MCP-Server
   ```

2. Create and activate a virtual environment, then install the project dependencies and Google Generative AI integration.

   ```powershell
   uv venv
   .\.venv\Scripts\Activate.ps1
   uv pip install -e . langchain-google-genai
   ```

3. Create a `.env` file in the repository root and add your Gemini API key using the variable name  `ChatGoogleGenerativeAI` (commonly `GOOGLE_API_KEY`). 

4. Install or clone the math, expense, and Manim MCP server projects separately. In both `client1.py` and `client2.py`, update the `SERVERS` configuration with the correct local paths to each server's Python/uv executable, project directory, entry point, and—if needed—the Manim executable.

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

The available tools depend on the server implementations installed on your machine.
