"""
Gumroad Spider - Digital Products & Creator Economy Intelligence
================================================================

Session 534: Simplified to work with spider network interface.
Uses creator economy RSS feeds and curated digital product categories.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class GumroadSpider:
    """Gumroad spider - digital products and creator economy trends"""

    name = "gumroad"

    # Creator economy RSS feeds
    RSS_FEEDS = {
        'creator_economy': 'https://newsletter.creatoreconomy.so/feed',
        'simon_owens': 'https://simonowens.substack.com/feed',
    }

    # Digital product categories on Gumroad
    CATEGORIES = [
        ('3D', '3d', 'Blender assets, 3D models, and game assets.'),
        ('Design', 'design', 'UI kits, icons, fonts, and design resources.'),
        ('Drawing & Painting', 'drawing-painting', 'Brushes, tutorials, and art resources.'),
        ('Software', 'software', 'Apps, plugins, and developer tools.'),
        ('Self-improvement', 'self-improvement', 'Productivity and personal development.'),
        ('Fiction Books', 'fiction', 'eBooks, novels, and short stories.'),
        ('Comics & Graphic Novels', 'comics', 'Webcomics and graphic novels.'),
        ('Audio', 'audio', 'Music, sound effects, and audio tools.'),
        ('Recorded Music', 'music', 'Albums, singles, and music packs.'),
        ('Films', 'films', 'Short films, documentaries, and video content.'),
        ('Courses', 'courses', 'Online courses and educational content.'),
        ('Tutorials', 'tutorials', 'Step-by-step guides and how-tos.'),
        ('Photography', 'photography', 'Photo presets, lightroom, and photography guides.'),
        ('Business & Money', 'business', 'Business templates and finance guides.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch digital product trends and creator economy news.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of digital product/creator economy dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from RSS feeds
        for feed_name, feed_url in self.RSS_FEEDS.items():
            try:
                items = self._fetch_rss(feed_url, feed_name, max_per_feed=15)
                for item in items:
                    if item['url'] not in seen_urls:
                        seen_urls.add(item['url'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Error fetching {feed_name} feed: {e}")

        # Add Gumroad category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Gumroad categories: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Gumroad spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str, max_per_feed: int = 15) -> List[Dict[str, Any]]:
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
                    'source': 'Creator Economy',
                    'data_type': 'creator_economy_news',
                    'tags': ['digital-products', 'creator-economy', 'gumroad', category],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS feed {feed_url}: {e}")

        return items

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Gumroad category exploration links."""
        return [
            {
                'title': f"Gumroad: {name}",
                'url': f'https://gumroad.com/discover?query={slug}',
                'link': f'https://gumroad.com/discover?query={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Gumroad',
                'data_type': 'digital_product_category',
                'tags': ['digital-products', 'gumroad', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _detect_category(self, text: str) -> str:
        """Detect product category from text."""
        categories = {
            'design': ['design', 'ui', 'icon', 'font', 'template'],
            'software': ['software', 'app', 'plugin', 'tool', 'code'],
            'courses': ['course', 'learn', 'tutorial', 'class', 'lesson'],
            'ebook': ['book', 'ebook', 'pdf', 'guide', 'manual'],
            'audio': ['audio', 'music', 'sound', 'beat', 'sample'],
            '3d': ['3d', 'blender', 'model', 'asset', 'render'],
            'art': ['art', 'illustration', 'drawing', 'brush', 'paint'],
            'photo': ['photo', 'preset', 'lightroom', 'photography'],
            'business': ['business', 'notion', 'template', 'spreadsheet'],
        }

        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat
        return 'digital-product'

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated digital product topics when feeds fail."""
        topics = [
            ('Design Templates', 'design', 'UI kits, icons, and design resources.'),
            ('Online Courses', 'courses', 'Educational content and tutorials.'),
            ('eBooks & Guides', 'ebook', 'Digital books and comprehensive guides.'),
            ('Software & Tools', 'software', 'Apps, plugins, and developer tools.'),
            ('Music & Audio', 'audio', 'Sound packs, beats, and audio resources.'),
            ('3D Assets', '3d', 'Blender models and game assets.'),
            ('Art Resources', 'art', 'Brushes, tutorials, and art packs.'),
            ('Notion Templates', 'business', 'Productivity and business templates.'),
            ('Photo Presets', 'photo', 'Lightroom presets and photography tools.'),
            ('Creator Tools', 'creator', 'Resources for content creators.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://gumroad.com/discover?query={category}',
                'link': f'https://gumroad.com/discover?query={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Gumroad',
                'data_type': 'digital_product_topic',
                'tags': ['digital-products', 'gumroad', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
