"""
Worker failure cluster → HAI signals — Session 2734 (Platform Closure Category B).

Capability Chain §15 Item 14 wire-up: when Celery emits ``task_failure``
and ``core/celery_telemetry.py`` writes a ``CeleryTaskEvent`` with
``status='FAILURE'``, this post_save receiver runs the sliding-window
:class:`~core.services.failure_cluster_aggregator.FailureClusterSnapshot`
and — if the distinct-task-id count exceeds the configured threshold and
no open ``failure_cluster`` HAI exists for the same
``(task_name, urgency_band)`` in the last 30 minutes — dispatches
``HumanAttentionBridge.create_failure_cluster_attention`` on-commit.

Chain::

    Celery task_failure
      → CeleryTaskEvent(status='FAILURE') written by celery_telemetry
      → [this receiver, on_commit]
      → FailureClusterAggregator.compute_cluster(task_name)
      → threshold + dedup gates
      → HumanAttentionBridge.create_failure_cluster_attention(snapshot)
      → HumanInterfaceService.create_attention_item(source_type='failure_cluster')
      → HumanAttentionItem row → inbox

Filtering contract:
    * Only rows whose current ``status`` is ``'FAILURE'`` are considered
      — mirrors the audit §15 F.CELERY-TELEMETRY signature.
    * ``created=True`` is accepted (eager fallback path in
      ``celery_telemetry.on_task_failure`` line 209) as well as
      ``created=False`` transitions (STARTED→FAILURE update at
      ``celery_telemetry.on_task_failure`` line 203). Any other save
      (STARTED prerun, SUCCESS postrun, unrelated update) is filtered
      out by the ``status`` check.
    * Empty ``task_name`` rows are skipped so the aggregator's
      task-name-keyed query does not degenerate into a global scan.

Dedup contract:
    * Dedup key: ``(task_name, urgency_band)`` per Rigby SIGN
      ``pa-74ecac300bba4ab3`` Q3 refinement. Allows a previously-high
      cluster to still escalate to ``critical`` within the dedup window
      when the count crosses the critical threshold.
    * Window: 30 minutes (settings ``FAILURE_CLUSTER_DEDUP_MINUTES``,
      default 30). Compare §14 body-system 1h — clusters resolve fast
      or escalate; 30 min is the right cadence.
    * Fails safe: on any dedup-lookup exception, allow the escalation
      (safer to duplicate than to swallow a critical alert).

Kill switch:
    ``settings.FAILURE_CLUSTER_HAI_ENABLED`` (default True).
"""
from __future__ import annotations

import logging
from datetime import timedelta

from django.conf import settings
from django.db import models, transaction
from django.db.models.signals import post_save
from django.utils import timezone

logger = logging.getLogger(__name__)

_DEFAULT_DEDUP_MIN = 30


def _dedup_minutes() -> int:
    return int(getattr(settings, 'FAILURE_CLUSTER_DEDUP_MINUTES', _DEFAULT_DEDUP_MIN))


def _open_hai_exists(idempotency_key: str, task_name: str, urgency_band: str) -> bool:
    """True if an undecided ``failure_cluster`` HAI matching either the
    exact ``idempotency_key`` OR the same ``(task_name, urgency_band)``
    was created inside the dedup window.

    The two-key OR is deliberate: ``idempotency_key`` narrows a
    concurrency race where two near-simultaneous saves land in the same
    second (same window_start_ts, same band → same key); the
    ``(task_name, urgency_band)`` fallback catches drift when the
    aggregator's ``window_start`` moves by a few seconds across saves
    but the cluster is the same open incident (per Rigby SIGN
    ``pa-74ecac300bba4ab3`` post-implementation Q2 refinement — the
    race is narrow but real without a DB uniqueness constraint).

    Fails safe to ``False`` on any error so a broken lookup does NOT
    swallow a genuinely critical escalation.
    """
    try:
        from core.models_human_interface import HumanAttentionItem
        cutoff = timezone.now() - timedelta(minutes=_dedup_minutes())
        return HumanAttentionItem.objects.filter(
            source_type='failure_cluster',
            decided_at__isnull=True,
            created_at__gte=cutoff,
        ).filter(
            models.Q(payload__idempotency_key=idempotency_key)
            | models.Q(
                payload__task_name=task_name,
                payload__urgency_band=urgency_band,
            )
        ).exists()
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[FAILURE_CLUSTER] dedup lookup failed task_name=%s "
            "band=%s (%s: %s); allowing escalation",
            task_name, urgency_band, type(e).__name__, e,
        )
        return False


def _dispatch(snapshot):
    """Dispatch to the HumanAttentionBridge on-commit."""
    try:
        from core.services.human_attention_bridge import attention_bridge
        attention_bridge.create_failure_cluster_attention(snapshot)
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[FAILURE_CLUSTER] bridge dispatch failed task_name=%s "
            "(%s: %s)",
            getattr(snapshot, 'task_name', 'unknown'),
            type(e).__name__, e,
        )


def escalate_failure_cluster(sender, instance, created, **kwargs):
    """Post-save receiver on ``CeleryTaskEvent``.

    Escalates to HAI when:
      * kill switch is not tripped;
      * the row's current ``status`` is ``'FAILURE'``;
      * ``task_name`` is non-empty;
      * the sliding-window aggregator says the distinct-task-id count
        for this ``task_name`` meets the standard threshold;
      * no open ``failure_cluster`` HAI for the same
        ``(task_name, urgency_band)`` exists inside the dedup window.

    Escalation is scheduled via ``transaction.on_commit`` so a
    rolled-back CeleryTaskEvent produces no phantom HAI.
    """
    if not getattr(settings, 'FAILURE_CLUSTER_HAI_ENABLED', True):
        return
    status = getattr(instance, 'status', None) or ''
    if status != 'FAILURE':
        return
    task_name = getattr(instance, 'task_name', '') or ''
    if not task_name.strip():
        return

    try:
        from core.services.failure_cluster_aggregator import compute_cluster
        snapshot = compute_cluster(task_name)
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[FAILURE_CLUSTER] compute_cluster failed task_name=%s "
            "(%s: %s); skipping escalation",
            task_name, type(e).__name__, e,
        )
        return

    if not snapshot.exceeds_threshold:
        return
    if _open_hai_exists(
        snapshot.idempotency_key,
        snapshot.task_name,
        snapshot.urgency_band,
    ):
        logger.info(
            "[FAILURE_CLUSTER] dedup suppressed task_name=%s band=%s "
            "distinct=%d (open HAI already present in window)",
            snapshot.task_name, snapshot.urgency_band,
            snapshot.distinct_task_id_count,
        )
        return

    transaction.on_commit(lambda: _dispatch(snapshot))


def connect_failure_cluster_signals():
    """Wire the ``CeleryTaskEvent`` post_save receiver.

    Registered from ``core/apps.py::CoreConfig._register_signals`` at
    Django startup. Idempotent via ``dispatch_uid``.
    """
    from core.models_celery_telemetry import CeleryTaskEvent
    post_save.connect(
        escalate_failure_cluster,
        sender=CeleryTaskEvent,
        dispatch_uid=(
            "core.signals.failure_cluster_signals.escalate_failure_cluster"
        ),
    )
    logger.info(
        "[FAILURE_CLUSTER_SIGNALS] receiver wired on "
        "CeleryTaskEvent.post_save (dedup_window_min=%d)",
        _dedup_minutes(),
    )
