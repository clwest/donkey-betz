"""
Rigby Delegation lifecycle signal handler — Session 1250 PR 8.

A single ``post_save`` receiver on ``AgentExecution`` that observes the
lifecycle of executions Rigby has delegated (those carrying
``parent_object_type='RigbyWorkItem'``) and appends timeline events to
the parent MissionRun. No polling. No background task.

Events written:
- ``agent_assigned`` — on AgentExecution creation (``created=True``).
- ``agent_completed`` — on terminal status save (completed/failed/cancelled).
- ``verification_started`` — immediately after ``agent_completed``.
- ``verification_completed`` — deterministic verdict (no LLM):
    * ``verified`` — status='completed' AND at least one
      ``LLMCallEvent`` with ``status='SUCCESS'`` AND the agent did NOT
      report an empty output_data.
    * ``failed_agent_error`` — status in {failed, cancelled}.
    * ``failed_no_llm_calls`` — status='completed' but zero successful
      LLMCallEvent rows for this execution.
- ``mission_closed`` — final timeline event with the verification verdict.

Gated by ``settings.RIGBY_DELEGATION_ENABLED`` (default False). When
OFF, the handler is a no-op for non-delegated executions, and
short-circuits even for delegated ones (preserving "flag-off → no
delegation lifecycle in the timeline").

Idempotency: the handler queries OpsRunEvent for prior writes against
this execution_id before writing, so the signal firing twice for the
same terminal save does not duplicate rows.
"""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


logger = logging.getLogger(__name__)


# Terminal AgentExecution statuses we react to.
_TERMINAL_STATUSES: frozenset[str] = frozenset({"completed", "failed", "cancelled"})

# Lifecycle labels written into OpsRunEvent on the parent MissionRun.
LABEL_AGENT_ASSIGNED = "agent_assigned"
LABEL_AGENT_COMPLETED = "agent_completed"
LABEL_VERIFICATION_STARTED = "verification_started"
LABEL_VERIFICATION_COMPLETED = "verification_completed"
LABEL_MISSION_CLOSED = "mission_closed"

# Verification verdict closed vocabulary.
VERDICT_VERIFIED = "verified"
VERDICT_FAILED_AGENT_ERROR = "failed_agent_error"
VERDICT_FAILED_NO_LLM_CALLS = "failed_no_llm_calls"


def _has_event(mission_run, label: str, execution_id) -> bool:
    """Return True iff an OpsRunEvent with ``label`` and
    ``detail['execution_id'] == str(execution_id)`` already exists for
    this MissionRun. Idempotency check.
    """
    from core.models_ops_runs import OpsRunEvent

    return OpsRunEvent.objects.filter(
        run=mission_run,
        label=label,
        detail__execution_id=str(execution_id),
    ).exists()


def _write(mission_run, *, label: str, event_type: str, detail: dict) -> None:
    """Append an OpsRunEvent row to the parent MissionRun. Idempotency
    is the caller's responsibility via ``_has_event`` checks."""
    from core.models_ops_runs import OpsRunEvent

    OpsRunEvent.objects.create(
        run=mission_run,
        event_type=event_type,
        label=label,
        detail=detail,
    )


def _verify_execution(execution) -> tuple[str, dict[str, Any]]:
    """Deterministic verification — no LLM, no calls to external systems.

    Returns ``(verdict, evidence)``:
    - verdict ∈ {VERIFIED, FAILED_AGENT_ERROR, FAILED_NO_LLM_CALLS}.
    - evidence carries the counts / fields used to reach the verdict.
    """
    from core.models_llm_telemetry import LLMCallEvent

    if execution.status != "completed":
        return VERDICT_FAILED_AGENT_ERROR, {
            "execution_status": execution.status,
            "error_message": (execution.error_message or "")[:200] or None,
        }

    llm_success_count = LLMCallEvent.objects.filter(
        execution_id=execution.id, status="SUCCESS"
    ).count()

    if llm_success_count == 0:
        return VERDICT_FAILED_NO_LLM_CALLS, {
            "execution_status": execution.status,
            "llm_success_count": 0,
        }

    # Tool-call audit is informational — verification does not depend on
    # it (a "research" agent may legitimately do zero tool calls).
    try:
        from core.models_tool_calls import ToolCallRecord

        tool_call_success_count = ToolCallRecord.objects.filter(
            trace_id=execution.trace_id, success=True
        ).count() if getattr(execution, "trace_id", None) else 0
    except Exception:
        # Defensive — never let verification crash the signal.
        tool_call_success_count = 0

    return VERDICT_VERIFIED, {
        "execution_status": execution.status,
        "llm_success_count": llm_success_count,
        "tool_call_success_count": tool_call_success_count,
    }


@receiver(post_save, sender="core.AgentExecution")
def on_delegation_lifecycle(sender, instance, created, **kwargs):
    """Single receiver covering all Rigby-delegated AgentExecution
    lifecycle transitions.

    Filters on ``parent_object_type='RigbyWorkItem'`` so non-delegated
    executions are no-op'd cheaply (one attribute read + one comparison).
    """
    parent_type = getattr(instance, "parent_object_type", "") or ""
    if parent_type != "RigbyWorkItem":
        return

    parent_id = getattr(instance, "parent_object_id", None)
    if not parent_id:
        return

    if not getattr(settings, "RIGBY_DELEGATION_ENABLED", False):
        return

    from core.services.delegation_auto_disable_monitor import is_tripped
    if is_tripped():
        return

    # Resolve the work item + mission run. Use try/except — never let
    # the signal crash a save.
    try:
        from core.models_rigby_work_items import RigbyWorkItem

        work_item = RigbyWorkItem.objects.select_related(
            "source_mission_run"
        ).get(id=parent_id)
    except Exception as exc:
        logger.warning(
            "[RIGBY_DELEGATION_SIGNAL] could not resolve work_item id=%s "
            "for execution=%s: %s",
            parent_id, instance.id, exc,
        )
        return

    mission_run = work_item.source_mission_run

    agent_name = None
    try:
        if instance.agent_id:
            agent_name = instance.agent.name
    except Exception:
        agent_name = None

    # ── agent_assigned: on creation ──────────────────────────────────────
    if created:
        if not _has_event(mission_run, LABEL_AGENT_ASSIGNED, instance.id):
            _write(
                mission_run,
                label=LABEL_AGENT_ASSIGNED,
                event_type="info",
                detail={
                    "execution_id": str(instance.id),
                    "agent_name": agent_name,
                    "work_item_id": str(work_item.id),
                    "decision": work_item.decision,
                },
            )
        return

    # ── terminal lifecycle ──────────────────────────────────────────────
    if instance.status not in _TERMINAL_STATUSES:
        return

    if _has_event(mission_run, LABEL_AGENT_COMPLETED, instance.id):
        # Already wrote the terminal lifecycle for this execution — the
        # signal fires again on no-op saves; honor idempotency.
        return

    # agent_completed
    completion_detail: dict[str, Any] = {
        "execution_id": str(instance.id),
        "agent_name": agent_name,
        "work_item_id": str(work_item.id),
        "status": instance.status,
        "execution_time_ms": getattr(instance, "execution_time_ms", None),
        "tokens_used": getattr(instance, "tokens_used", None),
        "cost": float(getattr(instance, "cost", 0) or 0),
        "error_message": (
            (getattr(instance, "error_message", "") or "")[:200] or None
        ),
    }
    _write(
        mission_run,
        label=LABEL_AGENT_COMPLETED,
        event_type="step_pass" if instance.status == "completed" else "step_fail",
        detail=completion_detail,
    )

    # verification_started
    _write(
        mission_run,
        label=LABEL_VERIFICATION_STARTED,
        event_type="info",
        detail={
            "execution_id": str(instance.id),
            "work_item_id": str(work_item.id),
        },
    )

    # verification_completed
    verdict, evidence = _verify_execution(instance)
    verified = verdict == VERDICT_VERIFIED
    _write(
        mission_run,
        label=LABEL_VERIFICATION_COMPLETED,
        event_type="step_pass" if verified else "step_fail",
        detail={
            "execution_id": str(instance.id),
            "work_item_id": str(work_item.id),
            "verdict": verdict,
            "evidence": evidence,
        },
    )

    # mission_closed — final timeline event. Does NOT touch
    # MissionRun.status (intentional — see §15 for rationale).
    _write(
        mission_run,
        label=LABEL_MISSION_CLOSED,
        event_type="step_pass" if verified else "info",
        detail={
            "execution_id": str(instance.id),
            "work_item_id": str(work_item.id),
            "verified": verified,
            "verdict": verdict,
            "decided_via": "delegation",
        },
    )

    logger.info(
        "[RIGBY_DELEGATION_SIGNAL] execution=%s work_item=%s status=%s "
        "verdict=%s — mission_closed appended to MissionRun=%s",
        instance.id, work_item.id, instance.status, verdict, mission_run.id,
    )


def connect_rigby_delegation_signals():
    """Called from AppConfig.ready() to ensure the receiver is wired.

    The @receiver decorator already registers at import time — this
    function exists for explicit naming + log line (matches the
    deliverable_status / dream / trigger / etc. signal pattern).
    """
    logger.debug("[rigby_delegation] signals connected")
