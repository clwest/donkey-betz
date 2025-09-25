#!/usr/bin/env python3
"""
Test Real Spider Data Collection
Uses actual APIs with authentication
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealDataSpider:
    """Spider that fetches real data from APIs"""

    def __init__(self):
        self.session = None
        self.api_keys = {
            'polygon': os.getenv('POLYGON_API_KEY'),
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'reddit_client_id': os.getenv('REDDIT_CLIENT_ID'),
            'reddit_client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'bluesky_identifier': os.getenv('BLUESKY_IDENTIFIER'),
            'bluesky_password': os.getenv('BLUESKY_PASSWORD'),
        }
        self.bluesky_token = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def authenticate_bluesky(self) -> bool:
        """Authenticate with Bluesky API"""
        try:
            url = "https://bsky.social/xrpc/com.atproto.server.createSession"
            data = {
                "identifier": self.api_keys['bluesky_identifier'],
                "password": self.api_keys['bluesky_password']
            }

            async with self.session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.bluesky_token = result.get('accessJwt')
                    logger.info("✅ Bluesky authentication successful")
                    return True
                else:
                    logger.error(f"Bluesky auth failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Bluesky auth error: {e}")
            return False

    async def fetch_bluesky_posts(self, query: str = "AI") -> Optional[List[Dict]]:
        """Fetch posts from Bluesky"""
        if not self.bluesky_token:
            if not await self.authenticate_bluesky():
                return None

        try:
            url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
            headers = {"Authorization": f"Bearer {self.bluesky_token}"}
            params = {"q": query, "limit": 10}

            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    posts = data.get('posts', [])
                    logger.info(f"✅ Fetched {len(posts)} Bluesky posts")
                    return posts
                else:
                    logger.error(f"Bluesky fetch failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Bluesky fetch error: {e}")
            return None

    async def fetch_polygon_ticker(self, ticker: str = "AAPL") -> Optional[Dict]:
        """Fetch stock data from Polygon.io"""
        try:
            api_key = self.api_keys['polygon']
            if not api_key:
                logger.error("No Polygon API key found")
                return None

            # Get previous close
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
            params = {"apiKey": api_key}

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Fetched Polygon data for {ticker}")
                    return data
                else:
                    logger.error(f"Polygon fetch failed: {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text[:200]}")
                    return None
        except Exception as e:
            logger.error(f"Polygon fetch error: {e}")
            return None

    async def fetch_alpha_vantage_quote(self, symbol: str = "MSFT") -> Optional[Dict]:
        """Fetch stock quote from Alpha Vantage"""
        try:
            api_key = self.api_keys['alpha_vantage']
            if not api_key:
                logger.error("No Alpha Vantage API key found")
                return None

            url = "https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": api_key
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Global Quote" in data:
                        logger.info(f"✅ Fetched Alpha Vantage data for {symbol}")
                        return data["Global Quote"]
                    else:
                        logger.warning(f"Alpha Vantage: {data.get('Note', 'No data')}")
                        return None
                else:
                    logger.error(f"Alpha Vantage fetch failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Alpha Vantage fetch error: {e}")
            return None

    async def fetch_reddit_posts(self, subreddit: str = "technology") -> Optional[List[Dict]]:
        """Fetch posts from Reddit"""
        try:
            client_id = self.api_keys['reddit_client_id']
            client_secret = self.api_keys['reddit_client_secret']

            if not client_id or not client_secret:
                logger.error("No Reddit credentials found")
                return None

            # Get access token
            auth = aiohttp.BasicAuth(client_id, client_secret)
            data = {'grant_type': 'client_credentials'}
            headers = {'User-Agent': 'UnifiedDonkeyBetz/1.0'}

            async with self.session.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data['access_token']

                    # Fetch subreddit posts
                    headers = {
                        'Authorization': f'bearer {access_token}',
                        'User-Agent': 'UnifiedDonkeyBetz/1.0'
                    }
                    url = f"https://oauth.reddit.com/r/{subreddit}/hot"
                    params = {'limit': 10}

                    async with self.session.get(url, headers=headers, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            posts = data['data']['children']
                            logger.info(f"✅ Fetched {len(posts)} Reddit posts from r/{subreddit}")
                            return posts
                        else:
                            logger.error(f"Reddit fetch failed: {response.status}")
                            return None
                else:
                    logger.error(f"Reddit auth failed: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Reddit fetch error: {e}")
            return None


async def test_real_data_collection():
    """Test real data collection from various sources"""

    print("\n" + "="*80)
    print("REAL SPIDER DATA COLLECTION TEST")
    print("Testing with actual API endpoints")
    print("="*80 + "\n")

    results = {
        'bluesky': {'success': False, 'data': None},
        'polygon': {'success': False, 'data': None},
        'alpha_vantage': {'success': False, 'data': None},
        'reddit': {'success': False, 'data': None}
    }

    async with RealDataSpider() as spider:
        # Test Bluesky
        print("🦋 Testing Bluesky API...")
        bluesky_posts = await spider.fetch_bluesky_posts("AI")
        if bluesky_posts:
            results['bluesky']['success'] = True
            results['bluesky']['data'] = f"Fetched {len(bluesky_posts)} posts"
            print(f"  ✅ Success: {results['bluesky']['data']}")
            if bluesky_posts:
                first_post = bluesky_posts[0]
                text = first_post.get('record', {}).get('text', '')[:100]
                print(f"  Sample: {text}...")
        else:
            print("  ❌ Failed to fetch Bluesky data")

        print("\n📈 Testing Polygon.io API...")
        polygon_data = await spider.fetch_polygon_ticker("AAPL")
        if polygon_data:
            results['polygon']['success'] = True
            results['polygon']['data'] = polygon_data
            print(f"  ✅ Success: Got data for AAPL")
            if 'results' in polygon_data and polygon_data['results']:
                result = polygon_data['results'][0]
                print(f"  Close: ${result.get('c', 'N/A')}, Volume: {result.get('v', 'N/A')}")
        else:
            print("  ❌ Failed to fetch Polygon data")

        print("\n💹 Testing Alpha Vantage API...")
        av_data = await spider.fetch_alpha_vantage_quote("MSFT")
        if av_data:
            results['alpha_vantage']['success'] = True
            results['alpha_vantage']['data'] = av_data
            print(f"  ✅ Success: Got quote for MSFT")
            print(f"  Price: ${av_data.get('05. price', 'N/A')}, Volume: {av_data.get('06. volume', 'N/A')}")
        else:
            print("  ⚠️  Alpha Vantage may be rate limited (5 calls/minute for free tier)")

        print("\n🔴 Testing Reddit API...")
        reddit_posts = await spider.fetch_reddit_posts("technology")
        if reddit_posts:
            results['reddit']['success'] = True
            results['reddit']['data'] = f"Fetched {len(reddit_posts)} posts"
            print(f"  ✅ Success: {results['reddit']['data']}")
            if reddit_posts:
                first_post = reddit_posts[0]['data']
                print(f"  Sample: {first_post['title'][:80]}...")
        else:
            print("  ❌ Failed to fetch Reddit data")

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)

    print(f"\n📊 Results: {successful}/{total} APIs working")
    for api, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"  {status} {api.upper()}: {'Working' if result['success'] else 'Failed'}")

    if successful > 0:
        print("\n✅ At least some real data sources are working!")
        print("The learning pipeline can use these for continuous agent learning.")
    else:
        print("\n⚠️  No APIs returned data. Please check:")
        print("  1. API keys are correctly set in .env")
        print("  2. Internet connection is working")
        print("  3. API rate limits haven't been exceeded")

    return results


if __name__ == "__main__":
    try:
        asyncio.run(test_real_data_collection())
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")