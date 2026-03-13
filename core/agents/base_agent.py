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
from enum import Enum
from openai import OpenAI


class OutputCategory(Enum):
    """
    Session 857: Standard output categories for agent results.

    Used for UI routing, filtering, and harmonization.
    """
    CONTENT = "content"      # Blog, article, newsletter, scripts
    RESEARCH = "research"    # Analysis, findings, intelligence
    CREATION = "creation"    # Image, video, audio, 3D assets
    CODE = "code"            # Generated code, scripts, configs
    ANALYSIS = "analysis"    # Trends, scores, reports, audits
    DECISION = "decision"    # Recommendations, choices, strategies
    GENERAL = "general"      # Default for unclassified outputs


class QualityTier(Enum):
    """
    Session 857: Quality tiers for content readiness.

    - BRONZE: Needs significant review/editing
    - SILVER: Publishable with minor edits
    - GOLD: Ready to publish as-is
    """
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"

# Session 727: Migrated TimeTravelMixin to core/agents
from core.agents.time_travel_mixin import TimeTravelMixin

logger = logging.getLogger(__name__)

# Session 988: Shared web_search tool definition — importable by any agent
WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for current information, news, and market data. Use when local data is unavailable or stale.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'AAPL SEC 8-K filing 2026', 'CoreWeave class action lawsuit')"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["search", "news"],
                    "default": "search",
                    "description": "Type of search: 'search' for general, 'news' for recent news"
                }
            },
            "required": ["query"]
        }
    }
}

# Session 1002B: Cache for dynamic AVAILABLE_SPECIALISTS (refreshes every 5 min)
_AVAILABLE_SPECIALISTS_CACHE = None
_AVAILABLE_SPECIALISTS_CACHE_TIME = 0

# Session 1002B: Shared spider_query tool definition — any agent can include this
SPIDER_QUERY_TOOL = {
    "type": "function",
    "function": {
        "name": "spider_query",
        "description": "Query the spider network for trending data, discussions, and real-time intelligence from 77 data spiders. Use when you need current trends, community discussions, or market data.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for spider data"
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Categories: tech, financial, news, social, creative, legal, sports, crypto, jobs, entertainment, science, health. Empty for all."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results (default 20)",
                    "default": 20
                }
            },
            "required": ["query"]
        }
    }
}


# Session 1018: JSON markers that indicate the LLM simulated tool calls as text
# instead of using the proper tool_calls API
_SIMULATED_TOOL_MARKERS = ['{"query":', '{"success":', '{"url":', '{"method":']


def strip_simulated_tool_json(analysis: str) -> str:
    """
    Session 1018: Strip simulated JSON tool calls from LLM text output.

    Some models (especially reasoning models) simulate tool calls as text
    instead of using the API's tool_calls mechanism. This produces output
    with raw JSON interspersed in the narrative. Detect and strip it.
    """
    if not analysis:
        return analysis

    # Check if analysis contains simulated tool markers
    marker_count = sum(1 for m in _SIMULATED_TOOL_MARKERS if m in analysis)
    if marker_count < 2:
        return analysis  # Not enough markers to indicate simulation

    # Strip lines that are pure JSON objects
    cleaned_lines = []
    in_json = False
    brace_depth = 0

    for line in analysis.split('\n'):
        stripped = line.strip()
        if not stripped:
            if not in_json:
                cleaned_lines.append(line)
            continue

        # Detect start of a simulated JSON tool block
        if stripped.startswith('{') and any(m.lstrip('{') in stripped for m in _SIMULATED_TOOL_MARKERS):
            brace_depth = stripped.count('{') - stripped.count('}')
            in_json = brace_depth > 0  # Multi-line JSON continues; single-line ends here
            continue

        if in_json:
            brace_depth += stripped.count('{') - stripped.count('}')
            if brace_depth <= 0:
                in_json = False
            continue

        cleaned_lines.append(line)

    result = '\n'.join(cleaned_lines).strip()
    # Collapse multiple blank lines
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')

    return result if result else analysis


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
    # Session 735: Cost and token tracking for orchestration
    tokens_used: int = 0
    cost: float = 0.0
    # Session 765: Link to AgentExecution record for intelligence data
    execution_id: Optional[str] = None
    # Session 857: Quality and truncation tracking
    quality_tier: str = "bronze"  # bronze/silver/gold - content readiness level
    output_category: str = "general"  # content/research/creation/code/analysis/decision
    truncated: bool = False  # True if output was cut off due to token limits
    confidence: float = 0.0  # Overall confidence in the output (0.0-1.0)

    # Session 840: Backwards compatibility alias for .content
    @property
    def content(self) -> str:
        """Alias for message - backwards compatibility with code expecting .content."""
        return self.message

    # Session 1017: Backwards compatibility alias for .metadata
    @property
    def metadata(self) -> Dict[str, Any]:
        """Alias for data - backwards compatibility with code expecting .metadata."""
        return self.data

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
            # Session 735: Include cost tracking
            'tokens_used': self.tokens_used,
            'cost': self.cost,
            # Session 765: Include execution ID for intelligence lookup
            'execution_id': self.execution_id,
            # Session 857: Quality and truncation tracking
            'quality_tier': self.quality_tier,
            'output_category': self.output_category,
            'truncated': self.truncated,
            'confidence': self.confidence,
        }
        # Session 400: Include knowledge attribution if present
        if self.knowledge_attribution:
            result['knowledge_attribution'] = self.knowledge_attribution.to_dict()
        return result


@dataclass
class ActionableOutputConfig:
    """
    Session 763: Configuration for when an agent output creates a Mission Control attention item.

    When enabled, successful agent executions will create HumanAttentionItems
    that appear on the Human Page with action buttons.

    Example:
        actionable_config = ActionableOutputConfig(
            enabled=True,
            item_type='insight',
            default_urgency='medium',
            actions=[
                {'id': 'review', 'label': 'Review Analysis', 'primary': True},
                {'id': 'set_alert', 'label': 'Set Alert'},
                {'id': 'ignore', 'label': 'Ignore'},
            ],
            payload_fields=['ticker', 'analysis_type', 'findings', 'recommendations']
        )
    """
    enabled: bool = False
    item_type: str = 'review'  # review, alert, opportunity, insight, approval
    urgency_from_field: str = None  # Field in result.data that determines urgency
    default_urgency: str = 'medium'  # critical, high, medium, low
    required_fields: List[str] = field(default_factory=list)  # Fields that must be in result.data
    min_confidence: float = 0.0  # Minimum confidence to create item
    actions: List[Dict[str, Any]] = field(default_factory=list)  # Available action buttons
    payload_fields: List[str] = field(default_factory=list)  # Fields to include in attention item payload
    max_items_per_hour: int = 5  # Rate limiting


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
    can_delegate: bool = True  # Session 744: Enable autonomous delegation to specialists
    requires_system_context: bool = False  # Session 820: Inject CLAUDE.md + critical docs for system-aware agents

    # Session 874: Prompt sharpening - transforms hedging language into decisive language
    enable_prompt_sharpening: bool = True  # Enable decisive language transformation
    sharpening_type: str = 'debate'  # 'debate', 'synthesis', or 'analysis'

    # Session 970: Auto-wrap _execute_tool_call in subclasses with recording
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '_execute_tool_call' in cls.__dict__:
            original = cls.__dict__['_execute_tool_call']
            def _wrapped_execute_tool_call(self, tool_name, arguments, *args, _orig=original, **kwargs):
                import time as _time
                _start = _time.time()
                _success = True
                _result = None
                _err_msg = ''
                _err_type = ''
                try:
                    _result = _orig(self, tool_name, arguments, *args, **kwargs)
                    return _result
                except Exception as _e:
                    _success = False
                    _err_msg = str(_e)
                    _err_type = type(_e).__name__
                    _result = {'error': _err_msg, 'error_type': _err_type}
                    raise
                finally:
                    try:
                        _latency = int((_time.time() - _start) * 1000)
                        self._record_tool_call(
                            tool_name=tool_name,
                            arguments=arguments,
                            result=_result,
                            latency_ms=_latency,
                            success=_success,
                            error_message=_err_msg,
                            error_type=_err_type,
                        )
                    except Exception:
                        pass  # Never let recording break agent execution
            _wrapped_execute_tool_call.__name__ = '_execute_tool_call'
            _wrapped_execute_tool_call.__doc__ = original.__doc__
            cls._execute_tool_call = _wrapped_execute_tool_call

    def __init__(self, user=None, health_check_mode: bool = False):
        """
        Initialize the agent.

        Args:
            user: Django User object for session tracking
            health_check_mode: Session 768 - If True, skip learning/memory creation.
                               Use for connectivity tests, agent health checks.
        """
        self.user = user
        self.agent_name = self.name  # For TimeTravelMixin compatibility
        self._client = None
        self._learning_loop = None
        self._memory_service = None
        self._agent_model = None  # Cached Agent model instance
        self._mythology_enforcer = None  # Session 354: Mythology validation
        self._progress_service = None  # Session 489: Streaming progress
        self._llm_router = None  # Session 697: Multi-model routing
        # Session 735: Cost tracking for orchestration
        self._accumulated_cost = 0.0
        self._accumulated_tokens = 0
        # Session 768: Health check mode - skip learning/embedding for test interactions
        self._health_check_mode = health_check_mode
        # Session 960 Phase 0: Track internal docs consumed during execution
        self._docs_consumed: list = []

    # ==================== Doc Consumption Tracking (Session 960) ====================

    def get_docs_consumed(self) -> list:
        """
        Session 960 Phase 0: Return list of SourceInfo dicts for internal docs
        read during this agent execution. Used by build_provenance() to merge
        internal doc references into report provenance.
        """
        return list(self._docs_consumed)

    # ==================== Cost Tracking Helpers (Session 735) ====================

    def _reset_cost_tracking(self) -> None:
        """
        Session 735: Reset accumulated cost and tokens before a new execution.
        Call this at the start of execute() to ensure clean tracking.
        """
        self._accumulated_cost = 0.0
        self._accumulated_tokens = 0

    def _make_result(
        self,
        success: bool,
        message: str = "",
        data: Dict[str, Any] = None,
        error: Optional[str] = None,
        execution_time_ms: int = 0,
        decisions_made: int = 0,
        tool_calls: List[Dict[str, Any]] = None,
        knowledge_attribution: Optional[KnowledgeAttribution] = None,
    ) -> AgentResult:
        """
        Session 735: Create an AgentResult with accumulated cost/tokens.

        Use this helper instead of constructing AgentResult directly to ensure
        cost and token tracking is included automatically.

        Args:
            success: Whether the execution succeeded
            message: Human-readable result message
            data: Optional result data dict
            error: Optional error message
            execution_time_ms: Execution time in milliseconds
            decisions_made: Number of decisions made during execution
            tool_calls: List of tool calls made
            knowledge_attribution: Optional knowledge attribution info

        Returns:
            AgentResult with cost and tokens populated from accumulated values
        """
        return AgentResult(
            success=success,
            message=message,
            data=data or {},
            error=error,
            agent_name=self.name,
            execution_time_ms=execution_time_ms,
            decisions_made=decisions_made,
            tool_calls=tool_calls or [],
            knowledge_attribution=knowledge_attribution,
            tokens_used=self._accumulated_tokens,
            cost=self._accumulated_cost,
        )

    # ==================== Lazy-Loaded Services ====================

    # Session 1074: Per-agent LLM timeout. Document-generation agents override
    # to 180s because gpt-5-mini reasoning + long output needs more than 60s.
    llm_timeout: float = 60.0

    @property
    def client(self) -> OpenAI:
        """Lazy-load OpenAI client with timeout to prevent hanging requests."""
        if self._client is None:
            from django.conf import settings
            # Session 411: Add timeout to prevent indefinite hangs
            # Session 1020: Reduced from 120s to 60s — if OpenAI hasn't responded
            # in 60s it's having issues; agents with tool loops compound this delay
            # Session 1074: Use per-agent llm_timeout class attribute
            self._client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=self.llm_timeout,
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
    def sharpened_system_prompt(self) -> str:
        """
        Session 874: Get the sharpened version of the system prompt.

        Transforms hedging language into decisive language based on
        ChatGPT feedback about needing "sharper conflict" in agent debates.

        Uses the sharpening_type class attribute to determine which rules to apply:
        - 'debate': For debate/discussion agents
        - 'synthesis': For synthesis/conclusion agents
        - 'analysis': For analysis-focused agents

        Returns:
            Sharpened system prompt with decisive language
        """
        if not self.enable_prompt_sharpening or not self.system_prompt:
            return self.system_prompt

        try:
            from core.prompts.sharpening import get_sharpened_agent_prompt
            return get_sharpened_agent_prompt(
                base_prompt=self.system_prompt,
                agent_type=self.sharpening_type
            )
        except ImportError:
            logger.debug("Prompt sharpening module not available")
            return self.system_prompt
        except Exception as e:
            logger.warning(f"Prompt sharpening failed: {e}")
            return self.system_prompt

    def _get_system_learnings_section(self, max_learnings: int = 3) -> str:
        """
        Session 946: Get system learnings formatted for prompt injection.

        Retrieves recent learnings from the LearningLoopOrchestrator that
        apply to this agent. These learnings are derived from:
        - Tool execution outcomes (success/failure patterns)
        - Decision record analysis
        - Cross-agent performance patterns

        Args:
            max_learnings: Maximum learnings to include

        Returns:
            Formatted string for prompt injection, or empty string if none
        """
        try:
            from core.agent_context_middleware import get_system_learnings_for_agent
            learnings = get_system_learnings_for_agent(self.name, max_learnings)
            return learnings if learnings else ""
        except Exception as e:
            logger.debug(f"Could not get system learnings for {self.name}: {e}")
            return ""

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

    @property
    def llm_router(self):
        """
        Session 697: Lazy-load AgentLLMRouter for multi-model routing.

        Enables agents to use different LLMs (OpenAI, Anthropic, DeepSeek, Gemini, Ollama)
        based on their configured optimal model. This is the Enhanced Nervous System
        that routes neural signals (prompts) to the appropriate brain region (LLM).
        """
        if self._llm_router is None:
            try:
                from core.services.agent_llm_router import get_agent_llm_router
                self._llm_router = get_agent_llm_router()
            except ImportError:
                logger.debug("AgentLLMRouter not available")
        return self._llm_router

    # ==================== Agent Delegation (Session 744) ====================

    # Tool definition for delegate_to_specialist - agents can add this to their tools list
    DELEGATE_TO_SPECIALIST_TOOL = {
        "type": "function",
        "function": {
            "name": "delegate_to_specialist",
            "description": (
                "Delegate a sub-task to a specialist agent from our 82-agent system. "
                "Categories: Research (ResearchAgent, TrendAnalysisAgent, MarketIntelligenceAgent), "
                "Content (ContentWriterAgent, EditorAgent, SEOOptimizerAgent), "
                "Media (ImageAgent, VideoAgent, AudioAgent), "
                "Finance (StockAnalystAgent, BullCaseAgent, BearCaseAgent), "
                "Development (CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent), "
                "Business (BrandStrategyAgent, CompetitorAnalysisAgent, CustomerResearchAgent), "
                "Blockchain (SmartContractAuditorAgent, WhaleWatcherAgent), "
                "Markets (SportsOddsAnalyst, ArbitrageDetector, GamePredictor), "
                "and 50+ more specialists. Delegate when a task is outside your expertise."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "specialist_agent": {
                        "type": "string",
                        "description": "Name of the specialist agent to call (e.g., 'ResearchAgent', 'ImageAgent', 'ContentWriterAgent', 'StockAnalystAgent')"
                    },
                    "task": {
                        "type": "string",
                        "description": "The specific task you want the specialist to perform"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about why you need this help and how it fits into your current task"
                    }
                },
                "required": ["specialist_agent", "task"]
            }
        }
    }

    # Session 1002B: Dynamic specialist list from AgentRouter (cached 5 min)
    @property
    def AVAILABLE_SPECIALISTS(self) -> list:
        """Dynamic list from AgentRouter.AGENT_MAP, cached 5 min."""
        global _AVAILABLE_SPECIALISTS_CACHE, _AVAILABLE_SPECIALISTS_CACHE_TIME
        now = time.time()
        if _AVAILABLE_SPECIALISTS_CACHE is None or (now - _AVAILABLE_SPECIALISTS_CACHE_TIME) > 300:
            try:
                from core.agent_router import AgentRouter
                _AVAILABLE_SPECIALISTS_CACHE = [
                    name for name in AgentRouter.AGENT_MAP.keys()
                    if name != 'PersonalAssistantAgent'
                ]
            except Exception:
                _AVAILABLE_SPECIALISTS_CACHE = [
                    'ResearchAgent', 'ContentWriterAgent', 'ImageAgent', 'VideoAgent',
                    'AudioAgent', 'StockAnalystAgent', 'TrendAnalysisAgent',
                    'CompetitorAnalysisAgent', 'CustomerResearchAgent', 'SEOOptimizerAgent',
                    'SocialMediaAgent', 'CodeGeneratorAgent', 'LegalDocDrafterAgent',
                ]
            _AVAILABLE_SPECIALISTS_CACHE_TIME = now
        return _AVAILABLE_SPECIALISTS_CACHE

    @property
    def agent_router(self):
        """
        Session 744: Lazy-load AgentRouter for cross-agent delegation.

        This enables any agent to call other specialist agents for help,
        creating true multi-agent collaboration.
        """
        if not hasattr(self, '_agent_router') or self._agent_router is None:
            try:
                from core.agent_router import AgentRouter
                self._agent_router = AgentRouter(user=self.user)
            except ImportError:
                logger.warning("AgentRouter not available for delegation")
                self._agent_router = None
        return self._agent_router

    def _handle_delegate_to_specialist(
        self,
        specialist_agent: str,
        task: str,
        context: str = "",
        delegation_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Session 744: Handle delegation to a specialist agent.

        This enables cross-agent collaboration where any agent can call
        another agent for help with specialized tasks.

        Args:
            specialist_agent: Name of the agent to delegate to
            task: The task for the specialist
            context: Optional context about the delegation
            delegation_context: Full context dict (spider_context, scifi_context)

        Returns:
            Dict with the specialist's response
        """
        try:
            # Check recursion depth to prevent infinite loops
            if delegation_context is None:
                delegation_context = {}

            delegation_depth = delegation_context.get('_delegation_depth', 0)
            max_depth = 3  # Maximum delegation chain length

            if delegation_depth >= max_depth:
                logger.warning(
                    f"🚫 [Session 744] Delegation depth limit ({max_depth}) reached. "
                    f"{self.name} cannot delegate to {specialist_agent}"
                )
                return {
                    'success': False,
                    'error': f'Maximum delegation depth ({max_depth}) reached',
                    'specialist': specialist_agent,
                    'delegating_agent': self.name
                }

            # Validate specialist exists
            if specialist_agent not in self.AVAILABLE_SPECIALISTS:
                # Try to route anyway - AgentRouter might know about it
                logger.debug(f"Specialist {specialist_agent} not in AVAILABLE_SPECIALISTS, trying anyway")

            # Get router
            if not self.agent_router:
                return {
                    'success': False,
                    'error': 'AgentRouter not available for delegation',
                    'specialist': specialist_agent
                }

            logger.info(
                f"🤝 [Session 744] {self.name} delegating to {specialist_agent}: "
                f"{task[:100]}..."
            )

            # Build delegation context with depth tracking
            delegation_ctx = {
                '_delegation_depth': delegation_depth + 1,
                '_delegation_chain': delegation_context.get('_delegation_chain', []) + [self.name],
                '_original_task': delegation_context.get('_original_task', task),
                'delegating_agent': self.name,
                'delegation_context': context,
                # Pass through spider/scifi context if available
                '_inherited_spider_context': delegation_context.get('spider_context', {}),
                '_inherited_scifi_context': delegation_context.get('scifi_context', {}),
            }

            # Route to the specialist
            result = self.agent_router.route(
                specialist_agent,
                task,
                context=delegation_ctx
            )

            # Record cross-agent collaboration for learning
            self._record_delegation(specialist_agent, task, result)

            # Format response
            if hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            elif isinstance(result, dict):
                result_data = result
            else:
                result_data = {'result': str(result)}

            return {
                'success': result_data.get('success', True),
                'specialist': specialist_agent,
                'delegating_agent': self.name,
                'specialist_response': result_data.get('message', ''),
                'specialist_data': result_data.get('data', {}),
                'delegation_depth': delegation_depth + 1
            }

        except Exception as e:
            logger.error(f"Delegation to {specialist_agent} failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'specialist': specialist_agent,
                'delegating_agent': self.name
            }

    def _record_delegation(
        self,
        specialist_agent: str,
        task: str,
        result: Any
    ) -> None:
        """
        Session 744: Record cross-agent delegation for learning.

        Creates an AgentLearning record to track which agents collaborate
        and how effective the collaborations are.
        """
        try:
            from core.models_unified_system import Agent, AgentLearning, AgentSolution

            # Get both agent models
            teacher_model = Agent.objects.filter(name=specialist_agent).first()
            student_model = self.agent_model

            if not teacher_model or not student_model:
                logger.debug(f"Could not record delegation: missing agent models")
                return

            # Determine success from result
            if hasattr(result, 'success'):
                success = result.success
            elif isinstance(result, dict):
                success = result.get('success', True)
            else:
                success = True

            # Get or create a solution for this delegation
            # AgentSolution requires: agent (FK), title, description, solution_type
            solution, _ = AgentSolution.objects.get_or_create(
                agent=teacher_model,  # The specialist providing the solution
                title=f"Delegation: {self.name} → {specialist_agent}",
                solution_type='cross_agent_delegation',
                defaults={
                    'description': f"Cross-agent delegation from {self.name} to {specialist_agent}",
                    'metrics': {
                        'category': 'collaboration',
                        'success': success,
                        'session': 744
                    },
                    'tags': ['delegation', 'cross_agent', self.name, specialist_agent],
                    'success_rate': 0.8 if success else 0.5,
                }
            )

            # Delegation is tracked via AgentExecution records now;
            # synthetic AgentLearning records removed (effectiveness_before/after were hardcoded).
            logger.debug(
                f"Recorded delegation: {self.name} -> {specialist_agent}"
            )

        except Exception as e:
            logger.debug(f"Could not record delegation learning: {e}")

    def get_tools_with_delegation(self) -> List[Dict[str, Any]]:
        """
        Session 744: Get this agent's tools plus shared tools.
        Session 1002C: Also injects web_search and spider_query.

        Returns:
            List of tool definitions including delegate_to_specialist,
            web_search, and spider_query
        """
        all_tools = self._get_tools_with_shared()
        # Add delegation tool if not already present
        has_delegation = any(
            t.get('function', {}).get('name') == 'delegate_to_specialist'
            for t in all_tools
        )
        if not has_delegation:
            all_tools.append(self.DELEGATE_TO_SPECIALIST_TOOL)

        return all_tools

    def _get_tools_with_shared(self) -> List[Dict[str, Any]]:
        """
        Session 1002C: Inject web_search and spider_query into any agent's
        tool list. Called by get_tools_with_delegation() and also used
        directly for non-delegating agents.
        """
        all_tools = list(self.tools) if self.tools else []
        existing_names = {
            t.get('function', {}).get('name') for t in all_tools
        }
        if 'web_search' not in existing_names:
            all_tools.append(WEB_SEARCH_TOOL)
        if 'spider_query' not in existing_names:
            all_tools.append(SPIDER_QUERY_TOOL)
        return all_tools

    def get_available_specialists_prompt(self) -> str:
        """
        Session 744: Get a prompt snippet listing available specialists.

        Include this in your system prompt to inform the LLM about
        available specialists for delegation.

        Returns:
            String to include in system prompt
        """
        specialists_list = "\n".join(f"- {s}" for s in self.AVAILABLE_SPECIALISTS)
        return f"""
## Available Specialist Agents
You can delegate tasks to these specialists using the delegate_to_specialist tool:
{specialists_list}

Use delegation when you need expertise outside your specialty. For example:
- Need research? Delegate to ResearchAgent
- Need an image? Delegate to ImageAgent
- Need market analysis? Delegate to StockAnalystAgent
"""

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

    def _get_relevant_docs_for_task(self, task: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Session 786: Retrieve relevant documentation for the current task.

        Uses the ScopedRetrievalService to search curated documentation
        with smart defaults:
        - Searches active curated docs first (scope=docs_index_active)
        - Auto-expands to superseded docs if no results
        - Ranks curated > uncurated, active > superseded

        Args:
            task: The current task to find relevant docs for
            limit: Maximum docs to retrieve

        Returns:
            List of relevant doc dicts with title, path, snippet, scope
        """
        results = []

        try:
            from core.services.scoped_retrieval import get_scoped_retrieval_service

            service = get_scoped_retrieval_service()
            retrieval_results = service.search(
                query=task,
                limit=limit,
                auto_expand=True  # Expand scope if no results in curated
            )

            for r in retrieval_results:
                results.append({
                    'source_agent': 'Documentation',
                    'title': r.title[:60] if r.title else 'Documentation',
                    'summary': r.content_snippet[:200] if r.content_snippet else '',
                    'knowledge_type': 'documentation',
                    'confidence': r.similarity_score,
                    'doc_path': r.path,
                    'doc_scope': r.scope,
                    'is_curated': r.is_curated,
                })

        except Exception as e:
            logger.debug(f"Doc retrieval not available: {e}")

        return results

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
        spider_context: Dict[str, Any],
        intelligence_context: Dict[str, Any] = None  # Session 565: Platform intelligence
    ) -> tuple:
        """
        Session 400: Build prompt AND return knowledge attribution.
        Session 565: Now includes platform intelligence (agent knowledge, dreams, policies).

        This is the preferred method for agents that want to surface
        what knowledge influenced their response.

        Args:
            task: The user's task
            scifi_context: Sci-fi system context
            spider_context: Spider intelligence context
            intelligence_context: Session 565 - Platform intelligence from PAIntelligenceEnricher

        Returns:
            Tuple of (prompt_string, KnowledgeAttribution)
        """
        # Get relevant knowledge first (we need it for both prompt and attribution)
        relevant_knowledge = self._get_relevant_knowledge_for_task(task)

        # Build the attribution
        attribution = self._build_knowledge_attribution(relevant_knowledge)

        # Build the prompt (using the already-retrieved knowledge)
        # Session 874: Use sharpened system prompt for decisive language
        parts = [self.sharpened_system_prompt]

        # Session 575: Add current date/time context so agents know they have recent data
        from datetime import datetime
        from django.utils import timezone
        current_time = timezone.now()
        parts.append(f"\n\n## CURRENT DATE & TIME")
        parts.append(f"Today is {current_time.strftime('%A, %B %d, %Y at %I:%M %p %Z')}.")
        parts.append("You have access to real-time data through your spider network. Do NOT say your knowledge cutoff is 2024.")

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

        # Session 946: Add system learnings from execution data
        system_learnings = self._get_system_learnings_section()
        if system_learnings:
            parts.append(f"\n\n{system_learnings}")

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

            # Session 773: Add PA Knowledge if injected
            pa_knowledge = spider_context.get('pa_knowledge')
            if pa_knowledge and pa_knowledge.get('has_dynamic_context'):
                try:
                    from core.services.pa_knowledge_injector import get_pa_knowledge_injector
                    injector = get_pa_knowledge_injector()
                    pa_prompt_section = injector.format_for_prompt(pa_knowledge)
                    if pa_prompt_section:
                        parts.append(pa_prompt_section)
                except Exception as e:
                    logger.debug(f"Failed to format PA knowledge: {e}")

        # Session 565: Add platform intelligence context
        # Session 573: Now includes system state awareness
        if intelligence_context and intelligence_context.get('context_text'):
            intel_text = intelligence_context.get('context_text', '')
            intel_attribution = intelligence_context.get('attribution', '')
            intel_metadata = intelligence_context.get('metadata', {})

            total_sources = (
                intel_metadata.get('knowledge_count', 0) +
                intel_metadata.get('experts_count', 0) +
                intel_metadata.get('dreams_count', 0) +
                intel_metadata.get('policies_count', 0) +
                intel_metadata.get('trends_count', 0) +
                intel_metadata.get('system_state_count', 0)  # Session 573
            )

            if total_sources > 0:
                parts.append(f"\n\n## 🧠 Platform Intelligence ({total_sources} sources)")
                parts.append(intel_text)
                if intel_attribution:
                    parts.append(f"\n*{intel_attribution}*")
                parts.append("\nUse this knowledge from our agent network to inform your response.")

                # Update attribution with intelligence sources
                knowledge_items = attribution.knowledge_items.copy() if attribution.knowledge_items else []
                for item in intelligence_context.get('knowledge', [])[:3]:
                    knowledge_items.append({
                        'title': item.get('title', '')[:60],
                        'source': item.get('agent__name', 'Platform'),
                        'type': 'platform_intelligence'
                    })

                attribution = KnowledgeAttribution(
                    spider_sources=attribution.spider_sources + intel_metadata.get('spider_sources', [])[:5],
                    knowledge_items=knowledge_items,
                    confidence_score=max(attribution.confidence_score, 0.7),
                    data_freshness_hours=attribution.data_freshness_hours,
                    total_sources=attribution.total_sources + total_sources
                )

        # Session 1078: Inject learned user preferences from learning loop
        learned_prefs = (spider_context or {}).get('learned_user_preferences') or ''
        agent_prefs = (spider_context or {}).get('agent_learned_preferences') or ''
        if learned_prefs or agent_prefs:
            parts.append("\n\n## User Preferences (from learning loop)")
            if learned_prefs:
                parts.append(learned_prefs)
            if agent_prefs:
                parts.append(agent_prefs)

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
        # Session 874: Use sharpened system prompt for decisive language
        parts = [self.sharpened_system_prompt]

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

        # Session 946: Add system learnings from execution data
        system_learnings = self._get_system_learnings_section()
        if system_learnings:
            parts.append(f"\n\n{system_learnings}")

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

        # Session 1078: Inject learned user preferences from learning loop
        learned_prefs = (spider_context or {}).get('learned_user_preferences') or ''
        agent_prefs = (spider_context or {}).get('agent_learned_preferences') or ''
        if learned_prefs or agent_prefs:
            parts.append("\n\n## User Preferences (from learning loop)")
            if learned_prefs:
                parts.append(learned_prefs)
            if agent_prefs:
                parts.append(agent_prefs)

        # Add the task
        parts.append(f"\n\n## Task")
        parts.append(task)

        return "\n".join(parts)

    def _build_intelligent_prompt(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        additional_context: str = ""
    ) -> str:
        """
        Session 528: Build an intelligent, context-aware prompt.

        This is the PREFERRED method for building prompts. All agents should
        use this instead of _build_prompt() for full intelligent prompting.

        Includes:
        - Platform context (capabilities, agents, etc.)
        - Memory Palace context (past interactions)
        - Agent mood influence
        - User preferences
        - Dynamic year/date references
        - Spider intelligence summary
        - Evolution level
        - Policy context
        - Learned knowledge

        Args:
            task: The user's task
            scifi_context: Sci-fi system context (mood, evolution, memory)
            spider_context: Spider intelligence context
            additional_context: Any agent-specific context to append

        Returns:
            Complete intelligent prompt string
        """
        from datetime import datetime

        now = datetime.now()
        year = now.year
        month_year = now.strftime('%B %Y')
        today = now.strftime('%B %d, %Y')

        # Session 874: Use sharpened system prompt for decisive language
        prompt_parts = [self.sharpened_system_prompt]

        # Session 817: Add AUTONOMOUS BEHAVIOR directive to ALL agents
        # This ensures agents work autonomously and don't try to converse with users
        prompt_parts.append("""

## CRITICAL: AUTONOMOUS AGENT BEHAVIOR (Session 817)
You are an AUTONOMOUS agent running in an automated pipeline. You are NOT in a conversation with a human user.

MANDATORY BEHAVIORS:
- NEVER ask questions or request clarification - there is no one to respond
- NEVER use phrases like "Please provide...", "Could you clarify...", "I need you to..."
- NEVER output content that expects a human response
- If you lack required data, USE YOUR AVAILABLE TOOLS to discover it
- If tools can't get the data, REPORT what you found and what you couldn't find
- Always produce a COMPLETE OUTPUT even with partial information

OUTPUT FORMAT:
- Produce structured reports, not conversations
- State what was analyzed, what was found, what actions were taken
- Include a "Limitations" section if data was unavailable
- End with concrete findings/recommendations, not questions

EXAMPLES OF WRONG OUTPUT:
- "What channel would you like me to analyze?" ❌
- "Please provide the topic you want me to evaluate" ❌
- "I need more information about..." ❌

EXAMPLES OF CORRECT OUTPUT:
- "Analyzed 3 available channels. Top performer: Channel X with 10k avg views." ✓
- "No channels found in system. Unable to perform analysis." ✓
- "Partial analysis complete. Found 5 trends. Missing: engagement data." ✓
""")

        # 1. Add Platform Context
        try:
            from core.prompts.registry import PLATFORM_CONTEXT
            if PLATFORM_CONTEXT:
                prompt_parts.append(f"\n\n{PLATFORM_CONTEXT}")
        except ImportError:
            pass

        # 1.5 Session 820: Inject critical system docs for system-aware agents
        # Agents with requires_system_context=True get CLAUDE.md, 00-START-NEXT-SESSION.md
        # injected so they have accurate knowledge of system state (74 agents, 77 spiders, etc.)
        if self.requires_system_context:
            try:
                from core.services.docs_context_builder import get_docs_context_builder
                builder = get_docs_context_builder()
                critical_content = builder._get_critical_docs_content()
                if critical_content:
                    prompt_parts.append(f"\n\n{critical_content}")
                    logger.debug(f"📚 [Session 820] Injected critical docs for {self.name}")
            except Exception as e:
                logger.warning(f"📚 [Session 820] Failed to inject critical docs for {self.name}: {e}")

        # 2. Add Temporal Awareness
        prompt_parts.append(f"""

## TEMPORAL AWARENESS (Session 528 / Strengthened Session 1006)
- Current Date: {today}
- Current Year: {year}
- CRITICAL: All content must be current and relevant to {month_year}
- DO NOT reference outdated years like {year-2} or {year-1} unless discussing historical context
- Use phrases like "in {year}" and "as of {month_year}" to ensure freshness
- Your training data may be outdated. When writing about current events, politics,
  or any time-sensitive topic, ground your claims ONLY in the source data provided.
  Do NOT rely on your training data for who currently holds political office,
  recent legislation, or market conditions.""")

        # 3. Add Agent Mood from scifi_context
        if scifi_context:
            mood = scifi_context.get('mood', {})
            if mood:
                mood_name = mood.get('mood_type') or mood.get('name', 'focused')
                mood_desc = mood.get('description', '')
                style_mod = mood.get('style_modifier', 'balanced')
                confidence_mod = mood.get('confidence_modifier', 1.0)

                prompt_parts.append(f"""

## CREATIVE MOOD (Session 528)
Current Mood: **{mood_name.title() if isinstance(mood_name, str) else 'Focused'}**
Style Tendency: {style_mod}
{f'Description: {mood_desc}' if mood_desc else ''}

This influences your approach - embrace it!""")

                # Add behavioral directive based on confidence
                if confidence_mod >= 1.3:
                    prompt_parts.append("**BEHAVIORAL DIRECTIVE:** You are highly confident. Make bold recommendations.")
                elif confidence_mod >= 1.1:
                    prompt_parts.append("**BEHAVIORAL DIRECTIVE:** You are confident. Provide clear recommendations with conviction.")
                elif confidence_mod <= 0.8:
                    prompt_parts.append("**BEHAVIORAL DIRECTIVE:** You are in a cautious state. Prefer safe, proven approaches.")

            # 4. Add Evolution Level
            evolution = scifi_context.get('evolution', {})
            if evolution:
                level = evolution.get('level', 1)
                title = evolution.get('title', 'Apprentice')
                authority = evolution.get('authority_level', 'junior')

                prompt_parts.append(f"""

## AGENT EVOLUTION (Session 528)
Level: {level} - {title} ({authority})
Your experience level influences the sophistication of your approach.""")

                # Authority-based guidance
                if authority == 'master' or level >= 31:
                    prompt_parts.append("**AUTHORITY:** Lead with authority. Be definitive in your assessments.")
                elif authority == 'expert' or level >= 16:
                    prompt_parts.append("**AUTHORITY:** Provide authoritative guidance with confidence.")
                elif authority == 'senior' or level >= 6:
                    prompt_parts.append("**AUTHORITY:** Provide balanced recommendations based on experience.")

            # 5. Add Memory Palace context
            memory = scifi_context.get('memory', {})
            if memory:
                patterns = memory.get('learned_patterns', [])
                if patterns:
                    prompt_parts.append(f"""

## MEMORY PALACE - Past Learning (Session 528)
I remember from past interactions:
{chr(10).join(f'- {p}' for p in patterns[:5])}

Use these insights to personalize and improve the response.""")

            # Recent dreams/insights
            dreams = scifi_context.get('dreams', [])
            if dreams:
                recent = dreams[0] if isinstance(dreams, list) else {}
                content = recent.get('content', '')[:100] if isinstance(recent, dict) else ''
                if content:
                    prompt_parts.append(f"""

## Recent Creative Thought
{content}""")

        # 6. Add User Preferences (if user available)
        if self.user:
            try:
                from core.models_unified_system import UserPreferences
                prefs = UserPreferences.objects.filter(user=self.user).first()
                if prefs:
                    pref_items = []
                    for attr in ['preferred_tone', 'writing_style', 'industry', 'preferred_style']:
                        val = getattr(prefs, attr, None)
                        if val:
                            pref_items.append(f"- {attr.replace('_', ' ').title()}: {val}")

                    if pref_items:
                        prompt_parts.append(f"""

## USER PREFERENCES (Session 528)
{chr(10).join(pref_items)}

Tailor the response to match these preferences.""")
            except Exception:
                pass

        # 7. Add Spider Intelligence Summary
        if spider_context:
            trends = spider_context.get('relevant_trends', []) or spider_context.get('trends', [])
            if trends:
                # Handle both string lists and dict lists
                trend_names = []
                for t in trends[:5]:
                    if isinstance(t, str):
                        trend_names.append(t)
                    elif isinstance(t, dict):
                        trend_names.append(t.get('topic') or t.get('title') or str(t))

                if trend_names:
                    prompt_parts.append(f"""

## REAL-TIME INTELLIGENCE (Session 528)
Current trending topics from spider network:
{', '.join(trend_names)}

Consider these trends when crafting the response to maximize relevance and engagement.""")

            # Creative trends
            creative = spider_context.get('creative_trends', {})
            if creative:
                styles = creative.get('trending_styles', [])
                if styles:
                    style_names = [s.get('style', '') for s in styles[:3] if isinstance(s, dict)]
                    if style_names:
                        prompt_parts.append(f"Trending creative styles: {', '.join(style_names)}")

        # 8. Add Relevant Knowledge from Past Learning (existing infrastructure)
        relevant_knowledge = self._get_relevant_knowledge_for_task(task)
        if relevant_knowledge:
            prompt_parts.append(f"\n\n## Relevant Knowledge from Past Learning (Session 528)")
            prompt_parts.append("You have learned the following that may be relevant:")
            for idx, knowledge in enumerate(relevant_knowledge[:3], 1):
                source = knowledge.get('source_agent', 'Unknown')
                title = knowledge.get('title', '')[:60]
                summary = knowledge.get('summary', '')[:150]
                prompt_parts.append(f"\n{idx}. [{source}] {title}")
                if summary:
                    prompt_parts.append(f"   {summary}")

        # 8.5 Session 786: Add Relevant Documentation from Embedded Documents
        # This connects agents to the 390+ curated documents (session handoffs,
        # architecture docs, guides) that were previously isolated from agent context.
        relevant_docs = self._get_relevant_docs_for_task(task, limit=3)
        if relevant_docs:
            prompt_parts.append(f"\n\n## Relevant Documentation (Session 786)")
            # Session 850: Clarify that docs are reference material, not tasks
            prompt_parts.append("**REFERENCE ONLY:** The following describes EXISTING code/features.")
            prompt_parts.append("Use this to understand the codebase - do NOT treat as work to be done.")
            for idx, doc in enumerate(relevant_docs, 1):
                title = doc.get('title', 'Documentation')
                summary = doc.get('summary', '')[:200]
                doc_path = doc.get('doc_path', '')
                confidence = doc.get('confidence', 0)
                scope = doc.get('doc_scope', 'unknown')

                prompt_parts.append(f"\n{idx}. **{title}** (relevance: {confidence:.0%})")
                if summary:
                    prompt_parts.append(f"   {summary}")
                if doc_path:
                    prompt_parts.append(f"   Source: {doc_path} [{scope}]")

            prompt_parts.append("\nUse these documents to ground your response in established patterns and decisions.")

        # 8.6 Session 1035: Inject user-uploaded document context from RAG
        user_docs_text = spider_context.get('user_documents_text', '') if spider_context else ''
        if user_docs_text:
            user_docs_sources = spider_context.get('user_documents_sources', [])
            prompt_parts.append("\n\n## Your Uploaded Documents")
            prompt_parts.append(
                "The user has uploaded documents relevant to this task. "
                "Use these as primary reference material. Cite specific details when relevant."
            )
            prompt_parts.append(user_docs_text)
            if user_docs_sources:
                prompt_parts.append(f"\nDocument sources: {', '.join(user_docs_sources)}")

        # 9. Add Policy Context (from Boardroom Decisions)
        try:
            from core.services.policy_context import get_policy_context_service
            policy_service = get_policy_context_service()
            policy_context = policy_service.get_policies_for_agent(self.name, max_policies=3)
            if policy_context:
                prompt_parts.append(policy_context)
        except Exception:
            pass

        # 9.5 Session 946: Add System Learnings from execution data
        # These learnings come from analyzing ToolCallRecord and DecisionRecord
        # to identify patterns (tool reliability, agent performance, confidence calibration)
        system_learnings = self._get_system_learnings_section()
        if system_learnings:
            prompt_parts.append(f"\n\n{system_learnings}")

        # 10. Add Agent-specific context if provided
        if additional_context:
            prompt_parts.append(f"\n\n{additional_context}")

        # 10.5 Session 1078: Inject learned user preferences from learning loop
        learned_prefs = (spider_context or {}).get('learned_user_preferences') or ''
        agent_prefs = (spider_context or {}).get('agent_learned_preferences') or ''
        if learned_prefs or agent_prefs:
            prompt_parts.append("\n\n## User Preferences (from learning loop)")
            if learned_prefs:
                prompt_parts.append(learned_prefs)
            if agent_prefs:
                prompt_parts.append(agent_prefs)

        # 11. Add the Task
        prompt_parts.append(f"""

## Task
{task}""")

        # Session 729: Track intelligent prompting metrics
        # Session 786: Added included_documentation tracking
        self._track_intelligent_prompt_metrics(
            task=task,
            scifi_context=scifi_context,
            spider_context=spider_context,
            included_learned_knowledge=bool(relevant_knowledge),
            included_documentation=bool(relevant_docs),  # Session 786
            prompt_parts=prompt_parts
        )

        return "\n".join(prompt_parts)

    def _track_intelligent_prompt_metrics(
        self,
        task: str,
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        included_learned_knowledge: bool,
        included_documentation: bool,  # Session 786: Track doc retrieval
        prompt_parts: List[str]
    ) -> None:
        """
        Session 729: Track intelligent prompting usage metrics.
        Session 786: Added included_documentation parameter.

        Records which context components were included in the prompt,
        token estimates, and task info. This enables analysis of:
        - Which agents use which context types
        - Token overhead from context injection
        - Correlation between context usage and response quality

        All tracking is wrapped in try/except to never break agent execution.
        """
        try:
            from core.models_agent_memory import IntelligentPromptMetric

            # Detect which context components were included
            scifi = scifi_context or {}
            spider = spider_context or {}

            mood = scifi.get('mood', {})
            evolution = scifi.get('evolution', {})
            memory = scifi.get('memory', {})

            included_mood = bool(mood)
            included_evolution = bool(evolution)
            included_memory = bool(memory.get('learned_patterns'))
            included_spider = bool(spider.get('relevant_trends') or spider.get('trends'))

            # Check if policy was included (look for policy marker in prompt)
            full_prompt = "\n".join(prompt_parts)
            included_policy = '## Active Policies' in full_prompt or 'POLICY' in full_prompt

            # Estimate token counts (rough: ~4 chars per token)
            base_tokens = len(self.system_prompt) // 4 if self.system_prompt else 0
            total_tokens = len(full_prompt) // 4
            context_tokens = total_tokens - base_tokens

            # Extract task type
            task_type = self._detect_query_type(task)
            task_preview = task[:255] if task else ""

            # Build context summaries (limited size)
            mood_context = {
                'mood_type': mood.get('mood_type', ''),
                'confidence': mood.get('confidence_modifier', 1.0)
            } if mood else {}

            spider_summary = {}
            if spider:
                trends = spider.get('relevant_trends', []) or spider.get('trends', [])
                if trends:
                    trend_names = []
                    for t in trends[:3]:
                        if isinstance(t, str):
                            trend_names.append(t)
                        elif isinstance(t, dict):
                            trend_names.append(t.get('topic', str(t))[:50])
                    spider_summary = {'trends': trend_names}

            memory_summary = {}
            if memory:
                patterns = memory.get('learned_patterns', [])
                if patterns:
                    memory_summary = {'pattern_count': len(patterns)}

            # Get agent category from name
            agent_category = ''
            if 'Content' in self.name:
                agent_category = 'content'
            elif 'Stock' in self.name or 'Market' in self.name:
                agent_category = 'financial'
            elif 'Code' in self.name or 'Developer' in self.name:
                agent_category = 'development'
            elif 'Research' in self.name:
                agent_category = 'research'
            elif 'Image' in self.name or 'Video' in self.name or 'Audio' in self.name:
                agent_category = 'creative'
            elif 'Blockchain' in self.name:
                agent_category = 'blockchain'

            # Create metric record
            IntelligentPromptMetric.objects.create(
                agent_name=self.name,
                agent_category=agent_category,
                included_mood=included_mood,
                included_memory_palace=included_memory,
                included_spider_intel=included_spider,
                included_evolution=included_evolution,
                included_policy=included_policy,
                included_learned_knowledge=included_learned_knowledge,
                included_documentation=included_documentation,  # Session 786
                included_temporal=True,  # Always included
                base_prompt_tokens=base_tokens,
                context_tokens_added=context_tokens,
                total_prompt_tokens=total_tokens,
                mood_context=mood_context,
                spider_summary=spider_summary,
                memory_summary=memory_summary,
                task_type=task_type,
                task_preview=task_preview,
            )

            logger.debug(f"Tracked intelligent prompt for {self.name}: {total_tokens} tokens")

        except Exception as e:
            # Never let tracking break agent execution
            logger.debug(f"Intelligent prompt tracking failed (non-critical): {e}")

    def _call_openai(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]] = None,
        execution_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make a GPT API call with this agent's tools.

        Args:
            prompt: The complete prompt (system + context + task)
            conversation_history: Optional previous messages
            execution_context: Optional context (spider_context, scifi_context) for delegation
                              Session 744: Store this so _execute_tool_call can access it

        Returns:
            OpenAI response dict with message and tool_calls
        """
        # Session 744: Store execution context for delegation tool calls
        if execution_context:
            self._current_delegation_context = execution_context
        elif not hasattr(self, '_current_delegation_context'):
            self._current_delegation_context = {}
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
        start_time = time.time()  # Session 536: Track timing for analytics

        # Session 744: Auto-include delegation tool if can_delegate is True
        # Session 1002C: Always inject web_search + spider_query for all agents
        if self.can_delegate:
            effective_tools = self.get_tools_with_delegation()
        else:
            effective_tools = self._get_tools_with_shared()

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                tools=effective_tools if effective_tools else None,
                tool_choice="auto" if effective_tools else None,
                max_completion_tokens=6000,  # High enough for reasoning + output
            )

            # Session 536: Track analytics (cost, tokens, performance)
            self._track_llm_analytics(response, start_time)

            choice = response.choices[0]

            # Session 735: Extract and accumulate cost/tokens
            usage = getattr(response, 'usage', None)
            input_tokens = getattr(usage, 'prompt_tokens', 0) if usage else 0
            output_tokens = getattr(usage, 'completion_tokens', 0) if usage else 0
            total_tokens = getattr(usage, 'total_tokens', 0) if usage else 0
            # GPT-5-mini pricing: $0.003/1K input, $0.012/1K output
            call_cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.012 / 1000)

            # Accumulate for this execution
            self._accumulated_tokens += total_tokens
            self._accumulated_cost += call_cost

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
                # Session 735: Return cost/tokens for tracking
                'tokens_used': total_tokens,
                'cost': call_cost,
            }

        except TimeoutError as e:
            # Session 411: Handle timeout specifically
            logger.error(f"OpenAI API timeout in {self.name} after {self.llm_timeout}s: {e}")
            raise TimeoutError(f"OpenAI API request timed out after {self.llm_timeout}s in {self.name}")
        except Exception as e:
            logger.error(f"OpenAI API error in {self.name}: {e}")
            raise

    def _call_llm_with_retry(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]] = None,
        execution_context: Dict[str, Any] = None,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Session 841: Call LLM with exponential backoff retry on transient errors.

        This wrapper around _call_openai adds intelligent retry logic for:
        - Rate limit errors (429)
        - Server errors (5xx)
        - Connection errors

        Args:
            prompt: The complete prompt
            conversation_history: Optional previous messages
            execution_context: Optional context for delegation
            max_retries: Maximum retry attempts (default: 3)
            base_delay: Initial delay in seconds (default: 1.0)
            max_delay: Maximum delay cap in seconds (default: 30.0)

        Returns:
            OpenAI response dict (same as _call_openai)

        Raises:
            Exception: If all retries exhausted
        """
        import random

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return self._call_openai(prompt, conversation_history, execution_context)

            except Exception as e:
                last_exception = e
                error_str = str(e).lower()

                # Session 1074: Distinguish API timeouts (model too slow, NOT retryable)
                # from connection errors (transient, retryable). Retrying a 60s timeout
                # 3 times wastes 180s and always fails identically.
                from openai import APITimeoutError
                is_api_timeout = isinstance(e, APITimeoutError)

                # Check if this is a retryable error
                is_rate_limit = '429' in str(e) or 'rate limit' in error_str
                is_server_error = any(code in str(e) for code in ['500', '502', '503', '504'])
                is_connection_error = 'connection' in error_str and not is_api_timeout

                is_retryable = is_rate_limit or is_server_error or is_connection_error

                if is_api_timeout:
                    logger.error(
                        f"[Session 1074] {self.name} LLM call timed out after {self.llm_timeout}s "
                        f"(not retrying — increase llm_timeout for heavy agents): {e}"
                    )
                    raise

                if not is_retryable or attempt >= max_retries:
                    # Not retryable or out of retries
                    logger.error(
                        f"[Session 841] {self.name} LLM call failed after {attempt + 1} attempts: {e}"
                    )
                    raise

                # Calculate exponential backoff with jitter
                delay = min(base_delay * (2 ** attempt), max_delay)
                delay += delay * 0.1 * random.random()  # Add 0-10% jitter

                error_type = 'rate_limit' if is_rate_limit else 'server_error' if is_server_error else 'connection'
                logger.warning(
                    f"[Session 841] {self.name} LLM call failed ({error_type}), "
                    f"retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries}): {e}"
                )

                time.sleep(delay)

        # Should not reach here, but just in case
        raise last_exception

    def _call_completion_with_retry(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_completion_tokens: int = 6000,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        """
        Session 857: Call OpenAI completion with retry logic for simple prompts.

        This method is for agents that need to make simple completion calls without
        the full tool framework. It provides exponential backoff retry for:
        - Rate limit errors (429)
        - Server errors (5xx)
        - Connection errors

        Args:
            messages: List of message dicts (role, content)
            model: Model to use (default: gpt-4o-mini)
            max_completion_tokens: Max tokens for response
            max_retries: Maximum retry attempts (default: 3)
            base_delay: Initial delay in seconds (default: 1.0)
            max_delay: Maximum delay cap in seconds (default: 30.0)

        Returns:
            OpenAI ChatCompletion response object

        Raises:
            Exception: If all retries exhausted
        """
        import random

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_completion_tokens,
                )
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()

                # Session 1074: Don't retry API timeouts (see _call_llm_with_retry)
                from openai import APITimeoutError
                is_api_timeout = isinstance(e, APITimeoutError)

                # Check if this is a retryable error
                is_rate_limit = '429' in str(e) or 'rate limit' in error_str
                is_server_error = any(code in str(e) for code in ['500', '502', '503', '504'])
                is_connection_error = 'connection' in error_str and not is_api_timeout

                is_retryable = is_rate_limit or is_server_error or is_connection_error

                if is_api_timeout:
                    logger.error(
                        f"[Session 1074] {self.name} completion timed out after {self.llm_timeout}s "
                        f"(not retrying): {e}"
                    )
                    raise

                if not is_retryable or attempt >= max_retries:
                    # Not retryable or out of retries
                    logger.error(
                        f"[Session 857] {self.name} completion call failed after {attempt + 1} attempts: {e}"
                    )
                    raise

                # Calculate exponential backoff with jitter
                delay = min(base_delay * (2 ** attempt), max_delay)
                delay += delay * 0.1 * random.random()  # Add 0-10% jitter

                error_type = 'rate_limit' if is_rate_limit else 'server_error' if is_server_error else 'connection'
                logger.warning(
                    f"[Session 857] {self.name} completion call failed ({error_type}), "
                    f"retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries}): {e}"
                )

                time.sleep(delay)

        # Should not reach here, but just in case
        raise last_exception

    def _track_llm_analytics(self, response, start_time: float) -> None:
        """
        Session 536: Track LLM call analytics - cost, tokens, performance.

        This method is called after every successful OpenAI API call to record:
        - Token usage (input/output)
        - Estimated cost
        - Response time
        - Performance metrics

        All tracking is wrapped in try/except to never break agent execution.
        """
        try:
            from core.views_analytics import AdvancedAnalyticsService
            from core.models_unified_system import PerformanceLog

            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)

            # Get user context (may be None for system operations)
            user = getattr(self, 'user', None)

            # Extract token usage from response
            usage = getattr(response, 'usage', None)
            input_tokens = getattr(usage, 'prompt_tokens', 0) if usage else 0
            output_tokens = getattr(usage, 'completion_tokens', 0) if usage else 0
            total_tokens = getattr(usage, 'total_tokens', 0) if usage else 0

            # Calculate cost (GPT-5-mini estimated pricing)
            # Reasoning models typically: $0.003/1K input, $0.012/1K output
            estimated_cost = (input_tokens * 0.003 / 1000) + (output_tokens * 0.012 / 1000)

            # Track cost (requires authenticated user)
            if user:
                AdvancedAnalyticsService.track_cost(
                    user=user,
                    provider='openai',
                    service='gpt-5-mini',
                    operation='agent_execution',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    estimated_cost_usd=estimated_cost,
                    metadata={'agent': self.name, 'total_tokens': total_tokens}
                )

                # Track usage metric
                AdvancedAnalyticsService.track_usage(
                    user=user,
                    category='agent',
                    metric_type='llm_call',
                    feature_name=self.name,
                    count=1,
                    duration_ms=duration_ms,
                    provider='openai'
                )

            # Track performance (system-wide, no user required)
            PerformanceLog.objects.create(
                component_type='api',
                component_name=f'agent:{self.name}',
                response_time_ms=duration_ms,
                success=True,
                endpoint='openai/chat/completions',
                method='POST'
            )

            logger.debug(f"Analytics tracked for {self.name}: {total_tokens} tokens, ${estimated_cost:.4f}, {duration_ms}ms")

        except Exception as tracking_error:
            # Never let tracking failures break agent execution
            logger.debug(f"Analytics tracking failed (non-critical): {tracking_error}")

    # ==================== Mission Control (Session 763) ====================

    def _maybe_create_attention_item(
        self,
        result: AgentResult,
        task: str,
        context: Dict[str, Any] = None
    ) -> None:
        """
        Session 763: Create Mission Control attention item if result is actionable.

        Called at the end of execute() to surface actionable outputs to humans.
        Override `actionable_config` in subclasses to enable.

        The attention item appears on the Human Page with action buttons that
        actually execute (publish, set alert, deep dive, etc.) rather than
        just recording the decision.

        Args:
            result: The AgentResult from execute()
            task: The original task string
            context: Optional execution context
        """
        from django.core.cache import cache

        config = getattr(self, 'actionable_config', None)
        if not config or not config.enabled:
            return

        if not result.success:
            return  # Don't create items for failed executions

        # Check required fields are present
        for field_name in config.required_fields:
            if field_name not in (result.data or {}):
                logger.debug(f"Skipping attention item: missing required field {field_name}")
                return

        # Check confidence threshold
        if hasattr(result, 'knowledge_attribution') and result.knowledge_attribution:
            if result.knowledge_attribution.confidence_score < config.min_confidence:
                logger.debug(f"Skipping attention item: confidence {result.knowledge_attribution.confidence_score} < {config.min_confidence}")
                return

        # Rate limiting: max items per agent per hour
        cache_key = f"mission_control_rate:{self.name}"
        current_count = cache.get(cache_key, 0)
        max_items = getattr(config, 'max_items_per_hour', 5)

        if current_count >= max_items:
            logger.debug(f"Rate limited: {self.name} has created {current_count} items this hour")
            return

        # Determine urgency
        urgency = config.default_urgency
        if config.urgency_from_field and config.urgency_from_field in (result.data or {}):
            urgency_value = result.data[config.urgency_from_field]
            if urgency_value in ['critical', 'high', 'medium', 'low']:
                urgency = urgency_value

        # Build payload from configured fields
        payload = {}
        for field_name in config.payload_fields:
            if field_name in (result.data or {}):
                payload[field_name] = result.data[field_name]

        payload['task'] = task[:200]
        payload['available_actions'] = config.actions
        payload['agent_name'] = self.name

        # Create attention item via bridge
        try:
            from core.services.human_attention_bridge import attention_bridge

            # Build title from task
            title = f"{self.name}: {task[:50]}{'...' if len(task) > 50 else ''}"

            # Build summary from result message (word-boundary truncation)
            if result.message and len(result.message) > 2000:
                summary = result.message[:2000].rsplit(' ', 1)[0] + '...'
            else:
                summary = result.message or "Agent completed with actionable output"

            attention_bridge.create_agent_output_attention(
                agent_name=self.name,
                item_type=config.item_type,
                title=title,
                summary=summary,
                urgency=urgency,
                payload=payload,
                result_data=result.data,
            )

            # Increment rate limit counter (1 hour TTL)
            cache.set(cache_key, current_count + 1, timeout=3600)

            logger.info(f"🎯 Mission Control: Created attention item for {self.name}")

        except Exception as e:
            logger.warning(f"Failed to create attention item for {self.name}: {e}")

    # ==================== Multi-Model Routing (Session 697) ====================

    def _call_llm_routed(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None,
        task_type: Optional[str] = None,
        execution_context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Session 697: Make an LLM call using the Enhanced Nervous System router.

        This method routes the request to the optimal LLM model configured for
        this agent. Different agents can use different models:
        - CodeGeneratorAgent → DeepSeek Coder (specialized coding model)
        - ContentWriterAgent → Claude (excellent creative writing)
        - ResearchAgent → GPT-5.1 (strong analysis)
        - ThinkingAgent → Claude Opus (deep reasoning)

        Falls back to _call_openai if router is unavailable.

        Args:
            prompt: The user's prompt
            system_prompt: Optional system prompt (defaults to self.system_prompt)
            conversation_history: Optional previous messages
            task_type: Optional task type for model override
            execution_context: Optional context (spider_context, scifi_context) for delegation
                              Session 744: Passed to _call_openai for delegation support

        Returns:
            Dict with 'content', 'tool_calls', 'finish_reason', 'provider', 'model'
        """
        # Session 744: Store execution context for delegation tool calls
        if execution_context:
            self._current_delegation_context = execution_context
        elif not hasattr(self, '_current_delegation_context'):
            self._current_delegation_context = {}

        # Fall back to direct OpenAI if router not available
        if not self.llm_router:
            return self._call_openai(prompt, conversation_history, execution_context)

        try:
            from core.services.llm_provider_registry import LLMRequest

            # Build messages
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({'role': 'user', 'content': prompt})

            # Create request
            request_system_prompt = system_prompt or self.system_prompt

            # Convert tools to OpenAI format if present
            tools = None
            if self.tools:
                tools = self.tools

            # Route through the nervous system
            response = self.llm_router.route_completion(
                agent_name=self.name,
                prompt=prompt,
                system_prompt=request_system_prompt,
                messages=messages,
                task_type=task_type,
                tools=tools,
                max_tokens=6000,
                user=self.user,
            )

            # Convert response to expected format
            tool_calls = []
            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_calls.append({
                        'id': tc.get('id', ''),
                        'name': tc.get('function', {}).get('name', ''),
                        'arguments': json.loads(tc.get('function', {}).get('arguments', '{}'))
                    })

            # Session 735: Accumulate cost/tokens for this execution
            call_tokens = response.tokens_total or 0
            call_cost = response.cost or 0.0
            self._accumulated_tokens += call_tokens
            self._accumulated_cost += call_cost

            return {
                'content': response.content,
                'tool_calls': tool_calls,
                'finish_reason': 'stop' if response.success else 'error',
                'provider': response.provider,
                'model': response.model,
                'tokens_used': call_tokens,
                'cost': call_cost,
                'latency_ms': response.latency_ms,
            }

        except Exception as e:
            logger.warning(f"Routed LLM call failed for {self.name}, falling back to OpenAI: {e}")
            return self._call_openai(prompt, conversation_history)

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool call. Override in subclasses for tool-specific logic.

        Session 744: Now handles delegate_to_specialist tool automatically.
        Subclasses should call super()._execute_tool_call() as a fallback
        to handle delegation, web_search, and spider_query automatically.
        Returns an error dict for unrecognized tools (never raises).

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        # Session 744: Handle delegate_to_specialist tool automatically
        if tool_name == 'delegate_to_specialist':
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )

        # Session 988: Handle web_search tool for any agent that includes it
        # Session 1090: Now the universal fallback — agents no longer define their own handlers
        if tool_name == 'web_search':
            logger.debug(f"web_search fallback handler invoked by {self.__class__.__name__}")
            try:
                from core.tools.web_search import WebSearchTool
                search_tool = WebSearchTool()
                return search_tool.execute(
                    query=arguments.get('query', ''),
                    max_results=arguments.get('num_results', 10),
                    search_type=arguments.get('search_type', 'text'),
                )
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Web search failed: {str(e)}"
                }

        # Session 1002B: Handle spider_query tool for any agent that includes it
        if tool_name == 'spider_query':
            try:
                from core.services.spider_intelligence import SpiderIntelligenceService
                service = SpiderIntelligenceService()
                query = arguments.get('query', '')
                categories = arguments.get('categories', [])
                limit = arguments.get('limit', 20)
                results = service.search_spider_data(
                    query=query,
                    category=categories[0] if len(categories) == 1 else None,
                    hours=72,
                    limit=limit
                )
                return {'success': True, 'discussions': results, 'query': query, 'count': len(results)}
            except Exception as e:
                return {'success': False, 'error': f"Spider query failed: {e}", 'discussions': []}

        # Session 1002C: Return error dict instead of raising, so subclasses
        # can safely call super()._execute_tool_call() as a fallback.
        return {
            'success': False,
            'error': f"Tool execution for '{tool_name}' not implemented in {self.name}"
        }

    def _execute_and_record_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        trace_id: str = None,
        conversation_id: str = None,
        task_summary: str = '',
    ) -> Dict[str, Any]:
        """
        Session 861: Execute a tool call and record it for audit trail.

        This wrapper around _execute_tool_call adds persistence to the
        ToolCallRecord model, providing a complete audit trail of tool usage.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            trace_id: Optional trace ID for linking
            conversation_id: Optional conversation ID
            task_summary: Optional summary of the task

        Returns:
            Tool execution result
        """
        import time
        start_time = time.time()
        result = None
        success = True
        error_message = ''
        error_type = ''

        try:
            result = self._execute_tool_call(tool_name, arguments)
            return result
        except Exception as e:
            success = False
            error_message = str(e)
            error_type = type(e).__name__
            result = {'error': error_message, 'error_type': error_type}
            raise
        finally:
            # Record the tool call regardless of success/failure
            latency_ms = int((time.time() - start_time) * 1000)
            self._record_tool_call(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                latency_ms=latency_ms,
                success=success,
                error_message=error_message,
                error_type=error_type,
                trace_id=trace_id,
                conversation_id=conversation_id,
                task_summary=task_summary,
            )

    def _record_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Any,
        latency_ms: int,
        success: bool = True,
        error_message: str = '',
        error_type: str = '',
        trace_id: str = None,
        conversation_id: str = None,
        task_summary: str = '',
    ) -> None:
        """
        Session 861: Record a tool call to the ToolCallRecord model.

        This method persists tool call data for audit trail and debugging.
        Called automatically by _execute_and_record_tool_call, but can also
        be called manually for tools executed outside the standard flow.

        Args:
            tool_name: Name of the tool called
            arguments: Dict of parameters passed to tool
            result: The tool's result
            latency_ms: Execution time in milliseconds
            success: Whether the call succeeded
            error_message: Error message if failed
            error_type: Exception class name if failed
            trace_id: Optional trace ID for linking
            conversation_id: Optional conversation ID
            task_summary: Optional summary of the task
        """
        try:
            from core.models_tool_calls import ToolCallRecord

            ToolCallRecord.record(
                agent_name=self.name,
                tool_name=tool_name,
                parameters=arguments,
                result=result,
                latency_ms=latency_ms,
                success=success,
                error_message=error_message,
                error_type=error_type,
                trace_id=trace_id,
                conversation_id=conversation_id,
                task_summary=task_summary,
            )
            logger.debug(f"📝 Session 861: Recorded tool call {self.name}.{tool_name}")
        except Exception as e:
            # Don't let recording failures break the agent
            logger.warning(f"Failed to record tool call for {self.name}.{tool_name}: {e}")

    def _record_decision(
        self,
        decision_type: str,
        action: str,
        reasoning: str = '',
        alternatives: List[str] = None,
        context: Dict[str, Any] = None,
        confidence: float = 0.8,
        trace_id: str = None,
        conversation_id: str = None,
        task_summary: str = '',
    ) -> None:
        """
        Session 861: Always-on decision recording.

        Unlike TimeTravelMixin.record_decision which only works when a
        time_travel_session is active, this method ALWAYS records decisions
        to the DecisionRecord model for audit trail and debugging.

        This addresses the MEDIUM RISK data persistence gap where ~90% of
        agent decisions were not recorded because trace_id was opt-in.

        Args:
            decision_type: Type of decision (analysis, selection, action, tool_call, etc.)
            action: The action taken
            reasoning: Why this decision was made
            alternatives: Other options that were considered
            context: Additional context data
            confidence: Confidence score (0-1)
            trace_id: Optional trace ID for linking related decisions
            conversation_id: Optional conversation ID
            task_summary: Optional summary of the task

        Example:
            self._record_decision(
                decision_type='tool_call',
                action='Calling analyze_filing for AAPL',
                reasoning='LLM requested SEC filing analysis',
                confidence=0.9
            )
        """
        try:
            from core.models_decision_records import DecisionRecord

            DecisionRecord.record(
                agent_name=self.name,
                decision_type=decision_type,
                action=action,
                reasoning=reasoning,
                alternatives=alternatives or [],
                context=context or {},
                confidence=confidence,
                trace_id=trace_id,
                conversation_id=conversation_id,
                task_summary=task_summary,
            )
            logger.debug(f"📝 Session 861: Recorded decision {self.name}.{decision_type}: {action[:50]}")
        except Exception as e:
            # Don't let recording failures break the agent
            logger.warning(f"Failed to record decision for {self.name}: {e}")

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

    # ==================== Spider Context Integration (Session 736) ====================

    def _extract_spider_intelligence(
        self,
        spider_context: Dict[str, Any],
        max_items: int = 5
    ) -> Dict[str, Any]:
        """
        Session 736: Extract and format spider intelligence for agent use.

        This helper makes it easy for any agent to utilize spider data.
        Call this at the start of execute() to get formatted intelligence.

        Args:
            spider_context: Raw spider context from AgentRouter
            max_items: Maximum items to include from each category

        Returns:
            Dict with:
                - trends: List of trending topics
                - market_data: Market/financial data if available
                - discussions: Relevant discussions/articles
                - summary: Formatted string ready for prompt injection
                - has_data: Boolean indicating if any data was found
        """
        if not spider_context:
            return {
                'trends': [],
                'market_data': None,
                'discussions': [],
                'summary': '',
                'has_data': False
            }

        # Extract trends
        trends = spider_context.get('relevant_trends', []) or spider_context.get('trends', [])
        if trends:
            trends = trends[:max_items]
            if isinstance(trends[0], dict):
                trends = [t.get('topic', t.get('title', str(t))) for t in trends]

        # Extract market data
        market_data = spider_context.get('market_data') or spider_context.get('market_analysis')

        # Extract discussions/articles
        discussions = spider_context.get('related_discussions', []) or spider_context.get('articles', [])
        if discussions:
            discussions = discussions[:max_items]

        # Extract creative trends if present
        creative = spider_context.get('creative_trends', {})

        # Build formatted summary for prompt injection
        summary_parts = []

        if trends:
            trend_text = ", ".join(str(t) for t in trends[:5])
            summary_parts.append(f"Current Trends: {trend_text}")

        if market_data:
            if isinstance(market_data, dict):
                summary_parts.append(f"Market Data: {json.dumps(market_data)[:500]}")
            else:
                summary_parts.append(f"Market Analysis Available: Yes")

        if discussions:
            disc_titles = []
            for d in discussions[:3]:
                if isinstance(d, dict):
                    title = d.get('title', d.get('headline', ''))[:100]
                    if title:
                        disc_titles.append(title)
                elif isinstance(d, str):
                    disc_titles.append(d[:100])
            if disc_titles:
                summary_parts.append(f"Related Content: {'; '.join(disc_titles)}")

        if creative:
            if creative.get('colors'):
                summary_parts.append(f"Trending Colors: {', '.join(creative['colors'][:5])}")
            if creative.get('styles'):
                summary_parts.append(f"Trending Styles: {', '.join(creative['styles'][:5])}")

        summary = "\n".join(summary_parts) if summary_parts else ""

        return {
            'trends': trends,
            'market_data': market_data,
            'discussions': discussions,
            'creative': creative,
            'summary': summary,
            'has_data': bool(summary_parts)
        }

    def _enhance_prompt_with_spider_data(
        self,
        prompt: str,
        spider_context: Dict[str, Any]
    ) -> str:
        """
        Session 736: Enhance any prompt with spider intelligence.

        Simple helper that appends spider data to an existing prompt.

        Args:
            prompt: The original prompt
            spider_context: Raw spider context from AgentRouter

        Returns:
            Enhanced prompt with spider intelligence section
        """
        intel = self._extract_spider_intelligence(spider_context)

        if not intel['has_data']:
            return prompt

        spider_section = f"""

## Real-Time Intelligence (Spider Network)
{intel['summary']}

Consider this current data when formulating your response."""

        return prompt + spider_section

    def _annotate_spider_data(
        self,
        spider_data_id: str,
        annotation_type: str,
        confidence: float = 0.7,
        note: str = ""
    ) -> bool:
        """
        Session 783: Annotate a spider data item with intelligence insight.

        Allows agents to flag interesting spider data items for the Spider News Feed.
        Annotations help humans discover valuable information from the spider network.

        Args:
            spider_data_id: UUID of the SpiderData item to annotate
            annotation_type: One of: useful, profitable, podcast_worthy, breaking_news,
                           investment_opportunity, action_required, warning, trending
            confidence: 0.0-1.0 confidence score (default: 0.7)
            note: Optional note explaining why this item is noteworthy

        Returns:
            True if annotation was created/updated, False on failure

        Example:
            # During agent execution, flag an interesting item
            spider_item_id = spider_context.get('source_item_id')
            if spider_item_id and is_profitable:
                self._annotate_spider_data(
                    spider_item_id,
                    'profitable',
                    confidence=0.85,
                    note='High ROI opportunity based on market analysis'
                )
        """
        try:
            from core.models_unified_system import SpiderData, SpiderDataAnnotation

            # Validate annotation type
            valid_types = [t[0] for t in SpiderDataAnnotation.ANNOTATION_TYPES]
            if annotation_type not in valid_types:
                logger.warning(
                    f"[{self.name}] Invalid annotation_type '{annotation_type}'. "
                    f"Must be one of: {valid_types}"
                )
                return False

            # Get the spider data item
            try:
                spider_data = SpiderData.objects.get(id=spider_data_id)
            except SpiderData.DoesNotExist:
                logger.warning(f"[{self.name}] SpiderData {spider_data_id} not found")
                return False

            # Create or update the annotation
            annotation, created = SpiderDataAnnotation.objects.update_or_create(
                spider_data=spider_data,
                agent_name=self.name,
                annotation_type=annotation_type,
                defaults={
                    'confidence_score': max(0.0, min(1.0, confidence)),
                    'note': note,
                }
            )

            action = "Created" if created else "Updated"
            logger.info(
                f"[{self.name}] {action} {annotation_type} annotation on "
                f"spider data {spider_data_id} (confidence: {confidence:.2f})"
            )

            return True

        except Exception as e:
            logger.exception(f"[{self.name}] Error annotating spider data: {e}")
            return False

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
        scifi_context_used: bool = False,
        success: bool = None
    ) -> Optional[str]:
        """
        Record execution outcome for learning, XP, and pattern detection.

        This should be called at the end of execute() to:
        1. Record the outcome for the learning loop
        2. Award XP to the agent on success
        3. Detect patterns in successful/failed interactions

        Session 768: Respects health_check_mode - skips recording for test interactions.

        Args:
            result: The AgentResult from execution
            task: The original task
            context: Execution context
            spider_data_used: Whether spider data was used
            scifi_context_used: Whether sci-fi features were used
            success: Override for result.success (optional, for backwards compatibility)

        Returns:
            Outcome ID if recorded, None otherwise
        """
        # Session 768: Skip learning in health check mode
        if getattr(self, '_health_check_mode', False):
            logger.debug(f"Skipping learning outcome recording in health_check_mode for {self.name}")
            return None

        if not self.learning_loop:
            return None

        # Session 736: Guard against None result
        if result is None:
            logger.debug("Cannot record learning outcome: result is None")
            return None

        # Use explicit success parameter if provided, otherwise use result.success
        outcome_success = success if success is not None else result.success

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type=self._detect_query_type(task),
                query_text=task,
                execution_mode='agent',
                agents_used=[self.name],
                response=result.message or '',
                execution_time_ms=result.execution_time_ms,
                success=outcome_success,
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
        importance: float = 0.5,
        safety_class: str = "candidate"
    ) -> Optional[Any]:
        """
        Session 757: Enhanced to store RICH memories with actual content.
        Session 768: Added safety_class parameter for Memory Safety Classification.

        Create a memory from a meaningful interaction, including:
        - Actual output/results from result.data
        - Execution metadata (time, tools used)
        - Structured tags for filtering
        - Content summaries and key insights

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
            safety_class: test_only, exploratory, candidate, approved (Session 768)

        Returns:
            Created AgentMemory instance or None
        """
        # Session 768: Skip memory creation in health check mode
        if getattr(self, '_health_check_mode', False):
            logger.debug(f"Skipping memory creation in health_check_mode for {self.name}")
            return None

        if not self.memory_service or not self.agent_model:
            return None

        try:
            # Determine memory type based on result
            if memory_type == "interaction":
                memory_type = "success" if result.success else "failure"

            # Session 757: Build RICH memory content from result.data
            title, content, tags = self._build_rich_memory_content(result, task, memory_type)

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
                tags=tags,
                safety_class=safety_class  # Session 768: Pass safety classification
            )

            logger.debug(f"Created rich memory: {memory.title}")
            return memory

        except Exception as e:
            logger.warning(f"Failed to create execution memory: {e}")
            return None

    def _build_rich_memory_content(
        self,
        result: 'AgentResult',
        task: str,
        memory_type: str
    ) -> tuple:
        """
        Session 757: Extract rich content from AgentResult for meaningful memories.

        Returns: (title, content, tags)
        """
        data = result.data or {}
        tags = [self.name, memory_type]

        # Extract key information based on common result.data patterns
        output_type = None
        output_title = None
        output_summary = None
        key_fields = []

        # Common patterns in result.data across agents
        # Content creation agents (ContentWriter, Image, Video, Audio, etc.)
        if 'content_type' in data:
            output_type = data['content_type']
            tags.append(output_type)

        if 'content' in data:
            content_data = data['content']
            if isinstance(content_data, dict):
                output_title = (
                    content_data.get('title') or
                    content_data.get('headline') or
                    content_data.get('subject_line') or
                    content_data.get('name')
                )
                # Get a preview of the content
                full_text = content_data.get('full_text', '')
                if full_text:
                    output_summary = full_text[:400] + "..." if len(full_text) > 400 else full_text
            elif isinstance(content_data, str) and len(content_data) > 20:
                output_summary = content_data[:400] + "..." if len(content_data) > 400 else content_data

        # Research/Analysis agents
        if 'research' in data or 'analysis' in data or 'insights' in data:
            analysis = data.get('research') or data.get('analysis') or data.get('insights')
            if isinstance(analysis, dict):
                key_fields.extend([f"{k}: {str(v)[:50]}" for k, v in list(analysis.items())[:5]])
            elif isinstance(analysis, str):
                output_summary = analysis[:400] + "..." if len(analysis) > 400 else analysis
            tags.append('analysis')

        # Scoring/Metrics
        if 'score' in data or 'scores' in data:
            scores = data.get('scores') or {'score': data.get('score')}
            if isinstance(scores, dict):
                key_fields.extend([f"{k}: {v}" for k, v in scores.items() if isinstance(v, (int, float))])
            tags.append('scoring')

        # Workflow/Pipeline agents
        if 'steps' in data or 'stages' in data or 'pipeline' in data:
            steps = data.get('steps') or data.get('stages') or data.get('pipeline', [])
            if isinstance(steps, list):
                key_fields.append(f"Steps completed: {len(steps)}")
            tags.append('workflow')

        # Metadata extraction
        metadata = data.get('metadata', {})
        if metadata:
            if 'word_count' in metadata or 'actual_word_count' in metadata:
                wc = metadata.get('actual_word_count') or metadata.get('word_count')
                key_fields.append(f"Word count: {wc}")
            if 'topic' in metadata:
                key_fields.append(f"Topic: {metadata['topic'][:50]}")
            if 'tone' in metadata:
                tags.append(metadata['tone'])
            if 'target_audience' in metadata:
                key_fields.append(f"Audience: {metadata['target_audience']}")

        # Execution time
        if result.execution_time_ms:
            key_fields.append(f"Execution: {result.execution_time_ms}ms")

        # Tool calls - Session 759: Check for both 'name' and 'tool' keys (different agents use different keys)
        if result.tool_calls:
            tools_used = [
                tc.get('name') or tc.get('tool') or tc.get('function', {}).get('name') or 'unknown'
                for tc in result.tool_calls
            ]
            key_fields.append(f"Tools: {', '.join(tools_used[:5])}")

        # Build title - prefer specific output title, fall back to task
        if output_title:
            title = f"{output_type or 'Output'}: {output_title[:50]}"
            if len(output_title) > 50:
                title += "..."
        else:
            title = f"{self.name}: {task[:50]}"
            if len(task) > 50:
                title += "..."

        # Build rich content
        content_parts = []

        # Status line - Session 759: Use result.error for failures instead of result.message
        status = "Successfully completed" if result.success else "Failed"
        if result.success:
            content_parts.append(f"{status}: {result.message or task[:100]}")
        else:
            error_msg = result.error or result.message or "Unknown error"
            content_parts.append(f"{status}: {task[:100]}")
            content_parts.append(f"\nError: {error_msg}")

        # Output type and title
        if output_type and output_title:
            content_parts.append(f"\nCreated {output_type}: \"{output_title}\"")

        # Key fields/metrics
        if key_fields:
            content_parts.append("\n" + "\n".join(key_fields))

        # Output summary/preview
        if output_summary:
            content_parts.append(f"\nOutput preview:\n{output_summary}")

        # Fallback to result.data summary if nothing else
        if not output_summary and not key_fields and data:
            # Show first few key-value pairs from data
            data_preview = []
            for k, v in list(data.items())[:5]:
                if isinstance(v, (str, int, float, bool)):
                    data_preview.append(f"{k}: {str(v)[:100]}")
                elif isinstance(v, dict):
                    data_preview.append(f"{k}: {{{len(v)} fields}}")
                elif isinstance(v, list):
                    data_preview.append(f"{k}: [{len(v)} items]")
            if data_preview:
                content_parts.append("\nResult data:\n" + "\n".join(data_preview))

        content = "\n".join(content_parts)

        # Ensure we have meaningful content, not just "Successfully created X"
        if len(content) < 50 and result.message:
            content = f"{result.message}\n\nTask: {task}"

        return title, content, list(set(tags))  # Dedupe tags

    def _save_to_deliverable(
        self,
        title: str,
        content: str,
        deliverable_type: str = 'document',
        category: str = '',
        tags: List[str] = None,
        content_format: str = 'markdown',
        metadata: Dict[str, Any] = None,
        user=None,
        trace_id: str = None,
        quality_score: float = 0.7,
        confidence_score: float = 0.7,
        origin: str = '',
        provenance: Dict[str, Any] = None,
    ) -> Optional[Any]:
        """
        Session 861: Save agent output to Deliverable model for persistence.

        All content-creating agents should call this to ensure their output
        is not lost after the request completes. AgentResult is ephemeral
        and AgentMemory only stores summaries - this method persists the
        full content.

        Args:
            title: Human-readable title for the deliverable
            content: The full content to persist
            deliverable_type: One of: document, image, video, audio, code,
                             analysis, report, template, research, strategy,
                             plan, script
            category: Business category (Content, Finance, Legal, etc.)
            tags: List of tags for filtering
            content_format: text, markdown, html, json, python, etc.
            metadata: Additional metadata dict
            user: User who owns this (optional)
            trace_id: UUID for cross-artifact linking (optional)
            quality_score: AI-assessed quality (0.0-1.0)
            confidence_score: Agent confidence (0.0-1.0)

        Returns:
            Created Deliverable instance or None if creation failed

        Example:
            self._save_to_deliverable(
                title="Market Analysis: AAPL Q4 2026",
                content=analysis_text,
                deliverable_type='analysis',
                category='Finance',
                tags=['stocks', 'AAPL', 'quarterly'],
                metadata={'symbol': 'AAPL', 'period': 'Q4 2026'}
            )
        """
        try:
            from core.models_deliverables import Deliverable
            from core.services.data_scrubber import guard_persistence
            from django.utils.text import slugify
            from django.utils import timezone as tz
            from datetime import timedelta
            import uuid

            # Phase 3: Run content through persistence guard (scrub + provenance)
            guard_result = guard_persistence(
                content=content,
                origin=origin,
                provenance=provenance,
                metadata=metadata,
            )
            content = guard_result['scrubbed_content']
            metadata = guard_result['metadata']

            resolved_title = title or f"{self.name} Output"

            # Session 1022: Dedup — if same agent produced same title in last 4h, update it
            dedup_window = tz.now() - timedelta(hours=4)
            existing = Deliverable.objects.filter(
                title=resolved_title,
                agent_name=self.name,
                created_at__gte=dedup_window,
            ).order_by('-created_at').first()

            if existing:
                # Update content in-place instead of creating a duplicate
                preview = content[:500] if content else ''
                if len(content or '') > 500:
                    preview += '...'
                existing.content = content or ''
                existing.preview_content = preview
                existing.metadata = metadata or {}
                existing.quality_score = quality_score
                existing.confidence_score = confidence_score
                existing.agent_task = getattr(self, '_current_task', '')[:1000] if hasattr(self, '_current_task') else ''
                existing.save(update_fields=['content', 'preview_content', 'metadata', 'quality_score', 'confidence_score', 'agent_task', 'updated_at'])
                logger.info(f"📦 Session 1022: Updated existing Deliverable {existing.id} (dedup) - {resolved_title[:50]}")
                return existing

            # Generate unique slug
            base_slug = slugify(resolved_title[:100]) if resolved_title else 'untitled'
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

            # Determine category if not provided
            if not category:
                category = self._get_deliverable_category()

            # Build preview content
            preview = content[:500] if content else ''
            if len(content or '') > 500:
                preview += '...'

            # Session 1075: Fall back to self.user so agent-created deliverables
            # are owned by the real user (not NULL / system_autonomous).
            resolved_user = user or getattr(self, 'user', None)

            deliverable = Deliverable.objects.create(
                title=resolved_title,
                slug=unique_slug,
                deliverable_type=deliverable_type,
                category=category,
                tags=tags or [],
                agent_name=self.name,
                agent_task=getattr(self, '_current_task', '')[:1000] if hasattr(self, '_current_task') else '',
                content=content or '',
                content_format=content_format,
                preview_content=preview,
                metadata=metadata or {},
                user=resolved_user,
                trace_id=uuid.UUID(trace_id) if trace_id else None,
                quality_score=quality_score,
                confidence_score=confidence_score,
                status='ready',
            )

            logger.info(f"📦 Session 861: Saved Deliverable {deliverable.id} - {resolved_title[:50]}")

            # Session 930: Trigger auto-learning from deliverable
            self._trigger_deliverable_learning(deliverable, user)

            return deliverable

        except Exception as e:
            logger.warning(f"Failed to save Deliverable for {self.name}: {e}")
            return None

    def _trigger_deliverable_learning(self, deliverable, user) -> None:
        """
        Session 930: Trigger learning services after deliverable creation.
        """
        if not user:
            return

        try:
            from core.services.skill_evolution_service import get_skill_evolution_service
            skill_service = get_skill_evolution_service()
            base_quality = float(deliverable.quality_score) if deliverable.quality_score else 0.7
            skill_service.update_skills_from_deliverable(user, deliverable, base_quality)
        except Exception as e:
            logger.debug(f"Skill evolution trigger failed: {e}")

        try:
            from core.services.goal_tracking_service import get_goal_tracking_service
            goal_service = get_goal_tracking_service()
            goal_service.auto_link_deliverable(deliverable)
        except Exception as e:
            logger.debug(f"Goal tracking trigger failed: {e}")

    def _get_deliverable_category(self) -> str:
        """
        Session 861: Map agent name to a Deliverable category.

        Returns a category string based on agent name patterns.
        """
        category_map = {
            'ContentWriter': 'Content',
            'Technical': 'Development',
            'Stock': 'Finance',
            'Bull': 'Finance',
            'Bear': 'Finance',
            'Market': 'Finance',
            'Opportunity': 'Finance',
            'Signal': 'Finance',
            'Institutional': 'Finance',
            'Legal': 'Legal',
            'Code': 'Development',
            'FullStack': 'Development',
            'DevOps': 'Development',
            'Research': 'Research',
            'Customer': 'Research',
            'Trend': 'Analysis',
            'Competitor': 'Business',
            'Brand': 'Marketing',
            'SEO': 'Marketing',
            'Social': 'Marketing',
            'Content Strategy': 'Marketing',
            'Marketing': 'Marketing',
            'Podcast': 'Content',
            'Debate': 'Content',
            'Moderator': 'Content',
            'Smart': 'Blockchain',
            'Whale': 'Blockchain',
            'Exploit': 'Blockchain',
            'Transaction': 'Blockchain',
            'Blockchain': 'Blockchain',
            'Narrative': 'Analysis',
            'Cultural': 'Analysis',
            'Bookmaker': 'Betting',
            'Sports': 'Betting',
            'Prediction': 'Betting',
            'Arbitrage': 'Betting',
            'CTO': 'Executive',
            'COO': 'Executive',
            'Creative': 'Executive',
            'Meeting': 'Executive',
            'Platform': 'Operations',
            'System': 'Operations',
            'Thinking': 'Analysis',
        }
        for prefix, category in category_map.items():
            if prefix in self.name:
                return category
        return 'General'

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

        Session 754: Fixed to use correct model and fields.
        - Uses AgentContribution from core.models.agents_registry
        - Looks up UnifiedAgentTemplate by agent name
        - Links to actual ImageHistory/VideoHistory objects
        - Uses correct contribution_type choices

        Args:
            content_type: Type of content (image, video, audio, research)
            content_id: ID of the content record
            contribution_type: primary_creator, assistant, reviewer, optimizer
            contribution_score: 0-1 contribution percentage (maps to contribution_percentage)

        Returns:
            Created AgentContribution instance or None
        """
        try:
            from core.models.agents_registry import AgentContribution, UnifiedAgentTemplate
            from content.models import ImageHistory, VideoHistory

            # Get or create the UnifiedAgentTemplate for this agent
            agent_template, _ = UnifiedAgentTemplate.objects.get_or_create(
                name=self.name,
                defaults={
                    'display_name': self.name.replace('Agent', ' Agent'),
                    'description': self.system_prompt[:500] if self.system_prompt else f'{self.name} agent',
                    'specialization': 'content',
                    'system_prompt': self.system_prompt or '',
                }
            )

            # Map contribution_type to valid choices
            # Valid choices: generation, editing, orchestration, analysis, recommendation, iteration
            type_mapping = {
                'primary_creator': 'generation',
                'creator': 'generation',
                'generator': 'generation',
                'editor': 'editing',
                'assistant': 'editing',
                'reviewer': 'analysis',
                'optimizer': 'iteration',
                'orchestrator': 'orchestration',
            }
            mapped_type = type_mapping.get(contribution_type, 'generation')

            # Map contribution_type to role
            role_mapping = {
                'primary_creator': 'Primary Creator',
                'creator': 'Creator',
                'generator': 'Generator',
                'editor': 'Editor',
                'assistant': 'Assistant',
                'reviewer': 'Reviewer',
                'optimizer': 'Optimizer',
                'orchestrator': 'Orchestrator',
            }
            contribution_role = role_mapping.get(contribution_type, 'Contributor')

            # Convert score (0-1) to percentage (0-100)
            contribution_percentage = int(contribution_score * 100)

            # Build contribution kwargs
            contribution_kwargs = {
                'agent': agent_template,
                'contribution_type': mapped_type,
                'contribution_role': contribution_role,
                'contribution_percentage': contribution_percentage,
                'task_description': f'{self.name} {mapped_type} of {content_type}',
            }

            # Link to the actual content object
            if content_type == 'image' and content_id:
                try:
                    image = ImageHistory.objects.get(id=content_id)
                    contribution_kwargs['image'] = image
                    if image.project:
                        contribution_kwargs['project'] = image.project
                except ImageHistory.DoesNotExist:
                    logger.debug(f"ImageHistory {content_id} not found, creating contribution without image link")

            elif content_type == 'video' and content_id:
                try:
                    video = VideoHistory.objects.get(id=content_id)
                    contribution_kwargs['video'] = video
                    if video.project:
                        contribution_kwargs['project'] = video.project
                except VideoHistory.DoesNotExist:
                    logger.debug(f"VideoHistory {content_id} not found, creating contribution without video link")

            # Create the contribution
            contribution = AgentContribution.objects.create(**contribution_kwargs)

            logger.info(f"✓ Tracked contribution: {self.name} -> {content_type}:{content_id} ({mapped_type})")
            return contribution

        except Exception as e:
            logger.warning(f"Failed to track contribution: {e}", exc_info=True)
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

    # =========================================================================
    # SESSION 695: SKIN LAYER INTEGRATION - Workspace file writing for all agents
    # =========================================================================

    def _get_workspace_manager(self, user=None):
        """
        Session 695: Get WorkspaceManager for file operations.
        Session 855: Added system user fallback for autonomous operations.

        The SKIN layer enables agents to write generated code to real project
        workspaces with full audit trail and rollback capability.

        Args:
            user: User for workspace lookup (defaults to self.user)

        Returns:
            WorkspaceManager instance or None if unavailable
        """
        target_user = user or self.user

        # Session 855: Fall back to system user for autonomous operations (Celery tasks)
        if not target_user:
            target_user = self._get_system_user()
            if target_user:
                logger.debug(f"🤖 Using system_autonomous user for workspace operations")

        if not target_user:
            return None

        try:
            from core.services.workspace_manager import WorkspaceManager
            return WorkspaceManager(user=target_user)
        except Exception as e:
            logger.warning(f"Could not initialize WorkspaceManager: {e}")
            return None

    def _get_system_user(self):
        """
        Session 855: Get or create system user for autonomous operations.

        When agents execute autonomously (via Celery tasks), there's no
        authenticated user. This provides a system user so workspace
        operations can still be tracked properly.

        Returns:
            User: The system user for autonomous operations, or None if failed
        """
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            system_user, created = User.objects.get_or_create(
                username='system_autonomous',
                defaults={
                    'email': 'system@autonomous.internal',
                    'is_active': True,
                    'first_name': 'System',
                    'last_name': 'Autonomous',
                }
            )

            if created:
                logger.info("🤖 Created system_autonomous user for autonomous operations")

            return system_user
        except Exception as e:
            logger.warning(f"Could not get system user: {e}")
            return None

    def _write_files_to_workspace(
        self,
        files: List[Dict[str, str]],
        user=None,
        base_path: str = ""
    ) -> Dict[str, Any]:
        """
        Session 695: Write generated files to the active workspace.

        This is the core SKIN layer method that enables agents to write
        real files to project directories with full audit trail.

        Args:
            files: List of {filename, language, content} dicts
            user: User for workspace lookup (defaults to self.user)
            base_path: Optional base path prefix for all files

        Returns:
            Dict with written files, operations, and any errors
        """
        target_user = user or self.user
        manager = self._get_workspace_manager(target_user)

        if not manager:
            artifacts = self._capture_files_as_artifacts(files, base_path)
            return {
                'written': False,
                'reason': 'WorkspaceManager not available',
                'files_generated': len(files),
                'artifacts_captured': len(artifacts),
                'artifact_ids': [str(a.id) for a in artifacts],
            }

        workspace = manager.get_active_workspace()
        if not workspace:
            artifacts = self._capture_files_as_artifacts(files, base_path)
            return {
                'written': False,
                'reason': 'No active workspace. Register a workspace first.',
                'files_generated': len(files),
                'artifacts_captured': len(artifacts),
                'artifact_ids': [str(a.id) for a in artifacts],
            }

        # Check permissions
        if not workspace.allow_file_write:
            artifacts = self._capture_files_as_artifacts(files, base_path)
            return {
                'written': False,
                'reason': 'Workspace does not allow file writes',
                'workspace': workspace.name,
                'files_generated': len(files),
                'artifacts_captured': len(artifacts),
                'artifact_ids': [str(a.id) for a in artifacts],
            }

        written_files = []
        failed_files = []
        operations = []

        for file_info in files:
            filename = file_info.get('filename', '')
            content = file_info.get('content', '')

            # Construct full path
            if base_path:
                file_path = f"{base_path}/{filename}".lstrip('/')
            else:
                file_path = filename.lstrip('/')

            # Skip empty filenames
            if not file_path:
                continue

            try:
                # Write file using WorkspaceManager
                operation = manager.write_file(
                    workspace=workspace,
                    file_path=file_path,
                    content=content,
                    agent_name=self.name
                )

                if operation.success:
                    written_files.append({
                        'path': file_path,
                        'operation_id': str(operation.id),
                        'size': len(content)
                    })
                    operations.append(str(operation.id))
                else:
                    failed_files.append({
                        'path': file_path,
                        'error': operation.error_message
                    })

            except Exception as e:
                logger.error(f"Failed to write {file_path}: {e}")
                failed_files.append({
                    'path': file_path,
                    'error': str(e)
                })

        # Capture failed files as artifacts so content isn't lost
        if failed_files:
            for file_info in files:
                filename = file_info.get('filename', '')
                content = file_info.get('content', '')
                if base_path:
                    fp = f"{base_path}/{filename}".lstrip('/')
                else:
                    fp = filename.lstrip('/')
                if any(f['path'] == fp for f in failed_files):
                    self._capture_single_file_artifact(fp, content)

        return {
            'written': len(written_files) > 0,
            'workspace': workspace.name,
            'workspace_path': workspace.root_path,
            'files_written': written_files,
            'files_failed': failed_files,
            'operations': operations,
            'total_written': len(written_files),
            'total_failed': len(failed_files)
        }

    def _capture_files_as_artifacts(
        self,
        files: List[Dict[str, str]],
        base_path: str = ""
    ) -> list:
        """Session 1012: Capture all files as CodeArtifacts when workspace is unavailable."""
        artifacts = []
        for file_info in files:
            filename = file_info.get('filename', '')
            content = file_info.get('content', '')
            if not filename or not content:
                continue
            if base_path:
                target_path = f"{base_path}/{filename}".lstrip('/')
            else:
                target_path = filename.lstrip('/')
            artifact = self._capture_single_file_artifact(target_path, content)
            if artifact:
                artifacts.append(artifact)
        return artifacts

    def _capture_single_file_artifact(self, target_path: str, content: str):
        """Session 1012: Capture a single file as a CodeArtifact."""
        try:
            from core.models_code_artifacts import CodeArtifact
            artifact = CodeArtifact.objects.create(
                agent_name=self.name,
                trace_id=getattr(self, '_current_trace_id', ''),
                kind='file_create',
                target_path=target_path,
                content=content,
                description=f"Generated by {self.name} (workspace write failed)",
            )
            logger.info(f"Captured CodeArtifact {artifact.id} for {target_path}")
            return artifact
        except Exception as e:
            logger.error(f"Failed to capture CodeArtifact for {target_path}: {e}")
            return None

    def _parse_code_files(self, content: str) -> List[Dict[str, str]]:
        """
        Session 695: Parse generated content into individual files.

        Extracts files from LLM output that uses the format:
        ### path/to/file.ext
        ```language
        content
        ```

        Args:
            content: Raw LLM output containing file definitions

        Returns:
            List of {filename, language, content} dicts
        """
        import re

        files = []
        pattern = r'###\s+([^\n]+)\n```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        for filename, language, code in matches:
            files.append({
                "filename": filename.strip(),
                "language": language or "text",
                "content": code.strip()
            })

        return files

    def execute_with_workspace(
        self,
        task: str,
        context: Dict[str, Any],
        user=None,
        write_to_workspace: bool = True,
        base_path: str = ""
    ) -> 'AgentResult':
        """
        Session 695: Execute agent task and optionally write output to workspace.

        This is the SKIN-layer-aware wrapper around execute() that:
        1. Runs the standard agent execution
        2. Extracts any generated files from the result
        3. Writes them to the active workspace
        4. Returns result with workspace write info

        Args:
            task: The task description
            context: Additional context
            user: User for workspace (defaults to self.user)
            write_to_workspace: Whether to write files to workspace
            base_path: Base path within workspace for files

        Returns:
            AgentResult with workspace_write info in data
        """
        target_user = user or self.user

        # Execute standard agent logic
        result = self.execute(
            task=task,
            context=context,
            scifi_context=context.get('scifi_context', {}),
            spider_context=context.get('spider_context', {})
        )

        # If generation failed or no workspace write, return as-is
        if not result.success or not write_to_workspace:
            return result

        # Extract files from result
        files_to_write = []

        # Session 1028: Guard against result.data being a string (causes
        # "'str' object has no attribute 'get'" — 9 failures on 2026-02-17)
        if result.data and isinstance(result.data, dict):
            # Check for files in the results (from tool calls)
            results = result.data.get('results', [])
            for r in results:
                if not isinstance(r, dict):
                    continue
                data = r.get('data', {})
                if isinstance(data, dict) and 'files' in data:
                    files_to_write.extend(data['files'])

            # Try to parse from raw code if no files found
            if not files_to_write:
                for r in results:
                    if not isinstance(r, dict):
                        continue
                    data = r.get('data', {})
                    if isinstance(data, dict) and 'code' in data:
                        parsed = self._parse_code_files(data['code'])
                        files_to_write.extend(parsed)

        # Also try parsing from message if it contains code blocks
        if not files_to_write and result.message:
            parsed = self._parse_code_files(result.message)
            files_to_write.extend(parsed)

        # Session 943: If still no files, check for report-style content
        # Financial agents produce structured_report or long messages that should be saved
        if not files_to_write and result.data and isinstance(result.data, dict):
            from django.utils import timezone

            # Check for structured_report field (used by stock/market agents)
            structured_report = result.data.get('structured_report')
            if structured_report and len(str(structured_report)) > 200:
                # Generate a filename based on agent name and task
                agent_name = self.__class__.__name__.replace('Agent', '').lower()
                timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M')
                filename = f"{agent_name}_report_{timestamp}.md"

                # Determine category from agent name
                category_map = {
                    'stock': 'financial/stocks',
                    'bull': 'financial/bull_cases',
                    'bear': 'financial/bear_cases',
                    'market': 'financial/market_analysis',
                    'crypto': 'blockchain/analysis',
                    'prediction': 'predictions',
                    'trend': 'analysis/trends',
                    'research': 'research',
                }
                category = 'reports'  # Default
                for key, path in category_map.items():
                    if key in agent_name.lower():
                        category = path
                        break

                files_to_write.append({
                    'filename': f"{category}/{filename}",
                    'content': str(structured_report),
                    'language': 'markdown'
                })
                logger.info(f"📊 [Session 943] Created report file from structured_report: {category}/{filename}")

            # Also check for substantial message content (analysis results)
            # Session 943 fix: Expanded detection - check for any report-like content, not just ## headers
            # Reports often use **bold**, ---, bullet points, or section markers
            elif result.message and len(result.message) > 500:
                # Check if it looks like formatted content (not just plain text)
                has_formatting = any(marker in result.message for marker in [
                    '##', '**', '---', '•', '- ', '1)', '1.', ':',
                ])
                # Save if it has formatting OR is from a known report-producing agent
                report_agents = {'stock', 'bull', 'bear', 'market', 'analyst', 'research', 'prediction', 'crypto', 'trend'}
                agent_name_lower = self.__class__.__name__.lower()
                is_report_agent = any(name in agent_name_lower for name in report_agents)

                if has_formatting or is_report_agent:
                    # Looks like a report - save it
                    agent_name = self.__class__.__name__.replace('Agent', '').lower()
                    timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M')
                    filename = f"{agent_name}_analysis_{timestamp}.md"

                    category_map = {
                        'stock': 'financial/stocks',
                        'bull': 'financial/bull_cases',
                        'bear': 'financial/bear_cases',
                        'market': 'financial/market_analysis',
                        'crypto': 'blockchain/analysis',
                        'prediction': 'predictions',
                        'trend': 'analysis/trends',
                        'research': 'research',
                    }
                    category = 'reports'
                    for key, path in category_map.items():
                        if key in agent_name.lower():
                            category = path
                            break

                    files_to_write.append({
                        'filename': f"{category}/{filename}",
                        'content': result.message,
                        'language': 'markdown'
                    })
                    logger.info(f"📊 [Session 943] Created report file from message: {category}/{filename}")

        # Write files to workspace
        if files_to_write:
            write_result = self._write_files_to_workspace(
                files=files_to_write,
                user=target_user,
                base_path=base_path
            )

            # Add workspace write info to result data
            # Session 1028: Ensure result.data is a dict before subscript assignment
            if not isinstance(result.data, dict):
                result.data = {}

            result.data['workspace_write'] = write_result

            # Update message to include write status
            if write_result.get('written'):
                result.message = (
                    f"{result.message}\n\n"
                    f"📁 Wrote {write_result['total_written']} files to workspace '{write_result['workspace']}'"
                )
                if write_result.get('total_failed', 0) > 0:
                    result.message += f" ({write_result['total_failed']} failed)"

        return result

    # =========================================================================
    # Documentation Tools (Session 798)
    # =========================================================================
    # These methods allow agents to read, write, and maintain the /docs/ system.
    # Agents can create session handoffs, update documentation, and regenerate
    # the docs index to keep the system's knowledge base current.

    def _read_doc(self, doc_path: str) -> Dict[str, Any]:
        """
        Session 798: Read a documentation file from the docs directory.

        Args:
            doc_path: Path relative to project root (e.g., 'docs/ARCHITECTURE.md')

        Returns:
            Dict with 'success', 'content', and 'metadata'
        """
        from pathlib import Path
        from django.conf import settings

        try:
            full_path = Path(settings.BASE_DIR) / doc_path

            if not full_path.exists():
                return {
                    'success': False,
                    'error': f"Document not found: {doc_path}",
                    'content': None,
                }

            # Security check: ensure path is within docs directory
            docs_root = Path(settings.BASE_DIR) / 'docs'
            if not str(full_path.resolve()).startswith(str(docs_root.resolve())):
                # Allow CLAUDE.md and 00-START-NEXT-SESSION.md at root
                allowed_root_files = ['CLAUDE.md', '00-START-NEXT-SESSION.md']
                if full_path.name not in allowed_root_files:
                    return {
                        'success': False,
                        'error': f"Access denied: {doc_path} is outside docs directory",
                        'content': None,
                    }

            content = full_path.read_text(encoding='utf-8')

            logger.info(f"📖 [Session 798] {self.name} read doc: {doc_path}")

            # Session 960 Phase 0: Track internal doc reads for provenance
            import hashlib
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            # Deduplicate by path + hash
            already_tracked = any(
                d.get('path') == doc_path and d.get('content_hash') == content_hash
                for d in self._docs_consumed
            )
            if not already_tracked:
                self._docs_consumed.append({
                    'name': doc_path,
                    'source_type': 'internal_doc',
                    'content_hash': content_hash,
                    'record_count': content.count('\n') + 1,
                    'freshness_hours': 0.0,
                })

            return {
                'success': True,
                'content': content,
                'path': doc_path,
                'size': len(content),
                'lines': content.count('\n') + 1,
            }

        except Exception as e:
            logger.error(f"📖 [Session 798] {self.name} failed to read doc {doc_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': None,
            }

    def _write_doc(self, doc_path: str, content: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        Session 798: Write or update a documentation file.

        Args:
            doc_path: Path relative to project root (e.g., 'docs/handoffs/SESSION_798_EXAMPLE.md')
            content: The markdown content to write
            create_backup: If True, backup existing file before overwriting

        Returns:
            Dict with 'success', 'path', and operation details
        """
        from pathlib import Path
        from datetime import datetime
        from django.conf import settings

        try:
            full_path = Path(settings.BASE_DIR) / doc_path

            # Security check: only allow writing to docs/ directory
            docs_root = Path(settings.BASE_DIR) / 'docs'
            if not str(full_path.resolve()).startswith(str(docs_root.resolve())):
                # Allow updating 00-START-NEXT-SESSION.md at root
                if full_path.name != '00-START-NEXT-SESSION.md':
                    return {
                        'success': False,
                        'error': f"Access denied: Can only write to docs/ directory",
                        'path': doc_path,
                    }

            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Backup existing file if requested
            backup_path = None
            if create_backup and full_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = full_path.with_suffix(f'.backup_{timestamp}.md')
                backup_path.write_text(full_path.read_text(encoding='utf-8'), encoding='utf-8')

            # Session 962 Phase 1: Create DocVersion before overwriting
            if full_path.exists():
                try:
                    import hashlib
                    from core.models_deliberation import DocVersion
                    existing_content = full_path.read_text(encoding='utf-8')
                    new_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                    old_hash = hashlib.sha256(existing_content.encode('utf-8')).hexdigest()
                    if new_hash != old_hash:
                        # Normalize path relative to repo root
                        rel_path = str(full_path.resolve().relative_to(Path(settings.BASE_DIR).resolve()))
                        last_version = DocVersion.objects.filter(
                            doc_path=rel_path
                        ).order_by('-version_number').values_list('version_number', flat=True).first()
                        next_version = (last_version or 0) + 1
                        DocVersion.objects.create(
                            doc_path=rel_path,
                            version_number=next_version,
                            content_hash=old_hash,
                            content_snapshot=existing_content,
                            author_agent=getattr(self, 'name', ''),
                            change_reason=f"Overwritten by {getattr(self, 'name', 'unknown')}",
                        )
                        logger.info(f"📋 [Session 962] DocVersion v{next_version} saved for {rel_path}")
                except Exception as e:
                    logger.warning(f"[Session 962] DocVersion creation failed: {e}")

            # Write the new content
            full_path.write_text(content, encoding='utf-8')

            logger.info(f"📝 [Session 798] {self.name} wrote doc: {doc_path}")

            return {
                'success': True,
                'path': doc_path,
                'size': len(content),
                'lines': content.count('\n') + 1,
                'backup_created': backup_path is not None,
                'backup_path': str(backup_path) if backup_path else None,
            }

        except Exception as e:
            logger.error(f"📝 [Session 798] {self.name} failed to write doc {doc_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'path': doc_path,
            }

    def _create_session_handoff(
        self,
        session_num: int,
        title: str,
        content: str,
        update_start_file: bool = True
    ) -> Dict[str, Any]:
        """
        Session 798: Create a session handoff document.

        This is a convenience method for creating standardized session handoff files.

        Args:
            session_num: The session number (e.g., 798)
            title: Short title for the session (e.g., "Docs Integration")
            content: The markdown content for the handoff
            update_start_file: If True, also update 00-START-NEXT-SESSION.md

        Returns:
            Dict with 'success' and created file paths
        """
        from datetime import datetime

        try:
            # Create handoff filename
            safe_title = title.upper().replace(' ', '_').replace('-', '_')
            filename = f"SESSION_{session_num}_{safe_title}.md"
            doc_path = f"docs/handoffs/{filename}"

            # Add standard header if not present
            if not content.startswith('# Session'):
                header = f"""# Session {session_num} - {title}

**Date:** {datetime.now().strftime('%B %d, %Y')}
**Focus:** {title}
**Status:** IN PROGRESS

---

"""
                content = header + content

            # Write the handoff document
            write_result = self._write_doc(doc_path, content, create_backup=False)

            if not write_result['success']:
                return write_result

            result = {
                'success': True,
                'handoff_path': doc_path,
                'session': session_num,
                'title': title,
            }

            # Optionally update the start file
            if update_start_file:
                start_update = self._update_start_next_session(session_num, title)
                result['start_file_updated'] = start_update.get('success', False)

            logger.info(f"📋 [Session 798] {self.name} created handoff: {doc_path}")

            return result

        except Exception as e:
            logger.error(f"📋 [Session 798] {self.name} failed to create handoff: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def _update_start_next_session(self, session_num: int, focus: str) -> Dict[str, Any]:
        """
        Session 798: Update 00-START-NEXT-SESSION.md with current session info.

        Args:
            session_num: Current session number
            focus: Short description of session focus

        Returns:
            Dict with 'success' and update details
        """
        from datetime import datetime
        from pathlib import Path
        from django.conf import settings

        try:
            start_file = Path(settings.BASE_DIR) / '00-START-NEXT-SESSION.md'

            if not start_file.exists():
                return {
                    'success': False,
                    'error': '00-START-NEXT-SESSION.md not found',
                }

            content = start_file.read_text(encoding='utf-8')

            # Update the session number in the header
            import re

            # Update "# Session XXX" pattern
            content = re.sub(
                r'# Session \d+',
                f'# Session {session_num}',
                content,
                count=1
            )

            # Update date if present
            today = datetime.now().strftime('%B %d, %Y')
            content = re.sub(
                r'\*\*Date:\*\* .+',
                f'**Date:** {today}',
                content,
                count=1
            )

            start_file.write_text(content, encoding='utf-8')

            logger.info(f"📄 [Session 798] Updated 00-START-NEXT-SESSION.md for Session {session_num}")

            return {
                'success': True,
                'session': session_num,
                'focus': focus,
            }

        except Exception as e:
            logger.error(f"📄 [Session 798] Failed to update start file: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def _regenerate_docs_index(self) -> Dict[str, Any]:
        """
        Session 798: Regenerate the docs index by running the build_docs_index command.

        This should be called after creating or modifying documentation to keep
        the index current.

        Returns:
            Dict with 'success' and command output
        """
        try:
            # Session 1012: Use call_command instead of subprocess with hardcoded .venv path
            from io import StringIO
            from django.core.management import call_command

            stdout = StringIO()
            stderr = StringIO()
            call_command('build_docs_index', stdout=stdout, stderr=stderr)

            logger.info(f"🔄 [Session 798] {self.name} regenerated docs index")
            return {
                'success': True,
                'stdout': stdout.getvalue(),
                'stderr': stderr.getvalue(),
                'return_code': 0,
            }

        except Exception as e:
            logger.error(f"🔄 [Session 798] Failed to regenerate docs index: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def _get_docs_for_task(self, task: str, max_docs: int = 5) -> Dict[str, Any]:
        """
        Session 798: Get relevant documentation for the current task.

        This method uses the DocsContextBuilder to find relevant docs
        based on the agent's type and the task at hand.

        Args:
            task: Description of the current task
            max_docs: Maximum number of docs to return

        Returns:
            Dict with relevant documentation context
        """
        try:
            from core.services.docs_context_builder import get_docs_context_builder

            builder = get_docs_context_builder()
            context = builder.build_context_for_agent(
                agent_name=self.name,
                task=task,
                max_docs=max_docs,
                include_recent_sessions=True,
                include_content_snippets=True,
            )

            logger.debug(f"📚 [Session 798] {self.name} retrieved {len(context.get('relevant_docs', []))} docs for task")

            return context

        except Exception as e:
            logger.warning(f"📚 [Session 798] {self.name} failed to get docs context: {e}")
            return {
                'has_docs': False,
                'relevant_docs': [],
                'recent_sessions': [],
                'summary': f'Documentation context unavailable: {str(e)}',
            }


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

    def update(self, message: str, percentage: int) -> None:
        """No-op progress update."""


# Import models at module level for F expression
try:
    pass
except ImportError:
    pass
