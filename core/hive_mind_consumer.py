"""
Session 250: Hive Mind Mode WebSocket Consumer

Real-time updates for Hive Mind sessions as agents contribute.
"""
import json
import asyncio
import logging
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class HiveMindConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time Hive Mind session updates.

    Provides:
    - Live contribution status updates as each agent thinks
    - Session status transitions (gathering -> synthesizing -> completed)
    - Progress tracking
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.room_group_name = 'hive_mind'
        self.session_id = None
        self.redis_task = None

        # Join the hive mind room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Start Redis subscription for real-time updates
        self.redis_task = asyncio.create_task(self.subscribe_to_redis())

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'Connected to Hive Mind updates'
        }))

        logger.info("Hive Mind WebSocket connected")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Cancel Redis subscription
        if self.redis_task:
            self.redis_task.cancel()
            try:
                await self.redis_task
            except asyncio.CancelledError:
                pass

        # Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        logger.info("Hive Mind WebSocket disconnected")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'subscribe':
                # Subscribe to a specific session
                self.session_id = data.get('session_id')
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'session_id': self.session_id
                }))

                # Send current session status
                await self.send_session_status()

            elif message_type == 'get_status':
                # Get current session status
                await self.send_session_status()

            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.exception(f"Error in Hive Mind consumer: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def subscribe_to_redis(self):
        """Subscribe to Redis pub/sub for real-time updates."""
        try:
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
            pubsub = r.pubsub()
            await pubsub.subscribe('hive_mind')

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])

                        # Forward update to WebSocket
                        await self.send(text_data=json.dumps(data))

                        # Also send to channel group for other consumers
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'hive_mind_update',
                                'data': data
                            }
                        )
                    except json.JSONDecodeError:
                        pass

        except asyncio.CancelledError:
            await pubsub.unsubscribe('hive_mind')
            await r.close()
        except Exception as e:
            logger.error(f"Redis subscription error: {e}")

    async def hive_mind_update(self, event):
        """Handle hive mind updates from channel layer."""
        data = event.get('data', {})

        # Only send if subscribed to this session or subscribed to all
        if not self.session_id or data.get('session_id') == self.session_id:
            await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def get_session_data(self):
        """Get current session data from database."""
        from core.models import HiveMindSession

        if not self.session_id:
            return None

        try:
            session = HiveMindSession.objects.get(id=self.session_id)
            contributions = session.contributions.all().select_related('agent')

            total = contributions.count()
            completed = contributions.filter(status='completed').count()
            thinking = contributions.filter(status='thinking').count()

            return {
                'session_id': str(session.id),
                'status': session.status,
                'question': session.question,
                'progress': round((completed / total * 100) if total > 0 else 0, 1),
                'stats': {
                    'total': total,
                    'completed': completed,
                    'thinking': thinking,
                    'pending': total - completed - thinking
                },
                'contributions': [
                    {
                        'agent_name': c.agent.name,
                        'status': c.status,
                        'thinking_time': c.thinking_time,
                        'key_points': c.key_points[:3] if c.key_points else []
                    }
                    for c in contributions
                ],
                'synthesis': session.synthesis if session.status == 'completed' else None,
                'synthesis_summary': session.synthesis_summary if session.status == 'completed' else None
            }
        except HiveMindSession.DoesNotExist:
            return None

    async def send_session_status(self):
        """Send current session status to client."""
        if not self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'No session subscribed'
            }))
            return

        session_data = await self.get_session_data()

        if session_data:
            await self.send(text_data=json.dumps({
                'type': 'session_status',
                **session_data
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Session not found'
            }))
