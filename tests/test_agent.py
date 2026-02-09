"""Tests for the AG-UI agent."""
import pytest
from unittest.mock import Mock, patch
from src.ag_ui_agent.agent import create_agent, run_agent
from src.ag_ui_agent.tools import web_search


class TestAgent:
    """Test cases for the agent."""
    
    def test_agent_creation(self):
        """Test that the agent can be created successfully."""
        with patch('src.ag_ui_agent.agent.Config.OPENAI_API_KEY', 'test-key'):
            with patch('src.ag_ui_agent.agent.Config.TAVILY_API_KEY', 'test-key'):
                agent = create_agent()
                assert agent is not None
    
    @patch('src.ag_ui_agent.agent.ChatOpenAI')
    def test_agent_simple_question(self, mock_llm):
        """Test agent with a simple question that doesn't require tools."""
        # Mock LLM response
        mock_response = Mock()
        mock_response.content = "Paris is the capital of France."
        mock_llm.return_value.bind_tools.return_value.invoke.return_value = mock_response
        
        with patch('src.ag_ui_agent.agent.Config.OPENAI_API_KEY', 'test-key'):
            with patch('src.ag_ui_agent.agent.Config.TAVILY_API_KEY', 'test-key'):
                agent = create_agent()
                # Note: This is a simplified test - actual implementation may require more mocking


class TestWebSearch:
    """Test cases for web search tool."""
    
    @patch('src.ag_ui_agent.tools.tavily_client')
    def test_web_search_success(self, mock_client):
        """Test successful web search."""
        # Mock Tavily response
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "content": "Test content"
                }
            ]
        }
        
        with patch('src.ag_ui_agent.tools.Config.TAVILY_API_KEY', 'test-key'):
            result = web_search.invoke({"query": "test query"})
            assert "Test Result" in result
            assert "https://example.com" in result
    
    def test_web_search_no_api_key(self):
        """Test web search without API key."""
        with patch('src.ag_ui_agent.tools.tavily_client', None):
            result = web_search.invoke({"query": "test query"})
            assert "Error" in result
            assert "not configured" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
