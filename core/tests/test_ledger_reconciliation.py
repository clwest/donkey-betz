"""Tests for the S3041 meta-fix — ledger reconciliation enforcement.

Covers three layers:

1. ``core.services.ledger_reconciliation.extract_ledger_references`` +
   ``detect_flipped_entries`` — pure-Python parsing invariants.

2. ``check_ledger_reconciliation_at_close`` — the enforcement decision
   layer. Refuse path (drift + no escape), allow path (escape flag),
   silent no-op paths (no handoff / no references).

3. ``check_ledger_reconciliation`` standalone management command — CLI
   integration. Same handoff → deliverable check without close side
   effects.

Run::

    python manage.py test core.tests.test_ledger_reconciliation -v2
"""
from __future__ import annotations

import tempfile
import uuid
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.ledger_reconciliation import (
    DEFAULT_LEDGER_DELIVERABLE_ID,
    LedgerReconciliationError,
    check_ledger_reconciliation_at_close,
    detect_flipped_entries,
    extract_ledger_references,
)


def _write_handoff(text: str) -> Path:
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8",
    )
    f.write(text)
    f.close()
    return Path(f.name)


class ExtractLedgerReferencesTests(TestCase):
    """Parse-invariant tests — no DB, no CLI."""

    def test_extracts_single_reference(self):
        self.assertEqual(extract_ledger_references("touched Ledger #5"), [5])

    def test_extracts_multiple_references_sorted_unique(self):
        text = "Flipped Ledger #16 and Ledger #5. Also referenced Ledger #5 again."
        self.assertEqual(extract_ledger_references(text), [5, 16])

    def test_case_insensitive(self):
        self.assertEqual(
            extract_ledger_references("see LEDGER #7 and ledger #7"),
            [7],
        )

    def test_tolerates_extra_whitespace(self):
        self.assertEqual(extract_ledger_references("Ledger    #12"), [12])

    def test_does_not_match_other_spellings(self):
        # Convention is `Ledger #N` — other spellings intentionally not matched.
        text = "ledger row #99 and entry #42 and row-99"
        self.assertEqual(extract_ledger_references(text), [])

    def test_empty_text_returns_empty(self):
        self.assertEqual(extract_ledger_references(""), [])

    def test_no_references_returns_empty(self):
        self.assertEqual(extract_ledger_references("nothing to see here"), [])


class DetectFlippedEntriesTests(TestCase):
    """detect_flipped_entries — verifies the `Ledger #N status flip` pattern."""

    def test_detects_flipped_entry(self):
        ledger = "Some content. ### Ledger #5 status flip: open → resolved. More."
        self.assertEqual(detect_flipped_entries(ledger, [5]), [5])

    def test_does_not_detect_unflipped_entry(self):
        ledger = "Ledger #5 is mentioned but no flip block here."
        self.assertEqual(detect_flipped_entries(ledger, [5]), [])

    def test_returns_only_referenced_subset(self):
        ledger = (
            "Ledger #5 status flip: open → resolved.\n"
            "Ledger #16 status flip: open → resolved.\n"
            "Ledger #27 status flip: open → resolved."
        )
        # Only asks about #5 + #27; #16 not requested even though flipped.
        self.assertEqual(detect_flipped_entries(ledger, [5, 27]), [5, 27])

    def test_case_insensitive_and_whitespace_tolerant(self):
        ledger = "LEDGER   #5    STATUS   FLIP: open → resolved"
        self.assertEqual(detect_flipped_entries(ledger, [5]), [5])

    def test_empty_ledger_returns_none(self):
        self.assertEqual(detect_flipped_entries("", [5, 16]), [])


class CheckLedgerReconciliationAtCloseTests(TestCase):
    """check_ledger_reconciliation_at_close — the enforcement decision layer."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username="ledger-recon-test-user",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user,
            name="ledger-recon-test-workspace",
        )

    def _make_ledger(self, content: str) -> Deliverable:  # noqa: F811 defined per class
        return Deliverable.objects.create(
            id=uuid.uuid4(),
            title="Test Ledger",
            deliverable_type="engineering_backlog",
            category="platform",
            agent_name="Rigby",
            content=content,
            workspace=self.workspace,
        )

    def test_no_handoff_path_returns_no_handoff(self):
        result = check_ledger_reconciliation_at_close(
            handoff_path=None,
        )
        self.assertEqual(result.mode, "no_handoff")
        self.assertIsNone(result.handoff_path)

    def test_missing_handoff_file_returns_no_handoff(self):
        result = check_ledger_reconciliation_at_close(
            handoff_path="/tmp/does-not-exist-xyz.md",
        )
        self.assertEqual(result.mode, "no_handoff")

    def test_handoff_with_no_references_is_clean(self):
        handoff = _write_handoff("No ledger references at all.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        result = check_ledger_reconciliation_at_close(
            handoff_path=str(handoff),
        )
        self.assertEqual(result.mode, "clean")
        self.assertEqual(result.referenced_entries, [])

    def test_referenced_and_flipped_is_clean(self):
        ledger = self._make_ledger(
            "### Ledger #5 status flip: open → resolved.\n"
            "Evidence PR #3512."
        )
        handoff = _write_handoff("Ledger #5 flip shipped this session.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        result = check_ledger_reconciliation_at_close(
            handoff_path=str(handoff),
            ledger_deliverable_id=str(ledger.id),
        )
        self.assertEqual(result.mode, "clean")
        self.assertEqual(result.referenced_entries, [5])
        self.assertEqual(result.flipped_entries, [5])
        self.assertEqual(result.drift_entries, [])

    def test_referenced_but_not_flipped_raises(self):
        ledger = self._make_ledger("Just narrative content, no flip block.")
        handoff = _write_handoff("Fixed Ledger #7 this session.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        with self.assertRaises(LedgerReconciliationError) as ctx:
            check_ledger_reconciliation_at_close(
                handoff_path=str(handoff),
                ledger_deliverable_id=str(ledger.id),
            )
        self.assertIn("#7", str(ctx.exception))
        self.assertIn("--allow-ledger-drift", str(ctx.exception))

    def test_referenced_but_not_flipped_with_escape_hatch_returns_allowed_drift(self):
        ledger = self._make_ledger("Narrative only.")
        handoff = _write_handoff("Ledger #9 mentioned in narrative context.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        result = check_ledger_reconciliation_at_close(
            handoff_path=str(handoff),
            ledger_deliverable_id=str(ledger.id),
            allow_ledger_drift=True,
        )
        self.assertEqual(result.mode, "allowed_drift")
        self.assertEqual(result.referenced_entries, [9])
        self.assertEqual(result.flipped_entries, [])
        self.assertEqual(result.drift_entries, [9])

    def test_mixed_referenced_partial_flipped_raises_naming_drifted_ones(self):
        ledger = self._make_ledger(
            "### Ledger #5 status flip: open → resolved.\n"
            "(nothing about #7)"
        )
        handoff = _write_handoff(
            "Flipped Ledger #5, also touched Ledger #7 needing flip."
        )
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        with self.assertRaises(LedgerReconciliationError) as ctx:
            check_ledger_reconciliation_at_close(
                handoff_path=str(handoff),
                ledger_deliverable_id=str(ledger.id),
            )
        msg = str(ctx.exception)
        self.assertIn("#7", msg)
        # #5 was flipped so it must NOT appear in the drift list of the error.
        self.assertNotIn("#5,", msg)
        self.assertNotIn("#5 ", msg)

    def test_ledger_not_found_raises(self):
        handoff = _write_handoff("Ledger #5 referenced.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        bogus_id = str(uuid.uuid4())
        with self.assertRaises(LedgerReconciliationError) as ctx:
            check_ledger_reconciliation_at_close(
                handoff_path=str(handoff),
                ledger_deliverable_id=bogus_id,
            )
        self.assertIn(bogus_id, str(ctx.exception))
        self.assertIn("not found", str(ctx.exception))

    def test_invalid_uuid_raises(self):
        handoff = _write_handoff("Ledger #5 referenced.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        with self.assertRaises(LedgerReconciliationError) as ctx:
            check_ledger_reconciliation_at_close(
                handoff_path=str(handoff),
                ledger_deliverable_id="not-a-uuid",
            )
        self.assertIn("not a valid UUID", str(ctx.exception))


class CheckLedgerReconciliationCommandTests(TestCase):
    """Standalone `check_ledger_reconciliation` management command tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            username="ledger-recon-cmd-test-user",
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user,
            name="ledger-recon-cmd-test-workspace",
        )
        cls.ledger = Deliverable.objects.create(
            id=uuid.uuid4(),
            title="Test Ledger",
            deliverable_type="engineering_backlog",
            category="platform",
            agent_name="Rigby",
            content=(
                "### Ledger #5 status flip: open → resolved.\n"
                "Evidence PR #3512."
            ),
            workspace=cls.workspace,
        )

    def test_clean_referenced_and_flipped_prints_clean_mode(self):
        handoff = _write_handoff("Flipped Ledger #5 this session.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        out = StringIO()
        call_command(
            "check_ledger_reconciliation",
            "--handoff", str(handoff),
            "--ledger-deliverable-id", str(self.ledger.id),
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("[LEDGER-RECON]", output)
        self.assertIn("referenced: #5", output)
        self.assertIn("flipped:    #5", output)
        self.assertIn("mode:       clean", output)

    def test_drift_without_escape_raises_command_error(self):
        handoff = _write_handoff("Referenced Ledger #99 with no flip.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        out = StringIO()
        with self.assertRaises(CommandError) as ctx:
            call_command(
                "check_ledger_reconciliation",
                "--handoff", str(handoff),
                "--ledger-deliverable-id", str(self.ledger.id),
                stdout=out,
            )
        self.assertIn("#99", str(ctx.exception))

    def test_drift_with_escape_hatch_reports_allowed_drift(self):
        handoff = _write_handoff("Ledger #99 referenced in narrative.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        out = StringIO()
        call_command(
            "check_ledger_reconciliation",
            "--handoff", str(handoff),
            "--ledger-deliverable-id", str(self.ledger.id),
            "--allow-ledger-drift",
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("drift:      #99", output)
        self.assertIn("allowed_drift", output)

    def test_no_references_prints_clean_message(self):
        handoff = _write_handoff("Nothing to see here — no ledger refs.")
        self.addCleanup(lambda: handoff.unlink(missing_ok=True))
        out = StringIO()
        call_command(
            "check_ledger_reconciliation",
            "--handoff", str(handoff),
            "--ledger-deliverable-id", str(self.ledger.id),
            stdout=out,
        )
        self.assertIn("[LEDGER-RECON CLEAN]", out.getvalue())
        self.assertIn("no `Ledger #N` references", out.getvalue())

    def test_missing_handoff_prints_no_handoff(self):
        out = StringIO()
        call_command(
            "check_ledger_reconciliation",
            "--handoff", "/tmp/does-not-exist-xyz.md",
            "--ledger-deliverable-id", str(self.ledger.id),
            stdout=out,
        )
        self.assertIn("[LEDGER-RECON NO_HANDOFF]", out.getvalue())
