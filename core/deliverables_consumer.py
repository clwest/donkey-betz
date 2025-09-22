"""
WebSocket Consumer for Live Deliverables
Shows actual deliverables being created by agents
"""
import json
import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
import redis

class DeliverablesConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time deliverable updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(
            'deliverables',
            self.channel_name
        )

        # Send recent deliverables
        await self.send_recent_deliverables()

        # Start monitoring loop
        self.monitoring = True
        asyncio.create_task(self.monitor_deliverables())

    async def disconnect(self, close_code):
        self.monitoring = False
        await self.channel_layer.group_discard(
            'deliverables',
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get('type') == 'request_deliverables':
            await self.send_recent_deliverables()

    async def send_recent_deliverables(self):
        """Send recent deliverables from the system"""

        deliverables = []

        # Get recent deliverables from Redis
        deliverable_keys = self.redis_client.keys('deliverable:*')

        for key in deliverable_keys[:20]:  # Last 20 deliverables
            data = self.redis_client.hgetall(key)
            if data:
                deliverables.append({
                    'id': data.get('id'),
                    'type': data.get('type', 'document'),
                    'title': data.get('title'),
                    'description': data.get('description'),
                    'agent': data.get('agent'),
                    'createdAt': data.get('created_at'),
                    'status': data.get('status', 'ready'),
                    'progress': float(data.get('progress', 100)),
                    'value': float(data.get('value', 0)),
                    'wordCount': int(data.get('word_count', 0)) if data.get('word_count') else None,
                    'fileSize': data.get('file_size'),
                    'preview': data.get('preview', ''),
                    'downloadUrl': data.get('download_url')
                })

        # Also check for deliverables from freelance jobs
        job_deliverables = self.redis_client.keys('freelance:deliverable:*')

        for key in job_deliverables[:10]:
            data = self.redis_client.hgetall(key)
            if data:
                deliverables.append({
                    'id': data.get('id'),
                    'type': self.determine_type(data),
                    'title': data.get('title'),
                    'description': f"Freelance project: {data.get('job_title', '')}",
                    'agent': data.get('agent', 'Content Creator'),
                    'createdAt': data.get('created_at'),
                    'status': data.get('status', 'generating'),
                    'progress': float(data.get('progress', 0)),
                    'value': float(data.get('value', 0)),
                    'preview': data.get('preview', ''),
                    'downloadUrl': data.get('download_url')
                })

        await self.send(text_data=json.dumps({
            'type': 'deliverables_list',
            'deliverables': deliverables,
            'timestamp': datetime.now().isoformat()
        }))

    def determine_type(self, data):
        """Determine deliverable type from job data"""
        job_type = data.get('job_type', '').lower()
        skills = data.get('skills', '').lower()

        if 'blog' in job_type or 'content' in job_type or 'article' in job_type:
            return 'blog_post'
        elif 'code' in skills or 'api' in skills or 'react' in skills:
            return 'code'
        elif 'design' in skills or 'ui' in skills or 'ux' in skills:
            return 'design'
        elif 'data' in skills or 'analysis' in skills:
            return 'data_analysis'
        else:
            return 'document'

    async def monitor_deliverables(self):
        """Monitor for new deliverables being created"""

        while self.monitoring:
            try:
                # Check for new deliverables
                updates_key = 'deliverable:updates:queue'

                update = self.redis_client.lpop(updates_key)

                if update:
                    update_data = json.loads(update)

                    # Send update to client
                    await self.send(text_data=json.dumps({
                        'type': 'deliverable_update',
                        **update_data,
                        'timestamp': datetime.now().isoformat()
                    }))

                # Check for freelance job completions
                completed_jobs = self.redis_client.keys('freelance:job:completed:*')

                for job_key in completed_jobs[:5]:  # Check latest 5
                    job_data = self.redis_client.hgetall(job_key)

                    if job_data and job_data.get('deliverable_notified') != 'true':
                        # Send deliverable created notification
                        await self.send(text_data=json.dumps({
                            'type': 'deliverable_created',
                            'deliverable': {
                                'id': f"deliverable_{job_data.get('id')}",
                                'type': self.determine_type(job_data),
                                'title': job_data.get('deliverable_title', 'Project Deliverable'),
                                'agent': job_data.get('agent', 'AI Agent'),
                                'value': float(job_data.get('value', 0)),
                                'status': 'ready'
                            }
                        }))

                        # Mark as notified
                        self.redis_client.hset(job_key, 'deliverable_notified', 'true')

                # Check for active job progress
                active_jobs = self.redis_client.keys('freelance:job:executing:*')

                for job_key in active_jobs:
                    job_data = self.redis_client.hgetall(job_key)

                    if job_data:
                        # Send progress update
                        await self.send(text_data=json.dumps({
                            'type': 'progress_update',
                            'id': f"deliverable_{job_data.get('id')}",
                            'progress': float(job_data.get('progress', 0)),
                            'status': job_data.get('status', 'generating')
                        }))

            except Exception as e:
                print(f"Deliverables monitor error: {e}")

            await asyncio.sleep(2)  # Check every 2 seconds

    async def deliverable_update(self, event):
        """Handle deliverable updates from other parts of the system"""
        await self.send(text_data=json.dumps(event['data']))