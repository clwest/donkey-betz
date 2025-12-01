"""
Indie Hackers Spider - Maker/Founder Community Intelligence
============================================================

Session 294: Customer research spider for Indie Hackers community.
Collects discussions about tools, pain points, and business challenges.

No API key required - uses public RSS feeds.
"""

import aiohttp
import asyncio
import feedparser
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class IndieHackersSpider(BaseIntelligenceSpider):
    """Indie Hackers spider - maker/founder discussions and pain points"""

    # RSS feeds for different categories
    FEEDS = {
        'popular': 'https://www.indiehackers.com/feed.xml',
        'interviews': 'https://www.indiehackers.com/interviews/feed.xml',
    }

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.headers = {
            'User-Agent': 'DonkeyBetz-Spider/1.0 (AI Content Studio; Research)'
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch data from Indie Hackers RSS feeds"""
        try:
            all_posts = []

            async with aiohttp.ClientSession(headers=self.headers) as session:
                for feed_name, feed_url in self.FEEDS.items():
                    try:
                        async with session.get(feed_url, timeout=15) as response:
                            if response.status == 200:
                                content = await response.text()
                                feed = feedparser.parse(content)

                                for entry in feed.entries[:20]:
                                    all_posts.append({
                                        'title': entry.get('title', ''),
                                        'description': entry.get('summary', '')[:500] if entry.get('summary') else '',
                                        'link': entry.get('link', ''),
                                        'author': entry.get('author', ''),
                                        'published': entry.get('published', ''),
                                        'category': feed_name,
                                        'source': 'indiehackers',
                                        'type': 'discussion',
                                    })

                        await asyncio.sleep(0.5)

                    except Exception as e:
                        self.logger.warning(f"Error fetching {feed_name}: {e}")

            return {'posts': all_posts, 'source': 'indiehackers'}

        except Exception as e:
            self.logger.error(f"Error fetching Indie Hackers data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Indie Hackers posts into intelligence"""
        try:
            posts = raw_data.get('posts', [])

            # Extract pain points keywords
            pain_keywords = ['struggle', 'problem', 'issue', 'frustrat', 'difficult', 'challenge',
                           'fail', 'stuck', 'help', 'advice', 'how do', 'anyone else']

            pain_point_posts = []
            for post in posts:
                text = f"{post.get('title', '')} {post.get('description', '')}".lower()
                if any(kw in text for kw in pain_keywords):
                    pain_point_posts.append(post)

            content = {
                'posts': posts,
                'pain_point_discussions': pain_point_posts,
                'total_posts': len(posts),
                'pain_points_found': len(pain_point_posts),
            }

            quality_score = min(1.0, len(posts) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='indiehackers.com',
                data_type='community_intelligence',
                content=content,
                metadata={
                    'post_count': len(posts),
                    'pain_points': len(pain_point_posts),
                    'source': 'indiehackers',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['indiehackers', 'makers', 'founders', 'pain_points', 'startups', 'saas'],
                target_agents=['customer_research_agent', 'trend_analysis_agent', 'content_strategy_agent'],
                target_advisors=['business_advisor', 'market_strategist']
            )

        except Exception as e:
            self.logger.error(f"Error processing Indie Hackers data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['indiehackers', 'makers', 'founders', 'startup', 'saas', 'bootstrap', 'indie']
