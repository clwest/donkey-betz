"""
Synchronous Wrapper for Agent Execution
========================================
This allows synchronous code to call async agents

AUTONOMOUS LEARNING INTEGRATION:
- Creates AgentExecution records for EVERY execution
- Triggers Django signals that fire learning bridges
- Enables autonomous self-development through learning loops
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from ai_core.agents.concrete_executor import ConcreteAgentExecutor

logger = logging.getLogger(__name__)


class SyncAgentExecutor:
    """Synchronous wrapper for async agent execution with automatic learning"""

    def __init__(self):
        self.executor = ConcreteAgentExecutor()

    def execute(self, agent_name: str, task_description: str, context: Optional[Dict] = None, user=None) -> Dict[str, Any]:
        """
        Execute an agent synchronously and create execution record for learning

        Args:
            agent_name: Name of the agent to execute
            task_description: Description of the task
            context: Optional context dictionary
            user: User executing the agent (required for learning)

        Returns:
            Execution result dictionary
        """
        task = {
            "description": task_description,
            "context": context or {},
            "type": "general"
        }

        # Create AgentExecution record for autonomous learning
        execution_record = None
        start_time = timezone.now()

        if user:
            try:
                from core.models_unified_system import Agent, AgentExecution

                # Get or create agent record
                agent_record, created = Agent.objects.get_or_create(
                    name=agent_name,
                    defaults={
                        'specialization': 'general',
                        'description': f'Agent: {agent_name}',
                        'is_active': True
                    }
                )

                # Create execution record
                execution_record = AgentExecution.objects.create(
                    agent=agent_record,
                    user=user,
                    task=task_description,
                    status='in_progress',
                    input_data={'task': task_description, 'context': context or {}}
                )
                logger.info(f"📝 Created AgentExecution record {execution_record.id} for {agent_name}")

            except Exception as e:
                logger.error(f"Failed to create AgentExecution record: {e}")

        # Execute the agent
        try:
            try:
                loop = asyncio.get_running_loop()
                # We're already in an async context
                import nest_asyncio
                nest_asyncio.apply()
                result = loop.run_until_complete(
                    self.executor.execute_agent(agent_name, task)
                )
            except RuntimeError:
                # No event loop, create one
                result = asyncio.run(
                    self.executor.execute_agent(agent_name, task)
                )

            # Update execution record with success
            if execution_record:
                execution_time = (timezone.now() - start_time).total_seconds() * 1000
                execution_record.status = 'completed'
                execution_record.output_data = result
                execution_record.execution_time_ms = int(execution_time)
                execution_record.completed_at = timezone.now()
                execution_record.save()
                logger.info(f"✅ Updated AgentExecution {execution_record.id} - completed in {execution_time:.0f}ms")

            return result

        except Exception as e:
            # Update execution record with failure
            if execution_record:
                execution_time = (timezone.now() - start_time).total_seconds() * 1000
                execution_record.status = 'failed'
                execution_record.error_message = str(e)
                execution_record.execution_time_ms = int(execution_time)
                execution_record.completed_at = timezone.now()
                execution_record.save()
                logger.error(f"❌ Updated AgentExecution {execution_record.id} - failed: {e}")

            return {
                "success": False,
                "error": str(e),
                "agent": agent_name
            }

    def execute_content(self, content_request: str, max_length: int = 500) -> Dict[str, Any]:
        """Execute content generation agent"""
        request = {
            "prompt": content_request,
            "max_length": max_length,
            "type": "content_generation"
        }

        try:
            try:
                loop = asyncio.get_running_loop()
                # We're already in an async context
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(
                    self.executor.execute_content_agent("content_creator", request)
                )
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(
                    self.executor.execute_content_agent("content_creator", request)
                )
        except Exception as e:
            return {"success": False, "error": str(e)}