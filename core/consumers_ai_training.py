"""
WebSocket consumer for AI Job Market Intelligence training updates
"""
import json
import asyncio
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AITrainingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time AI training updates"""

    async def connect(self):
        """Accept WebSocket connection and set up Redis subscription"""
        # Join the channel layer group for agent execution updates
        self.room_group_name = 'ai_training'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Initialize Redis connection
        self.redis_client = await redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

        # Create pubsub and subscribe to training updates
        self.pubsub = self.redis_client.pubsub()
        await self.pubsub.subscribe('ai_training_updates')

        # Send initial connection message
        await self.send(json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to AI Training Updates stream'
        }))

        # Send recent history
        await self.send_history()

        # Start listening to Redis channel
        self.redis_task = asyncio.create_task(self.redis_listener())

        logger.info("AITrainingConsumer: WebSocket connected")

    async def disconnect(self, close_code):
        """Clean up on disconnect"""
        # Leave the channel layer group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        if hasattr(self, 'redis_task'):
            self.redis_task.cancel()

        if hasattr(self, 'pubsub'):
            await self.pubsub.unsubscribe('ai_training_updates')
            await self.pubsub.close()

        if hasattr(self, 'redis_client'):
            await self.redis_client.close()

        logger.info(f"AITrainingConsumer: WebSocket disconnected with code {close_code}")

    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))

            elif message_type == 'get_history':
                await self.send_history()

            elif message_type == 'get_metrics':
                await self.send_current_metrics()

            elif message_type == 'get_content':
                await self.send_generated_content()

        except json.JSONDecodeError:
            await self.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def redis_listener(self):
        """Listen for Redis pubsub messages and forward to WebSocket"""
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    # Forward the message to WebSocket
                    await self.send(message['data'])
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Redis listener error: {e}")

    async def send_history(self):
        """Send recent training history"""
        try:
            # Get last 50 events from history
            history = await self.redis_client.lrange('ai_training:history', 0, 49)

            events = []
            for item in history:
                try:
                    events.append(json.loads(item))
                except Exception as _e:
                    logger.warning(
                        "consumers_ai_training.op: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            await self.send(json.dumps({
                'type': 'history',
                'events': events[::-1]  # Reverse to get chronological order
            }))
        except Exception as e:
            logger.error(f"Error sending history: {e}")

    async def send_current_metrics(self):
        """Send current system metrics"""
        try:
            # Fetch various metrics from Redis
            metrics = {}

            # Get spider status
            spider_keys = await self.redis_client.keys('spider:*')
            metrics['active_spiders'] = len([k for k in spider_keys if not k.endswith(':feed')])

            # Get team information
            team_keys = await self.redis_client.keys('team:*')
            metrics['teams_formed'] = len(team_keys)

            # Get content metrics
            content_keys = await self.redis_client.keys('content:*')
            metrics['content_pieces'] = len(content_keys)

            # Get blog posts count
            blog_posts = await self.redis_client.hlen('blog:posts')
            metrics['blog_posts'] = blog_posts

            # Get social posts count
            social_posts = await self.redis_client.llen('social:posts')
            metrics['social_posts'] = social_posts

            # Get baseline measurement if exists
            baseline = await self.redis_client.get('baseline:measurement')
            if baseline:
                metrics['baseline'] = json.loads(baseline)

            # Get ebook metadata if exists
            ebook = await self.redis_client.get('ebook:metadata')
            if ebook:
                metrics['ebook'] = json.loads(ebook)

            await self.send(json.dumps({
                'type': 'metrics',
                'data': metrics
            }))
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")

    async def send_generated_content(self):
        """Send list of generated content"""
        try:
            content = {}

            # Get blog posts
            blog_posts = await self.redis_client.hgetall('blog:posts')
            content['blog_posts'] = [json.loads(post) for post in blog_posts.values()]

            # Get social posts
            social_posts = await self.redis_client.lrange('social:posts', 0, -1)
            content['social_posts'] = [json.loads(post) for post in social_posts]

            # Get content pieces
            content_types = ['blog_post', 'career_guide', 'skill_matrix', 'industry_report']
            content['content_pieces'] = {}

            for content_type in content_types:
                key = f'content:{content_type}'
                pieces = await self.redis_client.hgetall(key)
                if pieces:
                    content['content_pieces'][content_type] = [
                        json.loads(piece) for piece in pieces.values()
                    ]

            await self.send(json.dumps({
                'type': 'content',
                'data': content
            }))
        except Exception as e:
            logger.error(f"Error sending content: {e}")

    async def broadcast_learning_update(self, event):
        """Broadcast agent learning updates"""
        await self.send(json.dumps({
            'type': 'learning_update',
            'data': event['data']
        }))

    async def broadcast_agent_collaboration(self, event):
        """Broadcast when agents collaborate"""
        await self.send(json.dumps({
            'type': 'agent_collaboration',
            'agents': event['agents'],
            'knowledge_shared': event['knowledge'],
            'timestamp': event.get('timestamp', str(datetime.now().isoformat()))
        }))

    async def broadcast_code_evolution(self, event):
        """Show code getting better over time"""
        await self.send(json.dumps({
            'type': 'code_evolution',
            'agent': event['agent'],
            'version': event['version'],
            'improvements': event['improvements'],
            'metrics': event['metrics']
        }))