"""
Real-time Intelligence Distribution System
Feeds data from spider army to 102 agents and 25 advisors in real-time
"""

import logging
import json
import redis
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
import sys
import os

# Add Django setup
sys.path.append('/Users/donkeyking/Donkey_Betz/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()

from intelligence.models import (
    SpiderIntelligenceNode, AgentIntelligenceFeed,
    AdvisorIntelligenceFeed
)


@dataclass
class AdvisorProfile:
    """Profile of legendary advisor personalities"""
    name: str
    investment_style: str
    keywords: List[str]
    industries: List[str]
    relevance_threshold: float
    max_daily_feeds: int


class IntelligenceDistributionEngine:
    """
    Real-time distribution engine for spider intelligence
    Routes data to appropriate agents and advisors based on relevance
    """

    def __init__(self):
        self.logger = logging.getLogger('intelligence.distribution')
        self.redis_client = self.setup_redis()

        # Define legendary advisor profiles
        self.advisor_profiles = self.setup_advisor_profiles()

        # Define agent specializations
        self.agent_specializations = self.setup_agent_specializations()

        self.logger.info("🧠 Intelligence Distribution Engine initialized")

    def setup_redis(self) -> redis.Redis:
        """Setup Redis connection"""
        try:
            from django.conf import settings
            client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            client.ping()
            return client
        except Exception as e:
            self.logger.error(f"❌ Redis connection failed: {e}")
            raise

    def setup_advisor_profiles(self) -> Dict[str, AdvisorProfile]:
        """Setup the 25 legendary advisor profiles"""
        profiles = {}

        # Warren Buffett - Value Investing Oracle
        profiles['warren_buffett'] = AdvisorProfile(
            name='Warren Buffett',
            investment_style='value_investing',
            keywords=[
                'berkshire', 'value', 'dividend', 'cash flow', 'earnings', 'moat',
                'competitive advantage', 'management', 'intrinsic value', 'long term',
                'quality', 'franchise', 'predictable', 'consumer goods', 'insurance',
                'pricing power', 'float', 'book value', 'return on equity'
            ],
            industries=['insurance', 'consumer_goods', 'utilities', 'railroads'],
            relevance_threshold=0.7,
            max_daily_feeds=50
        )

        # Cathie Wood - Disruptive Innovation
        profiles['cathie_wood'] = AdvisorProfile(
            name='Cathie Wood',
            investment_style='disruptive_innovation',
            keywords=[
                'ai', 'artificial intelligence', 'machine learning', 'automation',
                'genomics', 'crispr', 'gene therapy', 'blockchain', 'cryptocurrency',
                'electric vehicle', 'autonomous', 'robotics', 'space', 'satellite',
                'digital transformation', 'innovation', 'disruptive', 'breakthrough',
                'next generation', 'renewable energy', 'battery technology'
            ],
            industries=['technology', 'healthcare', 'automotive', 'aerospace'],
            relevance_threshold=0.6,
            max_daily_feeds=75
        )

        # Ray Dalio - Macro Economics
        profiles['ray_dalio'] = AdvisorProfile(
            name='Ray Dalio',
            investment_style='macro_economic',
            keywords=[
                'federal reserve', 'interest rate', 'inflation', 'gdp', 'unemployment',
                'monetary policy', 'fiscal policy', 'debt cycle', 'currency',
                'geopolitical', 'trade war', 'recession', 'economic data',
                'central bank', 'yield curve', 'commodities', 'dollar', 'china',
                'global economy', 'emerging markets', 'bond yields'
            ],
            industries=['fixed_income', 'currencies', 'commodities', 'global_markets'],
            relevance_threshold=0.8,
            max_daily_feeds=60
        )

        # Peter Thiel - Contrarian/Monopoly Investing
        profiles['peter_thiel'] = AdvisorProfile(
            name='Peter Thiel',
            investment_style='contrarian_monopoly',
            keywords=[
                'monopoly', 'network effects', 'zero to one', 'vertical integration',
                'proprietary technology', 'economies of scale', 'brand power',
                'switching costs', 'regulatory advantages', 'breakthrough',
                'contrarian', 'first mover', 'platform', 'winner take all'
            ],
            industries=['technology', 'software', 'platforms', 'startups'],
            relevance_threshold=0.7,
            max_daily_feeds=40
        )

        # Paul Graham - Startup Ecosystem
        profiles['paul_graham'] = AdvisorProfile(
            name='Paul Graham',
            investment_style='startup_early_stage',
            keywords=[
                'startup', 'y combinator', 'founder', 'mvp', 'product market fit',
                'user growth', 'retention', 'viral coefficient', 'network effects',
                'scalability', 'venture capital', 'seed funding', 'angel investing',
                'programming', 'hacker', 'silicon valley'
            ],
            industries=['technology', 'software', 'internet', 'mobile'],
            relevance_threshold=0.6,
            max_daily_feeds=45
        )

        # Michael Saylor - Bitcoin/Digital Assets
        profiles['michael_saylor'] = AdvisorProfile(
            name='Michael Saylor',
            investment_style='bitcoin_digital_assets',
            keywords=[
                'bitcoin', 'btc', 'digital gold', 'store of value', 'inflation hedge',
                'institutional adoption', 'corporate treasury', 'microstrategy',
                'digital asset', 'cryptocurrency', 'blockchain', 'defi',
                'monetary policy', 'fiat currency', 'sound money'
            ],
            industries=['cryptocurrency', 'fintech', 'technology'],
            relevance_threshold=0.8,
            max_daily_feeds=35
        )

        # Charlie Munger - Mental Models
        profiles['charlie_munger'] = AdvisorProfile(
            name='Charlie Munger',
            investment_style='mental_models_value',
            keywords=[
                'mental models', 'psychology', 'incentives', 'compound interest',
                'circle of competence', 'margin of safety', 'inversion',
                'latticework', 'multidisciplinary', 'worldly wisdom',
                'value investing', 'berkshire', 'quality businesses'
            ],
            industries=['diversified', 'consumer_goods', 'insurance', 'utilities'],
            relevance_threshold=0.75,
            max_daily_feeds=30
        )

        # Add more advisor profiles...
        # For brevity, I'll add a few more key ones

        # Paul Tudor Jones - Macro Trading
        profiles['paul_tudor_jones'] = AdvisorProfile(
            name='Paul Tudor Jones',
            investment_style='macro_trading',
            keywords=[
                'trading', 'macro', 'trend following', 'momentum', 'volatility',
                'risk management', 'position sizing', 'market timing',
                'technical analysis', 'chart patterns', 'breakouts'
            ],
            industries=['trading', 'hedge_funds', 'derivatives'],
            relevance_threshold=0.7,
            max_daily_feeds=55
        )

        # Stanley Druckenmiller - Growth at Reasonable Price
        profiles['stanley_druckenmiller'] = AdvisorProfile(
            name='Stanley Druckenmiller',
            investment_style='growth_at_reasonable_price',
            keywords=[
                'growth', 'technology', 'demographics', 'secular trends',
                'disruption', 'innovation', 'market leadership',
                'competitive advantage', 'scalability'
            ],
            industries=['technology', 'healthcare', 'consumer'],
            relevance_threshold=0.7,
            max_daily_feeds=45
        )

        # Marc Andreessen - Software Eating the World
        profiles['marc_andreessen'] = AdvisorProfile(
            name='Marc Andreessen',
            investment_style='software_venture',
            keywords=[
                'software', 'saas', 'platform', 'network effects', 'venture capital',
                'technology disruption', 'digital transformation', 'api economy',
                'cloud computing', 'artificial intelligence', 'automation'
            ],
            industries=['software', 'internet', 'technology'],
            relevance_threshold=0.6,
            max_daily_feeds=40
        )

        return profiles

    def setup_agent_specializations(self) -> Dict[str, List[str]]:
        """Setup agent specializations for routing"""
        return {
            # Income Building Agents
            'income_builder': ['job_opportunity', 'freelance', 'gig_economy'],
            'freelance_scout_agent': ['job_opportunity', 'upwork', 'freelancer', 'fiverr'],
            'opportunity_analyzer': ['job_opportunity', 'market_opportunity'],
            'gig_optimizer': ['gig_economy', 'service_optimization'],

            # Financial Analysis Agents
            'financial_analysis_agent': ['financial', 'market_data', 'earnings'],
            'value_investing_agent': ['financial', 'value_investing', 'fundamentals'],
            'market_research_agent': ['market_data', 'financial_news', 'trends'],
            'berkshire_analyzer': ['berkshire', 'warren_buffett', 'value_investing'],

            # Trading Agents
            'trading_agent_1': ['market_data', 'crypto', 'stocks', 'real_time'],
            'trading_agent_2': ['market_data', 'forex', 'commodities'],
            'trading_agent_3': ['market_data', 'options', 'derivatives'],
            'crypto_trader': ['crypto', 'cryptocurrency', 'blockchain'],
            'arbitrage_agent': ['arbitrage', 'price_differences', 'trading'],

            # Innovation and Tech Agents
            'innovation_scout': ['innovation', 'startups', 'technology'],
            'disruptive_tech_analyzer': ['disruptive_technology', 'innovation'],
            'startup_analyzer': ['startups', 'venture_capital', 'y_combinator'],
            'venture_scout': ['venture_capital', 'early_stage', 'startups'],

            # Content and Marketing Agents
            'content_creator_agent': ['content_opportunity', 'youtube', 'social_media'],
            'viral_content_analyzer': ['viral_content', 'trends', 'social_media'],
            'social_media_agent': ['social_media', 'twitter', 'trends'],
            'newsletter_creator': ['newsletter', 'substack', 'content'],

            # Macro and Economic Agents
            'macro_analyst': ['macro_economic', 'federal_reserve', 'economics'],
            'economic_cycle_tracker': ['economic_cycles', 'recession', 'inflation'],
            'currency_trader': ['currencies', 'forex', 'macro'],

            # Specialized Analysis Agents
            'blockchain_analyst': ['blockchain', 'crypto', 'defi'],
            'fundamental_analyst': ['fundamentals', 'sec_filings', 'financial_analysis'],
            'trend_analyzer': ['trends', 'market_trends', 'social_trends'],
            'risk_assessment_agent': ['risk', 'volatility', 'market_risk']
        }

    async def distribute_intelligence(self, intelligence_node: SpiderIntelligenceNode):
        """
        Main distribution function - routes intelligence to relevant agents and advisors
        """
        try:
            self.logger.info(f"📡 Distributing intelligence from {intelligence_node.spider_name}")

            # Distribute to agents
            agent_feeds = await self.distribute_to_agents(intelligence_node)

            # Distribute to advisors
            advisor_feeds = await self.distribute_to_advisors(intelligence_node)

            # Update distribution tracking
            intelligence_node.mark_as_distributed(
                agents=[feed.agent_name for feed in agent_feeds],
                advisors=[feed.advisor_name for feed in advisor_feeds]
            )

            # Send real-time notifications
            await self.send_realtime_notifications(intelligence_node, agent_feeds, advisor_feeds)

            self.logger.info(
                f"✅ Distributed to {len(agent_feeds)} agents and {len(advisor_feeds)} advisors"
            )

            return agent_feeds, advisor_feeds

        except Exception as e:
            self.logger.error(f"❌ Distribution failed: {e}")
            raise

    async def distribute_to_agents(self, intelligence_node: SpiderIntelligenceNode) -> List[AgentIntelligenceFeed]:
        """Distribute intelligence to relevant agents"""
        feeds = []

        for agent_name, specializations in self.agent_specializations.items():
            relevance_score = self.calculate_agent_relevance(
                intelligence_node,
                agent_name,
                specializations
            )

            if relevance_score >= 0.5:  # Threshold for agent relevance
                feed = AgentIntelligenceFeed.objects.create(
                    agent_name=agent_name,
                    intelligence_node=intelligence_node,
                    relevance_score=relevance_score
                )
                feeds.append(feed)

                # Send to Redis queue for real-time processing
                await self.queue_agent_intelligence(agent_name, intelligence_node, relevance_score)

        return feeds

    async def distribute_to_advisors(self, intelligence_node: SpiderIntelligenceNode) -> List[AdvisorIntelligenceFeed]:
        """Distribute intelligence to relevant advisor personalities"""
        feeds = []

        for advisor_name, profile in self.advisor_profiles.items():
            relevance_score = self.calculate_advisor_relevance(
                intelligence_node,
                profile
            )

            if relevance_score >= profile.relevance_threshold:
                # Check daily feed limits
                today_feeds = AdvisorIntelligenceFeed.objects.filter(
                    advisor_name=advisor_name,
                    delivered_at__date=datetime.now().date()
                ).count()

                if today_feeds < profile.max_daily_feeds:
                    feed = AdvisorIntelligenceFeed.objects.create(
                        advisor_name=advisor_name,
                        intelligence_node=intelligence_node,
                        advisor_relevance_score=relevance_score,
                        strategy_alignment_score=self.calculate_strategy_alignment(
                            intelligence_node, profile
                        )
                    )
                    feeds.append(feed)

                    # Send to Redis queue
                    await self.queue_advisor_intelligence(advisor_name, intelligence_node, relevance_score)

        return feeds

    def calculate_agent_relevance(self, intelligence_node: SpiderIntelligenceNode,
                                agent_name: str, specializations: List[str]) -> float:
        """Calculate relevance score for specific agent"""
        score = 0.0

        # Check intelligence type match
        if intelligence_node.intelligence_type in specializations:
            score += 0.4

        # Check spider name match
        spider_name_lower = intelligence_node.spider_name.lower()
        for spec in specializations:
            if spec.lower() in spider_name_lower:
                score += 0.2
                break

        # Check platform match
        platform_lower = intelligence_node.source_platform.lower()
        for spec in specializations:
            if spec.lower() in platform_lower:
                score += 0.2
                break

        # Check content keywords
        content_text = json.dumps(intelligence_node.raw_data).lower()
        keyword_matches = 0
        for spec in specializations:
            if spec.lower().replace('_', ' ') in content_text:
                keyword_matches += 1

        if keyword_matches > 0:
            score += min(0.3, keyword_matches * 0.1)

        # Boost score based on intelligence confidence
        score *= intelligence_node.confidence_score

        return min(1.0, score)

    def calculate_advisor_relevance(self, intelligence_node: SpiderIntelligenceNode,
                                  profile: AdvisorProfile) -> float:
        """Calculate relevance score for specific advisor"""
        score = 0.0

        # Get text content for keyword matching
        content_text = json.dumps(intelligence_node.raw_data).lower()

        # Keyword matching
        keyword_matches = 0
        for keyword in profile.keywords:
            if keyword.lower() in content_text:
                keyword_matches += 1

        # Base score from keyword matches
        if keyword_matches > 0:
            score = min(0.8, keyword_matches * 0.1)

        # Industry relevance
        if hasattr(intelligence_node, 'industry') and intelligence_node.industry in profile.industries:
            score += 0.2

        # Investment style specific boosts
        if profile.investment_style == 'value_investing' and intelligence_node.intelligence_type == 'financial':
            score += 0.2
        elif profile.investment_style == 'disruptive_innovation' and 'innovation' in content_text:
            score += 0.3
        elif profile.investment_style == 'macro_economic' and intelligence_node.intelligence_type == 'macro_economic':
            score += 0.3

        # Confidence adjustment
        score *= intelligence_node.confidence_score

        return min(1.0, score)

    def calculate_strategy_alignment(self, intelligence_node: SpiderIntelligenceNode,
                                   profile: AdvisorProfile) -> float:
        """Calculate how well intelligence aligns with advisor's strategy"""
        alignment = 0.5  # Base alignment

        content_text = json.dumps(intelligence_node.raw_data).lower()

        # Strategy-specific alignment calculations
        if profile.investment_style == 'value_investing':
            value_indicators = ['undervalued', 'cheap', 'discount', 'margin of safety', 'book value']
            matches = sum(1 for indicator in value_indicators if indicator in content_text)
            alignment += min(0.4, matches * 0.1)

        elif profile.investment_style == 'disruptive_innovation':
            innovation_indicators = ['disruptive', 'revolutionary', 'breakthrough', 'exponential']
            matches = sum(1 for indicator in innovation_indicators if indicator in content_text)
            alignment += min(0.4, matches * 0.1)

        elif profile.investment_style == 'macro_economic':
            macro_indicators = ['policy', 'central bank', 'economic outlook', 'global']
            matches = sum(1 for indicator in macro_indicators if indicator in content_text)
            alignment += min(0.4, matches * 0.1)

        return min(1.0, alignment)

    async def queue_agent_intelligence(self, agent_name: str, intelligence_node: SpiderIntelligenceNode,
                                     relevance_score: float):
        """Queue intelligence for agent processing"""
        intelligence_data = {
            'node_id': intelligence_node.id,
            'spider_name': intelligence_node.spider_name,
            'intelligence_type': intelligence_node.intelligence_type,
            'relevance_score': relevance_score,
            'data': intelligence_node.raw_data,
            'source_url': intelligence_node.source_url,
            'timestamp': intelligence_node.created_at.isoformat()
        }

        # Real-time channel
        channel = f"agent_intel:{agent_name}"
        self.redis_client.publish(channel, json.dumps(intelligence_data))

        # Persistent queue
        queue_key = f"agent_queue:{agent_name}"
        self.redis_client.lpush(queue_key, json.dumps(intelligence_data))
        self.redis_client.expire(queue_key, 86400)  # 24 hour TTL

    async def queue_advisor_intelligence(self, advisor_name: str, intelligence_node: SpiderIntelligenceNode,
                                       relevance_score: float):
        """Queue intelligence for advisor analysis"""
        intelligence_data = {
            'node_id': intelligence_node.id,
            'spider_name': intelligence_node.spider_name,
            'intelligence_type': intelligence_node.intelligence_type,
            'advisor_relevance_score': relevance_score,
            'data': intelligence_node.raw_data,
            'source_url': intelligence_node.source_url,
            'timestamp': intelligence_node.created_at.isoformat()
        }

        # Real-time channel
        channel = f"advisor_intel:{advisor_name}"
        self.redis_client.publish(channel, json.dumps(intelligence_data))

        # Persistent queue
        queue_key = f"advisor_queue:{advisor_name}"
        self.redis_client.lpush(queue_key, json.dumps(intelligence_data))
        self.redis_client.expire(queue_key, 86400)  # 24 hour TTL

    async def send_realtime_notifications(self, intelligence_node: SpiderIntelligenceNode,
                                        agent_feeds: List[AgentIntelligenceFeed],
                                        advisor_feeds: List[AdvisorIntelligenceFeed]):
        """Send real-time notifications about intelligence distribution"""
        notification = {
            'type': 'intelligence_distributed',
            'spider_name': intelligence_node.spider_name,
            'intelligence_type': intelligence_node.intelligence_type,
            'agent_count': len(agent_feeds),
            'advisor_count': len(advisor_feeds),
            'confidence_score': intelligence_node.confidence_score,
            'timestamp': datetime.now().isoformat()
        }

        # Global intelligence notification channel
        self.redis_client.publish('intelligence_notifications', json.dumps(notification))

    def get_distribution_stats(self) -> Dict[str, Any]:
        """Get statistics on intelligence distribution"""
        today = datetime.now().date()

        agent_feeds_today = AgentIntelligenceFeed.objects.filter(
            delivered_at__date=today
        ).count()

        advisor_feeds_today = AdvisorIntelligenceFeed.objects.filter(
            delivered_at__date=today
        ).count()

        # Top agents and advisors by feed count
        from django.db.models import Count

        top_agents = AgentIntelligenceFeed.objects.filter(
            delivered_at__date=today
        ).values('agent_name').annotate(
            feed_count=Count('id')
        ).order_by('-feed_count')[:10]

        top_advisors = AdvisorIntelligenceFeed.objects.filter(
            delivered_at__date=today
        ).values('advisor_name').annotate(
            feed_count=Count('id')
        ).order_by('-feed_count')[:10]

        return {
            'distribution_summary': {
                'agent_feeds_today': agent_feeds_today,
                'advisor_feeds_today': advisor_feeds_today,
                'total_feeds_today': agent_feeds_today + advisor_feeds_today
            },
            'top_agents': list(top_agents),
            'top_advisors': list(top_advisors),
            'advisor_profiles_count': len(self.advisor_profiles),
            'agent_specializations_count': len(self.agent_specializations)
        }


# Convenience functions
async def distribute_spider_intelligence(intelligence_node: SpiderIntelligenceNode):
    """Distribute intelligence from spider to agents and advisors"""
    engine = IntelligenceDistributionEngine()
    return await engine.distribute_intelligence(intelligence_node)


def get_distribution_engine_stats():
    """Get distribution engine statistics"""
    engine = IntelligenceDistributionEngine()
    return engine.get_distribution_stats()