"""
Learning Feed WebSocket Consumer
================================

Session 324: Real-time streaming of agent learning activity.

Broadcasts knowledge transfers, learning events, and agent collaborations
as they happen - no more polling!
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class LearningFeedConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time agent learning activity feed.

    Features:
    - Stream learning events as they happen
    - Broadcast knowledge transfers between agents
    - Real-time stats updates
    """

    async def connect(self):
        """Accept connection and join learning feed broadcast group."""
        self.room_group_name = 'agent_learning_feed'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Learning Feed WebSocket connected: {self.channel_name}")

        # Send recent learning activity on connect
        await self.send_recent_activity()

        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'Connected to Agent Learning Feed',
            'timestamp': timezone.now().isoformat()
        }))

    async def disconnect(self, close_code):
        """Leave group on disconnect."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Learning Feed WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming messages from client."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'get_recent':
                # User wants recent activity
                await self.send_recent_activity()

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

    async def send_recent_activity(self):
        """Send recent learning activity to client."""
        try:
            activity = await self.get_recent_activity()
            await self.send(text_data=json.dumps({
                'type': 'learning_activity',
                'feed_items': activity['feed_items'],
                'stats': activity['stats'],
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Error sending recent activity: {e}")

    @database_sync_to_async
    def get_recent_activity(self):
        """Fetch recent learning activity from database."""
        from core.models import Agent, AgentLearningConnection, AgentKnowledgeSource, KnowledgeTransfer

        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)

        # Gather stats
        stats = {
            'total_agents': Agent.objects.filter(is_active=True).count(),
            'total_knowledge': AgentKnowledgeSource.objects.filter(is_active=True).count(),
            'total_connections': AgentLearningConnection.objects.filter(is_active=True).count(),
            'transfers_last_hour': KnowledgeTransfer.objects.filter(created_at__gte=last_hour).count(),
            'transfers_last_day': KnowledgeTransfer.objects.filter(created_at__gte=last_day).count(),
        }

        # Recent knowledge transfers as feed items
        feed_items = []
        for transfer in KnowledgeTransfer.objects.select_related(
            'connection__teacher_agent',
            'connection__student_agent'
        ).order_by('-created_at')[:20]:
            teacher = transfer.connection.teacher_agent
            student = transfer.connection.student_agent

            # Determine learning source type
            if teacher.id == student.id:
                source = 'self_learning'
                description = f"{teacher.name} acquired new knowledge"
            else:
                source = 'knowledge_transfer'
                description = f"{teacher.name} shared knowledge with {student.name}"

            feed_items.append({
                'timestamp': transfer.created_at.isoformat(),
                'type': source,
                'source': 'Knowledge transfer',
                'description': description,
                'knowledge': transfer.transfer_summary[:100] if transfer.transfer_summary else 'Knowledge shared',
                'teacher': teacher.name,
                'student': student.name,
                'was_useful': transfer.was_useful,
                # Session 761: Use usefulness_score as effectiveness_gain proxy
                'effectiveness_gain': transfer.usefulness_score if transfer.usefulness_score else 0.0
            })

        return {
            'feed_items': feed_items,
            'stats': stats
        }

    # Handler for group messages - called when Celery broadcasts a learning event
    async def learning_event(self, event):
        """Handle learning event broadcast from Celery task."""
        await self.send(text_data=json.dumps({
            'type': 'learning_event',
            'event': event.get('data', {}),
            'timestamp': timezone.now().isoformat()
        }))

    # Handler for full feed refresh
    async def learning_feed_update(self, event):
        """Handle full feed update broadcast."""
        await self.send(text_data=json.dumps({
            'type': 'learning_activity',
            'feed_items': event.get('feed_items', []),
            'stats': event.get('stats', {}),
            'timestamp': timezone.now().isoformat()
        }))
