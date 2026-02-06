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
    DEFAULT_SUCCESS_SIGNALS = {
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
            }
            for p in patterns
        ]

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
