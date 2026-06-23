"""Tests for core.services.smoke_dispatch — Session 1213 smoke context
minimization (deliverable afe36715-721c-400f-b36f-4b9717467b66).

Covers:
- pass-through for non-smoke modes
- strip (default) for receipt_only / fleet_smoke
- warn-only enforcement
- error enforcement raises SmokeContextViolation
- smoke -> smoke_id alias
- clean smoke context (no forbidden keys) -> no-op
- AC-4 byte size: post-strip context <=200 bytes for realistic input
"""

from __future__ import annotations

import json
import os
import unittest
from unittest import mock

from core.services.smoke_dispatch import (
    SMOKE_CONTEXT_KEYS,
    SMOKE_MODES,
    SmokeContextViolation,
    apply_smoke_allowlist,
)


class ApplySmokeAllowlistTests(unittest.TestCase):
    def test_non_dict_passes_through(self):
        ctx, meta = apply_smoke_allowlist("not a dict")  # type: ignore[arg-type]
        self.assertEqual(ctx, "not a dict")
        self.assertEqual(meta["smoke_gate"], "skipped_non_dict")

    def test_non_smoke_mode_passes_through_unchanged(self):
        original = {"mode": "production", "research": "x" * 5000}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(ctx, original)
        self.assertEqual(meta["smoke_gate"], "non_smoke")

    def test_missing_mode_treated_as_non_smoke(self):
        original = {"research": "spec body"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(ctx, original)
        self.assertEqual(meta["smoke_gate"], "non_smoke")

    def test_outbound_pack_not_gated(self):
        original = {"mode": "outbound_pack", "research": "campaign spec body"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(ctx, original)
        self.assertEqual(meta["smoke_gate"], "non_smoke")

    def test_clean_smoke_context_no_op(self):
        original = {"mode": "receipt_only", "smoke_id": "abc", "user_id": "1"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(ctx, original)
        self.assertEqual(meta["smoke_gate"], "clean")

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "strip"})
    def test_strip_default_removes_forbidden_receipt_only(self):
        original = {
            "mode": "receipt_only",
            "smoke_id": "xyz",
            "user_id": "1",
            "conversation_id": "pa-abc",
            "workspace_id": "ws-1",
            "research": "URC v0.1 spec body " * 500,  # ~10KB of bloat
            "user_skills": ["python", "django"],
            "tone": "neutral",
        }
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(meta["smoke_gate"], "stripped")
        self.assertIn("research", meta["stripped_keys"])
        self.assertIn("user_skills", meta["stripped_keys"])
        self.assertIn("tone", meta["stripped_keys"])
        self.assertNotIn("research", ctx)
        self.assertNotIn("user_skills", ctx)
        self.assertEqual(ctx["smoke_id"], "xyz")
        self.assertEqual(ctx["mode"], "receipt_only")
        self.assertLess(meta["post_bytes"], meta["pre_bytes"])

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "strip"})
    def test_strip_fleet_smoke_mode_also_gated(self):
        original = {"mode": "fleet_smoke", "smoke_id": "fs1", "research": "x" * 1000}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(meta["smoke_gate"], "stripped")
        self.assertNotIn("research", ctx)

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "warn"})
    def test_warn_logs_but_does_not_strip(self):
        original = {"mode": "receipt_only", "smoke_id": "w1", "research": "spec"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(meta["smoke_gate"], "warned")
        self.assertIn("research", ctx)
        self.assertEqual(meta["forbidden_keys"], ["research"])

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "error"})
    def test_error_raises_smoke_context_violation(self):
        original = {"mode": "receipt_only", "smoke_id": "e1", "research": "spec"}
        with self.assertRaises(SmokeContextViolation) as cm:
            apply_smoke_allowlist(original)
        self.assertIn("research", str(cm.exception))
        self.assertIn("receipt_only", str(cm.exception))

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "error"})
    def test_error_mode_clean_context_does_not_raise(self):
        original = {"mode": "receipt_only", "smoke_id": "e2"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(meta["smoke_gate"], "clean")
        self.assertEqual(ctx, original)

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "invalid"})
    def test_invalid_enforcement_mode_falls_back_to_strip(self):
        original = {"mode": "receipt_only", "smoke_id": "i1", "research": "x"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(meta["smoke_gate"], "stripped")
        self.assertNotIn("research", ctx)

    def test_smoke_alias_rewritten_to_smoke_id(self):
        original = {"mode": "receipt_only", "smoke": "legacy-key"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(ctx.get("smoke_id"), "legacy-key")
        self.assertNotIn("smoke", ctx)

    def test_smoke_alias_does_not_overwrite_existing_smoke_id(self):
        original = {"mode": "receipt_only", "smoke": "old", "smoke_id": "new"}
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(ctx.get("smoke_id"), "new")
        # smoke key still gets stripped under default-strip enforcement
        self.assertNotIn("smoke", ctx)

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "strip"})
    def test_ac4_post_strip_context_under_200_bytes(self):
        """AC-4 from deliverable afe36715: post-fix smoke shows context
        <=200 bytes vs current 5-15KB baseline."""
        original = {
            "mode": "receipt_only",
            "smoke_id": "ac4-test",
            "user_id": "e0c9d44b-a876-4b30-b0da-e4d0b10006f6",
            "conversation_id": "pa-61c7b47d201d4591",
            "workspace_id": "b4503364-2573-4401-9e28-61a739e0ce50",
            # Bloat: realistic URC spec body that we saw on a14d4c7c
            "research": "## Rigby: URC v0.1 spec body " * 200,  # ~6KB
            "user_skills": ["python", "django", "react", "typescript"],
            "user_goals": ["ship session 1213", "save tokens"],
            "tone": "neutral",
            "purpose": "Smoke 2 Phase C contract_violation verify",
            "word_count": 120,
        }
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(meta["smoke_gate"], "stripped")
        self.assertLessEqual(meta["post_bytes"], 200, f"AC-4 fail: {meta['post_bytes']}B > 200B")
        self.assertGreater(meta["pre_bytes"], 5000)  # confirm we started bloated

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "error"})
    def test_error_mode_raises_on_oversize_clean_context(self):
        # Realistic UUID-shaped routing IDs can push allowlist-only context
        # past 200B. In error mode this is a hard violation.
        original = {
            "mode": "receipt_only",
            "smoke_id": "a" * 60,  # exaggerated long smoke_id
            "user_id": "00000000-0000-0000-0000-000000000001",
            "conversation_id": "pa-" + "b" * 40,
            "workspace_id": "00000000-0000-0000-0000-000000000002",
            "auto_followup": True,
            "receipt_only": True,
        }
        with self.assertRaises(SmokeContextViolation) as cm:
            apply_smoke_allowlist(original)
        self.assertIn("post-strip bytes", str(cm.exception))
        self.assertIn("> cap=200", str(cm.exception))

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "strip"})
    def test_strip_mode_logs_but_does_not_raise_when_oversize(self):
        # Same realistic-oversize input, strip mode -> over_cap=True in meta
        # but returns the (already minimal) allowlist context without raising.
        original = {
            "mode": "fleet_smoke",
            "smoke_id": "a" * 80,
            "workspace_id": "00000000-0000-0000-0000-000000000003",
            "conversation_id": "pa-" + "c" * 50,
        }
        ctx, meta = apply_smoke_allowlist(original)
        self.assertEqual(meta["smoke_gate"], "stripped")
        self.assertTrue(meta["over_cap"])
        self.assertGreater(meta["post_bytes"], 200)
        # Allowlist-only keys still preserved.
        self.assertIn("smoke_id", ctx)
        self.assertIn("workspace_id", ctx)

    @mock.patch.dict(os.environ, {"SMOKE_CONTEXT_ENFORCEMENT_MODE": "error"})
    def test_error_mode_raises_with_both_problems_listed(self):
        # Forbidden keys AND oversize-after-strip -> error message names both.
        original = {
            "mode": "receipt_only",
            "smoke_id": "x" * 200,  # ensures post-strip still >200B
            "workspace_id": "00000000-0000-0000-0000-000000000004",
            "research": "spec body",
            "tone": "neutral",
        }
        with self.assertRaises(SmokeContextViolation) as cm:
            apply_smoke_allowlist(original)
        msg = str(cm.exception)
        self.assertIn("non-allowlisted keys", msg)
        self.assertIn("post-strip bytes", msg)

    def test_allowlist_constants_documented_contract(self):
        # Defense in depth: assert the public allowlist hasn't drifted without
        # a deliberate change. If this fails, also update deliverable afe36715
        # AC-1 (allowlist contents) and the runbook on 1a8cde69.
        self.assertEqual(SMOKE_CONTEXT_KEYS, frozenset({
            "mode", "smoke_id", "receipt_only",
            "user_id", "conversation_id", "workspace_id", "auto_followup",
        }))
        self.assertEqual(SMOKE_MODES, frozenset({"receipt_only", "fleet_smoke"}))


if __name__ == "__main__":
    unittest.main()
