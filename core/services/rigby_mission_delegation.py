"""
rigby_mission_delegation — Session 1250 PR 8.

Rigby delegates an actionable RigbyWorkItem to an agent via the
existing async dispatch path (``execute_agent_task.apply_async``).
Completion is observed via the ``post_save`` signal on
``AgentExecution`` — see ``core/signals/rigby_delegation_signals.py``.

This module is intentionally minimal:
- Deterministic routing table (no LLM).
- Re-delegation rejected when a non-terminal execution already exists.
- Only the ``delegation_started`` event is written at dispatch time;
  all later lifecycle events (``agent_assigned``, ``agent_completed``,
  ``verification_started``, ``verification_completed``,
  ``mission_closed``) are written by the signal handler.
- No new model. No migration. Parent linkage is carried via
  ``AgentExecution.parent_object_type='RigbyWorkItem'`` +
  ``parent_object_id=<work_item.id>`` (Session 843 fields) — populated
  through context by the PR 8 amendment to
  ``_impl_execute_agent_task`` (parity with the sync ``route()`` path).

Gated by ``settings.RIGBY_DELEGATION_ENABLED`` (default False). When
OFF, ``delegate_work_item`` returns a structured "delegation disabled"
response without writing anything.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from django.conf import settings
from django.db import transaction


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


# v0 routing table — deterministic, no LLM. Add entries by editing this
# dict and the corresponding test fixture. Per S1250 PR 8 directive:
# only 'monitor' is delegatable in v0; 'notify' returns
# 'not_delegatable' and stays in Rigby's queue.
DELEGATION_ROUTING: dict[str, str] = {
    "monitor": "TrendAnalysisAgent",
}

# Terminal AgentExecution.status values (mirrors the model's choices).
# Re-delegation is allowed only when the previous execution is in one
# of these states OR cancelled. 'completed' is excluded because a
# successful delegation should not be re-run.
TERMINAL_FAILURE_STATUSES: frozenset[str] = frozenset({"failed", "cancelled"})
NON_TERMINAL_STATUSES: frozenset[str] = frozenset({"pending", "in_progress"})

# Stable lifecycle label written into OpsRunEvent at dispatch time.
# All later labels (agent_assigned / agent_completed / verification_* /
# mission_closed) are written by the signal handler.
LABEL_DELEGATION_STARTED = "delegation_started"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_delegatable(work_item) -> bool:
    """Return True iff the work item's decision has a routing entry."""
    return work_item.decision in DELEGATION_ROUTING


def routed_agent_for(work_item) -> Optional[str]:
    """Return the routed agent name for a work item's decision, or None."""
    return DELEGATION_ROUTING.get(work_item.decision)


def _existing_active_execution(work_item) -> Optional[Any]:
    """Return a non-terminal AgentExecution for this work item, or None.

    "Non-terminal" = status in {pending, in_progress}. completed,
    failed, cancelled are all terminal — but only failed/cancelled
    permit re-delegation (completed means we succeeded, do not re-run).
    """
    from core.models_unified_system import AgentExecution

    return (
        AgentExecution.objects.filter(
            parent_object_type="RigbyWorkItem",
            parent_object_id=work_item.id,
            status__in=list(NON_TERMINAL_STATUSES),
        )
        .order_by("-created_at")
        .first()
    )


def _compose_task(work_item) -> str:
    """Build the task description handed to the agent.

    Pulls from the work item's existing surface — same fields Rigby
    sees in her queue. Length-bounded so it fits the AgentExecution
    task field (max_length=500).
    """
    title = (work_item.title or "").strip()
    summary = (work_item.summary or "").strip()
    next_action = (work_item.recommended_next_action or "").strip()
    parts: list[str] = []
    if title:
        parts.append(title)
    if next_action:
        parts.append(f"Next action: {next_action}")
    if summary and summary not in (title, next_action):
        parts.append(f"Context: {summary}")
    task = " — ".join(parts) if parts else f"Investigate work item {work_item.id}"
    return task[:480]


def _disabled_response(reason: str, **extra: Any) -> dict[str, Any]:
    return {
        "ok": False,
        "action": "delegate",
        "gateway": "rigby_mission_delegation",
        "error": reason,
        "flag": "RIGBY_DELEGATION_ENABLED",
        **extra,
    }


def delegate_work_item(work_item_id: str) -> dict[str, Any]:
    """Delegate a RigbyWorkItem to an agent.

    Steps:
    1. Validate the work item exists.
    2. Refuse when the work item's decision has no routing entry
       (e.g., ``notify`` in v0).
    3. Refuse when a non-terminal AgentExecution already exists for
       this work item (allow re-delegation only after the prior
       execution is failed/cancelled).
    4. Write a ``delegation_started`` event to the parent MissionRun.
    5. Dispatch via ``execute_agent_task.apply_async`` on the
       ``long_running`` queue with context that carries
       ``parent_object_type='RigbyWorkItem'`` and
       ``parent_object_id=<work_item.id>``. ``auto_followup=False``
       to avoid PA conversation noise.

    Returns a dict the PA tool can echo back to the caller.

    Does not write ``agent_assigned`` / ``agent_completed`` /
    ``verification_*`` / ``mission_closed`` — those are the signal
    handler's job (push-based, no polling).

    Raises nothing. All failure paths return structured ``{ok: False,
    ...}`` dicts.
    """
    if not getattr(settings, "RIGBY_DELEGATION_ENABLED", False):
        return _disabled_response("rigby delegation is disabled (flag off)")

    from core.models_rigby_work_items import RigbyWorkItem
    from core.models_ops_runs import OpsRunEvent
    # ``execute_agent_task`` is the @shared_task wrapper in core.tasks;
    # the implementation lives at core.tasks_agents._impl_execute_agent_task
    # but Celery only registers the wrapper.
    from core.tasks import execute_agent_task

    # 1. Resolve work item.
    try:
        work_item = RigbyWorkItem.objects.select_related(
            "source_mission_run"
        ).get(id=work_item_id)
    except (RigbyWorkItem.DoesNotExist, ValueError) as exc:
        return {
            "ok": False,
            "action": "delegate",
            "gateway": "rigby_mission_delegation",
            "error": f"RigbyWorkItem {work_item_id} not found ({exc})",
        }

    # 2. Routing check.
    agent_name = routed_agent_for(work_item)
    if agent_name is None:
        return {
            "ok": False,
            "action": "delegate",
            "gateway": "rigby_mission_delegation",
            "error": (
                f"Decision {work_item.decision!r} is not delegatable in v0. "
                f"Routing table: {sorted(DELEGATION_ROUTING.keys())}"
            ),
            "work_item_id": str(work_item.id),
            "decision": work_item.decision,
            "not_delegatable": True,
        }

    # 3. Re-delegation guard.
    active = _existing_active_execution(work_item)
    if active is not None:
        return {
            "ok": False,
            "action": "delegate",
            "gateway": "rigby_mission_delegation",
            "error": (
                f"Work item {work_item.id} already has a non-terminal "
                f"AgentExecution ({active.id}, status={active.status!r}). "
                f"Wait for failure/cancellation before re-delegating."
            ),
            "work_item_id": str(work_item.id),
            "active_execution_id": str(active.id),
            "active_status": active.status,
        }

    # 4. Append delegation_started to the parent MissionRun.
    task = _compose_task(work_item)
    mission_run = work_item.source_mission_run
    with transaction.atomic():
        OpsRunEvent.objects.create(
            run=mission_run,
            event_type="info",
            label=LABEL_DELEGATION_STARTED,
            detail={
                "work_item_id": str(work_item.id),
                "decision": work_item.decision,
                "routed_agent": agent_name,
                "task_preview": task[:200],
            },
        )

    # 5. Async dispatch via the existing wrapper. Context carries the
    # parent linkage; the PR 8 amendment to _impl_execute_agent_task
    # plumbs these fields into the AgentExecution row.
    dispatch_context: dict[str, Any] = {
        "parent_object_type": "RigbyWorkItem",
        "parent_object_id": str(work_item.id),
        "auto_followup": False,
        "source": "rigby_mission_delegation",
        "work_item_id": str(work_item.id),
        "mission_run_id": str(mission_run.id),
    }
    async_result = execute_agent_task.apply_async(
        args=[agent_name, task, dispatch_context],
        queue="long_running",
    )
    celery_task_id = getattr(async_result, "id", None)

    logger.info(
        "[RIGBY_DELEGATION] dispatched work_item_id=%s decision=%s "
        "agent=%s celery_task_id=%s",
        work_item.id, work_item.decision, agent_name, celery_task_id,
    )

    return {
        "ok": True,
        "action": "delegate",
        "gateway": "rigby_mission_delegation",
        "work_item_id": str(work_item.id),
        "decision": work_item.decision,
        "agent_name": agent_name,
        "celery_task_id": str(celery_task_id) if celery_task_id else None,
        "mission_run_id": str(mission_run.id),
        "task_preview": task[:200],
    }
