"""
Business News Spider - Business & Finance News Intelligence
============================================================

Session 534: Simplified to work with spider network interface.
Aggregates business news from major financial publications via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class BusinessNewsSpider:
    """Business news spider - finance, markets, and business news"""

    name = "business_news"

    # Business news RSS feeds
    RSS_FEEDS = {
        'harvard_business': 'https://hbr.org/resources/xml/rss/feed.xml',
        'forbes': 'https://www.forbes.com/innovation/feed/',
        'entrepreneur': 'https://www.entrepreneur.com/latest.rss',
        'inc': 'https://www.inc.com/rss/',
        'fast_company': 'https://www.fastcompany.com/latest/rss',
    }

    # Business categories for classification
    CATEGORIES = [
        ('Startups', 'startups', 'Startup and entrepreneurship news.'),
        ('Markets', 'markets', 'Stock market and trading news.'),
        ('Tech Business', 'tech_business', 'Technology business coverage.'),
        ('Leadership', 'leadership', 'Leadership and management news.'),
        ('Small Business', 'small_business', 'SMB growth and strategy.'),
        ('Economy', 'economy', 'Economic news and analysis.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.business_categories = {
            'startups': ['startup', 'founder', 'entrepreneur', 'seed', 'venture', 'launch'],
            'markets': ['stock', 'market', 'trading', 'investor', 'shares', 'dow', 'nasdaq'],
            'tech_business': ['tech', 'ai', 'software', 'saas', 'cloud', 'digital'],
            'leadership': ['ceo', 'leadership', 'management', 'executive', 'strategy'],
            'small_business': ['small business', 'smb', 'growth', 'revenue', 'profit'],
            'economy': ['economy', 'inflation', 'fed', 'interest rate', 'gdp', 'recession'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch business news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of article dictionaries
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
            logger.warning(f"Error getting business categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Business News spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from business RSS feed."""
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

                # Detect business category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': category,
                    'business_category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'business_article',
                    'platform': 'business_news',
                    'tags': ['business', 'finance', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect business category from text."""
        for category, keywords in self.business_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return business category exploration links."""
        return [
            {
                'title': f"Business News: {name}",
                'url': f'https://www.forbes.com/{slug}/',
                'link': f'https://www.forbes.com/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Business News',
                'data_type': 'business_category',
                'platform': 'business_news',
                'tags': ['business', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Startup News', 'startups', 'Entrepreneurship and startups.'),
            ('Market Watch', 'markets', 'Stock market updates.'),
            ('Tech Business', 'tech', 'Technology business news.'),
            ('Leadership', 'leadership', 'Business leadership insights.'),
            ('Economy', 'economy', 'Economic news and trends.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.forbes.com/{category}/',
                'link': f'https://www.forbes.com/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Business News',
                'data_type': 'business_topic',
                'platform': 'business_news',
                'tags': ['business', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
