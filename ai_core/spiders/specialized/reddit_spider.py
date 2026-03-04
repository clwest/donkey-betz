"""
Reddit Spider - Community Intelligence Aggregator
===================================================

Session 534: Simplified to work with spider network interface.
Uses Reddit's public JSON endpoints (no API key required).
"""

from ai_core.spiders.web_request_layer import cached_get
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class RedditSpider:
    """Reddit spider - community intelligence across multiple subreddits"""

    name = "reddit"

    # Target subreddits organized by category
    SUBREDDITS = {
        'tech': ['webdev', 'programming', 'MachineLearning', 'artificial', 'datascience'],
        'design': ['graphic_design', 'design_critiques', 'web_design', 'UI_Design'],
        'freelance': ['forhire', 'freelance', 'DesignJobs', 'remotework'],
        'creative': ['SideProject', 'Entrepreneur', 'startups', 'IndieHackers'],
        'ai_tools': ['StableDiffusion', 'midjourney', 'ChatGPT', 'LocalLLaMA'],
    }

    # Flatten for easy access
    ALL_SUBREDDITS = [sub for subs in SUBREDDITS.values() for sub in subs]

    def __init__(self, spider_id: str = None, targets: list = None,
                 subscribers: list = None, redis_config: dict = None, **kwargs):
        """Initialize spider with optional network parameters."""
        self.spider_id = spider_id or self.name
        self.headers = {
            'User-Agent': 'DonkeyBetz-Spider/1.0 (AI Content Studio; Educational Research)'
        }
        self.opportunity_keywords = {
            'hiring': ['hiring', 'looking for', 'need a', 'seeking', 'job', 'position', 'remote'],
            'trending': ['trending', 'viral', 'popular', 'hot take', 'breaking'],
            'tools': ['tool', 'software', 'app', 'platform', 'just launched', 'released'],
            'learning': ['tutorial', 'guide', 'how to', 'learn', 'course', 'resource'],
        }

    def fetch_data(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch posts from Reddit JSON endpoints.

        Args:
            max_results: Maximum number of items to fetch

        Returns:
            List of Reddit post dictionaries
        """
        all_items = []
        seen_urls = set()

        # Fetch from each subreddit category
        for category, subreddits in self.SUBREDDITS.items():
            for subreddit in subreddits[:3]:  # Limit per category
                try:
                    items = self._fetch_subreddit(subreddit, category)
                    for item in items:
                        if item['url'] not in seen_urls:
                            seen_urls.add(item['url'])
                            all_items.append(item)
                except Exception as e:
                    logger.warning(f"Error fetching r/{subreddit}: {e}")

        # If all subreddits fail, use curated topics
        if len(all_items) == 0:
            all_items = self._get_curated_topics()

        logger.info(f"Reddit spider collected {len(all_items)} items")
        return all_items[:max_results]

    def _fetch_subreddit(self, subreddit: str, category: str) -> List[Dict[str, Any]]:
        """Fetch hot posts from a subreddit."""
        items = []

        try:
            response = cached_get(
                f"https://www.reddit.com/r/{subreddit}/hot.json",
                headers=self.headers,
                params={'limit': 10},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])

                for post in posts:
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    if not title:
                        continue

                    selftext = post_data.get('selftext', '')[:500]
                    text = f"{title} {selftext}".lower()

                    # Detect opportunity types
                    opportunity_types = self._detect_opportunities(text)
                    sentiment = self._analyze_sentiment(text)
                    is_job = self._is_job_post(text)
                    is_tool = self._is_tool_post(text)

                    score = post_data.get('score', 0)
                    comments = post_data.get('num_comments', 0)
                    engagement = min(1.0, (score + comments * 2) / 500)

                    items.append({
                        'title': title,
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'link': f"https://reddit.com{post_data.get('permalink', '')}",
                        'summary': selftext[:300] if selftext else title,
                        'description': selftext[:300] if selftext else '',
                        'subreddit': subreddit,
                        'category': category,
                        'author': post_data.get('author', ''),
                        'score': score,
                        'num_comments': comments,
                        'engagement_score': engagement,
                        'sentiment': sentiment,
                        'opportunity_types': opportunity_types,
                        'is_job': is_job,
                        'is_tool': is_tool,
                        'flair': post_data.get('link_flair_text', ''),
                        'created_utc': post_data.get('created_utc', 0),
                        'source': f"r/{subreddit}",
                        'data_type': 'community_post',
                        'platform': 'reddit',
                        'tags': ['reddit', category, subreddit],
                        'timestamp': datetime.now().isoformat(),
                    })

        except Exception as e:
            logger.warning(f"Error parsing subreddit: {e}")

        return items

    def _detect_opportunities(self, text: str) -> List[str]:
        """Detect opportunity types from text."""
        opportunities = []
        for opp_type, keywords in self.opportunity_keywords.items():
            if any(kw in text for kw in keywords):
                opportunities.append(opp_type)
        return opportunities

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze post sentiment."""
        positive_words = ['love', 'amazing', 'great', 'awesome', 'helpful', 'thanks', 'excited']
        negative_words = ['hate', 'terrible', 'awful', 'problem', 'issue', 'frustrated', 'disappointed']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'

    def _is_job_post(self, text: str) -> bool:
        """Check if post is a job listing."""
        job_keywords = ['hiring', 'job', 'position', 'remote', '[for hire]', '[hiring]', 'looking for']
        return any(kw in text for kw in job_keywords)

    def _is_tool_post(self, text: str) -> bool:
        """Check if post is about a tool/product."""
        tool_keywords = ['tool', 'app', 'launched', 'built', 'made', 'created', 'open source']
        return any(kw in text for kw in tool_keywords)

    def _get_curated_topics(self) -> List[Dict[str, Any]]:
        """Return curated topics when API fails."""
        topics = [
            ('Tech Discussions', 'tech', 'programming', 'Programming and tech talk.'),
            ('Design Community', 'design', 'graphic_design', 'Graphic design discussions.'),
            ('Freelance Jobs', 'freelance', 'forhire', 'Freelance opportunities.'),
            ('Startups', 'creative', 'startups', 'Startup and entrepreneur discussions.'),
            ('AI Tools', 'ai_tools', 'ChatGPT', 'AI and ML tool discussions.'),
        ]

        return [
            {
                'title': title,
                'url': f'https://reddit.com/r/{subreddit}',
                'link': f'https://reddit.com/r/{subreddit}',
                'summary': desc,
                'description': desc,
                'subreddit': subreddit,
                'category': category,
                'source': f"r/{subreddit}",
                'data_type': 'community_topic',
                'platform': 'reddit',
                'tags': ['reddit', category, subreddit],
                'timestamp': datetime.now().isoformat(),
            }
            for title, category, subreddit, desc in topics
        ]
