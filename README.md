# AG-UI-Agent

A Python-based AI agent built with LangGraph that uses OpenAI's API and web search capabilities to answer user questions. The agent implements the [AG-UI (Agent-User Interaction) protocol](https://ag-ui.com) for standardized communication with frontend applications.

**Two Server Options:**
- **server.py** - Custom AG-UI implementation with Server-Sent Events
- **server_sdk.py** - Official `ag-ui-langgraph` SDK integration

## Features

- 🤖 **LangGraph Agent**: Sophisticated agent workflow with tool execution
- 🔍 **Web Search**: Real-time web search using Tavily API
- 🌊 **Streaming Responses**: Server-Sent Events (SSE) for real-time updates
- 🎯 **AG-UI Protocol**: Standardized agent-to-UI communication
- ⚡ **FastAPI Server**: High-performance async API server
- 🛠️ **Tool Execution**: Transparent tool usage with status updates

## Architecture

The agent follows a LangGraph workflow:

1. **Receive Question** → User sends a question via HTTP/SSE
2. **LLM Analysis** → OpenAI model determines if web search is needed
3. **Tool Execution** → If needed, executes Tavily web search
4. **Response Generation** → LLM generates final answer using search results
5. **Stream Events** → AG-UI protocol events sent to client

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- Tavily API key

### Setup

1. **Clone the repository**:
   ```bash
   cd /Users/subhendu/dev/AG-UI-Agent
   ```

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=sk-...
   TAVILY_API_KEY=tvly-...
   ```

### Getting API Keys

- **OpenAI**: Get your API key from [platform.openai.com](https://platform.openai.com/api-keys)
- **Tavily**: Sign up at [tavily.com](https://tavily.com) to get your API key

## Usage

### Starting the Server

**Option 1: Using AG-UI SDK (Recommended)**
```bash
uv run uvicorn src.ag_ui_agent.server_sdk:app --reload
```

**Option 2: Custom Implementation**
```bash
uv run uvicorn src.ag_ui_agent.server:app --reload
```

The server will start at `http://localhost:8000`

### API Endpoints

#### 1. **Non-Streaming Chat** (`POST /api/chat`)

Simple request-response interaction:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is LangGraph?"}'
```

Response:
```json
{
  "type": "message",
  "content": "LangGraph is a library for building stateful...",
  "metadata": {
    "model": "gpt-4o-mini"
  }
}
```

#### 2. **Streaming Chat** (`GET /api/stream`)

Real-time streaming with SSE:

```bash
curl -N "http://localhost:8000/api/stream?message=What%20is%20the%20latest%20news%20about%20AI?"
```

Events streamed:
- `state_update`: Agent status changes
- `tool_start`: Tool execution begins
- `tool_end`: Tool execution completes
- `message`: Content chunks from LLM
- `error`: Error information

#### 3. **Health Check** (`GET /health`)

```bash
curl http://localhost:8000/health
```

#### 4. **Agent State** (`GET /api/state`)

```bash
curl http://localhost:8000/api/state
```

### Using as a Python Library

```python
from src.ag_ui_agent import create_agent, run_agent

# Create the agent
agent = create_agent()

# Ask a question
response = run_agent("What is quantum computing?", agent)
print(response)
```

### Streaming Example

```python
import asyncio
from src.ag_ui_agent import stream_agent

async def main():
    async for event in stream_agent("Latest news on AI"):
        print(event)

asyncio.run(main())
```

## AG-UI Protocol

The server implements the AG-UI protocol with the following event types:

### Event Format

```json
{
  "event": "message|tool_start|tool_end|state_update|error",
  "data": {
    "type": "...",
    "content": "...",
    "metadata": {...}
  }
}
```

### Event Types

| Event | Description |
|-------|-------------|
| `state_update` | Agent state changed (processing, completed) |
| `tool_start` | Tool execution started |
| `tool_end` | Tool execution completed |
| `message` | Content chunk from LLM |
| `error` | Error occurred |

## Configuration

Environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | *Required* |
| `TAVILY_API_KEY` | Tavily API key | *Required* |
| `OPENAI_ENDPOINT` | OpenAI API endpoint (for custom/local LLMs) | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `TEMPERATURE` | LLM temperature | `0.7` |
| `MAX_TOKENS` | Max tokens per response | `2000` |
| `TAVILY_MAX_RESULTS` | Max search results | `5` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## Testing

Run the test suite:

```bash
uv run pytest tests/ -v
```

Add pytest to dev dependencies:

```bash
uv add --dev pytest pytest-asyncio
```

## Project Structure

```
AG-UI-Agent/
├── src/ag_ui_agent/
│   ├── __init__.py      # Package exports
│   ├── config.py        # Configuration management
│   ├── tools.py         # Web search tool (Tavily)
│   ├── agent.py         # LangGraph agent
│   └── server.py        # FastAPI AG-UI server
├── tests/
│   ├── __init__.py
│   └── test_agent.py    # Unit tests
├── .env.example         # Environment template
├── pyproject.toml       # Dependencies
└── README.md
```

## Development

### Add Dependencies

```bash
uv add package-name
```

### Add Dev Dependencies

```bash
uv add --dev package-name
```

### Run in Development Mode

```bash
uv run uvicorn src.ag_ui_agent.server:app --reload --log-level debug
```

## Example Interactions

### Question Requiring Web Search

```bash
curl -N "http://localhost:8000/api/stream?message=What%20happened%20today%20in%20AI?"
```

The agent will:
1. Recognize it needs current information
2. Execute `web_search` tool
3. Receive search results from Tavily
4. Generate a comprehensive answer using the search results

### Simple Question (No Search Needed)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}'
```

The agent will directly answer from its knowledge without using tools.

## Troubleshooting

### API Key Errors

If you see "Configuration errors", ensure your `.env` file has valid API keys:

```bash
cat .env
# Should show OPENAI_API_KEY and TAVILY_API_KEY
```

### Port Already in Use

Change the port in `.env` or run with a different port:

```bash
uv run uvicorn src.ag_ui_agent.server:app --port 8001
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AG-UI Protocol Specification](https://ag-ui.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Tavily API Documentation](https://docs.tavily.com)

