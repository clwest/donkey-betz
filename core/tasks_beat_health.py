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
