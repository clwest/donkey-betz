"""
Giphy Spider - GIF & Meme Trends Intelligence
==============================================

Session 343: Spider for Giphy API to track trending GIFs and meme culture.
Collects trending GIFs, popular searches, and visual culture trends.

Uses GIPHY_API_Key from environment for authenticated requests.
"""

import aiohttp
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class GiphySpider(BaseIntelligenceSpider):
    """Giphy spider - trending GIFs, stickers, and meme culture"""

    BASE_URL = "https://api.giphy.com/v1"

    # Search terms to track trends
    TREND_SEARCHES = [
        'reaction',
        'meme',
        'funny',
        'celebrate',
        'work',
        'mood',
        'tech',
        'business',
    ]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)
        self.api_key = os.getenv('GIPHY_API_Key', '')

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch trending GIFs from Giphy"""
        if not self.api_key:
            self.logger.warning("GIPHY_API_Key not configured")
            return {'gifs': [], 'source': 'giphy', 'error': 'API key not configured'}

        try:
            all_gifs = []
            trending_searches = []

            async with aiohttp.ClientSession() as session:
                # Fetch trending GIFs
                try:
                    url = f"{self.BASE_URL}/gifs/trending"
                    params = {
                        'api_key': self.api_key,
                        'limit': 25,
                        'rating': 'pg-13'
                    }

                    async with session.get(url, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            gifs = data.get('data', [])

                            for gif in gifs:
                                all_gifs.append({
                                    'id': gif.get('id', ''),
                                    'title': gif.get('title', ''),
                                    'url': gif.get('url', ''),
                                    'embed_url': gif.get('embed_url', ''),
                                    'preview_url': gif.get('images', {}).get('preview_gif', {}).get('url', ''),
                                    'original_url': gif.get('images', {}).get('original', {}).get('url', ''),
                                    'username': gif.get('username', ''),
                                    'source_domain': gif.get('source_tld', ''),
                                    'trending_datetime': gif.get('trending_datetime', ''),
                                    'import_datetime': gif.get('import_datetime', ''),
                                    'rating': gif.get('rating', ''),
                                    'source': 'giphy',
                                    'type': 'gif',
                                    'category': 'trending',
                                })
                        else:
                            self.logger.warning(f"Giphy trending returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching trending GIFs: {e}")

                await asyncio.sleep(0.3)

                # Fetch trending search terms
                try:
                    url = f"{self.BASE_URL}/trending/searches"
                    params = {
                        'api_key': self.api_key,
                    }

                    async with session.get(url, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            trending_searches = data.get('data', [])
                        else:
                            self.logger.warning(f"Giphy trending searches returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching trending searches: {e}")

                await asyncio.sleep(0.3)

                # Fetch stickers (another trend indicator)
                try:
                    url = f"{self.BASE_URL}/stickers/trending"
                    params = {
                        'api_key': self.api_key,
                        'limit': 15,
                        'rating': 'pg-13'
                    }

                    async with session.get(url, params=params, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            stickers = data.get('data', [])

                            for sticker in stickers:
                                all_gifs.append({
                                    'id': sticker.get('id', ''),
                                    'title': sticker.get('title', ''),
                                    'url': sticker.get('url', ''),
                                    'embed_url': sticker.get('embed_url', ''),
                                    'preview_url': sticker.get('images', {}).get('preview_gif', {}).get('url', ''),
                                    'original_url': sticker.get('images', {}).get('original', {}).get('url', ''),
                                    'username': sticker.get('username', ''),
                                    'rating': sticker.get('rating', ''),
                                    'source': 'giphy',
                                    'type': 'sticker',
                                    'category': 'trending_sticker',
                                })
                        else:
                            self.logger.warning(f"Giphy stickers returned {response.status}")

                except Exception as e:
                    self.logger.warning(f"Error fetching stickers: {e}")

            return {
                'gifs': all_gifs,
                'trending_searches': trending_searches,
                'source': 'giphy'
            }

        except Exception as e:
            self.logger.error(f"Error fetching Giphy data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Giphy data into intelligence"""
        try:
            gifs = raw_data.get('gifs', [])
            trending_searches = raw_data.get('trending_searches', [])

            # Separate GIFs and stickers
            gif_items = [g for g in gifs if g.get('type') == 'gif']
            sticker_items = [g for g in gifs if g.get('type') == 'sticker']

            # Extract creators
            creator_counts = {}
            for gif in gifs:
                creator = gif.get('username', 'anonymous')
                if creator:
                    creator_counts[creator] = creator_counts.get(creator, 0) + 1

            top_creators = sorted(creator_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            # Extract source domains
            domain_counts = {}
            for gif in gifs:
                domain = gif.get('source_domain', '')
                if domain:
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1

            top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            content = {
                'gifs': gif_items,
                'stickers': sticker_items,
                'trending_searches': trending_searches[:20],
                'top_creators': top_creators,
                'top_domains': top_domains,
                'total_gifs': len(gif_items),
                'total_stickers': len(sticker_items),
            }

            quality_score = min(1.0, len(gifs) / 30 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='giphy.com',
                data_type='meme_intelligence',
                content=content,
                metadata={
                    'gif_count': len(gif_items),
                    'sticker_count': len(sticker_items),
                    'trending_search_count': len(trending_searches),
                    'source': 'giphy',
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['giphy', 'gif', 'meme', 'sticker', 'visual', 'culture', 'trending', 'social'],
                target_agents=['trend_analysis_agent', 'social_media_agent', 'content_strategy_agent'],
                target_advisors=['social_media_advisor', 'content_strategist', 'culture_analyst']
            )

        except Exception as e:
            self.logger.error(f"Error processing Giphy data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['id', 'url']

    def get_relevance_keywords(self) -> List[str]:
        return ['giphy', 'gif', 'meme', 'sticker', 'reaction', 'viral', 'trending']
