"""
Health Spider - Medical & Health News Intelligence
===================================================

Session 534: Simplified to work with spider network interface.
Aggregates health news from trusted medical sources via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class HealthSpider:
    """Health news spider - medical research, wellness, and health news"""

    name = "health"

    # Health RSS feeds
    RSS_FEEDS = {
        'webmd': 'https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC',
        'nih_news': 'https://www.nih.gov/news-events/news-releases/feed',
        'medical_news_today': 'https://www.medicalnewstoday.com/rss',
        'healthline': 'https://www.healthline.com/rss',
        'mayo_clinic': 'https://newsnetwork.mayoclinic.org/feed/',
        'harvard_health': 'https://www.health.harvard.edu/blog/feed',
    }

    # Health categories
    CATEGORIES = [
        ('Mental Health', 'mental_health', 'Mental wellness and psychology.'),
        ('Nutrition', 'nutrition', 'Diet and healthy eating.'),
        ('Fitness', 'fitness', 'Exercise and physical wellness.'),
        ('Disease', 'disease', 'Medical conditions and research.'),
        ('Wellness', 'wellness', 'General health and prevention.'),
        ('Medication', 'medication', 'Drugs and treatments.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.health_categories = {
            'mental_health': ['mental', 'anxiety', 'depression', 'stress', 'therapy', 'psychology'],
            'nutrition': ['nutrition', 'diet', 'vitamin', 'food', 'eating', 'weight'],
            'fitness': ['exercise', 'fitness', 'workout', 'physical activity', 'gym'],
            'disease': ['disease', 'cancer', 'diabetes', 'heart', 'alzheimer', 'infection'],
            'medication': ['drug', 'medication', 'treatment', 'therapy', 'fda', 'vaccine'],
            'wellness': ['wellness', 'sleep', 'lifestyle', 'healthy', 'prevention'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch health news from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of health content dictionaries
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
            logger.warning(f"Error getting health categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Health spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from health RSS feed."""
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

                # Detect health category
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                categories = self._detect_all_categories(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'category': category,
                    'health_categories': categories,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'health_news',
                    'platform': 'health',
                    'tags': ['health', 'medical', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect primary health category from text."""
        for category, keywords in self.health_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_all_categories(self, text: str) -> List[str]:
        """Detect all applicable health categories from text."""
        categories = []
        for category, keywords in self.health_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        return categories if categories else ['general']

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return health category links."""
        return [
            {
                'title': f"Health: {name}",
                'url': f'https://www.webmd.com/{slug}',
                'link': f'https://www.webmd.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Health',
                'data_type': 'health_category',
                'platform': 'health',
                'tags': ['health', 'medical', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Mental Health News', 'mental_health', 'Mental wellness updates.'),
            ('Nutrition & Diet', 'nutrition', 'Healthy eating news.'),
            ('Fitness & Exercise', 'fitness', 'Workout and fitness tips.'),
            ('Medical Research', 'research', 'Latest medical research.'),
            ('Wellness Tips', 'wellness', 'General health and wellness.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.webmd.com/{category}',
                'link': f'https://www.webmd.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Health',
                'data_type': 'health_topic',
                'platform': 'health',
                'tags': ['health', 'medical', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
