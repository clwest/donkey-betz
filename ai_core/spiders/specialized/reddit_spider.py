"""
Reddit Spider - Community Intelligence Aggregator
==================================================

Session 263: Specialized spider for Reddit community intelligence.
Monitors tech, design, freelance, and AI subreddits for trending discussions,
job postings, and emerging trends before they hit mainstream news.

No API key required - uses public JSON endpoints.
"""

import asyncio
import aiohttp
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class RedditSpider(BaseIntelligenceSpider):
    """Reddit spider - community intelligence across multiple subreddits"""

    # Target subreddits organized by category
    SUBREDDITS = {
        'tech': [
            'webdev',
            'programming',
            'MachineLearning',
            'artificial',
            'datascience',
        ],
        'design': [
            'graphic_design',
            'design_critiques',
            'web_design',
            'UI_Design',
        ],
        'freelance': [
            'forhire',
            'freelance',
            'DesignJobs',
            'remotework',
        ],
        'creative': [
            'SideProject',
            'Entrepreneur',
            'startups',
            'IndieHackers',
        ],
        'ai_tools': [
            'StableDiffusion',
            'midjourney',
            'ChatGPT',
            'LocalLLaMA',
        ],
    }

    # All subreddits flattened for easy iteration
    ALL_SUBREDDITS = [sub for subs in SUBREDDITS.values() for sub in subs]

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.headers = {
            'User-Agent': 'DonkeyBetz-Spider/1.0 (AI Content Studio; Educational Research)'
        }

        # Keywords for opportunity detection
        self.opportunity_keywords = {
            'hiring': ['hiring', 'looking for', 'need a', 'seeking', 'job', 'position', 'remote'],
            'trending': ['trending', 'viral', 'popular', 'hot take', 'breaking'],
            'tools': ['tool', 'software', 'app', 'platform', 'just launched', 'released'],
            'learning': ['tutorial', 'guide', 'how to', 'learn', 'course', 'resource'],
        }

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch data from Reddit JSON endpoints"""
        try:
            all_posts = []

            async with aiohttp.ClientSession(headers=self.headers) as session:
                # Fetch from each subreddit category
                for category, subreddits in self.SUBREDDITS.items():
                    for subreddit in subreddits[:3]:  # Limit per category to avoid rate limits
                        try:
                            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                            async with session.get(url, timeout=10) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    posts = data.get('data', {}).get('children', [])

                                    for post in posts:
                                        post_data = post.get('data', {})
                                        if post_data.get('title'):
                                            all_posts.append({
                                                'title': post_data.get('title', ''),
                                                'selftext': post_data.get('selftext', '')[:500],
                                                'subreddit': subreddit,
                                                'category': category,
                                                'url': f"https://reddit.com{post_data.get('permalink', '')}",
                                                'score': post_data.get('score', 0),
                                                'num_comments': post_data.get('num_comments', 0),
                                                'created_utc': post_data.get('created_utc', 0),
                                                'author': post_data.get('author', ''),
                                                'is_self': post_data.get('is_self', False),
                                                'link_flair_text': post_data.get('link_flair_text', ''),
                                            })

                            # Small delay to respect rate limits
                            await asyncio.sleep(0.5)

                        except asyncio.TimeoutError:
                            self.logger.warning(f"Timeout fetching r/{subreddit}")
                        except Exception as e:
                            self.logger.warning(f"Error fetching r/{subreddit}: {e}")

            return {'posts': all_posts, 'source': 'reddit'}

        except Exception as e:
            self.logger.error(f"Error fetching Reddit data: {e}")
            return None

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Reddit posts into intelligence"""
        try:
            posts = raw_data.get('posts', [])
            processed_posts = []

            for post in posts:
                processed = self._process_post(post)
                if processed:
                    processed_posts.append(processed)

            insights = self._generate_insights(processed_posts)

            content = {
                'posts': processed_posts,
                'insights': insights,
                'by_category': self._group_by_category(processed_posts),
                'by_subreddit': self._group_by_subreddit(processed_posts),
                'trending_topics': self._extract_trending_topics(processed_posts),
                'job_opportunities': self._extract_opportunities(processed_posts),
                'tool_discoveries': self._extract_tools(processed_posts),
            }

            quality_score = min(1.0, len(processed_posts) / 50 + 0.4)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='reddit.com',
                data_type='community_intelligence',
                content=content,
                metadata={
                    'post_count': len(processed_posts),
                    'source': 'reddit',
                    'subreddits_scraped': list(set(p.get('subreddit', '') for p in posts)),
                    'categories': list(self.SUBREDDITS.keys()),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['reddit', 'community', 'trending', 'discussions', 'jobs', 'tools'],
                target_agents=['research_agent', 'trend_analysis_agent', 'content_strategy_agent'],
                target_advisors=['community_advisor', 'trend_strategist', 'content_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing Reddit data: {e}")
            return None

    def _process_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual Reddit post"""
        try:
            title = post.get('title', '')
            selftext = post.get('selftext', '')
            text = f"{title} {selftext}".lower()

            # Detect opportunity type
            opportunity_types = []
            for opp_type, keywords in self.opportunity_keywords.items():
                if any(kw in text for kw in keywords):
                    opportunity_types.append(opp_type)

            # Sentiment analysis
            blob = TextBlob(title)
            sentiment = blob.sentiment.polarity

            # Engagement score (normalized)
            score = post.get('score', 0)
            comments = post.get('num_comments', 0)
            engagement = min(1.0, (score + comments * 2) / 500)

            # Is this a job posting?
            is_job = any(word in text for word in ['hiring', 'job', 'position', 'remote', '[for hire]', '[hiring]'])

            # Is this about a tool/product?
            is_tool = any(word in text for word in ['tool', 'app', 'launched', 'built', 'made', 'created'])

            return {
                'title': title,
                'selftext': selftext[:200] if selftext else '',
                'subreddit': post.get('subreddit', ''),
                'category': post.get('category', ''),
                'url': post.get('url', ''),
                'score': score,
                'num_comments': comments,
                'engagement_score': engagement,
                'sentiment': sentiment,
                'opportunity_types': opportunity_types,
                'is_job': is_job,
                'is_tool': is_tool,
                'flair': post.get('link_flair_text', ''),
                'author': post.get('author', ''),
            }

        except Exception as e:
            self.logger.warning(f"Error processing post: {e}")
            return None

    def _generate_insights(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate community insights from posts"""
        if not posts:
            return {}

        # Category distribution
        category_counts = {}
        for post in posts:
            cat = post.get('category', 'other')
            category_counts[cat] = category_counts.get(cat, 0) + 1

        # Sentiment overview
        sentiments = [p.get('sentiment', 0) for p in posts]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        # Opportunity counts
        job_posts = [p for p in posts if p.get('is_job')]
        tool_posts = [p for p in posts if p.get('is_tool')]

        # High engagement posts
        high_engagement = [p for p in posts if p.get('engagement_score', 0) > 0.5]

        return {
            'total_posts': len(posts),
            'category_distribution': category_counts,
            'average_sentiment': round(avg_sentiment, 3),
            'sentiment_label': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral',
            'job_postings': len(job_posts),
            'tool_discoveries': len(tool_posts),
            'high_engagement_count': len(high_engagement),
            'community_pulse': 'active' if len(posts) > 30 else 'moderate' if len(posts) > 15 else 'quiet',
        }

    def _group_by_category(self, posts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group posts by category"""
        groups = {}
        for post in posts:
            cat = post.get('category', 'other')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append({
                'title': post.get('title'),
                'subreddit': post.get('subreddit'),
                'url': post.get('url'),
                'engagement': post.get('engagement_score'),
            })
        return groups

    def _group_by_subreddit(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count posts by subreddit"""
        counts = {}
        for post in posts:
            sub = post.get('subreddit', 'unknown')
            counts[sub] = counts.get(sub, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_trending_topics(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract trending topics based on engagement"""
        sorted_posts = sorted(posts, key=lambda x: x.get('engagement_score', 0), reverse=True)
        return [
            {
                'title': p.get('title'),
                'subreddit': p.get('subreddit'),
                'url': p.get('url'),
                'score': p.get('score'),
                'comments': p.get('num_comments'),
            }
            for p in sorted_posts[:10]
        ]

    def _extract_opportunities(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract job/freelance opportunities"""
        job_posts = [p for p in posts if p.get('is_job')]
        return [
            {
                'title': p.get('title'),
                'subreddit': p.get('subreddit'),
                'url': p.get('url'),
                'flair': p.get('flair'),
            }
            for p in job_posts[:10]
        ]

    def _extract_tools(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract tool/product discoveries"""
        tool_posts = [p for p in posts if p.get('is_tool')]
        sorted_tools = sorted(tool_posts, key=lambda x: x.get('engagement_score', 0), reverse=True)
        return [
            {
                'title': p.get('title'),
                'subreddit': p.get('subreddit'),
                'url': p.get('url'),
                'score': p.get('score'),
            }
            for p in sorted_tools[:10]
        ]

    def get_required_fields(self) -> List[str]:
        return ['title']

    def get_relevance_keywords(self) -> List[str]:
        return ['reddit', 'community', 'trending', 'discussion', 'jobs', 'tools', 'ai', 'design', 'programming']
