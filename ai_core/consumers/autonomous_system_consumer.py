"""
WebSocket consumer for the Autonomous Revenue System
Streams real-time updates from the 30-day autonomous run
"""

import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ai_core.agents.autonomous_revenue_system import AutonomousRevenueSystem
import logging

logger = logging.getLogger(__name__)

class AutonomousSystemConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for autonomous system real-time updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autonomous_system = None
        self.update_task = None

    async def connect(self):
        """Accept WebSocket connection and start system"""
        await self.accept()
        logger.info("Autonomous System WebSocket connected")

        # Initialize the autonomous revenue system
        self.autonomous_system = AutonomousRevenueSystem()

        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to Autonomous Revenue System'
        }))

        # Start the update task
        self.update_task = asyncio.create_task(self.stream_system_updates())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        logger.info(f"Autonomous System WebSocket disconnected: {close_code}")

        # Cancel update task if running
        if self.update_task:
            self.update_task.cancel()

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)

            if data.get('action') == 'start_system':
                await self.start_autonomous_run(data.get('days', 30))
            elif data.get('action') == 'get_metrics':
                await self.send_current_metrics()
            elif data.get('action') == 'pause_system':
                await self.pause_system()
            elif data.get('action') == 'resume_system':
                await self.resume_system()

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def start_autonomous_run(self, days: int = 30):
        """Start the 30-day autonomous system run"""
        try:
            # Start in a background task to not block the WebSocket
            asyncio.create_task(self.run_autonomous_system(days))

            await self.send(text_data=json.dumps({
                'type': 'system_started',
                'message': f'Starting {days}-day autonomous run',
                'timestamp': datetime.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error starting autonomous system: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def run_autonomous_system(self, days: int):
        """Run the autonomous system and stream updates"""
        try:
            # This would integrate with the actual autonomous_revenue_system.py
            for day in range(1, days + 1):
                # Send daily update
                await self.send(text_data=json.dumps({
                    'type': 'day_started',
                    'data': {
                        'day': day,
                        'timestamp': datetime.now().isoformat()
                    }
                }))

                # Simulate daily operations (replace with actual system calls)
                await self.simulate_daily_operations(day)

                # Wait before next day (shortened for demo, would be longer in production)
                await asyncio.sleep(10)  # 10 seconds per "day" for demo

        except Exception as e:
            logger.error(f"Error in autonomous system run: {e}")

    async def simulate_daily_operations(self, day: int):
        """Simulate daily agent operations and send updates"""

        # Simulate finding jobs
        jobs_found = [
            {
                'id': f'job_{day}_{i}',
                'title': f'Build {["Django API", "React Dashboard", "Data Pipeline", "Mobile App"][i % 4]}',
                'client': f'Client_{day}_{i}',
                'budget': 500 + (i * 100),
                'platform': ['Upwork', 'Freelancer', 'Fiverr'][i % 3]
            }
            for i in range(3)
        ]

        for job in jobs_found:
            await self.send(text_data=json.dumps({
                'type': 'job_found',
                'data': job
            }))
            await asyncio.sleep(0.5)

        # Simulate agent assignments
        agents_working = [
            {'name': 'CodeMaster-7', 'job': jobs_found[0]['title'], 'status': 'working'},
            {'name': 'ReactNinja-X', 'job': jobs_found[1]['title'], 'status': 'working'},
            {'name': 'DataWizard-3', 'job': jobs_found[2]['title'], 'status': 'working'},
        ]

        for agent in agents_working:
            await self.send(text_data=json.dumps({
                'type': 'agent_activity',
                'data': {
                    'agentName': agent['name'],
                    'action': f"Started working on {agent['job']}",
                    'status': agent['status'],
                    'timestamp': datetime.now().isoformat()
                }
            }))
            await asyncio.sleep(1)

        # Simulate deliverable creation
        deliverables = [
            {
                'id': f'del_{day}_1',
                'agentName': 'CodeMaster-7',
                'jobTitle': jobs_found[0]['title'],
                'type': 'Django API',
                'files': ['models.py', 'views.py', 'serializers.py', 'tests.py'],
                'status': 'completed',
                'createdAt': datetime.now().isoformat(),
                'revenue': jobs_found[0]['budget']
            },
            {
                'id': f'del_{day}_2',
                'agentName': 'ReactNinja-X',
                'jobTitle': jobs_found[1]['title'],
                'type': 'React App',
                'files': ['App.tsx', 'Dashboard.tsx', 'components/', 'hooks/'],
                'status': 'completed',
                'createdAt': datetime.now().isoformat(),
                'revenue': jobs_found[1]['budget']
            }
        ]

        for deliverable in deliverables:
            await self.send(text_data=json.dumps({
                'type': 'deliverable_created',
                'data': deliverable
            }))
            await asyncio.sleep(1)

        # Simulate social media posts
        social_posts = [
            {
                'id': f'post_{day}_1',
                'platform': 'twitter',
                'content': f"🚀 Day {day}: Our AI agents just completed {len(deliverables)} projects! Building the future of automated development. #AI #Automation #TechInnovation",
                'engagement': {
                    'likes': 150 + (day * 10),
                    'shares': 25 + day,
                    'comments': 10 + day,
                    'views': 1000 + (day * 100)
                },
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': f'post_{day}_2',
                'platform': 'linkedin',
                'content': f"Milestone Update - Day {day}:\n\n✅ {len(jobs_found)} new projects secured\n✅ {len(agents_working)} AI agents deployed\n✅ 100% on-time delivery\n\nOur autonomous AI workforce is revolutionizing software development.",
                'engagement': {
                    'likes': 200 + (day * 15),
                    'shares': 30 + day,
                    'comments': 15 + day,
                    'views': 2000 + (day * 150)
                },
                'timestamp': datetime.now().isoformat()
            }
        ]

        for post in social_posts:
            await self.send(text_data=json.dumps({
                'type': 'social_post',
                'data': post
            }))
            await asyncio.sleep(0.5)

        # Send metrics update
        total_revenue = sum(d['revenue'] for d in deliverables) * day
        await self.send(text_data=json.dumps({
            'type': 'metrics_update',
            'data': {
                'day': day,
                'totalRevenue': total_revenue,
                'activeAgents': len(agents_working),
                'completedJobs': len(deliverables) * day,
                'pendingJobs': len(jobs_found),
                'clientSatisfaction': 4.5 + (day * 0.01),
                'socialReach': sum(p['engagement']['views'] for p in social_posts)
            }
        }))

    async def stream_system_updates(self):
        """Continuously stream system updates"""
        while True:
            try:
                # This would connect to the actual autonomous system
                # For now, we'll send periodic status updates
                await asyncio.sleep(5)

                # Send heartbeat
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat',
                    'timestamp': datetime.now().isoformat()
                }))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update stream: {e}")
                await asyncio.sleep(5)

    async def send_current_metrics(self):
        """Send current system metrics"""
        # This would fetch real metrics from the database
        metrics = {
            'type': 'metrics',
            'data': {
                'totalRevenue': 12500,
                'activeAgents': 47,
                'completedJobs': 89,
                'pendingJobs': 12,
                'clientSatisfaction': 4.7,
                'timestamp': datetime.now().isoformat()
            }
        }
        await self.send(text_data=json.dumps(metrics))

    async def pause_system(self):
        """Pause the autonomous system"""
        # Implementation for pausing
        await self.send(text_data=json.dumps({
            'type': 'system_paused',
            'message': 'Autonomous system paused'
        }))

    async def resume_system(self):
        """Resume the autonomous system"""
        # Implementation for resuming
        await self.send(text_data=json.dumps({
            'type': 'system_resumed',
            'message': 'Autonomous system resumed'
        }))