"""
Simplified WebSocket Consumer for Real-Time Agent Monitor
Shows actual status of agents and active projects
"""
import json
import asyncio
import logging
import os
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import redis

logger = logging.getLogger(__name__)

class AgentMonitorConsumer(AsyncWebsocketConsumer):
    """Simple WebSocket consumer for monitoring real agent activity"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = None
        self.monitoring = False

    async def connect(self):
        """Accept WebSocket connection"""
        await self.accept()

        # Initialize Redis connection
        self.redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)

        # Send initial status
        await self.send_initial_data()

        # Start monitoring loop
        self.monitoring = True
        asyncio.create_task(self.monitor_loop())

    async def disconnect(self, close_code):
        """Clean up on disconnect"""
        self.monitoring = False

    async def receive(self, text_data):
        """Handle incoming messages from client"""
        try:
            data = json.loads(text_data)

            if data.get('type') == 'request_agent_status':
                await self.send_agent_status()
            elif data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def project_progress(self, event):
        """Handle project progress updates"""
        await self.send(text_data=json.dumps({
            'type': 'project_progress',
            'data': event['message']
        }))

    async def send_initial_data(self):
        """Send initial data to client"""
        await self.send_agent_status()
        await self.send_active_projects()

    async def send_agent_status(self):
        """Send current agent and project status"""
        agents = []

        # Check for active projects
        try:
            project_keys = self.redis_client.keys('freelance:project:*')

            for project_key in project_keys:
                project_data = self.redis_client.get(project_key)
                if project_data:
                    project = json.loads(project_data)

                    # Intelligently assign agent based on job requirements
                    skills = project.get('opportunity', {}).get('skills_required', [])
                    title = project.get('opportunity', {}).get('title', '').lower()

                    # Smart agent assignment based on skills and title
                    if any(skill in str(skills).lower() for skill in ['python', 'javascript', 'react', 'api', 'code', 'script', 'programming']):
                        agent_name = 'Code Generator'
                    elif any(skill in str(skills).lower() for skill in ['data analysis', 'analytics', 'pandas', 'numpy', 'excel']):
                        agent_name = 'Data Analyst'
                    elif any(skill in str(skills).lower() for skill in ['design', 'ui', 'ux', 'figma', 'photoshop']):
                        agent_name = 'UI Designer'
                    elif any(skill in str(skills).lower() for skill in ['market research', 'analysis', 'report']):
                        agent_name = 'Market Analyst'
                    elif any(skill in str(skills).lower() for skill in ['video', 'editing', 'premiere', 'after effects']):
                        agent_name = 'Video Editor'
                    elif any(skill in str(skills).lower() for skill in ['seo', 'content writing', 'blog', 'article']):
                        agent_name = 'Content Creator'
                    else:
                        agent_name = 'General Assistant'  # Better default than Content Creator

                    # Override with actual assignment if it exists
                    if project.get('analysis', {}).get('agent_team', {}).get('lead_agent'):
                        agent_name = project['analysis']['agent_team']['lead_agent']

                    # Get current progress from Redis
                    current_progress = project.get('progress', 0)

                    agents.append({
                        'name': agent_name,
                        'status': 'working',
                        'currentTask': project.get('opportunity', {}).get('title', 'Unknown Project'),
                        'completedTasks': 0,
                        'revenue': project.get('opportunity', {}).get('budget', 0),
                        'successRate': 95,
                        'specialization': 'Freelance',
                        'lastActive': project.get('created_at', datetime.now().isoformat()),
                        'platform': project.get('opportunity', {}).get('platform', 'Unknown'),
                        'projectId': project.get('id'),
                        'progress': current_progress,  # Use actual progress value
                        'projectStatus': project.get('status', 'active')
                    })
        except Exception as e:
            logger.error(f"Error loading projects: {e}")

        # Check for any agent tasks
        try:
            task_keys = self.redis_client.keys('agent:task:*')

            for task_key in task_keys:
                agent_name = task_key.split(':')[2]  # Extract agent name
                task_title = self.redis_client.get(task_key)

                # Don't duplicate if already in projects
                if not any(a['name'] == agent_name for a in agents):
                    agents.append({
                        'name': agent_name,
                        'status': 'working',
                        'currentTask': task_title,
                        'completedTasks': 0,
                        'revenue': 0,
                        'successRate': 95,
                        'specialization': 'Analysis',
                        'lastActive': datetime.now().isoformat()
                    })
        except Exception as e:
            logger.error(f"Error loading agent tasks: {e}")

        # Don't show idle agents if no active ones - wait for real data
        # if not agents:
        #     agents = [
        #         {'name': 'Content Creator', 'status': 'idle', 'completedTasks': 12, 'revenue': 4500, 'successRate': 98, 'specialization': 'Content'},
        #         {'name': 'Data Analyst', 'status': 'idle', 'completedTasks': 8, 'revenue': 3200, 'successRate': 95, 'specialization': 'Analysis'},
        #         {'name': 'Code Generator', 'status': 'idle', 'completedTasks': 15, 'revenue': 6000, 'successRate': 97, 'specialization': 'Development'}
        #     ]

        # Send to client
        await self.send(text_data=json.dumps({
            'type': 'agent_status',
            'agents': agents,
            'totalAgents': len(agents),
            'activeAgents': sum(1 for a in agents if a['status'] == 'working'),
            'timestamp': datetime.now().isoformat()
        }))

    async def send_active_projects(self):
        """Send active project information"""
        tasks = []

        try:
            # Get active tasks from queue
            queue_data = self.redis_client.lrange('agent:updates:queue', 0, 10)

            for item in queue_data:
                try:
                    update = json.loads(item)
                    if update.get('type') == 'task_update':
                        tasks.append(update.get('task'))
                except Exception as _e:
                    logger.warning(
                        "agent_monitor_consumer_simple.__init__: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            # Get active projects
            project_keys = self.redis_client.keys('freelance:project:*')

            for project_key in project_keys[:5]:  # Limit to 5 for display
                project_data = self.redis_client.get(project_key)
                if project_data:
                    project = json.loads(project_data)

                    # Get the opportunity details
                    opportunity = project.get('opportunity', {})

                    tasks.append({
                        'id': project.get('id'),
                        'agentName': project.get('analysis', {}).get('agent_team', {}).get('lead_agent', 'Content Creator'),
                        'taskType': 'Freelance Project',
                        'progress': 25,  # Simulate some progress
                        'estimatedTime': '2 hours',
                        'value': opportunity.get('budget', 0),
                        'status': 'executing',
                        'title': opportunity.get('title', 'Unknown Project'),
                        'description': opportunity.get('description', 'No description available')[:200],  # First 200 chars
                        'platform': opportunity.get('platform', 'Unknown'),
                        'skills': opportunity.get('skills_required', []),
                        'url': opportunity.get('url', '#')
                    })
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")

        if tasks:
            await self.send(text_data=json.dumps({
                'type': 'active_tasks',
                'tasks': tasks,
                'timestamp': datetime.now().isoformat()
            }))

    async def monitor_loop(self):
        """Monitor for changes and send updates"""
        while self.monitoring:
            try:
                # Check for updates every 5 seconds
                await asyncio.sleep(5)

                # Send updated status
                await self.send_agent_status()

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")

            await asyncio.sleep(1)