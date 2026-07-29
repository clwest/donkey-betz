# CRITICAL_PATH_HUB — see docs/CRITICAL_PATH_HUBS.md
# Changes here can break the whole platform. Request Chris review before merge.
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


# Session 2731 F-CW-2 — worker lifecycle observability. Pre-S2731 the
# only way to see a prefork child recycle (Railway/production, triggered
# by CELERY_WORKER_MAX_TASKS_PER_CHILD or CELERY_WORKER_MAX_MEMORY_PER_CHILD)
# was to parse celery's internal MainProcess logger — easy to miss in
# tail. These two handlers emit `[CELERY_WORKER_INIT]` at child startup
# and `[CELERY_WORKER_SHUTDOWN]` at child exit so recycle events become
# grep-visible in ≤1 second.
#
# The `worker_process_init` signal fires once per prefork child at
# fork-time (Railway) OR once per worker process at startup (macOS
# solo pool, which doesn't fork). Either way the log line lets an
# operator answer "when did this worker child last restart?" without
# parsing multiple log sources.
from celery.signals import worker_process_init, worker_process_shutdown


@worker_process_init.connect
def _log_worker_process_init(**_kwargs):
    """Session 2731 F-CW-2 — emit grep-visible worker child startup event."""
    import os as _os
    logger.info(
        "[CELERY_WORKER_INIT] pid=%d ppid=%d hostname=%s app=%s",
        _os.getpid(),
        _os.getppid(),
        _os.uname().nodename,
        app.main,
    )


@worker_process_shutdown.connect
def _log_worker_process_shutdown(pid=None, exitcode=None, **_kwargs):
    """Session 2731 F-CW-2 — emit grep-visible worker child shutdown event.

    On prefork, this fires per-child when the child is recycled
    (max_tasks_per_child or max_memory_per_child reached) or when the
    parent shuts down. `exitcode` names the reason: 0 = clean recycle,
    non-zero = kill signal (e.g. SIGKILL from OOM).
    """
    import os as _os
    logger.info(
        "[CELERY_WORKER_SHUTDOWN] pid=%s exitcode=%s hostname=%s",
        pid if pid is not None else _os.getpid(),
        exitcode,
        _os.uname().nodename,
    )


@worker_process_init.connect
def _reap_orphan_agent_executions_on_startup(**_kwargs):
    """S2800 (Session 2800 Option B): sweep AgentExecution rows left in
    `in_progress` state by a dead worker + transition to `cancelled` with
    a machine-parseable error_message so the 60-min cleanup watchdog
    doesn't later reap them as `failed`.

    Runs on every worker child startup. Rows with fresh heartbeats
    (still-alive workers) are excluded via the `last_heartbeat_at`
    staleness filter. Bounded to `created_at` in the last 24h to avoid
    picking up truly ancient rows (those are their own housekeeping
    problem). Bulk UPDATE — best-effort, does not block worker startup
    if the query errors.

    Rigby T1 SIGN (S2800): use existing `cancelled` enum value +
    machine-parseable error_message rather than adding a new
    `interrupted` enum value; reduces downstream consumer audit.
    """
    try:
        # Local imports — signal handlers must not touch the import
        # machinery at tick time. See heartbeat comment at
        # core/tasks_agents.py:2450 for the rationale.
        from datetime import timedelta
        from django.db import close_old_connections as _reap_close_old_connections
        from django.db.models import Q
        from django.utils import timezone as _reap_timezone
        from core.models_unified_system import AgentExecution

        _reap_close_old_connections()
        now = _reap_timezone.now()
        heartbeat_cutoff = now - timedelta(minutes=3)
        created_cutoff = now - timedelta(hours=24)

        # Orphan filter: in-progress AND (no heartbeat ever, or heartbeat
        # went stale ≥3min ago). Fresh-heartbeat rows are left alone (those
        # workers are still running).
        rowcount = AgentExecution.objects.filter(
            Q(last_heartbeat_at__isnull=True) | Q(last_heartbeat_at__lt=heartbeat_cutoff),
            status='in_progress',
            created_at__gte=created_cutoff,
        ).update(
            status='cancelled',
            error_message='Worker restart — execution interrupted (S2800)',
            completed_at=now,
        )
        if rowcount:
            logger.info(
                "[CELERY_WORKER_STARTUP_REAP] transitioned %d orphan AgentExecution row(s) to cancelled",
                rowcount,
            )
    except Exception as e:
        # Best-effort — never block worker startup on this.
        logger.warning("[CELERY_WORKER_STARTUP_REAP] reap failed: %s", e)

# Celery Beat Schedule — MINIMAL (token-conservation mode)
# Session 1077+: Stripped to essentials only. Full schedule preserved in git history.
# Only cleanups + health checks run. All agent exercises, spider crawls,
# intelligence loops, and content generation DISABLED to conserve API tokens.
# Re-enable selectively when needed.
#
# **CANONICAL SOURCE (Session 1157, option A):** The Celery beat schedule
# is defined here in `core/celery.py` (code-first single source of truth).
# `core/management/commands/add_critical_celery_tasks.py` reads this dict
# and materializes/repairs django-celery-beat `PeriodicTask` rows from it;
# that command does not define scheduling semantics. Docs across the repo
# describe this schedule but must not contradict it — if any doc disagrees
# with what's defined here, this file wins.
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

    # Session 1161 cadence wrapper for the PA acks_late=False 24-48h
    # observation window. Every 30 minutes, append a pa_acks_health
    # snapshot (queue depth + per-worker rollup + oldest_queued +
    # inflight_estimate + hang_signature) to logs/pa_acks_health/
    # YYYY-MM-DD.jsonl. Status changes trigger WARN log lines.
    'pa-acks-health-capture': {
        'task': 'core.tasks.capture_pa_acks_health_snapshot',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'broadcast', 'expires': 1800},
    },

    # Session 1167 — COO Nervous System Backlog item #5. Every 5 min,
    # sample per-worker RSS via psutil and compare to the cap parsed
    # from each worker's --max-memory-per-child cmdline flag. Writes
    # logs/worker_memory/YYYY-MM-DD.jsonl (UTC). Sustained pressure
    # (>=80% of cap on N=3 consecutive adjacent samples) → CRIT +
    # downshift recommendation. Soft signal only — no auto-restart.
    'worker-memory-capture': {
        'task': 'core.tasks.capture_worker_memory_snapshot',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'broadcast', 'expires': 240},
    },

    # Session 1191 — Initiative activity tick. Cheap, no-LLM staleness
    # sweep that refreshes `last_activity_at` for Initiatives where the
    # field is NULL or older than 24h, based on cheap signals only (max
    # of initiative.updated_at + linked action_items.updated_at + linked
    # deliverables.updated_at). Hard-capped at 100 Initiatives per run.
    # Pairs with the populate_initiatives_api auto-bootstrap fix + the
    # `backfill_initiative_activity` mgmt command (one-shot for historical
    # NULL rows). Singleton-locked via redis_lock primitive — TTL=300s
    # comfortably covers expected runtime (~1-2s per Initiative * 100 cap).
    # Per Rigby's Session 1162 §6.4 invariant this task ONLY touches the
    # read-side staleness signal — advance_initiative_pipeline remains the
    # only path that writes stages or invokes LLM/content generation.
    'initiative-activity-tick': {
        'task': 'core.tasks.initiative_activity_tick',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'default', 'expires': 1500},
    },

    # Session 1174 PR-2a — Expire stale AgentFollowupSubscription rows.
    # Subscriptions are created with after_seconds<=600 TTL. If the
    # corresponding execution never reaches terminal status before
    # expires_at, the row stays armed. This task transitions stale rows
    # to expired. Every 2 minutes is well below the 600s cap so any
    # expired row is reaped within one cadence cycle. Atomic queryset
    # update is race-safe against concurrent fire_agent_followup_subscriptions.
    'expire-stale-followup-subscriptions': {
        'task': 'core.tasks.expire_stale_followup_subscriptions',
        'schedule': crontab(minute='*/2'),
        'options': {'queue': 'broadcast', 'expires': 90},
    },

    # Session 1129 Move 2 Round 2 — Soft-delete expired fleet artifacts.
    # Daily run is the spec'd default. Staging may want hourly; if so,
    # change schedule to crontab(minute=0).
    'cleanup-expired-fleet-artifacts': {
        'task': 'core.tasks.cleanup_expired_fleet_artifacts',
        'schedule': crontab(hour=2, minute=10),  # 2:10 AM MST daily
        'options': {'queue': 'broadcast', 'expires': 3600},
    },

    # Session 1163 B-style — hard-delete FinalAppliedOverrides rows
    # older than 90 days. Slightly offset from the other 2 AM cleanups
    # so they don't all hit Postgres at once.
    'purge-finaloverrides-90d': {
        'task': 'core.tasks.purge_finaloverrides_older_than_90d',
        'schedule': crontab(hour=2, minute=40),  # 2:40 AM MST daily
        'options': {'queue': 'broadcast', 'expires': 3600},
    },

    # T-VIP-1 backstop (ADR-0005 §3.5 F-C-VIP-1 risk-gate). Primary
    # enforcement is middleware-side; this deactivates any VIP user
    # whose invite is past account_expires_at within one beat cycle
    # even if they never make another request. Offset from other 2 AM
    # cleanups.
    'cleanup-expired-vip-users': {
        'task': 'core.tasks_vip.cleanup_expired_vip_users',
        'schedule': crontab(hour=2, minute=55),  # 2:55 AM MST daily
        'options': {'queue': 'broadcast', 'expires': 3600},
    },

    # Session 1130 Move 3 Round 2 — Hard-delete expired fleet events.
    # Slightly later than the artifact cleanup so the two don't both
    # hit Postgres at once. Retention controlled by
    # FLEET_EVENT_RETENTION_DAYS (default 30).
    'cleanup-expired-fleet-events': {
        'task': 'core.tasks.cleanup_expired_fleet_events',
        'schedule': crontab(hour=2, minute=25),  # 2:25 AM MST daily
        'options': {'queue': 'broadcast', 'expires': 3600},
    },

    # ── Essential cleanups (daily/weekly, low cost) ──────────────────────
    'cleanup-stuck-agent-executions': {
        'task': 'core.tasks.cleanup_stale_agent_executions',
        'schedule': crontab(minute='*/10'),
        'options': {'queue': 'broadcast', 'expires': 600},
    },
    # Session 1221 P2 — Tier 2 from deliverable 7ae61cf7. Sweep orphaned
    # LLMCallEvent.status='STARTED' rows. Same 10-min cadence + broadcast
    # queue as the agent-execution cleanup so they tend to fire in the
    # same beat tick. Default threshold 10 min — well above the longest
    # observed legitimate call (102.7s) and the Tier 1 cap floor (180s).
    'cleanup-stuck-llm-calls': {
        'task': 'core.tasks.cleanup_stale_llm_calls',
        'schedule': crontab(minute='*/10'),
        'options': {'queue': 'broadcast', 'expires': 600},
    },
    # S3037 Reliability Audit v0 Step 6 S4 — sweep stale-running OpsRun
    # rows. Mirror of cleanup-stuck-agent-executions cadence + queue.
    # Discharges the "no lost dispatches" reliability rule violation
    # (2 rows were found stuck 383h + 434h at audit time). Default
    # threshold 60min — matches AgentExecution sibling cleanup; well
    # above the longest observed legitimate OpsRun (~40s).
    'cleanup-stuck-ops-runs': {
        'task': 'core.tasks.cleanup_stale_ops_runs',
        'schedule': crontab(minute='*/10'),
        'options': {'queue': 'broadcast', 'expires': 600},
    },
    'cleanup-celery-task-events': {
        'task': 'core.tasks.cleanup_celery_task_events',
        # Session 1165 (COO #3): staggered 4:00 → 4:50 to relieve hour=4 :00 cluster
        'schedule': crontab(minute=50, hour=4, day_of_week='sunday'),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-boardroom-junk': {
        'task': 'core.tasks.cleanup_boardroom_junk',
        'schedule': crontab(minute=30, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-junk-initiatives': {
        'task': 'core.tasks.cleanup_junk_initiatives',
        # Session 1165 (COO #3): staggered 4:00 → 4:05 (hour=4 :00 cluster relief)
        'schedule': crontab(minute=5, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-conversation-duplicates': {
        'task': 'core.tasks.cleanup_conversation_duplicates_task',
        # Session 1165 (COO #3): staggered 4:30 → 4:33 (hour=4 :30 cluster relief)
        'schedule': crontab(minute=33, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-stale-content': {
        'task': 'core.tasks.cleanup_stale_content',
        'schedule': crontab(minute=5, hour=10),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-expired-uploads': {
        'task': 'core.tasks.cleanup_expired_uploads',
        # Session 1165 (COO #3): staggered 4:30 → 4:36 (hour=4 :30 cluster relief)
        'schedule': crontab(minute=36, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'enforce-data-retention': {
        'task': 'core.tasks.enforce_data_retention',
        # Session 1165 (COO #3): staggered 4:00 → 4:55 (heavy retention → end of hour)
        'schedule': crontab(minute=55, hour=4),
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
        # Session 1165 (COO #3): staggered 3:30 → 3:35
        'schedule': crontab(minute=35, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-spider-item-hashes': {
        'task': 'core.tasks.cleanup_spider_item_hashes',
        # Session 1165 (COO #3): staggered 3:30 → 3:40 (isolate heavy hash sweep)
        'schedule': crontab(minute=40, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Apr 2026: SpiderData retention — trim raw_data >7d, delete >30d
    # Prevents raw JSON blobs (~440KB/row) from filling the database
    'spider-data-retention': {
        'task': 'core.tasks.spider_data_retention',
        # Session 1165 (COO #3): staggered 4:00 → 4:58 (heavy long_running, end-of-hour anchor)
        'schedule': crontab(minute=58, hour=4),
        'options': {'queue': 'long_running', 'expires': 3600},
    },
    'cleanup-expired-pa-insights': {
        'task': 'core.tasks.cleanup_expired_pa_insights',
        # Session 1165 (COO #3): staggered 3:00 → 3:10 (hour=3 :00 cluster relief)
        'schedule': crontab(minute=10, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-stale-dreams': {
        'task': 'core.tasks.cleanup_stale_dreams',
        'schedule': crontab(minute=0, hour=6),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-old-resolve-jobs': {
        'task': 'core.tasks.cleanup_old_resolve_jobs',
        # Session 1165 (COO #3): staggered 4:00 → 4:25
        'schedule': crontab(minute=25, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-resolved-signatures': {
        'task': 'core.tasks.cleanup_resolved_signatures',
        'schedule': crontab(minute=45, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-learning-readback': {
        'task': 'core.tasks.cleanup_learning_readback_events',
        # Session 1165 (COO #3): staggered 4:00 → 4:10
        'schedule': crontab(minute=10, hour=4),
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
        # Session 1165 (COO #3): staggered 3:00 → 3:25 (Mon-only; hour 3 cluster relief)
        'schedule': crontab(minute=25, hour=3, day_of_week=1),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-opportunities-daily': {
        'task': 'intelligence.tasks.cleanup_old_opportunities',
        # Session 1165 (COO #3): staggered 3:00 → 3:20
        'schedule': crontab(minute=20, hour=3),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'cleanup-expired-signals': {
        'task': 'cleanup_expired_signals',
        # Session 1165 (COO #3): staggered 4:30 → 4:39
        'schedule': crontab(minute=39, hour=4),
        'options': {'queue': 'default', 'expires': 3600},
    },
    'auto-archive-stale-deliverables': {
        'task': 'core.tasks.auto_archive_stale_deliverables',
        'schedule': crontab(minute=0, hour=12),
        'options': {'queue': 'default', 'expires': 3600},
    },

    # ── CTOAgent daily reliability diagnostic (Session 1093) ────────────────
    # Session 1096 fix: hour=7 NOT 13. django-celery-beat's DatabaseScheduler
    # interprets CrontabSchedule.hour in the schedule's timezone (which defaults
    # to `America/Denver` on this project — see Django TIME_ZONE). The prior
    # `hour=13` was intended as UTC but got interpreted as 13:00 Denver time
    # (19:00 UTC), so the diagnostic had literally never fired. Fixed now:
    # hour=7 + Denver tz = 13:00 UTC during DST / 14:00 UTC during MST.
    # Task itself is gated by CTO_DIAGNOSTIC_ENABLED env flag — safe to leave
    # in the schedule even when the flag is off (returns immediately).
    # Governance posting is gated independently by CTO_DIAGNOSTIC_POSTING_ENABLED.
    'cto-daily-diagnostic': {
        'task': 'core.tasks.run_cto_daily_diagnostic',
        'schedule': crontab(minute=15, hour=7),  # 7:15 AM Denver local
        'options': {'queue': 'long_running', 'expires': 7200},
    },

    # ── COOAgent daily operations diagnostic (Session 1094) ─────────────────
    # Second consumer of the scheduled_diagnostic_runner primitive. Fires at
    # 7:30 AM Denver local = 13:30 UTC (DST) / 14:30 UTC (MST) — 15 minutes
    # after CTO so the two don't hit long_running simultaneously and their
    # outputs are visually spaced. See Session 1096 note on the CTO entry
    # above for the hour=7 vs hour=13 fix history.
    # Gated by COO_DIAGNOSTIC_ENABLED (default false); posting gated
    # independently by COO_DIAGNOSTIC_POSTING_ENABLED.
    'coo-daily-diagnostic': {
        'task': 'core.tasks.run_coo_daily_diagnostic',
        'schedule': crontab(minute=30, hour=7),  # 7:30 AM Denver local
        'options': {'queue': 'long_running', 'expires': 7200},
    },

    # ── TrendAnalysisAgent daily anomaly diagnostic (Session 1094) ──────────
    # Third consumer of the scheduled_diagnostic_runner primitive. Fires at
    # 7:45 AM Denver local = 13:45 UTC (DST) / 14:45 UTC (MST) — another 15
    # min after COO so the three diagnostics stagger and never hit
    # long_running simultaneously. Metrics surface is distributional anomaly
    # (volume deltas, coverage gaps, spider concentration, cluster velocity)
    # — structurally different from CTO (counts) and COO (throughput+aging),
    # validates primitive generality on non-SLA data per Rigby's Session
    # 1094 recommendation. See Session 1096 note on the CTO entry above
    # for the hour=7 vs hour=13 fix history.
    'trend-daily-diagnostic': {
        'task': 'core.tasks.run_trend_daily_diagnostic',
        'schedule': crontab(minute=45, hour=7),  # 7:45 AM Denver local
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
    # Session 1131 Phase 2 (Rigby's path C) — daily curated snapshot.
    # Runs at 6:00 AM MST (= 13:00 UTC) so signal-studio's Curated tab
    # has fresh content before any morning sessions. Expires at 4h so
    # a stuck task can't trip an evening re-run.
    'curate-signal-clusters': {
        'task': 'curate_signal_clusters',
        'schedule': crontab(hour=13, minute=0),
        'kwargs': {'top_n': 10},
        'options': {'queue': 'long_running', 'expires': 4 * 3600},
    },
    # Session 2933 A3 v1 — signal-triggered agent auto-dispatch.
    # Scans SignalDispatch rules (code-defined in
    # core.services.signal_dispatch_service.SIGNAL_DISPATCH_RULES) every
    # 5 min, enqueues per-cluster dispatch tasks with global +
    # per-rule caps. Kill switch: settings.SIGNAL_DISPATCH_ENABLED.
    'scan-signal-dispatch-rules': {
        'task': 'scan_signal_dispatch_rules',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'long_running', 'expires': 300},
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
    # Weekly newsletter from signal clusters + spider data.
    # Session 1222 P6 (audit B2) — re-enabled with dry_run=True for the
    # 2-Friday burn-in. Migration 0364 flips the PeriodicTask row to
    # enabled=True; this static entry matches so a fresh environment
    # materializes the same safe-by-default state via
    # `add_critical_celery_tasks --force`. After burn-in passes, update
    # kwargs to {} or {'dry_run': False} to promote to live publishing.
    #
    # Schedule semantics (Session 1228 P3 fix): `crontab(...)` resolves
    # against CELERY_TIMEZONE = Django TIME_ZONE = America/Denver. The
    # original entry used `hour=13` with a "Friday 6 AM MST = 13:00 UTC"
    # comment but actually fired at 13:00 Denver = 19:00 UTC (during MDT).
    # Same misinterpretation class as the outreach beat (P2 PR #2569).
    # Pin to `hour=6, minute=0` Denver local; resulting UTC time drifts
    # seasonally (12:00 UTC in MDT, 13:00 UTC in MST) — matches the
    # Denver-morning intent stated in the comment.
    'generate-operator-edge-newsletter': {
        'task': 'core.tasks.generate_operator_edge_newsletter',
        'schedule': crontab(hour=6, minute=0, day_of_week='friday'),  # 6:00 AM Denver
        'kwargs': {'dry_run': True},
        'options': {'queue': 'content', 'expires': 3600},
    },

    # ── Outreach drafts daily (Session 1225 P2 — closes Option B beat) ─────
    # Generates up to 5 touch-1 OutreachDraft rows per UTC day from
    # contactable Opportunity rows via OpportunityDraftGenerator. Drafts
    # are approval-required (no auto-send). DAILY_GENERATE_CAP=5 is
    # enforced inside the generator regardless of the limit kwarg.
    # SYSTEM_PROMPT envelope (PR #2544) + anti-scrape sanitizer (PR #2545)
    # bind the LLM output to a specific per-offer delivery scope.
    #
    # Schedule semantics (Session 1228 P2 fix): `crontab(...)` resolves
    # against CELERY_TIMEZONE = Django TIME_ZONE = America/Denver. The
    # original PR #2548 used `hour=13` thinking it meant UTC, but it
    # actually meant 13:30 Denver = 19:30 UTC (during MDT). That mismatch
    # left the PeriodicTask row with crontab `30 13` and timezone
    # America/Denver — the task never fired at the intended 13:30 UTC =
    # 7:30 AM Denver morning slot. Pin to `hour=7, minute=30` Denver
    # local; the resulting UTC time drifts seasonally (13:30 UTC in MDT,
    # 14:30 UTC in MST) — same drift as the operator-edge convention.
    'generate-outreach-drafts-daily': {
        'task': 'core.tasks.generate_outreach_drafts_daily',
        'schedule': crontab(hour=7, minute=30),  # 7:30 AM Denver
        'options': {'queue': 'content', 'expires': 3600},
    },

    # Session 1233 Sub-step C — daily Chief-of-Staff morning brief.
    # Dispatches the morning_brief workflow which runs 8 steps
    # (rotation_slot_resolve → 4 lanes → decision_card_synthesis →
    # strategic_synthesis → create_morning_brief_deliverable) and
    # persists the final markdown brief into Chris's "Morning Brief"
    # ProjectWorkspace. Pin to 7:00 AM Denver local — drifts UTC
    # seasonally (13:00 UTC during MDT, 14:00 UTC during MST). Per
    # spec § Scheduling and the Session 1228 TZ trap fix pattern.
    # Default queue is fine: this task is low-frequency (1×/day) and
    # the workflow itself routes individual agent dispatches.
    #
    # Session 1258 PR 3.3 — beat row task field flipped from the
    # legacy ``core.tasks.generate_morning_brief_daily`` to the
    # MissionRunner-backed ``chief_of_staff_morning_brief_run``.
    # Cadence + queue + row name unchanged. Legacy task body deleted
    # from core/tasks.py in the same PR. Workflow internals unchanged
    # (wrap-as-single-step via MissionRunner per PR 3.2 contract).
    'generate-morning-brief-daily': {
        'task': 'chief_of_staff_morning_brief_run',
        'schedule': crontab(hour=7, minute=0),  # 7:00 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },

    # Cycle 1A KFI-4 (ADR-0140 §2.1 (1)) — the legacy
    # ``refresh-docs-corpus-daily`` static beat_schedule entry was
    # removed as part of KFI-4. Scheduled invocation of the docs
    # cascade moved to ``rigby_documentation_manager_daily`` (DB
    # PeriodicTask seeded by migration 0372, fires daily at 12:30 UTC
    # via the MissionRunner path with hash-delta preflight). The
    # underlying ``core.tasks.refresh_docs_corpus`` function is
    # preserved as a callable-only compatibility API (see the
    # docstring on that function for details). Migration 0378 drops
    # the DB PeriodicTask row that mirrored this entry.

    # ────────────────────────────────────────────────────────────────────────
    # Session 1115 batch-3 — DB hygiene + metrics tasks that were defined but
    # never wired. All entries below are safe by inspection:
    #   - no LLM/embedding calls (Chris is out of OpenAI credits)
    #   - no agent dispatch (per agent noise rule)
    #   - pure database hygiene, telemetry, or metric computation
    # Behavior-changing tasks (auto_approve_*, auto_promote_*, run_ops_autopilot,
    # post_ops_digest, send_weekly_kpi_summary, rag_retrieval_canary) are
    # deferred for explicit green-light — see AUDIT_FINDINGS.md #12.
    # ────────────────────────────────────────────────────────────────────────

    # Expire old opportunities past their relevance window
    'expire-old-opportunities': {
        'task': 'core.tasks.expire_old_opportunities',
        'schedule': crontab(hour=2, minute=30),  # 2:30 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Mark old pending suggestions as expired
    'expire-old-suggestions': {
        'task': 'core.tasks.expire_old_suggestions',
        'schedule': crontab(hour=2, minute=45),  # 2:45 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # HITL validations past deadline → expired (docstring: "Every hour")
    'expire-overdue-validations': {
        'task': 'core.tasks.expire_overdue_validations',
        'schedule': crontab(minute=0),  # Top of every hour
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Reclaim Redis-stream events stuck in consumer groups (docstring: "Every 5 minutes")
    'claim-stale-events': {
        'task': 'core.tasks.claim_stale_events',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'default', 'expires': 300},
    },
    # Cleanup auto-generated Discussion-prefixed conversation artifacts
    'cleanup-automated-conversation-artifacts': {
        'task': 'core.tasks.cleanup_automated_conversation_artifacts',
        # Session 1165 (COO #3): staggered 3:00 → 3:05 (hour 3 :00 cluster relief)
        'schedule': crontab(hour=3, minute=5),
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Cleanup boardroom items past retention (default 7 days)
    'cleanup-expired-boardroom-items': {
        'task': 'core.tasks.cleanup_expired_boardroom_items',
        'schedule': crontab(hour=3, minute=15),  # 3:15 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Cleanup halted experiments past retention
    'cleanup-halted-experiments': {
        'task': 'core.tasks.cleanup_halted_experiments',
        'schedule': crontab(hour=3, minute=30),  # 3:30 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Session 1195 — Plan C Phase 1 (Initiatives-First Backbone).
    # Archive TTL-expired diagnostic deliverables flagged by the
    # factory/update hooks (PRs #2403/#2404). Non-destructive: flips
    # canonical Deliverable.status='archived' and augments
    # diagnostic_payload with archived_by/reason/at; preserves all
    # diagnostic_* fields for attribution rollups. Staggered after
    # the 3:30 cleanup-halted-experiments to land in the 3:00 maintenance
    # cluster. Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C.
    'sweep-diagnostic-deliverables': {
        'task': 'core.tasks.sweep_diagnostic_deliverables',
        'schedule': crontab(hour=3, minute=45),  # 3:45 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Session 1196 — Plan C side-quest: archive TTL-expired diagnostic
    # Initiatives (those created without target_workspace_id and unfixed
    # for 7 days). Mirror of sweep-diagnostic-deliverables with the
    # Initiative-specific filter (diagnostic_code='missing_target_workspace_id'
    # + exclude status__in=['ARCHIVED','COMPLETED']). Staggered 10 min
    # after the deliverable sweep so they don't compete for the default
    # queue worker. Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C.
    'sweep-diagnostic-initiatives': {
        'task': 'core.tasks.sweep_diagnostic_initiatives',
        'schedule': crontab(hour=3, minute=55),  # 3:55 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Cleanup stale scoring requests (high-frequency queue hygiene)
    'cleanup-stale-scoring-requests': {
        'task': 'core.tasks.cleanup_stale_scoring_requests',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'default', 'expires': 1800},
    },
    # Reap zombie deliberation + pilot work
    'reap-zombie-work': {
        'task': 'core.tasks.reap_zombie_work',
        'schedule': crontab(minute=15),  # 15 min past every hour
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Mark due scheduled notifications as delivered (in-app only, no email)
    'send-pending-notifications': {
        'task': 'core.tasks.send_pending_notifications',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'default', 'expires': 300},
    },
    # Daily SLO check: learning loop usage_rate >= 5% over 24h (read-only)
    'check-learning-loop-slo': {
        'task': 'core.check_learning_loop_slo',
        'schedule': crontab(hour=9, minute=0),  # 9 AM Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Hourly LLM cost-spike detector (read-only aggregate on LLMCallLog)
    'check-llm-cost-spike': {
        'task': 'core.tasks.check_llm_cost_spike',
        'schedule': crontab(minute=5),  # 5 min past every hour
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Daily ROI metrics aggregation (docstring: "every day at 2:00 AM")
    'aggregate-roi-metrics-daily': {
        'task': 'core.tasks.aggregate_roi_metrics_daily',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM Denver
        'options': {'queue': 'default', 'expires': 7200},
    },
    # Daily revenue metrics (docstring: "Runs daily at midnight")
    'calculate-daily-revenue-metrics': {
        'task': 'intelligence.tasks.calculate_daily_revenue_metrics',
        'schedule': crontab(hour=0, minute=15),  # 12:15 AM Denver
        'options': {'queue': 'default', 'expires': 7200},
    },

    # ────────────────────────────────────────────────────────────────────────
    # Session 1115 batch-4 — behavior-changing DB tasks that were defined but
    # never wired. All entries below were verified by inspection to:
    #   - make NO LLM/embedding calls (Chris is out of OpenAI credits)
    #   - dispatch NO agents (per agent noise rule)
    #   - perform only DB queryset updates, file reads, or in-app state changes
    # These are "behavior-changing" only in that they update DB state (auto-
    # approve, auto-promote, archive, etc.) — not in that they call external
    # services or burn credits.
    #
    # Deferred for separate green-light:
    #   - run_ops_autopilot, post_ops_digest, send_weekly_kpi_summary (Discord/external)
    #   - rag_retrieval_canary, maintain_knowledge_freshness (OpenAI cost)
    #   - check_blocked_research_for_unblock, process_pending_action_plans (chain into agent dispatch)
    #   - discover_and_import_audits, assign_open_findings_to_agents (Session 1031 blocked)
    # ────────────────────────────────────────────────────────────────────────

    # Auto-approve low-risk HumanAttentionItems + auto-promote experiment/pipeline decisions
    'auto-approve-boardroom-items': {
        'task': 'core.tasks.auto_approve_boardroom_items',
        'schedule': crontab(minute='*/30'),  # Every 30 min
        'options': {'queue': 'default', 'expires': 1800},
    },
    # Auto-promote tier-1 (low-risk) AgentDecisionSummary rows after aging window
    'auto-promote-low-risk-decisions': {
        'task': 'core.tasks.auto_promote_low_risk_decisions',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
        'options': {'queue': 'default', 'expires': 7200},
    },
    # Verify completed audit fixes (file existence + regex checks; no subprocess)
    'verify-completed-fixes': {
        'task': 'core.tasks.verify_completed_fixes',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'options': {'queue': 'default', 'expires': 21600},
    },
    # Weekly: promote high-confidence AgentKnowledgeSource → SharedKnowledge
    # Session 1165 (COO #3): staggered 4:00 → 4:52 (Mon-only; end of hour 4)
    'promote-to-shared-knowledge': {
        'task': 'core.tasks.promote_to_shared_knowledge',
        'schedule': crontab(hour=4, minute=52, day_of_week='monday'),  # Mon 04:52 Denver (staggered)
        'options': {'queue': 'default', 'expires': 7200},
    },
    # Daily ContentDistribution analytics aggregation
    'update-distribution-analytics': {
        'task': 'core.tasks.update_distribution_analytics',
        'schedule': crontab(hour=4, minute=0),  # 04:00 Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Daily document namespace isolation progress snapshot
    'monitor-isolation-progress': {
        'task': 'core.tasks.monitor_isolation_progress',
        # Session 1165 (COO #3): staggered 4:30 → 4:48 (hour 4 :30 cluster relief)
        'schedule': crontab(hour=4, minute=48),
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Daily MythPattern frequency rollup (docstring: "Runs daily at 4am")
    'update-mythology-pattern-statistics': {
        'task': 'core.tasks.update_mythology_pattern_statistics',
        # Session 1165 (COO #3): staggered 4:00 → 4:20
        'schedule': crontab(hour=4, minute=20),
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Sync style/voice performance insights to collective intelligence (docstring: "every 6 hours")
    'sync-pipeline-insights-to-collective': {
        'task': 'core.tasks.sync_pipeline_insights_to_collective',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'options': {'queue': 'default', 'expires': 21600},
    },
    # HITL escalations: bump priority, extend deadlines, unassign (docstring: "Every 15 minutes")
    'process-hitl-escalations': {
        'task': 'core.tasks.process_hitl_escalations',
        'schedule': crontab(minute='*/15'),
        'options': {'queue': 'default', 'expires': 900},
    },
    # Scan TrackedConcerns + create action-required ProactiveNotifications
    'scan-concerns-for-human-action': {
        'task': 'core.tasks.scan_concerns_for_human_action',
        'schedule': crontab(minute=30),  # 30 min past every hour
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Archive low-score AgentDreams (composite_score < 0.3 after 7d, < 0.5 after 14d)
    'maintain-dream-backlog': {
        'task': 'core.tasks.maintain_dream_backlog',
        # Session 1165 (COO #3): staggered 4:30 → 4:42
        'schedule': crontab(hour=4, minute=42),
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Daily pending-review metrics log (Session 589)
    'report-pending-review-metrics': {
        'task': 'core.tasks.report_pending_review_metrics',
        'schedule': crontab(hour=9, minute=0),  # 09:00 Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # HumanAttentionItem lifecycle: expire, auto-dismiss, auto-escalate, auto-approve
    # (docstring: "Every 10 minutes")
    'process-human-attention-lifecycle': {
        'task': 'core.tasks.process_human_attention_lifecycle',
        'schedule': crontab(minute='*/10'),
        'options': {'queue': 'default', 'expires': 600},
    },
    # Poll Replicate for pending 3D model status (no-op when no pending)
    'poll-pending-3d-models': {
        'task': 'core.tasks.poll_pending_3d_models',
        'schedule': crontab(minute='*/5'),
        'options': {'queue': 'default', 'expires': 300},
    },
    # Daily duplicate-initiative detection (similarity-based; no LLM)
    'detect-duplicate-initiatives': {
        'task': 'core.tasks.detect_duplicate_initiatives',
        # Session 1165 (COO #3): staggered 4:15 → 4:18 (isolate DB-scan from llm-call-logs)
        'schedule': crontab(hour=4, minute=18),
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Operating rhythm health check (read-only) — Session 914.7
    'check-operating-rhythm-status': {
        'task': 'core.tasks.check_operating_rhythm_status',
        'schedule': crontab(hour=9, minute=15),  # 09:15 Denver
        'options': {'queue': 'default', 'expires': 3600},
    },
    # Rescan active workspaces with stale WorkspaceContext (Session 1055)
    'rescan-active-workspaces': {
        'task': 'core.tasks.rescan_active_workspaces',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'options': {'queue': 'default', 'expires': 14400},
    },

    # ────────────────────────────────────────────────────────────────────────
    # Session 1115 batch-6 — "truly forgotten" task that was clearly designed
    # to be scheduled. Docstring says: "Should run every hour to gather
    # opportunities from multiple sources." Uses spiders (no LLM); discovers
    # opportunities and saves them to DB.
    # ────────────────────────────────────────────────────────────────────────
    'scan-income-spider-orchestrator': {
        'task': 'intelligence.tasks.scan_income_spider_orchestrator',
        'schedule': crontab(minute=10),  # 10 min past every hour
        'options': {'queue': 'long_running', 'expires': 3600},
    },

    # ────────────────────────────────────────────────────────────────────────
    # Session 1205 — Sports + market intelligence producers (Capability Audit
    # finding 6869fa55). All 7 sports-betting agents were classified DEAD on
    # the Layer 1 dashboard (zero 30d invocations). Deep-dive revealed they
    # are wired and code-functional but their producer beat tasks were never
    # scheduled. `_impl_market_intelligence_scan` docstring even claimed
    # "Scheduled to run every 2 hours" but no PeriodicTask row existed.
    # These 4 entries materialize the missing trigger surface.
    #
    # Operator directive (Session 1205): production rollout is gated on
    # "everything connected first" — these fire on LOCAL too so we can
    # verify the producer→consumer chain works end-to-end before
    # promoting to Railway. NOT in LOCAL_DENY_TASKS. If local cost
    # becomes a concern, add them to LOCAL_DENY_TASKS in
    # add_critical_celery_tasks.py later.
    # ────────────────────────────────────────────────────────────────────────
    'market-intelligence-scan': {
        'task': 'core.tasks.market_intelligence_scan',
        'schedule': crontab(minute=0, hour='*/2'),  # every 2h on the hour
        'options': {'queue': 'long_running', 'expires': 7200},
    },
    'generate-daily-betting-brief': {
        'task': 'core.tasks.generate_daily_betting_brief',
        'schedule': crontab(hour=7, minute=0),  # 7:00 AM MT daily — MLB Run Line Desk spec 46332cee
        'options': {'queue': 'default', 'expires': 3600},
    },
    'collect-sports-odds-intelligence': {
        'task': 'core.tasks.collect_sports_odds_intelligence',
        'schedule': crontab(minute='*/30'),  # every 30 min — keep theodds snapshot fresh
        'options': {'queue': 'long_running', 'expires': 1800},
    },
    'collect-kalshi-prediction-markets': {
        'task': 'core.tasks.collect_kalshi_prediction_markets',
        'schedule': crontab(minute=15),  # every hour at :15 — offset from sports odds
        'options': {'queue': 'long_running', 'expires': 3600},
    },

    # ── Cost Protection (Session 2735 P1) ──────────────────────────────────
    # Rolling hour/day/month spend check against CostTracking. Monitor-only
    # at ship: if any window breaches its configured SystemConfiguration
    # threshold, dispatches an HAI(source_type='cost_breach', urgency=
    # 'critical'). Enforcement (auto governance.set_mode('freeze')) is
    # DELIBERATELY not implemented in this release per Chris's enforcement-
    # gate discipline (requires monitor observation period + explicit
    # approval before freeze becomes active).
    'check-cost-thresholds': {
        'task': 'check_cost_thresholds',
        'schedule': crontab(minute='*/15'),
        'options': {'queue': 'default', 'expires': 900},
    },

    # ── Beat Schedule Health (Session 2735 Beat Health Campaign P1) ────────
    # Compare app.conf.beat_schedule allowlisted entries against observed
    # CeleryTaskEvent fires over lookback_days. If any allowlisted beat
    # entry failed the min_expected_fires threshold, dispatch a single
    # consolidated HAI(source_type='beat_health', urgency='critical').
    # Allowlist starter set: heart-service-heartbeat, check-celery-health,
    # monitor-celery-health. Runtime-tunable via SystemConfiguration
    # (beat_health_allowlist as JSON list).
    'check-beat-health': {
        'task': 'check_beat_health',
        'schedule': crontab(hour=1, minute=17),
        'options': {'queue': 'default', 'expires': 3600},
    },
    # S2759 stale-process detection. Fires every 30 min to catch the
    # 3-incident stale-Daphne class regression (S2755/S2756/S2757 view-layer
    # merges silently ran pre-merge code for hours). Complements the live
    # `ops_tool.version` staleness verdict — this is the passive "nobody
    # remembered to check" defense in depth. Emits an OpsRunEvent with
    # label='staleness_warning' when verdict != FRESH.
    'check-process-staleness': {
        'task': 'check_process_staleness',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'default', 'expires': 1800},
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
#
# Session 1115: added four more app tasks modules to close the broken-beat-refs
# finding (AUDIT_FINDINGS.md #3). All four files were registered in INSTALLED_APPS
# with `@shared_task` decorated functions that beat_schedule references, but
# autodiscover_tasks() wasn't picking them up reliably at worker boot. As a
# result, seven scheduled tasks were firing into a registry that had no handler
# and silently no-op'ing — see docs/BEAT_AUDIT.md and docs/CELERY_AUDIT.md.
#
# Re-enabling these makes the following schedules go live:
#   `clean-stale-data`           (daily 02:00) — DB cleanup, low risk
#   `cleanup-old-model-files`    (Mon 01:00)   — file cleanup, low risk
#   `cleanup-old-predictions`    (Mon 03:00)   — DB cleanup, low risk
#   `cleanup-opportunities-daily`(daily 03:00) — DB cleanup, low risk
#   `collect-real-opportunities` (every 30m)   — ACTIVE WORK: external job
#                                                scrapes + writes ActionPlan rows
#   `scan-spider-opportunities`  (every 30m)   — ACTIVE WORK: scans cached
#                                                spider data, creates opportunities
#   `warm-up-spiders`            (every 6h)    — ACTIVE WORK: spider connection
#                                                warming, lightweight HTTP probes
app.conf.imports = (
    'core.tasks_agents',
    'ai_core.tasks',
    'ml.tasks',
    'sports.tasks',
    'intelligence.tasks',
    # Session 1250 PR 5: ensure rigby_event_intake is registered at
    # worker boot so apply_async / .delay calls from signal handlers
    # resolve. Subscriber is gated by settings.RIGBY_EVENT_INTAKE_ENABLED
    # (default False); this import only registers the task name, it
    # does not enqueue anything.
    'core.services.rigby_event_intake',
    # Session 1253 hotfix: PR #2730 added the Documentation Manager
    # `@shared_task rigby_documentation_manager_daily` in a non-standard
    # tasks_documentation_manager.py module. The S1252 cutover verified
    # the cascade through the management command (in-process import) but
    # never exercised the worker dispatch path — so when the first beat
    # fire at 2026-06-29 06:30 MDT sent the task message, the default
    # worker rejected it with `KeyError: 'rigby_documentation_manager_daily'`.
    # Adding the module here ensures the worker imports it at boot and
    # registers the task name in the registry.
    'core.tasks_documentation_manager',
    # Session 1257 PR 2.2: Platform Auditor task. Same lesson as the
    # docs-manager hotfix above — the `@shared_task platform_auditor_run`
    # in a non-standard `tasks_platform_audit.py` module needs to be
    # explicitly listed so worker dispatch resolves the task name on
    # the first beat fire (PR 2.3) + on manual `run_now` dispatches
    # via the PA tool.
    'core.tasks_platform_audit',
    # Session 1257 PR 3.2: Chief of Staff Morning Brief task. Same
    # lesson — `@shared_task chief_of_staff_morning_brief_run` in a
    # non-standard `tasks_chief_of_staff.py` module needs explicit
    # listing here so worker dispatch resolves the task name on
    # manual `run_now` dispatches via the PA tool. The future beat
    # row task-name flip (legacy `generate-morning-brief-daily` →
    # `chief_of_staff_morning_brief_run`) lands in PR 3.3; until
    # then the legacy task keeps firing from beat and this task is
    # callable only via run_now / Celery shell.
    'core.tasks_chief_of_staff',
    # Session 1267 PR 4.2: Bug Triage Specialist task. Same lesson —
    # `@shared_task bug_triage_daily_run` in a non-standard
    # `tasks_bug_triage.py` module needs explicit listing here so
    # worker dispatch resolves the task name on the first beat fire
    # (PR 4.3) + on manual `run_now` dispatches via the PA tool.
    'core.tasks_bug_triage',
    # Session 2735 Cost Protection Campaign P1: check_cost_thresholds
    # beat task in tasks_cost_protection.py. Same lesson — non-standard
    # module needs explicit listing so worker dispatch resolves the
    # task name on beat fires + manual run_now dispatches. Task is
    # monitor-only at ship; will never call governance.set_mode('freeze')
    # regardless of cost_protection_enforce_mode config value.
    'core.tasks_cost_protection',
    # Session 2735 Beat Schedule Health Campaign P1: check_beat_health
    # beat task in tasks_beat_health.py. Same lesson — non-standard
    # module needs explicit listing so worker dispatch resolves the
    # task name on beat fires + manual run_now dispatches. Task is
    # monitor-only (no auto-remediation, no restart, no reschedule).
    'core.tasks_beat_health',
    # Session 2737 — HAI push notifications module. Discovered post-
    # recycle during §16 wrap-up bundle close: `core.tasks_push_notifications`
    # was not loaded at worker boot because the four signal modules
    # (signals_push_notifications, signals_discord_notifications,
    # signals_webpush_notifications, signals_inbox_notifications) all
    # import from it *inside function bodies* (lazy `from core.tasks_push_notifications import ...`
    # at the enqueue helpers). The `@shared_task` decorators therefore
    # never fired at boot, so `notify_hai_discord.delay(...)` /
    # `notify_hai_webpush.delay(...)` / `notify_critical_attention_item.delay(...)`
    # / `notify_needs_classification.delay(...)` / `notify_hai_inbox.delay(...)`
    # all failed silent-KeyError on the running worker.
    #
    # Ships fix for all five task names at once — closes the same-class-
    # bug in PR #1458 (Expo, 2026-02-24), PR #3038 (Discord, 2026-07-09
    # S2735), PR #3040 (Web Push, 2026-07-09 S2735), and PR #3050 (Inbox,
    # 2026-07-09 S2737).
    'core.tasks_push_notifications',
    # S3003 T-VIP-1 — VIP invite lifecycle cleanup (backstop for
    # middleware enforcement of VIPInvite.account_expires_at). Same
    # lesson as the docs-manager / platform-audit / bug-triage entries
    # above — non-standard `tasks_vip.py` needs explicit listing so
    # worker dispatch resolves the task name on beat fires.
    'core.tasks_vip',
)


@app.on_after_finalize.connect
def _eager_import_session1115_modules(sender, **kwargs):
    """Force-import task modules that `autodiscover_tasks()` doesn't always
    pick up before the registry is read.

    Session 1115: the build_celery_audit + beat_schedule_task_refs_resolve
    verifier read `app.tasks` at app-finalize time, which is before any
    worker boot. Without this eager-import hook, the four extra modules
    listed in `app.conf.imports` only get imported when a worker actually
    starts — and the audit/verifier flags 7 beat refs as broken even
    though `app.conf.imports` would have eventually loaded them.

    Hooking into `on_after_finalize` (fired exactly once when the Celery
    app is fully configured, AFTER Django apps are loaded) gives us a
    deterministic moment to trigger the imports. The `import` side-effect
    registers each module's `@shared_task` functions in the global
    registry.
    """
    import importlib
    # Session 1115 set: ai_core/ml/sports/intelligence.
    # Session 1253 hotfix: + core.tasks_documentation_manager so the
    # docs-manager `@shared_task` registers at finalize time too (not
    # just at worker boot). Without this, `verify_doc_claims` /
    # build_celery_audit reading `app.tasks` early can miss the task.
    eager_modules = (
        'ai_core.tasks',
        'ml.tasks',
        'sports.tasks',
        'intelligence.tasks',
        'core.tasks_documentation_manager',
        # Session 1257 PR 2.2: Platform Auditor task — same lesson as
        # docs-manager. Forces the @shared_task to register at finalize
        # time so app.tasks reads (build_celery_audit / verify_doc_claims
        # / queue parity tests) see it without waiting for worker boot.
        'core.tasks_platform_audit',
        # Session 1257 PR 3.2: Chief of Staff Morning Brief task — same
        # lesson. Forces the @shared_task to register at finalize time
        # so `chief_of_staff_morning_brief_run` shows up in app.tasks
        # without waiting for worker boot.
        'core.tasks_chief_of_staff',
        # Session 1267 PR 4.2: Bug Triage Specialist task — same
        # lesson. Forces the @shared_task to register at finalize time
        # so `bug_triage_daily_run` shows up in app.tasks without
        # waiting for worker boot.
        'core.tasks_bug_triage',
        # S3003 T-VIP-1: VIP cleanup task — same lesson. Forces
        # `cleanup_expired_vip_users` into app.tasks at finalize time
        # so build_celery_audit / beat_schedule_task_refs_resolve see it.
        'core.tasks_vip',
    )
    for mod in eager_modules:
        try:
            importlib.import_module(mod)
        except Exception as e:
            logger.warning(f"Eager-import of {mod} failed: {e}")


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
