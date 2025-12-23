"""
Government Spider - Government News & Policy Intelligence
==========================================================

Session 534: Simplified to work with spider network interface.
Aggregates government news, policy updates, and economic data.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class GovernmentSpider:
    """Government news spider - federal agencies, policy, and economic data"""

    name = "government"

    # Government RSS feeds
    RSS_FEEDS = {
        'whitehouse': 'https://www.whitehouse.gov/feed/',
        'usa_gov': 'https://www.usa.gov/rss/updates.xml',
        'federal_register': 'https://www.federalregister.gov/documents/current.rss',
        'bls': 'https://www.bls.gov/feed/bls_latest.rss',
        'sec_news': 'https://www.sec.gov/news/pressreleases.rss',
        'ftc': 'https://www.ftc.gov/news-events/rss/press-releases.xml',
        'sba': 'https://www.sba.gov/feeds/sba-news',
    }

    # Government categories
    CATEGORIES = [
        ('Policy', 'policy', 'Policy and legislation news.'),
        ('Economic', 'economic', 'Economic data and reports.'),
        ('Regulatory', 'regulatory', 'Regulatory updates.'),
        ('Small Business', 'small_business', 'SBA and small business news.'),
        ('Consumer', 'consumer', 'Consumer protection news.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.gov_categories = {
            'economic': ['economic', 'employment', 'jobs', 'unemployment', 'gdp', 'inflation'],
            'regulatory': ['regulation', 'rule', 'compliance', 'enforcement', 'fine', 'penalty'],
            'policy': ['policy', 'legislation', 'bill', 'law', 'act', 'executive order'],
            'small_business': ['small business', 'entrepreneur', 'sba', 'loan', 'grant'],
            'trade': ['trade', 'tariff', 'import', 'export', 'commerce'],
            'consumer': ['consumer', 'protection', 'safety', 'recall', 'warning'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch government news and data from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of government content dictionaries
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
            logger.warning(f"Error getting government categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Government spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from government RSS feed."""
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

                # Detect government category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'gov_category': category,
                    'category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'government_news',
                    'platform': 'government',
                    'tags': ['government', 'policy', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect government category from text."""
        for category, keywords in self.gov_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return government category links."""
        return [
            {
                'title': f"Government: {name}",
                'url': f'https://www.usa.gov/{slug}',
                'link': f'https://www.usa.gov/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'USA.gov',
                'data_type': 'gov_category',
                'platform': 'government',
                'tags': ['government', 'policy', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Federal Policy News', 'policy', 'Policy and legislation updates.'),
            ('Economic Indicators', 'economic', 'Economic data from federal agencies.'),
            ('Regulatory Updates', 'regulatory', 'Federal regulatory news.'),
            ('Small Business Resources', 'small_business', 'SBA news and resources.'),
            ('Consumer Protection', 'consumer', 'Consumer safety and protection.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.usa.gov/{category}',
                'link': f'https://www.usa.gov/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'USA.gov',
                'data_type': 'gov_topic',
                'platform': 'government',
                'tags': ['government', 'federal', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
