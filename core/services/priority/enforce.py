"""
Session 1086 PR 3a: Priority enforcement helper — the single public API
that every dispatch path (``AgentRouter.route()`` + known bypasses) uses
to consult the :class:`PriorityRouter`.

This module is deliberately thin. It exists to:

1. Centralize the ``PRIORITY_ROUTER_ENABLED`` env-gate check so no call
   site accidentally forgets to wrap the call (consistent kill-switch).
2. Fail-open the entire priority path — exceptions inside matching never
   escape to the dispatch caller. Same contract as
   :meth:`PriorityRouter.check` but enforced at the module boundary.
3. Provide ``check_priority()`` as the ONLY function call sites need to
   import. PR 3b's throttling + telemetry recording will hang additional
   helpers off this module without touching call sites.
4. Close Q7 from the Rigby design review: because every known bypass
   path imports from here, we can grep for call-site coverage and
   enforce it with the PR 3a test in ``core/tests/test_priority_enforcement.py``.

## What PR 3a does NOT do

- **No semaphore throttling.** The decision is computed, logged, and
  returned — no concurrency limits are applied yet. PR 3b wires that.
- **No telemetry recording.** ``CeleryTaskEvent.priority_matched`` etc.
  don't exist yet. PR 3b ships the migration.
- **No runtime behavior change when gate is OFF.** Default env is
  ``PRIORITY_ROUTER_ENABLED=false`` so first deploy is observer-only.
  Flip to ``true`` after smoke validation.

The pattern: every dispatch path does the same 2 lines.

    from core.services.priority.enforce import check_priority

    decision = check_priority(agent_name, task, trigger_source='autonomous_beat')
    # ... existing agent.execute(...) unchanged ...

The returned ``decision`` is either a :class:`PriorityDecision` or
``None`` (when the gate is OFF). Callers that want to stash it on an
execution record for later telemetry correlation may do so, but are
not required to. PR 3a call sites just log it.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# ── Env gate ────────────────────────────────────────────────────────────

# ``PRIORITY_ROUTER_ENABLED`` is the master kill-switch for the entire
# priority-aware routing feature. Default FALSE on first deploy so PR 3a
# can ship in observer-only mode with zero behavior change. Flip to TRUE
# after Rigby confirms the smoke telemetry looks right.
PRIORITY_ROUTER_ENABLED_ENV = "PRIORITY_ROUTER_ENABLED"


def _gate_enabled() -> bool:
    """Read the env var each call — allows operators to flip it live
    via ``export PRIORITY_ROUTER_ENABLED=true`` without restarting.
    Accepts ``true``, ``1``, ``yes``, ``on`` (case-insensitive) as True;
    anything else is False."""
    raw = os.environ.get(PRIORITY_ROUTER_ENABLED_ENV, "").strip().lower()
    return raw in ("true", "1", "yes", "on")


# ── Rate-limited fail-open log ──────────────────────────────────────────

import time
_last_fail_log_ts: float = 0.0


def _log_enforce_failure() -> None:
    """Rate-limit the fail-open log to once per 60s so catastrophic
    outages don't flood logs. Same pattern as
    :func:`core.services.priority.priority_router._log_fail_open_rate_limited`
    and :meth:`ActivePriority.get_active_priorities`."""
    global _last_fail_log_ts
    try:
        now = time.monotonic()
        if now - _last_fail_log_ts > 60.0:
            _last_fail_log_ts = now
            logger.exception(
                "priority.enforce.check_priority fail-open: exception "
                "suppressed, returning None"
            )
    except Exception:
        pass  # logging must never break fail-open


# ── Public API: check_priority() ────────────────────────────────────────

def check_priority(
    agent_name: str,
    task: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    trigger_source: Optional[str] = None,
) -> Optional[Any]:
    """
    Single enforcement entrypoint. Every dispatch path in the platform
    should call this BEFORE invoking an agent. Returns the
    :class:`PriorityDecision` from :meth:`PriorityRouter.check` if the
    gate is enabled, or ``None`` if the gate is disabled or an
    exception occurred.

    ``None`` means "treat as matched, skip any throttling" — the same
    semantics as fail-open. PR 3a callers log the decision and proceed.
    PR 3b callers will add semaphore acquisition when the decision is
    ``matched=False``.

    Parameters
    ----------
    agent_name
        The exact agent name being dispatched (e.g. ``"ImageAgent"``).
        Used for whitelist/blacklist matching and tag derivation.
    task
        Optional task description text. Used only for opt-in keyword
        matching (priorities that set ``enable_keyword_match=True``).
    context
        Optional dict passed through for future extension. Not read by
        the matching logic in PR 3a but accepted for API stability so
        PR 3b can add context-aware matching (e.g., workspace-scoped
        priorities) without breaking call sites.
    trigger_source
        Where this dispatch came from. The critical value is
        ``"user_chat"`` — it tells the router this is user-triggered
        work and exempts it from throttling unconditionally. Other
        values (``"autonomous_beat"``, ``"direct_dispatch"``, ``None``)
        go through the full matching pipeline.

    Returns
    -------
    Optional[PriorityDecision]
        - ``PriorityDecision`` when the gate is ON and matching ran
        - ``None`` when the gate is OFF, or when a matching exception
          was caught and suppressed (fail-open)

    Notes
    -----
    This function NEVER raises. Even a catastrophic ``PriorityRouter``
    bug will return ``None`` and log once per 60s via
    :func:`_log_enforce_failure`.
    """
    if not _gate_enabled():
        return None

    try:
        # Lazy inline import so this module stays importable even if
        # priority_router has a top-level exception — fail-open at the
        # boundary.
        from core.services.priority.priority_router import PriorityRouter

        router = PriorityRouter()
        return router.check(
            agent_name=agent_name,
            task=task,
            context=context,
            trigger_source=trigger_source,
        )
    except Exception:
        _log_enforce_failure()
        return None


def log_decision(decision: Optional[Any], agent_name: str) -> None:
    """
    Observer-mode logging + telemetry recording per dispatch.

    Two actions, both fail-open:
      1. Emit a single INFO log line describing the decision
      2. Record the decision into the current task's :class:`CeleryTaskEvent`
         row if one exists (PR 3b addition)

    No-ops when ``decision`` is ``None`` (gate OFF or fail-open).
    """
    if decision is None:
        return
    try:
        logger.info(
            "[priority] %s %s via=%s priority=%s queue=%s",
            agent_name,
            "MATCH" if decision.matched else "MISMATCH",
            decision.matched_via,
            decision.priority_name,
            decision.recommended_queue,
        )
    except Exception:
        pass  # logging must never break dispatch

    # Session 1086 PR 3b: Record to CeleryTaskEvent so dashboards can
    # query "what percentage of last-hour tasks matched priorities?".
    # Uses celery.current_task to find the row; silently no-ops when
    # called from outside a Celery worker (HTTP request path, management
    # command, test harness). The fail-open guarantee still holds:
    # any exception in the recording path is swallowed, not propagated.
    _record_priority_telemetry(decision)


def _record_priority_telemetry(decision: Any) -> None:
    """
    Update the current CeleryTaskEvent row with priority_matched,
    priority_name, throttle_class. If the row doesn't exist yet (race
    with task_prerun signal) or we're not in a Celery context, skip.

    Only records the FIRST decision per task — subsequent dispatches
    from the same task won't overwrite. Use ``update_fields`` to avoid
    stomping other signal-handler updates (heartbeat thread, etc.).
    """
    try:
        from celery import current_task
        request = getattr(current_task, "request", None)
        task_id = getattr(request, "id", None) if request is not None else None
        if not task_id:
            return  # not inside a Celery task — HTTP request, test, etc.

        from core.models_celery_telemetry import CeleryTaskEvent

        # Only write if no prior decision has been recorded for this
        # task (first-dispatch-wins). Avoids thrash when a task runs
        # multiple agents back-to-back.
        event = CeleryTaskEvent.objects.filter(task_id=task_id).first()
        if event is None:
            return  # task_prerun signal hasn't fired yet — skip
        if event.priority_matched is not None:
            return  # already recorded — first-wins

        event.priority_matched = bool(decision.matched)
        event.priority_name = (
            str(decision.priority_name)[:120]
            if getattr(decision, "priority_name", None)
            else None
        )
        event.throttle_class = (
            str(decision.throttle_class)[:16]
            if getattr(decision, "throttle_class", None)
            else None
        )
        event.save(
            update_fields=[
                "priority_matched",
                "priority_name",
                "throttle_class",
            ]
        )
    except Exception:
        _log_enforce_failure()
