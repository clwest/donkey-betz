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

# Session 1250 PR 6: decisions that produce a RigbyWorkItem row.
# 'ignore' never produces a work item; 'log' is a v0-reserved bucket
# with no rules attached today (no work item either, since no rule
# produces 'log' in v0). 'create_initiative' / 'delegate' are deferred
# to later PRs which need to make additional plumbing decisions about
# what those side effects mean.
ACTIONABLE_DECISIONS: frozenset[str] = frozenset({"monitor", "notify"})

# Priority ladder: mission_impact → priority integer. Higher = sooner.
_PRIORITY_BY_IMPACT: dict[str, int] = {
    "unknown": 1,
    "low": 3,
    "medium": 5,
    "high": 8,
}


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


def _compose_work_item_fields(
    event: PlatformEvent, result: DecisionResult, event_ref: str
) -> dict[str, Any]:
    """Build the human-readable + structured fields for a RigbyWorkItem.

    Each rule produces a tailored title + recommended_next_action so
    Rigby's queue surface (future PR) can render meaningful entries
    without joining back to the original event payload. The summary
    quotes the rule's ``reason`` directly.
    """
    rule = result.rules_fired[0] if result.rules_fired else None
    title: str
    next_action: str
    if rule == "deliverable_status_backward":
        title = f"Monitor: Deliverable rework signal"
        next_action = (
            "Review the rework reason. Verify it wasn't a regression "
            "or a quality leak; if it was, surface to the COO gate."
        )
    elif rule == "deliverable_status_terminal":
        title = f"Notify: Deliverable reached terminal state"
        next_action = (
            "Confirm the terminal outcome (published / rejected / "
            "archived) was the expected one. If unexpected, escalate."
        )
    elif rule == "ops_step_fail":
        title = f"Notify: Ops step failed"
        next_action = (
            "Investigate the failed ops step. Verify recovery; if the "
            "failure is ongoing or recurrent, surface to oncall."
        )
    else:  # pragma: no cover - defensive default
        title = f"{result.decision.capitalize()}: {event.kind}"
        next_action = "Review the event and decide a next step."

    summary = result.reason or f"{event.source}:{event.source_id} → {result.decision}"

    return {
        "title": title,
        "summary": summary,
        "recommended_next_action": next_action,
        "evidence": {
            "event_ref": event_ref,
            "rules_fired": list(result.rules_fired),
            "decision_reason": result.reason,
            "source": event.source,
            "kind": event.kind,
            "severity": event.severity,
        },
        "priority": _PRIORITY_BY_IMPACT.get(result.mission_impact, 1),
    }


def _maybe_create_work_item(
    *,
    event_ref: str,
    mission_run: Any,
    event: PlatformEvent,
    result: DecisionResult,
) -> Optional[str]:
    """Create a RigbyWorkItem when the decision is actionable and the
    feature flag is on. Returns the work item's UUID string or None.

    Idempotent: ``unique_together = (source_event_ref, decision)`` on
    the model + ``get_or_create`` here means re-running the intake
    task never produces duplicates.

    NB: creates a Rigby-internal row only. Does NOT notify any human,
    dispatch any agent, or call any external surface. PR 7+ will
    decide what consumes the queue.
    """
    if result.decision not in ACTIONABLE_DECISIONS:
        return None
    from django.conf import settings as _settings

    if not getattr(_settings, "RIGBY_INTERNAL_WORK_QUEUE_ENABLED", False):
        return None

    from core.models_rigby_work_items import RigbyWorkItem

    fields = _compose_work_item_fields(event, result, event_ref)
    item, _created = RigbyWorkItem.objects.get_or_create(
        source_event_ref=event_ref,
        decision=result.decision,
        defaults={
            "source_mission_run": mission_run,
            "severity": event.severity,
            "mission_impact": result.mission_impact,
            "priority": fields["priority"],
            "title": fields["title"],
            "summary": fields["summary"],
            "recommended_next_action": fields["recommended_next_action"],
            "evidence": fields["evidence"],
            # status defaults to 'open' per model definition.
        },
    )
    return str(item.id)


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
            "work_item_id": None,
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

    # 6b. Session 1250 PR 6: create RigbyWorkItem when the decision is
    # actionable (monitor / notify) AND the work-queue flag is on.
    # This is Rigby's internal queue — no human notification, no agent
    # dispatch. See docs/EVENT_SYSTEM_INVENTORY.md §13.
    work_item_id = _maybe_create_work_item(
        event_ref=event_ref,
        mission_run=mission_run,
        event=event,
        result=result,
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
        "work_item_id": work_item_id,
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
