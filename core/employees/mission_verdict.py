"""
Mission verdict helper (Session 1252 PR 1).

Pure-Python entry point that emits an idempotent ``verdict_issued``
event on a MissionRun and flips ``OpsRun.status`` accordingly. Lives
outside the ToolDispatcher mixin so it can be called both from the
PA tool surface (where Rigby invokes it) and from trusted server-side
code (PR 2's daily routine, which calls it programmatically after the
cascade finishes).

Idempotency contract:
  - Per ``(mission_id, verdict)`` combination, exactly one
    OpsRunEvent row is created. Repeated calls with the same verdict
    return the same row (``created=False``).
  - ``OpsRun.status`` is only mutated from ``running``; subsequent
    verdicts do not overwrite a terminal status. Tracked in the
    returned response as ``status_changed`` / ``previous_status``.

See ``docs/handoffs/SESSION_1251_CAPABILITY_AUDIT.md`` §5 + Session
1252 discovery report for the contract.
"""

from __future__ import annotations

from typing import Any, Optional

from django.db import transaction
from django.utils import timezone


# ── Verdict vocabulary ───────────────────────────────────────────────

VERDICT_CERTIFIED = "certified"
VERDICT_REJECTED = "rejected"
VERDICT_DEFERRED = "deferred"

VALID_VERDICTS = frozenset(
    {VERDICT_CERTIFIED, VERDICT_REJECTED, VERDICT_DEFERRED}
)

# Maps verdict → terminal OpsRun.status. Matches the established S1250
# OpsRun lifecycle: running → {passed, failed, partial}.
_VERDICT_TO_STATUS = {
    VERDICT_CERTIFIED: "passed",
    VERDICT_REJECTED: "failed",
    VERDICT_DEFERRED: "partial",
}

# Label prefix — distinct labels per verdict so different verdicts can
# coexist on a mission timeline without clobbering each other via the
# OpsRunEvent (run, label) idempotency key.
LABEL_VERDICT_PREFIX = "verdict_issued"


def verdict_label(verdict: str) -> str:
    """Return the OpsRunEvent label for a given verdict string."""
    return f"{LABEL_VERDICT_PREFIX}:{verdict}"


# ── Public API ───────────────────────────────────────────────────────


def emit_mission_verdict(
    *,
    mission_id: Any,
    verdict: str,
    confidence: Optional[float] = None,
    evidence_refs: Optional[list[str]] = None,
    notes: str = "",
    issued_by: str = "rigby",
) -> dict[str, Any]:
    """Write the verdict event + flip OpsRun status (idempotent).

    Args:
        mission_id: UUID of the OpsRun(domain='mission') row.
        verdict: one of ``certified`` / ``rejected`` / ``deferred``.
        confidence: 0.0-1.0; clamped to range.
        evidence_refs: optional list of evidence pointer strings
            (e.g. ``["llm_call:<uuid>", "deliverable:<uuid>"]``).
        notes: optional free-form note.
        issued_by: handle of the AIEmployee issuing the verdict
            (defaults to ``rigby``; the only v0 employee).

    Returns a structured response describing what happened. Never
    raises for a valid mission_id; raises ``ValueError`` for an
    unknown verdict or for a mission_id that doesn't resolve.
    """
    # Lazy import — avoids a circular at the module-import boundary
    # between ``core.employees`` and Django model loading.
    from core.models_ops_runs import OpsRun, OpsRunEvent

    if verdict not in VALID_VERDICTS:
        raise ValueError(
            f"Unknown verdict {verdict!r}; "
            f"expected one of {sorted(VALID_VERDICTS)}."
        )

    if confidence is not None:
        try:
            confidence = max(0.0, min(1.0, float(confidence)))
        except (TypeError, ValueError):
            raise ValueError(
                f"confidence must be a number 0.0-1.0; got {confidence!r}."
            )

    try:
        mission_run = OpsRun.objects.get(
            id=mission_id, domain="mission"
        )
    except OpsRun.DoesNotExist:
        raise ValueError(
            f"No MissionRun (OpsRun domain='mission') "
            f"with id={mission_id!r}."
        )

    label = verdict_label(verdict)
    detail = {
        "verdict": verdict,
        "issued_by": issued_by,
        "confidence": confidence,
        "evidence_refs": list(evidence_refs or []),
        "notes": notes,
        "issued_at": timezone.now().isoformat(),
    }
    # certified → step_pass; rejected → step_fail; deferred → info.
    event_type = {
        VERDICT_CERTIFIED: "step_pass",
        VERDICT_REJECTED: "step_fail",
        VERDICT_DEFERRED: "info",
    }[verdict]

    with transaction.atomic():
        event, event_created = OpsRunEvent.objects.get_or_create(
            run=mission_run,
            label=label,
            defaults={
                "event_type": event_type,
                "detail": detail,
            },
        )

        previous_status = mission_run.status
        new_status = _VERDICT_TO_STATUS[verdict]
        status_changed = False
        # Only flip from 'running' — terminal statuses are preserved
        # to keep this call idempotent across re-invocations and to
        # avoid overwriting a 'failed' with a later 'partial' etc.
        if mission_run.status == "running":
            mission_run.status = new_status
            mission_run.finished_at = timezone.now()
            existing_summary = mission_run.summary or {}
            mission_run.summary = {
                **existing_summary,
                "verdict": verdict,
                "verdict_issued_by": issued_by,
                "verdict_confidence": confidence,
                "verdict_issued_at": detail["issued_at"],
            }
            mission_run.save(
                update_fields=["status", "finished_at", "summary"]
            )
            status_changed = True

    return {
        "ok": True,
        "mission_id": str(mission_run.id),
        "verdict": verdict,
        "issued_by": issued_by,
        "confidence": confidence,
        "event_id": str(event.id),
        "event_created": event_created,
        "previous_status": previous_status,
        "current_status": mission_run.status,
        "status_changed": status_changed,
    }
