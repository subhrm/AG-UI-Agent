#!/usr/bin/env python3
"""
Example script demonstrating the AG-UI agent.

This script shows how to use the agent both synchronously and with streaming.
Before running, make sure you have set up your .env file with API keys.
"""
import asyncio
from src.ag_ui_agent import create_agent, run_agent, stream_agent


def example_sync():
    """Example of synchronous agent usage."""
    print("=" * 60)
    print("SYNCHRONOUS AGENT EXAMPLE")
    print("=" * 60)
    
    # Create the agent
    print("\n1. Creating agent...")
    agent = create_agent()
    print("✓ Agent created successfully")
    
    # Ask a simple question (no search needed)
    print("\n2. Asking a simple question...")
    question1 = "What is Python?"
    print(f"   Question: {question1}")
    response1 = run_agent(question1, agent)
    print(f"   Response: {response1[:200]}...")
    
    # Ask a question that requires web search
    print("\n3. Asking a question requiring web search...")
    question2 = "What are the latest developments in AI this week?"
    print(f"   Question: {question2}")
    response2 = run_agent(question2, agent)
    print(f"   Response: {response2[:200]}...")
    
    print("\n" + "=" * 60)


async def example_stream():
    """Example of streaming agent usage."""
    print("\n" + "=" * 60)
    print("STREAMING AGENT EXAMPLE")
    print("=" * 60)
    
    question = "Explain quantum computing in simple terms"
    print(f"\nQuestion: {question}")
    print("\nStreaming response events:")
    print("-" * 60)
    
    event_count = 0
    async for event in stream_agent(question):
        event_type = event.get("event")
        
        # Only show interesting events (not all internal events)
        if event_type in ["on_chat_model_start", "on_chat_model_stream", "on_tool_start", "on_tool_end"]:
            event_count += 1
            
            if event_type == "on_chat_model_start":
                print("🤖 LLM started processing...")
            
            elif event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    print(f"   {chunk.content}", end="", flush=True)
            
            elif event_type == "on_tool_start":
                tool_name = event.get("name", "unknown")
                print(f"\n\n🔧 Tool started: {tool_name}")
            
            elif event_type == "on_tool_end":
                print("✓ Tool completed")
        
        # Limit to prevent too much output in example
        if event_count > 50:
            print("\n\n... (output truncated for example)")
            break
    
    print("\n" + "=" * 60)


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AG-UI AGENT EXAMPLES")
    print("=" * 60)
    
    try:
        # Run synchronous example
        example_sync()
        
        # Run streaming example
        await example_stream()
        
        print("\n✅ All examples completed successfully!")
        print("\nNext steps:")
        print("  1. Start the server: uv run uvicorn src.ag_ui_agent.server:app --reload")
        print("  2. Test endpoints with curl (see README.md)")
        print("  3. Integrate with your frontend using AG-UI protocol")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Created .env file with API keys")
        print("  2. Set OPENAI_API_KEY and TAVILY_API_KEY")
        print("\nSee .env.example for template")


if __name__ == "__main__":
    asyncio.run(main())
