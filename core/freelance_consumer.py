"""
WebSocket consumer for freelance opportunities real-time updates
"""
import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class FreelanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "freelance_updates",
            self.channel_name
        )
        await self.accept()

        # Send initial data
        await self.send_initial_opportunities()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "freelance_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'subscribe':
                await self.send_current_opportunities()
            elif message_type == 'refresh_opportunities':
                await self.send_current_opportunities()
            elif message_type == 'get_projects':
                await self.send_current_projects()

        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_opportunities(self):
        """Send initial opportunities when client connects"""
        opportunities = await self.get_opportunities_from_redis()
        await self.send(text_data=json.dumps({
            'type': 'initial_opportunities',
            'opportunities': opportunities,
            'count': len(opportunities)
        }))

    async def send_current_opportunities(self):
        """Send current opportunities from Redis"""
        opportunities = await self.get_opportunities_from_redis()
        await self.send(text_data=json.dumps({
            'type': 'opportunities_update',
            'opportunities': opportunities,
            'count': len(opportunities)
        }))

    async def send_current_projects(self):
        """Send current projects from Redis"""
        projects = await self.get_projects_from_redis()
        await self.send(text_data=json.dumps({
            'type': 'projects_update',
            'projects': projects,
            'count': len(projects)
        }))

    @database_sync_to_async
    def get_opportunities_from_redis(self):
        """Get opportunities from Redis"""
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        opp_keys = r.keys('freelance:opportunity:*')
        opportunities = []

        for key in opp_keys[:20]:  # Limit to 20 for performance
            data = r.get(key)
            if data:
                opportunities.append(json.loads(data))

        # Sort by suitability score
        opportunities.sort(key=lambda x: x.get('agent_suitability', 0), reverse=True)
        return opportunities

    @database_sync_to_async
    def get_projects_from_redis(self):
        """Get projects from Redis"""
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        project_keys = r.keys('freelance:project:*')
        projects = []

        for key in project_keys:
            data = r.get(key)
            if data:
                projects.append(json.loads(data))

        return projects

    # Handle group messages
    async def freelance_update(self, event):
        """Handle freelance update messages from channel layer"""
        await self.send(text_data=json.dumps(event['data']))