"""
Data Transformation Pipeline - Spider to Learning Signals
========================================================

This module transforms raw spider data into actionable learning signals
that can be consumed by the learning loop and agents.

Capabilities:
- Real-time data transformation from 1,770+ spiders
- Learning signal generation and enrichment
- Data quality scoring and validation
- Multi-format data normalization
- Context-aware signal routing
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class RawSpiderData:
    """Raw data from spiders before transformation"""
    spider_id: str
    spider_type: str
    source_url: str
    timestamp: datetime
    raw_content: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float = 0.0


@dataclass
class EnrichedLearningSignal:
    """Enriched learning signal for agents"""
    signal_id: str
    signal_type: str  # 'market_trend', 'opportunity', 'insight', 'alert'
    category: str     # 'financial', 'freelance', 'content', 'tech', etc.
    priority: int     # 1=critical, 2=high, 3=medium, 4=low, 5=info
    confidence: float # 0.0-1.0

    # Learning data
    content: Dict[str, Any]
    key_insights: List[str]
    actionable_items: List[str]
    trend_indicators: Dict[str, Any]

    # Routing information
    target_agents: List[str]
    target_advisors: List[str]
    affected_domains: List[str]

    # Metadata
    source_spiders: List[str]
    generation_method: str
    timestamp: datetime
    expires_at: Optional[datetime] = None
    processing_metadata: Dict[str, Any] = None


@dataclass
class TransformationRule:
    """Rule for transforming spider data to learning signals"""
    rule_id: str
    name: str
    description: str
    source_spider_types: List[str]
    data_patterns: List[str]
    transformation_function: Callable
    target_signal_types: List[str]
    priority: int = 3
    enabled: bool = True


class DataTransformationPipeline:
    """
    Transforms raw spider data into enriched learning signals.
    Handles data from 1,770+ spiders and creates actionable intelligence.
    """

    def __init__(self):
        self.transformation_rules: Dict[str, TransformationRule] = {}
        self.redis_client: Optional[redis.Redis] = None
        self.processing_stats = {
            'signals_generated': 0,
            'data_processed': 0,
            'transformations_applied': 0,
            'quality_score_avg': 0.0
        }

        # Signal routing configuration
        self.agent_routing_map = {
            'financial': ['investment_advisor', 'crypto_analyst', 'market_predictor', 'financial_planner'],
            'freelance': ['job_matcher', 'career_advisor', 'skill_analyzer', 'rate_optimizer'],
            'content': ['content_strategist', 'monetization_optimizer', 'audience_builder'],
            'tech': ['tech_scout', 'innovation_tracker', 'startup_analyzer', 'patent_monitor'],
            'news': ['news_analyst', 'sentiment_tracker', 'trend_predictor'],
            'market': ['market_analyst', 'trading_bot', 'risk_assessor'],
            'social': ['social_analyst', 'influencer_tracker', 'viral_predictor'],
            'innovation': ['innovation_scout', 'patent_analyzer', 'research_tracker']
        }

        self.advisor_routing_map = {
            'financial': ['Warren Buffett', 'Ray Dalio', 'George Soros', 'Paul Tudor Jones'],
            'freelance': ['Reid Hoffman', 'Sheryl Sandberg'],
            'content': ['Gary Vaynerchuk', 'Seth Godin', 'Naval Ravikant'],
            'tech': ['Peter Thiel', 'Marc Andreessen', 'Sam Altman', 'Cathie Wood'],
            'general': ['All']
        }

        # Initialize transformation rules
        self._initialize_transformation_rules()

    async def initialize(self):
        """Initialize Redis connection and pipeline components"""
        try:
            self.redis_client = await redis.from_url(
                'redis://localhost:6379/0',
                encoding='utf-8',
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Data transformation pipeline Redis connection established")

            # Subscribe to spider data channels
            await self._setup_spider_data_subscriptions()

        except Exception as e:
            logger.error(f"Failed to initialize transformation pipeline: {e}")

    async def _setup_spider_data_subscriptions(self):
        """Setup subscriptions to spider data channels"""
        try:
            # Subscribe to all spider categories
            channels = [
                'spider:data:financial',
                'spider:data:freelance',
                'spider:data:content',
                'spider:data:tech',
                'spider:data:news',
                'spider:data:market',
                'spider:data:social',
                'spider:data:innovation',
                'spider:data:general'
            ]

            pubsub = self.redis_client.pubsub()
            for channel in channels:
                await pubsub.subscribe(channel)

            # Start processing task
            asyncio.create_task(self._process_spider_data_stream(pubsub))
            logger.info(f"Subscribed to {len(channels)} spider data channels")

        except Exception as e:
            logger.error(f"Failed to setup spider data subscriptions: {e}")

    async def _process_spider_data_stream(self, pubsub):
        """Process incoming spider data stream"""
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    channel = message['channel']
                    category = channel.split(':')[-1]  # Extract category from channel name

                    raw_data = json.loads(message['data'])
                    spider_data = RawSpiderData(**raw_data)

                    # Transform to learning signals
                    signals = await self.transform_data_to_signals(spider_data, category)

                    # Process and route signals
                    for signal in signals:
                        await self._route_learning_signal(signal)

                    self.processing_stats['data_processed'] += 1

                except Exception as e:
                    logger.error(f"Error processing spider data stream: {e}")

    def _initialize_transformation_rules(self):
        """Initialize data transformation rules for different spider types"""

        # Financial data transformation rules
        self._register_transformation_rule(TransformationRule(
            rule_id='financial_market_trend',
            name='Financial Market Trend Analysis',
            description='Transform financial data into market trend signals',
            source_spider_types=['financial', 'market', 'crypto'],
            data_patterns=['price', 'volume', 'market_cap', 'volatility'],
            transformation_function=self._transform_financial_data,
            target_signal_types=['market_trend', 'price_alert', 'volume_spike'],
            priority=1
        ))

        # Freelance opportunity transformation
        self._register_transformation_rule(TransformationRule(
            rule_id='freelance_opportunity',
            name='Freelance Opportunity Detection',
            description='Transform job/freelance data into opportunity signals',
            source_spider_types=['freelance', 'remote_work'],
            data_patterns=['job_title', 'salary', 'skills_required', 'deadline'],
            transformation_function=self._transform_freelance_data,
            target_signal_types=['job_opportunity', 'skill_demand', 'rate_trend'],
            priority=1
        ))

        # Content monetization transformation
        self._register_transformation_rule(TransformationRule(
            rule_id='content_monetization',
            name='Content Monetization Analysis',
            description='Transform content data into monetization signals',
            source_spider_types=['content', 'digital_products', 'social'],
            data_patterns=['engagement', 'views', 'revenue', 'audience_growth'],
            transformation_function=self._transform_content_data,
            target_signal_types=['content_trend', 'monetization_opportunity'],
            priority=2
        ))

        # Innovation tracking transformation
        self._register_transformation_rule(TransformationRule(
            rule_id='innovation_tracking',
            name='Innovation & Technology Tracking',
            description='Transform tech/research data into innovation signals',
            source_spider_types=['tech', 'innovation', 'research'],
            data_patterns=['patent', 'research_paper', 'funding', 'breakthrough'],
            transformation_function=self._transform_innovation_data,
            target_signal_types=['tech_breakthrough', 'patent_filed', 'research_published'],
            priority=2
        ))

        # News sentiment transformation
        self._register_transformation_rule(TransformationRule(
            rule_id='news_sentiment',
            name='News Sentiment Analysis',
            description='Transform news data into sentiment signals',
            source_spider_types=['news', 'social'],
            data_patterns=['headline', 'article_text', 'sentiment_score'],
            transformation_function=self._transform_news_data,
            target_signal_types=['breaking_news', 'sentiment_shift', 'public_opinion'],
            priority=2
        ))

        logger.info(f"Initialized {len(self.transformation_rules)} transformation rules")

    def _register_transformation_rule(self, rule: TransformationRule):
        """Register a transformation rule"""
        self.transformation_rules[rule.rule_id] = rule

    async def transform_data_to_signals(self, spider_data: RawSpiderData, category: str) -> List[EnrichedLearningSignal]:
        """Transform raw spider data to enriched learning signals"""
        signals = []

        try:
            # Find applicable transformation rules
            applicable_rules = self._find_applicable_rules(spider_data, category)

            for rule in applicable_rules:
                if rule.enabled:
                    try:
                        # Apply transformation rule
                        rule_signals = await rule.transformation_function(spider_data, category)
                        signals.extend(rule_signals)
                        self.processing_stats['transformations_applied'] += 1

                    except Exception as e:
                        logger.error(f"Error applying transformation rule {rule.rule_id}: {e}")

            # Enhance signals with routing information
            for signal in signals:
                signal = self._enrich_signal_routing(signal, category)

            # Update statistics
            self.processing_stats['signals_generated'] += len(signals)

            return signals

        except Exception as e:
            logger.error(f"Error transforming data to signals: {e}")
            return []

    def _find_applicable_rules(self, spider_data: RawSpiderData, category: str) -> List[TransformationRule]:
        """Find transformation rules applicable to the spider data"""
        applicable_rules = []

        for rule in self.transformation_rules.values():
            # Check spider type match
            if spider_data.spider_type in rule.source_spider_types or category in rule.source_spider_types:
                # Check data pattern match
                content_str = json.dumps(spider_data.raw_content).lower()
                pattern_matches = sum(1 for pattern in rule.data_patterns if pattern in content_str)

                if pattern_matches > 0:
                    applicable_rules.append(rule)

        # Sort by priority (lower number = higher priority)
        applicable_rules.sort(key=lambda r: r.priority)
        return applicable_rules

    async def _transform_financial_data(self, spider_data: RawSpiderData, category: str) -> List[EnrichedLearningSignal]:
        """Transform financial spider data into market signals"""
        signals = []
        content = spider_data.raw_content

        try:
            # Price movement signals
            if 'price' in content:
                price_data = content['price']
                if isinstance(price_data, (int, float)):
                    signal = EnrichedLearningSignal(
                        signal_id=f"financial_price_{datetime.now().timestamp()}",
                        signal_type='market_trend',
                        category='financial',
                        priority=1 if abs(price_data) > 0.05 else 2,  # High priority for >5% moves
                        confidence=spider_data.quality_score * 0.9,
                        content={
                            'price_data': price_data,
                            'source': spider_data.source_url,
                            'timestamp': spider_data.timestamp.isoformat()
                        },
                        key_insights=[
                            f"Price movement detected: {price_data}%",
                            f"Source: {spider_data.spider_type}"
                        ],
                        actionable_items=[
                            "Monitor portfolio exposure",
                            "Review risk management strategy",
                            "Consider rebalancing opportunities"
                        ],
                        trend_indicators={
                            'direction': 'up' if price_data > 0 else 'down',
                            'magnitude': abs(price_data),
                            'significance': 'high' if abs(price_data) > 0.05 else 'medium'
                        },
                        target_agents=[],
                        target_advisors=[],
                        affected_domains=['investing', 'trading', 'portfolio_management'],
                        source_spiders=[spider_data.spider_id],
                        generation_method='financial_transformation',
                        timestamp=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
                        processing_metadata={
                            'transformation_rule': 'financial_market_trend',
                            'data_quality': spider_data.quality_score
                        }
                    )
                    signals.append(signal)

            # Volume spike signals
            if 'volume' in content:
                volume_data = content['volume']
                if isinstance(volume_data, (int, float)) and volume_data > 1.5:  # 50% above normal
                    signal = EnrichedLearningSignal(
                        signal_id=f"financial_volume_{datetime.now().timestamp()}",
                        signal_type='volume_spike',
                        category='financial',
                        priority=2,
                        confidence=spider_data.quality_score * 0.8,
                        content={
                            'volume_ratio': volume_data,
                            'source': spider_data.source_url
                        },
                        key_insights=[
                            f"Volume spike detected: {volume_data:.1f}x normal",
                            "Potential market interest increase"
                        ],
                        actionable_items=[
                            "Investigate cause of volume increase",
                            "Monitor for breakout patterns",
                            "Check news correlations"
                        ],
                        trend_indicators={
                            'volume_multiplier': volume_data,
                            'market_interest': 'high'
                        },
                        target_agents=[],
                        target_advisors=[],
                        affected_domains=['trading', 'market_analysis'],
                        source_spiders=[spider_data.spider_id],
                        generation_method='financial_transformation',
                        timestamp=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
                    )
                    signals.append(signal)

        except Exception as e:
            logger.error(f"Error in financial data transformation: {e}")

        return signals

    async def _transform_freelance_data(self, spider_data: RawSpiderData, category: str) -> List[EnrichedLearningSignal]:
        """Transform freelance spider data into opportunity signals"""
        signals = []
        content = spider_data.raw_content

        try:
            # Job opportunity signals
            if 'job_title' in content or 'title' in content:
                title = content.get('job_title', content.get('title', ''))
                salary = content.get('salary', content.get('budget', 0))
                skills = content.get('skills_required', content.get('skills', []))

                signal = EnrichedLearningSignal(
                    signal_id=f"freelance_job_{datetime.now().timestamp()}",
                    signal_type='job_opportunity',
                    category='freelance',
                    priority=1 if salary > 5000 else 2,  # High priority for >$5k jobs
                    confidence=spider_data.quality_score,
                    content={
                        'job_title': title,
                        'salary_budget': salary,
                        'required_skills': skills,
                        'source_platform': spider_data.spider_type,
                        'posting_url': spider_data.source_url
                    },
                    key_insights=[
                        f"New opportunity: {title}",
                        f"Budget: ${salary}" if salary else "Budget not specified",
                        f"Skills: {', '.join(skills[:3])}" if skills else "Skills not specified"
                    ],
                    actionable_items=[
                        "Assess skill requirements match",
                        "Prepare tailored proposal",
                        "Research client/company background",
                        "Calculate time investment needed"
                    ],
                    trend_indicators={
                        'skill_demand': skills,
                        'budget_tier': 'high' if salary > 5000 else 'medium' if salary > 1000 else 'low',
                        'urgency': 'high' if 'urgent' in title.lower() else 'normal'
                    },
                    target_agents=[],
                    target_advisors=[],
                    affected_domains=['freelancing', 'career_development', 'skill_matching'],
                    source_spiders=[spider_data.spider_id],
                    generation_method='freelance_transformation',
                    timestamp=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=7)  # Jobs expire in a week
                )
                signals.append(signal)

        except Exception as e:
            logger.error(f"Error in freelance data transformation: {e}")

        return signals

    async def _transform_content_data(self, spider_data: RawSpiderData, category: str) -> List[EnrichedLearningSignal]:
        """Transform content spider data into monetization signals"""
        signals = []
        content = spider_data.raw_content

        try:
            # Viral content signals
            if 'engagement' in content or 'views' in content:
                engagement = content.get('engagement', 0)
                views = content.get('views', 0)

                if engagement > 1000 or views > 10000:  # Viral threshold
                    signal = EnrichedLearningSignal(
                        signal_id=f"content_viral_{datetime.now().timestamp()}",
                        signal_type='content_trend',
                        category='content',
                        priority=1,
                        confidence=spider_data.quality_score,
                        content={
                            'engagement_count': engagement,
                            'view_count': views,
                            'content_type': content.get('type', 'unknown'),
                            'platform': spider_data.spider_type,
                            'content_url': spider_data.source_url
                        },
                        key_insights=[
                            f"Viral content detected: {engagement} engagement, {views} views",
                            f"Content type: {content.get('type', 'unknown')}",
                            f"Platform: {spider_data.spider_type}"
                        ],
                        actionable_items=[
                            "Analyze content format and style",
                            "Identify viral elements for replication",
                            "Consider similar content creation",
                            "Study audience engagement patterns"
                        ],
                        trend_indicators={
                            'virality_score': min(1.0, (engagement + views/10) / 10000),
                            'content_format': content.get('type', 'unknown'),
                            'engagement_rate': engagement / max(views, 1) if views else 0
                        },
                        target_agents=[],
                        target_advisors=[],
                        affected_domains=['content_creation', 'social_media', 'marketing'],
                        source_spiders=[spider_data.spider_id],
                        generation_method='content_transformation',
                        timestamp=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(days=3)
                    )
                    signals.append(signal)

        except Exception as e:
            logger.error(f"Error in content data transformation: {e}")

        return signals

    async def _transform_innovation_data(self, spider_data: RawSpiderData, category: str) -> List[EnrichedLearningSignal]:
        """Transform innovation spider data into breakthrough signals"""
        signals = []
        content = spider_data.raw_content

        try:
            # Technology breakthrough signals
            if any(keyword in json.dumps(content).lower() for keyword in ['ai', 'blockchain', 'quantum', 'breakthrough']):
                signal = EnrichedLearningSignal(
                    signal_id=f"innovation_tech_{datetime.now().timestamp()}",
                    signal_type='tech_breakthrough',
                    category='tech',
                    priority=1,
                    confidence=spider_data.quality_score,
                    content={
                        'innovation_type': self._extract_innovation_type(content),
                        'description': content.get('description', ''),
                        'research_source': spider_data.source_url,
                        'publication_date': spider_data.timestamp.isoformat()
                    },
                    key_insights=[
                        f"Technology breakthrough in {self._extract_innovation_type(content)}",
                        "Potential disruption opportunity identified",
                        f"Source: {spider_data.spider_type}"
                    ],
                    actionable_items=[
                        "Research commercial applications",
                        "Assess market disruption potential",
                        "Identify investment opportunities",
                        "Monitor patent filings"
                    ],
                    trend_indicators={
                        'innovation_field': self._extract_innovation_type(content),
                        'disruption_potential': 'high',
                        'market_readiness': self._assess_market_readiness(content)
                    },
                    target_agents=[],
                    target_advisors=[],
                    affected_domains=['technology', 'innovation', 'investing', 'startups'],
                    source_spiders=[spider_data.spider_id],
                    generation_method='innovation_transformation',
                    timestamp=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + timedelta(days=30)
                )
                signals.append(signal)

        except Exception as e:
            logger.error(f"Error in innovation data transformation: {e}")

        return signals

    async def _transform_news_data(self, spider_data: RawSpiderData, category: str) -> List[EnrichedLearningSignal]:
        """Transform news spider data into sentiment signals"""
        signals = []
        content = spider_data.raw_content

        try:
            # Breaking news signals
            if 'headline' in content or 'title' in content:
                headline = content.get('headline', content.get('title', ''))
                sentiment = self._calculate_sentiment(headline)

                # High impact news detection
                impact_keywords = ['crisis', 'breakthrough', 'merger', 'acquisition', 'bankruptcy', 'ipo']
                is_high_impact = any(keyword in headline.lower() for keyword in impact_keywords)

                if is_high_impact or abs(sentiment) > 0.5:
                    signal = EnrichedLearningSignal(
                        signal_id=f"news_break_{datetime.now().timestamp()}",
                        signal_type='breaking_news',
                        category='news',
                        priority=1 if is_high_impact else 2,
                        confidence=spider_data.quality_score,
                        content={
                            'headline': headline,
                            'sentiment_score': sentiment,
                            'article_summary': content.get('summary', ''),
                            'news_source': spider_data.spider_type,
                            'article_url': spider_data.source_url
                        },
                        key_insights=[
                            f"Breaking: {headline}",
                            f"Sentiment: {'Positive' if sentiment > 0 else 'Negative' if sentiment < 0 else 'Neutral'}",
                            f"Impact level: {'High' if is_high_impact else 'Medium'}"
                        ],
                        actionable_items=[
                            "Monitor market reaction",
                            "Assess portfolio implications",
                            "Update risk assessments",
                            "Prepare client communications"
                        ],
                        trend_indicators={
                            'sentiment_direction': 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral',
                            'impact_level': 'high' if is_high_impact else 'medium',
                            'market_relevance': self._assess_market_relevance(headline)
                        },
                        target_agents=[],
                        target_advisors=[],
                        affected_domains=['news_analysis', 'market_sentiment', 'risk_management'],
                        source_spiders=[spider_data.spider_id],
                        generation_method='news_transformation',
                        timestamp=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=6)
                    )
                    signals.append(signal)

        except Exception as e:
            logger.error(f"Error in news data transformation: {e}")

        return signals

    def _enrich_signal_routing(self, signal: EnrichedLearningSignal, category: str) -> EnrichedLearningSignal:
        """Enrich signal with appropriate agent and advisor routing"""
        try:
            # Add target agents
            signal.target_agents = self.agent_routing_map.get(category, [])

            # Add target advisors
            signal.target_advisors = self.advisor_routing_map.get(category, self.advisor_routing_map.get('general', []))

            return signal

        except Exception as e:
            logger.error(f"Error enriching signal routing: {e}")
            return signal

    async def _route_learning_signal(self, signal: EnrichedLearningSignal):
        """Route enriched learning signal to learning loop"""
        try:
            # Convert to learning loop format
            from .learning_loop import FeedbackItem, learning_loop

            feedback = FeedbackItem(
                id=signal.signal_id,
                timestamp=signal.timestamp,
                source=f"spider_{signal.category}",
                category=signal.signal_type,
                target='platform_learning',
                rating=signal.confidence,
                message=f"Spider intelligence: {signal.signal_type}",
                context=asdict(signal),
                metadata={
                    'affected_agents': signal.target_agents,
                    'affected_advisors': signal.target_advisors,
                    'expires_at': signal.expires_at.isoformat() if signal.expires_at else None,
                    'priority': signal.priority,
                    'domains': signal.affected_domains
                }
            )

            # Store in learning loop
            learning_loop._store_feedback(feedback)

            # Trigger learning if high priority
            if signal.priority <= 2:  # High priority signals
                await learning_loop._trigger_immediate_learning(feedback)

            # Publish to Redis for real-time consumption
            await self._publish_signal_to_redis(signal)

            logger.debug(f"Routed learning signal {signal.signal_id} to learning loop")

        except Exception as e:
            logger.error(f"Error routing learning signal: {e}")

    async def _publish_signal_to_redis(self, signal: EnrichedLearningSignal):
        """Publish learning signal to Redis for real-time consumption"""
        try:
            if not self.redis_client:
                return

            signal_data = asdict(signal)
            signal_data['timestamp'] = signal.timestamp.isoformat()
            if signal.expires_at:
                signal_data['expires_at'] = signal.expires_at.isoformat()

            # Publish to general learning signal channel
            await self.redis_client.publish(
                'learning:signals:general',
                json.dumps(signal_data)
            )

            # Publish to category-specific channel
            await self.redis_client.publish(
                f'learning:signals:{signal.category}',
                json.dumps(signal_data)
            )

            # Publish to each target agent
            for agent in signal.target_agents:
                await self.redis_client.publish(
                    f'learning:signals:agent:{agent}',
                    json.dumps(signal_data)
                )

        except Exception as e:
            logger.error(f"Error publishing signal to Redis: {e}")

    # Helper methods for data analysis
    def _extract_innovation_type(self, content: Dict[str, Any]) -> str:
        """Extract innovation type from content"""
        text = json.dumps(content).lower()

        if 'ai' in text or 'artificial intelligence' in text:
            return 'artificial_intelligence'
        elif 'blockchain' in text or 'crypto' in text:
            return 'blockchain'
        elif 'quantum' in text:
            return 'quantum_computing'
        elif 'biotech' in text or 'medical' in text:
            return 'biotechnology'
        elif 'energy' in text or 'solar' in text:
            return 'clean_energy'
        else:
            return 'general_technology'

    def _assess_market_readiness(self, content: Dict[str, Any]) -> str:
        """Assess market readiness of innovation"""
        text = json.dumps(content).lower()

        if any(word in text for word in ['commercial', 'market', 'product', 'launch']):
            return 'ready'
        elif any(word in text for word in ['prototype', 'pilot', 'testing']):
            return 'development'
        elif any(word in text for word in ['research', 'study', 'laboratory']):
            return 'research'
        else:
            return 'unknown'

    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score for text"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except ImportError:
            # Fallback sentiment calculation
            positive_words = ['good', 'great', 'excellent', 'success', 'growth', 'profit', 'up', 'rise', 'gain']
            negative_words = ['bad', 'terrible', 'crisis', 'loss', 'down', 'fall', 'drop', 'decline']

            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count + negative_count == 0:
                return 0.0

            return (positive_count - negative_count) / (positive_count + negative_count)

    def _assess_market_relevance(self, headline: str) -> str:
        """Assess market relevance of news headline"""
        headline_lower = headline.lower()

        if any(word in headline_lower for word in ['stock', 'market', 'trading', 'nasdaq', 'dow', 'sp500']):
            return 'high'
        elif any(word in headline_lower for word in ['economy', 'gdp', 'inflation', 'fed', 'interest']):
            return 'high'
        elif any(word in headline_lower for word in ['company', 'earnings', 'revenue', 'profit']):
            return 'medium'
        else:
            return 'low'

    async def get_transformation_statistics(self) -> Dict[str, Any]:
        """Get transformation pipeline statistics"""
        return {
            'rules_registered': len(self.transformation_rules),
            'signals_generated': self.processing_stats['signals_generated'],
            'data_processed': self.processing_stats['data_processed'],
            'transformations_applied': self.processing_stats['transformations_applied'],
            'average_quality_score': self.processing_stats['quality_score_avg'],
            'active_rules': len([r for r in self.transformation_rules.values() if r.enabled]),
            'pipeline_status': 'active' if self.redis_client else 'disconnected'
        }

    async def cleanup(self):
        """Cleanup pipeline resources"""
        if self.redis_client:
            await self.redis_client.close()


# Global pipeline instance
_transformation_pipeline = None

def get_transformation_pipeline() -> DataTransformationPipeline:
    """Get or create the global transformation pipeline instance"""
    global _transformation_pipeline
    if _transformation_pipeline is None:
        _transformation_pipeline = DataTransformationPipeline()
    return _transformation_pipeline


# Convenience functions
async def transform_spider_data(spider_data: RawSpiderData, category: str) -> List[EnrichedLearningSignal]:
    """Transform spider data using the global pipeline"""
    pipeline = get_transformation_pipeline()
    return await pipeline.transform_data_to_signals(spider_data, category)


async def start_transformation_pipeline():
    """Start the transformation pipeline"""
    pipeline = get_transformation_pipeline()
    await pipeline.initialize()
    return pipeline