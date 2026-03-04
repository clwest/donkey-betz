"""
NewsAPI Spider - Breaking News Intelligence
============================================

Session 534: Simplified to work with spider network interface.
Uses NewsAPI when key available, RSS fallback otherwise.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class NewsAPISpider:
    """NewsAPI spider - breaking news from 80k+ sources worldwide"""

    name = "newsapi"

    BASE_URL = "https://newsapi.org/v2"

    # Fallback news RSS feeds
    RSS_FEEDS = {
        'google_news': 'https://news.google.com/rss',
        'bbc_world': 'https://feeds.bbci.co.uk/news/world/rss.xml',
        'npr': 'https://feeds.npr.org/1001/rss.xml',
        'ap_news': 'https://rsshub.app/apnews/topics/apf-topnews',
        'cnn': 'https://rss.cnn.com/rss/edition.rss',
    }

    # News categories
    CATEGORIES = [
        ('Technology', 'technology', 'Tech and innovation news.'),
        ('Business', 'business', 'Business and finance news.'),
        ('Science', 'science', 'Science and research news.'),
        ('Health', 'health', 'Health and medicine news.'),
        ('World', 'world', 'World news and events.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.api_key = os.getenv('NEWS_API_KEY', '')

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch breaking news from NewsAPI and fallback sources.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of news content dictionaries
        """
        all_items = []
        seen_urls = set()

        # Try NewsAPI if key available
        if self.api_key:
            try:
                api_items = self._fetch_from_newsapi()
                for item in api_items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching from NewsAPI: {e}")

        # Fetch from fallback RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting news categories: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"NewsAPI spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_from_newsapi(self) -> List[Dict[str, Any]]:
        """Fetch news from NewsAPI."""
        items = []

        # Fetch top headlines
        try:
            for category in ['technology', 'business', 'science']:
                response = cached_get(
                    f"{self.BASE_URL}/top-headlines",
                    params={
                        'category': category,
                        'country': 'us',
                        'pageSize': 10,
                        'apiKey': self.api_key
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('articles', [])[:10]:
                        items.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'link': article.get('url', ''),
                            'summary': article.get('description', '')[:400] if article.get('description') else '',
                            'description': article.get('description', '')[:400] if article.get('description') else '',
                            'published': article.get('publishedAt', ''),
                            'author': article.get('author', article.get('source', {}).get('name', '')),
                            'image_url': article.get('urlToImage', ''),
                            'category': category,
                            'news_source': article.get('source', {}).get('name', ''),
                            'source': 'NewsAPI',
                            'data_type': 'news_article',
                            'platform': 'newsapi',
                            'tags': ['newsapi', 'headlines', category],
                            'timestamp': datetime.now().isoformat(),
                        })

        except Exception as e:
            logger.warning(f"Error fetching NewsAPI headlines: {e}")

        return items

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch news from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:12]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.title()),
                    'category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'news_article',
                    'platform': 'newsapi',
                    'tags': ['newsapi', 'news', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect news category from text."""
        categories = {
            'technology': ['tech', 'software', 'ai', 'startup', 'computer', 'digital'],
            'business': ['business', 'market', 'economy', 'finance', 'stock', 'trade'],
            'science': ['science', 'research', 'study', 'discovery', 'space'],
            'health': ['health', 'medicine', 'medical', 'drug', 'disease', 'hospital'],
            'world': ['world', 'international', 'global', 'foreign', 'country'],
        }

        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return news category links."""
        return [
            {
                'title': f"News: {name}",
                'url': f'https://news.google.com/topics/{slug}',
                'link': f'https://news.google.com/topics/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'NewsAPI',
                'data_type': 'news_category',
                'platform': 'newsapi',
                'tags': ['newsapi', 'news', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when all sources fail."""
        topics = [
            ('Tech Headlines', 'technology', 'Latest technology news.'),
            ('Business News', 'business', 'Business and finance updates.'),
            ('Science News', 'science', 'Science and research discoveries.'),
            ('Health News', 'health', 'Health and medicine updates.'),
            ('World News', 'world', 'Global news and events.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://news.google.com/topics/{category}',
                'link': f'https://news.google.com/topics/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'NewsAPI',
                'data_type': 'news_topic',
                'platform': 'newsapi',
                'tags': ['newsapi', 'news', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
