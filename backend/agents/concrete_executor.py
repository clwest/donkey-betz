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
from backend.agents.mythology_validator import mythology_enforcer
from backend.agents.project_builder_base import ProjectBuilderAgent, FullStackBuilderAgent

# Import Content Studio Integration (lazy import to avoid circular deps)
content_studio_integration = None

# Lazy imports to avoid circular dependencies and import issues
def get_agent_classes():
    """Load ALL 151 agents from database and create executable classes"""
    try:
        from backend.agents.universal_agent_loader import get_all_agent_classes
        agent_classes = get_all_agent_classes()
        logger.info(f"🚀 Loaded {len(agent_classes)} agent classes from universal loader")
        return agent_classes
    except Exception as e:
        logger.error(f"Failed to load agents from universal loader: {e}")

        # Fallback to minimal agents
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
        self.agent_registry = self.agent_classes  # Expose for spider connector

        self.execution_history = []
        self.content_studio_connected = False
        self.spider_connector = None
        self.llm_integration = None
        logger.info(f"🚀 Initialized ConcreteAgentExecutor with {len(self.agent_classes)} agent types")

        # Initialize Content Studio integration
        self._initialize_content_studio()

        # Initialize Spider-Agent connector
        self._initialize_spider_connector()

        # Initialize LLM integration
        self._initialize_llm_integration()

    async def get_spider_data_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get pending spider data for an agent"""
        if not self.spider_connector:
            return []
        await self._ensure_spider_connector_initialized()
        return await self.spider_connector.get_agent_data(agent_name)

    async def enable_agent_with_intelligence(self, agent_name: str, agent_instance: Any):
        """Enable an agent with both spider data access and LLM capabilities"""
        # Enable spider data access
        if self.spider_connector:
            agent_instance.get_spider_data = lambda: self.get_spider_data_for_agent(agent_name)

        # Enable LLM capabilities
        if self.llm_integration:
            await self.llm_integration.enable_agent_with_llm(agent_name, agent_instance)

    async def execute_agent(self, agent_name: str, task: Dict[str, Any], user=None) -> Dict[str, Any]:
        """
        Execute a specific agent with given task parameters with retry logic.

        Args:
            agent_name: Name of the agent to execute
            task: Task configuration including input data
            user: Optional user context

        Returns:
            Execution result dictionary
        """
        import time
        import os
        start_time = timezone.now()

        # Check for API keys early
        api_keys_available = bool(os.environ.get('OPENAI_API_KEY') or os.environ.get('ANTHROPIC_API_KEY'))
        if not api_keys_available:
            logger.warning(f"⚠️ No API keys found for {agent_name}. Agent may fail without AI capabilities.")

        try:
            # Check for project building agents first
            if self._is_project_builder_task(task):
                return await self._execute_project_builder_agent(agent_name, task, user, start_time)

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

            # Enable intelligence capabilities (spider data + LLM)
            await self.enable_agent_with_intelligence(agent_name, agent_instance)

            logger.info(f"🏃 Executing agent: {agent_name} (with spider data + LLM)")

            # Prepare task input
            task_input = task.get('input', {})
            if 'task_description' in task:
                task_input['task'] = task['task_description']

            # Execute with retry logic
            result = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Execute the agent
                    if hasattr(agent_instance, 'execute'):
                        result = await agent_instance.execute(**task_input)
                    elif hasattr(agent_instance, 'run'):
                        result = await agent_instance.run(**task_input)
                    else:
                        # Fallback for agents without execute method
                        result = await self._execute_generic_agent(agent_instance, task_input)

                    # If we got a result, check if it's successful
                    if result and (result.get('success', False) or 'error' not in result):
                        break  # Success, exit retry loop

                    # If it failed but we have retries left, log and retry
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                        logger.warning(f"⚠️ Agent {agent_name} failed on attempt {attempt + 1}/{max_retries}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)

                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"⚠️ Agent {agent_name} exception on attempt {attempt + 1}/{max_retries}: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise  # Re-raise on last attempt

            # If no result after all retries, create a failure result
            if not result:
                result = {
                    'success': False,
                    'error': f'Agent {agent_name} failed after {max_retries} attempts',
                    'retries_attempted': max_retries
                }

            # Calculate execution time
            execution_time = (timezone.now() - start_time).total_seconds()

            # Verify AI usage if this is an AI-enforced agent
            ai_stats = {}
            if isinstance(agent_instance, AIEnforcedAgent):
                ai_used = agent_instance.verify_ai_usage()
                ai_stats = agent_instance.get_ai_usage_stats()
                logger.info(f"✅ Agent {agent_name} AI usage verified: {ai_used}")

            # Get implementation metrics if this is a project builder
            implementation_metrics = {}
            if isinstance(agent_instance, ProjectBuilderAgent):
                implementation_metrics = agent_instance.get_implementation_metrics()

            # Validate output with mythology enforcer
            validated_result = mythology_enforcer.enforce(agent_name, result)

            # Build success response with validation
            execution_result = {
                'success': True,
                'agent': agent_name,
                'execution_time': execution_time,
                'result': validated_result.get('result', result),
                'ai_stats': ai_stats,
                'implementation_metrics': implementation_metrics,
                'mythology_validated': validated_result.get('mythology_validated', False),
                'mythology_corrected': validated_result.get('mythology_corrected', False),
                'timestamp': timezone.now().isoformat()
            }

            # Add warning if mythology corrections were made
            if validated_result.get('mythology_corrected'):
                execution_result['warning'] = validated_result.get('warning', 'Output was adjusted for realism')
                logger.warning(f"⚠️ Mythology corrections applied to {agent_name} output")

            # Store in history
            self.execution_history.append(execution_result)

            # Track execution in Redis for real-time metrics - Added 9/26/25 11:57 AM MST
            try:
                from backend.agents.execution_tracker import execution_tracker
                execution_tracker.track_agent_execution(
                    agent_name=agent_name,
                    execution_data={
                        'task_description': task.get('task_description', 'Agent task'),
                        'is_real_execution': True,
                        'success': True,
                        'quality_score': 85,  # Default quality score
                        'complexity_score': 50,  # Default complexity
                        'code_generated': bool(implementation_metrics),
                        'lines_of_code': implementation_metrics.get('total_lines', 0) if implementation_metrics else 0
                    }
                )
            except Exception as track_error:
                logger.debug(f"Could not track execution: {track_error}")

            # Broadcast to WebSocket for frontend display
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync

                channel_layer = get_channel_layer()

                # Prepare result data for frontend
                frontend_data = {
                    'type': 'agent_result',
                    'agent_name': agent_instance.agent_name if 'agent_instance' in locals() else agent_name,
                    'task': task.get('task_description', 'Agent task'),
                    'result': validated_result.get('result', result) if 'validated_result' in locals() else result,
                    'success': True,
                    'execution_time': execution_time,
                    'ai_stats': ai_stats,
                    'timestamp': timezone.now().isoformat()
                }

                # Send to consciousness stream (which the dashboard listens to)
                await channel_layer.group_send(
                    'consciousness_stream',
                    {
                        'type': 'consciousness_update',
                        'data': frontend_data
                    }
                )

                logger.info(f"📡 Broadcast agent result to WebSocket: {agent_name}")
            except Exception as ws_error:
                logger.error(f"Failed to broadcast to WebSocket: {ws_error}")

            return execution_result

        except Exception as e:
            error_msg = f"Error executing agent {agent_name}: {str(e)}"
            logger.error(f"❌ {error_msg}\n{traceback.format_exc()}")

            # Track failed execution - Added 9/26/25 11:58 AM MST
            try:
                from backend.agents.execution_tracker import execution_tracker
                execution_tracker.track_agent_execution(
                    agent_name=agent_name,
                    execution_data={
                        'task_description': task.get('task_description', 'Agent task'),
                        'is_real_execution': True,
                        'success': False,
                        'error': str(e)
                    }
                )
            except Exception as track_error:
                logger.debug(f"Could not track failed execution: {track_error}")

            return {
                'success': False,
                'agent': agent_name,
                'error': error_msg,
                'traceback': traceback.format_exc(),
                'execution_time': (timezone.now() - start_time).total_seconds(),
                'timestamp': timezone.now().isoformat()
            }

    def _is_project_builder_task(self, task: Dict[str, Any]) -> bool:
        """Check if this task requires project building capabilities"""
        task_type = task.get('type', '').lower()
        task_desc = task.get('task_description', '').lower()

        project_keywords = ['build', 'create project', 'full-stack', 'generate app', 'scaffold', 'new project']

        return (task_type in ['build', 'project', 'fullstack'] or
                any(keyword in task_desc for keyword in project_keywords))

    async def _execute_project_builder_agent(self, agent_name: str, task: Dict[str, Any], user=None, start_time=None) -> Dict[str, Any]:
        """Execute a project building agent with real file system capabilities"""
        if start_time is None:
            start_time = timezone.now()

        try:
            # Determine which project builder to use
            task_type = task.get('type', 'fullstack').lower()

            if task_type == 'fullstack' or 'full-stack' in task.get('task_description', '').lower():
                agent_instance = FullStackBuilderAgent(f"FullStackBuilder_{agent_name}", user)
            else:
                agent_instance = ProjectBuilderAgent(f"ProjectBuilder_{agent_name}", user)

            # Enable intelligence capabilities
            await self.enable_agent_with_intelligence(agent_name, agent_instance)

            logger.info(f"🏗️ Executing PROJECT BUILDER agent: {agent_instance.agent_name}")

            # Prepare task input for project building
            task_input = task.get('input', {})
            project_idea = task.get('task_description', 'Build a web application')

            # Extract project parameters
            project_params = {
                'project_name': task_input.get('project_name') or task.get('project_name'),
                'tech_stack': task_input.get('tech_stack') or task.get('tech_stack', {}),
                'features': task_input.get('features') or task.get('features', []),
                'containerize': task_input.get('containerize', True),
                'git_init': task_input.get('git_init', True)
            }

            # Execute the project builder
            result = await agent_instance.execute(project_idea, **project_params)

            # Calculate execution time
            execution_time = (timezone.now() - start_time).total_seconds()

            # Get AI usage stats
            ai_stats = agent_instance.get_ai_usage_stats()
            implementation_metrics = agent_instance.get_implementation_metrics()

            logger.info(f"✅ Project builder completed: {agent_instance.agent_name}")
            logger.info(f"📊 Files created: {implementation_metrics.get('files_created', 0)}")
            logger.info(f"🔧 Commands executed: {implementation_metrics.get('commands_executed', 0)}")

            # Build comprehensive response
            execution_result = {
                'success': result.get('success', True),
                'agent': agent_instance.agent_name,
                'agent_type': 'project_builder',
                'execution_time': execution_time,
                'result': result,
                'ai_stats': ai_stats,
                'implementation_metrics': implementation_metrics,
                'build_log': agent_instance.get_build_log() if hasattr(agent_instance, 'get_build_log') else [],
                'project_path': result.get('project_path'),
                'files_created': result.get('files_created', []),
                'real_execution': True,  # Flag indicating this was real execution
                'timestamp': timezone.now().isoformat()
            }

            # Store in history
            self.execution_history.append(execution_result)

            # Track execution in Redis for real-time metrics - Added 9/26/25 11:57 AM MST
            try:
                from backend.agents.execution_tracker import execution_tracker
                execution_tracker.track_agent_execution(
                    agent_name=agent_name,
                    execution_data={
                        'task_description': task.get('task_description', 'Agent task'),
                        'is_real_execution': True,
                        'success': True,
                        'quality_score': 85,  # Default quality score
                        'complexity_score': 50,  # Default complexity
                        'code_generated': bool(implementation_metrics),
                        'lines_of_code': implementation_metrics.get('total_lines', 0) if implementation_metrics else 0
                    }
                )
            except Exception as track_error:
                logger.debug(f"Could not track execution: {track_error}")

            # Broadcast to WebSocket for frontend display
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync

                channel_layer = get_channel_layer()

                # Prepare result data for frontend
                frontend_data = {
                    'type': 'agent_result',
                    'agent_name': agent_instance.agent_name if 'agent_instance' in locals() else agent_name,
                    'task': task.get('task_description', 'Agent task'),
                    'result': validated_result.get('result', result) if 'validated_result' in locals() else result,
                    'success': True,
                    'execution_time': execution_time,
                    'ai_stats': ai_stats,
                    'timestamp': timezone.now().isoformat()
                }

                # Send to consciousness stream (which the dashboard listens to)
                await channel_layer.group_send(
                    'consciousness_stream',
                    {
                        'type': 'consciousness_update',
                        'data': frontend_data
                    }
                )

                logger.info(f"📡 Broadcast agent result to WebSocket: {agent_name}")
            except Exception as ws_error:
                logger.error(f"Failed to broadcast to WebSocket: {ws_error}")

            return execution_result

        except Exception as e:
            error_msg = f"Error executing project builder agent {agent_name}: {str(e)}"
            logger.error(f"❌ {error_msg}\n{traceback.format_exc()}")

            return {
                'success': False,
                'agent': f"ProjectBuilder_{agent_name}",
                'agent_type': 'project_builder',
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

    def _initialize_content_studio(self):
        """Initialize Content Studio integration"""
        global content_studio_integration
        try:
            from backend.agents.content_studio_integration import content_studio_integration as csi
            content_studio_integration = csi
            self.content_studio_connected = True
            logger.info("🎨 Content Studio integration connected successfully")
        except Exception as e:
            logger.warning(f"Content Studio integration not available: {e}")
            self.content_studio_connected = False

    def _initialize_spider_connector(self):
        """Initialize Spider-Agent data connector"""
        try:
            from backend.agents.spider_agent_connector import spider_agent_connector
            self.spider_connector = spider_agent_connector
            logger.info("🕷️ Spider-Agent connector will be initialized on first use")
        except Exception as e:
            logger.warning(f"Spider-Agent connector not available: {e}")
            self.spider_connector = None

    async def _ensure_spider_connector_initialized(self):
        """Ensure spider connector is initialized before use"""
        if self.spider_connector and not self.spider_connector.initialized:
            await self.spider_connector.initialize()
            logger.info("🕷️ Spider-Agent connector initialized successfully")

    def _initialize_llm_integration(self):
        """Initialize LLM integration for agent intelligence"""
        try:
            from backend.agents.agent_llm_integration import agent_llm_integration
            self.llm_integration = agent_llm_integration
            logger.info(f"🧠 LLM integration initialized with provider: {self.llm_integration.default_provider}")
        except Exception as e:
            logger.warning(f"LLM integration not available: {e}")
            self.llm_integration = None

    async def create_content(self, agent_name: str, content_type: str, topic: str, user=None, **kwargs):
        """Create content through the Content Studio using a specific agent"""
        if not self.content_studio_connected:
            self._initialize_content_studio()

        if content_studio_integration:
            return await content_studio_integration.create_content_through_agent(
                agent_name, content_type, topic, user, **kwargs
            )
        else:
            return {
                'success': False,
                'error': 'Content Studio integration not available'
            }


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


# Global executor instance - created lazily to avoid circular imports
_concrete_executor_instance = None

def get_concrete_executor():
    """Get or create the singleton ConcreteAgentExecutor instance"""
    global _concrete_executor_instance
    if _concrete_executor_instance is None:
        _concrete_executor_instance = ConcreteAgentExecutor()
    return _concrete_executor_instance

# For backward compatibility, will be created on first real use
concrete_executor = None


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


def execute_agent_sync(agent_name: str, task_description: str, context: Dict = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for agent execution
    Use this when calling from non-async code
    """
    from backend.agents.sync_executor import SyncAgentExecutor
    sync_executor = SyncAgentExecutor()
    return sync_executor.execute(agent_name, task_description, context)