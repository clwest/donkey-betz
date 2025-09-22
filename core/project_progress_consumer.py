"""
Project Progress WebSocket Consumer
===================================

Real-time WebSocket consumer for streaming project execution progress
from agents to the frontend. Provides live updates on task phases,
completion percentages, and deliverable generation.
"""

import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class ProjectProgressConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time project progress updates"""

    async def connect(self):
        """Accept WebSocket connection and setup project monitoring"""
        self.project_id = self.scope['url_route']['kwargs'].get('project_id', 'general')
        self.room_group_name = f'project_{self.project_id}'

        # Join project-specific room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Initialize Redis connection for project data
        self.redis_client = await aioredis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

        # Send initial project status if available
        await self.send_initial_project_status()

        logger.info(f"WebSocket connected for project {self.project_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Close Redis connection
        if hasattr(self, 'redis_client'):
            await self.redis_client.close()

        logger.info(f"WebSocket disconnected for project {self.project_id}")

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

            elif message_type == 'request_status':
                await self.send_project_status()

            elif message_type == 'request_updates':
                limit = data.get('limit', 20)
                await self.send_project_updates(limit)

            elif message_type == 'request_deliverables':
                await self.send_project_deliverables()

            elif message_type == 'pause_project':
                await self.handle_pause_project()

            elif message_type == 'resume_project':
                await self.handle_resume_project()

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def send_initial_project_status(self):
        """Send initial project status when client connects"""
        try:
            execution_key = f"project_execution:{self.project_id}"
            execution_data = await self.redis_client.get(execution_key)

            if execution_data:
                project_data = json.loads(execution_data)
                await self.send(text_data=json.dumps({
                    'type': 'initial_status',
                    'project_id': self.project_id,
                    'status': project_data.get('status', 'unknown'),
                    'progress_percentage': project_data.get('progress_percentage', 0),
                    'current_phase': project_data.get('current_phase', 'unknown'),
                    'assigned_agent': project_data.get('assigned_agent'),
                    'estimated_completion': project_data.get('estimated_completion'),
                    'deliverables_count': len(project_data.get('deliverables', [])),
                    'timestamp': datetime.now().isoformat()
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'initial_status',
                    'project_id': self.project_id,
                    'status': 'not_found',
                    'message': 'Project not found or not started',
                    'timestamp': datetime.now().isoformat()
                }))

        except Exception as e:
            logger.error(f"Error sending initial project status: {e}")

    async def send_project_status(self):
        """Send current project status"""
        try:
            execution_key = f"project_execution:{self.project_id}"
            execution_data = await self.redis_client.get(execution_key)

            if execution_data:
                project_data = json.loads(execution_data)
                await self.send(text_data=json.dumps({
                    'type': 'status_update',
                    'project_id': self.project_id,
                    'status': project_data.get('status'),
                    'progress_percentage': project_data.get('progress_percentage'),
                    'current_phase': project_data.get('current_phase'),
                    'assigned_agent': project_data.get('assigned_agent'),
                    'backup_agents': project_data.get('backup_agents', []),
                    'estimated_completion': project_data.get('estimated_completion'),
                    'deliverables_count': len(project_data.get('deliverables', [])),
                    'error_count': len(project_data.get('error_log', [])),
                    'last_updated': project_data.get('last_updated'),
                    'timestamp': datetime.now().isoformat()
                }))

        except Exception as e:
            logger.error(f"Error sending project status: {e}")

    async def send_project_updates(self, limit: int = 20):
        """Send recent project updates"""
        try:
            updates_key = f"project_updates:{self.project_id}"
            updates_raw = await self.redis_client.lrange(updates_key, 0, limit - 1)

            updates = []
            for update_raw in updates_raw:
                updates.append(json.loads(update_raw))

            await self.send(text_data=json.dumps({
                'type': 'updates_history',
                'project_id': self.project_id,
                'updates': updates,
                'count': len(updates),
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending project updates: {e}")

    async def send_project_deliverables(self):
        """Send project deliverables information"""
        try:
            # Get deliverables from project execution data
            execution_key = f"project_execution:{self.project_id}"
            execution_data = await self.redis_client.get(execution_key)

            deliverables = []
            if execution_data:
                project_data = json.loads(execution_data)
                deliverables = project_data.get('deliverables', [])

            await self.send(text_data=json.dumps({
                'type': 'deliverables_update',
                'project_id': self.project_id,
                'deliverables': deliverables,
                'count': len(deliverables),
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending project deliverables: {e}")

    async def handle_pause_project(self):
        """Handle project pause request"""
        try:
            # Import here to avoid circular imports
            from backend.agents.realtime_project_executor import get_project_executor

            executor = get_project_executor()
            success = await executor.pause_project(self.project_id)

            await self.send(text_data=json.dumps({
                'type': 'pause_response',
                'project_id': self.project_id,
                'success': success,
                'message': 'Project paused' if success else 'Failed to pause project',
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error pausing project: {e}")
            await self.send(text_data=json.dumps({
                'type': 'pause_response',
                'project_id': self.project_id,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }))

    async def handle_resume_project(self):
        """Handle project resume request"""
        try:
            # Import here to avoid circular imports
            from backend.agents.realtime_project_executor import get_project_executor

            executor = get_project_executor()
            success = await executor.resume_project(self.project_id)

            await self.send(text_data=json.dumps({
                'type': 'resume_response',
                'project_id': self.project_id,
                'success': success,
                'message': 'Project resumed' if success else 'Failed to resume project',
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error resuming project: {e}")
            await self.send(text_data=json.dumps({
                'type': 'resume_response',
                'project_id': self.project_id,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }))

    # Group message handlers (called by channel layer)
    async def project_progress(self, event):
        """Send project progress update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'progress_update',
            **event['data']
        }))

    async def project_status_changed(self, event):
        """Send project status change to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'status_changed',
            **event['data']
        }))

    async def project_deliverable_ready(self, event):
        """Send deliverable ready notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'deliverable_ready',
            **event['data']
        }))

    async def project_error(self, event):
        """Send project error notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'project_error',
            **event['data']
        }))


class AllProjectsConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for monitoring all projects"""

    async def connect(self):
        """Accept WebSocket connection for all projects monitoring"""
        self.room_group_name = 'all_projects'

        # Join all projects room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Initialize Redis connection
        self.redis_client = await aioredis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

        # Send initial projects overview
        await self.send_projects_overview()

        logger.info("WebSocket connected for all projects monitoring")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Close Redis connection
        if hasattr(self, 'redis_client'):
            await self.redis_client.close()

        logger.info("WebSocket disconnected from all projects monitoring")

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

            elif message_type == 'request_overview':
                await self.send_projects_overview()

            elif message_type == 'request_active_projects':
                await self.send_active_projects()

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def send_projects_overview(self):
        """Send overview of all projects"""
        try:
            # Get all project execution keys
            project_keys = await self.redis_client.keys('project_execution:*')

            projects_summary = {
                'total_projects': len(project_keys),
                'active_projects': 0,
                'completed_projects': 0,
                'failed_projects': 0,
                'recent_projects': []
            }

            for key in project_keys[:10]:  # Limit to last 10 for performance
                try:
                    project_data = await self.redis_client.get(key)
                    if project_data:
                        project = json.loads(project_data)
                        status = project.get('status', 'unknown')

                        if status in ['in_progress', 'starting', 'agent_assigned']:
                            projects_summary['active_projects'] += 1
                        elif status == 'completed':
                            projects_summary['completed_projects'] += 1
                        elif status == 'failed':
                            projects_summary['failed_projects'] += 1

                        projects_summary['recent_projects'].append({
                            'project_id': project.get('project_id'),
                            'job_id': project.get('job_id'),
                            'status': status,
                            'progress_percentage': project.get('progress_percentage', 0),
                            'assigned_agent': project.get('assigned_agent'),
                            'last_updated': project.get('last_updated')
                        })
                except Exception as e:
                    logger.error(f"Error processing project key {key}: {e}")

            await self.send(text_data=json.dumps({
                'type': 'projects_overview',
                'summary': projects_summary,
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending projects overview: {e}")

    async def send_active_projects(self):
        """Send details of all active projects"""
        try:
            project_keys = await self.redis_client.keys('project_execution:*')
            active_projects = []

            for key in project_keys:
                try:
                    project_data = await self.redis_client.get(key)
                    if project_data:
                        project = json.loads(project_data)
                        status = project.get('status', 'unknown')

                        if status in ['in_progress', 'starting', 'agent_assigned', 'generating_deliverable']:
                            active_projects.append({
                                'project_id': project.get('project_id'),
                                'job_id': project.get('job_id'),
                                'status': status,
                                'progress_percentage': project.get('progress_percentage', 0),
                                'current_phase': project.get('current_phase'),
                                'assigned_agent': project.get('assigned_agent'),
                                'estimated_completion': project.get('estimated_completion'),
                                'last_updated': project.get('last_updated')
                            })
                except Exception as e:
                    logger.error(f"Error processing project key {key}: {e}")

            await self.send(text_data=json.dumps({
                'type': 'active_projects',
                'projects': active_projects,
                'count': len(active_projects),
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error sending active projects: {e}")

    # Group message handlers for all projects updates
    async def global_project_update(self, event):
        """Send global project update to all monitoring clients"""
        await self.send(text_data=json.dumps({
            'type': 'global_update',
            **event['data']
        }))

    async def new_project_started(self, event):
        """Send new project started notification"""
        await self.send(text_data=json.dumps({
            'type': 'new_project',
            **event['data']
        }))

    async def project_completed(self, event):
        """Send project completion notification"""
        await self.send(text_data=json.dumps({
            'type': 'project_completed',
            **event['data']
        }))