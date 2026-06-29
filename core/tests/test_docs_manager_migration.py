"""Session 1256 PR 1.2 — Documentation Manager → MissionRunner migration tests.

These tests prove the post-PR-1.2 wiring of the Documentation Manager
job. They complement (do NOT replace) the existing
``test_documentation_manager_routine`` + ``test_documentation_manager_escalation``
suites which prove **observable behavior** is preserved. The tests
here prove the **architectural shape**: that the migration actually
happened and that the docs-specific bits live in the right places.

Real PostgreSQL (per the S1234 memory rule).

Run::

    .venv/bin/python manage.py test core.tests.test_docs_manager_migration -v2
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from core.employees import DOCUMENTATION_MANAGER, RIGBY
from core.employees.mission_runner import (
    MissionRunner,
    MissionRunnerConfig,
    Step,
)
from core.jobs.docs_cascade import (
    CONFIDENCE_FAILURE,
    CONFIDENCE_SUCCESS_DEGRADED,
    CONFIDENCE_SUCCESS_FULL,
    DELIVERABLE_TITLE_PREFIX,
    DONKEY_BETZ_WORKSPACE_NAME,
    DRIFT_LABEL,
    ESCALATION_SOURCE,
    MISSION_RUN_KIND,
    PIN_SETTINGS_KEY,
    STEP_5_SKIPPED_LABEL,
    build_docs_manager_runner,
)


User = get_user_model()


# ═════════════════════════════════════════════════════════════════════
# Architectural shape
# ═════════════════════════════════════════════════════════════════════


class DocsCascadeBuilderShapeTests(SimpleTestCase):
    """Verify build_docs_manager_runner() returns a properly-wired runner."""

    def test_builder_returns_mission_runner_instance(self):
        runner = build_docs_manager_runner()
        self.assertIsInstance(runner, MissionRunner)

    def test_builder_returns_fresh_instance_each_call(self):
        """Concurrent runs must not share state (mission_holder closure)."""
        r1 = build_docs_manager_runner()
        r2 = build_docs_manager_runner()
        self.assertIsNot(r1, r2)

    def test_config_has_docs_cascade_run_kind(self):
        runner = build_docs_manager_runner()
        self.assertEqual(runner.config.mission_run_kind, "docs_cascade")
        self.assertEqual(
            runner.config.mission_run_kind,
            DOCUMENTATION_MANAGER.mission_run_kind,
        )

    def test_config_identity_matches_rigby(self):
        runner = build_docs_manager_runner()
        self.assertEqual(runner.config.employee_handle, RIGBY.handle)
        self.assertEqual(
            runner.config.employee_display_name, RIGBY.display_name
        )
        self.assertEqual(
            runner.config.runs_as_username, RIGBY.runs_as_username
        )

    def test_config_confidence_values(self):
        runner = build_docs_manager_runner()
        self.assertEqual(
            runner.config.confidence_success_full,
            CONFIDENCE_SUCCESS_FULL,
        )
        self.assertEqual(
            runner.config.confidence_success_degraded,
            CONFIDENCE_SUCCESS_DEGRADED,
        )
        self.assertEqual(
            runner.config.confidence_failure, CONFIDENCE_FAILURE,
        )
        self.assertEqual(runner.config.confidence_success_full, 0.95)
        self.assertEqual(runner.config.confidence_success_degraded, 0.6)
        self.assertEqual(runner.config.confidence_failure, 0.0)

    def test_config_escalation_source_is_docs_manager(self):
        runner = build_docs_manager_runner()
        self.assertEqual(runner.config.escalation_source, "DocsManager")
        self.assertEqual(runner.config.escalation_source, ESCALATION_SOURCE)

    def test_config_escalation_title_prefix(self):
        runner = build_docs_manager_runner()
        self.assertEqual(
            runner.config.escalation_title_prefix, DELIVERABLE_TITLE_PREFIX
        )
        self.assertEqual(
            runner.config.escalation_title_prefix,
            "Docs Manager Escalation",
        )

    def test_config_workspace_name(self):
        runner = build_docs_manager_runner()
        self.assertEqual(
            runner.config.workspace_name, DONKEY_BETZ_WORKSPACE_NAME
        )
        self.assertEqual(runner.config.workspace_name, "Donkey Betz")

    def test_config_pin_settings_key(self):
        runner = build_docs_manager_runner()
        self.assertEqual(runner.config.pin_settings_key, PIN_SETTINGS_KEY)
        self.assertEqual(
            runner.config.pin_settings_key, "RIGBY_PRIMARY_PA_PIN"
        )

    def test_config_dedupe_window_24h(self):
        runner = build_docs_manager_runner()
        self.assertEqual(runner.config.dedupe_window_hours, 24)

    def test_runner_has_four_cascade_steps(self):
        runner = build_docs_manager_runner()
        self.assertEqual(len(runner.steps), 4)
        for s in runner.steps:
            self.assertIsInstance(s, Step)

    def test_runner_step_names_match_pre_1_2_labels(self):
        runner = build_docs_manager_runner()
        names = [s.name for s in runner.steps]
        self.assertEqual(
            names,
            [
                "step_1_index",
                "step_2_corpus",
                "step_3_sync",
                "step_4_embed",
            ],
        )

    def test_runner_has_preflight_hook(self):
        runner = build_docs_manager_runner()
        self.assertIsNotNone(runner.preflight_fn)

    def test_runner_has_postflight_hook(self):
        runner = build_docs_manager_runner()
        self.assertIsNotNone(runner.postflight_fn)

    def test_runner_has_pa_post_hook(self):
        runner = build_docs_manager_runner()
        self.assertIsNotNone(runner.pa_post_fn)

    def test_runner_has_shift_report_hook(self):
        runner = build_docs_manager_runner()
        self.assertIsNotNone(runner.shift_report_fn)

    def test_runner_has_escalation_spec_factory(self):
        runner = build_docs_manager_runner()
        self.assertIsNotNone(runner.escalation_deliverable_spec_factory)

    def test_runner_has_escalation_body_formatter(self):
        runner = build_docs_manager_runner()
        self.assertIsNotNone(runner.escalation_body_formatter)


class CeleryTaskFacadeTests(SimpleTestCase):
    """The Celery task wraps MissionRunner.

    Tests the *shape* of the task — the actual execution end-to-end is
    covered by the existing routine + escalation suites.
    """

    def test_task_module_re_exports_helpers_for_test_compat(self):
        """Existing tests import via tasks_documentation_manager; verify."""
        import core.tasks_documentation_manager as tdm

        # Constants
        self.assertEqual(tdm.MISSION_RUN_KIND, "docs_cascade")
        self.assertEqual(tdm.DRIFT_LABEL, "step_5_drift_observed")
        self.assertEqual(tdm.ERROR_TAIL_LINES_FIRST, 100)
        self.assertEqual(tdm.ERROR_TAIL_LINES_RECURRENCE, 30)

        # Functions
        self.assertTrue(callable(tdm.rigby_documentation_manager_daily))
        self.assertTrue(callable(tdm._probe_documents_count))
        self.assertTrue(callable(tdm._probe_embeddings_count))
        self.assertTrue(callable(tdm._probe_docs_indexed_count))
        self.assertTrue(callable(tdm._run_drift_observation))
        self.assertTrue(callable(tdm._signature_for))
        self.assertTrue(callable(tdm._force_deliverable_ready))
        self.assertTrue(callable(tdm._emit_event))
        self.assertTrue(callable(tdm._tail_lines))
        self.assertTrue(callable(tdm.build_docs_manager_runner))

    def test_signature_for_delegates_to_mission_runner(self):
        """_signature_for is a wrapper; should match MissionRunner.make_error_signature."""
        import core.tasks_documentation_manager as tdm

        a = tdm._signature_for("step_x", "synthetic error")
        b = MissionRunner.make_error_signature("step_x", "synthetic error")
        self.assertEqual(a, b)

    def test_force_deliverable_ready_validates_inputs(self):
        """Empty error_signature or null ops_run_id → ValueError."""
        import core.tasks_documentation_manager as tdm

        with self.assertRaises(ValueError):
            tdm._force_deliverable_ready(
                "deadbeef-dead-beef-dead-beefdeadbeef",
                ops_run_id="00000000-0000-0000-0000-000000000000",
                error_signature="",
            )
        with self.assertRaises(ValueError):
            tdm._force_deliverable_ready(
                "deadbeef-dead-beef-dead-beefdeadbeef",
                ops_run_id=None,
                error_signature="abc",
            )


# ═════════════════════════════════════════════════════════════════════
# End-to-end behavior preservation
# ═════════════════════════════════════════════════════════════════════


class EndToEndMigrationTests(TestCase):
    """Drive the task through real DB + verify the post-1.2 shape.

    Cascades are mocked at the docs_cascade module level (per the
    updated patch paths). Asserts: task returns MissionRunner result
    envelope shape; OpsRun has correct domain + run_kind; OpsRunEvent
    timeline includes the singular ``step_5_drift_observed`` event
    on success.
    """

    def setUp(self):
        User.objects.get_or_create(
            username="chris",
            defaults={"email": "chris@test.donkey"},
        )

    def _mock_all_pass(self):
        from contextlib import ExitStack
        from unittest.mock import MagicMock, patch

        stack = ExitStack()
        cc = stack.enter_context(
            patch("core.jobs.docs_cascade.call_command")
        )
        cc.return_value = None
        sp = stack.enter_context(
            patch("core.jobs.docs_cascade.subprocess.run")
        )
        sp.return_value = MagicMock(
            returncode=0, stdout="ok\n", stderr=""
        )
        # Stub the probes so drift observation has clean data.
        stack.enter_context(
            patch(
                "core.jobs.docs_cascade._probe_documents_count",
                return_value=10,
            )
        )
        stack.enter_context(
            patch(
                "core.jobs.docs_cascade._probe_embeddings_count",
                return_value=100,
            )
        )
        stack.enter_context(
            patch(
                "core.jobs.docs_cascade._probe_docs_indexed_count",
                return_value=10,
            )
        )
        return stack

    def test_task_returns_mission_runner_envelope_shape(self):
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_all_pass():
            result = rigby_documentation_manager_daily()

        # Envelope keys produced by MissionRunResult.as_dict()
        for k in (
            "ok",
            "mission_id",
            "status",
            "verdict",
            "wall_time_ms",
            "summary",
            "already_ran",
        ):
            self.assertIn(k, result, f"missing envelope key {k!r}")
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["verdict"], "certified")
        self.assertFalse(result["already_ran"])

    def test_ops_run_persisted_with_docs_cascade_run_kind(self):
        from core.models_ops_runs import OpsRun
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_all_pass():
            result = rigby_documentation_manager_daily()

        run = OpsRun.objects.get(id=result["mission_id"])
        self.assertEqual(run.domain, "mission")
        self.assertEqual(run.run_kind, MISSION_RUN_KIND)
        self.assertEqual(run.run_kind, "docs_cascade")
        self.assertEqual(run.status, "passed")

    def test_summary_contains_docs_specific_keys(self):
        from core.models_ops_runs import OpsRun
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_all_pass():
            result = rigby_documentation_manager_daily()

        run = OpsRun.objects.get(id=result["mission_id"])
        for k in (
            "docs_indexed_count",
            "documents_count_before",
            "documents_count_after",
            "embeddings_count_before",
            "embeddings_count_after",
            "embedding_delta",
            "drift_count",
            "drift_items_count",
            "degraded_evidence",
            "wall_time_ms",
            "failed_step",
        ):
            self.assertIn(
                k, run.summary, f"summary missing docs-specific key {k!r}"
            )

    def test_event_timeline_includes_singular_drift_event_on_success(self):
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_all_pass():
            result = rigby_documentation_manager_daily()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at", "id")
            .values_list("label", flat=True)
        )

        # Singular drift event present (not _started/_passed pair).
        self.assertIn(DRIFT_LABEL, labels)
        self.assertNotIn(f"{DRIFT_LABEL}_started", labels)
        self.assertNotIn(f"{DRIFT_LABEL}_passed", labels)

        # And the step 5 skipped label is NOT emitted on success.
        self.assertNotIn(STEP_5_SKIPPED_LABEL, labels)

        # Steps 1-4 emit the standard runner paired events.
        for step in ("step_1_index", "step_2_corpus", "step_3_sync", "step_4_embed"):
            self.assertIn(f"{step}_started", labels)
            self.assertIn(f"{step}_passed", labels)

    def test_idempotency_second_call_returns_already_ran(self):
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_all_pass():
            first = rigby_documentation_manager_daily()
            second = rigby_documentation_manager_daily()

        self.assertFalse(first["already_ran"])
        self.assertTrue(second["already_ran"])
        self.assertEqual(first["mission_id"], second["mission_id"])


# ═════════════════════════════════════════════════════════════════════
# Tasks file thinness
# ═════════════════════════════════════════════════════════════════════


class TasksFileThinnessTests(SimpleTestCase):
    """Confirm tasks_documentation_manager.py is now a thin facade."""

    def test_tasks_file_under_200_lines(self):
        from pathlib import Path

        path = (
            Path(__file__).resolve().parents[1]
            / "tasks_documentation_manager.py"
        )
        line_count = sum(1 for _ in path.open())
        self.assertLess(
            line_count,
            200,
            f"tasks_documentation_manager.py grew to {line_count} lines — "
            "should be a thin facade (<200 lines).",
        )

    def test_docs_cascade_module_holds_step_implementations(self):
        """Cascade step implementations live in docs_cascade, not the task module."""
        import inspect

        from core.jobs import docs_cascade
        # The 4 step functions must be defined in docs_cascade.
        for step_name in (
            "step_1_build_docs_index",
            "step_2_build_rag_corpus",
            "step_3_sync_docs_index_to_documents",
            "step_4_embed",
        ):
            fn = getattr(docs_cascade, step_name, None)
            self.assertIsNotNone(
                fn, f"docs_cascade missing step {step_name!r}"
            )
            mod = inspect.getmodule(fn)
            self.assertEqual(mod.__name__, "core.jobs.docs_cascade")


# ═════════════════════════════════════════════════════════════════════
# Closure-capture workaround safety (Rigby PR 1.2 SIGN-WITH-EDITS)
# ═════════════════════════════════════════════════════════════════════
#
# The docs cascade uses a closure-capture pattern to give postflight
# access to the mission row that MissionRunner's postflight_fn
# signature does not pass. These tests prove the workaround is safe:
#
#   * Mission is captured before postflight runs
#   * Missing capture fails loud (no silent fallback)
#   * Each runner has its own holder (no cross-run bleed)
#   * Event labels + order match pre-PR-1.2 behavior


class ClosureCaptureSafetyTests(TestCase):
    """Rigby PR 1.2 SIGN-WITH-EDITS — workaround must fail loud."""

    def setUp(self):
        User.objects.get_or_create(
            username="chris",
            defaults={"email": "chris@test.donkey"},
        )

    def test_postflight_raises_when_mission_holder_empty(self):
        """Empty holder → RuntimeError (no silent fallback)."""
        from core.jobs.docs_cascade import _make_postflight

        postflight = _make_postflight(mission_holder={})
        with self.assertRaises(RuntimeError) as ctx:
            postflight(True, {})
        self.assertIn(
            "without a captured mission row",
            str(ctx.exception),
        )

    def test_step_wrapper_raises_on_none_mission(self):
        """A null mission at step entry → RuntimeError."""
        from core.employees.mission_runner import StepResult
        from core.jobs.docs_cascade import _make_mission_capturing_step

        def _inner(mission):
            return StepResult(passed=True)

        wrapped = _make_mission_capturing_step(_inner, mission_holder={})
        with self.assertRaises(RuntimeError) as ctx:
            wrapped(None)
        self.assertIn("mission=None", str(ctx.exception))

    def test_step_wrapper_captures_mission_into_holder(self):
        """The wrapper writes the mission into the holder before calling
        the inner step fn."""
        from core.employees.mission_runner import StepResult
        from core.jobs.docs_cascade import _make_mission_capturing_step
        from core.models_ops_runs import OpsRun

        # Synthetic mission row.
        run = OpsRun.objects.create(
            title="capture-test",
            run_type="manual",
            domain="mission",
            run_kind="docs_cascade",
            triggered_by="manual",
            status="running",
            summary={},
        )

        holder: dict = {}

        def _inner(mission):
            # By the time inner runs, the holder must already have the
            # mission (capture happens BEFORE inner is invoked).
            self.assertEqual(mission_holder_get(holder), str(run.id))
            return StepResult(passed=True)

        def mission_holder_get(h):
            m = h.get("mission")
            return str(m.id) if m is not None else None

        wrapped = _make_mission_capturing_step(_inner, holder)
        wrapped(run)
        self.assertEqual(holder["mission"], run)

    def test_two_runners_have_independent_mission_holders(self):
        """Each build_docs_manager_runner() call must produce a runner
        with its own mission_holder closure (no cross-run bleed)."""
        from core.jobs.docs_cascade import build_docs_manager_runner

        r1 = build_docs_manager_runner()
        r2 = build_docs_manager_runner()

        # Steps captured into the runner instances are wrapped by the
        # builder. The wrappers close over the *holder*, not the runner.
        # Inspecting the closure cells reveals whether they share state.
        def _extract_holder(step_fn):
            # _wrapped closes over (base_step_fn, mission_holder); the
            # holder is the dict cell.
            for cell in step_fn.__closure__ or ():
                if isinstance(cell.cell_contents, dict):
                    return cell.cell_contents
            return None

        holders_r1 = {id(_extract_holder(s.fn)) for s in r1.steps}
        holders_r2 = {id(_extract_holder(s.fn)) for s in r2.steps}

        # Within one runner, all step wrappers share the SAME holder.
        self.assertEqual(len(holders_r1), 1)
        self.assertEqual(len(holders_r2), 1)

        # Across runners, holders are DIFFERENT objects.
        self.assertNotEqual(
            holders_r1.pop(), holders_r2.pop(),
            "build_docs_manager_runner() must produce a fresh "
            "mission_holder per call — cross-run bleed would corrupt "
            "step_5 event emission",
        )

    def test_postflight_with_captured_mission_succeeds_silently(self):
        """Sanity check: when the holder IS populated, postflight runs
        normally (validates the guard doesn't false-positive)."""
        from core.jobs.docs_cascade import _make_postflight
        from core.models_ops_runs import OpsRun

        run = OpsRun.objects.create(
            title="postflight-positive",
            run_type="manual",
            domain="mission",
            run_kind="docs_cascade",
            triggered_by="manual",
            status="running",
            summary={},
        )

        # Failure path postflight does no probes that hit real
        # docs/_index.json; just emits step_5_skipped. The default
        # probes return None safely.
        from unittest.mock import patch

        postflight = _make_postflight({"mission": run})
        summary_acc: dict = {}
        with patch(
            "core.jobs.docs_cascade._probe_documents_count",
            return_value=None,
        ), patch(
            "core.jobs.docs_cascade._probe_embeddings_count",
            return_value=None,
        ):
            postflight(False, summary_acc)

        # step_5_skipped event was emitted on the captured mission.
        from core.models_ops_runs import OpsRunEvent
        self.assertTrue(
            OpsRunEvent.objects.filter(
                run=run, label="step_5_skipped"
            ).exists()
        )


class EventLabelOrderPreservationTests(TestCase):
    """Rigby PR 1.2 SIGN-WITH-EDITS — event sequence matches pre-1.2."""

    def setUp(self):
        User.objects.get_or_create(
            username="chris",
            defaults={"email": "chris@test.donkey"},
        )

    def _mock_all_pass(self):
        from contextlib import ExitStack
        from unittest.mock import MagicMock, patch

        stack = ExitStack()
        cc = stack.enter_context(
            patch("core.jobs.docs_cascade.call_command")
        )
        cc.return_value = None
        sp = stack.enter_context(
            patch("core.jobs.docs_cascade.subprocess.run")
        )
        sp.return_value = MagicMock(
            returncode=0, stdout="ok\n", stderr=""
        )
        stack.enter_context(
            patch(
                "core.jobs.docs_cascade._probe_documents_count",
                return_value=10,
            )
        )
        stack.enter_context(
            patch(
                "core.jobs.docs_cascade._probe_embeddings_count",
                return_value=100,
            )
        )
        stack.enter_context(
            patch(
                "core.jobs.docs_cascade._probe_docs_indexed_count",
                return_value=10,
            )
        )
        return stack

    def _mock_step_fails(self, fail_at: str):
        from contextlib import ExitStack
        from unittest.mock import patch

        def _cc_side(cmd, *args, **kwargs):
            if cmd == fail_at:
                raise SystemExit(2)
            return None

        stack = ExitStack()
        stack.enter_context(
            patch(
                "core.jobs.docs_cascade.call_command",
                side_effect=_cc_side,
            )
        )
        return stack

    def test_success_event_order_matches_pre_1_2(self):
        """Successful run produces the canonical pre-1.2 event sequence."""
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_all_pass():
            result = rigby_documentation_manager_daily()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at", "id")
            .values_list("label", flat=True)
        )

        # Canonical pre-1.2 sequence — exact match:
        expected = [
            "run_started",
            "step_1_index_started", "step_1_index_passed",
            "step_2_corpus_started", "step_2_corpus_passed",
            "step_3_sync_started", "step_3_sync_passed",
            "step_4_embed_started", "step_4_embed_passed",
            "step_5_drift_observed",
            "verdict_issued:certified",
        ]
        self.assertEqual(labels, expected)

    def test_step_3_failure_emits_step_5_skipped_not_drift(self):
        """Failure mid-cascade emits step_5_skipped, NOT step_5_drift_observed."""
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_step_fails("sync_docs_index_to_documents"):
            result = rigby_documentation_manager_daily()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at", "id")
            .values_list("label", flat=True)
        )

        # Step 3 failed; step 4 was skipped; step_5_skipped emitted by
        # the docs-cascade postflight (NOT step_5_drift_observed).
        self.assertIn("step_3_sync_failed", labels)
        self.assertIn("step_4_embed_skipped", labels)
        self.assertIn("step_5_skipped", labels)
        self.assertNotIn("step_5_drift_observed", labels)

        # And the escalation + rejected verdict events.
        self.assertIn("escalation_emitted", labels)
        self.assertIn("verdict_issued:rejected", labels)

    def test_no_duplicate_step_5_events_on_success(self):
        """Sanity: success emits exactly one step_5_drift_observed and
        zero step_5_skipped."""
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_all_pass():
            result = rigby_documentation_manager_daily()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .values_list("label", flat=True)
        )
        self.assertEqual(labels.count("step_5_drift_observed"), 1)
        self.assertEqual(labels.count("step_5_skipped"), 0)

    def test_no_duplicate_step_5_events_on_failure(self):
        """Sanity: failure emits exactly one step_5_skipped and zero
        step_5_drift_observed."""
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        with self._mock_step_fails("build_docs_index"):
            result = rigby_documentation_manager_daily()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .values_list("label", flat=True)
        )
        self.assertEqual(labels.count("step_5_skipped"), 1)
        self.assertEqual(labels.count("step_5_drift_observed"), 0)
