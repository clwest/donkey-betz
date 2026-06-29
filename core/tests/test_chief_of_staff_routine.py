"""Session 1257 PR 3.2 — Chief of Staff Morning Brief task runner tests.

End-to-end behavior of the morning_brief mission via MissionRunner +
the wrap-as-single-step pattern. Real-DB PostgreSQL integration. The
underlying WorkflowOrchestrationAgent.execute is mocked at the
``core.jobs.morning_brief`` import surface so tests stay deterministic
+ fast — but all OpsRun / OpsRunEvent / Deliverable assertions hit
real DB rows.

Covers the 16-point contract from Chris's PR 3.2 directive:
  1. Celery task registered
  2. employee_tool run_now dispatches the task
  3. Rigby + Platform Auditor run_now still work
  4. MissionRunner production caller count = exactly 3
  5. No MissionRunner public contract changes
  6. No workflow internal files modified
  7. No PeriodicTask / beat schedule added
  8. Successful Morning Brief mission creates OpsRun with
     run_kind=morning_brief
  9. Event timeline matches expected single-step wrapper shape
  10. Required summary keys are present
  11. brief_chars derived from created Deliverable via ORM read
  12. OpsRun.summary does not include the full workflow envelope
  13. Verdict emits correctly
  14. evidence_for_mission works
  15. status works for Chief of Staff + doesn't leak other employees'
      missions
  16. Failure path emits rejected verdict + escalation Deliverable
"""

from __future__ import annotations

import ast
import hashlib
import inspect
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.employees import (
    CHIEF_OF_STAFF,
    DOCUMENTATION_MANAGER,
    MORNING_BRIEF_JOB,
    PLATFORM_AUDIT_JOB,
    PLATFORM_AUDITOR,
    RIGBY,
)

User = get_user_model()


# ── Fixtures ──────────────────────────────────────────────────────────


def _setup_user_and_workspaces():
    """Ensure chris user + Donkey Betz + Morning Brief workspaces exist."""
    chris, _ = User.objects.get_or_create(
        username="chris",
        defaults={"email": "chris@test.donkey"},
    )
    try:
        from core.models_skin_layer import ProjectWorkspace

        ProjectWorkspace.objects.get_or_create(
            name="Donkey Betz",
            defaults={
                "description": "Test workspace for CoS tests.",
                "user": chris,
                "root_path": "/tmp/test-donkey-betz",
            },
        )
        ProjectWorkspace.objects.get_or_create(
            user=chris,
            name="Morning Brief",
            defaults={
                "description": "Test Morning Brief workspace.",
                "workspace_type": "local",
                "root_path": "/morning-brief",
                "tech_stack": {},
            },
        )
    except Exception:
        pass
    return chris


def _make_morning_brief_deliverable(user, workspace=None) -> str:
    """Create a Morning Brief Deliverable; return its UUID as str.

    The wrapper step's brief_chars derivation does an ORM read of
    ``Deliverable.content`` length; pre-creating a row here lets the
    tests assert that derivation without invoking the real workflow.
    """
    from core.models_deliverables import Deliverable

    if workspace is None:
        from core.models_skin_layer import ProjectWorkspace

        workspace = ProjectWorkspace.objects.filter(
            user=user, name="Morning Brief"
        ).first()

    content = (
        "# Morning Brief — synthetic test content\n\n"
        "## TL;DR\nThe brief Deliverable is synthetic for test purposes.\n\n"
        "## Lane 1 — Platform Readiness\nAll systems nominal.\n\n"
        "## Decision Card\n- Decision: ship the test\n"
    )
    deliv = Deliverable.objects.create(
        title="Morning Brief — TEST",
        content=content,
        content_format="markdown",
        category="Morning Brief",
        agent_name="WorkflowOrchestrationAgent",
        agent_task="morning_brief workflow",
        user=user,
        workspace=workspace,
        status="ready",
        metadata={"workflow": "morning_brief", "session": "1257-PR3.2-test"},
    )
    return str(deliv.id)


def _success_envelope(
    deliverable_id: str,
    workspace_id: str,
    rotation_slot: str = "ai_infra_deep_dive",
    lane_4_slot_used: str = "ai_infra_deep_dive",
    decision_cards: int = 2,
    decision_card_text_chars: int = 540,
) -> Dict[str, Any]:
    """Build a synthetic successful WorkflowOrchestrationAgent envelope.

    Shape mirrors the real workflow's ``_compile_final_result`` output:
    per-step ``result`` dicts under ``steps[]`` plus a top-level
    ``success: bool``. No nested workflow secret state — this is what
    the wrapper step extracts scalars from.
    """
    dct = "X" * decision_card_text_chars
    return {
        "success": True,
        "workflow": "morning_brief",
        "steps": [
            {
                "step": 1,
                "name": "rotation_slot_resolve",
                "agent": "rotation_slot_resolve",
                "success": True,
                "result": {
                    "success": True,
                    "rotation_slot": rotation_slot,
                    "reason": "weekday_default:0",
                },
            },
            {
                "step": 2,
                "name": "lane_1_platform_readiness",
                "agent": "system_intelligence_agent",
                "success": True,
                "result": {
                    "success": True,
                    "output": "Lane 1 text",
                    "data": {},
                },
            },
            {
                "step": 3,
                "name": "lane_2_build_focus",
                "agent": "coo_agent",
                "success": True,
                "result": {
                    "success": True,
                    "output": "Lane 2 text",
                    "data": {},
                },
            },
            {
                "step": 4,
                "name": "lane_3_competitive_landscape",
                "agent": "trend_analysis_agent",
                "success": True,
                "result": {
                    "success": True,
                    "output": "Lane 3 text",
                    "data": {},
                },
            },
            {
                "step": 5,
                "name": "lane_4_rotating_focus",
                "agent": "lane_4_rotating_focus",
                "success": True,
                "result": {
                    "success": True,
                    "output": "Lane 4 text",
                    "slot_used": lane_4_slot_used,
                    "agent_name": "ResearchAgent",
                    "data": {},
                },
            },
            {
                "step": 6,
                "name": "decision_card_synthesis",
                "agent": "decision_card_synthesis",
                "success": True,
                "result": {
                    "success": True,
                    "decision_card_text": dct,
                    "decision_cards": [
                        {"decision": f"d{i}"} for i in range(decision_cards)
                    ],
                },
            },
            {
                "step": 7,
                "name": "strategic_synthesis",
                "agent": "strategic_synthesis",
                "success": True,
                "result": {
                    "success": True,
                    "synthesis": "Final brief markdown placeholder.",
                },
            },
            {
                "step": 8,
                "name": "create_deliverable",
                "agent": "create_morning_brief_deliverable",
                "success": True,
                "result": {
                    "success": True,
                    "deliverable_id": deliverable_id,
                    "workspace_id": workspace_id,
                    "title": "Morning Brief — TEST",
                },
            },
        ],
    }


def _failure_envelope(
    fail_at: str = "lane_2_build_focus",
    inner_error: str = "synthetic LLM stall",
    rotation_slot: str = "ai_infra_deep_dive",
) -> Dict[str, Any]:
    """Build a synthetic failed WorkflowOrchestrationAgent envelope.

    ``fail_at`` is the inner workflow step name. The wrapper step's
    extract path looks for the first step with ``success=False`` and
    surfaces it via ``inner_failed_step``.
    """
    return {
        "success": False,
        "workflow": "morning_brief",
        "error": f"Step {fail_at!r} failed: {inner_error}",
        "steps": [
            {
                "step": 1,
                "name": "rotation_slot_resolve",
                "agent": "rotation_slot_resolve",
                "success": True,
                "result": {
                    "success": True,
                    "rotation_slot": rotation_slot,
                    "reason": "weekday_default:0",
                },
            },
            {
                "step": 2,
                "name": fail_at,
                "agent": fail_at.replace("_", "-"),
                "success": False,
                "result": {
                    "success": False,
                    "error": inner_error,
                },
            },
        ],
    }


# ═════════════════════════════════════════════════════════════════════
# 1. Celery task registered
# ═════════════════════════════════════════════════════════════════════


class CeleryRegistrationTests(TestCase):

    def test_task_registered_in_celery_app(self):
        from core.celery import app

        # Force-import in case eager hook hasn't fired yet.
        import core.tasks_chief_of_staff  # noqa: F401
        self.assertIn(
            "chief_of_staff_morning_brief_run", app.tasks,
            "chief_of_staff_morning_brief_run not registered in Celery — "
            "check core/celery.py app.conf.imports + the eager-import set.",
        )

    def test_task_in_app_conf_imports(self):
        from core.celery import app

        self.assertIn(
            "core.tasks_chief_of_staff", app.conf.imports,
            "core.tasks_chief_of_staff missing from app.conf.imports — "
            "worker boot won't register the task.",
        )

    def test_task_in_eager_import_set(self):
        """The S1253 hotfix lesson: app.conf.imports alone isn't enough;
        the @app.on_after_finalize hook must also include the module so
        app.tasks reads (verifier / build_celery_audit) see the task name
        without waiting for worker boot."""
        celery_src = (
            Path(__file__).resolve().parents[1] / "celery.py"
        ).read_text()
        # Find the eager_modules tuple inside
        # _eager_import_session1115_modules.
        idx = celery_src.find("_eager_import_session1115_modules")
        self.assertGreater(idx, 0, "eager-import hook missing")
        block = celery_src[idx: idx + 4000]
        self.assertIn(
            "'core.tasks_chief_of_staff'", block,
            "core.tasks_chief_of_staff missing from "
            "_eager_import_session1115_modules — verify_doc_claims / "
            "build_celery_audit may miss the task.",
        )


# ═════════════════════════════════════════════════════════════════════
# 2. employee_tool run_now dispatches the task
# ═════════════════════════════════════════════════════════════════════


class RunNowDispatchTests(TestCase):

    def setUp(self):
        _setup_user_and_workspaces()

    def test_chief_of_staff_morning_brief_in_registry(self):
        from core.services.td_handlers_employee import _RUN_NOW_TASKS

        self.assertIn(("chief_of_staff", "morning_brief"), _RUN_NOW_TASKS)
        dispatch = _RUN_NOW_TASKS[("chief_of_staff", "morning_brief")]
        self.assertEqual(dispatch.run_kind, "morning_brief")
        task_callable = dispatch.resolve_task()
        self.assertEqual(
            task_callable.name, "chief_of_staff_morning_brief_run"
        )

    def test_run_now_handler_dispatches_chief_of_staff_task(self):
        """The PA-tool action=run_now path should dispatch via the
        registry entry. Mock .delay() so we don't actually queue a task."""
        from core.services.td_handlers_employee import EmployeeHandlersMixin

        chris = User.objects.get(username="chris")
        handler = EmployeeHandlersMixin()
        with patch(
            "core.tasks_chief_of_staff.chief_of_staff_morning_brief_run.delay"
        ) as mock_delay:
            mock_delay.return_value.id = "task-id-12345"
            result = handler._handle_employee_tool(
                tool_name="employee_tool",
                payload={
                    "action": "run_now",
                    "employee": "chief_of_staff",
                    "job": "morning_brief",
                },
                user_id=chris.id,
                trace_id="trace-test",
            )
        self.assertTrue(result["ok"], f"run_now failed: {result}")
        self.assertEqual(result["employee"], "chief_of_staff")
        self.assertEqual(result["job"], "morning_brief")
        self.assertEqual(result["task_id"], "task-id-12345")
        mock_delay.assert_called_once()


# ═════════════════════════════════════════════════════════════════════
# 3. Rigby + Platform Auditor run_now still work (no regression)
# ═════════════════════════════════════════════════════════════════════


class RunNowRegressionTests(TestCase):

    def setUp(self):
        _setup_user_and_workspaces()

    def test_rigby_docs_manager_still_in_registry(self):
        from core.services.td_handlers_employee import _RUN_NOW_TASKS

        self.assertIn(("rigby", "docs_manager"), _RUN_NOW_TASKS)
        dispatch = _RUN_NOW_TASKS[("rigby", "docs_manager")]
        self.assertEqual(dispatch.run_kind, "docs_cascade")
        task_callable = dispatch.resolve_task()
        self.assertEqual(
            task_callable.name, "rigby_documentation_manager_daily"
        )

    def test_platform_auditor_still_in_registry(self):
        from core.services.td_handlers_employee import _RUN_NOW_TASKS

        self.assertIn(
            ("platform_auditor", "platform_audit"), _RUN_NOW_TASKS
        )
        dispatch = _RUN_NOW_TASKS[("platform_auditor", "platform_audit")]
        self.assertEqual(dispatch.run_kind, "platform_audit")
        task_callable = dispatch.resolve_task()
        self.assertEqual(task_callable.name, "platform_auditor_run")

    def test_registry_has_exactly_three_entries(self):
        from core.services.td_handlers_employee import _RUN_NOW_TASKS

        self.assertEqual(
            len(_RUN_NOW_TASKS), 3,
            f"Expected exactly 3 (employee, job) entries; got "
            f"{sorted(_RUN_NOW_TASKS.keys())}",
        )

    def test_rigby_run_now_dispatches_correctly(self):
        from core.services.td_handlers_employee import EmployeeHandlersMixin

        chris = User.objects.get(username="chris")
        handler = EmployeeHandlersMixin()
        with patch(
            "core.tasks_documentation_manager."
            "rigby_documentation_manager_daily.delay"
        ) as mock_delay:
            mock_delay.return_value.id = "task-id-rigby-abc"
            result = handler._handle_employee_tool(
                tool_name="employee_tool",
                payload={
                    "action": "run_now",
                    "employee": "rigby",
                    "job": "docs_manager",
                },
                user_id=chris.id,
                trace_id="trace-test",
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["employee"], "rigby")
        self.assertEqual(result["job"], "docs_manager")
        mock_delay.assert_called_once()

    def test_platform_auditor_run_now_dispatches_correctly(self):
        from core.services.td_handlers_employee import EmployeeHandlersMixin

        chris = User.objects.get(username="chris")
        handler = EmployeeHandlersMixin()
        with patch(
            "core.tasks_platform_audit.platform_auditor_run.delay"
        ) as mock_delay:
            mock_delay.return_value.id = "task-id-pa-xyz"
            result = handler._handle_employee_tool(
                tool_name="employee_tool",
                payload={
                    "action": "run_now",
                    "employee": "platform_auditor",
                    "job": "platform_audit",
                },
                user_id=chris.id,
                trace_id="trace-test",
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["employee"], "platform_auditor")
        self.assertEqual(result["job"], "platform_audit")
        mock_delay.assert_called_once()


# ═════════════════════════════════════════════════════════════════════
# 4. MissionRunner production caller count = exactly 3
# ═════════════════════════════════════════════════════════════════════


class ThreeProductionCallersTests(TestCase):
    """PR 3.2 promotes MissionRunner from 2 to 3 production callers.

    Mirrors the AST scan from
    ``test_platform_audit_routine.TwoProductionCallersTests`` with one
    additional job entry.
    """

    def test_exactly_three_production_callers(self):
        repo_root = Path(__file__).resolve().parents[2]
        core_dir = repo_root / "core"

        callers = set()
        for py in core_dir.rglob("*.py"):
            if "/tests/" in str(py):
                continue
            if py.name == "mission_runner.py":
                continue
            try:
                tree = ast.parse(py.read_text(), filename=str(py))
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_repr = ast.dump(node.func)
                    if (
                        "MissionRunner" in func_repr
                        or "build_docs_manager_runner" in func_repr
                        or "build_platform_audit_runner" in func_repr
                        or "build_chief_of_staff_runner" in func_repr
                    ):
                        callers.add(str(py.relative_to(repo_root)))

        job_to_factory = {
            "docs_manager": {
                "core/tasks_documentation_manager.py",
                "core/jobs/docs_cascade.py",
            },
            "platform_audit": {
                "core/tasks_platform_audit.py",
                "core/jobs/platform_audit.py",
            },
            "morning_brief": {
                "core/tasks_chief_of_staff.py",
                "core/jobs/morning_brief.py",
            },
        }
        observed_jobs = set()
        for path in callers:
            for job, files in job_to_factory.items():
                if path in files:
                    observed_jobs.add(job)
        self.assertEqual(
            observed_jobs,
            {"docs_manager", "platform_audit", "morning_brief"},
            f"Expected exactly 3 production callers (docs_manager + "
            f"platform_audit + morning_brief); observed call sites: "
            f"{sorted(callers)}",
        )


# ═════════════════════════════════════════════════════════════════════
# 5. No MissionRunner public contract changes
# ═════════════════════════════════════════════════════════════════════


class NoMissionRunnerChangesTests(TestCase):
    """PR 3.2 must not modify MissionRunner's public contract.

    Snapshot of MissionRunner.__init__ signature (the public contract)
    plus the canonical public symbols a caller depends on. A breaking
    edit would change one of these and the test fails — pointing
    Reviewer (Chris/Rigby) at the contract surface.
    """

    EXPECTED_INIT_KW_ONLY = {
        "config",
        "steps",
        "escalation_body_formatter",
        "escalation_summary_formatter",
        "escalation_deliverable_spec_factory",
        "shift_report_fn",
        "pa_post_fn",
        "preflight_fn",
        "postflight_fn",
    }

    EXPECTED_PUBLIC_SYMBOLS = (
        "MissionRunner",
        "MissionRunnerConfig",
        "MissionRunResult",
        "Step",
        "StepResult",
        "FailureContext",
        "PAPostContext",
        "PostflightContext",
        "EscalationDeliverableSpec",
        "RUN_STARTED_LABEL",
        "ESCALATION_LABEL",
        "VERDICT_CERTIFIED",
        "VERDICT_REJECTED",
        "VERDICT_DEFERRED",
    )

    def test_mission_runner_init_signature_unchanged(self):
        from core.employees.mission_runner import MissionRunner

        sig = inspect.signature(MissionRunner.__init__)
        kw_only_names = {
            name for name, p in sig.parameters.items()
            if p.kind in (
                inspect.Parameter.KEYWORD_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
            and name != "self"
        }
        self.assertEqual(
            kw_only_names, self.EXPECTED_INIT_KW_ONLY,
            "MissionRunner.__init__ signature changed; PR 3.2 must not "
            f"modify the runner contract. Got {sorted(kw_only_names)}, "
            f"expected {sorted(self.EXPECTED_INIT_KW_ONLY)}.",
        )

    def test_mission_runner_public_symbols_present(self):
        import core.employees.mission_runner as mr

        for symbol in self.EXPECTED_PUBLIC_SYMBOLS:
            self.assertTrue(
                hasattr(mr, symbol),
                f"MissionRunner module missing public symbol {symbol!r} "
                "— PR 3.2 must not remove or rename public symbols.",
            )


# ═════════════════════════════════════════════════════════════════════
# 6. No workflow internal files modified
# ═════════════════════════════════════════════════════════════════════


class NoWorkflowInternalsModifiedTests(TestCase):
    """Rigby S1257 SIGN-WITH-EDITS lock #1 + lock #2 constraint.

    Asserts the workflow internal files still contain the load-bearing
    symbols PR 3.1 / S1233 established. This is NOT a checksum freeze
    (Chris's directives allow incidental edits to those files in
    future PRs), but it catches accidental removal of:
      * WORKFLOWS['morning_brief'] template
      * _execute_create_morning_brief_deliverable_step
      * _get_or_create_morning_brief_workspace
      * _execute_strategic_synthesis_step
      * _execute_rotation_slot_resolve_step
      * _execute_lane_4_rotating_focus_step
      * _execute_decision_card_synthesis_step

    If PR 3.2 needed to modify these, the test author would update
    this assertion — the test acts as a tripwire for unintentional
    drift.
    """

    EXPECTED_WORKFLOW_SYMBOLS = (
        "morning_brief",  # WORKFLOWS key
        "_execute_create_morning_brief_deliverable_step",
        "_get_or_create_morning_brief_workspace",
        "_execute_strategic_synthesis_step",
        "_execute_rotation_slot_resolve_step",
        "_execute_lane_4_rotating_focus_step",
        "_execute_decision_card_synthesis_step",
        "_resolve_workflow_target_workspace_id",
        "_MORNING_BRIEF_LANE_4_SLOT_AGENT",
        "_MORNING_BRIEF_LANE_4_DEFAULT_SLOT",
        "_WEEKDAY_DEFAULT_SLOT",
        "_ROTATION_OVERRIDE_SHORTHAND_TO_SLOT",
    )

    def test_workflow_internals_still_present(self):
        workflow_path = (
            Path(__file__).resolve().parents[1]
            / "services"
            / "workflow_orchestration_agent.py"
        )
        src = workflow_path.read_text()
        for symbol in self.EXPECTED_WORKFLOW_SYMBOLS:
            self.assertIn(
                symbol, src,
                f"Workflow internal symbol {symbol!r} missing from "
                "workflow_orchestration_agent.py — PR 3.2 must preserve "
                "the workflow's internal contract per Rigby SIGN-WITH-"
                "EDITS lock #1.",
            )


# ═════════════════════════════════════════════════════════════════════
# 7. No PeriodicTask / beat schedule added
# ═════════════════════════════════════════════════════════════════════


class NoBeatScheduleTests(TestCase):

    def test_no_periodic_task_for_chief_of_staff(self):
        from django_celery_beat.models import PeriodicTask

        # The beat schedule task-name flip lands in PR 3.3; PR 3.2
        # must NOT register any PeriodicTask for the new task name.
        count = PeriodicTask.objects.filter(
            task="chief_of_staff_morning_brief_run"
        ).count()
        self.assertEqual(
            count, 0,
            "PR 3.2 must not register a PeriodicTask for "
            "chief_of_staff_morning_brief_run — the beat row flip "
            "lands in PR 3.3.",
        )

    def test_legacy_beat_row_task_unchanged(self):
        """The existing generate-morning-brief-daily beat row (if it
        exists in this DB) should still point at the legacy task. PR
        3.2 must NOT flip it (that's PR 3.3)."""
        from django_celery_beat.models import PeriodicTask

        legacy_row = PeriodicTask.objects.filter(
            name="generate-morning-brief-daily"
        ).first()
        if legacy_row is not None:
            self.assertEqual(
                legacy_row.task,
                "core.tasks.generate_morning_brief_daily",
                "PR 3.2 must not flip the legacy beat row task name — "
                "that's PR 3.3's scope.",
            )


# ═════════════════════════════════════════════════════════════════════
# 8 + 9 + 10 + 11 + 12 + 13. Successful mission shape end-to-end
# ═════════════════════════════════════════════════════════════════════


class SuccessPathTests(TestCase):
    """Real-DB successful run via the wrap-as-single-step path."""

    def setUp(self):
        self.chris = _setup_user_and_workspaces()
        from core.models_skin_layer import ProjectWorkspace
        self.mb_ws = ProjectWorkspace.objects.get(
            user=self.chris, name="Morning Brief"
        )

    def test_8_run_creates_ops_run_with_morning_brief_kind(self):
        from core.models_ops_runs import OpsRun
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        deliv_id = _make_morning_brief_deliverable(self.chris, self.mb_ws)
        envelope = _success_envelope(deliv_id, str(self.mb_ws.id))

        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            result = chief_of_staff_morning_brief_run()

        self.assertTrue(result["ok"])
        run = OpsRun.objects.get(id=result["mission_id"])
        self.assertEqual(run.domain, "mission")
        self.assertEqual(run.run_kind, "morning_brief")
        self.assertEqual(run.status, "passed")

    def test_9_event_timeline_matches_single_step_wrapper(self):
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        deliv_id = _make_morning_brief_deliverable(self.chris, self.mb_ws)
        envelope = _success_envelope(deliv_id, str(self.mb_ws.id))

        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            result = chief_of_staff_morning_brief_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at", "id")
            .values_list("label", flat=True)
        )
        # Expected: run_started + single wrapper step + verdict
        self.assertEqual(
            labels,
            [
                "run_started",
                "step_brief_workflow_started",
                "step_brief_workflow_passed",
                "verdict_issued:certified",
            ],
        )

    def test_10_summary_contains_all_required_summary_keys(self):
        from core.models_ops_runs import OpsRun
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        deliv_id = _make_morning_brief_deliverable(self.chris, self.mb_ws)
        envelope = _success_envelope(deliv_id, str(self.mb_ws.id))

        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            result = chief_of_staff_morning_brief_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        summary_keys = set(run.summary.keys())
        for key in MORNING_BRIEF_JOB.required_summary_keys:
            self.assertIn(
                key, summary_keys,
                f"summary missing required key {key!r}; "
                f"got keys: {sorted(summary_keys)}",
            )

    def test_11_brief_chars_derived_from_deliverable_via_orm(self):
        """brief_chars must equal len(Deliverable.content). Lock #1
        from Rigby's S1257 SIGN-WITH-EDITS: derived postflight via ORM
        read, NOT from a workflow return-dict field."""
        from core.models_deliverables import Deliverable
        from core.models_ops_runs import OpsRun
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        deliv_id = _make_morning_brief_deliverable(self.chris, self.mb_ws)
        deliv = Deliverable.objects.get(id=deliv_id)
        expected_len = len(deliv.content or "")

        envelope = _success_envelope(deliv_id, str(self.mb_ws.id))
        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            result = chief_of_staff_morning_brief_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        self.assertEqual(run.summary.get("brief_chars"), expected_len)
        # And separately confirm the workflow envelope did NOT carry a
        # brief_chars field (it must be postflight-derived only).
        synth_step = next(
            s for s in envelope["steps"] if s["name"] == "strategic_synthesis"
        )
        self.assertNotIn("brief_chars", synth_step["result"])

    def test_12_summary_does_not_include_full_workflow_envelope(self):
        """Lock #2 from Rigby's S1257 SIGN-WITH-EDITS: scalar-only
        extraction; never persist the entire workflow envelope."""
        from core.models_ops_runs import OpsRun
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        deliv_id = _make_morning_brief_deliverable(self.chris, self.mb_ws)
        envelope = _success_envelope(deliv_id, str(self.mb_ws.id))

        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            result = chief_of_staff_morning_brief_run()

        run = OpsRun.objects.get(id=result["mission_id"])

        # Forbid any nested keys that would indicate envelope stashing.
        forbidden_keys = (
            "steps", "workflow_result", "_workflow_result_envelope",
            "envelope", "step_results", "lane_1_text", "lane_2_text",
            "lane_3_text", "lane_4_text", "decision_card_text",
            "decision_cards",
        )
        for forbidden in forbidden_keys:
            self.assertNotIn(
                forbidden, run.summary,
                f"summary contains forbidden key {forbidden!r} — the "
                "full workflow envelope (or large sub-fields) must NOT "
                "be persisted per Rigby S1257 SIGN-WITH-EDITS lock #2.",
            )

        # Every persisted value must be JSON-scalar-ish (no nested list
        # of dicts, no nested dict of dicts). Counts the depth of any
        # JSON-incompatible structures.
        for key, value in run.summary.items():
            if isinstance(value, list):
                # Allowed lists are short scalar lists (e.g., empty);
                # forbid lists of dicts.
                for item in value:
                    self.assertFalse(
                        isinstance(item, dict),
                        f"summary[{key!r}] contains a dict-element list "
                        "— must be scalar-only.",
                    )

    def test_13_verdict_certified_on_success(self):
        from core.models_ops_runs import OpsRun
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        deliv_id = _make_morning_brief_deliverable(self.chris, self.mb_ws)
        envelope = _success_envelope(deliv_id, str(self.mb_ws.id))

        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            result = chief_of_staff_morning_brief_run()

        self.assertEqual(result["verdict"], "certified")
        run = OpsRun.objects.get(id=result["mission_id"])
        self.assertEqual(run.summary.get("verdict"), "certified")


# ═════════════════════════════════════════════════════════════════════
# 14. evidence_for_mission works for a Chief of Staff mission
# ═════════════════════════════════════════════════════════════════════


class EvidenceForMissionTests(TestCase):

    def setUp(self):
        self.chris = _setup_user_and_workspaces()
        from core.models_skin_layer import ProjectWorkspace
        self.mb_ws = ProjectWorkspace.objects.get(
            user=self.chris, name="Morning Brief"
        )

    def test_evidence_for_mission_returns_chief_of_staff_envelope(self):
        from core.services.td_handlers_employee import EmployeeHandlersMixin
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        deliv_id = _make_morning_brief_deliverable(self.chris, self.mb_ws)
        envelope = _success_envelope(deliv_id, str(self.mb_ws.id))
        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            result = chief_of_staff_morning_brief_run()

        mission_id = result["mission_id"]
        handler = EmployeeHandlersMixin()
        evidence = handler._handle_employee_tool(
            tool_name="employee_tool",
            payload={
                "action": "evidence_for_mission",
                "mission_id": mission_id,
            },
            user_id=self.chris.id,
            trace_id="trace-evidence",
        )
        self.assertTrue(
            evidence.get("ok"),
            f"evidence_for_mission failed: {evidence}",
        )
        # Mission identity is recorded under 'ops_run'.
        self.assertIn("ops_run", evidence)
        ops_run = evidence["ops_run"]
        self.assertEqual(ops_run.get("run_kind"), "morning_brief")
        self.assertEqual(ops_run.get("status"), "passed")
        # Summary on the ops_run carries the CoS-specific scalar fields.
        summary = ops_run.get("summary") or {}
        self.assertEqual(summary.get("verdict"), "certified")
        self.assertEqual(summary.get("lanes_completed_count"), 4)
        # The brief Deliverable is referenced via the summary.
        self.assertIsNotNone(summary.get("deliverable_id"))


# ═════════════════════════════════════════════════════════════════════
# 15. status works for Chief of Staff + no leak across employees
# ═════════════════════════════════════════════════════════════════════


class StatusNoLeakTests(TestCase):
    """Mirrors S1257 PR 2.2.1 generalized-status no-leak guarantee.

    Creates one ``morning_brief`` mission row directly (no Celery
    needed) + an unrelated ``docs_cascade`` mission row + an unrelated
    ``platform_audit`` mission row, then asserts status only sees the
    Chief of Staff one.
    """

    def setUp(self):
        self.chris = _setup_user_and_workspaces()

    def _make_passed_mission(self, run_kind: str):
        from core.models_ops_runs import OpsRun
        from django.utils import timezone

        now = timezone.now()
        run = OpsRun.objects.create(
            title=f"{run_kind}: test row",
            run_type="manual",
            domain="mission",
            run_kind=run_kind,
            mission_id=uuid4(),
            triggered_by="test",
            status="passed",
            started_at=now,
            finished_at=now,
            summary={
                "verdict": "certified",
                "wall_time_ms": 1000,
                "failed_step": None,
                "error_tail": None,
            },
        )
        return run

    def test_status_returns_chief_of_staff_data(self):
        from core.services.td_handlers_employee import EmployeeHandlersMixin

        # Create rows for all three employees so we can verify no leak.
        cos_run = self._make_passed_mission("morning_brief")
        rigby_run = self._make_passed_mission("docs_cascade")
        pa_run = self._make_passed_mission("platform_audit")

        handler = EmployeeHandlersMixin()
        status = handler._handle_employee_tool(
            tool_name="employee_tool",
            payload={
                "action": "status",
                "employee": "chief_of_staff",
                "job": "morning_brief",
                "window": "7d",
            },
            user_id=self.chris.id,
            trace_id="trace-status",
        )
        self.assertTrue(
            status.get("ok"), f"status failed: {status}"
        )
        # CoS handle + job should be reflected in the response (per the
        # derive_status return contract in core/employees/status.py).
        self.assertEqual(status.get("employee"), "chief_of_staff")
        self.assertEqual(status.get("job"), "morning_brief")

        # Mission stats: count of morning_brief missions over the window
        # — must be exactly 1 (the CoS row we created), NOT 3 (which
        # would indicate run_kind leaking across employees).
        missions = status.get("missions") or {}
        self.assertEqual(
            missions.get("total"), 1,
            f"status.missions.total leaked across employees; "
            f"expected 1 (CoS-only), got {missions}",
        )
        self.assertEqual(missions.get("certified"), 1)
        self.assertEqual(missions.get("rejected"), 0)

    def test_status_does_not_leak_rigby_or_platform_audit_missions(self):
        """The CoS status response must not reference docs_cascade /
        platform_audit run_kind data anywhere."""
        from core.services.td_handlers_employee import EmployeeHandlersMixin

        self._make_passed_mission("morning_brief")
        self._make_passed_mission("docs_cascade")
        self._make_passed_mission("platform_audit")

        handler = EmployeeHandlersMixin()
        status = handler._handle_employee_tool(
            tool_name="employee_tool",
            payload={
                "action": "status",
                "employee": "chief_of_staff",
                "job": "morning_brief",
                "window": "7d",
            },
            user_id=self.chris.id,
            trace_id="trace-no-leak",
        )

        # Serialize the whole response and assert other run_kinds /
        # employee handles don't appear.
        serialized = repr(status)
        self.assertNotIn("docs_cascade", serialized)
        self.assertNotIn("platform_audit", serialized)
        # The handle 'rigby' might appear in known_employees lists
        # which is fine; checking run_kind strings catches mission leakage.


# ═════════════════════════════════════════════════════════════════════
# 16. Failure path emits rejected verdict + escalation Deliverable
# ═════════════════════════════════════════════════════════════════════


class FailurePathTests(TestCase):

    def setUp(self):
        self.chris = _setup_user_and_workspaces()
        from core.models_skin_layer import ProjectWorkspace
        self.mb_ws = ProjectWorkspace.objects.get(
            user=self.chris, name="Morning Brief"
        )

    def test_failure_emits_rejected_verdict_and_escalation(self):
        from core.models_deliverables import Deliverable
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )

        envelope = _failure_envelope(
            fail_at="lane_2_build_focus",
            inner_error="COOAgent dispatched but returned success=False",
        )
        with patch(
            "core.services.workflow_orchestration_agent."
            "WorkflowOrchestrationAgent.execute",
            return_value=envelope,
        ):
            # Wrapper re-raises on result.ok=False (CoS-specific
            # belt-and-suspenders behavior). MissionRunner itself catches
            # step failures + emits an escalation; the runner returns
            # ok=True at the envelope level. But the wrapper compares
            # ``result.ok`` (the runner's "did the lifecycle complete?"
            # boolean) — which IS True here. Failure mode is captured
            # by the verdict, NOT by the runner-level ok flag.
            #
            # So under our wrap-as-single-step contract: the workflow
            # returns success=False → wrapper Step returns passed=False
            # → MissionRunner emits rejected verdict + escalation
            # Deliverable + returns runner.ok=True + status='failed'.
            # The wrapper task's re-raise check (``if not result.ok``)
            # does NOT fire because the lifecycle completed cleanly.
            result = chief_of_staff_morning_brief_run()

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["verdict"], "rejected")

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at", "id")
            .values_list("label", flat=True)
        )
        self.assertIn("step_brief_workflow_failed", labels)
        self.assertIn("escalation_emitted", labels)
        self.assertIn("verdict_issued:rejected", labels)

        # Escalation Deliverable in Donkey Betz workspace.
        esc_id = run.summary.get("escalation_deliverable_id")
        self.assertIsNotNone(
            esc_id, "escalation_deliverable_id missing from summary"
        )
        esc = Deliverable.objects.get(id=esc_id)
        self.assertTrue(
            esc.title.startswith("Chief of Staff Escalation"),
            f"Escalation Deliverable title wrong: {esc.title!r}",
        )
        # Inner failed step surfaces in escalation body for diagnostic.
        self.assertIn("lane_2_build_focus", esc.content)
        # Summary captures the inner failed step too.
        self.assertEqual(
            run.summary.get("inner_failed_step"), "lane_2_build_focus"
        )

    def test_failure_with_runner_level_error_re_raises(self):
        """Sanity: if the runner itself fails (top-level exception not
        a step failure), the Celery wrapper re-raises so the
        CeleryTaskEvent records FAILURE."""
        from core.tasks_chief_of_staff import (
            chief_of_staff_morning_brief_run,
        )
        from core.employees.mission_runner import MissionRunResult

        bad_result = MissionRunResult(
            ok=False,
            mission_id="",
            status="unknown",
            verdict=None,
            wall_time_ms=0,
            summary={"runner_error": "synthetic"},
        )
        # IMPORTANT: patch the symbol on the WRAPPER's module, not the
        # source module. The wrapper imports build_chief_of_staff_runner
        # at module-load time via ``from core.jobs.morning_brief import
        # build_chief_of_staff_runner``, which binds the function into
        # ``core.tasks_chief_of_staff``'s namespace. Patching the source
        # module would leave the wrapper's reference unchanged — and the
        # real runner would dispatch the real workflow.
        with patch(
            "core.tasks_chief_of_staff.build_chief_of_staff_runner"
        ) as mock_builder:
            runner = mock_builder.return_value
            runner.run.return_value = bad_result

            with self.assertRaises(RuntimeError):
                chief_of_staff_morning_brief_run()


# ═════════════════════════════════════════════════════════════════════
# Builder-shape spot-checks (matches platform_audit BuilderTests shape)
# ═════════════════════════════════════════════════════════════════════


class ChiefOfStaffBuilderTests(TestCase):

    def test_builder_returns_mission_runner(self):
        from core.employees.mission_runner import MissionRunner
        from core.jobs.morning_brief import build_chief_of_staff_runner

        runner = build_chief_of_staff_runner()
        self.assertIsInstance(runner, MissionRunner)

    def test_runner_config_identity(self):
        from core.jobs.morning_brief import build_chief_of_staff_runner

        runner = build_chief_of_staff_runner()
        self.assertEqual(runner.config.employee_handle, "chief_of_staff")
        self.assertEqual(runner.config.mission_run_kind, "morning_brief")
        self.assertEqual(runner.config.escalation_source, "ChiefOfStaff")
        self.assertEqual(runner.config.workspace_name, "Donkey Betz")
        self.assertIsNone(runner.config.pin_settings_key)
        self.assertIsNone(runner.config.primary_chat_id)

    def test_runner_has_one_wrapper_step(self):
        from core.jobs.morning_brief import (
            STEP_NAME,
            build_chief_of_staff_runner,
        )

        runner = build_chief_of_staff_runner()
        names = [s.name for s in runner.steps]
        self.assertEqual(names, [STEP_NAME])
        self.assertEqual(STEP_NAME, "step_brief_workflow")

    def test_runner_has_no_pa_post_or_shift_report_or_pre_postflight(self):
        from core.jobs.morning_brief import build_chief_of_staff_runner

        runner = build_chief_of_staff_runner()
        self.assertIsNone(runner.pa_post_fn)
        self.assertIsNone(runner.shift_report_fn)
        self.assertIsNone(runner.preflight_fn)
        self.assertIsNone(runner.postflight_fn)
