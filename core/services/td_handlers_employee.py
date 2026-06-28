"""
ToolDispatcher EmployeeHandlersMixin — Session 1252 PR 1.

Adds two PA tools to the dispatcher:

  * ``employee_tool`` (action=describe) — read-only inspection of the
    AI Employee registry and the assigned JobContract(s).
  * ``mission_verdict`` (action=certify|reject|defer) — Rigby-gated
    verdict emission on a MissionRun. Wraps the canonical helper at
    ``core.employees.mission_verdict.emit_mission_verdict``.

Auth honesty (v0): the dispatcher only propagates ``user_id`` into
handlers, not the caller ``agent_name``. We cannot distinguish
"Rigby-as-LLM" from "Chris typing in the same PA chat session"
because both invocations carry the same authenticated user_id. The
v0 gate verifies the caller's user_id resolves to the username that
the AIEmployee runs as (``RIGBY.runs_as_username == "chris"``).
Anything else is rejected. The schema is otherwise visible only via
the PA tool surface — i.e. through GPT-5.2 function-calling on the
PA chat path — so the realistic invocation set is already small.
Plumbing ``agent_name`` through to handlers is tracked as a future
PR; documented here so the gap doesn't get re-discovered.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model

from core.employees import (
    AuthorityLevel,
    DOCUMENTATION_MANAGER,
    RIGBY,
    get_employee,
    get_job,
    list_employees,
    list_jobs_for_employee,
)
from core.employees.mission_verdict import (
    VALID_VERDICTS,
    VERDICT_CERTIFIED,
    VERDICT_DEFERRED,
    VERDICT_REJECTED,
    emit_mission_verdict,
)

logger = logging.getLogger(__name__)


# ── Action → verdict translation for mission_verdict tool ────────────

_ACTION_TO_VERDICT = {
    "certify": VERDICT_CERTIFIED,
    "reject": VERDICT_REJECTED,
    "defer": VERDICT_DEFERRED,
}


def _dataclass_to_jsonable(obj: Any) -> Any:
    """Convert AIEmployee / JobContract dataclasses to JSON-safe dicts.

    Preserves tuples as lists, enums as their string values, and
    nested dataclasses recursively. Used by employee_tool describe to
    return a structured response under 2KB for the v0 single-job
    registry.
    """
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _dataclass_to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, AuthorityLevel):
        # AuthorityLevel is a str-enum; coerce to its underlying string
        # value. ``str(obj)`` returns "AuthorityLevel.OBSERVE" — we want
        # just "observe", so reach for the enum value explicitly.
        return getattr(obj, "value", str(obj))
    if isinstance(obj, dict):
        return {k: _dataclass_to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_dataclass_to_jsonable(v) for v in obj]
    return obj


class EmployeeHandlersMixin:
    """Mixin attached to ``ToolDispatcher`` — registers two handlers.

    Mixin pattern matches ``CoreHandlersMixin`` / ``OpsHandlersMixin``
    /etc. in this package. The handlers are bound by name in
    ``ToolDispatcher._register_default_handlers`` (see
    ``core/services/tool_dispatcher.py``).
    """

    # ── employee_tool ────────────────────────────────────────────────

    def _handle_employee_tool(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[Any],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Read-only inspection of the AI Employee + JobContract registry.

        Actions:
          * ``describe`` — returns employee profile + assigned jobs.
            Required arg: ``employee`` (handle). Optional: ``job``
            (job key) to scope the response to a single job.

        Returns structured JSON suitable for direct PA chat surfacing.
        """
        action = (payload.get("action") or "describe").lower()

        if action != "describe":
            return {
                "ok": False,
                "error": (
                    f"Unknown employee_tool action {action!r}; "
                    f"v0 supports only 'describe'."
                ),
                "valid_actions": ["describe"],
            }

        employee_handle = (payload.get("employee") or "").strip().lower()
        if not employee_handle:
            return {
                "ok": False,
                "error": (
                    "Missing required arg 'employee'. "
                    "Try: action=describe employee=rigby"
                ),
                "known_employees": [
                    e.handle for e in list_employees()
                ],
            }

        employee = get_employee(employee_handle)
        if employee is None:
            return {
                "ok": False,
                "error": f"Unknown employee {employee_handle!r}.",
                "known_employees": [
                    e.handle for e in list_employees()
                ],
            }

        job_key = (payload.get("job") or "").strip().lower() or None

        if job_key:
            job = get_job(employee_handle, job_key)
            if job is None:
                return {
                    "ok": False,
                    "error": (
                        f"Employee {employee_handle!r} has no job "
                        f"keyed {job_key!r}."
                    ),
                    "known_jobs": [
                        # Re-derive by stable lookup ordering.
                        "docs_manager"
                    ] if employee_handle == RIGBY.handle else [],
                }
            jobs_payload = [
                {"key": job_key, "contract": _dataclass_to_jsonable(job)}
            ]
        else:
            # All jobs for this employee. v0: just one (docs_manager).
            jobs_payload = []
            for job in list_jobs_for_employee(employee_handle):
                # Reverse-lookup the key — only one job in v0 so this
                # is a stable enumeration, not a fragile mapping.
                if job is DOCUMENTATION_MANAGER:
                    jobs_payload.append(
                        {
                            "key": "docs_manager",
                            "contract": _dataclass_to_jsonable(job),
                        }
                    )

        return {
            "ok": True,
            "action": "describe",
            "employee": _dataclass_to_jsonable(employee),
            "job_count": len(jobs_payload),
            "jobs": jobs_payload,
        }

    # ── mission_verdict ──────────────────────────────────────────────

    def _handle_mission_verdict(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id: Optional[Any],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Rigby-only: certify / reject / defer a MissionRun.

        Actions: ``certify`` / ``reject`` / ``defer``. Writes one
        OpsRunEvent (``label='verdict_issued:<verdict>'``) and flips
        ``OpsRun.status`` to the corresponding terminal value. Calling
        with the same (mission_id, verdict) twice is a no-op for the
        event row (idempotent) and does not overwrite a terminal
        status.

        v0 auth gate documented in module docstring above.
        """
        action = (payload.get("action") or "").strip().lower()
        if action not in _ACTION_TO_VERDICT:
            return {
                "ok": False,
                "error": (
                    f"Unknown mission_verdict action {action!r}; "
                    f"valid: {sorted(_ACTION_TO_VERDICT)}."
                ),
                "valid_actions": sorted(_ACTION_TO_VERDICT),
            }

        # ── Auth gate (v0): caller's user_id must resolve to the user
        #    that Rigby runs as. See module docstring for the
        #    honest-but-limited v0 contract.
        gate_check = _verify_rigby_caller(user_id)
        if not gate_check["ok"]:
            return {
                "ok": False,
                "error": gate_check["error"],
                "error_code": "TOOL_PERMISSION_DENIED",
                # Surface the v0 gate definition for any caller who
                # hits this — keeps the audit trail honest about how
                # the gate works rather than masking it as a generic
                # "denied".
                "auth_gate": gate_check["gate_describe"],
            }

        mission_id = payload.get("mission_id")
        if not mission_id:
            return {
                "ok": False,
                "error": "Missing required arg 'mission_id'.",
            }

        try:
            verdict = _ACTION_TO_VERDICT[action]
            result = emit_mission_verdict(
                mission_id=mission_id,
                verdict=verdict,
                confidence=payload.get("confidence"),
                evidence_refs=payload.get("evidence_refs"),
                notes=payload.get("notes", ""),
                issued_by=RIGBY.handle,
            )
        except ValueError as exc:
            return {
                "ok": False,
                "error": str(exc),
            }

        return {
            "ok": True,
            "action": action,
            **result,
        }


# ── Auth helper (module-private) ─────────────────────────────────────


def _verify_rigby_caller(user_id: Optional[Any]) -> Dict[str, Any]:
    """Best-effort v0 gate: caller must be the user Rigby runs as.

    Returns ``{"ok": True}`` on pass and ``{"ok": False, "error":
    ..., "gate_describe": ...}`` on fail.

    The gate is honest about its limitation — both Chris-typing-in-PA
    and Rigby-as-LLM resolve to the same authenticated user_id, so
    this is a *channel* gate, not a *speaker* gate. Future PRs can
    promote it to a real speaker gate when ``agent_name`` is plumbed
    through the dispatcher to handlers.
    """
    gate_describe = (
        f"v0 gate: caller user_id must resolve to "
        f"username='{RIGBY.runs_as_username}'. Plumbing of caller "
        "agent_name into handlers is a future PR."
    )
    if not user_id:
        return {
            "ok": False,
            "error": "No authenticated user_id available; refusing.",
            "gate_describe": gate_describe,
        }

    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(id=user_id)
    except UserModel.DoesNotExist:
        return {
            "ok": False,
            "error": f"user_id={user_id!r} not found.",
            "gate_describe": gate_describe,
        }

    caller_username = (getattr(user, "username", "") or "").lower()
    if caller_username != RIGBY.runs_as_username.lower():
        return {
            "ok": False,
            "error": (
                f"Caller username={caller_username!r} is not the user "
                f"Rigby runs as ({RIGBY.runs_as_username!r})."
            ),
            "gate_describe": gate_describe,
        }

    return {"ok": True, "gate_describe": gate_describe}
