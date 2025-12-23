"""
Education Spider - Educational News & Resources
===============================================

Session 534: Simplified to work with spider network interface.
Aggregates education news from multiple sources via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class EducationRSSSpider:
    """Education news spider - K-12, higher ed, and edtech news"""

    name = "education_rss"

    # Education news RSS feeds
    RSS_FEEDS = {
        'ed_week': 'https://www.edweek.org/feed',
        'inside_higher_ed': 'https://www.insidehighered.com/rss/feed',
        'edsurge': 'https://www.edsurge.com/rss',
        'the_74': 'https://www.the74million.org/feed/',
        'edutopia': 'https://www.edutopia.org/rss.xml',
    }

    # Education categories
    CATEGORIES = [
        ('K-12 Education', 'k12', 'Elementary and secondary education news.'),
        ('Higher Ed', 'higher-ed', 'College and university news.'),
        ('EdTech', 'edtech', 'Education technology and tools.'),
        ('Policy', 'policy', 'Education policy and legislation.'),
        ('Teaching', 'teaching', 'Teaching methods and resources.'),
        ('STEM', 'stem', 'Science, technology, engineering, math.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.education_categories = {
            'k12': ['k-12', 'elementary', 'middle school', 'high school', 'students', 'teachers'],
            'higher_ed': ['college', 'university', 'higher education', 'degree', 'campus'],
            'edtech': ['edtech', 'online learning', 'e-learning', 'digital', 'platform'],
            'policy': ['policy', 'legislation', 'funding', 'budget', 'government'],
            'curriculum': ['curriculum', 'stem', 'math', 'reading', 'science', 'arts'],
            'special_ed': ['special education', 'disability', 'accommodations', 'iep'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch education news from RSS feeds.

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
            logger.warning(f"Error getting education categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Education spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from education RSS feed."""
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

                # Detect education category
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
                    'education_category': category,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'education_article',
                    'platform': 'education_rss',
                    'tags': ['education', 'learning', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect education category from text."""
        for category, keywords in self.education_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return education category links."""
        return [
            {
                'title': f"Education: {name}",
                'url': f'https://www.edweek.org/search?q={slug}',
                'link': f'https://www.edweek.org/search?q={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Education News',
                'data_type': 'education_category',
                'platform': 'education_rss',
                'tags': ['education', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('K-12 News', 'k12', 'Elementary and secondary education.'),
            ('Higher Education', 'higher-ed', 'College and university news.'),
            ('EdTech Tools', 'edtech', 'Education technology.'),
            ('Education Policy', 'policy', 'Legislation and funding.'),
            ('Teaching Resources', 'teaching', 'Methods and materials.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.edweek.org/{category}',
                'link': f'https://www.edweek.org/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Education News',
                'data_type': 'education_topic',
                'platform': 'education_rss',
                'tags': ['education', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
