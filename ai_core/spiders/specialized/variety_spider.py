"""
Variety Spider - Entertainment Industry News Intelligence
==========================================================

Session 534: Simplified to work with spider network interface.
Aggregates entertainment industry news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class VarietySpider:
    """Variety spider - entertainment industry news and analysis"""

    name = "variety"

    # Entertainment news RSS feeds
    RSS_FEEDS = {
        'variety_main': 'https://variety.com/feed/',
        'variety_film': 'https://variety.com/v/film/feed/',
        'variety_tv': 'https://variety.com/v/tv/feed/',
        'variety_music': 'https://variety.com/v/music/feed/',
        'hollywood_reporter': 'https://www.hollywoodreporter.com/feed/',
    }

    # Entertainment categories
    CATEGORIES = [
        ('Film', 'film', 'Movie news and box office.'),
        ('Television', 'tv', 'TV shows and streaming.'),
        ('Music', 'music', 'Music industry news.'),
        ('Digital', 'digital', 'Digital media and streaming.'),
        ('Awards', 'awards', 'Awards and ceremonies.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.entertainment_categories = {
            'film': ['movie', 'film', 'cinema', 'box office', 'director', 'actor', 'actress'],
            'tv': ['tv', 'television', 'series', 'show', 'streaming', 'netflix', 'hbo', 'disney+'],
            'music': ['music', 'album', 'song', 'concert', 'artist', 'singer', 'band', 'grammy'],
            'streaming': ['streaming', 'netflix', 'disney+', 'hulu', 'amazon prime', 'max', 'peacock'],
            'gaming': ['game', 'gaming', 'video game', 'esports', 'playstation', 'xbox'],
            'celebrity': ['celebrity', 'star', 'famous', 'red carpet', 'interview'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch entertainment news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of entertainment news dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from RSS feeds
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
            logger.warning(f"Error getting entertainment categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Variety spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch entertainment news from RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Analysis
                text = f"{title} {summary}".lower()
                categories = self._detect_categories(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Variety'),
                    'categories': categories,
                    'category': categories[0] if categories else 'general',
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'entertainment_news',
                    'platform': 'variety',
                    'tags': ['entertainment', 'hollywood'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect entertainment categories from text."""
        categories = []
        for category, keywords in self.entertainment_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        return categories or ['general']

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze news sentiment."""
        positive = ['hit', 'success', 'wins', 'award', 'celebrates', 'premiere', 'acclaimed']
        negative = ['flop', 'cancel', 'lawsuit', 'controversy', 'fails', 'disappoints']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return entertainment category links."""
        return [
            {
                'title': f"Variety: {name}",
                'url': f'https://variety.com/v/{slug}/',
                'link': f'https://variety.com/v/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Variety',
                'data_type': 'entertainment_category',
                'platform': 'variety',
                'tags': ['entertainment', 'hollywood', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Box Office News', 'film', 'Latest movie box office reports.'),
            ('Streaming Updates', 'tv', 'TV and streaming news.'),
            ('Music Industry', 'music', 'Music charts and industry news.'),
            ('Awards Season', 'awards', 'Oscars, Emmys, and Grammys.'),
            ('Celebrity News', 'celebrity', 'Entertainment celebrity updates.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://variety.com/v/{category}/',
                'link': f'https://variety.com/v/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Variety',
                'data_type': 'entertainment_topic',
                'platform': 'variety',
                'tags': ['entertainment', 'hollywood', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
