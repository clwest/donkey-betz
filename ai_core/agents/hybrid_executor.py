"""
Hybrid Agent Executor

Supports both synchronous (for development/testing) and asynchronous
(Celery-based for production) execution modes.
"""

import logging
import asyncio
from typing import Dict, Any, List, Literal
from django.conf import settings

logger = logging.getLogger(__name__)


class HybridAgentExecutor:
    """
    Hybrid executor that can run agents either:
    1. Synchronously (for development/testing)
    2. Asynchronously via Celery (for production)

    This allows proper task chaining, background processing,
    and scalability in production while maintaining easy testing.
    """

    def __init__(self):
        self.execution_mode = getattr(settings, 'AGENT_EXECUTION_MODE', 'hybrid')
        self.celery_available = self._check_celery_availability()
        logger.info(f"🔀 Hybrid Executor initialized - Mode: {self.execution_mode}, Celery: {self.celery_available}")

    def _check_celery_availability(self) -> bool:
        """Check if Celery is available and running"""
        try:
            from celery import current_app
            # Try to inspect active workers
            inspector = current_app.control.inspect()
            stats = inspector.stats()
            if stats:
                logger.info(f"✅ Celery is running with {len(stats)} worker(s)")
                return True
            else:
                logger.warning("⚠️ Celery is installed but no workers are running")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Celery not available: {e}")
            return False

    async def execute_agent(
        self,
        agent_name: str,
        task: Dict[str, Any],
        user=None,
        mode: Literal['sync', 'async', 'auto'] = 'auto'
    ) -> Dict[str, Any]:
        """
        Execute an agent with flexible execution mode.

        Args:
            agent_name: Name of the agent to execute
            task: Task configuration
            user: Optional user context
            mode: Execution mode:
                - 'sync': Always run synchronously (blocking)
                - 'async': Always use Celery (non-blocking)
                - 'auto': Use Celery if available, otherwise sync

        Returns:
            Execution result or task ID (for async mode)
        """
        # Determine execution mode
        use_celery = False
        if mode == 'async':
            if not self.celery_available:
                logger.warning("Celery requested but not available, falling back to sync")
            else:
                use_celery = True
        elif mode == 'auto':
            use_celery = self.celery_available

        if use_celery:
            return await self._execute_with_celery(agent_name, task, user)
        else:
            return await self._execute_synchronously(agent_name, task, user)

    async def _execute_synchronously(
        self,
        agent_name: str,
        task: Dict[str, Any],
        user=None
    ) -> Dict[str, Any]:
        """Execute agent synchronously (blocking)"""
        from ai_core.agents.concrete_executor import execute_agent_directly

        logger.info(f"⚡ Executing '{agent_name}' synchronously")

        try:
            result = await execute_agent_directly(agent_name, task, user)
            return {
                'success': True,
                'mode': 'synchronous',
                'result': result,
                'execution_time': result.get('execution_time', 0)
            }
        except Exception as e:
            logger.error(f"Sync execution failed: {e}")
            return {
                'success': False,
                'mode': 'synchronous',
                'error': str(e)
            }

    async def _execute_with_celery(
        self,
        agent_name: str,
        task: Dict[str, Any],
        user=None
    ) -> Dict[str, Any]:
        """Execute agent asynchronously via Celery"""
        from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
        from agents.tasks import execute_agent as execute_agent_task
        import uuid

        logger.info(f"📋 Queuing '{agent_name}' for Celery execution")

        try:
            # Get agent template
            agent_template = UnifiedAgentTemplate.objects.get(
                name=agent_name,
                is_active=True
            )

            # Create execution record
            execution_id = f"exec_{agent_name}_{uuid.uuid4().hex[:8]}"

            execution = AgentExecution.objects.create(
                template=agent_template,
                user=user,
                execution_id=execution_id,
                task_description=task.get('task_description', ''),
                input_data=task.get('input', {}),
                context=task.get('context', {})
            )

            # Queue the task
            celery_task = execute_agent_task.delay(execution_id=execution_id)

            return {
                'success': True,
                'mode': 'asynchronous',
                'execution_id': execution_id,
                'task_id': celery_task.id,
                'status': 'queued',
                'message': 'Task queued for background execution'
            }

        except UnifiedAgentTemplate.DoesNotExist:
            return {
                'success': False,
                'mode': 'asynchronous',
                'error': f'Agent {agent_name} not found in database'
            }
        except Exception as e:
            logger.error(f"Celery execution failed: {e}")
            return {
                'success': False,
                'mode': 'asynchronous',
                'error': str(e)
            }

    async def chain_agents(
        self,
        agent_chain: List[Dict[str, Any]],
        user=None,
        mode: Literal['sync', 'async', 'auto'] = 'auto'
    ) -> Dict[str, Any]:
        """
        Execute a chain of agents with data passing between them.

        Args:
            agent_chain: List of agent configurations:
                [
                    {"agent": "agent1", "task": {...}},
                    {"agent": "agent2", "task": {...}, "depends_on": "agent1"},
                    ...
                ]
            user: Optional user context
            mode: Execution mode

        Returns:
            Chain execution result
        """
        use_celery = (mode == 'async' and self.celery_available) or \
                     (mode == 'auto' and self.celery_available)

        if use_celery:
            return await self._chain_with_celery(agent_chain, user)
        else:
            return await self._chain_synchronously(agent_chain, user)

    async def _chain_synchronously(
        self,
        agent_chain: List[Dict[str, Any]],
        user=None
    ) -> Dict[str, Any]:
        """Execute agent chain synchronously"""
        results = {}

        for step in agent_chain:
            agent_name = step['agent']
            task = step['task'].copy()

            # Inject results from dependencies
            if 'depends_on' in step:
                dep_name = step['depends_on']
                if dep_name in results:
                    task['input']['previous_result'] = results[dep_name]

            # Execute this step
            result = await self._execute_synchronously(agent_name, task, user)
            results[agent_name] = result

            # Stop on failure
            if not result.get('success'):
                return {
                    'success': False,
                    'mode': 'synchronous_chain',
                    'failed_at': agent_name,
                    'error': result.get('error'),
                    'partial_results': results
                }

        return {
            'success': True,
            'mode': 'synchronous_chain',
            'results': results
        }

    async def _chain_with_celery(
        self,
        agent_chain: List[Dict[str, Any]],
        user=None
    ) -> Dict[str, Any]:
        """Execute agent chain using Celery task chaining"""
        from celery import chain
        from agents.tasks import execute_agent as execute_agent_task

        # Build Celery chain
        celery_tasks = []

        for step in agent_chain:
            # Create task signature
            sig = execute_agent_task.si(
                agent_name=step['agent'],
                task=step['task'],
                user_id=user.id if user else None
            )
            celery_tasks.append(sig)

        # Create chain
        workflow = chain(*celery_tasks)

        # Execute chain
        result = workflow.apply_async()

        return {
            'success': True,
            'mode': 'asynchronous_chain',
            'workflow_id': result.id,
            'status': 'queued',
            'message': f'Chain of {len(agent_chain)} agents queued for execution'
        }

    async def parallel_execute(
        self,
        agents: List[Dict[str, Any]],
        user=None,
        mode: Literal['sync', 'async', 'auto'] = 'auto'
    ) -> Dict[str, Any]:
        """
        Execute multiple agents in parallel.

        Args:
            agents: List of agent configurations
            user: Optional user context
            mode: Execution mode

        Returns:
            Parallel execution results
        """
        use_celery = (mode == 'async' and self.celery_available) or \
                     (mode == 'auto' and self.celery_available)

        if use_celery:
            return await self._parallel_with_celery(agents, user)
        else:
            return await self._parallel_synchronously(agents, user)

    async def _parallel_synchronously(
        self,
        agents: List[Dict[str, Any]],
        user=None
    ) -> Dict[str, Any]:
        """Execute agents in parallel using asyncio"""
        tasks = []

        for agent_config in agents:
            task = self._execute_synchronously(
                agent_config['agent'],
                agent_config['task'],
                user
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful = []
        failed = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append({
                    'agent': agents[i]['agent'],
                    'error': str(result)
                })
            elif result.get('success'):
                successful.append({
                    'agent': agents[i]['agent'],
                    'result': result
                })
            else:
                failed.append({
                    'agent': agents[i]['agent'],
                    'error': result.get('error')
                })

        return {
            'success': len(failed) == 0,
            'mode': 'synchronous_parallel',
            'successful': successful,
            'failed': failed,
            'total': len(agents)
        }

    async def _parallel_with_celery(
        self,
        agents: List[Dict[str, Any]],
        user=None
    ) -> Dict[str, Any]:
        """Execute agents in parallel using Celery group"""
        from celery import group
        from agents.tasks import execute_agent as execute_agent_task

        # Create group of tasks
        job = group(
            execute_agent_task.s(
                agent_name=agent_config['agent'],
                task=agent_config['task'],
                user_id=user.id if user else None
            )
            for agent_config in agents
        )

        # Execute group
        result = job.apply_async()

        return {
            'success': True,
            'mode': 'asynchronous_parallel',
            'group_id': result.id,
            'status': 'queued',
            'message': f'{len(agents)} agents queued for parallel execution'
        }

    def get_execution_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of an async task"""
        if not self.celery_available:
            return {
                'error': 'Celery not available',
                'status': 'unknown'
            }

        from celery.result import AsyncResult

        result = AsyncResult(task_id)

        return {
            'task_id': task_id,
            'status': result.status,
            'ready': result.ready(),
            'successful': result.successful() if result.ready() else None,
            'result': result.result if result.successful() else None,
            'error': str(result.info) if result.failed() else None
        }


# Global hybrid executor instance
hybrid_executor = HybridAgentExecutor()


async def smart_execute_agent(
    agent_name: str,
    task: Dict[str, Any],
    user=None,
    prefer_async: bool = True
) -> Dict[str, Any]:
    """
    Smart execution that automatically chooses the best mode.

    Args:
        agent_name: Agent to execute
        task: Task configuration
        user: Optional user context
        prefer_async: If True, prefer Celery when available

    Returns:
        Execution result
    """
    mode = 'auto' if prefer_async else 'sync'
    return await hybrid_executor.execute_agent(agent_name, task, user, mode)