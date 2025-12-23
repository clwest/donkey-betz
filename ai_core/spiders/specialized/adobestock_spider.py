"""
Adobe Stock Spider - Stock Content & Creative Trends Intelligence
===================================================================

Session 534: Simplified to work with spider network interface.
Uses Adobe Creative blog RSS feeds for creative industry trends.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AdobeStockSpider:
    """Adobe Stock spider - stock content and creative trends intelligence"""

    name = "adobestock"

    # Adobe and creative industry RSS feeds
    RSS_FEEDS = {
        'adobe_blog': 'https://blog.adobe.com/en/publish/rss',
        'psdvault': 'https://www.psd-vault.com/feed/',
        'creativebloq': 'https://www.creativebloq.com/feed',
    }

    # Stock content categories
    CATEGORIES = [
        ('Stock Photos', 'photos', 'High-quality stock photography.'),
        ('Vector Graphics', 'vectors', 'Illustrations and vector art.'),
        ('Stock Video', 'videos', 'Video footage and B-roll.'),
        ('Templates', 'templates', 'PSD and design templates.'),
        ('3D Assets', '3d', '3D models and renders.'),
        ('Audio', 'audio', 'Music and sound effects.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch creative industry news and stock content trends.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of article and category dictionaries
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

        # Add stock content category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Adobe Stock categories: {e}")

        # If all feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Adobe Stock spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch articles from RSS feed."""
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

                # Detect content type
                content_type = self._detect_content_type(f"{title} {description}".lower())

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', feed_name),
                    'category': content_type,
                    'source': feed_name.replace('_', ' ').title(),
                    'data_type': 'creative_article',
                    'platform': 'adobestock',
                    'tags': ['adobe', 'creative', 'design', 'stock', content_type],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_content_type(self, text: str) -> str:
        """Detect content type from text."""
        types = {
            'photo': ['photo', 'photography', 'image', 'picture', 'portrait'],
            'vector': ['vector', 'illustration', 'graphic', 'icon', 'svg'],
            'video': ['video', 'footage', 'motion', 'clip', 'b-roll'],
            'template': ['template', 'psd', 'mockup', 'layout'],
            '3d': ['3d', 'render', 'model', 'dimension'],
            'audio': ['audio', 'music', 'sound', 'soundtrack'],
        }

        for ctype, keywords in types.items():
            if any(kw in text for kw in keywords):
                return ctype
        return 'general'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Adobe Stock category exploration links."""
        return [
            {
                'title': f"Adobe Stock: {name}",
                'url': f'https://stock.adobe.com/search?k={slug}',
                'link': f'https://stock.adobe.com/search?k={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Adobe Stock',
                'data_type': 'stock_category',
                'platform': 'adobestock',
                'tags': ['adobe', 'stock', 'creative', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Stock Photography', 'photos', 'Professional stock photos.'),
            ('Vector Illustrations', 'vectors', 'Scalable vector graphics.'),
            ('Video Templates', 'video-templates', 'Motion graphics and video.'),
            ('Photoshop Templates', 'psd-templates', 'Layered PSD files.'),
            ('Creative Cloud', 'creative-cloud', 'Adobe Creative Cloud tools.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://stock.adobe.com/{category}',
                'link': f'https://stock.adobe.com/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Adobe Stock',
                'data_type': 'stock_topic',
                'platform': 'adobestock',
                'tags': ['adobe', 'stock', 'creative', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
