"""
LemonSqueezy Spider - SaaS & Digital Product Sales Intelligence
==================================================================

Session 534: Simplified to work with spider network interface.
Aggregates SaaS and creator economy content via RSS feeds.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class LemonSqueezySpider:
    """LemonSqueezy spider - SaaS and digital product sales intelligence"""

    name = "lemonsqueezy"

    # SaaS and creator economy RSS feeds
    RSS_FEEDS = {
        'indie_hackers': 'https://www.indiehackers.com/feed.xml',
        'saas_weekly': 'https://saasweekly.com/feed/',
        'bootstrapped_founder': 'https://thebootstrappedfounder.com/feed/',
        'microconf': 'https://www.microconf.com/feed/',
        'product_hunt': 'https://www.producthunt.com/feed',
    }

    # Product categories
    CATEGORIES = [
        ('SaaS', 'saas', 'Software as a service products.'),
        ('Courses', 'courses', 'Online courses and education.'),
        ('Templates', 'templates', 'Digital templates and assets.'),
        ('Memberships', 'memberships', 'Subscription communities.'),
        ('Ebooks', 'ebooks', 'Digital books and guides.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.product_types = {
            'saas': ['saas', 'software', 'app', 'tool', 'platform', 'subscription'],
            'courses': ['course', 'workshop', 'bootcamp', 'training', 'education'],
            'ebooks': ['ebook', 'book', 'guide', 'pdf', 'handbook'],
            'templates': ['template', 'notion', 'figma', 'airtable', 'spreadsheet'],
            'memberships': ['membership', 'community', 'access', 'exclusive'],
            'licenses': ['license', 'commercial', 'extended', 'lifetime'],
        }
        self.business_topics = {
            'monetization': ['monetization', 'revenue', 'income', 'profit', 'mrr'],
            'marketing': ['marketing', 'launch', 'promotion', 'audience', 'growth'],
            'payments': ['payment', 'stripe', 'checkout', 'pricing', 'billing'],
            'analytics': ['analytics', 'metrics', 'conversion', 'churn', 'retention'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch SaaS and creator economy content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of SaaS/creator content dictionaries
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
            logger.warning(f"Error getting SaaS categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"LemonSqueezy spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from SaaS/creator RSS feed."""
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

                # Detect product type and business topics
                text = f"{title} {summary}".lower()
                product_type = self._detect_product_type(text)
                topics = self._detect_business_topics(text)
                is_digital_product = self._is_digital_product(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'product_type': product_type,
                    'category': product_type,
                    'business_topics': topics,
                    'is_digital_product': is_digital_product,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'digital_sales',
                    'platform': 'lemonsqueezy',
                    'tags': ['lemonsqueezy', 'saas', product_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_product_type(self, text: str) -> str:
        """Detect product type from text."""
        for ptype, keywords in self.product_types.items():
            if any(kw in text for kw in keywords):
                return ptype
        return 'general'

    def _detect_business_topics(self, text: str) -> List[str]:
        """Detect business topics from text."""
        topics = []
        for topic, keywords in self.business_topics.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        return topics

    def _is_digital_product(self, text: str) -> bool:
        """Check if content discusses digital products."""
        digital_keywords = ['digital', 'product', 'saas', 'subscription', 'download', 'online']
        return any(kw in text for kw in digital_keywords)

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return SaaS category links."""
        return [
            {
                'title': f"LemonSqueezy: {name}",
                'url': f'https://www.lemonsqueezy.com/discover/{slug}',
                'link': f'https://www.lemonsqueezy.com/discover/{slug}',
                'summary': desc,
                'description': desc,
                'product_type': slug,
                'category': slug,
                'source': 'LemonSqueezy',
                'data_type': 'saas_category',
                'platform': 'lemonsqueezy',
                'tags': ['lemonsqueezy', 'saas', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('SaaS Products', 'saas', 'Software subscription products.'),
            ('Digital Courses', 'courses', 'Online learning and education.'),
            ('Templates & Assets', 'templates', 'Digital templates and resources.'),
            ('Membership Sites', 'memberships', 'Community subscriptions.'),
            ('Creator Economy', 'creator', 'Creator monetization strategies.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.indiehackers.com/groups/{category}',
                'link': f'https://www.indiehackers.com/groups/{category}',
                'summary': desc,
                'description': desc,
                'product_type': category,
                'category': category,
                'source': 'LemonSqueezy',
                'data_type': 'saas_topic',
                'platform': 'lemonsqueezy',
                'tags': ['lemonsqueezy', 'saas', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
