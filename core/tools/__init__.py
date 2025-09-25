"""
Tool Registry System for Unified Donkey Betz Platform

This module provides a central registry for all tools available to agents,
including web search, research APIs, and data processing capabilities.
"""

from typing import Dict, Any, Optional, Type
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry for all agent tools."""
    
    _tools: Dict[str, Type] = {}
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, name: str, tool_class: Type) -> None:
        """Register a new tool class."""
        cls._tools[name] = tool_class
        logger.info(f"Registered tool: {name}")
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[Any]:
        """Get or create a tool instance."""
        if name not in cls._tools:
            logger.warning(f"Tool not found: {name}")
            return None
        
        # Create singleton instance if not exists
        if name not in cls._instances:
            try:
                cls._instances[name] = cls._tools[name]()
                logger.info(f"Created tool instance: {name}")
            except Exception as e:
                logger.error(f"Failed to create tool {name}: {e}")
                return None
        
        return cls._instances[name]
    
    @classmethod
    def list_tools(cls) -> list:
        """List all registered tool names."""
        return list(cls._tools.keys())
    
    @classmethod
    def get_tool_info(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        tool = cls.get_tool(name)
        if tool and hasattr(tool, 'get_info'):
            return tool.get_info()
        return None


# Auto-register tools when imported
def auto_register_tools():
    """Automatically register all available tools."""
    try:
        from .web_search import WebSearchTool
        ToolRegistry.register('web_search', WebSearchTool)
    except ImportError as e:
        logger.warning(f"Could not import WebSearchTool: {e}")
    
    try:
        from .arxiv_search import ArXivSearchTool
        ToolRegistry.register('arxiv_search', ArXivSearchTool)
    except ImportError as e:
        logger.warning(f"Could not import ArXivSearchTool: {e}")
    
    try:
        from .reddit_search import RedditSearchTool
        ToolRegistry.register('reddit_api', RedditSearchTool)
    except ImportError as e:
        logger.warning(f"Could not import RedditSearchTool: {e}")
    
    try:
        from .wikipedia_search import WikipediaSearchTool
        ToolRegistry.register('wikipedia_search', WikipediaSearchTool)
    except ImportError as e:
        logger.warning(f"Could not import WikipediaSearchTool: {e}")
    
    try:
        from .news_api import NewsAPITool
        ToolRegistry.register('news_api', NewsAPITool)
    except ImportError as e:
        logger.warning(f"Could not import NewsAPITool: {e}")

    try:
        from .documentation_fetcher import DocumentationFetcherTool
        ToolRegistry.register('documentation_fetcher', DocumentationFetcherTool)
        logger.info("Registered Documentation Fetcher for real-time docs")
    except ImportError as e:
        logger.warning(f"Could not import DocumentationFetcherTool: {e}")
    
    # Register sports-specific tools
    try:
        from .sports_tools import register_sports_tools
        registered_sports = register_sports_tools()
        logger.info(f"Registered {len(registered_sports)} sports tools: {registered_sports}")
    except ImportError as e:
        logger.warning(f"Could not import sports tools: {e}")
    
    logger.info(f"Tool registry initialized with {len(ToolRegistry._tools)} tools")


# Initialize on import
auto_register_tools()