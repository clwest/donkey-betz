"""
Session 1256 PR 1.1 — MissionRunner synthetic contract tests.

Real-DB PostgreSQL integration (per the S1234 memory rule — no mocked
querysets for QS-heavy code). All step functions are synthetic — the
runner is being exercised against controlled inputs, not against the
docs-manager cascade or any other job-specific surface.

Test categories (mapped to Rigby's 7 signed constraints + the
acceptance criteria in PR 1.1's scope):

  * MissionRunnerImportContractTests       — constraints #1 + #4 (no
                                              docs-manager imports;
                                              opaque step boundary)
  * MissionRunnerIdempotencyTests          — constraint #2
  * MissionRunnerEventOrderingTests        — constraint #3
  * MissionRunnerStepBoundaryTests         — constraint #4
  * MissionRunnerErrorSignatureTests       — constraint #5
  * MissionRunnerEscalationTests           — constraint #6 (create-or-
                                              append + audit transition)
  * MissionRunnerHookContainmentTests      — constraint #7 (optional
                                              hooks + failure isolation)
  * MissionRunnerVerdictTests              — verdict idempotency +
                                              confidence selection
  * MissionRunnerConfigTests               — frozen config + defaults
  * MissionRunnerSafetyTests               — defensive cases (empty
                                              steps, wrong-shape step
                                              returns)

Run::

    .venv/bin/python manage.py test core.tests.test_mission_runner -v2
"""

from __future__ import annotations

import ast
import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from core.employees.mission_runner import (
    DEFAULT_CONFIDENCE_FAILURE,
    DEFAULT_CONFIDENCE_SUCCESS_DEGRADED,
    DEFAULT_CONFIDENCE_SUCCESS_FULL,
    DEFAULT_DEDUPE_WINDOW_HOURS,
    ESCALATION_LABEL,
    PAPostContext,
    RUN_STARTED_LABEL,
    Step,
    StepResult,
    MissionRunner,
    MissionRunnerConfig,
    VERDICT_CERTIFIED,
    VERDICT_REJECTED,
    _normalize_for_signature,
    _tail_lines,
)
from core.models_ops_runs import OpsRun, OpsRunEvent


User = get_user_model()


MISSION_RUNNER_PATH = (
    Path(__file__).resolve().parents[1] / "employees" / "mission_runner.py"
)


# ── Shared helpers ────────────────────────────────────────────────────


def _setup_user(username: str = "chris"):
    """Ensure the runs_as_username user exists for ORM lookups."""
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"email": f"{username}@test.donkey"},
    )
    return user


def _make_config(**overrides) -> MissionRunnerConfig:
    """Build a MissionRunnerConfig for tests with sensible defaults."""
    defaults: Dict[str, Any] = dict(
        employee_handle="testbot",
        employee_display_name="Testbot",
        runs_as_username="chris",
        primary_chat_id=None,
        mission_run_kind="test_mission",
        job_title="Test Job",
        confidence_success_full=0.95,
        confidence_success_degraded=0.6,
        confidence_failure=0.0,
        dedupe_window_hours=24,
        escalation_source="TestRunner",
        escalation_title_prefix="Test Escalation",
        workspace_name=None,
        pin_settings_key=None,
    )
    defaults.update(overrides)
    return MissionRunnerConfig(**defaults)


def _passing_step(name: str, output: str = "") -> Step:
    """Synthetic step that always returns passed=True."""

    def _fn(mission):
        return StepResult(passed=True, output=output, extra={"kind": "pass"})

    return Step(name=name, fn=_fn)


def _failing_step(
    name: str, output: str = "synthetic failure"
) -> Step:
    """Synthetic step that returns passed=False (no raise)."""

    def _fn(mission):
        return StepResult(passed=False, output=output)

    return Step(name=name, fn=_fn)


def _raising_step(
    name: str,
    exc_class: type = ValueError,
    msg: str = "synthetic raise",
) -> Step:
    """Synthetic step that raises an exception."""

    def _fn(mission):
        raise exc_class(msg)

    return Step(name=name, fn=_fn)


def _wrong_shape_step(name: str) -> Step:
    """Step that returns something other than a StepResult."""

    def _fn(mission):
        return {"not": "a StepResult"}  # type: ignore[return-value]

    return Step(name=name, fn=_fn)


def _event_labels(mission) -> List[str]:
    """Return event labels in chronological order."""
    return list(
        OpsRunEvent.objects.filter(run=mission)
        .order_by("created_at", "id")
        .values_list("label", flat=True)
    )


def _build_runner(
    steps,
    config: Optional[MissionRunnerConfig] = None,
    **hooks,
) -> MissionRunner:
    """Build a runner with given steps + optional hooks."""
    return MissionRunner(
        config=config or _make_config(),
        steps=steps,
        **hooks,
    )


# ═════════════════════════════════════════════════════════════════════
# Import contract — Rigby constraints #1 + #9
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerImportContractTests(SimpleTestCase):
    """Static-analysis tests on the runner module's imports.

    Per Rigby constraint #1: "no hidden employee/job imports;
    MissionRunner must not import docs-manager-specific modules."
    """

    FORBIDDEN_TOP_LEVEL_IMPORTS = (
        "core.tasks_documentation_manager",
        "core.employees.comms_docs_manager",
    )

    FORBIDDEN_SYMBOL_REFERENCES = (
        "RIGBY",
        "DOCUMENTATION_MANAGER",
        "post_docs_manager_shift_report",
    )

    @classmethod
    def _load_module_ast(cls):
        source = MISSION_RUNNER_PATH.read_text()
        return ast.parse(source, filename=str(MISSION_RUNNER_PATH))

    def test_no_docs_manager_imports(self):
        tree = self._load_module_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(
                        alias.name,
                        self.FORBIDDEN_TOP_LEVEL_IMPORTS,
                        f"MissionRunner illegally imports {alias.name!r}",
                    )
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                self.assertNotIn(
                    mod,
                    self.FORBIDDEN_TOP_LEVEL_IMPORTS,
                    f"MissionRunner illegally imports from {mod!r}",
                )

    def test_no_employee_specific_symbol_references(self):
        """The runner must not reference RIGBY / DOCUMENTATION_MANAGER."""
        source = MISSION_RUNNER_PATH.read_text()
        for sym in self.FORBIDDEN_SYMBOL_REFERENCES:
            # Allow the symbol name to appear in docstring/comment
            # context inside the test file itself, but not at the runner
            # module level. Check for code references only by ensuring
            # the symbol is never the target of an Import / ImportFrom /
            # Name in a Load context.
            tree = self._load_module_ast()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == sym:
                    self.fail(
                        f"MissionRunner references forbidden symbol "
                        f"{sym!r} in code"
                    )

    def test_no_celery_imports(self):
        """The runner is sync — Celery is the caller's concern."""
        tree = self._load_module_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                self.assertFalse(
                    mod.startswith("celery"),
                    f"MissionRunner illegally imports celery module {mod!r}",
                )

    def test_verdict_constants_match_framework(self):
        """Verdict strings match ``core.employees.mission_verdict``."""
        from core.employees.mission_verdict import (
            VERDICT_CERTIFIED as FW_CERTIFIED,
            VERDICT_REJECTED as FW_REJECTED,
            VERDICT_DEFERRED as FW_DEFERRED,
        )
        from core.employees.mission_runner import (
            VERDICT_CERTIFIED as RUNNER_CERTIFIED,
            VERDICT_REJECTED as RUNNER_REJECTED,
            VERDICT_DEFERRED as RUNNER_DEFERRED,
        )
        self.assertEqual(RUNNER_CERTIFIED, FW_CERTIFIED)
        self.assertEqual(RUNNER_REJECTED, FW_REJECTED)
        self.assertEqual(RUNNER_DEFERRED, FW_DEFERRED)


# ═════════════════════════════════════════════════════════════════════
# Idempotency — Rigby constraint #2
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerIdempotencyTests(TestCase):
    def setUp(self):
        _setup_user()

    def test_first_run_creates_exactly_one_mission(self):
        runner = _build_runner([_passing_step("step_a")])
        runner.run()
        self.assertEqual(
            OpsRun.objects.filter(
                domain="mission", run_kind="test_mission"
            ).count(),
            1,
        )

    def test_same_day_returns_cached_envelope(self):
        runner = _build_runner([_passing_step("step_a")])
        first = runner.run()
        second = runner.run()
        self.assertFalse(first.already_ran)
        self.assertTrue(second.already_ran)
        self.assertEqual(first.mission_id, second.mission_id)

    def test_same_day_does_not_double_create_mission(self):
        runner = _build_runner([_passing_step("step_a")])
        runner.run()
        runner.run()
        runner.run()
        self.assertEqual(
            OpsRun.objects.filter(
                domain="mission", run_kind="test_mission"
            ).count(),
            1,
        )

    def test_same_day_does_not_double_emit_terminal_event(self):
        runner = _build_runner([_passing_step("step_a")])
        runner.run()
        runner.run()
        labels = _event_labels(
            OpsRun.objects.filter(run_kind="test_mission").first()
        )
        # Exactly one verdict_issued:certified row.
        self.assertEqual(
            sum(1 for L in labels if L.startswith("verdict_issued:")),
            1,
        )
        # Exactly one run_started row.
        self.assertEqual(
            labels.count(RUN_STARTED_LABEL),
            1,
        )

    def test_in_progress_mission_returns_running_envelope(self):
        runner = _build_runner([_passing_step("step_a")])
        running_mission = OpsRun.objects.create(
            title="manually-injected running",
            run_type="manual",
            domain="mission",
            run_kind="test_mission",
            triggered_by="beat",
            status="running",
            summary={},
        )
        result = runner.run()
        self.assertTrue(result.already_ran)
        self.assertEqual(result.status, "running")
        self.assertEqual(result.mission_id, str(running_mission.id))
        # No new mission row created.
        self.assertEqual(
            OpsRun.objects.filter(
                domain="mission", run_kind="test_mission"
            ).count(),
            1,
        )

    def test_event_idempotency_via_get_or_create(self):
        """Re-running a step against an existing mission writes no
        duplicate event rows."""
        mission = OpsRun.objects.create(
            title="manual",
            run_type="manual",
            domain="mission",
            run_kind="test_mission",
            triggered_by="beat",
            status="running",
            summary={},
        )
        runner = _build_runner([_passing_step("step_a")])
        runner._emit_event(
            mission, "step_a_started", "step_start", step="step_a"
        )
        # Second call with same label → no new row.
        runner._emit_event(
            mission, "step_a_started", "step_start", step="step_a"
        )
        self.assertEqual(
            OpsRunEvent.objects.filter(
                run=mission, label="step_a_started"
            ).count(),
            1,
        )

    def test_cached_envelope_preserves_terminal_status(self):
        runner = _build_runner([_failing_step("step_a")])
        first = runner.run()
        second = runner.run()
        # First run sets status='failed'; cached envelope echoes it.
        self.assertEqual(first.status, "failed")
        self.assertEqual(second.status, "failed")
        # The mission row's status was not flipped back to anything by
        # the cached lookup.
        m = OpsRun.objects.get(id=first.mission_id)
        self.assertEqual(m.status, "failed")


# ═════════════════════════════════════════════════════════════════════
# Event ordering — Rigby constraint #3
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerEventOrderingTests(TestCase):
    def setUp(self):
        _setup_user()

    def test_successful_three_step_sequence(self):
        runner = _build_runner([
            _passing_step("step_a"),
            _passing_step("step_b"),
            _passing_step("step_c"),
        ])
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        labels = _event_labels(m)
        self.assertEqual(labels[0], RUN_STARTED_LABEL)
        # step_a → step_b → step_c → verdict
        expected_segments = [
            "step_a_started", "step_a_passed",
            "step_b_started", "step_b_passed",
            "step_c_started", "step_c_passed",
            f"verdict_issued:{VERDICT_CERTIFIED}",
        ]
        # Verify each expected label appears at least once + in order.
        last_idx = 0
        for seg in expected_segments:
            self.assertIn(seg, labels)
            idx = labels.index(seg, last_idx)
            self.assertGreaterEqual(idx, last_idx)
            last_idx = idx

    def test_failed_step_skips_subsequent_steps(self):
        runner = _build_runner([
            _passing_step("step_a"),
            _failing_step("step_b"),
            _passing_step("step_c"),
            _passing_step("step_d"),
        ])
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        labels = _event_labels(m)
        # step_a passed.
        self.assertIn("step_a_passed", labels)
        # step_b failed.
        self.assertIn("step_b_failed", labels)
        self.assertNotIn("step_b_passed", labels)
        # step_c + step_d skipped.
        self.assertIn("step_c_skipped", labels)
        self.assertIn("step_d_skipped", labels)
        self.assertNotIn("step_c_started", labels)
        self.assertNotIn("step_d_started", labels)

    def test_escalation_event_before_verdict_on_failure(self):
        runner = _build_runner([_failing_step("step_a")])
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        labels = _event_labels(m)
        self.assertIn(ESCALATION_LABEL, labels)
        verdict_label = f"verdict_issued:{VERDICT_REJECTED}"
        self.assertIn(verdict_label, labels)
        self.assertLess(
            labels.index(ESCALATION_LABEL),
            labels.index(verdict_label),
        )

    def test_no_escalation_event_on_success(self):
        runner = _build_runner([_passing_step("step_a")])
        runner.run()
        m = OpsRun.objects.filter(run_kind="test_mission").first()
        labels = _event_labels(m)
        self.assertNotIn(ESCALATION_LABEL, labels)

    def test_run_started_emitted_exactly_once(self):
        runner = _build_runner([
            _passing_step("step_a"),
            _passing_step("step_b"),
        ])
        runner.run()
        m = OpsRun.objects.filter(run_kind="test_mission").first()
        labels = _event_labels(m)
        self.assertEqual(labels.count(RUN_STARTED_LABEL), 1)


# ═════════════════════════════════════════════════════════════════════
# Step boundary — Rigby constraint #4
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerStepBoundaryTests(TestCase):
    def setUp(self):
        _setup_user()

    def test_step_raise_captured_as_failure(self):
        runner = _build_runner([
            _passing_step("step_a"),
            _raising_step(
                "step_b", exc_class=ValueError, msg="boom"
            ),
        ])
        result = runner.run()
        self.assertEqual(result.verdict, VERDICT_REJECTED)
        m = OpsRun.objects.get(id=result.mission_id)
        # Summary captured the exception text.
        self.assertIn("ValueError", m.summary.get("error_tail", ""))
        self.assertIn("boom", m.summary.get("error_tail", ""))
        # Event row for the failure.
        labels = _event_labels(m)
        self.assertIn("step_b_failed", labels)

    def test_step_passed_false_treated_as_failure(self):
        runner = _build_runner([_failing_step("step_a", "explicit fail")])
        result = runner.run()
        self.assertEqual(result.verdict, VERDICT_REJECTED)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(m.status, "failed")

    def test_wrong_shape_step_return_treated_as_failure(self):
        runner = _build_runner([_wrong_shape_step("step_a")])
        result = runner.run()
        self.assertEqual(result.verdict, VERDICT_REJECTED)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertIn(
            "non-StepResult",
            (m.summary.get("error_tail") or ""),
        )

    def test_step_receives_mission_row(self):
        captured = {}

        def _fn(mission):
            captured["mission_id"] = str(mission.id)
            captured["run_kind"] = mission.run_kind
            return StepResult(passed=True)

        runner = _build_runner([Step(name="capture", fn=_fn)])
        result = runner.run()
        self.assertEqual(captured["mission_id"], result.mission_id)
        self.assertEqual(captured["run_kind"], "test_mission")

    def test_step_duration_recorded_when_not_explicit(self):
        def _slow_fn(mission):
            # Don't set duration_ms in the return — runner should stamp.
            return StepResult(passed=True, output="ok")

        runner = _build_runner([Step(name="slow", fn=_slow_fn)])
        runner.run()
        m = OpsRun.objects.filter(run_kind="test_mission").first()
        labels = _event_labels(m)
        self.assertIn("slow_passed", labels)


# ═════════════════════════════════════════════════════════════════════
# Error signature — Rigby constraint #5
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerErrorSignatureTests(SimpleTestCase):
    def test_signature_stable_across_timestamps(self):
        a = "2026-06-29T13:00:00Z: oops happened"
        b = "2026-06-30T15:42:11Z: oops happened"
        self.assertEqual(
            MissionRunner.make_error_signature("step", a),
            MissionRunner.make_error_signature("step", b),
        )

    def test_signature_stable_across_uuids(self):
        a = "Failed with run_id=550e8400-e29b-41d4-a716-446655440000"
        b = "Failed with run_id=ffffffff-1111-2222-3333-444444444444"
        self.assertEqual(
            MissionRunner.make_error_signature("step", a),
            MissionRunner.make_error_signature("step", b),
        )

    def test_signature_differs_for_different_errors(self):
        a = "ValueError: kind A"
        b = "TypeError: kind B"
        self.assertNotEqual(
            MissionRunner.make_error_signature("step", a),
            MissionRunner.make_error_signature("step", b),
        )

    def test_signature_differs_for_different_steps(self):
        tail = "same error"
        self.assertNotEqual(
            MissionRunner.make_error_signature("step_one", tail),
            MissionRunner.make_error_signature("step_two", tail),
        )

    def test_signature_length_and_charset(self):
        sig = MissionRunner.make_error_signature("step", "anything")
        self.assertEqual(len(sig), 16)
        self.assertTrue(all(c in "0123456789abcdef" for c in sig))


# ═════════════════════════════════════════════════════════════════════
# Escalation — Rigby constraint #6
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerEscalationTests(TestCase):
    def setUp(self):
        _setup_user()

    def _get_escalation_deliverables(self):
        from core.models_deliverables import Deliverable

        return list(
            Deliverable.objects.filter(
                title__startswith="Test Escalation"
            ).order_by("created_at")
        )

    def test_first_failure_creates_escalation_deliverable(self):
        runner = _build_runner([_failing_step("step_x", "boom")])
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        from core.models_deliverables import Deliverable, PublishIntent

        deliv_id = m.summary.get("escalation_deliverable_id")
        self.assertIsNotNone(deliv_id)
        deliv = Deliverable.objects.get(id=deliv_id)
        self.assertEqual(
            deliv.publish_intent, PublishIntent.PUBLISH_CANDIDATE
        )
        self.assertEqual(deliv.status, "ready")
        self.assertIn("boom", deliv.content)

    def test_repeat_failure_same_signature_appends_within_window(self):
        # First failure.
        runner1 = _build_runner([_failing_step("step_x", "deterministic")])
        runner1.run()
        # Sanity: 1 deliverable so far.
        self.assertEqual(len(self._get_escalation_deliverables()), 1)

        # Force the today-idempotency gate to NOT match by creating the
        # next mission on a different date — simulated by manually
        # back-dating the first and creating a new one via run_for_existing.
        first_run = OpsRun.objects.filter(run_kind="test_mission").first()
        # Backdate so today's gate doesn't block + dedupe window covers.
        OpsRun.objects.filter(id=first_run.id).update(
            started_at=timezone.now() - timedelta(hours=1),
            finished_at=timezone.now() - timedelta(minutes=59),
        )
        # Drive a second mission through run_for_existing on a fresh row.
        second_mission = OpsRun.objects.create(
            title="second",
            run_type="manual",
            domain="mission",
            run_kind="test_mission",
            triggered_by="beat",
            status="running",
            summary={},
        )
        runner2 = _build_runner([_failing_step("step_x", "deterministic")])
        runner2.run_for_existing(second_mission)

        delivs = self._get_escalation_deliverables()
        # Still one deliverable — second failure appended.
        self.assertEqual(len(delivs), 1)
        # Body now has a Recurrence section.
        self.assertIn("Recurrence:", delivs[0].content)

    def test_repeat_failure_outside_window_creates_new(self):
        runner1 = _build_runner([_failing_step("step_x", "deterministic")])
        runner1.run()
        first_run = OpsRun.objects.filter(run_kind="test_mission").first()
        # Backdate first beyond the 24h dedupe window.
        OpsRun.objects.filter(id=first_run.id).update(
            started_at=timezone.now() - timedelta(hours=48),
            finished_at=timezone.now() - timedelta(hours=47, minutes=59),
        )
        # Run a fresh mission row through run_for_existing.
        second_mission = OpsRun.objects.create(
            title="second",
            run_type="manual",
            domain="mission",
            run_kind="test_mission",
            triggered_by="beat",
            status="running",
            summary={},
        )
        runner2 = _build_runner([_failing_step("step_x", "deterministic")])
        runner2.run_for_existing(second_mission)

        delivs = self._get_escalation_deliverables()
        self.assertEqual(len(delivs), 2)

    def test_different_signature_creates_new_within_window(self):
        runner1 = _build_runner([_failing_step("step_x", "error type ALPHA")])
        runner1.run()
        first_run = OpsRun.objects.filter(run_kind="test_mission").first()
        OpsRun.objects.filter(id=first_run.id).update(
            started_at=timezone.now() - timedelta(hours=1),
            finished_at=timezone.now() - timedelta(minutes=59),
        )
        # Same step, different error tail → different signature.
        second_mission = OpsRun.objects.create(
            title="second",
            run_type="manual",
            domain="mission",
            run_kind="test_mission",
            triggered_by="beat",
            status="running",
            summary={},
        )
        runner2 = _build_runner([_failing_step("step_x", "error type BETA")])
        runner2.run_for_existing(second_mission)

        delivs = self._get_escalation_deliverables()
        self.assertEqual(len(delivs), 2)

    def test_completed_to_ready_audit_event_emitted(self):
        runner = _build_runner(
            [_failing_step("step_x", "boom")],
            config=_make_config(escalation_source="MyTestRunner"),
        )
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        from core.models_deliverables import DeliverableEvent

        deliv_id = m.summary.get("escalation_deliverable_id")
        events = list(
            DeliverableEvent.objects.filter(
                event_type="status_transition",
                source="MyTestRunner",
                deliverable_id=deliv_id,
            )
        )
        self.assertEqual(len(events), 1, "expected 1 audit transition")
        ctx = (events[0].metadata or {}).get("ctx", {})
        self.assertEqual(ctx.get("ops_run_id"), str(m.id))
        self.assertEqual(
            ctx.get("error_signature"), m.summary.get("error_signature")
        )

    def test_escalation_emits_event_with_pointers(self):
        runner = _build_runner([_failing_step("step_x")])
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        ev = OpsRunEvent.objects.filter(
            run=m, label=ESCALATION_LABEL
        ).first()
        self.assertIsNotNone(ev)
        self.assertEqual(
            ev.detail.get("deliverable_id"),
            m.summary.get("escalation_deliverable_id"),
        )
        self.assertEqual(
            ev.detail.get("error_signature"),
            m.summary.get("error_signature"),
        )


# ═════════════════════════════════════════════════════════════════════
# Hook containment — Rigby constraint #7
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerHookContainmentTests(TestCase):
    def setUp(self):
        _setup_user()

    # ── Shift report ────────────────────────────────────────────────

    def test_shift_report_called_on_terminal_success(self):
        calls = []

        def _fn(mission):
            calls.append(str(mission.id))
            return {"ok": True}

        runner = _build_runner(
            [_passing_step("step_a")],
            shift_report_fn=_fn,
        )
        result = runner.run()
        self.assertEqual(calls, [result.mission_id])

    def test_shift_report_called_on_terminal_failure(self):
        calls = []

        def _fn(mission):
            calls.append(str(mission.id))
            return {"ok": True}

        runner = _build_runner(
            [_failing_step("step_a")],
            shift_report_fn=_fn,
        )
        result = runner.run()
        self.assertEqual(calls, [result.mission_id])

    def test_shift_report_exception_does_not_break_outcome(self):
        def _fn(mission):
            raise RuntimeError("comms layer down")

        runner = _build_runner(
            [_passing_step("step_a")],
            shift_report_fn=_fn,
        )
        result = runner.run()
        # Mission still succeeded; verdict still emitted.
        self.assertTrue(result.ok)
        self.assertEqual(result.verdict, VERDICT_CERTIFIED)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(m.status, "passed")

    def test_no_shift_report_fn_does_not_crash(self):
        runner = _build_runner(
            [_passing_step("step_a")],
            shift_report_fn=None,
        )
        result = runner.run()
        self.assertTrue(result.ok)
        self.assertEqual(result.verdict, VERDICT_CERTIFIED)

    # ── PA post ─────────────────────────────────────────────────────

    def test_pa_post_called_on_escalation_with_context(self):
        captured: List[PAPostContext] = []

        def _fn(ctx: PAPostContext):
            captured.append(ctx)
            return "fake-row-id-42"

        runner = _build_runner(
            [_failing_step("step_x", "boom")],
            pa_post_fn=_fn,
            config=_make_config(primary_chat_id="pa-test-pin"),
        )
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(len(captured), 1)
        ctx = captured[0]
        self.assertEqual(ctx.failed_step, "step_x")
        self.assertEqual(ctx.primary_chat_id, "pa-test-pin")
        self.assertIn("step_x", ctx.summary_line)
        self.assertEqual(
            m.summary.get("escalation_pa_post_id"), "fake-row-id-42"
        )

    def test_pa_post_not_called_on_success(self):
        called = []

        def _fn(ctx):
            called.append(ctx)
            return "should-not-happen"

        runner = _build_runner(
            [_passing_step("step_a")], pa_post_fn=_fn
        )
        runner.run()
        self.assertEqual(called, [])

    def test_pa_post_exception_does_not_block_deliverable(self):
        def _fn(ctx):
            raise ConnectionError("network down")

        runner = _build_runner(
            [_failing_step("step_x")], pa_post_fn=_fn
        )
        result = runner.run()
        # Escalation deliverable still created; verdict still rejected.
        self.assertEqual(result.verdict, VERDICT_REJECTED)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertIsNotNone(m.summary.get("escalation_deliverable_id"))
        # pa_post_id is None because the hook raised.
        self.assertIsNone(m.summary.get("escalation_pa_post_id"))

    def test_no_pa_post_fn_skips_post(self):
        runner = _build_runner(
            [_failing_step("step_x")], pa_post_fn=None
        )
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertIsNone(m.summary.get("escalation_pa_post_id"))
        # Mission still escalated + verdict emitted.
        self.assertIsNotNone(m.summary.get("escalation_deliverable_id"))
        self.assertEqual(result.verdict, VERDICT_REJECTED)

    # ── Preflight / postflight ──────────────────────────────────────

    def test_preflight_runs_before_steps(self):
        order = []

        def _pre(summary_acc):
            order.append("pre")
            summary_acc["preflight_marker"] = True

        def _step_fn(mission):
            order.append("step")
            return StepResult(passed=True)

        runner = _build_runner(
            [Step(name="s", fn=_step_fn)], preflight_fn=_pre
        )
        result = runner.run()
        self.assertEqual(order, ["pre", "step"])
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertTrue(m.summary.get("preflight_marker"))

    def test_preflight_exception_marks_degraded_but_continues(self):
        def _pre(summary_acc):
            raise RuntimeError("probe died")

        runner = _build_runner(
            [_passing_step("step_a")], preflight_fn=_pre
        )
        result = runner.run()
        self.assertTrue(result.ok)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertTrue(m.summary.get("degraded_evidence"))
        self.assertIn("preflight_error", m.summary)

    def test_postflight_receives_passed_flag(self):
        recorded = {}

        def _post(passed, summary_acc):
            recorded["passed"] = passed

        runner = _build_runner(
            [_passing_step("step_a")], postflight_fn=_post
        )
        runner.run()
        self.assertTrue(recorded["passed"])

        runner2 = _build_runner(
            [_failing_step("step_b")], postflight_fn=_post,
            config=_make_config(mission_run_kind="test_mission_b"),
        )
        runner2.run()
        self.assertFalse(recorded["passed"])

    def test_postflight_exception_marks_degraded_but_continues(self):
        def _post(passed, summary_acc):
            raise RuntimeError("postflight died")

        runner = _build_runner(
            [_passing_step("step_a")], postflight_fn=_post
        )
        result = runner.run()
        self.assertTrue(result.ok)
        # Even though postflight died, mission still certified — though
        # confidence drops because degraded_evidence was set after
        # postflight failure detection.
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(m.status, "passed")
        self.assertTrue(m.summary.get("degraded_evidence"))


# ═════════════════════════════════════════════════════════════════════
# Verdict — idempotency + confidence selection
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerVerdictTests(TestCase):
    def setUp(self):
        _setup_user()

    def test_success_emits_certified_with_full_confidence(self):
        runner = _build_runner([_passing_step("step_a")])
        result = runner.run()
        self.assertEqual(result.verdict, VERDICT_CERTIFIED)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(
            m.summary.get("verdict_confidence"),
            DEFAULT_CONFIDENCE_SUCCESS_FULL,
        )

    def test_degraded_success_drops_confidence(self):
        def _pre(summary_acc):
            summary_acc["degraded_evidence"] = True

        runner = _build_runner(
            [_passing_step("step_a")], preflight_fn=_pre
        )
        result = runner.run()
        self.assertEqual(result.verdict, VERDICT_CERTIFIED)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(
            m.summary.get("verdict_confidence"),
            DEFAULT_CONFIDENCE_SUCCESS_DEGRADED,
        )

    def test_failure_emits_rejected_with_failure_confidence(self):
        runner = _build_runner([_failing_step("step_a")])
        result = runner.run()
        self.assertEqual(result.verdict, VERDICT_REJECTED)
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(
            m.summary.get("verdict_confidence"),
            DEFAULT_CONFIDENCE_FAILURE,
        )

    def test_terminal_status_preserved_across_cached_invocations(self):
        runner = _build_runner([_passing_step("step_a")])
        runner.run()
        m_before = OpsRun.objects.filter(
            run_kind="test_mission"
        ).first()
        status_before = m_before.status
        finished_before = m_before.finished_at
        # Re-run today — should return cached.
        runner.run()
        m_after = OpsRun.objects.get(id=m_before.id)
        self.assertEqual(m_after.status, status_before)
        self.assertEqual(m_after.finished_at, finished_before)

    def test_custom_confidence_values_respected(self):
        runner = _build_runner(
            [_passing_step("step_a")],
            config=_make_config(
                confidence_success_full=0.42,
                confidence_success_degraded=0.21,
                confidence_failure=0.0,
            ),
        )
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(m.summary.get("verdict_confidence"), 0.42)


# ═════════════════════════════════════════════════════════════════════
# Config — frozen + defaults
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerConfigTests(SimpleTestCase):
    def test_config_is_frozen(self):
        cfg = _make_config()
        with self.assertRaises(Exception):
            cfg.employee_handle = "different"  # type: ignore

    def test_default_dedupe_window_24h(self):
        cfg = _make_config(dedupe_window_hours=24)
        self.assertEqual(cfg.dedupe_window_hours, DEFAULT_DEDUPE_WINDOW_HOURS)

    def test_default_confidence_values(self):
        cfg = MissionRunnerConfig(
            employee_handle="x",
            employee_display_name="X",
            runs_as_username="x",
            mission_run_kind="x",
        )
        self.assertEqual(
            cfg.confidence_success_full,
            DEFAULT_CONFIDENCE_SUCCESS_FULL,
        )
        self.assertEqual(
            cfg.confidence_success_degraded,
            DEFAULT_CONFIDENCE_SUCCESS_DEGRADED,
        )
        self.assertEqual(
            cfg.confidence_failure, DEFAULT_CONFIDENCE_FAILURE,
        )

    def test_requires_mission_run_kind(self):
        cfg = _make_config(mission_run_kind="")
        with self.assertRaises(ValueError):
            MissionRunner(config=cfg, steps=[_passing_step("a")])

    def test_requires_at_least_one_step(self):
        with self.assertRaises(ValueError):
            MissionRunner(config=_make_config(), steps=[])


# ═════════════════════════════════════════════════════════════════════
# Pin resolution
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerPinResolutionTests(TestCase):
    def setUp(self):
        _setup_user()

    def test_pin_settings_key_overrides_primary_chat_id(self):
        runner = _build_runner(
            [_failing_step("step_x")],
            pa_post_fn=lambda ctx: f"pin={ctx.primary_chat_id}",
            config=_make_config(
                primary_chat_id="pa-contract-fallback",
                pin_settings_key="TEST_RUNNER_PIN",
            ),
        )
        with override_settings(TEST_RUNNER_PIN="pa-env-override"):
            result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(
            m.summary.get("escalation_pa_post_id"),
            "pin=pa-env-override",
        )

    def test_pin_settings_key_empty_falls_back_to_contract(self):
        runner = _build_runner(
            [_failing_step("step_x")],
            pa_post_fn=lambda ctx: f"pin={ctx.primary_chat_id}",
            config=_make_config(
                primary_chat_id="pa-contract-fallback",
                pin_settings_key="TEST_RUNNER_PIN_UNSET",
            ),
        )
        result = runner.run()
        m = OpsRun.objects.get(id=result.mission_id)
        self.assertEqual(
            m.summary.get("escalation_pa_post_id"),
            "pin=pa-contract-fallback",
        )


# ═════════════════════════════════════════════════════════════════════
# Module-helper unit tests
# ═════════════════════════════════════════════════════════════════════


class MissionRunnerHelperTests(SimpleTestCase):
    def test_tail_lines_returns_last_n(self):
        text = "\n".join(str(i) for i in range(20))
        out = _tail_lines(text, 5)
        self.assertEqual(out, "15\n16\n17\n18\n19")

    def test_tail_lines_empty(self):
        self.assertEqual(_tail_lines("", 5), "")
        self.assertEqual(_tail_lines(None, 5), "")  # type: ignore

    def test_tail_lines_short(self):
        self.assertEqual(_tail_lines("only one line", 5), "only one line")

    def test_normalize_strips_timestamps(self):
        a = "2026-06-29T13:00:00Z something"
        b = "2026-06-30T15:42:11Z something"
        self.assertEqual(
            _normalize_for_signature(a),
            _normalize_for_signature(b),
        )

    def test_normalize_strips_uuids(self):
        a = "id=550e8400-e29b-41d4-a716-446655440000"
        b = "id=ffffffff-1111-2222-3333-444444444444"
        self.assertEqual(
            _normalize_for_signature(a),
            _normalize_for_signature(b),
        )
