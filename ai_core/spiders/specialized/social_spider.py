"""
Social Sentiment Spider - Elite Social Intelligence Gathering
===========================================================

Specialized spider for gathering social sentiment and trend data from
Reddit, Bluesky, and other social platforms. Provides real-time sentiment
analysis and social trend intelligence.
"""

import re
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import praw
from textblob import TextBlob

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class SocialSentimentSpider(BaseIntelligenceSpider):
    """Social sentiment and trend tracking spider"""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.subreddits = [
            'wallstreetbets', 'investing', 'stocks', 'SecurityAnalysis',
            'ValueInvesting', 'financialindependence', 'CryptoCurrency'
        ]

        self.sentiment_keywords = {
            'bullish': ['bullish', 'moon', 'rocket', 'diamond hands', 'hodl', 'buy the dip'],
            'bearish': ['bearish', 'crash', 'bubble', 'sell', 'dump', 'paper hands'],
            'neutral': ['sideways', 'consolidation', 'wait and see', 'cautious']
        }

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process social media data"""
        try:
            if 'reddit.com' in target.url:
                return await self._process_reddit_data(raw_data, target)
            elif 'bsky.social' in target.url or 'bluesky' in target.url.lower():
                return await self._process_bluesky_data(raw_data, target)
            else:
                return await self._process_general_social(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing social data: {e}")
            return None

    async def _process_reddit_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Reddit posts and comments"""
        try:
            posts = []
            sentiment_summary = {
                'overall_sentiment': 0.0,
                'bullish_posts': 0,
                'bearish_posts': 0,
                'neutral_posts': 0,
                'trending_tickers': {},
                'sentiment_distribution': {}
            }

            # Extract posts from HTML or API data
            if 'content' in data:
                soup = BeautifulSoup(data['content'], 'html.parser')
                posts = self._extract_reddit_posts(soup)
            elif 'posts' in data:
                posts = data['posts']

            # Analyze each post
            for post in posts:
                # Sentiment analysis
                text = f"{post.get('title', '')} {post.get('body', '')}"
                sentiment = self._analyze_sentiment(text)
                post['sentiment'] = sentiment

                # Extract mentioned tickers
                tickers = self._extract_tickers(text)
                post['mentioned_tickers'] = tickers

                # Update summary
                if sentiment > 0.1:
                    sentiment_summary['bullish_posts'] += 1
                elif sentiment < -0.1:
                    sentiment_summary['bearish_posts'] += 1
                else:
                    sentiment_summary['neutral_posts'] += 1

                # Track ticker mentions
                for ticker in tickers:
                    if ticker not in sentiment_summary['trending_tickers']:
                        sentiment_summary['trending_tickers'][ticker] = {'count': 0, 'sentiment': 0.0}
                    sentiment_summary['trending_tickers'][ticker]['count'] += 1
                    sentiment_summary['trending_tickers'][ticker]['sentiment'] += sentiment

            # Calculate overall metrics
            if posts:
                sentiment_summary['overall_sentiment'] = sum(p.get('sentiment', 0) for p in posts) / len(posts)

            # Create intelligence content
            intelligence_content = {
                'posts': posts,
                'sentiment_summary': sentiment_summary,
                'social_trends': self._identify_social_trends(posts),
                'viral_content': self._identify_viral_content(posts)
            }

            quality_score = self._calculate_social_quality(intelligence_content)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="social_sentiment",
                content=intelligence_content,
                metadata={
                    'post_count': len(posts),
                    'overall_sentiment': sentiment_summary['overall_sentiment'],
                    'trending_tickers_count': len(sentiment_summary['trending_tickers']),
                    'data_source': 'reddit'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['social', 'sentiment', 'reddit', 'trends'],
                target_agents=['sentiment_analysis_agent', 'social_trend_agent'],
                target_advisors=['warren_buffett', 'crypto_expert', 'marketing_strategist']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing Reddit data: {e}")
            return None

    def _extract_reddit_posts(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract Reddit posts from HTML"""
        posts = []
        try:
            # Look for post containers
            for post_element in soup.find_all(['div'], class_=re.compile(r'post|thing')):
                post = {
                    'title': '',
                    'body': '',
                    'author': '',
                    'score': 0,
                    'comments': 0,
                    'subreddit': '',
                    'url': '',
                    'created': datetime.now(timezone.utc).isoformat()
                }

                # Extract title
                title_elem = post_element.find(['h1', 'h2', 'h3'], class_=re.compile(r'title'))
                if title_elem:
                    post['title'] = title_elem.get_text().strip()

                # Extract body text
                body_elem = post_element.find(['div', 'p'], class_=re.compile(r'body|text'))
                if body_elem:
                    post['body'] = body_elem.get_text().strip()[:500]  # Limit length

                # Extract score
                score_elem = post_element.find(['span', 'div'], class_=re.compile(r'score|points'))
                if score_elem:
                    score_text = score_elem.get_text()
                    score_match = re.search(r'(\d+)', score_text)
                    if score_match:
                        post['score'] = int(score_match.group(1))

                if post['title']:  # Only add if we have a title
                    posts.append(post)

        except Exception as e:
            self.logger.warning(f"Error extracting Reddit posts: {e}")

        return posts

    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob and custom keywords"""
        try:
            # Basic sentiment using TextBlob
            blob = TextBlob(text.lower())
            base_sentiment = blob.sentiment.polarity

            # Enhance with domain-specific keywords
            text_lower = text.lower()
            keyword_sentiment = 0.0

            for sentiment_type, keywords in self.sentiment_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        if sentiment_type == 'bullish':
                            keyword_sentiment += 0.2
                        elif sentiment_type == 'bearish':
                            keyword_sentiment -= 0.2

            # Combine sentiments
            final_sentiment = (base_sentiment + keyword_sentiment) / 2
            return max(-1.0, min(1.0, final_sentiment))

        except Exception as e:
            self.logger.warning(f"Error analyzing sentiment: {e}")
            return 0.0

    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text"""
        tickers = []
        try:
            # Common ticker patterns
            patterns = [
                r'\$([A-Z]{1,5})',  # $AAPL format
                r'\b([A-Z]{2,5})\b',  # AAPL format (2-5 letters)
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text.upper())
                tickers.extend(matches)

            # Filter out common false positives
            false_positives = {
                'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN',
                'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM',
                'HOW', 'ITS', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY',
                'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'
            }

            filtered_tickers = [t for t in tickers if t not in false_positives and len(t) >= 2]
            return list(set(filtered_tickers))[:10]  # Limit to 10 unique tickers

        except Exception as e:
            self.logger.warning(f"Error extracting tickers: {e}")
            return []

    def _identify_social_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify trending topics and themes"""
        trends = {
            'trending_topics': {},
            'viral_threshold': 100,
            'engagement_leaders': [],
            'sentiment_leaders': []
        }

        try:
            # Count topic mentions
            all_text = ' '.join([f"{p.get('title', '')} {p.get('body', '')}" for p in posts]).lower()

            # Common investment topics
            topics = [
                'earnings', 'dividend', 'buyback', 'merger', 'acquisition',
                'ipo', 'options', 'calls', 'puts', 'squeeze', 'short',
                'crypto', 'bitcoin', 'ethereum', 'defi', 'nft'
            ]

            for topic in topics:
                count = all_text.count(topic)
                if count > 0:
                    trends['trending_topics'][topic] = count

            # Sort by popularity
            trends['trending_topics'] = dict(
                sorted(trends['trending_topics'].items(), key=lambda x: x[1], reverse=True)[:10]
            )

            # Identify high engagement posts
            high_engagement = sorted(posts, key=lambda x: x.get('score', 0), reverse=True)[:5]
            trends['engagement_leaders'] = [
                {'title': p.get('title', ''), 'score': p.get('score', 0)}
                for p in high_engagement
            ]

        except Exception as e:
            self.logger.warning(f"Error identifying social trends: {e}")

        return trends

    def _identify_viral_content(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify viral or trending content"""
        viral_content = []

        try:
            # Sort by engagement metrics
            sorted_posts = sorted(posts, key=lambda x: x.get('score', 0) + x.get('comments', 0), reverse=True)

            # Top 10% or posts with high engagement
            viral_threshold = len(posts) // 10 if len(posts) > 10 else 1

            for post in sorted_posts[:viral_threshold]:
                if post.get('score', 0) > 50:  # Minimum threshold
                    viral_content.append({
                        'title': post.get('title', ''),
                        'score': post.get('score', 0),
                        'comments': post.get('comments', 0),
                        'sentiment': post.get('sentiment', 0),
                        'mentioned_tickers': post.get('mentioned_tickers', [])
                    })

        except Exception as e:
            self.logger.warning(f"Error identifying viral content: {e}")

        return viral_content[:10]  # Limit to top 10

    def _calculate_social_quality(self, content: Dict[str, Any]) -> float:
        """Calculate quality score for social intelligence"""
        score = 0.0

        # Post count
        post_count = len(content.get('posts', []))
        score += min(0.3, post_count / 50)  # Up to 50 posts = full score

        # Sentiment analysis completeness
        posts_with_sentiment = sum(1 for p in content.get('posts', []) if 'sentiment' in p)
        if post_count > 0:
            score += (posts_with_sentiment / post_count) * 0.3

        # Trending tickers identified
        trending_count = len(content.get('sentiment_summary', {}).get('trending_tickers', {}))
        score += min(0.2, trending_count / 10)  # Up to 10 tickers = full score

        # Social trends identified
        trends_count = len(content.get('social_trends', {}).get('trending_topics', {}))
        score += min(0.2, trends_count / 5)  # Up to 5 trends = full score

        return score

    async def _process_bluesky_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Bluesky data"""
        try:
            posts = []
            sentiment_summary = {
                'overall_sentiment': 0.0,
                'bullish_posts': 0,
                'bearish_posts': 0,
                'neutral_posts': 0,
                'trending_tickers': {},
                'sentiment_distribution': {}
            }

            # Process Bluesky posts
            if 'posts' in data:
                posts = data['posts']
            elif 'feed' in data:
                posts = data['feed']

            # Analyze each post (similar to Reddit processing)
            for post in posts:
                text = post.get('text', '') or post.get('post', {}).get('record', {}).get('text', '')
                sentiment = self._analyze_sentiment(text)
                post['sentiment'] = sentiment

                tickers = self._extract_tickers(text)
                post['mentioned_tickers'] = tickers

                if sentiment > 0.1:
                    sentiment_summary['bullish_posts'] += 1
                elif sentiment < -0.1:
                    sentiment_summary['bearish_posts'] += 1
                else:
                    sentiment_summary['neutral_posts'] += 1

                for ticker in tickers:
                    if ticker not in sentiment_summary['trending_tickers']:
                        sentiment_summary['trending_tickers'][ticker] = {'count': 0, 'sentiment': 0.0}
                    sentiment_summary['trending_tickers'][ticker]['count'] += 1
                    sentiment_summary['trending_tickers'][ticker]['sentiment'] += sentiment

            if posts:
                sentiment_summary['overall_sentiment'] = sum(p.get('sentiment', 0) for p in posts) / len(posts)

            intelligence_content = {
                'posts': posts,
                'sentiment_summary': sentiment_summary,
                'social_trends': self._identify_social_trends(posts),
                'viral_content': self._identify_viral_content(posts)
            }

            quality_score = self._calculate_social_quality(intelligence_content)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="social_sentiment",
                content=intelligence_content,
                metadata={
                    'post_count': len(posts),
                    'overall_sentiment': sentiment_summary['overall_sentiment'],
                    'trending_tickers_count': len(sentiment_summary['trending_tickers']),
                    'data_source': 'bluesky'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['social', 'sentiment', 'bluesky', 'trends'],
                target_agents=['sentiment_analysis_agent', 'social_trend_agent'],
                target_advisors=['warren_buffett', 'crypto_expert', 'marketing_strategist']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing Bluesky data: {e}")
            return None

    async def _process_general_social(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general social media data"""
        try:
            social_data = data.copy() if isinstance(data, dict) else {'raw_data': data}

            # Basic sentiment analysis on any text content
            text_content = json.dumps(social_data).lower()
            sentiment = self._analyze_sentiment(text_content)

            social_data['sentiment'] = sentiment
            social_data['tickers'] = self._extract_tickers(text_content)

            quality_score = self.calculate_data_quality(social_data)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="general_social",
                content=social_data,
                metadata={
                    'sentiment': sentiment,
                    'data_source': 'general_social'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['social', 'sentiment', 'general'],
                target_agents=['sentiment_analysis_agent'],
                target_advisors=['marketing_strategist']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing general social data: {e}")
            return None

    def get_required_fields(self) -> List[str]:
        return ['title', 'sentiment']

    def get_timestamp_field(self) -> Optional[str]:
        return 'created'

    def get_relevance_keywords(self) -> List[str]:
        return ['social', 'sentiment', 'reddit', 'bluesky', 'trending', 'viral']

    def validate_data_accuracy(self, data: Dict[str, Any]) -> bool:
        try:
            # Check sentiment range
            if 'sentiment' in data:
                sentiment = float(data['sentiment'])
                if sentiment < -1 or sentiment > 1:
                    return False

            # Check score values
            if 'score' in data:
                score = int(data['score'])
                if score < 0:
                    return False

            return True
        except (ValueError, TypeError):
            return False