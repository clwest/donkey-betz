"""
Base Agent Class for Clean Architecture
========================================

Session 268: Phase 1 - Foundation
Session 304: Added Learning Infrastructure Hooks
Session 334: Added Project Context Support - All agents can now work within projects
Session 354: Added Mythology Validation - All agents validate outputs for unrealistic claims

This is the abstract base class for all clean architecture agents.
Each agent inherits from this class and TimeTravelMixin for debugging.

Key Features:
1. Abstract execute() method that subclasses must implement
2. TimeTravelMixin integration for decision replay/debugging
3. Standard interfaces for sci-fi and spider context injection
4. Prompt building helpers that combine context sources
5. Learning hooks for memory, evolution, and knowledge sharing (Session 304)
6. Project context support - agents can enhance prompts with project info (Session 334)
7. Mythology validation - outputs checked for unrealistic claims (Session 354)

Usage:
    class MyAgent(BaseAgent):
        name = "MyAgent"
        system_prompt = "You do X. That's all."
        tools = [...]

        def execute(self, task, context, scifi_context, spider_context):
            # Get project context if project_id is in context
            project_id = context.get('project_id')
            project_context = self._get_project_context(project_id)
            task = self._enhance_task_with_project(task, project_context)

            # Implementation
            # After execution, call learning hooks:
            # self._record_learning_outcome(result, task, context)
            #
            # Validate output for mythology (called automatically via _validate_output):
            # validated_result = self._validate_output(result)
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
class KnowledgeAttribution:
    """
    Session 400: Tracks what knowledge influenced an agent's response.
    This enables transparency - users can see WHY the agent said what it said.
    """
    spider_sources: List[str] = field(default_factory=list)  # e.g., ['techcrunch', 'hackernews']
    knowledge_items: List[Dict[str, Any]] = field(default_factory=list)  # Relevant knowledge used
    confidence_score: float = 0.0  # Overall confidence in the response
    data_freshness_hours: float = 0.0  # How old is the data
    total_sources: int = 0  # Total number of sources consulted

    def to_dict(self) -> dict:
        return {
            'spider_sources': self.spider_sources,
            'knowledge_items': self.knowledge_items,
            'confidence_score': self.confidence_score,
            'data_freshness_hours': self.data_freshness_hours,
            'total_sources': self.total_sources,
        }


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
    # Session 400: Knowledge attribution for transparency
    knowledge_attribution: Optional[KnowledgeAttribution] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error': self.error,
            'agent_name': self.agent_name,
            'execution_time_ms': self.execution_time_ms,
            'decisions_made': self.decisions_made,
            'tool_calls': self.tool_calls,
        }
        # Session 400: Include knowledge attribution if present
        if self.knowledge_attribution:
            result['knowledge_attribution'] = self.knowledge_attribution.to_dict()
        return result


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
        self._mythology_enforcer = None  # Session 354: Mythology validation
        self._progress_service = None  # Session 489: Streaming progress

    # ==================== Lazy-Loaded Services ====================

    @property
    def client(self) -> OpenAI:
        """Lazy-load OpenAI client with timeout to prevent hanging requests."""
        if self._client is None:
            from django.conf import settings
            # Session 411: Add 120 second timeout to prevent indefinite hangs
            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=120.0  # 2 minute timeout for API calls
            )
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

    @property
    def mythology_enforcer(self):
        """
        Session 354: Lazy-load MythologyEnforcer for reality validation.

        Validates agent outputs to prevent unrealistic promises like:
        - Financial myths ($10k/day guaranteed)
        - Technical myths (100% accurate, never fails)
        - Time myths (instant results)
        - Dangerous myths (medical claims)
        """
        if self._mythology_enforcer is None:
            try:
                from ai_core.agents.mythology_validator import mythology_enforcer
                self._mythology_enforcer = mythology_enforcer
            except ImportError:
                logger.warning("MythologyEnforcer not available")
        return self._mythology_enforcer

    @property
    def progress_service(self):
        """
        Session 489: Lazy-load StreamingProgressService for real-time updates.

        Provides WebSocket-enabled progress tracking during agent execution.
        """
        if self._progress_service is None:
            try:
                from core.services.streaming_progress import get_streaming_progress_service
                self._progress_service = get_streaming_progress_service()
            except ImportError:
                logger.warning("StreamingProgressService not available")
        return self._progress_service

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

    # ==================== Progress Tracking (Session 489) ====================

    def _get_progress_type(self) -> str:
        """
        Session 489: Get the progress stage type for this agent.

        Returns:
            Progress type key (e.g., 'image_generation', 'research')
        """
        try:
            from core.services.streaming_progress import get_progress_type_for_agent
            return get_progress_type_for_agent(self.name)
        except ImportError:
            return 'default'

    def _create_progress_tracker(self, task_id: str, description: str = ''):
        """
        Session 489: Create a progress tracker for this agent's execution.

        Usage in execute():
            with self._create_progress_tracker(task_id, task) as tracker:
                tracker.advance()  # Move to next stage
                # ... do work ...
                tracker.update("Custom message", 75)
                # ... more work ...

        Args:
            task_id: Unique task identifier (e.g., UUID)
            description: Human-readable task description

        Returns:
            ProgressTracker context manager or None if service unavailable
        """
        if not self.progress_service:
            return _NullProgressTracker()

        try:
            from core.services.streaming_progress import ProgressTracker
            return ProgressTracker(
                task_id=task_id,
                agent_type=self._get_progress_type(),
                description=description,
                service=self.progress_service
            )
        except Exception as e:
            logger.warning(f"Failed to create progress tracker: {e}")
            return _NullProgressTracker()

    def _emit_progress(
        self,
        task_id: str,
        stage: str,
        message: str,
        percentage: int
    ) -> None:
        """
        Session 489: Emit a progress update for a task.

        This is a simpler alternative to the context manager for
        cases where you want manual control over progress updates.

        Args:
            task_id: Task identifier
            stage: Current stage name
            message: Human-readable message
            percentage: Progress percentage (0-100)
        """
        if self.progress_service:
            try:
                self.progress_service.emit_progress(task_id, stage, message, percentage)
            except Exception as e:
                logger.debug(f"Progress emit failed: {e}")


    def _get_fresh_spider_intelligence(self, categories: List[str] = None, hours: int = 24, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Session 400: Get fresh spider intelligence for the agent's domain.

        Retrieves recent spider data relevant to the agent's specialization.
        This complements _get_relevant_knowledge_for_task by providing
        real-time intelligence from the spider network.

        Args:
            categories: List of spider categories to query (tech, news, jobs, etc.)
                       If None, uses all categories
            hours: How far back to look for data
            limit: Maximum items to return

        Returns:
            List of spider intelligence dicts with title, content, source
        """
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone
            from datetime import timedelta

            cutoff = timezone.now() - timedelta(hours=hours)

            query = SpiderData.objects.filter(
                created_at__gte=cutoff
            ).exclude(
                embedding__isnull=True
            ).exclude(
                embedding=[]
            )

            if categories:
                query = query.filter(data_type__in=categories)

            # Order by recency and relevance
            query = query.order_by('-relevance_score', '-created_at')[:limit * 2]

            results = []
            for spider_data in query:
                raw_data = spider_data.raw_data or {}
                items = raw_data.get('items', [])

                # Extract useful content from items
                sample_titles = []
                for item in items[:3]:
                    title = item.get('title', '')
                    if title:
                        sample_titles.append(title[:80])

                if sample_titles:
                    results.append({
                        'source': spider_data.spider_name,
                        'category': spider_data.data_type,
                        'titles': sample_titles,
                        'item_count': len(items),
                        'relevance': spider_data.relevance_score or 50,
                        'timestamp': spider_data.created_at.isoformat() if spider_data.created_at else None,
                    })

                if len(results) >= limit:
                    break

            return results

        except Exception as e:
            logger.warning(f"Failed to get fresh spider intelligence: {e}")
            return []

    def _get_relevant_knowledge_for_task(self, task: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Session 400: Retrieve relevant learned knowledge for the current task.

        This queries AgentKnowledgeSource for knowledge that might help with
        the current task, including:
        - Knowledge from this agent's past executions
        - Knowledge shared by other agents
        - Spider-derived intelligence

        Uses a hybrid approach:
        1. First tries semantic search on spider data (embeddings)
        2. Falls back to keyword matching on AgentKnowledgeSource

        Args:
            task: The current task to find relevant knowledge for
            limit: Maximum knowledge items to retrieve

        Returns:
            List of relevant knowledge dicts with title, summary, source
        """
        results = []

        # Try semantic search on spider data first
        # Session 434: Was disabled due to slow on-the-fly embedding generation
        # Session 452: RE-ENABLED - Celery task now pre-generates embeddings (~20% coverage)
        # Embeddings are generated every 10 min by backfill_spider_embeddings task
        ENABLE_SEMANTIC_SEARCH = True  # Re-enabled with pre-generated embeddings

        if ENABLE_SEMANTIC_SEARCH:
            try:
                from core.services.spider_semantic_search import get_spider_semantic_search
                search = get_spider_semantic_search()
                # Session 468: Use pre-computed embeddings to avoid on-the-fly generation
                # This is MUCH faster than semantic_search() which generates embeddings
                # for every spider data entry on each call
                semantic_results = search.semantic_search_with_db_embeddings(task, limit=3)

                for sr in semantic_results:
                    results.append({
                        'source_agent': 'SpiderNetwork',
                        'title': sr.title[:60] if sr.title else 'Spider Intelligence',
                        # Session 483: SemanticSearchResult has 'description', not 'content'
                        'summary': sr.description[:200] if sr.description else '',
                        'knowledge_type': 'spider_data',
                        'confidence': sr.similarity,
                        'spider_sources': [sr.source] if sr.source else [],
                    })
            except Exception as e:
                logger.debug(f"Semantic search not available: {e}")

        # Also query AgentKnowledgeSource for learned knowledge
        try:
            from core.models_unified_system import AgentKnowledgeSource
            from django.db.models import Q

            # Extract keywords from task for matching
            task_lower = task.lower()
            keywords = [w for w in task_lower.split() if len(w) > 3][:5]

            # Build query - look for knowledge matching task keywords
            query = Q(is_active=True)

            # Add keyword filters
            keyword_q = Q()
            for keyword in keywords:
                keyword_q |= Q(title__icontains=keyword)
                keyword_q |= Q(summary__icontains=keyword)

            if keywords:
                query &= keyword_q

            # Query for relevant knowledge, prioritize by confidence and freshness
            remaining_limit = limit - len(results)
            if remaining_limit > 0:
                knowledge_items = AgentKnowledgeSource.objects.filter(query).order_by(
                    '-confidence_score',
                    '-freshness_score',
                    '-last_updated_at'
                )[:remaining_limit]

                for ks in knowledge_items:
                    results.append({
                        'source_agent': ks.agent.name if ks.agent else 'Unknown',
                        'title': ks.title[:60] if ks.title else '',
                        'summary': ks.summary[:300] if ks.summary else '',
                        'knowledge_type': ks.knowledge_type,
                        'confidence': ks.confidence_score,
                        'spider_sources': ks.source_spider_names or [],
                    })

        except Exception as e:
            logger.warning(f"Failed to retrieve agent knowledge: {e}")

        if results:
            logger.debug(f"Found {len(results)} relevant knowledge items for task")

        return results[:limit]

    def _build_knowledge_attribution(self, knowledge_items: List[Dict[str, Any]]) -> KnowledgeAttribution:
        """
        Session 400: Build a KnowledgeAttribution object from retrieved knowledge.

        This creates the transparency metadata that shows users what influenced
        the agent's response.

        Args:
            knowledge_items: List of knowledge dicts from _get_relevant_knowledge_for_task()

        Returns:
            KnowledgeAttribution object with sources, confidence, freshness
        """
        if not knowledge_items:
            return KnowledgeAttribution()

        # Collect all spider sources
        all_spider_sources = []
        for item in knowledge_items:
            sources = item.get('spider_sources', [])
            if sources:
                all_spider_sources.extend(sources)

        # Deduplicate and clean spider sources
        unique_sources = []
        for source in all_spider_sources:
            if source and source not in unique_sources:
                # Skip internal sources like 'dream_exploration', 'learned_from_X'
                if not source.startswith(('dream_', 'learned_from_')):
                    unique_sources.append(source)

        # Calculate average confidence
        confidences = [item.get('confidence', 0.5) for item in knowledge_items]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        # Estimate data freshness (simplified - would need timestamps for accuracy)
        # For now, use a heuristic based on knowledge type
        freshness_hours = 24.0  # Default assumption

        # Build simplified knowledge items for attribution display
        attribution_items = []
        for item in knowledge_items[:3]:  # Limit to top 3 for display
            attribution_items.append({
                'source': item.get('source_agent', 'Unknown'),
                'title': item.get('title', '')[:50],
                'type': item.get('knowledge_type', 'general'),
                'confidence': round(item.get('confidence', 0.5), 2),
            })

        return KnowledgeAttribution(
            spider_sources=unique_sources[:5],  # Top 5 sources
            knowledge_items=attribution_items,
            confidence_score=round(avg_confidence, 2),
            data_freshness_hours=freshness_hours,
            total_sources=len(unique_sources),
        )

    def _build_prompt_with_attribution(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> tuple:
        """
        Session 400: Build prompt AND return knowledge attribution.

        This is the preferred method for agents that want to surface
        what knowledge influenced their response.

        Args:
            task: The user's task
            scifi_context: Sci-fi system context
            spider_context: Spider intelligence context

        Returns:
            Tuple of (prompt_string, KnowledgeAttribution)
        """
        # Get relevant knowledge first (we need it for both prompt and attribution)
        relevant_knowledge = self._get_relevant_knowledge_for_task(task)

        # Build the attribution
        attribution = self._build_knowledge_attribution(relevant_knowledge)

        # Build the prompt (using the already-retrieved knowledge)
        parts = [self.system_prompt]

        # Add relevant learned knowledge to prompt
        if relevant_knowledge:
            parts.append(f"\n\n## Relevant Knowledge from Past Learning")
            parts.append("You have learned the following that may be relevant:")
            for idx, knowledge in enumerate(relevant_knowledge[:3], 1):
                source = knowledge.get('source_agent', 'Unknown')
                title = knowledge.get('title', '')[:60]
                summary = knowledge.get('summary', '')[:150]
                spider_sources = knowledge.get('spider_sources', [])

                parts.append(f"\n{idx}. [{source}] {title}")
                if summary:
                    parts.append(f"   {summary}")
                if spider_sources and spider_sources[0] not in ['learned_from_', 'dream_']:
                    sources_str = ', '.join(spider_sources[:3])
                    parts.append(f"   (from: {sources_str})")

        # Add mood modifier if available - Session 497: Now affects behavior
        if scifi_context:
            mood = scifi_context.get('mood')
            if mood:
                mood_type = mood.get('mood_type', 'focused')
                style_mod = mood.get('style_modifier', 'balanced')
                confidence_mod = mood.get('confidence_modifier', 1.0)

                parts.append(f"\n\n## Current Mood & Behavioral Guidance")
                parts.append(f"State: {mood_type}")
                parts.append(f"Style tendency: {style_mod}")

                # Session 497: Apply behavioral constraints based on confidence modifier
                if confidence_mod >= 1.3:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are highly confident. Make bold recommendations. Be decisive and assertive.")
                elif confidence_mod >= 1.1:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are confident. Provide clear recommendations with conviction.")
                elif confidence_mod <= 0.8:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are in a cautious state. Prefer safe, proven approaches.")
                elif confidence_mod <= 0.9:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are focused. Be direct and efficient.")

            # Add evolution context - Session 497: Authority now affects behavior
            evolution = scifi_context.get('evolution')
            if evolution:
                level = evolution.get('level', 1)
                title_evo = evolution.get('title', 'Apprentice')
                authority = evolution.get('authority_level', 'junior')

                parts.append(f"\n\n## Experience Level & Authority")
                parts.append(f"Level {level} - {title_evo} ({authority})")

                # Session 497: Apply authority-based behavioral guidance
                if authority == 'master' or level >= 31:
                    parts.append("**AUTHORITY DIRECTIVE:** Lead with authority. Be definitive in your assessments.")
                elif authority == 'expert' or level >= 16:
                    parts.append("**AUTHORITY DIRECTIVE:** Provide authoritative guidance with confidence.")
                elif authority == 'senior' or level >= 6:
                    parts.append("**AUTHORITY DIRECTIVE:** Provide balanced recommendations based on experience.")
                else:
                    parts.append("**AUTHORITY DIRECTIVE:** Be thorough. Consider multiple perspectives.")

        # Add spider context (trends, market data)
        if spider_context:
            trends = spider_context.get('relevant_trends', [])
            if trends:
                # Session 495: Handle both string lists (from SmartTrendingService) and dict lists (legacy)
                trend_names = []
                for t in trends[:5]:
                    if isinstance(t, str):
                        trend_names.append(t)
                    elif isinstance(t, dict) and t.get('topic'):
                        trend_names.append(t.get('topic'))
                if trend_names:
                    parts.append(f"\n\n## Current Trends")
                    parts.append(f"Trending topics: {', '.join(trend_names)}")

        # Add the task
        parts.append(f"\n\n## Task")
        parts.append(task)

        prompt = "\n".join(parts)
        return prompt, attribution

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
        2. Learned knowledge relevant to this task (Session 400)
        3. Sci-fi context (mood, evolution, relationships, memories)
        4. Spider context (trends, market data)
        5. The actual task

        Args:
            task: The user's task
            scifi_context: Sci-fi system context
            spider_context: Spider intelligence context

        Returns:
            Complete prompt string
        """
        parts = [self.system_prompt]

        # Session 400: Add relevant learned knowledge
        relevant_knowledge = self._get_relevant_knowledge_for_task(task)
        if relevant_knowledge:
            parts.append(f"\n\n## Relevant Knowledge from Past Learning")
            parts.append("You have learned the following that may be relevant:")
            for idx, knowledge in enumerate(relevant_knowledge[:3], 1):
                source = knowledge.get('source_agent', 'Unknown')
                title = knowledge.get('title', '')[:60]
                summary = knowledge.get('summary', '')[:150]
                spider_sources = knowledge.get('spider_sources', [])

                parts.append(f"\n{idx}. [{source}] {title}")
                if summary:
                    parts.append(f"   {summary}")
                if spider_sources and spider_sources[0] not in ['learned_from_', 'dream_']:
                    sources_str = ', '.join(spider_sources[:3])
                    parts.append(f"   (from: {sources_str})")

        # Session 412: Add canonical policies from Boardroom Decisions
        try:
            from core.services.policy_context import get_policy_context_service
            policy_service = get_policy_context_service()
            policy_context = policy_service.get_policies_for_agent(self.name, max_policies=3)
            if policy_context:
                parts.append(policy_context)
        except Exception as e:
            logger.debug(f"Could not get policy context for {self.name}: {e}")

        # Add mood modifier if available - Session 497: Now affects behavior
        if scifi_context:
            mood = scifi_context.get('mood')
            if mood:
                mood_type = mood.get('mood_type', 'focused')
                style_mod = mood.get('style_modifier', 'balanced')
                confidence_mod = mood.get('confidence_modifier', 1.0)
                description = mood.get('description', '')

                parts.append(f"\n\n## Current Mood & Behavioral Guidance")
                parts.append(f"State: {mood_type}")
                parts.append(f"Style tendency: {style_mod}")

                # Session 497: Apply behavioral constraints based on confidence modifier
                if confidence_mod >= 1.3:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are highly confident. Make bold recommendations. Be decisive and assertive in your responses. Don't hedge or qualify unnecessarily.")
                elif confidence_mod >= 1.1:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are confident. Provide clear recommendations with conviction. Balance assertiveness with appropriate caveats.")
                elif confidence_mod <= 0.8:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are in a cautious state. Prefer safe, proven approaches. Acknowledge uncertainty where it exists. Suggest alternatives.")
                elif confidence_mod <= 0.9:
                    parts.append("**BEHAVIORAL DIRECTIVE:** You are in a focused, efficient state. Be direct and avoid over-elaboration. Get to the point quickly.")

            # Add evolution context - Session 497: Authority now affects behavior
            evolution = scifi_context.get('evolution')
            if evolution:
                level = evolution.get('level', 1)
                title = evolution.get('title', 'Apprentice')
                authority = evolution.get('authority_level', 'junior')
                confidence_boost = evolution.get('confidence_boost', 1.0)

                parts.append(f"\n\n## Experience Level & Authority")
                parts.append(f"Level {level} - {title} ({authority})")

                # Session 497: Apply authority-based behavioral guidance
                if authority == 'master' or level >= 31:
                    parts.append("**AUTHORITY DIRECTIVE:** As a master-level agent, you have extensive experience. Lead with authority. Your recommendations carry significant weight. Be definitive in your assessments.")
                elif authority == 'expert' or level >= 16:
                    parts.append("**AUTHORITY DIRECTIVE:** As an expert-level agent, provide authoritative guidance. You can make strong recommendations based on your experience. Be confident but open to edge cases.")
                elif authority == 'senior' or level >= 6:
                    parts.append("**AUTHORITY DIRECTIVE:** As a senior-level agent, provide balanced recommendations. You have solid experience but remain open to learning.")
                else:
                    parts.append("**AUTHORITY DIRECTIVE:** As a developing agent, be thorough in your analysis. Consider multiple perspectives before making recommendations.")

            # Session 497: Add synergy-based collaboration guidance
            relationships = scifi_context.get('relationships')
            if relationships:
                allies = relationships.get('allies', [])
                team_synergy = relationships.get('team_synergy', 1.0)
                collab_bonus = relationships.get('collaboration_bonus', {})

                if allies:
                    parts.append(f"\n\n## Collaboration Synergies")
                    parts.append(f"Works well with: {', '.join(allies[:5])}")

                    # Session 497: Apply synergy-based behavioral guidance
                    if team_synergy >= 1.5:
                        parts.append("**SYNERGY DIRECTIVE:** You have strong team synergy. Actively build on and enhance collaborators' ideas. Seek integration opportunities. Your combined output should exceed individual contributions.")
                    elif team_synergy >= 1.2:
                        parts.append("**SYNERGY DIRECTIVE:** You have good team synergy. Coordinate with allies and complement their work. Look for synthesis opportunities.")
                    elif team_synergy < 1.0:
                        parts.append("**SYNERGY DIRECTIVE:** Team dynamics are neutral. Focus on your individual contribution. Be clear and explicit in handoffs.")

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
                # Session 495: Handle both string lists (from SmartTrendingService) and dict lists (legacy)
                trend_names = []
                for t in trends[:5]:
                    if isinstance(t, str):
                        trend_names.append(t)
                    elif isinstance(t, dict) and t.get('topic'):
                        trend_names.append(t.get('topic'))
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

        # Session 490: Add relevant memories from semantic memory service
        try:
            if self.memory_service and self.agent_model:
                memory_context = self.memory_service.get_memory_context(
                    agent=self.agent_model,
                    query=task,
                    max_memories=3,
                    max_chars=800
                )
                if memory_context:
                    parts.append(f"\n\n## Relevant Memories")
                    parts.append(memory_context)
                    logger.debug(f"🧠 [Session 490] Injected {len(memory_context)} chars of memory context")
        except Exception as e:
            logger.debug(f"Memory context injection failed (non-fatal): {e}")

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

        except TimeoutError as e:
            # Session 411: Handle timeout specifically
            logger.error(f"OpenAI API timeout in {self.name} after 120s: {e}")
            raise TimeoutError(f"OpenAI API request timed out after 120 seconds in {self.name}")
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

    # ==================== Mythology Validation (Session 354) ====================

    def _validate_output(self, result: 'AgentResult') -> 'AgentResult':
        """
        Session 354: Validate agent output for unrealistic claims.

        Checks the result message and data for mythology patterns like:
        - Financial myths ($10k/day, guaranteed income)
        - Technical myths (100% accurate, never fails)
        - Time myths (instant results, learn in hours)
        - Dangerous myths (medical claims, legal advice)

        If violations are found, the output is corrected and flagged.

        Args:
            result: The AgentResult to validate

        Returns:
            Validated (and possibly corrected) AgentResult
        """
        if not self.mythology_enforcer:
            return result

        try:
            # Validate the message
            if result.message:
                validated = self.mythology_enforcer.enforce(self.name, result.message)

                if validated.get('mythology_corrected'):
                    logger.warning(
                        f"🚨 Mythology corrected in {self.name}: "
                        f"{validated.get('violations', 0)} violations"
                    )
                    result.message = validated.get('result', result.message)
                    result.data['mythology_corrected'] = True
                    result.data['mythology_violations'] = validated.get('violations', 0)
                    result.data['mythology_warning'] = validated.get('warning', '')

                    # Session 461: Publish hallucination event for real-time dashboard
                    try:
                        from intelligence.hallucination_publisher import HallucinationPublisher
                        publisher = HallucinationPublisher()
                        violations = validated.get('violations', [])
                        patterns = [v.get('type', 'unknown') for v in violations] if isinstance(violations, list) else []
                        risk_score = len(patterns) * 0.2  # Rough estimate
                        severity = 'critical' if risk_score > 0.6 else 'high' if risk_score > 0.4 else 'medium'
                        publisher.publish_hallucination_blocked(
                            agent_name=self.name,
                            original_text=str(result.message)[:500],
                            patterns=patterns,
                            risk_score=min(risk_score, 1.0),
                            corrected_text=validated.get('result', '')[:500] if validated.get('result') else None,
                            severity=severity
                        )
                    except Exception as pub_error:
                        logger.debug(f"HallucinationPublisher not available: {pub_error}")

            # Also validate any text in data
            if result.data:
                self._validate_data_dict(result.data)

            return result

        except Exception as e:
            logger.warning(f"Mythology validation failed: {e}")
            return result

    def _validate_data_dict(self, data: Dict[str, Any]) -> None:
        """
        Session 354: Recursively validate data dict for mythology.

        Modifies the data dict in place if violations are found.
        """
        if not self.mythology_enforcer:
            return

        for key, value in data.items():
            if isinstance(value, str) and len(value) > 20:
                validated = self.mythology_enforcer.enforce(self.name, value)
                if validated.get('mythology_corrected'):
                    data[key] = validated.get('result', value)
            elif isinstance(value, dict):
                self._validate_data_dict(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, str) and len(item) > 20:
                        validated = self.mythology_enforcer.enforce(self.name, item)
                        if validated.get('mythology_corrected'):
                            value[i] = validated.get('result', item)
                    elif isinstance(item, dict):
                        self._validate_data_dict(item)

    def _guard_prompt(self, prompt: str) -> str:
        """
        Session 354: Guard prompt before sending to LLM.

        Injects anti-mythology instructions to prevent the LLM from
        generating unrealistic claims in the first place.

        Args:
            prompt: The prompt to guard

        Returns:
            Guarded prompt with anti-mythology instructions
        """
        anti_mythology_instructions = """

## Reality Constraints (IMPORTANT)
When generating responses, you MUST avoid:
- Unrealistic financial promises (no "$X per day guaranteed", "risk-free income")
- Impossible technical claims (no "100% accurate", "never fails", "unlimited")
- Exaggerated time claims (no "instant results", "learn in hours")
- Medical/legal claims without qualifications
- Guarantees of specific outcomes

Always be realistic and honest about capabilities, timelines, and potential results.
Use phrases like "potential", "may help", "typically", "can vary" instead of absolutes.
"""
        # Insert before the task section
        if "## Task" in prompt:
            prompt = prompt.replace("## Task", f"{anti_mythology_instructions}\n## Task")
        else:
            prompt = prompt + anti_mythology_instructions

        return prompt

    def _build_prompt_with_mythology_guard(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> str:
        """
        Session 354: Build prompt with mythology guard included.

        Combines base prompt building with anti-mythology instructions.
        Use this instead of _build_prompt for full protection.

        Args:
            task: The user's task
            scifi_context: Sci-fi system context
            spider_context: Spider intelligence context

        Returns:
            Complete prompt string with mythology guard
        """
        base_prompt = self._build_prompt(task, scifi_context, spider_context)
        return self._guard_prompt(base_prompt)

    # ==================== Project Context Support (Session 334) ====================

    def _get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Session 334: Fetch project context when project_id is provided.

        This enables all agents to work within projects by understanding
        the project's name, description, and type. When users say
        "create a logo for this project", the agent automatically knows
        what the project is about.

        Args:
            project_id: UUID of the PartnershipProject

        Returns:
            Dict with project context (name, description, type, id) or empty dict
        """
        if not project_id:
            return {}

        try:
            from core.models_partnership import PartnershipProject
            project = PartnershipProject.objects.get(id=project_id)

            context = {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'project_description': project.description or '',
                'project_type': project.project_type or 'general',
            }

            # Include brand context if available
            if hasattr(project, 'brand_colors') and project.brand_colors:
                context['brand_colors'] = project.brand_colors
            if hasattr(project, 'brand_style') and project.brand_style:
                context['brand_style'] = project.brand_style

            logger.debug(f"Fetched project context for {project.project_name}")
            return context

        except Exception as e:
            logger.warning(f"Failed to fetch project context for {project_id}: {e}")
            return {}

    def _enhance_task_with_project(self, task: str, project_context: Dict[str, Any]) -> str:
        """
        Session 334: Enhance the task with project context.

        If user says "create a logo" and we have project context,
        enhance it to "create a logo for [project name]: [description]"

        This allows all agents to understand what they're creating for.

        Args:
            task: Original task
            project_context: Dict from _get_project_context()

        Returns:
            Enhanced task with project context
        """
        if not project_context:
            return task

        project_name = project_context.get('project_name', '')
        project_description = project_context.get('project_description', '')

        # Check if task is vague (doesn't specify what to create for)
        # Look for common creative action words without specific context
        creative_keywords = [
            'create', 'generate', 'make', 'design', 'build',
            'logo', 'image', 'banner', 'thumbnail', 'video', 'brand'
        ]
        has_creative_intent = any(kw in task.lower() for kw in creative_keywords)
        is_short_task = len(task.split()) < 15  # Short tasks likely need context

        # Only enhance if task seems to need project context
        if has_creative_intent and is_short_task and project_name:
            enhanced = f"{task} for '{project_name}'"
            if project_description and len(project_description) < 200:
                enhanced += f" - {project_description}"
            logger.info(f"Enhanced task with project context: {enhanced[:100]}...")
            return enhanced

        return task

    def _build_prompt_with_project(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        project_context: Dict[str, Any]
    ) -> str:
        """
        Session 334: Build prompt with project context included.

        Extends _build_prompt to add project-specific context like
        brand colors, style preferences, and project description.

        Args:
            task: The user's task
            scifi_context: Sci-fi system context
            spider_context: Spider intelligence context
            project_context: Project context from _get_project_context()

        Returns:
            Complete prompt string with project context
        """
        # Start with base prompt
        prompt = self._build_prompt(task, scifi_context, spider_context)

        # Add project context if available
        if project_context:
            project_section = "\n\n## Project Context"
            project_section += f"\nProject: {project_context.get('project_name', 'Unknown')}"

            if project_context.get('project_description'):
                desc = project_context['project_description'][:500]
                project_section += f"\nDescription: {desc}"

            if project_context.get('project_type'):
                project_section += f"\nType: {project_context['project_type']}"

            if project_context.get('brand_colors'):
                project_section += f"\nBrand Colors: {project_context['brand_colors']}"

            if project_context.get('brand_style'):
                project_section += f"\nBrand Style: {project_context['brand_style']}"

            # Insert project section before the task
            # Find the ## Task section and insert before it
            task_marker = "\n\n## Task"
            if task_marker in prompt:
                prompt = prompt.replace(task_marker, f"{project_section}{task_marker}")
            else:
                prompt += project_section

        return prompt

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


class _NullProgressTracker:
    """
    Session 489: Null object pattern for when progress service is unavailable.

    Allows agents to use progress tracking code without checking for None.
    This is returned by BaseAgent._create_progress_tracker() when the
    StreamingProgressService is not available.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def advance(self, custom_message: str = None) -> None:
        """No-op advance to next stage."""
        pass

    def update(self, message: str, percentage: int) -> None:
        """No-op progress update."""
        pass


# Import models at module level for F expression
try:
    from django.db import models
except ImportError:
    pass
