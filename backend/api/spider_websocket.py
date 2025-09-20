"""
WebSocket consumer for real-time spider updates
"""
import json
import asyncio
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SpiderWebSocketConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time spider data"""

    async def connect(self):
        """Accept WebSocket connection"""
        self.room_name = 'spider_updates'
        self.room_group_name = f'spider_{self.room_name}'

        # Join room group
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

        # Start Redis subscription task
        self.redis_task = asyncio.create_task(self._redis_subscriber())

        # Send initial data
        await self.send_initial_data()

        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Cancel Redis subscription
        if hasattr(self, 'redis_task'):
            self.redis_task.cancel()

        # Close Redis connection
        if hasattr(self, 'redis_client'):
            await self.redis_client.close()

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))

            elif message_type == 'request_stats':
                await self.send_stats()

            elif message_type == 'request_opportunities':
                await self.send_opportunities()

            elif message_type == 'request_revenue':
                await self.send_revenue()

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")

    async def _redis_subscriber(self):
        """Subscribe to Redis channels for real-time updates"""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(
                'spider:data:stream',
                'agent:notify:*',
                'workflow:status:*'
            )

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    await self.process_redis_message(message)

        except asyncio.CancelledError:
            await pubsub.unsubscribe()
            raise
        except Exception as e:
            logger.error(f"Redis subscriber error: {e}")

    async def process_redis_message(self, message):
        """Process message from Redis subscription"""
        channel = message['channel']
        data = message['data']

        try:
            if channel == 'spider:data:stream':
                # New spider data available
                spider_data = json.loads(data)
                await self.send(text_data=json.dumps({
                    'type': 'spider_update',
                    'spider': spider_data['spider_name'],
                    'spider_type': spider_data['spider_type'],
                    'confidence': spider_data.get('confidence', 1.0),
                    'timestamp': spider_data['timestamp']
                }))

            elif channel.startswith('agent:notify:'):
                # Agent notification
                agent_data = json.loads(data)
                await self.send(text_data=json.dumps({
                    'type': 'agent_update',
                    'agent': channel.replace('agent:notify:', ''),
                    'notification': agent_data,
                    'timestamp': datetime.now().isoformat()
                }))

            elif channel.startswith('workflow:status:'):
                # Workflow status update
                workflow_data = json.loads(data)
                await self.send(text_data=json.dumps({
                    'type': 'workflow_update',
                    'workflow': workflow_data,
                    'timestamp': datetime.now().isoformat()
                }))

        except Exception as e:
            logger.error(f"Error processing Redis message: {e}")

    async def send_initial_data(self):
        """Send initial data when client connects"""
        # Get current stats
        stats = await self.get_current_stats()
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }))

    async def send_stats(self):
        """Send current spider statistics"""
        stats = await self.get_current_stats()
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }))

    async def send_opportunities(self):
        """Send current opportunities"""
        opportunities = await self.get_opportunities()
        await self.send(text_data=json.dumps({
            'type': 'opportunities_update',
            'opportunities': opportunities,
            'timestamp': datetime.now().isoformat()
        }))

    async def send_revenue(self):
        """Send revenue data"""
        revenue = await self.get_revenue()
        await self.send(text_data=json.dumps({
            'type': 'revenue_update',
            'revenue': revenue,
            'timestamp': datetime.now().isoformat()
        }))

    async def get_current_stats(self):
        """Get current statistics"""
        try:
            # Count active spiders
            spider_keys = await self.redis_client.keys('spider_latest:*')
            active_spiders = len(spider_keys)

            # Count agent queues with data
            agent_queues = await self.redis_client.keys('agent:queue:*')
            active_agents = 0
            for queue in agent_queues:
                size = await self.redis_client.llen(queue)
                if size > 0:
                    active_agents += 1

            return {
                'active_spiders': active_spiders,
                'active_agents': active_agents,
                'total_agents': 152,
                'data_collected': len(await self.redis_client.keys('spider_result:*'))
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'active_spiders': 0,
                'active_agents': 0,
                'total_agents': 152,
                'data_collected': 0
            }

    async def get_opportunities(self):
        """Get current opportunities"""
        opportunities = []

        try:
            # Check job opportunities
            job_keys = await self.redis_client.keys('spider_latest:*job*')
            for key in job_keys[:3]:
                data = await self.redis_client.get(key)
                if data:
                    result = json.loads(data)
                    if 'data' in result and 'jobs' in result['data']:
                        for job in result['data']['jobs'][:2]:
                            opportunities.append({
                                'type': 'job',
                                'title': job.get('title', 'Unknown'),
                                'value': job.get('salary', 'Competitive')
                            })

            # Check trading opportunities
            trading_keys = await self.redis_client.keys('spider_latest:*crypto*')
            for key in trading_keys[:2]:
                data = await self.redis_client.get(key)
                if data:
                    result = json.loads(data)
                    opportunities.append({
                        'type': 'trading',
                        'title': 'Crypto Opportunity',
                        'value': result.get('data', {}).get('potential_profit', 'High')
                    })

        except Exception as e:
            logger.error(f"Error getting opportunities: {e}")

        return opportunities

    async def get_revenue(self):
        """Get revenue data"""
        # For now, return mock data (will be real when payment integration is done)
        return {
            'total': 2847.50,
            'today': 347.50,
            'sources': {
                'content': 1200.00,
                'trading': 847.50,
                'jobs': 500.00,
                'betting': 300.00
            }
        }

    # Group message handlers
    async def spider_update(self, event):
        """Send spider update to WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def agent_update(self, event):
        """Send agent update to WebSocket"""
        await self.send(text_data=json.dumps(event))

    async def revenue_update(self, event):
        """Send revenue update to WebSocket"""
        await self.send(text_data=json.dumps(event))