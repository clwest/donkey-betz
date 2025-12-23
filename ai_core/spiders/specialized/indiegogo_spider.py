"""
Indiegogo Spider - Crowdfunding & Innovation Intelligence
==========================================================

Session 534: Simplified to work with spider network interface.
Uses crowdfunding news RSS feeds since Indiegogo has no public API.
"""

import feedparser
import requests
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class IndiegogoSpider:
    """Indiegogo spider - crowdfunding news and innovation trends"""

    name = "indiegogo"

    # Crowdfunding news RSS feeds
    RSS_FEEDS = {
        'crowdfund_insider': 'https://www.crowdfundinsider.com/feed/',
        'product_hunt': 'https://www.producthunt.com/feed',
    }

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch crowdfunding news and innovation content.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of crowdfunding/innovation dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name, max_per_feed=max_results // 2)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add Indiegogo category topics
        try:
            categories = self._fetch_indiegogo_categories()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error fetching Indiegogo categories: {e}")

        # If all feeds fail, return curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Indiegogo spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str, max_per_feed: int = 25) -> List[Dict[str, Any]]:
        """Fetch items from an RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:max_per_feed]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')
                description = entry.get('summary', entry.get('description', ''))
                if description:
                    description = re.sub(r'<[^>]+>', '', description)[:500]

                # Detect category
                category = self._detect_category(f"{title} {description}".lower())

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': category,
                    'feed_source': feed_name,
                    'source': 'Crowdfunding News',
                    'data_type': 'crowdfunding_news',
                    'tags': ['crowdfunding', 'innovation', 'startups', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS feed {feed_url}: {e}")

        return items

    def _fetch_indiegogo_categories(self) -> List[Dict[str, Any]]:
        """Return Indiegogo category exploration links."""
        categories = [
            ('Tech & Innovation', 'tech-innovation', 'Innovative technology and gadgets.'),
            ('Audio', 'audio', 'Speakers, headphones, and audio gear.'),
            ('Camera Gear', 'camera-gear', 'Photography and video equipment.'),
            ('Home', 'home', 'Smart home and household products.'),
            ('Travel & Outdoors', 'travel-outdoors', 'Travel gear and outdoor equipment.'),
            ('Health & Fitness', 'health-fitness', 'Wellness and fitness products.'),
            ('Phones & Accessories', 'phones-accessories', 'Mobile devices and accessories.'),
            ('Productivity', 'productivity', 'Tools for work and productivity.'),
        ]

        return [
            {
                'title': f"Indiegogo: {title}",
                'url': f'https://www.indiegogo.com/explore/{slug}',
                'link': f'https://www.indiegogo.com/explore/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Indiegogo',
                'data_type': 'crowdfunding_category',
                'tags': ['crowdfunding', 'indiegogo', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for title, slug, desc in categories
        ]

    def _detect_category(self, text: str) -> str:
        """Detect crowdfunding category from text."""
        categories = {
            'tech': ['tech', 'gadget', 'device', 'smart', 'ai', 'robot'],
            'audio': ['speaker', 'headphone', 'earbuds', 'audio', 'music'],
            'home': ['home', 'kitchen', 'furniture', 'household'],
            'outdoor': ['outdoor', 'camping', 'travel', 'adventure'],
            'health': ['health', 'fitness', 'wellness', 'medical'],
            'sustainable': ['sustainable', 'eco', 'green', 'solar'],
            'gaming': ['game', 'gaming', 'console', 'esports'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'innovation'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated crowdfunding topics when feeds fail."""
        topics = [
            ('Tech Gadgets', 'tech', 'Innovative technology products and gadgets.'),
            ('Smart Home', 'home', 'Connected home devices and automation.'),
            ('Sustainable Products', 'sustainable', 'Eco-friendly and sustainable innovations.'),
            ('Health & Wellness', 'health', 'Fitness trackers and health devices.'),
            ('Audio Equipment', 'audio', 'Speakers, headphones, and audio gear.'),
            ('Travel Gear', 'outdoor', 'Travel accessories and outdoor equipment.'),
            ('Gaming Accessories', 'gaming', 'Gaming peripherals and accessories.'),
            ('Productivity Tools', 'productivity', 'Tools to boost productivity.'),
            ('Camera & Photo', 'camera', 'Photography and videography equipment.'),
            ('Fashion Tech', 'fashion', 'Wearable technology and smart accessories.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.indiegogo.com/explore/{category}',
                'link': f'https://www.indiegogo.com/explore/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Indiegogo',
                'data_type': 'crowdfunding_topic',
                'tags': ['crowdfunding', 'indiegogo', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
