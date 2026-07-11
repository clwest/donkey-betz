"""
tests/security/test_i0302_p4_endpoint_sentinels.py — I-0302 Phase 4
Sub-phase 3 endpoint sentinels layer.

Contract refs:
  docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md §1.2
  docs/research/implementation/tenant_boundary_lockdown/I-030204_ast_conformance_rule_spec.md §9
  S2749 open — Rigby routed endpoint discovery via `pa-e71c011bfa3d4124`

**What this covers.** Hand-picked view-layer risk endpoints outside the
5-canonical-model matrix runner surface (which lives in
`test_i0302_p4_matrix_harness.py`). This module focuses on the *cockpit
ops control-plane* — endpoints that:
  - Trigger arbitrary agent runs, retries, or long-running tasks
  - Mutate feature flags / provider configs / autopilot policies
  - List / update / approve incidents, decisions, gates
  - Expose queue depths, cost telemetry, run traces, audit logs

**The invariant.** These endpoints are *ops-only*. The 4-role posture:

  - anon      → 401 (blocked by UnifiedTokenAuthenticationMiddleware)
  - user_a    → 403 (must be blocked by @superuser_required)
  - user_b    → 403 (must be blocked by @superuser_required)
  - superuser → any status EXCEPT 401 or 403 (reached the endpoint body;
                actual code is 200/404/409/etc. depending on request shape)

**Report-only mode.** Ships with `ENFORCE_SENTINEL_POSTURE = False` per
the same substrate pattern that landed §14 codification (PR #3116 →
#3117 → #3118). Emits `test_reports/i0302_p4_endpoint_sentinels.json`
per run. Flip enforcing after any missing-gate bugs surface and get
batch-fixed.

Rigby proposed 30 candidate endpoints at S2749 open via `repo_tool`
verified against HEAD `b91c10d1`. Extracted 28 with valid URL patterns
from `core/urls.py`. Grep-verified: as of HEAD, 25 of 28 lack
`@superuser_required` — the sentinel is expected to flag those as
missing-gate on first run.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pytest
from django.test import Client


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "test_reports"
REPORT_PATH = REPORT_DIR / "i0302_p4_endpoint_sentinels.json"

ENFORCE_SENTINEL_POSTURE = False


# --------------------------------------------------------------------------
# Sentinel spec
# --------------------------------------------------------------------------


@dataclass
class Sentinel:
    """One sentinel endpoint under the cockpit ops-superuser-only invariant."""

    name: str
    method: str  # "GET" or "POST"
    url: str
    category: str
    urls_py_line: int
    view_file: str
    view_line: int
    body: dict = field(default_factory=dict)


# 28 sentinels — Rigby's S2749 proposal grounded against HEAD b91c10d1.
# All share the same 4-role invariant (ops-superuser-only), which is why
# the harness codes the assertion once and iterates SENTINELS below.
SENTINELS: list[Sentinel] = [
    # ---- Custom actions on cockpit agents ---------------------------------
    Sentinel(
        name="cockpit_agent_run_now",
        method="POST",
        url="/api/cockpit/agents/tb-fake-agent/run-now/",
        category="custom-action",
        urls_py_line=1802,
        view_file="core/views_diagnostics.py",
        view_line=2652,
    ),
    Sentinel(
        name="cockpit_agent_pause",
        method="POST",
        url="/api/cockpit/agents/tb-fake-agent/pause/",
        category="custom-action",
        urls_py_line=1803,
        view_file="core/views_diagnostics.py",
        view_line=2692,
    ),
    Sentinel(
        name="cockpit_agent_resume",
        method="POST",
        url="/api/cockpit/agents/tb-fake-agent/resume/",
        category="custom-action",
        urls_py_line=1804,
        view_file="core/views_diagnostics.py",
        view_line=2734,
    ),
    # ---- Config / flags mutation -----------------------------------------
    Sentinel(
        name="cockpit_config_toggle_provider",
        method="POST",
        url="/api/cockpit/config/providers/tb-fake-provider/toggle/",
        category="custom-action",
        urls_py_line=1824,
        view_file="core/views_diagnostics.py",
        view_line=3786,
    ),
    Sentinel(
        name="cockpit_config_flags_list",
        method="GET",
        url="/api/cockpit/config/flags/",
        category="bulk",
        urls_py_line=1825,
        view_file="core/views_diagnostics.py",
        view_line=3808,
    ),
    Sentinel(
        name="cockpit_config_delete_flag",
        method="POST",
        url="/api/cockpit/config/flags/tb-fake-flag/delete/",
        category="bulk",
        urls_py_line=1826,
        view_file="core/views_diagnostics.py",
        view_line=3862,
    ),
    # ---- Cockpit operations / mode / autopilot ---------------------------
    Sentinel(
        name="cockpit_focus_mode_update",
        method="POST",
        url="/api/cockpit/focus-mode/update/",
        category="custom-action",
        urls_py_line=1710,
        view_file="core/views_diagnostics.py",
        view_line=1251,
    ),
    Sentinel(
        name="cockpit_autopilot_toggle",
        method="POST",
        url="/api/cockpit/autopilot/policies/tb-fake-policy/toggle/",
        category="custom-action",
        urls_py_line=1811,
        view_file="core/views_diagnostics.py",
        view_line=3132,
    ),
    Sentinel(
        name="cockpit_autopilot_policies",
        method="GET",
        url="/api/cockpit/autopilot/policies/",
        category="other-with-reason",
        urls_py_line=1810,
        view_file="core/views_diagnostics.py",
        view_line=3110,
    ),
    # ---- Ops introspection / telemetry -----------------------------------
    Sentinel(
        name="cockpit_queues_overview",
        method="GET",
        url="/api/cockpit/queues/",
        category="other-with-reason",
        urls_py_line=1806,
        view_file="core/views_diagnostics.py",
        view_line=2771,
    ),
    Sentinel(
        name="cockpit_queue_depths",
        method="GET",
        url="/api/cockpit/queues/depths/",
        category="other-with-reason",
        urls_py_line=1807,
        view_file="core/views_diagnostics.py",
        view_line=2886,
    ),
    Sentinel(
        name="cockpit_cost_overview",
        method="GET",
        url="/api/cockpit/cost/",
        category="export",
        urls_py_line=1808,
        view_file="core/views_diagnostics.py",
        view_line=2964,
    ),
    # ---- Library / audit / approvals -------------------------------------
    Sentinel(
        name="cockpit_library_deliverables",
        method="GET",
        url="/api/cockpit/library/deliverables/",
        category="export",
        urls_py_line=1721,
        view_file="core/views_diagnostics.py",
        view_line=1958,
    ),
    Sentinel(
        name="cockpit_library_media",
        method="GET",
        url="/api/cockpit/library/media/",
        category="export",
        urls_py_line=1722,
        view_file="core/views_diagnostics.py",
        view_line=2006,
    ),
    Sentinel(
        name="cockpit_audit_list",
        method="GET",
        url="/api/cockpit/audit/",
        category="export",
        urls_py_line=1730,
        view_file="core/views_diagnostics.py",
        view_line=2499,
    ),
    Sentinel(
        name="cockpit_approvals_list",
        method="GET",
        url="/api/cockpit/approvals/",
        category="export",
        urls_py_line=1723,
        view_file="core/views_diagnostics.py",
        view_line=2077,
    ),
    Sentinel(
        name="cockpit_approve_decision",
        method="POST",
        url="/api/cockpit/approvals/decision/tb-fake-id/decide/",
        category="custom-action",
        urls_py_line=1724,
        view_file="core/views_diagnostics.py",
        view_line=2140,
    ),
    Sentinel(
        name="cockpit_approve_gate",
        method="POST",
        url="/api/cockpit/approvals/gate/tb-fake-id/decide/",
        category="custom-action",
        urls_py_line=1725,
        view_file="core/views_diagnostics.py",
        view_line=2168,
    ),
    Sentinel(
        name="cockpit_retry_run",
        method="POST",
        url="/api/cockpit/remediate/retry-run/tb-fake-run/",
        category="custom-action",
        urls_py_line=1728,
        view_file="core/views_diagnostics.py",
        view_line=2393,
    ),
    # ---- Incidents ---------------------------------------------------------
    Sentinel(
        name="cockpit_incidents_list",
        method="GET",
        url="/api/cockpit/incidents/",
        category="other-with-reason",
        urls_py_line=1832,
        view_file="core/views_diagnostics.py",
        view_line=3919,
    ),
    Sentinel(
        name="cockpit_incident_detail",
        method="GET",
        url="/api/cockpit/incidents/tb-fake-id/",
        category="nested",
        urls_py_line=1833,
        view_file="core/views_diagnostics.py",
        view_line=4011,
    ),
    Sentinel(
        name="cockpit_incident_update",
        method="POST",
        url="/api/cockpit/incidents/tb-fake-id/update/",
        category="nested",
        urls_py_line=1834,
        view_file="core/views_diagnostics.py",
        view_line=4051,
    ),
    Sentinel(
        name="cockpit_incident_add_event",
        method="POST",
        url="/api/cockpit/incidents/tb-fake-id/events/",
        category="nested",
        urls_py_line=1835,
        view_file="core/views_diagnostics.py",
        view_line=4108,
    ),
    # ---- Ops-runs export --------------------------------------------------
    Sentinel(
        name="cockpit_ops_runs_list",
        method="GET",
        url="/api/cockpit/ops-runs/",
        category="export",
        urls_py_line=1837,
        view_file="core/views_diagnostics.py",
        view_line=4165,
    ),
    Sentinel(
        name="cockpit_ops_run_detail",
        method="GET",
        # ops-run-detail uses <uuid:run_id> so path must be a valid UUID
        url="/api/cockpit/ops-runs/00000000-0000-0000-0000-000000000000/",
        category="nested",
        urls_py_line=1838,
        view_file="core/views_diagnostics.py",
        view_line=4209,
    ),
    # ---- Job / trace introspection ---------------------------------------
    Sentinel(
        name="cockpit_job_status",
        method="GET",
        url="/api/cockpit/create/status/tb-fake-job/",
        category="other-with-reason",
        urls_py_line=1714,
        view_file="core/views_diagnostics.py",
        view_line=1419,
    ),
    Sentinel(
        name="cockpit_run_trace",
        method="GET",
        url="/api/cockpit/runs/tb-fake-run/trace/",
        category="other-with-reason",
        urls_py_line=1821,
        view_file="core/views_diagnostics.py",
        view_line=3511,
    ),
    Sentinel(
        name="cockpit_resolve_node_render_start",
        method="POST",
        url="/api/cockpit/resolve-node/render/start/",
        category="custom-action",
        urls_py_line=1717,
        view_file="core/views_diagnostics.py",
        view_line=1839,
    ),
]


# --------------------------------------------------------------------------
# Posture assertion
# --------------------------------------------------------------------------


def _hit(sentinel: Sentinel, client_: Client) -> int:
    """Send the sentinel request and return the numeric HTTP status."""
    if sentinel.method == "GET":
        response = client_.get(sentinel.url)
    elif sentinel.method == "POST":
        response = client_.post(
            sentinel.url,
            data=json.dumps(sentinel.body),
            content_type="application/json",
        )
    else:  # pragma: no cover — defensive
        raise ValueError(f"Unsupported method: {sentinel.method}")
    return response.status_code


def _classify(role: str, status: int) -> tuple[bool, str]:
    """Return (pass_ok, reason) for the posture at (role, status).

    The ops-superuser-only invariant:
      - anon      → 401 (blocked at middleware)
      - user_a    → 403 (must be blocked by @superuser_required)
      - user_b    → 403 (must be blocked by @superuser_required)
      - superuser → NOT 401 or 403 (reached endpoint body)
    """
    if role == "anon":
        if status == 401:
            return True, "middleware blocked as expected"
        return False, f"expected 401, got {status}"
    if role in ("user_a", "user_b"):
        if status == 403:
            return True, "@superuser_required blocked as expected"
        if status == 401:
            return False, (
                "regular user got 401 (session/auth glitch — investigate); "
                "expected 403 from @superuser_required"
            )
        return False, (
            f"regular user got {status} — endpoint likely missing "
            f"@superuser_required (would-be bug)"
        )
    if role == "superuser":
        if status in (401, 403):
            return False, (
                f"superuser got {status} — endpoint gate rejected superuser "
                f"(over-gated or wrong role predicate)"
            )
        return True, f"superuser reached endpoint (status {status})"
    raise ValueError(f"unknown role: {role}")  # pragma: no cover


def _head_sha() -> str:
    try:
        head_file = REPO_ROOT / ".git" / "HEAD"
        head_ref = head_file.read_text().strip()
        if head_ref.startswith("ref: "):
            ref_path = REPO_ROOT / ".git" / head_ref[5:]
            return ref_path.read_text().strip()[:12]
        return head_ref[:12]
    except OSError:
        return "unknown"


def _write_report(payload: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))


# --------------------------------------------------------------------------
# Pytest test
# --------------------------------------------------------------------------


def test_ops_superuser_sentinel_posture(
    client: Client,
    tb_user_a,
    tb_user_b,
    tb_superuser,
) -> None:
    """Assert the ops-superuser-only invariant across every sentinel.

    Report-only by default (ENFORCE_SENTINEL_POSTURE = False):
      - JSON report emitted to test_reports/i0302_p4_endpoint_sentinels.json
      - Test passes regardless of pass/fail counts

    Enforcing (flag True):
      - Same report emitted
      - pytest.fail on any posture failure
    """
    roles_and_users = [
        ("anon", None),
        ("user_a", tb_user_a),
        ("user_b", tb_user_b),
        ("superuser", tb_superuser),
    ]

    results: list[dict] = []

    for sentinel in SENTINELS:
        for role, user in roles_and_users:
            # Fresh client per role so session state doesn't carry over.
            role_client = Client()
            if user is not None:
                role_client.force_login(user)
            status = _hit(sentinel, role_client)
            ok, reason = _classify(role, status)
            results.append(
                {
                    "sentinel": sentinel.name,
                    "category": sentinel.category,
                    "url": sentinel.url,
                    "method": sentinel.method,
                    "role": role,
                    "status": status,
                    "expected": "401" if role == "anon"
                    else "403" if role in ("user_a", "user_b")
                    else "not 401/403",
                    "pass": ok,
                    "reason": reason,
                    "urls_py_line": sentinel.urls_py_line,
                    "view_file": sentinel.view_file,
                    "view_line": sentinel.view_line,
                }
            )

    failures = [r for r in results if not r["pass"]]
    failures_by_sentinel: dict[str, list[dict]] = {}
    for f in failures:
        failures_by_sentinel.setdefault(f["sentinel"], []).append(f)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "head_sha": _head_sha(),
        "invariant_id": "i0302-p4-ops-superuser-only",
        "mode": "enforcing" if ENFORCE_SENTINEL_POSTURE else "report-only",
        "sentinels_total": len(SENTINELS),
        "roles_per_sentinel": 4,
        "results": results,
        "summary": {
            "checks_total": len(results),
            "pass_total": len(results) - len(failures),
            "fail_total": len(failures),
            "sentinels_with_any_failure": len(failures_by_sentinel),
            "sentinels_fully_passing": len(SENTINELS) - len(failures_by_sentinel),
        },
    }
    _write_report(payload)

    if ENFORCE_SENTINEL_POSTURE and failures:
        preview = "\n".join(
            f"  {f['sentinel']:35} role={f['role']:10} status={f['status']:3} "
            f"— {f['reason']}"
            for f in failures[:10]
        )
        pytest.fail(
            f"Endpoint sentinel posture failures: {len(failures)} across "
            f"{len(failures_by_sentinel)} sentinels.\n"
            f"Report: {REPORT_PATH}\n"
            f"First 10:\n{preview}"
        )


def test_sentinel_report_written_and_shape_ok() -> None:
    """Confirm the JSON report was written and its shape is valid."""
    assert REPORT_PATH.exists(), (
        f"Expected report at {REPORT_PATH}. Run the posture test first."
    )
    payload = json.loads(REPORT_PATH.read_text())
    assert payload["invariant_id"] == "i0302-p4-ops-superuser-only"
    assert isinstance(payload["results"], list)
    assert payload["summary"]["checks_total"] == len(payload["results"])
    assert (
        payload["summary"]["pass_total"] + payload["summary"]["fail_total"]
        == payload["summary"]["checks_total"]
    )
