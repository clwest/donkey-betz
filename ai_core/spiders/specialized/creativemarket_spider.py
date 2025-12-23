"""
Creative Market Spider - Design Assets & Fonts Intelligence
=============================================================

Session 534: Simplified to work with spider network interface.
Uses design RSS feeds for assets, fonts, and creative resources.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CreativeMarketSpider:
    """Creative Market spider - design assets and fonts intelligence"""

    name = "creativemarket"

    # Design asset RSS feeds
    RSS_FEEDS = {
        'creative_bloq': 'https://www.creativebloq.com/feed',
        'designmodo': 'https://designmodo.com/feed/',
        'smashing_mag': 'https://www.smashingmagazine.com/feed/',
    }

    # Asset type categories
    CATEGORIES = [
        ('Fonts', 'fonts', 'Typography and typeface resources.'),
        ('Graphics', 'graphics', 'Vector graphics and illustrations.'),
        ('Templates', 'templates', 'Design templates and mockups.'),
        ('Photos', 'photos', 'Stock photography resources.'),
        ('Themes', 'themes', 'Website and UI themes.'),
        ('Add-ons', 'add-ons', 'Plugins, brushes, and actions.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.asset_types = {
            'fonts': ['font', 'typeface', 'typography', 'lettering', 'type design'],
            'graphics': ['graphic', 'illustration', 'vector', 'clipart', 'artwork'],
            'templates': ['template', 'mockup', 'presentation', 'resume', 'flyer'],
            'photos': ['photo', 'stock photo', 'image', 'photography'],
            'themes': ['theme', 'wordpress', 'website', 'ui kit', 'dashboard'],
            'add_ons': ['add-on', 'plugin', 'extension', 'brush', 'action'],
        }
        self.design_trends = {
            'minimalist': ['minimal', 'clean', 'simple', 'modern', 'flat'],
            'vintage': ['vintage', 'retro', 'classic', 'old school', 'nostalgic'],
            'bold': ['bold', 'vibrant', 'colorful', 'bright', 'striking'],
            'elegant': ['elegant', 'luxury', 'premium', 'sophisticated', 'refined'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch design asset content from RSS feeds.

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
            logger.warning(f"Error getting Creative Market categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Creative Market spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from design RSS feed."""
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

                # Detect asset type and design trend
                text = f"{title} {summary}".lower()
                asset_type = self._detect_asset_type(text)
                trend_style = self._detect_trend_style(text)

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': summary,
                    'description': summary,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name.replace('_', ' ').title()),
                    'category': asset_type,
                    'asset_type': asset_type,
                    'trend_style': trend_style,
                    'is_font': asset_type == 'fonts',
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'design_asset',
                    'platform': 'creativemarket',
                    'tags': ['design', 'assets', asset_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_asset_type(self, text: str) -> str:
        """Detect asset type from text."""
        for atype, keywords in self.asset_types.items():
            if any(kw in text for kw in keywords):
                return atype
        return 'general'

    def _detect_trend_style(self, text: str) -> str:
        """Detect design trend style from text."""
        for trend, keywords in self.design_trends.items():
            if any(kw in text for kw in keywords):
                return trend
        return None

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Creative Market category links."""
        return [
            {
                'title': f"Creative Market: {name}",
                'url': f'https://creativemarket.com/{slug}',
                'link': f'https://creativemarket.com/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Creative Market',
                'data_type': 'asset_category',
                'platform': 'creativemarket',
                'tags': ['design', 'assets', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Free Fonts', 'fonts', 'Free and premium typography.'),
            ('Vector Graphics', 'graphics', 'Illustrations and clipart.'),
            ('Design Templates', 'templates', 'Mockups and presentations.'),
            ('UI Kits', 'themes', 'Website and app themes.'),
            ('Design Resources', 'resources', 'Tools and add-ons.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://creativemarket.com/{category}',
                'link': f'https://creativemarket.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Creative Market',
                'data_type': 'asset_topic',
                'platform': 'creativemarket',
                'tags': ['design', 'assets', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
