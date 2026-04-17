"""
Celery configuration for the core Django application.
This file initializes Celery with Django settings and automated schedules.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
import logging
logger = logging.getLogger(__name__)  # Session 1083

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
    # Apr 2026: SpiderData retention — trim raw_data >7d, delete >30d
    # Prevents raw JSON blobs (~440KB/row) from filling the database
    'spider-data-retention': {
        'task': 'core.tasks.spider_data_retention',
        'schedule': crontab(minute=0, hour=4),  # Daily at 4 AM
        'options': {'queue': 'long_running', 'expires': 3600},
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
    # Session 1085: Weekly pattern decay — stale/ineffective patterns lose confidence
    'decay-learning-patterns': {
        'task': 'core.tasks.decay_learning_patterns',
        'schedule': crontab(minute=0, hour=5, day_of_week=0),  # Sunday 5am
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

    # ── CTOAgent daily reliability diagnostic (Session 1093) ────────────────
    # Fires once daily at 13:15 UTC = 7:15 AM MDT / 6:15 AM MST.
    # Task itself is gated by CTO_DIAGNOSTIC_ENABLED env flag — safe to leave
    # in the schedule even when the flag is off (returns immediately).
    # Governance posting is gated independently by CTO_DIAGNOSTIC_POSTING_ENABLED.
    'cto-daily-diagnostic': {
        'task': 'core.tasks.run_cto_daily_diagnostic',
        'schedule': crontab(minute=15, hour=13),
        'options': {'queue': 'long_running', 'expires': 7200},
    },

    # ── COOAgent daily operations diagnostic (Session 1094) ─────────────────
    # Second consumer of the scheduled_diagnostic_runner primitive. Fires at
    # 13:30 UTC = 7:30 AM MDT / 6:30 AM MST — 15 minutes after the CTO
    # diagnostic so the two don't hit the long_running queue simultaneously
    # and so their narrative outputs are visually spaced in the attention
    # inbox. Gated by COO_DIAGNOSTIC_ENABLED (default false); posting gated
    # independently by COO_DIAGNOSTIC_POSTING_ENABLED.
    'coo-daily-diagnostic': {
        'task': 'core.tasks.run_coo_daily_diagnostic',
        'schedule': crontab(minute=30, hour=13),
        'options': {'queue': 'long_running', 'expires': 7200},
    },

    # ── TrendAnalysisAgent daily anomaly diagnostic (Session 1094) ──────────
    # Third consumer of the scheduled_diagnostic_runner primitive. Fires at
    # 13:45 UTC = 7:45 AM MDT / 6:45 AM MST — another 15 min after COO so
    # the three diagnostics stagger and never hit long_running simultaneously.
    # Metrics surface is distributional anomaly (volume deltas, coverage
    # gaps, spider concentration, cluster velocity) — structurally different
    # from CTO (counts) and COO (throughput+aging), validates primitive
    # generality on non-SLA data per Rigby's Session 1094 recommendation.
    'trend-daily-diagnostic': {
        'task': 'core.tasks.run_trend_daily_diagnostic',
        'schedule': crontab(minute=45, hour=13),
        'options': {'queue': 'long_running', 'expires': 7200},
    },

    # ── Spider Network (re-enabled) ────────────────────────────────────────
    # Core spider execution — crawl all registered spiders
    'run-spider-network': {
        'task': 'core.tasks.run_spider_network',
        'schedule': crontab(minute='*/30'),  # Every 30 min
        'options': {'queue': 'long_running', 'expires': 1800},
    },
    # Warm up spider network — pre-flight checks + health
    'warm-up-spiders': {
        'task': 'ai_core.tasks.warm_up_spider_network',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'options': {'queue': 'long_running', 'expires': 21600},
    },

    # ── Spider Data Processing ──────────────────────────────────────────────
    # Process new SpiderData rows (embedding text, dedup, quality)
    'process-core-spider-data': {
        'task': 'core.tasks.process_core_spider_data',
        'schedule': crontab(minute='*/5'),  # Every 5 min
        'options': {'queue': 'long_running', 'expires': 300},
    },
    # Backfill embeddings for spider data without vectors
    'backfill-spider-embeddings': {
        'task': 'core.tasks.backfill_spider_embeddings',
        'schedule': crontab(minute='*/15'),  # Every 15 min
        'kwargs': {'batch_size': 500},
        'options': {'queue': 'ml', 'expires': 900},
    },

    # ── Signal Intelligence ─────────────────────────────────────────────────
    # Aggregate spider data into signal clusters
    'aggregate-spider-signals': {
        'task': 'aggregate_spider_signals',
        'schedule': crontab(minute='*/30'),
        'kwargs': {'lookback_hours': 6},
        'options': {'queue': 'long_running', 'expires': 1800},
    },
    # Scan spider data for opportunities
    'scan-spider-opportunities': {
        'task': 'intelligence.tasks.scan_spider_opportunities',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'long_running', 'expires': 1800},
    },
    # Process spider actions (convert spider data to action items)
    'process-spider-actions': {
        'task': 'core.tasks.process_spider_actions',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'long_running', 'expires': 1800},
    },
    # Collect real opportunities from spider data
    'collect-real-opportunities': {
        'task': 'ai_core.tasks.collect_real_opportunities',
        'schedule': crontab(minute='*/30'),  # Every 30 min (was 15)
        'options': {'queue': 'long_running', 'expires': 1800},
    },

    # ── Dreams & Content ────────────────────────────────────────────────────
    # Surface top dreams as boardroom attention items
    'dream-daily-surfacing': {
        'task': 'core.tasks.surface_top_dreams',
        'schedule': crontab(hour=9, minute=0),  # Daily 9 AM
        'options': {'queue': 'default', 'expires': 3600},
    },

    # ── Operator Edge Newsletter ───────────────────────────────────────────
    # Weekly newsletter from signal clusters + spider data
    'generate-operator-edge-newsletter': {
        'task': 'core.tasks.generate_operator_edge_newsletter',
        'schedule': crontab(hour=13, minute=0, day_of_week='friday'),  # Friday 6 AM MST = 13:00 UTC
        'options': {'queue': 'content', 'expires': 3600},
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
