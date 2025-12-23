"""
Sellfy Spider - Digital Products & POD Intelligence
====================================================

Session 534: Simplified to work with spider network interface.
Aggregates digital products and e-commerce creator content via RSS.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class SellfySpider:
    """Sellfy spider - digital products and POD intelligence"""

    name = "sellfy"

    # E-commerce and creator RSS feeds
    RSS_FEEDS = {
        'ecommerce_fuel': 'https://www.ecommercefuel.com/feed/',
        'practical_ecom': 'https://www.practicalecommerce.com/feed',
        'shopify_blog': 'https://www.shopify.com/blog/feed',
        'bigcommerce': 'https://www.bigcommerce.com/blog/feed/',
        'gumroad_blog': 'https://blog.gumroad.com/rss',
    }

    # Product categories
    CATEGORIES = [
        ('Digital Downloads', 'digital', 'Ebooks, courses, templates, and files.'),
        ('Print on Demand', 'pod', 'T-shirts, merch, and custom apparel.'),
        ('Subscriptions', 'subscriptions', 'Membership and recurring products.'),
        ('Music & Audio', 'music', 'Beats, samples, and audio products.'),
        ('Software', 'software', 'Plugins, apps, and digital tools.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.product_types = {
            'digital': ['digital', 'download', 'ebook', 'course', 'pdf', 'template'],
            'pod': ['print on demand', 'pod', 't-shirt', 'merch', 'apparel', 'printful'],
            'subscriptions': ['subscription', 'membership', 'recurring', 'monthly', 'patreon'],
            'music': ['music', 'beats', 'samples', 'audio', 'sound', 'loops'],
            'video': ['video', 'footage', 'tutorial', 'workshop', 'course'],
            'software': ['software', 'plugin', 'extension', 'app', 'tool', 'saas'],
        }
        self.selling_strategies = {
            'pricing': ['pricing', 'price', 'discount', 'bundle', 'tier'],
            'marketing': ['marketing', 'promotion', 'social', 'email', 'funnel'],
            'conversion': ['conversion', 'checkout', 'cart', 'upsell', 'cross-sell'],
            'branding': ['branding', 'design', 'storefront', 'logo', 'visual'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch digital products and creator content from RSS feeds.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of e-commerce content dictionaries
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
            logger.warning(f"Error getting product categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Sellfy spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch e-commerce content from RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Analysis
                text = f"{title} {description}".lower()
                product_type = self._detect_product_type(text)
                strategies = self._detect_strategies(text)
                is_creator_focused = self._is_creator_focused(text)
                sentiment = self._analyze_sentiment(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', ''),
                    'product_type': product_type,
                    'category': product_type,
                    'strategies': strategies,
                    'is_creator_focused': is_creator_focused,
                    'sentiment': sentiment,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'ecommerce_content',
                    'platform': 'sellfy',
                    'tags': ['ecommerce', 'digital products', product_type],
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

    def _detect_strategies(self, text: str) -> List[str]:
        """Detect selling strategies mentioned in text."""
        strategies = []
        for strategy, keywords in self.selling_strategies.items():
            if any(kw in text for kw in keywords):
                strategies.append(strategy)
        return strategies

    def _is_creator_focused(self, text: str) -> bool:
        """Check if content is creator/seller focused."""
        creator_keywords = ['creator', 'sell', 'product', 'store', 'shop', 'revenue', 'income', 'launch']
        return any(word in text for word in creator_keywords)

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze content sentiment."""
        positive = ['success', 'grow', 'increase', 'profit', 'launch', 'best', 'tips', 'guide']
        negative = ['fail', 'mistake', 'avoid', 'problem', 'issue', 'struggle']

        pos_count = sum(1 for word in positive if word in text)
        neg_count = sum(1 for word in negative if word in text)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return product category links."""
        return [
            {
                'title': f"Sellfy: {name}",
                'url': f'https://sellfy.com/{slug}/',
                'link': f'https://sellfy.com/{slug}/',
                'summary': desc,
                'description': desc,
                'category': slug,
                'product_type': slug,
                'source': 'Sellfy',
                'data_type': 'product_category',
                'platform': 'sellfy',
                'tags': ['ecommerce', 'digital products', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Digital Downloads Guide', 'digital', 'How to sell ebooks, courses, and files.'),
            ('Print on Demand', 'pod', 'T-shirt and merch selling strategies.'),
            ('Subscription Products', 'subscriptions', 'Building recurring revenue.'),
            ('Selling Music Online', 'music', 'Beats, samples, and audio products.'),
            ('Creator Economy', 'creator', 'Making money as a digital creator.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://sellfy.com/blog/{category}/',
                'link': f'https://sellfy.com/blog/{category}/',
                'summary': desc,
                'description': desc,
                'category': category,
                'product_type': category,
                'source': 'Sellfy',
                'data_type': 'ecommerce_topic',
                'platform': 'sellfy',
                'tags': ['ecommerce', 'digital products', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
