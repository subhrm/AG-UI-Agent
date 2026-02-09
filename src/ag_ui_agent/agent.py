"""LangGraph agent implementation."""
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from .config import Config
from .tools import TOOLS


# Define the state for our graph
class State(TypedDict):
    """State of the agent conversation."""
    messages: Annotated[list, add_messages]


def create_agent():
    """
    Create and return a LangGraph agent with web search capabilities.
    
    The agent follows this workflow:
    1. Receives user message
    2. LLM decides whether to use tools (web search) or respond directly
    3. If tools are needed, execute them
    4. Generate final response using LLM
    
    Returns:
        Compiled LangGraph agent
    """
    # Initialize the LLM with tools
    llm = ChatOpenAI(
        model=Config.OPENAI_MODEL,
        temperature=Config.TEMPERATURE,
        max_tokens=Config.MAX_TOKENS,
        api_key=Config.OPENAI_API_KEY,
        base_url=Config.OPENAI_ENDPOINT,
        streaming=True,
    )
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(TOOLS)
    
    # Define the agent node
    def agent(state: State):
        """Agent node that calls the LLM."""
        return {"messages": [llm_with_tools.invoke(state["messages"])]}
    
    # Create the graph
    graph_builder = StateGraph(State)
    
    # Add nodes
    graph_builder.add_node("agent", agent)
    graph_builder.add_node("tools", ToolNode(TOOLS))
    
    # Add edges
    graph_builder.add_edge(START, "agent")
    
    # Add conditional edges
    # After the agent node, either:
    # 1. Go to tools if the agent wants to use a tool
    # 2. End if the agent has a final response
    graph_builder.add_conditional_edges(
        "agent",
        tools_condition,
    )
    
    # After tools are executed, always go back to the agent
    graph_builder.add_edge("tools", "agent")
    
    # Compile the graph
    return graph_builder.compile()


def run_agent(question: str, agent=None):
    """
    Run the agent with a given question.
    
    Args:
        question: The user's question
        agent: Optional pre-compiled agent (will create if not provided)
        
    Returns:
        The agent's response
    """
    if agent is None:
        agent = create_agent()
    
    # Run the agent
    result = agent.invoke({
        "messages": [("user", question)]
    })
    
    # Extract the final message
    if result and "messages" in result:
        final_message = result["messages"][-1]
        return final_message.content if hasattr(final_message, "content") else str(final_message)
    
    return "No response generated"


async def stream_agent(question: str, agent=None):
    """
    Stream the agent's response for a given question.
    
    Args:
        question: The user's question
        agent: Optional pre-compiled agent (will create if not provided)
        
    Yields:
        Events from the agent execution
    """
    if agent is None:
        agent = create_agent()
    
    # Stream the agent execution
    async for event in agent.astream_events(
        {"messages": [("user", question)]},
        version="v2"
    ):
        yield event
