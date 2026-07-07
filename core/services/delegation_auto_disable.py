"""Arc I-0100 P3 (IB-1799-T1-03) — Phase 2 auto-disable trigger
specification per ADR-0003 §3.4 (F7 fold data-integrity + F8 fold
Phase 2 discipline).

This module defines the CONSTANTS + SPEC for the Phase 2 auto-disable
triggers that gate ``RIGBY_DELEGATION_ENABLED=True`` in production.
Actual monitoring integration (which system EMITS these triggers) is
DEFERRED to Phase 2 flag-flip time per ADR-0003 §3.4: "Either new code
paths in P3 OR pre-existing monitoring surfaces accept the
responsibility. Stage 3 pre-flight determines implementation surface."

Baseline captured 2026-07-06 during Stage 3 pre-flight (A6 assumption
verification):

- OpsRun last 30d: 43 total (24 with mission_id populated)
- OpsRunEvent last 30d: 299 (~9.97/day)
- Handler exceptions since S1250 PR 8 wire-up: 0 (dormant per R3)

Phase 2 auto-disable trigger thresholds:

- **OpsRunEvent daily growth** > 14.9 rows/day sustained (baseline
  × 1.5 per §3.4 default).
- **Handler exception rate** > 3/hour.
- **`execution_id` NULL-rate** > 5% over 10 minutes (F7 data-integrity).
- **Repeated error signature across distinct trace_ids** ≥ 3 in a
  rolling window (F7 protect against code-path bugs reproducing for
  different inputs).

Phase 2 flag flip requires ALL of the above trigger monitoring surfaces
active + Chris explicit directive. Monitoring surface integration is
deferred; this module exposes the constants any monitoring surface
would reference.
"""
from __future__ import annotations

from typing import Final


# ─── Baseline captured at 2026-07-06 Stage 3 pre-flight A6 ───────────

BASELINE_OPSRUNEVENT_DAILY: Final[float] = 9.97
"""Baseline OpsRunEvent creation rate before RIGBY_DELEGATION_ENABLED
flips. 30-day ORM count / 30, verified 2026-07-06."""

BASELINE_OPSRUN_DAILY: Final[float] = 1.43
"""Baseline OpsRun creation rate — for cross-reference."""

BASELINE_HANDLER_EXCEPTIONS_HOURLY: Final[int] = 0
"""Baseline handler exception rate — dormant per R3 since S1250 PR 8."""


# ─── Phase 2 auto-disable thresholds per ADR-0003 §3.4 F7 ────────────

VOLUME_MULTIPLIER: Final[float] = 1.5
"""Multiplier applied to baseline for Phase 2 sustained volume threshold."""

OPSRUNEVENT_DAILY_AUTO_DISABLE: Final[float] = BASELINE_OPSRUNEVENT_DAILY * VOLUME_MULTIPLIER
"""OpsRunEvent daily count above this triggers Phase 2 auto-disable.

Value: ~14.9/day at 2026-07-06 baseline. Recalibrate at future Phase 2
re-runs.
"""

HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE: Final[int] = 3
"""Handler exception count per hour above this triggers auto-disable."""

EXECUTION_ID_NULL_RATE_THRESHOLD: Final[float] = 0.05
"""``execution_id`` NULL-rate on emitted OpsRunEvent rows above this
value over ``NULL_RATE_WINDOW_MINUTES`` triggers auto-disable per F7
fold data-integrity regression.
"""

NULL_RATE_WINDOW_MINUTES: Final[int] = 10
"""Rolling window for NULL-rate calculation."""

DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD: Final[int] = 3
"""Repeated error signature across this many distinct trace_ids
in a rolling window triggers auto-disable per F7 fold. Even if the
per-hour rate is below ``HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE``, a
signature repeating across N distinct requests indicates a code path
bug reproducing for different inputs.
"""


# ─── Monitoring-surface integration status ──────────────────────────

MONITORING_SURFACE_INTEGRATED: Final[bool] = True
"""TRUE — monitoring surface wired via
``core.services.delegation_auto_disable_monitor`` (see module) +
``manage.py delegation_auto_disable_check`` (Arc I-0100 P3 Stop
Condition #1 discharge). On threshold breach, ``trip()`` sets a shared
cache-key kill sentinel (``KILL_SWITCH_KEY``). The delegation entry
points at ``core.services.rigby_mission_delegation.delegate_work_item``
and ``core.signals.rigby_delegation_signals.on_delegation_lifecycle``
short-circuit on ``is_tripped()`` in addition to the existing
``settings.RIGBY_DELEGATION_ENABLED`` check.

Under the LOCAL-only operating model per PR #2972 + P4 acceptance
PR #2973, monitor invocation is on-demand via the management command
above. When production arrives, a follow-on arc would wire the same
monitor module to a periodic beat task; the constants + kill-switch
surface here do not need to change.
"""


def get_all_thresholds() -> dict[str, object]:
    """Return the full threshold spec as a dict — useful for
    ``manage.py delegation_lifecycle_smoke_test`` evidence bundle,
    ops-tool queries, and dashboard rendering.
    """
    return {
        "adr_ref": "ADR-0003",
        "phase": 2,
        "baseline": {
            "opsrunevent_daily": BASELINE_OPSRUNEVENT_DAILY,
            "opsrun_daily": BASELINE_OPSRUN_DAILY,
            "handler_exceptions_hourly": BASELINE_HANDLER_EXCEPTIONS_HOURLY,
        },
        "thresholds": {
            "opsrunevent_daily_auto_disable": OPSRUNEVENT_DAILY_AUTO_DISABLE,
            "handler_exception_hourly_auto_disable": HANDLER_EXCEPTION_HOURLY_AUTO_DISABLE,
            "execution_id_null_rate": EXECUTION_ID_NULL_RATE_THRESHOLD,
            "null_rate_window_minutes": NULL_RATE_WINDOW_MINUTES,
            "distinct_trace_error_signature": DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD,
        },
        "monitoring_surface_integrated": MONITORING_SURFACE_INTEGRATED,
        "baseline_measured_at": "2026-07-06 Stage 3 pre-flight A6",
    }
