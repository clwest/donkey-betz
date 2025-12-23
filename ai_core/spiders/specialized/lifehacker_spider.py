"""
Lifehacker Spider - Productivity & Life Tips
============================================

Session 534: Simplified to work with spider network interface.
Aggregates productivity and lifestyle tips via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class LifehackerSpider:
    """Lifehacker spider - productivity tips and life hacks"""

    name = "lifehacker"

    # Productivity and lifestyle RSS feeds
    RSS_FEEDS = {
        'lifehacker': 'https://lifehacker.com/rss',
        'zen_habits': 'https://zenhabits.net/feed/',
        'productivity_blog': 'https://www.productivitygame.com/feed/',
        'asian_efficiency': 'https://www.asianefficiency.com/feed/',
    }

    # Productivity categories
    CATEGORIES = [
        ('Productivity', 'productivity', 'Time management and efficiency.'),
        ('Tech', 'tech', 'Technology tips and tools.'),
        ('Money', 'money', 'Finance and budgeting.'),
        ('Health', 'health', 'Fitness and wellness.'),
        ('Work', 'work', 'Career and job tips.'),
        ('Home', 'home', 'Home organization and DIY.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.topic_categories = {
            'productivity': ['productivity', 'efficiency', 'workflow', 'time management', 'organize'],
            'tech': ['tech', 'app', 'software', 'tool', 'device', 'gadget'],
            'money': ['money', 'finance', 'budget', 'save', 'invest', 'credit', 'debt'],
            'health': ['health', 'fitness', 'exercise', 'diet', 'sleep', 'mental health'],
            'work': ['work', 'career', 'job', 'office', 'remote', 'interview'],
            'home': ['home', 'cleaning', 'cooking', 'diy', 'kitchen', 'garden'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch productivity and lifestyle content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of productivity content dictionaries
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
            logger.warning(f"Error getting productivity categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Lifehacker spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from productivity RSS feed."""
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

                # Detect topic category
                text = f"{title} {summary}".lower()
                categories = self._detect_categories(text)
                is_actionable = self._is_actionable_tip(text)

                # Extract tags from feed entry
                entry_tags = []
                if hasattr(entry, 'tags'):
                    entry_tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')][:5]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Lifehacker'),
                    'categories': categories,
                    'category': categories[0] if categories else 'general',
                    'is_actionable': is_actionable,
                    'entry_tags': entry_tags,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'lifestyle',
                    'platform': 'lifehacker',
                    'tags': ['lifehacker', 'productivity'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect topic categories from text."""
        categories = []
        for cat, keywords in self.topic_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(cat)
        return categories if categories else ['general']

    def _is_actionable_tip(self, text: str) -> bool:
        """Check if content contains actionable tips."""
        action_keywords = ['how to', 'tips', 'ways to', 'steps', 'guide', 'tutorial', 'hack']
        return any(kw in text for kw in action_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return productivity category links."""
        return [
            {
                'title': f"Tips: {name}",
                'url': f'https://lifehacker.com/c/{slug}',
                'link': f'https://lifehacker.com/c/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Lifehacker',
                'data_type': 'lifestyle_category',
                'platform': 'lifehacker',
                'tags': ['lifehacker', 'productivity', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Productivity Tips', 'productivity', 'Time management and efficiency.'),
            ('Tech Hacks', 'tech', 'Technology tips and tools.'),
            ('Money Advice', 'money', 'Financial tips and budgeting.'),
            ('Health & Fitness', 'health', 'Wellness and exercise tips.'),
            ('Career Tips', 'work', 'Job and career advice.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://lifehacker.com/c/{category}',
                'link': f'https://lifehacker.com/c/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Lifehacker',
                'data_type': 'lifestyle_topic',
                'platform': 'lifehacker',
                'tags': ['lifehacker', 'productivity', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
