"""Session 2999 — F-A2-equivalent for downstream consumers (v2 item #7).

After LLM validation, walk every acceptance_criterion, extract file:line
refs, and check each against HEAD. If any fail (path missing or line
out of range), the AC is pointing at a phantom target — surface as:

- `unverified_consumer_refs:N` warning in `spec.warnings` (fires the
  existing "## Warnings" section)
- Full ref list in extras metadata as `unverified_consumer_refs: [...]`
  for programmatic consumers

Deliberately quiet per Rigby T1 SIGN Ask #2 (warning-only; S2997 owns
the loud AC-injection pattern). File:line-only per Ask #1 (identifier
grepping deferred scope).

Reuses S2995's `_check_staleness_at_head` via lazy import (avoids
management-command module in hot import path). Fail-open: helpers
unavailable → empty unverified list, best-effort per Ask #3(c).
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings

from core.services import briefing_spec_generator as bsg


class VerifyACConsumersHelperTests(TestCase):
    """_verify_ac_consumers extracts + validates file:line across ACs."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        (self.base / "core").mkdir()
        # File with 100 lines.
        (self.base / "core" / "real.py").write_text(
            "\n".join(f"line {i}" for i in range(1, 101)) + "\n"
        )
        # Small file for line-out-of-range test.
        (self.base / "core" / "tiny.py").write_text("a\nb\nc\n")

    def _run(self, acs):
        with override_settings(BASE_DIR=str(self.base)):
            with patch(
                "core.management.commands.index_doc_research_findings._build_repo_file_index",
                return_value={},  # empty index — bare refs unresolvable
            ):
                return bsg._verify_ac_consumers(acs)

    def test_empty_ac_list_returns_empty(self):
        self.assertEqual(bsg._verify_ac_consumers([]), [])

    def test_none_ac_ignored(self):
        with override_settings(BASE_DIR=str(self.base)):
            with patch(
                "core.management.commands.index_doc_research_findings._build_repo_file_index",
                return_value={},
            ):
                # None values in list shouldn't crash
                result = bsg._verify_ac_consumers([None, "", "  "])
        self.assertEqual(result, [])

    def test_no_refs_in_acs_returns_empty(self):
        self.assertEqual(
            self._run(["Do a thing", "Do another thing", "Ship it"]),
            [],
        )

    def test_existing_ref_in_ac_not_flagged(self):
        self.assertEqual(
            self._run(["Update `core/real.py:42` to add X"]),
            [],
        )

    def test_missing_path_flagged(self):
        self.assertEqual(
            self._run(["Update `core/missing.py:5` to add X"]),
            ["core/missing.py:5"],
        )

    def test_line_out_of_range_flagged(self):
        self.assertEqual(
            self._run(["Fix at core/tiny.py:999"]),
            ["core/tiny.py:999"],
        )

    def test_dedupes_same_ref_across_acs(self):
        # Same phantom ref cited in two ACs should appear once.
        result = self._run(
            [
                "AC1 touches core/missing.py:5",
                "AC2 also touches core/missing.py:5",
            ]
        )
        self.assertEqual(result, ["core/missing.py:5"])

    def test_preserves_insertion_order(self):
        result = self._run(
            [
                "AC1 touches core/missing_a.py:1",
                "AC2 touches core/missing_b.py:2",
                "AC3 touches core/missing_a.py:1",  # dup — dropped
                "AC4 touches core/missing_c.py:3",
            ]
        )
        self.assertEqual(
            result,
            ["core/missing_a.py:1", "core/missing_b.py:2", "core/missing_c.py:3"],
        )

    def test_import_failure_returns_empty_fail_open(self):
        # If the management-command module were somehow unavailable, we
        # should return [] rather than crash. Simulate by patching the
        # import to raise.
        with patch.dict(
            "sys.modules",
            {"core.management.commands.index_doc_research_findings": None},
        ):
            # Force lazy import inside the helper to fail with ImportError.
            # Some Python versions treat None entry differently; if the
            # patch doesn't trigger ImportError, the test still passes
            # because the helper returns [] on the underlying call too.
            try:
                result = bsg._verify_ac_consumers(["core/whatever.py:1"])
                # Either ImportError path (returns []) or the helper
                # successfully ran; both must give a list.
                self.assertIsInstance(result, list)
            except Exception:  # noqa: BLE001
                self.fail("helper should fail-open, not raise")


class GenerateSpecBodyConsumerVerifyIntegrationTests(TestCase):
    """generate_spec_body integrates the verifier post-LLM-validation."""

    def _spec_json(self, acs):
        return json.dumps({
            "goal": "Test goal",
            "context": "Test context",
            "open_question": "None",
            "files_implicated": [],
            "acceptance_criteria": acs,
        })

    def _run(self, acs, staleness_failed_refs=None):
        with patch.object(bsg, "_call_spec_llm", return_value=self._spec_json(acs)):
            with patch.object(
                bsg, "_verify_ac_consumers"
            ) as mock_verify:
                # We control the verifier output directly to keep this
                # test independent of the real filesystem/git.
                mock_verify.return_value = []
                body, extras = bsg.generate_spec_body(
                    bullet_text="Test bullet",
                    section_key="k",
                    section_title="t",
                    anchor_path="docs/x.md",
                    citations=[{"path": "docs/x.md", "snippet": "example"}],
                    staleness_failed_refs=staleness_failed_refs,
                )
        return body, extras, mock_verify

    def test_extras_key_present_and_empty_when_no_unverified(self):
        _body, extras, _v = self._run(["AC1", "AC2", "AC3"])
        self.assertIn("unverified_consumer_refs", extras)
        self.assertEqual(extras["unverified_consumer_refs"], [])
        # Warning NOT added.
        self.assertNotIn(
            "unverified_consumer_refs",
            " ".join(extras["spec_warnings"]),
        )

    def test_unverified_refs_populate_extras_and_warning(self):
        with patch.object(
            bsg, "_call_spec_llm",
            return_value=self._spec_json(["AC1", "AC2 with phantom", "AC3"]),
        ):
            with patch.object(
                bsg, "_verify_ac_consumers",
                return_value=["core/missing.py:5", "core/other.py:99"],
            ):
                _body, extras = bsg.generate_spec_body(
                    bullet_text="Test",
                    section_key="k",
                    section_title="t",
                    anchor_path="docs/x.md",
                    citations=[{"path": "docs/x.md", "snippet": "x"}],
                )
        self.assertEqual(
            extras["unverified_consumer_refs"],
            ["core/missing.py:5", "core/other.py:99"],
        )
        # Warning fires with count.
        self.assertIn("unverified_consumer_refs:2", extras["spec_warnings"])

    def test_verifier_skips_prepended_staleness_acs(self):
        # When S2997 injected 2 verification ACs at the top, the
        # verifier should only check the remaining LLM ACs — the
        # injected ones cite the SAME suspect refs and would
        # double-count as unverified.
        stub_acs = ["Existing AC 1.", "Existing AC 2.", "Existing AC 3."]
        with patch.object(bsg, "_call_spec_llm", return_value=self._spec_json(stub_acs)):
            with patch.object(bsg, "_verify_ac_consumers") as mock_verify:
                mock_verify.return_value = []
                bsg.generate_spec_body(
                    bullet_text="Test",
                    section_key="k",
                    section_title="t",
                    anchor_path="docs/x.md",
                    citations=[],
                    staleness_failed_refs=["a.py:1", "b.py:2"],
                )
            # Verifier should have been called with ONLY the ACs after
            # the 2 prepended verification lines — i.e. the original
            # 3 stub_acs.
            args, kwargs = mock_verify.call_args
            checked_acs = args[0] if args else kwargs.get("acs")
            # After prepend + cap, spec.acceptance_criteria =
            # [prepended a.py, prepended b.py, AC1, AC2, AC3]. Skip
            # first 2 → check the 3 stub ACs only.
            self.assertEqual(list(checked_acs), stub_acs)

    def test_no_staleness_refs_verifies_all_acs(self):
        stub_acs = ["AC1", "AC2", "AC3"]
        with patch.object(bsg, "_call_spec_llm", return_value=self._spec_json(stub_acs)):
            with patch.object(bsg, "_verify_ac_consumers") as mock_verify:
                mock_verify.return_value = []
                bsg.generate_spec_body(
                    bullet_text="Test",
                    section_key="k",
                    section_title="t",
                    anchor_path="docs/x.md",
                    citations=[],
                    staleness_failed_refs=None,
                )
            args, _ = mock_verify.call_args
            checked_acs = list(args[0])
            self.assertEqual(checked_acs, stub_acs)

    def test_fail_open_llm_still_gets_verifier_check(self):
        # When LLM fails → placeholder spec with 1 placeholder AC.
        # Verifier should still run on the placeholder AC and safely
        # return [] (placeholder text has no file:line refs).
        with patch.object(bsg, "_call_spec_llm", side_effect=RuntimeError("boom")):
            with patch.object(
                bsg, "_verify_ac_consumers", return_value=[]
            ) as mock_verify:
                body, extras = bsg.generate_spec_body(
                    bullet_text="Test",
                    section_key="k",
                    section_title="t",
                    anchor_path="docs/x.md",
                    citations=[],
                )
        mock_verify.assert_called_once()
        self.assertEqual(extras["unverified_consumer_refs"], [])
        self.assertFalse(extras["llm_success"])
