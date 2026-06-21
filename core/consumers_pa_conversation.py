"""
PA Conversation WebSocket Consumer
===================================

Real-time 3-way chat between User (ChatUI), Claude Code (CLI), and Rigby (PA).

WebSocket endpoint: ws/pa/conversations/<conversation_id>/
Group name: pa_conversation_<conversation_id>

Events pushed to clients:
- message.created: New message from any participant (user, claude-code, pa)
- participant.typing: Typing indicator
- participant.joined: A participant connected
- rigby.tool.started: PA started a tool call (Session 1172, live ticker)
- rigby.tool.completed: PA finished a tool call (Session 1172, live ticker)

Broadcast from backend via:
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"pa_conversation_{conversation_id}",
        {"type": "message.created", "message": {...}}
    )
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

logger = logging.getLogger(__name__)


# Session 1175 PR-2b-2: module-level helpers for agent-completion persistence.
# Split out so tests can drive them directly with a real DB and skip the async
# / channels machinery. The consumer wraps each via database_sync_to_async in
# its async agent_completed handler.

def compose_completion_body(
    *, execution_id, agent_name, status, error_signature, artifact_pointers, is_background,
):
    """Pure-sync, no-DB. The text Rigby authors for an agent-completion follow-up.

    Idempotent: the "Background completion: " prefix is added at most once per call
    (and the consumer's flow only invokes this once per agent_completed event), so
    rerunning the helper on the same inputs always produces the same body.
    """
    if status == 'completed':
        body = f"Agent **{agent_name}** finished (execution `{execution_id}`)."
    elif status == 'failed':
        err = f" — `{error_signature}`" if error_signature else ""
        body = f"Agent **{agent_name}** failed (execution `{execution_id}`){err}."
    else:
        body = f"Agent **{agent_name}** ended with status `{status}` (execution `{execution_id}`)."

    ptr_lines = []
    for kind in ('deliverable_ids', 'blog_ids', 'media_ids'):
        ids = (artifact_pointers or {}).get(kind) or []
        if ids:
            ptr_lines.append(f"- {kind.replace('_', ' ')}: {', '.join(str(i) for i in ids[:5])}")
    if ptr_lines:
        body += "\n\nArtifacts:\n" + "\n".join(ptr_lines)

    if is_background:
        body = "Background completion: " + body
    return body


def check_background_completion(*, conversation_id, execution_id):
    """Rigby's stricter "user moved on" detector (sync, DB-bound).

    True iff there exists a ChatConversation in this conversation_id with:
    - user_message non-empty (real user turn, not a structured/system message)
    - created_at > subscription.created_at (post-dispatch)
    - metadata.kind != 'agent_completion' (so prior follow-ups don't self-trigger)

    metadata.kind exclusion uses ``__contains`` (Postgres JSONB containment) rather
    than ``metadata__kind=...`` because the latter treats rows where ``metadata={}``
    (no ``kind`` key) as NULL → NOT excluded in Postgres ternary logic. ``__contains``
    only matches rows whose JSONB actually contains the ``{'kind': 'agent_completion'}``
    subset, so default-metadata rows are correctly kept.
    """
    from core.models.conversations.models import ChatConversation
    from core.models_unified_system import AgentFollowupSubscription
    try:
        sub = AgentFollowupSubscription.objects.filter(
            execution_id=execution_id,
            conversation_id=conversation_id,
        ).only('created_at').first()
        if not sub:
            return False
        return ChatConversation.objects.filter(
            conversation_id=conversation_id,
            created_at__gt=sub.created_at,
        ).exclude(user_message='').exclude(
            metadata__contains={'kind': 'agent_completion'},
        ).exists()
    except Exception:
        return False


def create_completion_row(
    *, user, conversation_id, execution_id, agent_name, status, completed_at,
    error_signature, artifact_pointers, assistant_response,
):
    """Write the Rigby-authored completion row (sync, DB-bound). Idempotent per
    (conversation_id, execution_id) pair — Session 1180 P1: when multiple
    PAConversationConsumer instances (one per browser tab) all receive the same
    channels group_send agent.completed event, each calls this helper; the
    metadata-lookup short-circuit prevents N tabs from writing N duplicate rows.

    Uses assistant_response (renders as Rigby bubble) per the ratified Session 1175
    design — existing precedent in collaboration_protocol uses user_message which
    would misattribute the message as a user turn. source='pa' matches other Rigby
    turns. Q-C investigation found ChatConversation has zero post_save signals, so
    the write is fire-and-forget — no token/embedding/unread side effects to mirror.
    """
    from core.models.conversations.models import ChatConversation
    from core.models_unified_system import AgentFollowupSubscription
    sub = AgentFollowupSubscription.objects.filter(
        execution_id=execution_id,
        conversation_id=conversation_id,
    ).only('id').first()
    # Idempotency check: if another consumer already wrote the completion row for
    # this (conversation_id, execution_id), reuse it. No DB-level unique constraint
    # yet (JSON-expression partial index deferred to a later PR per Session 1180
    # Rigby ratification); app-level get_or_create-equivalent is the v1 path.
    existing = ChatConversation.objects.filter(
        conversation_id=conversation_id,
        metadata__contains={'kind': 'agent_completion', 'execution_id': execution_id},
    ).first()
    if existing is not None:
        return existing
    return ChatConversation.objects.create(
        user=user if (user and getattr(user, 'is_authenticated', False)) else None,
        conversation_id=conversation_id,
        user_message='',
        assistant_response=assistant_response,
        source='pa',
        platform='api',
        metadata={
            'kind': 'agent_completion',
            'execution_id': execution_id,
            'subscription_id': str(sub.id) if sub else None,
            'agent_name': agent_name,
            'status': status,
            'completed_at': completed_at,
            'error_signature': error_signature,
            'artifact_pointers': artifact_pointers,
        },
    )


class PAConversationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time PA conversation streaming.
    Enables 3-way chat: User + Claude Code + Rigby.
    """

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or isinstance(self.user, AnonymousUser):
            await self.close(code=4001)
            return

        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id', '')
        if not self.conversation_id:
            await self.close(code=4002)
            return

        self.room_group_name = f"pa_conversation_{self.conversation_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        logger.info(f"[PA-WS] Connected: user={self.user.username} conversation={self.conversation_id}")

        # Notify group that a participant joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "participant.joined",
                "participant": self.user.username,
                "source": "web",
                "timestamp": timezone.now().isoformat(),
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"[PA-WS] Disconnected: conversation={getattr(self, 'conversation_id', '?')}")

    async def receive(self, text_data):
        """Handle incoming messages from the WebSocket client (future use for typing indicators)."""
        try:
            data = json.loads(text_data)
            msg_type = data.get('type', '')

            if msg_type == 'typing':
                # Broadcast typing indicator to all participants
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "participant.typing",
                        "participant": self.user.username,
                        "source": data.get('source', 'web'),
                        "timestamp": timezone.now().isoformat(),
                    }
                )
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"[PA-WS] Invalid message: {e}")

    # --- Event handlers (called by channel_layer.group_send) ---

    async def message_created(self, event):
        """Push a new message to the WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "message.created",
            "message": event.get("message", {}),
        }))

    async def participant_typing(self, event):
        """Push typing indicator to the WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "participant.typing",
            "participant": event.get("participant", ""),
            "source": event.get("source", ""),
            "timestamp": event.get("timestamp", ""),
        }))

    async def participant_joined(self, event):
        """Notify client that a participant joined."""
        await self.send(text_data=json.dumps({
            "type": "participant.joined",
            "participant": event.get("participant", ""),
            "source": event.get("source", ""),
            "timestamp": event.get("timestamp", ""),
        }))

    # Session 1172: live tool-lifecycle ticker for the chat UI. Emits are
    # sourced from core.services.pa_status_events (called from
    # tool_dispatcher.execute when a PA pipeline threads its pa_trace_id).
    # Group events use dotted names; channels maps dots to underscores
    # for handler method dispatch, so "rigby.tool.started" → this method.

    async def rigby_tool_started(self, event):
        """Push a `rigby.tool.started` ticker event to the WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "rigby.tool.started",
            "trace_id": event.get("trace_id", ""),
            "seq": event.get("seq", 0),
            "tool_call_id": event.get("tool_call_id", ""),
            "tool_name": event.get("tool_name", ""),
            "started_at": event.get("started_at", ""),
            "arg_summary": event.get("arg_summary", ""),
        }))

    async def rigby_tool_completed(self, event):
        """Push a `rigby.tool.completed` ticker event to the WebSocket client."""
        await self.send(text_data=json.dumps({
            "type": "rigby.tool.completed",
            "trace_id": event.get("trace_id", ""),
            "seq": event.get("seq", 0),
            "tool_call_id": event.get("tool_call_id", ""),
            "tool_name": event.get("tool_name", ""),
            "latency_ms": event.get("latency_ms", 0),
            "status": event.get("status", "ok"),
            "result_summary": event.get("result_summary", ""),
        }))

    # Session 1174 PR-2a: agent-completion event handler. Fired from
    # core.tasks_agents.fire_agent_followup_subscriptions when a terminal-state
    # AgentExecution has an armed AgentFollowupSubscription for this conversation.
    # Channels maps dots to underscores so "agent.completed" → this method.
    #
    # Session 1175 PR-2b-2 extends this to ALSO persist a Rigby-authored ChatConversation
    # row so the completion message survives page refresh (the load-bearing D3 chat
    # bubble per the ratified design). The WS broadcast (existing PR-2a behavior) is kept
    # for the live banner in PR-2b-3. Q-C investigation (Session 1175) confirmed
    # ChatConversation has no post_save signals + no tokens/cost/embedding fields wired,
    # so the direct .create() is safe — no side-effect avalanche.
    #
    # Invariants honored (Rigby ratification, Session 1175):
    # 1. Non-PA dispatch keeps conversation_id NULL — fire_agent_followup_subscriptions
    #    already bails on NULL conv_id, so by the time we land here the dispatch was PA-
    #    originated and the WS room (pa_conversation_<conversation_id>) already matches.
    # 2. The fire helper does the atomic armed → fired transition; we just persist + send.
    # 3. Background-completion tagging: prepend "Background completion: " to the message
    #    if the user has posted to this conversation *after* the subscription was created
    #    (and the post itself is not another agent_completion row, to avoid self-trigger).

    async def agent_completed(self, event):
        """Persist a Rigby-authored ChatConversation row + push the live banner event."""
        execution_id = event.get("execution_id", "")
        agent_name = event.get("agent_name", "") or "agent"
        status = event.get("status", "") or "completed"
        completed_at = event.get("completed_at", "")
        error_signature = event.get("error_signature")
        artifact_pointers = event.get("artifact_pointers", {}) or {}

        # 1. Persist the Rigby-authored completion message server-side so it survives refresh.
        # Fail-open: if persistence breaks for any reason, still send the live banner event —
        # users would rather see the completion live and lose the history than miss it entirely.
        try:
            is_background = await database_sync_to_async(check_background_completion)(
                conversation_id=self.conversation_id,
                execution_id=execution_id,
            )
            assistant_response = compose_completion_body(
                execution_id=execution_id,
                agent_name=agent_name,
                status=status,
                error_signature=error_signature,
                artifact_pointers=artifact_pointers,
                is_background=is_background,
            )
            await database_sync_to_async(create_completion_row)(
                user=self.user,
                conversation_id=self.conversation_id,
                execution_id=execution_id,
                agent_name=agent_name,
                status=status,
                completed_at=completed_at,
                error_signature=error_signature,
                artifact_pointers=artifact_pointers,
                assistant_response=assistant_response,
            )
        except Exception as e:
            logger.warning(
                f"[PA-WS agent_completed] persist fail-open: execution={execution_id} err={e}",
                exc_info=True,
            )

        # 2. Live banner event for the connected client (existing PR-2a behavior unchanged).
        await self.send(text_data=json.dumps({
            "type": "agent.completed",
            "execution_id": execution_id,
            "agent_name": agent_name,
            "status": status,
            "completed_at": completed_at,
            "error_signature": error_signature,
            "artifact_pointers": artifact_pointers,
            "timestamp": event.get("timestamp", ""),
        }))
