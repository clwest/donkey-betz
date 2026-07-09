"""
Failure Cluster Aggregator — Session 2734 (Platform Closure Category B).

Pure query helper for Capability Chain §15 Worker Failure Item 14. Given a
``task_name`` and a window duration, returns a snapshot of the current
failure cluster: distinct-task-id count, distinct queues/workers/error
types, and a small sample of the offending ``CeleryTaskEvent`` rows for
downstream HAI payload rendering.

Design notes
------------

* **Distinct-task-id count, not raw count.** Rigby SIGN
  ``pa-74ecac300bba4ab3`` Q2 refinement: retries + late updates can
  inflate raw counts. The cluster is meaningful only when N *distinct*
  Celery tasks failed for the same ``task_name``.

* **Read-only.** No side effects. Callers own dispatch, dedup, urgency
  policy, and idempotency-key composition.

* **Uses the ``celery_evt_name_time`` index** on
  ``(task_name, -started_at)`` per ``models_celery_telemetry.py:97``.
  Query filters on ``finished_at`` because that's when the FAILURE
  transition landed — but this still hits the compound index for the
  task_name-first branch and the small window keeps the scan cheap.

* **Idempotency key.** Returned in the snapshot as
  ``idempotency_key = 'failure_cluster:{task_name}:{window_start_ts}:{urgency}'``.
  Callers can attach it to the HAI payload for audit joins per Rigby
  SIGN refinement.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db.models import Count
from django.utils import timezone

logger = logging.getLogger(__name__)

_DEFAULT_THRESHOLD = 5
_DEFAULT_WINDOW_MIN = 5
_DEFAULT_CRITICAL_THRESHOLD = 15
_DEFAULT_SAMPLE_SIZE = 5

_THRESHOLD_KEY = 'failure_cluster_threshold'
_WINDOW_KEY = 'failure_cluster_window_minutes'
_CRITICAL_KEY = 'failure_cluster_critical_threshold'


def _read_int_config(key: str, default: int) -> int:
    """Read an integer SystemConfiguration value; fail safe to ``default``."""
    try:
        from core.models.system import SystemConfiguration
        entry = SystemConfiguration.objects.filter(
            key=key, is_active=True,
        ).values_list('value', flat=True).first()
        if entry is None or entry == '':
            return default
        return int(str(entry).strip())
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[FAILURE_CLUSTER_AGGREGATOR] config read failed key=%s "
            "(%s: %s); using default %d",
            key, type(e).__name__, e, default,
        )
        return default


def read_thresholds() -> tuple[int, int, int]:
    """Return ``(threshold, critical_threshold, window_minutes)``.

    Values are pulled from ``SystemConfiguration`` (Chris-tunable at
    runtime, same pattern as §6 signal-pattern-criticality). Falls back
    to module defaults on any error.
    """
    threshold = _read_int_config(_THRESHOLD_KEY, _DEFAULT_THRESHOLD)
    critical_threshold = _read_int_config(_CRITICAL_KEY, _DEFAULT_CRITICAL_THRESHOLD)
    window_minutes = _read_int_config(_WINDOW_KEY, _DEFAULT_WINDOW_MIN)
    return threshold, critical_threshold, window_minutes


@dataclass(frozen=True)
class FailureClusterSnapshot:
    """Immutable point-in-time snapshot of a failure cluster.

    Callers use ``.exceeds_threshold`` / ``.urgency_band`` to gate
    escalation and ``.idempotency_key`` for audit-trail composition.
    """

    task_name: str
    window_minutes: int
    window_start: datetime
    window_end: datetime
    distinct_task_id_count: int
    total_event_count: int
    distinct_queues: tuple[str, ...] = ()
    distinct_workers: tuple[str, ...] = ()
    distinct_error_types: tuple[str, ...] = ()
    top_error_signature: str = ''
    sample_task_ids: tuple[str, ...] = ()
    earliest_finished_at: datetime | None = None
    latest_finished_at: datetime | None = None
    threshold: int = _DEFAULT_THRESHOLD
    critical_threshold: int = _DEFAULT_CRITICAL_THRESHOLD
    idempotency_key: str = ''

    @property
    def exceeds_threshold(self) -> bool:
        """True when the distinct-task-id count meets the standard threshold."""
        return self.distinct_task_id_count >= self.threshold

    @property
    def urgency_band(self) -> str:
        """``'critical'`` at critical_threshold, ``'high'`` at threshold, else ``'below'``."""
        if self.distinct_task_id_count >= self.critical_threshold:
            return 'critical'
        if self.distinct_task_id_count >= self.threshold:
            return 'high'
        return 'below'


def compute_cluster(
    task_name: str,
    *,
    now: datetime | None = None,
    threshold: int | None = None,
    critical_threshold: int | None = None,
    window_minutes: int | None = None,
    sample_size: int = _DEFAULT_SAMPLE_SIZE,
) -> FailureClusterSnapshot:
    """Compute a failure-cluster snapshot for ``task_name``.

    Callers supply ``task_name`` (required); everything else defaults
    to SystemConfiguration values via :func:`read_thresholds`. Passing
    explicit overrides is intended for tests, not production callers.
    """
    from core.models_celery_telemetry import CeleryTaskEvent

    now = now or timezone.now()
    cfg_threshold, cfg_critical, cfg_window = read_thresholds()
    threshold = threshold if threshold is not None else cfg_threshold
    critical_threshold = (
        critical_threshold if critical_threshold is not None else cfg_critical
    )
    window_minutes = window_minutes if window_minutes is not None else cfg_window
    window_start = now - timedelta(minutes=window_minutes)

    qs = CeleryTaskEvent.objects.filter(
        status='FAILURE',
        task_name=task_name,
        finished_at__gte=window_start,
        finished_at__lte=now,
    )

    distinct_task_ids = list(
        qs.values_list('task_id', flat=True).distinct()[: max(sample_size, 100)]
    )
    distinct_task_id_count = qs.values('task_id').distinct().count()
    total_event_count = qs.count()

    distinct_queues = tuple(
        sorted({q for q in qs.values_list('queue', flat=True) if q})
    )
    distinct_workers = tuple(
        sorted({w for w in qs.values_list('worker', flat=True) if w})
    )
    error_types = [et for et in qs.values_list('error_type', flat=True) if et]
    distinct_error_types = tuple(sorted(set(error_types)))
    top_error_signature = ''
    if error_types:
        signature_counts = (
            qs.exclude(error_type='')
            .values('error_type')
            .annotate(n=Count('id'))
            .order_by('-n')
        )
        top = signature_counts.first()
        if top:
            top_error_signature = f"{top['error_type']} ({top['n']}x)"

    sample_task_ids = tuple(distinct_task_ids[:sample_size])
    finished = list(
        qs.values_list('finished_at', flat=True).order_by('finished_at')
    )
    earliest = finished[0] if finished else None
    latest = finished[-1] if finished else None

    urgency_band = (
        'critical' if distinct_task_id_count >= critical_threshold
        else 'high' if distinct_task_id_count >= threshold
        else 'below'
    )
    idempotency_key = (
        f"failure_cluster:{task_name}:"
        f"{int(window_start.timestamp())}:{urgency_band}"
    )

    return FailureClusterSnapshot(
        task_name=task_name,
        window_minutes=window_minutes,
        window_start=window_start,
        window_end=now,
        distinct_task_id_count=distinct_task_id_count,
        total_event_count=total_event_count,
        distinct_queues=distinct_queues,
        distinct_workers=distinct_workers,
        distinct_error_types=distinct_error_types,
        top_error_signature=top_error_signature,
        sample_task_ids=sample_task_ids,
        earliest_finished_at=earliest,
        latest_finished_at=latest,
        threshold=threshold,
        critical_threshold=critical_threshold,
        idempotency_key=idempotency_key,
    )
