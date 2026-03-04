"""
Web Search Tool with Serper API + DuckDuckGo Fallback

Session 758: Updated to use Serper API as primary (more reliable, has API key)
with DuckDuckGo as fallback.

Search priority:
1. Serper API (Google search via API - reliable, fast)
2. DuckDuckGo library (free, but rate-limited)
3. DuckDuckGo HTML scraping (fallback)
4. Synthetic results (development fallback)
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.core.cache import cache

from .base import BaseTool

# DDGS calls can hang indefinitely — cap at 15 seconds
_DDGS_TIMEOUT = 15

logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """Web search tool using Serper API with DuckDuckGo fallback."""

    name = "web_search"
    description = "Search the web using Serper API (Google) with DuckDuckGo fallback"
    requires_auth = False
    tool_type = "research"

    def __init__(self):
        """Initialize the web search tool."""
        self.ddgs = None
        self.cache_duration = 3600  # Cache for 1 hour
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        super().__init__()
    
    @staticmethod
    def _run_with_timeout(fn, timeout=_DDGS_TIMEOUT):
        """Run a callable with a hard wall-clock timeout (prevents DDGS hangs)."""
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(fn)
            return future.result(timeout=timeout)

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

        # Session 758: Normalize 'search' to 'text' (ResearchAgent compatibility)
        if search_type == 'search':
            search_type = 'text'

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

            # Validate results
            if not results:
                logger.warning(f"No results returned for query: {query}")
                return self.format_result(
                    success=False,
                    error="No search results found",
                    data={
                        'query': query,
                        'search_type': search_type,
                        'results': [],
                        'total_results': 0,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            
            # Format and cache result with enhanced metadata
            result = self.format_result(
                success=True,
                data={
                    'query': query,
                    'search_type': search_type,
                    'results': results,
                    'total_results': len(results),
                    'search_methods_used': list(set([r.get('method', 'unknown') for r in results])),
                    'real_results': len([r for r in results if r.get('method') != 'synthetic_fallback']),
                    'synthetic_results': len([r for r in results if r.get('method') == 'synthetic_fallback']),
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
        """Perform text search with enhanced error handling and fallback APIs."""
        results = []

        # Session 758: Primary method - Serper API (Google search, reliable)
        if self.serper_api_key:
            try:
                import requests
                url = "https://google.serper.dev/search"
                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": query,
                    "num": max_results
                }

                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                organic = data.get('organic', [])

                for item in organic[:max_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'Google (Serper)',
                        'method': 'serper_api'
                    })

                if results:
                    logger.info(f"Serper API returned {len(results)} results")
                    return results

            except Exception as e:
                logger.warning(f"Serper API failed: {e}, trying DuckDuckGo")

        # Fallback 1: DuckDuckGo search library (with timeout guard)
        try:
            def _ddgs_text():
                with self.DDGS() as ddgs:
                    return list(ddgs.text(
                        query,
                        max_results=max_results,
                        safesearch=kwargs.get('safesearch', 'moderate'),
                        region=kwargs.get('region', 'us-en')
                    ))

            for r in self._run_with_timeout(_ddgs_text):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('href', ''),
                    'snippet': r.get('body', ''),
                    'source': 'DuckDuckGo',
                    'method': 'ddgs_library'
                })

            if results:
                logger.info(f"DuckDuckGo library returned {len(results)} results")
                return results

        except FuturesTimeout:
            logger.warning("DuckDuckGo text search timed out after %ds", _DDGS_TIMEOUT)
        except Exception as e:
            logger.warning(f"DuckDuckGo library failed: {e}, trying backup methods")

        # Fallback method 1: Direct HTML scraping (basic)
        try:
            import requests
            from urllib.parse import quote_plus

            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Simple text extraction for basic results
                import re
                text = response.text

                # Extract basic search result patterns
                title_pattern = r'<a[^>]+class="result__a"[^>]*>([^<]+)</a>'
                url_pattern = r'<a[^>]+class="result__url"[^>]*href="([^"]+)"'
                snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>([^<]+)</a>'

                titles = re.findall(title_pattern, text)[:max_results]
                urls = re.findall(url_pattern, text)[:max_results]
                snippets = re.findall(snippet_pattern, text)[:max_results]

                for i in range(min(len(titles), max_results)):
                    results.append({
                        'title': titles[i] if i < len(titles) else 'Search Result',
                        'url': urls[i] if i < len(urls) else '',
                        'snippet': snippets[i] if i < len(snippets) else 'Content available',
                        'source': 'DuckDuckGo HTML',
                        'method': 'html_scraping'
                    })

                if results:
                    logger.info(f"HTML scraping returned {len(results)} results")
                    return results

        except Exception as e:
            logger.warning(f"HTML scraping failed: {e}")

        # Fallback method 2: Generate synthetic but realistic results for development
        if not results:
            logger.warning("All search methods failed, generating synthetic results for development")

            # Create realistic synthetic results based on query
            query_lower = query.lower()

            if 'freelance' in query_lower or 'job' in query_lower:
                results = [
                    {
                        'title': 'Upwork - Find Freelance Work Online',
                        'url': 'https://www.upwork.com',
                        'snippet': 'Find freelance work online. Millions of projects posted daily. Connect with clients worldwide.',
                        'source': 'Synthetic',
                        'method': 'synthetic_fallback'
                    },
                    {
                        'title': 'Fiverr - Freelance Services Marketplace',
                        'url': 'https://www.fiverr.com',
                        'snippet': 'Find & hire freelance services online. Start your freelance business today.',
                        'source': 'Synthetic',
                        'method': 'synthetic_fallback'
                    }
                ]
            elif 'content' in query_lower or 'writing' in query_lower:
                results = [
                    {
                        'title': 'Content Writing Opportunities 2024',
                        'url': 'https://contentfly.com/opportunities',
                        'snippet': 'High-paying content writing jobs. Remote work available. Apply today.',
                        'source': 'Synthetic',
                        'method': 'synthetic_fallback'
                    },
                    {
                        'title': 'ProBlogger Job Board',
                        'url': 'https://problogger.com/jobs/',
                        'snippet': 'Professional blogging and content writing opportunities.',
                        'source': 'Synthetic',
                        'method': 'synthetic_fallback'
                    }
                ]
            else:
                # Generic results
                results = [
                    {
                        'title': f'Search Results for {query}',
                        'url': f'https://example.com/search?q={query}',
                        'snippet': f'Relevant information about {query} can be found here.',
                        'source': 'Synthetic',
                        'method': 'synthetic_fallback'
                    }
                ]

            logger.info(f"Generated {len(results)} synthetic results as fallback")

        return results
    
    def _search_news(self, query: str, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform news search with Serper API fallback to DuckDuckGo.

        Session 846: Added Serper news API support to avoid DuckDuckGo rate limits.
        """
        results = []

        # Session 846: Primary method - Serper News API (Google News via API)
        if self.serper_api_key:
            try:
                import requests
                url = "https://google.serper.dev/news"
                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": query,
                    "num": max_results
                }

                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()

                data = response.json()
                news_items = data.get('news', [])

                for item in news_items[:max_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'date': item.get('date', ''),
                        'source': item.get('source', 'Google News (Serper)'),
                        'image': item.get('imageUrl', ''),
                        'method': 'serper_news'
                    })

                if results:
                    logger.info(f"Serper News API returned {len(results)} results")
                    return results

            except Exception as e:
                logger.warning(f"Serper News API failed: {e}, trying DuckDuckGo")

        # Fallback: DuckDuckGo news search (with timeout guard)
        try:
            def _ddgs_news():
                with self.DDGS() as ddgs:
                    return list(ddgs.news(
                        query,
                        max_results=max_results,
                        safesearch=kwargs.get('safesearch', 'moderate'),
                        region=kwargs.get('region', 'us-en')
                    ))

            for r in self._run_with_timeout(_ddgs_news):
                results.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'snippet': r.get('body', ''),
                    'date': r.get('date', ''),
                    'source': r.get('source', 'DuckDuckGo News'),
                    'image': r.get('image', ''),
                    'method': 'ddgs_news'
                })

            if results:
                logger.info(f"DuckDuckGo News returned {len(results)} results")
                return results

        except FuturesTimeout:
            logger.warning("DuckDuckGo news search timed out after %ds", _DDGS_TIMEOUT)
        except Exception as e:
            logger.warning(f"DuckDuckGo News failed: {e}")

        # Session 846: Synthetic fallback for news when all APIs fail
        if not results:
            logger.warning("All news search methods failed, generating synthetic results")
            results = [
                {
                    'title': f'News Results for: {query[:50]}',
                    'url': f'https://news.google.com/search?q={query.replace(" ", "+")}',
                    'snippet': f'Search for news about: {query}. Visit Google News for recent articles.',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'source': 'Synthetic (Search Failed)',
                    'image': '',
                    'method': 'synthetic_news_fallback'
                }
            ]

        return results
    
    def _search_images(self, query: str, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform image search (with timeout guard)."""
        def _ddgs_images():
            with self.DDGS() as ddgs:
                return list(ddgs.images(
                    query,
                    max_results=max_results,
                    safesearch=kwargs.get('safesearch', 'moderate'),
                    size=kwargs.get('size', None),
                    color=kwargs.get('color', None),
                    type_image=kwargs.get('type_image', None)
                ))

        try:
            raw = self._run_with_timeout(_ddgs_images)
        except (FuturesTimeout, Exception) as e:
            logger.warning("DuckDuckGo image search failed: %s", e)
            return []

        return [
            {
                'title': r.get('title', ''),
                'url': r.get('image', ''),
                'thumbnail': r.get('thumbnail', ''),
                'source': r.get('source', ''),
                'width': r.get('width', 0),
                'height': r.get('height', 0)
            }
            for r in raw
        ]
    
    def _search_videos(self, query: str, max_results: int, **kwargs) -> List[Dict[str, Any]]:
        """Perform video search (with timeout guard)."""
        def _ddgs_videos():
            with self.DDGS() as ddgs:
                return list(ddgs.videos(
                    query,
                    max_results=max_results,
                    safesearch=kwargs.get('safesearch', 'moderate'),
                    duration=kwargs.get('duration', None)
                ))

        try:
            raw = self._run_with_timeout(_ddgs_videos)
        except (FuturesTimeout, Exception) as e:
            logger.warning("DuckDuckGo video search failed: %s", e)
            return []

        return [
            {
                'title': r.get('title', ''),
                'url': r.get('content', ''),
                'description': r.get('description', ''),
                'duration': r.get('duration', ''),
                'embed_url': r.get('embed_url', ''),
                'thumbnail': r.get('images', {}).get('large', ''),
                'published': r.get('published', ''),
                'publisher': r.get('publisher', ''),
                'views': r.get('statistics', {}).get('viewCount', 0)
            }
            for r in raw
        ]
    
    def validate_input(self, query: str = None, search_type: str = None, **kwargs) -> bool:
        """Validate input parameters."""
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return False

        # Session 758: Accept 'search' as alias for 'text' (ResearchAgent sends 'search')
        valid_types = ['text', 'news', 'images', 'videos', 'search']
        if search_type and search_type not in valid_types:
            return False

        return True
    
    def instant_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """Get instant answer for a query (like calculator, conversions, etc)."""
        if not self.is_configured:
            return None

        try:
            def _ddgs_answers():
                with self.DDGS() as ddgs:
                    return list(ddgs.answers(query))

            results = self._run_with_timeout(_ddgs_answers)
            if results:
                answer = results[0]
                return {
                    'answer': answer.get('text', ''),
                    'type': answer.get('type', ''),
                    'topic': answer.get('topic', ''),
                    'url': answer.get('url', '')
                }
        except FuturesTimeout:
            logger.warning("DuckDuckGo instant answer timed out after %ds", _DDGS_TIMEOUT)
        except Exception as e:
            logger.error(f"Instant answer error: {e}")

        return None