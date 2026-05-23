"""Fleet artifact retention/cleanup service (Move 2 Round 2).

Implements the cleanup half of `docs/specs/FLEET_MOVE_2_ROUND_2_SPEC.md`
section 3. Soft-deletes expired artifacts so they stop appearing in
list/pull responses without freeing storage (hard delete is Round 3+).

Public surface:
- `run_cleanup()` — pure function. Called by the Celery beat task AND
  by a management command for ops + tests. Returns a stats dict.

Invariants (locked with Rigby):
- Selection: `expires_at <= now AND deleted_at IS NULL`
- Action: set `deleted_at = now` + `delete_reason = "expired"`
- Batched updates (`FLEET_ARTIFACT_CLEANUP_BATCH_SIZE`, default 500)
- Capped per run (`FLEET_ARTIFACT_CLEANUP_CAP_PER_RUN`, default 5000)
- Idempotent: re-running on an already-deleted row is a no-op because
  `deleted_at IS NULL` filter eliminates it from selection

Observability: returns + logs per-run counters
(scanned/eligible/soft_deleted/capped). No standalone audit row in MLC.
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

    scanned: int      # rows touched in any UPDATE
    soft_deleted: int  # rows that transitioned from `deleted_at IS NULL` → `deleted_at != NULL`
    capped: bool      # True when we bailed at FLEET_ARTIFACT_CLEANUP_CAP_PER_RUN
    duration_ms: int

    def as_dict(self) -> dict:
        return {
            "scanned": self.scanned,
            "soft_deleted": self.soft_deleted,
            "capped": self.capped,
            "duration_ms": self.duration_ms,
        }


def run_cleanup(*, now=None) -> CleanupStats:
    """Soft-delete expired fleet artifacts.

    Args:
        now: optional datetime override for tests / deterministic runs.

    Returns CleanupStats with per-run counters.
    """
    import time as _time
    from core.models.fleet import FleetArtifact

    start = _time.monotonic()
    moment = now or timezone.now()

    batch_size = int(
        getattr(settings, "FLEET_ARTIFACT_CLEANUP_BATCH_SIZE", 500)
    )
    cap = int(
        getattr(settings, "FLEET_ARTIFACT_CLEANUP_CAP_PER_RUN", 5000)
    )

    total_soft_deleted = 0
    capped = False

    # Session 1129 Move 3 — emit artifact.expired events per row.
    # We need (id, app_slug) for each expired artifact to publish the
    # event correctly. Pull a small projection so we can fan out events
    # AFTER the soft-delete commits.
    while True:
        remaining = cap - total_soft_deleted
        if remaining <= 0:
            capped = True
            break

        # Select up to min(batch_size, remaining) ids to update.
        # `expires_at__lte` + `deleted_at__isnull=True` is the canonical
        # selection. Use list() so we can update by id (and so the
        # update is bounded — Postgres UPDATE ... WHERE id IN (...)).
        rows = list(
            FleetArtifact.objects.filter(
                expires_at__lte=moment,
                deleted_at__isnull=True,
            )
            .select_related("created_by_identity")
            .order_by("expires_at", "id")[: min(batch_size, remaining)]
            .values(
                "id",
                "artifact_type",
                "sha256",
                "size_bytes",
                "caller_metadata",
                "created_by_identity__app_slug",
            )
        )
        if not rows:
            break

        ids = [r["id"] for r in rows]
        updated = FleetArtifact.objects.filter(
            id__in=ids,
            deleted_at__isnull=True,  # idempotency belt-and-suspenders
        ).update(
            deleted_at=moment,
            delete_reason="expired",
        )
        total_soft_deleted += updated

        # Emit one artifact.expired event per row. After the commit so
        # subscribers can't see an "expired" event before the soft-
        # delete actually lands. Best-effort — never blocks the loop.
        try:
            from core.services.fleet_events import emit_event
            for r in rows:
                emit_event(
                    event_type="artifact.expired",
                    app_slug=r["created_by_identity__app_slug"] or "",
                    payload={
                        "artifact_id": str(r["id"]),
                        "artifact_type": r["artifact_type"],
                        "sha256": r["sha256"],
                        "size_bytes": r["size_bytes"],
                        "metadata": r["caller_metadata"] or {},
                        "delete_reason": "expired",
                        "deleted_at": moment.isoformat(),
                    },
                    # No FK — the row exists but we already have everything
                    # we need in payload, and avoiding the lookup keeps
                    # the cleanup loop fast.
                    source_artifact=None,
                )
        except Exception as e:
            logger.warning(
                "[fleet-events] emit failed for artifact.expired batch: %s", e
            )

        # If we got fewer rows than the batch limit, we drained the
        # eligible set — exit cleanly.
        if len(rows) < batch_size:
            break

    duration_ms = int((_time.monotonic() - start) * 1000)

    stats = CleanupStats(
        scanned=total_soft_deleted,  # in MLC scanned == updated; future rounds may diverge
        soft_deleted=total_soft_deleted,
        capped=capped,
        duration_ms=duration_ms,
    )

    logger.info(
        "[fleet-artifacts] cleanup soft_deleted=%d capped=%s duration_ms=%d",
        stats.soft_deleted, stats.capped, stats.duration_ms,
    )

    return stats


__all__ = ["run_cleanup", "CleanupStats"]
