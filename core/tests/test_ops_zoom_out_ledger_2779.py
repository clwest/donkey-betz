"""S2779 N22 v2 — ops_tool.zoom_out_ledger PA-tool read surface tests.

Locks eight contracts for the new read action that promotes
``logs/zoom_out_classifications.jsonl`` from CLI-only
(``zoom_out_streak_report``) to a Rigby-consumable PA tool action:

  1. Missing log file returns fail-soft empty response with diagnostic
     note. ``malformed_lines_skipped: 0`` is present (schema consistency
     per S2779 T1 SIGN V2 fold — always emit the field, even when zero).

  2. Advisory posture is preserved: every response embeds ``advisory``
     header, ``is_gate: False``, and ``semantics: "advisory_pattern_evidence"``
     per S2779 T1 SIGN V4 fold to prevent advisory→gate drift.

  3. Valid ledger reads return ``total_rows`` + ``counts_by_classification``
     aggregates computed across ALL rows (not just filtered tail).

  4. Filters compose: session (exact match) + classification (enum) +
     arc (substring) narrow the ``items`` list while aggregates remain
     over the full ledger.

  5. ``limit`` is clamped to [1, 100] and defaults to 20.

  6. Malformed JSON lines are skipped defensively; the count surfaces
     in ``malformed_lines_skipped``.

  7. Path-traversal defense: BASE_DIR escapes are refused with a
     diagnostic note.

  8. Filter echo: when a filter is applied, the corresponding
     ``*_filter`` key echoes back in the response (for operator
     transparency).

Ratified: S2779 T1 Rigby joint SIGN V1..V6 AGREE (V6 fold classified
``future_trigger`` and persisted to ledger before D-verdict per
PLAYBOOK-6.10.8) + Chris D-verdict "ship it".
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from core.services.td_handlers_ops import OpsHandlersMixin


class _StubHandler:
    """Bare-bones host for the mixin method under test."""
    pass


class _ZoomOutLedgerHandler(OpsHandlersMixin, _StubHandler):
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
        "session": 2779,
        "arc": "n22v2_zoom_out_pa_tool_read_surface",
        "classification": "same_pr_actionable",
        "concern_text": "V2 fold — malformed_lines_skipped consistency.",
        "evidence_ref": None,
        "backfilled": False,
        "entered_by": "claude",
    },
]


class ZoomOutLedgerActionTests(SimpleTestCase):

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        (self.tmpdir / "logs").mkdir()
        self.handler = _ZoomOutLedgerHandler()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_ledger(self, rows, extra_lines=None):
        path = self.tmpdir / "logs" / "zoom_out_classifications.jsonl"
        lines = [json.dumps(r) for r in rows]
        if extra_lines:
            lines.extend(extra_lines)
        path.write_text("\n".join(lines) + "\n")
        return path

    def _call(self, payload=None):
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            return self.handler._ops_zoom_out_ledger(
                payload or {}, trace_id="trace-test"
            )

    # ── Contract 1: missing file, fail-soft ──────────────────────────────
    def test_missing_log_returns_soft_empty_with_note(self):
        result = self._call()
        self.assertEqual(result["action"], "zoom_out_ledger")
        self.assertFalse(result["log_exists"])
        self.assertEqual(result["items"], [])
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["total_rows"], 0)
        self.assertEqual(result["counts_by_classification"], {})
        self.assertEqual(result["malformed_lines_skipped"], 0)
        self.assertIn("note", result)
        self.assertIn("record_zoom_out_concern", result["note"])

    # ── Contract 2: advisory posture on every response ───────────────────
    def test_advisory_posture_on_empty_response(self):
        result = self._call()
        self.assertIn("pattern evidence", result["advisory"])
        self.assertFalse(result["is_gate"])
        self.assertEqual(result["semantics"], "advisory_pattern_evidence")

    def test_advisory_posture_on_populated_response(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call()
        self.assertIn("pattern evidence", result["advisory"])
        self.assertFalse(result["is_gate"])
        self.assertEqual(result["semantics"], "advisory_pattern_evidence")

    # ── Contract 3: aggregates over full ledger ──────────────────────────
    def test_total_rows_and_counts_span_full_ledger(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"limit": 2})
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

    # ── Contract 4: filter composition ───────────────────────────────────
    def test_filter_by_session(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"session": 2774})
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["session"], 2774)
        self.assertEqual(result["session_filter"], 2774)

    def test_filter_by_classification(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"classification": "same_pr_actionable"})
        self.assertEqual(result["count"], 2)
        for row in result["items"]:
            self.assertEqual(row["classification"], "same_pr_actionable")
        self.assertEqual(result["classification_filter"], "same_pr_actionable")

    def test_filter_by_arc_substring(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"arc": "ops_urlconf"})
        self.assertEqual(result["count"], 1)
        self.assertIn("ops_urlconf", result["items"][0]["arc"])
        self.assertEqual(result["arc_filter"], "ops_urlconf")

    def test_composed_filters_intersect(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({
            "classification": "same_pr_actionable",
            "session": 2779,
        })
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["session"], 2779)
        self.assertEqual(result["items"][0]["classification"], "same_pr_actionable")

    # ── Contract 5: limit clamping ───────────────────────────────────────
    def test_limit_defaults_to_20(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call()
        self.assertEqual(result["limit"], 20)

    def test_limit_clamped_to_max_100(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"limit": 500})
        self.assertEqual(result["limit"], 100)

    def test_limit_clamped_to_min_1(self):
        # Negative values are truthy so bypass the `or 20` fallback and
        # exercise the max(1, ...) clamp directly.
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"limit": -5})
        self.assertEqual(result["limit"], 1)
        self.assertEqual(result["count"], 1)

    def test_limit_zero_falls_back_to_default(self):
        # 0 is falsy — matches _ops_recent_recycles idiom: "0 = unset".
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"limit": 0})
        self.assertEqual(result["limit"], 20)

    def test_limit_returns_tail_window(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"limit": 2})
        self.assertEqual(result["count"], 2)
        # Tail — last two rows in append order
        self.assertEqual(result["items"][0]["session"], 2778)
        self.assertEqual(result["items"][1]["session"], 2779)

    # ── Contract 6: malformed lines skipped defensively ──────────────────
    def test_malformed_lines_skipped(self):
        self._write_ledger(
            _SAMPLE_ROWS,
            extra_lines=[
                "{not valid json",
                "[]",  # valid JSON but not a dict
            ],
        )
        result = self._call()
        self.assertEqual(result["total_rows"], 4)
        self.assertEqual(result["malformed_lines_skipped"], 2)

    def test_malformed_lines_skipped_field_present_when_zero(self):
        # S2779 T1 SIGN V2 fold — schema consistency
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call()
        self.assertIn("malformed_lines_skipped", result)
        self.assertEqual(result["malformed_lines_skipped"], 0)

    # ── Contract 7: path-traversal defense ───────────────────────────────
    def test_path_traversal_refused(self):
        # Force a resolved log_path that escapes BASE_DIR by pointing
        # BASE_DIR at a nested tmpdir whose logs/ resolves outside.
        with patch("django.conf.settings.BASE_DIR", str(self.tmpdir)):
            with patch(
                "pathlib.Path.resolve",
                lambda self, strict=False: Path("/etc") / self.name,
            ):
                result = self.handler._ops_zoom_out_ledger(
                    {}, trace_id="trace-test"
                )
        self.assertFalse(result["log_exists"])
        self.assertIn("outside BASE_DIR", result["note"])
        self.assertFalse(result["is_gate"])

    # ── Contract 8: unknown classification returns empty list ────────────
    def test_unknown_classification_returns_empty_items(self):
        self._write_ledger(_SAMPLE_ROWS)
        result = self._call({"classification": "nonexistent_enum"})
        self.assertEqual(result["count"], 0)
        # Aggregates still reflect full ledger
        self.assertEqual(result["total_rows"], 4)
