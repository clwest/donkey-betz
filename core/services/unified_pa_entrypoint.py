"""
Unified PA Entrypoint - Single Front Door for All PA Requests
==============================================================

Session 931: Created to solve the fragmented PA architecture problem.

This is the ONLY class that UI should hit. It:
1. Builds context (profile + last N turns + system vitals when relevant)
2. Routes to appropriate agent/tool via semantic + keyword routing
3. Executes via ToolDispatcher (no silent failures)
4. Logs outcome + errors in one place
5. Returns structured response with trace_id

Usage:
    from core.services.unified_pa_entrypoint import get_unified_pa

    pa = get_unified_pa(user)
    response = await pa.process_message("What are my pending decisions?")

    # Response is always structured:
    # {
    #     "content": "You have 5 pending decisions...",
    #     "trace_id": "pa-123-abc",
    #     "tool_runs": [{"tool": "human_decisions_tool", "ok": True, "latency_ms": 234}],
    #     "audio_url": None,  # Optional TTS
    #     "intent": "decision_management",
    #     "routed_to": "human_decisions_tool"
    # }
"""

import json
import logging
import re
import time
import uuid
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime

from django.contrib.auth import get_user_model
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()

# Deterministic memory intent detection patterns (Task D)
_MEMORY_PATTERNS = [
    re.compile(r'(?:please\s+)?remember\s+(?:that\s+)?(.{10,200})', re.IGNORECASE),
    re.compile(r'(?:please\s+)?(?:always|never)\s+(.{5,200})', re.IGNORECASE),
    re.compile(r'(?:save|note|pin)\s+(?:that|this)[\s:]+(.{10,200})', re.IGNORECASE),
    re.compile(r'keep\s+in\s+mind\s+(?:that\s+)?(.{10,200})', re.IGNORECASE),
    re.compile(r'(?:from now on|going forward)[,\s]+(.{10,200})', re.IGNORECASE),
    re.compile(r'i\s+prefer\s+(.{5,200})', re.IGNORECASE),
]


def _detect_memory_intent(message: str) -> str | None:
    """Return captured memory content if message contains an explicit memory intent."""
    for pattern in _MEMORY_PATTERNS:
        m = pattern.search(message)
        if m:
            return m.group(1).strip().rstrip('.')
    return None


@dataclass
class PAResponse:
    """Structured response from PA."""
    content: str
    trace_id: str
    tool_runs: List[Dict[str, Any]] = field(default_factory=list)
    audio_url: Optional[str] = None
    intent: Optional[str] = None
    routed_to: Optional[str] = None
    profile_completeness: Optional[int] = None
    latency_ms: int = 0
    error: Optional[str] = None
    # Session 1036: Function calling metadata
    tool_call_metadata: Optional[List[Dict]] = None
    tool_result_data: Optional[List[Dict]] = None
    response_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class UnifiedPAEntrypoint:
    """
    Single front door for all PA requests.

    Consolidates:
    - PersonalAssistantAgent (routing)
    - PersonalAIAssistant (learning)
    - EnhancedPersonalAIAssistant (tools)
    - WebSocket consumer (real-time)

    Into ONE consistent interface.
    """

    # Session 1065: Signals that suggest the user wants a long-form response
    _LONG_RESPONSE_SIGNALS = re.compile(
        r'\b(analy[zs]|evaluat|comprehensive|detailed|in.depth|thorough|'
        r'compare.*contrast|full.*report|write.*essay|write.*blog|'
        r'list.*all|summarize.*everything)\b', re.IGNORECASE
    )

    @staticmethod
    def _estimate_max_tokens(message: str) -> int:
        if UnifiedPAEntrypoint._LONG_RESPONSE_SIGNALS.search(message):
            return 3500
        return 2000

    # Session 959: Intent-to-enrichment mapping
    # Determines which intelligence services fire for each intent
    INTENT_ENRICHMENT_MAP = {
        'content_review':    ['blog_performance', 'domain_context', 'spider_trends', 'strategic_memory', 'proactive_intelligence'],
        'opportunities':     ['spider_trends', 'domain_context', 'advisor', 'proactive_intelligence'],
        'predictions':       ['spider_trends', 'domain_context'],
        'initiatives':       ['intelligence_enricher', 'strategic_memory'],
        'boardroom':         ['intelligence_enricher', 'strategic_memory'],
        'system_health':     ['intelligence_enricher'],
        'stock_intelligence': ['domain_context', 'spider_trends', 'proactive_intelligence'],
        'legislation':       ['domain_context', 'spider_trends'],
        'crypto_price':      ['domain_context'],
        'spider_data':       ['domain_context'],
        'execution_history': ['intelligence_enricher', 'strategic_memory', 'platform_briefing'],
        'learning_patterns': ['spider_trends'],
        'pilots':            ['intelligence_enricher'],
        'gates':             ['intelligence_enricher'],
        'reasoning':         ['intelligence_enricher', 'advisor', 'strategic_memory'],
        # Session 969: Live telemetry tools — pure data, no enrichment needed
        'recent_activity':     [],
        'system_health_check': [],
        'error_summary':       [],
        # Session 970: Surgical moves verification — pure data
        'surgical_moves_status': [],
        # Session 973: Broad system overview — light enrichment
        'system_overview': ['intelligence_enricher', 'proactive_intelligence', 'platform_briefing'],
        # Session 1007: Agent introspection + scheduled tasks — pure data
        'agent_introspection': [],
        'scheduled_tasks': [],
        # Session 1031: Dream browsing — pure data
        'dreams': [],
    }

    # Alias map: normalize variant intent names to canonical names
    INTENT_ALIASES = {
        'content': 'content_review',
        'blogs': 'content_review',
        'blog_list': 'content_review',
        'blog_query': 'content_review',
        'attention_items': 'boardroom',
        'decisions': 'boardroom',
        'decision_management': 'boardroom',
        'opportunity': 'opportunities',
        'health': 'system_health',
        'spider': 'spider_data',
        'experiments': 'pilots',
        'pilot': 'pilots',
        'gate': 'gates',
        # Session 969: Telemetry aliases
        'activity': 'recent_activity',
        'whats_happening': 'recent_activity',
        'errors': 'error_summary',
        'failures': 'error_summary',
        'platform_health': 'system_health_check',
        # Session 970: Surgical moves aliases
        'deliberation_status': 'surgical_moves_status',
        'verification_status': 'surgical_moves_status',
        'moves_status': 'surgical_moves_status',
        # Session 973: System overview aliases
        'overview': 'system_overview',
        'executive_summary': 'system_overview',
    }

    # Intents where spider_trends and domain_context always apply (no relevance gate)
    DIRECT_RELEVANCE_INTENTS = {
        'content_review', 'opportunities', 'predictions', 'spider_data', 'stock_intelligence', 'crypto_price',
    }

    # Per-section character caps to prevent any one source dominating
    # Session 1006: Raised from 300-600 → 1500-2000; old caps discarded 85-95% of enrichment data
    ENRICHMENT_CAPS = {
        'system_brief':     1500,
        'spider_trends':    2000,
        'blog_performance': 1500,
        'domain_context':   2000,
        'advisor':          1000,
        'strategic_memory':  1500,
        'learning_insights': 1500,
        'proactive_intelligence': 1500,
        'platform_briefing': 1500,
    }

    # Stop words for relevance gating
    STOP_WORDS = frozenset({
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'what', 'which',
        'who', 'how', 'when', 'where', 'why', 'my', 'me', 'i',
        'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
    })

    def __init__(self, user: User, conversation_id: str | None = None):
        self.user = user
        self.conversation_id = conversation_id
        self._execution_count = 0
        self._conversation_history: List[Dict[str, Any]] = []

        # Session 1030: Load recent conversation history from DB so context survives
        # Celery worker recycling. ChatConversation stores all PA exchanges.
        self._load_conversation_history_from_db()

        # Lazy-loaded services
        self._tool_dispatcher = None
        self._llm_enforcer = None
        self._profile_service = None
        self._knowledge_injector = None
        self._docs_context_builder = None  # Session 943: Docs injection for PA

        # Session 959: Intelligence enrichment services
        self._intelligence_enricher = None
        self._blog_performance_fn = None
        self._domain_context_builder = None
        self._spider_context_builder = None
        self._advisor_context_builder = None
        self._proactive_intelligence_service = None
        # Session 992: Platform Intelligence Briefing
        self._platform_briefing_service = None

        # Session 997: Mythology validation services
        self._mythology_prevention_service = None
        self._hallucination_flagging_service = None

        # Session 940: Triage mode state
        self._triage_mode = False
        self._triage_items: List[Dict[str, Any]] = []
        self._triage_index = 0
        self._triage_type = None  # 'attention' or 'decisions'
        self._triage_stats = {'approved': 0, 'ignored': 0, 'skipped': 0, 'promoted': 0, 'rejected': 0}

        # Session 1000B: Map #N display numbers to item UUIDs so users
        # can say "approve item #2" instead of pasting hex IDs.
        self._last_boardroom_items: Dict[int, str] = {}

        logger.info(f"UnifiedPA initialized for user {user.username}")  # type: ignore[attr-defined]

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID for this request."""
        self._execution_count += 1
        return f"pa-{self._execution_count}-{uuid.uuid4().hex[:8]}"

    @property
    def tool_dispatcher(self):
        """Lazy load ToolDispatcher."""
        if self._tool_dispatcher is None:
            from core.services.tool_dispatcher import get_tool_dispatcher
            self._tool_dispatcher = get_tool_dispatcher()
        return self._tool_dispatcher

    @property
    def llm_enforcer(self):
        """Lazy load LLMEnforcer."""
        if self._llm_enforcer is None:
            from core.llm_enforcer import LLMEnforcer
            self._llm_enforcer = LLMEnforcer()
        return self._llm_enforcer

    @property
    def profile_service(self):
        """Lazy load ProfileCompletenessService."""
        if self._profile_service is None:
            try:
                from core.services.profile_completeness_service import get_profile_completeness_service
                self._profile_service = get_profile_completeness_service()
            except ImportError:
                self._profile_service = None
        return self._profile_service

    @property
    def knowledge_injector(self):
        """Lazy load PAKnowledgeInjector."""
        if self._knowledge_injector is None:
            try:
                from core.services.pa_knowledge_injector import get_pa_knowledge_injector
                self._knowledge_injector = get_pa_knowledge_injector()
            except ImportError:
                self._knowledge_injector = None
        return self._knowledge_injector

    @property
    def docs_context_builder(self):
        """
        Session 943: Lazy load DocsContextBuilder for PA awareness of system docs.

        This gives the PA knowledge of:
        - CLAUDE.md (system overview, stats, architecture)
        - 00-START-NEXT-SESSION.md (current priorities)
        - Recent session handoffs (what we've been working on)
        - Relevant architecture and feature docs
        """
        if self._docs_context_builder is None:
            try:
                from core.services.docs_context_builder import get_docs_context_builder
                self._docs_context_builder = get_docs_context_builder()
            except ImportError:
                logger.warning("DocsContextBuilder not available")
                self._docs_context_builder = None
        return self._docs_context_builder

    # --- Session 959: Intelligence enrichment properties ---

    @property
    def intelligence_enricher(self):
        """Lazy load PAIntelligenceEnricher."""
        if self._intelligence_enricher is None:
            try:
                from core.services.pa_intelligence_enricher import PAIntelligenceEnricher
                # Session 1068: Disable spider trends in enricher — already handled
                # by SpiderContextBuilder, avoiding duplicate 300-record scans
                self._intelligence_enricher = PAIntelligenceEnricher(
                    config={'include_trends': False}
                )
            except ImportError:
                logger.warning("PAIntelligenceEnricher not available")
                self._intelligence_enricher = None
        return self._intelligence_enricher

    @property
    def blog_performance_fn(self):
        """Lazy load get_blog_performance_context function."""
        if self._blog_performance_fn is None:
            try:
                from core.services.blog_performance_context import get_blog_performance_context
                self._blog_performance_fn = get_blog_performance_context
            except ImportError:
                logger.warning("get_blog_performance_context not available")
                self._blog_performance_fn = None
        return self._blog_performance_fn

    @property
    def domain_context_builder(self):
        """Lazy load DomainContentContextBuilder."""
        if self._domain_context_builder is None:
            try:
                from core.services.domain_content_context import DomainContentContextBuilder
                self._domain_context_builder = DomainContentContextBuilder()
            except ImportError:
                logger.warning("DomainContentContextBuilder not available")
                self._domain_context_builder = None
        return self._domain_context_builder

    @property
    def spider_context_builder(self):
        """Lazy load SpiderContextBuilder."""
        if self._spider_context_builder is None:
            try:
                from core.services.spider_context_builder import get_spider_context_builder
                self._spider_context_builder = get_spider_context_builder()
            except ImportError:
                logger.warning("SpiderContextBuilder not available")
                self._spider_context_builder = None
        return self._spider_context_builder

    @property
    def advisor_context_builder(self):
        """Lazy load AdvisorContextBuilder."""
        if self._advisor_context_builder is None:
            try:
                from core.services.advisor_context_builder import get_advisor_context_builder
                self._advisor_context_builder = get_advisor_context_builder()
            except ImportError:
                logger.warning("AdvisorContextBuilder not available")
                self._advisor_context_builder = None
        return self._advisor_context_builder

    @property
    def proactive_intelligence_service(self):
        """Lazy load ProactiveIntelligenceService."""
        if self._proactive_intelligence_service is None:
            try:
                from core.services.proactive_intelligence import get_proactive_intelligence_service
                self._proactive_intelligence_service = get_proactive_intelligence_service(self.user)
            except ImportError:
                logger.warning("ProactiveIntelligenceService not available")
                self._proactive_intelligence_service = None
        return self._proactive_intelligence_service

    @property
    def platform_briefing_service(self):
        """Session 992: Lazy load PlatformIntelligenceBriefingService."""
        if self._platform_briefing_service is None:
            try:
                from core.services.platform_intelligence_briefing import get_platform_intelligence_service
                self._platform_briefing_service = get_platform_intelligence_service()
            except ImportError:
                logger.warning("PlatformIntelligenceBriefingService not available")
                self._platform_briefing_service = None
        return self._platform_briefing_service

    # --- Session 997: Mythology validation properties ---

    @property
    def mythology_prevention(self):
        """Lazy load MythologyPreventionService."""
        if self._mythology_prevention_service is None:
            from mythology.services import MythologyPreventionService
            self._mythology_prevention_service = MythologyPreventionService()
        return self._mythology_prevention_service

    @property
    def hallucination_flagging(self):
        """Lazy load HallucinationFlaggingService."""
        if self._hallucination_flagging_service is None:
            from mythology.services import HallucinationFlaggingService
            self._hallucination_flagging_service = HallucinationFlaggingService()
        return self._hallucination_flagging_service

    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        generate_audio: bool = False
    ) -> PAResponse:
        """
        Process a user message through the PA pipeline.

        Args:
            message: User's message
            context: Optional additional context
            generate_audio: Whether to generate TTS audio

        Returns:
            PAResponse with structured result
        """
        trace_id = self._generate_trace_id()
        start_time = time.time()
        context = context or {}

        logger.info(f"[{trace_id}] Processing message: {message[:100]}...")

        # Session 1085: Prompt injection defense
        from core.services.pa_security import scan_for_injection
        _inj = scan_for_injection(message, source='user_input')
        if _inj.severity == 'block':
            latency_ms = int((time.time() - start_time) * 1000)
            return PAResponse(
                content="I can't process that request. Please rephrase.",
                trace_id=trace_id,
                tool_runs=[],
                audio_url=None,
                intent='blocked',
                routed_to=None,
                profile_completeness=None,
                latency_ms=latency_ms,
                error=f"injection_blocked:{_inj.pattern_name}",
            )

        try:
            # Session 940: Check for triage mode first
            if self._triage_mode:
                # Handle triage responses
                content = await self.handle_triage_response(message)
                latency_ms = int((time.time() - start_time) * 1000)
                return PAResponse(
                    content=content,
                    trace_id=trace_id,
                    tool_runs=[],
                    audio_url=None,
                    intent='triage',
                    routed_to='governance_tool',
                    profile_completeness=None,
                    latency_ms=latency_ms,
                    error=None
                )

            # Session 940: Check for triage start commands
            # Only trigger on explicit commands, not conversational mentions
            message_lower = message.lower().strip()
            _triage_start_patterns = (
                'triage attention', 'triage decisions', 'triage items',
                'start triage', 'begin triage', 'let\'s triage',
                'run triage', 'do triage',
            )
            _is_triage_command = (
                message_lower in ('triage', 'triage please')
                or any(message_lower.startswith(p) for p in _triage_start_patterns)
            )
            if _is_triage_command:
                if 'attention' in message_lower or 'review' in message_lower:
                    content = await self.start_triage('attention')
                elif 'decision' in message_lower:
                    content = await self.start_triage('decisions')
                else:
                    content = await self.start_triage('attention')  # Default to attention

                latency_ms = int((time.time() - start_time) * 1000)
                return PAResponse(
                    content=content,
                    trace_id=trace_id,
                    tool_runs=[],
                    audio_url=None,
                    intent='triage',
                    routed_to='governance_tool',
                    profile_completeness=None,
                    latency_ms=latency_ms,
                    error=None
                )

            # 1. Build context
            t0 = time.time()
            full_context = await self._build_context(message, context)
            logger.info(f"[{trace_id}] Step 1 _build_context: {int((time.time()-t0)*1000)}ms")

            # Session 1036: Feature flag for LLM-driven function calling
            tool_call_metadata = None
            tool_result_data = None
            response_id = None

            if getattr(settings, 'PA_USE_FUNCTION_CALLING', False):
                # ── New path: GPT-5.2 function calling ──────────────────────
                content, tool_runs_raw, fc_meta, response_id = await self._run_agentic_loop(
                    message, full_context, trace_id
                )
                tool_runs = tool_runs_raw

                # Session 1076: Fix hallucinated Cloudinary URLs in LLM response.
                # The LLM sometimes constructs URLs from prompt text instead of
                # copying the real URL from tool results.
                content = self._fix_hallucinated_urls(content, tool_runs_raw, trace_id)

                # Deterministic fallback: if user said "remember X" but LLM didn't call remember_tool
                if not any(r.get('tool') == 'remember_tool' for r in tool_runs_raw):
                    memory_match = _detect_memory_intent(message)
                    if memory_match:
                        try:
                            from core.services.tool_dispatcher import _redact_secrets
                            from core.models import UserMemoryContext, EnhancedUserProfile
                            fallback_content = _redact_secrets(memory_match)
                            profile, _ = EnhancedUserProfile.objects.get_or_create(user=self.user)
                            UserMemoryContext.objects.create(
                                user=self.user,
                                profile=profile,
                                memory_type='instruction',
                                content=fallback_content[:500],
                                importance=7,
                                source='auto_detect',
                                context_metadata={'trigger': 'deterministic_fallback'},
                            )
                            from core.services.memory_context_service import get_memory_context_service
                            get_memory_context_service().clear_cache(self.user)
                            logger.info(f"[{trace_id}] Deterministic memory fallback saved: {fallback_content[:80]}")
                        except Exception as e:
                            logger.warning(f"[PA] Deterministic memory save failed: {e}")

                # Infer intent from tool names for enrichment
                tool_names = [r.get('tool', '') for r in tool_runs_raw]
                intent = self._infer_intent_from_tools(tool_names)
                routed_to = tool_names[0] if tool_names else None

                # Use GPT function call metadata (has name, arguments, call_id, ok)
                tool_call_metadata = fc_meta
                tool_result_data = tool_runs_raw

                # Run enrichment if tools were called and succeeded
                if tool_runs_raw and any(r.get('ok') for r in tool_runs_raw):
                    t2 = time.time()
                    try:
                        enrichment_sections = await asyncio.wait_for(
                            self._enrich_tool_result(
                                message, intent or 'general', {}, trace_id
                            ),
                            timeout=15.0
                        )
                    except asyncio.TimeoutError:
                        enrichment_sections = {}
                    # Session 1085: Scrub enrichment context (PII + injection scan)
                    if enrichment_sections:
                        from core.services.pa_security import scrub_enrichment_context
                        enrichment_sections = scrub_enrichment_context(enrichment_sections)
                    logger.info(f"[{trace_id}] FC enrichment: {int((time.time()-t2)*1000)}ms sections={list(enrichment_sections.keys())}")
            else:
                # ── Existing path: keyword routing (unchanged) ──────────────
                # 2. Detect intent and route
                detected_intent, routed_to = self._detect_intent_and_route(message)
                intent = detected_intent or 'general'
                logger.info(f"[{trace_id}] Step 2 intent={intent} routed_to={routed_to}")

                # 3. Execute (tool or direct response)
                tool_runs = []
                if routed_to:
                    # Execute via ToolDispatcher
                    t1 = time.time()
                    # Session 1034: research_and_create needs longer timeout (web search + LLM generation)
                    # Session 1035: legal_assistance — agent does spider queries + OpenAI LLM calls
                    # Session 1035: agent_execution — 60s for agents that do LLM calls (30s default too tight)
                    # Session 1076: studio — external API calls (RunwayML, ElevenLabs) take 40-90s
                    if intent in ('research_and_create', 'legal_assistance',
                                   'image_creation', 'video_creation', 'studio'):
                        tool_timeout = 120
                    elif intent == 'agent_execution':
                        tool_timeout = 60
                    else:
                        tool_timeout = None
                    tool_result = await self.tool_dispatcher.execute(
                        tool_name=routed_to,
                        payload=self._build_tool_payload(message, intent, context),
                        user_id=self.user.id,  # type: ignore[attr-defined]
                        timeout=tool_timeout
                    )
                    logger.info(f"[{trace_id}] Step 3a tool_dispatch: {int((time.time()-t1)*1000)}ms ok={tool_result.ok}")
                    tool_runs.append(tool_result.to_dict())

                    if tool_result.ok:
                        # Session 959: Enrich tool result with intelligence context
                        # Session 977: Cap enrichment at 15s to prevent pipeline stalls
                        t2 = time.time()
                        try:
                            enrichment_sections = await asyncio.wait_for(
                                self._enrich_tool_result(
                                    message, intent, tool_result.result, trace_id
                                ),
                                timeout=15.0
                            )
                        except asyncio.TimeoutError:
                            logger.warning(f"[{trace_id}] Enrichment timed out after 15s, proceeding without")
                            enrichment_sections = {}
                        # Session 1085: Scrub enrichment context (PII + injection scan)
                        if enrichment_sections:
                            from core.services.pa_security import scrub_enrichment_context
                            enrichment_sections = scrub_enrichment_context(enrichment_sections)
                        logger.info(f"[{trace_id}] Step 3b enrichment: {int((time.time()-t2)*1000)}ms sections={list(enrichment_sections.keys())}")

                        # Generate response from tool result + enrichment
                        t3 = time.time()
                        content = await self._generate_response_from_tool(
                            message, intent, tool_result.result, full_context, trace_id,
                            enrichment_sections=enrichment_sections
                        )
                        logger.info(f"[{trace_id}] Step 3c generate_response: {int((time.time()-t3)*1000)}ms")
                    else:
                        # Tool failed - generate error response
                        content = f"I encountered an issue: {tool_result.error_message}. " \
                                  f"(trace: {tool_result.trace_id})"
                else:
                    # No tool needed - direct LLM response
                    # Session 948: Special handling for user feedback - be honest about limitations
                    if intent == 'user_feedback':
                        content = await self._generate_honest_feedback_response(message, full_context, trace_id)
                    elif intent == 'capabilities':
                        content = self._generate_capabilities_response(full_context.get('user_name', 'there'))
                    else:
                        content = await self._generate_direct_response(message, full_context, trace_id)

            # Session 997: Validate response for mythology/hallucinations
            content = self._validate_mythology(content, message, trace_id)

            # Session 1060: Strip leaked internal reasoning from FC responses
            # (e.g. "to=functions.content_review_tool", raw JSON tool call syntax)
            if getattr(settings, 'PA_USE_FUNCTION_CALLING', False):
                content = self._sanitize_fc_response(content, trace_id)

            # Session 1085: Scrub PII/secrets from final response
            if content:
                from core.services.data_scrubber import scrub
                content = scrub(content)

            # 4. Generate audio if requested
            audio_url = None
            if generate_audio and content:
                audio_url = await self._generate_audio(content, trace_id)

            # 5. Store in conversation history
            self._conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            assistant_turn = {
                'role': 'assistant',
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'trace_id': trace_id,
            }
            # Session 1036: Store function calling metadata for multi-turn context
            if tool_call_metadata:
                assistant_turn['tool_calls'] = tool_call_metadata  # type: ignore[arg-type]
            if tool_result_data:
                assistant_turn['tool_results'] = tool_result_data  # type: ignore[arg-type]
            if response_id:
                assistant_turn['response_id'] = response_id
            self._conversation_history.append(assistant_turn)

            # Keep only last 20 turns (was 40 — each turn is re-sent to GPT-5.2)
            if len(self._conversation_history) > 20:
                self._conversation_history = self._conversation_history[-20:]

            latency_ms = int((time.time() - start_time) * 1000)

            # Get profile completeness
            profile_completeness = None
            if self.profile_service:
                try:
                    score = self.profile_service.get_completeness_score(self.user)
                    profile_completeness = int(score * 100)
                except Exception as e:
                    logger.warning(f"Profile completeness score failed: {e}")

            # Structured task summary for cost/performance analysis
            tool_names = [r.get('tool', '') for r in tool_runs] if tool_runs else []
            logger.info(
                "[PA_TASK_SUMMARY] trace_id=%s latency_ms=%d llm_iterations=%d "
                "tool_calls=%d tools=%s history_turns=%d intent=%s",
                trace_id, latency_ms,
                len(tool_call_metadata) if tool_call_metadata else 1,
                len(tool_names), ','.join(tool_names) or 'none',
                len(self._conversation_history), intent,
            )

            return PAResponse(
                content=content,
                trace_id=trace_id,
                tool_runs=tool_runs,
                audio_url=audio_url,
                intent=intent,
                routed_to=routed_to,
                profile_completeness=profile_completeness,
                latency_ms=latency_ms,
                error=None,
                tool_call_metadata=tool_call_metadata,
                tool_result_data=tool_result_data,
                response_id=response_id,
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{trace_id}] Error processing message: {e}", exc_info=True)

            return PAResponse(
                content=f"I'm sorry, I encountered an error processing your request. (trace: {trace_id})",
                trace_id=trace_id,
                tool_runs=[],
                audio_url=None,
                intent=None,
                routed_to=None,
                profile_completeness=None,
                latency_ms=latency_ms,
                error=str(e)
            )

    # =========================================================================
    # Session 1080: Live schema reload — detect new tools after deploy
    # =========================================================================

    _cached_schema_version: Optional[str] = None

    def _get_live_tool_schemas(self) -> list:
        """
        Return PA_TOOL_SCHEMAS, reloading the module if the version has changed.

        After a Railway deploy, Celery workers restart and all caches clear.
        But if a process is long-lived (local dev, or slow worker recycling),
        this detects that the schema module has been updated and reloads it.

        This ensures Rigby always gets the latest tool schemas without needing
        a manual cache clear or process restart.
        """
        import importlib
        import core.services.pa_tool_schemas as schema_module

        current_version = schema_module.SCHEMA_VERSION

        if (UnifiedPAEntrypoint._cached_schema_version is not None
                and UnifiedPAEntrypoint._cached_schema_version != current_version):
            # Schema version changed — reload module to pick up new tools
            logger.info(
                f"[PA] Schema version changed: "
                f"{UnifiedPAEntrypoint._cached_schema_version} -> {current_version}, "
                f"reloading tool schemas and dispatcher"
            )
            schema_module = importlib.reload(schema_module)

            # Also reset the ToolDispatcher singleton so new handlers are registered
            from core.services.tool_dispatcher import reset_tool_dispatcher
            reset_tool_dispatcher()

        UnifiedPAEntrypoint._cached_schema_version = schema_module.SCHEMA_VERSION
        return schema_module.PA_TOOL_SCHEMAS

    # =========================================================================
    # Session 1036: LLM-Driven Function Calling (Agentic Loop)
    # =========================================================================

    async def _run_agentic_loop(
        self,
        message: str,
        context: Dict[str, Any],
        trace_id: str,
        max_iterations: int = 8,  # Session 1075: raised from 5 to handle batch ops (15+ boardroom items)
        total_timeout: float = 120.0,
    ) -> tuple[str, List[Dict], List[Dict], Optional[str]]:
        """
        Core agentic loop: GPT-5.2 decides which tools to call.

        Returns (content, tool_runs, fc_metadata, response_id)
        where fc_metadata captures the GPT function call info (name, arguments, call_id).
        """
        PA_TOOL_SCHEMAS = self._get_live_tool_schemas()

        # Build initial messages array
        messages = self._build_messages_array(message, context)

        tool_runs = []
        fc_metadata: List[Dict] = []  # GPT function call metadata (name, args, call_id)
        response_id = None
        prev_tool_sigs: List[str] = []  # Session 1043: Track tool call signatures for loop detection

        for iteration in range(max_iterations):
            # On final iteration, don't offer tools — force a text response
            is_final = (iteration == max_iterations - 1)

            logger.info(f"[{trace_id}] FC iteration {iteration+1}/{max_iterations} (final={is_final})")

            # Call GPT-5.2 with tools
            # Always pass messages as input_messages — on iteration 1 it's the full
            # messages array; on subsequent iterations it's the tool_call_output items.
            # previous_response_id provides conversation continuity; input provides
            # the new content (tool outputs) that the API needs to continue.
            result = await asyncio.to_thread(
                self.llm_enforcer.enforce_real_ai,
                prompt=message,
                input_messages=messages,
                tools=PA_TOOL_SCHEMAS if not is_final else None,
                previous_response_id=response_id,
                task_type='conversation',
                max_tokens=self._estimate_max_tokens(message),
                agent_name='PersonalAssistant',
                trace_id=trace_id,
            )

            if not result.get('success'):
                error_msg = result.get('error', '')
                logger.error(f"[{trace_id}] FC LLM call failed at iteration {iteration+1}: {error_msg}")
                # Session 1079: Retry once on first iteration — transient API
                # errors or input validation failures may succeed on a second try
                # with a fresh request (no previous_response_id chain).
                if iteration == 0 and not result.get('blocked_by_lungs'):
                    logger.info(f"[{trace_id}] LLM call failed on first iteration — retrying fresh")
                    messages = self._build_messages_array(message, context)
                    response_id = None
                    continue
                # Session 1086: If tools already ran successfully but the
                # continuation/summary LLM call failed (e.g. OpenAI 400
                # "invalid_prompt" from accumulated context), attempt a
                # fresh summarization call with truncated tool results
                # instead of returning the raw error to the user.
                successful_runs = [r for r in tool_runs if r.get('ok')]
                if successful_runs:
                    logger.info(
                        f"[{trace_id}] LLM failed at iteration {iteration+1} with "
                        f"{len(successful_runs)} successful tool runs — attempting fresh summary"
                    )
                    fresh_messages = self._build_messages_array(message, context)
                    tool_summary = json.dumps(
                        [{'tool': r.get('tool', ''), 'ok': r.get('ok'),
                          'result': str(r.get('result', ''))[:500]}
                         for r in tool_runs],
                        default=str
                    )[:4000]
                    fresh_messages.append({
                        "role": "user",
                        "content": (
                            "Here are the tool results I gathered. "
                            "Please summarize them for the user:\n" + tool_summary
                        ),
                    })
                    summary_result = await asyncio.to_thread(
                        self.llm_enforcer.enforce_real_ai,
                        prompt=message,
                        input_messages=fresh_messages,
                        tools=None,
                        previous_response_id=None,
                        task_type='conversation',
                        max_tokens=2000,
                        agent_name='PersonalAssistant',
                        trace_id=trace_id,
                    )
                    if summary_result.get('success'):
                        return (summary_result.get('response', ''), tool_runs, fc_metadata,
                                summary_result.get('response_id'))
                return (result.get('response', 'I encountered an error.'), tool_runs, fc_metadata, response_id)

            response_id = result.get('response_id')
            tool_calls = result.get('tool_calls', [])

            # If no tool calls, LLM responded with text — done
            if not tool_calls:
                # Session 1079: Empty response on first iteration — retry fresh
                text_content = result.get('response', '')
                if not text_content.strip() and iteration == 0 and not tool_runs:
                    logger.warning(f"[{trace_id}] Empty LLM response on first iteration — retrying fresh")
                    messages = self._build_messages_array(message, context)
                    response_id = None
                    continue

                # Session 1056: Also check text-only responses for degeneracy.
                # Model may get stuck generating filler like "Ok.Ok.Let's call.Ok."
                # instead of emitting actual function calls.
                if text_content and self._is_degenerate_content(text_content):
                    logger.warning(
                        f"[{trace_id}] Degenerate text-only response at iteration {iteration+1}, "
                        f"len={len(text_content)}, content: {text_content[:200]!r}"
                    )
                    # Session 1063: If we have successful tool runs, do a clean
                    # summary instead of returning the generic error. The tools
                    # DID work (e.g. images were generated) — the LLM just
                    # degenerated when forced to text on the final iteration.
                    successful_runs = [r for r in tool_runs if r.get('ok')]
                    if successful_runs:
                        logger.info(f"[{trace_id}] Attempting clean summary of {len(successful_runs)} successful tool runs")
                        fresh_messages = self._build_messages_array(message, context)
                        tool_summary = json.dumps(
                            [{'tool': r.get('tool', ''), 'ok': r.get('ok'), 'result': str(r.get('result', ''))[:500]}
                             for r in tool_runs],
                            default=str
                        )[:4000]
                        fresh_messages.append({
                            "role": "user",
                            "content": f"Here are the tool results I gathered. Please summarize them for the user:\n{tool_summary}",
                        })
                        final_result = await asyncio.to_thread(
                            self.llm_enforcer.enforce_real_ai,
                            prompt=message,
                            input_messages=fresh_messages,
                            tools=None,
                            previous_response_id=None,
                            task_type='conversation',
                            max_tokens=2000,
                            agent_name='PersonalAssistant',
                            trace_id=trace_id,
                        )
                        return (final_result.get('response', ''), tool_runs, fc_metadata, final_result.get('response_id'))

                    # Session 1079: Retry once with a fresh call before giving up.
                    # The LLM may have degenerated due to an overly long/complex
                    # user message overwhelming the first attempt. A fresh call
                    # without previous_response_id and with tools gives it another
                    # chance to respond properly.
                    if iteration == 0:
                        logger.info(f"[{trace_id}] Degenerate on first iteration with no tool runs — retrying fresh")
                        messages = self._build_messages_array(message, context)
                        response_id = None
                        continue

                    return (
                        "I ran into an issue processing that request. Could you try again or rephrase?",
                        tool_runs, fc_metadata, response_id,
                    )
                # Session 1065: Auto-continue truncated text responses
                if result.get('truncated') and response_id:
                    parts = [result.get('response', '')]
                    for cont_i in range(2):
                        logger.info(f"[{trace_id}] Truncation continuation {cont_i+1}/2 ({len(''.join(parts))} chars so far)")
                        cont_result = await asyncio.to_thread(
                            self.llm_enforcer.enforce_real_ai,
                            prompt="continue",
                            input_messages=[{"role": "user", "content": "continue"}],
                            tools=None,
                            previous_response_id=response_id,
                            task_type='conversation',
                            max_tokens=2000,
                            agent_name='PersonalAssistant',
                            trace_id=trace_id,
                        )
                        if not cont_result.get('success'):
                            break
                        response_id = cont_result.get('response_id', response_id)
                        parts.append(cont_result.get('response', ''))
                        if not cont_result.get('truncated'):
                            break
                    combined = ''.join(parts)
                    logger.info(f"[{trace_id}] Truncation resolved: {len(parts)} parts, {len(combined)} chars")
                    return (combined, tool_runs, fc_metadata, response_id)

                return (result.get('response', ''), tool_runs, fc_metadata, response_id)

            # Session 1043: Detect degenerate loops — LLM stuck repeating itself
            text_content = result.get('response', '')
            if text_content and self._is_degenerate_content(text_content):
                logger.warning(
                    f"[{trace_id}] Degenerate content detected at iteration {iteration+1}, "
                    f"forcing final text response. Content: {text_content[:100]!r}"
                )
                # Re-run WITHOUT tools to force a clean text answer.
                # Session 1060: Drop previous_response_id — the current response
                # has pending tool_calls, so OpenAI rejects continuations without
                # function_call_output. Rebuild fresh messages instead.
                fresh_messages = self._build_messages_array(message, context)
                final_result = await asyncio.to_thread(
                    self.llm_enforcer.enforce_real_ai,
                    prompt=message,
                    input_messages=fresh_messages,
                    tools=None,
                    previous_response_id=None,
                    task_type='conversation',
                    max_tokens=2000,
                    agent_name='PersonalAssistant',
                    trace_id=trace_id,
                )
                return (final_result.get('response', ''), tool_runs, fc_metadata, final_result.get('response_id'))

            # Session 1043: Detect repeated identical tool calls (same tool+args)
            current_sigs = sorted(
                f"{tc.get('function', {}).get('name', '')}:{tc.get('function', {}).get('arguments', '')}"
                for tc in tool_calls
            )
            sig_key = '|'.join(current_sigs)
            if sig_key in prev_tool_sigs:
                logger.warning(
                    f"[{trace_id}] Duplicate tool call signature detected at iteration {iteration+1}, "
                    f"breaking loop. Sig: {sig_key[:100]}"
                )
                # Session 1060: Drop previous_response_id — see degenerate break above.
                # Also inject tool results as user context so the LLM can summarize.
                fresh_messages = self._build_messages_array(message, context)
                tool_summary = json.dumps(
                    [{'tool': r.get('tool', ''), 'ok': r.get('ok'), 'result': str(r.get('result', ''))[:500]}
                     for r in tool_runs],
                    default=str
                )[:4000]
                fresh_messages.append({
                    "role": "user",
                    "content": f"Here are the tool results I gathered. Please summarize them for the user:\n{tool_summary}",
                })
                final_result = await asyncio.to_thread(
                    self.llm_enforcer.enforce_real_ai,
                    prompt=message,
                    input_messages=fresh_messages,
                    tools=None,
                    previous_response_id=None,
                    task_type='conversation',
                    max_tokens=2000,
                    agent_name='PersonalAssistant',
                    trace_id=trace_id,
                )
                return (final_result.get('response', ''), tool_runs, fc_metadata, final_result.get('response_id'))
            prev_tool_sigs.append(sig_key)

            # Execute each tool call via ToolDispatcher
            tool_result_inputs = []
            for tc in tool_calls:
                fn = tc.get('function', {})
                tool_name = fn.get('name', '')
                call_id = tc.get('id', '')

                try:
                    arguments = json.loads(fn.get('arguments', '{}'))
                except (json.JSONDecodeError, TypeError):
                    arguments = {}

                logger.info(f"[{trace_id}] FC calling tool: {tool_name}({list(arguments.keys())})")

                # Handle the 'run_agent' meta-tool by routing to the actual agent tool
                actual_tool_name = tool_name
                if tool_name == 'run_agent':
                    actual_tool_name = arguments.pop('agent_name', tool_name)

                # Determine timeout based on tool
                if actual_tool_name in ('research_and_create_tool', 'legal_doc_drafter_agent',
                                       'image_generation_agent', 'video_generation_agent',
                                       'video_editing_agent', 'studio_tool',
                                       'talking_character_agent', 'http_smoke_test'):
                    tool_timeout = 120
                elif actual_tool_name in ('universal_agent_tool',) or actual_tool_name.endswith('_agent'):
                    tool_timeout = 60
                else:
                    tool_timeout = None

                tool_result = await self.tool_dispatcher.execute(
                    tool_name=actual_tool_name,
                    payload=arguments,
                    user_id=self.user.id,  # type: ignore[attr-defined]
                    timeout=tool_timeout,
                )
                tool_runs.append(tool_result.to_dict())

                # Session 1060: Record tool call in ToolCallRecord for observability.
                # Session 1061: Must use asyncio.to_thread — we're in an async
                # coroutine, so synchronous ORM raises SynchronousOnlyOperation.
                try:
                    await asyncio.to_thread(
                        self._record_tool_call,
                        trace_id=trace_id,
                        tool_name=actual_tool_name,
                        arguments=arguments,
                        tool_result=tool_result,
                        task_summary=message[:200],
                    )
                except Exception as rec_err:
                    logger.warning(f"[{trace_id}] ToolCallRecord save failed (non-fatal): {rec_err}")

                # Capture GPT function call metadata for persistence/multi-turn
                fc_metadata.append({
                    'name': tool_name,
                    'arguments': arguments,
                    'call_id': call_id,
                    'ok': tool_result.ok,
                })

                # Format result for feeding back to LLM
                if tool_result.ok:
                    output = json.dumps(tool_result.result, default=str)
                else:
                    output = json.dumps({'error': tool_result.error_message})

                tool_result_inputs.append({
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": self._truncate_tool_output(output, 8000),
                })

            # Log tool output token budget for this iteration
            tool_output_chars = sum(len(t.get('output', '')) for t in tool_result_inputs)
            logger.info(
                "[PA_TOOL_INJECTION] iteration=%d tools=%d chars=%d tokens_est=%d",
                iteration + 1, len(tool_result_inputs),
                tool_output_chars, tool_output_chars // 4,
            )

            # Feed tool results back — use previous_response_id for efficiency
            messages = tool_result_inputs

        # Safety: shouldn't normally reach here
        return ("I wasn't able to complete that request.", tool_runs, fc_metadata, response_id)

    @staticmethod
    def _fix_hallucinated_urls(content: str, tool_runs: list, trace_id: str) -> str:
        """Session 1076: Replace hallucinated Cloudinary URLs with real ones.

        The LLM sometimes constructs Cloudinary URLs from prompt text instead
        of copying the actual URL returned by the tool. This method:
        1. Collects all real Cloudinary URLs from tool results
        2. Finds all Cloudinary URLs in the response text
        3. Replaces any hallucinated URL (not in the real set) with the closest
           real URL from the same tool run.
        """
        import re

        if not content or 'cloudinary' not in content:
            return content

        # Collect real URLs from tool results
        real_urls: list[str] = []
        for run in (tool_runs or []):
            result = run.get('result', {}) or {}
            if isinstance(result, dict):
                # Direct image_url field
                if result.get('image_url'):
                    real_urls.append(result['image_url'])
                # images list with url field
                for img in (result.get('images') or result.get('data', {}).get('images', []) or []):
                    if isinstance(img, dict) and img.get('url'):
                        real_urls.append(img['url'])
                # Nested output (agent results)
                output = result.get('output', '')
                if isinstance(output, str):
                    for m in re.finditer(r'https://res\.cloudinary\.com/[^\s\)\"\']+', output):
                        real_urls.append(m.group(0))

        if not real_urls:
            return content

        real_url_set = set(real_urls)

        # Find all Cloudinary URLs in the response
        url_pattern = re.compile(r'https://res\.cloudinary\.com/[^\s\)\"\']+')
        response_urls = url_pattern.findall(content)

        if not response_urls:
            return content

        # Replace hallucinated URLs with the first real URL
        replaced = False
        for resp_url in response_urls:
            if resp_url not in real_url_set:
                # This URL was hallucinated — replace with real URL
                content = content.replace(resp_url, real_urls[0])
                replaced = True
                logger.warning(
                    f"[{trace_id}] Replaced hallucinated URL "
                    f"({resp_url[:80]}...) with real URL ({real_urls[0][:80]}...)"
                )

        if replaced:
            logger.info(f"[{trace_id}] Fixed hallucinated Cloudinary URLs in response")

        return content

    @staticmethod
    def _truncate_tool_output(output: str, limit: int = 8000) -> str:
        """
        Session 1065: Smart truncation that preserves valid JSON structure.

        Raw [:8000] slicing broke JSON mid-object, causing GPT-5.2 to see
        only partial results (e.g. 1 of 13 initiatives). This helper:
        1. Returns as-is if under limit
        2. Parses JSON, finds the main list field, and drops tail items
           until the re-serialized output fits, adding a _truncated marker
        3. Falls back to raw slice if JSON parsing fails
        """
        if len(output) <= limit:
            return output

        original_chars = len(output)
        logger.info(
            "[PA_TOOL_TRUNCATE] chars=%d limit=%d trimming=%d",
            original_chars, limit, original_chars - limit,
        )

        # Try JSON-aware truncation
        try:
            data = json.loads(output)
        except (json.JSONDecodeError, TypeError):
            return output[:limit]

        if not isinstance(data, dict):
            return output[:limit]

        # Find the main list field
        list_key = None
        list_val = None
        for key in ('items', 'results', 'data', 'entries', 'records'):
            if key in data and isinstance(data[key], list):
                list_key = key
                list_val = data[key]
                break

        # If no known list key, try the first list-valued field
        if list_key is None:
            for key, val in data.items():
                if isinstance(val, list) and len(val) > 1:
                    list_key = key
                    list_val = val
                    break

        if list_key is None or not list_val:
            return output[:limit]

        total_count = len(list_val)

        # Binary search for the max number of items that fit
        lo, hi = 0, total_count
        while lo < hi:
            mid = (lo + hi + 1) // 2
            data[list_key] = list_val[:mid]
            data['_truncated'] = {'shown': mid, 'total': total_count}
            candidate = json.dumps(data, default=str)
            if len(candidate) <= limit:
                lo = mid
            else:
                hi = mid - 1

        data[list_key] = list_val[:lo]
        if lo < total_count:
            data['_truncated'] = {'shown': lo, 'total': total_count}
        else:
            data.pop('_truncated', None)

        return json.dumps(data, default=str)

    @staticmethod
    def _is_degenerate_content(text: str) -> bool:
        """
        Session 1043: Detect degenerate LLM output (stuck loops).
        Session 1060: Fixed false positives — use word-boundary matching,
        narrower filler list, and log which pattern triggered.

        Catches patterns like "Ok.Ok.Ok.Ok..." or "Stop.Stop.Stop."
        where the model is generating filler instead of real content.
        """
        if not text or len(text) < 30:
            return False

        # Strip whitespace and check for high repetition of short tokens
        compressed = text.replace(' ', '').replace('\n', '')
        if not compressed:
            return False

        # Pattern 1: Extremely repetitive — same 2-5 char substring repeated many times
        # e.g. "Ok.Ok.Ok.Ok.Ok." or "Stop.Stop.Stop."
        # Session 1060: Require >40% of windows to match, not just 6 absolute.
        # '##' appears 8 times in a 2000-char markdown report (0.8%) — that's
        # not degenerate, just normal headings. True degenerate text has >40%.
        for chunk_len in (2, 3, 4, 5):
            total_windows = len(compressed) // chunk_len
            if total_windows >= 6:
                chunk = compressed[:chunk_len]
                repeat_count = 0
                for i in range(0, len(compressed) - chunk_len + 1, chunk_len):
                    if compressed[i:i+chunk_len] == chunk:
                        repeat_count += 1
                repeat_ratio = repeat_count / total_windows
                if repeat_count >= 6 and repeat_ratio > 0.4:
                    logger.debug(f"[degenerate] Pattern 1 hit: chunk={chunk!r} repeated {repeat_count}/{total_windows} ({repeat_ratio:.0%})")
                    return True

        # Pattern 2: High ratio of filler words (word-boundary matching).
        # Session 1060: Use split-based matching instead of str.count() to avoid
        # substring false positives ('ok' in 'token', 'now' in 'know', etc.).
        # Narrowed list to genuinely degenerate words — removed 'call', 'tool',
        # 'now', 'proceed', 'send', "let's" which appear in normal tool-planning text.
        _FILLER_WORDS = {'ok', 'stop', 'done', 'alright', 'enough', 'sorry', 'ok.', 'stop.', 'done.'}
        words = text.lower().split()
        word_count = len(words)
        if word_count > 10:
            filler_count = sum(1 for w in words if w.strip('.,!?:;') in _FILLER_WORDS)
            if filler_count / word_count > 0.5:
                logger.debug(f"[degenerate] Pattern 2 hit: {filler_count}/{word_count} filler words")
                return True

        # Pattern 3: Very long text with almost no unique words (degenerate repetition)
        if len(words) > 20:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.15:
                logger.debug(f"[degenerate] Pattern 3 hit: unique_ratio={unique_ratio:.2f}")
                return True

        # Session 1056: Pattern 4 — high "Ok." density anywhere in text.
        # Model stuck in acknowledgment/attempt loop: "Ok.Let's call.Ok.Ok.Ok."
        # Normal text never has "ok." 8+ times.
        lower = text.lower()
        ok_count = lower.count('ok.')
        if ok_count >= 8:
            logger.debug(f"[degenerate] Pattern 4 hit: 'ok.' count={ok_count}")
            return True

        # Session 1065: Pattern 5 — run-on sentences without spaces after periods.
        # Degenerate text often concatenates fragments: "call.Ok.Let's call.Ok.Stop."
        # Normal text always has spaces after periods. Count period followed
        # immediately by an uppercase letter — if >= 10, it's degenerate.
        import re as _degen_re
        runon_count = len(_degen_re.findall(r'\.[A-Z]', text))
        if runon_count >= 10:
            logger.debug(f"[degenerate] Pattern 5 hit: run-on sentences count={runon_count}")
            return True

        return False

    def _record_tool_call(
        self,
        trace_id: str,
        tool_name: str,
        arguments: dict,
        tool_result,  # ToolResult dataclass
        task_summary: str = '',
    ) -> None:
        """
        Session 1060: Persist PA tool calls to ToolCallRecord for observability.

        Previously PA had zero records — impossible to debug what tools were
        called, what succeeded/failed. This runs synchronously but is fast
        (single INSERT).
        """
        import hashlib
        from core.models_tool_calls import ToolCallRecord

        result_str = json.dumps(tool_result.result, default=str) if tool_result.result else ''
        result_size = len(result_str.encode('utf-8', errors='replace'))

        ToolCallRecord.objects.create(
            trace_id=None,  # PA trace_id is "pa-N-hex" not UUID; store in task_summary
            conversation_id=self.conversation_id,  # Session 1085: link PA tool records to conversation
            agent_name='PersonalAssistant',
            tool_name=tool_name,
            parameters=arguments,
            result_summary=result_str[:4096],
            result_hash=f"sha256:{hashlib.sha256(result_str.encode()).hexdigest()}" if result_str else '',
            full_result=result_str if result_size <= 65536 else '',
            result_size_bytes=result_size,
            success=tool_result.ok,
            error_message=tool_result.error_message or '',
            error_type=tool_result.error_code or '',
            latency_ms=tool_result.latency_ms,
            task_summary=f"[{trace_id}] {task_summary}"[:500],
        )

    @staticmethod
    def _sanitize_fc_response(content: str, trace_id: str) -> str:
        """
        Session 1060: Strip leaked internal reasoning from FC responses.

        GPT-5.2 sometimes includes function-calling syntax or raw JSON tool
        call artifacts in its text response (e.g. "to=functions.tool_name",
        raw JSON blobs from tool results). These should never reach the user.
        """
        if not content:
            return content

        original_len = len(content)

        # Strip "to=functions.xxx" patterns (leaked tool routing syntax)
        content = re.sub(r'\bto=functions\.\w+', '', content)

        # Strip lines that are pure JSON objects (tool result leaks)
        # but preserve JSON inside markdown code blocks
        lines = content.split('\n')
        cleaned_lines = []
        in_code_block = False
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
            if in_code_block:
                cleaned_lines.append(line)
                continue
            stripped = line.strip()
            # Skip lines that are pure JSON objects (not in code blocks)
            if stripped.startswith('{') and stripped.endswith('}') and len(stripped) > 100:
                try:
                    json.loads(stripped)
                    continue  # Skip pure JSON lines
                except (json.JSONDecodeError, ValueError):
                    pass
            cleaned_lines.append(line)
        content = '\n'.join(cleaned_lines)

        # Clean up multiple blank lines left by removals
        content = re.sub(r'\n{3,}', '\n\n', content).strip()

        if len(content) < original_len:
            logger.info(
                f"[{trace_id}] Sanitized FC response: removed "
                f"{original_len - len(content)} chars of leaked internal content"
            )

        return content

    def _build_messages_array(self, message: str, context: Dict[str, Any]) -> List[Dict]:
        """
        Build the Responses API input from system prompt + history + user message.
        """
        messages = []

        # System instruction
        system_content = self._build_function_calling_system_prompt(context)
        messages.append({
            "role": "system",
            "content": system_content,
        })

        # Conversation history with tool call metadata
        history_chars = 0
        for turn in self._conversation_history:
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            history_chars += len(content)

            if role == 'user':
                messages.append({"role": "user", "content": content})
            elif role == 'assistant':
                messages.append({"role": "assistant", "content": content})
                # If this assistant turn had tool calls, include them for context
                # (The LLM benefits from seeing what tools were called previously)

        # Current user message
        messages.append({"role": "user", "content": message})

        # Token budget instrumentation — estimate tokens as chars/4
        system_tokens_est = len(system_content) // 4
        history_tokens_est = history_chars // 4
        message_tokens_est = len(message) // 4
        total_est = system_tokens_est + history_tokens_est + message_tokens_est
        logger.info(
            "[PA_TOKEN_BUDGET] system=%d history=%d (turns=%d) message=%d total=%d",
            system_tokens_est, history_tokens_est,
            len(self._conversation_history), message_tokens_est, total_est,
        )

        return messages

    def _build_function_calling_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Streamlined system prompt for the agentic function-calling path.
        """
        user_name = context.get('user_name', 'there')
        profile = context.get('profile', {})
        stats = context.get('system_stats', {})
        docs_ctx = context.get('docs_context', {})

        skills = ', '.join(profile.get('skills', [])) if profile.get('skills') else 'Not set'
        goals = profile.get('goals', 'Not set') or 'Not set'

        agent_count = stats.get('agent_count', 92)
        spider_count = stats.get('spider_count', 77)

        prompt_parts = [
            f"You are the Personal Assistant for {user_name} on the Donkey Betz Unified AI Platform.",
            "",
            "PLATFORM IDENTITY:",
            "This is NOT a simple chatbot. It is a fully autonomous AI operations platform with:",
            f"- {agent_count} AI Agents running autonomously on scheduled tasks (research, writing, analysis, publishing, market intelligence, sports analytics, legal drafting, and more)",
            f"- {spider_count} Data Spiders continuously scraping real-time data (news, crypto, stocks, sports odds, jobs, legislation, Reddit, etc.)",
            "- Multi-Agent Deliberation: structured panels, debates, brainstorms with 3-reviewer quality gates",
            "- Autonomous Content Pipeline: draft → citation → review panel → quality gate → enhance → publish",
            "- Initiative Pipeline: 5-stage project management running end-to-end autonomously",
            "- 4 Intelligence Desks (Stocks, Sports, Blockchain, Narrative) coordinating specialized agents daily",
            "- 25 Legendary Advisors (Warren Buffett, Cathie Wood, etc.) providing domain expertise",
            "- Signal Intelligence: spider data → signal clustering → auto-topic generation → initiatives",
            "- 9 Body Systems monitoring platform health (HEART, LUNGS, BRAIN, SPINE, etc.)",
            "- Sports Betting Pipeline: odds collection, ML predictions, score tracking, accuracy reporting",
            "- Creative Studio: image generation, video production, talking-head characters, audio, 3D, DaVinci Resolve integration",
            "- Learning loops where agent performance feeds back into future executions",
            "Agents don't wait for prompts — they run on schedules, research, write, review each other's work, and publish. You are the human interface to this autonomous system.",
            "",
            "TOOL USAGE:",
            "You have tools to query and act on all platform data.",
            "Call tools when you need data. Do NOT guess or fabricate data.",
            "You can call multiple tools in sequence if needed.",
            "After getting tool results, provide a concise, conversational summary.",
            "",
            "MEDIA FORMATTING:",
            "When a tool returns generated media (images, videos, audio):",
            "- Show images inline using markdown: ![description](url)",
            "- For videos/audio, say 'Your [type] is ready!' and link to the Media library: [View in Media Library](/media)",
            "- NEVER dump raw Cloudinary or Resolve node URLs as plain text",
            "- If a job is still processing (mode=async), tell the user it's generating and they'll be notified when ready",
            "- For job status results, summarize the status conversationally instead of showing raw JSON",
            "If the user refers to items from a previous response (e.g. '#2', 'the first one'), "
            "use your conversation history to resolve the reference.",
            "",
            "USER PROFILE:",
            f"- Skills: {skills}",
            f"- Goals: {goals}",
            "",
            "PLATFORM STATS:",
            f"- {agent_count} Agents | {spider_count} Spiders | 25 Advisors",
        ]

        # Inject persistent memory context
        try:
            from core.services.memory_context_service import get_memory_context_service
            memory_svc = get_memory_context_service()
            memory_context = memory_svc.get_prompt_context(self.user)
            if memory_context:
                prompt_parts.append("")
                prompt_parts.append("YOUR MEMORY (things the user asked you to remember):")
                prompt_parts.append(memory_context)
                # OpsRun event for memory injection
                from core.tools.ops_run_tracker import get_active_tracker
                tracker = get_active_tracker()
                if tracker:
                    tracker.info('memory_injected', {
                        'user_id': str(self.user.id),
                        'chars': len(memory_context),
                    })
        except Exception as e:
            logger.debug(f"[PA] Memory context injection skipped: {e}")

        # Add docs context summary if available
        if docs_ctx.get('has_docs'):
            docs_summary = docs_ctx.get('summary', '')
            if docs_summary:
                prompt_parts.append("")
                prompt_parts.append(f"RELEVANT DOCS: {docs_summary[:500]}")

        # Add workspace/codebase context if available
        ws_ctx = context.get('workspace_context', {})
        if ws_ctx:
            parts = []
            tech = ws_ctx.get('tech_stack', {})
            if tech:
                tech_items = list(tech.values())[:8] if isinstance(tech, dict) else list(tech)[:8]
                parts.append(f"Tech: {', '.join(str(t) for t in tech_items)}")
            key_files = ws_ctx.get('key_files', {})
            if key_files:
                kf_items = list(key_files.values())[:10] if isinstance(key_files, dict) else list(key_files)[:10]
                parts.append(f"Key files: {', '.join(str(f) for f in kf_items)}")
            if ws_ctx.get('total_files'):
                parts.append(f"{ws_ctx['total_files']} total files")
            if parts:
                prompt_parts.append("")
                prompt_parts.append(f"CODEBASE: {' | '.join(parts)}")

        # Append learned tool insights (approved PAToolInsights)
        try:
            from core.services.pa_tool_learning_enricher import PAToolLearningEnricher
            tool_insights = PAToolLearningEnricher().enrich({})
            if tool_insights:
                prompt_parts.append("")
                prompt_parts.append(tool_insights)
        except Exception as e:
            logger.debug(f"[PA] Tool learning enricher skipped: {e}")

        return "\n".join(prompt_parts)

    def _infer_intent_from_tools(self, tool_names: List[str]) -> Optional[str]:
        """
        Map tool names back to canonical intent names for the enrichment pipeline.
        """
        from core.services.pa_tool_schemas import TOOL_TO_INTENT_MAP

        for name in tool_names:
            intent = TOOL_TO_INTENT_MAP.get(name)
            if intent:
                return intent
        return 'general'

    async def _build_context(
        self,
        message: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build full context for the request."""
        context = {
            'user_id': self.user.id,  # type: ignore[attr-defined]
            'username': self.user.username,  # type: ignore[attr-defined]
            'user_name': self.user.first_name or self.user.username,  # type: ignore[attr-defined]
            'timestamp': datetime.now().isoformat(),
        }

        # Add conversation history (last 5 turns)
        context['conversation_history'] = self._conversation_history[-10:]

        # Add profile data (must use asyncio.to_thread for sync ORM in async context)
        # 5s timeout: DB connection issues must not block the entire PA request
        try:
            from core.models import ExtendedUserProfile
            profile = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: ExtendedUserProfile.objects.filter(user=self.user).first()
                ),
                timeout=5.0,
            )
            if profile:
                context['profile'] = {
                    'skills': profile.skills or [],  # type: ignore[attr-defined]
                    'experience': profile.experience,  # type: ignore[attr-defined]
                    'goals': profile.goals,  # type: ignore[attr-defined]
                    'work_preference': profile.work_preference,  # type: ignore[attr-defined]
                    'desired_income': profile.desired_income,  # type: ignore[attr-defined]
                    'availability': profile.availability,  # type: ignore[attr-defined]
                }
        except asyncio.TimeoutError:
            logger.warning("Profile load timed out after 5s — skipping")
        except Exception as e:
            logger.warning(f"Failed to load profile: {e}")

        # Add dynamic system knowledge if relevant (3s timeout)
        if self.knowledge_injector:
            try:
                knowledge_context = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.knowledge_injector.get_context_for_query, message
                    ),
                    timeout=3.0,
                )
                if knowledge_context.get('has_dynamic_context'):
                    context['system_knowledge'] = knowledge_context
            except asyncio.TimeoutError:
                logger.warning("Knowledge injection timed out after 3s — skipping")
            except Exception as e:
                logger.warning(f"Failed to inject knowledge: {e}")

        # Add system stats (5s timeout)
        try:
            context['system_stats'] = await asyncio.wait_for(
                self._get_system_stats(),
                timeout=5.0,
            )
        except asyncio.TimeoutError:
            logger.warning("System stats timed out after 5s — skipping")
        except Exception as e:
            logger.warning(f"Failed to get system stats: {e}")

        # Session 943: Inject docs context so PA knows about system architecture,
        # recent sessions, and what we've been working on (5s timeout)
        if self.docs_context_builder:
            try:
                docs_context = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.docs_context_builder.build_context_for_agent,
                        agent_name='personal_assistant',
                        task=message,
                        max_docs=8,
                        include_recent_sessions=True,
                        include_content_snippets=False,  # Keep context size manageable
                        include_critical_docs=True  # Always include CLAUDE.md, 00-START-NEXT-SESSION.md
                    ),
                    timeout=5.0,
                )
                if docs_context.get('has_docs'):
                    context['docs_context'] = docs_context
                    logger.debug(f"[Session 943] PA docs context: {len(docs_context.get('relevant_docs', []))} docs")
            except asyncio.TimeoutError:
                logger.warning("Docs context injection timed out after 5s — skipping")
            except Exception as e:
                logger.debug(f"Failed to inject docs context: {e}")

        # Workspace context (codebase structure from SKIN layer)
        try:
            from core.services.workspace_manager import get_workspace_manager
            manager = get_workspace_manager(self.user)
            workspace = await asyncio.wait_for(
                asyncio.to_thread(manager.get_active_workspace),
                timeout=3.0,
            )
            if workspace:
                ws_ctx = await asyncio.wait_for(
                    asyncio.to_thread(
                        manager.get_workspace_context_for_agent,
                        workspace, 'personal_assistant', message
                    ),
                    timeout=3.0,
                )
                if ws_ctx:
                    context['workspace_context'] = ws_ctx
                    logger.debug(f"PA workspace context: {ws_ctx.get('workspace_name')} ({ws_ctx.get('total_files', 0)} files)")
        except asyncio.TimeoutError:
            logger.warning("Workspace context injection timed out after 3s — skipping")
        except Exception as e:
            logger.debug(f"Failed to inject workspace context: {e}")

        # Merge user-provided context
        context.update(user_context)

        return context

    async def _get_system_stats(self) -> Dict[str, Any]:
        """Get basic system stats for context."""
        stats = {
            'agent_count': 74,
            'spider_count': 77,
            'advisor_count': 25,
        }

        try:
            from core.models_unified_system import Agent, SpiderData, Opportunity
            from django.db.models import Count

            # Real counts
            stats['agent_count'] = await asyncio.to_thread(Agent.objects.count)
            stats['spider_data_count'] = await asyncio.to_thread(SpiderData.objects.count)
            stats['opportunity_count'] = await asyncio.to_thread(
                lambda: Opportunity.objects.filter(status='active').count()
            )
        except Exception as e:
            logger.debug(f"Failed to get real stats: {e}")

        return stats

    def _detect_intent_and_route(self, message: str) -> tuple[Optional[str], Optional[str]]:
        """
        Detect intent and determine routing.

        Returns:
            (intent, tool_name) - tool_name is None if no tool needed
        """
        message_lower = message.lower()

        # Session 1016: Media creation guard — MUST be checked FIRST.
        # "create a YouTube video", "make a video comparing...", "generate an image of..."
        # must route to creation intents even when other keywords like "project" are present.
        # Session 1034: Tightened — "youtube" alone doesn't trigger video generation.
        # "create a comparison for a YouTube video" = research, not video gen.
        # Only trigger when the creation verb directly modifies the media noun.
        creation_verbs = ['create ', 'make ', 'generate ', 'produce ', "let's create",
                          "let's make", "let's generate"]
        if any(cv in message_lower for cv in creation_verbs):
            # Session 1034: Only route to video gen if "video" or "animation" appears near a creation verb,
            # NOT if "youtube" appears anywhere (e.g., "create a script for a YouTube video" = research)
            _video_nouns = ['video', 'animation', 'animate']
            _is_direct_video_creation = any(
                f'{cv}{vn}' in message_lower or f'{cv}a {vn}' in message_lower or f'{cv}an {vn}' in message_lower
                for cv in creation_verbs for vn in _video_nouns
            )
            if _is_direct_video_creation:
                return ('video_creation', 'video_generation_agent')
            if any(media in message_lower for media in [
                'image', 'picture', 'logo', 'banner', 'illustration', 'photo',
            ]):
                return ('image_creation', 'image_generation_agent')
            if any(media in message_lower for media in ['audio', 'sound', 'voice', 'podcast']):
                return ('audio_creation', 'audio_generation_agent')

        # Session 996: Initiative ownership patterns — check BEFORE generic initiative match
        if any(phrase in message_lower for phrase in [
            'assign owner', 'who owns', 'my initiatives', 'unowned initiative',
            'unowned project', 'transfer ownership', 'take ownership',
            'no owner', 'initiatives i own', 'projects i own',
        ]):
            return ('initiatives', 'work_tool')

        # Session 988: Initiative/project patterns — check BEFORE boardroom
        # so "initiative" + "attention" routes to initiatives, not boardroom
        # Session 1016: Tightened "project"/"projects" — bare words are too broad
        # and match "other Agent based project that are popular" (external projects).
        # Now requires context like "my project", "the project", "our projects".
        if any(word in message_lower for word in [
            'initiative', 'initiatives',
            'what are we working on', 'active projects', 'current projects',
            'my project', 'my projects', 'our project', 'our projects',
            'the project', 'the projects', 'this project',
        ]):
            return ('initiatives', 'work_tool')

        # Session 1031: Dream patterns — BEFORE boardroom because "approve dream" contains "approve"
        if any(phrase in message_lower for phrase in [
            'dream', 'dreams', 'dreaming', 'dreamed',
            'what are agents dreaming', 'best ideas',
        ]):
            return ('dreams', 'dream_tool')

        # Session 940: Boardroom patterns (takes precedence for boardroom-specific requests)
        if 'boardroom' in message_lower or any(word in message_lower for word in [
            'draft decision', 'promote decision', 'reject decision', 'canonical'
        ]):
            return ('boardroom', 'governance_tool')

        # Session 1000C: Content-specific review patterns must check BEFORE generic
        # boardroom "review" patterns (which catch "for review", "pending review", etc.)
        content_review_words = ['blog', 'blogs', 'content', 'article', 'articles', 'post', 'posts']
        if any(cw in message_lower for cw in content_review_words):
            review_phrases = ['for review', 'waiting for review', 'needs review',
                              'pending review', 'ready for review', 'to review',
                              'ready to publish', 'review']
            if any(rp in message_lower for rp in review_phrases):
                return ('content_review', 'content_tool')

        # Decision/attention patterns
        # Session 997B: "review" alone is too greedy — matches "review this system" etc.
        # Use phrase-level patterns so we only route when intent is clearly boardroom-related.
        if any(word in message_lower for word in [
            'decision', 'pending', 'attention', 'approve', 'reject',
        ]):
            return ('boardroom', 'governance_tool')
        if any(phrase in message_lower for phrase in [
            'review item', 'review decision', 'review alert', 'needs review',
            'pending review', 'review attention', 'for review', 'items to review',
        ]):
            return ('boardroom', 'governance_tool')

        # Session 969: Recent activity patterns — "what's been going on?"
        if any(phrase in message_lower for phrase in [
            'what\'s been going on', 'what happened', 'what\'s new', 'catch me up',
            'while i was away', 'update me', 'what\'s happening', 'what has happened',
            'bring me up to speed', 'what did i miss',
        ]):
            return ('recent_activity', 'recent_activity_tool')

        # Session 969: System health check patterns — "how's the system?"
        # Session 1000B: Added "system status", "current status"
        if any(phrase in message_lower for phrase in [
            'how\'s the system', 'system ok', 'anything down', 'is everything working',
            'platform health', 'system check', 'are things running', 'is the system',
            'everything ok', 'how is the platform',
            'system status', 'current status', 'current system',
        ]):
            return ('system_health_check', 'ops_tool')

        # Session 970: Surgical moves / deliberation status patterns
        if any(phrase in message_lower for phrase in [
            'surgical moves', 'deliberation status', 'deliberation sessions',
            'verification report', 'moves status', 'what deliberations',
        ]):
            return ('surgical_moves_status', 'surgical_moves_status_tool')

        # Session 969: Error summary patterns — "any errors?"
        if any(phrase in message_lower for phrase in [
            'any errors', 'what failed', 'what broke', 'error log', 'what went wrong',
            'issues today', 'any failures', 'error summary', 'recent errors', 'any problems',
        ]):
            return ('error_summary', 'ops_tool')

        # Session 973: Broad system overview — "how is everything?", "what updates?"
        if any(phrase in message_lower for phrase in [
            'how is everything', 'how\'s everything', 'overall system',
            'platform overview', 'system overview', 'give me a summary',
            'what\'s the state', 'state of the system', 'general status',
            'what updates', 'platform updates', 'system updates',
            'executive summary', 'big picture', 'how is the platform doing',
            'overall status', 'overall health',
        ]):
            return ('system_overview', 'status_snapshot_tool')

        # Session 989: "Tell me about" / "Tell me more about" — item lookup
        # These come from frontend buttons on attention items, decisions, agent outputs.
        # Session 1000B: Route to boardroom lookup instead of LLM hallucination.
        # MUST be checked before content_writing to prevent "draft"/"write" in titles
        # from hijacking to content creation.
        if any(phrase in message_lower for phrase in [
            'tell me about', 'tell me more about',
        ]):
            return ('item_lookup', 'governance_tool')

        # Session 987: Body vitals patterns — specific body-system queries only
        # Generic "health" / "status" were too broad and caught system health queries
        if any(phrase in message_lower for phrase in [
            'body vitals', 'body systems', 'body health', 'organ health',
            'vitals', 'heart system', 'lungs system', 'spine system',
            'immune system', 'digestive system', 'muscular system',
            'brain system', 'skin system', 'circulatory system',
            'body status', 'all systems',
        ]):
            return ('system_health', 'get_body_vitals')

        # Prediction patterns
        if any(word in message_lower for word in [
            'predict', 'prediction', 'forecast'
        ]):
            return ('predictions', 'predictions_tool')

        # Pilot/experiment patterns
        if any(word in message_lower for word in [
            'pilot', 'experiment', 'running', 'gates'
        ]):
            if 'gate' in message_lower:
                return ('gates', 'gates_tool')
            return ('pilots', 'pilots_tool')

        # Session 1035: Legal assistance — MUST be BEFORE user_feedback (which catches
        # "wish" in court orders like "the child wishes to call") and BEFORE
        # research_and_create/content_writing.
        _legal_keywords = [
            'motion', 'custody', 'divorce', 'parenting time', 'parenting plan',
            'child support', 'family law', 'family court', 'court order',
            'jdf form', 'jdf ', 'contempt', 'legal filing', 'file a motion',
            'court case', 'legal case', 'pro se', 'respondent', 'petitioner',
            'child custody', 'visitation', 'legal document', 'legal doc',
            'legal help', 'legal assist', 'legal question', 'legal advice',
            'court filing', 'court form', 'denied motion', 'modify order',
            'enforce order', 'emergency motion', 'restraining order',
            'dissolution', 'separation agreement', 'mediation',
            'meet and confer', 'conferral', 'declaration',
            'temporary orders', 'permanent orders', 'parenting plan',
            'non disparagement', 'non-disparagement',
        ]
        if any(lk in message_lower for lk in _legal_keywords):
            return ('legal_assistance', 'legal_doc_drafter_agent')

        # Session 948: User feedback/issues/complaints - be honest about limitations
        # These are things the PA can't fix with tools - requires code changes
        # IMPORTANT: This must come BEFORE reasoning patterns to avoid false triggers
        feedback_indicators = [
            # Problem statements — Session 1035: tightened bare 'issue' → 'issue with'/'issue is'
            'not working', 'doesn\'t work', 'broken', 'bug',
            'issue with', 'issue is', 'issues with',
            'problem with', 'can\'t access', 'cannot access', 'losing context',
            'context lost', 'context loss', 'disconnect', 'not connected',
            'spread out', 'fragmented',
            # Feature requests disguised as complaints — Session 1035: tightened 'should be'
            'it should be', 'it should', 'need to be', 'would be better', 'wish',
            'why can\'t', 'why isn\'t', 'why doesn\'t',
        ]
        if any(phrase in message_lower for phrase in feedback_indicators):
            # Check if this is actually a fixable issue or needs code changes
            # Session 1035: Expanded from 6 keywords to cover analytical/reporting queries
            fixable_keywords = [
                'approve', 'reject', 'list', 'show', 'what', 'how', 'which', 'where',
                'rank', 'sort', 'order', 'prioritize', 'top ', 'compare',
                'produce', 'create', 'generate', 'build', 'give me', 'provide',
                'analyze', 'analysis', 'report', 'count', 'find', 'check',
            ]
            is_actionable = any(kw in message_lower for kw in fixable_keywords)
            if not is_actionable:
                return ('user_feedback', None)  # No tool - direct honest response

        # Reasoning patterns - only for genuine reasoning requests
        if any(word in message_lower for word in [
            'analyze deeply', 'reflect on', 'think about this'
        ]):
            return ('reasoning', 'reasoning_engine_tool')

        # Session 1030: Sports betting BEFORE generic opportunities — "sports betting opportunities"
        # must route to sports_betting, not opportunities
        if any(phrase in message_lower for phrase in [
            'betting', 'sports betting', 'odds', 'spread', 'moneyline',
            'arbitrage', 'arb ', 'arbs', 'sharp action', 'sharp money',
            'line movement', 'steam move', 'wager', 'wagers', 'parlay',
            'game prediction', 'who will win', 'betting brief',
            'top plays', 'value bet', 'value bets', 'stale line',
        ]):
            return ('sports_betting', 'intelligence_tool')

        # Opportunity patterns
        if any(word in message_lower for word in [
            'opportunity', 'opportunities', 'job', 'gig', 'income'
        ]):
            return ('opportunities', 'opportunity_manager_tool')

        # Deliverables library patterns — save/unsave/browse agent outputs
        if any(phrase in message_lower for phrase in [
            'my deliverables', 'saved deliverables', 'deliverables library',
            'save to library', 'saved items', 'my saved', 'bookmarks',
            'saved outputs', 'unsave deliverable', 'save deliverable',
            'show deliverables', 'list deliverables', 'deliverable stats',
        ]):
            return ('deliverables', 'content_tool')

        # Session 943: Content REVIEW patterns - MUST come before content creation patterns
        # These are for viewing/reviewing existing content, not creating new
        # Session 957: Added blog/report query patterns for "what blogs have been written by agents"
        if any(phrase in message_lower for phrase in [
            'what content', 'content created', 'content been created',
            'show content', 'list content', 'my content', 'created content',
            'content ready', 'ready for review',
            'ready to publish', 'publish content', 'archive content',
            'content stats', 'review content', 'view content',
            # Session 957: Blog/report query patterns
            'what blogs', 'blogs written', 'written by agents', 'agent written',
            'list blogs', 'show blogs', 'blog posts', 'what reports',
            'reports written', 'what has been written', 'produced by agents',
            'agent outputs', 'agent content', 'agent created',
            # Session 986: Blog content reading patterns
            'reading the blog', 'the blog titled', 'blog titled',
            'about the blog', 'blog called', 'read the blog',
            'blog accuracy', 'accurate is the blog', 'accurate is that',
            'about this blog', 'about that blog',
            # Session 1004: Broader blog reference patterns
            'one titled', 'titled "', "titled '", 'is titled',
            'inaccuracy', 'inaccurate', 'factual error', 'factually',
            'fix the blog', 'edit the blog', 'correct the blog',
            'update the blog', 'revise the blog', 'blog has',
            # Session 993: Triage, batch publish/archive patterns
            'triage content', 'triage blogs', 'summarize all blogs',
            'blog triage', 'review all blogs', 'publish all',
            'batch publish', 'batch archive',
            # Session 1030: Broader blog patterns — catch "latest blogs", "blog quality", etc.
            'latest blogs', 'recent blogs', 'my blogs', 'our blogs',
            'blog quality', 'blog stats', 'blog statistics',
            'how many blogs', 'blog count', 'blog performance',
            'publish-ready', 'publish ready',
        ]):
            return ('content_review', 'content_tool')

        # Session 993: Deliberation blog generation
        if any(phrase in message_lower for phrase in [
            'generate a blog', 'generate blog', 'create a deliberated blog',
            'deliberated blog', 'write a blog with review', 'blog with deliberation',
            'full review blog', 'v2 blog', 'generate content',
        ]):
            return ('generate_blog', 'content_tool')

        # Session 943: Brainstorming/Discussion/Panel search patterns
        if any(word in message_lower for word in [
            'brainstorm', 'discussion', 'panel', 'ideas from',
            'what did agents', 'agent ideas', 'think tank',
            'past conversations', 'previous discussion'
        ]):
            return ('brainstorming', 'brainstorm_tool')

        # Content CREATION patterns - come after review patterns
        if any(word in message_lower for word in [
            'create image', 'generate image', 'logo', 'banner'
        ]):
            return ('image_creation', 'image_generation_agent')

        if any(phrase in message_lower for phrase in [
            'talking head', 'talking character', 'talking video',
            'talking avatar',
        ]):
            return ('video_creation', 'studio_tool')

        if any(word in message_lower for word in [
            'create video', 'generate video', 'animate'
        ]):
            return ('video_creation', 'video_generation_agent')

        # Session 1034: Research-and-create — MUST be BEFORE content_writing and research.
        # Catches "research X and create/write Y" patterns where the user wants both
        # research AND content creation in one step, saved as a Deliverable.
        _research_words = ['research', 'look up', 'search', 'find out about', 'investigate']
        _create_words = ['create ', 'write ', 'draft ', 'compose ', 'make ', 'generate ', 'build ']
        _has_research = any(rw in message_lower for rw in _research_words)
        _has_create = any(cw in message_lower for cw in _create_words)
        # Also catch "comparison" / "script" / "report" as implicit creation
        _has_output_noun = any(on in message_lower for on in [
            'comparison', 'script', 'report', 'analysis', 'outline',
            'summary', 'brief', 'proposal', 'plan', 'guide',
        ])
        if _has_research and (_has_create or _has_output_noun):
            return ('research_and_create', 'research_and_create_tool')

        # Content writing - only for actual creation requests
        # Session 989: tightened — bare 'write'/'draft' matched inside item titles
        if any(phrase in message_lower for phrase in [
            'write a ', 'write me ', 'write an ', 'write about ',
            'create content', 'create a blog', 'write a blog',
            'draft a ', 'draft an ', 'draft me ',
            'compose a ', 'compose an ',
            'generate article', 'generate a ',
        ]):
            return ('content_writing', 'content_writer_agent')

        # Session 1030: Agent invocation — BEFORE research (otherwise "ResearchAgent" matches "research")
        import re as _agent_re
        if any(word in message_lower for word in [
            'run agent', 'execute agent', 'use agent', 'ask agent',
        ]):
            return ('agent_execution', 'universal_agent_tool')
        # Session 1030: "run/execute SomethingAgent" — no \b before "agent" since
        # "researchagent" is one word (no word boundary between "research" and "agent")
        if _agent_re.search(r'\b(?:run|execute|invoke|trigger|use|ask)\b.*agent', message_lower):
            return ('agent_execution', 'universal_agent_tool')

        # Research patterns
        if any(word in message_lower for word in [
            'search', 'find', 'research', 'trending',
            'compare', 'comparison', 'vs', 'versus',
            'look up', 'lookup',
        ]):
            return ('research', 'intelligence_tool')

        # Session 943: Initiative-adjacent patterns (fallback for generic terms)
        if any(word in message_lower for word in [
            'pipeline', 'stage', 'action item', 'action items',
        ]):
            return ('initiatives', 'work_tool')

        # Session 988: Crypto / price lookup — route to spider_data (coingecko spider)
        if any(phrase in message_lower for phrase in [
            'btc', 'bitcoin', 'ethereum', 'eth ', 'crypto', 'solana', 'sol ',
            'dogecoin', 'doge', 'xrp', 'bnb', 'cardano', 'ada ',
            'coin price', 'token price', 'crypto price', 'how much is',
        ]):
            return ('crypto_price', 'intelligence_tool')

        # Session 995B: Sports betting — moved to line ~841 (Session 1030, before opportunities)

        # Session 979: Stock intelligence patterns (before spider_data to avoid overlap)
        if any(phrase in message_lower for phrase in [
            'stock', 'stocks', 'market brief', 'market briefs', 'sec filing',
            'sec filings', 'edgar', 'stock intelligence', 'stock alert',
            'stock prediction', 'bull case', 'bear case', 'stock dashboard',
        ]):
            return ('stock_intelligence', 'intelligence_tool')

        # Session 1014: Legislation / congressional bill patterns
        # Session 1015: Added "ask a bill" / RAG question patterns
        if any(phrase in message_lower for phrase in [
            'legislation', 'bills in congress', 'congressional',
            'senate bill', 'house bill', 'what bills', 'any bills',
            'legislation about', 'proposed law', 'legislat',
            'congress is working', 'congressional hearing',
            'passed the senate', 'passed the house', 'bill status',
            'sponsor of', 'cosponsors', 'committee hearing',
            'how does this bill', 'bill affect me', 'ask a bill',
            'explain the bill', 'what does the bill', 'bill impact',
        ]):
            return ('legislation', 'intelligence_tool')

        # Session 948: Spider data patterns — removed bare 'intelligence' (too broad)
        if any(word in message_lower for word in [
            'spider', 'spiders', 'crawl', 'crawled', 'collected data',
            'spider intelligence', 'news feed', 'what have spiders', 'spider data'
        ]):
            return ('spider_data', 'intelligence_tool')

        # Session 948/988: Execution history patterns
        if any(word in message_lower for word in [
            'execution', 'executions', 'agent history', 'what agents did',
            'agent activity', 'recent activity', 'what has been running',
            'agent failures', 'failed agents',
            'agents been doing', 'agents doing', 'what are agents',
            'what have agents', 'agents been up to', 'agent work',
            'agent conversations', 'deliberations',
        ]):
            return ('execution_history', 'execution_history_tool')

        # Session 948: Learning patterns
        if any(word in message_lower for word in [
            'learning', 'learnings', 'learned', 'patterns',
            'what has the system learned', 'system learnings'
        ]):
            return ('learning_patterns', 'learning_patterns_tool')

        # Session 948: View feedback queue
        if any(kw in message_lower for kw in [
            'feedback queue', 'feedback items', 'open feedback',
            'user feedback', 'reported issues', 'bug reports',
            'feature requests', 'what feedback', 'show feedback',
            'list feedback', 'feedback stats'
        ]):
            return ('feedback', 'feedback_tool')

        # Session 987: Revenue / financial tracking
        if any(phrase in message_lower for phrase in [
            'revenue', 'earnings', 'income earned', 'financial performance',
            'how much money', 'how much have', 'revenue stats',
            'revenue breakdown', 'revenue by source',
        ]):
            return ('revenue', 'revenue_tracker_tool')

        # Session 987: Task management
        if any(phrase in message_lower for phrase in [
            'my tasks', 'task list', 'open tasks', 'pending tasks',
            'what tasks', 'task stats', 'show tasks', 'list tasks',
            'what\'s on my plate', 'assigned to me',
        ]):
            return ('task_management', 'task_manager_tool')

        # Session 987: Workspace management
        if any(phrase in message_lower for phrase in [
            'workspace', 'workspaces', 'workspace files', 'list workspaces',
            'my workspace', 'workspace status',
        ]):
            return ('workspace', 'workspace_tool')

        # Session 987: Budget / resource usage
        if any(phrase in message_lower for phrase in [
            'budget', 'resource budget', 'resource usage', 'cost tracking',
            'token budget', 'token usage', 'api cost', 'api spend',
        ]):
            return ('budget', 'check_resource_budget')

        # Session 987: System alerts (distinct from error_summary — alerts are body-system warnings)
        if any(phrase in message_lower for phrase in [
            'system alerts', 'active alerts', 'warning messages',
            'show alerts', 'list alerts', 'any alerts',
            'critical alerts', 'alert summary',
        ]):
            return ('system_alerts', 'get_system_alerts')

        # Session 987: ML analysis
        if any(phrase in message_lower for phrase in [
            'ml status', 'ml engine', 'machine learning',
            'ml analysis', 'ml health', 'decision pattern',
            'detect opportunity', 'cross domain opportunity',
        ]):
            return ('ml_analysis', 'ml_analysis')

        # Session 987: Pipeline orchestrator status
        if any(phrase in message_lower for phrase in [
            'pipeline status', 'pipeline stats', 'pipeline overview',
            'initiative pipeline', 'stage breakdown', 'pipeline stages',
        ]):
            return ('pipeline_status', 'pipeline_orchestrator_tool')

        # Session 1007: Agent introspection — "what can [agent] do?"
        if any(phrase in message_lower for phrase in [
            'what can ', 'what does ', 'describe agent', 'agent capabilities',
            'tell me about agent', 'how does agent', 'what is the ',
            'agent info', 'agent details',
        ]) and any(word in message_lower for word in [
            'agent', 'do', 'does',
        ]):
            # Only if it's asking about a specific agent, not "what can you do"
            if not any(phrase in message_lower for phrase in [
                'what can you', 'what do you', 'your capabilities',
            ]):
                return ('agent_introspection', 'agent_introspection_tool')

        # Session 1007: Scheduled tasks visibility — "what tasks are scheduled?"
        if any(phrase in message_lower for phrase in [
            'scheduled task', 'scheduled tasks', 'celery beat', 'beat schedule',
            'what is scheduled', 'what runs automatically', 'cron', 'periodic task',
            'periodic tasks', 'when does', 'what runs', 'automated tasks',
            'background schedule', 'recurring tasks', 'task schedule',
        ]):
            return ('scheduled_tasks', 'scheduled_tasks_tool')

        # Session 987/988: Self-awareness — PA knows its own capabilities
        # Note: removed 'have access to' (too broad, catches "access to internet")
        if any(phrase in message_lower for phrase in [
            'what can you do', 'what do you do', 'what are you capable',
            'your capabilities', 'what tools do you', 'what areas',
            'what can you access', 'help me with',
            'your features', 'what can i ask',
        ]):
            return ('capabilities', None)

        # Default: no tool, direct response
        return ('general', None)

    def _build_tool_payload(
        self,
        message: str,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build payload for tool execution."""
        # Base payload
        payload: Dict[str, Any] = {
            'query': message,
            'task': message,
            'action': 'list',  # Default action
        }

        # Intent-specific payload adjustments
        # Session 1000B: "Tell me more about" → lookup attention item by title
        if intent == 'item_lookup':
            import re
            # Extract the subject after "tell me (more) about:" or similar
            subject_match = re.search(
                r'(?:tell me (?:more )?about[:\s]+)(.*)',
                message, re.IGNORECASE
            )
            title_query = subject_match.group(1).strip() if subject_match else message
            payload['action'] = 'lookup'
            payload['title_query'] = title_query

        # Session 940: Boardroom tool actions
        # Session 947: Enhanced to extract urgency filters and handle "list critical" patterns
        elif intent == 'boardroom':
            msg_lower = message.lower()
            import re

            # Session 947: Extract urgency level if present
            urgency_map = {
                'critical': 'critical',
                'high': 'high',
                'medium': 'medium',
                'low': 'low',
            }
            detected_urgency = None
            for urgency_word, urgency_value in urgency_map.items():
                if urgency_word in msg_lower:
                    detected_urgency = urgency_value
                    break

            # Determine action based on message
            if 'approve' in msg_lower and 'attention' in msg_lower:
                payload['action'] = 'approve_attention'
            elif 'ignore' in msg_lower and 'attention' in msg_lower:
                payload['action'] = 'ignore_attention'
            elif 'promote' in msg_lower and 'decision' in msg_lower:
                payload['action'] = 'promote_decision'
            elif 'reject' in msg_lower and 'decision' in msg_lower:
                payload['action'] = 'reject_decision'
            elif 'list' in msg_lower and 'decision' in msg_lower:
                payload['action'] = 'list_decisions'
            elif 'list' in msg_lower and ('attention' in msg_lower or detected_urgency):
                # Session 947: "list attention" OR "list critical/high/medium/low"
                payload['action'] = 'list_attention'
            elif 'stats' in msg_lower or 'status' in msg_lower:
                payload['action'] = 'stats'
            else:
                # Default: show stats
                payload['action'] = 'stats'

            # Session 947: Add urgency filter if detected
            if detected_urgency and payload['action'] == 'list_attention':
                payload['urgency'] = detected_urgency

            # Session 947: Extract limit if specified (e.g., "show 20", "list 50")
            limit_match = re.search(r'(?:show|list|top)\s+(\d+)', msg_lower)
            if limit_match:
                payload['limit'] = int(limit_match.group(1))

            # Session 1000B: Support "#N" references (e.g., "approve item #2")
            # that map to the UUID from the last boardroom listing.
            num_match = re.search(r'(?:item|decision)\s*#?(\d{1,2})\b', msg_lower)
            if num_match:
                ref_num = int(num_match.group(1))
                mapped_id = self._last_boardroom_items.get(ref_num)
                if mapped_id:
                    payload['id'] = mapped_id

            # Fallback: extract raw UUID if present (e.g., "approve attention item abc123def0")
            if 'id' not in payload:
                id_match = re.search(r'(?:item|decision|id)\s+([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)

        elif intent == 'decision_management':
            if 'approve' in message.lower():
                payload['action'] = 'decide'
                payload['decision'] = 'approve'
            elif 'reject' in message.lower():
                payload['action'] = 'decide'
                payload['decision'] = 'reject'
            else:
                payload['action'] = 'list'

        elif intent == 'system_health':
            payload['systems'] = ['all']
            payload['include_details'] = True

        elif intent in ['predictions', 'pilots', 'gates']:
            if 'stats' in message.lower():
                payload['action'] = 'stats'
            else:
                payload['action'] = 'list'

        elif intent == 'reasoning':
            if 'trigger' in message.lower() or 'think' in message.lower():
                payload['action'] = 'trigger'
            else:
                payload['action'] = 'thoughts'

        # Session 943: Brainstorming tool payload
        elif intent == 'brainstorming':
            msg_lower = message.lower()
            import re as _bs_re

            # Bulk list action: "list all brainstorm conversations", "export brainstorms"
            if any(kw in msg_lower for kw in ['list all', 'export', 'enumerate', 'bulk']):
                payload['action'] = 'list'
                # Extract offset if present (e.g., "offset 50")
                off_match = _bs_re.search(r'offset\s+(\d+)', msg_lower)
                if off_match:
                    payload['offset'] = int(off_match.group(1))
                # Extract limit if present
                lim_match = _bs_re.search(r'limit\s+(\d+)', msg_lower)
                if lim_match:
                    payload['limit'] = int(lim_match.group(1))
                # Extract days if present
                day_match = _bs_re.search(r'(\d+)\s*days?', msg_lower)
                if day_match:
                    payload['days'] = int(day_match.group(1))

            # Determine action based on message
            elif 'recent' in msg_lower or 'latest' in msg_lower or 'this week' in msg_lower:
                payload['action'] = 'recent'
                payload['days'] = 7
            elif 'stats' in msg_lower or 'statistics' in msg_lower or 'how much' in msg_lower:
                payload['action'] = 'stats'
            elif any(cat in msg_lower for cat in ['competitor', 'customer', 'pricing', 'content', 'product', 'technical', 'marketing']):
                # Category-based search
                payload['action'] = 'by_category'
                for cat in ['competitor', 'customer', 'pricing', 'content', 'product', 'technical', 'marketing']:
                    if cat in msg_lower:
                        payload['category'] = cat
                        break
            else:
                # Default to search with the query
                payload['action'] = 'search'
                # Extract meaningful search terms
                import re
                # Remove common words and extract key terms
                search_terms = re.sub(
                    r'\b(what|did|the|agents?|brainstorm|discuss|panel|about|from|conversations?|ideas?|think)\b',
                    '', msg_lower
                ).strip()
                payload['query'] = search_terms if search_terms else message

        # Session 1030: Agent execution payload — extract agent_name from message
        elif intent == 'agent_execution':
            import re as _ae_re
            msg_lower = message.lower()
            # Match "run ResearchAgent" or "execute TrendAnalysisAgent" etc.
            name_match = _ae_re.search(r'\b(\w+agent)\b', msg_lower)
            if name_match:
                # Convert to PascalCase: "researchagent" -> "ResearchAgent"
                raw = name_match.group(1)
                # Find the original case from the message
                orig_match = _ae_re.search(r'\b(\w+[Aa]gent)\b', message)
                payload['agent_name'] = orig_match.group(1) if orig_match else raw
            # Extract the task description (everything after the agent name)
            task_match = _ae_re.search(
                r'\b(?:run|execute|invoke|trigger|use|ask)\b\s+\w*agent\b\s*(.*)',
                msg_lower, _ae_re.IGNORECASE
            )
            if task_match and task_match.group(1).strip():
                task_text = task_match.group(1).strip()
                # Clean up common prepositions
                task_text = _ae_re.sub(r'^(?:to|on|about|for|with)\s+', '', task_text)
                payload['task'] = task_text
            elif not payload.get('task'):
                payload['task'] = message

        # Session 1031: Dream tool payload
        elif intent == 'dreams':
            import re as _dr_re
            msg_lower = message.lower()

            if 'approve' in msg_lower:
                payload['action'] = 'approve'
            elif any(w in msg_lower for w in ['dismiss', 'reject', 'ignore']):
                payload['action'] = 'dismiss'
            elif any(w in msg_lower for w in ['stats', 'pipeline', 'statistics']):
                payload['action'] = 'stats'
            elif any(w in msg_lower for w in ['detail', 'tell me more', 'full', 'expand']):
                payload['action'] = 'details'
            else:
                payload['action'] = 'list_top'

            # Extract UUID if present
            uuid_match = _dr_re.search(
                r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
                msg_lower,
            )
            if uuid_match:
                payload['id'] = uuid_match.group(1)

        # Session 1034: Research-and-create payload — extract research topic + output type
        elif intent == 'research_and_create':
            import re as _rc_re
            msg_lower = message.lower()

            # Detect the output type from the message
            _output_types = {
                'script': ('script', 'Script'),
                'comparison': ('comparison', 'Comparison'),
                'report': ('report', 'Report'),
                'analysis': ('analysis', 'Analysis'),
                'outline': ('outline', 'Outline'),
                'summary': ('summary', 'Summary'),
                'brief': ('brief', 'Brief'),
                'guide': ('guide', 'Guide'),
                'plan': ('plan', 'Plan'),
                'proposal': ('proposal', 'Proposal'),
                'blog': ('document', 'Blog Post'),
                'article': ('document', 'Article'),
                'post': ('document', 'Post'),
            }
            output_type = 'document'
            output_type_label = 'Content'
            for keyword, (otype, olabel) in _output_types.items():
                if keyword in msg_lower:
                    output_type = otype
                    output_type_label = olabel
                    break

            # If "youtube" or "video" is in context, it's a YouTube script
            if 'youtube' in msg_lower or ('video' in msg_lower and output_type != 'video'):
                output_type = 'script'
                output_type_label = 'YouTube Script'

            # Extract research topic: strip creation verbs and output nouns to isolate the topic
            research_topic = _rc_re.sub(
                r'\b(?:research|search|find|look up|investigate|and|then|please|can you|could you|i want you to|i need you to)\b',
                '', msg_lower
            ).strip()
            research_topic = _rc_re.sub(
                r'\b(?:create|write|draft|make|generate|build|compose)\b',
                '', research_topic
            ).strip()
            research_topic = _rc_re.sub(
                r'\b(?:a |an |the |for |that |which |can be |used as )\b',
                '', research_topic
            ).strip()
            # Clean up extra spaces
            research_topic = _rc_re.sub(r'\s+', ' ', research_topic).strip()
            # If topic got too short, use the full message
            if len(research_topic) < 5:
                research_topic = message

            payload['research_topic'] = research_topic
            payload['output_type'] = output_type
            payload['output_type_label'] = output_type_label

        # Session 943: Content review tool payload
        elif intent == 'content_review':
            msg_lower = message.lower()

            # Session 1030: If message mentions blogs, set type='blog' so handler queries SelfBlog
            if any(bw in msg_lower for bw in ['blog', 'blogs', 'blog post', 'blog posts']):
                payload['type'] = 'blog'

            # Determine action based on message
            # Session 1030: "publish-ready" / "publish ready" → list with filter, NOT publish action
            if any(pr in msg_lower for pr in ['publish-ready', 'publish ready']):
                payload['action'] = 'recent'
                payload['days'] = 30
            elif 'stats' in msg_lower or 'statistics' in msg_lower or 'how many' in msg_lower:
                payload['action'] = 'stats'
            # Session 948: "what content has been created" -> recent action
            # Session 957: Added "written", "blogs", "reports" patterns
            elif any(phrase in msg_lower for phrase in [
                'created', 'been created', 'was created', 'recently created',
                'my content', 'all content', 'recent content',
                # Session 957: Blog/report query patterns should show all recent, not just 'ready'
                'written', 'been written', 'blogs written', 'reports written',
                'what blogs', 'what reports', 'by agents', 'agent outputs',
                'produced by', 'agent created', 'agent content'
            ]):
                payload['action'] = 'recent'
                payload['days'] = 30  # Session 957: Default to 30 days for blog queries
            elif any(kw in msg_lower for kw in ['needs work', 'needs enhancement', 'needs_enhancement', 'needing enhancement', 'blogs to fix', 'blogs to improve']):
                payload['action'] = 'needs_work'
            elif any(kw in msg_lower for kw in ['batch enhance', 'enhance all', 'fix all blogs', 'improve all blogs', 'bulk enhance']):
                payload['action'] = 'batch_enhance'
            elif any(kw in msg_lower for kw in ['revise', 'improve', 'enhance', 'fix this blog', 'edit this blog', 'rewrite']):
                payload['action'] = 'revise'
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
            elif 'publish' in msg_lower:
                payload['action'] = 'publish'
                # Try to extract ID if present
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
            elif 'archive' in msg_lower or 'reject' in msg_lower:
                payload['action'] = 'archive'
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
            # Session 1030: "show me the latest blogs" / "recent blogs" → recent, not details
            elif any(phrase in msg_lower for phrase in [
                'latest', 'recent', 'newest', 'show me',
                'list', 'all blogs', 'show blogs',
            ]):
                payload['action'] = 'recent'
                payload['days'] = 30
            elif 'related' in msg_lower or 'similar' in msg_lower:
                # Session 971: Related blog discovery
                payload['action'] = 'related'
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
            elif 'detail' in msg_lower or 'show' in msg_lower:
                payload['action'] = 'details'
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
            # Session 986: Read/analyze specific blog content by title
            # Session 1004: Added inaccuracy/factual/titled patterns
            elif any(phrase in msg_lower for phrase in [
                'reading', 'read the', 'how accurate', 'accuracy',
                'about the blog', 'blog titled', 'blog called',
                'section titled', 'section called', 'section on',
                'about this blog', 'about that blog',
                'one titled', 'titled "', "titled '", 'is titled',
                'inaccuracy', 'inaccurate', 'factual error', 'factually',
                'fix the blog', 'edit the blog', 'correct the blog',
                'update the blog', 'revise the blog', 'blog has',
            ]):
                payload['action'] = 'read'
                import re
                # Extract blog title from quoted strings or "titled X" patterns
                title_match = (
                    re.search(r'["\u201c]([^"\u201d]+)["\u201d]', message)  # quoted
                    or re.search(r"'([^']{5,})'", message)  # single-quoted (min 5 chars to skip contractions)
                    or re.search(r'(?:blog\s+)?(?:titled|called)\s+(.+?)(?:\s*[-\u2014]\s*|\s+how\b|\s+is\b|\s+has\b|\s+that\b|$)', message, re.IGNORECASE)
                )
                if title_match:
                    payload['title'] = title_match.group(1).strip()
                # Extract section title
                section_match = (
                    re.search(r"section\s+(?:on|titled|called)\s+['\u2018\u201c\"](.*?)['\u2019\u201d\"]", message, re.IGNORECASE)
                    or re.search(r"section\s+(?:on|titled|called)\s+(.+?)(?:\?|$)", message, re.IGNORECASE)
                )
                if section_match:
                    payload['section'] = section_match.group(1).strip().rstrip('?')
            else:
                # Default to list (ready for review)
                payload['action'] = 'list'

            # Extract type filter if mentioned
            # Session 958: Added 'blog' type - queries SelfBlog model
            for content_type in ['blog', 'document', 'report', 'analysis', 'image', 'video', 'audio', 'code']:
                if content_type in msg_lower:
                    payload['type'] = content_type
                    break

        # Session 943: Initiative tool payload
        elif intent == 'initiatives':
            msg_lower = message.lower()

            # Determine action based on message
            # Session 1000C: Bulk operations (check before single-item patterns)
            if any(w in msg_lower for w in ['auto-assign', 'auto assign', 'assign agents', 'bulk assign']):
                payload['action'] = 'bulk_auto_assign'
                if 'clean' in msg_lower or 'archive' in msg_lower:
                    payload['also_cleanup'] = True
            elif any(w in msg_lower for w in ['clean up', 'cleanup', 'archive stale', 'archive duplicate', 'bulk cleanup', 'remove redundant', 'clean redundant']):
                payload['action'] = 'bulk_cleanup'
            elif any(w in msg_lower for w in ['audit', 'classify', 'classification', 'triage']):
                payload['action'] = 'audit'
            elif 'stats' in msg_lower or 'overview' in msg_lower or 'pipeline' in msg_lower:
                payload['action'] = 'stats'
            elif 'action item' in msg_lower or 'next step' in msg_lower or 'todo' in msg_lower:
                payload['action'] = 'action_items'
                # Check for priority filter
                if 'critical' in msg_lower:
                    payload['priority'] = 'critical'
                elif 'high' in msg_lower:
                    payload['priority'] = 'high'
            elif 'detail' in msg_lower or 'about' in msg_lower or 'status of' in msg_lower:
                payload['action'] = 'details'
                # Try to extract name or ID
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
                else:
                    # Try to extract initiative name from quotes or after "about"
                    name_match = re.search(r'(?:about|status of|details on)\s+["\']?([^"\']+)["\']?', msg_lower)
                    if name_match:
                        payload['name'] = name_match.group(1).strip()
            # Session 996: Ownership actions
            elif any(w in msg_lower for w in ['assign owner', 'transfer ownership', 'take ownership']):
                payload['action'] = 'assign_owner'
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
                else:
                    name_match = re.search(r'(?:assign|transfer|ownership)\s+(?:of\s+|to\s+)?["\']?([^"\']+?)["\']?\s+(?:to|from)', msg_lower)
                    if name_match:
                        payload['name'] = name_match.group(1).strip()
                # Extract target: "to ResearchAgent" or "to me"
                agent_match = re.search(r'to\s+(\w+Agent)\b', message)
                if agent_match:
                    payload['agent_name'] = agent_match.group(1)
                elif 'take ownership' in msg_lower or 'to me' in msg_lower:
                    payload['user_name'] = 'me'
                else:
                    user_match = re.search(r'to\s+(\w+)', msg_lower)
                    if user_match:
                        payload['agent_name'] = user_match.group(1)
            elif 'who owns' in msg_lower:
                payload['action'] = 'details'
                import re
                name_match = re.search(r'who owns\s+["\']?(.+?)["\']?\s*\??$', msg_lower)
                if name_match:
                    payload['name'] = name_match.group(1).strip()
            elif any(w in msg_lower for w in ['my initiative', 'my project', 'initiatives i own', 'projects i own']):
                payload['action'] = 'list'
                payload['owner'] = 'me'
            elif any(w in msg_lower for w in ['unowned', 'no owner']):
                payload['action'] = 'list'
                payload['owner'] = 'unowned'
            else:
                # Default to list
                payload['action'] = 'list'

            # Extract stage filter
            import re
            stage_match = re.search(r'stage\s*(\d)', msg_lower)
            if stage_match:
                payload['stage'] = stage_match.group(1)

            # Extract status filter
            if 'completed' in msg_lower:
                payload['status'] = 'COMPLETED'
            elif 'on hold' in msg_lower or 'paused' in msg_lower:
                payload['status'] = 'ON_HOLD'
            elif 'all' in msg_lower:
                payload['status'] = 'all'
            # Default is ACTIVE (handled by tool)

            # Extract purpose filter
            for purpose in ['revenue', 'stability', 'learning', 'expansion', 'maintenance']:
                if purpose in msg_lower:
                    payload['purpose'] = purpose
                    break

            # Extract program filter
            for program in ['growth', 'monetization', 'content', 'infrastructure', 'research']:
                if program in msg_lower:
                    payload['program'] = program
                    break

        # Session 948: Feedback tool payload
        elif intent == 'feedback':
            msg_lower = message.lower()

            if 'stats' in msg_lower or 'summary' in msg_lower or 'how many' in msg_lower:
                payload['action'] = 'stats'
            elif 'all' in msg_lower:
                payload['action'] = 'list'
                payload['status'] = None  # Show all statuses
            else:
                payload['action'] = 'list'
                # Default to open items

        # Session 969: Recent activity tool payload
        elif intent == 'recent_activity':
            import re
            msg_lower = message.lower()
            payload['action'] = 'detailed' if 'detail' in msg_lower else 'summary'
            # Extract hours from message (e.g., "last 6 hours", "past 12h")
            hours_match = re.search(r'(\d+)\s*(?:hour|hr|h)', msg_lower)
            payload['hours'] = int(hours_match.group(1)) if hours_match else 2

        # Session 969: System health tool payload
        elif intent == 'system_health_check':
            msg_lower = message.lower()
            payload['action'] = 'components' if 'component' in msg_lower or 'detail' in msg_lower else 'overview'

        # Session 969: Error summary tool payload
        elif intent == 'error_summary':
            import re
            msg_lower = message.lower()
            payload['action'] = 'detailed' if 'detail' in msg_lower else 'summary'
            hours_match = re.search(r'(\d+)\s*(?:hour|hr|h)', msg_lower)
            payload['hours'] = int(hours_match.group(1)) if hours_match else 4

        # Session 973: Status snapshot payload
        elif intent == 'system_overview':
            payload['action'] = 'snapshot'

        # Session 970: Surgical moves status tool payload
        elif intent == 'surgical_moves_status':
            import re
            msg_lower = message.lower()
            payload['action'] = 'detailed' if 'detail' in msg_lower else 'summary'
            hours_match = re.search(r'(\d+)\s*(?:hour|hr|h)', msg_lower)
            payload['hours'] = int(hours_match.group(1)) if hours_match else 24
            # Check for session_id UUID in message
            uuid_match = re.search(
                r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
                msg_lower,
            )
            if uuid_match:
                payload['session_id'] = uuid_match.group(0)

        # Session 987: Revenue tracker payload
        elif intent == 'revenue':
            msg_lower = message.lower()
            if any(w in msg_lower for w in ['list', 'recent', 'show', 'transactions']):
                payload['action'] = 'list'
            else:
                payload['action'] = 'stats'

        # Session 987: Task manager payload
        elif intent == 'task_management':
            msg_lower = message.lower()
            if 'stats' in msg_lower or 'how many' in msg_lower:
                payload['action'] = 'stats'
            else:
                payload['action'] = 'list'
                if 'high' in msg_lower:
                    payload['priority'] = 'high'
                elif 'critical' in msg_lower:
                    payload['priority'] = 'critical'
                for status_kw in ['pending', 'in_progress', 'completed']:
                    if status_kw.replace('_', ' ') in msg_lower or status_kw in msg_lower:
                        payload['status'] = status_kw
                        break

        # Session 987: Workspace payload
        elif intent == 'workspace':
            msg_lower = message.lower()
            payload['action'] = 'status' if 'status' in msg_lower else 'list'

        # Session 987: Budget payload
        elif intent == 'budget':
            payload['action'] = 'check'

        # Session 987: System alerts payload
        elif intent == 'system_alerts':
            msg_lower = message.lower()
            if 'critical' in msg_lower:
                payload['severity_threshold'] = 'critical'
            elif 'warning' in msg_lower:
                payload['severity_threshold'] = 'warning'
            else:
                payload['severity_threshold'] = 'info'

        # Session 987: ML analysis payload
        elif intent == 'ml_analysis':
            msg_lower = message.lower()
            if 'decision pattern' in msg_lower:
                payload['action'] = 'decision_pattern'
            elif any(w in msg_lower for w in ['detect opportunity', 'cross domain']):
                payload['action'] = 'detect_opportunity'
            else:
                payload['action'] = 'status'

        # Session 987: Pipeline orchestrator payload
        elif intent == 'pipeline_status':
            payload['action'] = 'status'

        # Session 979: Stock intelligence payload
        elif intent == 'stock_intelligence':
            msg_lower = message.lower()
            if any(w in msg_lower for w in ['brief', 'briefs', 'summary']):
                payload['action'] = 'briefs'
            elif any(w in msg_lower for w in ['alert', 'alerts']):
                payload['action'] = 'alerts'
            elif any(w in msg_lower for w in ['predict', 'prediction', 'predictions', 'accuracy']):
                payload['action'] = 'predictions'
            elif any(w in msg_lower for w in ['sec', 'filing', 'edgar']):
                payload['action'] = 'sec_filings'
            else:
                payload['action'] = 'overview'

        # Session 1014: Legislation payload
        # Session 1015: Added ask action for RAG-powered Q&A
        elif intent == 'legislation':
            import re as _re
            # Strip routing prefix added by GovernmentPage chat
            clean_msg = _re.sub(r'^(about\s+)?legislation\s*:?\s*', '', message, flags=_re.IGNORECASE).strip()
            if not clean_msg:
                clean_msg = message  # Fallback if stripping removed everything
            msg_lower = clean_msg.lower()

            bill_match = _re.search(r'(HR|S|HB|SB|HJR|SJR|HRES|SRES)\s*(\d+)', clean_msg.upper())
            if bill_match:
                payload['bill_number'] = f"{bill_match.group(1)} {bill_match.group(2)}"

            # Detect action from phrasing
            if any(w in msg_lower for w in ['trending', 'recent', 'latest', 'active', 'working on']):
                payload['action'] = 'trending'
            elif any(w in msg_lower for w in ['status', 'where is', 'progress']):
                payload['action'] = 'status'
            elif any(w in msg_lower for w in ['summary', 'plain english']):
                payload['action'] = 'summary'
            elif any(w in msg_lower for w in ['overview', 'dashboard', 'stats']):
                payload['action'] = 'overview'
            else:
                # Default to ask (RAG) for questions, search for keywords
                # Ask: conversational questions; Search: bare keyword lookups
                payload['action'] = 'ask'
                payload['query'] = clean_msg

            # For non-ask/non-query actions, extract keyword
            if payload['action'] not in ('ask',) and 'query' not in payload:
                query_text = _re.sub(
                    r'\b(what|which|are|is|any|about|regarding|on|the|bills?|legislation|congress|congressional|in|tell|me|show|find|search|for)\b',
                    '', msg_lower
                ).strip()
                # Clean up leftover punctuation/whitespace
                query_text = _re.sub(r'[^\w\s]', '', query_text).strip()
                query_text = _re.sub(r'\s+', ' ', query_text).strip()
                if query_text and not payload.get('bill_number'):
                    payload['query'] = query_text

        # Session 995B: Sports betting payload
        elif intent == 'sports_betting':
            msg_lower = message.lower()
            if any(w in msg_lower for w in ['arbitrage', 'arb ', 'arbs']):
                payload['action'] = 'arbs'
            elif any(w in msg_lower for w in ['prediction', 'predict', 'who will win', 'game prediction']):
                payload['action'] = 'predictions'
            elif any(w in msg_lower for w in ['sharp action', 'sharp money', 'stale line']):
                payload['action'] = 'sharp_action'
            elif any(w in msg_lower for w in ['line movement', 'steam move', 'line move']):
                payload['action'] = 'line_movements'
            elif any(w in msg_lower for w in ['wager', 'wagers', 'parlay', 'my bets']):
                payload['action'] = 'wagers'
            elif any(w in msg_lower for w in ['odds', 'spread', 'moneyline', 'live odds']):
                payload['action'] = 'live_odds'
            elif any(w in msg_lower for w in ['brief', 'top plays']):
                payload['action'] = 'brief'
            else:
                payload['action'] = 'overview'

        # Session 988: Crypto price lookup — search coingecko spider data
        # Session 1030: Use by_spider (not keyword search) — coingecko stores JSON
        # blobs where coin names may not appear in embedding_text
        elif intent == 'crypto_price':
            msg_lower = message.lower()
            # Map common tickers/names for context in LLM prompt
            crypto_map = {
                'btc': 'bitcoin', 'eth': 'ethereum', 'sol': 'solana',
                'doge': 'dogecoin', 'xrp': 'xrp', 'bnb': 'bnb',
                'ada': 'cardano', 'dot': 'polkadot', 'avax': 'avalanche',
                'matic': 'polygon', 'link': 'chainlink', 'uni': 'uniswap',
            }
            search_term = ''
            for ticker, name in crypto_map.items():
                if ticker in msg_lower or name in msg_lower:
                    search_term = name
                    break
            if not search_term:
                search_term = 'bitcoin'
            payload['action'] = 'by_spider'
            payload['spider_name'] = 'coingecko'
            payload['keyword'] = search_term  # passed for LLM context
            payload['days'] = 3

        # Session 989: Execution history payload — default to 'recent' (valid: recent, by_agent, stats, failures)
        elif intent == 'execution_history':
            msg_lower = message.lower()
            if any(w in msg_lower for w in ['fail', 'error', 'broken']):
                payload['action'] = 'failures'
            elif 'stats' in msg_lower or 'how many' in msg_lower:
                payload['action'] = 'stats'
            else:
                payload['action'] = 'recent'

        # Session 1007: Agent introspection payload — extract agent name from message
        elif intent == 'agent_introspection':
            import re
            msg_lower = message.lower()
            # Try to extract agent name: "what can ImageAgent do?" or "describe the research agent"
            agent_match = re.search(
                r'(?:what (?:can|does) |describe |tell me about |agent info |about )(?:the )?(\w+(?:\s?\w+)?)\s*(?:agent|do\??|does\??)?',
                msg_lower,
            )
            payload['agent_name'] = agent_match.group(1).strip() if agent_match else msg_lower
            payload['action'] = 'describe'

        # Session 1007: Scheduled tasks payload
        elif intent == 'scheduled_tasks':
            msg_lower = message.lower()
            if any(w in msg_lower for w in ['blog', 'content']):
                payload['filter'] = 'content'
            elif any(w in msg_lower for w in ['spider', 'crawl']):
                payload['filter'] = 'spider'
            elif any(w in msg_lower for w in ['desk', 'intelligence', 'brief']):
                payload['filter'] = 'intelligence'
            else:
                payload['filter'] = ''
            payload['action'] = 'list'

        # Session 979: Spider data default — override 'list' which is not a valid action
        elif intent == 'spider_data':
            payload['action'] = 'recent'

        # Add any context
        payload['context'] = context

        return payload

    # --- Session 959: Intelligence enrichment methods ---

    def _tokenize(self, text: str) -> set:
        """Extract lowercase alphanumeric tokens (handles punctuation properly)."""
        return set(re.findall(r'[a-z0-9_]+', text.lower()))

    def _passes_relevance_gate(self, message: str, enrichment_text: str, threshold: float = 0.15) -> bool:
        """Keyword overlap relevance check with regex tokenization."""
        if not enrichment_text:
            return False
        enrich_words = self._tokenize(enrichment_text)
        if len(enrich_words) < 30:
            return False  # Too short to be useful
        msg_words = self._tokenize(message) - self.STOP_WORDS
        if not msg_words:
            return True  # Can't filter, include it
        overlap = len(msg_words & enrich_words)
        return (overlap / len(msg_words)) >= threshold

    async def _enrich_tool_result(
        self,
        message: str,
        intent: str,
        tool_result: Any,
        trace_id: str
    ) -> Dict[str, str]:
        """
        Session 959: Gather intelligence enrichment sections for the current query.

        Returns a dict of named sections (each truncated to its cap).
        One service failure never blocks others.
        """
        sections: Dict[str, str] = {}

        canonical_intent = self.INTENT_ALIASES.get(intent, intent)
        enrichment_services = self.INTENT_ENRICHMENT_MAP.get(canonical_intent, [])

        if not enrichment_services:
            return sections

        is_direct = canonical_intent in self.DIRECT_RELEVANCE_INTENTS

        for service_key in enrichment_services:
            try:
                if service_key == 'intelligence_enricher' and self.intelligence_enricher:
                    result = await asyncio.to_thread(
                        self.intelligence_enricher.enrich_context, message
                    )
                    text = result.get('context_text', '') if isinstance(result, dict) else ''
                    if text:
                        # Session 972: Surface metadata counts from enrichment
                        meta = result.get('metadata', {}) if isinstance(result, dict) else {}
                        if meta:
                            parts = []
                            if meta.get('knowledge_count'):
                                parts.append(f"{meta['knowledge_count']} knowledge")
                            if meta.get('experts_count'):
                                parts.append(f"{meta['experts_count']} experts")
                            if meta.get('trends_count'):
                                parts.append(f"{meta['trends_count']} spider trends")
                            if parts:
                                text += f"\nSources: {', '.join(parts)}"
                        sections['learning_insights'] = text

                elif service_key == 'blog_performance' and self.blog_performance_fn:
                    text = await asyncio.to_thread(
                        self.blog_performance_fn,
                        limit=10, include_learning_rules=True
                    )
                    if text:
                        sections['blog_performance'] = str(text)

                elif service_key == 'domain_context' and self.domain_context_builder:
                    text = await asyncio.to_thread(
                        self.domain_context_builder.build_context, topic=message
                    )
                    if text:
                        if is_direct or self._passes_relevance_gate(message, str(text)):
                            sections['domain_context'] = str(text)

                elif service_key == 'spider_trends' and self.spider_context_builder:
                    result = await asyncio.to_thread(
                        self.spider_context_builder.build_context_for_agent,
                        'personal_assistant', message, hours=48, max_trends=5
                    )
                    text = result.get('summary', '') if isinstance(result, dict) else ''
                    if text:
                        if is_direct or self._passes_relevance_gate(message, text):
                            # Session 972: Surface market data and freshness
                            market_data = result.get('market_data', {}) if isinstance(result, dict) else {}
                            if isinstance(market_data, dict) and market_data.get('summary'):
                                text += f"\nMarket: {market_data['summary']}"
                            freshness = result.get('freshness', {}) if isinstance(result, dict) else {}
                            if isinstance(freshness, dict) and freshness:
                                quality = freshness.get('data_quality', 'unknown')
                                hours = freshness.get('hours_covered', 0)
                                text += f"\nData quality: {quality}, {hours}h window"
                            sections['spider_trends'] = text

                elif service_key == 'advisor' and self.advisor_context_builder:
                    result = await asyncio.to_thread(
                        self.advisor_context_builder.build_context_for_agent,
                        'personal_assistant', message
                    )
                    if isinstance(result, dict) and result.get('key_principles'):
                        principles = result['key_principles'][:3]
                        parts = [
                            f"- {p}" if isinstance(p, str) else f"- {p}"
                            for p in principles
                        ]
                        # Session 972: Surface frameworks, recommendation, advisor names
                        frameworks = result.get('decision_frameworks', [])[:3]
                        if frameworks:
                            parts.append(f"Frameworks: {', '.join(str(f) for f in frameworks)}")
                        approach = result.get('recommended_approach', '')
                        if approach:
                            parts.append(f"Recommendation: {str(approach)[:200]}")
                        advisors = result.get('relevant_advisors', [])
                        if advisors:
                            names = [a.get('name', str(a)) if isinstance(a, dict) else str(a) for a in advisors]
                            parts.append(f"Advisors: {', '.join(names)}")
                        sections['advisor'] = '\n'.join(parts)

                elif service_key == 'strategic_memory':
                    # Session 962 Phase 2: Strategic Memory Service
                    try:
                        from core.services.strategic_memory_service import get_strategic_memory_service
                        svc = get_strategic_memory_service()
                        mem_result = await asyncio.to_thread(
                            svc.format_for_pa, message, 7
                        )
                        if mem_result:
                            sections['strategic_memory'] = mem_result
                    except ImportError:
                        pass

                elif service_key == 'proactive_intelligence' and self.proactive_intelligence_service:
                    pi_result = await asyncio.to_thread(
                        self.proactive_intelligence_service.get_relevant_intelligence,
                        message, None, 3, 24
                    )
                    text = self.proactive_intelligence_service.format_for_prompt(pi_result)
                    if text:
                        if is_direct or self._passes_relevance_gate(message, text):
                            sections['proactive_intelligence'] = text

                # Session 992: Platform Intelligence Briefing
                # Skip relevance gate — only fires for system_overview/execution_history
                # where platform activity is inherently relevant
                elif service_key == 'platform_briefing' and self.platform_briefing_service:
                    text = await asyncio.to_thread(
                        self.platform_briefing_service.get_formatted_briefing
                    )
                    if text:
                        sections['platform_briefing'] = text

            except Exception as e:
                logger.warning(f"[{trace_id}] Enrichment '{service_key}' failed: {e}")

        # Truncate each section to its cap
        for key, text in sections.items():
            cap = self.ENRICHMENT_CAPS.get(key, 600)
            if len(text) > cap:
                sections[key] = text[:cap] + '...'

        return sections

    @staticmethod
    def _get_platform_identity() -> str:
        """Session 1034: Platform self-awareness for PA comparisons and identity questions."""
        return """ABOUT THIS PLATFORM (Donkey Betz Unified AI Platform):
This is NOT a simple chatbot or chat interface. It is a fully autonomous AI operations platform:

- 92 AI Agents that run AUTONOMOUSLY on scheduled Celery tasks — researching, writing, analyzing, and publishing content WITHOUT human prompting. Agents include specialists in market intelligence, content creation, blockchain auditing, sports analytics, legal drafting, narrative analysis, and more.
- 79 Data Spiders that continuously scrape real-time data from the web (news, Reddit, crypto, stocks, jobs, legislation, sports odds, etc.) and feed it into the agent pipeline.
- Multi-Agent Deliberation: Agents hold structured conversations (panels, debates, brainstorms) with 3-reviewer quality panels and a DecisionEnforcer that forces decisions.
- Content Pipeline: Autonomous draft → claims-based citation → 3-reviewer panel → quality gate → auto-enhance → auto-publish. Content is grounded in real spider data with citation tracking.
- Initiative Pipeline: 5-stage project management (Research Brief → Prototype Plan → Evaluation Protocol → Technical Design → Pilot Execution) that runs end-to-end autonomously.
- 4 Intelligence Desks (Stocks, Sports, Blockchain, Narrative) each coordinating 4-9 specialized agents daily.
- 25 Legendary Advisors (Warren Buffett, Cathie Wood, etc.) providing domain expertise injected into agent context.
- Signal Intelligence: Spider data → signal clustering → auto-topic generation → HiveMind sessions → initiatives with full provenance chain.
- 9 Body Systems (health monitoring metaphor): HEART, LUNGS, CIRCULATORY, SPINE, IMMUNE, DIGESTIVE, MUSCULAR, BRAIN, SKIN — each monitoring different platform health dimensions.
- Sports Betting Pipeline: Automated odds collection, ML game predictions, score tracking, prediction evaluation, and accuracy reporting.
- 271 Background Celery Tasks across 7 worker types running continuously.
- Learning loops where agent performance feeds back into future executions.

Key differentiator: This platform ACTS autonomously. Agents don't wait for prompts — they run on schedules, research topics, write content, review each other's work, and publish. The PA (you) is the human interface to this autonomous system."""

    def _build_analytical_prompt(
        self,
        message: str,
        intent: str,
        tool_result: Any,
        enrichment_sections: Dict[str, str],
        user_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Session 959: Build analytical system prompt with enrichment context."""
        # Session 1000C: Concise analytical prompt — no walls of text
        # Session 1034: Added platform identity so PA knows what "this platform" is
        base = f"""You are {user_name}'s personal assistant on the Donkey Betz Unified AI Platform.

{self._get_platform_identity()}

The structured data is already shown to the user above your response.
Add 2-4 sentences of insight: the most important pattern, risk, or next step.
Do NOT repeat numbers, counts, or item lists — the user already sees them.
Do NOT use section headers like KEY INSIGHT, ANALYSIS, or RECOMMENDED ACTIONS.
Be conversational and direct. Use plain text without markdown formatting.
If the answer is straightforward, one sentence is enough.
Only describe features and capabilities that actually exist. Never fabricate connections between subsystems."""

        # Session 1000C: One-liner directives — no multi-line blocks
        intent_directives = {
            'content_review': "Note which items are publish-ready and flag any quality concerns.",
            'opportunities': "Highlight the top 2-3 opportunities worth pursuing first.",
            'initiatives': "Flag any bottlenecks or stale items that need attention.",
            'crypto_price': "Report the price and note if data is stale. One sentence is fine.",
            'spider_data': "Identify the most notable pattern or trend in the data.",
            'execution_history': "Highlight any declining agents or systemic failures.",
            'system_health': "Lead with critical issues and whether things are improving or declining.",
            'boardroom': "Highlight the most urgent item and suggest what to handle first.",
            'stock_intelligence': "Highlight the key bull/bear signal and one actionable step.",
            'legislation': "Highlight the most impactful bill and explain why it matters to everyday people.",
            'system_overview': "Summarize the single most important observation and one action. End with: Want me to drill into any of these?",
            'learning_patterns': "Highlight the highest-confidence pattern and what it means.",
            'feedback': "Prioritize bugs over feature requests. Note recurring themes.",
            'gates': "Highlight blocked or high-risk gates that need action.",
            'pilots': "Assess active pilot performance and flag any stuck ones.",
            'reasoning': "Summarize the key insight from thinking cycles.",
            'recent_activity': "Highlight the most significant recent activity.",
            'error_summary': "Lead with highest-severity issues and recommend fixes.",
            'dreams': "Present dreams as creative proposals. Highlight what makes each interesting. Include the dream ID so the user can reference it.",
        }

        canonical_intent = self.INTENT_ALIASES.get(intent, intent)
        directive = intent_directives.get(canonical_intent, '')

        # Session 986: Override directive when reading specific blog content
        if canonical_intent == 'content_review' and isinstance(tool_result, dict) and tool_result.get('action') == 'read':
            directive = (
                "FOCUS: The user is asking about specific blog content shown above.\n"
                "- Analyze the accuracy and quality of the claims made\n"
                "- Flag any statements that seem unsubstantiated or oversimplified\n"
                "- Note what's well-supported vs speculative\n"
                "- Keep response focused on the content, not metrics"
            )

        parts = [base]
        if directive:
            parts.append(f"\n{directive}")

        # Add enrichment sections (only if non-empty)
        section_labels = {
            'system_brief': 'SYSTEM BRIEF',
            'learning_insights': 'LEARNING INSIGHTS',
            'spider_trends': 'REAL-TIME TRENDS',
            'blog_performance': 'PERFORMANCE CONTEXT',
            'domain_context': 'DOMAIN CONTEXT',
            'advisor': 'ADVISOR PRINCIPLES',
            'strategic_memory': 'STRATEGIC MEMORY',
            'proactive_intelligence': 'PROACTIVE INTELLIGENCE',
            'platform_briefing': 'PLATFORM ACTIVITY',
        }
        for key, label in section_labels.items():
            text = enrichment_sections.get(key, '')
            if text:
                parts.append(f"\n=== {label} ===\n{text}")

        # Session 972: Inject system knowledge (workspace, health, agents, etc.) into tool-based responses
        system_knowledge = context.get('system_knowledge', {})
        if system_knowledge.get('has_dynamic_context') and self.knowledge_injector:
            knowledge_text = self.knowledge_injector.format_for_prompt(system_knowledge)
            if knowledge_text:
                parts.append(knowledge_text)

        # Add the data to analyze
        # Session 1006: Raised from 3000 → 8000; tool results were losing most of their data
        tool_str = str(tool_result)
        if len(tool_str) > 8000:
            tool_str = tool_str[:8000] + '...'

        parts.append(f'\n=== DATA TO ANALYZE ===\nUser asked: "{message}"\nTool returned: {tool_str}')

        return '\n'.join(parts)

    async def _generate_response_from_tool(
        self,
        message: str,
        intent: str,
        tool_result: Any,
        context: Dict[str, Any],
        trace_id: str,
        enrichment_sections: Dict[str, str] = None  # type: ignore[arg-type]
    ) -> str:
        """
        Session 959: Generate response from tool result.

        Always shows structured list first. If enrichment is available,
        appends LLM analytical insight after a separator.
        """
        user_name = context.get('user_name', 'there')
        enrichment_sections = enrichment_sections or {}
        has_enrichment = any(v for v in enrichment_sections.values())

        # Always generate the compact structured list (users need IDs to act)
        structured_output = self._format_tool_result(tool_result, intent, user_name)
        # Session 1000C: Strip markdown for clean plain-text display
        structured_output = self._strip_markdown(structured_output)

        # If we have enrichment, get LLM analysis and APPEND it to structured output
        # Session 977: Cap LLM call at 60s to prevent pipeline stalls
        if has_enrichment:
            system_prompt = self._build_analytical_prompt(
                message, intent, tool_result, enrichment_sections,
                user_name, context
            )
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.llm_enforcer.enforce_real_ai,
                        prompt=f"Analyze and advise on this data: {tool_result}",
                        context=system_prompt,
                        agent_name="UnifiedPA",
                        # Session 977: Changed from "analysis" (medium reasoning, slow) to
                        # "conversation" (low reasoning, fast). The structured data is already
                        # computed; the LLM just needs to summarize, not deep-reason.
                        task_type="conversation",
                        # Session 1000C: Reduced from 4000 to 800 — prompt says
                        # 2-4 sentences, 800 tokens (~600 words) is plenty.
                        max_tokens=800
                    ),
                    timeout=60.0
                )
                if result.get('success'):
                    llm_analysis = self._strip_markdown(result.get('response', ''))
                    if llm_analysis:
                        return f"{structured_output}\n\n---\n\n{llm_analysis}"
            except asyncio.TimeoutError:
                logger.warning(f"[{trace_id}] LLM analysis timed out after 60s, returning structured output")
            except Exception as e:
                logger.warning(f"[{trace_id}] LLM analysis failed: {e}")

        # Fallback: no enrichment or LLM failed
        # For non-structured intents without enrichment, use original LLM summarization
        # Session 987: All intents with proper formatters skip generic LLM fallback
        if intent not in ['initiatives', 'brainstorming', 'content_review',
                          'boardroom', 'decision_management', 'opportunities',
                          'spider_data', 'stock_intelligence', 'legislation',
                          'execution_history',
                          'learning_patterns', 'feedback', 'system_overview',
                          'gates', 'pilots', 'predictions', 'reasoning',
                          'system_health', 'crypto_price',
                          'research_and_create', 'legal_assistance',
                          'task_breakdown']:
            # Session 1034: Include platform identity in fallback so PA knows what "this platform" is
            platform_id = self._get_platform_identity()
            system_prompt = f"""You are {user_name}'s personal assistant on the Donkey Betz Unified AI Platform.

{platform_id}

The user asked: "{message}"
You executed a tool and got this result:
{tool_result}

Generate a helpful, conversational response summarizing this information for {user_name}.
Be concise but informative. Use bullet points for lists.
Address the user by name occasionally."""
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.llm_enforcer.enforce_real_ai,
                        prompt=f"Summarize this tool result: {tool_result}",
                        context=system_prompt,
                        agent_name="UnifiedPA",
                        task_type="conversation",
                        # Session 977: Reduced from 4000 to 2000 to keep PA responses fast
                        max_tokens=2000
                    ),
                    timeout=60.0
                )
                if result.get('success'):
                    return result.get('response', structured_output)
            except asyncio.TimeoutError:
                logger.warning(f"[{trace_id}] LLM fallback timed out after 60s")
            except Exception as e:
                logger.warning(f"[{trace_id}] LLM synthesis fallback failed: {e}")

        return structured_output

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """Session 1000C: Strip markdown formatting for clean plain-text display."""
        import re
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\1', text)
        text = re.sub(r'^#{1,3}\s+', '', text, flags=re.MULTILINE)
        return text

    def _format_tool_result(
        self,
        tool_result: Any,
        intent: str,
        user_name: str
    ) -> str:
        """Simple formatting fallback for tool results."""
        if isinstance(tool_result, dict):
            # Session 1000B: "Tell me more about" item lookup
            if intent == 'item_lookup':
                if not tool_result.get('found'):
                    query = tool_result.get('query', 'that item')
                    return f"I couldn't find a matching item for \"{query}\", {user_name}. It may have been resolved or archived."

                item_type = tool_result.get('item_type', '')
                title = tool_result.get('title', 'Untitled')
                summary = tool_result.get('summary', '')
                source = tool_result.get('source_agent', '')
                urgency = tool_result.get('urgency', '')
                status = tool_result.get('status', '')
                created = tool_result.get('created_at', '')
                ml_rec = tool_result.get('ml_recommendation', '')
                impact = tool_result.get('impact_estimate', '')

                response = f"**{title}**\n\n"

                if summary:
                    response += f"{summary}\n\n"

                details = []
                if urgency:
                    details.append(f"Urgency: {urgency}")
                if status:
                    details.append(f"Status: {status}")
                if source:
                    details.append(f"Source: {source}")
                category = tool_result.get('item_category', '')
                if category:
                    details.append(f"Type: {category}")
                if ml_rec:
                    details.append(f"ML recommendation: {ml_rec}")
                if impact:
                    details.append(f"Impact: {impact}")

                # Decision-specific fields
                rec_stance = tool_result.get('recommended_stance', '')
                if rec_stance:
                    details.append(f"Recommended stance: {rec_stance}")
                impact_area = tool_result.get('impact_area', '')
                if impact_area:
                    details.append(f"Impact area: {impact_area}")

                if details:
                    response += "\n".join(f"- {d}" for d in details)

                # Actionable hint
                if item_type == 'attention' and status == 'pending':
                    response += f"\n\nSay 'approve this' or 'ignore this' to act on it."
                elif item_type == 'decision' and status == 'draft':
                    response += f"\n\nSay 'promote this' or 'reject this' to act on it."

                return response

            # Session 940: Boardroom results
            if intent == 'boardroom':
                action = tool_result.get('action', '')

                if action == 'stats':
                    total = tool_result.get('total_pending', 0)
                    attention = tool_result.get('attention_items', {})
                    decisions = tool_result.get('draft_decisions', {})

                    if total == 0:
                        return f"Great news, {user_name}! Your Boardroom is all clear - no pending items."

                    response = f"Hi {user_name}, your Boardroom has {total} pending items:\n\n"

                    if attention.get('count', 0) > 0:
                        att_count = attention['count']
                        by_urgency = attention.get('by_urgency', {})
                        response += f"**Attention Items:** {att_count}\n"
                        # Session 971: Show all urgency levels
                        for level in ['critical', 'high', 'medium', 'low']:
                            val = by_urgency.get(level, 0)
                            if val > 0:
                                label = level.upper() if level == 'critical' else level
                                response += f"  - {val} {label} urgency\n"

                    # Session 985: Show top critical/high items inline
                    # Session 997B: Added summary preview so users know WHY items need attention
                    # Session 1000B: Use #N numbering instead of UUID snippets
                    top_items = tool_result.get('top_items', [])
                    if top_items:
                        self._last_boardroom_items = {}
                        response += f"\n**Needs your attention now:**\n"
                        for idx, item in enumerate(top_items[:8], 1):
                            item_uuid = str(item.get('id', ''))
                            self._last_boardroom_items[idx] = item_uuid
                            raw_title = str(item.get('title', 'Untitled'))
                            source = item.get('source_agent', '')
                            # Strip redundant agent prefix from title
                            if source and raw_title.startswith(f"{source}: "):
                                raw_title = raw_title[len(source) + 2:]
                            # Truncate at word boundary
                            if len(raw_title) > 70:
                                raw_title = raw_title[:67].rsplit(' ', 1)[0] + '...'
                            urgency = item.get('urgency', '')
                            tag = urgency.upper() if urgency == 'critical' else urgency
                            line = f"  {idx}. **{raw_title}** [{tag}]"
                            if source:
                                line += f" from {source}"
                            # Session 997B: Show summary preview if available
                            summary = str(item.get('summary', '') or '')
                            if summary:
                                preview = summary[:120].rsplit(' ', 1)[0] + ('...' if len(summary) > 120 else '')
                                line += f"\n    _{preview}_"
                            response += line + "\n"

                    if decisions.get('count', 0) > 0:
                        dec_count = decisions['count']
                        by_type = decisions.get('by_type', {})
                        response += f"\n**Draft Decisions:** {dec_count}\n"
                        # Session 971: Show all decision types, not just top 3
                        for dtype, dcount in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                            response += f"  - {dcount} {dtype}\n"

                    response += "\nSay 'list critical' or 'list high' to see more, or 'approve item #1' to act."
                    return response

                elif action in ['list_attention', 'list_decisions']:
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', len(items))
                    filters_applied = tool_result.get('filters_applied', {})

                    if count == 0:
                        filter_desc = ""
                        if filters_applied.get('urgency'):
                            filter_desc = f" with {filters_applied['urgency'].upper()} urgency"
                        return f"No items found{filter_desc}, {user_name}."

                    # Session 947/959: Show items with ML/priority fields
                    # Session 997B: Added summary preview
                    # Session 1000B: Use #N numbering instead of UUID snippets
                    self._last_boardroom_items = {}
                    item_lines = []
                    for idx, item in enumerate(items[:15], 1):
                        item_uuid = str(item.get('id', ''))
                        self._last_boardroom_items[idx] = item_uuid
                        title = item.get('title', item.get('topic', 'Untitled'))[:60]
                        urgency = item.get('urgency', item.get('decision_type', ''))
                        source = item.get('source_agent', '')
                        ml_rec = item.get('ml_recommendation', '')
                        priority = item.get('priority_score') or 0
                        confidence = item.get('ml_confidence')
                        impact = item.get('impact_estimate', '')

                        line = f"{idx}. **{title}**"
                        if urgency:
                            line += f" [{urgency}]"
                        if priority:
                            line += f" (priority: {priority:.1f})"
                        if source:
                            line += f" from {source}"
                        if ml_rec:
                            line += f" - ML: {ml_rec}"
                        if confidence is not None:
                            line += f" (conf: {confidence:.0%})"
                        if impact:
                            line += f" | Impact: {impact}"
                        # Session 997B: Show summary preview
                        summary = str(item.get('summary', '') or '')
                        if summary:
                            preview = summary[:120].rsplit(' ', 1)[0] + ('...' if len(summary) > 120 else '')
                            line += f"\n  _{preview}_"
                        item_lines.append(line)

                    item_list = "\n".join(item_lines)

                    # Build header
                    filter_desc = ""
                    if filters_applied.get('urgency'):
                        filter_desc = f" {filters_applied['urgency'].upper()}"

                    remaining = count - len(items[:15])
                    more_text = f"\n\n*Showing {min(count, 15)} of {count} items.*" if remaining > 0 else ""

                    return f"Found {count}{filter_desc} items:\n\n{item_list}{more_text}\n\nTo act on an item, say 'approve item #1' or 'ignore item #3'."

                elif action in ['approve_attention', 'ignore_attention', 'promote_decision', 'reject_decision']:
                    if tool_result.get('success'):
                        title = tool_result.get('title', tool_result.get('topic', 'Item'))
                        return f"Done! {action.replace('_', ' ').title()}: {title}"
                    else:
                        return f"Failed to {action.replace('_', ' ')}: {tool_result}"

            elif intent == 'decision_management':
                items = tool_result.get('items', [])
                count = tool_result.get('count', len(items))
                if count == 0:
                    return f"Great news, {user_name}! You have no pending decisions right now."
                else:
                    item_list = "\n".join([f"- {item.get('title', 'Untitled')}" for item in items[:5]])
                    return f"Hi {user_name}, you have {count} pending decisions:\n{item_list}"

            elif intent == 'system_health':
                vitals = tool_result.get('vitals', {})
                health = vitals.get('overall_health', 'unknown')
                score = vitals.get('health_score', 0)
                systems = vitals.get('systems', {})

                lines = [f"Body Health: {health.upper()} ({score}%)"]

                if systems:
                    lines.append("")
                    for sys_name, sys_data in systems.items():
                        emoji = sys_data.get('emoji', '?')
                        status = sys_data.get('status', 'unknown')
                        sys_score = sys_data.get('score', 0)
                        error = sys_data.get('error', '')
                        if isinstance(sys_score, float):
                            sys_score = round(sys_score, 1)
                        line = f"{emoji} {sys_name.upper()}: {status} ({sys_score}%)"
                        if error:
                            # Truncate long error messages
                            error_short = error[:80] + '...' if len(error) > 80 else error
                            line += f" — {error_short}"
                        lines.append(line)

                rec = vitals.get('recommendation', '')
                if rec:
                    lines.append(f"\n{rec}")

                return "\n".join(lines)

            # Session 987: Predictions formatter
            elif intent == 'predictions':
                if tool_result.get('deprecated'):
                    return tool_result.get('message', 'Predictions tool is deprecated. Use stock intelligence instead.')
                return str(tool_result)

            # Session 987: Gates formatter
            elif intent == 'gates':
                action = tool_result.get('action', 'list')

                if action == 'list':
                    gates = tool_result.get('gates', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No readiness gates found, {user_name}."

                    response = f"Readiness Gates ({count}):\n\n"
                    for idx, gate in enumerate(gates[:10], 1):
                        summary = (gate.get('summary') or 'No summary')[:50]
                        status = gate.get('status', 'unknown')
                        risk = gate.get('risk_level', '')
                        topic = gate.get('topic', '')[:30]
                        risk_badge = f" [{risk}]" if risk else ""
                        topic_str = f" — {topic}" if topic else ""
                        response += f"{idx}. **{summary}**{topic_str} ({status}{risk_badge})\n"

                    if count > 10:
                        response += f"\n...and {count - 10} more gates."
                    return response

                elif action == 'stats':
                    total = tool_result.get('total', 0)
                    by_status = tool_result.get('by_status', {})
                    by_risk = tool_result.get('by_risk_level', {})

                    response = f"Gate Stats, {user_name}:\n\n"
                    response += f"- **Total gates:** {total}\n"
                    if by_status:
                        status_str = ', '.join(f"{s}: {c}" for s, c in by_status.items())
                        response += f"- **By status:** {status_str}\n"
                    if by_risk:
                        risk_str = ', '.join(f"{r}: {c}" for r, c in by_risk.items())
                        response += f"- **By risk:** {risk_str}\n"
                    return response

                else:
                    return str(tool_result)

            # Session 987: Pilots formatter
            elif intent == 'pilots':
                action = tool_result.get('action', 'list')

                if action in ['list', 'running']:
                    pilots = tool_result.get('pilots', [])
                    count = tool_result.get('count', 0)
                    label = "Running" if action == 'running' else "All"

                    if count == 0:
                        return f"No {'running ' if action == 'running' else ''}pilots found, {user_name}."

                    response = f"{label} Pilots ({count}):\n\n"
                    for idx, pilot in enumerate(pilots[:10], 1):
                        name = (pilot.get('name') or 'Unnamed')[:40]
                        status = pilot.get('status', 'unknown')
                        outcome = pilot.get('outcome', '')
                        outcome_str = f" — {outcome}" if outcome else ""
                        response += f"{idx}. **{name}** ({status}{outcome_str})\n"

                    if count > 10:
                        response += f"\n...and {count - 10} more pilots."
                    return response

                elif action == 'stats':
                    total = tool_result.get('total', 0)
                    by_status = tool_result.get('by_status', {})
                    by_outcome = tool_result.get('by_outcome', {})

                    response = f"Pilot Stats, {user_name}:\n\n"
                    response += f"- **Total pilots:** {total}\n"
                    if by_status:
                        status_str = ', '.join(f"{s}: {c}" for s, c in by_status.items())
                        response += f"- **By status:** {status_str}\n"
                    if by_outcome:
                        outcome_str = ', '.join(f"{o}: {c}" for o, c in by_outcome.items())
                        response += f"- **By outcome:** {outcome_str}\n"
                    return response

                else:
                    return str(tool_result)

            # Session 943: Brainstorming results formatting
            elif intent == 'brainstorming':
                action = tool_result.get('action', '')

                if action == 'list':
                    convos = tool_result.get('conversations', [])
                    total = tool_result.get('total_count', 0)
                    offset = tool_result.get('offset', 0)
                    limit = tool_result.get('limit', 50)
                    has_more = tool_result.get('has_more', False)

                    if total == 0:
                        return f"No brainstorm conversations found in that period, {user_name}."

                    end = offset + len(convos)
                    response = f"**Brainstorm Conversations** — showing {offset + 1}-{end} of {total}\n\n"
                    response += "| # | Type | Topic | Msgs | Participants | Date |\n"
                    response += "|---|------|-------|------|-------------|------|\n"
                    for i, c in enumerate(convos, offset + 1):
                        topic = c.get('topic', '').replace('Discussion:', '').replace('Panel:', '').strip()
                        if len(topic) > 50:
                            topic = topic[:47] + '...'
                        ctype = c.get('type', '?')[0]  # D or P
                        msgs = c.get('message_count', 0)
                        parts = len(c.get('participants', []))
                        date = c.get('started_at', '')[:10]
                        response += f"| {i} | {ctype} | {topic} | {msgs} | {parts} | {date} |\n"

                    if has_more:
                        next_offset = offset + limit
                        response += f"\n{total - end} more — say 'list brainstorm conversations offset {next_offset}' for next page."

                    return response

                elif action == 'search':
                    topic_matches = tool_result.get('topic_matches', [])
                    content_matches = tool_result.get('content_matches', [])
                    total = tool_result.get('total_found', 0)
                    query = tool_result.get('query', '')

                    if total == 0:
                        return f"No brainstorming results found for '{query}', {user_name}."

                    response = f"Found {total} brainstorming results for '{query}':\n\n"

                    if topic_matches:
                        response += "**Relevant discussions:**\n"
                        for m in topic_matches[:3]:
                            topic = m.get('topic', '').replace('Discussion:', '').replace('Panel:', '').strip()
                            response += f"- {topic[:60]}\n"

                    if content_matches:
                        response += "\n**Matching ideas:**\n"
                        for m in content_matches[:3]:
                            msg = m.get('matching_message', '')[:100]
                            agent = m.get('agent', 'Unknown')
                            response += f"- {agent}: \"{msg}...\"\n"

                    return response

                elif action == 'recent':
                    discussions = tool_result.get('discussions', [])
                    panels = tool_result.get('panels', [])
                    total_d = tool_result.get('total_discussions', 0)
                    total_p = tool_result.get('total_panels', 0)

                    response = f"Recent brainstorming activity ({tool_result.get('period_days', 7)} days):\n\n"
                    response += f"**{total_d} Discussions, {total_p} Panels**\n\n"

                    if discussions:
                        response += "Recent discussions:\n"
                        for d in discussions[:3]:
                            response += f"- {d.get('topic', 'Untitled')[:50]} ({d.get('date', '')})\n"

                    if panels:
                        response += "\nRecent panels:\n"
                        for p in panels[:3]:
                            response += f"- {p.get('topic', 'Untitled')[:50]} ({p.get('date', '')})\n"

                    return response

                elif action == 'stats':
                    total = tool_result.get('total_brainstorming', 0)
                    discussions = tool_result.get('total_discussions', 0)
                    panels = tool_result.get('total_panels', 0)
                    keywords = tool_result.get('top_keywords', [])

                    response = f"Brainstorming stats ({tool_result.get('period_days', 30)} days):\n\n"
                    response += f"- Total sessions: {total}\n"
                    response += f"- Discussions: {discussions}\n"
                    response += f"- Panels: {panels}\n"

                    if keywords:
                        top = ', '.join([k.get('word', '') for k in keywords[:5]])
                        response += f"\nTop topics: {top}"

                    return response

                elif action == 'by_category':
                    category = tool_result.get('category', '')
                    results = tool_result.get('results', [])
                    total = tool_result.get('total_found', 0)

                    if total == 0:
                        return f"No {category} brainstorming found, {user_name}."

                    response = f"Found {total} {category}-related brainstorming sessions:\n\n"
                    for r in results[:5]:
                        topic = r.get('topic', '').replace('Discussion:', '').replace('Panel:', '').strip()
                        response += f"- {topic[:60]}\n"

                    return response

                else:
                    return str(tool_result)

            # Session 943: Content review results formatting
            elif intent == 'content_review':
                action = tool_result.get('action', '')

                if action == 'list':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No content awaiting review, {user_name}. Everything is either published or archived."

                    response = f"Found {count} content items ready for review:\n\n"
                    for item in items[:5]:
                        title = item.get('title', 'Untitled')[:50]
                        content_type = item.get('deliverable_type', 'document')
                        quality = item.get('quality_score') or 0
                        response += f"- {title} ({content_type}, quality: {quality:.0%})\n"

                    if count > 5:
                        response += f"\n...and {count - 5} more."

                    response += "\n\nSay 'show details [id]' to view, or 'publish [id]' to publish."
                    return response

                # Session 948: Recently created content (any status)
                elif action == 'recent':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)
                    period = tool_result.get('period_days', 7)
                    by_status = tool_result.get('by_status', {})

                    if count == 0:
                        return f"No content created in the last {period} days, {user_name}."

                    response = f"Content created in the last {period} days ({count} items):\n\n"

                    for item in items[:8]:
                        title = item.get('title', 'Untitled')[:45]
                        content_type = item.get('deliverable_type', 'document')
                        status = item.get('status', 'unknown')
                        agent = item.get('agent_name', '')
                        quality = item.get('quality_score') or 0

                        status_icon = '✅' if status == 'published' else ('🟢' if status == 'ready' else '📝')
                        response += f"{status_icon} **{title}**\n"
                        response += f"   {content_type}"
                        if agent:
                            response += f" by {agent}"
                        if quality:
                            response += f" ({quality:.0%} quality)"
                        response += f" [{status}]\n"

                    if count > 8:
                        response += f"\n...and {count - 8} more.\n"

                    # Show status breakdown
                    if by_status:
                        status_summary = ', '.join([f"{s}: {c}" for s, c in by_status.items()])
                        response += f"\n**By status:** {status_summary}"

                    return response

                # Session 1042: Blog/content search by title
                elif action == 'search':
                    query = tool_result.get('query', '')
                    total = tool_result.get('total_found', 0)

                    # Handle both unified search (blogs + deliverables) and blog-only search
                    blog_data = tool_result.get('blogs') or tool_result
                    blog_items = blog_data.get('items', []) if isinstance(blog_data, dict) else []
                    deliverable_data = tool_result.get('deliverables', {})
                    deliverable_items = deliverable_data.get('items', []) if isinstance(deliverable_data, dict) else []

                    all_items = blog_items + deliverable_items
                    if not all_items:
                        return f"No content found matching \"{query}\", {user_name}."

                    response = f"Found {len(all_items)} result(s) for \"{query}\":\n\n"
                    for item in all_items[:8]:
                        title = item.get('title', 'Untitled')[:60]
                        status = item.get('status', 'unknown')
                        word_count = item.get('word_count', 0)
                        quality = item.get('quality_score')
                        item_id = str(item.get('id', ''))[:8]

                        status_icon = {'published': '✅', 'approved': '🟢', 'pending_review': '🔵', 'draft': '📝'}.get(status, '⬜')
                        response += f"{status_icon} **{title}**\n"
                        response += f"   [{status}]"
                        if word_count:
                            response += f" · {word_count:,} words"
                        if quality:
                            response += f" · {quality:.0%} quality"
                        response += f" · ID: {item_id}…\n"

                    if len(all_items) > 8:
                        response += f"\n...and {len(all_items) - 8} more."
                    response += "\n\nSay 'show details [id]' for full content."
                    return response

                elif action == 'stats':
                    ready = tool_result.get('ready_for_review', 0)
                    drafts = tool_result.get('drafts', 0)
                    published = tool_result.get('published', 0)
                    by_type = tool_result.get('by_type', {})

                    response = f"Content statistics, {user_name}:\n\n"
                    response += f"- **Ready for review:** {ready}\n"
                    response += f"- **Drafts:** {drafts}\n"
                    response += f"- **Published:** {published}\n"

                    # Session 972: Surface quality aggregate metrics
                    avg_q = tool_result.get('avg_quality')
                    avg_n = tool_result.get('avg_novelty')
                    avg_s = tool_result.get('avg_structure')
                    if avg_q is not None:
                        response += f"\n**Quality Averages:**\n"
                        response += f"- Quality: {avg_q:.0%}\n"
                        if avg_n is not None:
                            response += f"- Novelty: {avg_n:.0%}\n"
                        if avg_s is not None:
                            response += f"- Structure: {avg_s:.0%}\n"
                        pr_count = tool_result.get('publish_ready_count')
                        if pr_count is not None:
                            response += f"- Publish-ready: {pr_count}\n"

                    if by_type:
                        response += "\n**Ready by type:**\n"
                        for t, c in by_type.items():
                            response += f"- {t}: {c}\n"

                    return response

                elif action == 'details':
                    # Session 972: Also surface gate_notes, tone, word_count
                    blog = tool_result.get('blog', tool_result)
                    title = blog.get('title', 'Untitled')
                    content_type = blog.get('content_type', blog.get('type', 'document'))
                    status = blog.get('status', 'unknown')
                    quality = blog.get('quality_score') or 0
                    preview = blog.get('content_preview', '')[:300]
                    item_id = blog.get('id', '')

                    response = f"{title}\n\n"
                    response += f"- Type: {content_type}\n"
                    response += f"- Status: {status}\n"
                    response += f"- Quality: {quality:.0%}\n"
                    novelty = blog.get('novelty_score')
                    structure = blog.get('structure_score')
                    if novelty is not None:
                        response += f"- Novelty: {novelty:.0%}\n"
                    if structure is not None:
                        response += f"- Structure: {structure:.0%}\n"
                    tone = blog.get('tone', '')
                    if tone:
                        response += f"- Tone: {tone}\n"
                    word_count = blog.get('word_count', 0)
                    if word_count:
                        response += f"- Words: {word_count:,}\n"
                    response += f"- Agent: {blog.get('agent_name', 'Unknown')}\n"
                    gate_notes = blog.get('gate_notes', '')
                    if gate_notes:
                        response += f"\n**Editorial Notes:** {gate_notes}\n"
                    response += f"\n**Preview:**\n{preview}..."

                    if status == 'ready':
                        response += f"\n\nSay 'publish this' to publish or 'archive this' to reject."

                    return response

                elif action == 'publish':
                    if tool_result.get('success'):
                        title = tool_result.get('title', 'Content')
                        return f"Published: **{title}**"
                    else:
                        return f"Failed to publish: {tool_result}"

                elif action == 'archive':
                    if tool_result.get('success'):
                        title = tool_result.get('title', 'Content')
                        return f"Archived: **{title}**"
                    else:
                        return f"Failed to archive: {tool_result}"

                # Session 986: Blog content reading
                elif action == 'read':
                    error = tool_result.get('error')
                    if error:
                        available = tool_result.get('available_sections', [])
                        response = f"{error}"
                        if available:
                            response += "\n\nAvailable sections:\n"
                            for h in available:
                                response += f"- {h}\n"
                        return response

                    blog = tool_result.get('blog', {})
                    title = blog.get('title', 'Untitled')
                    quality = blog.get('quality_score')
                    word_count = blog.get('word_count', 0)

                    single_section = tool_result.get('section')
                    sections = tool_result.get('sections', [])

                    if single_section:
                        header = single_section.get('header', '')
                        content = single_section.get('content', '')
                        response = f"**{title}**"
                        if quality is not None:
                            response += f" (quality: {quality:.0%})"
                        response += f"\n\n## {header}\n\n{content}"
                    else:
                        response = f"**{title}**"
                        if quality is not None:
                            response += f" (quality: {quality:.0%}, {word_count:,} words)"
                        response += "\n"
                        for sec in sections:
                            header = sec.get('header', '')
                            content = sec.get('content', '')
                            response += f"\n## {header}\n\n{content}\n"

                    return response

                # Session 971: Related blogs formatting
                elif action == 'related':
                    blog_title = tool_result.get('blog_title', 'Unknown')
                    related = tool_result.get('related', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No related posts found for **{blog_title}**, {user_name}."

                    response = f"Found {count} posts related to **{blog_title}**:\n\n"
                    for item in related:
                        title = item.get('title', 'Untitled')[:60]
                        reason = item.get('relatedness_reason', '')
                        score = item.get('relatedness_score', 0)
                        words = item.get('word_count', 0)
                        reason_badge = (
                            '[Same Project]' if reason == 'same_initiative'
                            else '[Similar Topics]' if reason == 'tag_overlap'
                            else '[Related]'
                        )
                        response += f"- **{title}** {reason_badge} ({words} words, score: {score:.2f})\n"

                    blog_id = tool_result.get('blog_id', '')
                    response += f"\nView in browser: `/blog/{blog_id}`"
                    return response

                # Session 987: Blog revision before/after display
                elif action == 'revise':
                    error = tool_result.get('error')
                    if error:
                        return f"Revision failed: {error}"

                    title = tool_result.get('title', 'Untitled')
                    before = tool_result.get('before', {})
                    after = tool_result.get('after', {})
                    changes = tool_result.get('changes_made', [])
                    gate_notes = tool_result.get('gate_notes', '')

                    def _fmt_score(val):
                        return f"{val:.0%}" if val is not None else "n/a"

                    def _fmt_ready(val):
                        return "Yes" if val else "No"

                    response = f"Blog revised: **{title}**\n\n"
                    response += "**Before → After:**\n"
                    response += f"- Quality: {_fmt_score(before.get('quality'))} → {_fmt_score(after.get('quality'))}\n"
                    response += f"- Novelty: {_fmt_score(before.get('novelty'))} → {_fmt_score(after.get('novelty'))}\n"
                    response += f"- Structure: {_fmt_score(before.get('structure'))} → {_fmt_score(after.get('structure'))}\n"
                    response += f"- Publish ready: {_fmt_ready(before.get('publish_ready'))} → {_fmt_ready(after.get('publish_ready'))}\n"

                    if changes:
                        response += "\n**Changes made:**\n"
                        for change in changes[:8]:
                            response += f"- {change}\n"

                    if gate_notes:
                        response += f"\n**Editorial notes:** {gate_notes}"

                    return response

                # Session 987: Blogs needing enhancement
                elif action == 'needs_work':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)
                    total = tool_result.get('total', 0)

                    if count == 0:
                        return f"No blogs need enhancement right now, {user_name}."

                    response = f"Blogs needing enhancement ({total} total):\n\n"
                    for item in items[:10]:
                        title = (item.get('title') or 'Untitled')[:60]
                        q = item.get('quality_score')
                        notes = (item.get('gate_notes') or '')[:80]
                        q_str = f" (quality: {q:.0%})" if q is not None else ""
                        response += f"- **{title}**{q_str}\n"
                        if notes:
                            response += f"  {notes}\n"

                    response += f"\nSay 'batch enhance' to improve all, or 'revise [id]' for one."
                    return response

                # Session 987: Batch enhancement results
                elif action == 'batch_enhance':
                    total = tool_result.get('total_processed', 0)
                    succeeded = tool_result.get('succeeded', 0)
                    failed = tool_result.get('failed', 0)
                    details = tool_result.get('details', [])

                    if total == 0:
                        return f"No blogs needed enhancement, {user_name}."

                    response = f"Batch enhancement complete:\n\n"
                    response += f"**Processed:** {total} | **Succeeded:** {succeeded} | **Failed:** {failed}\n"

                    if details:
                        response += "\n**Details:**\n"
                        for d in details[:8]:
                            title = (d.get('title') or 'Untitled')[:50]
                            if d.get('success'):
                                changes = d.get('changes', [])
                                change_str = f" ({len(changes)} changes)" if changes else ""
                                response += f"- {title}{change_str}\n"
                            else:
                                response += f"- {title} — FAILED: {d.get('error', 'unknown')}\n"

                    return response

                else:
                    return str(tool_result)

            # Session 987: Opportunity results formatting
            elif intent == 'opportunities':
                action = tool_result.get('action', '')

                if action == 'list':
                    items = tool_result.get('opportunities', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No active opportunities found, {user_name}."

                    # Deduplicate by title (keep first occurrence)
                    seen_titles = set()
                    unique_items = []
                    for item in items:
                        title = item.get('title', '')
                        if title not in seen_titles:
                            seen_titles.add(title)
                            unique_items.append(item)

                    response = f"Found {count} opportunities ({len(unique_items)} unique):\n\n"
                    for idx, item in enumerate(unique_items[:10], 1):
                        title = item.get('title', 'Untitled')[:55]
                        opp_type = (item.get('opportunity_type') or 'unknown').replace('_', ' ')
                        score = item.get('match_score', 0)
                        response += f"{idx}. **{title}** ({opp_type}, match: {score}%)\n"

                    if len(unique_items) > 10:
                        response += f"\n...and {len(unique_items) - 10} more unique opportunities."

                    return response

                elif action == 'stats':
                    total = tool_result.get('total', 0)
                    by_status = tool_result.get('by_status', {})
                    by_type = tool_result.get('by_type', {})
                    revenue = tool_result.get('total_potential_revenue', '0')

                    response = f"Opportunity stats, {user_name}:\n\n"
                    response += f"- **Total:** {total}\n"
                    response += f"- **Potential revenue:** ${revenue}\n"
                    if by_status:
                        status_str = ', '.join(f"{s}: {c}" for s, c in by_status.items())
                        response += f"- **By status:** {status_str}\n"
                    if by_type:
                        type_str = ', '.join(f"{t.replace('_', ' ')}: {c}" for t, c in by_type.items())
                        response += f"- **By type:** {type_str}\n"

                    return response

                elif action == 'get':
                    opp = tool_result.get('opportunity', {})
                    title = opp.get('title', 'Untitled')
                    desc = opp.get('description', '')[:200]
                    opp_type = (opp.get('opportunity_type') or 'unknown').replace('_', ' ')
                    score = opp.get('match_score', 0)
                    revenue = opp.get('potential_revenue', '0')

                    response = f"**{title}**\n\n"
                    response += f"- Type: {opp_type}\n"
                    response += f"- Match score: {score}%\n"
                    response += f"- Potential revenue: ${revenue}\n"
                    if desc:
                        response += f"\n{desc}..."

                    return response

                else:
                    return str(tool_result)

            # Session 943: Initiative results formatting
            elif intent == 'initiatives':
                action = tool_result.get('action', '')

                if action == 'list':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)
                    total_count = tool_result.get('total_count', count)

                    if count == 0:
                        return f"No initiatives found matching your criteria, {user_name}."

                    if total_count > count:
                        response = f"**{total_count} initiatives** (showing {count}):\n\n"
                    else:
                        response = f"**{count} initiatives:**\n\n"

                    display_limit = 25
                    for i, item in enumerate(items[:display_limit]):
                        name = item.get('name', 'Untitled')[:80]
                        hid = item.get('human_id') or f"#{i + 1}"
                        stage = item.get('current_stage', 1)
                        purpose = item.get('purpose', 'unknown')
                        pending = item.get('pending_actions', 0)
                        critical = item.get('critical_actions', 0)
                        last_activity = item.get('last_activity_at')
                        owner = item.get('owner')
                        # Compact detail line
                        details = f"Stage {stage}/5"
                        if owner:
                            details += f" | {owner}"
                        if pending > 0:
                            details += f" | {pending} actions"
                            if critical > 0:
                                details += f" ({critical} critical)"
                        if not last_activity:
                            details += " | no activity"
                        response += f"- **{hid}** — {name}\n   {details}\n\n"

                    if count > display_limit:
                        response += f"...and {count - display_limit} more.\n"

                    return response

                elif action == 'audit':
                    total = tool_result.get('total', 0)
                    c = tool_result.get('classification', {})
                    real = c.get('real', {})
                    stalled = c.get('stalled', {})
                    noise_data = c.get('noise', {})
                    dupes = c.get('duplicates', {})

                    response = f"Initiative Audit ({total} total), {user_name}:\n\n"

                    response += f"**Real** (progressing or active): {real.get('count', 0)}\n"
                    for item in real.get('items', [])[:5]:
                        response += f"  - {item['name'][:80]} (Stage {item.get('stage', 1)}/5)\n"

                    response += f"\n**Stalled** (Stage 1, no activity, >14 days): {stalled.get('count', 0)}\n"
                    for item in stalled.get('items', [])[:3]:
                        response += f"  - {item['name'][:80]}\n"

                    response += f"\n**Noise** (recent, no engagement): {noise_data.get('count', 0)}\n"

                    response += f"\n**Duplicates**: {dupes.get('count', 0)} items in {dupes.get('cluster_count', 0)} clusters\n"
                    for cluster in dupes.get('clusters', [])[:5]:
                        response += f"  - \"{cluster['primary'][:60]}\" ({cluster['count']} copies)\n"

                    cleanup = stalled.get('count', 0) + noise_data.get('count', 0) + dupes.get('count', 0)
                    if cleanup > 0:
                        response += f"\n{cleanup} initiatives are candidates for cleanup."
                        if dupes.get('count', 0) > 0:
                            response += f" Run `consolidate_duplicate_initiatives --fix` to merge {dupes['count']} duplicates."

                    return response

                elif action == 'stats':
                    active = tool_result.get('active', 0)
                    completed = tool_result.get('completed', 0)
                    on_hold = tool_result.get('on_hold', 0)
                    by_stage = tool_result.get('by_stage', {})
                    pending_actions = tool_result.get('pending_action_items', 0)
                    critical_actions = tool_result.get('critical_action_items', 0)

                    response = f"Initiative Pipeline Overview, {user_name}:\n\n"
                    response += f"**Status:**\n"
                    response += f"- 🟢 Active: {active}\n"
                    response += f"- ✅ Completed: {completed}\n"
                    response += f"- ⏸️ On Hold: {on_hold}\n\n"

                    response += f"**By Stage:**\n"
                    for stage_key, count in by_stage.items():
                        stage_num = stage_key.replace('stage_', '')
                        response += f"- Stage {stage_num}: {count}\n"

                    response += f"\n**Action Items:**\n"
                    response += f"- Pending: {pending_actions}\n"
                    if critical_actions > 0:
                        response += f"- 🚨 Critical: {critical_actions}\n"

                    return response

                elif action == 'details':
                    name = tool_result.get('name', 'Unknown')
                    hid = tool_result.get('human_id')
                    description = tool_result.get('description', '')[:200]
                    status = tool_result.get('status', 'unknown')
                    stage = tool_result.get('current_stage', 1)
                    purpose = tool_result.get('purpose', 'unknown')
                    program = tool_result.get('program', 'unknown')
                    action_items = tool_result.get('action_items', [])

                    status_icon = '🟢' if status == 'ACTIVE' else ('✅' if status == 'COMPLETED' else '⏸️')

                    owner = tool_result.get('owner')

                    header = f"**{hid}** — {name}" if hid else f"**{name}**"
                    response = f"{status_icon} {header}\n\n"
                    response += f"- Status: {status}\n"
                    response += f"- Stage: {stage}/5\n"
                    response += f"- Purpose: {purpose}\n"
                    response += f"- Program: {program}\n"
                    response += f"- Owner: {owner or 'unassigned'}\n"

                    if description:
                        response += f"\n**Description:** {description}...\n"

                    # Session 1021: Render stage pipeline with document status
                    stages = tool_result.get('stages', [])
                    if stages:
                        response += f"\n**Stage Pipeline:**\n"
                        for s in stages:
                            stage_num = s.get('stage', '?')
                            stage_name = s.get('stage_name', f'Stage {stage_num}')
                            stage_status = s.get('status', 'PENDING')
                            status_icon = {'APPROVED': '✅', 'DRAFT': '📝', 'IN_REVIEW': '👀', 'PENDING': '⏳', 'REJECTED': '❌', 'BLOCKED': '🚫'}.get(stage_status, '⏳')
                            doc_len = s.get('document_length')
                            doc_info = f" ({doc_len:,} chars)" if doc_len else " (no document)"
                            response += f"{status_icon} Stage {stage_num}: {stage_name} — {stage_status}{doc_info}\n"
                            doc_preview = s.get('document_preview', '')
                            if doc_preview and stage_status in ('DRAFT', 'IN_REVIEW'):
                                response += f"   Preview: {doc_preview[:150]}...\n"

                    if action_items:
                        response += f"\n**Action Items ({len(action_items)}):**\n"
                        for item in action_items[:5]:
                            priority_icon = '🔴' if item.get('priority') == 'critical' else ('🟠' if item.get('priority') == 'high' else '⚪')
                            response += f"{priority_icon} {item.get('title', 'Untitled')[:50]} ({item.get('status', 'pending')})\n"

                    return response

                elif action == 'action_items':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No pending action items found, {user_name}. Great job!"

                    response = f"Found {count} action items:\n\n"
                    for item in items[:10]:
                        priority_icon = '🔴' if item.get('priority') == 'critical' else ('🟠' if item.get('priority') == 'high' else '⚪')
                        initiative = item.get('initiative_name', 'Unknown')[:25]
                        title = item.get('title', 'Untitled')[:40]
                        response += f"{priority_icon} **{title}**\n"
                        response += f"   └─ {initiative} ({item.get('status', 'pending')})\n"

                    return response

                elif action == 'assign_owner':
                    name = tool_result.get('name', 'Unknown')
                    old_owner = tool_result.get('old_owner', 'unowned')
                    new_owner = tool_result.get('new_owner', 'unknown')
                    return f"Done. **{name}** is now owned by **{new_owner}** (was: {old_owner})."

                elif action == 'update_status':
                    name = tool_result.get('name', 'Unknown')
                    return f"Updated **{name}** status: {tool_result.get('old_status')} → {tool_result.get('new_status')}."

                elif action == 'advance':
                    name = tool_result.get('name', 'Unknown')
                    return tool_result.get('message', f"Advanced **{name}**.")

                elif action == 'complete_action_item':
                    title = tool_result.get('title', 'Unknown')
                    init_name = tool_result.get('initiative_name', '')
                    return f"Completed action item **{title}** on {init_name}."

                elif action == 'flow_metrics':
                    cr = tool_result.get('creation_rate', {})
                    bl = tool_result.get('backlog', {})
                    sd = tool_result.get('stage_distribution', {})
                    cb = tool_result.get('circuit_breaker', {})
                    response = f"**Pipeline Health**, {user_name}:\n\n"
                    response += f"**Creation Rate:** {cr.get('last_24h', 0)} (24h) / {cr.get('last_7d', 0)} (7d)\n"
                    response += f"**Backlog:** {bl.get('active', 0)} active, {bl.get('triage', 0)} triage, {bl.get('no_activity', 0)} dormant\n"
                    response += f"**Stages:** "
                    response += " | ".join(f"S{k.replace('stage_', '')}: {v}" for k, v in sd.items())
                    response += "\n"
                    cb_status = "paused" if cb.get('paused') else f"{cb.get('utilization_pct', 0):.0f}% utilized"
                    response += f"**Circuit Breaker:** {cb_status} ({cb.get('pending', 0)}/{cb.get('threshold', 0)})\n"
                    response += f"**Completed (7d):** {tool_result.get('completed_last_7d', 0)}\n"
                    return response

                # Session 1000C: Bulk operation formatters
                elif action == 'bulk_auto_assign':
                    assigned = tool_result.get('assigned', 0)
                    skipped = tool_result.get('skipped', 0)
                    dry_run = tool_result.get('dry_run', False)
                    assignments = tool_result.get('assignments', [])
                    prefix = "**[DRY RUN]** " if dry_run else ""
                    response = f"{prefix}Auto-assigned {assigned} initiatives ({skipped} already owned):\n\n"
                    for a in assignments[:15]:
                        response += f"- **{a.get('name', '')[:60]}** → {a.get('agent', '')}\n"
                    if assigned > 15:
                        response += f"\n...and {assigned - 15} more.\n"
                    # Combined cleanup results
                    cleanup = tool_result.get('cleanup')
                    if cleanup:
                        total_cleaned = cleanup.get('total_cleaned', 0)
                        response += f"\n**Cleanup:** archived {total_cleaned} initiatives"
                        st = cleanup.get('stalled', {})
                        ns = cleanup.get('noise', {})
                        dp = cleanup.get('duplicates', {})
                        parts = []
                        if st.get('count', 0):
                            parts.append(f"{st['count']} stalled")
                        if ns.get('count', 0):
                            parts.append(f"{ns['count']} noise")
                        if dp.get('count', 0):
                            parts.append(f"{dp['count']} duplicates in {dp.get('cluster_count', 0)} clusters")
                        if parts:
                            response += f" ({', '.join(parts)})"
                        response += ".\n"
                    return response

                elif action == 'bulk_cleanup':
                    dry_run = tool_result.get('dry_run', False)
                    total = tool_result.get('total_cleaned', 0)
                    st = tool_result.get('stalled', {})
                    ns = tool_result.get('noise', {})
                    dp = tool_result.get('duplicates', {})
                    prefix = "**[DRY RUN]** " if dry_run else ""
                    response = f"{prefix}Cleaned up {total} initiatives:\n\n"
                    if st.get('count', 0):
                        response += f"**Stalled** ({st['count']} archived):\n"
                        for name in st.get('items', [])[:5]:
                            response += f"  - {name}\n"
                        response += "\n"
                    if ns.get('count', 0):
                        response += f"**Noise** ({ns['count']} archived):\n"
                        for name in ns.get('items', [])[:5]:
                            response += f"  - {name}\n"
                        response += "\n"
                    if dp.get('count', 0):
                        response += f"**Duplicates** ({dp['count']} archived, {dp.get('cluster_count', 0)} clusters):\n"
                        for name in dp.get('items', [])[:5]:
                            response += f"  - {name}\n"
                        response += "\n"
                    if total == 0:
                        response = f"No initiatives needed cleanup, {user_name}. Pipeline is clean."
                    return response

                else:
                    return str(tool_result)

            # Session 948/989: Spider data results formatting
            # Session 989: Fixed field names to match actual SpiderData model
            elif intent == 'spider_data':
                action = tool_result.get('action', '')

                if action == 'recent':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)
                    period = tool_result.get('days_back', 7)

                    if count == 0:
                        return f"No spider data collected in the last {period} days, {user_name}."

                    response = f"Spider intelligence from the last {period} days ({count} items):\n\n"
                    for item in items[:8]:
                        spider = item.get('spider_name', 'Unknown')
                        data_type = item.get('data_type', '')
                        source_url = item.get('source_url', '')
                        date = str(item.get('created_at', ''))[:16]
                        response += f"- **{spider}** ({date})"
                        if data_type:
                            response += f" [{data_type}]"
                        if source_url:
                            response += f" — {source_url[:60]}"
                        response += "\n"

                    if count > 8:
                        response += f"\n...and {count - 8} more items."
                    return response

                elif action == 'by_spider':
                    spider = tool_result.get('spider_name', 'Unknown')
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No data from {spider} spider, {user_name}."

                    response = f"Data from **{spider}** spider ({count} items):\n\n"
                    for item in items[:6]:
                        embed_text = item.get('embedding_text', '')
                        summary = embed_text[:80] + '...' if len(embed_text) > 80 else embed_text
                        date = str(item.get('created_at', ''))[:10]
                        response += f"- {summary or item.get('source_url', 'No data')} ({date})\n"

                    return response

                elif action == 'by_category':
                    category = tool_result.get('category', 'Unknown')
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No {category} data collected, {user_name}."

                    response = f"**{category.title()}** intelligence ({count} items):\n\n"
                    for item in items[:6]:
                        spider = item.get('spider_name', 'Unknown')
                        source_url = item.get('source_url', '')
                        date = str(item.get('created_at', ''))[:10]
                        response += f"- **{spider}** ({date}) — {source_url[:60]}\n"

                    return response

                elif action == 'search':
                    query = tool_result.get('keyword', tool_result.get('query', ''))
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No spider data matching '{query}', {user_name}."

                    response = f"Found {count} items matching '{query}':\n\n"
                    for item in items[:6]:
                        spider = item.get('spider_name', 'Unknown')
                        embed_text = item.get('embedding_text', '')
                        summary = embed_text[:80] + '...' if len(embed_text) > 80 else embed_text
                        response += f"- **{spider}**: {summary or item.get('source_url', 'No data')}\n"

                    return response

                elif action == 'stats':
                    total = tool_result.get('total_items', 0)
                    days = tool_result.get('days_back', 7)
                    by_spider = tool_result.get('by_spider', {})
                    by_data_type = tool_result.get('by_data_type', tool_result.get('by_category', {}))

                    response = f"Spider Network Stats ({days}d), {user_name}:\n\n"
                    response += f"- **Total collected:** {total}\n\n"

                    if by_spider:
                        response += "**Top spiders:**\n"
                        for spider, cnt in list(by_spider.items())[:5]:
                            response += f"- {spider}: {cnt} items\n"

                    if by_data_type:
                        response += "\n**By data type:**\n"
                        for dt, cnt in list(by_data_type.items())[:5]:
                            response += f"- {dt}: {cnt} items\n"

                    return response

                else:
                    return str(tool_result)

            # Session 988: Crypto price results formatting
            elif intent == 'crypto_price':
                items = tool_result.get('items', [])
                count = tool_result.get('count', 0)
                keyword = tool_result.get('keyword', 'crypto')

                if count == 0:
                    return (
                        f"No recent {keyword} data in the spider network, {user_name}. "
                        f"The CoinGecko spider may not have run recently. "
                        f"Try triggering a spider run or check CoinGecko directly."
                    )

                response = f"**{keyword.title()} Data** from spider network ({count} items):\n\n"
                for item in items[:6]:
                    # Session 989: Use actual SpiderData fields
                    spider = item.get('spider_name', 'Unknown')
                    source_url = item.get('source_url', '')
                    embed_text = item.get('embedding_text', '')
                    date = str(item.get('created_at', ''))[:16]
                    # Extract a summary from embedding_text (first 120 chars)
                    summary = embed_text[:120] + '...' if len(embed_text) > 120 else embed_text
                    response += f"- **{spider}** ({date}): {summary}\n"
                    if source_url:
                        response += f"  {source_url}\n"

                if count > 6:
                    response += f"\n...and {count - 6} more items."

                return response

            # Session 979: Stock intelligence results formatting
            elif intent == 'stock_intelligence':
                action = tool_result.get('action', '')

                if action == 'overview':
                    brief = tool_result.get('latest_brief')
                    total_briefs = tool_result.get('total_briefs', 0)
                    total_alerts = tool_result.get('total_alerts', 0)
                    acc_7d = tool_result.get('prediction_accuracy_7d')
                    acc_30d = tool_result.get('prediction_accuracy_30d')
                    sec_count = tool_result.get('sec_filings_count', 0)

                    response = f"Stock Intelligence Overview, {user_name}:\n\n"
                    response += f"- **Market Briefs:** {total_briefs}\n"
                    response += f"- **Active Alerts:** {total_alerts}\n"
                    if acc_7d is not None:
                        response += f"- **Prediction Accuracy (7D):** {acc_7d}%\n"
                    if acc_30d is not None:
                        response += f"- **Prediction Accuracy (30D):** {acc_30d}%\n"
                    response += f"- **SEC Filings:** {sec_count}\n"
                    if brief:
                        response += f"\n**Latest Brief** ({brief.get('brief_date', 'N/A')}):\n"
                        response += f"{brief.get('executive_summary', 'No summary')[:200]}\n"
                    return response

                elif action == 'briefs':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No market briefs found, {user_name}."
                    response = f"Market Intelligence Briefs ({total} total):\n\n"
                    for b in items[:6]:
                        date = b.get('brief_date', 'N/A')[:10]
                        summary = b.get('executive_summary', '')[:80]
                        analyzed = b.get('total_stocks_analyzed', 0)
                        response += f"- **{date}** ({analyzed} stocks): {summary}...\n"
                    if total > 6:
                        response += f"\n...and {total - 6} more briefs."
                    return response

                elif action == 'alerts':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No stock alerts found, {user_name}."
                    response = f"Stock Alerts ({total} total):\n\n"
                    for a in items[:8]:
                        symbol = a.get('symbol', '???')
                        title = a.get('title', 'Untitled')[:50]
                        atype = a.get('alert_type', '')
                        action_rec = a.get('recommended_action', '')
                        response += f"- **{symbol}** [{atype}]: {title}"
                        if action_rec:
                            response += f" ({action_rec})"
                        response += "\n"
                    if total > 8:
                        response += f"\n...and {total - 8} more alerts."
                    return response

                elif action == 'predictions':
                    items = tool_result.get('items', [])
                    stats = tool_result.get('stats', {})
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No stock predictions found, {user_name}."
                    response = f"Stock Predictions ({total} total):\n\n"
                    if stats:
                        acc_7 = stats.get('accuracy_7d_pct')
                        acc_30 = stats.get('accuracy_30d_pct')
                        if acc_7 is not None:
                            response += f"- **7-Day Accuracy:** {acc_7}%\n"
                        if acc_30 is not None:
                            response += f"- **30-Day Accuracy:** {acc_30}%\n"
                        response += "\n"
                    for p in items[:6]:
                        ticker = p.get('ticker', '???')
                        pred_type = p.get('prediction_type', '')
                        conviction = p.get('conviction_level', '')
                        correct_7 = p.get('was_correct_7_days')
                        icon = '?' if correct_7 is None else ('Y' if correct_7 else 'N')
                        response += f"- **{ticker}** ({pred_type}, {conviction}) 7D: {icon}\n"
                    return response

                elif action == 'sec_filings':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No SEC filings found, {user_name}."
                    response = f"SEC Edgar Filings ({total} total):\n\n"
                    for f in items[:6]:
                        url = f.get('source_url', '')
                        date = str(f.get('created_at', ''))[:10]
                        dtype = f.get('data_type', 'filing')
                        response += f"- [{dtype}] {url[:60]} ({date})\n"
                    if total > 6:
                        response += f"\n...and {total - 6} more filings."
                    return response

                else:
                    return str(tool_result)

            # Session 995B: Sports betting results formatting
            elif intent == 'sports_betting':
                action = tool_result.get('action', '')

                if action == 'overview':
                    pending = tool_result.get('pending_wagers', 0)
                    settled = tool_result.get('settled_wagers', 0)
                    arb_count = tool_result.get('active_arb_opps', 0)
                    hot_signals = tool_result.get('hot_sharp_signals', 0)
                    sports = tool_result.get('active_sports', [])

                    response = f"Sports Betting Dashboard, {user_name}:\n\n"
                    response += f"- **Wagers:** {pending} pending, {settled} settled\n"
                    response += f"- **Arbitrage:** {arb_count} active opportunities\n"
                    response += f"- **Sharp Signals:** {hot_signals} HOT signals detected\n"
                    if sports:
                        response += f"- **Active Sports:** {', '.join(sports[:6])}\n"
                    return response

                elif action == 'arbs':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No arbitrage opportunities found right now, {user_name}."
                    response = f"Arbitrage Opportunities ({total} found):\n\n"
                    for a in items[:6]:
                        matchup = a.get('matchup', 'Unknown')
                        profit = a.get('profit_pct', 0)
                        rating = a.get('rating', '')
                        sport = a.get('sport', '')
                        response += f"- **[{rating}]** {matchup} ({sport}): {profit:.1f}% guaranteed profit\n"
                    if total > 6:
                        response += f"\n...and {total - 6} more opportunities."
                    return response

                elif action == 'predictions':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No game predictions available, {user_name}."
                    response = f"Game Predictions ({total} games):\n\n"
                    for p in items[:8]:
                        matchup = p.get('matchup', '')
                        winner = p.get('predicted_winner', '')
                        conf = p.get('confidence', 0)
                        sport = p.get('sport_name', '')
                        response += f"- **{matchup}** ({sport}): {winner} ({conf}% confidence)\n"
                    return response

                elif action == 'sharp_action':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No sharp action signals detected, {user_name}."
                    response = f"Sharp Action Signals ({total} detected):\n\n"
                    for s in items[:6]:
                        matchup = s.get('matchup', '')
                        rating = s.get('rating', '')
                        sport = s.get('sport_name', '')
                        svs = s.get('sharp_vs_soft', {})
                        favors = svs.get('sharp_favors', '') if svs else ''
                        div = svs.get('divergence', 0) if svs else 0
                        response += f"- **[{rating}]** {matchup} ({sport})"
                        if favors:
                            response += f" — Sharps favor {favors} (divergence: {div} pts)"
                        response += "\n"
                    return response

                elif action == 'line_movements':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No significant line movements detected, {user_name}."
                    response = f"Line Movements ({total} detected):\n\n"
                    for m in items[:6]:
                        matchup = m.get('matchup', '')
                        rating = m.get('rating', '')
                        changes = m.get('changes', [])
                        response += f"- **[{rating}]** {matchup}: {'; '.join(changes[:2])}\n"
                    return response

                elif action == 'wagers':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No wagers found, {user_name}."
                    response = f"Your Wagers ({total} total):\n\n"
                    for w in items[:8]:
                        desc = w.get('description', '')
                        status = w.get('status', '')
                        stake = w.get('stake', 0)
                        payout = w.get('potential_payout', 0)
                        icon = {'pending': 'P', 'won': 'W', 'lost': 'L', 'push': '-'}.get(status, '?')
                        response += f"- [{icon}] {desc} — ${stake:.2f} stake"
                        if status == 'pending':
                            response += f" (potential: ${payout:.2f})"
                        response += "\n"
                    return response

                elif action in ('brief', 'live_odds'):
                    # Brief or live odds — just surface the data nicely
                    top_plays = tool_result.get('top_plays', [])
                    summary = tool_result.get('executive_summary', '')
                    if summary:
                        response = f"{summary}\n\n"
                    else:
                        response = f"Sports Betting Brief, {user_name}:\n\n"
                    if top_plays:
                        response += "**Top Plays:**\n"
                        for p in top_plays[:6]:
                            source = p.get('source', '')
                            pick = p.get('pick', '')
                            conf = p.get('confidence', 0)
                            matchup = p.get('matchup', '')
                            response += f"- [{source}] **{matchup}**: {pick} ({conf}%)\n"
                    return response

                else:
                    return str(tool_result)

            # Session 1014: Legislation results formatting
            elif intent == 'legislation':
                action = tool_result.get('action', '')

                if action == 'overview':
                    total = tool_result.get('total_tracked', 0)
                    topics = tool_result.get('top_topics', [])
                    states = tool_result.get('states_covered', [])
                    breakdown = tool_result.get('status_breakdown', {})

                    response = f"Legislation Dashboard, {user_name}:\n\n"
                    response += f"- **Bills Tracked:** {total}\n"
                    if breakdown:
                        parts = [f"{s}: {c}" for s, c in breakdown.items()]
                        response += f"- **Status:** {', '.join(parts)}\n"
                    if states:
                        response += f"- **States:** {', '.join(states[:10])}\n"
                    if topics:
                        response += "\n**Top Topics:**\n"
                        for t in topics[:8]:
                            response += f"- {t['topic']} ({t['count']} bills)\n"
                    return response

                elif action == 'trending':
                    items = tool_result.get('items', [])
                    total = tool_result.get('total', 0)
                    if not items:
                        return f"No legislation data available yet, {user_name}. The spider may not have run yet."
                    response = f"Trending Bills ({total} tracked):\n\n"
                    for i, b in enumerate(items[:10], 1):
                        bn = b.get('bill_number', '?')
                        state = b.get('state', '')
                        title = b.get('title', '')[:60]
                        status = b.get('status', '')
                        last = b.get('last_action', '')[:50]
                        response += f"{i}. **{bn}** ({state}) — {title}\n"
                        response += f"   Status: {status}"
                        if last:
                            response += f" | Last: {last}"
                        response += "\n"
                    return response

                elif action == 'search':
                    if tool_result.get('error'):
                        return f"I need a topic to search for, {user_name}. Try: \"What bills about healthcare?\""
                    items = tool_result.get('items', [])
                    query = tool_result.get('query', '')
                    total = tool_result.get('total', 0)
                    if total == 0:
                        return f"No bills found matching \"{query}\", {user_name}. Try broader terms like healthcare, immigration, or technology."
                    response = f"Bills matching \"{query}\" ({total} found):\n\n"
                    for b in items[:10]:
                        bn = b.get('bill_number', '?')
                        state = b.get('state', '')
                        title = b.get('title', '')[:60]
                        status = b.get('status', '')
                        sponsors = b.get('sponsor_count', 0)
                        response += f"- **{bn}** ({state}): {title}\n"
                        response += f"  Status: {status} | {sponsors} sponsor(s)\n"
                    return response

                elif action == 'status':
                    if not tool_result.get('found'):
                        bn = tool_result.get('bill_number', 'that bill')
                        return f"Could not find {bn} in tracked legislation, {user_name}."
                    bn = tool_result.get('bill_number', '')
                    title = tool_result.get('title', '')
                    state = tool_result.get('state', '')
                    status = tool_result.get('status', '')
                    last_action = tool_result.get('last_action', '')
                    last_date = tool_result.get('last_action_date', '')
                    sponsors = tool_result.get('sponsors', [])
                    committee = tool_result.get('committee', '')
                    url = tool_result.get('url', '')

                    response = f"**{bn}** ({state}): {title}\n\n"
                    response += f"- **Status:** {status}\n"
                    if last_action:
                        response += f"- **Last Action:** {last_action}"
                        if last_date:
                            response += f" ({last_date})"
                        response += "\n"
                    if committee:
                        response += f"- **Committee:** {committee}\n"
                    if sponsors:
                        response += f"- **Sponsors:** {', '.join(sponsors[:5])}\n"
                    if url:
                        response += f"- [Full text]({url})\n"
                    return response

                elif action == 'ask':
                    # Session 1015: Ask A Bill RAG answer formatting
                    if tool_result.get('error'):
                        return f"I need a question about legislation, {user_name}. Try: \"How does the healthcare bill affect me?\""
                    answer = tool_result.get('answer', '')
                    sources = tool_result.get('source_bills', [])
                    count = tool_result.get('sources_count', 0)
                    response = f"{answer}\n"
                    if sources:
                        response += f"\n**Sources** ({count} bill{'s' if count != 1 else ''}):\n"
                        for s in sources:
                            bn = s.get('bill_number', '?')
                            title = s.get('title', '')[:60]
                            url = s.get('url', '')
                            if url:
                                response += f"- [{bn}]({url}): {title}\n"
                            else:
                                response += f"- **{bn}**: {title}\n"
                    return response

                elif action == 'summary':
                    if not tool_result.get('found'):
                        q = tool_result.get('query', 'that bill')
                        return f"Could not find a bill matching \"{q}\", {user_name}."
                    bn = tool_result.get('bill_number', '')
                    title = tool_result.get('title', '')
                    state = tool_result.get('state', '')
                    status = tool_result.get('status', '')
                    desc = tool_result.get('description', '')
                    plain = tool_result.get('plain_summary', '')
                    sponsors = tool_result.get('sponsors', [])
                    topics = tool_result.get('topics', [])
                    url = tool_result.get('url', '')

                    response = f"**{bn}** ({state}): {title}\n\n"
                    if plain:
                        response += f"{plain}\n\n"
                    elif desc:
                        response += f"{desc}\n\n"
                    response += f"- **Status:** {status}\n"
                    if topics:
                        response += f"- **Topics:** {', '.join(topics[:5])}\n"
                    if sponsors:
                        response += f"- **Sponsors:** {', '.join(sponsors[:5])}\n"
                    if url:
                        response += f"- [Full text]({url})\n"
                    return response

                else:
                    return str(tool_result)

            # Session 948/988: Execution history results formatting
            # Session 988: Fixed field name mismatches (items→executions, hours_back→period_hours)
            elif intent == 'execution_history':
                action = tool_result.get('action', '')

                if action == 'recent':
                    executions = tool_result.get('items', [])
                    count = tool_result.get('count', 0)
                    period = tool_result.get('hours_back', 24)
                    conversations = tool_result.get('conversations', [])
                    conv_count = tool_result.get('conversation_count', 0)

                    if count == 0 and conv_count == 0:
                        return f"No agent executions or conversations in the last {period} hours, {user_name}. The system is standing by."

                    response = ""

                    if count > 0:
                        response += f"**Agent Executions** ({count} in last {period}h):\n\n"
                        for ex in executions[:8]:
                            # Session 989: AgentExecution.agent is FK — handler returns agent__name
                            agent = ex.get('agent__name', ex.get('agent_name', 'Unknown'))
                            status = ex.get('status', 'unknown')
                            status_icon = '✅' if status == 'completed' else ('❌' if status == 'failed' else '⏳')
                            duration_ms = ex.get('execution_time_ms', 0)
                            response += f"{status_icon} **{agent}**"
                            if duration_ms:
                                response += f" ({duration_ms / 1000:.1f}s)"
                            task_desc = ex.get('task', '')
                            if task_desc:
                                response += f" — {str(task_desc)[:50]}"
                            response += "\n"
                        if count > 8:
                            response += f"\n...and {count - 8} more executions.\n"

                    if conv_count > 0:
                        response += f"\n**Agent Conversations** ({conv_count} in last {period}h):\n\n"
                        for conv in conversations[:6]:
                            objective = conv.get('objective', 'No topic')[:60]
                            status = conv.get('status', 'unknown')
                            participants = conv.get('participants', [])
                            status_icon = '✅' if status == 'completed' else ('⏳' if status == 'active' else '📋')
                            # Session 989: participants is JSONField — may contain dicts or strings
                            if isinstance(participants, list):
                                names = [p.get('name', str(p)) if isinstance(p, dict) else str(p) for p in participants[:3]]
                                agent_names = ', '.join(names)
                            else:
                                agent_names = str(participants)
                            response += f"{status_icon} **{objective}**\n"
                            if agent_names:
                                response += f"   └─ {agent_names}\n"
                        if conv_count > 6:
                            response += f"\n...and {conv_count - 6} more conversations.\n"

                    if not response:
                        response = f"No agent activity in the last {period} hours, {user_name}."
                    return response

                elif action == 'by_agent':
                    agent = tool_result.get('agent_name', 'Unknown')
                    executions = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No recent executions from {agent}, {user_name}."

                    success_rate = tool_result.get('success_rate') or 0
                    response = f"{agent} execution history ({count} total, {success_rate:.0%} success):\n\n"
                    for ex in executions[:6]:
                        status = ex.get('status', 'unknown')
                        status_icon = '✅' if status == 'completed' else '❌'
                        date = str(ex.get('created_at', ''))[:16]
                        task_desc = str(ex.get('task', ''))[:40]
                        response += f"{status_icon} {date}"
                        if task_desc:
                            response += f" - {task_desc}"
                        response += "\n"

                    return response

                elif action == 'stats':
                    total = tool_result.get('total_executions', 0)
                    successes = tool_result.get('successes', 0)
                    failures = tool_result.get('failures', 0)
                    success_rate = tool_result.get('success_rate') or 0
                    conv_total = tool_result.get('total_conversations', 0)
                    conv_completed = tool_result.get('completed_conversations', 0)
                    by_agent = tool_result.get('by_agent', [])
                    period = tool_result.get('hours_back', 24)

                    response = f"Agent Activity Stats (last {period}h), {user_name}:\n\n"
                    response += f"- **Executions:** {total} ({successes} ✅ / {failures} ❌)\n"
                    if total > 0:
                        response += f"- **Success rate:** {success_rate:.0%}\n"
                    response += f"- **Conversations:** {conv_total} ({conv_completed} completed)\n\n"

                    if by_agent:
                        response += "**Most active agents:**\n"
                        for entry in (by_agent[:5] if isinstance(by_agent, list) else []):
                            # Session 989: handler returns agent__name (FK traversal)
                            name = entry.get('agent__name', entry.get('agent_name', 'Unknown'))
                            cnt = entry.get('count', 0)
                            response += f"- {name}: {cnt} executions\n"

                    return response

                elif action == 'failures':
                    failures = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No recent failures, {user_name}. System is running smoothly!"

                    response = f"Recent agent failures ({count}):\n\n"
                    for f in failures[:6]:
                        # Session 989: handler returns agent__name (FK traversal)
                        agent = f.get('agent__name', f.get('agent_name', 'Unknown'))
                        error = str(f.get('error_message', 'Unknown error'))[:60]
                        date = str(f.get('created_at', ''))[:16]
                        response += f"❌ **{agent}** ({date})\n"
                        response += f"   └─ {error}\n"

                    return response

                else:
                    return str(tool_result)

            # Session 948: Learning patterns results formatting
            elif intent == 'learning_patterns':
                action = tool_result.get('action', '')

                if action == 'list':
                    patterns = tool_result.get('patterns', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No learning patterns found, {user_name}."

                    response = f"System Learning Patterns ({count} total):\n\n"
                    for p in patterns[:8]:
                        pattern_type = p.get('pattern_type', 'unknown')
                        description = p.get('description', '')[:60]
                        confidence = p.get('confidence') or 0
                        response += f"- {pattern_type} ({confidence:.0%}): {description}\n"

                    if count > 8:
                        response += f"\n...and {count - 8} more patterns."
                    return response

                elif action == 'by_type':
                    pattern_type = tool_result.get('pattern_type', 'Unknown')
                    patterns = tool_result.get('patterns', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No {pattern_type} patterns found, {user_name}."

                    response = f"**{pattern_type.title()}** Learning Patterns ({count}):\n\n"
                    for p in patterns[:6]:
                        description = p.get('description', '')[:70]
                        confidence = p.get('confidence') or 0
                        response += f"- {description} ({confidence:.0%})\n"

                    return response

                elif action == 'stats':
                    total = tool_result.get('total_patterns', 0)
                    by_type = tool_result.get('by_type', {})
                    avg_confidence = tool_result.get('avg_confidence', 0)
                    recent = tool_result.get('recent_patterns', 0)

                    response = f"Learning System Stats, {user_name}:\n\n"
                    response += f"- **Total patterns:** {total}\n"
                    response += f"- **Avg confidence:** {avg_confidence:.1f}%\n"
                    response += f"- **Recent (7 days):** {recent}\n\n"

                    if by_type:
                        response += "**By type:**\n"
                        for ptype, cnt in by_type.items():
                            response += f"- {ptype}: {cnt} patterns\n"

                    return response

                else:
                    return str(tool_result)

            # Session 948: Feedback tool response formatting
            elif intent == 'feedback':
                action = tool_result.get('action', 'list')

                if action == 'list':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)
                    status_filter = tool_result.get('status_filter', 'open')

                    if count == 0:
                        return f"No {status_filter} feedback items, {user_name}. The queue is clear!"

                    type_icons = {
                        'ui_ux_issue': '🎨',
                        'bug': '🐛',
                        'feature_request': '✨',
                        'feedback': '💬'
                    }

                    response = f"**User Feedback Queue** ({count} {status_filter}):\n\n"
                    for item in items[:10]:
                        ftype = item.get('feedback_type', 'feedback')
                        icon = type_icons.get(ftype, '📝')
                        msg = item.get('message', '')[:80]
                        created = item.get('created_at', '')[:10]
                        response += f"{icon} [{ftype.upper()}] {created}: {msg}...\n"

                    return response

                elif action == 'stats':
                    total_open = tool_result.get('total_open', 0)
                    by_type = tool_result.get('by_type', {})
                    by_status = tool_result.get('by_status', {})

                    response = f"Feedback Stats, {user_name}:\n\n"
                    response += f"**Open items:** {total_open}\n\n"

                    if by_type:
                        response += "**By type:**\n"
                        for ftype, cnt in by_type.items():
                            response += f"- {ftype}: {cnt}\n"
                        response += "\n"

                    if by_status:
                        response += "**By status:**\n"
                        for status, cnt in by_status.items():
                            response += f"- {status}: {cnt}\n"

                    return response

                else:
                    return str(tool_result)

            # Session 973: System overview snapshot formatter
            elif intent == 'system_overview':
                lines = [f"**System Pulse**, {user_name}:\n"]

                health = tool_result.get('health', {})
                if 'error' not in health:
                    status = health.get('status', 'unknown')
                    score = health.get('score')
                    age = health.get('age_minutes', '?')
                    score_str = f" ({score})" if score is not None else ""
                    lines.append(f"- **Health:** {status}{score_str} — last heartbeat {age} min ago")
                else:
                    lines.append(f"- **Health:** data unavailable")

                init = tool_result.get('initiatives', {})
                if 'error' not in init:
                    lines.append(f"- **Initiatives:** {init.get('active', 0)} active, {init.get('updated_24h', 0)} updated (24h)")

                tc = tool_result.get('tool_calls_24h', {})
                if 'error' not in tc:
                    failed_str = f" ({tc.get('failed', 0)} failed)" if tc.get('failed', 0) > 0 else ""
                    lines.append(f"- **Tool calls (24h):** {tc.get('total', 0)}{failed_str}")

                sp = tool_result.get('spiders_24h', {})
                if 'error' not in sp:
                    lines.append(f"- **Spiders (24h):** {sp.get('items', 0)} items from {sp.get('active_spiders', 0)} spiders")

                convos = tool_result.get('conversations_24h', {})
                if 'error' not in convos:
                    lines.append(f"- **Conversations (24h):** {convos.get('count', 0)}")

                signals = tool_result.get('signal_clusters', {})
                if 'error' not in signals:
                    lines.append(f"- **Signal clusters:** {signals.get('active', 0)} active")

                celery = tool_result.get('celery_24h', {})
                if 'error' not in celery:
                    failed_str = f" ({celery.get('failed', 0)} failed)" if celery.get('failed', 0) > 0 else ""
                    lines.append(f"- **Celery tasks (24h):** {celery.get('total', 0)}{failed_str}")

                errors = tool_result.get('errors_24h', {})
                if 'error' not in errors:
                    lines.append(f"- **Errors (24h):** {errors.get('count', 0)}")

                blogs = tool_result.get('blogs_24h', {})
                if 'error' not in blogs:
                    lines.append(f"- **Blogs (24h):** {blogs.get('total', 0)} total, {blogs.get('published', 0)} published")

                lines.append("\n*Want me to drill into any of these?*")
                return "\n".join(lines)

            # Session 1035: Legal assistance formatter — show agent output + disclaimer
            elif intent == 'legal_assistance':
                success = tool_result.get('success', False)
                agent = tool_result.get('agent', 'LegalDocDrafterAgent')
                output = tool_result.get('output', '')

                if not success:
                    return (
                        f"The legal assistant couldn't process that request. "
                        f"Try being more specific about what you need help with — "
                        f"for example: \"I need to modify my parenting time in Larimer County\" "
                        f"or \"What forms do I need to file for contempt?\""
                    )

                # The agent returns an AgentResult — extract the message
                output_str = str(output)
                # If it's an AgentResult object, try to get the message
                if hasattr(output, 'message'):
                    output_str = output.message or str(output)
                elif hasattr(output, 'content'):
                    output_str = output.content or str(output)
                elif isinstance(output, dict):
                    output_str = output.get('message', output.get('content', str(output)))

                lines = []
                lines.append(f"**{agent}** — Colorado Family Law Assistant\n")
                lines.append(output_str)

                # Session 1035: Hint about document upload when no user docs were found
                if not tool_result.get('had_user_documents'):
                    lines.append("\n---")
                    lines.append(
                        "*Tip: Upload your court orders, emails, or other documents via the "
                        "Documents tab — I'll automatically reference them in future answers.*"
                    )

                return "\n".join(lines)

            # Session 987: Agent execution formatter (image, video, content_writer, etc.)
            # Session 1034: Research-and-create formatter — show preview + saved location
            elif intent == 'research_and_create':
                if not tool_result.get('success'):
                    error = tool_result.get('error', 'Content generation failed.')
                    return f"I wasn't able to generate the content: {error}"

                title = tool_result.get('title', 'Untitled')
                output_type_label = tool_result.get('output_type_label', 'Content')
                content = tool_result.get('content', '')
                deliverable_id = tool_result.get('deliverable_id')
                search_count = tool_result.get('search_results_count', 0)

                lines = []
                lines.append(f"{output_type_label}: {title}")
                lines.append(f"Researched {search_count} sources and generated your content.")
                if deliverable_id:
                    lines.append(f"Saved to Deliverables (ID: {deliverable_id})")
                    lines.append("You can find the full content in Workspace > Deliverables.")
                lines.append("")
                # Show full content — the PA chat can handle it, and user wants to see it
                lines.append(content)
                return "\n".join(lines)

            elif intent in ['agent_execution', 'image_creation', 'video_creation',
                            'content_writing', 'image_generation', 'video_generation']:
                agent = tool_result.get('agent', 'Agent')
                success = tool_result.get('success', False)
                output = tool_result.get('output', '')
                data = tool_result.get('data', {}) or {}
                # Session 1065: Deliverable ID from _handle_agent_tool
                deliverable_id = tool_result.get('deliverable_id')

                if not success:
                    return f"**{agent}** could not complete the task."

                saved_note = ''
                if deliverable_id:
                    saved_note = f"\n\n*Saved to your Deliverables library.*"

                # Session 1063: Render image results as markdown images
                if intent in ('image_creation', 'image_generation') and isinstance(data, dict):
                    images = data.get('images', [])
                    if images and isinstance(images, list):
                        lines = [f"**{agent}** generated {len(images)} image(s):\n"]
                        for i, img in enumerate(images, 1):
                            url = img.get('url', '') if isinstance(img, dict) else str(img)
                            if url:
                                lines.append(f"**Image {i}:**\n![Image {i}]({url})\n")
                        lines.append("\n[View in Media Library](/media)")
                        if saved_note:
                            lines.append(saved_note)
                        return "\n".join(lines)

                # Session 1080: Format video/audio async results as in-app links
                if intent in ('video_creation', 'video_generation') and isinstance(data, dict):
                    video_url = data.get('final_video_url') or data.get('video_url') or tool_result.get('video_url')
                    task_id = tool_result.get('task_id') or data.get('task_id')
                    if task_id and not video_url:
                        return (
                            f"**{agent}** is generating your video. "
                            f"You'll be notified when it's ready!\n\n"
                            f"[View in Media Library](/media)"
                        )
                    if video_url:
                        thumb = data.get('thumbnail_url') or tool_result.get('thumbnail_url')
                        lines = [f"Your video is ready!\n"]
                        if thumb:
                            lines.append(f"![Video thumbnail]({thumb})\n")
                        lines.append("[View in Media Library](/media)")
                        if saved_note:
                            lines.append(saved_note)
                        return "\n".join(lines)

                # Truncate long outputs
                output_str = str(output)
                if len(output_str) > 2000:
                    output_str = output_str[:2000] + '...'

                return f"**{agent}** completed successfully:\n\n{output_str}{saved_note}"

            # Session 987 / 1028: Web search / research formatter
            elif intent in ['web_search', 'research']:
                query = tool_result.get('query', '')
                results = tool_result.get('results', [])

                if isinstance(results, list) and results:
                    lines = []
                    for r in results[:5]:
                        title = r.get('title', 'Untitled')
                        url = r.get('url', '')
                        snippet = r.get('snippet', '')[:150]
                        if url:
                            lines.append(f"**[{title}]({url})**\n{snippet}")
                        else:
                            lines.append(f"**{title}**\n{snippet}")
                    return f"Search results for **\"{query}\"**:\n\n" + "\n\n".join(lines)

                # Fallback for string results or empty
                results_str = str(results)[:800]
                return f"Search results for **\"{query}\"**:\n\n{results_str}"

            # Session 987: Reasoning engine formatter
            elif intent == 'reasoning':
                action = tool_result.get('action', '')

                if action == 'status':
                    engine = tool_result.get('engine', 'ThinkingAgent')
                    status = tool_result.get('status', 'unknown')
                    return f"**{engine}**: {status}"

                elif action == 'thoughts':
                    thoughts = tool_result.get('thoughts', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No thinking cycles found, {user_name}."

                    response = f"Recent Thinking Cycles ({count}):\n\n"
                    for t in thoughts[:8]:
                        task = (t.get('task') or 'Unknown task')[:60]
                        success = t.get('success', False)
                        icon = 'Y' if success else 'N'
                        created = str(t.get('created_at', ''))[:16]
                        response += f"- [{icon}] {task} ({created})\n"

                    return response

                elif action == 'trigger':
                    if tool_result.get('triggered'):
                        output = str(tool_result.get('output', ''))[:300]
                        return f"Thinking cycle triggered.\n\n{output}"
                    else:
                        return f"Could not trigger thinking cycle: {tool_result.get('error', 'unknown error')}"

                else:
                    return str(tool_result)

            # Session 987: Revenue tracker formatter
            elif intent == 'revenue':
                action = tool_result.get('action', '')

                if action == 'stats':
                    total = tool_result.get('total_revenue', '0')
                    recent = tool_result.get('revenue_last_30_days', '0')
                    by_source = tool_result.get('by_source', {})
                    count = tool_result.get('record_count', 0)

                    response = f"Revenue Summary, {user_name}:\n\n"
                    response += f"**Total revenue:** ${total}\n"
                    response += f"**Last 30 days:** ${recent}\n"
                    response += f"**Records:** {count}\n"

                    if by_source:
                        response += "\n**By source:**\n"
                        for source, amount in by_source.items():
                            response += f"- {source}: ${amount}\n"

                    return response

                elif action == 'list':
                    revenues = tool_result.get('revenues', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No revenue records found, {user_name}."

                    response = f"Recent Revenue ({count} records):\n\n"
                    for r in revenues[:10]:
                        amount = r.get('amount', 0)
                        source = r.get('source', 'unknown')
                        desc = (r.get('description') or '')[:50]
                        created = str(r.get('created_at', ''))[:10]
                        response += f"- **${amount}** from {source} ({created}) {desc}\n"

                    return response

                else:
                    return str(tool_result)

            # Session 987: Task manager formatter
            elif intent == 'task_management':
                action = tool_result.get('action', '')

                if action == 'list':
                    tasks = tool_result.get('tasks', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No tasks found, {user_name}."

                    response = f"Your Tasks ({count}):\n\n"
                    for t in tasks[:15]:
                        title = (t.get('title') or 'Untitled')[:60]
                        status = t.get('status', 'unknown')
                        priority = t.get('priority', '')
                        priority_badge = f" [{priority.upper()}]" if priority else ""
                        response += f"- **{title}**{priority_badge} — {status}\n"

                    return response

                elif action == 'stats':
                    total = tool_result.get('total', 0)
                    by_status = tool_result.get('by_status', {})
                    by_priority = tool_result.get('by_priority', {})

                    response = f"Task Stats, {user_name}:\n\n"
                    response += f"**Total:** {total}\n"

                    if by_status:
                        response += "\n**By status:**\n"
                        for s, c in by_status.items():
                            response += f"- {s}: {c}\n"

                    if by_priority:
                        response += "\n**By priority:**\n"
                        for p, c in by_priority.items():
                            response += f"- {p}: {c}\n"

                    return response

                else:
                    return str(tool_result)

            # Session 987: Workspace formatter
            elif intent == 'workspace':
                action = tool_result.get('action', '')

                if action == 'list':
                    workspaces = tool_result.get('workspaces', [])
                    if not workspaces:
                        return f"No workspaces found, {user_name}."

                    response = f"Workspaces ({len(workspaces)}):\n\n"
                    for ws in workspaces[:10]:
                        if isinstance(ws, dict):
                            name = ws.get('name', 'Unknown')
                            response += f"- {name}\n"
                        else:
                            response += f"- {ws}\n"
                    return response

                elif action == 'status':
                    status = tool_result.get('status', {})
                    response = f"Workspace Status, {user_name}:\n\n"
                    if isinstance(status, dict):
                        for key, val in status.items():
                            response += f"- **{key}:** {val}\n"
                    else:
                        response += str(status)
                    return response

                else:
                    return str(tool_result)

            # Deliverables library formatter
            elif intent == 'deliverables':
                if isinstance(tool_result, dict):
                    action = tool_result.get('action', '')

                    if action in ('list', 'search'):
                        items = tool_result.get('items', [])
                        if not items:
                            return f"No deliverables found, {user_name}."

                        label = "Search results" if action == 'search' else "Deliverables"
                        response = f"{label} ({len(items)}):\n\n"
                        for i, item in enumerate(items[:15], 1):
                            if isinstance(item, dict):
                                title = item.get('title', 'Untitled')
                                dtype = item.get('deliverable_type', '')
                                score = item.get('quality_score', 0)
                                saved = ' [saved]' if item.get('is_saved') else ''
                                response += f"{i}. **{title}** ({dtype}) — quality: {score:.1f}{saved}\n"
                        return response

                    elif action == 'detail':
                        title = tool_result.get('title', 'Untitled Deliverable')
                        dtype = tool_result.get('deliverable_type', 'document')
                        agent = tool_result.get('agent_name', 'System')
                        preview = tool_result.get('content_preview', '')
                        score = tool_result.get('quality_score', 0)
                        saved = 'Yes' if tool_result.get('is_saved') else 'No'
                        tags = ', '.join(tool_result.get('tags', []))

                        response = f"**{title}**\n\n"
                        response += f"- **Type:** {dtype}\n"
                        if agent:
                            response += f"- **Agent:** {agent}\n"
                        response += f"- **Quality:** {score:.1f}\n"
                        response += f"- **Saved:** {saved}\n"
                        if tags:
                            response += f"- **Tags:** {tags}\n"
                        if preview:
                            response += f"\n**Preview:**\n{preview}\n"
                        response += "\n*View in Content Studio > Deliverables*"
                        return response

                    elif action in ('save', 'unsave'):
                        title = tool_result.get('title', '')
                        if action == 'save':
                            return f"Saved **{title}** to your library."
                        else:
                            return f"Removed **{title}** from your saved items."

                    elif action == 'stats':
                        total = tool_result.get('total', 0)
                        saved = tool_result.get('saved', 0)
                        templates = tool_result.get('templates', 0)
                        by_type = tool_result.get('by_type', {})

                        response = f"Deliverables Library, {user_name}:\n\n"
                        response += f"- **Total:** {total}\n"
                        response += f"- **Saved:** {saved}\n"
                        response += f"- **Templates:** {templates}\n"
                        if by_type:
                            response += "\n**By type:**\n"
                            for t, c in by_type.items():
                                response += f"- {t}: {c}\n"
                        return response

                    # Session 1065: Create action formatter
                    elif action == 'create':
                        title = tool_result.get('title', '')
                        dtype = tool_result.get('deliverable_type', 'document')
                        return f"Created **{title}** ({dtype}) and saved it to your Deliverables library."

                return str(tool_result)

            # Session 987: Budget formatter
            elif intent == 'budget':
                approved = tool_result.get('approved', False)
                budget_status = tool_result.get('budget_status', 'unknown')
                tokens = tool_result.get('estimated_tokens', 0)
                cost = tool_result.get('estimated_cost', 0)

                response = f"Budget Status, {user_name}:\n\n"
                response += f"**Status:** {budget_status}\n"
                response += f"**Approved:** {'Yes' if approved else 'No'}\n"
                if tokens:
                    response += f"**Estimated tokens:** {tokens:,}\n"
                if cost:
                    response += f"**Estimated cost:** ${cost}\n"
                return response

            # Session 987: System alerts formatter
            elif intent == 'system_alerts':
                alerts = tool_result.get('alerts', [])
                count = tool_result.get('alert_count', 0)
                threshold = tool_result.get('severity_threshold', 'info')

                if count == 0:
                    return f"No alerts above {threshold} severity, {user_name}. All clear."

                response = f"System Alerts ({count}, threshold: {threshold}):\n\n"
                for alert in alerts[:10]:
                    severity = alert.get('severity', 'info').upper()
                    msg = alert.get('message', '') or alert.get('description', '')
                    system = alert.get('system', '')
                    prefix = f"[{system}] " if system else ""
                    response += f"- **{severity}:** {prefix}{msg}\n"

                return response

            # Session 987: ML analysis formatter
            elif intent == 'ml_analysis':
                action = tool_result.get('action', '')

                if action == 'status':
                    health = tool_result.get('health', {})
                    response = f"ML Engine Status, {user_name}:\n\n"
                    if isinstance(health, dict):
                        for key, val in health.items():
                            response += f"- **{key}:** {val}\n"
                    else:
                        response += str(health)
                    return response

                elif action == 'decision_pattern':
                    confidence = tool_result.get('confidence') or 0
                    return f"Decision pattern confidence: {confidence:.1%}"

                elif action == 'detect_opportunity':
                    opps = tool_result.get('opportunities', [])
                    count = tool_result.get('count', 0)
                    if count == 0:
                        return f"No cross-domain opportunities detected, {user_name}."
                    response = f"Found {count} cross-domain opportunities:\n\n"
                    for opp in opps[:5]:
                        response += f"- {opp}\n"
                    return response

                else:
                    return str(tool_result)

            # Session 1048: Task volume breakdown formatter
            elif intent == 'task_breakdown':
                action = tool_result.get('action', 'summary')

                if action == 'summary':
                    totals = tool_result.get('totals', {})
                    by_task = tool_result.get('by_task', [])
                    by_agent = tool_result.get('by_agent', [])
                    window = tool_result.get('window', '60m')

                    response = f"Task Volume Breakdown ({window} window):\n\n"
                    response += (
                        f"**Totals:** {totals.get('tasks', 0)} tasks | "
                        f"{totals.get('success', 0)} success | "
                        f"{totals.get('failure', 0)} failure | "
                        f"{totals.get('started', 0)} in-flight\n\n"
                    )

                    if by_task:
                        response += "| Task | Count | Fail% | Avg | p50 | p95 |\n"
                        response += "|------|-------|-------|-----|-----|-----|\n"
                        for t in by_task[:20]:
                            short_name = t['task_name'].rsplit('.', 1)[-1]
                            fail_pct = f"{t['failure_rate']:.0%}" if t['failure_rate'] else "0%"
                            response += (
                                f"| {short_name} | {t['count_total']} | {fail_pct} | "
                                f"{t['avg_duration_ms']}ms | {t['p50_ms']}ms | {t['p95_ms']}ms |\n"
                            )

                    if by_agent:
                        response += "\n**Agent Executions:**\n"
                        for a in by_agent[:10]:
                            fail_pct = f" ({a['failure_rate']:.0%} fail)" if a['count_failure'] else ""
                            response += f"- {a['agent_name']}: {a['execution_count']}{fail_pct}\n"

                    return response

                elif action == 'drilldown':
                    task_name = tool_result.get('task_name', '')
                    executions = tool_result.get('executions', [])
                    count = tool_result.get('count', 0)
                    window = tool_result.get('window', '60m')

                    short_name = task_name.rsplit('.', 1)[-1]
                    response = f"**{short_name}** — {count} executions ({window} window):\n\n"

                    if executions:
                        response += "| Time | Duration | Status | Queue | Error |\n"
                        response += "|------|----------|--------|-------|-------|\n"
                        for e in executions[:30]:
                            started = (e.get('started_at') or '')[-8:]  # HH:MM:SS
                            dur = f"{e['duration_ms']}ms" if e.get('duration_ms') else "-"
                            status = e.get('status', '?')
                            queue = e.get('queue', 'default')
                            error = (e.get('error_type') or '')[:30]
                            response += f"| {started} | {dur} | {status} | {queue} | {error} |\n"
                    else:
                        response += "No executions found in this window."

                    return response

                else:
                    return str(tool_result)

            # Session 987: Pipeline status formatter
            elif intent == 'pipeline_status':
                total = tool_result.get('initiatives_total', 0)
                active = tool_result.get('initiatives_active', 0)
                by_stage = tool_result.get('by_stage', {})

                response = f"Pipeline Status, {user_name}:\n\n"
                response += f"**Total initiatives:** {total}\n"
                response += f"**Active:** {active}\n"

                if by_stage:
                    response += "\n**By stage:**\n"
                    stage_names = {
                        'stage_1': 'Research',
                        'stage_2': 'Strategy',
                        'stage_3': 'Execution',
                        'stage_4': 'Review',
                        'stage_5': 'Complete',
                    }
                    for stage_key, count in by_stage.items():
                        name = stage_names.get(stage_key, stage_key)
                        response += f"- {name}: {count}\n"

                return response

            else:
                return str(tool_result)

        else:
            return str(tool_result)
        return ''

    def _log_user_feedback_to_docs(
        self,
        message: str,
        feedback_type: str,
        trace_id: str
    ) -> bool:
        """
        Session 948: Actually log user feedback for persistence across sessions.

        Writes to a configurable location (via PA_FEEDBACK_FILE setting) or
        falls back to database storage if file system isn't available.

        Returns True if logged successfully.
        """
        # Try to log to file first (for Claude Code visibility)
        file_logged = self._log_feedback_to_file(message, feedback_type, trace_id)

        # Always log to database as backup (works in any deployment)
        db_logged = self._log_feedback_to_database(message, feedback_type, trace_id)

        return file_logged or db_logged

    def _log_feedback_to_file(
        self,
        message: str,
        feedback_type: str,
        trace_id: str
    ) -> bool:
        """Log feedback to file system (for Claude Code visibility)."""
        try:
            # Configurable feedback file location
            # Default: docs/USER_FEEDBACK_QUEUE.md in project root
            feedback_path = getattr(settings, 'PA_FEEDBACK_FILE', None)

            if not feedback_path:
                base_dir = getattr(settings, 'BASE_DIR', None)
                if not base_dir:
                    return False
                feedback_path = Path(base_dir) / 'docs' / 'USER_FEEDBACK_QUEUE.md'
            else:
                feedback_path = Path(feedback_path)

            # Create parent dir if needed
            feedback_path.parent.mkdir(parents=True, exist_ok=True)

            # Format the entry
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            user_name = self.user.username if hasattr(self.user, 'username') else 'unknown'  # type: ignore[attr-defined]

            entry = f"""
## [{feedback_type.upper()}] {timestamp}
**User:** {user_name}
**Trace:** {trace_id}

> {message}

**Status:** 🔴 OPEN

---
"""

            # Check if file exists and has header
            if not feedback_path.exists():
                header = """# User Feedback Queue

This file is auto-populated by the PA when users report issues, bugs, or feature requests.
The next session should review and address these items.

**How to use:**
1. Review each item below
2. Implement fixes or document why not feasible
3. Change status from 🔴 OPEN to ✅ ADDRESSED
4. Delete addressed items after confirming with user

---
"""
                feedback_path.write_text(header + entry)
            else:
                # Append to existing file
                with open(feedback_path, 'a') as f:
                    f.write(entry)

            logger.info(f"Logged user feedback to file {feedback_path}: {feedback_type}")
            return True

        except Exception as e:
            logger.warning(f"Could not log feedback to file: {e}")
            return False

    def _log_feedback_to_database(
        self,
        message: str,
        feedback_type: str,
        trace_id: str
    ) -> bool:
        """Log feedback to database (works in any deployment)."""
        try:
            from core.models_user_feedback import UserFeedback

            UserFeedback.objects.create(
                user=self.user,
                feedback_type=feedback_type,
                message=message,
                trace_id=trace_id,
                status='open'
            )
            logger.info(f"Logged user feedback to database: {feedback_type}")
            return True

        except ImportError:
            # UserFeedback model doesn't exist yet - that's ok
            logger.debug("UserFeedback model not available, skipping DB log")
            return False
        except Exception as e:
            logger.warning(f"Could not log feedback to database: {e}")
            return False

    def _generate_capabilities_response(self, user_name: str = 'there') -> str:
        """Session 987/988: PA self-awareness — returns actual capabilities from real tool registry."""
        return (
            f"Here's what I can help you with, {user_name}:\n\n"
            "**Web & Internet Access**\n"
            "Yes — I have 77 spiders crawling the internet (CoinGecko, Yahoo Finance, SEC Edgar, "
            "TechCrunch, Reuters, and more), plus web search for real-time research.\n"
            "Try: \"how much is BTC?\", \"search for AI trends\", \"what have spiders found?\"\n\n"
            "**Crypto & Market Prices**\n"
            "Live crypto data via CoinGecko spider, stock data via financial spiders\n"
            "Try: \"how much is bitcoin?\", \"ethereum price\", \"stock overview\"\n\n"
            "**System Health & Monitoring**\n"
            "Body vitals, system health checks, recent activity, error summaries\n"
            "Try: \"how's the system?\", \"any errors?\", \"what's been happening?\"\n\n"
            "**Boardroom & Decisions**\n"
            "Attention queue, draft decisions, approve/reject items, triage\n"
            "Try: \"what needs my attention?\", \"show decisions\"\n\n"
            "**Initiatives & Projects**\n"
            "Pipeline overview, stages, action items, audit/cleanup\n"
            "Try: \"show initiatives\", \"active projects\"\n\n"
            "**Content & Blogs**\n"
            "Review, publish, archive, quality stats, read blog posts\n"
            "Try: \"show blogs\", \"content stats\", \"publish-ready posts\"\n\n"
            "**Stock Intelligence**\n"
            "Market briefs, alerts, predictions, SEC filings, accuracy stats\n"
            "Try: \"stock overview\", \"market alerts\", \"SEC filings\"\n\n"
            "**Opportunities**\n"
            "Jobs, gigs, and income opportunities from the spider network\n"
            "Try: \"any opportunities?\", \"show jobs\"\n\n"
            "**Agent Execution**\n"
            "Run any of 76 agents for research, content creation, analysis, audits\n"
            "Try: \"create an image\", \"write a blog post\", \"run a security audit\"\n\n"
            "**Reasoning & Deliberation**\n"
            "Multi-agent debates, surgical moves verification, thinking sessions\n"
            "Try: \"deliberation status\", \"trigger a thinking session\"\n\n"
            "**Learning & Feedback**\n"
            "System learning patterns, feedback queue, experiment results\n"
            "Try: \"what has the system learned?\", \"show feedback\"\n\n"
            "**What I can't do:** Read raw database tables not exposed via tools, "
            "execute shell commands, or see API keys/credentials.\n\n"
            "Just ask naturally — I'll route to the right tool."
        )

    async def _generate_honest_feedback_response(
        self,
        message: str,
        context: Dict[str, Any],
        trace_id: str
    ) -> str:
        """
        Session 948: Generate honest response for user feedback/issues.

        Instead of triggering random tools and pretending they solve the problem,
        acknowledge the limitation honestly, LOG IT TO DOCS, and explain what would help.
        """
        user_name = context.get('user_name', 'there')

        # Categorize the type of feedback
        message_lower = message.lower()
        feedback_type = 'feedback'  # default

        if any(phrase in message_lower for phrase in [
            'not available', 'can\'t access', 'cannot access', 'losing context',
            'context lost', 'context loss', 'spread out', 'fragmented', 'disconnect'
        ]):
            feedback_type = 'ui_ux_issue'
        elif any(phrase in message_lower for phrase in [
            'not working', 'doesn\'t work', 'broken', 'bug'
        ]):
            feedback_type = 'bug'
        elif any(phrase in message_lower for phrase in [
            'should be', 'need to be', 'would be better', 'wish', 'why can\'t', 'why isn\'t'
        ]):
            feedback_type = 'feature_request'

        # Actually log the feedback to docs
        logged = self._log_user_feedback_to_docs(message, feedback_type, trace_id)
        log_status = "✅ **Logged to `docs/USER_FEEDBACK_QUEUE.md`** - the next Claude session will see this." if logged else "⚠️ Could not log feedback (file write error)."

        if feedback_type == 'ui_ux_issue':
            return (
                f"I hear you, {user_name}. You're describing a **UI/UX limitation** - "
                f"something that requires actual code changes to fix.\n\n"
                f"{log_status}\n\n"
                f"**What I can do now:**\n"
                f"- Help you work around it with current capabilities\n"
                f"- Explain what exists today\n\n"
                f"**What would actually fix it:**\n"
                f"- Code changes in a developer session\n\n"
                f"Is there anything else you'd like me to note about this issue?"
            )

        elif feedback_type == 'bug':
            return (
                f"Thanks for reporting this, {user_name}. This sounds like a **bug**.\n\n"
                f"{log_status}\n\n"
                f"I can't fix code bugs - that requires a developer - but I've recorded this.\n\n"
                f"To help the next session fix this faster:\n"
                f"- What did you expect to happen?\n"
                f"- What actually happened?\n"
                f"- Any error messages?"
            )

        elif feedback_type == 'feature_request':
            return (
                f"I understand, {user_name}. You're suggesting an **improvement**.\n\n"
                f"{log_status}\n\n"
                f"I can't implement code changes myself, but I've recorded this for future development.\n\n"
                f"Any additional context about the use case?"
            )

        else:
            return (
                f"I appreciate the feedback, {user_name}.\n\n"
                f"{log_status}\n\n"
                f"To help address this:\n"
                f"1. What were you trying to do?\n"
                f"2. What happened instead?\n"
                f"3. What would success look like?"
            )

    async def _generate_direct_response(
        self,
        message: str,
        context: Dict[str, Any],
        trace_id: str
    ) -> str:
        """Generate direct LLM response without tool."""
        user_name = context.get('user_name', 'there')
        stats = context.get('system_stats', {})
        profile = context.get('profile', {})
        docs_context = context.get('docs_context', {})

        # Build system context
        # Session 1034: Added platform identity so PA can compare itself to competitors
        system_prompt = f"""You are the operational advisor for {user_name} in the Donkey Betz Unified AI Platform.

{self._get_platform_identity()}

You are NOT a documentation narrator. Do NOT recite system capabilities from design documents.
You are an operational advisor with live system access.

If asked about system state, activity, or updates, suggest a targeted question like:
- "How's the system?" for health check
- "What's been going on?" for recent activity
- "Any errors?" for error summary
- "How is everything?" for a full system pulse

For broad questions, keep answers to 5 bullet points max.

SYSTEM STATS:
- {stats.get('agent_count', 74)} AI Agents | {stats.get('spider_count', 77)} Spiders | {stats.get('advisor_count', 25)} Advisors

USER PROFILE:
- Skills: {profile.get('skills', 'Not specified')}
- Goals: {profile.get('goals', 'Not specified')}

IMPORTANT: Only describe features and connections that actually exist in the system.
If you don't have verified data about a subsystem, say so. Never fabricate integrations or capabilities.

Be concise, conversational, and personalized. Address the user by name."""

        # Session 943: Add docs context so PA knows about system architecture and recent work
        if docs_context.get('has_docs'):
            docs_summary = docs_context.get('summary', '')
            if docs_summary:
                # Truncate if too long to keep context manageable
                if len(docs_summary) > 4000:
                    docs_summary = docs_summary[:4000] + "\n... (truncated)"
                system_prompt += f"\n\n{docs_summary}"
                logger.debug(f"[{trace_id}] Added docs context to PA prompt ({len(docs_summary)} chars)")

        # Session 972: Inject dynamic system knowledge (workspace, health, agents, etc.)
        system_knowledge = context.get('system_knowledge', {})
        if system_knowledge.get('has_dynamic_context') and self.knowledge_injector:
            knowledge_text = self.knowledge_injector.format_for_prompt(system_knowledge)
            if knowledge_text:
                system_prompt += knowledge_text
                logger.debug(f"[{trace_id}] Added system knowledge to PA prompt ({len(knowledge_text)} chars)")

        # Workspace/codebase context from SKIN layer
        ws_ctx = context.get('workspace_context', {})
        if ws_ctx:
            cb_parts = []
            if ws_ctx.get('workspace_name'):
                cb_parts.append(f"Project: {ws_ctx['workspace_name']}")
            tech = ws_ctx.get('tech_stack', {})
            if tech:
                tech_items = list(tech.values()) if isinstance(tech, dict) else list(tech)
                cb_parts.append(f"Tech stack: {', '.join(str(t) for t in tech_items)}")
            key_files = ws_ctx.get('key_files', {})
            if key_files:
                cb_parts.append("Key files:")
                kf_items = list(key_files.items())[:15] if isinstance(key_files, dict) else list(key_files)[:15]
                for kf in kf_items:
                    if isinstance(kf, tuple):
                        cb_parts.append(f"  - {kf[0]}: {kf[1]}")
                    else:
                        cb_parts.append(f"  - {kf}")
            dir_purposes = ws_ctx.get('directory_purposes', {})
            if isinstance(dir_purposes, dict) and dir_purposes:
                cb_parts.append("Directory purposes:")
                for d, purpose in list(dir_purposes.items())[:15]:
                    cb_parts.append(f"  - {d}: {purpose}")
            patterns = ws_ctx.get('coding_patterns', {})
            if patterns:
                cb_parts.append("Coding patterns:")
                pat_items = list(patterns.items())[:10] if isinstance(patterns, dict) else list(patterns)[:10]
                for p in pat_items:
                    if isinstance(p, tuple):
                        cb_parts.append(f"  - {p[0]}: {p[1]}")
                    else:
                        cb_parts.append(f"  - {p}")
            if ws_ctx.get('total_files'):
                cb_parts.append(f"Total files: {ws_ctx['total_files']}")
            if cb_parts:
                codebase_text = "\n\nCODEBASE CONTEXT:\n" + "\n".join(cb_parts)
                if len(codebase_text) > 3000:
                    codebase_text = codebase_text[:3000] + "\n... (truncated)"
                system_prompt += codebase_text
                logger.debug(f"[{trace_id}] Added codebase context to PA prompt ({len(codebase_text)} chars)")

        # Add conversation history
        history_text = ""
        for turn in context.get('conversation_history', [])[-6:]:
            role = turn.get('role', 'user')
            content = turn.get('content', '')[:200]
            history_text += f"{role}: {content}\n"

        if history_text:
            system_prompt += f"\n\nRECENT CONVERSATION:\n{history_text}"

        try:
            # Session 948: Increased max_tokens from 400 to 2000 for comprehensive responses
            result = await asyncio.to_thread(
                self.llm_enforcer.enforce_real_ai,
                prompt=message,
                context=system_prompt,
                agent_name="UnifiedPA",
                task_type="conversation",
                max_tokens=2000
            )

            if result.get('success'):
                return result.get('response', f"I understand you're asking about: {message}")
            else:
                return f"Hi {user_name}! I'd be happy to help with that. Could you tell me more about what you're looking for?"

        except Exception as e:
            logger.error(f"[{trace_id}] Direct response failed: {e}")
            return f"Hi {user_name}! I'm here to help. What would you like to know?"

    def _validate_mythology(self, content: str, message: str, trace_id: str) -> str:
        """
        Session 997: Validate PA response for mythology/hallucinations.

        Mirrors views_assistant_intelligent.py:175-217.
        Never blocks on failure — returns original content on any error.
        """
        try:
            validation = self.mythology_prevention.validate_response(
                content, message, user=self.user
            )

            if validation.get('mythology_risk', 0) > 0.3:
                logger.warning(
                    f"[{trace_id}] Mythology detected in PA response: "
                    f"risk={validation['mythology_risk']:.2f} patterns={validation.get('patterns_found', [])}"
                )
                try:
                    self.hallucination_flagging.flag_suspicious_response(
                        original_prompt=message,
                        response=content,
                        risk_score=validation['mythology_risk'],
                        patterns=validation.get('patterns_found', []),
                        user=self.user,
                        session_id=trace_id,
                    )
                except Exception as flag_err:
                    logger.warning(f"[{trace_id}] Hallucination flagging failed: {flag_err}")

            if validation.get('needs_regeneration'):
                content += (
                    "\n\n---\n*Note: This response may contain unverified claims. "
                    "Please verify details independently.*"
                )

            return content
        except Exception as e:
            logger.warning(f"[{trace_id}] Mythology validation skipped: {e}")
            return content

    async def _generate_audio(self, text: str, trace_id: str) -> Optional[str]:
        """Generate TTS audio for response."""
        try:
            from core.services.elevenlabs_tts_service import get_elevenlabs_service  # type: ignore[attr-defined]

            tts = get_elevenlabs_service()
            audio_url = await asyncio.to_thread(
                tts.generate_speech,
                text=text,
                voice_id='Rachel',  # Default voice
            )

            logger.info(f"[{trace_id}] Generated audio: {audio_url}")
            return audio_url

        except Exception as e:
            logger.warning(f"[{trace_id}] TTS generation failed: {e}")
            return None

    def _load_conversation_history_from_db(self):
        """
        Session 1030: Load recent PA conversation turns from ChatConversation DB.
        Session 1036: Include tool call metadata + increase response cap from 500→2000.

        This ensures context survives Celery worker recycling (max_tasks_per_child).
        Without this, each new worker child starts with empty conversation_history
        and can't handle follow-up references like "tell me more about those".
        """
        try:
            from django.db import connection
            from core.models import ChatConversation
            # 5s statement timeout: DB connection issues must not block PA startup
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '5000'")
            qs = ChatConversation.objects.filter(
                user=self.user,
            ).exclude(platform='discord')

            if self.conversation_id:
                # Scoped: last 20 exchanges from THIS conversation
                recent = qs.filter(
                    conversation_id=self.conversation_id,
                ).order_by('-created_at')[:20]
            else:
                # Unscoped fallback: last 10 across all conversations (legacy)
                recent = qs.order_by('-created_at')[:10]

            # Build history in chronological order (oldest first)
            turns = []
            for chat in reversed(list(recent)):
                if chat.user_message:
                    meta = chat.metadata or {}
                    src = meta.get('source', '')
                    content = chat.user_message
                    # Prefix non-web messages with source for speaker attribution
                    # (avoids OpenAI 'name' field which affects model behavior)
                    if src and src not in ('web', 'web-dock'):
                        content = f"[{src}] {content}"
                    turn = {
                        'role': 'user',
                        'content': content,
                        'timestamp': chat.created_at.isoformat() if chat.created_at else '',
                    }
                    turns.append(turn)
                if chat.assistant_response:
                    turn = {
                        'role': 'assistant',
                        'content': chat.assistant_response[:8000],  # Session 1085: Was 2000, now 8000 to preserve tool outputs
                        'timestamp': chat.created_at.isoformat() if chat.created_at else '',
                    }
                    # Session 1036: Include tool call metadata for function calling context
                    meta = chat.metadata or {}
                    if meta.get('tool_calls'):
                        turn['tool_calls'] = meta['tool_calls']
                        turn['tool_results'] = meta.get('tool_results', [])
                    if meta.get('response_id'):
                        turn['response_id'] = meta['response_id']
                    turns.append(turn)
            self._conversation_history = turns
            if turns:
                logger.debug(f"Loaded {len(turns)} conversation turns from DB for user {self.user.id}")  # type: ignore[attr-defined]
        except Exception as e:
            logger.debug(f"Could not load conversation history from DB: {e}")
            self._conversation_history = []

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get current conversation history."""
        return self._conversation_history.copy()

    def clear_history(self):
        """Clear conversation history."""
        self._conversation_history = []

    # =========================================================================
    # Session 940: Triage Mode Methods
    # =========================================================================

    async def start_triage(self, triage_type: str = 'attention', batch_size: int = 5) -> str:
        """
        Start triage mode for boardroom items.

        Args:
            triage_type: 'attention' or 'decisions'
            batch_size: Number of items to triage

        Returns:
            First item to triage or message if no items
        """
        # Get items to triage
        result = await self.tool_dispatcher.execute(
            tool_name='governance_tool',
            payload={
                'action': 'triage_batch',
                'triage_type': triage_type,
                'batch_size': batch_size,
            },
            user_id=self.user.id  # type: ignore[attr-defined]
        )

        if not result.ok:
            return f"Failed to start triage: {result.error_message}"

        items = result.result.get('items', [])
        if not items:
            return f"No {triage_type} items to triage. Your boardroom is clear!"

        # Set triage state
        self._triage_mode = True
        self._triage_items = items
        self._triage_index = 0
        self._triage_type = triage_type
        self._triage_stats = {'approved': 0, 'ignored': 0, 'skipped': 0, 'promoted': 0, 'rejected': 0}

        total = result.result.get('total_remaining', len(items))

        return self._format_triage_item(
            items[0],
            1,
            len(items),
            total,
            f"Starting triage of {triage_type} items. I'll walk you through {len(items)} items.\n\n"
        )

    def _format_triage_item(
        self,
        item: Dict[str, Any],
        current: int,
        batch_total: int,
        total_remaining: int,
        prefix: str = ""
    ) -> str:
        """Format a single item for triage display."""
        if self._triage_type == 'attention':
            urgency = item.get('urgency', 'unknown')
            urgency_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡'}.get(urgency, '⚪')

            return f"""{prefix}**Item {current}/{batch_total}** ({total_remaining} total remaining)

{urgency_icon} **{item.get('title', 'Untitled')}**
Type: {item.get('item_type', 'unknown')} | Urgency: {urgency}
Source: {item.get('source_agent', 'System')}

{item.get('summary', 'No summary available.')[:300]}

**ML Recommendation:** {item.get('ml_recommendation', 'No recommendation')}

Reply: **approve**, **ignore**, **skip**, or **stop**"""

        else:  # decisions
            return f"""{prefix}**Decision {current}/{batch_total}** ({total_remaining} total remaining)

**{item.get('topic', 'Untitled')}**
Type: {item.get('decision_type', 'unknown')} | Area: {item.get('impact_area', 'unknown')}

**Recommended Stance:**
{item.get('recommended_stance', 'No stance provided.')[:300]}

**Key Insights:**
{chr(10).join(['- ' + str(i) for i in item.get('key_insights', [])[:3]])}

Reply: **promote**, **reject**, **skip**, or **stop**"""

    async def handle_triage_response(self, response: str) -> str:
        """
        Handle user's response during triage mode.

        Args:
            response: User's response (approve/ignore/skip/stop for attention,
                     promote/reject/skip/stop for decisions)

        Returns:
            Next item or summary
        """
        if not self._triage_mode:
            return "Not in triage mode. Say 'triage attention' or 'triage decisions' to start."

        response_lower = response.lower().strip()
        current_item = self._triage_items[self._triage_index]
        item_id = current_item.get('id')

        # Handle the response
        action_taken = None
        if self._triage_type == 'attention':
            if response_lower in ['approve', 'yes', 'ok', 'y']:
                result = await self.tool_dispatcher.execute(
                    tool_name='governance_tool',
                    payload={'action': 'attention_approve', 'id': item_id},
                    user_id=self.user.id  # type: ignore[attr-defined]
                )
                action_taken = 'approved'
                self._triage_stats['approved'] += 1
            elif response_lower in ['ignore', 'no', 'n', 'dismiss']:
                result = await self.tool_dispatcher.execute(
                    tool_name='governance_tool',
                    payload={'action': 'attention_ignore', 'id': item_id},
                    user_id=self.user.id  # type: ignore[attr-defined]
                )
                action_taken = 'ignored'
                self._triage_stats['ignored'] += 1
            elif response_lower in ['skip', 's', 'next']:
                action_taken = 'skipped'
                self._triage_stats['skipped'] += 1
            elif response_lower in ['stop', 'done', 'exit', 'quit']:
                return self._end_triage()
            else:
                return f"Please reply with **approve**, **ignore**, **skip**, or **stop**."

        else:  # decisions
            if response_lower in ['promote', 'yes', 'ok', 'y', 'approve']:
                result = await self.tool_dispatcher.execute(
                    tool_name='governance_tool',
                    payload={'action': 'decision_promote', 'id': item_id},
                    user_id=self.user.id  # type: ignore[attr-defined]
                )
                action_taken = 'promoted'
                self._triage_stats['promoted'] += 1
            elif response_lower in ['reject', 'no', 'n', 'dismiss']:
                result = await self.tool_dispatcher.execute(
                    tool_name='governance_tool',
                    payload={'action': 'decision_reject', 'id': item_id},
                    user_id=self.user.id  # type: ignore[attr-defined]
                )
                action_taken = 'rejected'
                self._triage_stats['rejected'] += 1
            elif response_lower in ['skip', 's', 'next']:
                action_taken = 'skipped'
                self._triage_stats['skipped'] += 1
            elif response_lower in ['stop', 'done', 'exit', 'quit']:
                return self._end_triage()
            else:
                return f"Please reply with **promote**, **reject**, **skip**, or **stop**."

        # Move to next item
        self._triage_index += 1

        if self._triage_index >= len(self._triage_items):
            return self._end_triage(f"✓ {action_taken.title()}!\n\n")

        # Show next item
        return self._format_triage_item(
            self._triage_items[self._triage_index],
            self._triage_index + 1,
            len(self._triage_items),
            len(self._triage_items) - self._triage_index,
            f"✓ {action_taken.title()}!\n\n"
        )

    def _end_triage(self, prefix: str = "") -> str:
        """End triage mode and show summary."""
        stats = self._triage_stats
        triage_type = self._triage_type

        # Reset state
        self._triage_mode = False
        self._triage_items = []
        self._triage_index = 0
        self._triage_type = None

        if triage_type == 'attention':
            summary = f"""{prefix}**Triage Complete!**

| Action | Count |
|--------|-------|
| Approved | {stats['approved']} |
| Ignored | {stats['ignored']} |
| Skipped | {stats['skipped']} |

Say 'triage attention' to continue with more items, or 'what's in my boardroom' for stats."""
        else:
            summary = f"""{prefix}**Triage Complete!**

| Action | Count |
|--------|-------|
| Promoted | {stats['promoted']} |
| Rejected | {stats['rejected']} |
| Skipped | {stats['skipped']} |

Say 'triage decisions' to continue with more items, or 'what's in my boardroom' for stats."""

        return summary

    @property
    def is_in_triage_mode(self) -> bool:
        """Check if currently in triage mode."""
        return self._triage_mode


# Cache for PA instances per user
_pa_instances: Dict[int, UnifiedPAEntrypoint] = {}


def get_unified_pa(user: User) -> UnifiedPAEntrypoint:
    """
    Get or create UnifiedPA instance for a user.

    Instances are cached per user to maintain conversation history.
    """
    user_id = user.id  # type: ignore[attr-defined]

    if user_id not in _pa_instances:
        _pa_instances[user_id] = UnifiedPAEntrypoint(user)

    return _pa_instances[user_id]


def clear_pa_cache(user_id: Optional[int] = None):
    """Clear PA cache for a specific user or all users."""
    global _pa_instances

    if user_id:
        if user_id in _pa_instances:
            del _pa_instances[user_id]
    else:
        _pa_instances = {}
