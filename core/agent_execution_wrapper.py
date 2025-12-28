"""
Agent execution tracking wrapper
"""
from core.models_unified_system import AgentExecution, Agent
from django.utils import timezone
import time
import logging

logger = logging.getLogger(__name__)

class AgentExecutionTracker:
    """Context manager to track agent execution"""

    def __init__(self, agent_id, user, task_description):
        self.agent_id = agent_id
        self.user = user
        self.task_description = task_description
        self.execution = None
        self.start_time = None

    def __enter__(self):
        """Start tracking"""
        try:
            agent = Agent.objects.get(id=self.agent_id)

            self.execution = AgentExecution.objects.create(
                agent=agent,
                user=self.user,
                task=self.task_description,
                status='in_progress',
                input_data={},
                output_data={}
            )

            self.start_time = time.time()
            logger.info(f"🤖 Started execution: {agent.name} - {self.task_description[:50]}")

            return self.execution

        except Exception as e:
            logger.error(f"Error creating execution record: {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End tracking"""
        if not self.execution:
            return

        # Calculate execution time in milliseconds
        execution_time = int((time.time() - self.start_time) * 1000)

        if exc_type is None:
            # Success
            self.execution.status = 'completed'
            self.execution.completed_at = timezone.now()
            logger.info(f"✅ Completed: {self.execution.agent.name} in {execution_time}ms")
        else:
            # Error
            self.execution.status = 'failed'
            self.execution.error_message = str(exc_val)
            logger.error(f"❌ Failed: {self.execution.agent.name} - {exc_val}")

        self.execution.execution_time_ms = execution_time
        self.execution.save()

        # Update agent metrics
        agent = self.execution.agent
        agent.total_executions += 1
        if self.execution.status == 'completed':
            agent.successful_executions += 1
        agent.save()


def track_agent_execution(agent_id, user, task_description):
    """
    Decorator/context manager to track agent execution

    Usage:
        with track_agent_execution(agent.id, user, "Task description") as execution:
            result = agent.execute(task)
            if execution:
                execution.output_data = {'result': result}
                execution.save()
    """
    return AgentExecutionTracker(agent_id, user, task_description)
