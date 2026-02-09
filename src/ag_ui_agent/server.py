"""AG-UI protocol server implementation."""
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from .agent import create_agent, stream_agent
from .config import Config


# Initialize FastAPI app
app = FastAPI(
    title="AG-UI Agent Server",
    description="LangGraph agent server implementing the AG-UI protocol",
    version="1.0.0"
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
    """Chat message request model."""
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
    print(f"Agent initialized with model: {Config.OPENAI_MODEL}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AG-UI Agent Server",
        "version": "1.0.0",
        "status": "running"
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
    Stream agent responses using Server-Sent Events (SSE).
    
    This endpoint implements the AG-UI protocol for streaming responses.
    Events include:
    - message: Content chunks from the agent
    - tool_start: Tool execution started
    - tool_end: Tool execution completed
    - state_update: Agent state changes
    """
    async def event_generator():
        """Generate SSE events from agent execution."""
        try:
            # Send initial state update
            yield {
                "event": "state_update",
                "data": json.dumps({
                    "type": "state_update",
                    "content": "processing",
                    "metadata": {"model": Config.OPENAI_MODEL}
                })
            }
            
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
                        yield {
                            "event": "message",
                            "data": json.dumps({
                                "type": "message",
                                "content": chunk.content,
                                "metadata": {"streaming": True}
                            })
                        }
                
                elif event_type == "on_tool_start":
                    # Tool execution started
                    tool_name = event.get("name", "unknown")
                    current_tool = tool_name
                    yield {
                        "event": "tool_start",
                        "data": json.dumps({
                            "type": "tool_start",
                            "content": tool_name,
                            "metadata": {
                                "tool_input": event.get("data", {}).get("input", {})
                            }
                        })
                    }
                
                elif event_type == "on_tool_end":
                    # Tool execution completed
                    tool_output = event.get("data", {}).get("output")
                    yield {
                        "event": "tool_end",
                        "data": json.dumps({
                            "type": "tool_end",
                            "content": current_tool or "unknown",
                            "metadata": {
                                "tool_output": str(tool_output)[:500]  # Truncate for brevity
                            }
                        })
                    }
                    current_tool = None
            
            # Send completion state
            yield {
                "event": "state_update",
                "data": json.dumps({
                    "type": "state_update",
                    "content": "completed",
                    "metadata": {
                        "full_response": "".join(message_content)
                    }
                })
            }
            
        except Exception as e:
            # Send error event
            yield {
                "event": "error",
                "data": json.dumps({
                    "type": "error",
                    "content": str(e),
                    "metadata": {}
                })
            }
    
    return EventSourceResponse(event_generator())


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )
