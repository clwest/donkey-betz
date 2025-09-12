"""
Web Search Tool using DuckDuckGo

This tool provides web search capabilities without requiring API keys.
It uses the DuckDuckGo search engine through the duckduckgo_search library.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.core.cache import cache

from .base import BaseTool

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Web search tool using DuckDuckGo."""
    
    name = "web_search"
    description = "Search the web using DuckDuckGo search engine"
    requires_auth = False
    tool_type = "research"
    
    def __init__(self):
        """Initialize the web search tool."""
        self.ddgs = None
        self.cache_duration = 3600  # Cache for 1 hour
        super().__init__()
    
    def _check_configuration(self) -> bool:
        """Check if DuckDuckGo search is available."""
        try:
            from duckduckgo_search import DDGS
            self.DDGS = DDGS
            return True
        except ImportError:
            logger.error("duckduckgo_search library not installed. Run: pip install duckduckgo-search")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return [
            'web_search',
            'news_search',
            'image_search',
            'video_search',
            'instant_answers',
            'safe_search'
        ]
    
    def execute(self, query: str, search_type: str = 'text', max_results: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Execute a web search.
        
        Args:
            query: Search query string
            search_type: Type of search ('text', 'news', 'images', 'videos')
            max_results: Maximum number of results to return
            **kwargs: Additional search parameters
        
        Returns:
            Dict with search results or error
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="DuckDuckGo search not configured. Install: pip install duckduckgo-search"
            )
        
        if not self.validate_input(query=query, search_type=search_type):
            return self.format_result(
                success=False,
                error="Invalid input parameters"
            )
        
        # Check cache first
        cache_key = f"web_search_{search_type}_{query}_{max_results}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached results for: {query}")
            return cached
        
        try:
            # Perform search based on type
            if search_type == 'text':
                results = self._search_text(query, max_results, **kwargs)
            elif search_type == 'news':
                results = self._search_news(query, max_results, **kwargs)
            elif search_type == 'images':
                results = self._search_images(query, max_results, **kwargs)
            elif search_type == 'videos':
                results = self._search_videos(query, max_results, **kwargs)
            else:
                return self.format_result(
                    success=False,
                    error=f"Unsupported search type: {search_type}"
                )
            
            # Format and cache result
            result = self.format_result(
                success=True,
                data={
                    'query': query,
                    'search_type': search_type,
                    'results': results,
                    'total_results': len(results),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            cache.set(cache_key, result, self.cache_duration)
            return result
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    def _search_text(self, query: str, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform text search."""
        with self.DDGS() as ddgs:
            results = []
            for r in ddgs.text(
                query, 
                max_results=max_results,
                safesearch=kwargs.get('safesearch', 'moderate'),
                region=kwargs.get('region', 'us-en')
            ):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'snippet': r.get('body', ''),
                    'source': 'DuckDuckGo'
                })
            return results
    
    def _search_news(self, query: str, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform news search."""
        with self.DDGS() as ddgs:
            results = []
            for r in ddgs.news(
                query,
                max_results=max_results,
                safesearch=kwargs.get('safesearch', 'moderate'),
                region=kwargs.get('region', 'us-en')
            ):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'snippet': r.get('body', ''),
                    'date': r.get('date', ''),
                    'source': r.get('source', 'DuckDuckGo News'),
                    'image': r.get('image', '')
                })
            return results
    
    def _search_images(self, query: str, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform image search."""
        with self.DDGS() as ddgs:
            results = []
            for r in ddgs.images(
                query,
                max_results=max_results,
                safesearch=kwargs.get('safesearch', 'moderate'),
                size=kwargs.get('size', None),
                color=kwargs.get('color', None),
                type_image=kwargs.get('type_image', None)
            ):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('image', ''),
                    'thumbnail': r.get('thumbnail', ''),
                    'source': r.get('source', ''),
                    'width': r.get('width', 0),
                    'height': r.get('height', 0)
                })
            return results
    
    def _search_videos(self, query: str, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform video search."""
        with self.DDGS() as ddgs:
            results = []
            for r in ddgs.videos(
                query,
                max_results=max_results,
                safesearch=kwargs.get('safesearch', 'moderate'),
                duration=kwargs.get('duration', None)
            ):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('content', ''),
                    'description': r.get('description', ''),
                    'duration': r.get('duration', ''),
                    'embed_url': r.get('embed_url', ''),
                    'thumbnail': r.get('images', {}).get('large', ''),
                    'published': r.get('published', ''),
                    'publisher': r.get('publisher', ''),
                    'views': r.get('statistics', {}).get('viewCount', 0)
                })
            return results
    
    def validate_input(self, query: str = None, search_type: str = None, **kwargs) -> bool:
        """Validate input parameters."""
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return False
        
        if search_type and search_type not in ['text', 'news', 'images', 'videos']:
            return False
        
        return True
    
    def instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """Get instant answer for a query (like calculator, conversions, etc)."""
        if not self.is_configured:
            return None
        
        try:
            with self.DDGS() as ddgs:
                results = list(ddgs.answers(query))
                if results:
                    answer = results[0]
                    return {
                        'answer': answer.get('text', ''),
                        'type': answer.get('type', ''),
                        'topic': answer.get('topic', ''),
                        'url': answer.get('url', '')
                    }
        except Exception as e:
            logger.error(f"Instant answer error: {e}")
        
        return None