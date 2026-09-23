# app.py — Minimal MCP + Streamlit chat (correct tool message ordering, no filler rendered)

import os
import json
import asyncio
import streamlit as st
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

# ─────────────────────────────
# MCP servers: local math via uv + fastmcp
# ─────────────────────────────
SERVERS = {
    "math": {
        "transport": "stdio",
        "command": "C:/Users/anush/AppData/Local/Programs/Python/Python310/Scripts/uv.exe",
        "args": [
            "run",
            "--directory",
            "C:/Users/anush/OneDrive/Desktop/Math-Mcp-Server",
            "fastmcp",
            "run",
            "main.py",
        ],
    },
    "expense": {
    "transport": "stdio",
    "command": "C:/Users/anush/AppData/Local/Programs/Python/Python310/Scripts/uv.exe",
    "args": [
        "run",
        "--directory",
        "C:/Users/anush/OneDrive/Desktop/TestRemoteServer",
        "fastmcp",
        "run",
        "main.py",
    ],
    },
    "manim-server": {
            "transport": "stdio",
            "command": "C:/Users/anush/AppData/Local/Programs/Python/Python310/python.exe",
            "args": [
                "C:/Users/anush/OneDrive/Desktop/manim-mcp-server/src/manim_server.py"
            ],
            "env": {
                "MANIM_EXECUTABLE": "C:/Users/anush/AppData/Local/Programs/Python/Python310/Scripts/manim.exe"
            }
        }
}


SYSTEM_PROMPT = (
    "You have access to tools. When you choose to call a tool, do not narrate status updates. "
    "After tools run, return only a concise final answer."
)

st.set_page_config(page_title="MCP Chat", page_icon="🧰", layout="centered")
st.title("🧰 MCP Chat")

load_dotenv()

# Keep only normal message history in Streamlit state.
if "history" not in st.session_state:
    st.session_state.history = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]


def result_to_text(result):
    """Turn a tool result into text Gemini can read."""
    if isinstance(result, ToolMessage):
        result = result.content

    if isinstance(result, str):
        return result

    return json.dumps(result, default=str)


async def run_turn(history):
    # Create fresh async objects for this one Streamlit rerun.
    # Do NOT save these in st.session_state.
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    tool_by_name = {tool.name: tool for tool in tools}

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    llm_with_tools = llm.bind_tools(tools)

    # Let Gemini decide whether a tool is needed.
    first = await llm_with_tools.ainvoke(history)

    if not getattr(first, "tool_calls", None):
        return first, []

    # Run every tool Gemini requested.
    tool_messages = []

    for tool_call in first.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call.get("args") or {}

        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)

        result = await tool_by_name[tool_name].ainvoke(tool_args)

        tool_messages.append(
            ToolMessage(
                tool_call_id=tool_call["id"],
                content=result_to_text(result),
            )
        )

    # Give Gemini the tool outputs and request the final answer.
    final = await llm_with_tools.ainvoke(
        history + [first] + tool_messages
    )

    return final, [first] + tool_messages


# Display previous conversation.
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None):
        with st.chat_message("assistant"):
            st.markdown(msg.content)


user_text = st.chat_input("Type a message…")

if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)

    st.session_state.history.append(HumanMessage(content=user_text))

    # One asyncio.run call per user message.
    final, hidden_messages = asyncio.run(
        run_turn(st.session_state.history)
    )

    # Store hidden tool-call messages in the correct order.
    st.session_state.history.extend(hidden_messages)

    with st.chat_message("assistant"):
        st.markdown(final.content or "")

    st.session_state.history.append(final)