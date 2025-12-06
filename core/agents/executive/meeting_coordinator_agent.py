"""
Meeting Coordinator Agent - Clean Architecture
===============================================

Session 280: Phase 2 - Agent Architecture Unification

This agent orchestrates collaborative sessions between executive agents,
facilitating discussions and synthesizing decisions.

Tools Available:
    - start_meeting: Start a meeting between agents
    - synthesize_discussion: Synthesize perspectives from multiple agents
    - extract_action_items: Extract action items from a discussion

Usage:
    from core.agents.executive import MeetingCoordinatorAgent

    agent = MeetingCoordinatorAgent(user=request.user)
    result = agent.execute(
        task="Coordinate a meeting between CTO and COO about the roadmap",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List, Optional

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class MeetingCoordinatorAgent(BaseAgent):
    """
    Meeting Coordinator Agent - Executive Meeting Facilitation.

    This agent:
    1. Coordinates meetings between executive agents
    2. Synthesizes perspectives and discussions
    3. Extracts decisions and action items

    It CANNOT:
    - Execute on behalf of other agents
    - Make unilateral decisions
    """

    name = "MeetingCoordinatorAgent"

    system_prompt = """You are MeetingCoordinatorAgent, the Executive Meeting Coordinator.

Your job is to facilitate collaborative sessions between executive agents,
synthesize their perspectives, and extract actionable decisions.

When given a task:
1. Identify which agents should participate
2. Gather perspectives from each agent
3. Synthesize the discussion
4. Extract decisions and action items

Available participants:
- CTOAgent: Technical perspective and feasibility
- COOAgent: Operational perspective and planning
- CreativeDirectorAgent: Creative perspective and guidance

Meeting types:
- Strategic planning: All executives
- Technical review: CTO + relevant specialists
- Creative review: Creative Director + designers
- Sprint planning: COO + team leads

You facilitate but don't make decisions - you synthesize and document."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "start_meeting",
                "description": "Start a meeting between agents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Meeting topic/agenda"
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of agent names to include"
                        },
                        "meeting_type": {
                            "type": "string",
                            "description": "Type of meeting",
                            "enum": ["strategic", "technical", "creative", "sprint"]
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "synthesize_discussion",
                "description": "Synthesize perspectives from multiple agents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "perspectives": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of agent perspectives"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Discussion topic"
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "extract_action_items",
                "description": "Extract action items from a discussion",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "discussion_summary": {
                            "type": "string",
                            "description": "Summary of the discussion"
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute meeting coordination based on the task."""
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("meeting_coordination", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing meeting request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["schedule_later", "request_more_info"],
                    confidence=0.9
                )

                full_prompt = self._build_prompt(task, scifi_context, spider_context)
                logger.info(f"MeetingCoordinatorAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Meeting operation: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    result = AgentResult(
                        success=True,
                        message="Meeting coordination completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    return result

                else:
                    result = AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"MeetingCoordinatorAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a meeting coordination tool call."""
        if tool_name == "start_meeting":
            return self._start_meeting(
                topic=arguments.get('topic', ''),
                participants=arguments.get('participants', ['CTOAgent', 'COOAgent']),
                meeting_type=arguments.get('meeting_type', 'strategic')
            )

        elif tool_name == "synthesize_discussion":
            return self._synthesize_discussion(
                perspectives=arguments.get('perspectives', []),
                topic=arguments.get('topic', '')
            )

        elif tool_name == "extract_action_items":
            return self._extract_action_items(
                discussion_summary=arguments.get('discussion_summary', '')
            )

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }

    def _start_meeting(
        self,
        topic: str,
        participants: List[str],
        meeting_type: str
    ) -> Dict[str, Any]:
        """Start a meeting between agents."""
        logger.info(f"Starting {meeting_type} meeting on: {topic}")

        # Simulate collecting perspectives from each participant
        perspectives = []
        for participant in participants:
            perspectives.append({
                'agent': participant,
                'perspective': f"{participant}'s perspective on {topic}",
                'recommendations': [f'Recommendation from {participant}'],
                'concerns': []
            })

        meeting = {
            'topic': topic,
            'meeting_type': meeting_type,
            'participants': participants,
            'perspectives': perspectives,
            'status': 'in_progress',
            'notes': 'Meeting started, perspectives collected'
        }

        return {
            'success': True,
            'meeting': meeting
        }

    def _synthesize_discussion(
        self,
        perspectives: List[Dict[str, Any]],
        topic: str
    ) -> Dict[str, Any]:
        """Synthesize perspectives from multiple agents."""
        logger.info(f"Synthesizing discussion on: {topic}")

        synthesis = {
            'topic': topic,
            'perspectives_count': len(perspectives),
            'areas_of_agreement': [
                'Focus on quality',
                'Incremental progress',
                'Clear documentation'
            ],
            'areas_of_discussion': [
                'Prioritization of features',
                'Resource allocation'
            ],
            'recommended_approach': 'Proceed with phased implementation',
            'consensus_level': 'high'
        }

        return {
            'success': True,
            'synthesis': synthesis
        }

    def _extract_action_items(
        self,
        discussion_summary: str
    ) -> Dict[str, Any]:
        """Extract action items from a discussion."""
        logger.info("Extracting action items from discussion")

        action_items = [
            {
                'item': 'Complete current phase implementation',
                'owner': 'CTOAgent',
                'priority': 'high',
                'status': 'pending'
            },
            {
                'item': 'Update project roadmap',
                'owner': 'COOAgent',
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'item': 'Review creative direction',
                'owner': 'CreativeDirectorAgent',
                'priority': 'medium',
                'status': 'pending'
            }
        ]

        return {
            'success': True,
            'action_items': action_items,
            'total_items': len(action_items)
        }

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for meeting coordination."""
        return bool(task and task.strip())
