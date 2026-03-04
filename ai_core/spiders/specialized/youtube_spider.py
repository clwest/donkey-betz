"""
YouTube Spider - Video Trends & Creator Intelligence
======================================================

Session 534: Simplified to work with spider network interface.
Uses YouTube API when credentials available, otherwise provides curated topics.
"""

import os
from ai_core.spiders.web_request_layer import cached_get
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class YouTubeSpider:
    """YouTube spider - video trends and creator discussions"""

    name = "youtube"

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    # Search queries for trending content
    SEARCH_QUERIES = [
        'AI tools tutorial 2025',
        'tech review latest',
        'coding tutorial beginner',
        'startup advice entrepreneur',
        'productivity tips',
    ]

    # Video categories
    CATEGORIES = [
        ('Tech Reviews', 'tech', 'Technology and gadget reviews.'),
        ('Tutorials', 'tutorials', 'How-to and educational content.'),
        ('Coding', 'coding', 'Programming and development.'),
        ('AI & ML', 'ai', 'Artificial intelligence content.'),
        ('Business', 'business', 'Entrepreneurship and startups.'),
    ]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        # Session 840: Use YOUTUBE_API_KEY first, fallback to GOOGLE_API_KEY
        self.api_key = os.getenv('YOUTUBE_API_KEY', '') or os.getenv('GOOGLE_API_KEY', '')

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch video trends from YouTube API.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of video/trend dictionaries
        """
        all_items = []
        seen_ids = set()

        # Try YouTube API if credentials available
        if self.api_key:
            try:
                api_items = self._fetch_youtube_api()
                for item in api_items:
                    if item['id'] not in seen_ids:
                        seen_ids.add(item['id'])
                        all_items.append(item)
            except Exception as e:
                logger.warning(f"YouTube API error: {e}")

        # Add category links
        try:
            categories = self._get_category_links()
            all_items.extend(categories)
        except Exception as e:
            logger.warning(f"Error getting YouTube categories: {e}")

        # If all sources fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"YouTube spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_youtube_api(self) -> List[Dict[str, Any]]:
        """Fetch videos from YouTube API with full statistics."""
        items = []
        video_ids = []

        # Step 1: Search for videos
        for query in self.SEARCH_QUERIES[:3]:  # Limit queries to conserve quota
            try:
                search_url = f"{self.BASE_URL}/search"
                params = {
                    'part': 'snippet',
                    'q': query,
                    'type': 'video',
                    'maxResults': 5,
                    'order': 'relevance',
                    'key': self.api_key,
                }

                response = cached_get(search_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        video_id = item.get('id', {}).get('videoId')
                        snippet = item.get('snippet', {})

                        if video_id:
                            video_ids.append(video_id)
                            items.append({
                                'id': video_id,
                                'title': snippet.get('title', ''),
                                'url': f'https://www.youtube.com/watch?v={video_id}',
                                'link': f'https://www.youtube.com/watch?v={video_id}',
                                'summary': snippet.get('description', '')[:500],
                                'description': snippet.get('description', '')[:500],
                                'channel': snippet.get('channelTitle', ''),
                                'published': snippet.get('publishedAt', ''),
                                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                                'search_query': query,
                                'source': 'YouTube',
                                'data_type': 'video',
                                'platform': 'youtube',
                                'tags': ['youtube', 'video', 'tutorial'],
                                'timestamp': datetime.now().isoformat(),
                            })

            except Exception as e:
                logger.warning(f"Error searching '{query}': {e}")

        # Step 2: Fetch statistics for all videos in one batch call
        if video_ids:
            stats = self._fetch_video_statistics(video_ids)
            # Merge statistics into items
            for item in items:
                video_id = item['id']
                if video_id in stats:
                    item.update(stats[video_id])

        return items

    def _fetch_video_statistics(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch video statistics from YouTube Videos API.

        Session 840: Added to get view counts, likes, comments - fixes "no YouTube metrics" issue.

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            Dict mapping video_id to statistics
        """
        stats = {}

        # YouTube API allows up to 50 video IDs per request
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i + 50]
            try:
                videos_url = f"{self.BASE_URL}/videos"
                params = {
                    'part': 'statistics,contentDetails',
                    'id': ','.join(batch),
                    'key': self.api_key,
                }

                response = cached_get(videos_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        video_id = item.get('id')
                        statistics = item.get('statistics', {})
                        content_details = item.get('contentDetails', {})

                        # Parse view/like/comment counts as integers
                        view_count = int(statistics.get('viewCount', 0))
                        like_count = int(statistics.get('likeCount', 0))
                        comment_count = int(statistics.get('commentCount', 0))

                        # Calculate engagement rate (likes + comments) / views
                        engagement_rate = 0.0
                        if view_count > 0:
                            engagement_rate = round((like_count + comment_count) / view_count * 100, 4)

                        stats[video_id] = {
                            'view_count': view_count,
                            'like_count': like_count,
                            'comment_count': comment_count,
                            'engagement_rate': engagement_rate,
                            'duration': content_details.get('duration', ''),  # ISO 8601 format
                            'definition': content_details.get('definition', ''),  # hd or sd
                            'has_statistics': True,
                            'statistics_fetched_at': datetime.now().isoformat(),
                        }

            except Exception as e:
                logger.warning(f"Error fetching video statistics: {e}")

        return stats

    def _get_category_links(self) -> List[Dict[str, Any]]:
        """Return YouTube category links."""
        return [
            {
                'id': f'category-{slug}',
                'title': f"YouTube: {name}",
                'url': f'https://www.youtube.com/results?search_query={slug}',
                'link': f'https://www.youtube.com/results?search_query={slug}',
                'summary': desc,
                'description': desc,
                'category': slug,
                'source': 'YouTube',
                'data_type': 'video_category',
                'platform': 'youtube',
                'tags': ['youtube', 'video', slug],
                'timestamp': datetime.now().isoformat(),
            }
            for name, slug, desc in self.CATEGORIES
        ]

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when API fails."""
        topics = [
            ('AI Tools & Tutorials', 'ai-tools', 'Latest AI tool reviews and tutorials.'),
            ('Tech Product Reviews', 'tech-reviews', 'Gadget and device reviews.'),
            ('Coding Tutorials', 'coding-tutorials', 'Programming and development guides.'),
            ('Startup & Business', 'startup-advice', 'Entrepreneurship and business tips.'),
            ('Productivity Hacks', 'productivity', 'Tips for getting more done.'),
        ]

        return [
            {
                'id': f'curated-{category}',
                'title': title,
                'url': f'https://www.youtube.com/results?search_query={category}',
                'link': f'https://www.youtube.com/results?search_query={category}',
                'summary': desc,
                'description': desc,
                'category': category,
                'source': 'YouTube',
                'data_type': 'video_topic',
                'platform': 'youtube',
                'tags': ['youtube', 'video', category],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, desc in topics
        ]
