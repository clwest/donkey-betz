"""
Opportunity Scoring Agent - Clean Architecture
===============================================

Session 280: Phase 3 - Agent Architecture Unification
Session 470: Market Intelligence Architecture - ML Scoring Integration
Session 683: Added ML Integration (RL for opportunity ranking optimization)

This agent transforms raw spider data into scored, actionable opportunities
that feed into the content creation pipeline.

Now supports:
- Hybrid ML + rule-based scoring with SHAP explainability
- RL-powered opportunity ranking optimization (Session 683)

Tools Available:
    - score_data: Score spider data for opportunities
    - analyze_trend: Analyze and score a specific trend
    - get_top_opportunities: Get highest-scored opportunities
    - ML: RL optimization for opportunity ranking (auto-invoked)

Usage:
    from core.agents.analysis import OpportunityScoringAgent

    agent = OpportunityScoringAgent(user=request.user)
    result = agent.execute(
        task="Score the latest spider data for opportunities",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
from dataclasses import dataclass, field

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer

logger = logging.getLogger(__name__)

# Session 470: ML Scoring Engine
_ml_scoring_engine = None


def _get_ml_scoring_engine():
    """Lazy load ML scoring engine."""
    global _ml_scoring_engine
    if _ml_scoring_engine is None:
        try:
            from core.services.ml_scoring_engine import get_ml_scoring_engine
            _ml_scoring_engine = get_ml_scoring_engine()
            logger.info("ML Scoring Engine loaded successfully")
        except Exception as e:
            logger.warning(f"ML Scoring Engine not available: {e}")
    return _ml_scoring_engine


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
            },
            'metadata': {
                'confidence_level': self.confidence_level,
                'data_sources': self.data_sources,
            },
            'error': self.error,
        }


class OpportunityScoringAgent(BaseAgent):
    """
    Opportunity Scoring Agent - The Heart of the Opportunity Engine.

    This agent:
    1. Scores spider data for profit potential
    2. Analyzes trends for opportunities
    3. Suggests content types and workflows

    It CANNOT:
    - Create content directly
    - Execute workflows
    """

    name = "OpportunityScoringAgent"
    llm_timeout = 180.0  # Session 1074: Multi-industry scoring needs 3 min

    system_prompt = """You are OpportunityScoringAgent, the Opportunity Engine.

Your job is to transform raw spider data into scored, actionable opportunities:
- Score opportunities based on profit potential, competition, effort, and timing
- Suggest content types that could capitalize on each opportunity
- Estimate potential revenue and required effort

Scoring Factors (1-100):
- Profit Potential: How much money could this make?
- Competition Level: How saturated is this market?
- Effort Required: How much work to capitalize on this?
- Time Sensitivity: How urgent is this opportunity?

When given a task:
1. Analyze the data source (spider data, trend, or topic)
2. Calculate scores for each factor
3. Suggest appropriate content types
4. Estimate potential revenue

You score and analyze - you do NOT create content or execute workflows."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "score_data",
                "description": "Score spider data for opportunities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 24
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum items to score",
                            "default": 50
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_trend",
                "description": "Analyze and score a specific trend topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Trend topic to analyze"
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_opportunities",
                "description": "Get highest-scored opportunities",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of opportunities to return",
                            "default": 10
                        },
                        "min_score": {
                            "type": "integer",
                            "description": "Minimum score threshold",
                            "default": 50
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                            "enum": ["digital_product", "freelance", "content", "template", "course", "software"]
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    # Content type mappings
    CONTENT_TYPE_MAPPINGS = {
        'trend': ['logo', 'thumbnail', 'social_media', 'template'],
        'job': ['resume', 'portfolio', 'presentation'],
        'product': ['logo', 'product_photo', 'marketing_video', 'brand_kit'],
        'news': ['thumbnail', 'infographic', 'social_media'],
        'tech': ['tutorial', 'documentation', 'explainer_video'],
    }

    # Workflow suggestions
    WORKFLOW_MAPPINGS = {
        'logo': ['research_and_create_logos', 'brand_identity_package'],
        'thumbnail': ['youtube_thumbnail_package', 'video_thumbnail_series'],
        'video': ['logo_to_video'],
        'brand_kit': ['brand_identity_package'],
        'product_photo': ['product_photography_kit'],
    }

    # Revenue estimates by content type (USD)
    REVENUE_ESTIMATES = {
        'logo': (50, 500),
        'thumbnail': (15, 75),
        'video': (100, 1000),
        'template': (20, 100),
        'brand_kit': (200, 2000),
        'social_media': (10, 50),
    }

    def __init__(self, user=None):
        """Initialize OpportunityScoringAgent."""
        super().__init__(user=user)
        self._intelligence_service = None

    @property
    def intelligence_service(self):
        """Lazy load SpiderIntelligenceService."""
        if self._intelligence_service is None:
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                self._intelligence_service = SpiderIntelligenceService()
            except ImportError:
                logger.warning("SpiderIntelligenceService not available")
        return self._intelligence_service

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute opportunity scoring based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("opportunity_scoring", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing scoring request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["score_data", "analyze_trend", "get_top_opportunities"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"OpportunityScoringAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Scoring operation: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    # Session 683: Run RL optimization on scored opportunities
                    ml_insights = self._optimize_ranking_with_rl(tool_calls_made)

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 953: Build provenance from scoring results
                    sources = []
                    for tc in tool_calls_made:
                        sources.append({
                            'name': tc.get('tool', 'opportunity_scoring'),
                            'endpoint': 'spider_data',
                            'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                            'record_count': 1,
                        })
                    if not sources:
                        sources = [{
                            'name': 'opportunity_scoring',
                            'endpoint': 'spider_data',
                            'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                            'record_count': 0,
                        }]
                    provenance = build_provenance(
                        report_type='analysis',
                        agent_name=self.name,
                        sources=sources,
                        stale_threshold_hours=24.0,
                    )
                    provenance.disclaimer = format_disclaimer('analysis')
                    provenance_block = provenance.to_markdown_block()

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                    analysis_msg = synthesis if synthesis else "Opportunity scoring completed"

                    result = AgentResult(
                        success=True,
                        message=provenance_block + "\n\n" + analysis_msg,
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                            'content': synthesis,
                            'ml_analysis': ml_insights,  # Session 683: Add RL optimization
                            'provenance': provenance.to_dict(),
                            'publishable': provenance.publishable,
                            'validation_status': provenance.validation_status,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 861/1200: Persist synthesis to Deliverable
                    self._save_to_deliverable(
                        title=f"Opportunity Analysis: {task[:50]}",
                        content=analysis_msg,
                        deliverable_type='analysis',
                        category='Business',
                        tags=['opportunity', 'scoring', 'analysis'],
                        content_format='markdown',
                        metadata={
                            'task': task,
                            'execution_time_ms': execution_time,
                            'tools_used': [tc.get('tool') for tc in tool_calls_made],
                        },
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    return result

                else:
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"OpportunityScoringAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an opportunity scoring tool call."""
        if tool_name == "score_data":
            return self._score_data(
                hours=arguments.get('hours', 24),
                limit=arguments.get('limit', 50)
            )

        elif tool_name == "analyze_trend":
            return self._analyze_trend(
                topic=arguments.get('topic', '')
            )

        elif tool_name == "get_top_opportunities":
            return self._get_top_opportunities(
                limit=arguments.get('limit', 10),
                min_score=arguments.get('min_score', 50),
                category=arguments.get('category')
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _score_data(self, hours: int, limit: int) -> Dict[str, Any]:
        """Score spider data for opportunities."""
        logger.info(f"Scoring spider data from last {hours} hours (limit: {limit})")

        try:
            from django.utils import timezone
            from core.models_unified_system import SpiderData

            cutoff = timezone.now() - timedelta(hours=hours)

            # Get spider data
            spider_data = SpiderData.objects.filter(
                created_at__gte=cutoff,
                is_actionable=True
            ).order_by('-relevance_score')[:limit]

            scored_items = []
            for data in spider_data:
                score = self._calculate_score(data)
                scored_items.append(score)

            # Sort by overall score
            scored_items.sort(key=lambda x: x['overall_score'], reverse=True)

            return {
                'success': True,
                'items_scored': len(scored_items),
                'top_opportunities': scored_items[:10]
            }

        except Exception as e:
            logger.error(f"Error scoring data: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_trend(self, topic: str) -> Dict[str, Any]:
        """Analyze and score a specific trend."""
        logger.info(f"Analyzing trend: {topic}")

        try:
            # Calculate scores
            scores = self._calculate_trend_scores(topic)

            # Suggest content types
            content_types = self._suggest_content_types('trend', topic)
            workflows = self._suggest_workflows(content_types)

            # Estimate financials
            revenue, cost = self._estimate_financials(content_types)

            result = ScoringResult(
                success=True,
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
                estimated_revenue=revenue,
                estimated_cost=cost,
                confidence_level=scores.get('confidence', 70),
            )

            return {
                'success': True,
                'topic': topic,
                'analysis': result.to_dict()
            }

        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_top_opportunities(
        self,
        limit: int = 10,
        min_score: int = 50,
        category: Optional[str] = None,
        user=None
    ) -> List[Dict[str, Any]]:
        """
        Public method to get highest-scored opportunities.

        Args:
            limit: Number of opportunities to return
            min_score: Minimum score threshold
            category: Optional category filter
            user: Optional user for personalization (future use)

        Returns:
            List of opportunity dictionaries
        """
        result = self._get_top_opportunities(limit, min_score, category)
        if result.get('success'):
            return result.get('opportunities', [])
        return []

    def _get_top_opportunities(
        self,
        limit: int,
        min_score: int,
        category: Optional[str]
    ) -> Dict[str, Any]:
        """Get highest-scored opportunities."""
        logger.info(f"Getting top {limit} opportunities (min_score: {min_score})")

        try:
            from core.models_unified_system import Opportunity

            queryset = Opportunity.objects.filter(
                overall_score__gte=min_score,
                status__in=['new', 'reviewing', 'approved', 'active']
            )

            if category:
                queryset = queryset.filter(category=category)

            queryset = queryset.order_by('-overall_score', '-created_at')[:limit]

            opportunities = []
            for opp in queryset:
                opportunities.append({
                    'id': str(opp.id),
                    'title': opp.title,
                    'description': opp.description[:200] if opp.description else '',
                    'category': opp.category,
                    'overall_score': opp.overall_score,
                    'profit_potential': opp.profit_potential,
                    'suggested_content_types': opp.suggested_content_types or [],
                    'estimated_revenue': float(opp.potential_revenue) if opp.potential_revenue else 0,
                    'status': opp.status,
                })

            return {
                'success': True,
                'opportunities': opportunities,
                'total_found': len(opportunities)
            }

        except Exception as e:
            logger.error(f"Error getting opportunities: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _calculate_score(self, spider_data) -> Dict[str, Any]:
        """
        Calculate score for a spider data item.

        Session 470: Now uses hybrid ML + rule-based scoring with SHAP explanations.
        """
        raw_data = spider_data.raw_data or {}
        title = raw_data.get('title', f"{spider_data.data_type} from {spider_data.spider_name}")

        # Session 470: Try ML scoring first
        ml_engine = _get_ml_scoring_engine()
        if ml_engine:
            try:
                ml_result = ml_engine.score_opportunity(spider_data)
                if ml_result.success:
                    # Store explanation if we have an opportunity
                    explanation_data = None
                    if ml_result.shap_explanation:
                        explanation_data = ml_result.shap_explanation.to_dict()

                    return {
                        'title': title[:100],
                        'source': spider_data.spider_name,
                        'profit_potential': ml_result.profit_potential,
                        'competition_level': ml_result.competition_level,
                        'effort_required': ml_result.effort_required,
                        'time_sensitivity': ml_result.time_sensitivity,
                        'overall_score': min(100, max(1, int(ml_result.hybrid_score))),
                        'content_types': self._suggest_content_types('trend', title),
                        # Session 470: ML scoring metadata
                        'ml_score': ml_result.ml_score,
                        'rule_score': ml_result.rule_score,
                        'hybrid_score': ml_result.hybrid_score,
                        'confidence': ml_result.confidence,
                        'model_version': ml_result.model_version,
                        'explanation': explanation_data,
                        'scoring_method': 'hybrid_ml',
                    }
            except Exception as e:
                logger.warning(f"ML scoring failed, falling back to rules: {e}")

        # Fallback: Unified type-aware scoring
        from core.services.opportunity_scorer import score_opportunity
        result = score_opportunity(
            raw_data=raw_data,
            spider_name=spider_data.spider_name,
            data_type=spider_data.data_type,
            title=title,
        )

        return {
            'title': title[:100],
            'source': spider_data.spider_name,
            'profit_potential': result['profit_potential'],
            'competition_level': result['competition_level'],
            'effort_required': result['effort_required'],
            'time_sensitivity': result['time_sensitivity'],
            'overall_score': result['overall_score'],
            'content_types': self._suggest_content_types('trend', title),
            'scoring_method': result['scoring_method'],
        }

    def _calculate_trend_scores(self, topic: str) -> Dict[str, Any]:
        """Calculate scores for a trend topic."""
        # Base scores
        profit = 60
        competition = 50
        effort = 40
        timing = 70

        # Adjust based on topic keywords
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ['ai', 'ml', 'automation', 'tech']):
            profit += 10
            competition += 15
        if any(kw in topic_lower for kw in ['viral', 'trending', 'hot']):
            timing += 15

        # Cap scores
        scores = {
            'profit_potential': min(100, max(1, profit)),
            'competition_level': min(100, max(1, competition)),
            'effort_required': min(100, max(1, effort)),
            'time_sensitivity': min(100, max(1, timing)),
            'profit_reasoning': f"Based on topic relevance for '{topic}'",
            'competition_reasoning': f"Market saturation assessment",
            'effort_reasoning': f"Content creation effort estimate",
            'timing_reasoning': f"Time sensitivity based on trend signals",
            'confidence': 70,
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

    def _suggest_content_types(self, source_type: str, topic: str) -> List[str]:
        """Suggest content types based on opportunity."""
        content_types = self.CONTENT_TYPE_MAPPINGS.get(source_type, ['logo', 'thumbnail'])

        topic_lower = topic.lower()
        if 'video' in topic_lower or 'youtube' in topic_lower:
            if 'thumbnail' not in content_types:
                content_types.append('thumbnail')
        if 'brand' in topic_lower or 'logo' in topic_lower:
            if 'logo' not in content_types:
                content_types.insert(0, 'logo')

        return content_types[:5]

    def _suggest_workflows(self, content_types: List[str]) -> List[str]:
        """Suggest workflows based on content types."""
        workflows = set()
        for ct in content_types:
            for workflow in self.WORKFLOW_MAPPINGS.get(ct, []):
                workflows.add(workflow)
        return list(workflows)[:3]

    def _estimate_financials(
        self,
        content_types: List[str]
    ) -> Tuple[Decimal, Decimal]:
        """Estimate revenue and cost for content types."""
        total_revenue = 0
        total_cost = 0

        for ct in content_types:
            rev_range = self.REVENUE_ESTIMATES.get(ct, (25, 100))
            total_revenue += (rev_range[0] + rev_range[1]) / 2
            total_cost += 1.0  # Base cost estimate

        return Decimal(str(total_revenue)), Decimal(str(total_cost))

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for scoring."""
        return bool(task and task.strip())

    # =========================================================================
    # Session 671: Complete Pipeline Integration
    # =========================================================================

    def score_spider_data(self, hours: int = 24, limit: int = 100) -> List[ScoringResult]:
        """
        Score spider data and create opportunities for high-scoring items.

        This is the main entry point called by the Celery task
        `score_opportunities_from_spider_data`.

        Args:
            hours: Look back period in hours (default: 24)
            limit: Maximum items to process (default: 100)

        Returns:
            List of ScoringResult objects
        """
        logger.info(f"[PIPELINE] Scoring spider data from last {hours}h (limit: {limit})")

        results = []

        try:
            from django.utils import timezone
            from core.models_unified_system import SpiderData, Opportunity, OpportunityTask

            cutoff = timezone.now() - timedelta(hours=hours)

            # Get unprocessed spider data (not yet linked to an opportunity)
            # Note: Opportunity.spider_data has related_name='scored_opportunities'
            spider_data_qs = SpiderData.objects.filter(
                created_at__gte=cutoff,
                is_actionable=True,
                scored_opportunities__isnull=True  # Not yet processed into an opportunity
            ).order_by('-relevance_score')[:limit]

            logger.info(f"[PIPELINE] Found {spider_data_qs.count()} unprocessed spider data items")

            opportunities_created = 0
            tasks_created = 0

            for data in spider_data_qs:
                try:
                    # Score using ML engine
                    score_data = self._calculate_score(data)

                    result = ScoringResult(
                        success=True,
                        profit_potential=score_data.get('profit_potential', 50),
                        competition_level=score_data.get('competition_level', 50),
                        effort_required=score_data.get('effort_required', 50),
                        time_sensitivity=score_data.get('time_sensitivity', 50),
                        overall_score=score_data.get('overall_score', 50),
                        suggested_content_types=score_data.get('content_types', []),
                        confidence_level=int(score_data.get('confidence', 70)),
                        data_sources=[data.spider_name],
                    )

                    # Create Opportunity for high-scoring items (70+)
                    if result.overall_score >= 70:
                        opportunity = self._create_opportunity_from_score(data, score_data)
                        if opportunity:
                            result.opportunity_id = str(opportunity.id)
                            opportunities_created += 1

                            # Auto-create task for very high scores (80+)
                            if result.overall_score >= 80:
                                task = self._create_task_from_opportunity(opportunity, score_data)
                                if task:
                                    tasks_created += 1

                    results.append(result)

                except Exception as e:
                    logger.warning(f"[PIPELINE] Error scoring {data.id}: {e}")
                    results.append(ScoringResult(
                        success=False,
                        error=str(e)
                    ))

            logger.info(
                f"[PIPELINE] Complete: {len(results)} scored, "
                f"{opportunities_created} opportunities, {tasks_created} tasks"
            )

        except Exception as e:
            logger.error(f"[PIPELINE] Fatal error: {e}")
            results.append(ScoringResult(success=False, error=str(e)))

        return results

    def _create_opportunity_from_score(
        self,
        spider_data,
        score_data: Dict[str, Any]
    ) -> Optional['Opportunity']:
        """
        Create an Opportunity record from scored spider data.

        Args:
            spider_data: The SpiderData instance
            score_data: Score results from _calculate_score

        Returns:
            Created Opportunity or None if creation fails
        """
        try:
            from core.models_unified_system import Opportunity

            raw_data = spider_data.raw_data or {}
            title = raw_data.get('title', f"{spider_data.data_type} from {spider_data.spider_name}")

            # Determine category from spider name
            category = self._determine_category(spider_data.spider_name)

            opportunity = Opportunity.objects.create(
                spider_data=spider_data,
                title=title[:255],
                description=raw_data.get('description', '')[:2000],
                category=category,
                source=spider_data.spider_name,
                source_url=raw_data.get('url', ''),

                # Scores
                overall_score=score_data.get('overall_score', 50),
                profit_potential=score_data.get('profit_potential', 50),
                competition_level=score_data.get('competition_level', 50),
                effort_required=score_data.get('effort_required', 50),
                time_sensitivity=score_data.get('time_sensitivity', 50),

                # ML metadata
                suggested_content_types=score_data.get('content_types', []),
                metadata={
                    'scoring_method': score_data.get('scoring_method', 'unknown'),
                    'ml_score': score_data.get('ml_score'),
                    'rule_score': score_data.get('rule_score'),
                    'hybrid_score': score_data.get('hybrid_score'),
                    'model_version': score_data.get('model_version'),
                    'confidence': score_data.get('confidence'),
                    'explanation': score_data.get('explanation'),
                },

                status='new',
            )

            logger.info(f"[PIPELINE] Created opportunity {opportunity.id} (score: {opportunity.overall_score})")
            return opportunity

        except Exception as e:
            logger.error(f"[PIPELINE] Failed to create opportunity: {e}")
            return None

    def _create_task_from_opportunity(
        self,
        opportunity,
        score_data: Dict[str, Any]
    ) -> Optional['OpportunityTask']:
        """
        Create an OpportunityTask from a high-scoring Opportunity.

        Args:
            opportunity: The Opportunity instance
            score_data: Score results

        Returns:
            Created OpportunityTask or None
        """
        try:
            from core.models_unified_system import OpportunityTask

            # Use the model's factory method if available
            if hasattr(OpportunityTask, 'create_from_opportunity'):
                task = OpportunityTask.create_from_opportunity(opportunity, score_data)
                logger.info(f"[PIPELINE] Created task {task.id} for opportunity {opportunity.id}")
                return task

            # Fallback: create manually
            from django.utils import timezone
            from datetime import timedelta

            # Determine priority
            score = opportunity.overall_score
            if score >= 90:
                priority = 'critical'
                days_until_due = 1
            elif score >= 80:
                priority = 'high'
                days_until_due = 3
            else:
                priority = 'medium'
                days_until_due = 7

            # Build research context for better agent execution
            research_context = OpportunityTask._build_research_context(opportunity)
            task_metadata = {
                'research_query': research_context['research_query'],
                'research_topic': research_context['research_topic'],
                'keywords': research_context['keywords'],
                'category': research_context['category'],
                'source': research_context['source'],
                'clean_title': research_context['clean_title'],
            }

            task = OpportunityTask.objects.create(
                opportunity=opportunity,
                title=f"Act on: {opportunity.title[:100]}",
                description=f"High-scoring opportunity (score: {score}). Suggested content: {', '.join(score_data.get('content_types', []))}",
                priority=priority,
                status='pending',
                due_date=timezone.now() + timedelta(days=days_until_due),
                metadata=task_metadata,
            )

            # Assign agent (ForeignKey expects Agent object)
            relevant_agents = opportunity.get_relevant_agents()
            if relevant_agents:
                task.primary_agent = relevant_agents[0]
                task.save()

            logger.info(f"[PIPELINE] Created task {task.id} (priority: {priority})")
            return task

        except Exception as e:
            logger.error(f"[PIPELINE] Failed to create task: {e}")
            return None

    def _determine_category(self, spider_name: str) -> str:
        """Determine opportunity category from spider name."""
        spider_lower = spider_name.lower()

        category_mappings = {
            'freelance': ['freelancer', 'upwork', 'fiverr', 'remoteok', 'weworkremotely', 'real_job', 'job_opportunity'],
            'content': ['youtube', 'tiktok', 'instagram', 'twitter', 'reddit', 'news', 'trending_content', 'social_api'],
            'sports_betting': ['theodds', 'odds_api', 'sports_odds', 'sports_data', 'live_betting', 'prop_betting', 'esports'],
            'trading': ['yahoo_finance', 'coingecko', 'stock_options', 'forex_crypto', 'financial_api', 'crypto_intelligence'],
            'digital_product': ['gumroad', 'teachable', 'udemy', 'skillshare'],
            'software': ['github', 'producthunt', 'hackernews'],
            'consulting': ['ai_startup'],
            'course': ['coursera', 'edx', 'khan'],
            'template': ['envato', 'creative_market'],
        }

        for category, keywords in category_mappings.items():
            if any(kw in spider_lower for kw in keywords):
                return category

        return 'content'  # Default

    # =========================================================================
    # SESSION 683: ML INTEGRATION - RL FOR OPPORTUNITY RANKING OPTIMIZATION
    # =========================================================================

    def _optimize_ranking_with_rl(self, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use ML models to optimize opportunity ranking.

        Session 683: Integrates the Agent-Model Router to auto-select RL
        for decision optimization on opportunity prioritization.
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            # Build decision data from scoring results
            decision_data = self._build_decision_data(tool_results)

            if not decision_data.get('actions') or len(decision_data['actions']) < 2:
                return {
                    'ml_used': False,
                    'reason': 'Insufficient opportunities for ranking optimization'
                }

            # Get router and run auto-selection (should select RL for decision tasks)
            router = get_agent_model_router()

            # Provide hint that this is a decision/optimization task
            from ml.auto_selection import TaskType
            result = router.auto_route(
                decision_data,
                task_hint=TaskType.DECISION,
                max_models=2
            )

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'unknown'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'selection_reason': result.auto_selection.get('selection_reason', ''),
                'opportunities_optimized': len(decision_data.get('actions', [])),
            }

        except ImportError as e:
            logger.warning(f"ML router not available: {e}")
            return {'ml_used': False, 'reason': f'ML not available: {e}'}
        except Exception as e:
            logger.warning(f"ML analysis error: {e}")
            return {'ml_used': False, 'reason': f'ML error: {e}'}

    def _build_decision_data(self, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build decision data suitable for RL optimization.

        Creates state-action representation for opportunity ranking.
        """
        actions = []
        states = []

        for tool_result in tool_results:
            result_data = tool_result.get('result', {})

            # Extract opportunities from various tool results
            opportunities = []
            if 'opportunities' in result_data:
                opportunities = result_data['opportunities']
            elif 'top_opportunities' in result_data:
                opportunities = result_data['top_opportunities']
            elif 'analysis' in result_data and isinstance(result_data['analysis'], dict):
                opportunities = [result_data['analysis']]

            for opp in opportunities:
                if isinstance(opp, dict):
                    # State: current opportunity features
                    state = {
                        'profit_potential': opp.get('profit_potential', 50),
                        'competition_level': opp.get('competition_level', 50),
                        'effort_required': opp.get('effort_required', 50),
                        'time_sensitivity': opp.get('time_sensitivity', 50),
                        'overall_score': opp.get('overall_score', 50),
                    }
                    states.append(state)

                    # Action: prioritize/defer/skip
                    score = opp.get('overall_score', 50)
                    if score >= 80:
                        action = 'prioritize'
                    elif score >= 60:
                        action = 'queue'
                    else:
                        action = 'defer'

                    actions.append({
                        'opportunity_id': opp.get('id', opp.get('title', 'unknown')),
                        'action': action,
                        'score': score,
                    })

        return {
            'decision_type': 'opportunity_ranking',
            'states': states,
            'actions': actions,
            'reward_function': 'maximize_roi',  # Hint for RL model
        }
