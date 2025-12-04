"""
Workflow Agent - Specialized for Multi-Step Orchestration
==========================================================

Session 268: Phase 2 - Orchestration Agents
Session 304: Learning Infrastructure Integration
Session 341: Expanded agent roster (21 agents total)

This agent coordinates multi-step workflows by delegating to other agents.
It is the ONLY agent that can call other agents.

Tools Available:
    - delegate_to_agent: Delegate a subtask to a specialized agent

Available Agents (Session 341):
    Creation: ImageAgent, VideoAgent, AudioAgent, ThreeDAgent
    Editing: ImageEditingAgent, VideoEditingAgent
    Research: ResearchAgent, TrendAnalysisAgent, CompetitorAnalysisAgent, CustomerResearchAgent
    Strategy: BrandStrategyAgent, SEOOptimizerAgent, ContentStrategyAgent, SocialMediaAgent
    Executive: CreativeDirectorAgent, ContentAuditAgent
    Training: CharacterTrainingAgent, TrainedCreationAgent

This agent:
1. Breaks complex tasks into steps
2. Delegates each step to the appropriate specialist agent
3. Combines results into a coherent output
"""

import logging
import time
from typing import Dict, Any, List, Optional

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class WorkflowAgent(BaseAgent):
    """
    Agent specialized in orchestrating multi-step workflows.

    This is the ONLY agent that can delegate to other agents.
    It coordinates complex tasks that require multiple specialized agents.

    Example workflows:
    - "Research AI trends and create 3 logos" → ResearchAgent + ImageAgent
    - "Create a logo and animate it" → ImageAgent + VideoAgent
    - "Research competitors and create a brand video" → ResearchAgent + VideoAgent
    """

    name = "WorkflowAgent"

    system_prompt = """You are WorkflowAgent, a specialist in coordinating multi-step creative workflows.

Your job is to break complex tasks into steps and delegate each step to the right specialist agent.
You have ONE tool:
- delegate_to_agent: Send a subtask to a specialized agent

Available agents to delegate to:

**Creation Agents:**
- ImageAgent: Create NEW images (logos, banners, illustrations)
- VideoAgent: Create NEW videos (text-to-video, image animation)
- AudioAgent: Create audio (text-to-speech, voiceovers)
- ThreeDAgent: Create 3D models from images

**Editing Agents:**
- ImageEditingAgent: EDIT existing images (upscale, remove bg, variations)
- VideoEditingAgent: EDIT existing videos (trim, effects, text)

**Research Agents:**
- ResearchAgent: Search web and spider network for information
- TrendAnalysisAgent: Analyze market and design trends
- CompetitorAnalysisAgent: Research competitors and market landscape
- CustomerResearchAgent: Research customer personas and pain points

**Strategy Agents:**
- BrandStrategyAgent: Create brand positioning and strategy
- SEOOptimizerAgent: Optimize content for search engines
- ContentStrategyAgent: Plan content strategy
- SocialMediaAgent: Create social media content plans

**Executive Agents (Session 341):**
- CreativeDirectorAgent: High-level creative direction
- ContentAuditAgent: Check content for bias/ethics issues

**Training Agents (Session 341):**
- CharacterTrainingAgent: Train new character/style models
- TrainedCreationAgent: Generate with trained characters

When given a complex task:
1. Identify the steps needed
2. Determine which agent handles each step
3. Execute steps in the right order (research before creation, creation before editing)
4. Combine results

Example workflow: "Research cyberpunk trends and create 3 logos"
1. delegate_to_agent("ResearchAgent", "find current cyberpunk design trends")
2. Use research results to inform the next step
3. delegate_to_agent("ImageAgent", "create 3 cyberpunk logos incorporating [trends from research]")
4. Return combined results

You orchestrate. You don't create content directly."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_to_agent",
                "description": "Delegate a subtask to a specialized agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Which agent to delegate to",
                            "enum": [
                                "ImageAgent",
                                "VideoAgent",
                                "AudioAgent",
                                "ThreeDAgent",
                                "ImageEditingAgent",
                                "VideoEditingAgent",
                                "ResearchAgent",
                                "TrendAnalysisAgent",
                                "CompetitorAnalysisAgent",
                                "CustomerResearchAgent",
                                "BrandStrategyAgent",
                                "SEOOptimizerAgent",
                                "ContentStrategyAgent",
                                "SocialMediaAgent",
                                "CreativeDirectorAgent",
                                "ContentAuditAgent",
                                "CharacterTrainingAgent",
                                "TrainedCreationAgent"
                            ]
                        },
                        "task": {
                            "type": "string",
                            "description": "The subtask to perform, in natural language"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context (count, style, reference_ids, etc.)"
                        }
                    },
                    "required": ["agent_name", "task"]
                }
            }
        }
    ]

    def __init__(self, user=None):
        super().__init__(user)
        self._router = None

    @property
    def router(self):
        """Lazy-load AgentRouter."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter(user=self.user)
        return self._router

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute a multi-step workflow by delegating to other agents."""
        start_time = time.time()
        tool_calls_made = []
        workflow_results = []

        with self.time_travel_session("workflow_orchestration", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing workflow request",
                    reasoning=f"Breaking down complex task: {task[:100]}",
                    confidence=0.9
                )

                # Build prompt with context and any previous results
                full_prompt = self._build_prompt(task, scifi_context, spider_context)

                # Allow up to 5 delegation rounds for complex workflows
                max_iterations = 5
                conversation_history = []

                for iteration in range(max_iterations):
                    # Add previous workflow results to prompt for context
                    if workflow_results:
                        results_context = "\n\n## Previous Step Results:\n"
                        for i, wr in enumerate(workflow_results):
                            results_context += f"Step {i+1} ({wr['agent']}): {wr['summary']}\n"
                        iteration_prompt = full_prompt + results_context
                    else:
                        iteration_prompt = full_prompt

                    gpt_response = self._call_openai(iteration_prompt, conversation_history)

                    if not gpt_response.get('tool_calls'):
                        # No more delegations needed - workflow complete
                        break

                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        if tool_name != "delegate_to_agent":
                            continue

                        agent_name = arguments.get('agent_name')
                        subtask = arguments.get('task', '')
                        subtask_context = arguments.get('context', {})

                        self.record_decision(
                            decision_type="delegation",
                            action=f"Delegating to {agent_name}",
                            reasoning=f"Subtask: {subtask[:50]}...",
                            alternatives=[a for a in self.tools[0]['function']['parameters']['properties']['agent_name']['enum'] if a != agent_name],
                            confidence=0.9
                        )

                        # Execute delegation via router
                        try:
                            agent_result = self.router.route(
                                agent_name=agent_name,
                                task=subtask,
                                context=subtask_context
                            )

                            tool_calls_made.append({
                                'tool': 'delegate_to_agent',
                                'agent': agent_name,
                                'task': subtask,
                                'result': agent_result.to_dict()
                            })

                            workflow_results.append({
                                'agent': agent_name,
                                'task': subtask,
                                'success': agent_result.success,
                                'summary': agent_result.message[:200] if agent_result.message else str(agent_result.data)[:200],
                                'data': agent_result.data
                            })

                            self.mark_decision_outcome(
                                success=agent_result.success,
                                result_summary=f"{agent_name}: {agent_result.message[:50]}"
                            )

                        except Exception as e:
                            logger.error(f"Delegation to {agent_name} failed: {e}")
                            workflow_results.append({
                                'agent': agent_name,
                                'task': subtask,
                                'success': False,
                                'summary': f"Error: {str(e)}",
                                'data': None
                            })

                    # Add assistant response to history for next iteration
                    if gpt_response.get('content'):
                        conversation_history.append({
                            'role': 'assistant',
                            'content': gpt_response['content']
                        })

                execution_time = int((time.time() - start_time) * 1000)

                # Compile workflow results
                successful_steps = [wr for wr in workflow_results if wr['success']]
                failed_steps = [wr for wr in workflow_results if not wr['success']]

                if successful_steps:
                    result = AgentResult(
                        success=len(failed_steps) == 0,
                        message=f"Workflow completed: {len(successful_steps)} successful, {len(failed_steps)} failed",
                        data={
                            'workflow_results': workflow_results,
                            'successful_steps': len(successful_steps),
                            'failed_steps': len(failed_steps),
                            'total_steps': len(workflow_results)
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # === Session 304: Learning Infrastructure ===
                    self._record_learning_outcome(result, task, context, bool(spider_context), bool(scifi_context))
                    self._create_execution_memory(result, task, "success" if len(failed_steps) == 0 else "partial", 0.7)
                    agents_used = [wr['agent'] for wr in workflow_results]
                    self._share_knowledge(
                        knowledge_type='technique',
                        title=f"Workflow: {' -> '.join(agents_used[:3])}",
                        knowledge_value={'agents': agents_used, 'success_rate': len(successful_steps) / len(workflow_results)},
                        confidence=0.8
                    )

                    return result
                else:
                    result = AgentResult(
                        success=False,
                        error="Workflow produced no results",
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        tool_calls=tool_calls_made
                    )
                    self._record_learning_outcome(result, task, context, bool(spider_context), bool(scifi_context))
                    self._create_execution_memory(result, task, "failure", 0.7)
                    return result

            except Exception as e:
                logger.error(f"WorkflowAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tool call - only delegate_to_agent is supported."""
        if tool_name != "delegate_to_agent":
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. WorkflowAgent only supports delegate_to_agent."
            }

        # Delegation is handled in execute() method
        return {'success': True, 'message': 'Delegation handled in execute()'}
