"""
Concrete Agent Executor Implementation

This module provides a concrete implementation of the BaseAgentExecutor
that can execute agents synchronously without requiring Celery.
"""

import logging
import json
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from django.utils import timezone

from backend.agents.ai_enforced_base import AIEnforcedAgent

# Lazy imports to avoid circular dependencies and import issues
def get_agent_classes():
    """Lazy load agent classes to avoid import issues"""
    agent_classes = {}

    try:
        from backend.agents.real_content_creator import RealContentCreator
        agent_classes['real_content_creator'] = RealContentCreator
    except ImportError as e:
        logger.warning(f"Could not import RealContentCreator: {e}")

    try:
        from backend.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator
        agent_classes['zero_capital_income_generator'] = ZeroCapitalIncomeGenerator
    except ImportError as e:
        logger.warning(f"Could not import ZeroCapitalIncomeGenerator: {e}")

    # Additional agents can be added later
    return agent_classes

logger = logging.getLogger(__name__)


class ConcreteAgentExecutor:
    """
    Concrete executor that can instantiate and run agents directly.
    """

    def __init__(self):
        """Initialize the executor with agent registry"""
        # Use lazy loading to avoid import issues
        self.agent_classes = get_agent_classes()

        self.execution_history = []
        logger.info(f"🚀 Initialized ConcreteAgentExecutor with {len(self.agent_classes)} agent types")

    async def execute_agent(self, agent_name: str, task: Dict[str, Any], user=None) -> Dict[str, Any]:
        """
        Execute a specific agent with given task parameters.

        Args:
            agent_name: Name of the agent to execute
            task: Task configuration including input data
            user: Optional user context

        Returns:
            Execution result dictionary
        """
        start_time = timezone.now()

        try:
            # Validate agent exists
            if agent_name not in self.agent_classes:
                # Try partial match
                agent_name = self._find_agent_by_partial_name(agent_name)
                if not agent_name:
                    return {
                        'success': False,
                        'error': f'Agent {agent_name} not found in registry',
                        'available_agents': list(self.agent_classes.keys())
                    }

            # Instantiate the agent
            agent_class = self.agent_classes[agent_name]
            agent_instance = agent_class(user=user) if user else agent_class()

            logger.info(f"🏃 Executing agent: {agent_name}")

            # Prepare task input
            task_input = task.get('input', {})
            if 'task_description' in task:
                task_input['task'] = task['task_description']

            # Execute the agent
            if hasattr(agent_instance, 'execute'):
                result = await agent_instance.execute(**task_input)
            elif hasattr(agent_instance, 'run'):
                result = await agent_instance.run(**task_input)
            else:
                # Fallback for agents without execute method
                result = await self._execute_generic_agent(agent_instance, task_input)

            # Calculate execution time
            execution_time = (timezone.now() - start_time).total_seconds()

            # Verify AI usage if this is an AI-enforced agent
            ai_stats = {}
            if isinstance(agent_instance, AIEnforcedAgent):
                ai_used = agent_instance.verify_ai_usage()
                ai_stats = agent_instance.get_ai_usage_stats()
                logger.info(f"✅ Agent {agent_name} AI usage verified: {ai_used}")

            # Build success response
            execution_result = {
                'success': True,
                'agent': agent_name,
                'execution_time': execution_time,
                'result': result,
                'ai_stats': ai_stats,
                'timestamp': timezone.now().isoformat()
            }

            # Store in history
            self.execution_history.append(execution_result)

            return execution_result

        except Exception as e:
            error_msg = f"Error executing agent {agent_name}: {str(e)}"
            logger.error(f"❌ {error_msg}\n{traceback.format_exc()}")

            return {
                'success': False,
                'agent': agent_name,
                'error': error_msg,
                'traceback': traceback.format_exc(),
                'execution_time': (timezone.now() - start_time).total_seconds(),
                'timestamp': timezone.now().isoformat()
            }

    def _find_agent_by_partial_name(self, partial_name: str) -> Optional[str]:
        """Find agent by partial name match"""
        partial_lower = partial_name.lower()
        for agent_name in self.agent_classes.keys():
            if partial_lower in agent_name.lower():
                logger.info(f"🔍 Found agent '{agent_name}' for partial match '{partial_name}'")
                return agent_name
        return None

    async def _execute_generic_agent(self, agent_instance: Any, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generic execution for agents without standard execute method.
        """
        # Special handling for ZeroCapitalIncomeGenerator
        if agent_instance.__class__.__name__ == 'ZeroCapitalIncomeGenerator':
            if hasattr(agent_instance, 'generate_zero_capital_opportunities'):
                opportunities = await agent_instance.generate_zero_capital_opportunities(
                    user_skills=task_input.get('skills', [])
                )
                return {
                    'success': True,
                    'opportunities': opportunities,
                    'count': len(opportunities)
                }

        # Try common method names
        method_names = ['process', 'generate', 'analyze', 'perform']

        for method_name in method_names:
            if hasattr(agent_instance, method_name):
                method = getattr(agent_instance, method_name)
                if callable(method):
                    logger.info(f"🔧 Using method '{method_name}' for agent execution")
                    return await method(**task_input) if asyncio.iscoroutinefunction(method) else method(**task_input)

        # If no method found, try to generate something using AI if available
        if isinstance(agent_instance, AIEnforcedAgent):
            task_desc = task_input.get('task', 'Complete the requested task')
            response = agent_instance.generate_ai_text(
                prompt=f"Execute this task: {task_desc}",
                context=json.dumps(task_input),
                task_type="general"
            )
            return {
                'output': response,
                'method': 'ai_generation'
            }

        raise NotImplementedError(f"Agent {agent_instance.__class__.__name__} has no executable method")

    def list_available_agents(self) -> List[Dict[str, Any]]:
        """List all available agents and their capabilities"""
        agents = []

        for name, agent_class in self.agent_classes.items():
            agent_info = {
                'name': name,
                'class_name': agent_class.__name__,
                'has_execute': hasattr(agent_class, 'execute'),
                'is_ai_enforced': issubclass(agent_class, AIEnforcedAgent),
                'doc': agent_class.__doc__ or 'No documentation available'
            }
            agents.append(agent_info)

        return agents

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]

    def clear_history(self):
        """Clear execution history"""
        self.execution_history = []
        logger.info("🧹 Cleared execution history")


class SpecializedExecutors:
    """
    Collection of specialized executors for different agent types.
    """

    @staticmethod
    async def execute_content_agent(agent_name: str, content_request: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Execute content creation agents"""
        agent_classes = get_agent_classes()

        if agent_name in agent_classes:
            agent = agent_classes[agent_name](user=user)
            if hasattr(agent, 'execute'):
                return await agent.execute(**content_request)
            else:
                return {"error": f"Agent {agent_name} does not have execute method"}
        else:
            raise ValueError(f"Unknown content agent: {agent_name}")

    @staticmethod
    async def execute_job_agent(agent_name: str, job_request: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Execute job-related agents"""
        agent_classes = get_agent_classes()

        if agent_name in agent_classes:
            agent = agent_classes[agent_name](user=user)
            if hasattr(agent, 'execute'):
                return await agent.execute(**job_request)
            else:
                return {"error": f"Agent {agent_name} does not have execute method"}
        else:
            raise ValueError(f"Unknown job agent: {agent_name}")

    @staticmethod
    async def execute_income_agent(agent_name: str, income_request: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Execute income generation agents"""
        agent_classes = get_agent_classes()

        if agent_name in agent_classes:
            agent = agent_classes[agent_name](user=user)
            if hasattr(agent, 'execute'):
                return await agent.execute(**income_request)
            else:
                return {"error": f"Agent {agent_name} does not have execute method"}
        else:
            raise ValueError(f"Unknown income agent: {agent_name}")


# Global executor instance
concrete_executor = ConcreteAgentExecutor()


async def execute_agent_directly(agent_name: str, task: Dict[str, Any], user=None) -> Dict[str, Any]:
    """
    Convenience function to execute agents directly.

    Args:
        agent_name: Name of the agent
        task: Task configuration
        user: Optional user context

    Returns:
        Execution result
    """
    return await concrete_executor.execute_agent(agent_name, task, user)


def get_available_agents() -> List[Dict[str, Any]]:
    """Get list of available agents"""
    return concrete_executor.list_available_agents()


# Import asyncio for async execution
import asyncio

if __name__ == "__main__":
    # Test the concrete executor
    async def test_executor():
        # Test listing agents
        agents = get_available_agents()
        print(f"Available agents: {len(agents)}")
        for agent in agents:
            print(f"  - {agent['name']}: {agent['is_ai_enforced']}")

        # Test executing a simple agent
        result = await execute_agent_directly(
            'real_content_creator',
            {
                'task_description': 'Write about AI in business',
                'input': {
                    'topic': 'AI in Business',
                    'type': 'blog',
                    'keywords': ['AI', 'business', 'automation']
                }
            }
        )

        print(f"\nExecution result: {result['success']}")
        if result['success']:
            print(f"AI Stats: {result.get('ai_stats', {})}")

    asyncio.run(test_executor())