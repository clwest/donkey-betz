"""
Content Monetization Spider - Creator Economy Intelligence
===========================================================

Session 534: Simplified to work with spider network interface.
Uses RSS feeds from creator economy platforms and newsletters.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ContentMonetizationSpider:
    """Content monetization spider - creator economy intelligence"""

    name = "content_monetization"

    # Creator economy RSS feeds
    RSS_FEEDS = {
        'creator_economy': 'https://creatoreconomy.so/feed',
        'substack_feed': 'https://on.substack.com/feed',
        'product_hunt': 'https://www.producthunt.com/feed',
        'indie_hackers': 'https://www.indiehackers.com/feed.xml',
    }

    # Monetization platforms
    PLATFORMS = [
        ('Substack', 'substack', 'Newsletter subscriptions and paid content.'),
        ('Patreon', 'patreon', 'Membership and exclusive content.'),
        ('Ko-fi', 'kofi', 'Tips, donations, and commissions.'),
        ('Gumroad', 'gumroad', 'Digital products and courses.'),
        ('Product Hunt', 'producthunt', 'Product launches and discovery.'),
        ('Buy Me a Coffee', 'buymeacoffee', 'Tips and memberships.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.monetization_types = {
            'subscriptions': ['subscription', 'subscriber', 'newsletter', 'paid', 'member'],
            'tips': ['tip', 'coffee', 'donation', 'support', 'ko-fi'],
            'products': ['product', 'course', 'ebook', 'digital', 'gumroad', 'template'],
            'launches': ['launch', 'product hunt', 'ship', 'new product', 'introducing'],
            'membership': ['membership', 'patron', 'exclusive', 'community', 'access'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch creator economy content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of content dictionaries
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

        # Add platform links
        try:
            platforms = self._get_platform_links()
            all_items.extend(platforms)
        except Exception as e:
            logger.warning(f"Error getting monetization platforms: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Content Monetization spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from creator economy RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect monetization type
                text = f"{title} {summary}".lower()
                monetization_type = self._detect_monetization_type(text)
                platform = self._detect_platform(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': monetization_type,
                    'monetization_type': monetization_type,
                    'platform_detected': platform,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'creator_content',
                    'platform': 'content_monetization',
                    'tags': ['creator', 'monetization', monetization_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_monetization_type(self, text: str) -> str:
        """Detect monetization type from text."""
        for mtype, keywords in self.monetization_types.items():
            if any(kw in text for kw in keywords):
                return mtype
        return 'general'

    def _detect_platform(self, text: str) -> str:
        """Detect monetization platform from text."""
        platforms = {
            'substack': ['substack', 'newsletter'],
            'patreon': ['patreon', 'patron'],
            'gumroad': ['gumroad'],
            'kofi': ['ko-fi', 'kofi', 'coffee'],
            'producthunt': ['product hunt', 'producthunt'],
        }
        for platform, keywords in platforms.items():
            if any(kw in text for kw in keywords):
                return platform
        return 'general'

    def _get_platform_links(self) -> List[Dict[str, Any]]:
        """Return monetization platform links."""
        return [
            {
                'title': f"Creator Platform: {name}",
                'url': f'https://www.{slug}.com/',
                'link': f'https://www.{slug}.com/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Content Monetization',
                'data_type': 'monetization_platform',
                'platform': 'content_monetization',
                'tags': ['creator', 'monetization', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.PLATFORMS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Newsletter Monetization', 'newsletters', 'Paid newsletter strategies.'),
            ('Digital Products', 'products', 'Selling digital products online.'),
            ('Membership Sites', 'membership', 'Building paid communities.'),
            ('Creator Tools', 'tools', 'Tools for content creators.'),
            ('Product Launches', 'launches', 'Launching products successfully.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://creatoreconomy.so/{category}',
                'link': f'https://creatoreconomy.so/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Content Monetization',
                'data_type': 'monetization_topic',
                'platform': 'content_monetization',
                'tags': ['creator', 'monetization', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
