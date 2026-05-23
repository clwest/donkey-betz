"""Fleet event retention/cleanup service (Move 3 Round 2).

Hard-deletes FleetEvent rows past their retention window so the
replay endpoint stays bounded. Mirrors `fleet_artifact_cleanup.py` in
structure but diverges on one point per Rigby's lock #4 (Session 1130,
conversation pa-d19c1674b936):

- Events are **hard-deleted**, not soft-deleted. They're pure
  audit/replay log entries; once a subscriber is past the retention
  window they can't catch up anyway, and there's no FK protecting them.
- Artifacts soft-delete because they're work-product with
  retention-aware visibility rules; events have no such requirement.

Public surface:
- `run_cleanup()` — pure function. Called by the Celery beat task AND
  by a management command for ops + tests.

Settings:
- `FLEET_EVENT_RETENTION_DAYS` (default 30) — how long to keep events.
  30 days is enough for active dev debugging while bounding growth.
- `FLEET_EVENT_CLEANUP_BATCH_SIZE` (default 1000).
- `FLEET_EVENT_CLEANUP_CAP_PER_RUN` (default 50000).

Observability: returns + logs per-run counters (deleted/capped).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CleanupStats:
    """Result of `run_cleanup()`. Goes back to the caller AND to the log line."""

    deleted: int
    capped: bool
    duration_ms: int
    retention_days: int

    def as_dict(self) -> dict:
        return {
            "deleted": self.deleted,
            "capped": self.capped,
            "duration_ms": self.duration_ms,
            "retention_days": self.retention_days,
        }


def run_cleanup(*, now=None) -> CleanupStats:
    """Hard-delete FleetEvent rows older than the retention window.

    Args:
        now: optional datetime override for tests / deterministic runs.

    Returns CleanupStats with per-run counters.
    """
    import time as _time
    from datetime import timedelta
    from core.models.fleet import FleetEvent

    start = _time.monotonic()
    moment = now or timezone.now()

    retention_days = int(getattr(settings, "FLEET_EVENT_RETENTION_DAYS", 30))
    batch_size = int(getattr(settings, "FLEET_EVENT_CLEANUP_BATCH_SIZE", 1000))
    cap = int(getattr(settings, "FLEET_EVENT_CLEANUP_CAP_PER_RUN", 50000))

    cutoff = moment - timedelta(days=retention_days)

    total_deleted = 0
    capped = False

    while True:
        remaining = cap - total_deleted
        if remaining <= 0:
            capped = True
            break

        # Bounded batch DELETE — pick a slice of ids by seq order, then
        # DELETE by `id IN (...)`. Postgres handles the IN list well at
        # this scale. seq ordering means we delete oldest-first.
        batch_ids = list(
            FleetEvent.objects.filter(created_at__lt=cutoff)
            .order_by("seq")[: min(batch_size, remaining)]
            .values_list("id", flat=True)
        )
        if not batch_ids:
            break

        deleted_count, _ = FleetEvent.objects.filter(id__in=batch_ids).delete()
        total_deleted += deleted_count

        if len(batch_ids) < batch_size:
            break

    duration_ms = int((_time.monotonic() - start) * 1000)

    stats = CleanupStats(
        deleted=total_deleted,
        capped=capped,
        duration_ms=duration_ms,
        retention_days=retention_days,
    )

    logger.info(
        "[fleet-events] cleanup deleted=%d capped=%s duration_ms=%d retention_days=%d",
        stats.deleted, stats.capped, stats.duration_ms, stats.retention_days,
    )

    return stats


__all__ = ["run_cleanup", "CleanupStats"]
