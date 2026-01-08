"""
Universal LLM Executor for ALL Agents
=====================================

Session 728: Migrated from agents/universal_llm_executor.py to core/services/universal_llm_executor.py

This module ensures that ALL 149 registered agents use real LLMs
when they execute tasks, not mock responses.

Any agent execution goes through this executor which:
1. Loads the agent configuration
2. Enhances it with user context
3. Forces real LLM usage via AIEnforcedAgent
4. Returns actual AI-generated results
"""

import os
import sys
import logging
from typing import Dict, Any
from datetime import datetime
import json

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.agents.ai_enforced_base import AIEnforcedAgent
from core.agents.registry import agent_registry
from core.llm_enforcer import get_llm_enforcer

logger = logging.getLogger(__name__)


class UniversalLLMAgent(AIEnforcedAgent):
    """
    Universal agent that can become ANY of the 149 registered agents
    and execute their tasks using real LLMs.
    """

    def __init__(self, agent_config: Dict[str, Any], user=None):
        """Initialize with a specific agent's configuration"""
        # Get agent details from config
        self.agent_id = agent_config.get('id', 'unknown')
        self.agent_type = agent_config.get('type', 'general')
        self.agent_config = agent_config

        # Initialize parent with agent name
        agent_name = agent_config.get('name', self.agent_id)
        super().__init__(agent_name=agent_name, user=user)

        # Load agent-specific attributes
        self.capabilities = agent_config.get('capabilities', [])
        self.specialization = agent_config.get('specialization', 'general')
        self.description = agent_config.get('description', '')

        logger.info(f"🤖 Initialized Universal LLM Agent as: {agent_name}")
        logger.info(f"   Capabilities: {', '.join(self.capabilities[:3])}")

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute any task using real LLM based on the agent's specialization.

        This is the MAIN method that ensures ALL agents use real AI.
        """
        try:
            # Extract task details
            task_type = task.get('type', 'general')
            instruction = task.get('instruction', '')
            context = task.get('context', {})

            # Build agent-specific prompt
            prompt = self._build_agent_prompt(instruction, context)

            # Determine temperature based on agent type
            temperature = self._get_temperature_for_agent()

            # Generate response using REAL AI
            logger.info(f"🔮 {self.agent_name} executing task via LLM...")

            response = self.generate_ai_text(
                prompt=prompt,
                context=self._build_context_string(context),
                task_type=task_type,
                max_tokens=1000,
                temperature=temperature,
                personalize=True  # Use user context if available
            )

            # Structure the response
            result = {
                'success': True,
                'agent': self.agent_name,
                'agent_id': self.agent_id,
                'task_type': task_type,
                'response': response,
                'ai_generated': True,
                'tokens_used': self.ai_tokens_used,
                'cost': self.ai_cost,
                'timestamp': datetime.now().isoformat()
            }

            # Store in agent memory if user context exists
            if self.user:
                self.store_agent_memory(
                    memory_type='agent_execution',
                    content=f"{self.agent_name} completed {task_type}: {response[:200]}",
                    importance=7,
                    task_type=task_type,
                    agent_id=self.agent_id
                )

            logger.info(f"✅ {self.agent_name} completed task using {self.ai_tokens_used} tokens")
            return result

        except Exception as e:
            logger.error(f"❌ {self.agent_name} execution failed: {e}")
            return {
                'success': False,
                'agent': self.agent_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _build_agent_prompt(self, instruction: str, context: Dict[str, Any]) -> str:
        """Build a prompt specific to this agent's capabilities and role"""

        # Start with agent identity
        prompt = f"""You are {self.agent_name}, a specialized AI agent with the following profile:

Role: {self.agent_type}
Specialization: {self.specialization}
Description: {self.description}
Capabilities: {', '.join(self.capabilities)}

Your task is to {instruction}

Context provided:
{json.dumps(context, indent=2) if context else 'No additional context'}

Please provide a detailed, actionable response that leverages your specific expertise and capabilities.
Focus on concrete, practical solutions and insights.
"""

        # Add agent-specific instructions based on type
        if 'financial' in self.agent_type.lower() or 'investment' in self.specialization.lower():
            prompt += "\nInclude specific financial metrics, risk assessments, and investment recommendations."

        elif 'technical' in self.agent_type.lower() or 'developer' in self.specialization.lower():
            prompt += "\nProvide technical implementation details, code examples if relevant, and best practices."

        elif 'marketing' in self.agent_type.lower() or 'content' in self.specialization.lower():
            prompt += "\nFocus on engagement strategies, content ideas, and measurable marketing outcomes."

        elif 'data' in self.agent_type.lower() or 'analyst' in self.specialization.lower():
            prompt += "\nInclude data-driven insights, statistical analysis, and visualization recommendations."

        elif 'crypto' in self.agent_type.lower() or 'blockchain' in self.specialization.lower():
            prompt += "\nProvide blockchain insights, DeFi opportunities, and crypto market analysis."

        elif 'sports' in self.agent_type.lower() or 'betting' in self.specialization.lower():
            prompt += "\nInclude odds analysis, statistical predictions, and betting strategies."

        return prompt

    def _build_context_string(self, context: Dict[str, Any]) -> str:
        """Convert context dictionary to a readable string"""
        if not context:
            return ""

        context_parts = []
        for key, value in context.items():
            if isinstance(value, (list, dict)):
                context_parts.append(f"{key}: {json.dumps(value)}")
            else:
                context_parts.append(f"{key}: {value}")

        return "\n".join(context_parts)

    def _get_temperature_for_agent(self) -> float:
        """Get appropriate temperature setting based on agent type"""

        # Creative agents need higher temperature
        if any(word in self.agent_type.lower() for word in ['creative', 'marketing', 'content', 'idea']):
            return 0.9

        # Analytical agents need lower temperature
        elif any(word in self.agent_type.lower() for word in ['analyst', 'financial', 'data', 'technical']):
            return 0.3

        # Default moderate temperature
        else:
            return 0.7


class UniversalAgentExecutor:
    """
    Singleton executor that handles ALL agent executions through real LLMs.
    This replaces mock agent implementations with real AI.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.agent_registry = agent_registry
        self.llm_enforcer = get_llm_enforcer()
        self.execution_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0

        logger.info("🚀 Universal Agent Executor initialized")
        logger.info(f"   Managing {len(self.agent_registry.list_agents())} agents")

        self._initialized = True

    def execute_agent(self,
                      agent_id,  # Can be str or UUID
                      task: Dict[str, Any],
                      user=None) -> Dict[str, Any]:
        """
        Execute ANY registered agent with real LLM.

        This is the main entry point for all agent executions.
        """
        try:
            # Convert to string if UUID
            agent_id_str = str(agent_id)

            # Get agent configuration
            agent_config = self.agent_registry.get_agent(agent_id_str)

            # If not found by ID, try to find by ID match
            if not agent_config:
                for agent in self.agent_registry.list_agents():
                    if str(agent.get('id')) == agent_id_str:
                        agent_config = agent
                        break

            if not agent_config:
                logger.error(f"Agent {agent_id} not found in registry")
                return {
                    'success': False,
                    'error': f'Agent {agent_id} not found',
                    'timestamp': datetime.now().isoformat()
                }

            # Create universal agent with this config
            universal_agent = UniversalLLMAgent(agent_config, user=user)

            # Execute the task
            result = universal_agent.execute(task)

            # Track metrics
            self.execution_count += 1
            self.total_tokens += universal_agent.ai_tokens_used
            self.total_cost += universal_agent.ai_cost

            logger.info(f"📊 Execution #{self.execution_count} complete")
            logger.info(f"   Total tokens used: {self.total_tokens}")
            logger.info(f"   Total cost: ${self.total_cost:.4f}")

            return result

        except Exception as e:
            logger.error(f"Failed to execute agent {agent_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id,
                'timestamp': datetime.now().isoformat()
            }

    def execute_random_agent(self, task: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Execute a random agent for testing"""
        import random

        agents = self.agent_registry.list_agents()
        if not agents:
            return {'success': False, 'error': 'No agents available'}

        agent = random.choice(agents)
        logger.info(f"🎲 Randomly selected agent: {agent['name']}")

        return self.execute_agent(agent['id'], task, user)

    def execute_best_agent_for_task(self,
                                   task: Dict[str, Any],
                                   user=None) -> Dict[str, Any]:
        """Find and execute the best agent for a given task"""

        task_type = task.get('type', '')
        instruction = task.get('instruction', '')

        # Find best matching agent
        best_agent = None
        best_score = 0

        for agent in self.agent_registry.list_agents():
            score = 0

            # Check type match
            if task_type and task_type in agent.get('type', ''):
                score += 3

            # Check capability match
            for capability in agent.get('capabilities', []):
                if capability.lower() in instruction.lower():
                    score += 1

            # Check specialization match
            if agent.get('specialization', '') in instruction.lower():
                score += 2

            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent:
            logger.info(f"🎯 Selected best agent: {best_agent['name']} (score: {best_score})")
            return self.execute_agent(best_agent['id'], task, user)
        else:
            # Fallback to random agent
            return self.execute_random_agent(task, user)

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            'total_executions': self.execution_count,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost,
            'average_tokens': self.total_tokens / max(1, self.execution_count),
            'average_cost': self.total_cost / max(1, self.execution_count),
            'agents_available': len(self.agent_registry.list_agents())
        }


# Global executor instance
_executor = None

def get_universal_executor() -> UniversalAgentExecutor:
    """Get the global universal executor instance"""
    global _executor
    if _executor is None:
        _executor = UniversalAgentExecutor()
    return _executor


# Convenience function for quick agent execution
def execute_agent_with_llm(agent_id,  # Can be str or UUID
                          instruction: str,
                          context: Dict[str, Any] = None,
                          user=None) -> Dict[str, Any]:
    """
    Convenience function to execute any agent with real LLM.

    Args:
        agent_id: The agent ID from registry
        instruction: What the agent should do
        context: Additional context for the task
        user: User object for personalization

    Returns:
        Execution result with AI-generated response
    """
    executor = get_universal_executor()
    task = {
        'instruction': instruction,
        'context': context or {},
        'type': 'general'
    }
    return executor.execute_agent(agent_id, task, user)


if __name__ == "__main__":
    # Test the universal executor
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    print("\n🧪 Testing Universal LLM Executor\n")

    executor = get_universal_executor()

    # Test with a random agent
    test_task = {
        'instruction': 'Analyze the current AI job market and provide insights',
        'context': {
            'focus_areas': ['machine learning', 'data science', 'prompt engineering'],
            'location': 'remote'
        },
        'type': 'analysis'
    }

    print("Executing random agent with real LLM...")
    result = executor.execute_random_agent(test_task)

    if result['success']:
        print(f"\n✅ Agent: {result.get('agent', 'Unknown')}")
        print(f"📝 Response: {result['response'][:500]}...")
        print(f"💰 Cost: ${result.get('cost', 0):.4f}")
        print(f"🔢 Tokens: {result.get('tokens_used', 0)}")
    else:
        print(f"\n❌ Execution failed: {result.get('error', 'Unknown error')}")

    # Show stats
    stats = executor.get_execution_stats()
    print(f"\n📊 Execution Stats:")
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Total cost: ${stats['total_cost']:.4f}")
    print(f"   Agents available: {stats['agents_available']}")