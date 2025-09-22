"""
Agent Notifier Utility
Notifies the Agent Monitor when agents start/complete tasks
"""
import redis
import json
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class AgentNotifier:
    """Utility for notifying agent monitor of agent activity"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self._channel_layer = None

    @property
    def channel_layer(self):
        """Lazy initialization of channel layer"""
        if self._channel_layer is None:
            try:
                self._channel_layer = get_channel_layer()
            except Exception as e:
                print(f"Could not get channel layer: {e}")
                self._channel_layer = None
        return self._channel_layer

    def notify_task_start(self, agent_name, task_info):
        """Notify that an agent has started a task"""

        # Store in Redis for the agent monitor to read
        task_key = f"agent:task:{agent_name}"
        self.redis_client.set(task_key, task_info.get('title', 'Unknown Task'))

        # Update agent stats
        stats_key = f"agent:stats:{agent_name}"
        self.redis_client.hset(stats_key, 'last_active', datetime.now().isoformat())
        self.redis_client.hset(stats_key, 'status', 'working')

        # Store active task details
        active_task_key = f"task:active:{task_info.get('id', 'unknown')}"
        self.redis_client.hset(active_task_key, mapping={
            'id': task_info.get('id'),
            'agent': agent_name,
            'type': task_info.get('type', 'Freelance Project'),
            'progress': 0,
            'estimated_time': task_info.get('estimated_time', '30s'),
            'value': task_info.get('value', 0),
            'status': 'executing',
            'title': task_info.get('title', 'Unknown Task')
        })

        # Queue update for agent monitor
        update_data = {
            'type': 'task_update',
            'task': {
                'id': task_info.get('id'),
                'agentName': agent_name,
                'taskType': task_info.get('type', 'Freelance Project'),
                'progress': 0,
                'value': task_info.get('value', 0),
                'status': 'executing',
                'title': task_info.get('title')
            },
            'timestamp': datetime.now().isoformat()
        }

        self.redis_client.lpush('agent:updates:queue', json.dumps(update_data))

        # Try to send WebSocket notification
        if self.channel_layer:
            try:
                async_to_sync(self.channel_layer.group_send)(
                    'agent_monitor',
                    {
                        'type': 'agent_task_update',
                        'data': update_data
                    }
                )
            except Exception as e:
                print(f"Could not send WebSocket update: {e}")

    def notify_task_progress(self, agent_name, task_id, progress, status='executing'):
        """Update task progress"""

        # Update active task
        active_task_key = f"task:active:{task_id}"
        if self.redis_client.exists(active_task_key):
            self.redis_client.hset(active_task_key, 'progress', progress)
            self.redis_client.hset(active_task_key, 'status', status)

        # Queue progress update
        update_data = {
            'type': 'progress_update',
            'taskId': task_id,
            'agentName': agent_name,
            'progress': progress,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }

        self.redis_client.lpush('agent:updates:queue', json.dumps(update_data))

    def notify_task_complete(self, agent_name, task_id, result=None):
        """Notify that an agent has completed a task"""

        # Clear active task
        task_key = f"agent:task:{agent_name}"
        self.redis_client.delete(task_key)

        # Update agent stats
        stats_key = f"agent:stats:{agent_name}"
        self.redis_client.hincrby(stats_key, 'completed_tasks', 1)
        if result and result.get('value'):
            current_revenue = float(self.redis_client.hget(stats_key, 'revenue') or 0)
            self.redis_client.hset(stats_key, 'revenue', current_revenue + result['value'])

        # Remove from active tasks
        active_task_key = f"task:active:{task_id}"
        self.redis_client.delete(active_task_key)

        # Queue completion update
        update_data = {
            'type': 'task_completed',
            'taskId': task_id,
            'agentName': agent_name,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

        self.redis_client.lpush('agent:updates:queue', json.dumps(update_data))

    def notify_deliverable_created(self, deliverable_info):
        """Notify that a deliverable has been created"""

        # Store deliverable
        deliverable_key = f"deliverable:{deliverable_info.get('id')}"
        self.redis_client.hset(deliverable_key, mapping={
            'id': deliverable_info.get('id'),
            'type': deliverable_info.get('type', 'document'),
            'title': deliverable_info.get('title'),
            'agent': deliverable_info.get('agent'),
            'created_at': datetime.now().isoformat(),
            'status': deliverable_info.get('status', 'ready'),
            'value': deliverable_info.get('value', 0),
            'preview': deliverable_info.get('preview', ''),
            'word_count': deliverable_info.get('word_count', 0)
        })

        # Queue deliverable update
        update_data = {
            'type': 'deliverable_created',
            'deliverable': deliverable_info,
            'timestamp': datetime.now().isoformat()
        }

        self.redis_client.lpush('deliverable:updates:queue', json.dumps(update_data))

# Global instance
agent_notifier = AgentNotifier()