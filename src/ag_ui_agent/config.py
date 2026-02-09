"""Configuration management for AG-UI Agent."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the agent."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Model Configuration
    OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")  # Custom endpoint for OpenAI-compatible APIs
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Tavily Configuration
    TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY environment variable is required")
        
        if not cls.TAVILY_API_KEY:
            errors.append("TAVILY_API_KEY environment variable is required")
        
        if errors:
            raise ValueError(
                "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            )


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"Warning: {e}")
    print("Please set the required environment variables before running the agent.")
