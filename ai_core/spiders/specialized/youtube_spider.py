"""
YouTube Spider - Video Comments & Trends Intelligence
======================================================

Session 294: Customer research spider for YouTube.
Collects comments from AI tool reviews, tutorials, and creator content.

Uses YouTube Data API v3 with credentials from environment.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class YouTubeSpider(BaseIntelligenceSpider):
    """YouTube spider - video comments and creator discussions"""

    # Search queries for AI/creator content
    SEARCH_QUERIES = [
        'AI content creation tools review',
        'midjourney tutorial',
        'stable diffusion problems',
        'AI writing tools comparison',
        'content creator workflow',
        'freelancer tools 2024',
    ]

    # Video IDs of popular AI tool reviews (can be updated)
    POPULAR_VIDEOS = []  # Will use search instead

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('GOOGLE_API_KEY', '')
        self.base_url = "https://www.googleapis.com/youtube/v3"

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch YouTube videos and comments"""
        if not self.api_key:
            self.logger.warning("YouTube API key not configured (GOOGLE_API_KEY)")
            return {'videos': [], 'comments': [], 'source': 'youtube', 'error': 'API key not configured'}

        try:
            all_videos = []
            all_comments = []

            async with aiohttp.ClientSession() as session:
                # Search for relevant videos
                for query in self.SEARCH_QUERIES[:4]:  # Limit queries
                    try:
                        search_url = f"{self.base_url}/search"
                        params = {
                            'part': 'snippet',
                            'q': query,
                            'type': 'video',
                            'maxResults': 5,
                            'order': 'relevance',
                            'key': self.api_key,
                        }

                        async with session.get(search_url, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                items = data.get('items', [])

                                for item in items:
                                    video_id = item.get('id', {}).get('videoId')
                                    snippet = item.get('snippet', {})

                                    if video_id:
                                        all_videos.append({
                                            'video_id': video_id,
                                            'title': snippet.get('title', ''),
                                            'description': snippet.get('description', '')[:300],
                                            'channel': snippet.get('channelTitle', ''),
                                            'published': snippet.get('publishedAt', ''),
                                            'search_query': query,
                                            'source': 'youtube',
                                            'type': 'video',
                                        })

                                        # Fetch comments for this video
                                        comments = await self._fetch_comments(session, video_id)
                                        all_comments.extend(comments)

                            else:
                                self.logger.warning(f"YouTube search failed: {response.status}")

                        await asyncio.sleep(0.3)

                    except Exception as e:
                        self.logger.warning(f"Error searching '{query}': {e}")

            return {
                'videos': all_videos,
                'comments': all_comments,
                'source': 'youtube'
            }

        except Exception as e:
            self.logger.error(f"Error fetching YouTube data: {e}")
            return None

    async def _fetch_comments(self, session: aiohttp.ClientSession, video_id: str) -> List[Dict[str, Any]]:
        """Fetch comments for a specific video"""
        comments = []
        try:
            comments_url = f"{self.base_url}/commentThreads"
            params = {
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': 20,
                'order': 'relevance',
                'key': self.api_key,
            }

            async with session.get(comments_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('items', [])

                    for item in items:
                        snippet = item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
                        comments.append({
                            'text': snippet.get('textDisplay', ''),
                            'author': snippet.get('authorDisplayName', ''),
                            'likes': snippet.get('likeCount', 0),
                            'published': snippet.get('publishedAt', ''),
                            'video_id': video_id,
                            'source': 'youtube',
                            'type': 'comment',
                        })

        except Exception as e:
            self.logger.warning(f"Error fetching comments for {video_id}: {e}")

        return comments

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process YouTube data into intelligence"""
        try:
            videos = raw_data.get('videos', [])
            comments = raw_data.get('comments', [])

            # Analyze comments for pain points
            pain_keywords = ['frustrat', 'problem', 'issue', 'bug', 'broken', 'doesn\'t work',
                           'wish', 'should', 'missing', 'need', 'want', 'disappointed']

            pain_point_comments = []
            for comment in comments:
                text = comment.get('text', '').lower()
                if any(kw in text for kw in pain_keywords):
                    pain_point_comments.append(comment)

            content = {
                'videos': videos,
                'comments': comments[:100],  # Limit stored comments
                'pain_point_comments': pain_point_comments[:30],
                'total_videos': len(videos),
                'total_comments': len(comments),
                'pain_points_found': len(pain_point_comments),
            }

            quality_score = min(1.0, (len(videos) + len(comments)) / 100 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='youtube.com',
                data_type='video_intelligence',
                content=content,
                metadata={
                    'video_count': len(videos),
                    'comment_count': len(comments),
                    'pain_points': len(pain_point_comments),
                    'source': 'youtube',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['youtube', 'video', 'comments', 'reviews', 'tutorials', 'ai_tools'],
                target_agents=['customer_research_agent', 'trend_analysis_agent', 'content_strategy_agent'],
                target_advisors=['content_advisor', 'market_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing YouTube data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['title', 'text']

    def get_relevance_keywords(self) -> List[str]:
        return ['youtube', 'video', 'tutorial', 'review', 'ai', 'tools', 'creator']
