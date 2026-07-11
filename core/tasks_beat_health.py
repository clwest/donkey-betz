"""
Beat Health Celery task — Session 2735, Beat Schedule Health Campaign P1.

One beat task, ``check_beat_health``, that runs
``beat_health_monitor.compute_snapshot`` once per day and dispatches a
single consolidated HAI when any allowlisted beat entry failed the
minimum-expected-fires threshold. **Monitor-only** — no auto-remediation
(no restart, no reschedule). If a beat regressed, a human decides how
to respond.

Cat A discipline: no new architecture. Uses:
- ``beat_health_monitor.compute_snapshot`` — the new read-only helper
- ``HumanAttentionBridge.create_beat_health_attention`` — 12th producer
  method on the pre-existing bridge
- HAI Delivery Fanout receivers (Discord + Web Push) shipped in prior
  campaign — automatically fan the ``critical`` HAI to those channels
- Existing ``@shared_task`` pattern + ``default`` queue
- Existing Celery beat schedule mechanism (registered in
  ``core/celery.py``)

Beat schedule: daily at ``crontab(hour=1, minute=17)``.
"""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name='check_beat_health',
    queue='default',
    ignore_result=True,
    soft_time_limit=60,
)
def check_beat_health():
    """Compute and dispatch beat-health snapshot.

    Returns a structured summary for observability. Never raises; the
    outer try/except swallows any unexpected error so a monitor failure
    does not silence itself via crashloop.
    """
    from core.services.beat_health_monitor import (
        compute_snapshot,
        enabled,
    )
    from core.services.human_attention_bridge import attention_bridge

    if not enabled():
        logger.info(
            '[BEAT_HEALTH] beat_health_enabled=false; skipping tick'
        )
        return {'skipped': 'kill_switch'}

    try:
        snapshot = compute_snapshot()
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[BEAT_HEALTH] compute_snapshot failed (%s: %s); '
            'skipping this tick',
            type(e).__name__, e,
        )
        return {'skipped': f'compute_error:{type(e).__name__}'}

    logger.info(
        '[BEAT_HEALTH] lookback=%dd min_fires=%d allowlist=%d checked=%d '
        'missing=%d',
        snapshot.lookback_days,
        snapshot.min_expected_fires,
        snapshot.allowlist_size,
        snapshot.checked,
        snapshot.missing_count,
    )

    hai_dispatched = 0
    if snapshot.any_missing:
        try:
            attention_bridge.create_beat_health_attention(snapshot)
            hai_dispatched = 1
        except Exception as e:  # pragma: no cover — defensive
            logger.warning(
                '[BEAT_HEALTH] bridge dispatch failed (%s: %s); '
                'HAI not created for this tick',
                type(e).__name__, e,
            )

    return {
        'lookback_days': snapshot.lookback_days,
        'min_expected_fires': snapshot.min_expected_fires,
        'allowlist_size': snapshot.allowlist_size,
        'checked': snapshot.checked,
        'missing_count': snapshot.missing_count,
        'hai_dispatched': hai_dispatched,
        'missing': [
            {
                'beat_entry_name': mb.beat_entry_name,
                'task_name': mb.task_name,
                'observed_count': mb.observed_count,
                'expected_min': mb.expected_min,
            }
            for mb in snapshot.missing
        ],
    }


# --------------------------------------------------------------------------
# S2759: Stale-process detection (Daphne / Celery vs git HEAD commit time)
# --------------------------------------------------------------------------


@shared_task(
    name='check_process_staleness',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
)
def check_process_staleness():
    """Detect Daphne / Celery worker processes older than the current git HEAD.

    Beat-scheduled at 30 min per Rigby SIGN F3 QE. Complements the live
    ``ops_tool.version`` staleness surface — this task is the "nobody
    remembered to check" defense in depth. If any process is older than
    the HEAD commit, emits an ``OpsRunEvent`` with ``label='staleness_warning'``
    carrying the same verdict + process detail returned by
    ``ops_tool.version``. Never raises; monitor-failure-must-not-crashloop.

    Introduced to codify the 3-incident stale-Daphne class regression
    that silently affected S2755 / S2756 / S2757 view-layer merges. See
    ``feedback_local_truth_no_production`` memory rule + S2759 ratification
    envelope.
    """
    try:
        from core.services.td_handlers_ops import OpsHandlersMixin
    except ImportError:
        logger.warning(
            '[STALENESS] OpsHandlersMixin import failed; skipping tick'
        )
        return {'skipped': 'import_failed'}

    try:
        # Instantiate a lightweight proxy since the helper is a bound
        # method (needs `self`) but doesn't touch instance state.
        class _Proxy:
            _compute_process_staleness = (
                OpsHandlersMixin._compute_process_staleness
            )
            _DAPHNE_PROCESS_PATTERN = (
                OpsHandlersMixin._DAPHNE_PROCESS_PATTERN
            )
            _CELERY_WORKER_PROCESS_PATTERN = (
                OpsHandlersMixin._CELERY_WORKER_PROCESS_PATTERN
            )
        result = _Proxy()._compute_process_staleness()
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[STALENESS] compute_process_staleness failed (%s: %s); '
            'skipping this tick',
            type(e).__name__, e,
        )
        return {'skipped': f'compute_error:{type(e).__name__}'}

    verdict = result.get('staleness_verdict', 'UNKNOWN')

    logger.info(
        '[STALENESS] verdict=%s daphne_pid=%s celery_workers=%d head_commit=%s',
        verdict,
        result.get('daphne_pid'),
        len(result.get('celery_workers_status', [])),
        result.get('head_commit_sha', 'unknown')[:12],
    )

    if verdict in ('FRESH', 'UNKNOWN'):
        return {'verdict': verdict}

    # Stale — emit an OpsRunEvent envelope. Rigby / Chris can query the
    # accumulated warnings via ops_tool.tenant_boundary_violations pattern
    # or by direct OpsRunEvent read.
    try:
        from core.models_ops_runs import OpsRunEvent
        from core.security.error_envelope import _get_or_create_rur_failure_run

        run = _get_or_create_rur_failure_run()
        OpsRunEvent.objects.create(
            run=run,
            event_type='step_fail',
            label='staleness_warning',
            detail={
                'source': 'check_process_staleness_beat',
                'verdict': verdict,
                'head_commit_sha': result.get('head_commit_sha'),
                'head_commit_timestamp': result.get('head_commit_timestamp'),
                'daphne_pid': result.get('daphne_pid'),
                'daphne_pid_age_seconds': result.get('daphne_pid_age_seconds'),
                'daphne_started_before_head_commit': result.get(
                    'daphne_started_before_head_commit',
                ),
                'celery_workers_status': result.get('celery_workers_status', []),
                'fix': result.get('staleness_fix'),
            },
        )
        emitted = True
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[STALENESS] OpsRunEvent emission failed (%s: %s); logged only',
            type(e).__name__, e,
        )
        emitted = False

    return {
        'verdict': verdict,
        'ops_run_event_emitted': emitted,
        'head_commit_sha': result.get('head_commit_sha'),
    }
