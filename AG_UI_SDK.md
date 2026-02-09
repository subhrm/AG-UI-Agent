# AG-UI SDK Integration

This document explains the AG-UI protocol SDK integration added to the project.

## Overview

The project now includes **two server implementations**:

1. **server.py** - Custom AG-UI implementation using FastAPI and SSE
2. **server_sdk.py** - Official `ag-ui-langgraph` SDK integration ✨ **Recommended**

## AG-UI LangGraph SDK

The `ag-ui-langgraph` package (v0.0.24) provides an official,standardized way to expose LangGraph agents via the AG-UI protocol.

### Key SDK Features

- **Automatic Event Streaming**: Lifecycle, text message, and tool call events
- **LangGraph Integration**: Deep integration with LangGraph state graphs
- **FastAPI Endpoint**: `add_langgraph_fastapi_endpoint()` function
- **Pydantic Models**: Type-safe event structures
- **State Synchronization**: Efficient state management

### Installation

```bash
uv add ag-ui-langgraph
```

This automatically installs:
- `ag-ui-langgraph==0.0.24`
- `ag-ui-protocol==0.1.10` (dependency)
- `langchain==1.2.9` (dependency)

## Using the SDK Server

### Start the Server

```bash
uv run uvicorn src.ag_ui_agent.server_sdk:app --reload
```

### SDK Endpoints

The SDK automatically registers the AG-UI protocol endpoint:

**POST /api/run_agent** - Full AG-UI protocol endpoint
- Accepts RunAgentInput with messages, tools, and context
- Streams AG-UI events via Server-Sent Events
- Handles lifecycle events, text streaming, tool calls, and state

**Additional Endpoints** (for convenience):
- `POST /api/chat` - Simple non-streaming chat
- `GET /api/stream` - Legacy streaming endpoint
- `GET /api/state` - Agent state information
- `GET /health` - Health check

## AG-UI Protocol Events

The SDK automatically emits standardized events:

### Lifecycle Events
- `RunStarted` - Agent execution begins
- `RunFinished` - Agent execution completes
- `StepStarted` - Agent step begins
- `StepFinished` - Agent step completes

### Text Message Events
- `TextMessageStart` - Text generation begins
- `TextMessageContent` - Text content chunk
- `TextMessageEnd` - Text generation ends

### Tool Call Events
- `ToolCallStart` - Tool execution begins
- `ToolCallArgs` - Tool arguments
- `ToolCallEnd` - Tool execution completes

### State Management
- `StateSnapshot` - Complete state at a point in time
- `StateDelta` - Incremental state updates (JSON Patch)
- `MessagesSnapshot` - Message history

## Implementation Details

### SDK Integration Code

```python
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from .agent import create_agent

# Create LangGraph agent
agent = create_agent()

# Add AG-UI endpoint using SDK
add_langgraph_fastapi_endpoint(
    app=app,
    agent=agent,
    path="/api/run_agent"
)
```

That's it! The SDK handles all event generation, streaming, and protocol compliance.

### Advantages Over Custom Implementation

| Feature | Custom (server.py) | SDK (server_sdk.py) |
|---------|-------------------|---------------------|
| Protocol Compliance | Manual | Automatic ✅ |
| Event Types | Limited | Full AG-UI spec ✅ |
| State Management | Basic | Advanced with deltas ✅ |
| Maintenance | Manual updates | SDK updates ✅ |
| Type Safety | Partial | Full Pydantic models ✅ |
| LangGraph Integration | Basic | Deep integration ✅ |

## Frontend Integration

The SDK-based server is fully compatible with AG-UI frontend libraries:

### JavaScript/TypeScript Example

```javascript
// Using EventSource for SSE
const response = await fetch('http://localhost:8000/api/run_agent', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Your question here' }],
    tools: []
  })
});

const eventSource = new EventSource(response.url);

eventSource.addEventListener('TextMessageContent', (event) => {
  const data = JSON.parse(event.data);
  console.log('Content:', data.content);
});

eventSource.addEventListener('ToolCallStart', (event) => {
  const data = JSON.parse(event.data);
  console.log('Tool started:', data.tool_name);
});
```

### CopilotKit Integration

```typescript
import { CopilotKit } from "@copilotkit/react-core";

<CopilotKit runtimeUrl="http://localhost:8000/api/run_agent">
  <YourApp />
</CopilotKit>
```

## Testing the SDK Integration

### curl Example

```bash
curl -X POST http://localhost:8000/api/run_agent \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is LangGraph?"}],
    "tools": []
  }'
```

### Python Example

```python
import httpx

async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "http://localhost:8000/api/run_agent",
        json={
            "messages": [{"role": "user", "content": "Latest AI news"}],
            "tools": []
        }
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
                print(f"Event: {event_type}")
```

## Migration from Custom Server

To migrate from `server.py` to `server_sdk.py`:

1. Update your startup command:
   ```bash
   # Old
   uv run uvicorn src.ag_ui_agent.server:app --reload
   
   # New
   uv run uvicorn src.ag_ui_agent.server_sdk:app --reload
   ```

2. Update frontend endpoint (if using full protocol):
   ```javascript
   // No change needed - same endpoint path
   POST /api/run_agent
   ```

3. That's it! The SDK maintains API compatibility.

## Resources

- [AG-UI Protocol Specification](https://ag-ui.com)
- [ag-ui-langgraph PyPI](https://pypi.org/project/ag-ui-langgraph/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Example Projects](https://github.com/TheGreatBonnie/open-ag-ui-langgraph)

## Which Server Should You Use?

**Use `server_sdk.py` if:**
- You want official protocol compliance ✅
- You need full AG-UI event types ✅
- You're integrating with AG-UI frontends ✅
- You want automatic SDK updates ✅

**Use `server.py` if:**
- You need custom event handling
- You want to understand the protocol details
- You have specific customization needs

**Recommendation**: Start with `server_sdk.py` for production use.
