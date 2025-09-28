"""
Celery configuration for the Unified Donkey Betz Platform.

This configuration sets up:
- Redis as the message broker
- Task routing for different domains (agents, sports, content, self_awareness)
- Beat scheduling for periodic tasks
- Proper error handling and monitoring
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

app = Celery('unified_donkey_betz')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Task routing configuration
app.conf.task_routes = {
    'agents.*': {'queue': 'agents'},
    'sports.*': {'queue': 'sports'},
    'content.*': {'queue': 'content'},
    'self_awareness.*': {'queue': 'self_awareness'},
}

# Beat schedule configuration
app.conf.beat_schedule = {
    'self-awareness-scan': {
        'task': 'self_awareness.tasks.scan_codebase',
        'schedule': 3600.0,  # Run every hour
    },
    'sports-odds-update': {
        'task': 'sports.tasks.update_odds',
        'schedule': 30.0,  # Run every 30 seconds
    },
    'agent-registry-refresh': {
        'task': 'agents.tasks.refresh_registry',
        'schedule': 900.0,  # Run every 15 minutes
    },
    'system-health-check': {
        'task': 'core.tasks.system_health_check',
        'schedule': 300.0,  # Run every 5 minutes
    },
}

# Error handling configuration
app.conf.task_reject_on_worker_lost = True
app.conf.task_acks_late = True
app.conf.worker_prefetch_multiplier = 1

# Monitoring configuration
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'

if __name__ == '__main__':
    app.start()