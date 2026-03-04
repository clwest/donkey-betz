"""
Unsplash Spider - Visual Trends & Photography Intelligence
============================================================

Session 534: Simplified to work with spider network interface.
Uses Unsplash API when credentials available, otherwise provides curated topics.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class UnsplashSpider:
    """Unsplash spider - visual trends and photography intelligence"""

    name = "unsplash"

    BASE_URL = 'https://api.unsplash.com'

    # Topics to track for visual trends
    TOPICS = [
        ('Technology', 'technology', 'Tech and digital imagery.'),
        ('Business & Work', 'business-work', 'Professional and workplace visuals.'),
        ('Arts & Culture', 'arts-culture', 'Artistic and cultural photography.'),
        ('Nature', 'nature', 'Landscapes and wildlife.'),
        ('Architecture', 'architecture-interior', 'Buildings and interior design.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        self.headers = {
            'Authorization': f'Client-ID {self.access_key}',
            'Accept-Version': 'v1',
        } if self.access_key else {}

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch visual trends from Unsplash API.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of photo/trend dictionaries
        """
        all_items = []
        seen_ids = set()

        # Try Unsplash API if credentials available
        if self.access_key:
            try:
                api_items = self._fetch_unsplash_api()
                for item in api_items:
                    if item['id'] not in seen_ids:
                        seen_ids.add(item['id'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"Unsplash API error: {e}")

        # Add topic links
        try:
            topics = self._get_topic_links()
            all_items.extend(topics)
        except Exception as e:
            logger.warning(f"Error getting Unsplash topics: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Unsplash spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_unsplash_api(self) -> List[Dict[str, Any]]:
        """Fetch photos from Unsplash API."""
        items = []

        try:
            # Fetch popular photos
            url = f"{self.BASE_URL}/photos"
            params = {'order_by': 'popular', 'per_page': 20}

            response = cached_get(url, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                photos = response.json()

                for photo in photos:
                    description = photo.get('description') or photo.get('alt_description') or ''
                    tags = [tag.get('title', '') for tag in photo.get('tags', [])[:5]]

                    items.append({
                        'id': photo.get('id', ''),
                        'title': description[:100] if description else 'Untitled Photo',
                        'url': photo.get('urls', {}).get('regular', ''),
                        'link': photo.get('links', {}).get('html', ''),
                        'summary': description,
                        'description': description,
                        'color': photo.get('color', ''),
                        'likes': photo.get('likes', 0),
                        'width': photo.get('width', 0),
                        'height': photo.get('height', 0),
                        'user': photo.get('user', {}).get('username', ''),
                        'photo_tags': tags,
                        'source': 'Unsplash',
                        'data_type': 'photography',
                        'platform': 'unsplash',
                        'tags': ['photography', 'visual', 'stock'] + tags[:2],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error fetching Unsplash API: {e}")

        return items

    def _get_topic_links(self) -> List[Dict[str, Any]]:
        """Return Unsplash topic links."""
        return [
            {
                'id': f'topic-{slug}',
                'title': f"Unsplash: {name}",
                'url': f'https://unsplash.com/t/{slug}',
                'link': f'https://unsplash.com/t/{slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'Unsplash',
                'data_type': 'photo_topic',
                'platform': 'unsplash',
                'tags': ['photography', 'visual', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.TOPICS
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when API fails."""
        topics = [
            ('Trending Photography', 'popular', 'Most popular and liked photos.'),
            ('Editorial Picks', 'editorial', 'Curated editorial photography.'),
            ('Minimal Design', 'minimal', 'Clean and minimalist imagery.'),
            ('Dark & Moody', 'dark', 'Atmospheric dark photography.'),
            ('Textures & Patterns', 'textures-patterns', 'Abstract textures and patterns.'),
        ]

        return [
            {
                'id': f'curated-{category}',
                'title': title,
                'url': f'https://unsplash.com/t/{category}',
                'link': f'https://unsplash.com/t/{category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'Unsplash',
                'data_type': 'photo_topic',
                'platform': 'unsplash',
                'tags': ['photography', 'visual', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
