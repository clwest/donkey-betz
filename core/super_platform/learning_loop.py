"""
Learning Loop Service - Continuous Improvement from Outcomes
============================================================

Session 265: Phase 5 - Learning Loop

This service enables the Super Platform to learn from outcomes:
1. Outcome Recording - Track success/failure of coordinator responses
2. Agent Performance - Which agents excel at which query types
3. Pattern Detection - Discover what works for users
4. Adaptive Selection - Improve agent selection over time
5. User Personalization - Learn individual preferences

The Learning Loop:
    Action → Outcome → Pattern → Adaptation → Better Action

Integration with existing systems:
- PatternDiscoveryEngine (core/learning_engine.py)
- AgentLearningService (core/services/agent_learning_service.py)
- SciFi Evolution System (agent XP and leveling)
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q, F
from django.core.cache import cache

logger = logging.getLogger(__name__)


class OutcomeType(Enum):
    """Types of outcomes for learning."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    USER_SATISFIED = "user_satisfied"
    USER_UNSATISFIED = "user_unsatisfied"


class FeedbackType(Enum):
    """Types of user feedback."""
    EXPLICIT_POSITIVE = "explicit_positive"  # User said it was good
    EXPLICIT_NEGATIVE = "explicit_negative"  # User said it was bad
    IMPLICIT_POSITIVE = "implicit_positive"  # User used the result
    IMPLICIT_NEGATIVE = "implicit_negative"  # User ignored/retried
    ENGAGEMENT = "engagement"  # User engaged further


@dataclass
class OutcomeRecord:
    """Records an outcome for learning."""
    id: str
    query_type: str
    query_text: str
    execution_mode: str
    agents_used: List[str]
    response_length: int
    execution_time_ms: int
    outcome: OutcomeType
    user_feedback: Optional[FeedbackType] = None
    confidence: float = 0.0
    spider_data_used: bool = False
    scifi_context_used: bool = False
    revenue_generated: Optional[Decimal] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=timezone.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'query_type': self.query_type,
            'query_text': self.query_text[:100],  # Truncate for storage
            'execution_mode': self.execution_mode,
            'agents_used': self.agents_used,
            'response_length': self.response_length,
            'execution_time_ms': self.execution_time_ms,
            'outcome': self.outcome.value,
            'user_feedback': self.user_feedback.value if self.user_feedback else None,
            'confidence': self.confidence,
            'spider_data_used': self.spider_data_used,
            'scifi_context_used': self.scifi_context_used,
            'revenue_generated': float(self.revenue_generated) if self.revenue_generated else None,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
        }


@dataclass
class AgentPerformance:
    """Performance metrics for an agent."""
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time_ms: float = 0.0
    avg_response_length: float = 0.0
    user_satisfaction_rate: float = 0.0
    revenue_attributed: Decimal = Decimal('0.00')
    best_query_types: List[str] = field(default_factory=list)
    worst_query_types: List[str] = field(default_factory=list)
    recent_trend: str = "stable"  # improving, stable, declining

    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions

    def to_dict(self) -> dict:
        return {
            'agent_name': self.agent_name,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'success_rate': self.success_rate(),
            'avg_execution_time_ms': self.avg_execution_time_ms,
            'avg_response_length': self.avg_response_length,
            'user_satisfaction_rate': self.user_satisfaction_rate,
            'revenue_attributed': float(self.revenue_attributed),
            'best_query_types': self.best_query_types,
            'worst_query_types': self.worst_query_types,
            'recent_trend': self.recent_trend,
        }


@dataclass
class QueryTypeStats:
    """Statistics for a query type."""
    query_type: str
    total_queries: int = 0
    avg_success_rate: float = 0.0
    best_agents: List[str] = field(default_factory=list)
    avg_execution_time_ms: float = 0.0
    user_satisfaction_rate: float = 0.0

    def to_dict(self) -> dict:
        return {
            'query_type': self.query_type,
            'total_queries': self.total_queries,
            'avg_success_rate': self.avg_success_rate,
            'best_agents': self.best_agents,
            'avg_execution_time_ms': self.avg_execution_time_ms,
            'user_satisfaction_rate': self.user_satisfaction_rate,
        }


class LearningLoopService:
    """
    The learning loop service for continuous improvement.

    This service:
    - Records outcomes from coordinator executions
    - Tracks agent performance across query types
    - Detects patterns in successful/failed interactions
    - Provides adaptive agent selection recommendations
    - Integrates with evolution system for XP rewards
    """

    # Cache settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_PREFIX = 'learning_loop:'

    # Learning thresholds
    MIN_SAMPLES_FOR_LEARNING = 5
    CONFIDENCE_THRESHOLD = 0.6
    PERFORMANCE_WINDOW_DAYS = 30

    def __init__(self, user=None):
        """Initialize the learning loop service."""
        self.user = user
        self._outcome_model = None
        self._evolution_service = None

    # ==================== Lazy Loading ====================

    @property
    def outcome_model(self):
        """Lazy load OutcomeRecord model."""
        if self._outcome_model is None:
            try:
                from core.models_unified_system import CoordinatorOutcome
                self._outcome_model = CoordinatorOutcome
            except ImportError:
                logger.warning("CoordinatorOutcome model not available")
        return self._outcome_model

    @property
    def evolution_service(self):
        """Lazy load evolution service for XP rewards."""
        if self._evolution_service is None:
            try:
                from .scifi_integration import get_scifi_integration_service
                self._evolution_service = get_scifi_integration_service()
            except ImportError:
                logger.warning("SciFi integration service not available")
        return self._evolution_service

    # ==================== Outcome Recording ====================

    def record_outcome(
        self,
        query_type: str,
        query_text: str,
        execution_mode: str,
        agents_used: List[str],
        response: str,
        execution_time_ms: int,
        success: bool,
        classification_confidence: float = 0.0,
        spider_data_used: bool = False,
        scifi_context_used: bool = False,
        metadata: Optional[Dict] = None,
        context: Optional[Dict] = None  # Alias for metadata (Session 309 fix)
    ) -> Optional[str]:
        """
        Record an outcome from a coordinator execution.

        Args:
            query_type: Type of query (question, creation, etc.)
            query_text: Original query text
            execution_mode: How it was executed
            agents_used: List of agents involved
            response: The response given
            execution_time_ms: Execution time
            success: Whether it succeeded
            classification_confidence: Confidence in query classification
            spider_data_used: Whether spider data was used
            scifi_context_used: Whether sci-fi features were used
            metadata: Additional metadata
            context: Alias for metadata (for agent learning mixins)

        Returns:
            Outcome ID or None if failed
        """
        # Merge context into metadata if provided (Session 309 fix)
        if context and not metadata:
            metadata = context
        elif context and metadata:
            metadata = {**metadata, **context}
        import uuid

        outcome_type = OutcomeType.SUCCESS if success else OutcomeType.FAILURE

        outcome = OutcomeRecord(
            id=str(uuid.uuid4()),
            query_type=query_type,
            query_text=query_text,
            execution_mode=execution_mode,
            agents_used=agents_used,
            response_length=len(response),
            execution_time_ms=execution_time_ms,
            outcome=outcome_type,
            confidence=classification_confidence,
            spider_data_used=spider_data_used,
            scifi_context_used=scifi_context_used,
            user_id=self.user.id if self.user else None,
            metadata=metadata or {},
        )

        # Store in database if available
        if self.outcome_model:
            try:
                self._save_outcome_to_db(outcome)
            except Exception as e:
                logger.warning(f"Could not save outcome to DB: {e}")

        # Update in-memory performance cache
        self._update_performance_cache(outcome)

        # Award XP to agents on success
        if success and self.evolution_service:
            self._award_agent_xp(agents_used, outcome)

        logger.info(
            f"Recorded outcome: {outcome_type.value} for {query_type} "
            f"using {agents_used}"
        )

        return outcome.id

    def _save_outcome_to_db(self, outcome: OutcomeRecord) -> None:
        """Save outcome to database."""
        if not self.outcome_model:
            return

        self.outcome_model.objects.create(
            outcome_id=outcome.id,
            user_id=outcome.user_id,
            query_type=outcome.query_type,
            query_text=outcome.query_text[:500],
            execution_mode=outcome.execution_mode,
            agents_used=outcome.agents_used,
            response_length=outcome.response_length,
            execution_time_ms=outcome.execution_time_ms,
            outcome_type=outcome.outcome.value,
            confidence=outcome.confidence,
            spider_data_used=outcome.spider_data_used,
            scifi_context_used=outcome.scifi_context_used,
            metadata=outcome.metadata,
        )

        # Session 379: Update Agent model execution counters
        self._update_agent_execution_counts(outcome)

    # Session 379: Mapping from legacy snake_case names to proper agent names
    AGENT_NAME_MAPPING = {
        'image_generation_agent': 'ImageAgent',
        'video_generation_agent': 'VideoAgent',
        'audio_generation_agent': 'AudioAgent',
        'three_d_generation_agent': 'ThreeDAgent',
        'workflow_orchestration_agent': 'WorkflowAgent',
        'research_agent': 'ResearchAgent',
        'competitor_analysis_agent': 'CompetitorAnalysisAgent',
        'customer_research_agent': 'CustomerResearchAgent',
        'brand_strategy_agent': 'BrandStrategyAgent',
        'trend_analysis_agent': 'TrendAnalysisAgent',
        'opportunity_scoring_agent': 'OpportunityScoringAgent',
    }

    def _update_agent_execution_counts(self, outcome: OutcomeRecord) -> None:
        """
        Update the Agent model's total_executions and successful_executions.

        Session 379: Ensures Agent Overview shows accurate execution counts.
        """
        try:
            from core.models_unified_system import Agent
            from django.db.models import F

            for agent_name in outcome.agents_used:
                # Map legacy names to proper names
                proper_name = self.AGENT_NAME_MAPPING.get(agent_name, agent_name)

                # Skip non-agent entries (tools, etc.)
                if proper_name in ('web_search', 'coleadership_agent'):
                    continue

                # Try to find the agent by name
                agent = Agent.objects.filter(name=proper_name).first()
                if not agent:
                    # Try with common naming variations as fallback
                    clean_name = agent_name.replace('_agent', '').replace('_', ' ').title().replace(' ', '')
                    if not clean_name.endswith('Agent'):
                        clean_name += 'Agent'
                    agent = Agent.objects.filter(name=clean_name).first()

                if agent:
                    # Use F() for atomic increment
                    Agent.objects.filter(id=agent.id).update(
                        total_executions=F('total_executions') + 1,
                        successful_executions=F('successful_executions') + (1 if outcome.outcome == OutcomeType.SUCCESS else 0)
                    )
                    logger.debug(f"Updated execution count for {agent.name}")

        except Exception as e:
            logger.warning(f"Could not update agent execution counts: {e}")

    def _update_performance_cache(self, outcome: OutcomeRecord) -> None:
        """Update in-memory performance statistics."""
        cache_key = f"{self.CACHE_PREFIX}agent_performance"
        performance = cache.get(cache_key) or {}

        for agent in outcome.agents_used:
            if agent not in performance:
                performance[agent] = {
                    'total': 0,
                    'success': 0,
                    'total_time': 0,
                    'by_query_type': defaultdict(lambda: {'total': 0, 'success': 0}),
                }

            performance[agent]['total'] += 1
            performance[agent]['total_time'] += outcome.execution_time_ms

            if outcome.outcome == OutcomeType.SUCCESS:
                performance[agent]['success'] += 1

            # Track by query type
            qt_stats = performance[agent]['by_query_type']
            if isinstance(qt_stats, defaultdict):
                qt_stats = dict(qt_stats)
            if outcome.query_type not in qt_stats:
                qt_stats[outcome.query_type] = {'total': 0, 'success': 0}
            qt_stats[outcome.query_type]['total'] += 1
            if outcome.outcome == OutcomeType.SUCCESS:
                qt_stats[outcome.query_type]['success'] += 1
            performance[agent]['by_query_type'] = qt_stats

        cache.set(cache_key, performance, self.CACHE_TTL * 12)  # 1 hour

    def _award_agent_xp(self, agents: List[str], outcome: OutcomeRecord) -> None:
        """Award XP to agents for successful execution."""
        if not self.evolution_service:
            return

        # Base XP for successful execution
        base_xp = 10

        # Bonus for using spider data
        if outcome.spider_data_used:
            base_xp += 5

        # Bonus for fast execution
        if outcome.execution_time_ms < 1000:
            base_xp += 3

        for agent_name in agents:
            try:
                # Update agent evolution
                from core.models_unified_system import Agent, AgentEvolution

                agent = Agent.objects.filter(name=agent_name).first()
                if agent:
                    evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)
                    evolution.total_xp += base_xp

                    # Check for level up
                    old_level = evolution.current_level
                    new_level = self._calculate_level(evolution.total_xp)
                    if new_level > old_level:
                        evolution.current_level = new_level
                        logger.info(f"🎉 {agent_name} leveled up to {new_level}!")

                    evolution.save()

            except Exception as e:
                logger.debug(f"Could not award XP to {agent_name}: {e}")

    def _calculate_level(self, xp: int) -> int:
        """Calculate level from XP."""
        # XP thresholds for each level
        thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]
        for level, threshold in enumerate(thresholds):
            if xp < threshold:
                return max(1, level)
        return len(thresholds)

    def record_feedback(
        self,
        outcome_id: str,
        feedback_type: FeedbackType,
        feedback_text: Optional[str] = None
    ) -> bool:
        """
        Record user feedback for an outcome.

        Args:
            outcome_id: ID of the outcome
            feedback_type: Type of feedback
            feedback_text: Optional text feedback

        Returns:
            Success status
        """
        if not self.outcome_model:
            return False

        try:
            outcome = self.outcome_model.objects.get(outcome_id=outcome_id)
            outcome.user_feedback = feedback_type.value
            if feedback_text:
                outcome.metadata['feedback_text'] = feedback_text
            outcome.save()

            # Adjust agent performance based on feedback
            self._adjust_for_feedback(outcome, feedback_type)

            return True

        except Exception as e:
            logger.warning(f"Could not record feedback: {e}")
            return False

    def _adjust_for_feedback(self, outcome, feedback_type: FeedbackType) -> None:
        """Adjust learning based on user feedback."""
        if feedback_type in [FeedbackType.EXPLICIT_POSITIVE, FeedbackType.IMPLICIT_POSITIVE]:
            # Positive feedback - reinforce this pattern
            for agent in outcome.agents_used:
                self._reinforce_pattern(agent, outcome.query_type, positive=True)
        elif feedback_type in [FeedbackType.EXPLICIT_NEGATIVE, FeedbackType.IMPLICIT_NEGATIVE]:
            # Negative feedback - discourage this pattern
            for agent in outcome.agents_used:
                self._reinforce_pattern(agent, outcome.query_type, positive=False)

    def _reinforce_pattern(self, agent_name: str, query_type: str, positive: bool) -> None:
        """Reinforce or discourage an agent-query pattern."""
        cache_key = f"{self.CACHE_PREFIX}agent_patterns"
        patterns = cache.get(cache_key) or {}

        key = f"{agent_name}:{query_type}"
        if key not in patterns:
            patterns[key] = {'positive': 0, 'negative': 0}

        if positive:
            patterns[key]['positive'] += 1
        else:
            patterns[key]['negative'] += 1

        cache.set(cache_key, patterns, self.CACHE_TTL * 24)  # 2 hours

    # ==================== Agent Performance Analysis ====================

    def get_agent_performance(
        self,
        agent_name: str,
        days: int = 30
    ) -> AgentPerformance:
        """
        Get performance metrics for an agent.

        Args:
            agent_name: Name of the agent
            days: Number of days to analyze

        Returns:
            AgentPerformance with metrics
        """
        performance = AgentPerformance(agent_name=agent_name)

        # Check cache first
        cache_key = f"{self.CACHE_PREFIX}performance:{agent_name}"
        cached = cache.get(cache_key)
        if cached:
            # Remove computed fields that aren't constructor arguments
            cached_copy = {k: v for k, v in cached.items() if k != 'success_rate'}
            return AgentPerformance(**cached_copy)

        # Calculate from database
        if self.outcome_model:
            try:
                cutoff = timezone.now() - timedelta(days=days)
                outcomes = self.outcome_model.objects.filter(
                    agents_used__contains=[agent_name],
                    created_at__gte=cutoff,
                )

                if self.user:
                    outcomes = outcomes.filter(user=self.user)

                performance.total_executions = outcomes.count()
                performance.successful_executions = outcomes.filter(
                    outcome_type='success'
                ).count()
                performance.failed_executions = outcomes.filter(
                    outcome_type='failure'
                ).count()

                # Averages
                averages = outcomes.aggregate(
                    avg_time=Avg('execution_time_ms'),
                    avg_length=Avg('response_length'),
                )
                performance.avg_execution_time_ms = averages['avg_time'] or 0
                performance.avg_response_length = averages['avg_length'] or 0

                # Best/worst query types
                query_stats = outcomes.values('query_type').annotate(
                    total=Count('id'),
                    successes=Count('id', filter=Q(outcome_type='success'))
                )

                for qs in query_stats:
                    rate = qs['successes'] / qs['total'] if qs['total'] > 0 else 0
                    if rate >= 0.8 and qs['total'] >= 3:
                        performance.best_query_types.append(qs['query_type'])
                    elif rate <= 0.3 and qs['total'] >= 3:
                        performance.worst_query_types.append(qs['query_type'])

                # Calculate trend
                performance.recent_trend = self._calculate_trend(agent_name, days)

            except Exception as e:
                logger.warning(f"Error getting agent performance: {e}")

        # Cache result
        cache.set(cache_key, performance.to_dict(), self.CACHE_TTL)

        return performance

    def _calculate_trend(self, agent_name: str, days: int) -> str:
        """Calculate performance trend (improving, stable, declining)."""
        if not self.outcome_model:
            return "stable"

        try:
            now = timezone.now()
            mid = now - timedelta(days=days // 2)
            start = now - timedelta(days=days)

            # Recent period
            recent = self.outcome_model.objects.filter(
                agents_used__contains=[agent_name],
                created_at__gte=mid,
            )
            recent_rate = recent.filter(outcome_type='success').count() / max(recent.count(), 1)

            # Earlier period
            earlier = self.outcome_model.objects.filter(
                agents_used__contains=[agent_name],
                created_at__gte=start,
                created_at__lt=mid,
            )
            earlier_rate = earlier.filter(outcome_type='success').count() / max(earlier.count(), 1)

            if recent_rate > earlier_rate + 0.1:
                return "improving"
            elif recent_rate < earlier_rate - 0.1:
                return "declining"
            else:
                return "stable"

        except Exception:
            return "stable"

    def get_all_agent_performance(self, days: int = 30) -> List[AgentPerformance]:
        """Get performance for all agents."""
        performances = []

        # Get list of agents from outcomes
        if self.outcome_model:
            try:
                cutoff = timezone.now() - timedelta(days=days)
                agent_names = set()

                outcomes = self.outcome_model.objects.filter(created_at__gte=cutoff)
                for outcome in outcomes:
                    for agent in outcome.agents_used or []:
                        agent_names.add(agent)

                for agent_name in agent_names:
                    perf = self.get_agent_performance(agent_name, days)
                    if perf.total_executions > 0:
                        performances.append(perf)

            except Exception as e:
                logger.warning(f"Error getting all performances: {e}")

        # Sort by success rate
        performances.sort(key=lambda p: p.success_rate(), reverse=True)

        return performances

    # ==================== Adaptive Agent Selection ====================

    def recommend_agents(
        self,
        query_type: str,
        default_agents: List[str],
        limit: int = 3
    ) -> List[str]:
        """
        Recommend agents for a query type based on learned performance.

        Args:
            query_type: Type of query
            default_agents: Default agent suggestions
            limit: Max agents to return

        Returns:
            List of recommended agent names
        """
        # Get learned patterns
        cache_key = f"{self.CACHE_PREFIX}agent_patterns"
        patterns = cache.get(cache_key) or {}

        # Score agents for this query type
        agent_scores = {}

        for key, data in patterns.items():
            agent, qt = key.split(':')
            if qt == query_type:
                # Calculate score: (positive - negative) with decay
                positive = data.get('positive', 0)
                negative = data.get('negative', 0)
                score = positive - (negative * 1.5)  # Weight negatives more
                agent_scores[agent] = score

        # Add default agents with neutral score if not in patterns
        for agent in default_agents:
            if agent not in agent_scores:
                agent_scores[agent] = 0

        # Sort by score
        sorted_agents = sorted(
            agent_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top agents
        recommended = [agent for agent, score in sorted_agents[:limit]]

        # Ensure we have at least some agents
        if not recommended:
            recommended = default_agents[:limit]

        return recommended

    def get_query_type_stats(self, query_type: str, days: int = 30) -> QueryTypeStats:
        """Get statistics for a query type."""
        stats = QueryTypeStats(query_type=query_type)

        if self.outcome_model:
            try:
                cutoff = timezone.now() - timedelta(days=days)
                outcomes = self.outcome_model.objects.filter(
                    query_type=query_type,
                    created_at__gte=cutoff,
                )

                stats.total_queries = outcomes.count()
                if stats.total_queries > 0:
                    successes = outcomes.filter(outcome_type='success').count()
                    stats.avg_success_rate = successes / stats.total_queries

                    avg_time = outcomes.aggregate(avg=Avg('execution_time_ms'))['avg']
                    stats.avg_execution_time_ms = avg_time or 0

                    # Find best agents for this query type
                    agent_success = defaultdict(lambda: {'total': 0, 'success': 0})
                    for outcome in outcomes:
                        for agent in outcome.agents_used or []:
                            agent_success[agent]['total'] += 1
                            if outcome.outcome_type == 'success':
                                agent_success[agent]['success'] += 1

                    # Sort by success rate
                    sorted_agents = sorted(
                        agent_success.items(),
                        key=lambda x: x[1]['success'] / max(x[1]['total'], 1),
                        reverse=True
                    )
                    stats.best_agents = [a for a, _ in sorted_agents[:5]]

            except Exception as e:
                logger.warning(f"Error getting query type stats: {e}")

        return stats

    # ==================== Pattern Detection ====================

    def detect_patterns(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Detect patterns from outcome data.

        Returns patterns like:
        - "ImageAgent excels at creation queries (85% success)"
        - "Spider data improves accuracy by 20%"
        - "Fast responses correlate with satisfaction"
        """
        patterns = []

        if not self.outcome_model:
            return patterns

        try:
            cutoff = timezone.now() - timedelta(days=days)
            outcomes = self.outcome_model.objects.filter(created_at__gte=cutoff)

            if self.user:
                outcomes = outcomes.filter(user=self.user)

            if outcomes.count() < self.MIN_SAMPLES_FOR_LEARNING:
                return patterns

            # Pattern 1: Spider data impact
            spider_pattern = self._detect_spider_impact(outcomes)
            if spider_pattern:
                patterns.append(spider_pattern)

            # Pattern 2: Agent specialization
            agent_patterns = self._detect_agent_specializations(outcomes)
            patterns.extend(agent_patterns)

            # Pattern 3: Speed vs quality
            speed_pattern = self._detect_speed_quality_correlation(outcomes)
            if speed_pattern:
                patterns.append(speed_pattern)

            # Pattern 4: Query type success rates
            query_patterns = self._detect_query_patterns(outcomes)
            patterns.extend(query_patterns)

        except Exception as e:
            logger.warning(f"Error detecting patterns: {e}")

        return patterns

    def _detect_spider_impact(self, outcomes) -> Optional[Dict]:
        """Detect impact of spider data on success."""
        with_spider = outcomes.filter(spider_data_used=True)
        without_spider = outcomes.filter(spider_data_used=False)

        if with_spider.count() < 5 or without_spider.count() < 5:
            return None

        with_rate = with_spider.filter(outcome_type='success').count() / with_spider.count()
        without_rate = without_spider.filter(outcome_type='success').count() / without_spider.count()

        impact = (with_rate - without_rate) * 100

        if abs(impact) > 5:
            return {
                'type': 'spider_data_impact',
                'description': f"Spider data {'improves' if impact > 0 else 'decreases'} success rate by {abs(impact):.1f}%",
                'impact': impact,
                'confidence': min(0.9, (with_spider.count() + without_spider.count()) / 100),
                'recommendation': 'Enable spider data for better results' if impact > 0 else 'Review spider data usage',
            }

        return None

    def _detect_agent_specializations(self, outcomes) -> List[Dict]:
        """Detect which agents excel at which query types."""
        patterns = []

        # Group by agent and query type
        agent_qt_stats = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'success': 0}))

        for outcome in outcomes:
            for agent in outcome.agents_used or []:
                agent_qt_stats[agent][outcome.query_type]['total'] += 1
                if outcome.outcome_type == 'success':
                    agent_qt_stats[agent][outcome.query_type]['success'] += 1

        # Find specializations
        for agent, qt_stats in agent_qt_stats.items():
            for qt, stats in qt_stats.items():
                if stats['total'] >= 5:
                    rate = stats['success'] / stats['total']
                    if rate >= 0.8:
                        patterns.append({
                            'type': 'agent_specialization',
                            'agent': agent,
                            'query_type': qt,
                            'success_rate': rate,
                            'sample_size': stats['total'],
                            'description': f"{agent} excels at {qt} queries ({rate*100:.0f}% success)",
                            'confidence': min(0.9, stats['total'] / 50),
                        })

        return patterns[:10]  # Limit to top 10

    def _detect_speed_quality_correlation(self, outcomes) -> Optional[Dict]:
        """Detect correlation between response speed and outcome."""
        fast_outcomes = outcomes.filter(execution_time_ms__lt=2000)
        slow_outcomes = outcomes.filter(execution_time_ms__gte=5000)

        if fast_outcomes.count() < 5 or slow_outcomes.count() < 5:
            return None

        fast_rate = fast_outcomes.filter(outcome_type='success').count() / fast_outcomes.count()
        slow_rate = slow_outcomes.filter(outcome_type='success').count() / slow_outcomes.count()

        diff = fast_rate - slow_rate

        if abs(diff) > 0.1:
            return {
                'type': 'speed_correlation',
                'description': f"{'Fast' if diff > 0 else 'Slow'} responses have {abs(diff)*100:.0f}% higher success",
                'fast_success_rate': fast_rate,
                'slow_success_rate': slow_rate,
                'recommendation': 'Optimize for speed' if diff > 0 else 'Take time for quality',
            }

        return None

    def _detect_query_patterns(self, outcomes) -> List[Dict]:
        """Detect patterns for query types."""
        patterns = []

        qt_stats = outcomes.values('query_type').annotate(
            total=Count('id'),
            successes=Count('id', filter=Q(outcome_type='success')),
            avg_time=Avg('execution_time_ms'),
        )

        for stats in qt_stats:
            if stats['total'] >= 5:
                rate = stats['successes'] / stats['total']
                patterns.append({
                    'type': 'query_type_stats',
                    'query_type': stats['query_type'],
                    'success_rate': rate,
                    'sample_size': stats['total'],
                    'avg_time_ms': stats['avg_time'],
                    'description': f"{stats['query_type']} queries: {rate*100:.0f}% success ({stats['total']} samples)",
                })

        return patterns

    # ==================== Integration Helpers ====================

    def get_prompt_context(self) -> str:
        """Get learning context for prompt injection."""
        try:
            patterns = self.detect_patterns(days=7)

            if not patterns:
                return ""

            parts = ["\n## Learning Insights\n"]

            for pattern in patterns[:3]:
                if pattern['type'] == 'agent_specialization':
                    parts.append(f"- {pattern['description']}")
                elif pattern['type'] == 'spider_data_impact':
                    parts.append(f"- {pattern['description']}")

            return "\n".join(parts) + "\n"

        except Exception as e:
            logger.warning(f"Could not get learning context: {e}")
            return ""

    def get_learning_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get a summary of learning metrics."""
        summary = {
            'total_outcomes': 0,
            'success_rate': 0.0,
            'top_agents': [],
            'patterns_detected': 0,
            'query_type_breakdown': {},
        }

        if self.outcome_model:
            try:
                cutoff = timezone.now() - timedelta(days=days)
                outcomes = self.outcome_model.objects.filter(created_at__gte=cutoff)

                if self.user:
                    outcomes = outcomes.filter(user=self.user)

                summary['total_outcomes'] = outcomes.count()
                if summary['total_outcomes'] > 0:
                    successes = outcomes.filter(outcome_type='success').count()
                    summary['success_rate'] = successes / summary['total_outcomes']

                # Top agents
                performances = self.get_all_agent_performance(days)
                summary['top_agents'] = [
                    p.to_dict() for p in performances[:5]
                ]

                # Patterns
                patterns = self.detect_patterns(days)
                summary['patterns_detected'] = len(patterns)

                # Query type breakdown
                qt_stats = outcomes.values('query_type').annotate(
                    count=Count('id')
                )
                summary['query_type_breakdown'] = {
                    s['query_type']: s['count'] for s in qt_stats
                }

            except Exception as e:
                logger.warning(f"Error getting learning summary: {e}")

        return summary


# Singleton instance
_learning_loop_service = None


def get_learning_loop_service(user=None) -> LearningLoopService:
    """Get the LearningLoopService instance."""
    global _learning_loop_service
    if _learning_loop_service is None or user is not None:
        _learning_loop_service = LearningLoopService(user)
    return _learning_loop_service
