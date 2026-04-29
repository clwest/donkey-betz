"""Backfill Celery tasks.

Migrated out of `core.tasks` in Phase 3 of the Wave B refactor. Every
task here keeps the registered Celery name it had in `core.tasks`
(locked by the explicit `name=` kwarg from Phase 1), so beat schedule
entries, PeriodicTask DB rows, settings.py task-routing config, the
`add_critical_celery_tasks` management-cmd string dispatch, the
ops-autopilot budget cost dict, and string-dispatched callers in
`core/services/td_handlers_gateway.py` continue to resolve unchanged.

Tasks (data backfill / coverage):

- backfill_spider_embeddings        (registered: core.tasks.backfill_spider_embeddings, beat-scheduled, ml queue)
- backfill_signal_scores            (registered: backfill_signal_scores — non-standard, no prefix)
- backfill_memory_embeddings        (registered: core.tasks.backfill_memory_embeddings, ml queue)
- backfill_conversation_embeddings  (registered: core.tasks.backfill_conversation_embeddings, ml queue)
- backfill_voice_scores             (registered: content_studio.backfill_voice_scores — non-standard namespace)
- backfill_stage_documents          (registered: core.tasks.backfill_stage_documents, long_running queue)
- backfill_deliverable_workspaces   (registered: core.tasks.backfill_deliverable_workspaces, long_running queue, custom time limits)

No private helpers move with these tasks — substantive bodies use only
inline imports, thin wrappers delegate to `core.tasks_misc._impl_*`.
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True, name="core.tasks.backfill_spider_embeddings")
def backfill_spider_embeddings(batch_size: int = 50):
    """
    Session 293: Generate embeddings for SpiderData entries that don't have them.
    Session 394: Increased default batch size from 50 to 200 for faster processing.
    Session 1083 (Rigby audit): Reduced 200→50 after observing 1.37GB memory
    spike per run in celery telemetry (start=669MB → end=2042MB). Combined
    with the .only() column filter in spider_semantic_search.backfill_embeddings,
    this should keep the task's RSS delta under 300MB.
    Apr 2026: Removed hours=168 window — triage_spider_embeddings deduped the
    historical backlog so all remaining unembedded records are worth processing.

    Runs every 15 minutes via Celery Beat to gradually build embedding coverage.
    Uses the SpiderSemanticSearch service.

    Now also marks entries with no items as 'empty' so they're skipped in future runs.
    """
    logger.info("🧠 Starting spider embedding backfill...")

    try:
        from core.services.spider_semantic_search import get_spider_semantic_search

        search = get_spider_semantic_search()
        stats = search.backfill_embeddings(batch_size=batch_size)

        logger.info(
            f"✅ Embedding backfill complete: "
            f"{stats['processed']} processed, {stats['succeeded']} succeeded, "
            f"{stats['failed']} failed, {stats['skipped']} skipped, "
            f"{stats.get('marked_empty', 0)} marked empty"
        )

        # Get current coverage stats
        coverage = search.get_embedding_stats()
        logger.info(
            f"📊 Embedding stats: {coverage['searchable']} searchable, "
            f"{coverage.get('marked_empty', 0)} empty, {coverage.get('pending', 0)} pending "
            f"({coverage['coverage_percent']:.1f}% coverage)"
        )

        return {
            'success': True,
            'batch_stats': stats,
            'coverage': coverage
        }

    except Exception as e:
        logger.error(f"❌ Embedding backfill failed: {e}")
        return {'success': False, 'error': str(e)}

@shared_task(name='backfill_signal_scores')
def backfill_signal_scores():
    """Session 1025: Score all existing SignalClusters that have default scores."""
    from core.models_signal_intelligence import SignalCluster
    from core.services.content_scoring_service import ContentScoringService

    scorer = ContentScoringService()
    clusters = SignalCluster.objects.filter(reach_score=0.0, intent_score=0.0)
    updated = 0
    for cluster in clusters.iterator():
        scores = scorer.score_cluster(cluster)
        for field, value in scores.items():
            setattr(cluster, field, value)
        cluster.save(update_fields=list(scores.keys()))
        updated += 1
    logger.info(f"Scored {updated} signal clusters")
    return f"Scored {updated} clusters"

@shared_task(bind=True, name='core.tasks.backfill_memory_embeddings')
def backfill_memory_embeddings(self, batch_size: int = 50):
    """
    Session 490: Backfill embeddings for memories that don't have them.

    Runs periodically to ensure all memories have embeddings for semantic search.
    """
    logger.info(f"🧠 [MEMORY BACKFILL] Starting backfill (batch_size={batch_size})")

    try:
        from core.services.memory_embedding_service import get_memory_embedding_service

        service = get_memory_embedding_service()
        stats = service.backfill_embeddings(batch_size=batch_size)

        logger.info(
            f"🧠 [MEMORY BACKFILL] Completed: "
            f"{stats['succeeded']}/{stats['processed']} succeeded"
        )

        return {
            'status': 'completed',
            'processed': stats['processed'],
            'succeeded': stats['succeeded'],
            'failed': stats['failed']
        }

    except Exception as e:
        logger.error(f"🧠 [MEMORY BACKFILL] Error: {e}")
        return {'status': 'error', 'error': str(e)}

@shared_task(bind=True, name='core.tasks.backfill_conversation_embeddings')
def backfill_conversation_embeddings(self, batch_size: int = 50):
    from core.tasks_misc import _impl_backfill_conversation_embeddings
    return _impl_backfill_conversation_embeddings(self, batch_size)

@shared_task(name='content_studio.backfill_voice_scores')
def backfill_voice_scores(limit: int = 50, min_content_length: int = 100) -> dict:
    from core.tasks_misc import _impl_backfill_voice_scores
    return _impl_backfill_voice_scores(limit, min_content_length)

@shared_task(bind=True, queue='default', name="core.tasks.backfill_stage_documents")
def backfill_stage_documents(self, stage_num: int = 1, limit: int = 50):
    from core.tasks_misc import _impl_backfill_stage_documents
    return _impl_backfill_stage_documents(self, stage_num, limit)

@shared_task(
    name='core.tasks.backfill_deliverable_workspaces',
    ignore_result=False,
    queue='long_running',
    soft_time_limit=300,
    time_limit=360,
)
def backfill_deliverable_workspaces(workspace_name='Donkey Betz',
                                    username=None,
                                    include_archived=False,
                                    dry_run=False):
    """Backfill workspace_id on deliverables where it is NULL.

    Triggerable by PA via cockpit_tool.trigger_task.
    """
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    args = ['backfill_deliverable_workspaces', '--workspace', workspace_name]
    if username:
        args.extend(['--username', username])
    if include_archived:
        args.append('--include-archived')
    if dry_run:
        args.append('--dry-run')

    call_command(*args, stdout=out)
    output = out.getvalue()
    logger.info('[BACKFILL_WORKSPACES] %s', output)
    return {'output': output}

