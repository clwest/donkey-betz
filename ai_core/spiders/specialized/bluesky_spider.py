"""
BlueSky Spider - Social Media Intelligence (Twitter/X Alternative)
===================================================================

Session 294: Customer research spider for BlueSky social network.
Collects posts about AI tools, content creation, and creator pain points.

Uses BlueSky AT Protocol API with credentials from environment.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class BlueSkySpider(BaseIntelligenceSpider):
    """BlueSky spider - social media sentiment and discussions"""

    # Search terms for customer research
    SEARCH_TERMS = [
        'AI tools',
        'content creator',
        'stable diffusion',
        'midjourney',
        'AI writing',
        'creator economy',
        'freelance',
        'side project',
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.identifier = os.getenv('BLUESKY_IDENTIFIER', '')
        self.password = os.getenv('BLUESKY_PASSWORD', '')
        self.access_token = None
        self.did = None

    async def _authenticate(self, session: aiohttp.ClientSession) -> bool:
        """Authenticate with BlueSky API"""
        if not self.identifier or not self.password:
            self.logger.warning("BlueSky credentials not configured")
            return False

        try:
            auth_url = "https://bsky.social/xrpc/com.atproto.server.createSession"
            async with session.post(auth_url, json={
                "identifier": self.identifier,
                "password": self.password
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get('accessJwt')
                    self.did = data.get('did')
                    return True
                else:
                    self.logger.warning(f"BlueSky auth failed: {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"BlueSky auth error: {e}")
            return False

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch posts from BlueSky"""
        try:
            all_posts = []

            async with aiohttp.ClientSession() as session:
                # Authenticate first
                if not await self._authenticate(session):
                    return {'posts': [], 'source': 'bluesky', 'error': 'Authentication failed'}

                headers = {'Authorization': f'Bearer {self.access_token}'}

                # Search for each term
                for term in self.SEARCH_TERMS[:5]:  # Limit to avoid rate limits
                    try:
                        search_url = f"https://bsky.social/xrpc/app.bsky.feed.searchPosts"
                        params = {'q': term, 'limit': 20}

                        async with session.get(search_url, headers=headers, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                posts = data.get('posts', [])

                                for post in posts:
                                    record = post.get('record', {})
                                    author = post.get('author', {})

                                    all_posts.append({
                                        'text': record.get('text', ''),
                                        'author': author.get('handle', ''),
                                        'author_name': author.get('displayName', ''),
                                        'created_at': record.get('createdAt', ''),
                                        'uri': post.get('uri', ''),
                                        'likes': post.get('likeCount', 0),
                                        'reposts': post.get('repostCount', 0),
                                        'replies': post.get('replyCount', 0),
                                        'search_term': term,
                                        'source': 'bluesky',
                                        'type': 'social_post',
                                    })

                        await asyncio.sleep(0.5)

                    except Exception as e:
                        self.logger.warning(f"Error searching '{term}': {e}")

            return {'posts': all_posts, 'source': 'bluesky'}

        except Exception as e:
            self.logger.error(f"Error fetching BlueSky data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process BlueSky posts into intelligence"""
        try:
            posts = raw_data.get('posts', [])

            # Sentiment keywords
            negative_keywords = ['frustrat', 'annoying', 'broken', 'bug', 'issue', 'problem',
                               'hate', 'terrible', 'worst', 'disappointed', 'fail']
            positive_keywords = ['love', 'amazing', 'great', 'awesome', 'best', 'perfect',
                               'helpful', 'game changer', 'incredible']

            sentiment_analysis = {'positive': 0, 'negative': 0, 'neutral': 0}
            pain_point_posts = []

            for post in posts:
                text = post.get('text', '').lower()
                if any(kw in text for kw in negative_keywords):
                    sentiment_analysis['negative'] += 1
                    pain_point_posts.append(post)
                elif any(kw in text for kw in positive_keywords):
                    sentiment_analysis['positive'] += 1
                else:
                    sentiment_analysis['neutral'] += 1

            content = {
                'posts': posts,
                'pain_point_posts': pain_point_posts[:20],
                'sentiment_analysis': sentiment_analysis,
                'total_posts': len(posts),
                'engagement_avg': sum(p.get('likes', 0) + p.get('reposts', 0) for p in posts) / max(len(posts), 1),
            }

            quality_score = min(1.0, len(posts) / 50 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='bsky.social',
                data_type='social_intelligence',
                content=content,
                metadata={
                    'post_count': len(posts),
                    'pain_points': len(pain_point_posts),
                    'sentiment': sentiment_analysis,
                    'source': 'bluesky',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['bluesky', 'social', 'sentiment', 'ai_tools', 'creators'],
                target_agents=['customer_research_agent', 'trend_analysis_agent', 'social_media_agent'],
                target_advisors=['social_strategist', 'market_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing BlueSky data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['text']

    def get_relevance_keywords(self) -> List[str]:
        return ['bluesky', 'social', 'ai', 'tools', 'creator', 'sentiment']
