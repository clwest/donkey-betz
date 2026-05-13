"""
Agent Execution Learning Bridge
Learns from agent execution outcomes to improve future agent selection and performance

Session 1115 batch-10: refactored to inherit from the `LearningBridge` ABC
(third concrete migration). Public `process_execution` kept as a
back-compat shim so the existing `on_agent_execution_completed` signal
handler keeps working unchanged.
"""

import logging
from typing import Any, Dict, List

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F

from core.learning_bridges.base import LearningBridge
from core.models_unified_system import AgentExecution, UserAgentLearning

logger = logging.getLogger(__name__)


class AgentExecutionLearningLoop(LearningBridge):
    """
    Learns from every agent execution to optimize future performance

    Tracks:
    - Which agents perform best for which tasks
    - Execution time patterns
    - Success/failure factors
    - Cost-effectiveness
    - User-specific agent performance

    ABC contract mapping:
      - `process_event(exec)` wraps the original entry (gates on
        `status in ('completed', 'failed')`).
      - `_extract_patterns(exec)` computes performance metrics + success
        boolean, threads the AgentExecution instance through `_exec`.
      - `_update_learning(patterns)` calls the four original update
        methods (user perf, task-type, aggregate metrics, orchestrator).
      - `_generate_insights(patterns)` derives human-readable strings.
    """

    def __init__(self):
        super().__init__(bridge_name='agent_execution')

    # ------------------------------------------------------------------
    # ABC contract
    # ------------------------------------------------------------------
    def process_event(self, event_data: Any) -> Dict:
        """Process a finished AgentExecution end-to-end."""
        execution: AgentExecution = event_data
        if execution.status not in ['completed', 'failed']:
            return {'status': 'skipped', 'reason': f'status={execution.status}'}

        self.log_event(f"Learning from agent execution: {execution.agent.name}")
        try:
            patterns = self._extract_patterns(execution)
            self._update_learning(patterns)
            insights = self._generate_insights(patterns)
            self.log_success(f"Agent execution learning complete for {execution.id}")
            return {
                'status': 'ok',
                'execution_id': str(execution.id),
                'agent_name': execution.agent.name,
                'was_successful': patterns.get('was_successful', False),
                'performance': {
                    k: v for k, v in patterns.get('performance', {}).items()
                },
                'insights': insights,
            }
        except Exception as e:
            self.log_error(f"Error in agent execution learning: {e}")
            return {'status': 'error', 'error': str(e)}

    def _extract_patterns(self, event_data: Any) -> Dict:
        """Extract performance metrics + success classification."""
        execution: AgentExecution = event_data
        was_successful = execution.status == 'completed' and not execution.error_message
        performance = self._calculate_performance_metrics(execution)
        return {
            'was_successful': was_successful,
            'performance': performance,
            # Thread the AgentExecution instance through for `_update_learning`.
            '_exec': execution,
        }

    def _update_learning(self, patterns: Dict) -> None:
        """Update all four learning surfaces from extracted patterns."""
        execution: AgentExecution = patterns['_exec']
        was_successful: bool = patterns['was_successful']
        performance: Dict = patterns['performance']
        self._update_agent_performance_learning(execution, was_successful, performance)
        self._update_task_type_patterns(execution, was_successful)
        self._update_agent_aggregate_metrics(execution, was_successful)
        self._trigger_orchestrator(execution, was_successful, performance)

    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Derive human-readable insight strings."""
        insights: List[str] = []
        execution: AgentExecution = patterns['_exec']
        was_successful = patterns.get('was_successful', False)
        verb = 'succeeded' if was_successful else 'failed'
        performance = patterns.get('performance', {})

        insights.append(f"{execution.agent.name} {verb} on '{execution.task[:60]}'")
        if performance.get('execution_time_ms'):
            insights.append(f"time: {performance['execution_time_ms']}ms")
        if performance.get('cost'):
            insights.append(f"cost: ${performance['cost']:.4f}")
        if performance.get('task_complexity'):
            insights.append(f"complexity: {performance['task_complexity']}")
        if performance.get('efficiency_score') is not None:
            insights.append(f"efficiency: {performance['efficiency_score']:.2f}")
        return insights

    # ------------------------------------------------------------------
    # Bridge-specific helpers (unchanged from pre-refactor implementation)
    # ------------------------------------------------------------------
    def _calculate_performance_metrics(self, execution: AgentExecution) -> Dict:
        """Calculate performance metrics for this execution"""
        return {
            'execution_time_ms': (
                execution.execution_time_ms
                if hasattr(execution, 'execution_time_ms') and execution.execution_time_ms
                else 0
            ),
            'tokens_used': (
                execution.tokens_used
                if hasattr(execution, 'tokens_used') and execution.tokens_used
                else 0
            ),
            'cost': float(execution.cost) if hasattr(execution, 'cost') and execution.cost else 0,
            'efficiency_score': self._calculate_efficiency(execution),
            'task_complexity': self._estimate_task_complexity(
                execution.task if hasattr(execution, 'task') else ''
            ),
        }

    def _calculate_efficiency(self, execution: AgentExecution) -> float:
        """Calculate efficiency score (0-1) based on time, cost, and success."""
        if not hasattr(execution, 'execution_time_ms') or not execution.execution_time_ms:
            return 0.5

        time_score = max(0, 1 - (execution.execution_time_ms / 30000))
        cost = float(execution.cost) if hasattr(execution, 'cost') and execution.cost else 0.5
        cost_score = max(0, 1 - (cost / 0.50))
        return (time_score + cost_score) / 2

    def _estimate_task_complexity(self, task: str) -> str:
        """Estimate task complexity from description."""
        word_count = len(task.split())
        if word_count > 50:
            return 'high'
        elif word_count > 20:
            return 'medium'
        else:
            return 'low'

    def _update_agent_performance_learning(self, execution: AgentExecution,
                                          was_successful: bool, performance: Dict):
        """Update UserAgentLearning with execution results.

        Session 646: Skip user-specific learning if no user attached
        (Celery/API tasks).
        """
        if not execution.user:
            logger.debug(
                f"Skipping user learning for {execution.agent.name} - no user attached"
            )
            return

        learning, created = UserAgentLearning.objects.get_or_create(
            user=execution.user,
            agent_name=execution.agent.name,
            learning_domain='agent_execution_performance',
            defaults={
                'learning_content': {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'avg_execution_time_ms': 0,
                    'avg_cost': 0,
                    'task_types': {},
                },
                'confidence_score': 0.5,
                'learning_source': 'performance_tracking',
            },
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['total_executions'] = content.get('total_executions', 0) + 1

        if was_successful:
            content['successful_executions'] = content.get('successful_executions', 0) + 1
            learning.record_success()
        else:
            content['failed_executions'] = content.get('failed_executions', 0) + 1
            learning.record_failure()

        content['avg_execution_time_ms'] = performance['execution_time_ms']
        content['avg_cost'] = performance['cost']
        content['avg_efficiency'] = performance['efficiency_score']

        task_complexity = performance['task_complexity']
        if task_complexity not in content['task_types']:
            content['task_types'][task_complexity] = {'success': 0, 'failure': 0}

        if was_successful:
            content['task_types'][task_complexity]['success'] += 1
        else:
            content['task_types'][task_complexity]['failure'] += 1

        learning.learning_content = content
        learning.save()

        logger.info(f"✅ Updated agent performance learning for {execution.agent.name}")

    def _update_task_type_patterns(self, execution: AgentExecution, was_successful: bool):
        """Learn which types of tasks this agent excels at.

        Session 646: Skip if no user attached (Celery/API tasks).
        """
        if not execution.user:
            return

        task = execution.task if hasattr(execution, 'task') else ''
        task_lower = task.lower()

        task_type = 'general'
        if 'research' in task_lower or 'analyze' in task_lower:
            task_type = 'research'
        elif 'write' in task_lower or 'content' in task_lower:
            task_type = 'content_creation'
        elif 'code' in task_lower or 'develop' in task_lower:
            task_type = 'development'
        elif 'plan' in task_lower or 'strategy' in task_lower:
            task_type = 'planning'

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=execution.user,
            agent_name=execution.agent.name,
            learning_domain=f'task_type_{task_type}',
            defaults={
                'learning_content': {'success_count': 0, 'failure_count': 0},
                'confidence_score': 0.5,
                'learning_source': 'success_pattern',
            },
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        if was_successful:
            content['success_count'] = content.get('success_count', 0) + 1
            learning.record_success()
        else:
            content['failure_count'] = content.get('failure_count', 0) + 1
            learning.record_failure()

        learning.learning_content = content
        learning.save()

    def _update_agent_aggregate_metrics(self, execution: AgentExecution, was_successful: bool):
        """Update Agent model's aggregate success metrics."""
        agent = execution.agent

        if hasattr(agent, 'total_executions'):
            agent.total_executions = F('total_executions') + 1
        if was_successful and hasattr(agent, 'successful_executions'):
            agent.successful_executions = F('successful_executions') + 1

        agent.save()
        agent.refresh_from_db()

        if hasattr(agent, 'success_rate') and hasattr(agent, 'effectiveness_score'):
            recent_success_rate = agent.success_rate
            agent.effectiveness_score = int(
                agent.effectiveness_score * 0.8 + recent_success_rate * 0.2
            )
            agent.save()

    def _trigger_orchestrator(self, execution: AgentExecution, was_successful: bool, performance: Dict):
        """Trigger the Learning Orchestrator for autonomous improvement."""
        try:
            from core.self_development.learning_orchestrator import trigger_learning_cycle

            event_data = {
                'agent_name': execution.agent.name,
                'task': execution.task if hasattr(execution, 'task') else '',
                'success': was_successful,
                'performance': performance,
                'execution_id': str(execution.id),
            }

            trigger_learning_cycle(
                user=execution.user,
                event_type='agent_execution',
                event_data=event_data,
            )

            logger.info("🚀 Triggered learning orchestrator for autonomous improvement")
        except Exception as e:
            logger.error(f"Error triggering orchestrator: {e}")

    # ------------------------------------------------------------------
    # Back-compat alias used by `on_agent_execution_completed` signal handler
    # ------------------------------------------------------------------
    def process_execution(self, execution: AgentExecution) -> Dict:
        """Back-compat shim — delegates to `process_event`."""
        return self.process_event(execution)


# Signal integration
agent_execution_learning = AgentExecutionLearningLoop()


@receiver(post_save, sender=AgentExecution)
def on_agent_execution_completed(sender, instance, created, **kwargs):
    """Learn from completed agent executions"""
    if instance.status in ['completed', 'failed']:
        try:
            agent_execution_learning.process_execution(instance)
        except Exception as e:
            logger.error(f"Error in agent execution learning signal: {e}", exc_info=True)
