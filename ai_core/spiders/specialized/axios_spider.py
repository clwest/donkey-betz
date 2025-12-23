"""
Axios Spider - Concise Business & Tech News Intelligence
========================================================

Session 534: Simplified to work with spider network interface.
Uses Axios RSS feeds for "Smart Brevity" news summaries.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AxiosSpider:
    """Axios news spider - concise business and tech news"""

    name = "axios"

    # Axios RSS feeds by section
    RSS_FEEDS = {
        'main': 'https://api.axios.com/feed/',
        'technology': 'https://api.axios.com/feed/technology',
        'business': 'https://api.axios.com/feed/business',
        'markets': 'https://api.axios.com/feed/markets',
    }

    # News sections
    SECTIONS = [
        ('Technology', 'technology', 'Tech industry news and analysis.'),
        ('Business', 'business', 'Business and corporate news.'),
        ('Markets', 'markets', 'Stock market and financial news.'),
        ('Politics', 'politics', 'Political news and policy.'),
        ('Climate', 'climate', 'Climate and energy news.'),
        ('Healthcare', 'healthcare', 'Health industry coverage.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news from Axios RSS feeds.

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

        # Add section links
        try:
            sections = self._get_section_links()
            all_items.extend(sections)
        except Exception as e:
            logger.warning(f"Error getting Axios sections: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Axios spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from Axios RSS feed."""
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

                # Detect category from content
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                impact = self._detect_impact(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Axios'),
                    'category': category,
                    'section': feed_name,
                    'impact_level': impact,
                    'source': 'Axios',
                    'data_type': 'news_article',
                    'platform': 'axios',
                    'tags': ['news', 'axios', 'business', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect article category from text."""
        categories = {
            'technology': ['tech', 'software', 'app', 'digital', 'internet', 'cyber'],
            'ai': ['ai', 'artificial intelligence', 'chatgpt', 'openai', 'machine learning'],
            'business': ['business', 'company', 'corporate', 'ceo', 'executive'],
            'markets': ['market', 'stock', 'trading', 'investor', 'wall street'],
            'policy': ['policy', 'regulation', 'government', 'congress', 'law'],
            'climate': ['climate', 'energy', 'renewable', 'ev', 'sustainability'],
            'healthcare': ['health', 'medical', 'pharma', 'drug', 'fda'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'general'

    def _detect_impact(self, text: str) -> str:
        """Detect news impact level."""
        if any(kw in text for kw in ['breaking', 'exclusive', 'first', 'major', 'unprecedented']):
            return 'high'
        if any(kw in text for kw in ['significant', 'important', 'notable', 'new']):
            return 'medium'
        return 'low'

    def _get_section_links(self) -> List[Dict[str, Any]]:
        """Return Axios section links."""
        return [
            {
                'title': f"Axios: {name}",
                'url': f'https://www.axios.com/{slug}',
                'link': f'https://www.axios.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Axios',
                'data_type': 'news_section',
                'platform': 'axios',
                'tags': ['news', 'axios', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.SECTIONS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Tech News', 'technology', 'Technology industry updates.'),
            ('Business News', 'business', 'Corporate and business news.'),
            ('Market Updates', 'markets', 'Financial market coverage.'),
            ('Policy & Politics', 'politics', 'Government and policy news.'),
            ('Climate & Energy', 'climate', 'Sustainability coverage.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.axios.com/{category}',
                'link': f'https://www.axios.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Axios',
                'data_type': 'news_topic',
                'platform': 'axios',
                'tags': ['news', 'axios', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
