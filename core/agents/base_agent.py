"""
Base Agent Class for Clean Architecture
========================================

Session 268: Phase 1 - Foundation

This is the abstract base class for all clean architecture agents.
Each agent inherits from this class and TimeTravelMixin for debugging.

Key Features:
1. Abstract execute() method that subclasses must implement
2. TimeTravelMixin integration for decision replay/debugging
3. Standard interfaces for sci-fi and spider context injection
4. Prompt building helpers that combine context sources

Usage:
    class MyAgent(BaseAgent):
        name = "MyAgent"
        system_prompt = "You do X. That's all."
        tools = [...]

        def execute(self, task, context, scifi_context, spider_context):
            # Implementation
            pass
"""

import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from openai import OpenAI

from agents.time_travel_mixin import TimeTravelMixin

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Standard result object returned by all agents."""
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    agent_name: str = ""
    execution_time_ms: int = 0
    decisions_made: int = 0
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'agent_name': self.agent_name,
            'execution_time_ms': self.execution_time_ms,
            'decisions_made': self.decisions_made,
            'tool_calls': self.tool_calls,
        }


class BaseAgent(ABC, TimeTravelMixin):
    """
    Abstract base class for all clean architecture agents.

    Each agent is specialized for ONE domain and has access ONLY to its tools.
    This prevents the tool selection confusion that plagues the current system.

    Attributes:
        name: Agent's identifier (e.g., "ImageAgent")
        system_prompt: The system prompt that defines agent behavior
        tools: List of tool definitions this agent can use
        agent_name: Alias for name (used by TimeTravelMixin)

    Methods:
        execute(): Abstract method that performs the agent's task
        _build_prompt(): Builds prompt with sci-fi and spider context
        _call_openai(): Makes GPT API call with agent's tools
        _execute_tool_call(): Executes a tool call and returns result
    """

    # Class attributes to be overridden by subclasses
    name: str = "BaseAgent"
    system_prompt: str = ""
    tools: List[Dict[str, Any]] = []

    def __init__(self, user=None):
        """
        Initialize the agent.

        Args:
            user: Django User object for session tracking
        """
        self.user = user
        self.agent_name = self.name  # For TimeTravelMixin compatibility
        self._client = None

    @property
    def client(self) -> OpenAI:
        """Lazy-load OpenAI client."""
        if self._client is None:
            from django.conf import settings
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    @abstractmethod
    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute the agent's task.

        This is the main entry point for agent execution. Subclasses must
        implement this method to perform their specialized tasks.

        Args:
            task: The user's task/request in natural language
            context: Additional context (e.g., reference image IDs, count)
            scifi_context: Context from SciFiIntegrationService (mood, memory, evolution)
            spider_context: Context from SpiderIntelligenceService (trends, market data)

        Returns:
            AgentResult with success status, data, and metadata
        """
        pass

    def _build_prompt(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> str:
        """
        Build the complete prompt with all context sources.

        This combines:
        1. The agent's base system prompt
        2. Sci-fi context (mood, evolution, relationships, memories)
        3. Spider context (trends, market data)
        4. The actual task

        Args:
            task: The user's task
            scifi_context: Sci-fi system context
            spider_context: Spider intelligence context

        Returns:
            Complete prompt string
        """
        parts = [self.system_prompt]

        # Add mood modifier if available
        if scifi_context:
            mood = scifi_context.get('mood')
            if mood:
                mood_type = mood.get('mood_type', 'focused')
                style_mod = mood.get('style_modifier', 'balanced')
                parts.append(f"\n\n## Current Mood")
                parts.append(f"State: {mood_type}")
                parts.append(f"Style tendency: {style_mod}")

            # Add evolution context
            evolution = scifi_context.get('evolution')
            if evolution:
                level = evolution.get('level', 1)
                title = evolution.get('title', 'Apprentice')
                parts.append(f"\n\n## Experience Level")
                parts.append(f"Level {level} - {title}")

            # Add learned patterns from memory
            memory = scifi_context.get('memory')
            if memory:
                patterns = memory.get('learned_patterns', [])
                if patterns:
                    parts.append(f"\n\n## Learned from past interactions")
                    for pattern in patterns[:3]:
                        parts.append(f"- {pattern}")

            # Add recent dreams/insights
            dreams = scifi_context.get('dreams', [])
            if dreams:
                recent = dreams[0]
                content = recent.get('content', '')[:100]
                if content:
                    parts.append(f"\n\n## Recent creative thought")
                    parts.append(content)

        # Add spider context (trends, market data)
        if spider_context:
            trends = spider_context.get('relevant_trends', [])
            if trends:
                trend_names = [t.get('topic', '') for t in trends[:5] if t.get('topic')]
                if trend_names:
                    parts.append(f"\n\n## Current Trends")
                    parts.append(f"Trending topics: {', '.join(trend_names)}")

            # Add creative trends for image/design agents
            creative = spider_context.get('creative_trends', {})
            if creative:
                styles = creative.get('trending_styles', [])
                colors = creative.get('trending_colors', [])
                if styles:
                    style_names = [s.get('style', '') for s in styles[:3]]
                    parts.append(f"Trending styles: {', '.join(style_names)}")
                if colors:
                    color_names = [c.get('palette', '') for c in colors[:3]]
                    parts.append(f"Trending palettes: {', '.join(color_names)}")

        # Add the task
        parts.append(f"\n\n## Task")
        parts.append(task)

        return "\n".join(parts)

    def _call_openai(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a GPT API call with this agent's tools.

        Args:
            prompt: The complete prompt (system + context + task)
            conversation_history: Optional previous messages

        Returns:
            OpenAI response dict with message and tool_calls
        """
        messages = []

        # Add system message
        messages.append({
            "role": "system",
            "content": prompt
        })

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Make API call
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for best tool use
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=0.7,
                max_tokens=2000,
            )

            choice = response.choices[0]

            return {
                'content': choice.message.content,
                'tool_calls': [
                    {
                        'id': tc.id,
                        'name': tc.function.name,
                        'arguments': json.loads(tc.function.arguments)
                    }
                    for tc in (choice.message.tool_calls or [])
                ],
                'finish_reason': choice.finish_reason,
            }

        except Exception as e:
            logger.error(f"OpenAI API error in {self.name}: {e}")
            raise

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool call. Override in subclasses for tool-specific logic.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        raise NotImplementedError(
            f"Tool execution for '{tool_name}' not implemented in {self.name}"
        )

    def _validate_task(self, task: str) -> bool:
        """
        Validate the task is appropriate for this agent.

        Override in subclasses for domain-specific validation.

        Args:
            task: The task string

        Returns:
            True if valid, False otherwise
        """
        return bool(task and task.strip())

    def __repr__(self) -> str:
        return f"<{self.name}>"
