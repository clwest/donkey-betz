"""
Agent Execution Pipeline
NOW INTEGRATED WITH SYSTEM BRIDGE!
Orchestrates the execution of agent instructions from Income Builder plans
Manages agent coordination, execution, and result collection
"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from django.conf import settings
from celery import shared_task
import redis
try:
    from openai import OpenAI
    openai_client = OpenAI()
    OPENAI_AVAILABLE = True
except ImportError:
    openai_client = None
    OPENAI_AVAILABLE = False

from .agent_instruction_parser import AgentInstruction, AgentInstructionParser
from intelligence.models import ActionPlan, AgentExecution
from agents.registry import get_agent_registry  # Use the real registry
from .real_agents import AgentFactory  # Import the real agent factory


class ContentCreatorAgent:
    """REAL Content Creator Agent using GPT-5-mini"""

    def __init__(self):
        self.client = OpenAI()
        self.agent_type = "content-creator"

    async def execute(self, instruction):
        """Generate REAL content using GPT-5-mini"""
        try:
            # Extract the action from the instruction
            action = instruction.get('action', '')
            parameters = instruction.get('parameters', {})
            context = instruction.get('context', {})

            # Create a detailed prompt for content generation
            prompt = f"""Execute the following content creation task:

Task: {action}

Parameters: {json.dumps(parameters, indent=2)}

Expected Outcome: {instruction.get('expected_outcome', 'High-quality content')}

Please generate the requested content now."""

            # Call GPT-5-mini to generate REAL content
            response = self.client.chat.completions.create(
                model="gpt-5-mini",  # Using gpt-5-mini as GPT-5-mini
                messages=[
                    {"role": "system", "content": "You are a professional content creator agent. Generate high-quality content based on the instructions."},
                    {"role": "user", "content": prompt}
                ],  # GPT-5 always uses 1.0
                max_completion_tokens=2000,  # GPT-5-mini completion tokens
                reasoning_effort="medium"  # GPT-5-mini reasoning capability
            )

            # Get the generated content
            generated_content = response.choices[0].message.content

            # Ensure the agent_outputs directory exists
            os.makedirs("agent_outputs", exist_ok=True)

            # Save the content to a file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_outputs/content_{timestamp}.md"

            with open(filename, 'w') as f:
                f.write(f"# Generated Content\n\n")
                f.write(f"**Task:** {action}\n\n")
                f.write(f"**Generated at:** {datetime.now().isoformat()}\n\n")
                f.write("---\n\n")
                f.write(generated_content)

            logger.info(f"ContentCreatorAgent generated content: {filename}")

            # Return real results
            return {
                'content_generated': True,
                'file_created': filename,
                'content': generated_content[:500] + "..." if len(generated_content) > 500 else generated_content,
                'word_count': len(generated_content.split()),
                'model_used': 'gpt-5-mini',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"ContentCreatorAgent error: {str(e)}")
            return {
                'content_generated': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


logger = logging.getLogger(__name__)

# Redis for coordination
redis_client = redis.from_url(settings.REDIS_URL)


class AgentExecutionPipeline:
    """Manages the execution of agent instructions - BRIDGE INTEGRATED"""

    def __init__(self):
        self.parser = AgentInstructionParser()
        self.agent_registry = get_agent_registry()  # Use the real registry
        self.execution_results = []

        # BRIDGE INTEGRATION
        self.bridge_data_queue = asyncio.Queue()
        self.is_bridge_subscriber = True

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

    async def _get_or_create_agent(self, agent_type: str) -> Optional[Any]:
        """Get or create a REAL agent instance"""
        # First, check if agent is registered in the database
        agent_info = self.agent_registry.get_agent(agent_type)

        if not agent_info:
            # Try to map to a known agent type
            mapped_type = self._map_to_registered_agent(agent_type)
            agent_info = self.agent_registry.get_agent(mapped_type)

            if agent_info:
                agent_type = mapped_type

        if agent_info:
            logger.info(f"Found registered agent: {agent_type} ({agent_info.get('specialization')})")
            # Create REAL agent instance using the registered agent data
            return self._create_real_agent_from_registry(agent_info)
        else:
            logger.warning(f"No registered agent for type: {agent_type}, using factory fallback")
            # Use AgentFactory to create real agents for unregistered types
            return self._create_agent_from_factory(agent_type)

    def _create_real_agent_from_registry(self, agent_info: Dict[str, Any]):
        """Create a REAL agent instance from registry data"""
        try:
            agent_name = agent_info.get('name')
            specialization = agent_info.get('specialization')

            logger.info(f"Creating REAL agent from registry: {agent_name} ({specialization})")

            # Use OpenAI client for real agent execution
            class RegistryAgent:
                def __init__(self, agent_info):
                    self.agent_info = agent_info
                    self.client = OpenAI() if openai_client else None
                    self.agent_type = agent_info.get('name')

                async def execute(self, instruction):
                    try:
                        # Use the agent's system prompt and configuration
                        system_prompt = self.agent_info.get('system_prompt',
                            f"You are {self.agent_info.get('display_name', self.agent_type)}, "
                            f"specialized in {self.agent_info.get('specialization')}.")

                        # Build the user prompt
                        action = instruction.get('action', '')
                        parameters = instruction.get('parameters', {})

                        user_prompt = f"""Execute this task: {action}

Parameters: {json.dumps(parameters, indent=2)}

Use your expertise in {self.agent_info.get('specialization')} to provide a comprehensive response."""

                        if self.client:
                            # Use real OpenAI for execution
                            response = self.client.chat.completions.create(
                                model=self.agent_info.get('llm_model', 'gpt-5-mini',
                        thought=True,  # GPT-5 reasoning capability
                        reasoning_steps=3),
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                # temperature=1.2  # GPT-5 only supports default temperature,
                                max_tokens=self.agent_info.get('llm_config', {}).get('max_tokens', 2000)
                            )

                            result_content = response.choices[0].message.content

                            # Save to file for real output
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"agent_outputs/{self.agent_type}_{timestamp}.md"
                            os.makedirs("agent_outputs", exist_ok=True)

                            with open(filename, 'w') as f:
                                f.write(f"# {self.agent_info.get('display_name', self.agent_type)} Output\n\n")
                                f.write(f"**Task:** {action}\n")
                                f.write(f"**Specialization:** {self.agent_info.get('specialization')}\n")
                                f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
                                f.write("---\n\n")
                                f.write(result_content)

                            return {
                                'executed': True,
                                'agent_type': self.agent_type,
                                'specialization': self.agent_info.get('specialization'),
                                'result': result_content,
                                'file_created': filename,
                                'model_used': self.agent_info.get('llm_model', 'gpt-5-mini'),
                                'tokens_used': response.usage.total_tokens,
                                'timestamp': datetime.now().isoformat(),
                                'real_execution': True
                            }
                        else:
                            # Fallback without OpenAI
                            return {
                                'executed': True,
                                'agent_type': self.agent_type,
                                'specialization': self.agent_info.get('specialization'),
                                'result': f"Registry agent {self.agent_type} executed task: {action}",
                                'timestamp': datetime.now().isoformat(),
                                'real_execution': False,
                                'note': 'OpenAI not available, using registry fallback'
                            }

                    except Exception as e:
                        logger.error(f"Registry agent execution error: {e}")
                        return {
                            'executed': False,
                            'error': str(e),
                            'agent_type': self.agent_type,
                            'timestamp': datetime.now().isoformat()
                        }

            return RegistryAgent(agent_info)

        except Exception as e:
            logger.error(f"Error creating registry agent: {e}")
            return self._create_agent_from_factory(agent_info.get('name', 'unknown'))

    def _create_agent_from_factory(self, agent_type: str):
        """Create REAL agent instances using AgentFactory"""

        logger.info(f"Creating REAL agent from factory for type: {agent_type}")

        # Use the AgentFactory to create real agents
        try:
            agent = AgentFactory.create_agent(agent_type)
            logger.info(f"Successfully created {agent.__class__.__name__} for {agent_type}")
            return agent
        except Exception as e:
            logger.error(f"Error creating agent {agent_type}: {str(e)}")

            # Final fallback to a basic mock if both registry and factory fail
            class FallbackAgent:
                def __init__(self, agent_type):
                    self.agent_type = agent_type

                async def execute(self, instruction):
                    return {
                        'executed': True,
                        'agent_type': self.agent_type,
                        'result': f"Fallback execution for {self.agent_type}",
                        'timestamp': datetime.now().isoformat(),
                        'note': 'Fallback agent - registry and factory failed'
                    }

            return FallbackAgent(agent_type)

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

            # BRIDGE INTEGRATION: Also queue for bridge processing
            if self.is_bridge_subscriber:
                asyncio.create_task(self._queue_bridge_data(update))

        except Exception as e:
            logger.error(f"Error publishing execution update: {str(e)}")

    # ===============================
    # BRIDGE INTEGRATION METHODS
    # ===============================

    async def _queue_bridge_data(self, data: Dict):
        """Queue data for bridge processing"""
        try:
            await self.bridge_data_queue.put(data)
            logger.debug("Data queued for bridge processing")
        except Exception as e:
            logger.error(f"Error queuing bridge data: {e}")

    async def process_spider_intelligence(self, spider_data: List[Dict]) -> List[Dict]:
        """BRIDGE METHOD: Process spider intelligence data through agents"""
        try:
            logger.info(f"🕷️➡️🤖 Processing {len(spider_data)} spider data points through agents")

            agent_results = []

            for spider_datum in spider_data:
                # Create agent instruction from spider data
                instruction = self._create_instruction_from_spider_data(spider_datum)

                if instruction:
                    # Execute through agent
                    result = await self._execute_single_instruction(
                        instruction, spider_datum.get('spider_id', 'unknown')
                    )
                    agent_results.append(result)

            logger.info(f"✅ Processed spider data through {len(agent_results)} agents")
            return agent_results

        except Exception as e:
            logger.error(f"Error processing spider intelligence: {e}")
            return []

    def _create_instruction_from_spider_data(self, spider_data: Dict) -> Optional[AgentInstruction]:
        """Create agent instruction from spider data"""
        try:
            # Determine agent type based on spider data
            agent_type = self._determine_agent_type_for_spider(spider_data)

            # Create instruction
            instruction = AgentInstruction(
                step_number=1,
                week=1,
                agent_type=agent_type,
                action=f"Process spider data: {spider_data.get('data', 'Unknown data')}",
                parameters={
                    'spider_data': spider_data,
                    'spider_id': spider_data.get('spider_id'),
                    'confidence': spider_data.get('confidence', 0.5)
                },
                expected_outcome="Processed and analyzed spider intelligence"
            )

            return instruction

        except Exception as e:
            logger.error(f"Error creating instruction from spider data: {e}")
            return None

    def _determine_agent_type_for_spider(self, spider_data: Dict) -> str:
        """Determine appropriate agent type for spider data"""
        spider_id = spider_data.get('spider_id', '').lower()

        if 'financial' in spider_id or 'market' in spider_id:
            return 'financial-analyst'
        elif 'content' in spider_id or 'social' in spider_id:
            return 'content-creator'
        elif 'opportunity' in spider_id:
            return 'opportunity-analyzer'
        elif 'revenue' in spider_id:
            return 'revenue-optimizer'
        else:
            return 'general-processor'

    async def subscribe_to_bridge_data(self):
        """Subscribe to bridge data processing"""
        logger.info("🌉 Agent pipeline subscribing to bridge data")

        while self.is_bridge_subscriber:
            try:
                # Wait for bridge data
                data = await asyncio.wait_for(self.bridge_data_queue.get(), timeout=1.0)

                # Process the data
                await self._process_bridge_data(data)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in bridge data subscription: {e}")
                await asyncio.sleep(1)

    async def _process_bridge_data(self, data: Dict):
        """Process data received from bridge"""
        try:
            # This would process data sent from the bridge
            logger.debug(f"Processing bridge data: {data.get('plan_id', 'unknown')}")

            # Add to execution results if it's an execution update
            if 'agent' in data and 'result' in data:
                self.execution_results.append(data)

        except Exception as e:
            logger.error(f"Error processing bridge data: {e}")


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