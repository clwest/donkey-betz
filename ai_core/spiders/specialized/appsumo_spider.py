"""
AppSumo Spider - Digital Tool Deals & Product Launches Intelligence
======================================================================

Session 534: Simplified to work with spider network interface.
Uses product launch RSS feeds for software deals and SaaS trends.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AppSumoSpider:
    """AppSumo spider - digital tool deals and product launches intelligence"""

    name = "appsumo"

    # Product launch and deal RSS feeds
    RSS_FEEDS = {
        'product_hunt': 'https://www.producthunt.com/feed',
        'betalist': 'https://betalist.com/feed',
        'saas_weekly': 'https://saasweekly.io/feed/',
    }

    # AppSumo deal categories
    CATEGORIES = [
        ('Marketing Tools', 'marketing', 'SEO, email, and social media tools.'),
        ('Productivity', 'productivity', 'Project management and automation.'),
        ('Design Tools', 'design', 'Graphic and video design software.'),
        ('Development', 'development', 'Code, hosting, and API tools.'),
        ('AI Tools', 'ai', 'AI-powered software and automation.'),
        ('Business', 'business', 'CRM, finance, and operations.'),
        ('Lifetime Deals', 'lifetime-deals', 'One-time payment software deals.'),
        ('Plus Deals', 'plus', 'AppSumo Plus exclusive deals.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch software deals and product launches.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of deal and product dictionaries
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

        # Add deal category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting AppSumo categories: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"AppSumo spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch product launches from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Detect tool category and deal type
                text = f"{title} {description}".lower()
                category = self._detect_category(text)
                deal_type = self._detect_deal_type(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': category,
                    'deal_type': deal_type,
                    'is_lifetime_deal': 'lifetime' in deal_type,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'software_deal',
                    'platform': 'appsumo',
                    'tags': ['deals', 'saas', 'software', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect tool category from text."""
        categories = {
            'marketing': ['marketing', 'seo', 'email', 'social media', 'analytics'],
            'productivity': ['productivity', 'project', 'task', 'automation', 'workflow'],
            'design': ['design', 'graphic', 'video', 'photo', 'creative'],
            'development': ['development', 'code', 'api', 'hosting', 'database'],
            'ai': ['ai', 'gpt', 'chatbot', 'machine learning', 'automation'],
            'business': ['crm', 'sales', 'finance', 'hr', 'operations'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'general'

    def _detect_deal_type(self, text: str) -> str:
        """Detect deal type from text."""
        if any(kw in text for kw in ['lifetime', 'ltd', 'one-time', 'forever']):
            return 'lifetime'
        if any(kw in text for kw in ['discount', 'off', 'save', 'deal']):
            return 'discount'
        if any(kw in text for kw in ['launch', 'new', 'introducing', 'announcing']):
            return 'new_launch'
        return 'standard'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return AppSumo category links."""
        return [
            {
                'title': f"AppSumo: {name}",
                'url': f'https://appsumo.com/browse/?category={slug}',
                'link': f'https://appsumo.com/browse/?category={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'AppSumo',
                'data_type': 'deal_category',
                'platform': 'appsumo',
                'tags': ['deals', 'appsumo', 'saas', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Lifetime Deals', 'lifetime', 'Pay once, use forever software.'),
            ('AI Tools', 'ai-tools', 'AI-powered productivity tools.'),
            ('Marketing Stack', 'marketing', 'Essential marketing software.'),
            ('Developer Tools', 'dev-tools', 'APIs and development utilities.'),
            ('Hot Deals', 'hot', 'Trending software deals.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://appsumo.com/browse/?tag={category}',
                'link': f'https://appsumo.com/browse/?tag={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'AppSumo',
                'data_type': 'deal_topic',
                'platform': 'appsumo',
                'tags': ['deals', 'appsumo', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
