"""
tests/security/test_i0302_p4_coverage_gap_report.py — I-0302 Phase 4
Sub-phase 3 deferred-surface coverage-gap report emitter.

Contract refs:
  docs/research/implementation/tenant_boundary_lockdown/
      I-030203_phase4_harness_architecture.md §4.2 (report format)
      I-030203_phase4_harness_architecture.md §4.3 (posture probes)
      I-030201_model_audit_ledger.md §5.3.b / §5.1.a / §5.5.a
      (deferred-surface amendments)

**What this emits.** A structured JSON report at
`test_reports/i0302_p4_coverage_gaps.json` enumerating the three
deferred surface classes from the Phase 3 wiring ledger:

  - §5.3.b — ChatConversation ~126 non-view sites across ~43 files
             (C2 deferred pending Phase 0 multi-tenant flip)
  - §5.1.a — Deliverable non-view sites (distribution_agent, tasks,
             mission_runner — D-followup deferred)
  - §5.5.a — Document WebSocket sites (content/consumers.py —
             D2-followup deferred pending I-0303 async-boundary)

**Informational only.** Never test-fail-on-gap. The report is attached
to the Phase 4 close ratification for audit visibility per §4.2:
"Skips-without-reporting = invisible debt."

**Posture probes (§4.3).** Every deferred surface class in the current
manifest is either non-HTTP-addressable (services / Celery tasks /
agent + Employee-OS code paths) or WebSocket (probe-exempt). All rows
today ship `posture_probed: false` with a documented probe policy.
The probe-machinery structure is in place so a future HTTP-addressable
deferred surface can flip a row to probed without redesign.

**Live enumeration cross-check.** For each surface with a documented
grep pattern, the report includes a `live_enumeration` block with
current-HEAD site counts. Readers can spot drift between the
ledger-ratified count and observed reality — no test fails on drift
today, so ledger amendments remain manual (per Playbook §14 two-triggers
threshold).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "test_reports"
REPORT_PATH = REPORT_DIR / "i0302_p4_coverage_gaps.json"


# --------------------------------------------------------------------------
# Ratified deferred-surface manifest
#
# Sourced from I-030201 ledger amendments §5.1.a / §5.3.b / §5.5.a as of
# HEAD 9ea4475b (S2749 close). Any addition here requires a corresponding
# ledger amendment; drop-outs require an amendment plus a Phase 4 close
# criterion revisit.
# --------------------------------------------------------------------------


DEFERRED_SURFACES: list[dict] = [
    {
        "surface_id": "5.3.b",
        "model": "ChatConversation",
        "sub_phase": "C2",
        "sites_deferred_ledger": 126,
        "files_deferred_ledger": 43,
        "ledger_ref": (
            "docs/research/implementation/tenant_boundary_lockdown/"
            "I-030201_model_audit_ledger.md#§5.3.b"
        ),
        "expected_close": (
            "post-Phase-0-multi-tenant OR entry-criteria-triggered reopen"
        ),
        "entry_criteria_summary": (
            "Phase 0 multi-tenant enablement scheduled; new staff/support "
            "role; WebSocket/Discord exposed to non-Chris users; regression "
            "or CVE-class finding traces to C2-scope file"
        ),
        "rigby_inventory_deliverable": "7e3596c8-0f39-4600-a38a-31733fa55b18",
        "auth_mapping_exemptions": [
            "core/services/discord_bot.py — discord_user_id mapping",
            "core/tasks_conversations.py — system-context Celery",
            "core/tasks_misc.py — system-context Celery",
            "core/jobs/docs_cascade.py — system runner",
            "core/tasks.py:12100 cleanup — system-context",
        ],
        "posture_probed": False,
        "posture_probe_policy": (
            "non-HTTP-addressable — sites are services / Celery tasks / "
            "Discord bot / consumers / mgmt commands / tests; no cheap "
            "posture probe applies"
        ),
        "live_enumeration": {
            "grep_pattern": r"ChatConversation\.objects\.",
            "excluded_view_files": [
                "core/views_personal_assistant.py",
                "core/views_session_handoff.py",
                "core/views_project_hub.py",
            ],
        },
    },
    {
        "surface_id": "5.1.a",
        "model": "Deliverable",
        "sub_phase": "D-followup",
        "sites_deferred_ledger": 4,
        "files_deferred_ledger": 3,
        "ledger_ref": (
            "docs/research/implementation/tenant_boundary_lockdown/"
            "I-030201_model_audit_ledger.md#§5.1.a"
        ),
        "expected_close": (
            "post-Phase-0-multi-tenant OR entry-criteria-triggered reopen"
        ),
        "entry_criteria_summary": (
            "Phase 0 multi-tenant flip; new staff/support role; external "
            "user exposure; regression finding traces to D1-scope file"
        ),
        "specific_sites": [
            {
                "file": "core/agents/distribution_agent.py",
                "line": 189,
                "role": "agent code path",
            },
            {
                "file": "core/tasks.py",
                "line": None,
                "role": "mixed Celery system-context .get(id=...) paths",
            },
            {
                "file": "core/employees/mission_runner.py",
                "line": 1305,
                "role": "Employee OS system code path",
            },
            {
                "file": "core/employees/mission_runner.py",
                "line": 1434,
                "role": "Employee OS system code path",
            },
        ],
        "posture_probed": False,
        "posture_probe_policy": (
            "non-HTTP-addressable — internal agent / Celery / Employee OS "
            "code paths; no cheap posture probe applies"
        ),
        "live_enumeration_policy": (
            "hand-picked ledger set — a raw grep for Deliverable.objects.get "
            "would also match already-scoped .get(id=x, user=user) callers "
            "and yield noise; specific_sites is the authoritative list"
        ),
    },
    {
        "surface_id": "5.5.a",
        "model": "Document",
        "sub_phase": "D2-followup",
        "sites_deferred_ledger": 3,
        "files_deferred_ledger": 1,
        "ledger_ref": (
            "docs/research/implementation/tenant_boundary_lockdown/"
            "I-030201_model_audit_ledger.md#§5.5.a"
        ),
        "expected_close": (
            "post-I-0303 async-boundary enforcement OR Phase 0 flip"
        ),
        "entry_criteria_summary": (
            "WebSocket auth-model crystallization at Phase 0; I-0303 "
            "async-boundary arc opens"
        ),
        "specific_sites": [
            {
                "file": "content/consumers.py",
                "line": 288,
                "role": "WebSocket consumer — AMBIGUOUS per Phase 1 §5.5",
            },
            {
                "file": "content/consumers.py",
                "line": 320,
                "role": "WebSocket consumer — AMBIGUOUS per Phase 1 §5.5",
            },
            {
                "file": "content/consumers.py",
                "line": 508,
                "role": (
                    "WebSocket consumer — already SCOPED; retained for "
                    "I-0303 async-boundary review"
                ),
            },
        ],
        "posture_probed": False,
        "posture_probe_policy": (
            "WebSocket surface probe-exempt per I-030203 §4.3 "
            "(WebSocket handshakes are flaky under CI without a channels "
            "layer; probe would trade rigor for maintenance)"
        ),
        "live_enumeration_policy": (
            "hand-picked ledger set — 3 known content/consumers.py lines; "
            "no grep-derived count to cross-check"
        ),
    },
]


# --------------------------------------------------------------------------
# Live enumeration — grep for current site counts, cross-check ledger drift
# --------------------------------------------------------------------------


# Directory prefixes to skip during the walk. Cheap top-level excludes; the
# ledger methodology walked the entire repo root, so we mirror that.
_WALK_EXCLUDES = (
    "/.venv/",
    "/venv/",
    "/env/",
    "/node_modules/",
    "/.git/",
    "/site-packages/",
    "/__pycache__/",
    "/build/",
    "/dist/",
    "/.mypy_cache/",
    "/.pytest_cache/",
    "/.ruff_cache/",
)


def _iter_python_files() -> list[Path]:
    """Return sorted list of .py files under REPO_ROOT, excluding vendor dirs."""
    out: list[Path] = []
    for py_path in REPO_ROOT.rglob("*.py"):
        posix = py_path.as_posix()
        if any(exc in posix for exc in _WALK_EXCLUDES):
            continue
        out.append(py_path)
    return sorted(out)


def _live_enumerate(surface: dict) -> dict | None:
    """Run the surface's live_enumeration grep, if configured.

    Returns a dict with sites_observed (total pattern hits) and
    files_observed (files with at least one hit), excluding the wired
    view files documented in the surface manifest.
    """
    live = surface.get("live_enumeration")
    if not live:
        return None

    pattern = re.compile(live["grep_pattern"])
    excluded_view_files = set(live.get("excluded_view_files", []))

    matches_total = 0
    files_matched: set[str] = set()

    for py_path in _iter_python_files():
        rel = py_path.relative_to(REPO_ROOT).as_posix()
        if rel in excluded_view_files:
            continue
        try:
            src = py_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        file_hits = len(pattern.findall(src))
        if file_hits:
            matches_total += file_hits
            files_matched.add(rel)

    return {
        "grep_pattern": live["grep_pattern"],
        "excluded_view_files": sorted(excluded_view_files),
        "sites_observed": matches_total,
        "files_observed": len(files_matched),
    }


# --------------------------------------------------------------------------
# Report writer
# --------------------------------------------------------------------------


def _head_sha() -> str:
    """Best-effort HEAD sha for provenance; falls back to 'unknown'."""
    try:
        head_file = REPO_ROOT / ".git" / "HEAD"
        head_ref = head_file.read_text().strip()
        if head_ref.startswith("ref: "):
            ref_path = REPO_ROOT / ".git" / head_ref[5:]
            return ref_path.read_text().strip()[:12]
        return head_ref[:12]
    except OSError:
        return "unknown"


def _build_payload() -> dict:
    """Build the report payload with deterministic ordering (Rigby SIGN S2750)."""
    surfaces_out: list[dict] = []
    for surface in DEFERRED_SURFACES:
        row = {k: v for k, v in surface.items() if k != "live_enumeration"}
        # Deterministic ordering of specific_sites (by file, line).
        if "specific_sites" in row:
            row["specific_sites"] = sorted(
                row["specific_sites"],
                key=lambda s: (s["file"], s.get("line") or 0),
            )
        live = _live_enumerate(surface)
        if live is not None:
            row["live_enumeration"] = live
        surfaces_out.append(row)

    # Deterministic ordering of surfaces themselves (by surface_id).
    surfaces_out.sort(key=lambda r: r["surface_id"])

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "head_sha": _head_sha(),
        "report_id": "i0302-p4-coverage-gaps",
        "mode": "informational",
        "contract_ref": (
            "docs/research/implementation/tenant_boundary_lockdown/"
            "I-030203_phase4_harness_architecture.md#§4.2"
        ),
        "deferred_surfaces": surfaces_out,
        "summary": {
            "surfaces_total": len(surfaces_out),
            "sites_deferred_ledger_total": sum(
                s["sites_deferred_ledger"] for s in DEFERRED_SURFACES
            ),
            "files_deferred_ledger_total": sum(
                s["files_deferred_ledger"] for s in DEFERRED_SURFACES
            ),
            "posture_probes_run": sum(
                1 for s in DEFERRED_SURFACES if s.get("posture_probed")
            ),
        },
    }


def _write_report(payload: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True))


# --------------------------------------------------------------------------
# Pytest tests
# --------------------------------------------------------------------------


def test_coverage_gap_report_emit() -> None:
    """Emit the deferred-surface coverage-gap report.

    Informational only — never fails on missing coverage per I-030203 §4.2.
    """
    payload = _build_payload()
    _write_report(payload)


def test_coverage_gap_report_shape_ok() -> None:
    """Confirm the JSON report was written and its shape is valid."""
    assert REPORT_PATH.exists(), (
        f"Expected report at {REPORT_PATH}. Run the emit test first."
    )
    payload = json.loads(REPORT_PATH.read_text())
    assert payload["report_id"] == "i0302-p4-coverage-gaps"
    assert payload["schema_version"] == 1
    assert payload["mode"] == "informational"
    assert isinstance(payload["deferred_surfaces"], list)
    assert payload["summary"]["surfaces_total"] == len(payload["deferred_surfaces"])

    # Deterministic ordering (Rigby SIGN S2750): surfaces sorted by surface_id;
    # each surface's specific_sites sorted by (file, line).
    surface_ids = [row["surface_id"] for row in payload["deferred_surfaces"]]
    assert surface_ids == sorted(surface_ids), (
        f"Surfaces not sorted by surface_id: {surface_ids}"
    )
    for row in payload["deferred_surfaces"]:
        sites = row.get("specific_sites", [])
        site_keys = [(s["file"], s.get("line") or 0) for s in sites]
        assert site_keys == sorted(site_keys), (
            f"specific_sites not deterministically sorted in "
            f"{row['surface_id']}: {site_keys}"
        )
    for row in payload["deferred_surfaces"]:
        for field in (
            "surface_id",
            "model",
            "sub_phase",
            "sites_deferred_ledger",
            "files_deferred_ledger",
            "ledger_ref",
            "expected_close",
            "posture_probed",
            "posture_probe_policy",
        ):
            assert field in row, (
                f"Missing required field '{field}' in row {row.get('surface_id')}"
            )


def test_deferred_surface_ledger_refs_resolve() -> None:
    """Each surface's ledger_ref file component resolves to a real file.

    Anchor components (#§X.Y.z) are not validated — Markdown anchors don't
    render as HTML IDs deterministically; the file existence is what matters
    for the audit-trail contract.
    """
    for surface in DEFERRED_SURFACES:
        ref = surface["ledger_ref"]
        file_component = ref.split("#", 1)[0]
        file_path = REPO_ROOT / file_component
        assert file_path.exists(), (
            f"Ledger ref does not resolve to a file: {ref}"
        )


def test_specific_sites_files_exist() -> None:
    """Each hard-coded site.file in a surface manifest resolves to a real file.

    Line numbers are best-effort at snapshot time and may drift; the file's
    existence keeps the report referenceable for auditors chasing the pointer.
    """
    for surface in DEFERRED_SURFACES:
        for site in surface.get("specific_sites", []):
            site_file = site["file"]
            assert (REPO_ROOT / site_file).exists(), (
                f"Deferred site file missing on disk: {site_file} "
                f"(surface {surface['surface_id']})"
            )
