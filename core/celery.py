"""
Celery configuration for the core Django application.
This file initializes Celery with Django settings and automated schedules.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('unified_donkey_betz_core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Schedule — MINIMAL (token-conservation mode)
# Session 1077+: Stripped to essentials only. Full schedule preserved in git history.
# Only cleanups + health checks run. All agent exercises, spider crawls,
# intelligence loops, and content generation DISABLED to conserve API tokens.
# Re-enable selectively when needed.
app.conf.beat_schedule = {
    # ── Essential health checks ──────────────────────────────────────────
    'heart-service-heartbeat': {
        'task': 'core.tasks.run_heartbeat',
        'schedule': 600,  # Every 10 min
        'options': {'queue': 'broadcast', 'expires': 600},
    },
    'check-celery-health': {
        'task': 'core.tasks.check_celery_health',
        'schedule': 600,
        'options': {'queue': 'broadcast', 'expires': 600},
    },
    'monitor-celery-health': {
        'task': 'core.tasks.monitor_celery_health',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'broadcast', 'expires': 1800},
    },

    # ── Essential cleanups (daily/weekly, low cost) ──────────────────────
    'cleanup-stuck-agent-executions': {
        'task': 'core.tasks.cleanup_stale_agent_executions',
        'schedule': crontab(minute='*/10'),
        'options': {'queue': 'broadcast', 'expires': 600},
    },
    'cleanup-celery-task-events': {
        'task': 'core.tasks.cleanup_celery_task_events',
        'schedule': crontab(minute=0, hour=4, day_of_week='sunday'),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-boardroom-junk': {
        'task': 'core.tasks.cleanup_boardroom_junk',
        'schedule': crontab(minute=30, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-junk-initiatives': {
        'task': 'core.tasks.cleanup_junk_initiatives',
        'schedule': crontab(minute=0, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-conversation-duplicates': {
        'task': 'core.tasks.cleanup_conversation_duplicates_task',
        'schedule': crontab(minute=30, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-stale-content': {
        'task': 'core.tasks.cleanup_stale_content',
        'schedule': crontab(minute=5, hour=10),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-expired-uploads': {
        'task': 'core.tasks.cleanup_expired_uploads',
        'schedule': crontab(minute=30, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'enforce-data-retention': {
        'task': 'core.tasks.enforce_data_retention',
        'schedule': crontab(minute=0, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'enforce-db-retention-daily': {
        'task': 'core.tasks.enforce_db_retention',
        'schedule': crontab(minute=0, hour=11),
        'options': {'queue': 'long_running', 'expires': 3600},
    },
    'cleanup-llm-call-logs': {
        'task': 'core.tasks.cleanup_llm_call_logs',
        'schedule': crontab(minute=15, hour=4, day_of_week='sunday'),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-old-notifications': {
        'task': 'core.tasks.cleanup_old_notifications',
        'schedule': crontab(minute=30, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-spider-item-hashes': {
        'task': 'core.tasks.cleanup_spider_item_hashes',
        'schedule': crontab(minute=30, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-expired-pa-insights': {
        'task': 'core.tasks.cleanup_expired_pa_insights',
        'schedule': crontab(minute=0, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-stale-dreams': {
        'task': 'core.tasks.cleanup_stale_dreams',
        'schedule': crontab(minute=0, hour=6),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-old-resolve-jobs': {
        'task': 'core.tasks.cleanup_old_resolve_jobs',
        'schedule': crontab(minute=0, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-resolved-signatures': {
        'task': 'core.tasks.cleanup_resolved_signatures',
        'schedule': crontab(minute=45, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-learning-readback': {
        'task': 'core.tasks.cleanup_learning_readback_events',
        'schedule': crontab(minute=0, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'clean-stale-data': {
        'task': 'ai_core.tasks.clean_stale_data',
        'schedule': crontab(minute=0, hour=2),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-audio-cache': {
        'task': 'core.tasks.cleanup_audio_cache',
        'schedule': crontab(minute=0, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-old-model-files': {
        'task': 'ml.cleanup_old_model_files',
        'schedule': crontab(minute=0, hour=1, day_of_week=1),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-old-predictions': {
        'task': 'sports.cleanup_old_predictions',
        'schedule': crontab(minute=0, hour=3, day_of_week=1),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-opportunities-daily': {
        'task': 'intelligence.tasks.cleanup_old_opportunities',
        'schedule': crontab(minute=0, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-expired-signals': {
        'task': 'cleanup_expired_signals',
        'schedule': crontab(minute=30, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'auto-archive-stale-deliverables': {
        'task': 'core.tasks.auto_archive_stale_deliverables',
        'schedule': crontab(minute=0, hour=12),
        'options': {'queue': 'default', 'expires': 3600},
    },
}

# Task routing configuration
# Session 573: Task routes are now defined in settings.py (CELERY_TASK_ROUTES)
# Multi-queue architecture:
#   - default: Quick tasks (most core.tasks.*)
#   - long_running: Spider network, agent conversations, dreams (1+ min tasks)
#   - broadcast: High-frequency status updates (30-180s interval tasks)
#   - agents, sports, content, ml: Module-specific queues
# See settings.py CELERY_TASK_ROUTES for full configuration
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Session 919: Explicitly include task modules with non-standard names.
# autodiscover_tasks() only finds tasks.py, not tasks_agents.py
# Using app.conf.imports ensures workers import these modules at startup.
app.conf.imports = (
    'core.tasks_agents',  # Agent execution tasks (execute_agent, execute_orchestration)
)


# Session 983: Connect Celery task telemetry signals.
# Writes CeleryTaskEvent rows on task_prerun/task_postrun/task_failure
# so status_snapshot_tool can report accurate Celery execution counts
# regardless of the CELERY_RESULT_BACKEND setting.
import core.celery_telemetry  # noqa: F401  — signal handlers connect on import


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    logger.error(f'Request: {self.request!r}')
    return 'Core Celery is working!'
