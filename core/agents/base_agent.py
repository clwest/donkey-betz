"""
Base Agent Class for Clean Architecture
========================================

Session 268: Phase 1 - Foundation
Session 304: Added Learning Infrastructure Hooks

This is the abstract base class for all clean architecture agents.
Each agent inherits from this class and TimeTravelMixin for debugging.

Key Features:
1. Abstract execute() method that subclasses must implement
2. TimeTravelMixin integration for decision replay/debugging
3. Standard interfaces for sci-fi and spider context injection
4. Prompt building helpers that combine context sources
5. Learning hooks for memory, evolution, and knowledge sharing (Session 304)

Usage:
    class MyAgent(BaseAgent):
        name = "MyAgent"
        system_prompt = "You do X. That's all."
        tools = [...]

        def execute(self, task, context, scifi_context, spider_context):
            # Implementation
            # After execution, call learning hooks:
            # self._record_learning_outcome(result, task, context)
            pass
"""

import logging
import json
import time
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
        self._learning_loop = None
        self._memory_service = None
        self._agent_model = None  # Cached Agent model instance

    # ==================== Lazy-Loaded Services ====================

    @property
    def client(self) -> OpenAI:
        """Lazy-load OpenAI client."""
        if self._client is None:
            from django.conf import settings
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService for outcome recording and XP."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(self.user)
            except ImportError:
                logger.warning("LearningLoopService not available")
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService for memory creation."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.warning("MemoryEmbeddingService not available")
        return self._memory_service

    @property
    def agent_model(self):
        """Get or create the Agent model instance for this agent."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                self._agent_model, _ = Agent.objects.get_or_create(
                    name=self.name,
                    defaults={
                        'agent_type': 'clean_architecture',
                        'description': self.system_prompt[:500] if self.system_prompt else '',
                        'is_active': True
                    }
                )
            except Exception as e:
                logger.warning(f"Could not get/create Agent model: {e}")
        return self._agent_model

    # ==================== Abstract Methods ====================

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
        # Session 293: gpt-5-mini uses tokens for internal reasoning first
        # Need high token limit to ensure room for reasoning + visible output
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                max_completion_tokens=6000,  # High enough for reasoning + output
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

    # ==================== Learning Infrastructure (Session 304) ====================

    def _record_learning_outcome(
        self,
        result: 'AgentResult',
        task: str,
        context: Dict[str, Any],
        spider_data_used: bool = False,
        scifi_context_used: bool = False
    ) -> Optional[str]:
        """
        Record execution outcome for learning, XP, and pattern detection.

        This should be called at the end of execute() to:
        1. Record the outcome for the learning loop
        2. Award XP to the agent on success
        3. Detect patterns in successful/failed interactions

        Args:
            result: The AgentResult from execution
            task: The original task
            context: Execution context
            spider_data_used: Whether spider data was used
            scifi_context_used: Whether sci-fi features were used

        Returns:
            Outcome ID if recorded, None otherwise
        """
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type=self._detect_query_type(task),
                query_text=task,
                execution_mode='agent',
                agents_used=[self.name],
                response=result.message or '',
                execution_time_ms=result.execution_time_ms,
                success=result.success,
                classification_confidence=0.8,  # Default confidence
                spider_data_used=spider_data_used,
                scifi_context_used=scifi_context_used,
                metadata={
                    'tool_calls': result.tool_calls,
                    'decisions_made': result.decisions_made,
                    'context_keys': list(context.keys()) if context else [],
                }
            )
            logger.debug(f"Recorded learning outcome: {outcome_id}")
            return outcome_id

        except Exception as e:
            logger.warning(f"Failed to record learning outcome: {e}")
            return None

    def _detect_query_type(self, task: str) -> str:
        """Detect query type from task text for learning categorization."""
        task_lower = task.lower()
        if any(w in task_lower for w in ['create', 'generate', 'make', 'design']):
            return 'creation'
        elif any(w in task_lower for w in ['edit', 'modify', 'change', 'update']):
            return 'editing'
        elif any(w in task_lower for w in ['research', 'analyze', 'find', 'search']):
            return 'research'
        elif any(w in task_lower for w in ['what', 'how', 'why', 'when', 'who', '?']):
            return 'question'
        else:
            return 'other'

    def _create_execution_memory(
        self,
        result: 'AgentResult',
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ) -> Optional[Any]:
        """
        Create a memory from a meaningful interaction.

        Should be called for:
        - Successful executions (to remember what worked)
        - Failed executions (to remember what didn't work)
        - User preferences discovered during execution
        - Learned techniques or patterns

        Args:
            result: The AgentResult from execution
            task: The original task
            memory_type: success, failure, preference, technique, insight, interaction
            importance: 0-1 importance rating (default 0.5)

        Returns:
            Created AgentMemory instance or None
        """
        if not self.memory_service or not self.agent_model:
            return None

        try:
            # Determine memory type based on result
            if memory_type == "interaction":
                memory_type = "success" if result.success else "failure"

            # Build memory content
            title = f"{self.name}: {task[:50]}..." if len(task) > 50 else f"{self.name}: {task}"
            content = result.message or "No response message"

            # Add tool call details if available
            if result.tool_calls:
                tools_used = [tc.get('name', 'unknown') for tc in result.tool_calls]
                content += f"\n\nTools used: {', '.join(tools_used)}"

            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=title,
                content=content,
                memory_type=memory_type,
                context=f"Task: {task}",
                valence="positive" if result.success else "negative",
                importance_score=importance,
                source_type="agent_execution",
                source_id=result.agent_name,
                tags=[self.name, memory_type]
            )

            logger.debug(f"Created memory: {memory.title}")
            return memory

        except Exception as e:
            logger.warning(f"Failed to create execution memory: {e}")
            return None

    def _track_contribution(
        self,
        content_type: str,
        content_id: int,
        contribution_type: str = "primary_creator",
        contribution_score: float = 1.0
    ) -> Optional[Any]:
        """
        Track agent's contribution to created content.

        Should be called when the agent creates or modifies content.

        Args:
            content_type: Type of content (image, video, audio, research)
            content_id: ID of the content record
            contribution_type: primary_creator, assistant, reviewer, optimizer
            contribution_score: 0-1 contribution percentage

        Returns:
            Created AgentContribution instance or None
        """
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentContribution

            contribution = AgentContribution.objects.create(
                agent=self.agent_model,
                content_type=content_type,
                content_id=content_id,
                contribution_type=contribution_type,
                contribution_score=contribution_score
            )

            logger.debug(f"Tracked contribution: {self.name} -> {content_type}:{content_id}")
            return contribution

        except Exception as e:
            logger.warning(f"Failed to track contribution: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Any,
        confidence: float = 0.8
    ) -> Optional[Any]:
        """
        Share learned knowledge that other agents can access.

        Use this for patterns, preferences, or insights that would
        benefit other agents (cross-agent learning).

        Args:
            knowledge_type: Type of knowledge (trend, market, opportunity, competitor,
                           pricing, user_behavior, content_idea, tool_discovery)
            title: Title/key to identify this knowledge
            knowledge_value: The knowledge data (dict with details)
            confidence: 0-1 confidence in this knowledge

        Returns:
            Created AgentKnowledgeSource instance or None
        """
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            # Map generic types to model choices
            type_mapping = {
                'technique': 'tool_discovery',
                'insight': 'market',
                'pattern': 'user_behavior',
                'preference': 'user_behavior',
            }
            mapped_type = type_mapping.get(knowledge_type, knowledge_type)

            # Validate against model choices
            valid_types = ['trend', 'market', 'opportunity', 'competitor',
                          'pricing', 'user_behavior', 'content_idea', 'tool_discovery']
            if mapped_type not in valid_types:
                mapped_type = 'market'  # Default fallback

            # Build summary from knowledge_value
            if isinstance(knowledge_value, dict):
                summary = json.dumps(knowledge_value, indent=2)[:1000]
                key_insights = list(knowledge_value.values())[:5] if knowledge_value else []
            else:
                summary = str(knowledge_value)[:1000]
                key_insights = [str(knowledge_value)]

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title[:500],
                knowledge_type=mapped_type,
                defaults={
                    'summary': summary,
                    'key_insights': key_insights,
                    'confidence_score': confidence,
                    'data_points_count': 1,
                    'is_active': True
                }
            )

            if created:
                logger.info(f"Agent {self.name} shared new knowledge: {title}")
            else:
                logger.debug(f"Agent {self.name} updated knowledge: {title}")

            return knowledge

        except Exception as e:
            logger.warning(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge shared by other agents.

        Use this to learn from other agents' experiences.

        Args:
            knowledge_type: Filter by type (trend, market, opportunity, etc.)
            title_contains: Filter by title containing this text
            from_agents: Filter by source agents

        Returns:
            List of knowledge dicts
        """
        try:
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                # Map generic types
                type_mapping = {
                    'technique': 'tool_discovery',
                    'insight': 'market',
                    'pattern': 'user_behavior',
                    'preference': 'user_behavior',
                }
                mapped_type = type_mapping.get(knowledge_type, knowledge_type)
                queryset = queryset.filter(knowledge_type=mapped_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            # Exclude own knowledge to learn from others
            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            # Order by confidence and freshness
            queryset = queryset.order_by('-confidence_score', '-last_updated_at')

            results = []
            for ks in queryset[:20]:  # Limit to 20
                try:
                    insights = ks.key_insights if isinstance(ks.key_insights, list) else []
                except (TypeError, AttributeError):
                    insights = []

                results.append({
                    'source_agent': ks.agent.name,
                    'knowledge_type': ks.knowledge_type,
                    'title': ks.title,
                    'summary': ks.summary,
                    'key_insights': insights,
                    'confidence': ks.confidence_score,
                    'freshness': ks.freshness_score,
                })

            return results

        except Exception as e:
            logger.warning(f"Failed to get shared knowledge: {e}")
            return []

    def __repr__(self) -> str:
        return f"<{self.name}>"


# Import models at module level for F expression
try:
    from django.db import models
except ImportError:
    pass
