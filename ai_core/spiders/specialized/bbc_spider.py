"""
BBC Spider - BBC World News Intelligence
=========================================

Session 534: Simplified to work with spider network interface.
Uses BBC RSS feeds for comprehensive international news coverage.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class BBCSpider:
    """BBC news spider - international news coverage"""

    name = "bbc"

    # BBC RSS feeds by section
    RSS_FEEDS = {
        'top_stories': 'https://feeds.bbci.co.uk/news/rss.xml',
        'world': 'https://feeds.bbci.co.uk/news/world/rss.xml',
        'business': 'https://feeds.bbci.co.uk/news/business/rss.xml',
        'technology': 'https://feeds.bbci.co.uk/news/technology/rss.xml',
        'science': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
        'entertainment': 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
        'health': 'https://feeds.bbci.co.uk/news/health/rss.xml',
        'us_canada': 'https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml',
        'europe': 'https://feeds.bbci.co.uk/news/world/europe/rss.xml',
        'asia': 'https://feeds.bbci.co.uk/news/world/asia/rss.xml',
    }

    # News sections
    SECTIONS = [
        ('World News', 'world', 'International news coverage.'),
        ('Business', 'business', 'Business and economics.'),
        ('Technology', 'technology', 'Tech news and analysis.'),
        ('Science', 'science_and_environment', 'Science and environment.'),
        ('Health', 'health', 'Health news and research.'),
        ('Entertainment', 'entertainment_and_arts', 'Entertainment and arts.'),
        ('US & Canada', 'world/us_and_canada', 'North American news.'),
        ('Europe', 'world/europe', 'European news.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch news from BBC RSS feeds.

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
            logger.warning(f"Error getting BBC sections: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"BBC spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from BBC RSS feed."""
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

                # Detect category from content
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': 'BBC News',
                    'category': category,
                    'section': feed_name,
                    'source': 'BBC News',
                    'data_type': 'news_article',
                    'platform': 'bbc',
                    'tags': ['news', 'bbc', 'international', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect article category from text."""
        categories = {
            'technology': ['tech', 'software', 'ai', 'computer', 'digital', 'cyber'],
            'business': ['economy', 'market', 'company', 'industry', 'trade', 'finance'],
            'politics': ['government', 'minister', 'election', 'vote', 'parliament'],
            'science': ['research', 'study', 'scientist', 'discovery', 'space', 'nasa'],
            'health': ['health', 'medical', 'nhs', 'hospital', 'disease', 'vaccine'],
            'international': ['ukraine', 'russia', 'china', 'us', 'eu', 'un', 'nato'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'general'

    def _get_section_links(self) -> List[Dict[str, Any]]:
        """Return BBC section links."""
        return [
            {
                'title': f"BBC: {name}",
                'url': f'https://www.bbc.com/news/{slug}',
                'link': f'https://www.bbc.com/news/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug.split('/')[-1] if '/' in slug else slug,
                'source': 'BBC News',
                'data_type': 'news_section',
                'platform': 'bbc',
                'tags': ['news', 'bbc', slug.split('/')[-1]],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.SECTIONS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('World News', 'world', 'Global news coverage.'),
            ('Business', 'business', 'Business and economics.'),
            ('Technology', 'technology', 'Tech news and analysis.'),
            ('Science', 'science', 'Science and environment.'),
            ('Health', 'health', 'Health news and research.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.bbc.com/news/{category}',
                'link': f'https://www.bbc.com/news/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'BBC News',
                'data_type': 'news_topic',
                'platform': 'bbc',
                'tags': ['news', 'bbc', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
