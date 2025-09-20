"""
Advisor Spider Data Processor - Legendary Expert Intelligence Processing
=========================================================================

This module provides specialized data processors for legendary advisors,
each with their unique investment philosophies, analytical frameworks,
and decision-making processes. The processors transform raw spider intelligence
into advisor-specific insights and recommendations.

Features:
- Personality-specific data processing for each legendary advisor
- Investment philosophy-based filtering and analysis
- Specialized analytical frameworks (Value, Growth, Macro, etc.)
- Real-time insight generation and recommendations
- Performance tracking and optimization
"""

import asyncio
import json
import logging
import redis
from redis import asyncio as aioredis
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from abc import ABC, abstractmethod
from enum import Enum
import re
import uuid

from .agent_data_receiver import AgentSpiderDataReceiver, IntelligenceData, ProcessingMetrics

logger = logging.getLogger(__name__)


class InvestmentPhilosophy(Enum):
    """Investment philosophies of legendary advisors"""
    VALUE_INVESTING = "value_investing"        # Buffett, Graham, Munger
    GROWTH_INVESTING = "growth_investing"      # Cathie Wood, Peter Thiel
    MACRO_INVESTING = "macro_investing"        # Ray Dalio, George Soros
    MOMENTUM_TRADING = "momentum_trading"      # Paul Tudor Jones
    CONTRARIAN_INVESTING = "contrarian"       # Howard Marks
    QUANTITATIVE = "quantitative"             # Jim Simons
    VENTURE_CAPITAL = "venture_capital"       # Peter Thiel, Reid Hoffman


class AnalyticalFramework(Enum):
    """Analytical frameworks used by advisors"""
    DISCOUNTED_CASH_FLOW = "dcf"
    ECONOMIC_MOATS = "moats"
    DISRUPTIVE_INNOVATION = "disruption"
    MACRO_ECONOMIC_CYCLES = "macro_cycles"
    TECHNICAL_ANALYSIS = "technical"
    SENTIMENT_ANALYSIS = "sentiment"
    FUNDAMENTAL_ANALYSIS = "fundamental"


@dataclass
class AdvisorInsight:
    """Structured insight from an advisor"""
    advisor_id: str
    insight_id: str
    data_source_id: str
    insight_type: str
    confidence_level: float
    summary: str
    detailed_analysis: str
    investment_implications: List[str]
    risk_assessment: str
    time_horizon: str
    related_securities: List[str]
    action_items: List[str]
    timestamp: datetime
    expiry: Optional[datetime] = None


@dataclass
class AdvisorRecommendation:
    """Investment recommendation from an advisor"""
    advisor_id: str
    recommendation_id: str
    security_symbol: str
    recommendation_type: str  # "BUY", "SELL", "HOLD", "WATCH"
    confidence_score: float
    target_price: Optional[float]
    time_horizon: str
    reasoning: str
    supporting_data: List[str]
    risk_factors: List[str]
    timestamp: datetime


class BaseAdvisorDataProcessor(AgentSpiderDataReceiver):
    """
    Base class for advisor-specific data processors.

    Extends the agent data receiver with advisor-specific functionality
    for generating insights and investment recommendations.
    """

    def __init__(self, advisor_id: str, philosophy: InvestmentPhilosophy, frameworks: List[AnalyticalFramework], redis_config: Dict[str, Any] = None):
        super().__init__(advisor_id, redis_config)

        self.philosophy = philosophy
        self.frameworks = frameworks

        # Advisor-specific tracking
        self.generated_insights: Dict[str, AdvisorInsight] = {}
        self.generated_recommendations: Dict[str, AdvisorRecommendation] = {}
        self.insight_history: List[AdvisorInsight] = []

        # Performance metrics
        self.insight_accuracy_rate = 0.0
        self.recommendation_success_rate = 0.0

    @abstractmethod
    async def generate_advisor_insight(self, data: IntelligenceData) -> Optional[AdvisorInsight]:
        """Generate advisor-specific insight from intelligence data"""
        pass

    @abstractmethod
    async def evaluate_investment_opportunity(self, data: IntelligenceData) -> Optional[AdvisorRecommendation]:
        """Evaluate investment opportunity based on advisor's philosophy"""
        pass

    async def process_intelligence_data(self, data: IntelligenceData) -> Dict[str, Any]:
        """Process intelligence data with advisor-specific analysis"""
        try:
            result = {
                'advisor_id': self.advisor_id,
                'data_id': data.id,
                'philosophy': self.philosophy.value,
                'processing_timestamp': datetime.now(timezone.utc).isoformat(),
                'insights': [],
                'recommendations': [],
                'analysis_summary': {}
            }

            # Generate insights
            insight = await self.generate_advisor_insight(data)
            if insight:
                self.generated_insights[insight.insight_id] = insight
                result['insights'].append(insight.__dict__)

            # Evaluate for investment opportunities
            recommendation = await self.evaluate_investment_opportunity(data)
            if recommendation:
                self.generated_recommendations[recommendation.recommendation_id] = recommendation
                result['recommendations'].append(recommendation.__dict__)

            # Store advisor-specific analysis
            await self._store_advisor_analysis(result)

            return result

        except Exception as e:
            self.logger.error(f"Error in advisor data processing: {e}")
            return {'error': str(e)}

    async def _store_advisor_analysis(self, analysis: Dict[str, Any]):
        """Store advisor analysis in Redis"""
        try:
            analysis_key = f"advisor_analysis:{self.advisor_id}:{analysis['data_id']}"
            await self.redis_async.setex(
                analysis_key,
                7200,  # 2 hour expiry
                json.dumps(analysis)
            )
        except Exception as e:
            self.logger.error(f"Failed to store advisor analysis: {e}")


class WarrenBuffettProcessor(BaseAdvisorDataProcessor):
    """Warren Buffett's value investing data processor"""

    def __init__(self, redis_config: Dict[str, Any] = None):
        super().__init__(
            advisor_id="warren_buffett",
            philosophy=InvestmentPhilosophy.VALUE_INVESTING,
            frameworks=[AnalyticalFramework.FUNDAMENTAL_ANALYSIS, AnalyticalFramework.ECONOMIC_MOATS],
            redis_config=redis_config
        )

    async def _initialize_agent_subscriptions(self):
        """Initialize Warren Buffett's specialized subscriptions"""
        from .agent_data_receiver import AgentDataSubscription

        # Focus on fundamental data, earnings, and quality companies
        buffett_subscription = AgentDataSubscription(
            agent_id=self.agent_id,
            channel_pattern="intelligence:advisor:warren_buffett",
            data_types=["sec_filing", "earnings_report", "financial_news", "annual_report"],
            keywords=["earnings", "revenue", "profit", "moat", "competitive advantage", "management", "berkshire"],
            quality_threshold=0.9,  # Very high quality threshold
            max_queue_size=500      # Conservative queue size
        )

        self.add_subscription(buffett_subscription)

    async def generate_advisor_insight(self, data: IntelligenceData) -> Optional[AdvisorInsight]:
        """Generate Warren Buffett-style value investing insights"""
        try:
            content = data.content
            content_text = json.dumps(content).lower()

            # Look for value investing signals
            value_indicators = []
            competitive_advantages = []
            management_quality = []

            # Economic moats detection
            if any(term in content_text for term in ['competitive advantage', 'moat', 'barrier to entry', 'brand power']):
                competitive_advantages.append("Strong competitive positioning detected")

            # Quality earnings detection
            if any(term in content_text for term in ['consistent earnings', 'predictable', 'stable revenue']):
                value_indicators.append("Consistent earning patterns identified")

            # Management quality signals
            if any(term in content_text for term in ['shareholder friendly', 'capital allocation', 'buyback']):
                management_quality.append("Positive management indicators")

            # Only generate insight if we have strong value signals
            if len(value_indicators) + len(competitive_advantages) + len(management_quality) >= 2:
                insight = AdvisorInsight(
                    advisor_id=self.advisor_id,
                    insight_id=f"buffett_{data.id}_{int(datetime.now().timestamp())}",
                    data_source_id=data.id,
                    insight_type="value_investment_analysis",
                    confidence_level=min(0.95, data.quality_score + 0.1),
                    summary="Value investment opportunity identified based on fundamental strengths",
                    detailed_analysis=f"Analysis reveals: {'; '.join(value_indicators + competitive_advantages + management_quality)}",
                    investment_implications=[
                        "Potential long-term value creation",
                        "Strong competitive positioning",
                        "Quality management team"
                    ],
                    risk_assessment="Low to moderate risk given fundamental strength",
                    time_horizon="5-10 years",
                    related_securities=[],  # Would extract from data
                    action_items=[
                        "Conduct deeper fundamental analysis",
                        "Assess valuation metrics",
                        "Review management track record"
                    ],
                    timestamp=datetime.now(timezone.utc),
                    expiry=datetime.now(timezone.utc) + timedelta(days=30)
                )

                return insight

        except Exception as e:
            self.logger.error(f"Error generating Buffett insight: {e}")

        return None

    async def evaluate_investment_opportunity(self, data: IntelligenceData) -> Optional[AdvisorRecommendation]:
        """Evaluate using Buffett's value investing criteria"""
        try:
            content_text = json.dumps(data.content).lower()

            # Look for strong buy signals
            buy_signals = 0

            if 'undervalued' in content_text:
                buy_signals += 1
            if any(term in content_text for term in ['strong fundamentals', 'competitive moat']):
                buy_signals += 1
            if 'dividend' in content_text and 'growing' in content_text:
                buy_signals += 1
            if data.quality_score > 0.9:
                buy_signals += 1

            # Generate recommendation if we have enough signals
            if buy_signals >= 2:
                recommendation = AdvisorRecommendation(
                    advisor_id=self.advisor_id,
                    recommendation_id=f"buffett_rec_{data.id}_{int(datetime.now().timestamp())}",
                    security_symbol="",  # Would extract from data
                    recommendation_type="WATCH" if buy_signals == 2 else "BUY",
                    confidence_score=min(0.95, buy_signals * 0.2 + data.quality_score * 0.5),
                    target_price=None,  # Buffett focuses less on price targets
                    time_horizon="Long-term (5+ years)",
                    reasoning="Strong fundamental indicators align with value investing principles",
                    supporting_data=[data.id],
                    risk_factors=["Market volatility", "Economic cycle risk"],
                    timestamp=datetime.now(timezone.utc)
                )

                return recommendation

        except Exception as e:
            self.logger.error(f"Error evaluating investment opportunity: {e}")

        return None


class CathieWoodProcessor(BaseAdvisorDataProcessor):
    """Cathie Wood's disruptive innovation data processor"""

    def __init__(self, redis_config: Dict[str, Any] = None):
        super().__init__(
            advisor_id="cathie_wood",
            philosophy=InvestmentPhilosophy.GROWTH_INVESTING,
            frameworks=[AnalyticalFramework.DISRUPTIVE_INNOVATION],
            redis_config=redis_config
        )

    async def _initialize_agent_subscriptions(self):
        """Initialize Cathie Wood's innovation-focused subscriptions"""
        from .agent_data_receiver import AgentDataSubscription

        innovation_subscription = AgentDataSubscription(
            agent_id=self.advisor_id,
            channel_pattern="intelligence:advisor:cathie_wood",
            data_types=["research_papers", "patent_data", "tech_news", "innovation_intelligence"],
            keywords=["innovation", "disruptive", "ai", "genomics", "blockchain", "automation", "ark"],
            quality_threshold=0.85,
            max_queue_size=1000
        )

        self.add_subscription(innovation_subscription)

    async def generate_advisor_insight(self, data: IntelligenceData) -> Optional[AdvisorInsight]:
        """Generate Cathie Wood-style innovation insights"""
        try:
            content_text = json.dumps(data.content).lower()

            # Innovation themes Cathie Wood focuses on
            innovation_themes = []

            if any(term in content_text for term in ['artificial intelligence', 'ai', 'machine learning']):
                innovation_themes.append("Artificial Intelligence")

            if any(term in content_text for term in ['genomics', 'gene therapy', 'crispr', 'dna']):
                innovation_themes.append("Genomics Revolution")

            if any(term in content_text for term in ['blockchain', 'cryptocurrency', 'bitcoin']):
                innovation_themes.append("Digital Assets")

            if any(term in content_text for term in ['autonomous', 'self-driving', 'robotics']):
                innovation_themes.append("Autonomous Technology")

            if any(term in content_text for term in ['space', 'satellite', 'aerospace']):
                innovation_themes.append("Space Exploration")

            # Generate insight if we detect strong innovation signals
            if innovation_themes and data.quality_score > 0.8:
                insight = AdvisorInsight(
                    advisor_id=self.advisor_id,
                    insight_id=f"cathie_{data.id}_{int(datetime.now().timestamp())}",
                    data_source_id=data.id,
                    insight_type="disruptive_innovation_analysis",
                    confidence_level=data.quality_score * 0.9,
                    summary=f"Disruptive innovation opportunity in {', '.join(innovation_themes)}",
                    detailed_analysis=f"Intelligence suggests significant innovation potential across {len(innovation_themes)} key themes",
                    investment_implications=[
                        "High growth potential through technological disruption",
                        "First-mover advantage opportunities",
                        "Scalable business model potential"
                    ],
                    risk_assessment="High risk but transformative potential",
                    time_horizon="3-7 years",
                    related_securities=[],
                    action_items=[
                        "Assess innovation pipeline depth",
                        "Evaluate market disruption potential",
                        "Monitor competitive landscape"
                    ],
                    timestamp=datetime.now(timezone.utc),
                    expiry=datetime.now(timezone.utc) + timedelta(days=60)
                )

                return insight

        except Exception as e:
            self.logger.error(f"Error generating Cathie Wood insight: {e}")

        return None

    async def evaluate_investment_opportunity(self, data: IntelligenceData) -> Optional[AdvisorRecommendation]:
        """Evaluate using innovation-focused criteria"""
        try:
            content_text = json.dumps(data.content).lower()

            innovation_score = 0

            # High-conviction innovation areas
            if any(term in content_text for term in ['breakthrough', 'revolutionary', 'first-of-its-kind']):
                innovation_score += 2

            if any(term in content_text for term in ['scalable', 'platform', 'ecosystem']):
                innovation_score += 1

            if 'disruption' in content_text or 'disruptive' in content_text:
                innovation_score += 2

            if data.quality_score > 0.85:
                innovation_score += 1

            if innovation_score >= 3:
                recommendation = AdvisorRecommendation(
                    advisor_id=self.advisor_id,
                    recommendation_id=f"cathie_rec_{data.id}_{int(datetime.now().timestamp())}",
                    security_symbol="",
                    recommendation_type="BUY" if innovation_score >= 4 else "WATCH",
                    confidence_score=min(0.9, innovation_score * 0.15 + data.quality_score * 0.4),
                    target_price=None,
                    time_horizon="Medium-term (3-5 years)",
                    reasoning="Strong innovation signals suggest disruptive potential",
                    supporting_data=[data.id],
                    risk_factors=["Technology risk", "Market adoption uncertainty", "Regulatory challenges"],
                    timestamp=datetime.now(timezone.utc)
                )

                return recommendation

        except Exception as e:
            self.logger.error(f"Error in Cathie Wood investment evaluation: {e}")

        return None


class RayDalioProcessor(BaseAdvisorDataProcessor):
    """Ray Dalio's macro-economic data processor"""

    def __init__(self, redis_config: Dict[str, Any] = None):
        super().__init__(
            advisor_id="ray_dalio",
            philosophy=InvestmentPhilosophy.MACRO_INVESTING,
            frameworks=[AnalyticalFramework.MACRO_ECONOMIC_CYCLES],
            redis_config=redis_config
        )

    async def _initialize_agent_subscriptions(self):
        """Initialize Ray Dalio's macro-focused subscriptions"""
        from .agent_data_receiver import AgentDataSubscription

        macro_subscription = AgentDataSubscription(
            agent_id=self.advisor_id,
            channel_pattern="intelligence:advisor:ray_dalio",
            data_types=["economic_data", "fed_news", "market_data", "geopolitical_news"],
            keywords=["fed", "interest rates", "inflation", "debt", "cycles", "macro", "economy"],
            quality_threshold=0.9,
            max_queue_size=800
        )

        self.add_subscription(macro_subscription)

    async def generate_advisor_insight(self, data: IntelligenceData) -> Optional[AdvisorInsight]:
        """Generate Ray Dalio-style macro insights"""
        try:
            content_text = json.dumps(data.content).lower()

            macro_signals = []

            # Economic cycle indicators
            if any(term in content_text for term in ['recession', 'expansion', 'cycle', 'downturn']):
                macro_signals.append("Economic cycle signals detected")

            # Debt and credit cycle
            if any(term in content_text for term in ['debt', 'credit', 'leverage', 'deleveraging']):
                macro_signals.append("Credit cycle dynamics identified")

            # Monetary policy
            if any(term in content_text for term in ['fed', 'federal reserve', 'interest rates', 'monetary policy']):
                macro_signals.append("Monetary policy implications noted")

            # Inflation signals
            if any(term in content_text for term in ['inflation', 'deflation', 'price pressure']):
                macro_signals.append("Inflation dynamics observed")

            if macro_signals and data.quality_score > 0.85:
                insight = AdvisorInsight(
                    advisor_id=self.advisor_id,
                    insight_id=f"dalio_{data.id}_{int(datetime.now().timestamp())}",
                    data_source_id=data.id,
                    insight_type="macro_economic_analysis",
                    confidence_level=data.quality_score * 0.95,
                    summary=f"Macro-economic signals: {', '.join(macro_signals)}",
                    detailed_analysis="Analysis suggests significant macro-economic developments with portfolio implications",
                    investment_implications=[
                        "Asset allocation adjustments recommended",
                        "Risk parity considerations",
                        "Currency and geographic diversification"
                    ],
                    risk_assessment="Macro risk assessment required",
                    time_horizon="6 months to 2 years",
                    related_securities=[],
                    action_items=[
                        "Review portfolio risk balance",
                        "Assess inflation protection",
                        "Monitor central bank communications"
                    ],
                    timestamp=datetime.now(timezone.utc),
                    expiry=datetime.now(timezone.utc) + timedelta(days=90)
                )

                return insight

        except Exception as e:
            self.logger.error(f"Error generating Dalio insight: {e}")

        return None

    async def evaluate_investment_opportunity(self, data: IntelligenceData) -> Optional[AdvisorRecommendation]:
        """Evaluate using macro-economic principles"""
        # Ray Dalio focuses more on portfolio construction than individual securities
        # This would typically result in asset class recommendations rather than specific stocks
        return None


class CryptoExpertProcessor(BaseAdvisorDataProcessor):
    """Crypto Expert specialized data processor"""

    def __init__(self, redis_config: Dict[str, Any] = None):
        super().__init__(
            advisor_id="crypto_expert",
            philosophy=InvestmentPhilosophy.GROWTH_INVESTING,
            frameworks=[AnalyticalFramework.TECHNICAL_ANALYSIS, AnalyticalFramework.SENTIMENT_ANALYSIS],
            redis_config=redis_config
        )

    async def _initialize_agent_subscriptions(self):
        """Initialize crypto expert subscriptions"""
        from .agent_data_receiver import AgentDataSubscription

        crypto_subscription = AgentDataSubscription(
            agent_id=self.advisor_id,
            channel_pattern="intelligence:advisor:crypto_expert",
            data_types=["crypto_market_data", "blockchain_news", "defi_data"],
            keywords=["bitcoin", "ethereum", "crypto", "blockchain", "defi", "nft"],
            quality_threshold=0.8,
            max_queue_size=1500
        )

        self.add_subscription(crypto_subscription)

    async def generate_advisor_insight(self, data: IntelligenceData) -> Optional[AdvisorInsight]:
        """Generate crypto-specific insights"""
        try:
            content_text = json.dumps(data.content).lower()

            crypto_signals = []

            if 'bitcoin' in content_text and any(term in content_text for term in ['adoption', 'institutional']):
                crypto_signals.append("Bitcoin institutional adoption signals")

            if 'ethereum' in content_text and any(term in content_text for term in ['upgrade', 'layer 2']):
                crypto_signals.append("Ethereum scaling developments")

            if 'defi' in content_text and 'tvl' in content_text:
                crypto_signals.append("DeFi growth indicators")

            if crypto_signals:
                insight = AdvisorInsight(
                    advisor_id=self.advisor_id,
                    insight_id=f"crypto_{data.id}_{int(datetime.now().timestamp())}",
                    data_source_id=data.id,
                    insight_type="crypto_market_analysis",
                    confidence_level=data.quality_score * 0.85,
                    summary=f"Crypto market developments: {', '.join(crypto_signals)}",
                    detailed_analysis="Significant developments in crypto ecosystem with investment implications",
                    investment_implications=[
                        "Crypto market positioning opportunities",
                        "Technology adoption acceleration",
                        "Regulatory clarity improvements"
                    ],
                    risk_assessment="High volatility with strong upside potential",
                    time_horizon="1-3 years",
                    related_securities=[],
                    action_items=[
                        "Monitor on-chain metrics",
                        "Assess regulatory developments",
                        "Evaluate ecosystem growth"
                    ],
                    timestamp=datetime.now(timezone.utc),
                    expiry=datetime.now(timezone.utc) + timedelta(days=14)
                )

                return insight

        except Exception as e:
            self.logger.error(f"Error generating crypto insight: {e}")

        return None

    async def evaluate_investment_opportunity(self, data: IntelligenceData) -> Optional[AdvisorRecommendation]:
        """Evaluate crypto investment opportunities"""
        try:
            content_text = json.dumps(data.content).lower()

            bullish_signals = 0

            if any(term in content_text for term in ['bullish', 'moon', 'breakout']):
                bullish_signals += 1

            if 'adoption' in content_text:
                bullish_signals += 1

            if data.quality_score > 0.8:
                bullish_signals += 1

            if bullish_signals >= 2:
                recommendation = AdvisorRecommendation(
                    advisor_id=self.advisor_id,
                    recommendation_id=f"crypto_rec_{data.id}_{int(datetime.now().timestamp())}",
                    security_symbol="",
                    recommendation_type="BUY" if bullish_signals >= 3 else "WATCH",
                    confidence_score=bullish_signals * 0.25,
                    target_price=None,
                    time_horizon="Short to medium-term",
                    reasoning="Strong crypto market signals detected",
                    supporting_data=[data.id],
                    risk_factors=["High volatility", "Regulatory uncertainty"],
                    timestamp=datetime.now(timezone.utc)
                )

                return recommendation

        except Exception as e:
            self.logger.error(f"Error in crypto investment evaluation: {e}")

        return None


# Factory function for creating advisor data processors
def create_advisor_data_processor(advisor_id: str, redis_config: Dict[str, Any] = None) -> BaseAdvisorDataProcessor:
    """Create appropriate advisor data processor based on advisor ID"""

    processor_mapping = {
        "warren_buffett": WarrenBuffettProcessor,
        "cathie_wood": CathieWoodProcessor,
        "ray_dalio": RayDalioProcessor,
        "crypto_expert": CryptoExpertProcessor
    }

    processor_class = processor_mapping.get(advisor_id)
    if processor_class:
        return processor_class(redis_config)
    else:
        # Default processor for other advisors
        class DefaultAdvisorProcessor(BaseAdvisorDataProcessor):
            def __init__(self, advisor_id: str, redis_config: Dict[str, Any] = None):
                super().__init__(
                    advisor_id=advisor_id,
                    philosophy=InvestmentPhilosophy.VALUE_INVESTING,
                    frameworks=[AnalyticalFramework.FUNDAMENTAL_ANALYSIS],
                    redis_config=redis_config
                )

            async def _initialize_agent_subscriptions(self):
                from .agent_data_receiver import AgentDataSubscription
                subscription = AgentDataSubscription(
                    agent_id=self.advisor_id,
                    channel_pattern=f"intelligence:advisor:{self.advisor_id}",
                    data_types=[],
                    keywords=[],
                    quality_threshold=0.8
                )
                self.add_subscription(subscription)

            async def generate_advisor_insight(self, data: IntelligenceData) -> Optional[AdvisorInsight]:
                return None

            async def evaluate_investment_opportunity(self, data: IntelligenceData) -> Optional[AdvisorRecommendation]:
                return None

        return DefaultAdvisorProcessor(advisor_id, redis_config)