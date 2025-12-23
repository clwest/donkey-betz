"""
Parenting Spider - Parenting & Family Resources
===============================================

Session 534: Simplified to work with spider network interface.
Aggregates parenting, family, and childcare content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ParentingSpider:
    """Parenting spider - family, childcare, and parenting resources"""

    name = "parenting"

    # Parenting and family RSS feeds
    RSS_FEEDS = {
        'parents_magazine': 'https://www.parents.com/syndication/rss/',
        'scary_mommy': 'https://www.scarymommy.com/feed/',
        'fatherly': 'https://www.fatherly.com/feed/',
        'motherly': 'https://www.mother.ly/feed/',
        'today_parents': 'https://www.today.com/parents/rss',
    }

    # Parenting categories
    CATEGORIES = [
        ('Babies', 'babies', 'Infant and newborn care.'),
        ('Toddlers', 'toddlers', 'Toddler development and behavior.'),
        ('Kids', 'kids', 'Children and school-age topics.'),
        ('Teens', 'teens', 'Teenager parenting.'),
        ('Health', 'health', 'Child health and wellness.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.parenting_categories = {
            'babies': ['baby', 'infant', 'newborn', 'nursing', 'breastfeeding', 'formula'],
            'toddlers': ['toddler', 'potty', 'tantrum', 'walking', 'talking'],
            'kids': ['kids', 'children', 'school', 'homework', 'activities'],
            'teens': ['teen', 'teenager', 'adolescent', 'puberty', 'high school'],
            'sleep': ['sleep', 'bedtime', 'nap', 'night', 'routine'],
            'education': ['learning', 'reading', 'education', 'school', 'preschool'],
            'health': ['health', 'pediatric', 'vaccine', 'illness', 'doctor'],
            'activities': ['play', 'game', 'activity', 'craft', 'toy', 'outdoor'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch parenting and family content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of parenting content dictionaries
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
            logger.warning(f"Error getting parenting categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Parenting spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from parenting RSS feed."""
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

                # Detect parenting categories
                text = f"{title} {summary}".lower()
                categories = self._detect_categories(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'categories': categories,
                    'category': categories[0] if categories else 'general',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'parenting_content',
                    'platform': 'parenting',
                    'tags': ['parenting', 'family'] + categories[:2],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_categories(self, text: str) -> List[str]:
        """Detect parenting categories from text."""
        categories = []
        for cat, keywords in self.parenting_categories.items():
            if any(kw in text for kw in keywords):
                categories.append(cat)
        return categories if categories else ['general']

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return parenting category links."""
        return [
            {
                'title': f"Parenting: {name}",
                'url': f'https://www.parents.com/{slug}',
                'link': f'https://www.parents.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Parenting',
                'data_type': 'parenting_category',
                'platform': 'parenting',
                'tags': ['parenting', 'family', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Baby Care', 'babies', 'Infant care and development.'),
            ('Toddler Tips', 'toddlers', 'Toddler behavior and milestones.'),
            ('School-Age Kids', 'kids', 'Activities and education.'),
            ('Teen Parenting', 'teens', 'Teenager guidance.'),
            ('Child Health', 'health', 'Pediatric health and wellness.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.parents.com/{category}',
                'link': f'https://www.parents.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Parenting',
                'data_type': 'parenting_topic',
                'platform': 'parenting',
                'tags': ['parenting', 'family', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
