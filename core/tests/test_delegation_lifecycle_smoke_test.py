"""Arc I-0100 P3 (IB-1799-T1-03) — regression coverage of the
``manage.py delegation_lifecycle_smoke_test`` command per ADR-0003
§3.2 + Rigby SIGN Cycle 1 F3/F4 folds.

Verifies:

1. Command exits with code 0 on the happy path (all 5 lifecycle
   labels emit + idempotency + savepoint rollback).
2. Command emits the ``DELEGATION_LIFECYCLE_SMOKE_TEST_PASS`` marker
   on success.
3. Command emits the evidence bundle in the required shape per
   ADR-0003 §3.1 F1 fold (Phase 2 entry gate).
4. The command's default cleanup (transaction savepoint rollback)
   leaves zero persistent artifacts — the production DB should show
   no new OpsRun / OpsRunEvent / RigbyWorkItem / AgentExecution rows
   after the command runs.
5. The auto-disable threshold constants module exposes the expected
   ADR-0003 §3.4 F7 fold values.

Run::

    python manage.py test core.tests.test_delegation_lifecycle_smoke_test -v2 --keepdb
"""
from __future__ import annotations

import io
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class DelegationLifecycleSmokeTestCommandTests(TestCase):
    """Coverage of ``manage.py delegation_lifecycle_smoke_test``."""

    def test_command_exits_zero_on_happy_path(self):
        """Command runs cleanly + emits PASS marker."""
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.models_rigby_work_items import RigbyWorkItem
        from core.models_unified_system import AgentExecution

        pre_opsrun = OpsRun.objects.count()
        pre_opsrunevent = OpsRunEvent.objects.count()
        pre_workitem = RigbyWorkItem.objects.count()
        pre_execution = AgentExecution.objects.count()

        stdout = io.StringIO()

        with patch("sys.exit") as mock_exit:
            call_command("delegation_lifecycle_smoke_test", stdout=stdout)
            mock_exit.assert_called_once_with(0)

        output = stdout.getvalue()
        self.assertIn("DELEGATION_LIFECYCLE_SMOKE_TEST_PASS", output)
        self.assertIn("Evidence bundle", output)
        self.assertNotIn("DELEGATION_LIFECYCLE_SMOKE_TEST_FAIL", output)

        # Cleanup verification — savepoint rollback leaves zero net-new rows
        self.assertEqual(OpsRun.objects.count(), pre_opsrun)
        self.assertEqual(OpsRunEvent.objects.count(), pre_opsrunevent)
        self.assertEqual(RigbyWorkItem.objects.count(), pre_workitem)
        # AgentExecution count may or may not differ if a synthetic Agent
        # row was created + a real AgentExecution came in during the test.
        # In the smoke test we roll back the AgentExecution too.
        self.assertEqual(AgentExecution.objects.count(), pre_execution)

    def test_command_evidence_bundle_has_required_structure(self):
        """Evidence bundle per ADR-0003 §3.1 F1 fold."""
        stdout = io.StringIO()
        with patch("sys.exit"):
            call_command("delegation_lifecycle_smoke_test", stdout=stdout)
        output = stdout.getvalue()

        # Required evidence-bundle keys
        self.assertIn('"phase": "1_shadow_audit_synthetic"', output)
        self.assertIn('"adr_ref": "ADR-0003"', output)
        self.assertIn('"override_settings_applied":', output)
        self.assertIn('"RIGBY_DELEGATION_ENABLED=True"', output)
        self.assertIn('"CELERY_TASK_ALWAYS_EAGER=True"', output)
        self.assertIn('"expected_labels_in_order":', output)
        self.assertIn('"agent_assigned"', output)
        self.assertIn('"mission_closed"', output)
        self.assertIn('"unhandled_exceptions": []', output)
        self.assertIn('"verdict": "PASS"', output)

    def test_verbose_flag_prints_per_event_details(self):
        """--verbose emits per-event emission lines."""
        stdout = io.StringIO()
        with patch("sys.exit"):
            call_command(
                "delegation_lifecycle_smoke_test",
                "--verbose",
                stdout=stdout,
            )
        output = stdout.getvalue()
        self.assertIn("agent_assigned emitted:", output)
        self.assertIn("idempotency: pre=", output)

    def test_keep_artifacts_flag_persists_rows(self):
        """--keep-artifacts commits the savepoint (debug mode)."""
        from core.models_ops_runs import OpsRun

        pre = OpsRun.objects.filter(run_kind="delegation_smoke_test").count()
        stdout = io.StringIO()
        with patch("sys.exit"):
            call_command(
                "delegation_lifecycle_smoke_test",
                "--keep-artifacts",
                stdout=stdout,
            )
        post = OpsRun.objects.filter(run_kind="delegation_smoke_test").count()
        self.assertEqual(post, pre + 1)


class DelegationAutoDisableThresholdsTests(TestCase):
    """Coverage of ``core.services.delegation_auto_disable`` constants."""

    def test_all_thresholds_are_defined(self):
        from core.services.delegation_auto_disable import get_all_thresholds

        spec = get_all_thresholds()
        self.assertEqual(spec["adr_ref"], "ADR-0003")
        self.assertEqual(spec["phase"], 2)
        self.assertIn("baseline", spec)
        self.assertIn("thresholds", spec)
        self.assertIn("monitoring_surface_integrated", spec)

    def test_opsrunevent_threshold_is_1_5x_baseline(self):
        """Threshold = baseline × 1.5 per ADR-0003 §3.4."""
        from core.services.delegation_auto_disable import (
            BASELINE_OPSRUNEVENT_DAILY,
            OPSRUNEVENT_DAILY_AUTO_DISABLE,
            VOLUME_MULTIPLIER,
        )
        self.assertAlmostEqual(
            OPSRUNEVENT_DAILY_AUTO_DISABLE,
            BASELINE_OPSRUNEVENT_DAILY * VOLUME_MULTIPLIER,
        )

    def test_monitoring_surface_integrated(self):
        """MONITORING_SURFACE_INTEGRATED=True after Arc I-0100 P3 Stop
        Condition #1 discharge — the ``delegation_auto_disable_monitor``
        module + ``delegation_auto_disable_check`` management command
        are the wired consumer + kill-switch surface.
        """
        from core.services.delegation_auto_disable import MONITORING_SURFACE_INTEGRATED
        self.assertTrue(MONITORING_SURFACE_INTEGRATED)

    def test_null_rate_threshold_is_5_percent(self):
        """F7 fold: 5% NULL-rate over 10min triggers auto-disable."""
        from core.services.delegation_auto_disable import (
            EXECUTION_ID_NULL_RATE_THRESHOLD,
            NULL_RATE_WINDOW_MINUTES,
        )
        self.assertEqual(EXECUTION_ID_NULL_RATE_THRESHOLD, 0.05)
        self.assertEqual(NULL_RATE_WINDOW_MINUTES, 10)

    def test_distinct_trace_error_signature_is_3(self):
        """F7 fold: ≥3 distinct trace_ids with same error signature."""
        from core.services.delegation_auto_disable import (
            DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD,
        )
        self.assertEqual(DISTINCT_TRACE_ERROR_SIGNATURE_THRESHOLD, 3)
