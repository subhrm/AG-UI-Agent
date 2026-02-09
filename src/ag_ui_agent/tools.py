"""Web search and other tools for the agent."""
from typing import Annotated
from langchain_core.tools import tool
from tavily import TavilyClient
from .config import Config


# Initialize Tavily client
tavily_client = TavilyClient(api_key=Config.TAVILY_API_KEY) if Config.TAVILY_API_KEY else None


@tool
def web_search(query: Annotated[str, "The search query to look up on the web"]) -> str:
    """
    Search the web for current information using Tavily API.
    
    Use this tool when you need to find current information, news, or facts
    that are not in your training data or require real-time information.
    
    Args:
        query: The search query string
        
    Returns:
        A formatted string containing search results with titles, URLs, and snippets
    """
    if not tavily_client:
        return "Error: Tavily API key not configured. Cannot perform web search."
    
    try:
        # Perform the search
        response = tavily_client.search(
            query=query,
            max_results=Config.TAVILY_MAX_RESULTS,
            search_depth="advanced"
        )
        
        # Format the results
        if not response.get("results"):
            return f"No results found for query: {query}"
        
        formatted_results = [f"Search results for: {query}\n"]
        
        for idx, result in enumerate(response["results"], 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "No content available")
            
            formatted_results.append(
                f"\n{idx}. {title}\n"
                f"   URL: {url}\n"
                f"   {content}\n"
            )
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error performing web search: {str(e)}"


# List of all available tools
TOOLS = [web_search]
