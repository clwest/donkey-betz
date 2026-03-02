"""
Session 945: Learning Loop Orchestrator

Central service that unifies the learning feedback loop:
1. Consumes outcomes from ToolCallRecord, DecisionRecord, AgentFeedback
2. Extracts patterns (success factors, failure factors)
3. Creates/updates LearningPattern records
4. Provides learning context for agent prompts

This connects the scattered learning infrastructure into a coherent system.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import timedelta
from collections import defaultdict
from dataclasses import dataclass, field
from django.utils import timezone
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import TruncDate

logger = logging.getLogger(__name__)


@dataclass
class SuccessSignal:
    """Defines what success means for a specific context."""
    tool_name: str
    success_indicators: List[str] = field(default_factory=list)
    failure_indicators: List[str] = field(default_factory=list)
    latency_threshold_ms: int = 5000  # Max acceptable latency
    min_result_size: int = 10  # Minimum result size to be useful
    weight: float = 1.0  # How much to weight this signal


@dataclass
class ExtractedLearning:
    """A learning extracted from execution data."""
    pattern_type: str
    description: str
    confidence: float
    applies_to_agents: List[str]
    pattern_data: Dict[str, Any]
    source_records: int = 0


class LearningLoopOrchestrator:
    """
    Central orchestrator for the learning feedback loop.

    Responsibilities:
    1. Analyze tool execution outcomes
    2. Analyze decision outcomes
    3. Extract cross-agent patterns
    4. Update LearningPattern records
    5. Provide context builders for agents
    """

    # Default success signals for common tools
    # Session 954: Expanded from 3 to 15+ tools for comprehensive learning
    DEFAULT_SUCCESS_SIGNALS = {
        # Research & Search Tools
        'web_search': SuccessSignal(
            tool_name='web_search',
            success_indicators=['results', 'found', 'matches'],
            failure_indicators=['no results', 'error', 'timeout'],
            latency_threshold_ms=10000,
        ),
        'analyze_filing': SuccessSignal(
            tool_name='analyze_filing',
            success_indicators=['analysis', 'summary', 'findings'],
            failure_indicators=['not found', 'parsing error'],
            latency_threshold_ms=30000,
        ),
        'get_stock_data': SuccessSignal(
            tool_name='get_stock_data',
            success_indicators=['price', 'volume', 'data'],
            failure_indicators=['invalid ticker', 'no data'],
            latency_threshold_ms=5000,
        ),
        # Content Creation Tools
        'image_generation_agent': SuccessSignal(
            tool_name='image_generation_agent',
            success_indicators=['image_id', 'generated', 'url', 'created'],
            failure_indicators=['failed', 'error', 'quota exceeded', 'invalid prompt'],
            latency_threshold_ms=60000,  # Image gen can be slow
            weight=1.2,  # High-value tool
        ),
        'content_writer_agent': SuccessSignal(
            tool_name='content_writer_agent',
            success_indicators=['content', 'article', 'blog', 'written', 'draft'],
            failure_indicators=['failed', 'error', 'empty content'],
            latency_threshold_ms=45000,
            weight=1.2,
        ),
        'video_generation_agent': SuccessSignal(
            tool_name='video_generation_agent',
            success_indicators=['video_id', 'generated', 'url', 'rendering'],
            failure_indicators=['failed', 'error', 'quota exceeded'],
            latency_threshold_ms=120000,  # Videos take longer
            weight=1.5,  # High-value tool
        ),
        # Agent Orchestration Tools
        'universal_agent_tool': SuccessSignal(
            tool_name='universal_agent_tool',
            success_indicators=['result', 'response', 'completed', 'executed'],
            failure_indicators=['agent not found', 'execution failed', 'timeout'],
            latency_threshold_ms=60000,
            weight=1.0,
        ),
        'reasoning_engine_tool': SuccessSignal(
            tool_name='reasoning_engine_tool',
            success_indicators=['conclusion', 'analysis', 'reasoning', 'thought'],
            failure_indicators=['failed', 'error', 'no conclusion'],
            latency_threshold_ms=30000,
            weight=1.3,  # Strategic tool
        ),
        # System Health Tools
        'body_vitals_tool': SuccessSignal(
            tool_name='body_vitals_tool',
            success_indicators=['vitals', 'status', 'healthy', 'metrics'],
            failure_indicators=['error', 'unreachable', 'timeout'],
            latency_threshold_ms=5000,
            min_result_size=5,
        ),
        'system_alerts_tool': SuccessSignal(
            tool_name='system_alerts_tool',
            success_indicators=['alerts', 'status', 'notifications'],
            failure_indicators=['error', 'failed'],
            latency_threshold_ms=3000,
        ),
        # Intelligence Tools
        'predictions_tool': SuccessSignal(
            tool_name='predictions_tool',
            success_indicators=['prediction', 'confidence', 'forecast'],
            failure_indicators=['no predictions', 'error', 'insufficient data'],
            latency_threshold_ms=10000,
            weight=1.1,
        ),
        'gates_tool': SuccessSignal(
            tool_name='gates_tool',
            success_indicators=['gate', 'passed', 'ready', 'status'],
            failure_indicators=['failed', 'blocked', 'error'],
            latency_threshold_ms=5000,
        ),
        # Business Research Tools
        'competitor_analysis_agent': SuccessSignal(
            tool_name='competitor_analysis_agent',
            success_indicators=['competitors', 'analysis', 'market', 'insights'],
            failure_indicators=['not found', 'error', 'empty'],
            latency_threshold_ms=45000,
            weight=1.2,
        ),
        'customer_research_agent': SuccessSignal(
            tool_name='customer_research_agent',
            success_indicators=['customers', 'personas', 'research', 'segments'],
            failure_indicators=['not found', 'error', 'empty'],
            latency_threshold_ms=45000,
            weight=1.2,
        ),
        # Workspace & Execution Tools
        'workspace_tool': SuccessSignal(
            tool_name='workspace_tool',
            success_indicators=['created', 'updated', 'workspace', 'file'],
            failure_indicators=['error', 'failed', 'permission denied'],
            latency_threshold_ms=10000,
        ),
        # Human Decision Tools
        'human_decisions_tool': SuccessSignal(
            tool_name='human_decisions_tool',
            success_indicators=['decisions', 'pending', 'resolved', 'items'],
            failure_indicators=['error', 'failed'],
            latency_threshold_ms=5000,
        ),
        # Gateway tools (Session 1079)
        'governance_tool': SuccessSignal(
            tool_name='governance_tool',
            success_indicators=['decisions', 'pending', 'resolved', 'items', 'attention', 'triage'],
            failure_indicators=['error', 'failed'],
            latency_threshold_ms=5000,
        ),
        'work_tool': SuccessSignal(
            tool_name='work_tool',
            success_indicators=['initiative', 'stage', 'action_item', 'pipeline'],
            failure_indicators=['error', 'failed', 'not found'],
            latency_threshold_ms=5000,
        ),
        'content_tool': SuccessSignal(
            tool_name='content_tool',
            success_indicators=['content', 'blog', 'deliverable', 'published'],
            failure_indicators=['error', 'failed'],
            latency_threshold_ms=10000,
        ),
        'intelligence_tool': SuccessSignal(
            tool_name='intelligence_tool',
            success_indicators=['results', 'predictions', 'alerts', 'briefs'],
            failure_indicators=['error', 'failed', 'no data'],
            latency_threshold_ms=15000,
        ),
        'ops_tool': SuccessSignal(
            tool_name='ops_tool',
            success_indicators=['version', 'slo', 'status', 'healthy'],
            failure_indicators=['error', 'breach', 'failed'],
            latency_threshold_ms=5000,
        ),
    }

    def __init__(self, lookback_days: int = 7):
        """
        Initialize the orchestrator.

        Args:
            lookback_days: How many days of data to analyze
        """
        self.lookback_days = lookback_days
        self.cutoff = timezone.now() - timedelta(days=lookback_days)

    def analyze_tool_outcomes(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze tool execution outcomes to identify patterns.

        Args:
            agent_name: Optional filter for specific agent

        Returns:
            Dict with analysis results
        """
        from core.models_tool_calls import ToolCallRecord

        query = ToolCallRecord.objects.filter(created_at__gte=self.cutoff)
        if agent_name:
            query = query.filter(agent_name=agent_name)

        # Get success rates by tool
        tool_stats = query.values('tool_name').annotate(
            total=Count('id'),
            successes=Count('id', filter=Q(success=True)),
            failures=Count('id', filter=Q(success=False)),
            avg_latency=Avg('latency_ms'),
        ).order_by('-total')

        # Get success rates by agent
        agent_stats = query.values('agent_name').annotate(
            total=Count('id'),
            successes=Count('id', filter=Q(success=True)),
            avg_latency=Avg('latency_ms'),
        ).order_by('-total')

        # Identify problematic combinations (agent + tool with low success)
        problem_combos = query.values('agent_name', 'tool_name').annotate(
            total=Count('id'),
            successes=Count('id', filter=Q(success=True)),
        ).filter(total__gte=5).order_by('successes')[:10]

        return {
            'tool_stats': list(tool_stats),
            'agent_stats': list(agent_stats),
            'problem_combinations': list(problem_combos),
            'total_records': query.count(),
            'overall_success_rate': self._calculate_success_rate(query),
        }

    def analyze_decision_outcomes(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze decision outcomes to identify patterns.

        Args:
            agent_name: Optional filter for specific agent

        Returns:
            Dict with analysis results
        """
        from core.models_decision_records import DecisionRecord

        query = DecisionRecord.objects.filter(created_at__gte=self.cutoff)
        if agent_name:
            query = query.filter(agent_name=agent_name)

        # Only look at decisions with outcomes marked
        evaluated = query.exclude(was_successful__isnull=True)

        # Success rates by decision type
        type_stats = evaluated.values('decision_type').annotate(
            total=Count('id'),
            successes=Count('id', filter=Q(was_successful=True)),
            avg_confidence=Avg('confidence'),
        ).order_by('-total')

        # Confidence vs actual success correlation
        high_confidence = evaluated.filter(confidence__gte=0.8)
        high_conf_success = high_confidence.filter(was_successful=True).count()
        high_conf_total = high_confidence.count()

        low_confidence = evaluated.filter(confidence__lt=0.5)
        low_conf_success = low_confidence.filter(was_successful=True).count()
        low_conf_total = low_confidence.count()

        return {
            'type_stats': list(type_stats),
            'total_evaluated': evaluated.count(),
            'total_pending': query.filter(was_successful__isnull=True).count(),
            'high_confidence_accuracy': high_conf_success / high_conf_total if high_conf_total > 0 else 0,
            'low_confidence_accuracy': low_conf_success / low_conf_total if low_conf_total > 0 else 0,
        }

    def analyze_user_feedback(self, user=None) -> Dict[str, Any]:
        """
        Session 954: Analyze human attention item decisions as user feedback.

        User decisions on attention items are explicit feedback that can inform
        learning patterns. This connects the boardroom to the learning loop.

        Args:
            user: Optional user to filter by

        Returns:
            Dict with analysis results including agent/type approval rates
        """
        from core.models_human_interface import HumanAttentionItem

        # Get decided items within lookback period
        query = HumanAttentionItem.objects.filter(
            decided_at__gte=self.cutoff,
            decision__isnull=False,
        ).exclude(decision='')

        if user:
            query = query.filter(user=user)

        # Map decisions to approval/rejection
        APPROVAL_DECISIONS = ['approve', 'watch', 'act', 'verify']
        REJECTION_DECISIONS = ['ignore', 'dismiss', 'auto_dismiss', 'reject']

        # Approval rates by source agent
        agent_stats = []
        for stat in query.values('source_agent').annotate(
            total=Count('id'),
            approvals=Count('id', filter=Q(decision__in=APPROVAL_DECISIONS)),
            rejections=Count('id', filter=Q(decision__in=REJECTION_DECISIONS)),
        ).filter(total__gte=3).order_by('-total'):
            approval_rate = stat['approvals'] / stat['total'] if stat['total'] > 0 else 0
            agent_stats.append({
                'source_agent': stat['source_agent'],
                'total': stat['total'],
                'approval_rate': approval_rate,
                'approvals': stat['approvals'],
                'rejections': stat['rejections'],
            })

        # Approval rates by item type
        type_stats = []
        for stat in query.values('item_type').annotate(
            total=Count('id'),
            approvals=Count('id', filter=Q(decision__in=APPROVAL_DECISIONS)),
        ).filter(total__gte=3).order_by('-total'):
            approval_rate = stat['approvals'] / stat['total'] if stat['total'] > 0 else 0
            type_stats.append({
                'item_type': stat['item_type'],
                'total': stat['total'],
                'approval_rate': approval_rate,
            })

        # Approval rates by urgency level
        urgency_stats = []
        for stat in query.values('urgency').annotate(
            total=Count('id'),
            approvals=Count('id', filter=Q(decision__in=APPROVAL_DECISIONS)),
        ).filter(total__gte=2).order_by('-total'):
            approval_rate = stat['approvals'] / stat['total'] if stat['total'] > 0 else 0
            urgency_stats.append({
                'urgency': stat['urgency'],
                'total': stat['total'],
                'approval_rate': approval_rate,
            })

        # Overall stats
        total_decided = query.count()
        total_approved = query.filter(decision__in=APPROVAL_DECISIONS).count()
        total_rejected = query.filter(decision__in=REJECTION_DECISIONS).count()

        return {
            'agent_stats': agent_stats,
            'type_stats': type_stats,
            'urgency_stats': urgency_stats,
            'total_decided': total_decided,
            'total_approved': total_approved,
            'total_rejected': total_rejected,
            'overall_approval_rate': total_approved / total_decided if total_decided > 0 else 0,
        }

    def extract_learnings(self) -> List[ExtractedLearning]:
        """
        Extract actionable learnings from the data.

        Returns:
            List of ExtractedLearning objects
        """
        learnings = []

        # Analyze tool outcomes
        tool_analysis = self.analyze_tool_outcomes()

        # Extract learnings from tool stats
        for stat in tool_analysis['tool_stats']:
            if stat['total'] >= 10:  # Need enough data
                success_rate = stat['successes'] / stat['total'] if stat['total'] > 0 else 0

                if success_rate < 0.7:  # Problem tool
                    learnings.append(ExtractedLearning(
                        pattern_type='tool_reliability',
                        description=f"Tool '{stat['tool_name']}' has {success_rate:.0%} success rate - investigate failures",
                        confidence=min(0.9, stat['total'] / 50),  # More data = more confidence
                        applies_to_agents=[],  # Applies to all
                        pattern_data={
                            'tool_name': stat['tool_name'],
                            'success_rate': success_rate,
                            'avg_latency_ms': stat['avg_latency'],
                            'sample_size': stat['total'],
                        },
                        source_records=stat['total'],
                    ))
                elif success_rate >= 0.95:  # Reliable tool
                    learnings.append(ExtractedLearning(
                        pattern_type='tool_reliability',
                        description=f"Tool '{stat['tool_name']}' is highly reliable ({success_rate:.0%} success)",
                        confidence=min(0.9, stat['total'] / 50),
                        applies_to_agents=[],
                        pattern_data={
                            'tool_name': stat['tool_name'],
                            'success_rate': success_rate,
                            'avg_latency_ms': stat['avg_latency'],
                            'recommendation': 'prefer_this_tool',
                        },
                        source_records=stat['total'],
                    ))

        # Extract learnings from agent performance
        for stat in tool_analysis['agent_stats']:
            if stat['total'] >= 20:
                success_rate = stat['successes'] / stat['total'] if stat['total'] > 0 else 0

                if success_rate < 0.6:  # Struggling agent
                    learnings.append(ExtractedLearning(
                        pattern_type='agent_performance',
                        description=f"Agent '{stat['agent_name']}' has low tool success rate ({success_rate:.0%})",
                        confidence=min(0.85, stat['total'] / 100),
                        applies_to_agents=[stat['agent_name']],
                        pattern_data={
                            'agent_name': stat['agent_name'],
                            'success_rate': success_rate,
                            'recommendation': 'review_tool_usage',
                        },
                        source_records=stat['total'],
                    ))

        # Extract learnings from problem combinations
        for combo in tool_analysis['problem_combinations']:
            success_rate = combo['successes'] / combo['total'] if combo['total'] > 0 else 0
            if success_rate < 0.5:
                learnings.append(ExtractedLearning(
                    pattern_type='agent_tool_mismatch',
                    description=f"Agent '{combo['agent_name']}' struggles with tool '{combo['tool_name']}' ({success_rate:.0%} success)",
                    confidence=min(0.8, combo['total'] / 20),
                    applies_to_agents=[combo['agent_name']],
                    pattern_data={
                        'agent_name': combo['agent_name'],
                        'tool_name': combo['tool_name'],
                        'success_rate': success_rate,
                        'recommendation': 'consider_alternative_tool',
                    },
                    source_records=combo['total'],
                ))

        # Analyze decision outcomes
        decision_analysis = self.analyze_decision_outcomes()

        # Check confidence calibration
        high_conf_acc = decision_analysis['high_confidence_accuracy']
        low_conf_acc = decision_analysis['low_confidence_accuracy']

        if high_conf_acc < 0.8 and decision_analysis['total_evaluated'] >= 20:
            learnings.append(ExtractedLearning(
                pattern_type='confidence_calibration',
                description=f"High-confidence decisions only succeed {high_conf_acc:.0%} of the time - overconfident",
                confidence=0.7,
                applies_to_agents=[],
                pattern_data={
                    'high_confidence_accuracy': high_conf_acc,
                    'low_confidence_accuracy': low_conf_acc,
                    'recommendation': 'reduce_confidence_thresholds',
                },
                source_records=decision_analysis['total_evaluated'],
            ))

        # Session 954: Extract learnings from user feedback (boardroom decisions)
        try:
            feedback_analysis = self.analyze_user_feedback()

            # Learn from agent approval rates
            for stat in feedback_analysis.get('agent_stats', []):
                if stat['total'] >= 5:
                    approval_rate = stat['approval_rate']
                    agent_name = stat['source_agent'] or 'unknown'

                    if approval_rate < 0.3:  # User often ignores this agent's items
                        learnings.append(ExtractedLearning(
                            pattern_type='user_feedback_agent',
                            description=f"Agent '{agent_name}' items are often ignored by users ({approval_rate:.0%} approval rate)",
                            confidence=min(0.85, stat['total'] / 20),
                            applies_to_agents=[agent_name] if agent_name != 'unknown' else [],
                            pattern_data={
                                'source_agent': agent_name,
                                'approval_rate': approval_rate,
                                'total_items': stat['total'],
                                'recommendation': 'improve_relevance_filtering',
                            },
                            source_records=stat['total'],
                        ))
                    elif approval_rate >= 0.8:  # User trusts this agent
                        learnings.append(ExtractedLearning(
                            pattern_type='user_feedback_agent',
                            description=f"Agent '{agent_name}' items are highly valued by users ({approval_rate:.0%} approval rate)",
                            confidence=min(0.85, stat['total'] / 20),
                            applies_to_agents=[agent_name] if agent_name != 'unknown' else [],
                            pattern_data={
                                'source_agent': agent_name,
                                'approval_rate': approval_rate,
                                'total_items': stat['total'],
                                'recommendation': 'prioritize_this_agent',
                            },
                            source_records=stat['total'],
                        ))

            # Learn from item type approval rates
            for stat in feedback_analysis.get('type_stats', []):
                if stat['total'] >= 5:
                    approval_rate = stat['approval_rate']
                    item_type = stat['item_type']

                    if approval_rate < 0.2:  # Users rarely approve this type
                        learnings.append(ExtractedLearning(
                            pattern_type='user_feedback_type',
                            description=f"Item type '{item_type}' is rarely approved by users ({approval_rate:.0%})",
                            confidence=min(0.8, stat['total'] / 15),
                            applies_to_agents=[],
                            pattern_data={
                                'item_type': item_type,
                                'approval_rate': approval_rate,
                                'recommendation': 'reconsider_item_generation',
                            },
                            source_records=stat['total'],
                        ))
        except Exception as e:
            logger.warning(f"Failed to analyze user feedback: {e}")

        return learnings

    def persist_learnings(self, learnings: List[ExtractedLearning]) -> int:
        """
        Persist extracted learnings to LearningPattern model.

        Args:
            learnings: List of extracted learnings

        Returns:
            Number of patterns created/updated
        """
        from core.models_unified_system import LearningPattern

        count = 0
        for learning in learnings:
            # Check for existing pattern with same type and similar description
            existing = LearningPattern.objects.filter(
                pattern_type=learning.pattern_type,
                description__icontains=learning.pattern_data.get('tool_name', '')
                if 'tool_name' in learning.pattern_data else
                learning.pattern_data.get('agent_name', ''),
            ).first()

            if existing:
                # Update existing
                existing.confidence = learning.confidence
                existing.pattern_data = learning.pattern_data
                existing.applies_to_agents = learning.applies_to_agents
                existing.save()
                logger.info(f"Updated learning pattern: {existing.id}")
            else:
                # Create new
                LearningPattern.objects.create(
                    pattern_type=learning.pattern_type,
                    description=learning.description,
                    confidence=learning.confidence,
                    pattern_data=learning.pattern_data,
                    applies_to_agents=learning.applies_to_agents,
                    applies_to_query_types=[],
                )
                logger.info(f"Created learning pattern: {learning.description[:50]}")
            count += 1

        return count

    def get_learnings_for_agent(
        self,
        agent_name: str,
        max_learnings: int = 5,
        min_confidence: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Get relevant learnings for a specific agent.

        Args:
            agent_name: Name of the agent
            max_learnings: Maximum number of learnings to return
            min_confidence: Minimum confidence threshold

        Returns:
            List of learning dicts suitable for prompt injection
        """
        from core.models_unified_system import LearningPattern

        # Get patterns that apply to this agent or to all agents
        patterns = LearningPattern.objects.filter(
            is_active=True,
            confidence__gte=min_confidence,
        ).filter(
            Q(applies_to_agents__contains=[agent_name]) |
            Q(applies_to_agents=[])  # Empty means applies to all
        ).order_by('-confidence', '-updated_at')[:max_learnings]

        return [
            {
                'type': p.pattern_type,
                'description': p.description,
                'confidence': p.confidence,
                'data': p.pattern_data,
                'effectiveness': p.effectiveness_rate(),
                'id': str(p.id),  # Session 954: Include ID for tracking
            }
            for p in patterns
        ]

    def track_learning_application(
        self,
        pattern_id: str,
        was_successful: bool,
    ) -> bool:
        """
        Session 954: Track when a learning is applied and its outcome.

        This updates the times_applied and success_when_applied counters
        on LearningPattern to measure effectiveness.

        Args:
            pattern_id: UUID of the LearningPattern that was applied
            was_successful: Whether the outcome was successful

        Returns:
            True if tracking was successful
        """
        from core.models_unified_system import LearningPattern
        import uuid

        try:
            pattern_uuid = uuid.UUID(pattern_id) if isinstance(pattern_id, str) else pattern_id
            pattern = LearningPattern.objects.get(id=pattern_uuid)

            pattern.times_applied = (pattern.times_applied or 0) + 1
            if was_successful:
                pattern.success_when_applied = (pattern.success_when_applied or 0) + 1
            pattern.save(update_fields=['times_applied', 'success_when_applied', 'updated_at'])

            logger.info(f"📈 Tracked learning application: {pattern_id}, success={was_successful}")
            return True
        except LearningPattern.DoesNotExist:
            logger.warning(f"Learning pattern not found: {pattern_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to track learning application: {e}")
            return False

    def get_learning_effectiveness_stats(self) -> Dict[str, Any]:
        """
        Session 954: Get comprehensive stats on learning effectiveness.

        Returns stats for dashboard display including:
        - Total active learnings
        - Average effectiveness rate
        - Most/least effective learnings
        - Recent learnings extracted
        """
        from core.models_unified_system import LearningPattern

        active_patterns = LearningPattern.objects.filter(is_active=True)
        total_active = active_patterns.count()

        # Patterns that have been applied at least once
        applied_patterns = active_patterns.filter(times_applied__gt=0)
        applied_count = applied_patterns.count()

        # Calculate overall effectiveness
        if applied_count > 0:
            total_applied = sum(p.times_applied for p in applied_patterns)
            total_successful = sum(p.success_when_applied for p in applied_patterns)
            overall_effectiveness = total_successful / total_applied if total_applied > 0 else 0
        else:
            overall_effectiveness = 0
            total_applied = 0
            total_successful = 0

        # Most effective learnings (at least 5 applications)
        most_effective = []
        for p in applied_patterns.filter(times_applied__gte=5).order_by('-times_applied')[:5]:
            most_effective.append({
                'id': str(p.id),
                'description': p.description[:100],
                'effectiveness': p.effectiveness_rate(),
                'times_applied': p.times_applied,
                'pattern_type': p.pattern_type,
            })

        # Least effective (might need review)
        least_effective = []
        for p in applied_patterns.filter(times_applied__gte=3):
            eff = p.effectiveness_rate()
            if eff < 0.5:
                least_effective.append({
                    'id': str(p.id),
                    'description': p.description[:100],
                    'effectiveness': eff,
                    'times_applied': p.times_applied,
                    'pattern_type': p.pattern_type,
                })
        least_effective = sorted(least_effective, key=lambda x: x['effectiveness'])[:5]

        # Recently extracted learnings
        recent_learnings = []
        for p in active_patterns.order_by('-created_at')[:10]:
            recent_learnings.append({
                'id': str(p.id),
                'description': p.description[:100],
                'pattern_type': p.pattern_type,
                'confidence': p.confidence,
                'created_at': p.created_at.isoformat(),
            })

        # Stats by pattern type
        type_stats = active_patterns.values('pattern_type').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence'),
        ).order_by('-count')

        return {
            'total_active_learnings': total_active,
            'total_applied': total_applied,
            'total_successful': total_successful,
            'overall_effectiveness': overall_effectiveness,
            'applied_patterns_count': applied_count,
            'most_effective': most_effective,
            'least_effective': least_effective,
            'recent_learnings': recent_learnings,
            'by_pattern_type': list(type_stats),
            'timestamp': timezone.now().isoformat(),
        }

    def format_learnings_for_prompt(
        self,
        agent_name: str,
        max_learnings: int = 3,
    ) -> str:
        """
        Format learnings as a string for injection into agent prompts.

        Args:
            agent_name: Name of the agent
            max_learnings: Maximum number to include

        Returns:
            Formatted string for prompt injection
        """
        learnings = self.get_learnings_for_agent(agent_name, max_learnings)

        if not learnings:
            return ""

        lines = ["## System Learnings\n"]
        lines.append("Based on recent execution data, keep these patterns in mind:\n")

        for i, learning in enumerate(learnings, 1):
            confidence_str = f"({learning['confidence']:.0%} confidence)"
            lines.append(f"{i}. {learning['description']} {confidence_str}")

            # Add specific recommendations if present
            if 'recommendation' in learning.get('data', {}):
                lines.append(f"   → Recommendation: {learning['data']['recommendation']}")

        return "\n".join(lines)

    def run_learning_cycle(self) -> Dict[str, Any]:
        """
        Run a complete learning cycle: analyze → extract → persist.

        Returns:
            Summary of the cycle
        """
        logger.info("🧠 Starting learning cycle...")

        # Extract learnings
        learnings = self.extract_learnings()
        logger.info(f"📊 Extracted {len(learnings)} learnings")

        # Persist
        persisted = self.persist_learnings(learnings)
        logger.info(f"💾 Persisted {persisted} learning patterns")

        return {
            'learnings_extracted': len(learnings),
            'patterns_persisted': persisted,
            'timestamp': timezone.now().isoformat(),
        }

    def _calculate_success_rate(self, queryset) -> float:
        """Calculate overall success rate from a queryset."""
        total = queryset.count()
        if total == 0:
            return 0.0
        successes = queryset.filter(success=True).count()
        return successes / total


# Singleton instance
_orchestrator = None


def get_learning_loop_orchestrator(lookback_days: int = 7) -> LearningLoopOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LearningLoopOrchestrator(lookback_days)
    return _orchestrator
