"""
Behance Spider - Creative Portfolio & Project Intelligence
==========================================================

Session 534: Simplified to work with spider network interface.
Uses Behance RSS feeds for creative project trends and inspiration.
"""

import feedparser
import logging
import re
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class BehanceSpider:
    """Behance creative spider - projects, portfolios, and creative work"""

    name = "behance"

    # Behance RSS feeds
    RSS_FEEDS = {
        'featured': 'https://www.behance.net/feeds/projects',
        'curated': 'https://www.behance.net/feeds/curated',
    }

    # Creative field categories
    CATEGORIES = [
        ('Graphic Design', 'graphic-design', 'Branding, print, and visual design.'),
        ('UI/UX Design', 'ui-ux', 'Interface and experience design.'),
        ('Illustration', 'illustration', 'Digital art and illustrations.'),
        ('Photography', 'photography', 'Commercial and artistic photography.'),
        ('Motion Graphics', 'motion', 'Animation and video.'),
        ('Branding', 'branding', 'Brand identity and visual systems.'),
        ('Web Design', 'web-design', 'Website design and development.'),
        ('3D & CGI', '3d-art', '3D modeling and renders.'),
        ('Packaging', 'packaging', 'Product packaging design.'),
        ('Architecture', 'architecture', 'Architectural visualization.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch creative projects from Behance.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of project dictionaries
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

        # Add creative field category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting Behance categories: {e}")

        # If feeds fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Behance spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_rss(self, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
        """Fetch projects from Behance RSS feed."""
        items = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                if not title:
                    continue

                url = entry.get('link', '')

                # Extract description
                description = ''
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].get('value', '')
                    description = re.sub(r'<[^>]+>', '', content)[:400]
                elif hasattr(entry, 'summary'):
                    description = re.sub(r'<[^>]+>', '', entry.summary)[:400]

                # Detect creative field
                text = f"{title} {description}".lower()
                creative_field = self._detect_creative_field(text)

                # Get tags if available
                tags = []
                if hasattr(entry, 'tags'):
                    tags = [tag.term for tag in entry.tags][:5]

                items.append({
                    'title': title,
                    'url': url,
                    'link': url,
                    'summary': description,
                    'description': description,
                    'published': entry.get('published', ''),
                    'author': entry.get('author', 'Creative'),
                    'category': creative_field,
                    'creative_field': creative_field,
                    'is_featured': feed_name in ['featured', 'curated'],
                    'project_tags': tags,
                    'source': 'Behance',
                    'data_type': 'creative_project',
                    'platform': 'behance',
                    'tags': ['design', 'creative', 'portfolio', creative_field],
                    'timestamp': datetime.now().isoformat(),
                })

        except Exception as e:
            logger.warning(f"Error parsing RSS: {e}")

        return items

    def _detect_creative_field(self, text: str) -> str:
        """Detect creative field from text."""
        fields = {
            'graphic_design': ['graphic design', 'poster', 'print', 'layout', 'editorial'],
            'branding': ['branding', 'brand', 'identity', 'logo', 'visual identity'],
            'ui_ux': ['ui', 'ux', 'interface', 'app design', 'web design'],
            'illustration': ['illustration', 'digital art', 'character', 'concept art'],
            'photography': ['photography', 'photo', 'portrait', 'commercial'],
            'motion': ['motion graphics', 'animation', 'video', 'after effects'],
            '3d': ['3d', 'cgi', 'render', 'blender', 'cinema 4d'],
            'packaging': ['packaging', 'package design', 'label'],
        }

        for field, keywords in fields.items():
            if any(kw in text for kw in keywords):
                return field
        return 'mixed_media'

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return Behance creative field links."""
        return [
            {
                'title': f"Behance: {name}",
                'url': f'https://www.behance.net/search/projects?field={slug}',
                'link': f'https://www.behance.net/search/projects?field={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Behance',
                'data_type': 'creative_category',
                'platform': 'behance',
                'tags': ['design', 'behance', 'creative', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when feeds fail."""
        topics = [
            ('Featured Projects', 'featured', 'Curated creative work.'),
            ('Graphic Design', 'graphic-design', 'Visual design projects.'),
            ('UI/UX Design', 'ui-ux', 'Interface design projects.'),
            ('Illustration', 'illustration', 'Digital art and illustration.'),
            ('Photography', 'photography', 'Photo projects and portfolios.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://www.behance.net/galleries/{category}',
                'link': f'https://www.behance.net/galleries/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Behance',
                'data_type': 'creative_topic',
                'platform': 'behance',
                'tags': ['design', 'behance', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
