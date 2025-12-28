"""
Wikipedia Search and Knowledge Retrieval Tool

This tool provides access to Wikipedia for factual information,
definitions, and encyclopedic knowledge.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from django.core.cache import cache

from .base import BaseTool

logger = logging.getLogger(__name__)


class WikipediaSearchTool(BaseTool):
    """Wikipedia search and knowledge retrieval tool."""
    
    name = "wikipedia_search"
    description = "Search and retrieve information from Wikipedia"
    requires_auth = False
    tool_type = "research"
    
    def __init__(self):
        """Initialize the Wikipedia search tool."""
        self.wikipedia = None
        self.cache_duration = 86400  # Cache for 24 hours (Wikipedia content is relatively stable)
        super().__init__()
    
    def _check_configuration(self) -> bool:
        """Check if Wikipedia library is available."""
        try:
            import wikipedia
            self.wikipedia = wikipedia
            # Set default language
            self.wikipedia.set_lang('en')
            return True
        except ImportError:
            logger.error("wikipedia-api library not installed. Run: pip install wikipedia-api")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return [
            'article_search',
            'summary_retrieval',
            'full_content',
            'section_extraction',
            'multilingual_search',
            'disambiguation',
            'related_articles'
        ]
    
    def execute(self, query: str, action: str = 'search', limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Execute a Wikipedia search or retrieval.
        
        Args:
            query: Search query or page title
            action: Action to perform ('search', 'summary', 'content', 'sections')
            limit: Maximum number of results for search
            **kwargs: Additional parameters (lang, sentences for summary, etc.)
        
        Returns:
            Dict with results or error
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="Wikipedia library not configured. Install: pip install wikipedia-api"
            )
        
        if not self.validate_input(query=query, action=action):
            return self.format_result(
                success=False,
                error="Invalid input parameters"
            )
        
        # Set language if specified
        lang = kwargs.get('lang', 'en')
        if lang != 'en':
            self.wikipedia.set_lang(lang)
        
        # Check cache
        cache_key = f"wikipedia_{action}_{query}_{limit}_{lang}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached Wikipedia results for: {query}")
            return cached
        
        try:
            if action == 'search':
                results = self._search(query, limit)
            elif action == 'summary':
                results = self._get_summary(query, kwargs.get('sentences', 5))
            elif action == 'content':
                results = self._get_content(query)
            elif action == 'sections':
                results = self._get_sections(query)
            else:
                return self.format_result(
                    success=False,
                    error=f"Unsupported action: {action}"
                )
            
            # Format and cache result
            result = self.format_result(
                success=True,
                data={
                    'query': query,
                    'action': action,
                    'language': lang,
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            cache.set(cache_key, result, self.cache_duration)
            return result
            
        except self.wikipedia.exceptions.DisambiguationError as e:
            # Handle disambiguation pages
            return self.format_result(
                success=False,
                error="Ambiguous query",
                data={
                    'type': 'disambiguation',
                    'options': e.options[:10]  # Return first 10 options
                }
            )
        except self.wikipedia.exceptions.PageError:
            return self.format_result(
                success=False,
                error=f"Page not found: {query}"
            )
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
        finally:
            # Reset to English
            if lang != 'en':
                self.wikipedia.set_lang('en')
    
    def _search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search Wikipedia for matching articles."""
        search_results = self.wikipedia.search(query, results=limit)
        
        results = []
        for title in search_results:
            try:
                # Get basic info for each result
                page = self.wikipedia.page(title)
                results.append({
                    'title': page.title,
                    'url': page.url,
                    'summary': self.wikipedia.summary(title, sentences=2),
                    'categories': page.categories[:5] if hasattr(page, 'categories') else []
                })
            except Exception as e:
                logger.warning(f"Error getting info for {title}: {e}")
                results.append({
                    'title': title,
                    'url': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    'summary': 'Unable to retrieve summary',
                    'categories': []
                })
        
        return results
    
    def _get_summary(self, query: str, sentences: int) -> Dict[str, Any]:
        """Get summary of a Wikipedia article."""
        try:
            summary = self.wikipedia.summary(query, sentences=sentences)
            page = self.wikipedia.page(query)
            
            return {
                'title': page.title,
                'summary': summary,
                'url': page.url,
                'images': page.images[:5] if hasattr(page, 'images') else [],
                'references': len(page.references) if hasattr(page, 'references') else 0,
                'categories': page.categories[:10] if hasattr(page, 'categories') else [],
                'related': page.links[:10] if hasattr(page, 'links') else []
            }
        except Exception as e:
            logger.error(f"Error getting summary: {e}")
            raise
    
    def _get_content(self, query: str) -> Dict[str, Any]:
        """Get full content of a Wikipedia article."""
        page = self.wikipedia.page(query)
        
        return {
            'title': page.title,
            'content': page.content[:10000],  # Limit content length
            'url': page.url,
            'images': page.images[:10] if hasattr(page, 'images') else [],
            'references': page.references[:20] if hasattr(page, 'references') else [],
            'categories': page.categories if hasattr(page, 'categories') else [],
            'links': page.links[:20] if hasattr(page, 'links') else [],
            'sections': self._extract_sections(page.content) if hasattr(page, 'content') else []
        }
    
    def _get_sections(self, query: str) -> Dict[str, Any]:
        """Get sections of a Wikipedia article."""
        page = self.wikipedia.page(query)
        content = page.content if hasattr(page, 'content') else ''
        
        sections = self._extract_sections(content)
        
        return {
            'title': page.title,
            'url': page.url,
            'sections': sections,
            'total_sections': len(sections)
        }
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections from Wikipedia content."""
        sections = []
        current_section = {'title': 'Introduction', 'content': ''}
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('==') and line.endswith('=='):
                # New section found
                if current_section['content']:
                    sections.append(current_section)
                
                # Extract section title
                title = line.strip('= ')
                current_section = {'title': title, 'content': ''}
            else:
                current_section['content'] += line + '\n'
        
        # Add the last section
        if current_section['content']:
            sections.append(current_section)
        
        # Trim content for each section
        for section in sections:
            section['content'] = section['content'].strip()[:2000]  # Limit section length
        
        return sections
    
    def get_random_article(self) -> Dict[str, Any]:
        """Get a random Wikipedia article."""
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="Wikipedia not configured"
            )
        
        try:
            title = self.wikipedia.random()
            return self._get_summary(title, sentences=5)
        except Exception as e:
            logger.error(f"Error getting random article: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    def search_nearby(self, latitude: float, longitude: float, radius: int = 10000, limit: int = 10) -> Dict[str, Any]:
        """
        Search for Wikipedia articles about nearby locations.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in meters
            limit: Maximum number of results
        
        Returns:
            Dict with nearby articles
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="Wikipedia not configured"
            )
        
        try:
            results = self.wikipedia.geosearch(latitude, longitude, radius=radius, results=limit)
            
            articles = []
            for title in results:
                try:
                    summary = self.wikipedia.summary(title, sentences=2)
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'url': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                    })
                except Exception as e:
                    logger.warning(f"Error getting summary for {title}: {e}")
            
            return self.format_result(
                success=True,
                data={
                    'location': {'latitude': latitude, 'longitude': longitude},
                    'radius': radius,
                    'articles': articles
                }
            )
            
        except Exception as e:
            logger.error(f"Geosearch error: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    def validate_input(self, query: str = None, action: str = None, **kwargs) -> bool:
        """Validate input parameters."""
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return False
        
        if action and action not in ['search', 'summary', 'content', 'sections']:
            return False
        
        return True