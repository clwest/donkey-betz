"""
NPR Spider - National Public Radio News Intelligence
=====================================================

Session 534: Simplified to work with spider network interface.
Aggregates NPR news content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class NPRSpider:
    """NPR news spider - comprehensive news coverage across all topics"""

    name = "npr"

    # NPR RSS feeds by topic
    RSS_FEEDS = {
        'top_stories': 'https://feeds.npr.org/1001/rss.xml',
        'world': 'https://feeds.npr.org/1004/rss.xml',
        'national': 'https://feeds.npr.org/1003/rss.xml',
        'politics': 'https://feeds.npr.org/1014/rss.xml',
        'business': 'https://feeds.npr.org/1006/rss.xml',
        'technology': 'https://feeds.npr.org/1019/rss.xml',
        'science': 'https://feeds.npr.org/1007/rss.xml',
        'health': 'https://feeds.npr.org/1128/rss.xml',
    }

    # News categories
    CATEGORIES = [
        ('World News', 'world', 'International news coverage.'),
        ('Politics', 'politics', 'Political news and analysis.'),
        ('Business', 'business', 'Business and economy news.'),
        ('Technology', 'technology', 'Tech news and innovation.'),
        ('Science', 'science', 'Science and research news.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.topic_categories = {
            'technology': ['tech', 'software', 'ai', 'computer', 'digital', 'internet', 'cyber'],
            'business': ['economy', 'market', 'company', 'industry', 'trade', 'finance', 'stock'],
            'politics': ['congress', 'president', 'election', 'vote', 'bill', 'senate', 'house'],
            'science': ['research', 'study', 'scientist', 'discovery', 'space', 'climate'],
            'health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'treatment'],
            'world': ['international', 'global', 'foreign', 'country', 'nation', 'world'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch NPR news content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of news content dictionaries
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
            logger.warning(f"Error getting NPR categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"NPR spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from NPR RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                if summary:
                    summary = re.sub(r'<[^>]+>', '', summary)[:500]

                # Detect news categories
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
                    'author': entry.get('author', 'NPR'),
                    'categories': categories,
                    'category': categories[0] if categories else feed_name,
                    'feed_source': feed_name,
                    'sentiment': sentiment,
                    'source': 'NPR',
                    'data_type': 'news',
                    'platform': 'npr',
                    'tags': ['npr', 'news'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect news categories from text."""
        categories = []
        for cat, keywords in self.topic_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(cat)
        return categories if categories else ['general']

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze news sentiment."""
        positive_words = ['success', 'win', 'gain', 'improve', 'grow', 'progress', 'breakthrough']
        negative_words = ['fail', 'loss', 'decline', 'crisis', 'concern', 'threat', 'problem']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return NPR category links."""
        return [
            {
                'title': f"NPR: {name}",
                'url': f'https://www.npr.org/sections/{slug}',
                'link': f'https://www.npr.org/sections/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'NPR',
                'data_type': 'news_category',
                'platform': 'npr',
                'tags': ['npr', 'news', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Top Stories', 'news', 'NPR top stories.'),
            ('World News', 'world', 'International coverage.'),
            ('Politics', 'politics', 'Political news and analysis.'),
            ('Business', 'business', 'Economy and business news.'),
            ('Technology', 'technology', 'Tech news and innovation.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.npr.org/sections/{category}',
                'link': f'https://www.npr.org/sections/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'NPR',
                'data_type': 'news_topic',
                'platform': 'npr',
                'tags': ['npr', 'news', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
