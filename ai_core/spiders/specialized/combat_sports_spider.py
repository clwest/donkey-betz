"""
Combat Sports Spider - UFC/MMA/Boxing Intelligence Gathering
===========================================================

Specialized spider for gathering combat sports data including:
- Fight cards and results
- Fighter statistics and rankings
- Betting odds and line movements
- Injury reports and weight cut issues
- Training camp news

Target Sources:
- Reddit (r/MMA, r/ufc, r/Boxing)
- UFC Stats
- Sherdog
- Tapology
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


class CombatSportsSpider(BaseIntelligenceSpider):
    """Combat sports (UFC/MMA/Boxing) intelligence gathering spider"""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        # Initialize Reddit API with PRAW
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

        self.combat_keywords = {
            'positive': ['dominant', 'finishing', 'sharp', 'motivated', 'prepared', 'favor', 'value'],
            'negative': ['injured', 'weight cut issues', 'unmotivated', 'age', 'decline', 'avoid'],
            'fight_outcomes': ['ko', 'tko', 'submission', 'decision', 'split', 'unanimous', 'finish'],
            'betting_terms': ['underdog', 'favorite', 'odds', 'line', 'parlay', 'value', 'lock']
        }

    async def _fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Override base _fetch_data to use PRAW API for Reddit URLs"""
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
            self.logger.error(f"Error in CombatSportsSpider._fetch_data: {e}")
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
        """Process combat sports data"""
        try:
            if 'reddit.com' in target.url:
                return await self._process_reddit_combat_data(raw_data, target)
            elif 'ufc.com' in target.url.lower():
                return await self._process_ufc_data(raw_data, target)
            elif 'sherdog' in target.url.lower():
                return await self._process_sherdog_data(raw_data, target)
            else:
                return await self._process_general_combat_data(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing combat sports data: {e}")
            return None

    async def _process_reddit_combat_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Reddit combat sports posts"""
        try:
            posts = []
            combat_insights = {
                'fight_discussions': [],
                'betting_analysis': [],
                'injury_reports': [],
                'fighter_mentions': {},
                'event_buzz': {}
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

                # Extract fight discussions
                if any(word in text for word in ['fight', 'card', 'event', 'ufc', 'ppv', 'main event']):
                    combat_insights['fight_discussions'].append({
                        'title': post.get('title', ''),
                        'score': post.get('score', 0),
                        'url': post.get('url', '')
                    })

                # Extract betting analysis
                if any(word in text for word in self.combat_keywords['betting_terms']):
                    combat_insights['betting_analysis'].append({
                        'title': post.get('title', ''),
                        'body_preview': post.get('body', '')[:200],
                        'score': post.get('score', 0)
                    })

                # Extract injury/weight cut reports
                if any(word in text for word in ['injured', 'injury', 'weight', 'cut', 'pull out', 'withdrawal']):
                    combat_insights['injury_reports'].append({
                        'title': post.get('title', ''),
                        'urgency': 'high' if post.get('score', 0) > 100 else 'medium'
                    })

                # Extract fighter mentions
                self._extract_fighter_mentions(text, combat_insights)

                # Extract event buzz
                self._extract_event_buzz(text, combat_insights)

            # Create intelligence content
            intelligence_content = {
                'posts': posts,
                'combat_insights': combat_insights,
                'sentiment_summary': self._analyze_combat_sentiment(posts),
                'trending_topics': self._identify_combat_trends(posts)
            }

            quality_score = self._calculate_combat_quality(intelligence_content)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="combat_sports_intelligence",
                content=intelligence_content,
                metadata={
                    'post_count': len(posts),
                    'fight_discussions': len(combat_insights['fight_discussions']),
                    'betting_analysis': len(combat_insights['betting_analysis']),
                    'data_source': 'reddit_combat_sports'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['combat_sports', 'ufc', 'mma', 'boxing', 'betting'],
                target_agents=['combat-sports-specialist', 'betting-analyst', 'value-betting-agent'],
                target_advisors=['sports_betting_expert', 'combat_sports_analyst']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing Reddit combat data: {e}")
            return None

    def _extract_fighter_mentions(self, text: str, insights: Dict):
        """Extract fighter name mentions"""
        # Common MMA fighter name patterns
        # In production, this would use a fighter database or NER
        fighter_indicators = ['vs', 'versus', 'fight', 'fighter', 'champion']

        for indicator in fighter_indicators:
            if indicator in text:
                # Simple extraction - in production use proper NER
                words = text.split()
                if indicator in words:
                    idx = words.index(indicator)
                    # Look for capitalized words nearby (potential fighter names)
                    for i in range(max(0, idx-3), min(len(words), idx+3)):
                        word = words[i]
                        if len(word) > 2 and word[0].isupper():
                            if word not in insights['fighter_mentions']:
                                insights['fighter_mentions'][word] = 0
                            insights['fighter_mentions'][word] += 1

    def _extract_event_buzz(self, text: str, insights: Dict):
        """Extract event mentions and buzz"""
        event_patterns = [
            r'ufc\s+\d+',  # UFC 300
            r'ufc\s+[a-z]+\s+\d+',  # UFC Fight Night 123
        ]

        for pattern in event_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                event_name = match.upper()
                if event_name not in insights['event_buzz']:
                    insights['event_buzz'][event_name] = 0
                insights['event_buzz'][event_name] += 1

    def _analyze_combat_sentiment(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment in combat sports posts"""
        sentiment = {
            'positive_indicators': 0,
            'negative_indicators': 0,
            'finish_probability': 'unknown',
            'overall_sentiment': 'neutral'
        }

        finish_mentions = 0
        decision_mentions = 0

        for post in posts:
            text = f"{post.get('title', '')} {post.get('body', '')}".lower()

            # Count positive/negative indicators
            for pos_word in self.combat_keywords['positive']:
                if pos_word in text:
                    sentiment['positive_indicators'] += 1

            for neg_word in self.combat_keywords['negative']:
                if neg_word in text:
                    sentiment['negative_indicators'] += 1

            # Count finish vs decision mentions
            if any(word in text for word in ['ko', 'tko', 'submission', 'finish']):
                finish_mentions += 1
            if 'decision' in text:
                decision_mentions += 1

        # Determine finish probability
        if finish_mentions > decision_mentions * 1.5:
            sentiment['finish_probability'] = 'high'
        elif decision_mentions > finish_mentions * 1.5:
            sentiment['finish_probability'] = 'low'
        else:
            sentiment['finish_probability'] = 'medium'

        # Determine overall sentiment
        if sentiment['positive_indicators'] > sentiment['negative_indicators'] * 1.5:
            sentiment['overall_sentiment'] = 'positive'
        elif sentiment['negative_indicators'] > sentiment['positive_indicators'] * 1.5:
            sentiment['overall_sentiment'] = 'negative'

        return sentiment

    def _identify_combat_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify trending topics in combat sports"""
        trends = {
            'hot_fighters': [],
            'upcoming_events': {},
            'engagement_leaders': []
        }

        # Identify high engagement posts
        sorted_posts = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)[:5]
        trends['engagement_leaders'] = [
            {'title': p.get('title', ''), 'score': p.get('score', 0)}
            for p in sorted_posts
        ]

        # Count event/topic mentions
        combat_topics = ['ppv', 'main event', 'title fight', 'championship', 'contender', 'knockout']
        for post in posts:
            text = f"{post.get('title', '')} {post.get('body', '')}".lower()
            for topic in combat_topics:
                if topic in text:
                    if topic not in trends['upcoming_events']:
                        trends['upcoming_events'][topic] = 0
                    trends['upcoming_events'][topic] += 1

        return trends

    def _calculate_combat_quality(self, content: Dict[str, Any]) -> float:
        """Calculate quality score for combat sports intelligence"""
        score = 0.0

        # Post count
        post_count = len(content.get('posts', []))
        score += min(0.3, post_count / 30)

        # Combat insights
        insights = content.get('combat_insights', {})
        fight_discussions = len(insights.get('fight_discussions', []))
        betting_analysis = len(insights.get('betting_analysis', []))

        score += min(0.3, fight_discussions / 10)
        score += min(0.2, betting_analysis / 5)

        # Trending topics
        trends = content.get('trending_topics', {})
        upcoming_events = len(trends.get('upcoming_events', {}))
        score += min(0.2, upcoming_events / 5)

        return score

    async def _process_ufc_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process UFC stats data"""
        return await self._process_general_combat_data(data, target)

    async def _process_sherdog_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Sherdog fighter data"""
        return await self._process_general_combat_data(data, target)

    async def _process_general_combat_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general combat sports data"""
        try:
            combat_data = data.copy() if isinstance(data, dict) else {'raw_data': data}

            quality_score = self.calculate_data_quality(combat_data)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="general_combat_data",
                content=combat_data,
                metadata={
                    'data_source': 'general_combat'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['combat_sports', 'mma', 'ufc'],
                target_agents=['combat-sports-specialist', 'betting-analyst'],
                target_advisors=['sports_betting_expert']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing general combat data: {e}")
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
        return ['title', 'fighter', 'event']

    def get_timestamp_field(self) -> Optional[str]:
        return 'created'

    def get_relevance_keywords(self) -> List[str]:
        return ['ufc', 'mma', 'boxing', 'fight', 'fighter', 'knockout', 'submission', 'betting']

    def validate_data_accuracy(self, data: Dict[str, Any]) -> bool:
        try:
            if 'score' in data and int(data['score']) < 0:
                return False
            return True
        except (ValueError, TypeError):
            return False
