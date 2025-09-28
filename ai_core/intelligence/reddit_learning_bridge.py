"""
Reddit Learning Bridge - Orchestrates Reddit intelligence for AI agents and advisors
Connects 151 AI agents and 25 legendary advisors to Reddit's vast community knowledge
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import json
import re
from collections import defaultdict

# Handle imports gracefully
try:
    from ai_core.spiders.reddit_handler import RedditHandler, RedditPost, RedditComment
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Reddit handler not available, using mock classes")

    class RedditHandler:
        async def search_posts(self, *args, **kwargs): return []
        async def get_subreddit_posts(self, *args, **kwargs): return []
        async def get_post_comments(self, *args, **kwargs): return []
        async def get_trending_topics(self, *args, **kwargs): return {}

    class RedditPost:
        def __init__(self, **kwargs): pass

    class RedditComment:
        def __init__(self, **kwargs): pass

logger = logging.getLogger(__name__)


@dataclass
class RedditInsight:
    """Structured insight extracted from Reddit discussions"""
    subreddit: str
    topic: str
    sentiment: float  # -1.0 to 1.0
    consensus_level: float  # 0.0 to 1.0
    key_points: List[str]
    expert_opinions: List[str]
    contrarian_views: List[str]
    actionable_advice: List[str]
    related_resources: List[str]
    timestamp: datetime
    source_posts: List[str]  # Post IDs
    confidence: float  # 0.0 to 1.0

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class SubredditTrend:
    """Trending topic or discussion in a subreddit"""
    subreddit: str
    trend_type: str  # 'emerging', 'peak', 'declining'
    keywords: List[str]
    momentum: float  # Rate of growth/decline
    engagement_score: float
    top_posts: List[Dict]
    timeframe: str  # 'hour', 'day', 'week'
    predictions: List[str]
    timestamp: datetime

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class CommunityConsensus:
    """Aggregated community opinion on a topic"""
    topic: str
    subreddits: List[str]
    total_discussions: int
    average_sentiment: float
    key_arguments_for: List[str]
    key_arguments_against: List[str]
    expert_takes: List[str]
    resources: List[str]
    confidence: float
    timestamp: datetime

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class RedditLearningBridge:
    """
    Central orchestrator connecting Reddit community intelligence to agent learning.
    Extracts insights from specialized subreddits and feeds them to AI agents.
    """

    def __init__(self):
        """Initialize Reddit learning bridge"""
        self.reddit_handler = RedditHandler()
        self.insights_cache = {}
        self.trend_cache = {}
        self.consensus_cache = {}
        self.learning_active = False
        self.learning_tasks = []

        # Map subreddit categories to specific communities
        self.subreddit_mapping = {
            'ai_research': [
                'MachineLearning', 'artificial', 'singularity',
                'LocalLLaMA', 'OpenAI', 'deeplearning'
            ],
            'programming': [
                'programming', 'Python', 'javascript', 'golang',
                'rust', 'webdev', 'learnprogramming'
            ],
            'investing': [
                'investing', 'stocks', 'SecurityAnalysis',
                'ValueInvesting', 'wallstreetbets', 'StockMarket'
            ],
            'entrepreneurship': [
                'Entrepreneur', 'startups', 'smallbusiness',
                'SideProject', 'Startup_Ideas', 'venturecapital'
            ],
            'technology': [
                'technology', 'Futurology', 'gadgets',
                'hardware', 'tech', 'technews'
            ],
            'cryptocurrency': [
                'CryptoCurrency', 'Bitcoin', 'ethereum',
                'defi', 'CryptoMarkets', 'NFT'
            ],
            'data_science': [
                'datascience', 'datasets', 'bigdata',
                'analytics', 'BusinessIntelligence', 'dataengineering'
            ],
            'economics': [
                'Economics', 'finance', 'economy',
                'AskEconomics', 'econometrics', 'behavioral_economics'
            ],
            'productivity': [
                'productivity', 'getdisciplined', 'GetMotivated',
                'LifeProTips', 'DecidingToBeBetter', 'selfimprovement'
            ],
            'career': [
                'careerguidance', 'careeradvice', 'jobs',
                'resumes', 'interviews', 'cscareerquestions'
            ]
        }

        # Keywords for different expertise areas
        self.expertise_keywords = {
            'value_investing': [
                'fundamentals', 'P/E ratio', 'dividend', 'moat',
                'intrinsic value', 'margin of safety', 'cash flow'
            ],
            'growth_investing': [
                'growth stock', 'revenue growth', 'TAM', 'disruption',
                'market share', 'scaling', 'innovation'
            ],
            'ai_ml': [
                'neural network', 'transformer', 'LLM', 'GPT',
                'machine learning', 'deep learning', 'training'
            ],
            'blockchain': [
                'smart contract', 'DeFi', 'consensus', 'mining',
                'wallet', 'gas fees', 'layer 2'
            ],
            'startup': [
                'MVP', 'product-market fit', 'runway', 'burn rate',
                'seed funding', 'series A', 'pivot'
            ]
        }

        # Sentiment analysis patterns
        self.sentiment_patterns = {
            'positive': [
                r'\b(amazing|excellent|fantastic|great|love|wonderful|best|brilliant)\b',
                r'\b(bullish|moon|🚀|💎|gains|profit)\b',
                r'\b(solved|working|success|achieved|accomplished)\b'
            ],
            'negative': [
                r'\b(terrible|awful|hate|worst|disappointed|failed|broken)\b',
                r'\b(bearish|crash|dump|loss|scam)\b',
                r'\b(bug|issue|problem|error|failed|broken)\b'
            ],
            'neutral': [
                r'\b(maybe|perhaps|seems|appears|might|could)\b',
                r'\b(however|although|but|yet|still)\b'
            ]
        }

    async def start_continuous_learning(self):
        """Start continuous learning from Reddit communities"""
        if self.learning_active:
            logger.info("Reddit learning already active")
            return

        self.learning_active = True
        logger.info("Starting Reddit continuous learning systems...")

        # Create learning tasks
        self.learning_tasks = [
            asyncio.create_task(self._subreddit_monitor()),
            asyncio.create_task(self._trend_detector()),
            asyncio.create_task(self._consensus_builder()),
            asyncio.create_task(self._expert_discussion_extractor()),
            asyncio.create_task(self._controversy_analyzer()),
            asyncio.create_task(self._resource_aggregator())
        ]

        logger.info("Reddit learning bridge activated with 6 parallel systems")

    async def stop_learning(self):
        """Stop continuous learning"""
        self.learning_active = False

        # Cancel all learning tasks
        for task in self.learning_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.learning_tasks, return_exceptions=True)

        logger.info("Reddit learning stopped")

    async def _subreddit_monitor(self):
        """Monitor key subreddits for relevant discussions"""
        while self.learning_active:
            try:
                for category, subreddits in self.subreddit_mapping.items():
                    for subreddit in subreddits[:3]:  # Limit to top 3 per category
                        posts = await self.reddit_handler.get_subreddit_posts(
                            subreddit,
                            sort='hot',
                            limit=10
                        )

                        # Process posts for insights
                        for post in posts:
                            insight = await self._extract_post_insights(post, category)
                            if insight:
                                cache_key = f"{subreddit}_{post.id}"
                                self.insights_cache[cache_key] = insight

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Error in subreddit monitor: {e}")
                await asyncio.sleep(60)

    async def _trend_detector(self):
        """Detect emerging trends across subreddits"""
        while self.learning_active:
            try:
                trends = {}

                # Check trending topics in key subreddits
                for category, subreddits in self.subreddit_mapping.items():
                    category_trends = await self.reddit_handler.get_trending_topics(
                        subreddits[:5],
                        limit=5
                    )

                    for subreddit, topics in category_trends.items():
                        # Analyze trend momentum
                        trend = await self._analyze_trend(subreddit, topics)
                        if trend:
                            trends[subreddit] = trend

                self.trend_cache = trends
                logger.info(f"Detected {len(trends)} trending topics")

                await asyncio.sleep(600)  # Check every 10 minutes

            except Exception as e:
                logger.error(f"Error in trend detector: {e}")
                await asyncio.sleep(120)

    async def _consensus_builder(self):
        """Build consensus views from community discussions"""
        while self.learning_active:
            try:
                # Topics to analyze for consensus
                topics = [
                    'AI safety', 'market crash', 'recession',
                    'remote work', 'cryptocurrency adoption',
                    'climate tech', 'quantum computing'
                ]

                for topic in topics:
                    consensus = await self._build_consensus(topic)
                    if consensus:
                        self.consensus_cache[topic] = consensus

                await asyncio.sleep(900)  # Check every 15 minutes

            except Exception as e:
                logger.error(f"Error in consensus builder: {e}")
                await asyncio.sleep(180)

    async def _expert_discussion_extractor(self):
        """Extract insights from expert discussions and AMAs"""
        while self.learning_active:
            try:
                # Search for AMA posts and expert discussions
                expert_posts = await self.reddit_handler.search_posts(
                    'AMA expert',
                    sort='relevance',
                    time_filter='week',
                    limit=20
                )

                for post in expert_posts:
                    if post.score > 100:  # Focus on high-quality discussions
                        comments = await self.reddit_handler.get_post_comments(
                            post.id,
                            sort='best',
                            limit=50
                        )

                        insights = await self._extract_expert_insights(post, comments)
                        if insights:
                            cache_key = f"expert_{post.id}"
                            self.insights_cache[cache_key] = insights

                await asyncio.sleep(1800)  # Check every 30 minutes

            except Exception as e:
                logger.error(f"Error in expert extractor: {e}")
                await asyncio.sleep(300)

    async def _controversy_analyzer(self):
        """Analyze controversial topics for balanced perspectives"""
        while self.learning_active:
            try:
                # Search for controversial discussions
                controversial_posts = await self.reddit_handler.search_posts(
                    '',  # Will search in controversial sections
                    sort='controversial',
                    time_filter='day',
                    limit=15
                )

                for post in controversial_posts:
                    if post.num_comments > 50:  # Ensure substantial discussion
                        analysis = await self._analyze_controversy(post)
                        if analysis:
                            cache_key = f"controversy_{post.id}"
                            self.insights_cache[cache_key] = analysis

                await asyncio.sleep(1200)  # Check every 20 minutes

            except Exception as e:
                logger.error(f"Error in controversy analyzer: {e}")
                await asyncio.sleep(240)

    async def _resource_aggregator(self):
        """Aggregate educational resources and tutorials"""
        while self.learning_active:
            try:
                resource_queries = [
                    'tutorial', 'guide', 'how to', 'resources',
                    'learning path', 'roadmap', 'best practices'
                ]

                resources = {}
                for query in resource_queries:
                    posts = await self.reddit_handler.search_posts(
                        query,
                        sort='top',
                        time_filter='month',
                        limit=10
                    )

                    for post in posts:
                        if post.score > 100:
                            resource = await self._extract_resources(post)
                            if resource:
                                resources[post.id] = resource

                # Store aggregated resources
                if resources:
                    self.insights_cache['resources'] = resources

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                logger.error(f"Error in resource aggregator: {e}")
                await asyncio.sleep(600)

    async def _extract_post_insights(self, post: RedditPost, category: str) -> Optional[RedditInsight]:
        """Extract structured insights from a Reddit post"""
        try:
            # Get post comments for deeper analysis
            comments = await self.reddit_handler.get_post_comments(
                post.id,
                sort='best',
                limit=30
            )

            # Analyze sentiment
            sentiment = self._analyze_sentiment(post.content + ' '.join([c.body for c in comments]))

            # Extract key points
            key_points = self._extract_key_points(post, comments)

            # Find expert opinions
            expert_opinions = self._find_expert_opinions(comments)

            # Find contrarian views
            contrarian_views = self._find_contrarian_views(comments)

            # Extract actionable advice
            actionable_advice = self._extract_actionable_advice(post, comments)

            # Find related resources
            resources = self._extract_resource_links(post.content + ' '.join([c.body for c in comments]))

            # Calculate consensus level
            consensus_level = self._calculate_consensus(comments)

            # Create insight
            insight = RedditInsight(
                subreddit=post.subreddit,
                topic=post.title,
                sentiment=sentiment,
                consensus_level=consensus_level,
                key_points=key_points,
                expert_opinions=expert_opinions,
                contrarian_views=contrarian_views,
                actionable_advice=actionable_advice,
                related_resources=resources,
                timestamp=datetime.now(timezone.utc),
                source_posts=[post.id],
                confidence=min(post.score / 1000, 1.0)  # Score-based confidence
            )

            return insight

        except Exception as e:
            logger.error(f"Error extracting post insights: {e}")
            return None

    async def _analyze_trend(self, subreddit: str, topics: List[Dict]) -> Optional[SubredditTrend]:
        """Analyze trending topics in a subreddit"""
        try:
            if not topics:
                return None

            # Extract keywords from trending titles
            keywords = []
            for topic in topics:
                words = re.findall(r'\b[A-Z][a-z]+\b|\b[A-Z]+\b', topic['title'])
                keywords.extend(words)

            # Calculate momentum (based on score/comment ratio)
            total_score = sum(t['score'] for t in topics)
            total_comments = sum(t['comments'] for t in topics)
            momentum = (total_score / max(total_comments, 1)) / 100

            # Determine trend type
            if momentum > 1.0:
                trend_type = 'emerging'
            elif momentum > 0.5:
                trend_type = 'peak'
            else:
                trend_type = 'declining'

            # Generate predictions
            predictions = self._generate_trend_predictions(keywords, trend_type)

            trend = SubredditTrend(
                subreddit=subreddit,
                trend_type=trend_type,
                keywords=list(set(keywords))[:10],
                momentum=momentum,
                engagement_score=total_score / len(topics),
                top_posts=topics[:3],
                timeframe='day',
                predictions=predictions,
                timestamp=datetime.now(timezone.utc)
            )

            return trend

        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return None

    async def _build_consensus(self, topic: str) -> Optional[CommunityConsensus]:
        """Build consensus view on a topic across subreddits"""
        try:
            # Search for topic across multiple subreddits
            posts = await self.reddit_handler.search_posts(
                topic,
                sort='relevance',
                time_filter='month',
                limit=30
            )

            if len(posts) < 5:
                return None

            # Collect subreddits discussing the topic
            subreddits = list(set([p.subreddit for p in posts]))

            # Analyze sentiment across posts
            sentiments = []
            arguments_for = []
            arguments_against = []
            expert_takes = []
            resources = []

            for post in posts:
                # Get comments for deeper analysis
                comments = await self.reddit_handler.get_post_comments(
                    post.id,
                    limit=20
                )

                # Analyze sentiment
                sentiment = self._analyze_sentiment(
                    post.content + ' '.join([c.body for c in comments])
                )
                sentiments.append(sentiment)

                # Extract arguments
                for comment in comments:
                    if comment.score > 10:
                        if sentiment > 0.3:
                            arguments_for.append(comment.body[:200])
                        elif sentiment < -0.3:
                            arguments_against.append(comment.body[:200])

                        # Check for expert takes
                        if comment.awards or comment.score > 100:
                            expert_takes.append(comment.body[:300])

                # Extract resources
                post_resources = self._extract_resource_links(
                    post.content + ' '.join([c.body for c in comments])
                )
                resources.extend(post_resources)

            consensus = CommunityConsensus(
                topic=topic,
                subreddits=subreddits[:10],
                total_discussions=len(posts),
                average_sentiment=sum(sentiments) / len(sentiments),
                key_arguments_for=list(set(arguments_for))[:5],
                key_arguments_against=list(set(arguments_against))[:5],
                expert_takes=list(set(expert_takes))[:5],
                resources=list(set(resources))[:10],
                confidence=min(len(posts) / 30, 1.0),
                timestamp=datetime.now(timezone.utc)
            )

            return consensus

        except Exception as e:
            logger.error(f"Error building consensus: {e}")
            return None

    async def _extract_expert_insights(self, post: RedditPost,
                                     comments: List[RedditComment]) -> Optional[RedditInsight]:
        """Extract insights from expert discussions"""
        try:
            # Identify high-value comments
            expert_comments = [
                c for c in comments
                if c.score > 50 or c.awards or c.depth == 1
            ]

            if not expert_comments:
                return None

            # Extract expert opinions
            expert_opinions = [
                c.body[:500] for c in expert_comments[:5]
            ]

            # Extract Q&A pairs
            qa_pairs = []
            for comment in expert_comments:
                if comment.depth == 1:  # Direct replies to post
                    qa_pairs.append({
                        'question': comment.body[:200],
                        'score': comment.score
                    })

            # Create insight
            insight = RedditInsight(
                subreddit=post.subreddit,
                topic=f"Expert Discussion: {post.title}",
                sentiment=0.7,  # Generally positive for expert content
                consensus_level=0.8,
                key_points=[c.body[:200] for c in expert_comments[:3]],
                expert_opinions=expert_opinions,
                contrarian_views=[],
                actionable_advice=self._extract_actionable_advice(post, expert_comments),
                related_resources=self._extract_resource_links(
                    ' '.join([c.body for c in expert_comments])
                ),
                timestamp=datetime.now(timezone.utc),
                source_posts=[post.id],
                confidence=0.9  # High confidence for expert content
            )

            return insight

        except Exception as e:
            logger.error(f"Error extracting expert insights: {e}")
            return None

    async def _analyze_controversy(self, post: RedditPost) -> Optional[RedditInsight]:
        """Analyze controversial topics for balanced perspectives"""
        try:
            comments = await self.reddit_handler.get_post_comments(
                post.id,
                sort='controversial',
                limit=50
            )

            if not comments:
                return None

            # Separate supporting and opposing views
            supporting = []
            opposing = []

            for comment in comments:
                sentiment = self._analyze_sentiment(comment.body)
                if sentiment > 0.2:
                    supporting.append(comment.body[:300])
                elif sentiment < -0.2:
                    opposing.append(comment.body[:300])

            # Create balanced insight
            insight = RedditInsight(
                subreddit=post.subreddit,
                topic=f"Controversy: {post.title}",
                sentiment=0.0,  # Neutral for controversial topics
                consensus_level=0.3,  # Low consensus
                key_points=supporting[:3] + opposing[:3],
                expert_opinions=[],
                contrarian_views=opposing[:5],
                actionable_advice=[
                    "Consider multiple perspectives",
                    "Research primary sources",
                    "Avoid confirmation bias"
                ],
                related_resources=self._extract_resource_links(
                    post.content + ' '.join([c.body for c in comments[:20]])
                ),
                timestamp=datetime.now(timezone.utc),
                source_posts=[post.id],
                confidence=0.6
            )

            return insight

        except Exception as e:
            logger.error(f"Error analyzing controversy: {e}")
            return None

    async def _extract_resources(self, post: RedditPost) -> Optional[Dict]:
        """Extract educational resources from a post"""
        try:
            # Get post content and comments
            comments = await self.reddit_handler.get_post_comments(
                post.id,
                sort='best',
                limit=30
            )

            # Extract all links
            content = post.content + ' '.join([c.body for c in comments])
            resources = self._extract_resource_links(content)

            if not resources:
                return None

            return {
                'title': post.title,
                'subreddit': post.subreddit,
                'resources': resources,
                'score': post.score,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(f"Error extracting resources: {e}")
            return None

    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text (-1.0 to 1.0)"""
        if not text:
            return 0.0

        text_lower = text.lower()

        positive_count = sum(
            len(re.findall(pattern, text_lower))
            for pattern in self.sentiment_patterns['positive']
        )

        negative_count = sum(
            len(re.findall(pattern, text_lower))
            for pattern in self.sentiment_patterns['negative']
        )

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        # Calculate sentiment score
        sentiment = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, sentiment))

    def _extract_key_points(self, post: RedditPost,
                           comments: List[RedditComment]) -> List[str]:
        """Extract key discussion points"""
        points = []

        # Add post title as first point
        points.append(post.title)

        # Add high-scoring comments as points
        top_comments = sorted(comments, key=lambda c: c.score, reverse=True)[:5]
        for comment in top_comments:
            if len(comment.body) > 50:
                # Extract first sentence or 100 chars
                point = comment.body.split('.')[0][:100]
                points.append(point)

        return points[:5]

    def _find_expert_opinions(self, comments: List[RedditComment]) -> List[str]:
        """Find comments that appear to be from experts"""
        expert_opinions = []

        expert_indicators = [
            r'\b(I work in|I\'m a|As a|My experience|professionally)\b',
            r'\b(PhD|researcher|engineer|developer|analyst)\b',
            r'\b(years of experience|worked with|built|developed)\b'
        ]

        for comment in comments:
            if comment.score > 20:
                for pattern in expert_indicators:
                    if re.search(pattern, comment.body, re.I):
                        expert_opinions.append(comment.body[:300])
                        break

        return expert_opinions[:5]

    def _find_contrarian_views(self, comments: List[RedditComment]) -> List[str]:
        """Find contrarian or opposing viewpoints"""
        contrarian = []

        contrarian_indicators = [
            r'\b(actually|however|but|disagree|wrong|misconception)\b',
            r'\b(unpopular opinion|hot take|controversial)\b',
            r'\b(on the other hand|alternatively|counter)\b'
        ]

        for comment in comments:
            for pattern in contrarian_indicators:
                if re.search(pattern, comment.body, re.I):
                    contrarian.append(comment.body[:300])
                    break

        return contrarian[:5]

    def _extract_actionable_advice(self, post: RedditPost,
                                  comments: List[RedditComment]) -> List[str]:
        """Extract actionable advice from discussions"""
        advice = []

        action_patterns = [
            r'\b(you should|try|consider|recommend|suggest)\b',
            r'\b(step \d|first|then|finally|make sure)\b',
            r'\b(pro tip|advice|tip:|LPT:)\b'
        ]

        content = post.content + ' '.join([c.body for c in comments])
        sentences = content.split('.')

        for sentence in sentences:
            for pattern in action_patterns:
                if re.search(pattern, sentence, re.I):
                    advice.append(sentence.strip()[:200])
                    break

        return list(set(advice))[:10]

    def _extract_resource_links(self, text: str) -> List[str]:
        """Extract resource URLs from text"""
        # URL pattern
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+(?:\.[^\s<>"{}|\\^`\[\]]+)+'

        urls = re.findall(url_pattern, text)

        # Filter for quality resources
        quality_domains = [
            'github.com', 'arxiv.org', 'medium.com',
            'towardsdatascience.com', 'stackoverflow.com',
            'youtube.com', 'coursera.org', 'udemy.com',
            'wikipedia.org', 'investopedia.com'
        ]

        quality_urls = []
        for url in urls:
            for domain in quality_domains:
                if domain in url:
                    quality_urls.append(url)
                    break

        return list(set(quality_urls))[:10]

    def _calculate_consensus(self, comments: List[RedditComment]) -> float:
        """Calculate consensus level from comments"""
        if not comments:
            return 0.5

        # Calculate variance in sentiment
        sentiments = [self._analyze_sentiment(c.body) for c in comments[:20]]

        if not sentiments:
            return 0.5

        # Low variance = high consensus
        avg_sentiment = sum(sentiments) / len(sentiments)
        variance = sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)

        # Convert variance to consensus (0-1 scale)
        consensus = max(0.0, 1.0 - (variance * 2))

        return consensus

    def _generate_trend_predictions(self, keywords: List[str],
                                   trend_type: str) -> List[str]:
        """Generate predictions based on trending keywords"""
        predictions = []

        keyword_str = ' '.join(keywords).lower()

        # AI/Tech predictions
        if any(word in keyword_str for word in ['ai', 'gpt', 'llm', 'neural']):
            if trend_type == 'emerging':
                predictions.append("AI adoption will accelerate in this domain")
                predictions.append("Expect new AI-powered tools and services")
            elif trend_type == 'peak':
                predictions.append("AI market consolidation likely")
                predictions.append("Focus shifting from hype to practical applications")

        # Investment predictions
        if any(word in keyword_str for word in ['stock', 'invest', 'market', 'trading']):
            if trend_type == 'emerging':
                predictions.append("Increased retail investor interest expected")
                predictions.append("New investment opportunities emerging")
            elif trend_type == 'declining':
                predictions.append("Market correction or rotation possible")
                predictions.append("Risk-off sentiment developing")

        # Crypto predictions
        if any(word in keyword_str for word in ['crypto', 'bitcoin', 'ethereum', 'defi']):
            if trend_type == 'emerging':
                predictions.append("Potential price momentum building")
                predictions.append("New protocols and platforms launching")
            elif trend_type == 'peak':
                predictions.append("Volatility likely to increase")
                predictions.append("Regulatory attention possible")

        # Default predictions
        if not predictions:
            if trend_type == 'emerging':
                predictions.append("This trend is gaining momentum")
                predictions.append("Early adoption phase - opportunities exist")
            elif trend_type == 'peak':
                predictions.append("Trend at maximum visibility")
                predictions.append("Competition and saturation increasing")
            else:
                predictions.append("Trend losing momentum")
                predictions.append("Focus shifting to next innovation")

        return predictions[:3]

    async def get_insights_for_agent(self, agent_name: str,
                                    specialization: str) -> List[RedditInsight]:
        """Get Reddit insights relevant to a specific agent"""
        relevant_insights = []

        # Find relevant subreddits for this specialization
        relevant_subreddits = []
        for category, subreddits in self.subreddit_mapping.items():
            if any(keyword in specialization.lower() for keyword in category.split('_')):
                relevant_subreddits.extend(subreddits)

        # Get insights from cache
        for key, insight in self.insights_cache.items():
            if isinstance(insight, RedditInsight):
                if insight.subreddit in relevant_subreddits:
                    relevant_insights.append(insight)

        # If not enough cached insights, fetch new ones
        if len(relevant_insights) < 5:
            for subreddit in relevant_subreddits[:3]:
                posts = await self.reddit_handler.get_subreddit_posts(
                    subreddit,
                    sort='hot',
                    limit=5
                )

                for post in posts:
                    insight = await self._extract_post_insights(post, specialization)
                    if insight:
                        relevant_insights.append(insight)

        return relevant_insights[:10]

    async def get_insights_for_advisor(self, advisor_name: str,
                                      keywords: List[str]) -> List[RedditInsight]:
        """Get Reddit insights relevant to a specific advisor"""
        relevant_insights = []

        # Search for advisor-specific content
        for keyword in keywords[:3]:
            posts = await self.reddit_handler.search_posts(
                keyword,
                sort='relevance',
                time_filter='month',
                limit=10
            )

            for post in posts:
                if post.score > 50:  # Quality filter
                    insight = await self._extract_post_insights(post, advisor_name)
                    if insight:
                        relevant_insights.append(insight)

        return relevant_insights[:15]

    async def get_trending_topics(self) -> List[SubredditTrend]:
        """Get current trending topics across Reddit"""
        trends = []

        for trend in self.trend_cache.values():
            if isinstance(trend, SubredditTrend):
                trends.append(trend)

        # Sort by momentum
        trends.sort(key=lambda t: t.momentum, reverse=True)

        return trends[:20]

    async def get_community_consensus(self, topic: str) -> Optional[CommunityConsensus]:
        """Get community consensus on a specific topic"""
        # Check cache first
        if topic in self.consensus_cache:
            return self.consensus_cache[topic]

        # Build new consensus
        consensus = await self._build_consensus(topic)

        if consensus:
            self.consensus_cache[topic] = consensus

        return consensus

    async def cleanup(self):
        """Clean up resources"""
        await self.stop_learning()
        await self.reddit_handler.cleanup()

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_continuous_learning()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()


# Singleton instance getter
_reddit_bridge = None

def get_reddit_learning_bridge() -> RedditLearningBridge:
    """Get or create singleton Reddit learning bridge instance"""
    global _reddit_bridge
    if _reddit_bridge is None:
        _reddit_bridge = RedditLearningBridge()
    return _reddit_bridge