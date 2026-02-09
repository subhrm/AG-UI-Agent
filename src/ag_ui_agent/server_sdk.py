"""AG-UI protocol server implementation using ag-ui-langgraph SDK."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from .agent import create_agent
from .config import Config


# Initialize FastAPI app
app = FastAPI(
    title="AG-UI Agent Server",
    description="LangGraph agent server implementing the AG-UI protocol with ag-ui-langgraph SDK",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = None


class ChatMessage(BaseModel):
    """Chat message request model for simple endpoint."""
    message: str
    conversation_id: Optional[str] = None


class StateResponse(BaseModel):
    """Agent state response model."""
    status: str
    model: str
    temperature: float


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    global agent
    print("Initializing LangGraph agent...")
    agent = create_agent()
    print(f"✓ Agent initialized with model: {Config.OPENAI_MODEL}")
    
    # Add AG-UI protocol endpoint using the SDK
    add_langgraph_fastapi_endpoint(
        app=app,
        agent=agent,
        path="/api/run_agent",
        # Optional configuration can be added here
    )
    print("✓ AG-UI protocol endpoint added at /api/run_agent")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AG-UI Agent Server (ag-ui-langgraph SDK)",
        "version": "2.0.0",
        "status": "running",
        "protocol": "AG-UI",
        "endpoints": {
            "ag_ui": "POST /api/run_agent - Full AG-UI protocol endpoint",
            "simple_chat": "POST /api/chat - Simple chat endpoint",
            "stream": "GET /api/stream - Simple streaming endpoint",
            "state": "GET /api/state - Agent state",
            "health": "GET /health - Health check"
        }
    }


@app.get("/api/state")
async def get_state():
    """Get current agent state."""
    return StateResponse(
        status="ready",
        model=Config.OPENAI_MODEL,
        temperature=Config.TEMPERATURE
    )


@app.post("/api/chat")
async def chat(message: ChatMessage):
    """
    Process a chat message and return the complete response.
    
    This is a non-streaming endpoint for simple request-response interactions.
    """
    from .agent import run_agent
    
    try:
        response = run_agent(message.message, agent)
        return {
            "type": "message",
            "content": response,
            "metadata": {
                "conversation_id": message.conversation_id,
                "model": Config.OPENAI_MODEL
            }
        }
    except Exception as e:
        return {
            "type": "error",
            "content": str(e),
            "metadata": {}
        }


@app.get("/api/stream")
async def stream_chat(message: str):
    """
    Stream agent responses (legacy endpoint).
    
    For full AG-UI protocol support, use POST /api/run_agent instead.
    This endpoint provides simple streaming for basic use cases.
    """
    from fastapi.responses import StreamingResponse
    import json
    
    async def event_generator():
        """Generate SSE events from agent execution."""
        try:
            from .agent import stream_agent
            
            # Send initial state update
            yield f"event: state_update\ndata: {json.dumps({'type': 'state_update', 'content': 'processing', 'metadata': {'model': Config.OPENAI_MODEL}})}\n\n"
            
            current_tool = None
            message_content = []
            
            # Stream events from the agent
            async for event in stream_agent(message, agent):
                event_type = event.get("event")
                
                # Handle different event types
                if event_type == "on_chat_model_stream":
                    # Streaming content from the LLM
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        message_content.append(chunk.content)
                        yield f"event: message\ndata: {json.dumps({'type': 'message', 'content': chunk.content, 'metadata': {'streaming': True}})}\n\n"
                
                elif event_type == "on_tool_start":
                    # Tool execution started
                    tool_name = event.get("name", "unknown")
                    current_tool = tool_name
                    yield f"event: tool_start\ndata: {json.dumps({'type': 'tool_start', 'content': tool_name, 'metadata': {'tool_input': event.get('data', {}).get('input', {})}})}\n\n"
                
                elif event_type == "on_tool_end":
                    # Tool execution completed
                    tool_output = event.get("data", {}).get("output")
                    yield f"event: tool_end\ndata: {json.dumps({'type': 'tool_end', 'content': current_tool or 'unknown', 'metadata': {'tool_output': str(tool_output)[:500]}})}\n\n"
                    current_tool = None
            
            # Send completion state
            yield f"event: state_update\ndata: {json.dumps({'type': 'state_update', 'content': 'completed', 'metadata': {'full_response': ''.join(message_content)}})}\n\n"
            
        except Exception as e:
            # Send error event
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'content': str(e), 'metadata': {}})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "sdk": "ag-ui-langgraph v0.0.24",
        "agent": "initialized" if agent is not None else "not initialized"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )
