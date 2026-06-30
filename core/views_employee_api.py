"""Read-only HTTP API for Employee OS — Session 1265 P1.

Thin DRF function-view wrappers around the same helpers
``employee_tool`` (PA tool) and ``derive_status`` /
``evidence_for_mission`` already use. **No new logic, no new
models, no new helpers** — just HTTP plumbing.

Endpoints (all GET, all ``IsAdminUser`` gated per Rigby S1265
SIGN-with-edits D3):

  1. ``GET /api/employees/`` — list registered employees.
  2. ``GET /api/employees/<handle>/`` — one employee + all jobs.
  3. ``GET /api/employees/<handle>/jobs/<job_key>/status/``
     — daily-read status surface (window=7d|30d|90d).
  4. ``GET /api/missions/<mission_id>/`` — minimal OpsRun detail.
  5. ``GET /api/missions/<mission_id>/evidence/`` — full evidence
     join (verbose=true for full error_tail).

Response shapes mirror ``employee_tool`` verbatim (per Rigby
SIGN-clean D1) so a contract test can deep-equal the two
surfaces. Auth gate is ``IsAdminUser`` because these endpoints
expose JobContract shapes + ops telemetry + mission evidence
which we should not assume are safe for arbitrary authenticated
users on a multi-tenant platform.
"""

from __future__ import annotations

from typing import Any, Dict, List

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.employees import (
    get_employee,
    get_job,
    list_employees,
    list_job_keys_for_employee,
    list_jobs_with_keys,
)
from core.employees.status import derive_status, evidence_for_mission
from core.services.td_handlers_employee import (
    _dataclass_to_jsonable,
    _parse_window,
)


# ── 1. GET /api/employees/ ───────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAdminUser])
def employee_list(request):
    """List registered AI Employees.

    Returns the same JSON-safe AIEmployee shape ``employee_tool``
    uses when serializing the registry. No filtering, no pagination
    — v0 registry is tiny (3 employees).
    """
    employees: List[Dict[str, Any]] = [
        _dataclass_to_jsonable(e) for e in list_employees()
    ]
    return Response(
        {
            "ok": True,
            "count": len(employees),
            "employees": employees,
        }
    )


# ── 2. GET /api/employees/<handle>/ ──────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAdminUser])
def employee_detail(request, handle: str):
    """One employee + every assigned JobContract.

    Response shape mirrors ``employee_tool`` action=describe
    verbatim — same ``employee`` + ``job_count`` + ``jobs[]``
    keys, same nested dataclass serialization. 404 with
    ``known_employees`` list on unknown handle.
    """
    employee_handle = (handle or "").strip().lower()
    employee = get_employee(employee_handle)
    if employee is None:
        return Response(
            {
                "ok": False,
                "error": f"Unknown employee {employee_handle!r}.",
                "known_employees": [e.handle for e in list_employees()],
            },
            status=404,
        )

    jobs_payload = [
        {"key": key, "contract": _dataclass_to_jsonable(job)}
        for key, job in list_jobs_with_keys(employee_handle)
    ]

    return Response(
        {
            "ok": True,
            "action": "describe",
            "employee": _dataclass_to_jsonable(employee),
            "job_count": len(jobs_payload),
            "jobs": jobs_payload,
        }
    )


# ── 3. GET /api/employees/<handle>/jobs/<job_key>/status/ ────────────


@api_view(["GET"])
@permission_classes([IsAdminUser])
def employee_job_status(request, handle: str, job_key: str):
    """Daily-read status surface for one (employee, job).

    Wraps ``core.employees.status.derive_status`` verbatim.

    Query params:
      * ``window`` — '7d' (default) | '30d' | '90d'.
      * ``mission_id`` — optional opt-in pointer redirect to
        ``evidence_for_mission`` (forwarded as ``mission_id_hint``).
    """
    employee_handle = (handle or "").strip().lower()
    job_key_norm = (job_key or "").strip().lower()

    employee = get_employee(employee_handle)
    if employee is None:
        return Response(
            {
                "ok": False,
                "error": (
                    f"Unknown employee {employee_handle!r}; "
                    "status surface requires a registered employee."
                ),
                "known_employees": [e.handle for e in list_employees()],
            },
            status=404,
        )

    job = get_job(employee_handle, job_key_norm)
    if job is None:
        return Response(
            {
                "ok": False,
                "error": (
                    f"Employee {employee_handle!r} has no job "
                    f"keyed {job_key_norm!r}."
                ),
                "known_jobs": list_job_keys_for_employee(employee_handle),
            },
            status=404,
        )

    window_days = _parse_window(request.query_params.get("window"))
    if window_days is None:
        return Response(
            {
                "ok": False,
                "error": (
                    "Unrecognized window. v0 supports '7d', '30d', "
                    "or '90d'."
                ),
                "valid_windows": ["7d", "30d", "90d"],
            },
            status=400,
        )

    mission_id_hint = (
        (request.query_params.get("mission_id") or "").strip() or None
    )

    return Response(
        derive_status(
            employee_handle=employee.handle,
            employee_display_name=employee.display_name,
            job_key=job_key_norm,
            job_display_name=job.title,
            mission_run_kind=job.mission_run_kind,
            window_days=window_days,
            mission_id_hint=mission_id_hint,
        )
    )


# ── 4. GET /api/missions/<mission_id>/ ───────────────────────────────


# Field contract for the mission detail endpoint. Locked by
# ``test_mission_detail_contract_field_presence`` so downstream
# consumers can assume these 8 keys are always present.
_MISSION_DETAIL_FIELDS = (
    "id",
    "status",
    "run_kind",
    "triggered_by",
    "started_at",
    "finished_at",
    "mission_id",
    "summary",
)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def mission_detail(request, mission_id):
    """Minimal OpsRun row detail for one mission.

    Subset of ``OpsRun`` fields (8) chosen to mirror what
    ``derive_status`` exposes in ``latest_mission``. Datetime
    fields render as ISO 8601 strings; ``finished_at`` may be
    null for still-running missions.
    """
    from core.models_ops_runs import OpsRun

    try:
        run = OpsRun.objects.get(id=mission_id)
    except (OpsRun.DoesNotExist, ValueError):
        return Response(
            {
                "ok": False,
                "error": "mission_not_found",
                "mission_id": str(mission_id),
            },
            status=404,
        )

    started = run.started_at.isoformat() if run.started_at else None
    finished = run.finished_at.isoformat() if run.finished_at else None
    mission_uuid_str = str(run.mission_id) if run.mission_id else None

    return Response(
        {
            "ok": True,
            "mission": {
                "id": str(run.id),
                "status": run.status,
                "run_kind": run.run_kind,
                "triggered_by": run.triggered_by,
                "started_at": started,
                "finished_at": finished,
                "mission_id": mission_uuid_str,
                "summary": run.summary or {},
            },
        }
    )


# ── 5. GET /api/missions/<mission_id>/evidence/ ──────────────────────


@api_view(["GET"])
@permission_classes([IsAdminUser])
def mission_evidence(request, mission_id):
    """Full evidence join for one mission.

    Wraps ``core.employees.status.evidence_for_mission`` verbatim.

    Query params:
      * ``verbose`` — 'true'/'1'/'yes' to return the full
        ``error_tail``; otherwise returns ``error_tail_preview``
        + ``has_full_error_tail`` (default).
    """
    raw_verbose = (request.query_params.get("verbose") or "").strip().lower()
    verbose = raw_verbose in ("true", "1", "yes")

    result = evidence_for_mission(
        mission_id=str(mission_id), verbose=verbose
    )

    # ``evidence_for_mission`` already returns ``{ok:False,
    # error:'mission_not_found', ...}`` for unknown ids; reflect that
    # as HTTP 404 so REST consumers get the right signal without
    # losing the body shape.
    status_code = 404 if result.get("error") == "mission_not_found" else 200
    return Response(result, status=status_code)
