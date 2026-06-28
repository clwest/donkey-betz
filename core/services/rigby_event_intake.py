"""
rigby_event_intake — Celery task: Rigby Event Intake (PR 4).

PR 4 of the Rigby Event Intake arc. Documentation lives in
``docs/EVENT_SYSTEM_INVENTORY.md`` §11.

This module wires together:
- PR 2's ``platform_event_view`` (read-only normalized event view)
- PR 3's MissionRun-compatible OpsRun (``domain='mission'``,
  ``run_kind='intake'``, ``mission_id``)
- A small, hard-coded set of rules (v0) that classify the event into
  a closed-vocabulary decision.

The intake task is intentionally **dry_run=True by default** and the
allowed side effects are constrained to:
- one MissionRun row (an OpsRun with ``domain='mission'``)
- three OpsRunEvent timeline rows (``intake_started``,
  ``impact_assessed``, ``decision_made``)
- one structured log line (``[RIGBY_INTAKE]``)

Forbidden v0 side effects (enforced by tests):
- no notifications
- no initiative creation
- no agent dispatch
- no tool dispatch
- no external calls
- no LLM invocations

Idempotency: ``mission_id = uuid5(MISSION_INTAKE_NAMESPACE, event_ref)``
makes the mission identity a deterministic function of the event_ref,
so re-running the task on the same event_ref returns the same
MissionRun without writing duplicate timeline rows (each lifecycle
event uses ``get_or_create`` keyed on ``(run, label)``).
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from core.services.platform_event_view import (
    PlatformEvent,
    get_event,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Stable namespace for deriving mission_id from event_ref.
# Derived once at module load from the DNS namespace; do not change without
# a migration plan, as it would re-key every prior MissionRun's identity.
MISSION_INTAKE_NAMESPACE: uuid.UUID = uuid.uuid5(
    uuid.NAMESPACE_DNS, "rigby-event-intake.donkeybetz.com"
)

# Closed vocabularies.
DECISION_VOCAB: frozenset[str] = frozenset(
    {"ignore", "log", "monitor", "notify", "create_initiative", "delegate"}
)
MISSION_IMPACT_VOCAB: frozenset[str] = frozenset(
    {"unknown", "low", "medium", "high"}
)

# Stable lifecycle labels written into OpsRunEvent.
LABEL_INTAKE_STARTED = "intake_started"
LABEL_IMPACT_ASSESSED = "impact_assessed"
LABEL_DECISION_MADE = "decision_made"


# ---------------------------------------------------------------------------
# Result shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DecisionResult:
    """Output of the v0 rule evaluator.

    Fields:
        decision:       Closed-vocab member (DECISION_VOCAB).
        mission_impact: Closed-vocab member (MISSION_IMPACT_VOCAB).
                        Defaults to ``'unknown'`` whenever no rule
                        provided evidence — never ``'low'`` without
                        evidence.
        rules_fired:    List of rule identifiers. Empty for ``'ignore'``
                        decisions (no rule fired); non-empty for any
                        non-``'unknown'`` mission_impact.
        reason:         Human-readable string citing the evidence in
                        the event payload that drove the rule.
    """

    decision: str
    mission_impact: str
    rules_fired: list[str] = field(default_factory=list)
    reason: str = ""

    def __post_init__(self) -> None:
        if self.decision not in DECISION_VOCAB:
            raise ValueError(
                f"decision must be in {sorted(DECISION_VOCAB)}, "
                f"got {self.decision!r}"
            )
        if self.mission_impact not in MISSION_IMPACT_VOCAB:
            raise ValueError(
                f"mission_impact must be in {sorted(MISSION_IMPACT_VOCAB)}, "
                f"got {self.mission_impact!r}"
            )
        # Invariant: non-'unknown' mission_impact requires at least one
        # rule fired (evidence). Conversely, an empty rules_fired list
        # with non-'unknown' mission_impact would be a silent claim
        # without evidence — forbidden per §5 guardrail.
        if self.mission_impact != "unknown" and not self.rules_fired:
            raise ValueError(
                "non-'unknown' mission_impact requires at least one rule "
                "in rules_fired (evidence)"
            )


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def derive_mission_id(event_ref: str) -> uuid.UUID:
    """Deterministic mission identity from an event_ref.

    Same ``event_ref`` → same ``mission_id``. This is the idempotency
    key for the intake MissionRun.

    Raises ``ValueError`` if ``event_ref`` is empty or whitespace-only.
    """
    if not event_ref or not event_ref.strip():
        raise ValueError("event_ref must be a non-empty string")
    return uuid.uuid5(MISSION_INTAKE_NAMESPACE, event_ref)


def apply_rules_v0(event: PlatformEvent) -> DecisionResult:
    """Hard-coded v0 rule set.

    Rules (first match wins; otherwise ``ignore``):
    1. ``deliverable_event`` + ``status_transition`` + direction ==
       ``'backward'`` → ``monitor`` (mission_impact=``low``).
    2. ``deliverable_event`` + ``status_transition`` + direction ==
       ``'terminal'`` → ``notify`` (mission_impact=``medium``).
    3. ``ops_run_event`` + kind == ``'step_fail'`` → ``notify``
       (mission_impact=``medium``).
    4. Otherwise → ``ignore`` (mission_impact=``unknown``,
       rules_fired=``[]``).

    Returns a frozen ``DecisionResult``. The class invariant ensures
    non-``unknown`` mission_impact always carries evidence in
    ``rules_fired``.
    """
    if event.source == "deliverable_event" and event.kind == "status_transition":
        metadata = event.payload.get("metadata") or {}
        direction = metadata.get("direction") if isinstance(metadata, dict) else None
        if direction == "backward":
            return DecisionResult(
                decision="monitor",
                mission_impact="low",
                rules_fired=["deliverable_status_backward"],
                reason=(
                    f"DeliverableEvent {event.source_id} is a backward "
                    f"status transition (direction='backward') — "
                    f"indicates rework or regression."
                ),
            )
        if direction == "terminal":
            return DecisionResult(
                decision="notify",
                mission_impact="medium",
                rules_fired=["deliverable_status_terminal"],
                reason=(
                    f"DeliverableEvent {event.source_id} is a terminal "
                    f"status transition (direction='terminal') — "
                    f"deliverable reached a terminal state."
                ),
            )
    if event.source == "ops_run_event" and event.kind == "step_fail":
        return DecisionResult(
            decision="notify",
            mission_impact="medium",
            rules_fired=["ops_step_fail"],
            reason=(
                f"OpsRunEvent {event.source_id} is a step_fail — an ops "
                f"step failed; oncall visibility warranted."
            ),
        )
    return DecisionResult(
        decision="ignore",
        mission_impact="unknown",
        rules_fired=[],
        reason=(
            f"No v0 rule matched event source={event.source!r} "
            f"kind={event.kind!r}; defaulting to ignore."
        ),
    )


# ---------------------------------------------------------------------------
# Side-effect-aware execution path
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return timezone.now().isoformat()


def _emit_telemetry(
    *,
    event_ref: str,
    events_seen: int,
    processed: int,
    ignored: int,
    dropped: int,
    lag_ms: int,
    decision: str,
    dry_run: bool,
    mission_id: uuid.UUID,
) -> None:
    """Emit the canonical [RIGBY_INTAKE] structured log line."""
    logger.info(
        "[RIGBY_INTAKE] events_seen=%d processed=%d ignored=%d dropped=%d "
        "lag_ms=%d event_ref=%s decision=%s dry_run=%s mission_id=%s",
        events_seen,
        processed,
        ignored,
        dropped,
        lag_ms,
        event_ref,
        decision,
        dry_run,
        mission_id,
    )


def _run_intake(event_ref: str, *, dry_run: bool = True) -> dict[str, Any]:
    """Implementation of the intake flow (sync, called by the Celery task).

    Returns a dict snapshot of the decision for callers / tests.

    Side effects (always allowed):
    - One MissionRun (OpsRun) row via ``get_or_create``.
    - Up to three OpsRunEvent rows via ``get_or_create`` per
      ``(run, label)``.
    - One structured log line.

    Side effects FORBIDDEN under any caller context (no flag flips them on):
    - No notifications. No initiative creation. No agent dispatch.
    - No tool dispatch. No external HTTP. No LLM calls.

    Raises ``ValueError`` for malformed ``event_ref`` and for unknown
    sources. Missing event rows (valid format, source registered, but
    no matching row) are captured as ``status='failed'`` MissionRuns
    with ``dropped=1`` telemetry — they do not raise.
    """
    # Lazy import — keeps top-of-module clean and breaks circular import risk.
    from core.models_ops_runs import OpsRun, OpsRunEvent

    started_at = time.monotonic()

    # 1. Validate event_ref shape early. Bad shape never produces a MissionRun.
    if not isinstance(event_ref, str) or not event_ref.strip():
        raise ValueError("event_ref must be a non-empty string")
    source, sep, source_id = event_ref.partition(":")
    if not sep or not source or not source_id:
        raise ValueError(
            f"Invalid event_ref format: {event_ref!r}; "
            f"expected '<source>:<source_id>'"
        )

    mission_id = derive_mission_id(event_ref)

    # 2. Load the event via platform_event_view. Unknown source raises
    #    ValueError before any MissionRun is created (clean error path).
    #    Missing event (LookupError) captures as a 'dropped' MissionRun.
    event: Optional[PlatformEvent]
    drop_reason: Optional[str] = None
    try:
        event = get_event(event_ref)
    except LookupError as exc:
        event = None
        drop_reason = str(exc)
    # NB: ValueError from get_event (unknown source) propagates — see docstring.

    # 3. Create the MissionRun (idempotent on mission_id).
    mission_title = f"intake: {event_ref}"
    with transaction.atomic():
        mission_run, created = OpsRun.objects.get_or_create(
            mission_id=mission_id,
            domain="mission",
            run_kind="intake",
            defaults={
                "title": mission_title,
                "run_type": "manual",
                "triggered_by": "pa_tool",
                "status": "running",
                "summary": {
                    "event_ref": event_ref,
                    "dry_run": dry_run,
                    "intake_started_at": _now_iso(),
                },
            },
        )

    # 4. Write the intake_started lifecycle event.
    OpsRunEvent.objects.get_or_create(
        run=mission_run,
        label=LABEL_INTAKE_STARTED,
        defaults={
            "event_type": "info",
            "detail": {
                "event_ref": event_ref,
                "dry_run": dry_run,
                "source": source,
                "source_id": source_id,
            },
        },
    )

    # 5. If we couldn't load the event, finalize as 'failed' and emit telemetry.
    if event is None:
        OpsRunEvent.objects.get_or_create(
            run=mission_run,
            label=LABEL_DECISION_MADE,
            defaults={
                "event_type": "step_fail",
                "detail": {
                    "decision": "ignore",
                    "mission_impact": "unknown",
                    "rules_fired": [],
                    "reason": drop_reason or "event not found",
                    "dropped": True,
                },
            },
        )
        # Only finalize if status is still 'running' — preserves
        # idempotency on re-run.
        if mission_run.status == "running":
            mission_run.status = "failed"
            mission_run.finished_at = timezone.now()
            mission_run.summary = {
                **(mission_run.summary or {}),
                "decision": "ignore",
                "mission_impact": "unknown",
                "rules_fired": [],
                "dropped": True,
                "drop_reason": drop_reason,
                "finished_at": _now_iso(),
            }
            mission_run.save(
                update_fields=["status", "finished_at", "summary"]
            )

        lag_ms = int((time.monotonic() - started_at) * 1000)
        _emit_telemetry(
            event_ref=event_ref,
            events_seen=1,
            processed=0,
            ignored=0,
            dropped=1,
            lag_ms=lag_ms,
            decision="ignore",
            dry_run=dry_run,
            mission_id=mission_id,
        )
        return {
            "mission_id": str(mission_id),
            "decision": "ignore",
            "mission_impact": "unknown",
            "rules_fired": [],
            "dropped": True,
            "drop_reason": drop_reason,
            "dry_run": dry_run,
            "created": created,
        }

    # 6. Apply rules and write the impact_assessed + decision_made events.
    result = apply_rules_v0(event)
    OpsRunEvent.objects.get_or_create(
        run=mission_run,
        label=LABEL_IMPACT_ASSESSED,
        defaults={
            "event_type": "info",
            "detail": {
                "mission_impact": result.mission_impact,
                "severity": event.severity,
                "rules_fired": list(result.rules_fired),
                "reason": result.reason,
            },
        },
    )
    decision_event_type = "info" if result.decision == "ignore" else "step_pass"
    OpsRunEvent.objects.get_or_create(
        run=mission_run,
        label=LABEL_DECISION_MADE,
        defaults={
            "event_type": decision_event_type,
            "detail": {
                "decision": result.decision,
                "mission_impact": result.mission_impact,
                "rules_fired": list(result.rules_fired),
                "reason": result.reason,
                "dry_run": dry_run,
            },
        },
    )

    # 7. Finalize MissionRun if not already finalized (idempotent re-run safety).
    if mission_run.status == "running":
        mission_run.status = "passed"
        mission_run.finished_at = timezone.now()
        mission_run.summary = {
            **(mission_run.summary or {}),
            "decision": result.decision,
            "mission_impact": result.mission_impact,
            "rules_fired": list(result.rules_fired),
            "severity": event.severity,
            "finished_at": _now_iso(),
        }
        mission_run.save(update_fields=["status", "finished_at", "summary"])

    lag_ms = int((time.monotonic() - started_at) * 1000)
    _emit_telemetry(
        event_ref=event_ref,
        events_seen=1,
        processed=1,
        ignored=1 if result.decision == "ignore" else 0,
        dropped=0,
        lag_ms=lag_ms,
        decision=result.decision,
        dry_run=dry_run,
        mission_id=mission_id,
    )

    return {
        "mission_id": str(mission_id),
        "decision": result.decision,
        "mission_impact": result.mission_impact,
        "rules_fired": list(result.rules_fired),
        "reason": result.reason,
        "dropped": False,
        "dry_run": dry_run,
        "created": created,
    }


# ---------------------------------------------------------------------------
# Celery task entrypoint
# ---------------------------------------------------------------------------


@shared_task(
    name="core.services.rigby_event_intake.rigby_event_intake",
    queue="pa",
    ignore_result=False,
    time_limit=30,
    soft_time_limit=20,
)
def rigby_event_intake(event_ref: str, dry_run: bool = True) -> dict[str, Any]:
    """Celery entrypoint for Rigby Event Intake.

    See module docstring for the v0 contract. Forbidden side effects
    are encoded by simply not implementing them in this codepath; tests
    assert their absence.

    Returns the decision dict from ``_run_intake``.
    """
    return _run_intake(event_ref, dry_run=dry_run)
