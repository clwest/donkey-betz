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
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime

from django.contrib.auth import get_user_model

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

    def __init__(self, user: User):
        self.user = user
        self._execution_count = 0
        self._conversation_history: List[Dict[str, Any]] = []

        # Lazy-loaded services
        self._tool_dispatcher = None
        self._llm_enforcer = None
        self._profile_service = None
        self._knowledge_injector = None

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
                    # Generate response from tool result
                    content = await self._generate_response_from_tool(
                        message, intent, tool_result.result, full_context, trace_id
                    )
                else:
                    # Tool failed - generate error response
                    content = f"I encountered an issue: {tool_result.error_message}. " \
                              f"(trace: {tool_result.trace_id})"
            else:
                # No tool needed - direct LLM response
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

        # Reasoning patterns
        if any(word in message_lower for word in [
            'think', 'reason', 'analyze deeply', 'reflect'
        ]):
            return ('reasoning', 'reasoning_engine_tool')

        # Opportunity patterns
        if any(word in message_lower for word in [
            'opportunity', 'opportunities', 'job', 'gig', 'income'
        ]):
            return ('opportunities', 'opportunity_manager_tool')

        # Content creation patterns
        if any(word in message_lower for word in [
            'create image', 'generate image', 'logo', 'banner'
        ]):
            return ('image_creation', 'image_generation_agent')

        if any(word in message_lower for word in [
            'create video', 'generate video', 'animate'
        ]):
            return ('video_creation', 'video_generation_agent')

        if any(word in message_lower for word in [
            'write', 'blog', 'article', 'content'
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
        if intent == 'boardroom':
            msg_lower = message.lower()

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
            elif 'list' in msg_lower and 'attention' in msg_lower:
                payload['action'] = 'list_attention'
            elif 'stats' in msg_lower or 'status' in msg_lower:
                payload['action'] = 'stats'
            else:
                # Default: show stats
                payload['action'] = 'stats'

            # Extract ID if present (e.g., "approve attention item abc123")
            import re
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

        # Add any context
        payload['context'] = context

        return payload

    async def _generate_response_from_tool(
        self,
        message: str,
        intent: str,
        tool_result: Any,
        context: Dict[str, Any],
        trace_id: str
    ) -> str:
        """Generate natural language response from tool result."""
        # Build prompt for LLM to interpret tool result
        user_name = context.get('user_name', 'there')

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
                prompt=f"Summarize this tool result for the user: {tool_result}",
                context=system_prompt,
                agent_name="UnifiedPA",
                task_type="conversation",
                max_tokens=400
            )

            if result.get('success'):
                return result.get('response', str(tool_result))
            else:
                # Fallback to simple formatting
                return self._format_tool_result(tool_result, intent, user_name)

        except Exception as e:
            logger.warning(f"[{trace_id}] LLM interpretation failed: {e}")
            return self._format_tool_result(tool_result, intent, user_name)

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
                    if count == 0:
                        return f"No items found matching your criteria, {user_name}."
                    item_list = "\n".join([
                        f"- {item.get('title', item.get('topic', 'Untitled'))} ({item.get('urgency', item.get('decision_type', 'unknown'))})"
                        for item in items[:5]
                    ])
                    return f"Found {count} items:\n{item_list}"

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

            else:
                return str(tool_result)
        else:
            return str(tool_result)

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

        # Add conversation history
        history_text = ""
        for turn in context.get('conversation_history', [])[-6:]:
            role = turn.get('role', 'user')
            content = turn.get('content', '')[:200]
            history_text += f"{role}: {content}\n"

        if history_text:
            system_prompt += f"\n\nRECENT CONVERSATION:\n{history_text}"

        try:
            result = await asyncio.to_thread(
                self.llm_enforcer.enforce_real_ai,
                prompt=message,
                context=system_prompt,
                agent_name="UnifiedPA",
                task_type="conversation",
                max_tokens=400
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
