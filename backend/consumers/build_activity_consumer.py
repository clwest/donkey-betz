"""
Build Activity WebSocket Consumer - Real-time Updates
Created: 9/26/25 11:54 AM MST
"""

import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from backend.agents.execution_tracker import execution_tracker
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class BuildActivityConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time build activity and metrics updates
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'build_activity'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial stats on connection
        stats = execution_tracker.get_comprehensive_stats()
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': {
                'active_agents': stats['active_agents'],
                'files_created': stats['files_created'],
                'success_rate': stats['success_rate'],
                'learning_rate': stats['learning_rate'],
                'projects_completed': stats['projects_completed']
            }
        }))

        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'project_start':
                await self.handle_project_start(data)
            elif message_type == 'agent_execute':
                await self.handle_agent_execution(data)
            elif message_type == 'request_stats':
                await self.send_current_stats()
            elif message_type == 'create_content':
                await self.handle_content_creation(data)

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def handle_project_start(self, data):
        """Handle project start event"""
        project_data = data.get('project', {})

        # Track in Redis
        execution_tracker.track_agent_execution(
            agent_name=project_data.get('agent', 'unknown'),
            execution_data={
                'task_description': project_data.get('name', 'New Project'),
                'is_real_execution': True,
                'success': False,  # Will update when complete
                'project_id': project_data.get('id')
            }
        )

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'project_update',
                'project': project_data
            }
        )

    async def handle_agent_execution(self, data):
        """Track when an agent executes"""
        agent_name = data.get('agent_name', 'unknown')
        task = data.get('task', {})

        # Track execution
        execution_tracker.track_agent_execution(
            agent_name=agent_name,
            execution_data={
                'task_description': task.get('description', 'Task execution'),
                'is_real_execution': not data.get('is_demo', False),
                'success': data.get('success', False),
                'quality_score': data.get('quality_score', 75),
                'complexity_score': data.get('complexity_score', 50),
                'code_generated': data.get('code_generated', False),
                'lines_of_code': data.get('lines_of_code', 0)
            }
        )

        # Send updated stats to all clients
        await self.send_stats_to_group()

    async def handle_content_creation(self, data):
        """Handle content creation requests"""
        content_type = data.get('content_type')
        title = data.get('title')

        # Track as agent execution
        execution_tracker.track_agent_execution(
            agent_name='content-creator',
            execution_data={
                'task_description': f"Create {content_type}: {title}",
                'is_real_execution': True,
                'success': False,  # Will update when complete
                'content_type': content_type
            }
        )

        # Notify all clients
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'activity',
                'activity': {
                    'icon': '✨',
                    'message': f'Creating {content_type}: {title}',
                    'time': 'just now'
                }
            }
        )

    async def send_current_stats(self):
        """Send current statistics to the client"""
        stats = execution_tracker.get_comprehensive_stats()
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': {
                'active_agents': stats['active_agents'],
                'files_created': stats['files_created'],
                'success_rate': stats['success_rate'],
                'learning_rate': stats['learning_rate'],
                'projects_completed': stats['projects_completed']
            }
        }))

    async def send_stats_to_group(self):
        """Send updated stats to all connected clients"""
        stats = execution_tracker.get_comprehensive_stats()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_stats_update',
                'data': {
                    'type': 'stats_update',
                    'stats': {
                        'active_agents': stats['active_agents'],
                        'files_created': stats['files_created'],
                        'success_rate': stats['success_rate'],
                        'learning_rate': stats['learning_rate'],
                        'projects_completed': stats['projects_completed']
                    }
                }
            }
        )

    # Channel layer message handlers
    async def project_update(self, event):
        """Send project update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'project_update',
            'project': event['project']
        }))

    async def build_output(self, event):
        """Send build output to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'build_output',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))

    async def file_created(self, event):
        """Send file creation notification"""
        # Track file creation
        execution_tracker.track_file_creation({
            'path': event.get('path', 'unknown'),
            'agent_name': event.get('agent_name'),
            'size': event.get('size', 0)
        })

        await self.send(text_data=json.dumps({
            'type': 'file_created',
            'file': event['file']
        }))

    async def activity(self, event):
        """Send activity update"""
        await self.send(text_data=json.dumps({
            'type': 'activity',
            'activity': event['activity']
        }))

    async def send_stats_update(self, event):
        """Send stats update from channel layer"""
        await self.send(text_data=json.dumps(event['data']))