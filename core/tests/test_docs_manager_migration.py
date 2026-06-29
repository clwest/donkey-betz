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
# PostflightContext seam (PR 1.3+)
# ═════════════════════════════════════════════════════════════════════
#
# PR 1.3 replaced the closure-capture workaround with MissionRunner's
# PostflightContext. The docs cascade postflight now reads ctx.mission
# directly. These tests verify:
#
#   * docs_cascade declares the new context-shaped postflight
#   * the postflight raises if ctx.mission is None (defensive guard)
#   * the postflight emits step_5_skipped on failure with ctx.mission
#   * the closure-capture surface is fully gone from docs_cascade
#   * build_docs_manager_runner is pure (no per-call mutable state)


class PostflightContextTests(TestCase):
    """PR 1.3 — postflight uses PostflightContext instead of closure-capture."""

    def setUp(self):
        User.objects.get_or_create(
            username="chris",
            defaults={"email": "chris@test.donkey"},
        )

    def test_docs_cascade_postflight_uses_single_context_signature(self):
        """The hook installed by the builder takes a single PostflightContext
        argument (not the legacy passed/summary_acc pair)."""
        import inspect

        from core.jobs.docs_cascade import build_docs_manager_runner

        runner = build_docs_manager_runner()
        sig = inspect.signature(runner.postflight_fn)
        positional = [
            p for p in sig.parameters.values()
            if p.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            and p.default is inspect.Parameter.empty
        ]
        self.assertEqual(
            len(positional), 1,
            "docs_cascade postflight should accept a single "
            "PostflightContext argument (PR 1.3+)",
        )

    def test_mission_runner_routes_to_context_signature(self):
        """MissionRunner detects the 1-arg signature + records True."""
        from core.jobs.docs_cascade import build_docs_manager_runner

        runner = build_docs_manager_runner()
        self.assertTrue(
            runner._postflight_uses_context,
            "Runner should detect the docs cascade postflight as a "
            "context-shape hook (1 required positional arg)",
        )

    def test_postflight_raises_when_ctx_mission_is_none(self):
        """Defensive guard — empty ctx.mission → RuntimeError."""
        from core.employees.mission_runner import PostflightContext
        from core.jobs.docs_cascade import _postflight

        ctx = PostflightContext(
            mission=None, passed=True, summary_acc={}
        )
        with self.assertRaises(RuntimeError) as exc_info:
            _postflight(ctx)
        self.assertIn("ctx.mission=None", str(exc_info.exception))

    def test_postflight_emits_step_5_skipped_on_failure_path(self):
        """When ctx.passed=False, emit step_5_skipped on ctx.mission."""
        from unittest.mock import patch

        from core.employees.mission_runner import PostflightContext
        from core.jobs.docs_cascade import _postflight
        from core.models_ops_runs import OpsRun, OpsRunEvent

        run = OpsRun.objects.create(
            title="postflight-fail-test",
            run_type="manual",
            domain="mission",
            run_kind="docs_cascade",
            triggered_by="manual",
            status="running",
            summary={},
        )
        ctx = PostflightContext(
            mission=run, passed=False, summary_acc={}
        )
        with patch(
            "core.jobs.docs_cascade._probe_documents_count",
            return_value=None,
        ), patch(
            "core.jobs.docs_cascade._probe_embeddings_count",
            return_value=None,
        ):
            _postflight(ctx)

        self.assertTrue(
            OpsRunEvent.objects.filter(
                run=run, label="step_5_skipped"
            ).exists()
        )

    def test_postflight_emits_step_5_drift_observed_on_success_path(self):
        """When ctx.passed=True, run drift observation + emit drift event."""
        from unittest.mock import patch

        from core.employees.mission_runner import PostflightContext
        from core.jobs.docs_cascade import _postflight
        from core.models_ops_runs import OpsRun, OpsRunEvent

        run = OpsRun.objects.create(
            title="postflight-pass-test",
            run_type="manual",
            domain="mission",
            run_kind="docs_cascade",
            triggered_by="manual",
            status="running",
            summary={},
        )
        ctx = PostflightContext(
            mission=run, passed=True, summary_acc={}
        )
        with patch(
            "core.jobs.docs_cascade._probe_docs_indexed_count",
            return_value=10,
        ), patch(
            "core.jobs.docs_cascade._probe_documents_count",
            return_value=10,
        ), patch(
            "core.jobs.docs_cascade._probe_embeddings_count",
            return_value=100,
        ), patch(
            "core.jobs.docs_cascade._run_drift_observation",
            return_value=(3, 3, False),
        ):
            _postflight(ctx)

        self.assertEqual(ctx.summary_acc["drift_count"], 3)
        self.assertEqual(ctx.summary_acc["drift_items_count"], 3)

    def test_docs_cascade_no_closure_capture_surface(self):
        """The closure-capture helpers must be deleted from docs_cascade."""
        from core.jobs import docs_cascade

        # The PR 1.2 helpers must be gone.
        self.assertFalse(
            hasattr(docs_cascade, "_make_mission_capturing_step"),
            "_make_mission_capturing_step should be deleted in PR 1.3",
        )
        # _make_postflight was the closure-capture factory; replaced by
        # a top-level _postflight function. _make_postflight may exist
        # as a function name if reused; verify it's NOT the closure
        # factory it used to be by checking its signature shape.
        if hasattr(docs_cascade, "_make_postflight"):
            import inspect
            sig = inspect.signature(docs_cascade._make_postflight)
            params = list(sig.parameters.values())
            self.assertEqual(
                len(params), 0,
                "_make_postflight should be parameter-less if it "
                "still exists; PR 1.3 closure-capture factory takes "
                "a mission_holder dict",
            )

    def test_build_docs_manager_runner_is_pure(self):
        """No per-call mutable state — two builds produce step_fns that
        do NOT close over a shared dict."""
        from core.jobs.docs_cascade import build_docs_manager_runner

        r1 = build_docs_manager_runner()
        r2 = build_docs_manager_runner()

        def _has_dict_closure_cell(fn):
            for cell in fn.__closure__ or ():
                if isinstance(cell.cell_contents, dict):
                    return True
            return False

        for s in r1.steps + r2.steps:
            self.assertFalse(
                _has_dict_closure_cell(s.fn),
                f"Step {s.name!r} closes over a dict — PR 1.3 should "
                "have removed the closure-capture wrappers",
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
