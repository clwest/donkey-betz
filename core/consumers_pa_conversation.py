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
