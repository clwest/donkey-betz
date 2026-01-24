"""
Lazy Context Loader Service
Session 806: On-demand context loading based on query classification.

This service:
1. Maps query types to required context sections
2. Only loads sections that are actually needed
3. Caches loaded sections for session reuse
4. Skips sections that aren't relevant to the query

The goal is to reduce from 16 context sections loaded per request
down to 2-5 sections based on query intent.
"""

import logging
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query types that determine context loading."""
    QUESTION = "question"           # User asking a question
    CREATION = "creation"           # User wants to create something
    CONVERSATION = "conversation"   # General chat/banter
    WORKFLOW = "workflow"           # Multi-step workflow request
    OPPORTUNITY = "opportunity"     # Business/revenue opportunity
    SYSTEM = "system"               # System status/management
    MEMORY = "memory"               # Memory-related queries
    ANALYSIS = "analysis"           # Analysis/research queries
    COLLABORATION = "collaboration" # Agent collaboration
    UNKNOWN = "unknown"             # Fallback


@dataclass
class ContextSection:
    """Represents a loadable context section."""
    name: str
    loader: Optional[Callable[[], str]] = None
    content: Optional[str] = None
    loaded_at: Optional[datetime] = None
    tokens: int = 0
    is_cached: bool = False
    ttl_seconds: int = 300  # Cache TTL


@dataclass
class SectionRequirements:
    """Defines which sections are required for a query type."""
    required: Set[str] = field(default_factory=set)
    optional: Set[str] = field(default_factory=set)
    skip: Set[str] = field(default_factory=set)


class LazyContextLoader:
    """
    Session 806: Loads context sections on-demand based on query classification.

    Usage:
        from core.services.lazy_context_loader import get_lazy_context_loader

        loader = get_lazy_context_loader()

        # Get sections needed for a query
        sections_to_load = loader.get_required_sections(
            query_type=QueryType.QUESTION,
            message="What are the current trends in AI?"
        )

        # Load only those sections
        for section_name in sections_to_load:
            content = loader.load_section(section_name)
    """

    # Section requirements by query type
    SECTION_REQUIREMENTS: Dict[QueryType, SectionRequirements] = {
        QueryType.QUESTION: SectionRequirements(
            required={'spider_intelligence', 'pending_decisions'},
            optional={'learning_patterns', 'advisor_context'},
            skip={'workspace_context', 'operator_mode', 'proactive_intelligence'}
        ),
        QueryType.CREATION: SectionRequirements(
            required={'project_context', 'learning_patterns', 'workspace_context'},
            optional={'spider_intelligence'},
            skip={'proactive_intelligence', 'operator_mode', 'advisor_context'}
        ),
        QueryType.CONVERSATION: SectionRequirements(
            required={'conversation_history'},
            optional={'pending_decisions'},
            skip={'spider_intelligence', 'learning_patterns', 'advisor_context',
                  'proactive_intelligence', 'workspace_context', 'operator_mode'}
        ),
        QueryType.WORKFLOW: SectionRequirements(
            required={'workspace_context', 'project_context', 'learning_patterns'},
            optional={'spider_intelligence'},
            skip={'proactive_intelligence', 'advisor_context', 'operator_mode'}
        ),
        QueryType.OPPORTUNITY: SectionRequirements(
            required={'spider_intelligence', 'proactive_intelligence', 'advisor_context'},
            optional={'pending_decisions'},
            skip={'workspace_context', 'learning_patterns', 'operator_mode'}
        ),
        QueryType.SYSTEM: SectionRequirements(
            required={'pending_decisions', 'proactive_intelligence'},
            optional={'workspace_context'},
            skip={'spider_intelligence', 'learning_patterns', 'advisor_context'}
        ),
        QueryType.MEMORY: SectionRequirements(
            required={'learning_patterns'},
            optional={'conversation_history'},
            skip={'spider_intelligence', 'advisor_context', 'proactive_intelligence',
                  'workspace_context', 'operator_mode'}
        ),
        QueryType.ANALYSIS: SectionRequirements(
            required={'spider_intelligence', 'advisor_context'},
            optional={'learning_patterns'},
            skip={'workspace_context', 'operator_mode', 'proactive_intelligence'}
        ),
        QueryType.COLLABORATION: SectionRequirements(
            required={'learning_patterns'},
            optional={'advisor_context', 'workspace_context'},
            skip={'spider_intelligence', 'proactive_intelligence', 'operator_mode'}
        ),
        QueryType.UNKNOWN: SectionRequirements(
            required=set(),
            optional={'spider_intelligence', 'pending_decisions'},
            skip=set()
        ),
    }

    # Keywords for boosting optional sections to required
    KEYWORD_BOOSTS: Dict[str, List[str]] = {
        'spider_intelligence': ['trending', 'news', 'market', 'latest', 'current',
                                 'today', 'recent', 'updates', 'happening'],
        'advisor_context': ['advice', 'strategy', 'should i', 'recommend', 'best',
                           'warren', 'buffett', 'expert', 'invest'],
        'learning_patterns': ['learned', 'pattern', 'improve', 'better', 'history',
                              'previous', 'last time', 'remember'],
        'workspace_context': ['project', 'code', 'file', 'workspace', 'repo',
                              'implementation', 'build', 'deploy'],
        'proactive_intelligence': ['opportunity', 'alert', 'action', 'pending',
                                   'waiting', 'attention', 'urgent'],
    }

    # Always-load sections (never skipped)
    ALWAYS_LOAD = {'system_prompt_core', 'user_message', 'user_profile'}

    # Feature flag
    ENABLE_LAZY_LOADING = True

    def __init__(self):
        self._section_cache: Dict[str, ContextSection] = {}
        self._loaders: Dict[str, Callable[[], str]] = {}
        self._stats = {
            'sections_loaded': 0,
            'sections_skipped': 0,
            'cache_hits': 0,
        }

    def register_loader(self, section_name: str, loader: Callable[[], str]) -> None:
        """
        Register a loader function for a section.

        Args:
            section_name: Name of the section
            loader: Function that returns the section content
        """
        self._loaders[section_name] = loader
        logger.debug(f"Registered loader for section: {section_name}")

    def get_required_sections(
        self,
        query_type: QueryType,
        message: str,
        force_sections: Optional[Set[str]] = None
    ) -> Set[str]:
        """
        Determine which sections should be loaded for a query.

        Args:
            query_type: The classified query type
            message: The user's message (for keyword boosting)
            force_sections: Sections to always include

        Returns:
            Set of section names to load
        """
        if not self.ENABLE_LAZY_LOADING:
            # Return all sections if lazy loading is disabled
            return set(self._loaders.keys()) | self.ALWAYS_LOAD

        # Start with required sections for this query type
        requirements = self.SECTION_REQUIREMENTS.get(
            query_type,
            self.SECTION_REQUIREMENTS[QueryType.UNKNOWN]
        )
        sections_to_load = set(requirements.required) | self.ALWAYS_LOAD

        # Add forced sections
        if force_sections:
            sections_to_load |= force_sections

        # Check keywords for boosting optional sections
        message_lower = message.lower()
        for section_name, keywords in self.KEYWORD_BOOSTS.items():
            if section_name in requirements.skip:
                continue  # Don't boost sections that are explicitly skipped

            if any(kw in message_lower for kw in keywords):
                if section_name in requirements.optional or section_name not in requirements.skip:
                    sections_to_load.add(section_name)
                    logger.debug(f"Keyword boost: '{section_name}' added based on message keywords")

        # Log what we're loading vs skipping
        skipped = requirements.skip - sections_to_load
        if skipped:
            logger.info(
                f"🔍 [Session 806] LazyLoader: Loading {len(sections_to_load)} sections, "
                f"skipping {len(skipped)} ({', '.join(skipped)})"
            )

        return sections_to_load

    def load_section(
        self,
        section_name: str,
        force_reload: bool = False
    ) -> Optional[str]:
        """
        Load a specific section, using cache if available.

        Args:
            section_name: Name of the section to load
            force_reload: Ignore cache and reload

        Returns:
            Section content or None if not available
        """
        # Check cache first
        if not force_reload and section_name in self._section_cache:
            cached = self._section_cache[section_name]
            if cached.loaded_at and cached.is_cached:
                age = (datetime.now() - cached.loaded_at).total_seconds()
                if age < cached.ttl_seconds:
                    self._stats['cache_hits'] += 1
                    logger.debug(f"Cache hit for section: {section_name}")
                    return cached.content

        # Load the section
        loader = self._loaders.get(section_name)
        if not loader:
            logger.debug(f"No loader registered for section: {section_name}")
            return None

        try:
            content = loader()
            if content:
                self._section_cache[section_name] = ContextSection(
                    name=section_name,
                    content=content,
                    loaded_at=datetime.now(),
                    is_cached=True,
                )
                self._stats['sections_loaded'] += 1
                return content
        except Exception as e:
            logger.warning(f"Failed to load section '{section_name}': {e}")
            return None

        return None

    def load_sections_for_query(
        self,
        query_type: QueryType,
        message: str,
        force_sections: Optional[Set[str]] = None
    ) -> Dict[str, str]:
        """
        Load all required sections for a query.

        Args:
            query_type: The classified query type
            message: The user's message
            force_sections: Additional sections to load

        Returns:
            Dict of section_name -> content
        """
        sections_to_load = self.get_required_sections(query_type, message, force_sections)
        loaded_sections: Dict[str, str] = {}

        for section_name in sections_to_load:
            content = self.load_section(section_name)
            if content:
                loaded_sections[section_name] = content

        # Track what was skipped
        all_sections = set(self._loaders.keys())
        skipped = all_sections - sections_to_load
        self._stats['sections_skipped'] += len(skipped)

        return loaded_sections

    def invalidate_cache(self, section_name: Optional[str] = None) -> None:
        """
        Invalidate cached sections.

        Args:
            section_name: Specific section to invalidate, or None for all
        """
        if section_name:
            if section_name in self._section_cache:
                del self._section_cache[section_name]
                logger.debug(f"Invalidated cache for section: {section_name}")
        else:
            self._section_cache.clear()
            logger.debug("Invalidated all section caches")

    def get_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        return {
            **self._stats,
            'cached_sections': len(self._section_cache),
            'registered_loaders': len(self._loaders),
        }

    def set_cache_ttl(self, section_name: str, ttl_seconds: int) -> None:
        """Set the cache TTL for a specific section."""
        if section_name in self._section_cache:
            self._section_cache[section_name].ttl_seconds = ttl_seconds

    @classmethod
    def classify_query_simple(cls, message: str) -> QueryType:
        """
        Simple keyword-based query classification (no LLM call).

        This is a fallback when the full QueryClassifier is not available.

        Args:
            message: The user's message

        Returns:
            QueryType based on keywords
        """
        message_lower = message.lower()

        # Creation keywords
        creation_kw = ['create', 'generate', 'make', 'design', 'draw', 'build',
                       'write', 'produce', 'compose', 'render']
        if any(kw in message_lower for kw in creation_kw):
            return QueryType.CREATION

        # Question keywords (ends with ?)
        if message.strip().endswith('?'):
            question_kw = ['what', 'how', 'why', 'when', 'where', 'who', 'which',
                          'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does']
            if any(message_lower.startswith(kw) or f' {kw} ' in message_lower
                   for kw in question_kw):
                return QueryType.QUESTION

        # Workflow keywords
        workflow_kw = ['workflow', 'pipeline', 'process', 'steps', 'automate',
                       'sequence', 'orchestrate']
        if any(kw in message_lower for kw in workflow_kw):
            return QueryType.WORKFLOW

        # Opportunity keywords
        opportunity_kw = ['opportunity', 'revenue', 'money', 'earn', 'profit',
                          'business', 'investment', 'trade']
        if any(kw in message_lower for kw in opportunity_kw):
            return QueryType.OPPORTUNITY

        # System keywords
        system_kw = ['status', 'health', 'system', 'agent', 'service',
                     'celery', 'queue', 'task']
        if any(kw in message_lower for kw in system_kw):
            return QueryType.SYSTEM

        # Analysis keywords
        analysis_kw = ['analyze', 'research', 'study', 'investigate', 'examine',
                       'explore', 'compare', 'evaluate']
        if any(kw in message_lower for kw in analysis_kw):
            return QueryType.ANALYSIS

        # Memory keywords
        memory_kw = ['remember', 'recall', 'history', 'past', 'previous',
                     'learned', 'memory']
        if any(kw in message_lower for kw in memory_kw):
            return QueryType.MEMORY

        # Collaboration keywords
        collaboration_kw = ['team', 'collaborate', 'together', 'consult',
                            'advisor', 'expert', 'help from']
        if any(kw in message_lower for kw in collaboration_kw):
            return QueryType.COLLABORATION

        # Short messages are usually conversation
        if len(message.split()) <= 3:
            return QueryType.CONVERSATION

        return QueryType.UNKNOWN

    @classmethod
    def set_lazy_loading(cls, enabled: bool) -> None:
        """Enable or disable lazy loading globally."""
        cls.ENABLE_LAZY_LOADING = enabled
        logger.info(f"🔍 [Session 806] Lazy loading {'enabled' if enabled else 'disabled'}")


# Singleton instance
_lazy_context_loader: Optional[LazyContextLoader] = None


def get_lazy_context_loader() -> LazyContextLoader:
    """Get the singleton LazyContextLoader instance."""
    global _lazy_context_loader
    if _lazy_context_loader is None:
        _lazy_context_loader = LazyContextLoader()
    return _lazy_context_loader
