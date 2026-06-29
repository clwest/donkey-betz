"""
ToolDispatcher EmployeeHandlersMixin — Session 1252 PR 1 + 1253 PR 3.

Adds these PA tools to the dispatcher:

  * ``employee_tool`` (actions: describe / run_now / status /
    evidence_for_mission) — read-only inspection of the AI Employee
    registry and assigned JobContract(s), on-demand dispatch
    (Rigby-only), daily-read status surface, and per-mission evidence
    join.
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
    list_jobs_with_keys,
    list_job_keys_for_employee,
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
        """Read-only describe + Rigby-only dispatch of an assigned job.

        Actions:
          * ``describe`` (PR 1) — employee profile + assigned jobs.
          * ``run_now`` (Session 1252 PR 2) — dispatch a job's task
            immediately. v0 supports only ``employee=rigby``,
            ``job=docs_manager``. Rigby-gated via
            ``_verify_rigby_caller``. Optional ``wait_for_result=True``
            polls the resulting OpsRun for up to 90s.
        """
        action = (payload.get("action") or "describe").lower()

        if action == "run_now":
            return self._handle_employee_run_now(
                payload, user_id, trace_id
            )

        if action == "status":
            return self._handle_employee_status(payload, trace_id)

        if action == "evidence_for_mission":
            return self._handle_employee_evidence_for_mission(
                payload, trace_id
            )

        if action != "describe":
            return {
                "ok": False,
                "error": (
                    f"Unknown employee_tool action {action!r}; "
                    f"v0 supports 'describe', 'run_now', 'status', "
                    f"'evidence_for_mission'."
                ),
                "valid_actions": [
                    "describe",
                    "run_now",
                    "status",
                    "evidence_for_mission",
                ],
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
                    # Session 1257 PR 2.1: generalized — list whatever
                    # jobs the registry actually holds for this
                    # employee instead of hardcoding 'docs_manager'.
                    "known_jobs": list_job_keys_for_employee(
                        employee_handle
                    ),
                }
            jobs_payload = [
                {"key": job_key, "contract": _dataclass_to_jsonable(job)}
            ]
        else:
            # All jobs for this employee. Session 1257 PR 2.1:
            # generalized via list_jobs_with_keys so any registered
            # employee (Rigby's docs_manager, Platform Auditor's
            # platform_audit, future Employee #3+) appears.
            jobs_payload = [
                {"key": key, "contract": _dataclass_to_jsonable(job)}
                for key, job in list_jobs_with_keys(employee_handle)
            ]

        return {
            "ok": True,
            "action": "describe",
            "employee": _dataclass_to_jsonable(employee),
            "job_count": len(jobs_payload),
            "jobs": jobs_payload,
        }

    # ── employee_tool action=run_now (Session 1252 PR 2) ─────────────

    def _handle_employee_run_now(
        self,
        payload: Dict[str, Any],
        user_id: Optional[Any],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Dispatch an assigned job's task immediately.

        Session 1257 PR 2.2: generalized to support multiple
        (employee, job) pairs via ``_RUN_NOW_TASKS`` registry. v0
        supports:

          * ``employee=rigby`` + ``job=docs_manager`` (run_kind=docs_cascade)
          * ``employee=platform_auditor`` + ``job=platform_audit``
            (run_kind=platform_audit)

        Returns a ``mission_id`` once the task has created the OpsRun
        row; ``wait_for_result=True`` polls every 2s up to 90s for a
        terminal status, otherwise returns immediately and the caller
        reads status later via ``employee_tool action=status`` (PR 3).
        """
        # Auth gate — both registered employees run as
        # RIGBY.runs_as_username (='chris') in v0, so the existing
        # gate covers both. When future employees declare a
        # different runs_as_username the gate will need broadening.
        gate_check = _verify_rigby_caller(user_id)
        if not gate_check["ok"]:
            return {
                "ok": False,
                "error": gate_check["error"],
                "error_code": "TOOL_PERMISSION_DENIED",
                "auth_gate": gate_check["gate_describe"],
            }

        employee_handle = (
            payload.get("employee") or ""
        ).strip().lower()
        job_key = (payload.get("job") or "").strip().lower()

        dispatch = _RUN_NOW_TASKS.get((employee_handle, job_key))
        if dispatch is None:
            return {
                "ok": False,
                "error": (
                    f"v0 run_now does not support "
                    f"(employee={employee_handle!r}, job={job_key!r})."
                ),
                "supported_pairs": [
                    {"employee": e, "job": j}
                    for (e, j) in sorted(_RUN_NOW_TASKS.keys())
                ],
            }

        wait = bool(payload.get("wait_for_result"))

        # Lazy import — keeps module load light + avoids dragging
        # Celery into the PA-tool import surface.
        task_callable = dispatch.resolve_task()
        async_result = task_callable.delay()
        task_id = getattr(async_result, "id", None)

        if not wait:
            return {
                "ok": True,
                "action": "run_now",
                "employee": employee_handle,
                "job": job_key,
                "task_id": task_id,
                "dispatch_status": "queued",
                "wait_for_result": False,
                "note": (
                    "Mission dispatched. Poll via "
                    "employee_tool action=status (PR 3) or by "
                    "looking up the OpsRun directly."
                ),
            }

        # Poll the latest mission of the matching run_kind for a terminal
        # status.
        terminal = _wait_for_terminal_mission(
            timeout_seconds=90,
            poll_interval_seconds=2,
            run_kind=dispatch.run_kind,
        )
        if terminal is None:
            return {
                "ok": True,
                "action": "run_now",
                "employee": employee_handle,
                "job": job_key,
                "task_id": task_id,
                "dispatch_status": "queued",
                "wait_for_result": True,
                "wait_timeout": True,
                "note": (
                    "Mission still running after 90s wait cap. "
                    "Check status later via employee_tool action=status."
                ),
            }

        return {
            "ok": True,
            "action": "run_now",
            "employee": employee_handle,
            "job": job_key,
            "task_id": task_id,
            "wait_for_result": True,
            "mission_id": str(terminal.id),
            "status": terminal.status,
            "summary": terminal.summary or {},
        }

    # ── employee_tool action=status (Session 1253 PR 3) ──────────────

    def _handle_employee_status(
        self,
        payload: Dict[str, Any],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Read-only daily-read status surface for one employee + job.

        Read-only. No writes. No new model. Trust ratio derived
        per-call. ``window`` is one of ``7d`` / ``30d`` / ``90d``.

        Session 1257 PR 2.2.1: generalized from Rigby/docs_manager-only
        to any registered (employee, job) pair. ``derive_status``
        already accepted ``mission_run_kind`` per-call; this handler's
        gate is the only thing that was hardcoded. Trust math is
        unchanged (certified / (certified + rejected); deferred neutral;
        under_review at 3 rejected in last 7 days regardless of caller
        window).

        If ``mission_id`` is supplied, the response carries a pointer
        to ``evidence_for_mission`` rather than inlining evidence
        (per Rigby SIGN-WITH-EDITS amendment 1).
        """
        employee_handle = (
            payload.get("employee") or ""
        ).strip().lower()
        employee = get_employee(employee_handle)
        if employee is None:
            return {
                "ok": False,
                "error": (
                    f"Unknown employee {employee_handle!r}; "
                    "status surface requires a registered employee."
                ),
                "known_employees": [
                    e.handle for e in list_employees()
                ],
            }

        job_key = (payload.get("job") or "").strip().lower()
        job = get_job(employee_handle, job_key)
        if job is None:
            return {
                "ok": False,
                "error": (
                    f"Employee {employee_handle!r} has no job "
                    f"keyed {job_key!r}."
                ),
                "known_jobs": list_job_keys_for_employee(
                    employee_handle
                ),
            }

        window_days = _parse_window(payload.get("window"))
        if window_days is None:
            return {
                "ok": False,
                "error": (
                    "Unrecognized window. v0 supports '7d', '30d', "
                    "or '90d'."
                ),
                "valid_windows": ["7d", "30d", "90d"],
            }

        mission_id_hint = (payload.get("mission_id") or "").strip() or None

        from core.employees.status import derive_status

        return derive_status(
            employee_handle=employee.handle,
            employee_display_name=employee.display_name,
            job_key=job_key,
            job_display_name=job.title,
            mission_run_kind=job.mission_run_kind,
            window_days=window_days,
            mission_id_hint=mission_id_hint,
        )

    # ── employee_tool action=evidence_for_mission (PR 3) ─────────────

    def _handle_employee_evidence_for_mission(
        self,
        payload: Dict[str, Any],
        trace_id: str,
    ) -> Dict[str, Any]:
        """Per-mission evidence join across the 5+ evidence tables.

        ``verbose=False`` (default) returns ``error_tail_preview``
        (last 30 lines) + ``has_full_error_tail`` rather than the full
        tail (per Rigby SIGN-WITH-EDITS amendment 2). ``verbose=True``
        returns the full ``error_tail``.
        """
        mission_id = (payload.get("mission_id") or "").strip()
        if not mission_id:
            return {
                "ok": False,
                "error": "Missing required arg 'mission_id'.",
            }

        verbose = bool(payload.get("verbose"))

        from core.employees.status import evidence_for_mission

        return evidence_for_mission(
            mission_id=mission_id, verbose=verbose
        )

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


# ── Polling helper (run_now wait_for_result, Session 1252 PR 2) ──────


def _wait_for_terminal_mission(
    *,
    timeout_seconds: int,
    poll_interval_seconds: int,
    run_kind: str = "docs_cascade",
):
    """Poll the latest mission of ``run_kind`` for a terminal status.

    Session 1257 PR 2.2: parameterized on ``run_kind`` so both Rigby's
    docs_cascade and Platform Auditor's platform_audit (and future
    employee missions) can use the same polling helper.

    Returns the OpsRun row once status != 'running', or None if the
    timeout elapses first. Reads from a real DB cursor each iteration
    so the LISTEN/NOTIFY-free poll picks up the worker's commits.
    """
    import time
    from core.models_ops_runs import OpsRun

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        run = (
            OpsRun.objects.filter(
                domain="mission",
                run_kind=run_kind,
            )
            .order_by("-started_at")
            .first()
        )
        if run is not None and run.status != "running":
            return run
        time.sleep(poll_interval_seconds)
    return None


# ── run_now dispatch registry (Session 1257 PR 2.2) ──────────────────


class _RunNowDispatch:
    """Maps an (employee_handle, job_key) pair to a Celery task callable.

    ``resolve_task`` lazy-imports the task module so the registry stays
    Celery-free at PA-tool import time.
    """

    def __init__(self, *, module: str, attr: str, run_kind: str):
        self._module = module
        self._attr = attr
        self.run_kind = run_kind

    def resolve_task(self):
        import importlib

        mod = importlib.import_module(self._module)
        return getattr(mod, self._attr)


_RUN_NOW_TASKS: Dict[tuple, _RunNowDispatch] = {
    ("rigby", "docs_manager"): _RunNowDispatch(
        module="core.tasks_documentation_manager",
        attr="rigby_documentation_manager_daily",
        run_kind="docs_cascade",
    ),
    ("platform_auditor", "platform_audit"): _RunNowDispatch(
        module="core.tasks_platform_audit",
        attr="platform_auditor_run",
        run_kind="platform_audit",
    ),
    # Session 1257 PR 3.2 — Chief of Staff Morning Brief.
    # Wraps the existing morning_brief workflow as a single
    # MissionRunner step (wrap-as-single-step pattern per discovery
    # deliverable 2983377c-08e3-44e6-aeef-cfcf742ae4cd).
    ("chief_of_staff", "morning_brief"): _RunNowDispatch(
        module="core.tasks_chief_of_staff",
        attr="chief_of_staff_morning_brief_run",
        run_kind="morning_brief",
    ),
}


# ── Window parser (PR 3, module-private) ─────────────────────────────


_WINDOW_MAP = {
    "7d": 7,
    "30d": 30,
    "90d": 90,
}


def _parse_window(raw: Optional[Any]) -> Optional[int]:
    """Translate the caller's ``window`` arg into a day count.

    Default is ``7d`` when unset. Returns ``None`` for unrecognized
    inputs so the handler can refuse with a clear error.
    """
    if raw is None or raw == "":
        return _WINDOW_MAP["7d"]
    key = str(raw).strip().lower()
    return _WINDOW_MAP.get(key)


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
