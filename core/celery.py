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
    for mod in ('ai_core.tasks', 'ml.tasks', 'sports.tasks', 'intelligence.tasks'):
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
