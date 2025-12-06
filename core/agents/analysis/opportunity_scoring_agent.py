"""
Opportunity Scoring Agent - Clean Architecture
===============================================

Session 280: Phase 3 - Agent Architecture Unification

This agent transforms raw spider data into scored, actionable opportunities
that feed into the content creation pipeline.

Tools Available:
    - score_data: Score spider data for opportunities
    - analyze_trend: Analyze and score a specific trend
    - get_top_opportunities: Get highest-scored opportunities

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
from datetime import timedelta
from decimal import Decimal
from dataclasses import dataclass, field

from core.agents.base_agent import BaseAgent, AgentResult

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

                full_prompt = self._build_prompt(task, scifi_context, spider_context)
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

                    execution_time = int((time.time() - start_time) * 1000)

                    result = AgentResult(
                        success=True,
                        message="Opportunity scoring completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
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

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

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
        """Calculate score for a spider data item."""
        raw_data = spider_data.raw_data or {}
        title = raw_data.get('title', f"{spider_data.data_type} from {spider_data.spider_name}")

        # Base scores from relevance
        base = spider_data.relevance_score / 2 + 25

        profit = min(100, max(1, int(base + 10)))
        competition = 50
        effort = 40
        timing = 60

        # Calculate overall
        competition_score = 100 - competition
        effort_score = 100 - effort
        overall = int(
            profit * 0.35 +
            competition_score * 0.35 +
            effort_score * 0.20 +
            timing * 0.10
        )

        return {
            'title': title[:100],
            'source': spider_data.spider_name,
            'profit_potential': profit,
            'competition_level': competition,
            'effort_required': effort,
            'time_sensitivity': timing,
            'overall_score': min(100, max(1, overall)),
            'content_types': self._suggest_content_types('trend', title),
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
