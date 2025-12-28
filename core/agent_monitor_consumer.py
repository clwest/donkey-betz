"""
WebSocket Consumer for Real-Time Agent Monitor
Shows actual status of all 152 agents
"""
import json
import asyncio
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import redis

logger = logging.getLogger(__name__)

class AgentMonitorConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for monitoring real agent activity"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(
            'agent_monitor',
            self.channel_name
        )

        # Send initial agent status
        await self.send_agent_status()

        # Start monitoring loop
        self.monitoring = True
        asyncio.create_task(self.monitor_agents())

    async def disconnect(self, close_code):
        self.monitoring = False
        await self.channel_layer.group_discard(
            'agent_monitor',
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'request_agent_status':
            await self.send_agent_status()
        elif data.get('type') == 'request_active_tasks':
            await self.send_active_tasks()

    async def send_agent_status(self):
        """Send current status of all agents"""

        agents = []

        # Try to get agent registry
        try:
            from ai_core.agents.agent_registry import agent_registry
            # Add all registered agents
            for agent_name, agent_config in agent_registry.agents.items():
                # Check if agent has active tasks in Redis
                task_key = f"agent:task:{agent_name}"
                current_task = self.redis_client.get(task_key)

                # Get agent stats from Redis
                stats_key = f"agent:stats:{agent_name}"
                stats = self.redis_client.hgetall(stats_key)

                agent_data = {
                    'name': agent_name,
                    'status': 'working' if current_task else 'idle',
                    'currentTask': current_task,
                    'completedTasks': int(stats.get('completed_tasks', 0)),
                    'revenue': float(stats.get('revenue', 0)),
                    'successRate': float(stats.get('success_rate', 95)),
                    'specialization': agent_config.get('specialization', 'General'),
                    'lastActive': stats.get('last_active', '')
                }
                agents.append(agent_data)
        except Exception as e:
            logger.error(f"Error loading agent registry: {e}")
            # Fallback - check for any active freelance jobs
            active_jobs = self.redis_client.keys('freelance:job:executing:*')
            for job_key in active_jobs:
                job_data = self.redis_client.hgetall(job_key)
                if job_data and job_data.get('assigned_agent'):
                    agent_data = {
                        'name': job_data.get('assigned_agent', 'Unknown Agent'),
                        'status': 'working',
                        'currentTask': job_data.get('title', 'Processing job'),
                        'completedTasks': 0,
                        'revenue': float(job_data.get('value', 0)),
                        'successRate': 95,
                        'specialization': 'Freelance',
                        'lastActive': datetime.now().isoformat()
                    }
                    agents.append(agent_data)

        # Send to client
        await self.send(text_data=json.dumps({
            'type': 'agent_status',
            'agents': agents,
            'totalAgents': len(agents),
            'activeAgents': sum(1 for a in agents if a['status'] == 'working'),
            'timestamp': datetime.now().isoformat()
        }))

    async def send_active_tasks(self):
        """Send currently active tasks across all agents"""

        tasks = []

        # Get all active tasks from Redis
        task_keys = self.redis_client.keys('task:active:*')

        for key in task_keys:
            task_data = self.redis_client.hgetall(key)
            if task_data:
                tasks.append({
                    'id': task_data.get('id'),
                    'agentName': task_data.get('agent'),
                    'taskType': task_data.get('type'),
                    'progress': float(task_data.get('progress', 0)),
                    'estimatedTime': task_data.get('estimated_time', '30s'),
                    'value': float(task_data.get('value', 0)),
                    'status': task_data.get('status', 'executing'),
                    'output': task_data.get('output', '')
                })

        await self.send(text_data=json.dumps({
            'type': 'active_tasks',
            'tasks': tasks,
            'timestamp': datetime.now().isoformat()
        }))

    async def monitor_agents(self):
        """Continuously monitor agent activity"""

        while self.monitoring:
            try:
                # Check for updates in Redis
                updates_key = 'agent:updates:queue'

                # Get any pending updates
                update = self.redis_client.lpop(updates_key)

                if update:
                    update_data = json.loads(update)

                    # Send update to client
                    await self.send(text_data=json.dumps({
                        'type': update_data.get('type', 'agent_update'),
                        **update_data,
                        'timestamp': datetime.now().isoformat()
                    }))

                # Check freelance pipeline for active jobs
                active_jobs = self.redis_client.keys('freelance:job:executing:*')

                for job_key in active_jobs:
                    job_data = self.redis_client.hgetall(job_key)
                    if job_data:
                        # Send task update
                        await self.send(text_data=json.dumps({
                            'type': 'task_update',
                            'task': {
                                'id': job_data.get('id'),
                                'agentName': job_data.get('assigned_agent'),
                                'taskType': 'Freelance Project',
                                'progress': float(job_data.get('progress', 0)),
                                'value': float(job_data.get('value', 0)),
                                'status': job_data.get('status', 'executing')
                            }
                        }))

                # Send periodic status update
                if asyncio.get_event_loop().time() % 10 < 1:  # Every 10 seconds
                    await self.send_agent_status()

            except Exception as e:
                logger.error(f"Monitor error: {e}")

            await asyncio.sleep(1)  # Check every second

    async def agent_task_update(self, event):
        """Handle agent task updates from other parts of the system"""
        await self.send(text_data=json.dumps(event['data']))