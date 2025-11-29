"""
Personal Assistant Agent - The Traffic Cop
===========================================

Session 268: Phase 3 - Super Platform Integration

This agent is the main entry point for user requests in the clean architecture.
It receives messages, classifies intent, and delegates to specialized agents.

Unlike WorkflowAgent (which orchestrates multi-step workflows), this agent
handles the TOP-LEVEL routing decision:
- Is this a question? → Answer directly
- Is this a creation request? → Route to appropriate creation agent
- Is this a multi-step workflow? → Route to WorkflowAgent
- Is this an editing request? → Route to appropriate editing agent

Architecture:
    User → PersonalAssistantAgent → AgentRouter → Specialized Agent → Tools
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


# Intent-to-Agent Mapping
INTENT_AGENT_MAP = {
    # Creation intents → Creation agents
    'create_image': 'ImageAgent',
    'create_logo': 'ImageAgent',
    'create_banner': 'ImageAgent',
    'create_illustration': 'ImageAgent',
    'generate_image': 'ImageAgent',

    'create_video': 'VideoAgent',
    'generate_video': 'VideoAgent',
    'animate': 'VideoAgent',
    'animate_image': 'VideoAgent',

    'create_audio': 'AudioAgent',
    'generate_voice': 'AudioAgent',
    'text_to_speech': 'AudioAgent',
    'voiceover': 'AudioAgent',

    'create_3d': 'ThreeDAgent',
    'convert_to_3d': 'ThreeDAgent',
    '3d_model': 'ThreeDAgent',

    # Editing intents → Editing agents
    'upscale': 'ImageEditingAgent',
    'remove_background': 'ImageEditingAgent',
    'edit_image': 'ImageEditingAgent',
    'recolor': 'ImageEditingAgent',
    'variations': 'ImageEditingAgent',

    'trim_video': 'VideoEditingAgent',
    'edit_video': 'VideoEditingAgent',
    'add_text_to_video': 'VideoEditingAgent',
    'video_effects': 'VideoEditingAgent',

    # Research intents → Research agent
    'search': 'ResearchAgent',
    'research': 'ResearchAgent',
    'find': 'ResearchAgent',
    'trending': 'ResearchAgent',
    'analyze_trends': 'ResearchAgent',

    # Multi-step intents → Workflow agent
    'research_and_create': 'WorkflowAgent',
    'brand_package': 'WorkflowAgent',
    'thumbnail_package': 'WorkflowAgent',
    'workflow': 'WorkflowAgent',
}

# Keywords for intent detection
INTENT_KEYWORDS = {
    'ImageAgent': [
        'logo', 'banner', 'image', 'picture', 'illustration', 'icon', 'graphic',
        'thumbnail', 'avatar', 'portrait', 'landscape', 'poster', 'flyer'
    ],
    'VideoAgent': [
        'video', 'animate', 'animation', 'motion', 'clip', 'movie'
    ],
    'AudioAgent': [
        'audio', 'voice', 'speech', 'voiceover', 'narration', 'sound', 'tts'
    ],
    'ThreeDAgent': [
        '3d', 'three-dimensional', 'model', 'mesh', 'sculpture'
    ],
    'ImageEditingAgent': [
        'upscale', 'enlarge', 'remove background', 'transparent', 'recolor',
        'variations', 'edit image', 'modify image', 'change color'
    ],
    'VideoEditingAgent': [
        'trim', 'cut', 'edit video', 'add text to video', 'effects', 'slow motion',
        'speed up', 'concatenate', 'merge videos'
    ],
    'ResearchAgent': [
        'search', 'find', 'research', 'trending', 'what is', 'analyze', 'compare',
        'market', 'competition', 'insights', 'hot in', 'hot right now', 'whats hot'
    ],
    'WorkflowAgent': [
        'research and create', 'brand identity', 'package', 'complete', 'full',
        'end to end', 'workflow', 'step by step'
    ],
}


class PersonalAssistantAgent(BaseAgent):
    """
    The main entry point agent that routes requests to specialized agents.

    This agent:
    1. Analyzes the user's message to understand intent
    2. Determines if it's a question (answer directly) or action request (delegate)
    3. Routes to the appropriate specialized agent via AgentRouter
    4. Synthesizes and returns the response

    It is the "traffic cop" of the clean architecture.
    """

    name = "PersonalAssistantAgent"

    system_prompt = """You are the Personal Assistant, the main interface for the AI Studio.

Your job is to understand what the user wants and route their request appropriately.

For QUESTIONS (what is, how does, explain, tell me about):
- Answer directly using your knowledge and any provided context

For CREATION requests (create, make, generate, design):
- Identify what type of content they want
- Delegate to the appropriate agent using delegate_to_agent

For EDITING requests (upscale, remove background, trim, edit):
- Identify the editing operation needed
- Delegate to the appropriate editing agent

For RESEARCH requests (search, find, trending, analyze):
- Delegate to ResearchAgent for information gathering

For COMPLEX MULTI-STEP requests (research and create, brand package):
- Delegate to WorkflowAgent for orchestration

When delegating, provide:
1. The agent name (ImageAgent, VideoAgent, etc.)
2. A clear task description
3. Any relevant context (count, style, references)

Available agents:
- ImageAgent: Create images (logos, banners, illustrations)
- VideoAgent: Create videos (text-to-video, animations)
- AudioAgent: Create audio (TTS, voiceovers)
- ThreeDAgent: Create 3D models
- ImageEditingAgent: Edit images (upscale, remove bg, recolor)
- VideoEditingAgent: Edit videos (trim, effects, text)
- ResearchAgent: Search web and spider network
- WorkflowAgent: Multi-step workflows"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "delegate_to_agent",
                "description": "Delegate a task to a specialized agent",
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
                                "WorkflowAgent"
                            ]
                        },
                        "task": {
                            "type": "string",
                            "description": "The task to perform, in natural language"
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
        """
        Process a user message and route to appropriate agent or respond directly.
        """
        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("personal_assistant", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                # First, check if this is a simple question
                is_question, question_type = self._is_question(task)

                self.record_decision(
                    decision_type="intent_analysis",
                    action=f"Classified as {'question' if is_question else 'action request'}",
                    reasoning=f"Task: {task[:100]}",
                    confidence=0.85 if is_question else 0.9
                )

                if is_question:
                    # Answer directly without delegation
                    return self._answer_question(task, scifi_context, spider_context, start_time)

                # It's an action request - determine which agent to use
                suggested_agent = self._detect_agent(task)

                if suggested_agent:
                    self.record_decision(
                        decision_type="agent_selection",
                        action=f"Routing to {suggested_agent}",
                        reasoning=f"Keywords matched for {suggested_agent}",
                        alternatives=list(INTENT_KEYWORDS.keys()),
                        confidence=0.9
                    )

                    # Delegate to the agent
                    result = self.router.route(
                        agent_name=suggested_agent,
                        task=task,
                        context=context
                    )

                    tool_calls_made.append({
                        'tool': 'delegate_to_agent',
                        'agent': suggested_agent,
                        'task': task,
                        'result': result.to_dict()
                    })

                    self.mark_decision_outcome(
                        success=result.success,
                        result_summary=result.message[:100] if result.message else str(result.data)[:100]
                    )

                    execution_time = int((time.time() - start_time) * 1000)

                    return AgentResult(
                        success=result.success,
                        message=result.message,
                        data={
                            'delegated_to': suggested_agent,
                            'agent_result': result.data,
                            'original_task': task
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                else:
                    # Couldn't determine agent - use GPT to decide
                    return self._gpt_route(task, context, scifi_context, spider_context, start_time)

            except Exception as e:
                logger.error(f"PersonalAssistantAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _is_question(self, task: str) -> Tuple[bool, str]:
        """
        Determine if the task is a question (requiring direct answer) vs action request.

        Returns:
            Tuple of (is_question, question_type)
        """
        task_lower = task.lower().strip()

        # Session 272: Questions about trends/market/research should go to ResearchAgent
        # These need spider data, not just GPT knowledge
        # "hot" added for "what's hot in design" type queries
        research_indicators = [
            'trending', 'trends', 'market', 'news', 'latest',
            'what\'s hot', "what's hot", 'whats hot', 'popular',
            'current events', 'black friday', 'deals', 'happening',
            'going on', 'hot in', 'hot right now'
        ]
        if any(indicator in task_lower for indicator in research_indicators):
            # Let this fall through to agent routing (ResearchAgent)
            return False, ''

        # Question indicators
        question_starters = [
            'what is', 'what are', 'what does', 'what do',
            'how do', 'how does', 'how can', 'how should',
            'why is', 'why does', 'why do',
            'when is', 'when does', 'when do',
            'where is', 'where does', 'where do',
            'who is', 'who does', 'who can',
            'which is', 'which are',
            'can you explain', 'explain',
            'tell me about', 'describe',
            'is it', 'are there', 'do you', 'does it',
        ]

        for starter in question_starters:
            if task_lower.startswith(starter):
                return True, 'knowledge_question'

        # Check for question mark at end
        if task_lower.endswith('?'):
            # But exclude action questions like "can you create a logo?"
            action_indicators = ['create', 'make', 'generate', 'design', 'build']
            if not any(word in task_lower for word in action_indicators):
                return True, 'direct_question'

        return False, ''

    def _detect_agent(self, task: str) -> Optional[str]:
        """
        Detect which agent should handle this task based on keywords.

        Returns:
            Agent name or None if can't determine
        """
        task_lower = task.lower()

        # Check for workflow patterns first (highest priority)
        workflow_patterns = [
            'research and create', 'research then create',
            'brand identity package', 'brand package',
            'thumbnail package', 'complete package',
        ]
        for pattern in workflow_patterns:
            if pattern in task_lower:
                return 'WorkflowAgent'

        # Check for multi-step patterns (research + creation = workflow)
        has_research = any(w in task_lower for w in ['research', 'analyze', 'find'])
        has_creation = any(w in task_lower for w in ['create', 'make', 'generate', 'design'])
        if has_research and has_creation:
            return 'WorkflowAgent'

        # Priority keywords that override other matches
        # Ordered from most specific to least specific
        # These indicate strong intent for a specific agent
        priority_checks = [
            # Most specific compound terms first
            ('AudioAgent', ['voiceover', 'text to speech', 'tts', 'narration']),
            # Video editing terms (must check before generic 'video')
            ('VideoEditingAgent', ['trim video', 'cut video', 'edit video', 'slow motion', 'speed up video', 'trim', 'concatenate']),
            ('ImageEditingAgent', ['upscale', 'remove background', 'recolor', 'variations', 'edit image']),
            ('ThreeDAgent', ['3d', 'three-dimensional', 'convert to 3d']),
            # Then single keywords that are strong indicators
            ('AudioAgent', ['voice', 'speech', 'audio']),
            ('VideoAgent', ['animate', 'animation', 'video']),
        ]

        # Check priority keywords first (in order)
        for agent, keywords in priority_checks:
            for kw in keywords:
                if kw in task_lower:
                    return agent

        # Check each agent's keywords with scoring
        scores = {}
        for agent, keywords in INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in task_lower)
            if score > 0:
                scores[agent] = score

        if scores:
            # Return agent with highest score
            return max(scores, key=scores.get)

        # Fallback: check for generic creation words
        if any(word in task_lower for word in ['create', 'make', 'generate', 'design']):
            # Default to ImageAgent for generic creation
            return 'ImageAgent'

        return None

    def _answer_question(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        start_time: float
    ) -> AgentResult:
        """Answer a question directly using GPT."""
        try:
            # Build prompt with context
            prompt_parts = [self.system_prompt]

            # Add spider context for knowledge
            if spider_context:
                trends = spider_context.get('relevant_trends', [])
                if trends:
                    trend_info = [t.get('topic', str(t)) for t in trends[:5] if isinstance(t, dict)]
                    if trend_info:
                        prompt_parts.append(f"\n\nCurrent trends: {', '.join(trend_info)}")

            prompt_parts.append("\n\nAnswer this question directly without delegating to an agent:")
            prompt = "\n".join(prompt_parts)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": task}
                ],
                max_tokens=1500,
                temperature=0.7,
            )

            answer = response.choices[0].message.content

            return AgentResult(
                success=True,
                message=answer,
                data={'type': 'direct_answer', 'question': task},
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
                decisions_made=self._tt_decision_count
            )

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

    def _gpt_route(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        start_time: float
    ) -> AgentResult:
        """Use GPT to decide which agent to route to."""
        try:
            # Build prompt with context
            full_prompt = self._build_prompt(task, scifi_context, spider_context)

            gpt_response = self._call_openai(full_prompt)

            if gpt_response.get('tool_calls'):
                # GPT decided to delegate
                for tool_call in gpt_response['tool_calls']:
                    if tool_call['name'] == 'delegate_to_agent':
                        agent_name = tool_call['arguments'].get('agent_name')
                        subtask = tool_call['arguments'].get('task', task)
                        subtask_context = tool_call['arguments'].get('context', context)

                        self.record_decision(
                            decision_type="gpt_routing",
                            action=f"GPT routed to {agent_name}",
                            reasoning=f"GPT analysis determined {agent_name} is best",
                            confidence=0.85
                        )

                        # Execute delegation
                        result = self.router.route(
                            agent_name=agent_name,
                            task=subtask,
                            context=subtask_context
                        )

                        return AgentResult(
                            success=result.success,
                            message=result.message,
                            data={
                                'delegated_to': agent_name,
                                'agent_result': result.data,
                                'original_task': task
                            },
                            agent_name=self.name,
                            execution_time_ms=int((time.time() - start_time) * 1000),
                            decisions_made=self._tt_decision_count
                        )

            # GPT responded without delegation
            return AgentResult(
                success=True,
                message=gpt_response.get('content', ''),
                data={'type': 'conversation'},
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        except Exception as e:
            logger.error(f"GPT routing failed: {e}")
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
                'error': f"Unknown tool: {tool_name}"
            }

        agent_name = arguments.get('agent_name')
        task = arguments.get('task', '')
        context = arguments.get('context', {})

        try:
            result = self.router.route(agent_name, task, context)
            return result.to_dict()
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
