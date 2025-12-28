"""
Reddit API Handler for Community Intelligence
Implements PRAW (Python Reddit API Wrapper) for comprehensive Reddit data collection
"""

import os
import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timezone
import time
import praw
from prawcore.exceptions import ResponseException
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class RedditPost:
    """Reddit post data structure"""
    id: str
    title: str
    author: str
    subreddit: str
    content: str
    score: int
    num_comments: int
    created_at: datetime
    url: str
    is_video: bool
    awards: List[str]
    flair: Optional[str] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class RedditComment:
    """Reddit comment data structure"""
    id: str
    author: str
    body: str
    score: int
    created_at: datetime
    parent_id: str
    submission_id: str
    depth: int
    awards: List[str]
    is_submitter: bool

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class SubredditInfo:
    """Subreddit information"""
    name: str
    subscribers: int
    description: str
    created_at: datetime
    rules: List[str]
    categories: List[str]

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


class RedditHandler:
    """
    Reddit API handler for extracting community intelligence.
    Uses PRAW for Reddit API access with robust error handling.
    """

    def __init__(self):
        """Initialize Reddit client with authentication"""
        self.reddit = None
        self.authenticated = False
        self.rate_limiter = RateLimiter()
        self._initialize_client()

    def _initialize_client(self):
        """Initialize PRAW Reddit client"""
        try:
            # Get Reddit API credentials from environment
            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'AI-Learning-Bot/1.0')

            if not client_id or not client_secret:
                logger.warning("Reddit API credentials not found in environment. Using read-only mode.")
                # Use read-only mode without credentials
                self.reddit = praw.Reddit(
                    client_id='your_client_id',
                    client_secret='your_client_secret',
                    user_agent=user_agent,
                    check_for_async=False
                )
                self.authenticated = False
                return

            # Initialize authenticated client
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                username=os.getenv('REDDIT_USERNAME'),
                password=os.getenv('REDDIT_PASSWORD'),
                check_for_async=False
            )

            # Verify authentication
            try:
                self.reddit.user.me()
                self.authenticated = True
                logger.info(f"Reddit API authenticated as {self.reddit.user.me()}")
            except:
                self.authenticated = False
                logger.info("Reddit API initialized in read-only mode")

        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None

    async def search_posts(self, query: str, subreddit: Optional[str] = None,
                          sort: str = 'relevance', time_filter: str = 'all',
                          limit: int = 25) -> List[RedditPost]:
        """
        Search Reddit posts

        Args:
            query: Search query
            subreddit: Specific subreddit to search (None for all)
            sort: Sort method ('relevance', 'hot', 'top', 'new', 'comments')
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
            limit: Maximum number of posts to return

        Returns:
            List of RedditPost objects
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return []

        posts = []
        try:
            await self.rate_limiter.check_rate_limit()

            # Search in specific subreddit or all
            if subreddit:
                search_target = self.reddit.subreddit(subreddit)
            else:
                search_target = self.reddit.subreddit('all')

            # Execute search
            for submission in search_target.search(query, sort=sort,
                                                  time_filter=time_filter,
                                                  limit=limit):
                post = RedditPost(
                    id=submission.id,
                    title=submission.title,
                    author=str(submission.author) if submission.author else '[deleted]',
                    subreddit=submission.subreddit.display_name,
                    content=submission.selftext or '',
                    score=submission.score,
                    num_comments=submission.num_comments,
                    created_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    url=submission.url,
                    is_video=submission.is_video,
                    awards=[award['name'] for award in submission.all_awardings],
                    flair=submission.link_flair_text
                )
                posts.append(post)

            logger.info(f"Found {len(posts)} posts for query: {query}")
            return posts

        except ResponseException as e:
            logger.error(f"Reddit API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []

    async def get_subreddit_posts(self, subreddit_name: str,
                                 sort: str = 'hot',
                                 time_filter: str = 'day',
                                 limit: int = 25) -> List[RedditPost]:
        """
        Get posts from a specific subreddit

        Args:
            subreddit_name: Name of the subreddit
            sort: Sort method ('hot', 'new', 'top', 'rising')
            time_filter: Time filter for 'top' sort
            limit: Maximum number of posts

        Returns:
            List of RedditPost objects
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return []

        posts = []
        try:
            await self.rate_limiter.check_rate_limit()

            subreddit = self.reddit.subreddit(subreddit_name)

            # Get posts based on sort method
            if sort == 'hot':
                submissions = subreddit.hot(limit=limit)
            elif sort == 'new':
                submissions = subreddit.new(limit=limit)
            elif sort == 'top':
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == 'rising':
                submissions = subreddit.rising(limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)

            for submission in submissions:
                post = RedditPost(
                    id=submission.id,
                    title=submission.title,
                    author=str(submission.author) if submission.author else '[deleted]',
                    subreddit=submission.subreddit.display_name,
                    content=submission.selftext or '',
                    score=submission.score,
                    num_comments=submission.num_comments,
                    created_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    url=submission.url,
                    is_video=submission.is_video,
                    awards=[award['name'] for award in submission.all_awardings],
                    flair=submission.link_flair_text
                )
                posts.append(post)

            logger.info(f"Retrieved {len(posts)} posts from r/{subreddit_name}")
            return posts

        except Exception as e:
            logger.error(f"Error getting subreddit posts: {e}")
            return []

    async def get_post_comments(self, post_id: str,
                               sort: str = 'best',
                               limit: int = 50) -> List[RedditComment]:
        """
        Get comments from a Reddit post

        Args:
            post_id: Reddit post ID
            sort: Comment sort ('best', 'top', 'new', 'controversial', 'old', 'qa')
            limit: Maximum number of comments

        Returns:
            List of RedditComment objects
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return []

        comments = []
        try:
            await self.rate_limiter.check_rate_limit()

            submission = self.reddit.submission(id=post_id)
            submission.comment_sort = sort
            submission.comments.replace_more(limit=0)  # Remove "load more comments"

            # Flatten comment tree
            all_comments = submission.comments.list()[:limit]

            for comment in all_comments:
                if isinstance(comment, praw.models.Comment):
                    reddit_comment = RedditComment(
                        id=comment.id,
                        author=str(comment.author) if comment.author else '[deleted]',
                        body=comment.body,
                        score=comment.score,
                        created_at=datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
                        parent_id=comment.parent_id,
                        submission_id=comment.submission.id,
                        depth=comment.depth,
                        awards=[award['name'] for award in comment.all_awardings],
                        is_submitter=comment.is_submitter
                    )
                    comments.append(reddit_comment)

            logger.info(f"Retrieved {len(comments)} comments from post {post_id}")
            return comments

        except Exception as e:
            logger.error(f"Error getting post comments: {e}")
            return []

    async def get_user_posts(self, username: str,
                           sort: str = 'new',
                           limit: int = 25) -> List[RedditPost]:
        """
        Get posts from a specific Reddit user

        Args:
            username: Reddit username
            sort: Sort method ('new', 'top', 'hot')
            limit: Maximum number of posts

        Returns:
            List of RedditPost objects
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return []

        posts = []
        try:
            await self.rate_limiter.check_rate_limit()

            redditor = self.reddit.redditor(username)

            # Get user submissions
            if sort == 'new':
                submissions = redditor.submissions.new(limit=limit)
            elif sort == 'top':
                submissions = redditor.submissions.top(limit=limit)
            elif sort == 'hot':
                submissions = redditor.submissions.hot(limit=limit)
            else:
                submissions = redditor.submissions.new(limit=limit)

            for submission in submissions:
                post = RedditPost(
                    id=submission.id,
                    title=submission.title,
                    author=str(submission.author) if submission.author else '[deleted]',
                    subreddit=submission.subreddit.display_name,
                    content=submission.selftext or '',
                    score=submission.score,
                    num_comments=submission.num_comments,
                    created_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    url=submission.url,
                    is_video=submission.is_video,
                    awards=[award['name'] for award in submission.all_awardings],
                    flair=submission.link_flair_text
                )
                posts.append(post)

            logger.info(f"Retrieved {len(posts)} posts from user {username}")
            return posts

        except Exception as e:
            logger.error(f"Error getting user posts: {e}")
            return []

    async def get_subreddit_info(self, subreddit_name: str) -> Optional[SubredditInfo]:
        """
        Get information about a subreddit

        Args:
            subreddit_name: Name of the subreddit

        Returns:
            SubredditInfo object or None
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return None

        try:
            await self.rate_limiter.check_rate_limit()

            subreddit = self.reddit.subreddit(subreddit_name)

            # Get subreddit rules
            rules = []
            try:
                for rule in subreddit.rules:
                    rules.append(rule.short_name)
            except:
                pass

            # Get categories/topics
            categories = []
            if hasattr(subreddit, 'topic'):
                categories.append(subreddit.topic)

            info = SubredditInfo(
                name=subreddit.display_name,
                subscribers=subreddit.subscribers,
                description=subreddit.public_description,
                created_at=datetime.fromtimestamp(subreddit.created_utc, tz=timezone.utc),
                rules=rules,
                categories=categories
            )

            logger.info(f"Retrieved info for r/{subreddit_name}")
            return info

        except Exception as e:
            logger.error(f"Error getting subreddit info: {e}")
            return None

    async def get_trending_topics(self, subreddits: List[str],
                                limit: int = 10) -> Dict[str, List[str]]:
        """
        Get trending topics from multiple subreddits

        Args:
            subreddits: List of subreddit names
            limit: Number of trending posts per subreddit

        Returns:
            Dictionary mapping subreddit to list of trending topics
        """
        trending = {}

        for subreddit_name in subreddits:
            posts = await self.get_subreddit_posts(
                subreddit_name,
                sort='hot',
                limit=limit
            )

            trending[subreddit_name] = [
                {
                    'title': post.title,
                    'score': post.score,
                    'comments': post.num_comments,
                    'url': f"https://reddit.com/r/{post.subreddit}/comments/{post.id}"
                }
                for post in posts
            ]

        return trending

    async def monitor_subreddit_stream(self, subreddit_name: str,
                                      callback: callable,
                                      stream_type: str = 'submissions'):
        """
        Monitor a subreddit stream in real-time

        Args:
            subreddit_name: Name of subreddit to monitor
            callback: Async callback function for new items
            stream_type: Type of stream ('submissions' or 'comments')
        """
        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            if stream_type == 'submissions':
                stream = subreddit.stream.submissions(skip_existing=True)
            else:
                stream = subreddit.stream.comments(skip_existing=True)

            logger.info(f"Starting stream monitor for r/{subreddit_name} ({stream_type})")

            for item in stream:
                await self.rate_limiter.check_rate_limit()
                await callback(item)

        except Exception as e:
            logger.error(f"Error in subreddit stream: {e}")

    async def cleanup(self):
        """Clean up Reddit client resources"""
        # PRAW handles cleanup automatically
        logger.info("Reddit handler cleaned up")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()


class RateLimiter:
    """Rate limiter for Reddit API requests"""

    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter

        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.request_times = []

    async def check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        # Check if we've exceeded rate limit
        if len(self.request_times) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = self.request_times[0]
            wait_time = 60 - (now - oldest_request) + 0.1
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)

        # Record this request
        self.request_times.append(now)


# Convenience functions for quick access
async def search_reddit(query: str, limit: int = 25) -> List[Dict]:
    """Quick Reddit search"""
    async with RedditHandler() as handler:
        posts = await handler.search_posts(query, limit=limit)
        return [post.to_dict() for post in posts]


async def get_subreddit_trending(subreddit: str, limit: int = 10) -> List[Dict]:
    """Get trending posts from a subreddit"""
    async with RedditHandler() as handler:
        posts = await handler.get_subreddit_posts(subreddit, sort='hot', limit=limit)
        return [post.to_dict() for post in posts]