"""S2794 — Cross-tenant regression runner service.

Runs the ``tests/security/*`` suite as the RUR-C1 shared cross-tenant
regression harness (CAMPAIGN.md §5.2 line 202). Returns a structured
summary consumed by:

  * ``python manage.py run_cross_tenant_regression`` — CLI entrypoint
  * ``core/tasks_tenant_boundary_health.py`` — Celery periodic task
  * ``tests/security/test_cross_tenant_regression.py`` — umbrella test

Result rows are persisted as
``core.models.TenantBoundaryHealthReport`` and read by the Tenant
Boundary Health Workspace sub-tab via
``/api/governance/tenant-boundary-health/``.

**Execution model:** we shell out to ``python -m pytest`` as a subprocess
and parse the JUnit XML pytest emits. Reason: pytest-django's test DB
fixture wiring needs to run in a fresh pytest process, not inside an
already-live Django process (where 250+ tests error on DB fixture
setup collision). Subprocess isolation avoids the landmine and matches
how CI would invoke the suite. Cost: ~5s startup per run, acceptable
for a periodic Celery job.

**Advisory posture (S2794 F1 mitigation):** results are longitudinal
signal for operator triage. They are NOT a launch gate. Chris
ratification remains the explicit gate for opening alpha cohort. The
consuming UI + REST envelope both repeat this advisory framing.

**Provenance (S2794 F3 mitigation):** each report carries ``env`` +
``git_sha`` + ``runner_identity`` + ``created_at`` so a green suite result
can be traced to a specific run — no ambiguity between fresh CI-blessed
data and stale hand-crafted local runs.

**Coverage honesty (S2794 F2 mitigation):** ``COVERAGE_METADATA`` below
lists per-surface status. Async Celery task boundary + WebSocket
consumer boundary are explicitly flagged ``not_yet_covered`` until
I-0303 is opened. Green suite result does NOT imply full-platform
tenant boundary confidence — the tab must render these gaps inline.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional


# ── The umbrella label list ──────────────────────────────────────────
#
# Curated list of test *paths* under ``tests/security/`` that constitute
# the RUR-C1 cross-tenant regression. Extending this list is intentional
# (a design choice, not a discovery); every addition should update
# ``COVERAGE_METADATA`` in the same PR so the tab surfaces the change.
#
# Path-based (not module-dotted) so pytest can collect them directly.
CROSS_TENANT_TEST_PATHS: List[str] = [
    # I-0301 substrate (HTTP + AllowAny + failure-data safety contract)
    "tests/security/test_bucket_a_public_endpoints.py",
    "tests/security/test_bucket_b_remediation.py",
    "tests/security/test_endpoint_drift.py",
    "tests/security/test_failure_envelope_conformance.py",
    # I-0302 substrate (object-level authZ per-model + P4 matrix + AST)
    "tests/security/test_i0302_a2_predicate_wiring.py",
    "tests/security/test_i0302_b_agent_execution_wiring.py",
    "tests/security/test_i0302_c1_chat_conversation_wiring.py",
    "tests/security/test_i0302_d1_deliverable_wiring.py",
    "tests/security/test_i0302_d2_document_wiring.py",
    "tests/security/test_i0302_p4_ast_conformance.py",
    "tests/security/test_i0302_p4_coverage_gap_report.py",
    "tests/security/test_i0302_p4_endpoint_sentinels.py",
    "tests/security/test_i0302_p4_matrix_harness.py",
    "tests/security/test_i0302_p4_ops_aggregate_decorator.py",
    "tests/security/test_object_authz_predicates.py",
    # I-0303 substrate (async task boundary — only partial today; see gaps)
    "tests/security/test_i0303_p2_task_enforcement.py",
    "tests/security/test_ops_tool_tenant_boundary_violations.py",
]


# ── S2794 F2 mitigation — coverage metadata ──────────────────────────
#
# Every surface the platform exposes to a real user needs an explicit
# entry here. ``covered`` / ``partial`` / ``not_yet_covered`` are the
# three status values the UI recognizes. Add a trailing note so the tab
# can render *why* something is not yet covered.
COVERAGE_METADATA: Dict[str, str] = {
    "sync_http_bucket_a_public_endpoints": "covered",
    "sync_http_bucket_b_remediation": "covered",
    "sync_http_endpoint_drift": "covered",
    "failure_envelope_conformance_i0301": "covered",
    "object_level_authz_i0302_predicates": "covered",
    "object_level_authz_i0302_agent_execution": "covered",
    "object_level_authz_i0302_chat_conversation": "covered",
    "object_level_authz_i0302_deliverable": "covered",
    "object_level_authz_i0302_document": "covered",
    "object_level_authz_i0302_ast_conformance": "covered",
    "object_level_authz_i0302_matrix_harness": "covered",
    "async_celery_task_boundary_i0303": "partial (I-0303 not opened — P2 predicate wiring shipped, task-side enforcement not yet)",
    "async_websocket_consumer_boundary": "not_yet_covered (I-0303 not opened)",
    "cross_tenant_signed_url_read": "not_yet_covered (not yet scoped)",
    "cross_tenant_admin_action_audit": "not_yet_covered (RUR-C2 territory)",
}


# ── Known gaps — explicit list for the UI "Known gaps" panel ─────────
KNOWN_GAPS: List[str] = [
    "Async Celery task boundary — I-0303 has scoping but no P2+ enforcement tests yet",
    "WebSocket consumer boundary — I-0303 not opened; no coverage",
    "Cross-tenant read via signed URL — not yet scoped anywhere",
    "Cross-tenant admin action audit — RUR-C2 territory (Async State + Fail-Loud + Traceability)",
]


def _detect_env() -> str:
    """Best-effort environment classification (F3 provenance)."""
    env = os.environ.get("PLATFORM_ENV") or os.environ.get("DJANGO_ENV")
    if env:
        return env.strip().lower()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return "ci"
    return "local"


def _detect_git_sha() -> str:
    """Best-effort HEAD SHA (F3 provenance). Empty string if unresolvable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return ""


def _detect_runner_identity() -> str:
    """Best-effort runner identity (F3 provenance)."""
    return os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown"


def _parse_junit_xml(xml_path: str) -> Dict[str, Any]:
    """Parse pytest-emitted JUnit XML into a summary dict.

    JUnit XML structure (single ``<testsuites>`` root with ``<testsuite>``
    children, each containing ``<testcase>`` rows with optional
    ``<failure>`` / ``<error>`` / ``<skipped>`` sub-elements):

        <testsuites>
          <testsuite tests=".." failures=".." errors=".." skipped="..">
            <testcase classname="..." name="..." time="..." />
            <testcase ...>
              <failure message="..." type="...">TRACEBACK</failure>
            </testcase>
          </testsuite>
        </testsuites>

    Non-existent XML file (subprocess crashed before writing) returns
    zero-count shape so the caller can still emit a report.
    """
    if not os.path.exists(xml_path):
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errored": 0,
            "skipped": 0,
            "failing_test_ids": [],
        }

    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errored": 0,
            "skipped": 0,
            "failing_test_ids": [],
        }

    root = tree.getroot()
    # pytest emits <testsuites> as root or a single <testsuite> — handle both.
    if root.tag == "testsuites":
        suites = root.findall("testsuite")
    else:
        suites = [root]

    total = 0
    failed = 0
    errored = 0
    skipped = 0
    failing_ids: List[str] = []

    for suite in suites:
        for tc in suite.findall("testcase"):
            total += 1
            classname = tc.get("classname", "")
            name = tc.get("name", "")
            # pytest emits classname as the module dotted path — build
            # a node-id-ish string for consumer-side readability.
            file_path = classname.replace(".", "/") + ".py"
            nodeid = f"{file_path}::{name}"
            if tc.find("failure") is not None:
                failed += 1
                failing_ids.append(nodeid)
            elif tc.find("error") is not None:
                errored += 1
                failing_ids.append(nodeid)
            elif tc.find("skipped") is not None:
                skipped += 1
    passed = total - failed - errored - skipped

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "errored": errored,
        "skipped": skipped,
        "failing_test_ids": sorted(failing_ids),
    }


def run_cross_tenant_regression(
    paths: Optional[List[str]] = None,
    quiet: bool = True,
    timeout_secs: int = 300,
) -> Dict[str, Any]:
    """Run the umbrella cross-tenant regression suite as a subprocess.

    Args:
        paths: Optional override for test paths. Defaults to
            ``CROSS_TENANT_TEST_PATHS``.
        quiet: If True (default) pytest runs with ``--no-header -q``.
        timeout_secs: Kill the subprocess after this many seconds
            (default 300).

    Returns:
        dict with keys: env, git_sha, runner_identity, elapsed_secs,
        total_tests, passed, failed, errored, skipped, failing_test_ids,
        coverage_metadata, known_gaps, overall_status
        ('green' / 'red' / 'unknown'), summary_json (echoes the full
        shape for durable persistence).

        If the subprocess fails to run at all (missing python,
        cwd-broken, timeout) the return dict has ``total_tests: 0``
        and ``overall_status: 'unknown'`` plus a diagnostic
        ``subprocess_error`` field so the caller can surface the
        infra issue in the UI without confusing it with a red result.
    """
    if paths is None:
        paths = list(CROSS_TENANT_TEST_PATHS)

    # tempfile for pytest's JUnit XML output.
    with tempfile.NamedTemporaryFile(
        prefix="tbr_junit_", suffix=".xml", delete=False
    ) as tf:
        junit_path = tf.name

    pytest_args: List[str] = [
        sys.executable,
        "-m",
        "pytest",
        *paths,
        f"--junit-xml={junit_path}",
        "--tb=no",
        "-p", "no:cacheprovider",  # avoid touching .pytest_cache
    ]
    if quiet:
        pytest_args.extend(["--no-header", "-q"])

    started = time.monotonic()
    subprocess_error: Optional[str] = None
    try:
        completed = subprocess.run(
            pytest_args,
            capture_output=True,
            text=True,
            timeout=timeout_secs,
        )
        # pytest exit codes: 0=all passed, 1=some failed, 2=interrupted,
        # 3=internal error, 4=usage error, 5=no tests collected. Any of
        # 1-5 still emits JUnit XML we can parse.
        if completed.returncode not in {0, 1, 2, 5}:
            subprocess_error = (
                f"pytest exit code {completed.returncode}; "
                f"stderr={completed.stderr[:500]!r}"
            )
    except subprocess.TimeoutExpired:
        subprocess_error = f"pytest subprocess timed out after {timeout_secs}s"
    except (subprocess.SubprocessError, FileNotFoundError) as exc:
        subprocess_error = f"{type(exc).__name__}: {exc}"
    elapsed = time.monotonic() - started

    summary = _parse_junit_xml(junit_path)
    try:
        os.unlink(junit_path)
    except OSError:
        pass

    overall_status = "unknown"
    if summary["total_tests"] > 0:
        overall_status = (
            "green"
            if (summary["failed"] == 0 and summary["errored"] == 0)
            else "red"
        )

    result: Dict[str, Any] = {
        "env": _detect_env(),
        "git_sha": _detect_git_sha(),
        "runner_identity": _detect_runner_identity(),
        "elapsed_secs": round(elapsed, 3),
        "total_tests": summary["total_tests"],
        "passed": summary["passed"],
        "failed": summary["failed"],
        "errored": summary["errored"],
        "skipped": summary["skipped"],
        "failing_test_ids": summary["failing_test_ids"],
        "coverage_metadata": dict(COVERAGE_METADATA),
        "known_gaps": list(KNOWN_GAPS),
        "overall_status": overall_status,
    }
    if subprocess_error:
        result["subprocess_error"] = subprocess_error
    # Denormalized envelope: consumers that just want to persist a
    # single JSONB blob (e.g., the TenantBoundaryHealthReport model)
    # can grab summary_json directly.
    result["summary_json"] = {k: v for k, v in result.items() if k != "summary_json"}
    return result
