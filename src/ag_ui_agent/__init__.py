"""AG-UI Agent package."""

__version__ = "1.0.0"

from .agent import create_agent, run_agent, stream_agent
from .config import Config
from .tools import TOOLS, web_search

__all__ = [
    "create_agent",
    "run_agent", 
    "stream_agent",
    "Config",
    "TOOLS",
    "web_search",
]
