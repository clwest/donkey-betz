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

    # Session 959: Intent-to-enrichment mapping
    # Determines which intelligence services fire for each intent
    INTENT_ENRICHMENT_MAP = {
        'content_review':    ['blog_performance', 'domain_context', 'spider_trends'],
        'opportunities':     ['spider_trends', 'domain_context', 'advisor'],
        'predictions':       ['spider_trends', 'domain_context'],
        'initiatives':       ['intelligence_enricher'],
        'boardroom':         ['intelligence_enricher'],
        'system_health':     ['intelligence_enricher'],
        'spider_data':       ['domain_context'],
        'execution_history': ['intelligence_enricher'],
        'learning_patterns': ['spider_trends'],
        'pilots':            ['intelligence_enricher'],
        'gates':             ['intelligence_enricher'],
        'reasoning':         ['intelligence_enricher', 'advisor'],
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
    }

    # Intents where spider_trends and domain_context always apply (no relevance gate)
    DIRECT_RELEVANCE_INTENTS = {
        'content_review', 'opportunities', 'predictions', 'spider_data',
    }

    # Per-section character caps to prevent any one source dominating
    ENRICHMENT_CAPS = {
        'system_brief':     600,
        'spider_trends':    600,
        'blog_performance': 600,
        'domain_context':   600,
        'advisor':          300,
    }

    # Stop words for relevance gating
    STOP_WORDS = frozenset({
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'what', 'which',
        'who', 'how', 'when', 'where', 'why', 'my', 'me', 'i',
        'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from',
    })

    def __init__(self, user: User):
        self.user = user
        self._execution_count = 0
        self._conversation_history: List[Dict[str, Any]] = []

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

        # Session 940: Triage mode state
        self._triage_mode = False
        self._triage_items: List[Dict[str, Any]] = []
        self._triage_index = 0
        self._triage_type = None  # 'attention' or 'decisions'
        self._triage_stats = {'approved': 0, 'ignored': 0, 'skipped': 0, 'promoted': 0, 'rejected': 0}

        logger.info(f"UnifiedPA initialized for user {user.username}")

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
                self._intelligence_enricher = PAIntelligenceEnricher()
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
                    routed_to='boardroom_tool',
                    profile_completeness=None,
                    latency_ms=latency_ms,
                    error=None
                )

            # Session 940: Check for triage start commands
            message_lower = message.lower()
            if 'triage' in message_lower:
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
                    routed_to='boardroom_tool',
                    profile_completeness=None,
                    latency_ms=latency_ms,
                    error=None
                )

            # 1. Build context
            full_context = await self._build_context(message, context)

            # 2. Detect intent and route
            intent, routed_to = self._detect_intent_and_route(message)

            # 3. Execute (tool or direct response)
            tool_runs = []
            if routed_to:
                # Execute via ToolDispatcher
                tool_result = await self.tool_dispatcher.execute(
                    tool_name=routed_to,
                    payload=self._build_tool_payload(message, intent, context),
                    user_id=self.user.id
                )
                tool_runs.append(tool_result.to_dict())

                if tool_result.ok:
                    # Session 959: Enrich tool result with intelligence context
                    enrichment_sections = await self._enrich_tool_result(
                        message, intent, tool_result.result, trace_id
                    )
                    # Generate response from tool result + enrichment
                    content = await self._generate_response_from_tool(
                        message, intent, tool_result.result, full_context, trace_id,
                        enrichment_sections=enrichment_sections
                    )
                else:
                    # Tool failed - generate error response
                    content = f"I encountered an issue: {tool_result.error_message}. " \
                              f"(trace: {tool_result.trace_id})"
            else:
                # No tool needed - direct LLM response
                # Session 948: Special handling for user feedback - be honest about limitations
                if intent == 'user_feedback':
                    content = await self._generate_honest_feedback_response(message, full_context, trace_id)
                else:
                    content = await self._generate_direct_response(message, full_context, trace_id)

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
            self._conversation_history.append({
                'role': 'assistant',
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'trace_id': trace_id
            })

            # Keep only last 20 turns
            if len(self._conversation_history) > 40:
                self._conversation_history = self._conversation_history[-40:]

            latency_ms = int((time.time() - start_time) * 1000)

            # Get profile completeness
            profile_completeness = None
            if self.profile_service:
                try:
                    score = self.profile_service.get_completeness_score(self.user)
                    profile_completeness = int(score * 100)
                except Exception:
                    pass

            logger.info(f"[{trace_id}] Completed in {latency_ms}ms")

            return PAResponse(
                content=content,
                trace_id=trace_id,
                tool_runs=tool_runs,
                audio_url=audio_url,
                intent=intent,
                routed_to=routed_to,
                profile_completeness=profile_completeness,
                latency_ms=latency_ms,
                error=None
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

    async def _build_context(
        self,
        message: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build full context for the request."""
        context = {
            'user_id': self.user.id,
            'username': self.user.username,
            'user_name': self.user.first_name or self.user.username,
            'timestamp': datetime.now().isoformat(),
        }

        # Add conversation history (last 5 turns)
        context['conversation_history'] = self._conversation_history[-10:]

        # Add profile data
        try:
            from core.models import ExtendedUserProfile
            profile = ExtendedUserProfile.objects.filter(user=self.user).first()
            if profile:
                context['profile'] = {
                    'skills': profile.skills or [],
                    'experience': profile.experience,
                    'goals': profile.goals,
                    'work_preference': profile.work_preference,
                    'desired_income': profile.desired_income,
                    'availability': profile.availability,
                }
        except Exception as e:
            logger.debug(f"Failed to load profile: {e}")

        # Add dynamic system knowledge if relevant
        if self.knowledge_injector:
            try:
                knowledge_context = self.knowledge_injector.get_context_for_query(message)
                if knowledge_context.get('has_dynamic_context'):
                    context['system_knowledge'] = knowledge_context
            except Exception as e:
                logger.debug(f"Failed to inject knowledge: {e}")

        # Add system stats
        try:
            context['system_stats'] = await self._get_system_stats()
        except Exception as e:
            logger.debug(f"Failed to get system stats: {e}")

        # Session 943: Inject docs context so PA knows about system architecture,
        # recent sessions, and what we've been working on
        if self.docs_context_builder:
            try:
                docs_context = await asyncio.to_thread(
                    self.docs_context_builder.build_context_for_agent,
                    agent_name='personal_assistant',
                    task=message,
                    max_docs=8,
                    include_recent_sessions=True,
                    include_content_snippets=False,  # Keep context size manageable
                    include_critical_docs=True  # Always include CLAUDE.md, 00-START-NEXT-SESSION.md
                )
                if docs_context.get('has_docs'):
                    context['docs_context'] = docs_context
                    logger.debug(f"📚 [Session 943] PA docs context: {len(docs_context.get('relevant_docs', []))} docs")
            except Exception as e:
                logger.debug(f"Failed to inject docs context: {e}")

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

        # Session 940: Boardroom patterns (takes precedence for boardroom-specific requests)
        if 'boardroom' in message_lower or any(word in message_lower for word in [
            'draft decision', 'promote decision', 'reject decision', 'canonical'
        ]):
            return ('boardroom', 'boardroom_tool')

        # Decision/attention patterns
        if any(word in message_lower for word in [
            'decision', 'pending', 'attention', 'approve', 'reject', 'review'
        ]):
            return ('boardroom', 'boardroom_tool')  # Session 940: Route to boardroom_tool

        # System health patterns
        if any(word in message_lower for word in [
            'health', 'status', 'vitals', 'body', 'system health'
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

        # Session 948: User feedback/issues/complaints - be honest about limitations
        # These are things the PA can't fix with tools - requires code changes
        # IMPORTANT: This must come BEFORE reasoning patterns to avoid false triggers
        feedback_indicators = [
            # Problem statements
            'not working', 'doesn\'t work', 'broken', 'bug', 'issue',
            'problem with', 'can\'t access', 'cannot access', 'losing context',
            'context lost', 'context loss', 'disconnect', 'not connected',
            'spread out', 'fragmented', 'difficult to', 'hard to',
            # Feature requests disguised as complaints
            'should be', 'need to be', 'would be better', 'wish',
            'why can\'t', 'why isn\'t', 'why doesn\'t',
        ]
        if any(phrase in message_lower for phrase in feedback_indicators):
            # Check if this is actually a fixable issue or needs code changes
            fixable_keywords = ['approve', 'reject', 'list', 'show', 'what', 'how']
            is_actionable = any(kw in message_lower for kw in fixable_keywords)
            if not is_actionable:
                return ('user_feedback', None)  # No tool - direct honest response

        # Reasoning patterns - only for genuine reasoning requests
        if any(word in message_lower for word in [
            'analyze deeply', 'reflect on', 'think about this'
        ]):
            return ('reasoning', 'reasoning_engine_tool')

        # Opportunity patterns
        if any(word in message_lower for word in [
            'opportunity', 'opportunities', 'job', 'gig', 'income'
        ]):
            return ('opportunities', 'opportunity_manager_tool')

        # Session 943: Content REVIEW patterns - MUST come before content creation patterns
        # These are for viewing/reviewing existing content, not creating new
        # Session 957: Added blog/report query patterns for "what blogs have been written by agents"
        if any(phrase in message_lower for phrase in [
            'what content', 'content created', 'content been created',
            'show content', 'list content', 'my content', 'created content',
            'deliverable', 'content ready', 'ready for review',
            'ready to publish', 'publish content', 'archive content',
            'content stats', 'review content', 'view content',
            # Session 957: Blog/report query patterns
            'what blogs', 'blogs written', 'written by agents', 'agent written',
            'list blogs', 'show blogs', 'blog posts', 'what reports',
            'reports written', 'what has been written', 'produced by agents',
            'agent outputs', 'agent content', 'agent created'
        ]):
            return ('content_review', 'content_review_tool')

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

        if any(word in message_lower for word in [
            'create video', 'generate video', 'animate'
        ]):
            return ('video_creation', 'video_generation_agent')

        # Content writing - only for actual creation requests
        # Note: "blog" alone could mean viewing OR creating, so we check for creation verbs
        if any(phrase in message_lower for phrase in [
            'write', 'create content', 'create a blog', 'write a blog',
            'draft', 'compose', 'generate article'
        ]):
            return ('content_writing', 'content_writer_agent')

        # Research patterns
        if any(word in message_lower for word in [
            'search', 'find', 'research', 'what is', 'trending'
        ]):
            return ('research', 'web_search')

        # Agent invocation patterns
        if any(word in message_lower for word in [
            'run agent', 'execute agent', 'use agent', 'ask agent'
        ]):
            return ('agent_execution', 'universal_agent_tool')

        # Session 943: Initiative/project patterns
        if any(word in message_lower for word in [
            'initiative', 'initiatives', 'project', 'projects',
            'pipeline', 'stage', 'action item', 'action items',
            'what are we working on', 'active projects', 'current projects'
        ]):
            return ('initiatives', 'initiative_tool')

        # Session 948: Spider data patterns
        if any(word in message_lower for word in [
            'spider', 'spiders', 'crawl', 'crawled', 'collected data',
            'intelligence', 'news feed', 'what have spiders', 'spider data'
        ]):
            return ('spider_data', 'spider_data_tool')

        # Session 948: Execution history patterns
        if any(word in message_lower for word in [
            'execution', 'executions', 'agent history', 'what agents did',
            'agent activity', 'recent activity', 'what has been running',
            'agent failures', 'failed agents'
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
        payload = {
            'query': message,
            'task': message,
            'action': 'list',  # Default action
        }

        # Intent-specific payload adjustments
        # Session 940: Boardroom tool actions
        # Session 947: Enhanced to extract urgency filters and handle "list critical" patterns
        if intent == 'boardroom':
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

            # Extract ID if present (e.g., "approve attention item abc123")
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

            # Determine action based on message
            if 'recent' in msg_lower or 'latest' in msg_lower or 'this week' in msg_lower:
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

        # Session 943: Content review tool payload
        elif intent == 'content_review':
            msg_lower = message.lower()

            # Determine action based on message
            if 'stats' in msg_lower or 'statistics' in msg_lower or 'how many' in msg_lower:
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
            elif 'detail' in msg_lower or 'show' in msg_lower:
                payload['action'] = 'details'
                import re
                id_match = re.search(r'([a-f0-9-]{36}|[a-f0-9]{8,})', msg_lower)
                if id_match:
                    payload['id'] = id_match.group(1)
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
            if 'stats' in msg_lower or 'overview' in msg_lower or 'pipeline' in msg_lower:
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
                        sections['system_brief'] = text

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
                            sections['spider_trends'] = text

                elif service_key == 'advisor' and self.advisor_context_builder:
                    result = await asyncio.to_thread(
                        self.advisor_context_builder.build_context_for_agent,
                        'personal_assistant', message
                    )
                    if isinstance(result, dict) and result.get('key_principles'):
                        principles = result['key_principles'][:3]
                        sections['advisor'] = '\n'.join(
                            f"- {p}" if isinstance(p, str) else f"- {p}"
                            for p in principles
                        )

            except Exception as e:
                logger.warning(f"[{trace_id}] Enrichment '{service_key}' failed: {e}")

        # Truncate each section to its cap
        for key, text in sections.items():
            cap = self.ENRICHMENT_CAPS.get(key, 600)
            if len(text) > cap:
                sections[key] = text[:cap] + '...'

        return sections

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
        base = f"""You are {user_name}'s intelligent personal assistant on a unified AI platform with \
74 AI agents, 77 data spiders, and 25 legendary advisors.

You are NOT a data listing tool. You are an analytical advisor.

RESPONSE FORMAT:
1. Start with 1-2 sentences of KEY INSIGHT (the most important finding)
2. Then your ANALYSIS with patterns, risks, and opportunities - reference specific item IDs
3. End with RECOMMENDED ACTIONS (1-3 concrete next steps)

IMPORTANT: The raw data listing with IDs is already shown to the user separately.
Do NOT repeat the full list. Only reference items by ID when analyzing them.

RULES:
- Lead with insight, not counts
- Reference item IDs when discussing specific items
- Highlight risks, opportunities, and anomalies
- Be direct and decisive, not hedging
- Do NOT reuse the same trend/incident across unrelated answers - only cite trends if they materially affect the user's question"""

        intent_directives = {
            'content_review': (
                "FOCUS: Evaluate content quality. Scores >0.8 are publish-ready, <0.5 need work. "
                "Compare novelty vs structure scores. Identify best and weakest topics. "
                "Flag any that need fact-checking against spider data. Recommend a publishing strategy."
            ),
            'opportunities': (
                "FOCUS: Evaluate viability and urgency of each opportunity. "
                "Cross-reference with spider trends. Prioritize by ROI potential. "
                "Flag time-sensitive items."
            ),
            'initiatives': (
                "FOCUS: Assess pipeline health. Identify bottlenecks, blockers, and stale items "
                "(check last_activity_at). Highlight at-risk initiatives and critical action items. "
                "Recommend which initiatives need attention now."
            ),
            'spider_data': (
                "FOCUS: Identify patterns and clusters in the spider data. "
                "Highlight emerging trends. Suggest applications and next actions."
            ),
            'execution_history': (
                "FOCUS: Identify declining agents and systemic failures. "
                "Compare performance to averages. Highlight outliers."
            ),
            'system_health': (
                "FOCUS: Lead with critical issues. Assess trajectory (improving/declining). "
                "Recommend preventive actions before problems escalate."
            ),
            'boardroom': (
                "FOCUS: Summarize the decision landscape. Highlight urgency levels. "
                "Recommend triage order. Note any items linked to active initiatives."
            ),
        }

        canonical_intent = self.INTENT_ALIASES.get(intent, intent)
        directive = intent_directives.get(canonical_intent, '')

        parts = [base]
        if directive:
            parts.append(f"\n{directive}")

        # Add enrichment sections (only if non-empty)
        section_labels = {
            'system_brief': 'SYSTEM BRIEF',
            'spider_trends': 'REAL-TIME TRENDS',
            'blog_performance': 'PERFORMANCE CONTEXT',
            'domain_context': 'DOMAIN CONTEXT',
            'advisor': 'ADVISOR PRINCIPLES',
        }
        for key, label in section_labels.items():
            text = enrichment_sections.get(key, '')
            if text:
                parts.append(f"\n=== {label} ===\n{text}")

        # Add the data to analyze
        tool_str = str(tool_result)
        if len(tool_str) > 3000:
            tool_str = tool_str[:3000] + '...'

        parts.append(f'\n=== DATA TO ANALYZE ===\nUser asked: "{message}"\nTool returned: {tool_str}')

        return '\n'.join(parts)

    async def _generate_response_from_tool(
        self,
        message: str,
        intent: str,
        tool_result: Any,
        context: Dict[str, Any],
        trace_id: str,
        enrichment_sections: Dict[str, str] = None
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

        # If we have enrichment, get LLM analysis and APPEND it to structured output
        if has_enrichment:
            system_prompt = self._build_analytical_prompt(
                message, intent, tool_result, enrichment_sections,
                user_name, context
            )
            try:
                result = await asyncio.to_thread(
                    self.llm_enforcer.enforce_real_ai,
                    prompt=f"Analyze and advise on this data: {tool_result}",
                    context=system_prompt,
                    agent_name="UnifiedPA",
                    task_type="analysis",
                    max_tokens=2000
                )
                if result.get('success'):
                    llm_analysis = result.get('response', '')
                    if llm_analysis:
                        return f"{structured_output}\n\n---\n\n{llm_analysis}"
            except Exception as e:
                logger.warning(f"[{trace_id}] LLM analysis failed: {e}")

        # Fallback: no enrichment or LLM failed
        # For non-structured intents without enrichment, use original LLM summarization
        if intent not in ['initiatives', 'brainstorming', 'content_review',
                          'boardroom', 'decision_management']:
            system_prompt = f"""You are a helpful AI assistant.
The user asked: "{message}"
You executed a tool and got this result:
{tool_result}

Generate a helpful, conversational response summarizing this information for {user_name}.
Be concise but informative. Use bullet points for lists.
Address the user by name occasionally."""
            try:
                result = await asyncio.to_thread(
                    self.llm_enforcer.enforce_real_ai,
                    prompt=f"Summarize this tool result: {tool_result}",
                    context=system_prompt,
                    agent_name="UnifiedPA",
                    task_type="conversation",
                    max_tokens=2000
                )
                if result.get('success'):
                    return result.get('response', structured_output)
            except Exception:
                pass

        return structured_output

    def _format_tool_result(
        self,
        tool_result: Any,
        intent: str,
        user_name: str
    ) -> str:
        """Simple formatting fallback for tool results."""
        if isinstance(tool_result, dict):
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
                        critical = by_urgency.get('critical', 0)
                        high = by_urgency.get('high', 0)
                        response += f"**Attention Items:** {att_count}\n"
                        if critical > 0:
                            response += f"  - {critical} CRITICAL urgency\n"
                        if high > 0:
                            response += f"  - {high} high urgency\n"

                    if decisions.get('count', 0) > 0:
                        dec_count = decisions['count']
                        by_type = decisions.get('by_type', {})
                        response += f"\n**Draft Decisions:** {dec_count}\n"
                        for dtype, count in list(by_type.items())[:3]:
                            response += f"  - {count} {dtype}\n"

                    response += "\nI can help you list, approve, ignore, promote, or reject items."
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

                    # Session 947/959: Show items with IDs + new ML/priority fields
                    item_lines = []
                    for item in items[:15]:
                        item_id = str(item.get('id', ''))[:8]  # Short ID for reference
                        title = item.get('title', item.get('topic', 'Untitled'))[:60]
                        urgency = item.get('urgency', item.get('decision_type', ''))
                        source = item.get('source_agent', '')
                        ml_rec = item.get('ml_recommendation', '')
                        priority = item.get('priority_score') or 0
                        confidence = item.get('ml_confidence')
                        impact = item.get('impact_estimate', '')

                        line = f"• **{title}**"
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
                        line += f" `{item_id}`"
                        item_lines.append(line)

                    item_list = "\n".join(item_lines)

                    # Build header
                    filter_desc = ""
                    if filters_applied.get('urgency'):
                        filter_desc = f" {filters_applied['urgency'].upper()}"

                    remaining = count - len(items[:15])
                    more_text = f"\n\n*Showing {min(count, 15)} of {count} items.*" if remaining > 0 else ""

                    return f"Found {count}{filter_desc} items:\n\n{item_list}{more_text}\n\nTo act on an item, say 'approve item [id]' or 'ignore item [id]'."

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
                return f"System health: {health.upper()} ({score}%)"

            elif intent in ['predictions', 'pilots', 'gates']:
                action = tool_result.get('action', 'list')
                count = tool_result.get('count', 0)
                return f"Found {count} {intent}: {tool_result}"

            # Session 943: Brainstorming results formatting
            elif intent == 'brainstorming':
                action = tool_result.get('action', '')

                if action == 'search':
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
                        quality = item.get('quality_score', 0)
                        response += f"- **{title}** ({content_type}, quality: {quality:.0%})\n"

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
                        quality = item.get('quality_score', 0)

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

                elif action == 'stats':
                    ready = tool_result.get('ready_for_review', 0)
                    drafts = tool_result.get('drafts', 0)
                    published = tool_result.get('published', 0)
                    by_type = tool_result.get('by_type', {})

                    response = f"Content statistics, {user_name}:\n\n"
                    response += f"- **Ready for review:** {ready}\n"
                    response += f"- **Drafts:** {drafts}\n"
                    response += f"- **Published:** {published}\n"

                    if by_type:
                        response += "\n**Ready by type:**\n"
                        for t, c in by_type.items():
                            response += f"- {t}: {c}\n"

                    return response

                elif action == 'details':
                    title = tool_result.get('title', 'Untitled')
                    content_type = tool_result.get('type', 'document')
                    status = tool_result.get('status', 'unknown')
                    quality = tool_result.get('quality_score', 0)
                    preview = tool_result.get('content_preview', '')[:300]
                    item_id = tool_result.get('id', '')

                    response = f"**{title}**\n\n"
                    response += f"- Type: {content_type}\n"
                    response += f"- Status: {status}\n"
                    response += f"- Quality: {quality:.0%}\n"
                    response += f"- Agent: {tool_result.get('agent_name', 'Unknown')}\n"
                    response += f"\n**Preview:**\n{preview}..."

                    if status == 'ready':
                        response += f"\n\nSay 'publish {item_id[:8]}' to publish or 'archive {item_id[:8]}' to reject."

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

                else:
                    return str(tool_result)

            # Session 943: Initiative results formatting
            elif intent == 'initiatives':
                action = tool_result.get('action', '')

                if action == 'list':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No initiatives found matching your criteria, {user_name}."

                    response = f"Found {count} initiatives:\n\n"
                    for item in items[:7]:
                        name = item.get('name', 'Untitled')[:40]
                        stage = item.get('current_stage', 1)
                        purpose = item.get('purpose', 'unknown')
                        pending = item.get('pending_actions', 0)
                        critical = item.get('critical_actions', 0)
                        status_icon = '🟢' if item.get('status') == 'ACTIVE' else '⏸️'
                        response += f"{status_icon} **{name}** (Stage {stage}/5, {purpose})"
                        if pending > 0:
                            action_desc = f"{pending} action items"
                            if critical > 0:
                                action_desc += f" ({critical} critical)"
                            response += f" - {action_desc}"
                        response += "\n"

                    if count > 7:
                        response += f"\n...and {count - 7} more."

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
                    description = tool_result.get('description', '')[:200]
                    status = tool_result.get('status', 'unknown')
                    stage = tool_result.get('current_stage', 1)
                    purpose = tool_result.get('purpose', 'unknown')
                    program = tool_result.get('program', 'unknown')
                    action_items = tool_result.get('action_items', [])

                    status_icon = '🟢' if status == 'ACTIVE' else ('✅' if status == 'COMPLETED' else '⏸️')

                    response = f"{status_icon} **{name}**\n\n"
                    response += f"- Status: {status}\n"
                    response += f"- Stage: {stage}/5\n"
                    response += f"- Purpose: {purpose}\n"
                    response += f"- Program: {program}\n"

                    if description:
                        response += f"\n**Description:** {description}...\n"

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

                else:
                    return str(tool_result)

            # Session 948: Spider data results formatting
            elif intent == 'spider_data':
                action = tool_result.get('action', '')

                if action == 'recent':
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)
                    period = tool_result.get('period_hours', 24)

                    if count == 0:
                        return f"No spider data collected in the last {period} hours, {user_name}."

                    response = f"Spider intelligence from the last {period} hours ({count} items):\n\n"
                    for item in items[:8]:
                        spider = item.get('spider_name', 'Unknown')
                        title = item.get('title', item.get('url', 'No title'))[:50]
                        category = item.get('category', '')
                        response += f"- **{spider}**: {title}"
                        if category:
                            response += f" [{category}]"
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
                        title = item.get('title', item.get('url', 'No title'))[:60]
                        date = item.get('collected_at', '')[:10]
                        response += f"- {title} ({date})\n"

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
                        title = item.get('title', item.get('url', 'No title'))[:50]
                        response += f"- {title} (via {spider})\n"

                    return response

                elif action == 'search':
                    query = tool_result.get('query', '')
                    items = tool_result.get('items', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No spider data matching '{query}', {user_name}."

                    response = f"Found {count} items matching '{query}':\n\n"
                    for item in items[:6]:
                        spider = item.get('spider_name', 'Unknown')
                        title = item.get('title', item.get('url', 'No title'))[:50]
                        response += f"- **{spider}**: {title}\n"

                    return response

                elif action == 'stats':
                    total = tool_result.get('total_items', 0)
                    by_spider = tool_result.get('by_spider', {})
                    by_category = tool_result.get('by_category', {})
                    recent = tool_result.get('items_last_24h', 0)

                    response = f"Spider Network Stats, {user_name}:\n\n"
                    response += f"- **Total collected:** {total}\n"
                    response += f"- **Last 24 hours:** {recent}\n\n"

                    if by_spider:
                        response += "**Top spiders:**\n"
                        for spider, cnt in list(by_spider.items())[:5]:
                            response += f"- {spider}: {cnt} items\n"

                    if by_category:
                        response += "\n**By category:**\n"
                        for cat, cnt in list(by_category.items())[:5]:
                            response += f"- {cat}: {cnt} items\n"

                    return response

                else:
                    return str(tool_result)

            # Session 948: Execution history results formatting
            elif intent == 'execution_history':
                action = tool_result.get('action', '')

                if action == 'recent':
                    executions = tool_result.get('executions', [])
                    count = tool_result.get('count', 0)
                    period = tool_result.get('period_hours', 24)

                    if count == 0:
                        return f"No agent executions in the last {period} hours, {user_name}."

                    response = f"Recent agent activity ({count} executions in {period}h):\n\n"
                    for ex in executions[:8]:
                        agent = ex.get('agent_name', 'Unknown')
                        status = ex.get('status', 'unknown')
                        status_icon = '✅' if status == 'completed' else ('❌' if status == 'failed' else '⏳')
                        duration = ex.get('duration_seconds', 0)
                        response += f"{status_icon} **{agent}**"
                        if duration:
                            response += f" ({duration:.1f}s)"
                        response += "\n"

                    if count > 8:
                        response += f"\n...and {count - 8} more executions."
                    return response

                elif action == 'by_agent':
                    agent = tool_result.get('agent_name', 'Unknown')
                    executions = tool_result.get('executions', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No recent executions from {agent}, {user_name}."

                    response = f"**{agent}** execution history ({count} total):\n\n"
                    for ex in executions[:6]:
                        status = ex.get('status', 'unknown')
                        status_icon = '✅' if status == 'completed' else ('❌' if status == 'failed' else '⏳')
                        date = ex.get('created_at', '')[:16]
                        topic = ex.get('topic', '')[:40]
                        response += f"{status_icon} {date}"
                        if topic:
                            response += f" - {topic}"
                        response += "\n"

                    return response

                elif action == 'stats':
                    total = tool_result.get('total_executions', 0)
                    successful = tool_result.get('successful', 0)
                    failed = tool_result.get('failed', 0)
                    success_rate = tool_result.get('success_rate', 0)
                    by_agent = tool_result.get('by_agent', {})
                    avg_duration = tool_result.get('avg_duration_seconds', 0)

                    response = f"Agent Execution Stats, {user_name}:\n\n"
                    response += f"- **Total executions:** {total}\n"
                    response += f"- **Successful:** {successful} ✅\n"
                    response += f"- **Failed:** {failed} ❌\n"
                    response += f"- **Success rate:** {success_rate:.1f}%\n"
                    response += f"- **Avg duration:** {avg_duration:.1f}s\n\n"

                    if by_agent:
                        response += "**Most active agents:**\n"
                        for agent, cnt in list(by_agent.items())[:5]:
                            response += f"- {agent}: {cnt} executions\n"

                    return response

                elif action == 'failures':
                    failures = tool_result.get('failures', [])
                    count = tool_result.get('count', 0)

                    if count == 0:
                        return f"No recent failures, {user_name}. System is running smoothly!"

                    response = f"Recent agent failures ({count}):\n\n"
                    for f in failures[:6]:
                        agent = f.get('agent_name', 'Unknown')
                        error = f.get('error_message', 'Unknown error')[:60]
                        date = f.get('created_at', '')[:16]
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
                        confidence = p.get('confidence', 0)
                        response += f"- **{pattern_type}** ({confidence:.0%}): {description}\n"

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
                        confidence = p.get('confidence', 0)
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

            else:
                return str(tool_result)
        else:
            return str(tool_result)

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
            user_name = self.user.username if hasattr(self.user, 'username') else 'unknown'

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
        system_prompt = f"""You are the Personal Assistant for {user_name} in the Unified AI Platform.

SYSTEM CAPABILITIES:
- {stats.get('agent_count', 74)} AI Agents available
- {stats.get('spider_count', 77)} Active Spiders collecting data
- {stats.get('advisor_count', 25)} Legendary Advisors

USER PROFILE:
- Skills: {profile.get('skills', 'Not specified')}
- Goals: {profile.get('goals', 'Not specified')}

Be helpful, conversational, and personalized. Address the user by name."""

        # Session 943: Add docs context so PA knows about system architecture and recent work
        if docs_context.get('has_docs'):
            docs_summary = docs_context.get('summary', '')
            if docs_summary:
                # Truncate if too long to keep context manageable
                if len(docs_summary) > 4000:
                    docs_summary = docs_summary[:4000] + "\n... (truncated)"
                system_prompt += f"\n\n{docs_summary}"
                logger.debug(f"[{trace_id}] Added docs context to PA prompt ({len(docs_summary)} chars)")

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

    async def _generate_audio(self, text: str, trace_id: str) -> Optional[str]:
        """Generate TTS audio for response."""
        try:
            from core.services.elevenlabs_tts_service import get_elevenlabs_service

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
            tool_name='boardroom_tool',
            payload={
                'action': 'get_triage_batch',
                'triage_type': triage_type,
                'batch_size': batch_size,
            },
            user_id=self.user.id
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
                    tool_name='boardroom_tool',
                    payload={'action': 'approve_attention', 'id': item_id},
                    user_id=self.user.id
                )
                action_taken = 'approved'
                self._triage_stats['approved'] += 1
            elif response_lower in ['ignore', 'no', 'n', 'dismiss']:
                result = await self.tool_dispatcher.execute(
                    tool_name='boardroom_tool',
                    payload={'action': 'ignore_attention', 'id': item_id},
                    user_id=self.user.id
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
                    tool_name='boardroom_tool',
                    payload={'action': 'promote_decision', 'id': item_id},
                    user_id=self.user.id
                )
                action_taken = 'promoted'
                self._triage_stats['promoted'] += 1
            elif response_lower in ['reject', 'no', 'n', 'dismiss']:
                result = await self.tool_dispatcher.execute(
                    tool_name='boardroom_tool',
                    payload={'action': 'reject_decision', 'id': item_id},
                    user_id=self.user.id
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
    user_id = user.id

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
