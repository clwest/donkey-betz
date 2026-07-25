"""Regression + smoke tests for the agent capability drift scanner.

Ratified at S2953 (plan pivot). Rigby SIGN-refined single-codepath design:
these tests exercise the same ``AgentCapabilityDriftScanner`` service that
powers the management command AND the ``agent_capability_drift_tool`` PA-callable
audit surface.

Test policy
-----------
- Assert scanner runs end-to-end without exception and returns a well-shaped
  report against live code+DB state (smoke).
- Assert the exceptions allowlist actually suppresses findings for the tiers
  it declares (behavior).
- Assert the invariant filter is honored (behavior).
- Do NOT assert on specific finding counts — those drift as agents are added
  or exercised. The scanner is soft-warn by design; strict-fail tests belong
  once Chris defines Tier-1.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from django.test import TestCase

from core.services.agent_capability_drift import (
    AgentCapabilityDriftScanner,
    DriftFinding,
    DriftReport,
    INTERNAL_ONLY,
    LEGACY,
    SUPPORTED,
    load_exceptions,
)


class AgentCapabilityDriftScannerSmokeTest(TestCase):
    """End-to-end smoke — scanner runs cleanly against live code state."""

    def test_scanner_runs_and_returns_well_shaped_report(self):
        scanner = AgentCapabilityDriftScanner()
        report = scanner.run_all()
        self.assertIsInstance(report, DriftReport)
        d = report.to_dict()
        self.assertIn('scanned_at', d)
        self.assertIn('totals', d)
        self.assertIn('findings', d)
        self.assertIn('suppressed_findings', d)
        totals = d['totals']
        self.assertGreater(totals['agent_map_entries'], 0)
        # NB: agent_db_rows can be < agent_map_entries in a fresh Django test DB
        # because migrations don't seed all Agent rows. That divergence is the
        # exact drift the scanner is designed to surface — we assert only
        # non-negative here and let the drift findings speak for themselves.
        self.assertGreaterEqual(totals['agent_db_rows'], 0)
        self.assertGreater(totals['run_agent_enum_entries'], 0)

    def test_report_has_active_failures_property(self):
        # Currently no invariant is severity='fail' by design (soft-warn only);
        # graduate to fail-severity for Tier-1 agents when defined.
        scanner = AgentCapabilityDriftScanner()
        report = scanner.run_all()
        self.assertFalse(report.has_active_failures)


class ExceptionAllowlistSuppressionTest(TestCase):
    """Behavior — allowlist entries actually suppress findings for their tier."""

    def _write_exceptions(self, entries: dict) -> Path:
        # Build a minimal exceptions file in a temp directory.
        tmp = Path(tempfile.mkdtemp())
        path = tmp / "capabilities_exceptions.yaml"
        lines = ["version: 1", "exceptions:"]
        for cls, meta in entries.items():
            lines.append(f"  {cls}:")
            for k, v in meta.items():
                lines.append(f"    {k}: {v!r}" if isinstance(v, str) else f"    {k}: {v}")
        path.write_text("\n".join(lines) + "\n")
        return path

    def test_internal_only_suppresses_exposure_invariant(self):
        # Pick an AGENT_MAP class that is NOT in the run_agent enum (there are
        # 27 such at S2953 open per the audit) and confirm tagging it
        # internal-only suppresses the exposure-completeness finding for it.
        from core.agent_router import AgentRouter

        # Find a class currently unreachable via run_agent.
        scanner_open = AgentCapabilityDriftScanner()
        report_open = scanner_open.run_all()
        exposure_findings = [
            f for f in report_open.findings if f.invariant == 'exposure_completeness'
        ]
        # Skip test if there happen to be no exposure findings on this branch
        # (scanner is soft-warn — this can go to zero once cleanup is done).
        if not exposure_findings:
            self.skipTest("No exposure_completeness findings to suppress in current state.")

        target_class = exposure_findings[0].agent_class
        path = self._write_exceptions({
            target_class: {"tier": INTERNAL_ONLY, "reason": "test-suppression"},
        })
        scanner_with_exc = AgentCapabilityDriftScanner(exceptions_path=path)
        report_with_exc = scanner_with_exc.run_all()

        active_for_target = [
            f for f in report_with_exc.findings
            if f.agent_class == target_class and f.invariant == 'exposure_completeness'
        ]
        suppressed_for_target = [
            f for f in report_with_exc.suppressed_findings
            if f.agent_class == target_class and f.invariant == 'exposure_completeness'
        ]
        self.assertEqual(len(active_for_target), 0,
                         "internal-only tier should suppress exposure_completeness")
        self.assertGreater(len(suppressed_for_target), 0,
                           "suppressed finding should appear in the allowlist bucket")

    def test_legacy_suppresses_recent_execution_invariant(self):
        # Pick an AGENT_MAP class with a recent-execution finding and confirm
        # tier=legacy moves it into the suppressed bucket.
        scanner_open = AgentCapabilityDriftScanner()
        report_open = scanner_open.run_all()
        recent_findings = [
            f for f in report_open.findings if f.invariant == 'recent_execution'
        ]
        if not recent_findings:
            self.skipTest("No recent_execution findings to suppress in current state.")

        target_class = recent_findings[0].agent_class
        path = self._write_exceptions({
            target_class: {"tier": LEGACY, "reason": "test-legacy"},
        })
        scanner_with_exc = AgentCapabilityDriftScanner(exceptions_path=path)
        report_with_exc = scanner_with_exc.run_all()

        active_for_target = [
            f for f in report_with_exc.findings
            if f.agent_class == target_class and f.invariant == 'recent_execution'
        ]
        suppressed_for_target = [
            f for f in report_with_exc.suppressed_findings
            if f.agent_class == target_class and f.invariant == 'recent_execution'
        ]
        self.assertEqual(len(active_for_target), 0)
        self.assertGreater(len(suppressed_for_target), 0)


class LoadExceptionsShapeTest(TestCase):
    """Behavior — load_exceptions parses valid YAML and normalizes bad tiers."""

    def test_load_missing_file_returns_empty(self):
        entries = load_exceptions(Path("/tmp/does-not-exist-agent-drift-test.yaml"))
        self.assertEqual(entries, {})

    def test_load_normalizes_unknown_tier_to_supported(self):
        tmp = Path(tempfile.mkdtemp()) / "excs.yaml"
        tmp.write_text(
            "version: 1\n"
            "exceptions:\n"
            "  BogusAgent:\n"
            "    tier: not-a-real-tier\n"
            "    reason: 'test'\n"
        )
        entries = load_exceptions(tmp)
        self.assertEqual(entries['BogusAgent']['tier'], SUPPORTED)


class PAHandlerContractTest(TestCase):
    """Behavior — the PA-callable handler returns the expected envelope shape."""

    def test_summary_action_returns_totals_only(self):
        from core.services.tool_dispatcher import ToolDispatcher

        d = ToolDispatcher()
        result = d._handle_agent_capability_drift(
            'agent_capability_drift_tool',
            {'action': 'summary'},
            None,
            'test-trace',
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'summary')
        self.assertIn('totals', result)
        self.assertNotIn('findings', result,
                         "summary action should NOT include full findings list")

    def test_scan_action_returns_full_findings(self):
        from core.services.tool_dispatcher import ToolDispatcher

        d = ToolDispatcher()
        result = d._handle_agent_capability_drift(
            'agent_capability_drift_tool',
            {'action': 'scan'},
            None,
            'test-trace',
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'scan')
        self.assertIn('findings', result)
        self.assertIn('suppressed_findings', result)

    def test_invariant_filter_narrows_findings(self):
        from core.services.tool_dispatcher import ToolDispatcher

        d = ToolDispatcher()
        result = d._handle_agent_capability_drift(
            'agent_capability_drift_tool',
            {'action': 'scan', 'invariant': 'recent_execution'},
            None,
            'test-trace',
        )
        for f in result['findings']:
            self.assertEqual(f['invariant'], 'recent_execution')
