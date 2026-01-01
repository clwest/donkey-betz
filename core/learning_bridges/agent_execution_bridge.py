"""
Agent Execution Learning Bridge
Learns from agent execution outcomes to improve future agent selection and performance
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from typing import Dict

from core.models_unified_system import AgentExecution, UserAgentLearning

logger = logging.getLogger(__name__)


class AgentExecutionLearningLoop:
    """
    Learns from every agent execution to optimize future performance

    Tracks:
    - Which agents perform best for which tasks
    - Execution time patterns
    - Success/failure factors
    - Cost-effectiveness
    - User-specific agent performance
    """

    def process_execution(self, execution: AgentExecution):
        """Process completed agent execution"""

        if execution.status not in ['completed', 'failed']:
            return  # Only learn from finished executions

        logger.info(f"🤖 Learning from agent execution: {execution.agent.name}")

        try:
            # Determine if execution was successful
            was_successful = execution.status == 'completed' and not execution.error_message

            # Extract performance metrics
            performance = self._calculate_performance_metrics(execution)

            # Update agent-specific learning
            self._update_agent_performance_learning(execution, was_successful, performance)

            # Update task-type success patterns
            self._update_task_type_patterns(execution, was_successful)

            # Update Agent model aggregate metrics
            self._update_agent_aggregate_metrics(execution, was_successful)

            # TRIGGER LEARNING ORCHESTRATOR
            self._trigger_orchestrator(execution, was_successful, performance)

            logger.info(f"✅ Agent execution learning complete")

        except Exception as e:
            logger.error(f"Error in agent execution learning: {e}", exc_info=True)

    def _calculate_performance_metrics(self, execution: AgentExecution) -> Dict:
        """Calculate performance metrics for this execution"""
        return {
            'execution_time_ms': execution.execution_time_ms if hasattr(execution, 'execution_time_ms') and execution.execution_time_ms else 0,
            'tokens_used': execution.tokens_used if hasattr(execution, 'tokens_used') and execution.tokens_used else 0,
            'cost': float(execution.cost) if hasattr(execution, 'cost') and execution.cost else 0,
            'efficiency_score': self._calculate_efficiency(execution),
            'task_complexity': self._estimate_task_complexity(execution.task if hasattr(execution, 'task') else '')
        }

    def _calculate_efficiency(self, execution: AgentExecution) -> float:
        """
        Calculate efficiency score (0-1) based on time, cost, and success
        """
        if not hasattr(execution, 'execution_time_ms') or not execution.execution_time_ms:
            return 0.5

        # Normalize time (assuming 30 seconds is average)
        time_score = max(0, 1 - (execution.execution_time_ms / 30000))

        # Normalize cost (assuming $0.50 is average)
        cost = float(execution.cost) if hasattr(execution, 'cost') and execution.cost else 0.5
        cost_score = max(0, 1 - (cost / 0.50))

        # Combined score
        return (time_score + cost_score) / 2

    def _estimate_task_complexity(self, task: str) -> str:
        """Estimate task complexity from description"""
        word_count = len(task.split())

        if word_count > 50:
            return 'high'
        elif word_count > 20:
            return 'medium'
        else:
            return 'low'

    def _update_agent_performance_learning(self, execution: AgentExecution,
                                          was_successful: bool, performance: Dict):
        """
        Update UserAgentLearning with execution results.
        Session 646: Skip user-specific learning if no user attached (Celery/API tasks).
        """
        # Skip user-specific learning if no user is attached
        if not execution.user:
            logger.debug(f"Skipping user learning for {execution.agent.name} - no user attached")
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
                    'task_types': {}
                },
                'confidence_score': 0.5,
                'learning_source': 'performance_tracking'
            }
        )

        # Update learning content
        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['total_executions'] = content.get('total_executions', 0) + 1

        if was_successful:
            content['successful_executions'] = content.get('successful_executions', 0) + 1
            learning.record_success()
        else:
            content['failed_executions'] = content.get('failed_executions', 0) + 1
            learning.record_failure()

        # Update averages
        content['avg_execution_time_ms'] = performance['execution_time_ms']
        content['avg_cost'] = performance['cost']
        content['avg_efficiency'] = performance['efficiency_score']

        # Track task types
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
        """
        Learn which types of tasks this agent excels at.
        Session 646: Skip if no user attached (Celery/API tasks).
        """
        # Skip user-specific learning if no user is attached
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

        # Update task-specific learning
        learning, _ = UserAgentLearning.objects.get_or_create(
            user=execution.user,
            agent_name=execution.agent.name,
            learning_domain=f'task_type_{task_type}',
            defaults={
                'learning_content': {'success_count': 0, 'failure_count': 0},
                'confidence_score': 0.5,
                'learning_source': 'success_pattern'
            }
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
        """
        Update Agent model's aggregate success metrics
        """
        agent = execution.agent

        # Update counters
        if hasattr(agent, 'total_executions'):
            agent.total_executions = F('total_executions') + 1
        if was_successful and hasattr(agent, 'successful_executions'):
            agent.successful_executions = F('successful_executions') + 1

        agent.save()
        agent.refresh_from_db()

        # Update effectiveness score based on recent performance
        if hasattr(agent, 'success_rate') and hasattr(agent, 'effectiveness_score'):
            recent_success_rate = agent.success_rate

            # Adjust effectiveness score (80% historical, 20% recent)
            agent.effectiveness_score = int(
                agent.effectiveness_score * 0.8 + recent_success_rate * 0.2
            )
            agent.save()

    def _trigger_orchestrator(self, execution: AgentExecution, was_successful: bool, performance: Dict):
        """
        Trigger the Learning Orchestrator for autonomous improvement
        """
        try:
            from core.self_development.learning_orchestrator import trigger_learning_cycle

            event_data = {
                'agent_name': execution.agent.name,
                'task': execution.task if hasattr(execution, 'task') else '',
                'success': was_successful,
                'performance': performance,
                'execution_id': str(execution.id)
            }

            trigger_learning_cycle(
                user=execution.user,
                event_type='agent_execution',
                event_data=event_data
            )

            logger.info(f"🚀 Triggered learning orchestrator for autonomous improvement")

        except Exception as e:
            logger.error(f"Error triggering orchestrator: {e}")


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
