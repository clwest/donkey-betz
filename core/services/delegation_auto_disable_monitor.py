"""Arc I-0100 P3 (IB-1799-T1-03) Stop Condition #1 — auto-disable monitor.

Consumes the thresholds defined in ``core.services.delegation_auto_disable``
and wires the flag-flip-to-False action on threshold breach via a shared
cache sentinel.

Under the LOCAL-only operating model formalized in PR #2972 and the P4
acceptance in PR #2973, this monitor is invoked on-demand via
``manage.py delegation_auto_disable_check``. When production arrives, a
follow-on arc would wire the same monitor to a Celery beat task; the
public surface here (``check_thresholds`` / ``trip`` / ``is_tripped`` /
``clear_trip``) does not need to change.

Kill-switch shape: cache-key sentinel via ``django.core.cache``. In
LOCAL dev this is Redis-backed via ``make celery``; the tests exercise
either Redis or the settings-fallback locmem backend. No DB schema
change. No new model.

Wiring:

- ``core.services.rigby_mission_delegation.delegate_work_item`` and
  ``core.signals.rigby_delegation_signals.on_delegation_lifecycle``
  short-circuit on ``is_tripped()`` after the existing
  ``settings.RIGBY_DELEGATION_ENABLED`` check. Existing flag-off
  behavior is preserved bit-for-bit.

Signal shape read by ``check_thresholds()``:

- OpsRunEvent daily count last 24h → compared to
  ``OPSRUNEVENT_DAILY_AUTO_DISABLE``.
- OpsRunEvent rows with ``label='handler_exception'`` last 1h →
  compared to ``HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE``.
- Lifecycle-labeled OpsRunEvent rows in the last
  ``NULL_RATE_WINDOW_MINUTES`` whose ``detail`` lacks
  ``execution_id`` → NULL rate compared to
  ``EXECUTION_ID_NULL_RATE_THRESHOLD``.
- OpsRunEvent rows with ``label='handler_exception'`` last 1h,
  grouped by ``detail['error_signature']``, max distinct
  ``detail['trace_id']`` per group → compared to
  ``DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD``.

Under LOCAL-only regime, the last three signals have no active
emission surface yet — reads simply return 0 and the check is a
no-op until emitters land. The consumer surface (this module) is
what Stop Condition #1 requires.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from django.core.cache import cache

from core.services.delegation_auto_disable import (
    DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD,
    EXECUTION_ID_NULL_RATE_THRESHOLD,
    HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE,
    NULL_RATE_WINDOW_MINUTES,
    OPSRUNEVENT_DAILY_AUTO_DISABLE,
)

logger = logging.getLogger(__name__)


KILL_SWITCH_KEY = "rigby_delegation_kill_switch"

HANDLER_EXCEPTION_LABEL = "handler_exception"
AUTO_DISABLED_LABEL = "rigby_delegation_auto_disabled"

LIFECYCLE_LABELS = (
    "agent_assigned",
    "agent_completed",
    "verification_started",
    "verification_completed",
    "mission_closed",
)


@dataclass
class ThresholdResult:
    name: str
    breached: bool
    measured: float
    threshold: float
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "breached": self.breached,
            "measured": self.measured,
            "threshold": self.threshold,
            "detail": self.detail,
        }


@dataclass
class TripDecision:
    breached: bool
    results: list[ThresholdResult] = field(default_factory=list)
    measured_at: str = ""

    @property
    def reasons(self) -> list[str]:
        return [r.name for r in self.results if r.breached]

    def to_dict(self) -> dict:
        return {
            "adr_ref": "ADR-0003 §3.4",
            "arc": "I-0100",
            "intake": "IB-1799-T1-03",
            "breached": self.breached,
            "reasons": self.reasons,
            "measured_at": self.measured_at,
            "results": [r.to_dict() for r in self.results],
        }


def check_thresholds(*, now: Optional[datetime] = None) -> TripDecision:
    """Read ORM state and return a structured decision.

    Zero side effects — callers decide whether to invoke ``trip()``.
    """
    from core.models_ops_runs import OpsRunEvent

    now = now or datetime.now(timezone.utc)

    day_ago = now - timedelta(hours=24)
    hour_ago = now - timedelta(hours=1)
    null_window_start = now - timedelta(minutes=NULL_RATE_WINDOW_MINUTES)

    daily_count = OpsRunEvent.objects.filter(created_at__gte=day_ago).count()
    daily = ThresholdResult(
        name="opsrunevent_daily_volume",
        breached=daily_count > OPSRUNEVENT_DAILY_AUTO_DISABLE,
        measured=float(daily_count),
        threshold=float(OPSRUNEVENT_DAILY_AUTO_DISABLE),
        detail=f"OpsRunEvent rows in last 24h ({daily_count})",
    )

    handler_exception_count = OpsRunEvent.objects.filter(
        created_at__gte=hour_ago, label=HANDLER_EXCEPTION_LABEL
    ).count()
    handler = ThresholdResult(
        name="handler_exception_hourly",
        breached=handler_exception_count > HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE,
        measured=float(handler_exception_count),
        threshold=float(HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE),
        detail=(
            "OpsRunEvent rows with label='handler_exception' in last 1h "
            f"({handler_exception_count})"
        ),
    )

    lifecycle_rows = OpsRunEvent.objects.filter(
        created_at__gte=null_window_start, label__in=LIFECYCLE_LABELS
    ).values_list("detail", flat=True)
    lifecycle_total = 0
    lifecycle_null = 0
    for detail in lifecycle_rows:
        lifecycle_total += 1
        if not isinstance(detail, dict) or "execution_id" not in detail:
            lifecycle_null += 1
    null_rate = (lifecycle_null / lifecycle_total) if lifecycle_total else 0.0
    null = ThresholdResult(
        name="execution_id_null_rate",
        breached=null_rate > EXECUTION_ID_NULL_RATE_THRESHOLD,
        measured=null_rate,
        threshold=float(EXECUTION_ID_NULL_RATE_THRESHOLD),
        detail=(
            f"NULL rate {lifecycle_null}/{lifecycle_total} over last "
            f"{NULL_RATE_WINDOW_MINUTES}min lifecycle rows"
        ),
    )

    error_rows = OpsRunEvent.objects.filter(
        created_at__gte=hour_ago, label=HANDLER_EXCEPTION_LABEL
    ).values_list("detail", flat=True)
    signature_hits: dict[str, set[str]] = {}
    for detail in error_rows:
        if not isinstance(detail, dict):
            continue
        sig = detail.get("error_signature")
        trace = detail.get("trace_id")
        if not sig or not trace:
            continue
        signature_hits.setdefault(sig, set()).add(str(trace))
    max_distinct = max((len(traces) for traces in signature_hits.values()), default=0)
    signature = ThresholdResult(
        name="distinct_trace_error_signature",
        breached=max_distinct >= DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD,
        measured=float(max_distinct),
        threshold=float(DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD),
        detail=(
            "max distinct trace_ids per error_signature in last 1h "
            f"({max_distinct})"
        ),
    )

    results = [daily, handler, null, signature]
    return TripDecision(
        breached=any(r.breached for r in results),
        results=results,
        measured_at=now.isoformat(),
    )


def trip(decision: TripDecision) -> None:
    """Flip the shared kill sentinel + emit audit + log evidence.

    Idempotent — safe to call repeatedly. Sentinel has no TTL; clear
    via ``clear_trip()``.
    """
    from core.models_ops_runs import OpsRun, OpsRunEvent

    cache.set(KILL_SWITCH_KEY, True, timeout=None)

    logger.error(
        "[RIGBY_DELEGATION_AUTO_DISABLED] reasons=%s measured_at=%s",
        decision.reasons,
        decision.measured_at,
    )

    try:
        run = OpsRun.objects.create(
            title="RIGBY_DELEGATION_AUTO_DISABLED",
            run_type="manual",
            triggered_by="management_cmd",
            status="passed",
            domain="ops",
            summary={
                "adr_ref": "ADR-0003 §3.4",
                "arc": "I-0100",
                "intake": "IB-1799-T1-03",
                "reasons": decision.reasons,
            },
        )
        OpsRunEvent.objects.create(
            run=run,
            event_type="info",
            label=AUTO_DISABLED_LABEL,
            detail=decision.to_dict(),
        )
    except Exception:
        logger.exception("[RIGBY_DELEGATION_AUTO_DISABLED] failed to write audit row")


def is_tripped() -> bool:
    """Return True if the shared kill sentinel is set."""
    return bool(cache.get(KILL_SWITCH_KEY, False))


def clear_trip() -> None:
    """Remove the shared kill sentinel. Used for rollback drills + tests."""
    cache.delete(KILL_SWITCH_KEY)
