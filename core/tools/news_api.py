"""
News API Integration Tool

This tool provides access to multiple news sources for current events,
breaking news, and topic-specific news articles. Based on the implementation
from donkey-betz-agent-orchestra.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
import aiohttp
import asyncio
from urllib.parse import quote

from .base import BaseTool

logger = logging.getLogger(__name__)


class NewsAPITool(BaseTool):
    """News API tool with multiple provider support."""
    
    name = "news_api"
    description = "Search and retrieve news articles from multiple sources"
    requires_auth = True
    tool_type = "research"
    
    def __init__(self):
        """Initialize the news API tool."""
        # Primary providers
        self.newsapi_key = os.getenv('NEWS_API_KEY', '')
        self.newsapi_base = 'https://newsapi.org/v2/'
        
        # Secondary providers
        self.gnews_key = os.getenv('GNEWS_API_KEY', '')
        self.gnews_base = 'https://gnews.io/api/v4/'
        
        self.currents_key = os.getenv('CURRENTS_API_KEY', '')
        self.currents_base = 'https://api.currentsapi.services/v1/'
        
        self.guardian_key = os.getenv('GUARDIAN_API_KEY', '')
        self.guardian_base = 'https://content.guardianapis.com/'
        
        self.cache_duration = 900  # Cache for 15 minutes
        super().__init__()
    
    def _check_configuration(self) -> bool:
        """Check if any news API is configured."""
        return bool(
            self.newsapi_key or 
            self.gnews_key or 
            self.currents_key or
            self.guardian_key
        )
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        capabilities = []
        
        if self.newsapi_key:
            capabilities.extend(['newsapi_headlines', 'newsapi_search'])
        if self.gnews_key:
            capabilities.extend(['gnews_headlines', 'gnews_search'])
        if self.currents_key:
            capabilities.extend(['currents_headlines', 'currents_search'])
        if self.guardian_key:
            capabilities.extend(['guardian_headlines', 'guardian_search'])
        
        capabilities.extend(['multi_source_aggregation', 'topic_monitoring'])
        
        return capabilities
    
    def execute(self, query: str = None, action: str = 'search', **kwargs) -> Dict[str, Any]:
        """
        Execute news API request.
        
        Args:
            query: Search query (optional for headlines)
            action: Action to perform ('search', 'headlines', 'topic')
            **kwargs: Additional parameters (category, country, from_date, to_date, etc.)
        
        Returns:
            Dict with news articles or error
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="No news API configured. Set NEWS_API_KEY or other news API keys"
            )
        
        if action == 'search' and not query:
            return self.format_result(
                success=False,
                error="Query required for search action"
            )
        
        # Run async method
        if action == 'headlines':
            result = asyncio.run(self._get_headlines_async(
                category=kwargs.get('category'),
                country=kwargs.get('country', 'us'),
                limit=kwargs.get('limit', 10)
            ))
        elif action == 'search':
            result = asyncio.run(self._search_news_async(
                query=query,
                from_date=kwargs.get('from_date'),
                to_date=kwargs.get('to_date'),
                limit=kwargs.get('limit', 10)
            ))
        elif action == 'topic':
            result = self._monitor_topic(
                topic=query,
                limit=kwargs.get('limit', 10)
            )
        else:
            return self.format_result(
                success=False,
                error=f"Unsupported action: {action}"
            )
        
        return result
    
    async def _get_headlines_async(self, category: Optional[str] = None, 
                                   country: str = 'us', limit: int = 10) -> Dict[str, Any]:
        """Get top headlines asynchronously."""
        # Check cache first
        cache_key = f"news_headlines_{category or 'general'}_{country}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Try providers in order
        result = None
        
        # Try NewsAPI first
        if self.newsapi_key and not result:
            result = await self._get_newsapi_headlines(category, country, limit)
            if result and result.get('success'):
                cache.set(cache_key, result, self.cache_duration)
                return result
        
        # Try GNews
        if self.gnews_key and not result:
            result = await self._get_gnews_headlines(category, country, limit)
            if result and result.get('success'):
                cache.set(cache_key, result, self.cache_duration)
                return result
        
        # Try CurrentsAPI
        if self.currents_key and not result:
            result = await self._get_currents_headlines(category, country, limit)
            if result and result.get('success'):
                cache.set(cache_key, result, self.cache_duration)
                return result
        
        # Try The Guardian
        if self.guardian_key and not result:
            result = await self._get_guardian_headlines(category, limit)
            if result and result.get('success'):
                cache.set(cache_key, result, self.cache_duration)
                return result
        
        # All failed
        return self.format_result(
            success=False,
            error="All news providers failed or returned no results"
        )
    
    async def _search_news_async(self, query: str, from_date: Optional[datetime] = None,
                                 to_date: Optional[datetime] = None, limit: int = 10) -> Dict[str, Any]:
        """Search news articles asynchronously."""
        # Check cache first
        cache_key = f"news_search_{query}_{from_date}_{to_date}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Try providers
        result = None
        
        # Try NewsAPI
        if self.newsapi_key:
            result = await self._search_newsapi(query, from_date, to_date, limit)
            if result and result.get('success'):
                cache.set(cache_key, result, self.cache_duration)
                return result
        
        # Try GNews
        if self.gnews_key and not result:
            result = await self._search_gnews(query, from_date, to_date, limit)
            if result and result.get('success'):
                cache.set(cache_key, result, self.cache_duration)
                return result
        
        # Try CurrentsAPI
        if self.currents_key and not result:
            result = await self._search_currents(query, from_date, to_date, limit)
            if result and result.get('success'):
                cache.set(cache_key, result, self.cache_duration)
                return result
        
        # All failed
        return self.format_result(
            success=False,
            error="Failed to search news from all providers"
        )
    
    async def _get_newsapi_headlines(self, category: Optional[str], country: str, limit: int) -> Dict[str, Any]:
        """Get headlines from NewsAPI."""
        try:
            url = f"{self.newsapi_base}top-headlines"
            params = {
                'apiKey': self.newsapi_key,
                'country': country,
                'pageSize': limit
            }
            
            if category:
                params['category'] = category
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'ok':
                            articles = []
                            for article in data.get('articles', []):
                                articles.append({
                                    'title': article['title'],
                                    'description': article.get('description', ''),
                                    'url': article['url'],
                                    'source': article['source']['name'],
                                    'published_at': article['publishedAt'],
                                    'image_url': article.get('urlToImage', ''),
                                    'author': article.get('author', ''),
                                    'content': article.get('content', '')
                                })
                            
                            return self.format_result(
                                success=True,
                                data={
                                    'provider': 'newsapi',
                                    'articles': articles,
                                    'total_results': data.get('totalResults', len(articles))
                                }
                            )
                    
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_gnews_headlines(self, category: Optional[str], country: str, limit: int) -> Dict[str, Any]:
        """Get headlines from GNews."""
        try:
            url = f"{self.gnews_base}top-headlines"
            params = {
                'token': self.gnews_key,
                'lang': 'en',
                'country': country,
                'max': limit
            }
            
            if category:
                params['topic'] = category
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        articles = []
                        for article in data.get('articles', []):
                            articles.append({
                                'title': article['title'],
                                'description': article.get('description', ''),
                                'url': article['url'],
                                'source': article['source']['name'],
                                'published_at': article['publishedAt'],
                                'image_url': article.get('image', ''),
                                'author': '',
                                'content': article.get('content', '')
                            })
                        
                        return self.format_result(
                            success=True,
                            data={
                                'provider': 'gnews',
                                'articles': articles,
                                'total_results': data.get('totalArticles', len(articles))
                            }
                        )
                    
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"GNews error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_currents_headlines(self, category: Optional[str], country: str, limit: int) -> Dict[str, Any]:
        """Get headlines from CurrentsAPI."""
        try:
            url = f"{self.currents_base}latest-news"
            params = {
                'apiKey': self.currents_key,
                'language': 'en',
                'country': country
            }
            
            if category:
                params['category'] = category
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'ok':
                            articles = []
                            for article in data.get('news', [])[:limit]:
                                articles.append({
                                    'title': article['title'],
                                    'description': article.get('description', ''),
                                    'url': article['url'],
                                    'source': article.get('author', 'CurrentsAPI'),
                                    'published_at': article['published'],
                                    'image_url': article.get('image', ''),
                                    'author': article.get('author', ''),
                                    'content': ''
                                })
                            
                            return self.format_result(
                                success=True,
                                data={
                                    'provider': 'currentsapi',
                                    'articles': articles,
                                    'total_results': len(articles)
                                }
                            )
                    
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"CurrentsAPI error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_guardian_headlines(self, category: Optional[str], limit: int) -> Dict[str, Any]:
        """Get headlines from The Guardian."""
        try:
            url = f"{self.guardian_base}search"
            params = {
                'api-key': self.guardian_key,
                'page-size': limit,
                'show-fields': 'headline,standfirst,thumbnail,bodyText,byline',
                'order-by': 'newest'
            }
            
            if category:
                params['section'] = category
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('response', {}).get('status') == 'ok':
                            articles = []
                            for article in data['response']['results']:
                                fields = article.get('fields', {})
                                articles.append({
                                    'title': fields.get('headline', article.get('webTitle', '')),
                                    'description': fields.get('standfirst', ''),
                                    'url': article['webUrl'],
                                    'source': 'The Guardian',
                                    'published_at': article['webPublicationDate'],
                                    'image_url': fields.get('thumbnail', ''),
                                    'author': fields.get('byline', ''),
                                    'content': fields.get('bodyText', '')[:500]
                                })
                            
                            return self.format_result(
                                success=True,
                                data={
                                    'provider': 'guardian',
                                    'articles': articles,
                                    'total_results': data['response']['total']
                                }
                            )
                    
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"Guardian error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _search_newsapi(self, query: str, from_date: Optional[datetime], 
                              to_date: Optional[datetime], limit: int) -> Dict[str, Any]:
        """Search news using NewsAPI."""
        try:
            url = f"{self.newsapi_base}everything"
            params = {
                'apiKey': self.newsapi_key,
                'q': query,
                'pageSize': limit,
                'sortBy': 'relevancy',
                'language': 'en'
            }
            
            if from_date:
                params['from'] = from_date.strftime('%Y-%m-%d')
            if to_date:
                params['to'] = to_date.strftime('%Y-%m-%d')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'ok':
                            articles = []
                            for article in data.get('articles', []):
                                articles.append({
                                    'title': article['title'],
                                    'description': article.get('description', ''),
                                    'url': article['url'],
                                    'source': article['source']['name'],
                                    'published_at': article['publishedAt'],
                                    'image_url': article.get('urlToImage', ''),
                                    'author': article.get('author', ''),
                                    'content': article.get('content', '')
                                })
                            
                            return self.format_result(
                                success=True,
                                data={
                                    'provider': 'newsapi',
                                    'query': query,
                                    'articles': articles,
                                    'total_results': data.get('totalResults', len(articles))
                                }
                            )
                    
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"NewsAPI search error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _search_gnews(self, query: str, from_date: Optional[datetime], 
                            to_date: Optional[datetime], limit: int) -> Dict[str, Any]:
        """Search news using GNews."""
        try:
            url = f"{self.gnews_base}search"
            params = {
                'token': self.gnews_key,
                'q': query,
                'lang': 'en',
                'max': limit
            }
            
            if from_date:
                params['from'] = from_date.strftime('%Y-%m-%d')
            if to_date:
                params['to'] = to_date.strftime('%Y-%m-%d')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        articles = []
                        for article in data.get('articles', []):
                            articles.append({
                                'title': article['title'],
                                'description': article.get('description', ''),
                                'url': article['url'],
                                'source': article['source']['name'],
                                'published_at': article['publishedAt'],
                                'image_url': article.get('image', ''),
                                'author': '',
                                'content': article.get('content', '')
                            })
                        
                        return self.format_result(
                            success=True,
                            data={
                                'provider': 'gnews',
                                'query': query,
                                'articles': articles,
                                'total_results': data.get('totalArticles', len(articles))
                            }
                        )
                    
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"GNews search error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _search_currents(self, query: str, from_date: Optional[datetime], 
                               to_date: Optional[datetime], limit: int) -> Dict[str, Any]:
        """Search news using CurrentsAPI."""
        try:
            url = f"{self.currents_base}search"
            params = {
                'apiKey': self.currents_key,
                'keywords': query,
                'language': 'en'
            }
            
            if from_date:
                params['start_date'] = from_date.strftime('%Y-%m-%d')
            if to_date:
                params['end_date'] = to_date.strftime('%Y-%m-%d')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 'ok':
                            articles = []
                            for article in data.get('news', [])[:limit]:
                                articles.append({
                                    'title': article['title'],
                                    'description': article.get('description', ''),
                                    'url': article['url'],
                                    'source': article.get('author', 'CurrentsAPI'),
                                    'published_at': article['published'],
                                    'image_url': article.get('image', ''),
                                    'author': article.get('author', ''),
                                    'content': ''
                                })
                            
                            return self.format_result(
                                success=True,
                                data={
                                    'provider': 'currentsapi',
                                    'query': query,
                                    'articles': articles,
                                    'total_results': len(articles)
                                }
                            )
                    
                    return {'success': False, 'error': f'API error: {response.status}'}
                    
        except Exception as e:
            logger.error(f"CurrentsAPI search error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _monitor_topic(self, topic: str, limit: int = 10) -> Dict[str, Any]:
        """Monitor a specific topic across all news sources."""
        # Synchronously call the async search
        return asyncio.run(self._search_news_async(topic, None, None, limit))
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        return True  # Basic validation, can be enhanced