"""
Universal Agent Loader - Connects all 151 agents to the executor
================================================================

This module bridges the gap between database-stored agent templates
and the concrete executor, enabling all 151 agents to be executed.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from agents.models import UnifiedAgentTemplate
from agents.registry import agent_registry
from asgiref.sync import sync_to_async
# Note: UniversalLLMExecutor not used directly, we create dynamic classes instead
from backend.agents.ai_enforced_base import AIEnforcedAgent

logger = logging.getLogger(__name__)


def get_all_agent_classes() -> Dict[str, type]:
    """
    Load all 151 agents from the database and create executable classes.

    Returns:
        Dictionary mapping agent names to executable agent classes
    """
    agent_classes = {}

    try:
        # Check if we're in an async context
        try:
            loop = asyncio.get_running_loop()
            is_async = True
        except RuntimeError:
            is_async = False

        if is_async:
            # We're in async context, need to use sync_to_async
            logger.warning("Async context detected, switching to sync mode for DB queries")
            return get_all_agent_classes_sync()

        # Get all agent templates from database (sync context)
        templates = UnifiedAgentTemplate.objects.all()
        logger.info(f"Loading {templates.count()} agents from database")

        for template in templates:
            # Create a dynamic agent class for each template
            agent_name = template.name.replace('-', '_')

            # Create agent configuration from template
            agent_config = {
                'id': str(template.id),
                'name': template.name,
                'type': template.specialization,
                'capabilities': template.capabilities or [],
                'description': template.description,
                'configuration': template.llm_config or {},
                'is_active': template.is_active,
                'system_prompt': template.system_prompt,
                'domain_tags': template.domain_tags or []
            }

            # Create a dynamic class that uses UniversalLLMAgent
            class DynamicAgent(AIEnforcedAgent):
                """Dynamically created agent from template"""

                def __init__(self, user=None):
                    # Store template configuration
                    self.template = template
                    self.config = agent_config

                    # Initialize as AI-enforced agent
                    super().__init__(agent_name=agent_name, user=user)

                    # Store capabilities
                    self.capabilities = agent_config.get('capabilities', [])
                    self.specialization = agent_config.get('type', 'general')

                    logger.info(f"Initialized {agent_name} with specialization: {self.specialization}")

                async def execute(self, **kwargs):
                    """Execute agent task using AI"""
                    # Build context from template
                    context = {
                        'agent_type': self.specialization,
                        'capabilities': self.capabilities,
                        'configuration': self.config.get('configuration', {}),
                        'user_input': kwargs
                    }

                    # Generate prompt based on specialization
                    task = kwargs.get('task', 'Complete the requested task')

                    prompt = f"""
                    You are a specialized {self.specialization} agent named {self.config['name']}.

                    Your capabilities include: {', '.join(self.capabilities) if self.capabilities else 'general task execution'}

                    Task: {task}

                    Additional context: {json.dumps(kwargs, default=str)}

                    Please complete this task using your specialized knowledge and capabilities.
                    Provide detailed, actionable output appropriate for a {self.specialization} agent.
                    """

                    # Use AI to generate response
                    response = super().generate_ai_text(
                        prompt=prompt,
                        context=json.dumps(context, default=str),
                        task_type=self.specialization
                    )

                    # Track AI usage if method exists
                    if hasattr(self, 'track_ai_usage'):
                        self.track_ai_usage('execute', prompt, response)

                    return {
                        'success': True,
                        'agent': self.config['name'],
                        'specialization': self.specialization,
                        'output': response,
                        'ai_used': True,
                        'timestamp': datetime.now().isoformat()
                    }

            # Set class name dynamically
            DynamicAgent.__name__ = f"{agent_name.title().replace('_', '')}Agent"
            DynamicAgent.__qualname__ = DynamicAgent.__name__

            # Add to registry
            agent_classes[agent_name] = DynamicAgent

        logger.info(f"✅ Successfully loaded {len(agent_classes)} agent classes")

        # Also include any hardcoded agents that might exist
        try:
            from backend.agents.real_content_creator import RealContentCreatorAgent
            agent_classes['real_content_creator'] = RealContentCreatorAgent
            logger.info("Added RealContentCreatorAgent")
        except ImportError:
            pass

        try:
            from backend.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator
            agent_classes['zero_capital_income_generator'] = ZeroCapitalIncomeGenerator
            logger.info("Added ZeroCapitalIncomeGenerator")
        except ImportError:
            pass

        try:
            from backend.agents.content_marketplace_agent import ContentMarketplaceAgent
            agent_classes['content_marketplace_agent'] = ContentMarketplaceAgent
            logger.info("Added ContentMarketplaceAgent")
        except ImportError as e:
            logger.warning(f"Could not add ContentMarketplaceAgent: {e}")

        return agent_classes

    except Exception as e:
        logger.error(f"Failed to load agent classes: {e}")
        return agent_classes


def get_all_agent_classes_sync() -> Dict[str, type]:
    """
    Sync version of get_all_agent_classes for use in async contexts.
    This forces the database queries to run in a thread pool.
    """
    import threading
    from django.db import connection

    # Force this to run in a new thread to avoid async context issues
    result_container = {}
    exception_container = {}

    def load_agents_sync():
        try:
            # Close any existing connections to ensure clean state
            connection.close()

            agent_classes = {}

            # Get all agent templates from database (now in sync context)
            templates = UnifiedAgentTemplate.objects.all()
            count = templates.count()
            logger.info(f"Loading {count} agents from database (sync mode)")

            for template in templates:
                # Create a dynamic agent class for each template
                agent_name = template.name.replace('-', '_')

                # Create agent configuration from template
                agent_config = {
                    'id': str(template.id),
                    'name': template.name,
                    'type': template.specialization,
                    'capabilities': template.capabilities or [],
                    'description': template.description,
                    'configuration': template.llm_config or {},
                    'is_active': template.is_active,
                    'system_prompt': template.system_prompt,
                    'domain_tags': template.domain_tags or []
                }

                # Create a dynamic class that uses UniversalLLMAgent
                class DynamicAgent(AIEnforcedAgent):
                    """Dynamically created agent from template"""

                    def __init__(self, user=None):
                        # Store template configuration
                        self.template = template
                        self.config = agent_config

                        # Initialize as AI-enforced agent
                        super().__init__(agent_name=agent_name, user=user)

                        # Store capabilities
                        self.capabilities = agent_config.get('capabilities', [])
                        self.specialization = agent_config.get('type', 'general')

                        logger.debug(f"Initialized {agent_name} with specialization: {self.specialization}")

                    async def execute(self, **kwargs):
                        """Execute agent task using AI"""
                        # Build context from template
                        context = {
                            'agent_type': self.specialization,
                            'capabilities': self.capabilities,
                            'configuration': self.config.get('configuration', {}),
                            'user_input': kwargs
                        }

                        # Generate prompt based on specialization
                        task = kwargs.get('task', 'Complete the requested task')

                        prompt = f"""
                        You are a specialized {self.specialization} agent with the following capabilities:
                        {', '.join(self.capabilities)}

                        Task: {task}

                        Additional context: {json.dumps(kwargs, default=str)}

                        Please complete this task using your specialized knowledge and capabilities.
                        Provide detailed, actionable output appropriate for a {self.specialization} agent.
                        """

                        # Use AI to generate response
                        response = self.generate_ai_text(
                            prompt=prompt,
                            context=json.dumps(context, default=str),
                            task_type=self.specialization
                        )

                        # Track AI usage if method exists
                        if hasattr(self, 'track_ai_usage'):
                            self.track_ai_usage('execute', prompt, response)

                        return {
                            'success': True,
                            'agent': self.config['name'],
                            'specialization': self.specialization,
                            'output': response,
                            'ai_used': True,
                            'timestamp': datetime.now().isoformat()
                        }

                # Set class name dynamically
                DynamicAgent.__name__ = f"{agent_name.title().replace('_', '')}Agent"
                DynamicAgent.__qualname__ = DynamicAgent.__name__

                # Add to registry
                agent_classes[agent_name] = DynamicAgent

            logger.info(f"✅ Successfully loaded {len(agent_classes)} agent classes (sync mode)")

            # Also include any hardcoded agents that might exist
            try:
                from backend.agents.real_content_creator import RealContentCreatorAgent
                agent_classes['real_content_creator'] = RealContentCreatorAgent
                logger.info("Added RealContentCreatorAgent")
            except ImportError:
                pass

            try:
                from backend.agents.zero_capital_income_generator import ZeroCapitalIncomeGenerator
                agent_classes['zero_capital_income_generator'] = ZeroCapitalIncomeGenerator
                logger.info("Added ZeroCapitalIncomeGenerator")
            except ImportError:
                pass

            try:
                from backend.agents.content_marketplace_agent import ContentMarketplaceAgent
                agent_classes['content_marketplace_agent'] = ContentMarketplaceAgent
                logger.info("Added ContentMarketplaceAgent")
            except ImportError as e:
                logger.warning(f"Could not add ContentMarketplaceAgent: {e}")

            result_container['agent_classes'] = agent_classes

        except Exception as e:
            logger.error(f"Failed to load agent classes in sync mode: {e}")
            exception_container['error'] = str(e)
            result_container['agent_classes'] = {}

    # Run in thread to avoid async context issues
    thread = threading.Thread(target=load_agents_sync)
    thread.start()
    thread.join(timeout=30)  # 30 second timeout

    if thread.is_alive():
        logger.error("Agent loading timed out after 30 seconds")
        return {}

    if 'error' in exception_container:
        logger.error(f"Agent loading failed: {exception_container['error']}")
        return {}

    return result_container.get('agent_classes', {})


# Required imports for dynamic execution
import json
from datetime import datetime