"""
Personal Assistant Agent Integration
===================================

Connects the Personal Assistant to the 149-agent system for unified orchestration.
Allows the assistant to route tasks to specialized agents and coordinate complex workflows.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from intelligence.agent_execution_pipeline import AgentExecutionPipeline
from intelligence.agent_instruction_parser import AgentInstruction, AgentInstructionParser
from intelligence.real_agents import AgentFactory
from core.agents.registry import get_agent_registry

# Session 352: Pipeline Visualizer integration
from core.pipeline_progress_consumer import (
    broadcast_stage_started,
    broadcast_stage_completed,
    broadcast_stage_failed
)

logger = logging.getLogger(__name__)


class PersonalAssistantAgentIntegration:
    """
    Integrates Personal Assistant with the 149-agent system for intelligent task routing
    """

    def __init__(self):
        self.agent_registry = get_agent_registry()
        self.pipeline = AgentExecutionPipeline()
        self.parser = AgentInstructionParser()
        self.execution_history = []

    def should_route_to_agents(self, message: str) -> bool:
        """
        Determine if a message should be routed through the agent system
        """
        message_lower = message.lower()

        # FIRST: Check if this is a QUESTION ABOUT agents (should NOT be routed)
        agent_question_patterns = [
            'recommend', 'suggest', 'which agent', 'what agent', 'best agent',
            'can you', 'help me find', 'tell me about', 'show me', 'list',
            'who should', 'advice on', 'guidance on'
        ]

        if 'agent' in message_lower and any(pattern in message_lower for pattern in agent_question_patterns):
            return False  # Don't route questions about agents

        # Check for greeting/conversational patterns that should not be routed
        greeting_patterns = ['hi', 'hello', 'hey', 'how are you', 'what can you do']
        if any(pattern in message_lower for pattern in greeting_patterns):
            return False

        # Keywords that indicate agent tasks (actual work to be done)
        agent_keywords = [
            'create', 'generate', 'analyze', 'optimize', 'schedule', 'post',
            'write', 'design', 'research', 'automate', 'execute', 'build',
            'deploy', 'monitor', 'track', 'calculate', 'process', 'extract'
        ]

        # Task-specific patterns (actual deliverables)
        task_patterns = [
            'content creation', 'image generation', 'seo optimization',
            'social media', 'email campaign', 'market research',
            'data analysis', 'automation', 'publishing'
        ]

        # Check for direct agent execution requests
        if 'agent' in message_lower and any(word in message_lower for word in ['use', 'run', 'execute']):
            return True

        # Check for action keywords (but not in questions)
        question_words = ['what', 'how', 'who', 'where', 'when', 'why', 'which', 'can you', 'could you', 'would you']
        is_question = any(q in message_lower for q in question_words)

        if not is_question:
            # Check for direct agent keywords only if it's not a question
            if any(keyword in message_lower for keyword in agent_keywords):
                return True

            # Check for task patterns only if it's not a question
            if any(pattern in message_lower for pattern in task_patterns):
                return True

        return False

    def find_best_agents_for_task(self, message: str, max_agents: int = 3) -> List[Dict[str, Any]]:
        """
        Find the best agents for a given task
        """
        try:
            # Use the registry to find suitable agents
            best_agent = self.agent_registry.find_best_agent(
                task_description=message,
                required_capabilities=self._extract_capabilities_from_message(message)
            )

            if best_agent:
                return [{
                    'name': best_agent['name'],
                    'display_name': best_agent.get('display_name', best_agent['name']),
                    'specialization': best_agent.get('specialization', 'general'),
                    'capabilities': best_agent.get('capabilities', []),
                    'confidence': 0.8  # Would be calculated based on matching
                }]

            # Fallback: get agents by category
            agents = self.agent_registry.list_agents()
            suitable_agents = []

            message_lower = message.lower()

            # Map message content to agent categories
            category_mapping = {
                'content': ['content-creator', 'content-writer', 'blog-writer'],
                'image': ['image-generator', 'ai-content-studio'],
                'social': ['social-media-scheduler', 'social-media-manager'],
                'email': ['email-marketer', 'email-marketing'],
                'seo': ['seo-optimizer'],
                'analytics': ['ml-analytics', 'data-analyst'],
                'research': ['market-researcher', 'market-research']
            }

            for category, agent_types in category_mapping.items():
                if category in message_lower:
                    for agent in agents:
                        if any(agent_type in agent['name'].lower() for agent_type in agent_types):
                            suitable_agents.append({
                                'name': agent['name'],
                                'display_name': agent.get('display_name', agent['name']),
                                'specialization': agent.get('specialization', category),
                                'capabilities': agent.get('capabilities', []),
                                'confidence': 0.7
                            })

            return suitable_agents[:max_agents]

        except Exception as e:
            logger.error(f"Error finding agents for task: {str(e)}")
            return []

    def _extract_capabilities_from_message(self, message: str) -> List[str]:
        """
        Extract required capabilities from message
        """
        message_lower = message.lower()
        capabilities = []

        capability_keywords = {
            'content_creation': ['write', 'create', 'generate', 'content', 'article', 'blog'],
            'image_generation': ['image', 'picture', 'visual', 'graphic', 'design'],
            'social_media': ['social', 'twitter', 'facebook', 'instagram', 'post'],
            'seo_optimization': ['seo', 'search', 'optimize', 'ranking'],
            'data_analysis': ['analyze', 'data', 'metrics', 'statistics', 'insights'],
            'email_marketing': ['email', 'newsletter', 'campaign', 'marketing'],
            'automation': ['automate', 'schedule', 'recurring', 'batch']
        }

        for capability, keywords in capability_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                capabilities.append(capability)

        return capabilities

    async def execute_through_agents(self, message: str, selected_agents: List[str] = None) -> Dict[str, Any]:
        """
        Execute a task through the agent system
        """
        try:
            if selected_agents:
                # Execute specific agents
                results = []
                for agent_name in selected_agents:
                    result = await self._execute_single_agent(agent_name, message)
                    results.append(result)

                return {
                    'success': True,
                    'execution_type': 'selected_agents',
                    'agents_used': selected_agents,
                    'results': results,
                    'summary': self._create_execution_summary(results)
                }

            else:
                # Auto-route to best agents
                best_agents = self.find_best_agents_for_task(message)

                if not best_agents:
                    return {
                        'success': False,
                        'error': 'No suitable agents found for this task',
                        'suggestion': 'Try being more specific about what you want to accomplish'
                    }

                # Execute the best agent
                primary_agent = best_agents[0]
                result = await self._execute_single_agent(primary_agent['name'], message)

                return {
                    'success': True,
                    'execution_type': 'auto_routed',
                    'primary_agent': primary_agent['name'],
                    'result': result,
                    'alternatives': [agent['name'] for agent in best_agents[1:]]
                }

        except Exception as e:
            logger.error(f"Error executing through agents: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_single_agent(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Execute a single agent with a task.

        Session 352: Now broadcasts to Pipeline Visualizer for real-time UI updates!
        """
        start_time = datetime.now()

        # Session 352: Map agent names to pipeline stage types
        agent_to_stage = {
            'image_generation_agent': 'image',
            'video_generation_agent': 'video',
            'audio_generation_agent': 'audio',
            '3d_generation_agent': '3d',
            'research_agent': 'initial_research',
            'trend_analysis_agent': 'trend_analysis',
            'competitor_analysis_agent': 'competitor_analysis',
            'customer_research_agent': 'customer_research',
            'brand_identity_agent': 'brand_strategy',
            'seo_optimizer_agent': 'seo',
            'content_strategy_agent': 'content_audit',
            'workflow_orchestration_agent': 'creative_direction',
            'prompt_engineering_agent': 'brief',
        }

        # Determine stage and pipeline type
        stage = agent_to_stage.get(agent_name, agent_name.replace('_agent', ''))
        pipeline_type = 'creative' if stage in ['image', 'video', 'audio', '3d', 'editing', 'brief', 'creative_direction', 'seo'] else 'research'

        try:
            # Session 352: Broadcast stage STARTED to Pipeline Visualizer
            broadcast_stage_started(
                stage=stage,
                pipeline_type=pipeline_type,
                agent_name=agent_name,
                business_idea=task[:100] if task else None
            )
            logger.info(f"🚀 [Pipeline] Agent started: {agent_name} ({stage})")

            # Create an agent instance
            agent = AgentFactory.create_agent(agent_name)

            # Create instruction
            instruction = {
                'action': task,
                'parameters': {},
                'expected_outcome': 'Complete the requested task',
                'context': {
                    'source': 'personal_assistant',
                    'timestamp': datetime.now().isoformat()
                }
            }

            # Execute the agent
            result = await agent.execute(instruction)

            execution_time = (datetime.now() - start_time).total_seconds()
            execution_time_ms = int(execution_time * 1000)
            success = 'error' not in result

            # Session 352: Broadcast stage COMPLETED to Pipeline Visualizer
            broadcast_stage_completed(
                stage=stage,
                pipeline_type=pipeline_type,
                agent_name=agent_name,
                success=success,
                duration_ms=execution_time_ms,
                summary=str(result)[:200] if result else f'{agent_name} completed'
            )
            logger.info(f"✅ [Pipeline] Agent completed: {agent_name} in {execution_time:.1f}s")

            # Log execution
            execution_log = {
                'agent_name': agent_name,
                'task': task[:100],
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'result_summary': str(result)[:200]
            }
            self.execution_history.append(execution_log)

            return {
                'agent_name': agent_name,
                'task': task,
                'success': success,
                'result': result,
                'execution_time': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error executing agent {agent_name}: {str(e)}")

            # Session 352: Broadcast stage FAILED to Pipeline Visualizer
            broadcast_stage_failed(
                stage=stage,
                pipeline_type=pipeline_type,
                agent_name=agent_name,
                error=str(e)[:200]
            )
            logger.warning(f"❌ [Pipeline] Agent failed: {agent_name} - {str(e)[:100]}")

            return {
                'agent_name': agent_name,
                'task': task,
                'success': False,
                'error': str(e),
                'execution_time': datetime.now().isoformat()
            }

    def _create_execution_summary(self, results: List[Dict[str, Any]]) -> str:
        """
        Create a human-readable summary of agent executions
        """
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]

        summary = f"Executed {len(results)} agents: {len(successful)} successful, {len(failed)} failed."

        if successful:
            summary += f"\n\nSuccessful executions:"
            for result in successful[:3]:  # Show first 3
                agent_name = result['agent_name']
                # Extract key info from result
                if 'file_created' in result.get('result', {}):
                    summary += f"\n• {agent_name}: Created {result['result']['file_created']}"
                elif 'content_generated' in result.get('result', {}):
                    summary += f"\n• {agent_name}: Generated content successfully"
                elif 'image_generated' in result.get('result', {}):
                    summary += f"\n• {agent_name}: Generated image successfully"
                else:
                    summary += f"\n• {agent_name}: Task completed"

        if failed:
            summary += f"\n\nFailed executions:"
            for result in failed[:2]:  # Show first 2 failures
                agent_name = result['agent_name']
                error = result.get('error', 'Unknown error')
                summary += f"\n• {agent_name}: {error[:50]}..."

        return summary

    def get_agent_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent agent execution history
        """
        return self.execution_history[-limit:]

    def get_available_agent_summary(self) -> Dict[str, Any]:
        """
        Get summary of available agents for the assistant
        """
        try:
            stats = self.agent_registry.get_registry_stats()
            agents = self.agent_registry.list_agents()

            # Group by specialization
            by_specialization = {}
            for agent in agents:
                spec = agent.get('specialization', 'general')
                if spec not in by_specialization:
                    by_specialization[spec] = 0
                by_specialization[spec] += 1

            return {
                'total_agents': stats.total_agents,
                'active_agents': stats.active_agents,
                'total_executions': stats.total_executions,
                'avg_success_rate': stats.avg_success_rate,
                'by_specialization': by_specialization,
                'recent_executions': len(self.execution_history)
            }

        except Exception as e:
            logger.error(f"Error getting agent summary: {str(e)}")
            return {
                'total_agents': 0,
                'active_agents': 0,
                'error': str(e)
            }

    def create_agent_recommendation(self, message: str) -> str:
        """
        Create a recommendation for which agents to use
        """
        best_agents = self.find_best_agents_for_task(message)

        if not best_agents:
            return "I couldn't find specific agents for this task. You might want to be more specific about what you need."

        if len(best_agents) == 1:
            agent = best_agents[0]
            return f"I recommend using the **{agent['display_name']}** for this task. It specializes in {agent['specialization']} and has capabilities including {', '.join(agent['capabilities'][:3])}."

        else:
            recommendations = []
            for agent in best_agents[:3]:
                recommendations.append(f"**{agent['display_name']}** ({agent['specialization']})")

            return f"I found several agents that could help:\n" + "\n".join(f"• {rec}" for rec in recommendations) + "\n\nWould you like me to use the primary recommendation or select a specific agent?"


# Global instance
personal_assistant_agent_integration = PersonalAssistantAgentIntegration()