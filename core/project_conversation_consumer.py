"""
Project Conversation WebSocket Consumer
========================================

Session 332: Real-time streaming of agent conversations about projects.

This brings the same real-time experience from Agent/Social tab to the
Project Intelligence Hub - agents chat in real-time via WebSocket with
typing indicators and live message streaming.

Features:
- Stream agent messages as they're generated
- Typing indicators between messages
- Project-scoped conversations only
- Live message append as messages come in
- Same UX as Agent/Social tab
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProjectConversationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time project-scoped agent conversations.

    Features:
    - Stream agent messages as they're generated
    - Project-specific conversation groups
    - Typing indicators between messages
    - Same experience as Agent/Social tab
    """

    async def connect(self):
        """Accept connection and join project conversation group."""
        self.project_id = self.scope['url_route']['kwargs'].get('project_id')

        if not self.project_id:
            await self.close()
            return

        # Create a unique group name for this project's conversations
        self.room_group_name = f'project_conversations_{self.project_id}'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Project Conversation WebSocket connected: {self.channel_name} for project {self.project_id}")

        # Send recent conversations on connect
        await self.send_recent_conversations()

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'project_id': self.project_id,
            'message': 'Connected to Project Conversations stream',
            'timestamp': timezone.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """Leave group on disconnect."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"Project Conversation WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming messages from client."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'start_conversation':
                # User requested a new conversation
                topic = data.get('topic', 'project discussion')
                await self.trigger_conversation(topic)

            elif message_type == 'get_recent':
                # User wants recent conversations
                await self.send_recent_conversations()

            elif message_type == 'ping':
                # Keep-alive
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))

        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_recent_conversations(self):
        """Send recent project conversations to the client."""
        conversations = await self.get_recent_conversations()
        await self.send(text_data=json.dumps({
            'type': 'recent_conversations',
            'project_id': self.project_id,
            'conversations': conversations,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_recent_conversations(self):
        """Fetch recent conversations for this project from database."""
        from core.models import AgentConversation

        conversations = AgentConversation.objects.filter(
            project_id=self.project_id
        ).select_related(
            'initiator'
        ).prefetch_related(
            'participants', 'messages__agent'
        ).order_by('-started_at')[:10]

        result = []
        for conv in conversations:
            messages = []
            for msg in conv.messages.all().order_by('sequence_number')[:20]:
                messages.append({
                    'agent': msg.agent.name if msg.agent else 'Unknown',
                    'agent_id': str(msg.agent.id) if msg.agent else None,
                    'content': msg.content,
                    'type': msg.message_type,
                    'sequence': msg.sequence_number,
                    'timestamp': msg.created_at.isoformat() if msg.created_at else None
                })

            result.append({
                'id': str(conv.id),
                'topic': conv.topic,
                'type': conv.conversation_type,
                'status': conv.status,
                'initiator': conv.initiator.name if conv.initiator else None,
                'participants': [p.name for p in conv.participants.all()],
                'message_count': conv.message_count or len(messages),
                'conclusion': conv.conclusion,
                'quality_score': conv.quality_score,
                'started_at': conv.started_at.isoformat() if conv.started_at else None,
                'messages': messages
            })

        return result

    async def trigger_conversation(self, topic):
        """Trigger a new project conversation via Celery task."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_starting',
            'project_id': self.project_id,
            'topic': topic,
            'message': 'Starting new agent conversation about this project...',
            'timestamp': timezone.now().isoformat()
        }))

        try:
            # Trigger the Celery task
            result = await self.start_conversation_task(topic)

            await self.send(text_data=json.dumps({
                'type': 'conversation_triggered',
                'project_id': self.project_id,
                'task_id': result,
                'topic': topic,
                'message': 'Conversation is being generated. Watch for live messages!',
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error triggering conversation: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to start conversation: {str(e)}'
            }))

    @database_sync_to_async
    def start_conversation_task(self, topic):
        """Start the Celery task for project conversation."""
        from core.tasks import run_project_conversation
        result = run_project_conversation.delay(self.project_id, topic)
        return str(result.id)

    # Group message handlers - these receive broadcasts from Celery tasks

    async def conversation_started(self, event):
        """Handle conversation started notification from Celery."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_started',
            'conversation_id': event.get('conversation_id'),
            'project_id': event.get('project_id'),
            'topic': event.get('topic'),
            'participants': event.get('participants'),
            'conversation_type': event.get('conversation_type'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def typing_indicator(self, event):
        """Handle typing indicator from Celery."""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'conversation_id': event.get('conversation_id'),
            'agent': event.get('agent'),
            'agent_id': event.get('agent_id'),
            'timestamp': timezone.now().isoformat()
        }))

    async def new_message(self, event):
        """Handle new message from Celery."""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'conversation_id': event.get('conversation_id'),
            'agent': event.get('agent'),
            'agent_id': event.get('agent_id'),
            'content': event.get('content'),
            'message_type': event.get('message_type'),
            'sequence': event.get('sequence'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))

    async def conversation_ended(self, event):
        """Handle conversation ended notification from Celery."""
        await self.send(text_data=json.dumps({
            'type': 'conversation_ended',
            'conversation_id': event.get('conversation_id'),
            'conclusion': event.get('conclusion'),
            'message_count': event.get('message_count'),
            'quality_score': event.get('quality_score'),
            'timestamp': event.get('timestamp', timezone.now().isoformat())
        }))


# =============================================================================
# Helper functions to broadcast messages from Celery tasks
# =============================================================================

def broadcast_project_conversation_started(project_id, conversation_id, topic, participants, conversation_type):
    """Broadcast that a project conversation has started."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_conversations_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'conversation_started',
            'conversation_id': str(conversation_id),
            'project_id': str(project_id),
            'topic': topic,
            'participants': participants,
            'conversation_type': conversation_type,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_typing_indicator(project_id, conversation_id, agent_name, agent_id=None):
    """Broadcast typing indicator for a project conversation."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_conversations_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'typing_indicator',
            'conversation_id': str(conversation_id),
            'agent': agent_name,
            'agent_id': str(agent_id) if agent_id else None,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_conversation_message(project_id, conversation_id, agent_name, agent_id, content, message_type, sequence):
    """Broadcast a new message in a project conversation."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_conversations_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'new_message',
            'conversation_id': str(conversation_id),
            'agent': agent_name,
            'agent_id': str(agent_id) if agent_id else None,
            'content': content,
            'message_type': message_type,
            'sequence': sequence,
            'timestamp': timezone.now().isoformat()
        }
    )


def broadcast_project_conversation_ended(project_id, conversation_id, conclusion, message_count, quality_score=None):
    """Broadcast that a project conversation has ended."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()
    group_name = f'project_conversations_{project_id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'conversation_ended',
            'conversation_id': str(conversation_id),
            'conclusion': conclusion,
            'message_count': message_count,
            'quality_score': quality_score,
            'timestamp': timezone.now().isoformat()
        }
    )
