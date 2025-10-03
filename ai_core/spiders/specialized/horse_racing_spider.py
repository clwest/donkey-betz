"""
Horse Racing Spider - Elite Horse Racing Intelligence Gathering
==============================================================

Specialized spider for gathering horse racing data including:
- Race schedules and results
- Jockey and trainer statistics
- Track conditions
- Betting odds and pools
- Historical performance data

Target Sources:
- Reddit (r/horseracing)
- Equibase
- Daily Racing Form (DRF)
- Horse Racing Nation
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import praw
import os

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class HorseRacingSpider(BaseIntelligenceSpider):
    """Horse racing intelligence gathering spider"""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # Initialize Reddit API with PRAW for r/horseracing
        self.reddit = None
        try:
            client_id = os.getenv('REDDIT_CLIENT_ID', '')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'unified-donkey-betz/1.0')

            if client_id and client_secret:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                self.logger.info(f"Reddit API authenticated for spider {spider_id}")
            else:
                self.logger.warning(f"Reddit API not configured for {spider_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit API: {e}")
            self.reddit = None

        self.racing_keywords = {
            'positive': ['favorite', 'strong', 'fast', 'winning', 'value', 'hot', 'sharp'],
            'negative': ['slow', 'weak', 'injured', 'cold', 'avoid', 'scratch'],
            'track_conditions': ['fast', 'muddy', 'sloppy', 'good', 'yielding', 'soft', 'heavy']
        }

    async def _fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """
        Override base _fetch_data to use PRAW API for Reddit URLs.
        """
        try:
            # For Reddit URLs, use PRAW API directly
            if 'reddit.com' in target.url and self.reddit:
                posts = await self._fetch_reddit_posts_with_praw(target.url)
                if posts:
                    return {'posts': posts, 'data_source': 'praw'}
                else:
                    self.logger.warning(f"PRAW returned no posts for {target.url}")
                    return None

            # For other URLs, use base HTTP fetching
            return await super()._fetch_data(target)

        except Exception as e:
            self.logger.error(f"Error in HorseRacingSpider._fetch_data: {e}")
            return None

    async def _fetch_reddit_posts_with_praw(self, url: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Fetch Reddit posts using PRAW API"""
        posts = []
        try:
            if not self.reddit:
                return posts

            # Extract subreddit from URL
            subreddit_name = None
            if '/r/' in url:
                parts = url.split('/r/')
                if len(parts) > 1:
                    subreddit_name = parts[1].split('/')[0]

            if not subreddit_name:
                self.logger.warning(f"Could not extract subreddit from URL: {url}")
                return posts

            # Run synchronous PRAW calls in a thread pool
            def fetch_posts():
                post_list = []
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)

                    for submission in subreddit.hot(limit=limit):
                        post = {
                            'title': submission.title,
                            'body': submission.selftext[:500] if submission.selftext else '',
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'score': submission.score,
                            'comments': submission.num_comments,
                            'subreddit': str(submission.subreddit),
                            'url': f"https://reddit.com{submission.permalink}",
                            'created': datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
                        }
                        post_list.append(post)
                except Exception as e:
                    self.logger.error(f"Error in PRAW fetch thread: {e}")
                return post_list

            # Execute in thread pool
            posts = await asyncio.to_thread(fetch_posts)

            if posts:
                self.logger.info(f"Fetched {len(posts)} posts from r/{subreddit_name} using PRAW API")

        except Exception as e:
            self.logger.error(f"Error fetching Reddit posts with PRAW: {e}")

        return posts

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process horse racing data"""
        try:
            if 'reddit.com' in target.url:
                return await self._process_reddit_racing_data(raw_data, target)
            elif 'equibase' in target.url.lower():
                return await self._process_equibase_data(raw_data, target)
            elif 'drf' in target.url.lower():
                return await self._process_drf_data(raw_data, target)
            else:
                return await self._process_general_racing_data(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing horse racing data: {e}")
            return None

    async def _process_reddit_racing_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Reddit horse racing posts"""
        try:
            posts = []
            racing_insights = {
                'race_discussions': [],
                'betting_tips': [],
                'track_reports': [],
                'jockey_trainer_mentions': {},
                'popular_horses': {}
            }

            # Get posts
            if 'posts' in data:
                posts = data['posts']
            elif 'content' in data:
                soup = BeautifulSoup(data['content'], 'html.parser')
                posts = self._extract_reddit_posts(soup)

            # Analyze each post
            for post in posts:
                text = f"{post.get('title', '')} {post.get('body', '')}".lower()

                # Extract race mentions
                if any(word in text for word in ['race', 'derby', 'stakes', 'cup', 'classic']):
                    racing_insights['race_discussions'].append({
                        'title': post.get('title', ''),
                        'score': post.get('score', 0),
                        'url': post.get('url', '')
                    })

                # Extract betting tips
                if any(word in text for word in ['pick', 'bet', 'value', 'longshot', 'favorite']):
                    racing_insights['betting_tips'].append({
                        'title': post.get('title', ''),
                        'body_preview': post.get('body', '')[:200],
                        'score': post.get('score', 0)
                    })

                # Extract track condition mentions
                track_conditions = self._extract_track_conditions(text)
                if track_conditions:
                    racing_insights['track_reports'].append({
                        'conditions': track_conditions,
                        'post': post.get('title', '')
                    })

                # Extract horse/jockey/trainer mentions
                self._extract_racing_entities(text, racing_insights)

            # Create intelligence content
            intelligence_content = {
                'posts': posts,
                'racing_insights': racing_insights,
                'sentiment_summary': self._analyze_racing_sentiment(posts),
                'trending_topics': self._identify_racing_trends(posts)
            }

            quality_score = self._calculate_racing_quality(intelligence_content)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="horse_racing_intelligence",
                content=intelligence_content,
                metadata={
                    'post_count': len(posts),
                    'race_discussions': len(racing_insights['race_discussions']),
                    'betting_tips': len(racing_insights['betting_tips']),
                    'data_source': 'reddit_horseracing'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['horse_racing', 'betting', 'reddit', 'racing_intelligence'],
                target_agents=['horse-racing-specialist', 'betting-analyst', 'value-betting-agent'],
                target_advisors=['sports_betting_expert', 'warren_buffett']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing Reddit racing data: {e}")
            return None

    def _extract_track_conditions(self, text: str) -> List[str]:
        """Extract track condition mentions"""
        conditions = []
        for condition in self.racing_keywords['track_conditions']:
            if condition in text:
                conditions.append(condition)
        return list(set(conditions))

    def _extract_racing_entities(self, text: str, insights: Dict):
        """Extract mentions of horses, jockeys, trainers"""
        # Simple pattern matching for common racing terms
        # In production, this would use NER or entity extraction
        patterns = {
            'horses': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b(?=\s+(?:won|placed|ran|finished))',
            'jockeys': r'jockey\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            'trainers': r'trainer\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        }

        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                entity = match if isinstance(match, str) else ' '.join(match)
                if entity_type == 'horses':
                    if entity not in insights['popular_horses']:
                        insights['popular_horses'][entity] = 0
                    insights['popular_horses'][entity] += 1

    def _analyze_racing_sentiment(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment in horse racing posts"""
        sentiment = {
            'positive_indicators': 0,
            'negative_indicators': 0,
            'overall_sentiment': 'neutral'
        }

        for post in posts:
            text = f"{post.get('title', '')} {post.get('body', '')}".lower()

            # Count positive/negative indicators
            for pos_word in self.racing_keywords['positive']:
                if pos_word in text:
                    sentiment['positive_indicators'] += 1

            for neg_word in self.racing_keywords['negative']:
                if neg_word in text:
                    sentiment['negative_indicators'] += 1

        # Determine overall sentiment
        if sentiment['positive_indicators'] > sentiment['negative_indicators'] * 1.5:
            sentiment['overall_sentiment'] = 'positive'
        elif sentiment['negative_indicators'] > sentiment['positive_indicators'] * 1.5:
            sentiment['overall_sentiment'] = 'negative'

        return sentiment

    def _identify_racing_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify trending topics in horse racing"""
        trends = {
            'popular_races': [],
            'hot_topics': {},
            'engagement_leaders': []
        }

        # Identify high engagement posts
        sorted_posts = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)[:5]
        trends['engagement_leaders'] = [
            {'title': p.get('title', ''), 'score': p.get('score', 0)}
            for p in sorted_posts
        ]

        # Count topic mentions
        racing_topics = ['derby', 'stakes', 'graded', 'maiden', 'claiming', 'allowance', 'handicap']
        for post in posts:
            text = f"{post.get('title', '')} {post.get('body', '')}".lower()
            for topic in racing_topics:
                if topic in text:
                    if topic not in trends['hot_topics']:
                        trends['hot_topics'][topic] = 0
                    trends['hot_topics'][topic] += 1

        return trends

    def _calculate_racing_quality(self, content: Dict[str, Any]) -> float:
        """Calculate quality score for racing intelligence"""
        score = 0.0

        # Post count
        post_count = len(content.get('posts', []))
        score += min(0.3, post_count / 30)

        # Racing insights
        insights = content.get('racing_insights', {})
        race_discussions = len(insights.get('race_discussions', []))
        betting_tips = len(insights.get('betting_tips', []))

        score += min(0.3, race_discussions / 10)
        score += min(0.2, betting_tips / 5)

        # Trending topics
        trends = content.get('trending_topics', {})
        hot_topics = len(trends.get('hot_topics', {}))
        score += min(0.2, hot_topics / 5)

        return score

    async def _process_equibase_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Equibase racing data"""
        # Placeholder for Equibase data processing
        return await self._process_general_racing_data(data, target)

    async def _process_drf_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Daily Racing Form data"""
        # Placeholder for DRF data processing
        return await self._process_general_racing_data(data, target)

    async def _process_general_racing_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general horse racing data"""
        try:
            racing_data = data.copy() if isinstance(data, dict) else {'raw_data': data}

            quality_score = self.calculate_data_quality(racing_data)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="general_racing_data",
                content=racing_data,
                metadata={
                    'data_source': 'general_racing'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['horse_racing', 'racing_data'],
                target_agents=['horse-racing-specialist', 'betting-analyst'],
                target_advisors=['sports_betting_expert']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing general racing data: {e}")
            return None

    def _extract_reddit_posts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Reddit posts from HTML (fallback method)"""
        posts = []
        try:
            for post_element in soup.find_all(['div'], class_=re.compile(r'post|thing')):
                post = {
                    'title': '',
                    'body': '',
                    'author': '',
                    'score': 0,
                    'comments': 0,
                    'url': '',
                    'created': datetime.now(timezone.utc).isoformat()
                }

                title_elem = post_element.find(['h1', 'h2', 'h3'], class_=re.compile(r'title'))
                if title_elem:
                    post['title'] = title_elem.get_text().strip()

                body_elem = post_element.find(['div', 'p'], class_=re.compile(r'body|text'))
                if body_elem:
                    post['body'] = body_elem.get_text().strip()[:500]

                if post['title']:
                    posts.append(post)

        except Exception as e:
            self.logger.warning(f"Error extracting Reddit posts: {e}")

        return posts

    def get_required_fields(self) -> List[str]:
        return ['title', 'race', 'track']

    def get_timestamp_field(self) -> Optional[str]:
        return 'created'

    def get_relevance_keywords(self) -> List[str]:
        return ['horse', 'racing', 'jockey', 'trainer', 'derby', 'stakes', 'track', 'betting']

    def validate_data_accuracy(self, data: Dict[str, Any]) -> bool:
        try:
            # Basic validation
            if 'score' in data and int(data['score']) < 0:
                return False
            return True
        except (ValueError, TypeError):
            return False
