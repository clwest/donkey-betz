"""
Agent Integration Utilities for Personal Assistant
Provides seamless integration between Personal Assistant and specialized agents.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from django.utils import timezone

from core.models.agents_registry import UnifiedAgentTemplate, AgentRegistry
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
            'optimize prompt', 'improve prompt', 'better prompt',
            'prompt engineering', 'enhance prompt', 'rewrite prompt',
            'prompt optimization', 'prompt quality'
        ]
        
        # Negative indicators - phrases that suggest NOT a prompt optimization task
        negative_indicators = [
            'system prompt', 'your prompt', 'main prompt', 
            'what page', 'what app', 'messed with'
        ]
        
        message_lower = message.lower()
        
        # Check for negative indicators first
        if any(neg in message_lower for neg in negative_indicators):
            return False
            
        # Only route if explicitly about prompt optimization
        return any(keyword in message_lower for keyword in prompting_keywords)
    
    def should_use_agent_routing(self, message: str) -> bool:
        """
        Determine if a message should be routed through the agent system
        """
        # Expanded keywords for better routing coverage
        complex_task_indicators = [
            # Original technical/business terms
            'analyze', 'research', 'strategy', 'plan', 'create content',
            'business', 'financial', 'marketing', 'legal', 'technical',
            'code', 'development', 'sports', 'betting', 'odds',
            
            # Common query patterns
            'summary', 'summarize', 'explain', 'what', 'how', 'why', 'when',
            'list', 'show', 'tell', 'describe', 'help', 'find', 'search',
            
            # Action verbs
            'write', 'generate', 'make', 'build', 'design', 'implement',
            'optimize', 'improve', 'fix', 'debug', 'test', 'deploy',
            
            # Status/info requests
            'status', 'update', 'changed', 'new', 'recent', 'latest',
            'current', 'progress', 'report', 'review', 'check',
            
            # Data/content requests
            'data', 'information', 'details', 'documentation', 'guide',
            'tutorial', 'example', 'template', 'pattern', 'best practice'
        ]
        
        message_lower = message.lower()
        
        # Quick exit for very short messages (likely just greetings)
        if len(message_lower.strip()) < 10:
            return False
            
        # Route most queries through agents for better responses
        # Only skip routing for extremely simple responses and casual conversations
        simple_patterns = [
            'hi', 'hello', 'thanks', 'goodbye', 'ok', 'yes', 'no',
            'how are you', 'how is it going', 'how\'s it going', 'what\'s up',
            'hey there', 'good morning', 'good afternoon', 'good evening',
            'nice to meet you', 'pleased to meet you'
        ]
        
        # Check for exact matches or substring matches for greetings
        for pattern in simple_patterns:
            if pattern in message_lower.strip():
                return False
                
        # Default to routing for richer responses
        return any(indicator in message_lower for indicator in complex_task_indicators)
    
    def find_best_agent(self, message: str, exclude_agents: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find the best agent for a given message with learning-based scoring
        """
        if not self.registry:
            # If no registry, try to find agents directly
            return self._find_agent_without_registry(message, exclude_agents)
            
        exclude_agents = exclude_agents or []
        
        # Find agents for the task
        agents = self.registry.find_agents_for_task(message, limit=5)  # Increased limit
        
        # Filter out excluded agents
        filtered_agents = [
            agent for agent in agents 
            if agent['agent_name'] not in exclude_agents
        ]
        
        # Apply learning-based score adjustments
        filtered_agents = self._apply_learning_adjustments(filtered_agents)
        
        # If no agents from registry, try direct matching
        if not filtered_agents:
            return self._find_agent_without_registry(message, exclude_agents)
            
        # Sort by adjusted score and return best
        filtered_agents.sort(key=lambda x: x.get('adjusted_score', x.get('score', 0)), reverse=True)
        return filtered_agents[0] if filtered_agents else None
    
    def _apply_learning_adjustments(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply learning-based adjustments to agent scores
        """
        from core.models.agents_registry import UnifiedAgentTemplate
        
        for agent_data in agents:
            try:
                # Get the actual agent to check performance metrics
                agent = UnifiedAgentTemplate.objects.filter(
                    name=agent_data['agent_name']
                ).first()
                
                if agent:
                    # Adjust score based on success rate
                    base_score = agent_data.get('score', 0.5)
                    
                    # Success rate adjustment (0-100 scale)
                    if agent.success_rate > 80:
                        score_boost = 0.2
                    elif agent.success_rate > 60:
                        score_boost = 0.1
                    elif agent.success_rate < 40:
                        score_boost = -0.2
                    else:
                        score_boost = 0
                    
                    # User rating adjustment (1-5 scale)
                    if agent.avg_user_rating > 4.0:
                        score_boost += 0.15
                    elif agent.avg_user_rating < 2.5:
                        score_boost -= 0.15
                    
                    # Speed adjustment
                    if agent.avg_completion_time > 0 and agent.avg_completion_time < 3.0:
                        score_boost += 0.1  # Fast agent
                    elif agent.avg_completion_time > 10.0:
                        score_boost -= 0.1  # Slow agent
                    
                    # Check for clarification issues from learning patterns
                    if agent.metadata and 'learning_patterns' in agent.metadata:
                        clarification_count = agent.metadata['learning_patterns'].get('asks_clarification_count', 0)
                        if clarification_count > 5:
                            score_boost -= 0.3  # Penalize agents that ask too many clarifications
                    
                    # Apply adjusted score
                    agent_data['adjusted_score'] = max(0.1, min(1.0, base_score + score_boost))
                    agent_data['learning_applied'] = True
                    agent_data['success_rate'] = agent.success_rate
                    agent_data['user_rating'] = agent.avg_user_rating
                    
                    logger.debug(f"Agent {agent.name}: base={base_score:.2f}, adjusted={agent_data['adjusted_score']:.2f}, "
                               f"success_rate={agent.success_rate:.1f}%, rating={agent.avg_user_rating:.1f}")
                    
            except Exception as e:
                logger.error(f"Error applying learning adjustments for {agent_data.get('agent_name')}: {e}")
                agent_data['adjusted_score'] = agent_data.get('score', 0.5)
        
        return agents
    
    def _find_agent_without_registry(self, message: str, exclude_agents: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fallback method to find agents when registry is unavailable
        """
        try:
            from core.models.agents_registry import UnifiedAgentTemplate
            
            exclude_agents = exclude_agents or []
            message_lower = message.lower()
            
            # Direct keyword to agent mapping for common cases
            agent_mappings = {
                'summary': 'Research Agent',
                'analyze': 'Data Analysis Agent',
                'write': 'Content Writer Agent',
                'code': 'Code Assistant Agent',
                'sports': 'Sports Analytics Agent',
                'betting': 'Betting Strategy Agent',
                'research': 'Research Agent',
                'explain': 'Educational Agent',
                'help': 'Personal Assistant Agent'
            }
            
            # Find best matching agent based on keywords
            for keyword, agent_name in agent_mappings.items():
                if keyword in message_lower and agent_name not in exclude_agents:
                    try:
                        agent = UnifiedAgentTemplate.objects.get(
                            name=agent_name,
                            is_active=True
                        )
                        return {
                            'agent_name': agent.name,
                            'score': 0.6,  # Default medium confidence
                            'agent_id': str(agent.id)
                        }
                    except UnifiedAgentTemplate.DoesNotExist:
                        continue
            
            # If no specific match, return a general agent
            try:
                general_agent = UnifiedAgentTemplate.objects.filter(
                    is_active=True
                ).exclude(
                    name__in=exclude_agents
                ).first()
                
                if general_agent:
                    return {
                        'agent_name': general_agent.name,
                        'score': 0.5,  # Lower confidence for general match
                        'agent_id': str(general_agent.id)
                    }
            except Exception as _e:
                logger.warning(
                    "agent_integration._find_agent_without_registry: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
                
        except Exception as e:
            logger.error(f"Error in fallback agent finding: {e}")
            
        return None
    
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
        execution_start = timezone.now()
        execution_id = f"direct_{agent.name}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Create execution record for tracking
            from core.models.agents_registry import AgentExecution, AgentStatus
            execution = AgentExecution.objects.create(
                template=agent,
                user=self.user,
                execution_id=execution_id,
                task_description=task_description,
                task_type='direct_routing',
                context=context,
                input_data=input_data,
                status=AgentStatus.RUNNING,
                started_at=execution_start
            )
            
            # Initialize AI provider
            ai_manager = AIProviderManager()
            available_providers = ai_manager.get_available_providers()
            
            if not available_providers:
                execution.status = AgentStatus.FAILED
                execution.error_message = 'No AI providers available'
                execution.completed_at = timezone.now()
                execution.save()
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
                # GPT-5 models use max_tokens (the ai_providers.py will convert it to max_completion_tokens)
                config = {'max_tokens': agent.llm_config.get('max_tokens', 1500)}
                # The ai_providers.py will handle GPT-5 specific parameters
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
            
            # Calculate execution time
            execution_time = (timezone.now() - execution_start).total_seconds()
            
            if result.success:
                # Update execution with success
                execution.status = AgentStatus.COMPLETED
                execution.result = {'content': result.content[:1000]}  # Store first 1000 chars
                execution.token_usage = result.token_usage
                execution.execution_time_seconds = execution_time
                execution.completed_at = timezone.now()
                execution.save()
                
                # Update agent metrics for learning
                self._update_agent_metrics(agent, success=True, execution_time=execution_time)
                
                return {
                    'success': True,
                    'content': result.content,
                    'agent_used': agent.name,
                    'provider': provider,
                    'model': agent.llm_model,
                    'token_usage': result.token_usage,
                    'generation_time_ms': result.generation_time_ms,
                    'execution_id': execution_id
                }
            else:
                # Update execution with failure
                execution.status = AgentStatus.FAILED
                execution.error_message = result.error_message
                execution.execution_time_seconds = execution_time
                execution.completed_at = timezone.now()
                execution.save()
                
                # Update agent metrics for learning
                self._update_agent_metrics(agent, success=False, execution_time=execution_time)
                
                return {
                    'success': False,
                    'error': result.error_message,
                    'fallback_to_direct': True,
                    'execution_id': execution_id
                }
                
        except Exception as e:
            logger.error(f"Error in direct agent execution: {e}")
            
            # Update execution record if it exists
            try:
                if 'execution' in locals():
                    execution.status = AgentStatus.FAILED
                    execution.error_message = str(e)
                    execution.completed_at = timezone.now()
                    execution.save()
            except Exception as _e:
                logger.warning(
                    "agent_integration._execute_agent_directly: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
                
            return {
                'success': False,
                'error': str(e),
                'fallback_to_direct': True,
                'execution_id': execution_id
            }
    
    def _update_agent_metrics(self, agent: UnifiedAgentTemplate, success: bool, execution_time: float):
        """
        Update agent performance metrics for learning
        """
        try:
            # Update usage count
            agent.usage_count += 1
            
            # Update success rate (rolling average)
            if agent.usage_count == 1:
                agent.success_rate = 100.0 if success else 0.0
            else:
                # Calculate new success rate as rolling average
                current_success = 1.0 if success else 0.0
                agent.success_rate = ((agent.success_rate * (agent.usage_count - 1)) + (current_success * 100)) / agent.usage_count
            
            # Update average completion time
            if agent.avg_completion_time == 0:
                agent.avg_completion_time = execution_time
            else:
                agent.avg_completion_time = ((agent.avg_completion_time * (agent.usage_count - 1)) + execution_time) / agent.usage_count
            
            # Save updated metrics
            agent.save(update_fields=['usage_count', 'success_rate', 'avg_completion_time'])
            
            # If learning is enabled, trigger learning update
            if agent.learning_enabled:
                self._trigger_learning_update(agent, success, execution_time)
                
        except Exception as e:
            logger.error(f"Error updating agent metrics: {e}")
    
    def _trigger_learning_update(self, agent: UnifiedAgentTemplate, success: bool, execution_time: float):
        """
        Trigger learning updates for agents with learning enabled
        """
        try:
            # Log learning event
            logger.info(f"Learning update for {agent.name}: success={success}, time={execution_time:.2f}s")
            
            # Update routing keywords based on success
            if success and execution_time < 5.0:  # Fast, successful execution
                # This agent performed well, increase its routing priority
                # Could update routing_keywords or scoring logic here
                pass
            elif not success:
                # This agent failed, might need to adjust routing
                # Could decrease confidence scores for similar tasks
                pass
                
            # Store learning outcome for future analysis
            from self_awareness.models import SystemEvolution
            SystemEvolution.objects.create(
                evolution_type='optimization',  # Using valid choice from EVOLUTION_TYPES
                title=f"Agent {agent.name} Learning Update",
                description=f"Agent {agent.name} execution: {'success' if success else 'failure'}",
                rationale=f"Tracking agent performance for continuous improvement",
                expected_benefit=f"Improved agent performance based on execution feedback",
                risk_assessment="Low risk - tracking only",
                rollback_plan="N/A - tracking only",
                confidence_score=0.7 if success else 0.3,
                priority=5,
                status='completed',
                success_metrics={
                    'agent_id': str(agent.id),
                    'agent_name': agent.name,
                    'success': success,
                    'execution_time': execution_time
                }
            )
            
        except Exception as e:
            logger.error(f"Error in learning update: {e}")


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
            'target_model': target_model or 'gpt-5-mini',
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