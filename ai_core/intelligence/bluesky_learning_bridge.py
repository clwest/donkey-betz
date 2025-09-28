"""
Bluesky Learning Bridge - AI Agent Learning Enhancement System
==============================================================

Transforms agents from static knowledge systems into dynamic,
community-connected intelligences that learn from real-time social data.

This module bridges Bluesky intelligence with the agent learning pipeline,
providing continuous updates from expert discussions, market trends, and
community insights.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re
import numpy as np
from textblob import TextBlob

# Import existing systems
from ..spiders.bluesky_handler import bluesky_handler, bluesky_collector
try:
    from .learning_loop import LearningLoop, FeedbackItem, LearningInsight, OptimizationAction
except ImportError:
    # Create mock classes if not available
    class LearningLoop:
        def __init__(self):
            pass

    class FeedbackItem:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class LearningInsight:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class OptimizationAction:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# Lazy import to avoid circular dependency
def get_all_agent_classes():
    """Lazy import to avoid circular dependency"""
    try:
        from ..agents.universal_agent_loader import get_all_agent_classes as _get_all_agent_classes
        return _get_all_agent_classes()
    except (ImportError, Exception):
        # Catch both ImportError and Django-related exceptions
        return {}

try:
    from ..spiders.advisor_feed import AdvisorFeed
except (ImportError, Exception):
    # Catch both ImportError and Django-related exceptions
    class AdvisorFeed:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)


@dataclass
class ExpertInsight:
    """Represents an insight extracted from expert discussions"""
    expert_handle: str
    content: str
    topic: str
    confidence: float
    engagement_score: int
    timestamp: datetime
    actionable_advice: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class MarketSignal:
    """Represents a market signal detected from Bluesky"""
    signal_type: str  # hiring, layoffs, skill_demand, opportunity
    content: str
    strength: float  # 0-1 based on engagement and relevance
    urgency: float   # 0-1 based on timing and community response
    affected_sectors: List[str]
    timestamp: datetime
    source_posts: List[Dict] = field(default_factory=list)


@dataclass
class TrendAnalysis:
    """Represents an emerging trend analysis"""
    trend_name: str
    trend_type: str  # technology, market, social, economic
    growth_rate: float
    adoption_signals: List[str]
    opportunity_score: float
    risk_factors: List[str]
    related_keywords: List[str]
    expert_mentions: int
    community_sentiment: float


class BlueskyLearningBridge:
    """
    Main bridge between Bluesky intelligence and agent learning systems.
    Orchestrates continuous learning from social intelligence.
    """

    def __init__(self):
        self.bluesky_handler = bluesky_handler
        self.bluesky_collector = bluesky_collector
        self.learning_loop = LearningLoop()
        self.advisor_feed = AdvisorFeed()

        # Learning state
        self.is_learning_active = False
        self.last_update_time = None

        # Expert tracking
        self.expert_handles = {
            'ai_researchers': ['karpathy.ai', 'ylecun.bsky.social', 'AndrewYNg.bsky.social'],
            'investors': ['pmarca.bsky.social', 'paulg.bsky.social', 'naval.bsky.social'],
            'entrepreneurs': ['sama.bsky.social', 'dhh.bsky.social'],
            'developers': ['gvanrossum.bsky.social', 'torvalds.bsky.social'],
            'economists': ['nouriel.bsky.social', 'stiglitzje.bsky.social']
        }

        # Market intelligence keywords
        self.market_keywords = {
            'hiring': ['hiring', 'looking for', 'job opening', 'we are hiring', 'join our team'],
            'layoffs': ['layoffs', 'downsizing', 'restructuring', 'job cuts'],
            'skills': ['in demand skills', 'looking for developers', 'need expertise in'],
            'opportunities': ['startup idea', 'market gap', 'business opportunity'],
            'risks': ['market crash', 'recession', 'bubble', 'overvalued']
        }

        # Learning metrics
        self.learning_stats = {
            'insights_extracted': 0,
            'trends_detected': 0,
            'market_signals_processed': 0,
            'agent_updates_made': 0,
            'accuracy_improvements': 0
        }

    async def start_continuous_learning(self):
        """Start the continuous learning system"""
        self.is_learning_active = True
        logger.info("🚀 Starting Bluesky continuous learning system")

        # Initialize baseline metrics
        await self._establish_learning_baselines()

        # Start parallel learning tasks
        await asyncio.gather(
            self._expert_knowledge_extractor(),
            self._trend_detection_monitor(),
            self._market_intelligence_collector(),
            self._community_insights_analyzer(),
            self._sentiment_learning_adjuster(),
            self._feedback_enhancement_loop()
        )

    async def stop_continuous_learning(self):
        """Stop the continuous learning system"""
        self.is_learning_active = False
        logger.info("⏹️ Stopping Bluesky continuous learning system")

    # ================================================================
    # EXPERT KNOWLEDGE EXTRACTION SYSTEM
    # ================================================================

    async def _expert_knowledge_extractor(self):
        """Continuously extract knowledge from expert discussions"""
        logger.info("🧠 Starting expert knowledge extraction")

        while self.is_learning_active:
            try:
                expert_insights = []

                for field, experts in self.expert_handles.items():
                    field_insights = await self._extract_field_expert_knowledge(field, experts)
                    expert_insights.extend(field_insights)

                # Process and apply insights
                if expert_insights:
                    await self._apply_expert_insights_to_agents(expert_insights)
                    self.learning_stats['insights_extracted'] += len(expert_insights)
                    logger.info(f"✅ Extracted {len(expert_insights)} expert insights")

                # Update every 30 minutes
                await asyncio.sleep(1800)

            except Exception as e:
                logger.error(f"Error in expert knowledge extraction: {e}")
                await asyncio.sleep(300)

    async def _extract_field_expert_knowledge(self, field: str, experts: List[str]) -> List[ExpertInsight]:
        """Extract knowledge from experts in a specific field"""
        insights = []

        for expert in experts:
            try:
                # Get recent posts from expert
                posts = await self.bluesky_handler.get_author_feed(expert, limit=10)

                if not posts:
                    continue

                for post in posts:
                    # Skip low-engagement posts
                    if post['metrics']['engagement'] < 5:
                        continue

                    # Extract insights from high-engagement posts
                    if post['metrics']['engagement'] > 20:
                        insight = await self._analyze_expert_post(expert, post, field)
                        if insight:
                            insights.append(insight)

                    # Analyze conversation threads for deeper insights
                    if post['metrics']['replies'] > 5:
                        thread_insights = await self._analyze_expert_thread(expert, post, field)
                        insights.extend(thread_insights)

            except Exception as e:
                logger.warning(f"Error extracting from {expert}: {e}")
                continue

        return insights

    async def _analyze_expert_post(self, expert: str, post: Dict, field: str) -> Optional[ExpertInsight]:
        """Analyze a single expert post for insights"""
        content = post['text']

        # Extract actionable advice
        actionable_advice = self._extract_actionable_advice(content)

        # Extract predictions
        predictions = self._extract_predictions(content)

        # Extract warnings
        warnings = self._extract_warnings(content)

        # Skip if no valuable insights found
        if not (actionable_advice or predictions or warnings):
            return None

        # Calculate confidence based on engagement and expert credibility
        confidence = min(1.0, (post['metrics']['engagement'] / 100) + 0.3)

        return ExpertInsight(
            expert_handle=expert,
            content=content,
            topic=self._classify_topic(content, field),
            confidence=confidence,
            engagement_score=post['metrics']['engagement'],
            timestamp=datetime.fromisoformat(post['created_at'].replace('Z', '+00:00')),
            actionable_advice=actionable_advice,
            predictions=predictions,
            warnings=warnings
        )

    def _extract_actionable_advice(self, content: str) -> List[str]:
        """Extract actionable advice from expert content"""
        advice_patterns = [
            r'(?:should|must|need to|have to|recommend)\s+(.+?)(?:\.|!|$)',
            r'(?:advice|tip|suggestion):\s*(.+?)(?:\.|!|$)',
            r'(?:key is|secret is|important to)\s+(.+?)(?:\.|!|$)'
        ]

        advice = []
        for pattern in advice_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            advice.extend([match.strip() for match in matches if len(match.strip()) > 10])

        return advice[:3]  # Limit to top 3 pieces of advice

    def _extract_predictions(self, content: str) -> List[str]:
        """Extract predictions from expert content"""
        prediction_patterns = [
            r'(?:predict|expect|forecast|will see|will be)\s+(.+?)(?:\.|!|$)',
            r'(?:in \d+ years?|by \d{4}|next year)\s+(.+?)(?:\.|!|$)',
            r'(?:trend|future|coming)\s+(.+?)(?:\.|!|$)'
        ]

        predictions = []
        for pattern in prediction_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            predictions.extend([match.strip() for match in matches if len(match.strip()) > 10])

        return predictions[:2]  # Limit to top 2 predictions

    def _extract_warnings(self, content: str) -> List[str]:
        """Extract warnings from expert content"""
        warning_patterns = [
            r'(?:warning|caution|careful|watch out|avoid)\s+(.+?)(?:\.|!|$)',
            r'(?:risk|danger|problem|issue)\s+(?:is|with)\s+(.+?)(?:\.|!|$)',
            r'(?:don\'t|avoid|never)\s+(.+?)(?:\.|!|$)'
        ]

        warnings = []
        for pattern in warning_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            warnings.extend([match.strip() for match in matches if len(match.strip()) > 10])

        return warnings[:2]  # Limit to top 2 warnings

    async def _analyze_expert_thread(self, expert: str, post: Dict, field: str) -> List[ExpertInsight]:
        """Analyze an expert's conversation thread for deeper insights"""
        try:
            thread = await self.bluesky_handler.get_post_thread(post['uri'])
            if not thread:
                return []

            # Extract insights from thread replies and discussions
            thread_insights = []
            # TODO: Implement thread analysis logic

            return thread_insights

        except Exception as e:
            logger.warning(f"Error analyzing thread for {expert}: {e}")
            return []

    # ================================================================
    # TREND DETECTION AND LEARNING SYSTEM
    # ================================================================

    async def _trend_detection_monitor(self):
        """Monitor and learn from emerging trends"""
        logger.info("📈 Starting trend detection monitor")

        while self.is_learning_active:
            try:
                # Get trending content
                trending_posts = await self.bluesky_handler.get_trending()

                if trending_posts:
                    trend_analyses = await self._analyze_trending_content(trending_posts)

                    if trend_analyses:
                        await self._apply_trend_learnings(trend_analyses)
                        self.learning_stats['trends_detected'] += len(trend_analyses)
                        logger.info(f"📊 Detected {len(trend_analyses)} emerging trends")

                # Check every 15 minutes for trending content
                await asyncio.sleep(900)

            except Exception as e:
                logger.error(f"Error in trend detection: {e}")
                await asyncio.sleep(300)

    async def _analyze_trending_content(self, trending_posts: List[Dict]) -> List[TrendAnalysis]:
        """Analyze trending posts to identify emerging trends"""
        trend_analyses = []

        # Group posts by similar topics
        topic_clusters = self._cluster_posts_by_topic(trending_posts)

        for topic, posts in topic_clusters.items():
            if len(posts) < 3:  # Need at least 3 posts to constitute a trend
                continue

            trend_analysis = await self._create_trend_analysis(topic, posts)
            if trend_analysis:
                trend_analyses.append(trend_analysis)

        return trend_analyses

    def _cluster_posts_by_topic(self, posts: List[Dict]) -> Dict[str, List[Dict]]:
        """Cluster posts by similar topics using keyword analysis"""
        topic_clusters = defaultdict(list)

        for post in posts:
            # Extract key topics from post content
            topics = self._extract_post_topics(post['text'])

            # Assign to primary topic cluster
            if topics:
                primary_topic = topics[0]
                topic_clusters[primary_topic].append(post)

        return dict(topic_clusters)

    def _extract_post_topics(self, text: str) -> List[str]:
        """Extract main topics from post text"""
        # Simplified topic extraction - in production, use more sophisticated NLP
        topic_keywords = {
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'llm'],
            'crypto': ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'defi'],
            'startup': ['startup', 'entrepreneur', 'funding', 'venture', 'vc'],
            'tech': ['technology', 'software', 'programming', 'developer', 'coding'],
            'jobs': ['jobs', 'hiring', 'career', 'employment', 'remote work'],
            'economy': ['economy', 'inflation', 'recession', 'market', 'finance']
        }

        text_lower = text.lower()
        detected_topics = []

        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_topics.append(topic)

        return detected_topics

    async def _create_trend_analysis(self, topic: str, posts: List[Dict]) -> Optional[TrendAnalysis]:
        """Create a comprehensive trend analysis"""
        if not posts:
            return None

        # Calculate trend metrics
        total_engagement = sum(post['metrics']['engagement'] for post in posts)
        avg_engagement = total_engagement / len(posts)

        # Extract related keywords
        all_text = ' '.join(post['text'] for post in posts)
        related_keywords = self._extract_keywords(all_text)

        # Analyze sentiment
        sentiment = self._analyze_collective_sentiment(posts)

        # Count expert mentions
        expert_mentions = self._count_expert_mentions(posts)

        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(posts, sentiment, expert_mentions)

        return TrendAnalysis(
            trend_name=topic,
            trend_type=self._classify_trend_type(topic),
            growth_rate=min(2.0, avg_engagement / 50),  # Normalized growth rate
            adoption_signals=self._extract_adoption_signals(posts),
            opportunity_score=opportunity_score,
            risk_factors=self._extract_risk_factors(posts),
            related_keywords=related_keywords,
            expert_mentions=expert_mentions,
            community_sentiment=sentiment
        )

    # ================================================================
    # MARKET INTELLIGENCE COLLECTOR
    # ================================================================

    async def _market_intelligence_collector(self):
        """Collect real-time market intelligence"""
        logger.info("💼 Starting market intelligence collector")

        while self.is_learning_active:
            try:
                market_signals = []

                # Monitor different market signal types
                for signal_type, keywords in self.market_keywords.items():
                    signals = await self._collect_market_signals(signal_type, keywords)
                    market_signals.extend(signals)

                if market_signals:
                    await self._process_market_signals(market_signals)
                    self.learning_stats['market_signals_processed'] += len(market_signals)
                    logger.info(f"💡 Processed {len(market_signals)} market signals")

                # Update every 20 minutes
                await asyncio.sleep(1200)

            except Exception as e:
                logger.error(f"Error in market intelligence collection: {e}")
                await asyncio.sleep(300)

    async def _collect_market_signals(self, signal_type: str, keywords: List[str]) -> List[MarketSignal]:
        """Collect market signals for a specific type"""
        signals = []

        # Search for posts containing market keywords
        for keyword in keywords[:3]:  # Limit to prevent rate limiting
            try:
                posts = await self.bluesky_handler.search_posts(keyword, limit=10, sort="latest")

                for post in posts:
                    if post['metrics']['engagement'] > 5:  # Filter for relevant posts
                        signal = self._create_market_signal(signal_type, post)
                        if signal:
                            signals.append(signal)

            except Exception as e:
                logger.warning(f"Error searching for {keyword}: {e}")
                continue

        return signals

    def _create_market_signal(self, signal_type: str, post: Dict) -> Optional[MarketSignal]:
        """Create a market signal from a post"""
        content = post['text']

        # Calculate signal strength based on engagement and content relevance
        engagement_score = post['metrics']['engagement']
        content_relevance = self._calculate_content_relevance(content, signal_type)
        strength = min(1.0, (engagement_score / 50 + content_relevance) / 2)

        # Calculate urgency based on timing and community response
        urgency = min(1.0, post['metrics']['replies'] / 20 + 0.3)

        # Extract affected sectors
        affected_sectors = self._extract_affected_sectors(content)

        return MarketSignal(
            signal_type=signal_type,
            content=content,
            strength=strength,
            urgency=urgency,
            affected_sectors=affected_sectors,
            timestamp=datetime.fromisoformat(post['created_at'].replace('Z', '+00:00')),
            source_posts=[post]
        )

    # ================================================================
    # SENTIMENT-BASED LEARNING ADJUSTMENTS
    # ================================================================

    async def _sentiment_learning_adjuster(self):
        """Adjust learning based on market sentiment"""
        logger.info("😊 Starting sentiment-based learning adjuster")

        while self.is_learning_active:
            try:
                # Analyze sentiment for key topics
                sentiment_analyses = await self._analyze_market_sentiments()

                if sentiment_analyses:
                    await self._apply_sentiment_adjustments(sentiment_analyses)
                    logger.info(f"🎯 Applied sentiment adjustments for {len(sentiment_analyses)} topics")

                # Update every 25 minutes
                await asyncio.sleep(1500)

            except Exception as e:
                logger.error(f"Error in sentiment learning adjustment: {e}")
                await asyncio.sleep(300)

    async def _analyze_market_sentiments(self) -> Dict[str, Dict]:
        """Analyze sentiment for key market topics"""
        key_topics = ['ai jobs', 'remote work', 'tech layoffs', 'startup funding', 'crypto market']
        sentiment_analyses = {}

        for topic in key_topics:
            try:
                posts = await self.bluesky_handler.search_posts(topic, limit=20)
                if posts:
                    sentiment_data = await self._analyze_topic_sentiment(topic, posts)
                    sentiment_analyses[topic] = sentiment_data
            except Exception as e:
                logger.warning(f"Error analyzing sentiment for {topic}: {e}")
                continue

        return sentiment_analyses

    async def _analyze_topic_sentiment(self, topic: str, posts: List[Dict]) -> Dict:
        """Analyze sentiment for a specific topic"""
        sentiment_data = {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'total_engagement': 0,
            'key_concerns': [],
            'opportunities': [],
            'overall_sentiment': 0
        }

        for post in posts:
            # Analyze sentiment using TextBlob
            blob = TextBlob(post['text'])
            sentiment_score = blob.sentiment.polarity
            engagement = post['metrics']['engagement']

            # Weight sentiment by engagement
            weighted_sentiment = sentiment_score * (1 + engagement / 100)

            if sentiment_score > 0.1:
                sentiment_data['positive'] += weighted_sentiment
                if engagement > 10:
                    sentiment_data['opportunities'].append(post['text'][:100])
            elif sentiment_score < -0.1:
                sentiment_data['negative'] += abs(weighted_sentiment)
                if engagement > 10:
                    sentiment_data['key_concerns'].append(post['text'][:100])
            else:
                sentiment_data['neutral'] += 1

            sentiment_data['total_engagement'] += engagement
            sentiment_data['overall_sentiment'] += weighted_sentiment

        # Calculate overall sentiment
        if posts:
            sentiment_data['overall_sentiment'] = sentiment_data['overall_sentiment'] / len(posts)

        return sentiment_data

    # ================================================================
    # COMMUNITY INSIGHTS ANALYZER
    # ================================================================

    async def _community_insights_analyzer(self):
        """Analyze community discussions for insights"""
        logger.info("👥 Starting community insights analyzer")

        while self.is_learning_active:
            try:
                community_insights = await self._extract_community_insights()

                if community_insights:
                    await self._apply_community_insights(community_insights)
                    logger.info(f"🔍 Analyzed {len(community_insights)} community insights")

                # Update every 35 minutes
                await asyncio.sleep(2100)

            except Exception as e:
                logger.error(f"Error in community insights analysis: {e}")
                await asyncio.sleep(300)

    async def _extract_community_insights(self) -> List[Dict]:
        """Extract insights from community discussions"""
        insights = []

        # Search for problem statements and discussions
        search_queries = [
            'problem with', 'struggling with', 'need help', 'looking for solution',
            'pain point', 'frustrating', 'difficult to', 'wish there was'
        ]

        for query in search_queries[:4]:  # Limit queries
            try:
                posts = await self.bluesky_handler.search_posts(query, limit=8)

                for post in posts:
                    if post['metrics']['engagement'] > 8:
                        insight = await self._analyze_community_post(post)
                        if insight:
                            insights.append(insight)

            except Exception as e:
                logger.warning(f"Error with query '{query}': {e}")
                continue

        return insights

    # ================================================================
    # FEEDBACK ENHANCEMENT LOOP
    # ================================================================

    async def _feedback_enhancement_loop(self):
        """Enhanced feedback collection from Bluesky"""
        logger.info("🔄 Starting feedback enhancement loop")

        while self.is_learning_active:
            try:
                # Collect Bluesky feedback
                bluesky_feedback = await self._collect_bluesky_feedback()

                if bluesky_feedback:
                    # Generate insights from feedback
                    insights = await self._generate_bluesky_insights(bluesky_feedback)

                    if insights:
                        await self._apply_feedback_insights(insights)
                        logger.info(f"💬 Processed {len(bluesky_feedback)} feedback items, generated {len(insights)} insights")

                # Update every 40 minutes
                await asyncio.sleep(2400)

            except Exception as e:
                logger.error(f"Error in feedback enhancement loop: {e}")
                await asyncio.sleep(300)

    async def _collect_bluesky_feedback(self) -> List[FeedbackItem]:
        """Collect feedback signals from Bluesky"""
        feedback_items = []

        # Monitor mentions of AI agents, job matching, etc.
        search_terms = ['AI agent', 'job matching', 'automated hiring', 'AI job search']

        for term in search_terms:
            try:
                posts = await self.bluesky_handler.search_posts(term, limit=5)

                for post in posts:
                    if self._contains_feedback_signals(post):
                        feedback = FeedbackItem(
                            id=f"bluesky_{post['cid']}",
                            timestamp=datetime.now(),
                            source="bluesky_community",
                            category=self._classify_feedback(post),
                            target="platform_reputation",
                            rating=self._extract_sentiment_rating(post),
                            message=post['text'],
                            context={
                                'author': post['author']['handle'],
                                'engagement': post['metrics']['engagement'],
                                'url': f"https://bsky.app/profile/{post['author']['handle']}/post/{post['uri'].split('/')[-1]}"
                            }
                        )
                        feedback_items.append(feedback)

            except Exception as e:
                logger.warning(f"Error collecting feedback for '{term}': {e}")
                continue

        return feedback_items

    # ================================================================
    # APPLICATION AND INTEGRATION METHODS
    # ================================================================

    async def _apply_expert_insights_to_agents(self, insights: List[ExpertInsight]):
        """Apply expert insights to relevant agents"""
        for insight in insights:
            # Determine which agents would benefit from this insight
            relevant_agents = self._find_relevant_agents(insight.topic)

            # Create learning updates for each relevant agent
            for agent_class in relevant_agents:
                await self._update_agent_knowledge(agent_class, insight)

        self.learning_stats['agent_updates_made'] += len(insights)

    async def _apply_trend_learnings(self, trend_analyses: List[TrendAnalysis]):
        """Apply trend learning to agent strategies"""
        for trend in trend_analyses:
            if trend.opportunity_score > 0.6:  # High opportunity trends
                await self._update_opportunity_detection_agents(trend)

            if trend.community_sentiment < -0.3:  # Negative sentiment trends
                await self._update_risk_assessment_agents(trend)

    async def _process_market_signals(self, signals: List[MarketSignal]):
        """Process market signals and update agents"""
        high_priority_signals = [s for s in signals if s.strength > 0.7 and s.urgency > 0.6]

        for signal in high_priority_signals:
            if signal.signal_type == 'hiring':
                await self._update_job_matching_agents(signal)
            elif signal.signal_type == 'layoffs':
                await self._update_market_risk_agents(signal)
            elif signal.signal_type == 'skills':
                await self._update_skill_demand_models(signal)

    async def _apply_sentiment_adjustments(self, sentiment_analyses: Dict[str, Dict]):
        """Apply sentiment-based adjustments to agent behavior"""
        for topic, sentiment_data in sentiment_analyses.items():
            if topic == 'ai jobs' and sentiment_data['overall_sentiment'] < -0.3:
                # Negative sentiment about AI jobs - adjust strategy
                await self._adjust_ai_job_strategy(sentiment_data)
            elif topic == 'remote work' and sentiment_data['overall_sentiment'] > 0.5:
                # Positive sentiment about remote work - boost remote opportunities
                await self._boost_remote_opportunities(sentiment_data)

    # ================================================================
    # UTILITY METHODS
    # ================================================================

    def _classify_topic(self, content: str, field: str) -> str:
        """Classify the topic of content within a field"""
        # Simplified classification - in production, use more sophisticated methods
        field_topics = {
            'ai_researchers': ['machine learning', 'deep learning', 'neural networks', 'AI safety'],
            'investors': ['valuation', 'market trends', 'investment strategy', 'portfolio management'],
            'entrepreneurs': ['startup strategy', 'product development', 'team building', 'fundraising'],
            'developers': ['programming', 'software architecture', 'development tools', 'best practices'],
            'economists': ['economic indicators', 'policy analysis', 'market dynamics', 'forecasting']
        }

        topics = field_topics.get(field, [])
        content_lower = content.lower()

        for topic in topics:
            if any(word in content_lower for word in topic.split()):
                return topic

        return f"{field}_general"

    def _calculate_content_relevance(self, content: str, signal_type: str) -> float:
        """Calculate how relevant content is to a signal type"""
        keywords = self.market_keywords.get(signal_type, [])
        content_lower = content.lower()

        relevance_score = sum(1 for keyword in keywords if keyword in content_lower)
        return min(1.0, relevance_score / len(keywords))

    def _extract_affected_sectors(self, content: str) -> List[str]:
        """Extract sectors mentioned in content"""
        sectors = ['tech', 'finance', 'healthcare', 'education', 'retail', 'manufacturing', 'energy']
        content_lower = content.lower()

        affected = [sector for sector in sectors if sector in content_lower]
        return affected

    def _contains_feedback_signals(self, post: Dict) -> bool:
        """Check if post contains feedback signals"""
        feedback_indicators = [
            'review', 'experience with', 'opinion on', 'thoughts on',
            'disappointed', 'impressed', 'works well', 'doesn\'t work',
            'recommend', 'avoid', 'love', 'hate'
        ]

        content_lower = post['text'].lower()
        return any(indicator in content_lower for indicator in feedback_indicators)

    def _classify_feedback(self, post: Dict) -> str:
        """Classify the type of feedback"""
        content_lower = post['text'].lower()

        if any(word in content_lower for word in ['error', 'bug', 'broken', 'doesn\'t work']):
            return 'error'
        elif any(word in content_lower for word in ['slow', 'fast', 'performance']):
            return 'performance'
        elif any(word in content_lower for word in ['difficult', 'easy', 'confusing', 'intuitive']):
            return 'usability'
        else:
            return 'general'

    def _extract_sentiment_rating(self, post: Dict) -> float:
        """Extract sentiment rating from post"""
        blob = TextBlob(post['text'])
        sentiment = blob.sentiment.polarity

        # Convert to 0-1 scale (0 = very negative, 1 = very positive)
        return (sentiment + 1) / 2

    def _find_relevant_agents(self, topic: str) -> List[str]:
        """Find agents relevant to a specific topic"""
        # This would integrate with your agent registry
        # For now, return example relevant agents
        topic_agent_mapping = {
            'machine learning': ['ml_specialist', 'data_analyst'],
            'investment strategy': ['financial_advisor', 'market_analyst'],
            'startup strategy': ['business_consultant', 'strategy_advisor'],
            'programming': ['code_reviewer', 'tech_consultant']
        }

        return topic_agent_mapping.get(topic, ['general_assistant'])

    async def _establish_learning_baselines(self):
        """Establish baselines for learning metrics"""
        logger.info("📊 Establishing learning baselines")

        # Initialize baseline metrics
        self.learning_baselines = {
            'daily_insights_target': 50,
            'trend_detection_accuracy': 0.7,
            'market_signal_relevance': 0.6,
            'agent_improvement_rate': 0.05
        }

        self.last_update_time = datetime.now()

    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        uptime_hours = (datetime.now() - self.last_update_time).total_seconds() / 3600 if self.last_update_time else 0

        return {
            'is_active': self.is_learning_active,
            'uptime_hours': round(uptime_hours, 2),
            'statistics': self.learning_stats,
            'learning_rate': {
                'insights_per_hour': self.learning_stats['insights_extracted'] / max(1, uptime_hours),
                'trends_per_hour': self.learning_stats['trends_detected'] / max(1, uptime_hours),
                'signals_per_hour': self.learning_stats['market_signals_processed'] / max(1, uptime_hours)
            },
            'expert_tracking': {
                'total_experts': sum(len(experts) for experts in self.expert_handles.values()),
                'fields_monitored': list(self.expert_handles.keys())
            }
        }


# Global instance for easy access
# Global instance - created lazily to avoid circular imports
_bluesky_learning_bridge_instance = None

def get_bluesky_learning_bridge():
    """Get or create the singleton BlueskyLearningBridge instance"""
    global _bluesky_learning_bridge_instance
    if _bluesky_learning_bridge_instance is None:
        _bluesky_learning_bridge_instance = BlueskyLearningBridge()
    return _bluesky_learning_bridge_instance

# For backward compatibility
bluesky_learning_bridge = None


async def start_bluesky_learning():
    """Start the Bluesky learning system"""
    await bluesky_learning_bridge.start_continuous_learning()


async def stop_bluesky_learning():
    """Stop the Bluesky learning system"""
    await bluesky_learning_bridge.stop_continuous_learning()


async def get_learning_stats():
    """Get learning statistics"""
    return await bluesky_learning_bridge.get_learning_statistics()


if __name__ == "__main__":
    # Test the learning system
    async def test_learning_system():
        print("🦋 Testing Bluesky Learning Bridge")

        # Initialize
        bridge = BlueskyLearningBridge()

        # Test expert knowledge extraction
        print("\n1. Testing expert knowledge extraction...")
        insights = await bridge._extract_field_expert_knowledge('ai_researchers', ['karpathy.ai'])
        print(f"   Extracted {len(insights)} expert insights")

        # Test trend detection
        print("\n2. Testing trend detection...")
        trending = await bluesky_handler.get_trending()
        if trending:
            trends = await bridge._analyze_trending_content(trending[:5])
            print(f"   Detected {len(trends)} trends")

        # Test market intelligence
        print("\n3. Testing market intelligence...")
        signals = await bridge._collect_market_signals('hiring', ['hiring', 'job opening'])
        print(f"   Collected {len(signals)} market signals")

        print("\n✅ Bluesky Learning Bridge test complete!")

    # Run test
    asyncio.run(test_learning_system())