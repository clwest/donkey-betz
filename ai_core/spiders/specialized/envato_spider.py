"""
Envato Spider - Creative Assets Marketplace Intelligence
==========================================================

Session 534: Simplified to work with spider network interface.
Uses Envato and design marketplace RSS feeds for asset trends.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class EnvatoSpider:
    """Envato spider - creative assets marketplace intelligence"""

    name = "envato"

    # Envato and design marketplace RSS feeds
    RSS_FEEDS = {
        'envato_blog': 'https://envato.com/blog/feed/',
        'tutsplus': 'https://tutsplus.com/posts.atom',
        'webdesigner_depot': 'https://www.webdesignerdepot.com/feed/',
    }

    # Asset categories
    CATEGORIES = [
        ('Themes', 'themes', 'WordPress and website themes.'),
        ('Graphics', 'graphics', 'Vector graphics and illustrations.'),
        ('Code', 'code', 'Plugins and scripts.'),
        ('Video', 'video', 'Video templates and motion graphics.'),
        ('Audio', 'audio', 'Music and sound effects.'),
        ('Photos', 'photos', 'Stock photography.'),
        ('3D', '3d', '3D models and renders.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.asset_categories = {
            'themes': ['theme', 'template', 'wordpress', 'html', 'landing page'],
            'graphics': ['graphic', 'vector', 'illustration', 'icon', 'logo'],
            'code': ['plugin', 'script', 'code', 'javascript', 'php'],
            'video': ['video', 'motion', 'after effects', 'premiere', 'animation'],
            'audio': ['audio', 'music', 'sound effect', 'podcast', 'sfx'],
            'photos': ['photo', 'stock', 'image', 'photography', 'mockup'],
            '3d': ['3d', 'model', 'render', 'blender', 'cinema 4d'],
        }
        self.trend_signals = {
            'trending': ['trending', 'popular', 'best seller', 'top rated', 'featured'],
            'new': ['new', 'just added', 'fresh', 'latest', 'released'],
            'sale': ['sale', 'discount', 'deal', 'offer', 'bundle'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch creative asset content from RSS feeds.

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

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Envato categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Envato spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from Envato RSS feed."""
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
                    summary = re.sub(r'<[^>]+>', '', summary)[:400]

                # Detect asset category and trend signals
                text = f"{title} {summary}".lower()
                category = self._detect_category(text)
                signals = self._detect_signals(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': category,
                    'asset_category': category,
                    'signals': signals,
                    'is_trending': 'trending' in signals,
                    'is_new': 'new' in signals,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'creative_asset',
                    'platform': 'envato',
                    'tags': ['envato', 'assets', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_category(self, text: str) -> str:
        """Detect asset category from text."""
        for category, keywords in self.asset_categories.items():
            if any(kw in text for kw in keywords):
                return category
        return 'general'

    def _detect_signals(self, text: str) -> List[str]:
        """Detect trend signals from text."""
        signals = []
        for signal, keywords in self.trend_signals.items():
            if any(kw in text for kw in keywords):
                signals.append(signal)
        return signals

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Envato category links."""
        return [
            {
                'title': f"Envato: {name}",
                'url': f'https://elements.envato.com/{slug}',
                'link': f'https://elements.envato.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Envato',
                'data_type': 'asset_category',
                'platform': 'envato',
                'tags': ['envato', 'assets', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Website Themes', 'themes', 'WordPress and HTML templates.'),
            ('Graphics & Icons', 'graphics', 'Vector graphics and illustrations.'),
            ('Code & Plugins', 'code', 'Scripts and extensions.'),
            ('Video Templates', 'video', 'Motion graphics and templates.'),
            ('Stock Photos', 'photos', 'Photography and mockups.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://elements.envato.com/{category}',
                'link': f'https://elements.envato.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Envato',
                'data_type': 'asset_topic',
                'platform': 'envato',
                'tags': ['envato', 'assets', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
