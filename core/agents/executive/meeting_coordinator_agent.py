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
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

# Session 895: Timeout for sub-agent executions to prevent coordinator hangs
# Session 990: Reduced from 300s to 180s — 5 min was too generous and caused
# 30-min overall timeouts when 3+ agents each consumed the full timeout
SUB_AGENT_TIMEOUT = 180  # 3 minutes per agent perspective

logger = logging.getLogger(__name__)


def analyze_meeting_with_ml(meeting_data: dict) -> dict:
    """Analyze meeting discussions using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=meeting_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'meeting_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML meeting analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


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

    @staticmethod
    def _is_receipt_only_mode(context: Dict[str, Any] | None) -> bool:
        """URC v0.1 receipt_only mode detector.

        Recognized signals (Session 1211 Phase B adoption):
          - context['mode'] == 'receipt_only'  (primary, URC spec)
          - context.get('receipt_only') is True  (secondary, forward-compat)
        """
        if not context:
            return False
        if context.get('mode') == 'receipt_only':
            return True
        if context.get('receipt_only') is True:
            return True
        return False

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute meeting coordination based on the task."""
        start_time = time.time()

        # Session 1211 Phase B: URC v0.1 receipt_only capability ping.
        # Skip the coordination pipeline (calendar / meeting details
        # access + spider intelligence extraction below) when the caller
        # signals receipt_only mode. The Q1 predicate at
        # urc_envelope._is_skipped checks data['skipped'] is True.
        if self._is_receipt_only_mode(context):
            return AgentResult(
                success=True,
                message='receipt_only mode — no meeting coordination performed',
                data={
                    'skipped': True,
                    'status': 'skipped',
                    'mode': 'receipt_only',
                    'message': 'receipt_only mode — no meeting coordination performed',
                },
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
                decisions_made=0,
                tool_calls=[],
            )

        tool_calls_made = []

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

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

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
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

                    # Session 1200: Synthesize tool results into real analysis
                    tool_results = [tc.get('result', {}) for tc in tool_calls_made]
                    synthesis = self._synthesize_tool_results(tool_calls_made, tool_results, task)
                    analysis_msg = synthesis if synthesis else "Meeting coordination completed"

                    result = AgentResult(
                        success=True,
                        message=analysis_msg,
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                            'content': synthesis,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 1006: Persist output to Deliverable
                    self._save_to_deliverable(
                        title=f"Meeting Coordination: {task[:80]}",
                        content=analysis_msg,
                        deliverable_type='document',
                        category='Meeting Coordination',
                        tags=['meeting', 'executive'],
                        metadata={'task': task[:200]},
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

        return super()._execute_tool_call(tool_name, arguments)

    def _start_meeting(
        self,
        topic: str,
        participants: List[str],
        meeting_type: str
    ) -> Dict[str, Any]:
        """Start a meeting between agents - ACTUALLY calls each agent."""
        logger.info(f"Starting {meeting_type} meeting on: {topic}")

        # Session 990: Parallelize sub-agent calls to avoid sequential 5-min timeouts
        # Previously: sequential loop → N agents × 5 min = 15+ min
        # Now: parallel with max 3 workers → max(agent times) ≈ 3 min
        perspectives = []
        with ThreadPoolExecutor(max_workers=min(len(participants), 3)) as executor:
            futures = {
                executor.submit(
                    self._get_agent_perspective, participant, topic, meeting_type
                ): participant
                for participant in participants
            }
            for future in futures:
                perspectives.append(future.result())

        # Determine status based on whether we got real perspectives
        has_real_content = any(
            p.get('perspective') and
            not p['perspective'].startswith(f"{p['agent']}'s perspective on")
            for p in perspectives
        )

        meeting = {
            'topic': topic,
            'meeting_type': meeting_type,
            'participants': participants,
            'perspectives': perspectives,
            'status': 'completed' if has_real_content else 'failed',
            'notes': 'Meeting completed with real agent perspectives' if has_real_content else 'Failed to get agent perspectives'
        }

        return {
            'success': has_real_content,
            'meeting': meeting
        }

    def _get_agent_perspective(
        self,
        agent_name: str,
        topic: str,
        meeting_type: str
    ) -> Dict[str, Any]:
        """Get a real perspective from an agent by actually calling it."""
        try:
            from core.agent_router import AgentRouter

            router = AgentRouter(user=self.user)

            # Build a specific prompt for this agent's perspective
            perspective_task = f"""As a participant in a {meeting_type} meeting about "{topic}", provide your expert perspective.

Include:
1. Your key insights and analysis on this topic
2. Specific recommendations (with rationale)
3. Any concerns or risks you see
4. Suggested action items

Be concrete and specific - no placeholder text."""

            # Session 895: Add timeout protection to prevent coordinator hangs
            # S3048: thread the parent AgentExecution.id into the child
            # dispatch context so router._create_execution_record sets
            # parent_execution_id + root_execution_id on the child row.
            _child_context = {'meeting_topic': topic, 'meeting_type': meeting_type}
            _parent_exec_id = (getattr(self, '_execution_context', None) or {}).get('execution_id')
            if _parent_exec_id:
                _child_context['execution_id'] = _parent_exec_id

            def route_to_agent():
                return router.route(
                    agent_name=agent_name,
                    task=perspective_task,
                    context=_child_context,
                )

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(route_to_agent)
                result = future.result(timeout=SUB_AGENT_TIMEOUT)

            if result and result.success:
                # Parse the response to extract structured data
                content = result.message or result.data.get('content', '')
                return {
                    'agent': agent_name,
                    'perspective': content,
                    'recommendations': self._extract_recommendations(content),
                    'concerns': self._extract_concerns(content),
                    'raw_response': result.data
                }
            else:
                logger.warning(f"Agent {agent_name} failed to provide perspective: {result.error if result else 'No result'}")
                return {
                    'agent': agent_name,
                    'perspective': f"[Agent {agent_name} unavailable]",
                    'recommendations': [],
                    'concerns': ['Agent did not respond'],
                    'error': result.error if result else 'No response'
                }

        except FuturesTimeoutError:
            logger.warning(f"⏰ {agent_name} timed out after {SUB_AGENT_TIMEOUT}s")
            return {
                'agent': agent_name,
                'perspective': f"[{agent_name} timed out after {SUB_AGENT_TIMEOUT}s]",
                'recommendations': [],
                'concerns': ['Agent timed out'],
                'timeout': True
            }
        except Exception as e:
            logger.error(f"Error getting perspective from {agent_name}: {e}")
            return {
                'agent': agent_name,
                'perspective': f"[Error calling {agent_name}]",
                'recommendations': [],
                'concerns': [f'Error: {str(e)}'],
                'error': str(e)
            }

    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from agent response."""
        recommendations = []
        lines = content.split('\n')
        in_recommendations = False

        for line in lines:
            line_lower = line.lower().strip()
            if 'recommendation' in line_lower or 'suggest' in line_lower or 'action' in line_lower:
                in_recommendations = True
            if in_recommendations and line.strip().startswith(('-', '•', '*', '1', '2', '3')):
                recommendations.append(line.strip().lstrip('-•*0123456789. '))
            if len(recommendations) >= 5:
                break

        return recommendations[:5] if recommendations else ['See full perspective for recommendations']

    def _extract_concerns(self, content: str) -> List[str]:
        """Extract concerns/risks from agent response."""
        concerns = []
        lines = content.split('\n')
        in_concerns = False

        for line in lines:
            line_lower = line.lower().strip()
            if 'concern' in line_lower or 'risk' in line_lower or 'challenge' in line_lower:
                in_concerns = True
            if in_concerns and line.strip().startswith(('-', '•', '*', '1', '2', '3')):
                concerns.append(line.strip().lstrip('-•*0123456789. '))
            if len(concerns) >= 5:
                break

        return concerns[:5] if concerns else []

    def _synthesize_discussion(
        self,
        perspectives: List[Dict[str, Any]],
        topic: str
    ) -> Dict[str, Any]:
        """Synthesize perspectives from multiple agents using LLM."""
        logger.info(f"Synthesizing discussion on: {topic}")

        # Session 836: Use LLM to actually synthesize the perspectives
        try:
            # Build a prompt with all perspectives
            perspectives_text = "\n\n".join([
                f"**{p.get('agent', 'Unknown')}:**\n{p.get('perspective', 'No perspective provided')}"
                for p in perspectives
            ])

            synthesis_prompt = f"""Synthesize the following perspectives from a meeting about "{topic}":

{perspectives_text}

Provide a structured synthesis with:
1. Areas of Agreement (specific points all participants agree on)
2. Areas of Discussion/Debate (where there are different views)
3. Recommended Approach (synthesized recommendation)
4. Consensus Level (high/medium/low with explanation)

Be specific and concrete - reference actual points from the perspectives."""

            # Call OpenAI for synthesis
            response = self._call_openai(synthesis_prompt)
            content = response.get('content', '')

            synthesis = {
                'topic': topic,
                'perspectives_count': len(perspectives),
                'synthesis_text': content,
                'areas_of_agreement': self._extract_section(content, 'agreement'),
                'areas_of_discussion': self._extract_section(content, 'discussion'),
                'recommended_approach': self._extract_section(content, 'recommended', single=True),
                'consensus_level': self._determine_consensus(content)
            }

            return {
                'success': True,
                'synthesis': synthesis
            }

        except Exception as e:
            logger.error(f"Error synthesizing discussion: {e}")
            return {
                'success': False,
                'error': str(e),
                'synthesis': {'topic': topic, 'perspectives_count': len(perspectives)}
            }

    def _extract_section(self, content: str, section_type: str, single: bool = False) -> Any:
        """Extract a section from synthesized content."""
        items = []
        lines = content.split('\n')

        keywords = {
            'agreement': ['agree', 'consensus', 'alignment', 'common'],
            'discussion': ['debate', 'discuss', 'differ', 'tension', 'concern'],
            'recommended': ['recommend', 'approach', 'suggest', 'propose']
        }

        in_section = False
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords.get(section_type, [])):
                in_section = True
                continue
            if in_section:
                if line.strip().startswith(('-', '•', '*', '1', '2', '3')):
                    items.append(line.strip().lstrip('-•*0123456789. '))
                elif line.strip() and not line.startswith('#'):
                    items.append(line.strip())
                if len(items) >= 5:
                    break

        if single:
            return items[0] if items else 'See full synthesis'
        return items if items else ['See full synthesis for details']

    def _determine_consensus(self, content: str) -> str:
        """Determine consensus level from content."""
        content_lower = content.lower()
        if 'high consensus' in content_lower or 'strong agreement' in content_lower:
            return 'high'
        elif 'low consensus' in content_lower or 'significant disagreement' in content_lower:
            return 'low'
        return 'medium'

    def _extract_action_items(
        self,
        discussion_summary: str
    ) -> Dict[str, Any]:
        """Extract action items from a discussion using LLM."""
        logger.info("Extracting action items from discussion")

        # Session 836: Use LLM to extract real action items
        try:
            extraction_prompt = f"""From the following discussion summary, extract specific action items:

{discussion_summary}

For each action item, provide:
1. Item: Clear, specific action (not vague)
2. Owner: Who should do this (agent name or role)
3. Priority: high/medium/low
4. Due: Suggested timeframe

Format as a numbered list. Be specific - no placeholder text like "Complete current phase" or "Update project"."""

            response = self._call_openai(extraction_prompt)
            content = response.get('content', '')

            # Parse the response into structured action items
            action_items = self._parse_action_items(content)

            return {
                'success': True,
                'action_items': action_items,
                'total_items': len(action_items),
                'raw_extraction': content
            }

        except Exception as e:
            logger.error(f"Error extracting action items: {e}")
            return {
                'success': False,
                'error': str(e),
                'action_items': [],
                'total_items': 0
            }

    def _parse_action_items(self, content: str) -> List[Dict[str, Any]]:
        """Parse action items from LLM response."""
        import re
        action_items = []
        lines = content.split('\n')

        current_item = {}
        for line in lines:
            line = line.strip()
            if not line:
                if current_item.get('item'):
                    action_items.append(current_item)
                    current_item = {}
                continue

            # Check for numbered item
            if re.match(r'^\d+[\.\)]\s*', line):
                if current_item.get('item'):
                    action_items.append(current_item)
                item_text = re.sub(r'^\d+[\.\)]\s*', '', line)
                # Check for "Item:" prefix
                if item_text.lower().startswith('item:'):
                    item_text = item_text[5:].strip()
                current_item = {
                    'item': item_text,
                    'owner': 'Unassigned',
                    'priority': 'medium',
                    'status': 'pending'
                }
            elif 'owner:' in line.lower():
                owner = line.split(':', 1)[1].strip()
                current_item['owner'] = owner
            elif 'priority:' in line.lower():
                priority = line.split(':', 1)[1].strip().lower()
                if priority in ['high', 'medium', 'low']:
                    current_item['priority'] = priority
            elif 'due:' in line.lower() or 'timeframe:' in line.lower():
                due = line.split(':', 1)[1].strip()
                current_item['due'] = due

        # Don't forget last item
        if current_item.get('item'):
            action_items.append(current_item)

        return action_items[:10]  # Limit to 10 items

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for meeting coordination."""
        return bool(task and task.strip())
