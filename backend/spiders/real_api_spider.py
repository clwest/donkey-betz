"""
Real API Spider Implementation
Uses actual API endpoints with authentication
"""

import asyncio
import aiohttp
import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .base_spider import BaseIntelligenceSpider
from .api_config import api_config

logger = logging.getLogger(__name__)


class RealAPISpider(BaseIntelligenceSpider):
    """Spider that fetches data from real APIs with authentication"""

    def __init__(self, spider_id: str, spider_type: str, category: str):
        super().__init__(spider_id, [], [])
        self.spider_type = spider_type
        self.category = category
        self.session = None
        self.tokens = {}
        self.api_configs = {
            'bluesky': api_config.get_bluesky_config(),
            'reddit': api_config.get_reddit_config(),
            'polygon': api_config.get_polygon_config(),
            'alpha_vantage': api_config.get_alpha_vantage_config(),
        }

    async def start(self):
        """Start the spider with API session"""
        self.session = aiohttp.ClientSession()
        self.is_running = True
        logger.info(f"✅ Started {self.spider_type} spider: {self.spider_id}")

    async def stop(self):
        """Stop the spider and cleanup"""
        self.is_running = False
        if self.session:
            await self.session.close()

    def process_data(self, raw_data: Any) -> Dict[str, Any]:
        """Process raw API data into structured format"""
        return {
            'spider_id': self.spider_id,
            'spider_type': self.spider_type,
            'category': self.category,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': raw_data
        }

    async def fetch_bluesky_data(self) -> Optional[Dict]:
        """Fetch data from Bluesky API"""
        try:
            config = self.api_configs['bluesky']

            # Authenticate if needed
            if 'bluesky' not in self.tokens:
                auth_url = f"{config['base_url']}com.atproto.server.createSession"
                auth_data = {
                    "identifier": config['identifier'],
                    "password": config['password']
                }
                async with self.session.post(auth_url, json=auth_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.tokens['bluesky'] = result.get('accessJwt')
                    else:
                        logger.error(f"Bluesky auth failed: {response.status}")
                        return None

            # Fetch posts
            url = f"{config['base_url']}app.bsky.feed.searchPosts"
            headers = {"Authorization": f"Bearer {self.tokens['bluesky']}"}
            params = {"q": self.category, "limit": 10}

            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.process_data(data)
                else:
                    logger.error(f"Bluesky fetch failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Bluesky error: {e}")
            return None

    async def fetch_reddit_data(self) -> Optional[Dict]:
        """Fetch data from Reddit API"""
        try:
            config = self.api_configs['reddit']

            # Get access token if needed
            if 'reddit' not in self.tokens:
                auth = aiohttp.BasicAuth(config['client_id'], config['client_secret'])
                data = {'grant_type': 'client_credentials'}
                headers = {'User-Agent': config['user_agent']}

                async with self.session.post(
                    "https://www.reddit.com/api/v1/access_token",
                    auth=auth,
                    data=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.tokens['reddit'] = token_data['access_token']
                    else:
                        logger.error(f"Reddit auth failed: {response.status}")
                        return None

            # Fetch subreddit data
            subreddit = self._get_subreddit_for_category()
            headers = {
                'Authorization': f"bearer {self.tokens['reddit']}",
                'User-Agent': config['user_agent']
            }
            url = f"{config['base_url']}/r/{subreddit}/hot"
            params = {'limit': 10}

            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.process_data(data)
                else:
                    logger.error(f"Reddit fetch failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Reddit error: {e}")
            return None

    async def fetch_polygon_data(self) -> Optional[Dict]:
        """Fetch financial data from Polygon.io"""
        try:
            config = self.api_configs['polygon']
            ticker = self._get_ticker_for_category()

            url = f"{config['base_url']}/v2/aggs/ticker/{ticker}/prev"
            params = {"apiKey": config['api_key']}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.process_data(data)
                else:
                    logger.error(f"Polygon fetch failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Polygon error: {e}")
            return None

    async def fetch_alpha_vantage_data(self) -> Optional[Dict]:
        """Fetch financial data from Alpha Vantage"""
        try:
            config = self.api_configs['alpha_vantage']
            symbol = self._get_ticker_for_category()

            url = config['base_url']
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": config['api_key']
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        return self.process_data(data["Global Quote"])
                    else:
                        logger.warning(f"Alpha Vantage: {data.get('Note', 'No data')}")
                        return None
                else:
                    logger.error(f"Alpha Vantage fetch failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Alpha Vantage error: {e}")
            return None

    async def fetch_data(self) -> Optional[Dict]:
        """Main fetch method - chooses appropriate API based on category"""
        if not self.session:
            await self.start()

        # Choose API based on category
        if self.category == 'social':
            # Try Bluesky first, then Reddit
            data = await self.fetch_bluesky_data()
            if not data:
                data = await self.fetch_reddit_data()
            return data

        elif self.category == 'financial':
            # Try Polygon first, then Alpha Vantage
            data = await self.fetch_polygon_data()
            if not data:
                data = await self.fetch_alpha_vantage_data()
            return data

        elif self.category == 'news':
            # Use Reddit for news
            return await self.fetch_reddit_data()

        else:
            # Default to Bluesky
            return await self.fetch_bluesky_data()

    def _get_subreddit_for_category(self) -> str:
        """Get appropriate subreddit for category"""
        subreddit_map = {
            'financial': 'stocks',
            'tech': 'technology',
            'news': 'worldnews',
            'freelance': 'freelance',
            'content': 'content_marketing',
            'social': 'socialmedia'
        }
        return subreddit_map.get(self.category, 'technology')

    def _get_ticker_for_category(self) -> str:
        """Get appropriate stock ticker for testing"""
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'META', 'NVDA']
        import random
        return random.choice(tickers)


class FinancialAPISpider(RealAPISpider):
    """Specialized financial spider"""

    def __init__(self, spider_id: str):
        super().__init__(spider_id, 'financial', 'financial')


class SocialAPISpider(RealAPISpider):
    """Specialized social media spider"""

    def __init__(self, spider_id: str):
        super().__init__(spider_id, 'social', 'social')


class NewsAPISpider(RealAPISpider):
    """Specialized news spider"""

    def __init__(self, spider_id: str):
        super().__init__(spider_id, 'news', 'news')