"""
Bluesky AT Protocol Handler
Replacement for Twitter API with Bluesky's open AT Protocol
Much more developer-friendly and no expensive API fees!
"""

import os
import json
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class BlueskySession:
    """Bluesky authenticated session"""
    did: str  # Decentralized identifier
    handle: str  # Username
    access_token: str
    refresh_token: str
    service_endpoint: str = "https://bsky.social"
    expires_at: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at


class BlueskyHandler:
    """
    Handler for Bluesky AT Protocol

    Bluesky uses the AT Protocol (Authenticated Transfer Protocol)
    which is open, decentralized, and much easier to work with than Twitter's API
    """

    def __init__(self):
        self.session: Optional[BlueskySession] = None
        self.http_session: Optional[aiohttp.ClientSession] = None

        # Load credentials from environment
        self.credentials = {
            'identifier': os.environ.get('BLUESKY_IDENTIFIER', ''),  # email or handle
            'password': os.environ.get('BLUESKY_PASSWORD', ''),
            'service': os.environ.get('BLUESKY_SERVICE', 'https://bsky.social')
        }

    async def initialize(self):
        """Initialize HTTP session"""
        if not self.http_session:
            self.http_session = aiohttp.ClientSession()

    async def close(self):
        """Clean up session"""
        if self.http_session:
            await self.http_session.close()
            self.http_session = None

    def __del__(self):
        """Cleanup when instance is garbage collected"""
        if self.http_session and not self.http_session.closed:
            # Schedule cleanup for event loop
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.http_session.close())
            except:
                pass  # Best effort cleanup

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def authenticate(self) -> bool:
        """
        Authenticate with Bluesky

        Unlike Twitter's complex OAuth, Bluesky uses simple username/password
        Returns: True if authentication successful
        """
        if not self.credentials['identifier'] or not self.credentials['password']:
            logger.warning("Bluesky credentials not configured in .env")
            logger.info("Add BLUESKY_IDENTIFIER (email/handle) and BLUESKY_PASSWORD to .env")
            return False

        await self.initialize()

        # Create session with Bluesky
        url = f"{self.credentials['service']}/xrpc/com.atproto.server.createSession"

        data = {
            'identifier': self.credentials['identifier'],
            'password': self.credentials['password']
        }

        try:
            async with self.http_session.post(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()

                    self.session = BlueskySession(
                        did=result['did'],
                        handle=result['handle'],
                        access_token=result['accessJwt'],
                        refresh_token=result['refreshJwt'],
                        service_endpoint=self.credentials['service'],
                        expires_at=datetime.now() + timedelta(hours=2)  # JWT typically valid for 2 hours
                    )

                    logger.info(f"✅ Authenticated with Bluesky as @{self.session.handle}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"Failed to authenticate with Bluesky: {error}")
                    return False

        except Exception as e:
            logger.error(f"Error authenticating with Bluesky: {e}")
            return False

    async def refresh_session(self) -> bool:
        """Refresh expired session"""
        if not self.session or not self.session.refresh_token:
            return await self.authenticate()

        await self.initialize()

        url = f"{self.session.service_endpoint}/xrpc/com.atproto.server.refreshSession"

        headers = {
            'Authorization': f'Bearer {self.session.refresh_token}'
        }

        try:
            async with self.http_session.post(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()

                    self.session.access_token = result['accessJwt']
                    self.session.refresh_token = result['refreshJwt']
                    self.session.expires_at = datetime.now() + timedelta(hours=2)

                    logger.info("✅ Refreshed Bluesky session")
                    return True
                else:
                    logger.error("Failed to refresh session, re-authenticating...")
                    return await self.authenticate()

        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return await self.authenticate()

    async def ensure_authenticated(self) -> bool:
        """Ensure we have a valid authenticated session"""
        if not self.session:
            return await self.authenticate()

        if self.session.is_expired:
            return await self.refresh_session()

        return True

    async def search_posts(
        self,
        query: str,
        limit: int = 25,
        sort: str = "latest"  # "latest" or "top"
    ) -> Optional[List[Dict]]:
        """
        Search for posts on Bluesky

        Args:
            query: Search query
            limit: Maximum number of posts to return
            sort: Sort order ("latest" or "top")

        Returns:
            List of posts matching the query
        """
        if not await self.ensure_authenticated():
            return None

        # Validate query parameter
        if not query or not query.strip():
            logger.warning(f"Empty query provided to search_posts, skipping search")
            return []

        url = f"{self.session.service_endpoint}/xrpc/app.bsky.feed.searchPosts"

        headers = {
            'Authorization': f'Bearer {self.session.access_token}'
        }

        params = {
            'q': query,
            'limit': min(limit, 100),  # Max 100 per request
            'sort': sort
        }

        try:
            async with self.http_session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    posts = result.get('posts', [])

                    # Process posts to extract useful information
                    processed_posts = []
                    for post in posts:
                        processed_posts.append(self._process_post(post))

                    logger.info(f"✅ Found {len(processed_posts)} posts for query: {query}")
                    return processed_posts
                else:
                    error = await response.text()
                    logger.error(f"Failed to search posts: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            return None

    async def get_timeline(
        self,
        algorithm: str = "reverse-chronological",
        limit: int = 25
    ) -> Optional[List[Dict]]:
        """
        Get timeline/feed posts

        Args:
            algorithm: Feed algorithm to use
            limit: Maximum number of posts

        Returns:
            List of timeline posts
        """
        if not await self.ensure_authenticated():
            return None

        url = f"{self.session.service_endpoint}/xrpc/app.bsky.feed.getTimeline"

        headers = {
            'Authorization': f'Bearer {self.session.access_token}'
        }

        params = {
            'algorithm': algorithm,
            'limit': min(limit, 100)
        }

        try:
            async with self.http_session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    feed = result.get('feed', [])

                    # Process feed items
                    processed_posts = []
                    for item in feed:
                        if 'post' in item:
                            processed_posts.append(self._process_post(item['post']))

                    logger.info(f"✅ Retrieved {len(processed_posts)} timeline posts")
                    return processed_posts
                else:
                    error = await response.text()
                    logger.error(f"Failed to get timeline: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error getting timeline: {e}")
            return None

    async def get_post_thread(self, uri: str) -> Optional[Dict]:
        """
        Get a complete post thread (post with all replies)

        Args:
            uri: AT URI of the post

        Returns:
            Post thread data
        """
        if not await self.ensure_authenticated():
            return None

        url = f"{self.session.service_endpoint}/xrpc/app.bsky.feed.getPostThread"

        headers = {
            'Authorization': f'Bearer {self.session.access_token}'
        }

        params = {
            'uri': uri,
            'depth': 10  # How deep to traverse reply tree
        }

        try:
            async with self.http_session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    thread = result.get('thread', {})

                    logger.info(f"✅ Retrieved post thread")
                    return thread
                else:
                    error = await response.text()
                    logger.error(f"Failed to get post thread: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error getting post thread: {e}")
            return None

    async def get_author_feed(
        self,
        actor: str,  # Handle or DID
        limit: int = 25
    ) -> Optional[List[Dict]]:
        """
        Get posts from a specific author

        Args:
            actor: Author handle (e.g., "user.bsky.social") or DID
            limit: Maximum number of posts

        Returns:
            List of author's posts
        """
        if not await self.ensure_authenticated():
            return None

        url = f"{self.session.service_endpoint}/xrpc/app.bsky.feed.getAuthorFeed"

        headers = {
            'Authorization': f'Bearer {self.session.access_token}'
        }

        params = {
            'actor': actor,
            'limit': min(limit, 100)
        }

        try:
            async with self.http_session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    feed = result.get('feed', [])

                    # Process feed items
                    processed_posts = []
                    for item in feed:
                        if 'post' in item:
                            processed_posts.append(self._process_post(item['post']))

                    logger.info(f"✅ Retrieved {len(processed_posts)} posts from @{actor}")
                    return processed_posts
                else:
                    error = await response.text()
                    # Handle common error cases more gracefully
                    if response.status == 400 and "Profile not found" in str(error):
                        logger.warning(f"Profile @{actor} not found on Bluesky, skipping")
                        return []
                    else:
                        logger.error(f"Failed to get author feed for @{actor}: {error}")
                        return None

        except Exception as e:
            logger.error(f"Error getting author feed: {e}")
            return None

    async def create_post(
        self,
        text: str,
        reply_to: Optional[str] = None,
        embed: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create a new post on Bluesky

        Args:
            text: Post text (max 300 characters)
            reply_to: URI of post to reply to (optional)
            embed: Embedded content (links, images, etc.)

        Returns:
            Created post data
        """
        if not await self.ensure_authenticated():
            return None

        if len(text) > 300:
            logger.error(f"Post text too long: {len(text)} > 300 characters")
            return None

        url = f"{self.session.service_endpoint}/xrpc/com.atproto.repo.createRecord"

        headers = {
            'Authorization': f'Bearer {self.session.access_token}',
            'Content-Type': 'application/json'
        }

        # Build the post record
        record = {
            '$type': 'app.bsky.feed.post',
            'text': text,
            'createdAt': datetime.now().isoformat() + 'Z'
        }

        if reply_to:
            record['reply'] = {'root': reply_to, 'parent': reply_to}

        if embed:
            record['embed'] = embed

        data = {
            'repo': self.session.did,
            'collection': 'app.bsky.feed.post',
            'record': record
        }

        try:
            async with self.http_session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Created post: {text[:50]}...")
                    return result
                else:
                    error = await response.text()
                    logger.error(f"Failed to create post: {error}")
                    return None

        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None

    def _process_post(self, post: Dict) -> Dict:
        """Process raw post data into a cleaner format"""

        # Extract author info
        author = post.get('author', {})

        # Extract post record
        record = post.get('record', {})

        # Extract metrics
        viewer_state = post.get('viewer', {})

        # Count metrics
        reply_count = post.get('replyCount', 0)
        repost_count = post.get('repostCount', 0)
        like_count = post.get('likeCount', 0)

        return {
            'uri': post.get('uri', ''),
            'cid': post.get('cid', ''),
            'author': {
                'did': author.get('did', ''),
                'handle': author.get('handle', ''),
                'display_name': author.get('displayName', ''),
                'avatar': author.get('avatar', '')
            },
            'text': record.get('text', ''),
            'created_at': record.get('createdAt', ''),
            'embed': record.get('embed'),
            'metrics': {
                'replies': reply_count,
                'reposts': repost_count,
                'likes': like_count,
                'engagement': reply_count + repost_count + like_count
            },
            'viewer': {
                'liked': viewer_state.get('like') is not None,
                'reposted': viewer_state.get('repost') is not None
            },
            'labels': post.get('labels', []),
            'indexed_at': post.get('indexedAt', '')
        }

    async def get_trending(self) -> Optional[List[Dict]]:
        """
        Get trending topics/posts from Bluesky

        Note: Bluesky doesn't have official trending topics API yet,
        so we'll use popular posts as a proxy
        """
        # Search for recent popular posts
        trending_queries = [
            '',  # Empty query gets recent posts
            'news',
            'breaking',
            'tech',
            'ai'
        ]

        all_posts = []
        for query in trending_queries[:3]:  # Limit to avoid rate limiting
            posts = await self.search_posts(query, limit=10, sort="top")
            if posts:
                all_posts.extend(posts)

        # Sort by engagement
        all_posts.sort(key=lambda p: p['metrics']['engagement'], reverse=True)

        # Return top trending posts
        return all_posts[:20]


class BlueskyCollector:
    """High-level Bluesky data collector"""

    def __init__(self, handler: BlueskyHandler):
        self.handler = handler

    async def collect_intelligence(
        self,
        keywords: List[str],
        max_posts_per_keyword: int = 10
    ) -> Dict[str, Any]:
        """
        Collect intelligence from Bluesky for given keywords

        Args:
            keywords: List of keywords to search
            max_posts_per_keyword: Maximum posts per keyword

        Returns:
            Collected intelligence data
        """
        intelligence = {
            'service': 'bluesky',
            'timestamp': datetime.now().isoformat(),
            'keywords': keywords,
            'posts': [],
            'metrics': {},
            'trending': []
        }

        # Search for each keyword
        for keyword in keywords:
            posts = await self.handler.search_posts(keyword, limit=max_posts_per_keyword)
            if posts:
                intelligence['posts'].extend(posts)
                logger.info(f"✅ Found {len(posts)} posts for keyword: {keyword}")

        # Get trending posts
        trending = await self.handler.get_trending()
        if trending:
            intelligence['trending'] = trending[:10]

        # Calculate aggregate metrics
        if intelligence['posts']:
            total_engagement = sum(p['metrics']['engagement'] for p in intelligence['posts'])
            total_likes = sum(p['metrics']['likes'] for p in intelligence['posts'])
            total_reposts = sum(p['metrics']['reposts'] for p in intelligence['posts'])
            total_replies = sum(p['metrics']['replies'] for p in intelligence['posts'])

            intelligence['metrics'] = {
                'total_posts': len(intelligence['posts']),
                'total_engagement': total_engagement,
                'total_likes': total_likes,
                'total_reposts': total_reposts,
                'total_replies': total_replies,
                'avg_engagement': total_engagement / len(intelligence['posts']) if intelligence['posts'] else 0
            }

        return intelligence

    async def monitor_topics(
        self,
        topics: List[str],
        interval_minutes: int = 15
    ):
        """
        Monitor topics continuously

        Args:
            topics: Topics to monitor
            interval_minutes: Check interval in minutes
        """
        logger.info(f"🔍 Starting Bluesky monitoring for topics: {topics}")

        while True:
            try:
                intelligence = await self.collect_intelligence(topics)

                # Check for high-engagement posts
                high_engagement = [
                    p for p in intelligence['posts']
                    if p['metrics']['engagement'] > 100
                ]

                if high_engagement:
                    logger.info(f"🔥 Found {len(high_engagement)} high-engagement posts!")
                    for post in high_engagement[:3]:
                        logger.info(f"   @{post['author']['handle']}: {post['text'][:100]}...")
                        logger.info(f"   Engagement: {post['metrics']['engagement']}")

                # Wait before next check
                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                logger.error(f"Error in monitoring: {e}")
                await asyncio.sleep(60)


# Singleton instances
bluesky_handler = BlueskyHandler()
bluesky_collector = BlueskyCollector(bluesky_handler)


async def test_bluesky_handler():
    """Test Bluesky handler functionality"""
    print("\n" + "="*60)
    print("🦋 TESTING BLUESKY HANDLER")
    print("="*60)

    handler = BlueskyHandler()

    # Test authentication
    print("\n1. Testing Authentication...")
    if await handler.authenticate():
        print(f"   ✅ Authenticated as @{handler.session.handle}")

        # Search for posts
        print("\n2. Testing Post Search...")
        posts = await handler.search_posts("AI", limit=5)
        if posts:
            print(f"   ✅ Found {len(posts)} posts about AI")
            for post in posts[:2]:
                print(f"\n   @{post['author']['handle']}:")
                print(f"   {post['text'][:150]}...")
                print(f"   Engagement: {post['metrics']['engagement']} (❤️ {post['metrics']['likes']} 🔁 {post['metrics']['reposts']} 💬 {post['metrics']['replies']})")

        # Get trending
        print("\n3. Testing Trending Posts...")
        trending = await handler.get_trending()
        if trending:
            print(f"   ✅ Found {len(trending)} trending posts")
            top_post = trending[0] if trending else None
            if top_post:
                print(f"\n   Top trending post:")
                print(f"   @{top_post['author']['handle']}: {top_post['text'][:100]}...")
                print(f"   Engagement: {top_post['metrics']['engagement']}")

        # Test collector
        print("\n4. Testing Intelligence Collector...")
        collector = BlueskyCollector(handler)
        intelligence = await collector.collect_intelligence(['technology', 'programming'])

        if intelligence['posts']:
            print(f"   ✅ Collected {intelligence['metrics']['total_posts']} posts")
            print(f"   Total engagement: {intelligence['metrics']['total_engagement']}")
            print(f"   Average engagement: {intelligence['metrics']['avg_engagement']:.1f}")

    else:
        print("   ❌ Authentication failed")
        print("   Add BLUESKY_IDENTIFIER and BLUESKY_PASSWORD to .env")
        print("   Example:")
        print("     BLUESKY_IDENTIFIER=your-email@example.com")
        print("     BLUESKY_PASSWORD=your-app-password")
        print("\n   To get an app password:")
        print("   1. Go to Settings in Bluesky")
        print("   2. Click on 'App passwords'")
        print("   3. Create a new app password")

    await handler.close()

    print("\n" + "="*60)
    print("Bluesky Handler Test Complete!")


if __name__ == "__main__":
    asyncio.run(test_bluesky_handler())