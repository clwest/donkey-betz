"""
Polygon Gaming Spider - Video Game News Intelligence
=====================================================

Session 534: Simplified to work with spider network interface.
Aggregates gaming industry news via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PolygonGamingSpider:
    """Polygon gaming spider - video game news, reviews, and industry coverage"""

    name = "polygon_gaming"

    # Gaming RSS feeds
    RSS_FEEDS = {
        'polygon_main': 'https://www.polygon.com/rss/index.xml',
        'polygon_reviews': 'https://www.polygon.com/rss/reviews/index.xml',
        'ign': 'https://feeds.feedburner.com/ign/all',
        'gamespot': 'https://www.gamespot.com/feeds/mashup/',
        'kotaku': 'https://kotaku.com/rss',
        'eurogamer': 'https://www.eurogamer.net/feed',
    }

    # Gaming categories
    CATEGORIES = [
        ('PlayStation', 'playstation', 'PS5 and PlayStation news.'),
        ('Xbox', 'xbox', 'Xbox and Game Pass news.'),
        ('Nintendo', 'nintendo', 'Switch and Nintendo news.'),
        ('PC Gaming', 'pc', 'PC gaming news and reviews.'),
        ('Esports', 'esports', 'Competitive gaming coverage.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.gaming_categories = {
            'playstation': ['playstation', 'ps5', 'ps4', 'sony', 'dualsense', 'psvr'],
            'xbox': ['xbox', 'microsoft', 'game pass', 'series x', 'series s', 'halo'],
            'nintendo': ['nintendo', 'switch', 'mario', 'zelda', 'pokemon', 'smash'],
            'pc': ['pc', 'steam', 'epic', 'valve', 'gog', 'nvidia', 'amd'],
            'mobile': ['mobile', 'ios', 'android', 'apple arcade', 'mobile gaming'],
            'esports': ['esports', 'tournament', 'competitive', 'league', 'championship'],
            'indie': ['indie', 'independent', 'pixel', 'retro', 'roguelike'],
            'vr': ['vr', 'virtual reality', 'meta quest', 'psvr', 'oculus'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch gaming news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of gaming news dictionaries
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
            logger.warning(f"Error getting gaming categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Polygon Gaming spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from gaming RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect gaming platform/category
                text = f"{title} {summary}".lower()
                platforms = self._detect_platforms(text)
                is_review = self._is_review(title, feed_name)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Polygon'),
                    'platforms': platforms,
                    'category': platforms[0] if platforms else 'general',
                    'is_review': is_review,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'gaming_news',
                    'platform': 'polygon_gaming',
                    'tags': ['gaming', 'videogames'] + platforms[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_platforms(self, text: str) -> List[str]:
        """Detect gaming platforms from text."""
        platforms = []
        for platform, keywords in self.gaming_categories.items():
            if any(kw in text for kw in keywords):
                platforms.append(platform)
        return platforms if platforms else ['general']

    def _is_review(self, title: str, feed_name: str) -> bool:
        """Check if article is a review."""
        review_keywords = ['review', 'score', 'rating', 'verdict', 'hands-on']
        return 'review' in feed_name.lower() or any(kw in title.lower() for kw in review_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze gaming news sentiment."""
        positive_words = ['amazing', 'great', 'excellent', 'best', 'fantastic', 'loved', 'masterpiece']
        negative_words = ['disappointing', 'failed', 'bad', 'worst', 'broken', 'delayed', 'cancelled']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return gaming category links."""
        return [
            {
                'title': f"Gaming: {name}",
                'url': f'https://www.polygon.com/{slug}',
                'link': f'https://www.polygon.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Polygon',
                'data_type': 'gaming_category',
                'platform': 'polygon_gaming',
                'tags': ['gaming', 'videogames', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Latest Reviews', 'reviews', 'Game reviews and scores.'),
            ('PlayStation News', 'playstation', 'PS5 and Sony gaming news.'),
            ('Xbox News', 'xbox', 'Xbox and Game Pass updates.'),
            ('Nintendo News', 'nintendo', 'Switch and Nintendo coverage.'),
            ('PC Gaming', 'pc', 'PC gaming news and hardware.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.polygon.com/{category}',
                'link': f'https://www.polygon.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Polygon',
                'data_type': 'gaming_topic',
                'platform': 'polygon_gaming',
                'tags': ['gaming', 'videogames', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
