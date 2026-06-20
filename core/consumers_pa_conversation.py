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
    # PR-2a scope is WebSocket-only — the frontend banner component (PR-2b) consumes
    # this event and renders the inline completion notice. Server-side ChatConversation
    # persistence (so the message survives a page refresh) is deferred to PR-2b along
    # with the schedule_followup PA tool; the open question on Q-C side effects
    # (token accounting / embeddings / last_message_at / unread counters) needs one
    # more pass before we start writing rows that bypass the FC loop.

    async def agent_completed(self, event):
        """Push an `agent.completed` event to the WebSocket client (PR-2a foundation)."""
        await self.send(text_data=json.dumps({
            "type": "agent.completed",
            "execution_id": event.get("execution_id", ""),
            "agent_name": event.get("agent_name", ""),
            "status": event.get("status", ""),
            "completed_at": event.get("completed_at", ""),
            "error_signature": event.get("error_signature"),
            "artifact_pointers": event.get("artifact_pointers", {}),
            "timestamp": event.get("timestamp", ""),
        }))
