"""Session 1267 PR 4.2 — Bug Triage Specialist runner tests.

Mirrors the shape of ``test_employees_platform_auditor.py`` /
``test_employees_chief_of_staff.py`` for the runner-side scope (PR 4.2
focuses on the job module, task wrapper, migration; the contract +
registry already shipped in PR 4.1).

Coverage:

  * **Factory** — ``build_bug_triage_runner()`` returns a MissionRunner
    with 7 steps + ``auto_emit_verdict=False`` + postflight wired.
  * **Step functions** — each step's ORM read + summary write,
    including empty-window edge cases (Rigby SIGN D4 — step events
    fire even on 0-row queries; here we assert the *summary write*
    completes for the 0-row case, which is the same surface
    MissionRunner inspects when emitting the step event).
  * **Cluster signature helper** — bounded + handles empty fields.
  * **Recommendation derivation** — rule firing thresholds.
  * **Markdown report builder** — all six contract sections present.
  * **Postflight** — bounded summary transform (Rigby SIGN D5).
  * **Shift report body formatter** — passed/failed branches +
    no-auto-cert language.
  * **MissionRunner ``auto_emit_verdict=False`` path** — DB test that
    the status flip works without writing a ``verdict_issued:*``
    OpsRunEvent row (the load-bearing assertion for Rigby SIGN D1).

Run::

    .venv/bin/python manage.py test core.tests.test_employees_bug_triage -v2
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import MagicMock

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from core.employees import BUG_TRIAGE_JOB, BUG_TRIAGE_SPECIALIST
from core.employees.mission_runner import MissionRunner, PostflightContext
from core.jobs.bug_triage import (
    DELIVERABLE_TITLE_PREFIX,
    ERROR_TAIL_PREVIEW_LINES,
    MISSION_RUN_KIND,
    TRIAGE_REPORT_TITLE_PREFIX,
    WINDOW_HOURS,
    _bug_triage_escalation_spec_factory,
    _build_triage_report_markdown,
    _cluster_signature,
    _derive_recommendations,
    _format_shift_report_body,
    _postflight,
    build_bug_triage_runner,
    build_escalation_body,
    step_1_collect_celery_failures,
    step_2_collect_agent_failures,
    step_3_collect_mission_verdicts,
    step_4_collect_authority_events,
    step_5_cluster_by_signature,
    step_6_generate_triage_report,
    step_7_record_run_summary,
)


def _make_mission_mock(summary=None, mission_id=None):
    m = MagicMock()
    m.id = mission_id or uuid.uuid4()
    m.summary = dict(summary or {})

    def _save(update_fields=None):
        pass

    m.save.side_effect = _save
    return m


# ═════════════════════════════════════════════════════════════════════
# Factory shape
# ═════════════════════════════════════════════════════════════════════


class BuildBugTriageRunnerTests(SimpleTestCase):

    def test_returns_mission_runner_instance(self):
        runner = build_bug_triage_runner()
        self.assertIsInstance(runner, MissionRunner)

    def test_has_seven_steps_in_contract_order(self):
        runner = build_bug_triage_runner()
        self.assertEqual(len(runner.steps), 7)
        expected_names = (
            "step_1_collect_celery_failures",
            "step_2_collect_agent_failures",
            "step_3_collect_mission_verdicts",
            "step_4_collect_authority_events",
            "step_5_cluster_by_signature",
            "step_6_generate_triage_report",
            "step_7_record_run_summary",
        )
        actual_names = tuple(s.name for s in runner.steps)
        self.assertEqual(actual_names, expected_names)

    def test_config_opts_out_of_auto_emit_verdict(self):
        # Rigby SIGN D1: v0 does NOT auto-certify.
        runner = build_bug_triage_runner()
        self.assertFalse(runner.config.auto_emit_verdict)

    def test_config_carries_job_contract_for_authority_warn(self):
        # Bug Triage extends the N=1 authority_contract_observed
        # evidence baseline → must opt in to warn-mode emission.
        runner = build_bug_triage_runner()
        self.assertIs(runner.config.job_contract, BUG_TRIAGE_JOB)

    def test_config_identity_matches_employee(self):
        runner = build_bug_triage_runner()
        self.assertEqual(
            runner.config.employee_handle, BUG_TRIAGE_SPECIALIST.handle
        )
        self.assertEqual(
            runner.config.employee_display_name,
            BUG_TRIAGE_SPECIALIST.display_name,
        )
        self.assertEqual(
            runner.config.runs_as_username,
            BUG_TRIAGE_SPECIALIST.runs_as_username,
        )
        self.assertIsNone(runner.config.primary_chat_id)

    def test_config_mission_run_kind_matches_contract(self):
        runner = build_bug_triage_runner()
        self.assertEqual(
            runner.config.mission_run_kind, "bug_triage_daily"
        )
        self.assertEqual(MISSION_RUN_KIND, "bug_triage_daily")

    def test_postflight_is_wired(self):
        # Rigby SIGN D5 transform happens here.
        runner = build_bug_triage_runner()
        self.assertIs(runner.postflight_fn, _postflight)

    def test_shift_report_is_wired(self):
        runner = build_bug_triage_runner()
        self.assertIsNotNone(runner.shift_report_fn)

    def test_pa_post_is_none_v0(self):
        # No pinned PA chat — visibility via inbox + Deliverable.
        runner = build_bug_triage_runner()
        self.assertIsNone(runner.pa_post_fn)

    def test_escalation_spec_factory_targets_donkey_betz(self):
        runner = build_bug_triage_runner()
        spec = runner.escalation_deliverable_spec_factory(
            _failure_ctx_stub()
        )
        self.assertEqual(spec.workspace_name, "Donkey Betz")


def _failure_ctx_stub():
    from core.employees.mission_runner import FailureContext

    return FailureContext(
        mission_id=uuid.uuid4(),
        failed_step="step_3_collect_mission_verdicts",
        error_tail="boom\nstack\nframe",
        error_signature="abc123",
        started_at=timezone.now() - timedelta(minutes=2),
        finished_at=timezone.now(),
        counts_so_far={"celery_failures_count": 0},
    )


# ═════════════════════════════════════════════════════════════════════
# Cluster signature
# ═════════════════════════════════════════════════════════════════════


class ClusterSignatureTests(SimpleTestCase):

    def test_basic_signature_shape(self):
        sig = _cluster_signature(
            source="celery",
            primary="core.tasks.foo",
            error_type="TimeoutError",
            error_message="connection reset by peer after 30s",
        )
        self.assertTrue(sig.startswith("celery|core.tasks.foo|TimeoutError|"))
        self.assertIn("connection reset", sig)

    def test_empty_fields_use_sentinel(self):
        sig = _cluster_signature(
            source="agent",
            primary="",
            error_type="",
            error_message="",
        )
        self.assertEqual(sig, "agent|(none)|(none)|(none)")

    def test_message_prefix_truncated(self):
        long_msg = "x" * 500
        sig = _cluster_signature(
            source="celery",
            primary="t",
            error_type="E",
            error_message=long_msg,
        )
        prefix = sig.rsplit("|", 1)[-1]
        self.assertLessEqual(len(prefix), 80)

    def test_newlines_normalized_in_prefix(self):
        sig = _cluster_signature(
            source="celery",
            primary="t",
            error_type="E",
            error_message="first\nsecond line",
        )
        # The newline should be collapsed to a space so the signature
        # is one-line.
        self.assertNotIn("\n", sig)


# ═════════════════════════════════════════════════════════════════════
# Step 5 — cluster ranking
# ═════════════════════════════════════════════════════════════════════


class Step5ClusterByCountTests(SimpleTestCase):

    def test_empty_aggregates_yields_zero_clusters(self):
        mission = _make_mission_mock(summary={
            "celery_cluster_aggregates": {},
            "agent_cluster_aggregates": {},
        })
        result = step_5_cluster_by_signature(mission)
        self.assertTrue(result.passed)
        self.assertEqual(mission.summary["cluster_count"], 0)
        self.assertIsNone(mission.summary["top_cluster_signature"])
        self.assertEqual(mission.summary["top_cluster_occurrences"], 0)

    def test_top_cluster_picks_highest_count_across_sources(self):
        mission = _make_mission_mock(summary={
            "celery_cluster_aggregates": {
                "celery|a|E|msg": 4,
                "celery|b|E|msg": 2,
            },
            "agent_cluster_aggregates": {
                "agent|x|E|msg": 7,
            },
        })
        result = step_5_cluster_by_signature(mission)
        self.assertTrue(result.passed)
        self.assertEqual(mission.summary["cluster_count"], 3)
        self.assertEqual(
            mission.summary["top_cluster_signature"], "agent|x|E|msg"
        )
        self.assertEqual(
            mission.summary["top_cluster_occurrences"], 7
        )

    def test_top_clusters_list_is_bounded_to_ten(self):
        celery_aggs = {
            f"celery|t{i}|E|msg": (i + 1) for i in range(20)
        }
        mission = _make_mission_mock(summary={
            "celery_cluster_aggregates": celery_aggs,
            "agent_cluster_aggregates": {},
        })
        step_5_cluster_by_signature(mission)
        self.assertLessEqual(len(mission.summary["top_clusters"]), 10)


# ═════════════════════════════════════════════════════════════════════
# Step 7 — passthrough
# ═════════════════════════════════════════════════════════════════════


class Step7RunSummaryTests(SimpleTestCase):

    def test_step_7_passes_with_counts_in_output(self):
        mission = _make_mission_mock(summary={
            "celery_failures_count": 3,
            "agent_failures_count": 1,
            "missions_today_total": 5,
            "authority_events_count": 7,
            "cluster_count": 2,
        })
        result = step_7_record_run_summary(mission)
        self.assertTrue(result.passed)
        self.assertIn("3 celery", result.output)
        self.assertIn("no auto-certification", result.output.lower())


# ═════════════════════════════════════════════════════════════════════
# Recommendation derivation
# ═════════════════════════════════════════════════════════════════════


class DeriveRecommendationsTests(SimpleTestCase):

    def test_clean_window_yields_no_recommendations(self):
        recs = _derive_recommendations({
            "celery_failures_count": 0,
            "agent_failures_count": 0,
            "missions_rejected_count": 0,
            "authority_events_count": 0,
            "top_cluster_signature": None,
            "top_cluster_occurrences": 0,
        })
        self.assertEqual(recs, [])

    def test_recurring_top_cluster_fires_high(self):
        recs = _derive_recommendations({
            "top_cluster_signature": "celery|t|E|m",
            "top_cluster_occurrences": 5,
        })
        self.assertTrue(any(r["priority"] == "high" for r in recs))

    def test_recurring_top_cluster_below_threshold_does_not_fire(self):
        recs = _derive_recommendations({
            "top_cluster_signature": "celery|t|E|m",
            "top_cluster_occurrences": 2,  # threshold is >= 3
        })
        # No high recs from the cluster rule.
        self.assertFalse(
            any(
                "Recurring failure cluster" in r.get("finding", "")
                for r in recs
            )
        )

    def test_high_celery_failures_fires_high(self):
        recs = _derive_recommendations({
            "celery_failures_count": 25,
        })
        self.assertTrue(any(r["priority"] == "high" for r in recs))

    def test_high_agent_failures_fires_medium(self):
        recs = _derive_recommendations({
            "agent_failures_count": 15,
        })
        self.assertTrue(
            any(
                "AgentExecution" in r.get("finding", "")
                and r["priority"] == "medium"
                for r in recs
            )
        )

    def test_missions_rejected_fires_medium(self):
        recs = _derive_recommendations({
            "missions_rejected_count": 1,
        })
        self.assertTrue(
            any(
                "mission(s) failed" in r.get("finding", "")
                and r["priority"] == "medium"
                for r in recs
            )
        )


# ═════════════════════════════════════════════════════════════════════
# Markdown report shape (all 6 contract sections)
# ═════════════════════════════════════════════════════════════════════


class BuildTriageReportMarkdownTests(SimpleTestCase):

    def _build(self, summary=None, recommendations=None):
        return _build_triage_report_markdown(
            today_str="2026-06-30",
            when_iso="2026-06-30T08:00:00-06:00",
            mission=_make_mission_mock(),
            summary=summary or {},
            recommendations=recommendations or [],
        )

    def test_contains_title(self):
        body = self._build()
        self.assertIn(f"# {TRIAGE_REPORT_TITLE_PREFIX} — 2026-06-30", body)

    def test_six_contract_sections_present(self):
        body = self._build()
        for section in (
            "## Window Summary",
            "## Top Failure Patterns",
            "## Mission Verdicts Today",
            "## Authority Telemetry Today",
            "## Recommendations",
            "## Green Checks",
        ):
            self.assertIn(section, body, f"missing section {section!r}")

    def test_empty_top_failure_patterns_renders_clean_sentinel(self):
        body = self._build()
        self.assertIn("No failure clusters in window", body)

    def test_recommendations_section_renders_each_item(self):
        body = self._build(
            recommendations=[
                {
                    "priority": "high",
                    "finding": "Recurring failure pattern",
                    "action": "Investigate immediately",
                },
            ]
        )
        self.assertIn("[high]", body)
        self.assertIn("Recurring failure pattern", body)
        self.assertIn("Investigate immediately", body)

    def test_mission_verdicts_section_renders_breakdown(self):
        body = self._build(summary={
            "missions_today_total": 4,
            "missions_certified_count": 2,
            "missions_rejected_count": 1,
            "missions_deferred_count": 0,
            "missions_in_progress_count": 1,
            "missions_by_run_kind": {"morning_brief": 1, "platform_audit": 2},
        })
        self.assertIn("Certified: **2**", body)
        self.assertIn("Rejected: **1**", body)
        self.assertIn("`morning_brief`: 1", body)


# ═════════════════════════════════════════════════════════════════════
# Postflight — bounded summary transform (Rigby SIGN D5)
# ═════════════════════════════════════════════════════════════════════


class PostflightBoundedSummaryTests(SimpleTestCase):

    def test_clean_path_writes_preview_none_and_false(self):
        summary_acc = {"wall_time_ms": 1500}
        ctx = PostflightContext(
            mission=_make_mission_mock(),
            passed=True,
            summary_acc=summary_acc,
        )
        _postflight(ctx)
        self.assertIsNone(summary_acc["error_tail_preview"])
        self.assertFalse(summary_acc["has_full_error_tail"])
        self.assertNotIn("error_tail", summary_acc)

    def test_failure_path_keeps_last_n_lines_and_drops_raw_tail(self):
        long_tail = "\n".join(f"line {i}" for i in range(30))
        summary_acc = {"error_tail": long_tail}
        ctx = PostflightContext(
            mission=_make_mission_mock(),
            passed=False,
            summary_acc=summary_acc,
        )
        _postflight(ctx)
        preview = summary_acc["error_tail_preview"]
        self.assertTrue(summary_acc["has_full_error_tail"])
        # Last N lines kept; total lines in preview equals
        # ERROR_TAIL_PREVIEW_LINES (or less if input was shorter).
        self.assertEqual(
            len(preview.splitlines()), ERROR_TAIL_PREVIEW_LINES
        )
        # Last line preserved verbatim.
        self.assertIn("line 29", preview)
        # Raw tail dropped from summary.
        self.assertNotIn("error_tail", summary_acc)


# ═════════════════════════════════════════════════════════════════════
# Escalation body formatter
# ═════════════════════════════════════════════════════════════════════


class EscalationBodyTests(SimpleTestCase):

    def test_includes_bug_triage_branding(self):
        body = build_escalation_body(_failure_ctx_stub())
        self.assertIn(DELIVERABLE_TITLE_PREFIX, body)
        self.assertIn("Daily Bug Triage cascade", body)

    def test_includes_full_error_tail(self):
        # D5: the escalation deliverable is where the full tail lives.
        body = build_escalation_body(_failure_ctx_stub())
        self.assertIn("boom", body)
        self.assertIn("stack", body)
        self.assertIn("frame", body)


# ═════════════════════════════════════════════════════════════════════
# Shift-report body
# ═════════════════════════════════════════════════════════════════════


class ShiftReportBodyTests(SimpleTestCase):

    def test_passed_status_uses_no_auto_cert_language(self):
        mission = _make_mission_mock(summary={"wall_time_ms": 12345})
        mission.status = "passed"
        body = _format_shift_report_body(mission, {
            "wall_time_ms": 12345,
            "celery_failures_count": 1,
            "agent_failures_count": 0,
            "missions_today_total": 3,
            "cluster_count": 1,
            "recommendations_count": 1,
            "report_deliverable_id": "deadbeef",
        })
        self.assertIn("completed cleanly", body)
        self.assertIn("12.3s", body)
        self.assertIn(
            "Awaiting Rigby/human verdict via PA tool", body
        )
        self.assertIn("v0 does not auto-certify", body)
        self.assertIn("Triage deliverable deadbeef", body)

    def test_failed_status_names_failed_step(self):
        mission = _make_mission_mock()
        mission.status = "failed"
        body = _format_shift_report_body(mission, {
            "wall_time_ms": 500,
            "failed_step": "step_2_collect_agent_failures",
            "escalation_deliverable_id": "esc-uuid",
        })
        self.assertIn("failed at step_2_collect_agent_failures", body)
        self.assertIn("Escalation deliverable esc-uuid", body)


# ═════════════════════════════════════════════════════════════════════
# Empty-window step coverage (Rigby SIGN D4 — steps fire even on 0 rows)
# ═════════════════════════════════════════════════════════════════════


class EmptyWindowStepCoverageTests(TestCase):
    """Real-DB tests with no fixtures → each step's query returns 0 rows.

    Verifies: steps still pass, summary gets the contract counts
    initialized to 0, no exceptions. Asserts the load-bearing piece of
    Rigby SIGN D4 — a 0-row query is not an error condition.
    """

    def _empty_mission(self):
        from core.models_ops_runs import OpsRun

        return OpsRun.objects.create(
            title="Bug Triage Test Mission",
            run_type="manual",
            domain="mission",
            run_kind="bug_triage_daily",
            status="running",
            summary={},
        )

    def test_step_1_handles_zero_celery_failures(self):
        mission = self._empty_mission()
        result = step_1_collect_celery_failures(mission)
        self.assertTrue(result.passed)
        mission.refresh_from_db()
        self.assertEqual(mission.summary["celery_failures_count"], 0)
        self.assertEqual(mission.summary["celery_cluster_aggregates"], {})
        self.assertIn("window_start_iso", mission.summary)
        self.assertIn("window_end_iso", mission.summary)

    def test_step_2_handles_zero_agent_failures(self):
        mission = self._empty_mission()
        result = step_2_collect_agent_failures(mission)
        self.assertTrue(result.passed)
        mission.refresh_from_db()
        self.assertEqual(mission.summary["agent_failures_count"], 0)
        self.assertEqual(mission.summary["agent_cluster_aggregates"], {})

    def test_step_3_excludes_self_mission_from_counts(self):
        mission = self._empty_mission()
        result = step_3_collect_mission_verdicts(mission)
        self.assertTrue(result.passed)
        mission.refresh_from_db()
        # Self-mission must not be counted in its own triage.
        self.assertEqual(mission.summary["missions_today_total"], 0)

    def test_step_4_handles_zero_authority_events(self):
        mission = self._empty_mission()
        result = step_4_collect_authority_events(mission)
        self.assertTrue(result.passed)
        mission.refresh_from_db()
        self.assertEqual(mission.summary["authority_events_count"], 0)
        self.assertEqual(
            mission.summary["authority_events_by_employee"], {}
        )

    def test_step_6_persists_clean_deliverable_with_six_sections(self):
        mission = self._empty_mission()
        # Pre-populate the summary with steps 1-5's clean-window output.
        mission.summary = {
            "window_start_iso": (
                timezone.now() - timedelta(hours=WINDOW_HOURS)
            ).isoformat(),
            "window_end_iso": timezone.now().isoformat(),
            "celery_failures_count": 0,
            "agent_failures_count": 0,
            "missions_today_total": 0,
            "missions_certified_count": 0,
            "missions_rejected_count": 0,
            "missions_deferred_count": 0,
            "missions_in_progress_count": 0,
            "missions_by_run_kind": {},
            "authority_events_count": 0,
            "authority_events_by_employee": {},
            "cluster_count": 0,
            "top_cluster_signature": None,
            "top_cluster_occurrences": 0,
            "top_clusters": [],
        }
        mission.save()
        result = step_6_generate_triage_report(mission)
        self.assertTrue(result.passed)
        mission.refresh_from_db()
        self.assertIn("report_deliverable_id", mission.summary)
        self.assertGreater(mission.summary["report_chars"], 0)

        # Pull the Deliverable + assert all six sections present.
        from core.models_deliverables import Deliverable

        deliverable = Deliverable.objects.get(
            id=mission.summary["report_deliverable_id"]
        )
        body = deliverable.content
        for section in (
            "## Window Summary",
            "## Top Failure Patterns",
            "## Mission Verdicts Today",
            "## Authority Telemetry Today",
            "## Recommendations",
            "## Green Checks",
        ):
            self.assertIn(section, body)
        # Deliverable shape: type=analysis, status=ready.
        self.assertEqual(deliverable.deliverable_type, "analysis")
        self.assertEqual(deliverable.status, "ready")


# ═════════════════════════════════════════════════════════════════════
# MissionRunner — auto_emit_verdict path
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerAutoEmitVerdictTests(TestCase):
    """Lock the new ``auto_emit_verdict=False`` path in MissionRunner.

    Existing employees (PA / CoS / Docs Manager) leave the field at
    its default True → unaffected. The new path is exercised here
    via Bug Triage specifically.
    """

    def test_config_default_is_true(self):
        from core.employees.mission_runner import MissionRunnerConfig

        cfg = MissionRunnerConfig(
            employee_handle="x",
            employee_display_name="X",
            runs_as_username="x",
            mission_run_kind="x_kind",
        )
        self.assertTrue(cfg.auto_emit_verdict)

    def test_flip_status_without_verdict_passes_path(self):
        from core.models_ops_runs import OpsRun, OpsRunEvent

        runner = build_bug_triage_runner()
        mission = OpsRun.objects.create(
            title="bt status flip",
            run_type="manual",
            domain="mission",
            run_kind="bug_triage_daily",
            status="running",
            summary={},
        )
        runner._flip_status_without_verdict(
            mission=mission, terminal_verdict="certified",
        )
        mission.refresh_from_db()
        self.assertEqual(mission.status, "passed")
        self.assertIsNotNone(mission.finished_at)
        # No verdict_issued OpsRunEvent emitted (Rigby SIGN D1 lock).
        self.assertEqual(
            OpsRunEvent.objects.filter(
                run=mission, label__startswith="verdict_issued"
            ).count(),
            0,
        )

    def test_flip_status_without_verdict_failed_path(self):
        from core.models_ops_runs import OpsRun, OpsRunEvent

        runner = build_bug_triage_runner()
        mission = OpsRun.objects.create(
            title="bt status flip rej",
            run_type="manual",
            domain="mission",
            run_kind="bug_triage_daily",
            status="running",
            summary={},
        )
        runner._flip_status_without_verdict(
            mission=mission, terminal_verdict="rejected",
        )
        mission.refresh_from_db()
        self.assertEqual(mission.status, "failed")
        self.assertEqual(
            OpsRunEvent.objects.filter(
                run=mission, label__startswith="verdict_issued"
            ).count(),
            0,
        )

    def test_flip_status_idempotent_on_terminal_status(self):
        from core.models_ops_runs import OpsRun

        runner = build_bug_triage_runner()
        mission = OpsRun.objects.create(
            title="bt status flip idem",
            run_type="manual",
            domain="mission",
            run_kind="bug_triage_daily",
            status="passed",
            summary={},
        )
        # Already terminal — must not flip back to failed.
        runner._flip_status_without_verdict(
            mission=mission, terminal_verdict="rejected",
        )
        mission.refresh_from_db()
        self.assertEqual(mission.status, "passed")
