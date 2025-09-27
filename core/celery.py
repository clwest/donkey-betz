"""
Celery configuration for the core Django application.
This file initializes Celery with Django settings and automated schedules.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('unified_donkey_betz_core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Schedule for Automated Spider Updates and Real Data Collection
app.conf.beat_schedule = {
    'collect-real-opportunities': {
        'task': 'backend.tasks.collect_real_opportunities',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # Expire after 15 minutes if not executed
        }
    },
    'refresh-ai-opportunities': {
        'task': 'backend.tasks.refresh_ai_content_opportunities',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,
        }
    },
    'sync-revenue-metrics': {
        'task': 'backend.tasks.sync_revenue_metrics',
        'schedule': crontab(minute=0),  # Every hour
        'options': {
            'expires': 3600,
        }
    },
    'sync-shared-memory': {
        'task': 'intelligence.shared_memory.sync_all_entity_memories',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'options': {
            'expires': 600,
        }
    },
    'clean-stale-data': {
        'task': 'backend.tasks.clean_stale_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'options': {
            'expires': 7200,
        }
    },
    'warm-up-spiders': {
        'task': 'backend.tasks.warm_up_spider_network',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'options': {
            'expires': 14400,
        }
    },
}

# Spider-specific task routing configuration
app.conf.task_routes = {
    'backend.spiders.tasks.*': {'queue': 'spider_queue'},
}
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f'Request: {self.request!r}')
    return 'Core Celery is working!'