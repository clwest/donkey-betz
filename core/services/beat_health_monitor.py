"""
Beat Health Monitor — Session 2735, Beat Schedule Health Campaign P1.

Compares the code-authoritative ``app.conf.beat_schedule`` (defined in
``core/celery.py``) against observed ``CeleryTaskEvent`` fires over a
rolling lookback window and returns a snapshot of allowlisted beat
entries that failed to fire above the minimum-expected-fires threshold.

Cat A discipline:

- Reuses the fast set-diff detection idiom from
  ``core/management/commands/audit_celery_zero_fire.py`` lines 244-277
  (Session 1245/1246 substrate). No subprocess. No static analysis.
  No rg calls. A single indexed DISTINCT query on
  ``CeleryTaskEvent(task_name, started_at)``.
- Reuses ``app.conf.beat_schedule`` (code-defined + deterministic + no
  DB dependency on django-celery-beat's ``PeriodicTask`` table).
- Reuses ``SystemConfiguration`` for runtime tuning (same pattern as
  Cost Protection, §6, §14, §15).
- Reuses ``HumanAttentionBridge`` producer pattern (12th method) +
  HAI Delivery Fanout receivers (Discord + Web Push) → automatic
  fanout on critical HAI.

Missing / deferred (Phase 2 candidates, evidence-only):

- ``PeriodicTask`` coverage — runtime-added beat entries (django-celery-beat
  DB rows). Skipped in v1; add only if evidence shows meaningful
  runtime-managed schedules.
- Cadence-aware expected-fires (e.g., 96 for */15 min, 1 for daily).
  v1 uses a single ``min_expected_fires`` threshold that catches
  zero-fire regardless of expected cadence.
- SUPPRESS_LIST / KNOWN_DEFERRED integration — allowlist-first posture
  (Rigby SIGN pa-bb5efc9a627f47ad Q4) obviates this for v1.
- Auto-remediation. Monitor never triggers restarts or reschedules.

Rigby SIGN pa-bb5efc9a627f47ad refinements folded:

- Q2 3-entry starter allowlist: ``run_heartbeat`` /
  ``check_celery_health`` / ``monitor_celery_health`` — "platform is
  alive" primitives with high signal / low noise.
- Q3 allowlist parsing: always a JSON list. Missing key → default
  3-entry starter set. Empty list → monitor nothing.
- Q5 primary identifier is the beat entry NAME (dict key), not
  ``task_name``. Multiple entries can point at the same task with
  different schedules.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from django.db.models import Count
from django.utils import timezone

logger = logging.getLogger(__name__)


_DEFAULT_LOOKBACK_DAYS = 1
_DEFAULT_MIN_FIRES = 1

# Starter allowlist per Rigby SIGN Q2 refinement — "platform is alive"
# primitives with high signal / low noise. Chris expands via
# SystemConfiguration when observation confirms the noise floor.
_DEFAULT_STARTER_ALLOWLIST: tuple[str, ...] = (
    'heart-service-heartbeat',
    'check-celery-health',
    'monitor-celery-health',
)


@dataclass(frozen=True)
class MissingBeat:
    """One beat entry that failed the expected-fires threshold."""

    beat_entry_name: str  # dict key from app.conf.beat_schedule
    task_name: str        # entry['task']
    schedule_hint: str    # printable repr of entry['schedule']
    expected_min: int
    observed_count: int


@dataclass(frozen=True)
class BeatHealthSnapshot:
    """Point-in-time zero-fire snapshot for the allowlisted beat entries."""

    lookback_days: int
    min_expected_fires: int
    now: datetime
    cutoff: datetime
    allowlist_size: int
    checked: int
    missing: tuple[MissingBeat, ...] = ()
    idempotency_key: str = ''

    @property
    def missing_count(self) -> int:
        return len(self.missing)

    @property
    def any_missing(self) -> bool:
        return bool(self.missing)


def _read_int_config(key: str, default: int) -> int:
    try:
        from core.models.system import SystemConfiguration
        raw = SystemConfiguration.objects.filter(
            key=key, is_active=True,
        ).values_list('value', flat=True).first()
        if raw is None or str(raw).strip() == '':
            return default
        return int(str(raw).strip())
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[BEAT_HEALTH] config read failed key=%s (%s: %s); using default %d',
            key, type(e).__name__, e, default,
        )
        return default


def _read_bool_config(key: str, default: bool) -> bool:
    try:
        from core.models.system import SystemConfiguration
        raw = SystemConfiguration.objects.filter(
            key=key, is_active=True,
        ).values_list('value', flat=True).first()
        if raw is None:
            return default
        s = str(raw).strip().lower()
        if s in ('true', '1', 'yes', 'on'):
            return True
        if s in ('false', '0', 'no', 'off'):
            return False
        return default
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[BEAT_HEALTH] bool config read failed key=%s (%s: %s); '
            'using default %s',
            key, type(e).__name__, e, default,
        )
        return default


def read_allowlist() -> tuple[str, ...]:
    """Read ``beat_health_allowlist`` from SystemConfiguration.

    Missing key → 3-entry starter set. Empty JSON list → empty (monitor
    nothing; effectively disabled without turning off the job). Invalid
    JSON → fail safe to starter set + WARNING log.

    Rigby SIGN Q3 refinement: always a JSON list; no 'auto' sentinel in
    v1.
    """
    try:
        from core.models.system import SystemConfiguration
        raw = SystemConfiguration.objects.filter(
            key='beat_health_allowlist', is_active=True,
        ).values_list('value', flat=True).first()
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[BEAT_HEALTH] allowlist read failed (%s: %s); using starter',
            type(e).__name__, e,
        )
        return _DEFAULT_STARTER_ALLOWLIST
    if raw is None:
        return _DEFAULT_STARTER_ALLOWLIST
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(
            '[BEAT_HEALTH] allowlist JSON parse failed (%s); using starter',
            e,
        )
        return _DEFAULT_STARTER_ALLOWLIST
    if not isinstance(parsed, list):
        logger.warning(
            '[BEAT_HEALTH] allowlist not a list (%s); using starter',
            type(parsed).__name__,
        )
        return _DEFAULT_STARTER_ALLOWLIST
    # Empty list is a valid "monitor nothing" state — do NOT fall back.
    return tuple(str(x) for x in parsed if isinstance(x, str))


def _beat_schedule_entries() -> dict[str, dict[str, Any]]:
    """Return the code-authoritative ``app.conf.beat_schedule`` dict.

    Isolated so tests can patch it. Also handles the (rare) case where
    a caller runs before Celery app import — returns empty dict rather
    than raising.
    """
    try:
        from core.celery import app
        return dict(app.conf.beat_schedule or {})
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[BEAT_HEALTH] beat_schedule read failed (%s: %s); returning empty',
            type(e).__name__, e,
        )
        return {}


def compute_snapshot(
    *,
    now: Optional[datetime] = None,
    lookback_days: Optional[int] = None,
    min_expected_fires: Optional[int] = None,
    allowlist: Optional[tuple[str, ...]] = None,
) -> BeatHealthSnapshot:
    """Compute a beat-health snapshot for the current window.

    Callers usually pass no kwargs — v1 pulls tuning from
    ``SystemConfiguration``. Kwargs exist for tests / manual probes.
    """
    from core.models_celery_telemetry import CeleryTaskEvent

    now = now or timezone.now()
    if lookback_days is None:
        lookback_days = _read_int_config(
            'beat_health_lookback_days', _DEFAULT_LOOKBACK_DAYS,
        )
    if min_expected_fires is None:
        min_expected_fires = _read_int_config(
            'beat_health_min_expected_fires', _DEFAULT_MIN_FIRES,
        )
    if allowlist is None:
        allowlist = read_allowlist()

    cutoff = now - timedelta(days=lookback_days)
    schedule = _beat_schedule_entries()

    # Filter the beat schedule to the allowlisted entries. Missing entries
    # (allowlisted-but-not-in-schedule) are logged but do NOT become
    # missing beats — they're a config bug, not a runtime regression.
    checked_entries: list[tuple[str, dict[str, Any]]] = []
    for entry_name in allowlist:
        entry = schedule.get(entry_name)
        if entry is None:
            logger.info(
                '[BEAT_HEALTH] allowlisted entry %r not present in '
                'app.conf.beat_schedule; skipping',
                entry_name,
            )
            continue
        checked_entries.append((entry_name, entry))

    # Batch a single CeleryTaskEvent query for all monitored task_names
    # so we don't do N queries in the beat tick.
    task_names = {
        str(entry.get('task', '')) for _, entry in checked_entries
        if entry.get('task')
    }
    counts_by_task: dict[str, int] = {}
    if task_names:
        rows = (
            CeleryTaskEvent.objects
            .filter(
                started_at__gte=cutoff,
                started_at__lte=now,
                task_name__in=task_names,
            )
            .values('task_name')
            .annotate(n=Count('task_id'))
        )
        counts_by_task = {row['task_name']: int(row['n']) for row in rows}

    missing: list[MissingBeat] = []
    for entry_name, entry in checked_entries:
        task_name = str(entry.get('task', ''))
        if not task_name:
            continue
        observed = counts_by_task.get(task_name, 0)
        if observed < min_expected_fires:
            missing.append(MissingBeat(
                beat_entry_name=entry_name,
                task_name=task_name,
                schedule_hint=repr(entry.get('schedule', 'unknown'))[:120],
                expected_min=min_expected_fires,
                observed_count=observed,
            ))

    idempotency_key = (
        f'beat_health:{lookback_days}d:{now.strftime("%Y-%m-%d")}'
    )

    return BeatHealthSnapshot(
        lookback_days=lookback_days,
        min_expected_fires=min_expected_fires,
        now=now,
        cutoff=cutoff,
        allowlist_size=len(allowlist),
        checked=len(checked_entries),
        missing=tuple(missing),
        idempotency_key=idempotency_key,
    )


def enabled() -> bool:
    """Master kill switch. Callers check this before running the monitor."""
    return _read_bool_config('beat_health_enabled', True)
