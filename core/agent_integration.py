"""
Agent Integration Utilities for Personal Assistant
Provides seamless integration between Personal Assistant and specialized agents.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from agents.models import UnifiedAgentTemplate, AgentExecution, AgentRegistry
from content.ai_providers import AIProviderManager
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Intelligent agent routing system that routes user queries through specialized agents
    """
    
    def __init__(self, user):
        self.user = user
        self.registry = self._get_registry()
        
    def _get_registry(self):
        """Get or create the unified agent registry"""
        try:
            return AgentRegistry.objects.get(registry_name='unified_agent_registry')
        except AgentRegistry.DoesNotExist:
            logger.warning("Agent registry not found, agent routing will be limited")
            return None
    
    def should_use_intelligent_prompting(self, message: str) -> bool:
        """
        Determine if a message should be routed through the Intelligent Prompting Agent
        """
        # Keywords that indicate prompting/optimization tasks
        prompting_keywords = [
            'prompt', 'prompting', 'optimize', 'improve', 'better response',
            'prompt engineering', 'AI response', 'model output', 'generation',
            'rephrase', 'rewrite prompt', 'enhance prompt', 'prompt quality'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in prompting_keywords)
    
    def should_use_agent_routing(self, message: str) -> bool:
        """
        Determine if a message should be routed through the agent system
        """
        # Check for complex tasks that would benefit from specialized agents
        complex_task_indicators = [
            'analyze', 'research', 'strategy', 'plan', 'create content',
            'business', 'financial', 'marketing', 'legal', 'technical',
            'code', 'development', 'sports', 'betting', 'odds'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in complex_task_indicators)
    
    def find_best_agent(self, message: str, exclude_agents: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find the best agent for a given message
        """
        if not self.registry:
            return None
            
        exclude_agents = exclude_agents or []
        
        # Find agents for the task
        agents = self.registry.find_agents_for_task(message, limit=3)
        
        # Filter out excluded agents
        filtered_agents = [
            agent for agent in agents 
            if agent['agent_name'] not in exclude_agents
        ]
        
        return filtered_agents[0] if filtered_agents else None
    
    def execute_intelligent_prompting(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the Intelligent Prompting Agent to optimize a prompt
        """
        try:
            # Get the Intelligent Prompting Agent
            intelligent_agent = UnifiedAgentTemplate.objects.get(
                name="Intelligent Prompting Agent", 
                is_active=True
            )
            
            # Determine the task type
            task_description = f"Optimize and enhance this prompt/query: '{message}'"
            
            # Prepare input data
            input_data = {
                "original_message": message,
                "user_context": context or {},
                "optimization_goal": "Improve clarity, specificity, and response quality"
            }
            
            # Execute directly without Celery for faster response
            result = self._execute_agent_directly(
                agent=intelligent_agent,
                task_description=task_description,
                input_data=input_data,
                context=context or {}
            )
            
            return result
            
        except UnifiedAgentTemplate.DoesNotExist:
            logger.error("Intelligent Prompting Agent not found")
            return {
                'success': False,
                'error': 'Intelligent Prompting Agent not available',
                'fallback_to_direct': True
            }
        except Exception as e:
            logger.error(f"Error executing Intelligent Prompting Agent: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_to_direct': True
            }
    
    def execute_agent_for_task(self, message: str, agent_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a specific agent for a task
        """
        try:
            agent = UnifiedAgentTemplate.objects.get(name=agent_name, is_active=True)
            
            result = self._execute_agent_directly(
                agent=agent,
                task_description=message,
                input_data={"user_query": message},
                context=context or {}
            )
            
            return result
            
        except UnifiedAgentTemplate.DoesNotExist:
            logger.error(f"Agent '{agent_name}' not found")
            return {
                'success': False,
                'error': f'Agent {agent_name} not available',
                'fallback_to_direct': True
            }
        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_to_direct': True
            }
    
    def _execute_agent_directly(self, agent: UnifiedAgentTemplate, task_description: str, 
                               input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an agent directly without Celery (for faster response times)
        """
        try:
            # Initialize AI provider
            ai_manager = AIProviderManager()
            available_providers = ai_manager.get_available_providers()
            
            if not available_providers:
                return {
                    'success': False,
                    'error': 'No AI providers available',
                    'fallback_to_direct': True
                }
            
            # Use agent's preferred provider if available, otherwise use first available
            provider = agent.llm_provider if agent.llm_provider in available_providers else available_providers[0]
            
            # Prepare the prompt
            system_prompt = agent.system_prompt
            user_prompt = f"""
Task: {task_description}

Input Data:
{input_data}

Context:
{context}

Please complete this task using your specialized capabilities.
"""
            
            # Prepare config based on model
            if 'gpt-5' in agent.llm_model.lower():
                config = {'max_completion_tokens': agent.llm_config.get('max_tokens', 1500)}
                if 'temperature' in agent.llm_config:
                    # GPT-5 models might not support temperature, so we skip it
                    pass
            else:
                config = agent.llm_config or {'max_tokens': 1500, 'temperature': 0.7}
            
            # Execute the AI call
            result = ai_manager.generate_content(
                provider=provider,
                model=agent.llm_model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                config=config
            )
            
            if result.success:
                return {
                    'success': True,
                    'content': result.content,
                    'agent_used': agent.name,
                    'provider': provider,
                    'model': agent.llm_model,
                    'token_usage': result.token_usage,
                    'generation_time_ms': result.generation_time_ms
                }
            else:
                return {
                    'success': False,
                    'error': result.error_message,
                    'fallback_to_direct': True
                }
                
        except Exception as e:
            logger.error(f"Error in direct agent execution: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_to_direct': True
            }


class IntelligentPromptOptimizer:
    """
    Specialized class for prompt optimization using the Intelligent Prompting Agent
    """
    
    def __init__(self, user):
        self.user = user
        self.router = AgentRouter(user)
    
    def optimize_prompt(self, original_prompt: str, context: Dict[str, Any] = None, 
                       target_model: str = None) -> Dict[str, Any]:
        """
        Optimize a prompt using the Intelligent Prompting Agent
        """
        optimization_context = {
            'target_model': target_model or 'gpt-4',
            'optimization_type': 'general_improvement',
            'user_preferences': context or {}
        }
        
        task_description = f"""Optimize this prompt for CONCISE, DIRECT responses:

Original Prompt: "{original_prompt}"

CRITICAL OPTIMIZATION GOALS:
- Enforce extreme brevity (1-3 sentences default)
- Remove any instructions that lead to verbose responses
- Eliminate requirements for lists, breakdowns, or explanations unless explicitly requested
- Add "Be EXTREMELY CONCISE" as primary directive

Target Model: {optimization_context['target_model']}
"""
        
        return self.router.execute_intelligent_prompting(
            message=task_description,
            context=optimization_context
        )
    
    def enhance_system_prompt(self, system_prompt: str, task_type: str = None) -> Dict[str, Any]:
        """
        Enhance a system prompt for specific task types
        """
        task_description = f"""Enhance this system prompt to ENFORCE BREVITY:

Current System Prompt: "{system_prompt}"

Task Type: {task_type or 'general'}

MANDATORY ENHANCEMENTS:
- Add "Be EXTREMELY CONCISE" as the primary directive
- Specify "1-3 sentences maximum" as default response length
- Remove any instructions encouraging detailed explanations
- Emphasize direct answers without preamble

Make responses SHORT by default.
"""
        
        context = {
            'task_type': task_type,
            'prompt_type': 'system_prompt',
            'enhancement_focus': 'performance_and_clarity'
        }
        
        return self.router.execute_intelligent_prompting(
            message=task_description,
            context=context
        )