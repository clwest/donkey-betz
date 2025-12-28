"""
Reddit Search and Sentiment Analysis Tool

This tool provides access to Reddit for social sentiment analysis,
trending topics, and community discussions.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from django.core.cache import cache

from .base import BaseTool

logger = logging.getLogger(__name__)


class RedditSearchTool(BaseTool):
    """Reddit search and sentiment analysis tool."""
    
    name = "reddit_api"
    description = "Search Reddit for discussions, sentiment, and trending topics"
    requires_auth = True
    tool_type = "research"
    
    def __init__(self):
        """Initialize the Reddit search tool."""
        self.reddit = None
        self.praw = None
        self.cache_duration = 1800  # Cache for 30 minutes
        super().__init__()
    
    def _check_configuration(self) -> bool:
        """Check if Reddit API is configured."""
        try:
            import praw
            self.praw = praw
            
            # Check for Reddit API credentials
            client_id = os.getenv('REDDIT_CLIENT_ID', '')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'unified-donkey-betz/1.0')
            
            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                return True
            else:
                logger.warning("Reddit API credentials not configured")
                return False
                
        except ImportError:
            logger.error("praw library not installed. Run: pip install praw")
            return False
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return [
            'subreddit_search',
            'post_search',
            'comment_analysis',
            'sentiment_analysis',
            'trending_topics',
            'user_activity'
        ]
    
    def execute(self, query: str, search_type: str = 'posts', subreddit: str = 'all', 
                limit: int = 25, sort: str = 'relevance', **kwargs) -> Dict[str, Any]:
        """
        Execute a Reddit search.
        
        Args:
            query: Search query string
            search_type: Type of search ('posts', 'subreddits', 'comments')
            subreddit: Specific subreddit or 'all'
            limit: Maximum number of results
            sort: Sort order ('relevance', 'hot', 'top', 'new')
            **kwargs: Additional search parameters
        
        Returns:
            Dict with search results or error
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="Reddit API not configured. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"
            )
        
        if not self.validate_input(query=query, search_type=search_type):
            return self.format_result(
                success=False,
                error="Invalid input parameters"
            )
        
        # Check cache first
        cache_key = f"reddit_{search_type}_{subreddit}_{query}_{limit}_{sort}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Returning cached Reddit results for: {query}")
            return cached
        
        try:
            if search_type == 'posts':
                results = self._search_posts(query, subreddit, limit, sort, **kwargs)
            elif search_type == 'subreddits':
                results = self._search_subreddits(query, limit)
            elif search_type == 'comments':
                results = self._search_comments(query, subreddit, limit, **kwargs)
            else:
                return self.format_result(
                    success=False,
                    error=f"Unsupported search type: {search_type}"
                )
            
            # Format and cache result
            result = self.format_result(
                success=True,
                data={
                    'query': query,
                    'search_type': search_type,
                    'subreddit': subreddit,
                    'results': results,
                    'total_results': len(results),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            cache.set(cache_key, result, self.cache_duration)
            return result
            
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    def _search_posts(self, query: str, subreddit: str, limit: int, sort: str, **kwargs) -> List[Dict[str, Any]]:
        """Search Reddit posts."""
        results = []
        
        # Get subreddit object
        if subreddit == 'all':
            subreddit_obj = self.reddit.subreddit('all')
        else:
            subreddit_obj = self.reddit.subreddit(subreddit)
        
        # Search posts
        for post in subreddit_obj.search(query, sort=sort, limit=limit, time_filter=kwargs.get('time_filter', 'all')):
            results.append({
                'id': post.id,
                'title': post.title,
                'author': str(post.author) if post.author else '[deleted]',
                'subreddit': str(post.subreddit),
                'url': f"https://reddit.com{post.permalink}",
                'score': post.score,
                'upvote_ratio': post.upvote_ratio,
                'num_comments': post.num_comments,
                'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                'selftext': post.selftext[:500] if post.selftext else '',
                'link_url': post.url if not post.is_self else None,
                'awards': len(post.all_awardings) if hasattr(post, 'all_awardings') else 0,
                'is_video': post.is_video if hasattr(post, 'is_video') else False
            })
        
        return results
    
    def _search_subreddits(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search for subreddits."""
        results = []
        
        for subreddit in self.reddit.subreddits.search(query, limit=limit):
            results.append({
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.public_description[:500],
                'subscribers': subreddit.subscribers,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc).isoformat(),
                'url': f"https://reddit.com/r/{subreddit.display_name}",
                'over_18': subreddit.over18
            })
        
        return results
    
    def _search_comments(self, query: str, subreddit: str, limit: int, **kwargs) -> List[Dict[str, Any]]:
        """Search Reddit comments."""
        results = []
        
        # This is more complex and would typically use pushshift.io API
        # For now, return a limited implementation
        if subreddit == 'all':
            subreddit_obj = self.reddit.subreddit('all')
        else:
            subreddit_obj = self.reddit.subreddit(subreddit)
        
        # Search in recent posts and get comments
        for post in subreddit_obj.search(query, limit=min(limit, 10)):
            post.comments.replace_more(limit=0)
            for comment in post.comments.list()[:5]:  # Get first 5 comments per post
                if hasattr(comment, 'body'):
                    results.append({
                        'id': comment.id,
                        'body': comment.body[:500],
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat(),
                        'post_title': post.title,
                        'post_id': post.id,
                        'permalink': f"https://reddit.com{comment.permalink}",
                        'is_submitter': comment.is_submitter if hasattr(comment, 'is_submitter') else False
                    })
                
                if len(results) >= limit:
                    break
            
            if len(results) >= limit:
                break
        
        return results[:limit]
    
    def get_trending(self, subreddit: str = 'all', limit: int = 10, time_filter: str = 'day') -> Dict[str, Any]:
        """
        Get trending posts from Reddit.
        
        Args:
            subreddit: Subreddit name or 'all'
            limit: Number of posts to retrieve
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
        
        Returns:
            Dict with trending posts
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="Reddit API not configured"
            )
        
        try:
            if subreddit == 'all':
                subreddit_obj = self.reddit.subreddit('all')
            else:
                subreddit_obj = self.reddit.subreddit(subreddit)
            
            posts = []
            for post in subreddit_obj.top(time_filter=time_filter, limit=limit):
                posts.append({
                    'title': post.title,
                    'score': post.score,
                    'subreddit': str(post.subreddit),
                    'url': f"https://reddit.com{post.permalink}",
                    'num_comments': post.num_comments,
                    'created_utc': datetime.fromtimestamp(post.created_utc).isoformat()
                })
            
            return self.format_result(
                success=True,
                data={
                    'subreddit': subreddit,
                    'time_filter': time_filter,
                    'posts': posts
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting trending posts: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    def analyze_sentiment(self, subreddit: str, topic: str, limit: int = 100) -> Dict[str, Any]:
        """
        Analyze sentiment for a topic in a subreddit.
        
        Args:
            subreddit: Subreddit to analyze
            topic: Topic/keyword to analyze
            limit: Number of posts to analyze
        
        Returns:
            Dict with sentiment analysis
        """
        if not self.is_configured:
            return self.format_result(
                success=False,
                error="Reddit API not configured"
            )
        
        try:
            results = self._search_posts(topic, subreddit, limit, 'relevance')
            
            # Simple sentiment analysis based on scores and ratios
            total_score = sum(post['score'] for post in results)
            avg_score = total_score / len(results) if results else 0
            avg_ratio = sum(post['upvote_ratio'] for post in results) / len(results) if results else 0
            total_comments = sum(post['num_comments'] for post in results)
            
            # Determine overall sentiment
            if avg_ratio > 0.8 and avg_score > 10:
                sentiment = 'positive'
            elif avg_ratio < 0.5 or avg_score < 0:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return self.format_result(
                success=True,
                data={
                    'topic': topic,
                    'subreddit': subreddit,
                    'posts_analyzed': len(results),
                    'sentiment': sentiment,
                    'metrics': {
                        'average_score': avg_score,
                        'average_upvote_ratio': avg_ratio,
                        'total_comments': total_comments,
                        'engagement_rate': total_comments / len(results) if results else 0
                    },
                    'top_posts': results[:5] if results else []
                }
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self.format_result(
                success=False,
                error=str(e)
            )
    
    def validate_input(self, query: str = None, search_type: str = None, **kwargs) -> bool:
        """Validate input parameters."""
        if query and (not isinstance(query, str) or len(query.strip()) == 0):
            return False
        
        if search_type and search_type not in ['posts', 'subreddits', 'comments']:
            return False
        
        return True