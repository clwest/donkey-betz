"""
Feedback Loop Engine
Session 744 Phase 5: Close the feedback loop for continuous improvement.

This service:
1. Mines performance metrics from AgentExecution and AgentExecutionMemory
2. Computes agent effectiveness scores based on success rates, execution times
3. Identifies best agents for specific task types
4. Provides recommendations to improve agent selection
5. Enables auto-tuning based on historical performance

The goal is to make the system self-improving by learning from past executions
and user feedback, adjusting agent behavior and routing accordingly.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import timedelta
from collections import defaultdict
from django.utils import timezone
from django.db.models import Count, Avg, F, Q, Sum, StdDev

logger = logging.getLogger(__name__)


class FeedbackLoopEngine:
    """
    Session 744 Phase 5: Mines feedback and performance data for continuous improvement.

    Usage:
        from core.services.feedback_loop_engine import get_feedback_loop_engine

        engine = get_feedback_loop_engine()
        feedback = engine.get_feedback_for_agent('ResearchAgent', task='analyze trends')
    """

    # Performance thresholds for classification
    EXCELLENT_SUCCESS_RATE = 0.95
    GOOD_SUCCESS_RATE = 0.80
    POOR_SUCCESS_RATE = 0.60

    # Execution time thresholds (milliseconds)
    FAST_EXECUTION_MS = 5000
    SLOW_EXECUTION_MS = 30000

    # Minimum executions for reliable metrics
    MIN_EXECUTIONS_FOR_METRICS = 3

    def __init__(self):
        self._agent_execution_model = None
        self._execution_memory_model = None
        self._agent_model = None
        self._agent_learning_model = None

    @property
    def AgentExecution(self):
        """Lazy-load AgentExecution model."""
        if self._agent_execution_model is None:
            from core.models_unified_system import AgentExecution
            self._agent_execution_model = AgentExecution
        return self._agent_execution_model

    @property
    def AgentExecutionMemory(self):
        """Lazy-load AgentExecutionMemory model."""
        if self._execution_memory_model is None:
            from core.models_agent_memory import AgentExecutionMemory
            self._execution_memory_model = AgentExecutionMemory
        return self._execution_memory_model

    @property
    def Agent(self):
        """Lazy-load Agent model."""
        if self._agent_model is None:
            from core.models_unified_system import Agent
            self._agent_model = Agent
        return self._agent_model

    @property
    def AgentLearning(self):
        """Lazy-load AgentLearning model."""
        if self._agent_learning_model is None:
            from core.models_unified_system import AgentLearning
            self._agent_learning_model = AgentLearning
        return self._agent_learning_model

    def get_feedback_for_agent(
        self,
        agent_name: str,
        task: str = '',
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive feedback context for an agent.

        This combines:
        - Historical success rate
        - Average execution time
        - Task type performance
        - User ratings (if available)
        - Improvement recommendations

        Args:
            agent_name: Name of the agent
            task: Current task description (for task-type matching)
            days_back: How far back to look for data

        Returns:
            Dict with performance metrics and recommendations
        """
        try:
            since = timezone.now() - timedelta(days=days_back)

            feedback = {
                'agent_name': agent_name,
                'success_rate': None,
                'avg_execution_time_ms': None,
                'total_executions': 0,
                'recent_executions': 0,
                'performance_rating': 'unknown',
                'task_type_performance': {},
                'user_rating_avg': None,
                'speed_rating': 'unknown',
                'reliability_score': 0.0,
                'recommendations': [],
                'alternatives': [],
                'summary': '',
                'has_feedback': False,
            }

            # 1. Get AgentExecution metrics
            exec_stats = self._get_execution_stats(agent_name, since)
            if exec_stats:
                feedback.update(exec_stats)

            # 2. Get AgentExecutionMemory metrics (more detailed)
            memory_stats = self._get_memory_stats(agent_name, since)
            if memory_stats:
                # Merge memory stats, preferring memory data where available
                if memory_stats.get('user_rating_avg'):
                    feedback['user_rating_avg'] = memory_stats['user_rating_avg']
                if memory_stats.get('task_type_performance'):
                    feedback['task_type_performance'] = memory_stats['task_type_performance']

            # 2b. Get PA content review feedback from AgentMemory
            try:
                from core.models_unified_system import AgentMemory
                agent_obj = self.Agent.objects.filter(name=agent_name).first()
                if agent_obj:
                    pa_reviews = list(
                        AgentMemory.objects.filter(
                            agent=agent_obj,
                            memory_type='feedback',
                            tags__contains=['pa_review'],
                            created_at__gte=since,
                        ).order_by('-created_at')[:5].values(
                            'title', 'content', 'valence', 'created_at'
                        )
                    )
                    if pa_reviews:
                        feedback['pa_review_feedback'] = pa_reviews
                        counts = defaultdict(int)
                        for r in pa_reviews:
                            counts[r['valence']] += 1
                        parts = []
                        if counts['positive']:
                            parts.append(f"{counts['positive']} published")
                        if counts['negative']:
                            parts.append(f"{counts['negative']} archived")
                        if counts['neutral']:
                            parts.append(f"{counts['neutral']} revised")
                        feedback['pa_review_summary'] = (
                            f"{len(pa_reviews)} PA reviews: {', '.join(parts)}"
                        )
            except Exception as e:
                logger.debug(f"PA review feedback lookup failed for {agent_name}: {e}")

            # 3. Calculate performance rating
            feedback['performance_rating'] = self._calculate_performance_rating(
                feedback['success_rate'],
                feedback['total_executions']
            )

            # 4. Calculate speed rating
            feedback['speed_rating'] = self._calculate_speed_rating(
                feedback['avg_execution_time_ms']
            )

            # 5. Calculate reliability score (0.0 to 1.0)
            feedback['reliability_score'] = self._calculate_reliability_score(feedback)

            # 6. Get task-specific recommendations
            if task:
                task_type = self._detect_task_type(task)
                feedback['recommendations'] = self._get_recommendations(
                    agent_name, feedback, task_type
                )
                feedback['alternatives'] = self._get_alternative_agents(
                    agent_name, task_type, since
                )

            # 7. Build summary
            feedback['summary'] = self._build_feedback_summary(feedback)
            feedback['has_feedback'] = feedback['total_executions'] >= self.MIN_EXECUTIONS_FOR_METRICS

            if feedback['has_feedback']:
                logger.info(
                    f"📊 [Session 744] Feedback for {agent_name}: "
                    f"success={feedback['success_rate']*100:.0f}%, "
                    f"reliability={feedback['reliability_score']:.2f}, "
                    f"rating={feedback['performance_rating']}"
                )

            return feedback

        except Exception as e:
            logger.error(f"Failed to get feedback for {agent_name}: {e}")
            return {
                'agent_name': agent_name,
                'has_feedback': False,
                'error': str(e),
            }

    def _get_execution_stats(self, agent_name: str, since) -> Optional[Dict[str, Any]]:
        """Get stats from AgentExecution model."""
        try:
            executions = self.AgentExecution.objects.filter(
                agent__name=agent_name,
                created_at__gte=since
            )

            total = executions.count()
            if total == 0:
                return None

            completed = executions.filter(status='completed').count()
            failed = executions.filter(status='failed').count()

            # Calculate average execution time
            avg_time = executions.filter(
                execution_time_ms__isnull=False
            ).aggregate(avg=Avg('execution_time_ms'))['avg']

            return {
                'total_executions': total,
                'recent_executions': total,
                'success_rate': completed / total if total > 0 else 0,
                'failure_count': failed,
                'avg_execution_time_ms': avg_time,
            }

        except Exception as e:
            logger.debug(f"Error getting execution stats: {e}")
            return None

    def _get_memory_stats(self, agent_name: str, since) -> Optional[Dict[str, Any]]:
        """Get stats from AgentExecutionMemory model."""
        try:
            memories = self.AgentExecutionMemory.objects.filter(
                agent_name=agent_name,
                execution_date__gte=since
            )

            total = memories.count()
            if total == 0:
                return None

            # Average success score
            avg_success = memories.aggregate(avg=Avg('success_score'))['avg']

            # Average user rating (if any)
            rated = memories.exclude(user_rating__isnull=True)
            avg_rating = rated.aggregate(avg=Avg('user_rating'))['avg'] if rated.exists() else None

            # Performance by task type
            task_performance = {}
            task_stats = memories.values('task_type').annotate(
                count=Count('id'),
                avg_success=Avg('success_score'),
                avg_time=Avg('execution_time_seconds')
            ).order_by('-count')

            for stat in task_stats:
                task_performance[stat['task_type']] = {
                    'executions': stat['count'],
                    'success_rate': stat['avg_success'],
                    'avg_time_seconds': stat['avg_time'],
                }

            return {
                'memory_executions': total,
                'avg_success_score': avg_success,
                'user_rating_avg': avg_rating,
                'task_type_performance': task_performance,
            }

        except Exception as e:
            logger.debug(f"Error getting memory stats: {e}")
            return None

    def _calculate_performance_rating(
        self,
        success_rate: Optional[float],
        total_executions: int
    ) -> str:
        """Calculate overall performance rating."""
        if success_rate is None or total_executions < self.MIN_EXECUTIONS_FOR_METRICS:
            return 'insufficient_data'

        if success_rate >= self.EXCELLENT_SUCCESS_RATE:
            return 'excellent'
        elif success_rate >= self.GOOD_SUCCESS_RATE:
            return 'good'
        elif success_rate >= self.POOR_SUCCESS_RATE:
            return 'needs_improvement'
        else:
            return 'poor'

    def _calculate_speed_rating(self, avg_time_ms: Optional[float]) -> str:
        """Calculate speed rating based on execution time."""
        if avg_time_ms is None:
            return 'unknown'

        if avg_time_ms <= self.FAST_EXECUTION_MS:
            return 'fast'
        elif avg_time_ms <= self.SLOW_EXECUTION_MS:
            return 'normal'
        else:
            return 'slow'

    def _calculate_reliability_score(self, feedback: Dict[str, Any]) -> float:
        """
        Calculate a 0.0-1.0 reliability score based on multiple factors.

        Factors:
        - Success rate (40% weight)
        - Execution count confidence (20% weight)
        - Speed (20% weight)
        - User rating if available (20% weight)
        """
        score = 0.0

        # Success rate factor (40%)
        success_rate = feedback.get('success_rate')
        if success_rate is not None:
            score += success_rate * 0.4

        # Execution count confidence (20%)
        # More executions = more confidence
        total = feedback.get('total_executions', 0)
        if total >= 20:
            score += 0.2
        elif total >= 10:
            score += 0.15
        elif total >= 5:
            score += 0.1
        elif total >= 3:
            score += 0.05

        # Speed factor (20%)
        speed = feedback.get('speed_rating', 'unknown')
        if speed == 'fast':
            score += 0.2
        elif speed == 'normal':
            score += 0.15
        elif speed == 'slow':
            score += 0.05

        # User rating factor (20%)
        user_rating = feedback.get('user_rating_avg')
        if user_rating is not None:
            # Convert 1-5 scale to 0-0.2
            score += (user_rating / 5.0) * 0.2
        else:
            # No user rating - give partial credit based on success rate
            if success_rate is not None:
                score += success_rate * 0.1

        return min(1.0, score)

    def _detect_task_type(self, task: str) -> str:
        """Detect task type from task text."""
        if not task:
            return 'other'
        task_lower = task.lower()

        if any(w in task_lower for w in ['create', 'generate', 'make', 'design', 'build']):
            return 'creation'
        elif any(w in task_lower for w in ['edit', 'modify', 'change', 'update', 'fix']):
            return 'editing'
        elif any(w in task_lower for w in ['research', 'analyze', 'find', 'search', 'investigate']):
            return 'research'
        elif any(w in task_lower for w in ['write', 'draft', 'compose', 'blog', 'article']):
            return 'writing'
        elif any(w in task_lower for w in ['review', 'audit', 'check', 'evaluate']):
            return 'review'
        else:
            return 'other'

    def _get_recommendations(
        self,
        agent_name: str,
        feedback: Dict[str, Any],
        task_type: str
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Based on performance rating
        rating = feedback.get('performance_rating', 'unknown')
        if rating == 'poor':
            recommendations.append(
                f"Consider alternative agents for {task_type} tasks - this agent has low success rate"
            )
        elif rating == 'needs_improvement':
            recommendations.append(
                "Success rate could be improved - review failed executions for patterns"
            )

        # Based on speed
        speed = feedback.get('speed_rating', 'unknown')
        if speed == 'slow':
            recommendations.append(
                "Execution time is high - consider simpler prompts or task decomposition"
            )

        # Based on task type performance
        task_perf = feedback.get('task_type_performance', {}).get(task_type)
        if task_perf:
            if task_perf.get('success_rate', 0) < self.GOOD_SUCCESS_RATE:
                recommendations.append(
                    f"This agent underperforms on {task_type} tasks specifically"
                )

        # Positive recommendations
        if rating == 'excellent':
            recommendations.append(
                f"This agent excels at its tasks - good choice for {task_type}"
            )

        return recommendations[:3]  # Max 3 recommendations

    def _get_alternative_agents(
        self,
        agent_name: str,
        task_type: str,
        since
    ) -> List[Dict[str, Any]]:
        """Find alternative agents that perform better for this task type."""
        try:
            # Get agents with good performance on this task type
            alternatives = []

            # Query AgentExecutionMemory for task type performance
            task_performers = self.AgentExecutionMemory.objects.filter(
                task_type=task_type,
                execution_date__gte=since
            ).exclude(
                agent_name=agent_name
            ).values('agent_name').annotate(
                count=Count('id'),
                avg_success=Avg('success_score')
            ).filter(
                count__gte=self.MIN_EXECUTIONS_FOR_METRICS,
                avg_success__gte=self.GOOD_SUCCESS_RATE
            ).order_by('-avg_success')[:3]

            for perf in task_performers:
                alternatives.append({
                    'agent_name': perf['agent_name'],
                    'success_rate': perf['avg_success'],
                    'executions': perf['count'],
                })

            return alternatives

        except Exception as e:
            logger.debug(f"Error finding alternatives: {e}")
            return []

    def _build_feedback_summary(self, feedback: Dict[str, Any]) -> str:
        """Build a concise summary for prompt injection."""
        parts = []

        # Performance rating
        rating = feedback.get('performance_rating', 'unknown')
        if rating != 'unknown' and rating != 'insufficient_data':
            parts.append(f"Performance: {rating}")

        # Success rate
        success_rate = feedback.get('success_rate')
        if success_rate is not None:
            parts.append(f"Success rate: {success_rate*100:.0f}%")

        # Speed
        speed = feedback.get('speed_rating', 'unknown')
        if speed != 'unknown':
            parts.append(f"Speed: {speed}")

        # Reliability
        reliability = feedback.get('reliability_score', 0)
        if reliability > 0:
            parts.append(f"Reliability: {reliability:.0%}")

        return " | ".join(parts) if parts else ""

    def get_system_performance_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get overall system performance summary.

        Returns aggregate metrics across all agents.
        """
        try:
            since = timezone.now() - timedelta(days=days_back)

            # Overall execution stats
            total_executions = self.AgentExecution.objects.filter(
                created_at__gte=since
            ).count()

            completed = self.AgentExecution.objects.filter(
                created_at__gte=since,
                status='completed'
            ).count()

            # Best performing agents.
            # Arc I-0100 P4 §4.2 F1 fold: exclude PA meta-agent rows —
            # per-agent success-rate rankings treat PA as a router-agent
            # dispatch target when it isn't.
            best_agents = self.AgentExecution.objects.filter(
                created_at__gte=since
            ).exclude(agent__name='PersonalAssistant').values('agent__name').annotate(
                total=Count('id'),
                successes=Count('id', filter=Q(status='completed'))
            ).filter(total__gte=self.MIN_EXECUTIONS_FOR_METRICS).annotate(
                success_rate=F('successes') * 1.0 / F('total')
            ).order_by('-success_rate')[:5]

            # Most active agents (exclude PA per §4.2 F1 fold).
            most_active = self.AgentExecution.objects.filter(
                created_at__gte=since
            ).exclude(agent__name='PersonalAssistant').values('agent__name').annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            # Agents needing attention — low success rate (exclude PA per §4.2 F1 fold).
            needs_attention = self.AgentExecution.objects.filter(
                created_at__gte=since
            ).exclude(agent__name='PersonalAssistant').values('agent__name').annotate(
                total=Count('id'),
                failures=Count('id', filter=Q(status='failed'))
            ).filter(
                total__gte=self.MIN_EXECUTIONS_FOR_METRICS,
                failures__gte=1
            ).annotate(
                failure_rate=F('failures') * 1.0 / F('total')
            ).filter(failure_rate__gte=0.2).order_by('-failure_rate')[:5]

            return {
                'period_days': days_back,
                'total_executions': total_executions,
                'overall_success_rate': completed / total_executions if total_executions > 0 else 0,
                'best_performers': list(best_agents),
                'most_active': list(most_active),
                'needs_attention': list(needs_attention),
            }

        except Exception as e:
            logger.error(f"Failed to get system performance: {e}")
            return {'error': str(e)}

    def record_user_feedback(
        self,
        execution_id: str,
        user_rating: int,
        feedback_text: str = ''
    ) -> bool:
        """
        Record explicit user feedback for an execution.

        Args:
            execution_id: UUID of the AgentExecution
            user_rating: 1-5 star rating
            feedback_text: Optional text feedback

        Returns:
            True if feedback was recorded
        """
        try:
            # Find the corresponding AgentExecutionMemory
            memory = self.AgentExecutionMemory.objects.filter(
                id=execution_id
            ).first()

            if memory:
                memory.user_rating = max(1, min(5, user_rating))  # Clamp 1-5
                if feedback_text:
                    memory.user_feedback = feedback_text
                memory.save()
                logger.info(f"📝 Recorded user feedback: {user_rating} stars for {memory.agent_name}")
                return True

            # Fallback: try to find by recent execution
            logger.warning(f"AgentExecutionMemory not found for execution_id: {execution_id}")
            return False

        except Exception as e:
            logger.error(f"Failed to record user feedback: {e}")
            return False


# Singleton instance
_feedback_loop_engine: Optional[FeedbackLoopEngine] = None


def get_feedback_loop_engine() -> FeedbackLoopEngine:
    """Get the singleton FeedbackLoopEngine instance."""
    global _feedback_loop_engine
    if _feedback_loop_engine is None:
        _feedback_loop_engine = FeedbackLoopEngine()
    return _feedback_loop_engine
