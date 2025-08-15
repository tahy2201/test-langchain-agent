# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangChain CLI Agent that uses Claude-3.5-Haiku and AWS Bedrock Agent Core to provide an interactive AI assistant with various tools.

## Dependencies and Environment

### Python Environment
- Uses `uv` for dependency management (lock file: `uv.lock`)
- Requires Python >= 3.12
- Main dependencies: langchain, langchain-anthropic, langchain-community, python-dotenv, anthropic, bedrock-agentcore

### Environment Variables
Required environment variables (should be set in `.env` file):
- `ANTHROPIC_API_KEY`: Claude API key (required)
- `AWS_ACCESS_KEY_ID`: AWS access key (required for Python code execution)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (required for Python code execution)

### Running the Application
```bash
# Run the main application
python src/main.py

# Or as a module
python -m src.main
```

### Installation
```bash
# Using uv (preferred)
uv add langchain langchain-anthropic langchain-community python-dotenv anthropic

# Using pip
pip install langchain langchain-anthropic langchain-community python-dotenv anthropic
```

## Architecture

### Core Components

1. **LangChainCLIAgent** (`src/main.py:25`): Main agent class that handles the chat interface and orchestrates tools
   - Uses Claude-3.5-Haiku as the LLM (`src/main.py:43`)
   - Implements interactive CLI session with chat history
   - Handles tool calling through LangChain's AgentExecutor

2. **Tools System** (`src/tools.py`): Collection of LangChain tools:
   - `get_weather_info`: Mock weather data retrieval
   - `calculate_math_expression`: Safe mathematical calculations using restricted eval
   - `create_todo_item`: JSON-based TODO management (saves to `todo_list.json`)
   - `execute_python_code`: AWS Code Interpreter integration for secure Python execution

3. **AWS Code Interpreter Integration** (`src/hello_world_sdk.py`): Demonstrates AWS Bedrock Agent Core usage
   - Uses `bedrock_agentcore.tools.code_interpreter_client.CodeInterpreter`
   - Region: us-west-2
   - Handles streaming responses and cleanup

### Agent Prompt Structure
The agent uses a system prompt that:
- Identifies as a helpful AI assistant
- Lists available tools (weather, math, TODO, Python execution)
- Responds in Japanese
- Uses LangChain's MessagesPlaceholder for chat history and agent scratchpad

### Tool Patterns
- All tools use the `@tool` decorator from langchain.tools
- Tools return structured string responses
- Error handling is built into each tool
- Math calculations use restricted eval with safe functions only
- Python code execution includes AWS credential validation

## Common Development Tasks

No specific build, test, or lint scripts are configured in this project. The application runs directly with Python.

## Important Implementation Notes

- The weather tool uses mock data (not real weather API)
- Math calculations are restricted to safe functions (math module functions, basic operators)
- TODO items are persisted in `todo_list.json` with timestamp-based IDs
- AWS Code Interpreter requires proper AWS credentials and uses streaming responses
- All tool responses are designed to be human-readable in Japanese
- The agent maintains chat history across the session but not between sessions