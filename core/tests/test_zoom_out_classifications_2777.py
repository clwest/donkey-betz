"""S2777 N22 — zoom-out classification ledger tests.

Locks three contracts introduced this session:

  1. ``record_zoom_out_concern`` appends a 7-field row (schema_version=1)
     to ``logs/zoom_out_classifications.jsonl``. Validates classification
     enum. Refuses empty ``--concern`` or ``--arc``. Preserves the
     ``--backfilled`` flag + optional ``--evidence-ref``.

  2. ``zoom_out_streak_report`` reads the JSONL, counts per classification,
     filters by ``--classification``/``--session``, and emits JSON on
     ``--as-json``. Advisory header ("pattern evidence for review")
     appears in both text and JSON output.

  3. Both commands honor ``--log-path`` override so tests avoid touching
     the real ``logs/`` directory.

Ratified: S2777 Rigby joint SIGN (Q1 AGREE JSONL, Q2 AGREE manual, Q3
AGREE backfill, Q4 AGREE CLI-only) + explicit DISAGREE on Claude's
original "PLAYBOOK-6.10 two-triggers threshold" rationale (rewritten to
"evidence substrate for a future rule that does not exist yet") + one
new same-PR-mitigatable concern (schema ossification) folded in via
``schema_version`` + additive-only field evolution + advisory report
language. Chris D-verdict yes.
"""
from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from django.core.management import call_command
from django.core.management.base import CommandError


def _read_rows(path: Path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class RecordZoomOutConcernTests(TestCase):
    """Write path — enum validation, required fields, backfilled flag."""

    def _log_path(self, tmp):
        return Path(tmp) / "zoom_out.jsonl"

    def test_valid_write_appends_seven_field_row(self):
        with TemporaryDirectory() as tmp:
            log_path = self._log_path(tmp)
            call_command(
                "record_zoom_out_concern",
                "--session", "2774",
                "--arc", "ops_urlconf_lambda_cleanup",
                "--concern", "URLConf lambdas hide view refs from static analysis.",
                "--classification", "same_pr_actionable",
                "--evidence-ref", "PR#3163",
                "--entered-by", "claude",
                "--log-path", str(log_path),
            )
            rows = _read_rows(log_path)
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["schema_version"], 1)
            self.assertEqual(row["session"], 2774)
            self.assertEqual(row["arc"], "ops_urlconf_lambda_cleanup")
            self.assertEqual(row["classification"], "same_pr_actionable")
            self.assertEqual(row["evidence_ref"], "PR#3163")
            self.assertFalse(row["backfilled"])
            self.assertEqual(row["entered_by"], "claude")
            self.assertIn("ts", row)
            self.assertIn("concern_text", row)

    def test_invalid_classification_raises(self):
        with TemporaryDirectory() as tmp:
            log_path = self._log_path(tmp)
            with self.assertRaises((CommandError, SystemExit)):
                call_command(
                    "record_zoom_out_concern",
                    "--session", "2777",
                    "--arc", "test",
                    "--concern", "x",
                    "--classification", "bogus_class",
                    "--log-path", str(log_path),
                )
            # File should not be created for a rejected classification.
            self.assertFalse(log_path.exists())

    def test_empty_concern_raises(self):
        with TemporaryDirectory() as tmp:
            log_path = self._log_path(tmp)
            with self.assertRaises(CommandError):
                call_command(
                    "record_zoom_out_concern",
                    "--session", "2777",
                    "--arc", "test",
                    "--concern", "   ",
                    "--classification", "future_trigger",
                    "--log-path", str(log_path),
                )
            self.assertFalse(log_path.exists())

    def test_empty_arc_raises(self):
        with TemporaryDirectory() as tmp:
            log_path = self._log_path(tmp)
            with self.assertRaises(CommandError):
                call_command(
                    "record_zoom_out_concern",
                    "--session", "2777",
                    "--arc", "",
                    "--concern", "x",
                    "--classification", "future_trigger",
                    "--log-path", str(log_path),
                )
            self.assertFalse(log_path.exists())

    def test_evidence_ref_optional_defaults_to_none(self):
        with TemporaryDirectory() as tmp:
            log_path = self._log_path(tmp)
            call_command(
                "record_zoom_out_concern",
                "--session", "2777",
                "--arc", "test",
                "--concern", "no evidence ref given",
                "--classification", "same_pr_mitigatable",
                "--log-path", str(log_path),
            )
            rows = _read_rows(log_path)
            self.assertIsNone(rows[0]["evidence_ref"])

    def test_backfilled_flag_marks_row(self):
        with TemporaryDirectory() as tmp:
            log_path = self._log_path(tmp)
            call_command(
                "record_zoom_out_concern",
                "--session", "2774",
                "--arc", "hist",
                "--concern", "historical seed",
                "--classification", "same_pr_actionable",
                "--backfilled",
                "--log-path", str(log_path),
            )
            rows = _read_rows(log_path)
            self.assertTrue(rows[0]["backfilled"])


class ZoomOutStreakReportTests(TestCase):
    """Read path — counts, filters, JSON emission, advisory header."""

    def _seed(self, log_path: Path, rows):
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    def test_empty_ledger_reports_zero(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "zoom_out.jsonl"
            out = StringIO()
            call_command(
                "zoom_out_streak_report",
                "--log-path", str(log_path),
                stdout=out,
            )
            text = out.getvalue()
            self.assertIn("Total rows: 0", text)
            self.assertIn("pattern evidence for review", text)

    def test_counts_by_classification_across_mixed_rows(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "zoom_out.jsonl"
            self._seed(
                log_path,
                [
                    {"session": 2774, "arc": "a", "classification": "same_pr_actionable", "concern_text": "x"},
                    {"session": 2774, "arc": "a", "classification": "same_pr_actionable", "concern_text": "x"},
                    {"session": 2775, "arc": "b", "classification": "same_pr_mitigatable", "concern_text": "x"},
                    {"session": 2776, "arc": "c", "classification": "future_trigger", "concern_text": "x"},
                ],
            )
            out = StringIO()
            call_command(
                "zoom_out_streak_report",
                "--as-json",
                "--log-path", str(log_path),
                stdout=out,
            )
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["total_rows"], 4)
            self.assertEqual(payload["counts_by_classification"]["same_pr_actionable"], 2)
            self.assertEqual(payload["counts_by_classification"]["same_pr_mitigatable"], 1)
            self.assertEqual(payload["counts_by_classification"]["future_trigger"], 1)
            self.assertIn("pattern evidence for review", payload["advisory"])

    def test_classification_filter_narrows_rows(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "zoom_out.jsonl"
            self._seed(
                log_path,
                [
                    {"session": 2774, "arc": "a", "classification": "same_pr_actionable", "concern_text": "x"},
                    {"session": 2775, "arc": "b", "classification": "same_pr_mitigatable", "concern_text": "y"},
                ],
            )
            out = StringIO()
            call_command(
                "zoom_out_streak_report",
                "--classification", "same_pr_actionable",
                "--as-json",
                "--log-path", str(log_path),
                stdout=out,
            )
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["total_rows"], 1)
            self.assertEqual(payload["rows"][0]["session"], 2774)

    def test_session_filter_narrows_rows(self):
        with TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "zoom_out.jsonl"
            self._seed(
                log_path,
                [
                    {"session": 2774, "arc": "a", "classification": "same_pr_actionable", "concern_text": "x"},
                    {"session": 2775, "arc": "b", "classification": "same_pr_mitigatable", "concern_text": "y"},
                ],
            )
            out = StringIO()
            call_command(
                "zoom_out_streak_report",
                "--session", "2775",
                "--as-json",
                "--log-path", str(log_path),
                stdout=out,
            )
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["total_rows"], 1)
            self.assertEqual(payload["rows"][0]["session"], 2775)
