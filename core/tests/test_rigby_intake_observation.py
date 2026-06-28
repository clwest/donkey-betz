"""
Tests for PR 9: Rigby Intake observation harness.

Covered cases (per PR 9 spec):
1.  production default for RIGBY_EVENT_INTAKE_ENABLED is False (source-level check)
2.  override_settings can enable intake locally
3.  rigby_intake_status returns a stable JSON shape
4.  status command handles zero MissionRuns
5.  status command handles multiple MissionRuns
6.  aggregate 24h / 7d counts are correct
7.  decision breakdown is correct
8.  work item presence is False when queue flag is off
9.  lag check detects stuck running intakes
10. lag check ignores recent running intakes
11. lag check ignores passed / failed intakes
12. no work items are created by either command
13. no delegation occurs from either command
14. all PR 2-8 tests still pass — covered by combined-suite run

Run::

    python manage.py test core.tests.test_rigby_intake_observation -v2 --keepdb
"""

from __future__ import annotations

import io
import json
import re
import uuid
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_ops_runs import OpsRun, OpsRunEvent
from core.models_rigby_work_items import RigbyWorkItem


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _make_intake_run(
    *,
    status="passed",
    decision=None,
    mission_impact=None,
    event_ref=None,
    started_at=None,
    finished_at=None,
):
    """Build a MissionRun(OpsRun) matching the intake-task contract."""
    event_ref = event_ref or f"deliverable_event:{uuid.uuid4()}"
    summary = {
        "event_ref": event_ref,
        "dry_run": True,
    }
    if decision is not None:
        summary["decision"] = decision
    if mission_impact is not None:
        summary["mission_impact"] = mission_impact

    run = OpsRun.objects.create(
        title=f"intake: {event_ref}",
        run_type="manual",
        triggered_by="pa_tool",
        status=status,
        domain="mission",
        run_kind="intake",
        mission_id=uuid.uuid4(),
        summary=summary,
        finished_at=finished_at,
    )
    # Override auto_now_add timestamp when caller wants to backdate.
    if started_at is not None:
        OpsRun.objects.filter(pk=run.pk).update(started_at=started_at)
        run.refresh_from_db()
    return run


def _add_timeline_events(run, labels):
    for label in labels:
        OpsRunEvent.objects.create(
            run=run,
            event_type="info",
            label=label,
            detail={"work_item_id": "synthetic"},
        )


# ---------------------------------------------------------------------------
# Settings / flag-default invariants
# ---------------------------------------------------------------------------


class ProductionDefaultInvariantTests(TestCase):

    @staticmethod
    def _settings_source() -> str:
        """Return the source text of the settings module.

        ``django.conf.settings`` is a lazy wrapper without ``__file__``;
        import the underlying module to get the real file path.
        """
        import importlib
        import os
        mod_name = os.environ.get("DJANGO_SETTINGS_MODULE", "core.settings")
        mod = importlib.import_module(mod_name)
        return Path(mod.__file__).read_text()

    def test_source_default_for_rigby_event_intake_is_false(self):
        """The settings.py env-var lookup must default to 'false'.

        We read the settings module source rather than the current
        runtime value so the assertion is independent of any local
        env override that happens to be set in the test runner's
        environment.
        """
        src = self._settings_source()
        # Match the literal line: env-var default must be 'false' (case-insensitive).
        self.assertRegex(
            src,
            r"RIGBY_EVENT_INTAKE_ENABLED\s*=\s*os\.environ\.get\(\s*['\"]RIGBY_EVENT_INTAKE_ENABLED['\"],\s*['\"]false['\"]",
            "Production default for RIGBY_EVENT_INTAKE_ENABLED must be the env-var "
            "fallback 'false'.",
        )

    def test_all_four_session_1250_flags_default_false_in_source(self):
        src = self._settings_source()
        for flag in (
            "RIGBY_EVENT_INTAKE_ENABLED",
            "RIGBY_INTERNAL_WORK_QUEUE_ENABLED",
            "RIGBY_WORK_QUEUE_REVIEW_ENABLED",
            "RIGBY_DELEGATION_ENABLED",
        ):
            pattern = (
                rf"{flag}\s*=\s*os\.environ\.get\(\s*['\"]" + flag + r"['\"]"
                r",\s*['\"]false['\"]"
            )
            self.assertRegex(src, pattern, f"{flag} must default to 'false' in settings.py")

    @override_settings(RIGBY_EVENT_INTAKE_ENABLED=True)
    def test_local_override_enables_intake(self):
        """override_settings (the same mechanism Django uses for the
        Local env override path) propagates to the running settings."""
        self.assertTrue(getattr(settings, "RIGBY_EVENT_INTAKE_ENABLED", False))


# ---------------------------------------------------------------------------
# rigby_intake_status command
# ---------------------------------------------------------------------------


class StatusCommandShapeTests(TestCase):

    def _call_json(self, **kwargs):
        out = io.StringIO()
        call_command("rigby_intake_status", "--json", stdout=out, **kwargs)
        return json.loads(out.getvalue())

    def _call_human(self, **kwargs):
        out = io.StringIO()
        call_command("rigby_intake_status", stdout=out, **kwargs)
        return out.getvalue()

    def test_empty_db_returns_zero_totals_and_no_rows(self):
        report = self._call_json()
        self.assertEqual(report["totals"]["all_time"], 0)
        self.assertEqual(report["totals"]["last_24h"], 0)
        self.assertEqual(report["totals"]["last_7d"], 0)
        self.assertEqual(report["totals"]["running_count"], 0)
        self.assertEqual(report["recent"], [])
        self.assertEqual(report["decision_breakdown_7d"], {})

    def test_report_shape_contains_required_top_level_keys(self):
        _make_intake_run(decision="ignore")
        report = self._call_json()
        for key in (
            "generated_at", "flags", "totals", "decision_breakdown_7d", "recent",
        ):
            self.assertIn(key, report)
        for flag in (
            "RIGBY_EVENT_INTAKE_ENABLED",
            "RIGBY_INTERNAL_WORK_QUEUE_ENABLED",
            "RIGBY_WORK_QUEUE_REVIEW_ENABLED",
            "RIGBY_DELEGATION_ENABLED",
        ):
            self.assertIn(flag, report["flags"])
            self.assertIsInstance(report["flags"][flag], bool)

    def test_per_run_row_shape(self):
        ev_ref = f"deliverable_event:{uuid.uuid4()}"
        run = _make_intake_run(
            decision="monitor", mission_impact="low", event_ref=ev_ref,
        )
        _add_timeline_events(
            run, ["intake_started", "impact_assessed", "decision_made"],
        )
        report = self._call_json()
        self.assertEqual(len(report["recent"]), 1)
        row = report["recent"][0]
        for key in (
            "mission_run_id", "started_at", "finished_at", "status",
            "source_event_ref", "decision", "mission_impact",
            "timeline_event_count", "has_work_item", "mission_id",
        ):
            self.assertIn(key, row)
        self.assertEqual(row["source_event_ref"], ev_ref)
        self.assertEqual(row["decision"], "monitor")
        self.assertEqual(row["mission_impact"], "low")
        self.assertEqual(row["timeline_event_count"], 3)

    def test_24h_and_7d_aggregates(self):
        now = timezone.now()
        _make_intake_run(decision="ignore", started_at=now - timedelta(hours=1))
        _make_intake_run(decision="monitor", started_at=now - timedelta(hours=10))
        _make_intake_run(decision="notify", started_at=now - timedelta(days=3))
        # Outside the 7d window:
        _make_intake_run(decision="ignore", started_at=now - timedelta(days=14))

        report = self._call_json()
        self.assertEqual(report["totals"]["all_time"], 4)
        self.assertEqual(report["totals"]["last_24h"], 2)  # the 1h and 10h
        self.assertEqual(report["totals"]["last_7d"], 3)   # the three within 7d

    def test_decision_breakdown_7d(self):
        now = timezone.now()
        _make_intake_run(decision="ignore", started_at=now - timedelta(hours=1))
        _make_intake_run(decision="ignore", started_at=now - timedelta(hours=2))
        _make_intake_run(decision="monitor", started_at=now - timedelta(hours=3))
        _make_intake_run(decision="notify", started_at=now - timedelta(days=2))
        # Out of window:
        _make_intake_run(decision="ignore", started_at=now - timedelta(days=14))

        report = self._call_json()
        self.assertEqual(report["decision_breakdown_7d"], {
            "ignore": 2,
            "monitor": 1,
            "notify": 1,
        })

    def test_running_count_reflects_status(self):
        _make_intake_run(status="running")
        _make_intake_run(status="running")
        _make_intake_run(status="passed")
        report = self._call_json()
        self.assertEqual(report["totals"]["running_count"], 2)

    @override_settings(
        RIGBY_INTERNAL_WORK_QUEUE_ENABLED=False,
        RIGBY_WORK_QUEUE_REVIEW_ENABLED=False,
        RIGBY_DELEGATION_ENABLED=False,
    )
    def test_work_item_presence_false_when_queue_flag_off(self):
        """No RigbyWorkItem rows exist when the queue flag is off
        (per PR 6 contract). The status report's `has_work_item`
        flag is False for every recent intake row."""
        _make_intake_run(decision="monitor")
        report = self._call_json()
        for row in report["recent"]:
            self.assertFalse(row["has_work_item"])

    def test_work_item_presence_true_when_row_exists(self):
        """If a RigbyWorkItem exists for the event_ref (perhaps because
        the queue flag was on at intake time), the status command surfaces it."""
        ev_ref = f"deliverable_event:{uuid.uuid4()}"
        mission_run = _make_intake_run(
            decision="monitor", event_ref=ev_ref,
        )
        RigbyWorkItem.objects.create(
            source_mission_run=mission_run,
            source_event_ref=ev_ref,
            decision="monitor",
            severity="warn",
            mission_impact="low",
            priority=3,
            status="open",
            title="x", summary="x", recommended_next_action="x",
            evidence={"event_ref": ev_ref, "rules_fired": []},
        )
        report = self._call_json()
        row = [r for r in report["recent"] if r["source_event_ref"] == ev_ref][0]
        self.assertTrue(row["has_work_item"])

    def test_limit_caps_rows(self):
        for _ in range(15):
            _make_intake_run(decision="ignore")
        report = self._call_json(limit=5)
        self.assertEqual(len(report["recent"]), 5)
        self.assertEqual(report["totals"]["all_time"], 15)

    def test_human_output_includes_flag_lines(self):
        text = self._call_human()
        self.assertIn("RIGBY_EVENT_INTAKE_ENABLED", text)
        self.assertIn("RIGBY_INTERNAL_WORK_QUEUE_ENABLED", text)
        self.assertIn("RIGBY_WORK_QUEUE_REVIEW_ENABLED", text)
        self.assertIn("RIGBY_DELEGATION_ENABLED", text)


class StatusCommandReadOnlyTests(TestCase):
    """Status command must not write any rows or fire any delegation."""

    def test_status_writes_zero_rows(self):
        _make_intake_run(decision="ignore")
        before_runs = OpsRun.objects.count()
        before_events = OpsRunEvent.objects.count()
        before_items = RigbyWorkItem.objects.count()

        out = io.StringIO()
        call_command("rigby_intake_status", "--json", stdout=out)

        self.assertEqual(OpsRun.objects.count(), before_runs)
        self.assertEqual(OpsRunEvent.objects.count(), before_events)
        self.assertEqual(RigbyWorkItem.objects.count(), before_items)


# ---------------------------------------------------------------------------
# rigby_intake_lag_check command
# ---------------------------------------------------------------------------


class LagCheckCommandTests(TestCase):

    def _call_json(self, **kwargs):
        out = io.StringIO()
        call_command("rigby_intake_lag_check", "--json", stdout=out, **kwargs)
        return json.loads(out.getvalue())

    def _call_human(self, **kwargs):
        out = io.StringIO()
        call_command("rigby_intake_lag_check", stdout=out, **kwargs)
        return out.getvalue()

    def test_no_stuck_runs_when_db_empty(self):
        report = self._call_json()
        self.assertEqual(report["stuck_count"], 0)
        self.assertEqual(report["stuck_runs"], [])

    def test_detects_stuck_running_intake(self):
        now = timezone.now()
        old = _make_intake_run(
            status="running", started_at=now - timedelta(minutes=10),
        )
        report = self._call_json()
        self.assertEqual(report["stuck_count"], 1)
        self.assertEqual(
            report["stuck_runs"][0]["mission_run_id"], str(old.id),
        )
        self.assertGreaterEqual(report["stuck_runs"][0]["age_minutes"], 9.5)

    def test_ignores_recent_running_intakes(self):
        now = timezone.now()
        _make_intake_run(
            status="running", started_at=now - timedelta(minutes=1),
        )
        report = self._call_json()
        self.assertEqual(report["stuck_count"], 0)

    def test_ignores_passed_intakes(self):
        now = timezone.now()
        _make_intake_run(
            status="passed", started_at=now - timedelta(minutes=60),
            finished_at=now - timedelta(minutes=59),
        )
        report = self._call_json()
        self.assertEqual(report["stuck_count"], 0)

    def test_ignores_failed_intakes(self):
        now = timezone.now()
        _make_intake_run(
            status="failed", started_at=now - timedelta(minutes=60),
            finished_at=now - timedelta(minutes=59),
        )
        report = self._call_json()
        self.assertEqual(report["stuck_count"], 0)

    def test_custom_threshold(self):
        now = timezone.now()
        _make_intake_run(
            status="running", started_at=now - timedelta(minutes=7),
        )
        # 5m threshold: stuck.
        self.assertEqual(self._call_json()["stuck_count"], 1)
        # 10m threshold: not stuck.
        self.assertEqual(self._call_json(threshold=10)["stuck_count"], 0)

    def test_human_output_says_ok_when_no_stuck_runs(self):
        text = self._call_human()
        self.assertIn("OK", text)

    def test_human_output_warns_when_stuck(self):
        now = timezone.now()
        _make_intake_run(
            status="running", started_at=now - timedelta(minutes=10),
        )
        text = self._call_human()
        self.assertRegex(text, r"\b1\s+stuck\b")


class LagCheckCommandReadOnlyTests(TestCase):

    def test_lag_check_writes_zero_rows(self):
        now = timezone.now()
        _make_intake_run(
            status="running", started_at=now - timedelta(minutes=15),
        )
        before_runs = OpsRun.objects.count()
        before_events = OpsRunEvent.objects.count()
        before_items = RigbyWorkItem.objects.count()

        out = io.StringIO()
        call_command("rigby_intake_lag_check", "--json", stdout=out)

        self.assertEqual(OpsRun.objects.count(), before_runs)
        self.assertEqual(OpsRunEvent.objects.count(), before_events)
        self.assertEqual(RigbyWorkItem.objects.count(), before_items)


# ---------------------------------------------------------------------------
# Side-effect containment across both commands
# ---------------------------------------------------------------------------


class NoDownstreamSideEffectTests(TestCase):
    """Neither command should create a RigbyWorkItem, dispatch an
    agent, or trigger any delegation pathway."""

    def test_no_agent_execution_rows_created(self):
        from core.models_unified_system import AgentExecution
        _make_intake_run(decision="monitor")
        before = AgentExecution.objects.count()

        call_command("rigby_intake_status", "--json", stdout=io.StringIO())
        call_command("rigby_intake_lag_check", "--json", stdout=io.StringIO())

        self.assertEqual(AgentExecution.objects.count(), before)

    def test_no_work_items_created(self):
        _make_intake_run(decision="monitor")
        before = RigbyWorkItem.objects.count()

        call_command("rigby_intake_status", "--json", stdout=io.StringIO())
        call_command("rigby_intake_lag_check", "--json", stdout=io.StringIO())

        self.assertEqual(RigbyWorkItem.objects.count(), before)
