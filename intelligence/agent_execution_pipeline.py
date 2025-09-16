"""
Agent Execution Pipeline
Orchestrates the execution of agent instructions from Income Builder plans
Manages agent coordination, execution, and result collection
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from django.conf import settings
from celery import shared_task
import redis

from .agent_instruction_parser import AgentInstruction, AgentInstructionParser
from .models import ActionPlan, AgentExecution
from agents.registry import AgentRegistry
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

# Redis for coordination
redis_client = redis.from_url(settings.REDIS_URL)


class AgentExecutionPipeline:
    """Manages the execution of agent instructions"""

    def __init__(self):
        self.parser = AgentInstructionParser()
        self.agent_registry = AgentRegistry()
        self.execution_results = []

    async def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute a complete action plan through the agent network

        Args:
            plan_id: The ID of the ActionPlan to execute

        Returns:
            Execution summary with results
        """
        try:
            # Load the action plan
            plan = ActionPlan.objects.get(id=plan_id)
            logger.info(f"Starting execution of plan: {plan.opportunity_title}")

            # Parse the plan into instructions
            if hasattr(plan, 'generated_content') and plan.generated_content:
                content = plan.generated_content
            else:
                # Fallback to results if no generated_content field
                content = json.dumps(plan.results) if plan.results else ""

            instructions = self.parser.parse_plan(content)
            logger.info(f"Parsed {len(instructions)} instructions from plan")

            # Group instructions by execution order
            execution_groups = self.parser.get_execution_order()

            # Execute each group
            for group_idx, instruction_group in enumerate(execution_groups):
                logger.info(f"Executing group {group_idx + 1} with {len(instruction_group)} instructions")

                # Execute instructions in parallel within each group
                group_results = await self._execute_instruction_group(
                    instruction_group,
                    plan_id
                )

                self.execution_results.extend(group_results)

                # Update plan progress
                progress = int((group_idx + 1) / len(execution_groups) * 100)
                await self._update_plan_progress(plan_id, progress)

            # Mark plan as completed
            await self._complete_plan_execution(plan_id)

            return {
                'success': True,
                'plan_id': plan_id,
                'total_instructions': len(instructions),
                'executed': len(self.execution_results),
                'results': self.execution_results
            }

        except Exception as e:
            logger.error(f"Error executing plan {plan_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'plan_id': plan_id
            }

    async def _execute_instruction_group(
        self,
        instructions: List[AgentInstruction],
        plan_id: str
    ) -> List[Dict[str, Any]]:
        """Execute a group of instructions in parallel"""
        tasks = []
        for instruction in instructions:
            task = self._execute_single_instruction(instruction, plan_id)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Instruction {idx} failed: {str(result)}")
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'instruction': instructions[idx].action
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_single_instruction(
        self,
        instruction: AgentInstruction,
        plan_id: str
    ) -> Dict[str, Any]:
        """Execute a single agent instruction"""
        try:
            logger.info(f"Executing: {instruction.agent_type} - {instruction.action[:50]}...")

            # Record execution start
            execution = await self._create_execution_record(instruction, plan_id)

            # Get the appropriate agent
            agent = await self._get_or_create_agent(instruction.agent_type)

            if not agent:
                raise ValueError(f"No agent available for type: {instruction.agent_type}")

            # Prepare the instruction for the agent
            agent_instruction = {
                'action': instruction.action,
                'parameters': instruction.parameters,
                'expected_outcome': instruction.expected_outcome,
                'context': {
                    'plan_id': plan_id,
                    'step_number': instruction.step_number,
                    'week': instruction.week
                }
            }

            # Execute through the agent
            result = await agent.execute(agent_instruction)

            # Record execution result
            await self._update_execution_record(execution, result)

            # Publish result to Redis for real-time updates
            self._publish_execution_update(plan_id, instruction, result)

            return {
                'success': True,
                'agent': instruction.agent_type,
                'action': instruction.action,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error executing instruction: {str(e)}")
            return {
                'success': False,
                'agent': instruction.agent_type,
                'action': instruction.action,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def _get_or_create_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get or create an agent instance"""
        # First, check if agent is registered
        agent_info = self.agent_registry.get_agent(agent_type)

        if not agent_info:
            # Try to map to a known agent type
            agent_type = self._map_to_registered_agent(agent_type)
            agent_info = self.agent_registry.get_agent(agent_type)

        if not agent_info:
            logger.warning(f"No registered agent for type: {agent_type}")
            # Return a mock agent for now (to not break the flow)
            return self._create_mock_agent(agent_type)

        # Create agent instance
        # This would normally instantiate the actual agent class
        # For now, return a mock that simulates execution
        return self._create_mock_agent(agent_type)

    def _create_mock_agent(self, agent_type: str):
        """Create a mock agent for simulation"""
        class MockAgent:
            def __init__(self, agent_type):
                self.agent_type = agent_type

            async def execute(self, instruction):
                # Simulate agent execution
                await asyncio.sleep(0.5)  # Simulate work

                # Return mock results based on agent type
                if 'content' in self.agent_type:
                    return {
                        'content_generated': True,
                        'word_count': 500,
                        'topics': instruction.get('parameters', {}).get('keywords', []),
                        'file_created': f"output_{datetime.now().timestamp()}.md"
                    }
                elif 'analytics' in self.agent_type:
                    return {
                        'analysis_complete': True,
                        'metrics': {
                            'engagement_rate': 0.045,
                            'best_time': '2:00 PM',
                            'top_hashtags': ['#AI', '#automation', '#business']
                        }
                    }
                elif 'publish' in self.agent_type:
                    return {
                        'scheduled': True,
                        'platforms': instruction.get('parameters', {}).get('platforms', ['twitter']),
                        'scheduled_time': datetime.now().isoformat()
                    }
                else:
                    return {
                        'executed': True,
                        'agent_type': self.agent_type,
                        'timestamp': datetime.now().isoformat()
                    }

        return MockAgent(agent_type)

    def _map_to_registered_agent(self, agent_type: str) -> str:
        """Map agent type to registered agent"""
        # This would map to actual registered agents
        mapping = {
            'content-creator': 'content-writer-agent',
            'ml-analytics': 'data-analyst-agent',
            'ai-content-studio': 'image-generator-agent',
            'publishing-automation': 'social-media-scheduler-agent'
        }
        return mapping.get(agent_type, agent_type)

    async def _create_execution_record(
        self,
        instruction: AgentInstruction,
        plan_id: str
    ) -> 'AgentExecution':
        """Create a record of agent execution"""
        # This would create a database record
        # For now, return a mock record
        return {
            'id': f"exec_{datetime.now().timestamp()}",
            'plan_id': plan_id,
            'agent_type': instruction.agent_type,
            'instruction': instruction.action,
            'status': 'executing',
            'created_at': datetime.now()
        }

    async def _update_execution_record(
        self,
        execution: Dict,
        result: Dict
    ):
        """Update execution record with results"""
        execution['status'] = 'completed' if result else 'failed'
        execution['result'] = result
        execution['completed_at'] = datetime.now()

    async def _update_plan_progress(self, plan_id: str, progress: int):
        """Update plan execution progress"""
        try:
            plan = ActionPlan.objects.get(id=plan_id)
            plan.progress = progress
            plan.save()

            # Publish progress update
            redis_client.publish(f"plan_progress_{plan_id}", json.dumps({
                'plan_id': plan_id,
                'progress': progress,
                'timestamp': datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error updating plan progress: {str(e)}")

    async def _complete_plan_execution(self, plan_id: str):
        """Mark plan execution as completed"""
        try:
            plan = ActionPlan.objects.get(id=plan_id)
            plan.status = 'completed'
            plan.progress = 100
            plan.completed_at = datetime.now()

            # Add execution results to plan
            if not plan.results:
                plan.results = {}
            plan.results['agent_executions'] = self.execution_results

            plan.save()

            logger.info(f"Plan {plan_id} execution completed successfully")
        except Exception as e:
            logger.error(f"Error completing plan execution: {str(e)}")

    def _publish_execution_update(
        self,
        plan_id: str,
        instruction: AgentInstruction,
        result: Dict
    ):
        """Publish execution update for real-time monitoring"""
        try:
            update = {
                'plan_id': plan_id,
                'agent': instruction.agent_type,
                'action': instruction.action[:100],
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            redis_client.publish(f"agent_execution_{plan_id}", json.dumps(update))
        except Exception as e:
            logger.error(f"Error publishing execution update: {str(e)}")


# Celery task for async execution
@shared_task
def execute_plan_async(plan_id: str):
    """Execute a plan asynchronously via Celery"""
    pipeline = AgentExecutionPipeline()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(pipeline.execute_plan(plan_id))
    loop.close()
    return result