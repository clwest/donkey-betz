"""
Opportunity Scoring Agent - The Heart of the Opportunity Engine
================================================================

Session 223: Phase 1 of The Creative Intelligence Empire

This agent transforms raw spider data into scored, actionable opportunities
that feed into the content creation pipeline.

The Scoring Flow:
    SpiderData -> Analyze -> Score -> Suggest Content -> Create Opportunity

Scoring Factors:
    - Profit Potential (1-100): How much money could this make?
    - Competition Level (1-100): How saturated is this market?
    - Effort Required (1-100): How much work to capitalize on this?
    - Time Sensitivity (1-100): How urgent is this opportunity?

Example:
    agent = OpportunityScoringAgent()

    # Score all unprocessed spider data
    scored = agent.score_spider_data()

    # Score a specific trend
    opportunity = agent.analyze_trend("AI video generation tools trending")

    # Get top opportunities
    top = agent.get_top_opportunities(limit=10)
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class ScoringResult:
    """Result from opportunity scoring."""
    success: bool
    opportunity_id: Optional[str] = None

    # Scores
    profit_potential: int = 50
    competition_level: int = 50
    effort_required: int = 50
    time_sensitivity: int = 50
    overall_score: int = 50

    # Reasoning
    profit_reasoning: str = ""
    competition_reasoning: str = ""
    effort_reasoning: str = ""
    timing_reasoning: str = ""

    # Suggestions
    suggested_content_types: List[str] = field(default_factory=list)
    suggested_workflows: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    # Estimates
    estimated_revenue: Decimal = Decimal('0.00')
    estimated_cost: Decimal = Decimal('0.00')

    # Metadata
    confidence_level: int = 70
    data_sources: List[str] = field(default_factory=list)
    advisors_consulted: List[str] = field(default_factory=list)

    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'opportunity_id': self.opportunity_id,
            'scores': {
                'profit_potential': self.profit_potential,
                'competition_level': self.competition_level,
                'effort_required': self.effort_required,
                'time_sensitivity': self.time_sensitivity,
                'overall_score': self.overall_score,
            },
            'reasoning': {
                'profit': self.profit_reasoning,
                'competition': self.competition_reasoning,
                'effort': self.effort_reasoning,
                'timing': self.timing_reasoning,
            },
            'suggestions': {
                'content_types': self.suggested_content_types,
                'workflows': self.suggested_workflows,
                'keywords': self.keywords,
            },
            'estimates': {
                'revenue': float(self.estimated_revenue),
                'cost': float(self.estimated_cost),
                'roi': float(self.estimated_revenue - self.estimated_cost) if self.estimated_cost else 0,
            },
            'metadata': {
                'confidence_level': self.confidence_level,
                'data_sources': self.data_sources,
                'advisors_consulted': self.advisors_consulted,
            },
            'error': self.error,
        }


class OpportunityScoringAgent:
    """
    AI agent that transforms spider data into scored opportunities.

    This agent analyzes market data, trends, and intelligence to:
    - Score opportunities based on profit potential, competition, effort, and timing
    - Suggest content types that could capitalize on each opportunity
    - Estimate potential revenue and required effort
    - Consult advisors for strategic input
    """

    # Content type mappings based on opportunity characteristics
    CONTENT_TYPE_MAPPINGS = {
        'trend': ['logo', 'thumbnail', 'social_media', 'template'],
        'job': ['resume', 'portfolio', 'presentation'],
        'product': ['logo', 'product_photo', 'marketing_video', 'brand_kit'],
        'news': ['thumbnail', 'infographic', 'social_media'],
        'tech': ['tutorial', 'documentation', 'explainer_video'],
        'viral': ['video', 'thumbnail', 'social_media', 'meme'],
        'seasonal': ['template', 'banner', 'social_media', 'card'],
    }

    # Workflow suggestions based on content types
    WORKFLOW_MAPPINGS = {
        'logo': ['research_and_create_logos', 'brand_identity_package'],
        'thumbnail': ['youtube_thumbnail_package', 'video_thumbnail_series'],
        'video': ['logo_to_video'],
        'brand_kit': ['brand_identity_package'],
        'product_photo': ['product_photography_kit'],
    }

    # Revenue estimates by content type (base estimates in USD)
    REVENUE_ESTIMATES = {
        'logo': (50, 500),
        'thumbnail': (15, 75),
        'video': (100, 1000),
        'template': (20, 100),
        'brand_kit': (200, 2000),
        'social_media': (10, 50),
        'product_photo': (50, 300),
        'infographic': (75, 400),
    }

    # Cost estimates per content type (API costs in USD)
    COST_ESTIMATES = {
        'logo': (0.50, 2.00),
        'thumbnail': (0.20, 0.50),
        'video': (2.00, 10.00),
        'template': (0.30, 1.00),
        'brand_kit': (2.00, 8.00),
        'social_media': (0.10, 0.30),
        'product_photo': (0.50, 2.00),
        'infographic': (0.50, 2.00),
    }

    def __init__(self):
        """Initialize OpportunityScoringAgent."""
        self._spider_data_model = None
        self._opportunity_model = None
        self._opportunity_score_model = None
        self._advisor_model = None
        self._intelligence_service = None

    # ==================== Model Lazy Loading ====================

    @property
    def SpiderData(self):
        """Lazy load SpiderData model."""
        if self._spider_data_model is None:
            from core.models_unified_system import SpiderData
            self._spider_data_model = SpiderData
        return self._spider_data_model

    @property
    def Opportunity(self):
        """Lazy load Opportunity model."""
        if self._opportunity_model is None:
            from core.models_unified_system import Opportunity
            self._opportunity_model = Opportunity
        return self._opportunity_model

    @property
    def OpportunityScore(self):
        """Lazy load OpportunityScore model."""
        if self._opportunity_score_model is None:
            from core.models_unified_system import OpportunityScore
            self._opportunity_score_model = OpportunityScore
        return self._opportunity_score_model

    @property
    def Advisor(self):
        """Lazy load Advisor model."""
        if self._advisor_model is None:
            from core.models_unified_system import Advisor
            self._advisor_model = Advisor
        return self._advisor_model

    @property
    def intelligence_service(self):
        """Lazy load SpiderIntelligenceService."""
        if self._intelligence_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._intelligence_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
                self._intelligence_service = None
        return self._intelligence_service

    # ==================== Main Scoring Methods ====================

    def score_spider_data(
        self,
        hours: int = 24,
        limit: int = 50,
        user=None
    ) -> List[ScoringResult]:
        """
        Score all unprocessed spider data from the last N hours.

        Args:
            hours: Look back period in hours
            limit: Maximum number of items to process
            user: Optional user to associate opportunities with

        Returns:
            List of ScoringResult objects
        """
        logger.info(f"Scoring spider data from last {hours} hours...")

        try:
            from django.utils import timezone
            cutoff = timezone.now() - timedelta(hours=hours)

            # Get unprocessed spider data
            spider_data = self.SpiderData.objects.filter(
                created_at__gte=cutoff,
                is_actionable=True
            ).order_by('-relevance_score')[:limit]

            results = []
            for data in spider_data:
                result = self._score_spider_item(data, user)
                results.append(result)

            # Sort by overall score
            results.sort(key=lambda x: x.overall_score, reverse=True)

            logger.info(f"Scored {len(results)} spider data items")
            return results

        except Exception as e:
            logger.error(f"Error scoring spider data: {e}")
            return [ScoringResult(success=False, error=str(e))]

    def analyze_trend(
        self,
        trend_topic: str,
        trend_data: Optional[Dict] = None,
        user=None
    ) -> ScoringResult:
        """
        Analyze and score a specific trend topic.

        Args:
            trend_topic: The trend topic to analyze
            trend_data: Optional additional trend data
            user: Optional user to associate with

        Returns:
            ScoringResult with scores and suggestions
        """
        logger.info(f"Analyzing trend: {trend_topic}")

        try:
            # Analyze the trend
            scores = self._calculate_trend_scores(trend_topic, trend_data)

            # Determine content suggestions
            content_types = self._suggest_content_types('trend', trend_topic)
            workflows = self._suggest_workflows(content_types)

            # Extract keywords
            keywords = self._extract_keywords(trend_topic, trend_data)

            # Estimate financials
            revenue, cost = self._estimate_financials(content_types)

            # Consult advisors (if available)
            advisor_input = self._consult_advisors(trend_topic, scores)

            # Create the opportunity in database
            opportunity = self._create_opportunity(
                title=f"Trending: {trend_topic}",
                description=f"Capitalize on trending topic: {trend_topic}",
                source_type='trend',
                category=self._determine_category(trend_topic),
                scores=scores,
                content_types=content_types,
                workflows=workflows,
                keywords=keywords,
                revenue=revenue,
                cost=cost,
                advisor_input=advisor_input,
                user=user,
            )

            return ScoringResult(
                success=True,
                opportunity_id=str(opportunity.id) if opportunity else None,
                profit_potential=scores['profit_potential'],
                competition_level=scores['competition_level'],
                effort_required=scores['effort_required'],
                time_sensitivity=scores['time_sensitivity'],
                overall_score=scores['overall_score'],
                profit_reasoning=scores.get('profit_reasoning', ''),
                competition_reasoning=scores.get('competition_reasoning', ''),
                effort_reasoning=scores.get('effort_reasoning', ''),
                timing_reasoning=scores.get('timing_reasoning', ''),
                suggested_content_types=content_types,
                suggested_workflows=workflows,
                keywords=keywords,
                estimated_revenue=revenue,
                estimated_cost=cost,
                confidence_level=scores.get('confidence', 70),
                advisors_consulted=list(advisor_input.keys()) if advisor_input else [],
            )

        except Exception as e:
            logger.error(f"Error analyzing trend '{trend_topic}': {e}")
            return ScoringResult(success=False, error=str(e))

    def score_job_opportunity(
        self,
        job_data: Dict[str, Any],
        user=None
    ) -> ScoringResult:
        """
        Score a job/gig opportunity.

        Args:
            job_data: Job data from spider
            user: Optional user

        Returns:
            ScoringResult
        """
        logger.info(f"Scoring job opportunity: {job_data.get('title', 'Unknown')}")

        try:
            title = job_data.get('title', '')
            company = job_data.get('company', '')
            salary = job_data.get('salary', 0)

            # Calculate scores for jobs
            scores = self._calculate_job_scores(job_data)

            # Content for job applications
            content_types = ['resume', 'portfolio', 'cover_letter']
            workflows = []

            keywords = self._extract_keywords(title, job_data)

            # Estimate based on salary info
            revenue = Decimal(str(salary)) if salary else Decimal('500.00')
            cost = Decimal('1.00')  # Minimal cost for job applications

            opportunity = self._create_opportunity(
                title=f"Job: {title[:100]}",
                description=f"Job at {company}: {title}",
                source_type='job',
                category='freelance',
                scores=scores,
                content_types=content_types,
                workflows=workflows,
                keywords=keywords,
                revenue=revenue,
                cost=cost,
                user=user,
                metadata=job_data,
            )

            return ScoringResult(
                success=True,
                opportunity_id=str(opportunity.id) if opportunity else None,
                profit_potential=scores['profit_potential'],
                competition_level=scores['competition_level'],
                effort_required=scores['effort_required'],
                time_sensitivity=scores['time_sensitivity'],
                overall_score=scores['overall_score'],
                suggested_content_types=content_types,
                keywords=keywords,
                estimated_revenue=revenue,
                estimated_cost=cost,
            )

        except Exception as e:
            logger.error(f"Error scoring job opportunity: {e}")
            return ScoringResult(success=False, error=str(e))

    def get_top_opportunities(
        self,
        limit: int = 10,
        category: Optional[str] = None,
        min_score: int = 50,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Get top-scored opportunities.

        Args:
            limit: Maximum number of opportunities
            category: Optional category filter
            min_score: Minimum overall score
            user: Optional user filter

        Returns:
            List of opportunity dictionaries
        """
        try:
            queryset = self.Opportunity.objects.filter(
                overall_score__gte=min_score,
                status__in=['new', 'reviewing', 'approved']
            )

            if category:
                queryset = queryset.filter(category=category)

            if user:
                queryset = queryset.filter(user=user)

            queryset = queryset.order_by('-overall_score', '-created_at')[:limit]

            opportunities = []
            for opp in queryset:
                opportunities.append({
                    'id': str(opp.id),
                    'title': opp.title,
                    'description': opp.description[:200] if opp.description else '',
                    'source_type': opp.source_type,
                    'category': opp.category,
                    'scores': {
                        'profit_potential': opp.profit_potential,
                        'competition_level': opp.competition_level,
                        'effort_required': opp.effort_required,
                        'time_sensitivity': opp.time_sensitivity,
                        'overall_score': opp.overall_score,
                    },
                    'suggested_content_types': opp.suggested_content_types,
                    'suggested_workflows': opp.suggested_workflows,
                    'estimated_revenue': float(opp.potential_revenue) if opp.potential_revenue else 0,
                    'urgency_level': opp.urgency_level,
                    'status': opp.status,
                    'created_at': opp.created_at.isoformat(),
                })

            return opportunities

        except Exception as e:
            logger.error(f"Error getting top opportunities: {e}")
            return []

    def rescore_opportunity(self, opportunity_id: str) -> ScoringResult:
        """
        Re-score an existing opportunity with fresh data.

        Args:
            opportunity_id: UUID of opportunity to rescore

        Returns:
            ScoringResult with updated scores
        """
        try:
            opportunity = self.Opportunity.objects.get(id=opportunity_id)

            # Gather fresh context
            context = {
                'title': opportunity.title,
                'description': opportunity.description,
                'metadata': opportunity.metadata,
                'market_data': opportunity.market_data,
            }

            # Recalculate scores
            scores = self._calculate_scores_from_context(context, opportunity.source_type)

            # Update opportunity
            opportunity.profit_potential = scores['profit_potential']
            opportunity.competition_level = scores['competition_level']
            opportunity.effort_required = scores['effort_required']
            opportunity.time_sensitivity = scores['time_sensitivity']
            opportunity.score_opportunity(save=True)

            # Update or create score details
            score_details, created = self.OpportunityScore.objects.get_or_create(
                opportunity=opportunity
            )
            score_details.profit_reasoning = scores.get('profit_reasoning', '')
            score_details.competition_reasoning = scores.get('competition_reasoning', '')
            score_details.effort_reasoning = scores.get('effort_reasoning', '')
            score_details.timing_reasoning = scores.get('timing_reasoning', '')
            score_details.scoring_model_version = 'v1.1'
            score_details.save()

            return ScoringResult(
                success=True,
                opportunity_id=opportunity_id,
                profit_potential=opportunity.profit_potential,
                competition_level=opportunity.competition_level,
                effort_required=opportunity.effort_required,
                time_sensitivity=opportunity.time_sensitivity,
                overall_score=opportunity.overall_score,
            )

        except self.Opportunity.DoesNotExist:
            return ScoringResult(success=False, error=f"Opportunity {opportunity_id} not found")
        except Exception as e:
            logger.error(f"Error rescoring opportunity: {e}")
            return ScoringResult(success=False, error=str(e))

    # ==================== Private Scoring Methods ====================

    def _score_spider_item(self, spider_data, user=None) -> ScoringResult:
        """Score a single spider data item."""
        try:
            raw_data = spider_data.raw_data or {}
            processed_data = spider_data.processed_data or {}
            data_type = spider_data.data_type

            # Determine source type from spider data
            source_type = self._determine_source_type(spider_data)

            # Extract title and description
            title = raw_data.get('title', '') or processed_data.get('title', '')
            if not title:
                title = f"{data_type} from {spider_data.spider_name}"

            description = raw_data.get('description', '') or processed_data.get('summary', '')

            # Calculate scores
            context = {
                'title': title,
                'description': description,
                'raw_data': raw_data,
                'processed_data': processed_data,
                'relevance_score': spider_data.relevance_score,
            }
            scores = self._calculate_scores_from_context(context, source_type)

            # Get content suggestions
            content_types = self._suggest_content_types(source_type, title)
            workflows = self._suggest_workflows(content_types)
            keywords = self._extract_keywords(title, raw_data)

            # Estimate financials
            revenue, cost = self._estimate_financials(content_types)

            # Create opportunity
            opportunity = self._create_opportunity(
                title=title[:300],
                description=description[:1000] if description else f"Opportunity from {spider_data.spider_name}",
                source_type=source_type,
                category=self._determine_category(title),
                scores=scores,
                content_types=content_types,
                workflows=workflows,
                keywords=keywords,
                revenue=revenue,
                cost=cost,
                user=user,
                spider_data=spider_data,
            )

            return ScoringResult(
                success=True,
                opportunity_id=str(opportunity.id) if opportunity else None,
                profit_potential=scores['profit_potential'],
                competition_level=scores['competition_level'],
                effort_required=scores['effort_required'],
                time_sensitivity=scores['time_sensitivity'],
                overall_score=scores['overall_score'],
                suggested_content_types=content_types,
                suggested_workflows=workflows,
                keywords=keywords,
                estimated_revenue=revenue,
                estimated_cost=cost,
                data_sources=[spider_data.spider_name],
            )

        except Exception as e:
            logger.error(f"Error scoring spider item: {e}")
            return ScoringResult(success=False, error=str(e))

    def _calculate_trend_scores(
        self,
        topic: str,
        trend_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Calculate scores for a trend topic."""
        trend_data = trend_data or {}

        # Base scores
        profit = 60
        competition = 50
        effort = 40
        timing = 70

        # Adjust based on trend characteristics
        mentions = trend_data.get('mentions', 1)
        if mentions >= 10:
            profit += 20
            competition += 10
        elif mentions >= 5:
            profit += 10

        growth = trend_data.get('growth', 0)
        if growth > 0.5:  # 50% growth
            timing += 20
            profit += 10

        # Check topic keywords for category hints
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ['ai', 'ml', 'automation', 'tech']):
            profit += 10
            competition += 15  # Tech is competitive
        if any(kw in topic_lower for kw in ['viral', 'trending', 'hot']):
            timing += 15
        if any(kw in topic_lower for kw in ['tutorial', 'guide', 'how to']):
            effort += 10  # More effort for educational content

        # Cap scores
        scores = {
            'profit_potential': min(100, max(1, profit)),
            'competition_level': min(100, max(1, competition)),
            'effort_required': min(100, max(1, effort)),
            'time_sensitivity': min(100, max(1, timing)),
            'profit_reasoning': f"Based on {mentions} mentions and topic relevance",
            'competition_reasoning': f"Market saturation assessment for '{topic}'",
            'effort_reasoning': f"Content creation effort estimate",
            'timing_reasoning': f"Time sensitivity based on trend growth: {growth:.0%}",
            'confidence': min(95, 50 + mentions * 3),
        }

        # Calculate overall
        competition_score = 100 - scores['competition_level']
        effort_score = 100 - scores['effort_required']
        scores['overall_score'] = min(100, max(1, int(
            scores['profit_potential'] * 0.35 +
            competition_score * 0.35 +
            effort_score * 0.20 +
            scores['time_sensitivity'] * 0.10
        )))

        return scores

    def _calculate_job_scores(self, job_data: Dict) -> Dict[str, Any]:
        """Calculate scores for a job opportunity."""
        salary = job_data.get('salary', 0) or 0
        is_remote = job_data.get('remote', False) or 'remote' in job_data.get('title', '').lower()
        company = job_data.get('company', '')

        # Base scores
        profit = 50
        competition = 60
        effort = 50
        timing = 60

        # Salary-based adjustments
        if salary > 100000:
            profit = 90
            competition = 80
        elif salary > 75000:
            profit = 75
            competition = 70
        elif salary > 50000:
            profit = 60
            competition = 60

        # Remote bonus
        if is_remote:
            profit += 10
            competition += 5

        scores = {
            'profit_potential': min(100, max(1, profit)),
            'competition_level': min(100, max(1, competition)),
            'effort_required': min(100, max(1, effort)),
            'time_sensitivity': min(100, max(1, timing)),
        }

        competition_score = 100 - scores['competition_level']
        effort_score = 100 - scores['effort_required']
        scores['overall_score'] = min(100, max(1, int(
            scores['profit_potential'] * 0.35 +
            competition_score * 0.35 +
            effort_score * 0.20 +
            scores['time_sensitivity'] * 0.10
        )))

        return scores

    def _calculate_scores_from_context(
        self,
        context: Dict,
        source_type: str
    ) -> Dict[str, Any]:
        """Calculate scores from generic context."""
        title = context.get('title', '')
        relevance = context.get('relevance_score', 50)

        # Base scores influenced by relevance
        base = relevance / 2 + 25  # 25-75 range based on relevance

        return {
            'profit_potential': min(100, max(1, int(base + 10))),
            'competition_level': min(100, max(1, int(50))),
            'effort_required': min(100, max(1, int(40))),
            'time_sensitivity': min(100, max(1, int(60))),
            'profit_reasoning': f"Based on relevance score {relevance} and source type {source_type}",
            'competition_reasoning': "Market competition assessment",
            'effort_reasoning': "Standard effort estimate",
            'timing_reasoning': "Default timing assessment",
            'overall_score': min(100, max(1, int(base + 5))),
        }

    def _suggest_content_types(self, source_type: str, topic: str) -> List[str]:
        """Suggest content types based on opportunity."""
        content_types = self.CONTENT_TYPE_MAPPINGS.get(source_type, ['logo', 'thumbnail'])

        # Add based on topic keywords
        topic_lower = topic.lower()
        if 'video' in topic_lower or 'youtube' in topic_lower:
            if 'thumbnail' not in content_types:
                content_types.append('thumbnail')
            if 'video' not in content_types:
                content_types.append('video')
        if 'brand' in topic_lower or 'logo' in topic_lower:
            if 'logo' not in content_types:
                content_types.insert(0, 'logo')
            if 'brand_kit' not in content_types:
                content_types.append('brand_kit')

        return content_types[:5]  # Limit to 5

    def _suggest_workflows(self, content_types: List[str]) -> List[str]:
        """Suggest workflows based on content types."""
        workflows = set()
        for ct in content_types:
            for workflow in self.WORKFLOW_MAPPINGS.get(ct, []):
                workflows.add(workflow)
        return list(workflows)[:3]  # Limit to 3

    def _extract_keywords(self, text: str, data: Optional[Dict] = None) -> List[str]:
        """Extract keywords from text and data."""
        keywords = set()
        data = data or {}

        # From text
        if text:
            # Simple keyword extraction
            words = text.lower().split()
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are'}
            for word in words:
                word = word.strip('.,!?()[]{}')
                if len(word) > 3 and word not in stopwords:
                    keywords.add(word)

        # From data
        if 'tags' in data:
            keywords.update(data['tags'][:10])
        if 'keywords' in data:
            keywords.update(data['keywords'][:10])

        return list(keywords)[:15]

    def _estimate_financials(
        self,
        content_types: List[str]
    ) -> Tuple[Decimal, Decimal]:
        """Estimate revenue and cost for content types."""
        total_revenue_low = 0
        total_revenue_high = 0
        total_cost_low = 0
        total_cost_high = 0

        for ct in content_types:
            rev_range = self.REVENUE_ESTIMATES.get(ct, (25, 100))
            cost_range = self.COST_ESTIMATES.get(ct, (0.25, 1.00))

            total_revenue_low += rev_range[0]
            total_revenue_high += rev_range[1]
            total_cost_low += cost_range[0]
            total_cost_high += cost_range[1]

        # Use midpoint estimates
        revenue = Decimal(str((total_revenue_low + total_revenue_high) / 2))
        cost = Decimal(str((total_cost_low + total_cost_high) / 2))

        return revenue, cost

    def _consult_advisors(
        self,
        topic: str,
        scores: Dict
    ) -> Dict[str, str]:
        """Consult relevant advisors for input."""
        try:
            # Get relevant advisors
            advisors = self.Advisor.objects.filter(
                is_active=True,
                category__in=['business', 'investing', 'marketing']
            )[:3]

            advisor_input = {}
            for advisor in advisors:
                # Generate advisor-style recommendation
                if advisor.name == 'Warren Buffett':
                    advisor_input[advisor.name] = "Focus on opportunities with strong fundamentals and sustainable competitive advantage."
                elif advisor.name == 'Peter Thiel':
                    advisor_input[advisor.name] = "Look for zero-to-one opportunities that create new markets."
                elif advisor.name == 'Gary Vee':
                    advisor_input[advisor.name] = "Execute quickly and iterate. Social content can drive awareness."
                else:
                    advisor_input[advisor.name] = f"Recommendation from {advisor.name}"

            return advisor_input

        except Exception as e:
            logger.warning(f"Could not consult advisors: {e}")
            return {}

    def _determine_source_type(self, spider_data) -> str:
        """Determine source type from spider data."""
        spider_name = spider_data.spider_name.lower()
        data_type = spider_data.data_type.lower() if spider_data.data_type else ''

        if any(kw in spider_name for kw in ['job', 'remote', 'work', 'career']):
            return 'job'
        if any(kw in spider_name for kw in ['news', 'tech', 'verge', 'wired']):
            return 'news'
        if any(kw in spider_name for kw in ['trend', 'viral', 'social']):
            return 'trend'
        if any(kw in spider_name for kw in ['product', 'launch', 'hunt']):
            return 'product'
        if any(kw in spider_name for kw in ['crypto', 'finance', 'stock']):
            return 'news'
        if 'tech' in data_type:
            return 'tech'

        return 'trend'  # Default

    def _determine_category(self, text: str) -> str:
        """Determine category from text."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ['design', 'logo', 'brand', 'creative']):
            return 'digital_product'
        if any(kw in text_lower for kw in ['freelance', 'gig', 'contract', 'remote']):
            return 'freelance'
        if any(kw in text_lower for kw in ['video', 'content', 'social', 'youtube']):
            return 'content'
        if any(kw in text_lower for kw in ['template', 'asset', 'resource']):
            return 'template'
        if any(kw in text_lower for kw in ['course', 'tutorial', 'learn', 'education']):
            return 'course'
        if any(kw in text_lower for kw in ['software', 'app', 'tool', 'saas']):
            return 'software'

        return 'digital_product'  # Default

    def _create_opportunity(
        self,
        title: str,
        description: str,
        source_type: str,
        category: str,
        scores: Dict,
        content_types: List[str],
        workflows: List[str],
        keywords: List[str],
        revenue: Decimal,
        cost: Decimal,
        user=None,
        spider_data=None,
        advisor_input: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ):
        """Create an Opportunity in the database."""
        try:
            from django.utils import timezone

            opportunity = self.Opportunity.objects.create(
                user=user,
                title=title,
                description=description,
                opportunity_type=source_type,
                source=spider_data.spider_name if spider_data else 'manual',
                potential_revenue=revenue,
                status='active',
                source_type=source_type,
                category=category,
                profit_potential=scores.get('profit_potential', 50),
                competition_level=scores.get('competition_level', 50),
                effort_required=scores.get('effort_required', 50),
                time_sensitivity=scores.get('time_sensitivity', 50),
                overall_score=scores.get('overall_score', 50),
                suggested_content_types=content_types,
                suggested_workflows=workflows,
                keywords=keywords,
                estimated_cost=cost,
                advisor_recommendations=advisor_input or {},
                metadata=metadata or {},
                spider_data=spider_data,
                scored_at=timezone.now(),
            )

            # Create score details
            self.OpportunityScore.objects.create(
                opportunity=opportunity,
                profit_reasoning=scores.get('profit_reasoning', ''),
                competition_reasoning=scores.get('competition_reasoning', ''),
                effort_reasoning=scores.get('effort_reasoning', ''),
                timing_reasoning=scores.get('timing_reasoning', ''),
                confidence_level=scores.get('confidence', 70),
                scoring_model_version='v1.0',
            )

            logger.info(f"Created opportunity: {opportunity.title} (Score: {opportunity.overall_score})")
            return opportunity

        except Exception as e:
            logger.error(f"Error creating opportunity: {e}")
            return None


# ==================== Convenience Functions ====================

def score_recent_data(hours: int = 24, user=None) -> List[Dict]:
    """Score recent spider data and return results."""
    agent = OpportunityScoringAgent()
    results = agent.score_spider_data(hours=hours, user=user)
    return [r.to_dict() for r in results if r.success]


def get_top_opportunities(limit: int = 10, min_score: int = 50) -> List[Dict]:
    """Get top-scored opportunities."""
    agent = OpportunityScoringAgent()
    return agent.get_top_opportunities(limit=limit, min_score=min_score)


def analyze_trend(topic: str, user=None) -> Dict:
    """Analyze and score a trend topic."""
    agent = OpportunityScoringAgent()
    result = agent.analyze_trend(topic, user=user)
    return result.to_dict()
