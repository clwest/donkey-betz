"""
OAuth Handler for Social Media APIs
Phase 2: Authentication & API Integration
Handles OAuth 2.0 authentication for Twitter, Reddit, LinkedIn, etc.
"""

import os
import json
import time
import base64
import hashlib
import secrets
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OAuthToken:
    """OAuth token with metadata"""
    access_token: str
    token_type: str
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    service: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at

    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refresh (5 minutes before expiry)"""
        if not self.expires_at:
            return False
        return datetime.now() >= (self.expires_at - timedelta(minutes=5))


class OAuthHandler:
    """Handles OAuth 2.0 authentication for various services"""

    def __init__(self):
        self.tokens: Dict[str, OAuthToken] = {}
        self.credentials = self._load_credentials()
        self.session = None

    def _load_credentials(self) -> Dict[str, Dict[str, str]]:
        """Load OAuth credentials from environment"""
        return {
            'twitter': {
                'client_id': os.environ.get('TWITTER_CLIENT_ID', ''),
                'client_secret': os.environ.get('TWITTER_CLIENT_SECRET', ''),
                'bearer_token': os.environ.get('TWITTER_BEARER_TOKEN', ''),
                'redirect_uri': 'http://localhost:8000/oauth/twitter/callback'
            },
            'reddit': {
                'client_id': os.environ.get('REDDIT_CLIENT_ID', ''),
                'client_secret': os.environ.get('REDDIT_CLIENT_SECRET', ''),
                'user_agent': 'SpiderArmy/1.0 by DonkeyKing',
                'redirect_uri': 'http://localhost:8000/oauth/reddit/callback'
            },
            'linkedin': {
                'client_id': os.environ.get('LINKEDIN_CLIENT_ID', ''),
                'client_secret': os.environ.get('LINKEDIN_CLIENT_SECRET', ''),
                'redirect_uri': 'http://localhost:8000/oauth/linkedin/callback'
            },
            'facebook': {
                'app_id': os.environ.get('FACEBOOK_APP_ID', ''),
                'app_secret': os.environ.get('FACEBOOK_APP_SECRET', ''),
                'redirect_uri': 'http://localhost:8000/oauth/facebook/callback'
            }
        }

    async def initialize(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Clean up session"""
        if self.session:
            await self.session.close()

    # ==================== Twitter OAuth 2.0 ====================

    async def get_twitter_bearer_token(self) -> Optional[str]:
        """Get Twitter Bearer token for App-only authentication"""
        # First check if we have it in environment
        bearer_token = self.credentials['twitter'].get('bearer_token')
        if bearer_token:
            return bearer_token

        # Otherwise, generate it from client credentials
        client_id = self.credentials['twitter'].get('client_id')
        client_secret = self.credentials['twitter'].get('client_secret')

        if not client_id or not client_secret:
            logger.error("Twitter client credentials not configured")
            return None

        await self.initialize()

        # Create Basic auth header
        credentials = f"{client_id}:{client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        data = {'grant_type': 'client_credentials'}

        try:
            async with self.session.post(
                'https://api.twitter.com/oauth2/token',
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result.get('access_token')
                    self.tokens['twitter'] = OAuthToken(
                        access_token=token,
                        token_type='bearer',
                        service='twitter'
                    )
                    return token
                else:
                    error = await response.text()
                    logger.error(f"Failed to get Twitter bearer token: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error getting Twitter bearer token: {e}")
            return None

    async def fetch_twitter_data(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Fetch data from Twitter API v2"""
        bearer_token = await self.get_twitter_bearer_token()
        if not bearer_token:
            return None

        await self.initialize()

        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'User-Agent': 'SpiderArmy v1.0'
        }

        url = f"https://api.twitter.com/2/{endpoint}"

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Twitter API error: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error fetching Twitter data: {e}")
            return None

    async def search_tweets(self, query: str, max_results: int = 10) -> Optional[List[Dict]]:
        """Search for tweets using Twitter API v2"""
        params = {
            'query': query,
            'max_results': min(max_results, 100),  # Max 100 per request
            'tweet.fields': 'created_at,author_id,public_metrics,context_annotations,entities'
        }

        result = await self.fetch_twitter_data('tweets/search/recent', params)
        if result:
            return result.get('data', [])
        return None

    async def get_trending_topics(self, woeid: int = 1) -> Optional[List[Dict]]:
        """Get trending topics for a location (WOEID)"""
        # Note: This requires v1.1 API which has different auth
        # For now, we'll use a simplified approach
        logger.warning("Trending topics require Twitter API v1.1 - using search as fallback")

        # Search for popular recent tweets as a proxy for trends
        trending_searches = [
            'trending', 'breaking news', 'viral', '#trending'
        ]

        all_tweets = []
        for search in trending_searches:
            tweets = await self.search_tweets(search, max_results=5)
            if tweets:
                all_tweets.extend(tweets)

        return all_tweets

    # ==================== Reddit OAuth 2.0 ====================

    async def get_reddit_token(self) -> Optional[str]:
        """Get Reddit access token using client credentials"""
        client_id = self.credentials['reddit'].get('client_id')
        client_secret = self.credentials['reddit'].get('client_secret')

        if not client_id or not client_secret:
            logger.error("Reddit client credentials not configured")
            return None

        # Check if we have a valid token
        if 'reddit' in self.tokens and not self.tokens['reddit'].is_expired:
            return self.tokens['reddit'].access_token

        await self.initialize()

        # Create auth header
        auth = aiohttp.BasicAuth(client_id, client_secret)

        headers = {
            'User-Agent': self.credentials['reddit'].get('user_agent', 'SpiderArmy/1.0')
        }

        data = {
            'grant_type': 'client_credentials',
            'device_id': 'DO_NOT_TRACK_THIS_DEVICE'
        }

        try:
            async with self.session.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result.get('access_token')
                    expires_in = result.get('expires_in', 3600)

                    self.tokens['reddit'] = OAuthToken(
                        access_token=token,
                        token_type='bearer',
                        expires_at=datetime.now() + timedelta(seconds=expires_in),
                        service='reddit'
                    )
                    return token
                else:
                    error = await response.text()
                    logger.error(f"Failed to get Reddit token: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error getting Reddit token: {e}")
            return None

    async def fetch_reddit_data(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Fetch data from Reddit API"""
        token = await self.get_reddit_token()
        if not token:
            return None

        await self.initialize()

        headers = {
            'Authorization': f'Bearer {token}',
            'User-Agent': self.credentials['reddit'].get('user_agent', 'SpiderArmy/1.0')
        }

        url = f"https://oauth.reddit.com/{endpoint}"

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    logger.error(f"Reddit API error: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error fetching Reddit data: {e}")
            return None

    async def get_subreddit_posts(self, subreddit: str, sort: str = 'hot', limit: int = 10) -> Optional[List[Dict]]:
        """Get posts from a subreddit"""
        params = {
            'limit': min(limit, 100),
            'raw_json': 1
        }

        result = await self.fetch_reddit_data(f"r/{subreddit}/{sort}", params)
        if result and 'data' in result:
            posts = result['data'].get('children', [])
            return [post['data'] for post in posts]
        return None

    async def search_reddit(self, query: str, subreddit: Optional[str] = None, limit: int = 10) -> Optional[List[Dict]]:
        """Search Reddit posts"""
        endpoint = f"r/{subreddit}/search" if subreddit else "search"
        params = {
            'q': query,
            'limit': min(limit, 100),
            'sort': 'relevance',
            'raw_json': 1
        }

        if subreddit:
            params['restrict_sr'] = 'true'

        result = await self.fetch_reddit_data(endpoint, params)
        if result and 'data' in result:
            posts = result['data'].get('children', [])
            return [post['data'] for post in posts]
        return None

    # ==================== LinkedIn OAuth 2.0 ====================

    async def get_linkedin_auth_url(self, state: str = None) -> str:
        """Generate LinkedIn OAuth authorization URL"""
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            'response_type': 'code',
            'client_id': self.credentials['linkedin'].get('client_id'),
            'redirect_uri': self.credentials['linkedin'].get('redirect_uri'),
            'state': state,
            'scope': 'r_liteprofile r_emailaddress w_member_social'
        }

        return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"

    async def exchange_linkedin_code(self, code: str) -> Optional[OAuthToken]:
        """Exchange LinkedIn authorization code for access token"""
        await self.initialize()

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.credentials['linkedin'].get('client_id'),
            'client_secret': self.credentials['linkedin'].get('client_secret'),
            'redirect_uri': self.credentials['linkedin'].get('redirect_uri')
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            async with self.session.post(
                'https://www.linkedin.com/oauth/v2/accessToken',
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    token = OAuthToken(
                        access_token=result.get('access_token'),
                        token_type='Bearer',
                        expires_at=datetime.now() + timedelta(seconds=result.get('expires_in', 3600)),
                        service='linkedin'
                    )
                    self.tokens['linkedin'] = token
                    return token
                else:
                    error = await response.text()
                    logger.error(f"Failed to exchange LinkedIn code: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error exchanging LinkedIn code: {e}")
            return None

    # ==================== Generic OAuth Methods ====================

    def generate_code_verifier(self) -> str:
        """Generate PKCE code verifier for OAuth 2.0"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

    def generate_code_challenge(self, verifier: str) -> str:
        """Generate PKCE code challenge from verifier"""
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

    def get_token(self, service: str) -> Optional[OAuthToken]:
        """Get stored token for a service"""
        return self.tokens.get(service)

    def is_authenticated(self, service: str) -> bool:
        """Check if we have valid authentication for a service"""
        token = self.tokens.get(service)
        return token is not None and not token.is_expired

    async def refresh_token(self, service: str) -> Optional[OAuthToken]:
        """Refresh an expired token"""
        token = self.tokens.get(service)
        if not token or not token.refresh_token:
            logger.warning(f"No refresh token available for {service}")
            return None

        # Service-specific refresh logic would go here
        # For now, return None as most services need specific implementation
        logger.warning(f"Token refresh not implemented for {service}")
        return None


class SocialMediaCollector:
    """High-level social media data collector using OAuth"""

    def __init__(self, oauth_handler: OAuthHandler):
        self.oauth = oauth_handler

    async def collect_twitter_intelligence(self, keywords: List[str]) -> Dict[str, Any]:
        """Collect Twitter intelligence for given keywords"""
        intelligence = {
            'service': 'twitter',
            'timestamp': datetime.now().isoformat(),
            'keywords': keywords,
            'tweets': [],
            'metrics': {}
        }

        for keyword in keywords:
            tweets = await self.oauth.search_tweets(keyword, max_results=10)
            if tweets:
                intelligence['tweets'].extend(tweets)

        # Calculate metrics
        if intelligence['tweets']:
            total_likes = sum(t.get('public_metrics', {}).get('like_count', 0) for t in intelligence['tweets'])
            total_retweets = sum(t.get('public_metrics', {}).get('retweet_count', 0) for t in intelligence['tweets'])

            intelligence['metrics'] = {
                'total_tweets': len(intelligence['tweets']),
                'total_likes': total_likes,
                'total_retweets': total_retweets,
                'avg_engagement': (total_likes + total_retweets) / len(intelligence['tweets']) if intelligence['tweets'] else 0
            }

        return intelligence

    async def collect_reddit_intelligence(self, subreddits: List[str], keywords: List[str]) -> Dict[str, Any]:
        """Collect Reddit intelligence from subreddits and keywords"""
        intelligence = {
            'service': 'reddit',
            'timestamp': datetime.now().isoformat(),
            'subreddits': subreddits,
            'keywords': keywords,
            'posts': [],
            'metrics': {}
        }

        # Get hot posts from subreddits
        for subreddit in subreddits:
            posts = await self.oauth.get_subreddit_posts(subreddit, sort='hot', limit=5)
            if posts:
                intelligence['posts'].extend(posts)

        # Search for keywords
        for keyword in keywords:
            search_results = await self.oauth.search_reddit(keyword, limit=5)
            if search_results:
                intelligence['posts'].extend(search_results)

        # Calculate metrics
        if intelligence['posts']:
            total_score = sum(p.get('score', 0) for p in intelligence['posts'])
            total_comments = sum(p.get('num_comments', 0) for p in intelligence['posts'])

            intelligence['metrics'] = {
                'total_posts': len(intelligence['posts']),
                'total_score': total_score,
                'total_comments': total_comments,
                'avg_score': total_score / len(intelligence['posts']) if intelligence['posts'] else 0
            }

        return intelligence

    async def collect_trending_topics(self) -> Dict[str, Any]:
        """Collect trending topics from multiple sources"""
        trending = {
            'timestamp': datetime.now().isoformat(),
            'twitter': [],
            'reddit': [],
            'combined': []
        }

        # Get Twitter trends (simplified)
        twitter_trends = await self.oauth.get_trending_topics()
        if twitter_trends:
            trending['twitter'] = twitter_trends[:10]

        # Get Reddit hot posts as trending
        reddit_hot = await self.oauth.get_subreddit_posts('all', sort='hot', limit=10)
        if reddit_hot:
            trending['reddit'] = reddit_hot

        # Combine and rank
        # This is a simplified combination - in production you'd want more sophisticated ranking
        trending['combined'] = trending['twitter'][:5] + trending['reddit'][:5]

        return trending


# Singleton instances
oauth_handler = OAuthHandler()
social_collector = SocialMediaCollector(oauth_handler)


async def test_oauth_handler():
    """Test OAuth handler functionality"""
    print("Testing OAuth Handler\n" + "="*50)

    handler = OAuthHandler()

    # Test Twitter
    print("\n1. Testing Twitter OAuth...")
    bearer_token = await handler.get_twitter_bearer_token()
    if bearer_token:
        print("   ✅ Got Twitter bearer token")

        # Search for tweets
        tweets = await handler.search_tweets("AI", max_results=3)
        if tweets:
            print(f"   ✅ Found {len(tweets)} tweets about AI")
            for tweet in tweets[:2]:
                text = tweet.get('text', '')[:100]
                print(f"      - {text}...")
        else:
            print("   ⚠️ No tweets found or API not configured")
    else:
        print("   ❌ Twitter credentials not configured")

    # Test Reddit
    print("\n2. Testing Reddit OAuth...")
    reddit_token = await handler.get_reddit_token()
    if reddit_token:
        print("   ✅ Got Reddit access token")

        # Get posts from r/programming
        posts = await handler.get_subreddit_posts('programming', limit=3)
        if posts:
            print(f"   ✅ Found {len(posts)} posts from r/programming")
            for post in posts[:2]:
                title = post.get('title', '')[:80]
                score = post.get('score', 0)
                print(f"      - [{score}] {title}...")
        else:
            print("   ⚠️ Could not fetch Reddit posts")
    else:
        print("   ❌ Reddit credentials not configured")

    # Test Social Media Collector
    print("\n3. Testing Social Media Collector...")
    collector = SocialMediaCollector(handler)

    # Collect Twitter intelligence
    twitter_intel = await collector.collect_twitter_intelligence(['python', 'AI'])
    if twitter_intel['tweets']:
        print(f"   ✅ Twitter Intelligence: {twitter_intel['metrics']['total_tweets']} tweets collected")
        print(f"      - Average engagement: {twitter_intel['metrics']['avg_engagement']:.1f}")
    else:
        print("   ⚠️ No Twitter intelligence collected")

    # Collect Reddit intelligence
    reddit_intel = await collector.collect_reddit_intelligence(['programming', 'machinelearning'], ['AI', 'python'])
    if reddit_intel['posts']:
        print(f"   ✅ Reddit Intelligence: {reddit_intel['metrics']['total_posts']} posts collected")
        print(f"      - Average score: {reddit_intel['metrics']['avg_score']:.1f}")
    else:
        print("   ⚠️ No Reddit intelligence collected")

    await handler.close()

    print("\n" + "="*50)
    print("OAuth Handler Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_oauth_handler())