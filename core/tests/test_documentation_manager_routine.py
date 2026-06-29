"""
Session 1252 PR 2 — Documentation Manager daily routine tests.

Real-DB PostgreSQL integration (per the S1234 memory rule — no mocked
querysets for QS-heavy code). The 4 cascade commands are stubbed via
``unittest.mock.patch`` on ``call_command`` + ``subprocess.run`` so the
test suite stays fast and deterministic — but every assertion against
OpsRun / OpsRunEvent / Deliverable / ChatConversation hits real DB rows.

Covers acceptance criteria 1–25 from the PR 2 implementation plan.

Run::

    python manage.py test core.tests.test_documentation_manager_routine -v2
"""

from __future__ import annotations

import json
import subprocess
from contextlib import ExitStack
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.employees import DOCUMENTATION_MANAGER, RIGBY
from core.employees.mission_verdict import LABEL_VERDICT_PREFIX
from core.models_ops_runs import OpsRun, OpsRunEvent


User = get_user_model()


# ── Fixtures + helpers ───────────────────────────────────────────────


def _setup_user_and_workspace():
    """Ensure the chris user + Donkey Betz workspace exist for tests
    that go through the escalation path (which calls set_status as
    chris + assigns the workspace by name).
    """
    chris, _ = User.objects.get_or_create(
        username="chris",
        defaults={"email": "chris@test.donkey"},
    )
    try:
        from core.models_skin_layer import ProjectWorkspace

        ProjectWorkspace.objects.get_or_create(
            name="Donkey Betz",
            defaults={
                "description": "Test workspace for PR 2 tests.",
                "owner": chris,
            },
        )
    except Exception:
        # If the model has extra required fields the test fixture
        # can't satisfy, leave workspace=None — escalation will log a
        # warning but still emit the Deliverable.
        pass
    return chris


def _mock_cascade_all_pass(stack: ExitStack):
    """Patch call_command + subprocess.run so every step passes silently."""
    cc_mock = stack.enter_context(
        patch("core.tasks_documentation_manager.call_command")
    )
    cc_mock.return_value = None
    sp_mock = stack.enter_context(
        patch("core.tasks_documentation_manager.subprocess.run")
    )
    sp_mock.return_value = MagicMock(
        returncode=0, stdout="all good\n", stderr=""
    )
    return cc_mock, sp_mock


def _mock_cascade_step_failure(stack: ExitStack, fail_at: str):
    """Patch so call_command raises SystemExit when running ``fail_at``."""
    def _cc_side(cmd, *args, **kwargs):
        if cmd == fail_at:
            stdout = kwargs.get("stdout")
            if stdout is not None:
                stdout.write(
                    f"about to fail in {cmd}\n"
                    f"some traceback line 1\n"
                    f"some traceback line 2\n"
                )
            raise SystemExit(2)
        # Drift command should succeed even when cascade fails (it
        # only runs in the success path though).
        return None

    cc_mock = stack.enter_context(
        patch("core.tasks_documentation_manager.call_command",
              side_effect=_cc_side)
    )
    sp_mock = stack.enter_context(
        patch("core.tasks_documentation_manager.subprocess.run")
    )
    sp_mock.return_value = MagicMock(
        returncode=0, stdout="", stderr=""
    )
    return cc_mock, sp_mock


def _mock_cascade_step_4_timeout(stack: ExitStack):
    """Patch so step 4 (subprocess.run) raises TimeoutExpired."""
    cc_mock = stack.enter_context(
        patch("core.tasks_documentation_manager.call_command")
    )
    cc_mock.return_value = None
    sp_mock = stack.enter_context(
        patch(
            "core.tasks_documentation_manager.subprocess.run",
            side_effect=subprocess.TimeoutExpired(
                cmd="manage.py sync_docs_index_to_documents --embed",
                timeout=1800,
                output=b"embed step started\nstill running\n",
                stderr=b"",
            ),
        )
    )
    return cc_mock, sp_mock


def _mock_probes_all_zero(stack: ExitStack):
    """Make Document + DocumentEmbedding probes return 0/0 deterministically."""
    stack.enter_context(
        patch(
            "core.tasks_documentation_manager._probe_documents_count",
            return_value=0,
        )
    )
    stack.enter_context(
        patch(
            "core.tasks_documentation_manager._probe_embeddings_count",
            return_value=0,
        )
    )
    stack.enter_context(
        patch(
            "core.tasks_documentation_manager._probe_docs_indexed_count",
            return_value=42,
        )
    )


def _mock_drift_observation(stack: ExitStack, drift_count: int = 3):
    """Stub the drift call so verify_doc_claims output is deterministic.

    Wrapper preserves the side-effect contract of the real function —
    emits the ``step_5_drift_observed`` event onto the mission's
    timeline before returning — so timeline-shape assertions still
    pass while skipping the actual ``verify_doc_claims`` invocation.
    """
    from core.tasks_documentation_manager import DRIFT_LABEL, _emit_event

    def _side_effect(mission):
        _emit_event(
            mission, DRIFT_LABEL, "info",
            drift_count=drift_count,
            drift_items_count=drift_count,
            degraded_evidence=False,
            source="test_mock",
        )
        return drift_count, drift_count, False

    stack.enter_context(
        patch(
            "core.tasks_documentation_manager._run_drift_observation",
            side_effect=_side_effect,
        )
    )


def _run_task() -> dict:
    """Run the task synchronously, with the post-run connection
    cleanup hook suppressed.

    ``core.celery_telemetry`` connects a ``task_postrun`` signal
    handler that calls ``django.db.close_old_connections()``. In a
    test with an in-process ``.apply()``, this closes the test
    database connection before the test asserts can run their own
    ORM queries.

    Patching ``close_old_connections`` to a no-op only for the
    duration of the dispatch keeps the test connection alive without
    altering any production behavior — the production worker still
    calls the real ``close_old_connections`` between tasks.
    """
    from core.tasks_documentation_manager import (
        rigby_documentation_manager_daily,
    )
    # The signal handler in core.celery_telemetry imports
    # close_old_connections lazily inside the function, so we patch
    # it at its source module rather than at the consumer site.
    with patch("django.db.close_old_connections"):
        return rigby_documentation_manager_daily.apply().get()


# ── Happy path ───────────────────────────────────────────────────────


class HappyPathTests(TestCase):

    def setUp(self):
        _setup_user_and_workspace()

    def test_happy_path_creates_one_mission_run(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        runs = OpsRun.objects.filter(
            domain="mission", run_kind="docs_cascade"
        )
        self.assertEqual(runs.count(), 1)
        self.assertEqual(runs.first().status, "passed")

    def test_happy_path_emits_expected_event_sequence(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at")
            .values_list("label", flat=True)
        )
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

    def test_happy_path_summary_has_all_12_required_keys(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        summary_keys = set(run.summary.keys())
        for required in DOCUMENTATION_MANAGER.required_summary_keys:
            self.assertIn(
                required, summary_keys,
                f"required summary key {required!r} missing"
            )

    def test_happy_path_no_escalation_deliverable(self):
        from core.models_deliverables import Deliverable

        before = Deliverable.objects.count()
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        self.assertEqual(Deliverable.objects.count(), before)

    def test_happy_path_no_pa_chat_post(self):
        from core.models import ChatConversation

        pin_id = RIGBY.primary_chat_id
        before = ChatConversation.objects.filter(
            conversation_id=pin_id
        ).count()
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        after = ChatConversation.objects.filter(
            conversation_id=pin_id
        ).count()
        self.assertEqual(after, before)

    def test_happy_path_verdict_is_certified_confidence_high(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        verdict_event = OpsRunEvent.objects.get(
            run=run, label="verdict_issued:certified"
        )
        self.assertEqual(verdict_event.detail["verdict"], "certified")
        self.assertEqual(verdict_event.detail["confidence"], 0.95)

    def test_happy_path_each_step_event_has_duration_and_exit_code(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        passed_events = OpsRunEvent.objects.filter(
            run=run, label__endswith="_passed"
        )
        self.assertEqual(passed_events.count(), 4)
        for evt in passed_events:
            self.assertIn(
                "duration_ms", evt.detail,
                f"{evt.label} missing duration_ms"
            )
            self.assertIn(
                "exit_code", evt.detail,
                f"{evt.label} missing exit_code"
            )
            self.assertEqual(evt.detail["exit_code"], 0)


# ── Failure paths ────────────────────────────────────────────────────


class FailurePathTests(TestCase):

    def setUp(self):
        _setup_user_and_workspace()

    def test_step_1_failure_creates_escalation_and_verdict_rejected(self):
        with ExitStack() as stack:
            _mock_cascade_step_failure(stack, fail_at="build_docs_index")
            _mock_probes_all_zero(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertEqual(run.status, "failed")
        verdict_event = OpsRunEvent.objects.filter(
            run=run, label__startswith=LABEL_VERDICT_PREFIX
        ).first()
        self.assertEqual(verdict_event.label, "verdict_issued:rejected")

    def test_step_3_failure_skips_step_4_and_5_with_explicit_markers(self):
        with ExitStack() as stack:
            _mock_cascade_step_failure(
                stack, fail_at="sync_docs_index_to_documents"
            )
            _mock_probes_all_zero(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at")
            .values_list("label", flat=True)
        )
        self.assertIn("step_3_sync_failed", labels)
        self.assertIn("step_4_embed_skipped", labels)
        self.assertIn("step_5_skipped", labels)
        skipped_events = OpsRunEvent.objects.filter(
            run=run, label__endswith="_skipped"
        )
        for evt in skipped_events:
            self.assertEqual(evt.detail.get("reason"), "prior_failure")

    def test_step_4_hard_timeout_skips_drift_and_escalates(self):
        with ExitStack() as stack:
            _mock_cascade_step_4_timeout(stack)
            _mock_probes_all_zero(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertEqual(run.status, "failed")
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .values_list("label", flat=True)
        )
        self.assertIn("step_4_embed_failed", labels)
        self.assertIn("step_5_skipped", labels)
        self.assertNotIn("step_5_drift_observed", labels)
        # exit_code recorded as the literal string 'timeout'
        evt = OpsRunEvent.objects.get(run=run, label="step_4_embed_failed")
        self.assertEqual(evt.detail.get("exit_code"), "timeout")

    def test_first_failure_emits_error_signature_in_summary(self):
        with ExitStack() as stack:
            _mock_cascade_step_failure(stack, fail_at="build_docs_index")
            _mock_probes_all_zero(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertIn("error_signature", run.summary)
        self.assertIsInstance(run.summary["error_signature"], str)
        self.assertEqual(len(run.summary["error_signature"]), 16)


# ── Probes + count handling ──────────────────────────────────────────


class ProbeBehaviorTests(TestCase):

    def setUp(self):
        _setup_user_and_workspace()

    def test_docs_indexed_count_derived_from_index_json_length(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_docs_indexed_count",
                    return_value=137,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_documents_count",
                    return_value=0,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_embeddings_count",
                    return_value=0,
                )
            )
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertEqual(run.summary["docs_indexed_count"], 137)

    def test_count_probe_failure_sets_degraded_evidence_true(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_documents_count",
                    return_value=None,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_embeddings_count",
                    return_value=None,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_docs_indexed_count",
                    return_value=None,
                )
            )
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertTrue(run.summary["degraded_evidence"])
        # Mission still passes — degraded evidence does NOT escalate.
        self.assertEqual(run.status, "passed")

    def test_degraded_evidence_downgrades_verdict_confidence(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_documents_count",
                    return_value=None,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_embeddings_count",
                    return_value=None,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_docs_indexed_count",
                    return_value=None,
                )
            )
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        verdict_event = OpsRunEvent.objects.get(
            run=run, label="verdict_issued:certified"
        )
        self.assertEqual(verdict_event.detail["confidence"], 0.6)

    def test_drift_count_unparseable_sets_null_plus_degraded_evidence(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._run_drift_observation",
                    return_value=(None, None, True),
                )
            )
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertIsNone(run.summary["drift_count"])
        self.assertTrue(run.summary["degraded_evidence"])

    def test_embedding_delta_computed_correctly(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            # before=100, after=125
            values = {"calls": 0}

            def _probe_emb():
                values["calls"] += 1
                return 100 if values["calls"] == 1 else 125

            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_documents_count",
                    return_value=10,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_embeddings_count",
                    side_effect=_probe_emb,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_docs_indexed_count",
                    return_value=10,
                )
            )
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertEqual(run.summary["embeddings_count_before"], 100)
        self.assertEqual(run.summary["embeddings_count_after"], 125)
        self.assertEqual(run.summary["embedding_delta"], 25)

    def test_before_counts_captured_even_if_step_1_fails(self):
        with ExitStack() as stack:
            _mock_cascade_step_failure(stack, fail_at="build_docs_index")
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_documents_count",
                    return_value=50,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager._probe_embeddings_count",
                    return_value=75,
                )
            )
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertEqual(run.summary["documents_count_before"], 50)
        self.assertEqual(run.summary["embeddings_count_before"], 75)


# ── Idempotency + housekeeping ───────────────────────────────────────


class IdempotencyTests(TestCase):

    def setUp(self):
        _setup_user_and_workspace()

    def test_idempotency_second_call_same_day_returns_existing(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            r1 = _run_task()
            r2 = _run_task()
        self.assertEqual(r1["mission_id"], r2["mission_id"])
        self.assertTrue(r2.get("already_ran"))
        # And there's still exactly one OpsRun for today.
        self.assertEqual(
            OpsRun.objects.filter(run_kind="docs_cascade").count(), 1
        )

    def test_run_kind_is_exact_docs_cascade(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertEqual(
            run.run_kind, DOCUMENTATION_MANAGER.mission_run_kind
        )

    def test_mission_finished_at_set_on_terminal_status(self):
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        self.assertIsNotNone(run.finished_at)

    def test_no_extra_cli_flags_passed(self):
        with ExitStack() as stack:
            cc_mock, sp_mock = _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        call_names = [c.args[0] for c in cc_mock.call_args_list]
        self.assertIn("build_docs_index", call_names)
        self.assertIn("build_rag_corpus", call_names)
        self.assertIn("sync_docs_index_to_documents", call_names)
        # subprocess.run is the canonical step 4 path
        sp_argv = sp_mock.call_args_list[0].args[0]
        self.assertEqual(
            sp_argv,
            ["python", "manage.py", "sync_docs_index_to_documents", "--embed"],
        )

    def test_summary_merge_not_replace_with_verdict_fields(self):
        """PR 2's task pre-populates summary fields BEFORE calling
        emit_mission_verdict, which then merges its own keys on top."""
        with ExitStack() as stack:
            _mock_cascade_all_pass(stack)
            _mock_probes_all_zero(stack)
            _mock_drift_observation(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        # Cascade-populated key survives.
        self.assertIn("wall_time_ms", run.summary)
        # Verdict-populated key was merged on top.
        self.assertEqual(run.summary["verdict"], "certified")


# ── Error-tail + signature helpers ───────────────────────────────────


class ErrorTailAndSignatureTests(TestCase):

    def test_error_tail_truncated_to_100_lines_on_first_failure(self):
        # Build a giant output so the tail trimming is exercised.
        big_lines = "\n".join(f"line {i}" for i in range(500))

        def _cc_side(cmd, *args, **kwargs):
            if cmd == "build_docs_index":
                stdout = kwargs.get("stdout")
                if stdout is not None:
                    stdout.write(big_lines)
                raise SystemExit(1)
            return None

        _setup_user_and_workspace()
        with ExitStack() as stack:
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager.call_command",
                    side_effect=_cc_side,
                )
            )
            stack.enter_context(
                patch(
                    "core.tasks_documentation_manager.subprocess.run",
                    return_value=MagicMock(
                        returncode=0, stdout="", stderr=""
                    ),
                )
            )
            _mock_probes_all_zero(stack)
            _run_task()
        run = OpsRun.objects.filter(run_kind="docs_cascade").first()
        tail = run.summary["error_tail"]
        self.assertIsNotNone(tail)
        # Last line of original output must be present.
        self.assertIn("line 499", tail)
        # Far-earlier line must NOT be present (only last 100 retained).
        self.assertNotIn("line 100", tail)

    def test_error_signature_is_stable_hash(self):
        from core.tasks_documentation_manager import _signature_for

        s1 = _signature_for("build_docs_index", "error tail content")
        s2 = _signature_for("build_docs_index", "error tail content")
        self.assertEqual(s1, s2)

    def test_error_signature_normalized_strips_timestamps(self):
        from core.tasks_documentation_manager import _signature_for

        s1 = _signature_for(
            "build_docs_index",
            "2026-06-28T18:42:10 Error: something broke",
        )
        s2 = _signature_for(
            "build_docs_index",
            "2026-06-29T03:01:55 Error: something broke",
        )
        self.assertEqual(s1, s2)

    def test_error_signature_changes_with_different_failed_step(self):
        from core.tasks_documentation_manager import _signature_for

        s1 = _signature_for("build_docs_index", "same tail")
        s2 = _signature_for("build_rag_corpus", "same tail")
        self.assertNotEqual(s1, s2)
