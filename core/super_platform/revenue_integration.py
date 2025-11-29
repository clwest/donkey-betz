"""
Revenue Integration Service - The Money Pipeline
================================================

Session 264: Phase 4 - Revenue Pipeline

This service connects opportunities to actual revenue generation through:
1. Opportunity discovery from spider data
2. Intelligent scoring with spider context
3. Revenue tracking and attribution
4. Automation hooks for smart actions

The Revenue Pipeline:
    Spider Data → Opportunity → Score → Action → Revenue → Learning

Key Features:
- Automatic opportunity creation from spider data
- Spider-informed scoring (trends, market data, competition)
- Agent contribution tracking for revenue attribution
- Smart automation (auto-apply, smart pricing)
- Revenue predictions based on historical data
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field

from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class RevenueOpportunity:
    """A revenue opportunity with scoring and recommendations."""
    id: str
    title: str
    source: str
    potential_revenue: Decimal
    overall_score: int
    confidence: float

    # Scoring breakdown
    profit_potential: int = 50
    competition_level: int = 50
    effort_required: int = 50
    time_sensitivity: int = 50

    # Recommendations
    suggested_actions: List[str] = field(default_factory=list)
    suggested_agents: List[str] = field(default_factory=list)
    suggested_workflows: List[str] = field(default_factory=list)

    # Automation eligibility
    auto_apply_eligible: bool = False
    smart_pricing_suggestion: Optional[Decimal] = None

    # Spider context used
    spider_insights: Dict[str, Any] = field(default_factory=dict)

    # Revenue prediction
    predicted_revenue: Optional[Decimal] = None
    prediction_confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'potential_revenue': float(self.potential_revenue),
            'overall_score': self.overall_score,
            'confidence': self.confidence,
            'scores': {
                'profit_potential': self.profit_potential,
                'competition_level': self.competition_level,
                'effort_required': self.effort_required,
                'time_sensitivity': self.time_sensitivity,
            },
            'suggestions': {
                'actions': self.suggested_actions,
                'agents': self.suggested_agents,
                'workflows': self.suggested_workflows,
            },
            'automation': {
                'auto_apply_eligible': self.auto_apply_eligible,
                'smart_pricing_suggestion': float(self.smart_pricing_suggestion) if self.smart_pricing_suggestion else None,
            },
            'spider_insights': self.spider_insights,
            'prediction': {
                'predicted_revenue': float(self.predicted_revenue) if self.predicted_revenue else None,
                'confidence': self.prediction_confidence,
            },
        }


@dataclass
class RevenueSummary:
    """Summary of revenue metrics."""
    total_revenue: Decimal
    pending_revenue: Decimal
    completed_revenue: Decimal
    opportunity_count: int
    conversion_rate: float
    top_sources: List[Dict[str, Any]]
    top_agents: List[Dict[str, Any]]
    period_start: datetime
    period_end: datetime

    def to_dict(self) -> dict:
        return {
            'total_revenue': float(self.total_revenue),
            'pending_revenue': float(self.pending_revenue),
            'completed_revenue': float(self.completed_revenue),
            'opportunity_count': self.opportunity_count,
            'conversion_rate': self.conversion_rate,
            'top_sources': self.top_sources,
            'top_agents': self.top_agents,
            'period': {
                'start': self.period_start.isoformat(),
                'end': self.period_end.isoformat(),
            },
        }


class RevenueIntegrationService:
    """
    The revenue pipeline service for the Super Platform.

    This service unifies:
    - Opportunity discovery from spider data
    - Intelligent scoring with real market context
    - Revenue tracking and attribution
    - Automation capabilities
    - Revenue predictions
    """

    # Cache settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_PREFIX = 'revenue_integration:'

    # Scoring thresholds
    HIGH_VALUE_THRESHOLD = 75
    AUTO_APPLY_THRESHOLD = 80

    def __init__(self, user=None):
        """Initialize the revenue integration service."""
        self.user = user
        self._spider_service = None
        self._agent_context_service = None
        self._scoring_agent = None

    # ==================== Lazy Loading ====================

    @property
    def spider_service(self):
        """Lazy load SpiderIntelligenceService."""
        if self._spider_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._spider_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
        return self._spider_service

    @property
    def agent_context_service(self):
        """Lazy load AgentContextService."""
        if self._agent_context_service is None:
            try:
                from .agent_context_service import get_agent_context_service
                self._agent_context_service = get_agent_context_service()
            except ImportError:
                logger.warning("AgentContextService not available")
        return self._agent_context_service

    @property
    def scoring_agent(self):
        """Lazy load OpportunityScoringAgent."""
        if self._scoring_agent is None:
            try:
                from agents.opportunity_scoring_agent import OpportunityScoringAgent
                self._scoring_agent = OpportunityScoringAgent()
            except ImportError:
                logger.warning("OpportunityScoringAgent not available")
        return self._scoring_agent

    # ==================== Opportunity Discovery ====================

    def discover_opportunities(
        self,
        hours: int = 24,
        min_score: int = 50,
        limit: int = 20
    ) -> List[RevenueOpportunity]:
        """
        Discover new opportunities from spider data.

        This method:
        1. Gets recent spider data
        2. Scores each item for opportunity potential
        3. Enriches with spider context (trends, market data)
        4. Returns ranked opportunities

        Args:
            hours: Look back period
            min_score: Minimum score threshold
            limit: Maximum opportunities to return

        Returns:
            List of RevenueOpportunity objects
        """
        logger.info(f"Discovering opportunities from last {hours} hours...")

        opportunities = []

        try:
            # Get spider context for opportunity scoring
            spider_context = self._get_spider_context_for_opportunities()

            # Score recent spider data
            if self.scoring_agent:
                scored = self.scoring_agent.score_spider_data(
                    hours=hours,
                    limit=limit * 2,  # Get more to filter
                    user=self.user
                )

                for result in scored:
                    if result.success and result.overall_score >= min_score:
                        opportunity = self._create_revenue_opportunity(
                            result,
                            spider_context
                        )
                        opportunities.append(opportunity)

            # Get existing opportunities from database
            db_opportunities = self._get_db_opportunities(min_score, limit)

            # Merge and deduplicate
            seen_ids = set(o.id for o in opportunities)
            for db_opp in db_opportunities:
                if db_opp.id not in seen_ids:
                    opportunities.append(db_opp)

            # Sort by score and limit
            opportunities.sort(key=lambda x: x.overall_score, reverse=True)
            opportunities = opportunities[:limit]

            logger.info(f"Discovered {len(opportunities)} opportunities")
            return opportunities

        except Exception as e:
            logger.error(f"Error discovering opportunities: {e}")
            return []

    def _get_spider_context_for_opportunities(self) -> Dict[str, Any]:
        """Get spider context relevant to opportunity scoring."""
        context = {
            'trends': [],
            'market_data': {},
            'job_market': {},
            'hot_skills': [],
        }

        try:
            if self.spider_service:
                # Get trending topics
                trends = self.spider_service.get_trending_topics(hours=24)
                context['trends'] = trends[:10] if trends else []

                # Get market insights
                market = self.spider_service.get_market_insights()
                context['market_data'] = market or {}

                # Get job market data
                jobs = self.spider_service.get_job_market_summary()
                context['job_market'] = jobs or {}

                # Extract hot skills from trends
                context['hot_skills'] = self._extract_hot_skills(trends)

        except Exception as e:
            logger.warning(f"Could not get spider context: {e}")

        return context

    def _extract_hot_skills(self, trends: List[Dict]) -> List[str]:
        """Extract hot skills from trending topics."""
        skill_keywords = [
            'python', 'javascript', 'react', 'node', 'typescript',
            'ai', 'ml', 'machine learning', 'gpt', 'llm',
            'design', 'figma', 'ui', 'ux',
            'video', 'animation', 'motion',
            'writing', 'content', 'seo',
        ]

        hot_skills = []
        trend_text = ' '.join(str(t).lower() for t in trends)

        for skill in skill_keywords:
            if skill in trend_text:
                hot_skills.append(skill)

        return hot_skills[:10]

    def _create_revenue_opportunity(
        self,
        scoring_result,
        spider_context: Dict[str, Any]
    ) -> RevenueOpportunity:
        """Create a RevenueOpportunity from a scoring result."""
        # Determine automation eligibility
        auto_apply = (
            scoring_result.overall_score >= self.AUTO_APPLY_THRESHOLD and
            scoring_result.confidence_level >= 80
        )

        # Calculate smart pricing if applicable
        smart_price = self._calculate_smart_pricing(
            scoring_result,
            spider_context
        )

        # Predict revenue
        predicted, confidence = self._predict_revenue(
            scoring_result,
            spider_context
        )

        return RevenueOpportunity(
            id=scoring_result.opportunity_id or 'pending',
            title=f"Opportunity: {scoring_result.keywords[0] if scoring_result.keywords else 'General'}",
            source='spider_data',
            potential_revenue=scoring_result.estimated_revenue,
            overall_score=scoring_result.overall_score,
            confidence=scoring_result.confidence_level / 100,
            profit_potential=scoring_result.profit_potential,
            competition_level=scoring_result.competition_level,
            effort_required=scoring_result.effort_required,
            time_sensitivity=scoring_result.time_sensitivity,
            suggested_actions=self._suggest_actions(scoring_result),
            suggested_agents=self._suggest_agents(scoring_result),
            suggested_workflows=scoring_result.suggested_workflows,
            auto_apply_eligible=auto_apply,
            smart_pricing_suggestion=smart_price,
            spider_insights={
                'trends_matched': len([
                    t for t in spider_context.get('trends', [])
                    if any(kw in str(t).lower() for kw in scoring_result.keywords[:3])
                ]),
                'hot_skills_matched': [
                    s for s in spider_context.get('hot_skills', [])
                    if s in ' '.join(scoring_result.keywords).lower()
                ],
                'market_timing': 'good' if scoring_result.time_sensitivity >= 70 else 'normal',
            },
            predicted_revenue=predicted,
            prediction_confidence=confidence,
        )

    def _get_db_opportunities(
        self,
        min_score: int,
        limit: int
    ) -> List[RevenueOpportunity]:
        """Get opportunities from the database."""
        opportunities = []

        try:
            from core.models_unified_system import Opportunity

            queryset = Opportunity.objects.filter(
                status__in=['active', 'pending'],
            )

            if self.user:
                queryset = queryset.filter(user=self.user)

            # Use match_score as a fallback for overall_score
            queryset = queryset.order_by('-match_score', '-created_at')[:limit]

            for opp in queryset:
                # Get overall_score if available, fallback to match_score
                score = getattr(opp, 'overall_score', opp.match_score) or opp.match_score

                if score >= min_score:
                    opportunities.append(RevenueOpportunity(
                        id=str(opp.id),
                        title=opp.title,
                        source=opp.source,
                        potential_revenue=opp.potential_revenue,
                        overall_score=score,
                        confidence=0.7,  # Default confidence for DB opportunities
                        suggested_actions=['Review', 'Apply', 'Track'],
                        suggested_agents=['OpportunityScoringAgent'],
                    ))

        except Exception as e:
            logger.warning(f"Could not get DB opportunities: {e}")

        return opportunities

    def _calculate_smart_pricing(
        self,
        scoring_result,
        spider_context: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Calculate smart pricing based on market data."""
        base_price = scoring_result.estimated_revenue

        if not base_price or base_price <= 0:
            return None

        # Adjust based on market conditions
        multiplier = 1.0

        # High demand = higher price
        if scoring_result.time_sensitivity >= 80:
            multiplier += 0.15

        # Low competition = higher price
        if scoring_result.competition_level <= 30:
            multiplier += 0.10

        # Match hot skills = premium pricing
        hot_skills = spider_context.get('hot_skills', [])
        if hot_skills:
            skill_match = sum(
                1 for skill in hot_skills
                if skill in ' '.join(scoring_result.keywords).lower()
            )
            if skill_match >= 2:
                multiplier += 0.20

        return Decimal(str(float(base_price) * multiplier)).quantize(Decimal('0.01'))

    def _predict_revenue(
        self,
        scoring_result,
        spider_context: Dict[str, Any]
    ) -> Tuple[Optional[Decimal], float]:
        """Predict actual revenue based on historical data and context."""
        base_revenue = scoring_result.estimated_revenue

        if not base_revenue or base_revenue <= 0:
            return None, 0.0

        # Simple prediction model based on score
        score = scoring_result.overall_score / 100
        conversion_likelihood = 0.1 + (score * 0.6)  # 10% to 70% conversion

        # Adjust for competition
        competition_factor = 1 - (scoring_result.competition_level / 200)  # 0.5 to 1.0

        predicted = Decimal(str(
            float(base_revenue) * conversion_likelihood * competition_factor
        )).quantize(Decimal('0.01'))

        confidence = min(0.9, score * competition_factor)

        return predicted, confidence

    def _suggest_actions(self, scoring_result) -> List[str]:
        """Suggest actions based on opportunity characteristics."""
        actions = []

        if scoring_result.overall_score >= self.HIGH_VALUE_THRESHOLD:
            actions.append("🔥 High Priority - Act Now")

        if scoring_result.time_sensitivity >= 80:
            actions.append("⏰ Time Sensitive - Apply Immediately")

        if scoring_result.competition_level <= 30:
            actions.append("💎 Low Competition - Great Opportunity")

        if scoring_result.profit_potential >= 80:
            actions.append("💰 High Revenue Potential")

        if not actions:
            actions = ["Review Details", "Evaluate Fit", "Consider Applying"]

        return actions[:4]

    def _suggest_agents(self, scoring_result) -> List[str]:
        """Suggest agents based on opportunity type."""
        agents = ['OpportunityScoringAgent']

        content_types = scoring_result.suggested_content_types or []

        if any(ct in content_types for ct in ['logo', 'brand_kit', 'design']):
            agents.append('ImageAgent')
            agents.append('BrandIdentityAgent')

        if any(ct in content_types for ct in ['video', 'thumbnail']):
            agents.append('VideoAgent')

        if any(ct in content_types for ct in ['content', 'social_media']):
            agents.append('ContentStrategyAgent')
            agents.append('SocialMediaAgent')

        return agents[:5]

    # ==================== Revenue Tracking ====================

    def get_revenue_summary(
        self,
        days: int = 30
    ) -> RevenueSummary:
        """
        Get revenue summary for the specified period.

        Args:
            days: Number of days to look back

        Returns:
            RevenueSummary with metrics
        """
        try:
            from core.models_unified_system import Revenue, Opportunity
            from django.db.models import Sum, Count, Avg

            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)

            # Base queryset
            queryset = Revenue.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
            )

            if self.user:
                queryset = queryset.filter(user=self.user)

            # Calculate totals
            totals = queryset.aggregate(
                total=Sum('amount'),
                pending=Sum('amount', filter=models.Q(status='pending')),
                completed=Sum('amount', filter=models.Q(status='completed')),
            )

            total_revenue = totals['total'] or Decimal('0.00')
            pending_revenue = totals['pending'] or Decimal('0.00')
            completed_revenue = totals['completed'] or Decimal('0.00')

            # Get opportunity count and conversion
            opp_queryset = Opportunity.objects.filter(
                created_at__gte=start_date,
            )
            if self.user:
                opp_queryset = opp_queryset.filter(user=self.user)

            total_opps = opp_queryset.count()
            accepted_opps = opp_queryset.filter(status='accepted').count()
            conversion_rate = (accepted_opps / total_opps * 100) if total_opps > 0 else 0

            # Top sources
            top_sources = list(queryset.values('source_type').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')[:5])

            # Top agents
            top_agents = list(queryset.exclude(agent__isnull=True).values(
                'agent__name'
            ).annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')[:5])

            return RevenueSummary(
                total_revenue=total_revenue,
                pending_revenue=pending_revenue,
                completed_revenue=completed_revenue,
                opportunity_count=total_opps,
                conversion_rate=conversion_rate,
                top_sources=top_sources,
                top_agents=[
                    {'agent': a['agent__name'], 'total': a['total'], 'count': a['count']}
                    for a in top_agents
                ],
                period_start=start_date,
                period_end=end_date,
            )

        except Exception as e:
            logger.error(f"Error getting revenue summary: {e}")
            return RevenueSummary(
                total_revenue=Decimal('0.00'),
                pending_revenue=Decimal('0.00'),
                completed_revenue=Decimal('0.00'),
                opportunity_count=0,
                conversion_rate=0,
                top_sources=[],
                top_agents=[],
                period_start=timezone.now() - timedelta(days=days),
                period_end=timezone.now(),
            )

    def track_revenue(
        self,
        opportunity_id: str,
        amount: Decimal,
        source_type: str = 'opportunity',
        agent_name: Optional[str] = None,
        description: str = '',
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Track revenue from an opportunity or other source.

        Args:
            opportunity_id: ID of the source opportunity
            amount: Revenue amount
            source_type: Type of revenue source
            agent_name: Name of agent that contributed
            description: Description of the revenue
            metadata: Additional metadata

        Returns:
            Revenue record ID or None if failed
        """
        try:
            from core.models_unified_system import Revenue, Agent

            agent = None
            if agent_name:
                agent = Agent.objects.filter(name=agent_name).first()

            revenue = Revenue.objects.create(
                user=self.user,
                source_type=source_type,
                source_id=opportunity_id,
                agent=agent,
                amount=amount,
                currency='USD',
                status='pending',
                description=description or f"Revenue from {source_type}",
                metadata=metadata or {},
            )

            logger.info(f"Tracked revenue: ${amount} from {source_type}")
            return str(revenue.id)

        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
            return None

    def update_revenue_status(
        self,
        revenue_id: str,
        status: str,
        paid_date: Optional[datetime] = None
    ) -> bool:
        """Update revenue status (pending → completed)."""
        try:
            from core.models_unified_system import Revenue

            revenue = Revenue.objects.get(id=revenue_id)
            revenue.status = status

            if status == 'completed':
                revenue.earned_at = paid_date or timezone.now()

            if paid_date:
                revenue.paid_at = paid_date

            revenue.save()

            # Update agent metrics if applicable
            if revenue.agent:
                revenue.agent.total_revenue_generated += revenue.amount
                revenue.agent.save()

            logger.info(f"Updated revenue {revenue_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Error updating revenue status: {e}")
            return False

    # ==================== Automation Hooks ====================

    def get_auto_apply_opportunities(self) -> List[RevenueOpportunity]:
        """Get opportunities eligible for auto-apply."""
        all_opportunities = self.discover_opportunities(
            hours=48,
            min_score=self.AUTO_APPLY_THRESHOLD,
            limit=10
        )

        return [o for o in all_opportunities if o.auto_apply_eligible]

    def execute_auto_apply(
        self,
        opportunity: RevenueOpportunity
    ) -> Dict[str, Any]:
        """
        Execute auto-apply for an opportunity.

        This is a placeholder for the actual auto-apply logic which would:
        1. Generate a proposal using agents
        2. Submit to the platform API
        3. Track the submission

        Args:
            opportunity: The opportunity to apply to

        Returns:
            Result dictionary with status and details
        """
        if not opportunity.auto_apply_eligible:
            return {
                'success': False,
                'error': 'Opportunity not eligible for auto-apply',
            }

        # Log the auto-apply attempt
        logger.info(f"Auto-applying to opportunity: {opportunity.title}")

        # For now, return a mock result
        # In production, this would integrate with platform APIs
        return {
            'success': True,
            'opportunity_id': opportunity.id,
            'action': 'auto_apply',
            'status': 'pending_submission',
            'suggested_bid': float(opportunity.smart_pricing_suggestion) if opportunity.smart_pricing_suggestion else None,
            'agents_used': opportunity.suggested_agents,
            'message': f"Prepared auto-apply for: {opportunity.title}",
        }

    # ==================== Revenue Predictions ====================

    def get_revenue_forecast(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get revenue forecast based on current opportunities.

        Args:
            days: Forecast period in days

        Returns:
            Forecast with predictions and confidence
        """
        opportunities = self.discover_opportunities(hours=168, limit=50)  # Last week

        # Calculate predicted revenue
        total_predicted = Decimal('0.00')
        high_confidence = Decimal('0.00')
        low_confidence = Decimal('0.00')

        for opp in opportunities:
            if opp.predicted_revenue:
                total_predicted += opp.predicted_revenue

                if opp.prediction_confidence >= 0.7:
                    high_confidence += opp.predicted_revenue
                else:
                    low_confidence += opp.predicted_revenue

        # Get historical comparison
        summary = self.get_revenue_summary(days=days)
        historical_avg = summary.total_revenue / (days or 1) * days

        return {
            'forecast_period_days': days,
            'predicted_revenue': float(total_predicted),
            'high_confidence_revenue': float(high_confidence),
            'low_confidence_revenue': float(low_confidence),
            'historical_comparison': {
                'previous_period': float(summary.total_revenue),
                'daily_average': float(summary.total_revenue / days) if days > 0 else 0,
            },
            'opportunity_count': len(opportunities),
            'high_value_opportunities': len([
                o for o in opportunities
                if o.overall_score >= self.HIGH_VALUE_THRESHOLD
            ]),
            'generated_at': timezone.now().isoformat(),
        }

    # ==================== Agent Attribution ====================

    def get_agent_revenue_attribution(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get revenue attribution by agent.

        Shows which agents contributed to revenue generation.
        """
        try:
            from core.models_unified_system import Revenue, Agent
            from django.db.models import Sum, Count

            cutoff = timezone.now() - timedelta(days=days)

            # Get all agents with revenue
            agents = Agent.objects.filter(
                revenue_set__created_at__gte=cutoff
            ).annotate(
                period_revenue=Sum('revenue_set__amount'),
                revenue_count=Count('revenue_set')
            ).order_by('-period_revenue')[:10]

            return [
                {
                    'agent_name': agent.name,
                    'agent_type': agent.agent_type,
                    'period_revenue': float(agent.period_revenue or 0),
                    'total_revenue': float(agent.total_revenue_generated),
                    'revenue_count': agent.revenue_count,
                    'effectiveness_score': agent.effectiveness_score,
                }
                for agent in agents
            ]

        except Exception as e:
            logger.error(f"Error getting agent attribution: {e}")
            return []

    # ==================== Integration with Coordinator ====================

    def get_prompt_context(self) -> str:
        """
        Get revenue context for prompt injection into coordinator.

        This provides the coordinator with current revenue intelligence.
        """
        try:
            summary = self.get_revenue_summary(days=7)
            opportunities = self.discover_opportunities(limit=5)

            parts = ["\n## Revenue Intelligence\n"]

            # Summary
            parts.append(f"**Last 7 Days:** ${summary.total_revenue:.2f} revenue")
            parts.append(f"**Pending:** ${summary.pending_revenue:.2f}")
            parts.append(f"**Conversion Rate:** {summary.conversion_rate:.1f}%")

            # Top opportunities
            if opportunities:
                parts.append("\n**Top Opportunities:**")
                for opp in opportunities[:3]:
                    parts.append(
                        f"- {opp.title[:50]} (Score: {opp.overall_score}, "
                        f"Est: ${opp.potential_revenue})"
                    )

            parts.append("")
            return "\n".join(parts)

        except Exception as e:
            logger.warning(f"Could not get revenue context: {e}")
            return ""


# Import models for Django queries (at module level to avoid circular imports)
from django.db import models


# Singleton instance
_revenue_integration_service = None


def get_revenue_integration_service(user=None) -> RevenueIntegrationService:
    """Get the RevenueIntegrationService instance."""
    global _revenue_integration_service
    if _revenue_integration_service is None or user is not None:
        _revenue_integration_service = RevenueIntegrationService(user)
    return _revenue_integration_service
