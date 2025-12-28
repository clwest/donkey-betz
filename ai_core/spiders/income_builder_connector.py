"""
Income Builder Agent - Personalized Spider Data Connector
=========================================================

This module creates a specialized connection between the Income Builder agent
and spider networks, providing personalized income opportunity intelligence
streams with dividend, yield, and monetization-focused data processing.

Features:
- Personalized income opportunity detection
- Dividend-focused intelligence filtering
- Real-time monetization alerts
- Performance tracking for income strategies
- Integration with Income Builder agent workflows
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum

from .agent_data_receiver import AgentSpiderDataReceiver, IntelligenceData, AgentDataSubscription

logger = logging.getLogger(__name__)


class IncomeOpportunityType(Enum):
    """Types of income opportunities"""
    DIVIDEND_STOCK = "dividend_stock"
    REIT = "reit"
    BOND = "bond"
    CRYPTO_YIELD = "crypto_yield"
    BUSINESS_OPPORTUNITY = "business_opportunity"
    INVESTMENT_STRATEGY = "investment_strategy"
    SIDE_HUSTLE = "side_hustle"
    PASSIVE_INCOME = "passive_income"


class IncomeUrgency(Enum):
    """Urgency levels for income opportunities"""
    IMMEDIATE = 1     # Act within hours
    HIGH = 2          # Act within days
    MEDIUM = 3        # Act within weeks
    LOW = 4           # Monitor for months


@dataclass
class IncomeOpportunity:
    """Structured income opportunity from spider intelligence"""
    id: str
    opportunity_type: IncomeOpportunityType
    title: str
    description: str
    estimated_yield: Optional[float]
    risk_level: str
    time_horizon: str
    capital_required: Optional[float]
    urgency: IncomeUrgency
    supporting_data: List[str]
    action_steps: List[str]
    confidence_score: float
    spider_source: str
    timestamp: datetime
    expiry: Optional[datetime] = None


@dataclass
class IncomeBuilderMetrics:
    """Metrics specific to Income Builder intelligence processing"""
    opportunities_detected: int = 0
    high_yield_alerts: int = 0
    dividend_opportunities: int = 0
    business_opportunities: int = 0
    avg_opportunity_yield: float = 0.0
    successful_recommendations: int = 0
    total_value_identified: float = 0.0
    last_opportunity_time: Optional[datetime] = None


class IncomeBuilderSpiderConnector(AgentSpiderDataReceiver):
    """
    Specialized spider connector for the Income Builder agent.

    Provides personalized income opportunity intelligence with advanced
    filtering, analysis, and integration with income-building strategies.
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        super().__init__("income_builder_agent", redis_config)

        # Income Builder specific tracking
        self.income_opportunities: Dict[str, IncomeOpportunity] = {}
        self.income_metrics = IncomeBuilderMetrics()
        self.opportunity_history: List[IncomeOpportunity] = []

        # Income-focused configuration
        self.yield_threshold = 0.04  # 4% minimum yield
        self.risk_tolerance = "moderate"
        self.capital_range = (1000, 100000)  # $1K - $100K

        # Integration with Income Builder agent
        self.income_builder_agent = None

    async def _initialize_agent_subscriptions(self):
        """Initialize Income Builder specific subscriptions"""

        # Primary income opportunities subscription
        income_subscription = AgentDataSubscription(
            agent_id=self.agent_id,
            channel_pattern="intelligence:agent:income_builder_agent",
            data_types=[
                "dividend_data",
                "reit_analysis",
                "bond_opportunities",
                "crypto_yield",
                "financial_news",
                "earnings_report",
                "sec_filing"
            ],
            keywords=[
                "dividend", "yield", "income", "payout", "distribution",
                "passive income", "monthly income", "quarterly dividend",
                "reit", "bond", "treasury", "high yield", "dividend growth",
                "monetization", "revenue stream", "cash flow"
            ],
            quality_threshold=0.8,
            max_queue_size=2000,
            processing_timeout_seconds=300
        )

        self.add_subscription(income_subscription)

        # Secondary opportunities subscription (broader scope)
        opportunity_subscription = AgentDataSubscription(
            agent_id=self.agent_id,
            channel_pattern="intelligence:category:financial",
            data_types=[
                "investment_opportunity",
                "business_opportunity",
                "market_analysis"
            ],
            keywords=[
                "opportunity", "investment", "returns", "profit",
                "side hustle", "business idea", "investment strategy"
            ],
            quality_threshold=0.75,
            max_queue_size=1000
        )

        self.add_subscription(opportunity_subscription)

        # High-priority alerts subscription
        alert_subscription = AgentDataSubscription(
            agent_id=self.agent_id,
            channel_pattern="intelligence:alert:*",
            data_types=["high_priority_alert", "breaking_news"],
            keywords=["dividend announced", "yield increase", "special dividend"],
            quality_threshold=0.9,
            max_queue_size=100
        )

        self.add_subscription(alert_subscription)

    async def process_intelligence_data(self, data: IntelligenceData) -> Dict[str, Any]:
        """Process intelligence data for income opportunities"""
        try:
            result = {
                'agent_id': self.agent_id,
                'data_id': data.id,
                'processing_type': 'income_opportunity_analysis',
                'opportunities_found': [],
                'income_signals': [],
                'recommendations': [],
                'priority_level': 'normal',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            # Analyze for income opportunities
            opportunities = await self._detect_income_opportunities(data)
            if opportunities:
                for opportunity in opportunities:
                    self.income_opportunities[opportunity.id] = opportunity
                    result['opportunities_found'].append(opportunity.__dict__)

                    # Update metrics
                    self.income_metrics.opportunities_detected += 1
                    if opportunity.opportunity_type == IncomeOpportunityType.DIVIDEND_STOCK:
                        self.income_metrics.dividend_opportunities += 1
                    elif opportunity.opportunity_type == IncomeOpportunityType.BUSINESS_OPPORTUNITY:
                        self.income_metrics.business_opportunities += 1

                    if opportunity.urgency in [IncomeUrgency.IMMEDIATE, IncomeUrgency.HIGH]:
                        result['priority_level'] = 'high'
                        self.income_metrics.high_yield_alerts += 1

            # Extract income signals
            income_signals = await self._extract_income_signals(data)
            result['income_signals'] = income_signals

            # Generate recommendations
            recommendations = await self._generate_income_recommendations(data, opportunities)
            result['recommendations'] = recommendations

            # Integrate with Income Builder agent if available
            if self.income_builder_agent:
                await self._integrate_with_income_builder(opportunities, data)

            # Store processing result
            await self._store_income_analysis(result)

            return result

        except Exception as e:
            self.logger.error(f"Error processing income intelligence: {e}")
            return {'error': str(e)}

    async def _detect_income_opportunities(self, data: IntelligenceData) -> List[IncomeOpportunity]:
        """Detect specific income opportunities from intelligence data"""
        opportunities = []

        try:
            content = data.content
            content_text = json.dumps(content).lower()

            # Dividend opportunity detection
            if await self._is_dividend_opportunity(content_text, data):
                opportunity = await self._create_dividend_opportunity(data)
                if opportunity:
                    opportunities.append(opportunity)

            # REIT opportunity detection
            if await self._is_reit_opportunity(content_text, data):
                opportunity = await self._create_reit_opportunity(data)
                if opportunity:
                    opportunities.append(opportunity)

            # Crypto yield opportunity detection
            if await self._is_crypto_yield_opportunity(content_text, data):
                opportunity = await self._create_crypto_yield_opportunity(data)
                if opportunity:
                    opportunities.append(opportunity)

            # Business opportunity detection
            if await self._is_business_opportunity(content_text, data):
                opportunity = await self._create_business_opportunity(data)
                if opportunity:
                    opportunities.append(opportunity)

        except Exception as e:
            self.logger.error(f"Error detecting income opportunities: {e}")

        return opportunities

    async def _is_dividend_opportunity(self, content_text: str, data: IntelligenceData) -> bool:
        """Check if this is a dividend opportunity"""
        dividend_indicators = [
            'dividend increase', 'dividend growth', 'quarterly dividend',
            'special dividend', 'dividend announcement', 'yield increase',
            'payout ratio', 'dividend yield'
        ]

        return any(indicator in content_text for indicator in dividend_indicators)

    async def _create_dividend_opportunity(self, data: IntelligenceData) -> Optional[IncomeOpportunity]:
        """Create a dividend income opportunity"""
        try:
            content_text = json.dumps(data.content).lower()

            # Extract yield information (simplified)
            estimated_yield = None
            if 'yield' in content_text:
                # Would use regex to extract actual yield percentage
                estimated_yield = 0.05  # Default 5% for demo

            # Determine urgency
            urgency = IncomeUrgency.MEDIUM
            if 'announcement' in content_text or 'increase' in content_text:
                urgency = IncomeUrgency.HIGH

            opportunity = IncomeOpportunity(
                id=f"div_{data.id}_{int(datetime.now().timestamp())}",
                opportunity_type=IncomeOpportunityType.DIVIDEND_STOCK,
                title="Dividend Income Opportunity Detected",
                description=f"Intelligence suggests dividend opportunity from {data.spider_id}",
                estimated_yield=estimated_yield,
                risk_level="Low to Moderate",
                time_horizon="Long-term",
                capital_required=None,
                urgency=urgency,
                supporting_data=[data.id],
                action_steps=[
                    "Research dividend history",
                    "Analyze payout sustainability",
                    "Evaluate stock fundamentals",
                    "Consider position sizing"
                ],
                confidence_score=data.quality_score * 0.9,
                spider_source=data.spider_id,
                timestamp=datetime.now(timezone.utc),
                expiry=datetime.now(timezone.utc) + timedelta(days=7)
            )

            return opportunity

        except Exception as e:
            self.logger.error(f"Error creating dividend opportunity: {e}")
            return None

    async def _is_reit_opportunity(self, content_text: str, data: IntelligenceData) -> bool:
        """Check if this is a REIT opportunity"""
        reit_indicators = ['reit', 'real estate investment trust', 'property income', 'rental income']
        return any(indicator in content_text for indicator in reit_indicators)

    async def _create_reit_opportunity(self, data: IntelligenceData) -> Optional[IncomeOpportunity]:
        """Create a REIT income opportunity"""
        try:
            opportunity = IncomeOpportunity(
                id=f"reit_{data.id}_{int(datetime.now().timestamp())}",
                opportunity_type=IncomeOpportunityType.REIT,
                title="REIT Income Opportunity",
                description="Real estate investment trust opportunity detected",
                estimated_yield=0.06,  # REITs typically yield ~6%
                risk_level="Moderate",
                time_horizon="Medium to Long-term",
                capital_required=None,
                urgency=IncomeUrgency.MEDIUM,
                supporting_data=[data.id],
                action_steps=[
                    "Analyze REIT fundamentals",
                    "Review property portfolio",
                    "Assess dividend sustainability",
                    "Evaluate market sector"
                ],
                confidence_score=data.quality_score * 0.85,
                spider_source=data.spider_id,
                timestamp=datetime.now(timezone.utc),
                expiry=datetime.now(timezone.utc) + timedelta(days=14)
            )

            return opportunity

        except Exception as e:
            self.logger.error(f"Error creating REIT opportunity: {e}")
            return None

    async def _is_crypto_yield_opportunity(self, content_text: str, data: IntelligenceData) -> bool:
        """Check if this is a crypto yield opportunity"""
        crypto_yield_indicators = [
            'crypto yield', 'defi yield', 'staking rewards', 'liquidity mining',
            'yield farming', 'crypto interest', 'staking'
        ]
        return any(indicator in content_text for indicator in crypto_yield_indicators)

    async def _create_crypto_yield_opportunity(self, data: IntelligenceData) -> Optional[IncomeOpportunity]:
        """Create a crypto yield opportunity"""
        try:
            opportunity = IncomeOpportunity(
                id=f"crypto_{data.id}_{int(datetime.now().timestamp())}",
                opportunity_type=IncomeOpportunityType.CRYPTO_YIELD,
                title="Crypto Yield Opportunity",
                description="Cryptocurrency yield opportunity detected",
                estimated_yield=0.08,  # Crypto yields vary widely
                risk_level="High",
                time_horizon="Short to Medium-term",
                capital_required=None,
                urgency=IncomeUrgency.HIGH,  # Crypto opportunities change quickly
                supporting_data=[data.id],
                action_steps=[
                    "Assess protocol security",
                    "Understand yield mechanism",
                    "Evaluate impermanent loss risk",
                    "Consider portfolio allocation"
                ],
                confidence_score=data.quality_score * 0.8,
                spider_source=data.spider_id,
                timestamp=datetime.now(timezone.utc),
                expiry=datetime.now(timezone.utc) + timedelta(days=3)
            )

            return opportunity

        except Exception as e:
            self.logger.error(f"Error creating crypto yield opportunity: {e}")
            return None

    async def _is_business_opportunity(self, content_text: str, data: IntelligenceData) -> bool:
        """Check if this is a business opportunity"""
        business_indicators = [
            'business opportunity', 'side hustle', 'passive income',
            'revenue stream', 'monetization', 'business idea'
        ]
        return any(indicator in content_text for indicator in business_indicators)

    async def _create_business_opportunity(self, data: IntelligenceData) -> Optional[IncomeOpportunity]:
        """Create a business income opportunity"""
        try:
            opportunity = IncomeOpportunity(
                id=f"biz_{data.id}_{int(datetime.now().timestamp())}",
                opportunity_type=IncomeOpportunityType.BUSINESS_OPPORTUNITY,
                title="Business Income Opportunity",
                description="Business or entrepreneurial opportunity detected",
                estimated_yield=None,  # Varies widely
                risk_level="Variable",
                time_horizon="Variable",
                capital_required=None,
                urgency=IncomeUrgency.MEDIUM,
                supporting_data=[data.id],
                action_steps=[
                    "Validate market demand",
                    "Assess competition",
                    "Estimate startup costs",
                    "Develop business plan"
                ],
                confidence_score=data.quality_score * 0.75,
                spider_source=data.spider_id,
                timestamp=datetime.now(timezone.utc),
                expiry=datetime.now(timezone.utc) + timedelta(days=30)
            )

            return opportunity

        except Exception as e:
            self.logger.error(f"Error creating business opportunity: {e}")
            return None

    async def _extract_income_signals(self, data: IntelligenceData) -> List[str]:
        """Extract income-related signals from data"""
        signals = []

        try:
            content_text = json.dumps(data.content).lower()

            # Yield signals
            if 'high yield' in content_text:
                signals.append("High yield opportunity detected")

            if 'dividend growth' in content_text:
                signals.append("Dividend growth potential identified")

            if 'passive income' in content_text:
                signals.append("Passive income opportunity available")

            if 'cash flow' in content_text:
                signals.append("Cash flow opportunity noted")

            # Market timing signals
            if 'undervalued' in content_text:
                signals.append("Potential undervaluation for income investing")

            if 'interest rate' in content_text:
                signals.append("Interest rate environment consideration")

        except Exception as e:
            self.logger.error(f"Error extracting income signals: {e}")

        return signals

    async def _generate_income_recommendations(self, data: IntelligenceData, opportunities: List[IncomeOpportunity]) -> List[str]:
        """Generate actionable income recommendations"""
        recommendations = []

        try:
            if opportunities:
                # Urgent opportunities
                urgent_opportunities = [opp for opp in opportunities if opp.urgency == IncomeUrgency.IMMEDIATE]
                if urgent_opportunities:
                    recommendations.append("IMMEDIATE ACTION: High-priority income opportunities require immediate attention")

                # High-yield opportunities
                high_yield_opportunities = [opp for opp in opportunities if opp.estimated_yield and opp.estimated_yield > self.yield_threshold]
                if high_yield_opportunities:
                    recommendations.append(f"High-yield opportunities available (>{self.yield_threshold*100:.1f}% yield)")

                # Diversification recommendations
                opportunity_types = set(opp.opportunity_type for opp in opportunities)
                if len(opportunity_types) > 1:
                    recommendations.append("Diversification opportunity across multiple income types")

            # General recommendations based on data quality
            if data.quality_score > 0.9:
                recommendations.append("High-quality intelligence - consider deeper analysis")

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")

        return recommendations

    async def _integrate_with_income_builder(self, opportunities: List[IncomeOpportunity], data: IntelligenceData):
        """Integrate opportunities with Income Builder agent"""
        try:
            if opportunities:
                # Prepare data for Income Builder agent
                integration_data = {
                    'source': 'spider_intelligence',
                    'data_id': data.id,
                    'opportunities': [opp.__dict__ for opp in opportunities],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                # Store for Income Builder agent consumption
                await self.redis_async.setex(
                    f"income_builder:opportunities:{data.id}",
                    3600,  # 1 hour expiry
                    json.dumps(integration_data)
                )

                # Notify Income Builder agent
                await self.redis_async.publish(
                    'income_builder:notifications',
                    json.dumps({
                        'type': 'new_opportunities',
                        'count': len(opportunities),
                        'data_id': data.id,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                )

        except Exception as e:
            self.logger.error(f"Error integrating with Income Builder: {e}")

    async def _store_income_analysis(self, analysis: Dict[str, Any]):
        """Store income analysis results"""
        try:
            analysis_key = f"income_analysis:{self.agent_id}:{analysis['data_id']}"
            await self.redis_async.setex(
                analysis_key,
                7200,  # 2 hour expiry
                json.dumps(analysis)
            )

            # Also store in income opportunities index
            if analysis['opportunities_found']:
                opportunity_index_key = "income_opportunities:index"
                await self.redis_async.lpush(
                    opportunity_index_key,
                    json.dumps({
                        'analysis_id': analysis['data_id'],
                        'opportunities_count': len(analysis['opportunities_found']),
                        'timestamp': analysis['timestamp']
                    })
                )
                await self.redis_async.ltrim(opportunity_index_key, 0, 999)  # Keep last 1000

        except Exception as e:
            self.logger.error(f"Failed to store income analysis: {e}")

    def get_income_metrics(self) -> IncomeBuilderMetrics:
        """Get Income Builder specific metrics"""
        return self.income_metrics

    def get_recent_opportunities(self, limit: int = 50) -> List[IncomeOpportunity]:
        """Get recent income opportunities"""
        sorted_opportunities = sorted(
            self.income_opportunities.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )
        return sorted_opportunities[:limit]

    def get_high_priority_opportunities(self) -> List[IncomeOpportunity]:
        """Get high-priority income opportunities"""
        return [
            opp for opp in self.income_opportunities.values()
            if opp.urgency in [IncomeUrgency.IMMEDIATE, IncomeUrgency.HIGH]
            and (not opp.expiry or opp.expiry > datetime.now(timezone.utc))
        ]

    async def get_income_status(self) -> Dict[str, Any]:
        """Get comprehensive Income Builder connector status"""
        status = await super().get_status()

        # Add Income Builder specific data
        status.update({
            'income_metrics': {
                'opportunities_detected': self.income_metrics.opportunities_detected,
                'high_yield_alerts': self.income_metrics.high_yield_alerts,
                'dividend_opportunities': self.income_metrics.dividend_opportunities,
                'business_opportunities': self.income_metrics.business_opportunities,
                'avg_opportunity_yield': self.income_metrics.avg_opportunity_yield
            },
            'active_opportunities': len(self.income_opportunities),
            'high_priority_opportunities': len(self.get_high_priority_opportunities()),
            'yield_threshold': self.yield_threshold,
            'risk_tolerance': self.risk_tolerance
        })

        return status


# Factory function for Income Builder connector
def create_income_builder_connector(redis_config: Dict[str, Any] = None) -> IncomeBuilderSpiderConnector:
    """Create Income Builder spider connector"""
    return IncomeBuilderSpiderConnector(redis_config)