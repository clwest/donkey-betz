"""S2780 N22 v3 — zoom_out_tool PA-tool + governance ledger handler tests.

Locks nine contracts for the factored-out dedicated tool that promotes
``logs/zoom_out_classifications.jsonl`` from an ``ops_tool`` sub-action
(S2779) to a first-class ``zoom_out_tool`` (S2780) — per S2779 V6 fold
Trigger B firing (first non-Rigby consumer via Workspace UI) and S2780
T1 SIGN V7 folds A + B (semantic boundary erosion; same-PR factor-out
mandate per PLAYBOOK-6.10.8 future_trigger discipline).

  1. Default ``action`` is ``list``; unknown actions return a
     structured error.

  2. Missing log file returns fail-soft empty response with diagnostic
     note. ``malformed_lines_skipped: 0`` always present (schema
     consistency per S2779 T1 SIGN V2 fold).

  3. Advisory posture preserved on every response: ``advisory`` header,
     ``is_gate: False``, ``semantics: "advisory_pattern_evidence"``.

  4. Aggregates (``total_rows``, ``counts_by_classification``) computed
     across ALL rows, not just filtered tail.

  5. Filters compose: session (exact) + classification (enum) +
     arc (substring). Filter echo (``*_filter`` keys) present when
     applied.

  6. ``limit`` clamping: default 20, max 100, min 1 (negative values).
     ``0 = unset`` idiom.

  7. Malformed JSON lines skipped defensively.

  8. Path-traversal defense refuses BASE_DIR escapes.

  9. Unknown classification returns empty items list; aggregates
     unchanged.

Ratified: S2780 T1 Rigby joint SIGN — V1..V6 iteration produced
F-BLOCKING DISAGREE on V1 (Trigger B disposition) + V3 (home choice);
V7 zoom-out surfaced 2 folds classified ``same_pr_actionable`` (ledger
rows 19 + 20) and persisted before D-verdict per PLAYBOOK-6.10.8;
Chris D-verdict "A: ship factor-out + UI in GovernanceTab".
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from core.services.td_handlers_governance import GovernanceHandlersMixin


class _StubHandler:
    """Bare-bones host for the mixin method under test."""
    pass


class _ZoomOutToolHandler(GovernanceHandlersMixin, _StubHandler):
    pass


_SAMPLE_ROWS = [
    {
        "ts": "2026-07-13T00:00:00+00:00",
        "schema_version": 1,
        "session": 2774,
        "arc": "ops_urlconf_lambda_cleanup",
        "classification": "same_pr_actionable",
        "concern_text": "URLConf lambdas hide view refs.",
        "evidence_ref": "PR#3163",
        "backfilled": True,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-13T00:01:00+00:00",
        "schema_version": 1,
        "session": 2775,
        "arc": "session_freshness_beat",
        "classification": "same_pr_mitigatable",
        "concern_text": "Beat cadence too aggressive.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-13T00:02:00+00:00",
        "schema_version": 1,
        "session": 2778,
        "arc": "playbook_v0_7_0_zoom_out_discipline",
        "classification": "future_trigger",
        "concern_text": "Amendment-cycle cadence risk.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
    {
        "ts": "2026-07-13T00:03:00+00:00",
        "schema_version": 1,
        "session": 2780,
        "arc": "n22v3_zoom_out_ledger_workspace_ui",
        "classification": "same_pr_actionable",
        "concern_text": "V7 fold — trigger B forces factor-out.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
]


class ZoomOutToolTests(SimpleTestCase):

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "logs").mkdir()
        self.handler = _ZoomOutToolHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_ledger(self, rows, extra_lines=None):
        path = self.tmpdir / "logs" / "zoom_out_classifications.jsonl"
        lines = [json.dumps(r) for r in rows]
        if extra_lines:
            lines.extend(extra_lines)
        path.write_text("\n".join(lines) + "\n")
        return path

    def _dispatch(self, payload=None):
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            return self.handler._handle_zoom_out(
                "zoom_out_tool", payload or {}, user_id=None, trace_id="trace-test"
            )

    def _list(self, payload=None):
        base = {"action": "list"}
        if payload:
            base.update(payload)
        return self._dispatch(base)

    # ── Contract 1: dispatch shape ───────────────────────────────────────
    def test_default_action_is_list(self):
        result = self._dispatch({})  # no action -> defaults to list
        self.assertEqual(result["action"], "list")

    def test_unknown_action_returns_error(self):
        result = self._dispatch({"action": "nonexistent"})
        self.assertIn("error", result)
        self.assertIn("Unknown zoom_out_tool action", result["error"])

    # ── Contract 2: missing file, fail-soft ──────────────────────────────
    def test_missing_log_returns_soft_empty_with_note(self):
        result = self._list()
        self.assertEqual(result["action"], "list")
        self.assertFalse(result["log_exists"])
        self.assertEqual(result["items"], [])
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["total_rows"], 0)
        self.assertEqual(result["counts_by_classification"], {})
        self.assertEqual(result["malformed_lines_skipped"], 0)
        self.assertIn("note", result)
        self.assertIn("record_zoom_out_concern", result["note"])

    # ── Contract 3: advisory posture on every response ───────────────────
    def test_advisory_posture_on_empty_response(self):
        result = self._list()
        self.assertIn("pattern evidence", result["advisory"])
        self.assertFalse(result["is_gate"])
        self.assertEqual(result["semantics"], "advisory_pattern_evidence")

    def test_advisory_posture_on_populated_response(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list()
        self.assertIn("pattern evidence", result["advisory"])
        self.assertFalse(result["is_gate"])
        self.assertEqual(result["semantics"], "advisory_pattern_evidence")

    # ── Contract 4: aggregates over full ledger ──────────────────────────
    def test_total_rows_and_counts_span_full_ledger(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"limit": 2})
        self.assertEqual(result["total_rows"], 4)
        self.assertEqual(
            result["counts_by_classification"],
            {
                "same_pr_actionable": 2,
                "same_pr_mitigatable": 1,
                "future_trigger": 1,
            },
        )
        # limit narrows items but not aggregates
        self.assertEqual(result["count"], 2)

    # ── Contract 5: filter composition ───────────────────────────────────
    def test_filter_by_session(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"session": 2774})
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["session"], 2774)
        self.assertEqual(result["session_filter"], 2774)

    def test_filter_by_classification(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"classification": "same_pr_actionable"})
        self.assertEqual(result["count"], 2)
        for row in result["items"]:
            self.assertEqual(row["classification"], "same_pr_actionable")
        self.assertEqual(result["classification_filter"], "same_pr_actionable")

    def test_filter_by_arc_substring(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"arc": "ops_urlconf"})
        self.assertEqual(result["count"], 1)
        self.assertIn("ops_urlconf", result["items"][0]["arc"])
        self.assertEqual(result["arc_filter"], "ops_urlconf")

    def test_composed_filters_intersect(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({
            "classification": "same_pr_actionable",
            "session": 2780,
        })
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["session"], 2780)
        self.assertEqual(result["items"][0]["classification"], "same_pr_actionable")

    # ── Contract 6: limit clamping ───────────────────────────────────────
    def test_limit_defaults_to_20(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list()
        self.assertEqual(result["limit"], 20)

    def test_limit_clamped_to_max_100(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"limit": 500})
        self.assertEqual(result["limit"], 100)

    def test_limit_clamped_to_min_1_on_negative(self):
        # Negative values are truthy so bypass the `or 20` fallback and
        # exercise the max(1, ...) clamp directly.
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"limit": -5})
        self.assertEqual(result["limit"], 1)
        self.assertEqual(result["count"], 1)

    def test_limit_zero_falls_back_to_default(self):
        # 0 is falsy — matches _ops_recent_recycles idiom: "0 = unset".
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"limit": 0})
        self.assertEqual(result["limit"], 20)

    def test_limit_returns_tail_window(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"limit": 2})
        self.assertEqual(result["count"], 2)
        # Tail — last two rows in append order
        self.assertEqual(result["items"][0]["session"], 2778)
        self.assertEqual(result["items"][1]["session"], 2780)

    # ── Contract 7: malformed lines skipped defensively ──────────────────
    def test_malformed_lines_skipped(self):
        self._write_ledger(
            _SAMPLE_ROWS,
            extra_lines=[
                "{not valid json",
                "[]",  # valid JSON but not a dict
            ],
        )
        result = self._list()
        self.assertEqual(result["total_rows"], 4)
        self.assertEqual(result["malformed_lines_skipped"], 2)

    def test_malformed_lines_skipped_field_present_when_zero(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list()
        self.assertIn("malformed_lines_skipped", result)
        self.assertEqual(result["malformed_lines_skipped"], 0)

    # ── Contract 8: path-traversal defense ───────────────────────────────
    def test_path_traversal_refused(self):
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            with patch(
                "pathlib.Path.resolve",
                lambda self, strict=False: Path("/etc") / self.name,
            ):
                result = self.handler._handle_zoom_out(
                    "zoom_out_tool", {"action": "list"}, user_id=None, trace_id="trace-test"
                )
        self.assertFalse(result["log_exists"])
        self.assertIn("outside BASE_DIR", result["note"])
        self.assertFalse(result["is_gate"])

    # ── Contract 9: unknown classification returns empty list ────────────
    def test_unknown_classification_returns_empty_items(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"classification": "nonexistent_enum"})
        self.assertEqual(result["count"], 0)
        # Aggregates still reflect full ledger
        self.assertEqual(result["total_rows"], 4)

    # ── Contract 10: LLM autofill guard on session=0 ─────────────────────
    def test_session_zero_treated_as_unset(self):
        # LLM commonly autofills integer params with 0. session=0 is
        # never a real session number; it must be treated as "no filter"
        # so filter combinations don't silently drop all rows.
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"session": 0})
        # No session_filter echo when 0 is guard-dropped.
        self.assertNotIn("session_filter", result)
        # Items reflect full ledger (up to limit).
        self.assertEqual(result["count"], 4)

    def test_session_negative_treated_as_unset(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._list({"session": -1})
        self.assertNotIn("session_filter", result)
        self.assertEqual(result["count"], 4)
