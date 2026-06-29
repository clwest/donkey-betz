"""Session 1257 PR 2.2 — Platform Auditor task runner routine tests.

End-to-end behavior of the Platform Audit cascade via MissionRunner.
Real-DB PostgreSQL integration. Each test mocks PlatformAuditAgent's
tool methods at the `core.jobs.platform_audit` import surface so
tests stay deterministic + fast — but all OpsRun / OpsRunEvent /
Deliverable / DirectMessage assertions hit real DB rows.

Covers:
  * Task delegates to MissionRunner via build_platform_audit_runner()
  * OpsRun has domain='mission', run_kind='platform_audit'
  * Event timeline matches expected sequence
  * mission.summary contains all 13 required_summary_keys
  * Successful run creates the audit Deliverable
  * Failed step path creates an escalation Deliverable (separate from
    audit Deliverable)
  * Verdict emits correctly (certified for success, rejected for fail)
  * Shift-report DM idempotency (one DM per terminal mission)
  * Daily idempotency (second run_now returns cached envelope)
  * No LLM calls happen during the task
  * No PeriodicTask added by PR 2.2
"""

from __future__ import annotations

from contextlib import ExitStack
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.employees import PLATFORM_AUDIT_JOB, PLATFORM_AUDITOR

User = get_user_model()


# ── Fixtures ──────────────────────────────────────────────────────────


def _setup_user_and_workspace():
    """Ensure chris user + Donkey Betz workspace exist."""
    chris, _ = User.objects.get_or_create(
        username="chris",
        defaults={"email": "chris@test.donkey"},
    )
    try:
        from core.models_skin_layer import ProjectWorkspace

        ProjectWorkspace.objects.get_or_create(
            name="Donkey Betz",
            defaults={
                "description": "Test workspace for Platform Audit tests.",
                "user": chris,
                "root_path": "/tmp/test-donkey-betz",
            },
        )
    except Exception:
        pass
    return chris


def _mock_all_steps_pass(stack: ExitStack):
    """Patch every tool method on the agent so the cascade passes."""
    # step 1 — _read_documentation returns valid doc for every name
    rd = stack.enter_context(
        patch(
            "core.agents.platform_audit_agent."
            "PlatformAuditAgent._read_documentation",
            return_value={
                "document": "x",
                "section": None,
                "content": "abc",
                "length": 3,
            },
        )
    )
    # step 2
    stack.enter_context(
        patch(
            "core.agents.platform_audit_agent."
            "PlatformAuditAgent._inventory_integrations",
            return_value={
                "total": 19,
                "configured": 7,
                "missing": 12,
                "integrations": [
                    {
                        "name": "OpenAI",
                        "env_var": "OPENAI_API_KEY",
                        "category": "llm",
                        "configured": True,
                        "status": "configured",
                    },
                    {
                        "name": "Anthropic",
                        "env_var": "ANTHROPIC_API_KEY",
                        "category": "llm",
                        "configured": False,
                        "status": "missing",
                    },
                ],
            },
        )
    )
    # step 3
    stack.enter_context(
        patch(
            "core.agents.platform_audit_agent."
            "PlatformAuditAgent._check_env_config",
            return_value={
                "api_keys": {
                    "OPENAI_API_KEY": {
                        "configured": True, "value_preview": "sk-***abcd"
                    },
                    "ANTHROPIC_API_KEY": {
                        "configured": False, "value_preview": None
                    },
                },
                "database": {
                    "DATABASE_URL": {
                        "configured": True,
                        "value_preview": "postgres://...",
                    },
                },
            },
        )
    )
    # step 4
    stack.enter_context(
        patch(
            "core.agents.platform_audit_agent."
            "PlatformAuditAgent._count_database_models",
            return_value={
                "Agent": {"count": 89},
                "AgentExecution": {"count": 1234},
                "AgentMemory": {"count": 567},
                "LegacySpiderData": {"count": 8200},
                "Conversation": {"count": 50},
                "User": {"count": 12},
                "ImageHistory": {"count": 200},
                "VideoHistory": {"count": 30},
            },
        )
    )
    return rd


def _mock_step_fails(stack: ExitStack, fail_at: str):
    """Patch so a specific step raises.

    fail_at: one of 'inventory_integrations' / 'check_env_config' /
    'count_database_models'.
    """
    method_map = {
        "inventory_integrations": "_inventory_integrations",
        "check_env_config": "_check_env_config",
        "count_database_models": "_count_database_models",
    }
    method_name = method_map[fail_at]
    stack.enter_context(
        patch(
            "core.agents.platform_audit_agent."
            f"PlatformAuditAgent.{method_name}",
            side_effect=RuntimeError(
                f"synthetic failure in {method_name}"
            ),
        )
    )
    # Other steps pass.
    stack.enter_context(
        patch(
            "core.agents.platform_audit_agent."
            "PlatformAuditAgent._read_documentation",
            return_value={
                "document": "x",
                "section": None,
                "content": "abc",
                "length": 3,
            },
        )
    )
    if fail_at != "inventory_integrations":
        stack.enter_context(
            patch(
                "core.agents.platform_audit_agent."
                "PlatformAuditAgent._inventory_integrations",
                return_value={
                    "total": 1, "configured": 1, "missing": 0,
                    "integrations": [],
                },
            )
        )
    if fail_at != "check_env_config":
        stack.enter_context(
            patch(
                "core.agents.platform_audit_agent."
                "PlatformAuditAgent._check_env_config",
                return_value={},
            )
        )
    if fail_at != "count_database_models":
        stack.enter_context(
            patch(
                "core.agents.platform_audit_agent."
                "PlatformAuditAgent._count_database_models",
                return_value={
                    name: {"count": 0}
                    for name in (
                        "Agent", "AgentExecution", "AgentMemory",
                        "LegacySpiderData", "Conversation", "User",
                        "ImageHistory", "VideoHistory",
                    )
                },
            )
        )


# ═════════════════════════════════════════════════════════════════════
# Builder shape — runner wiring
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditBuilderTests(TestCase):
    """build_platform_audit_runner() returns a properly-wired runner."""

    def test_builder_returns_mission_runner(self):
        from core.employees.mission_runner import MissionRunner
        from core.jobs.platform_audit import build_platform_audit_runner

        runner = build_platform_audit_runner()
        self.assertIsInstance(runner, MissionRunner)

    def test_builder_is_pure_no_per_call_state(self):
        """Two builds must produce step_fns that don't share dicts."""
        from core.jobs.platform_audit import build_platform_audit_runner

        r1 = build_platform_audit_runner()
        r2 = build_platform_audit_runner()

        def _has_dict_closure(fn):
            for cell in fn.__closure__ or ():
                if isinstance(cell.cell_contents, dict):
                    return True
            return False

        for s in r1.steps + r2.steps:
            self.assertFalse(
                _has_dict_closure(s.fn),
                f"Step {s.name!r} closes over a dict — builder should "
                "be pure (no closure-capture).",
            )

    def test_runner_config_identity(self):
        from core.jobs.platform_audit import build_platform_audit_runner

        runner = build_platform_audit_runner()
        self.assertEqual(
            runner.config.employee_handle, "platform_auditor"
        )
        self.assertEqual(runner.config.mission_run_kind, "platform_audit")
        self.assertEqual(
            runner.config.escalation_source, "PlatformAuditor"
        )
        self.assertEqual(runner.config.workspace_name, "Donkey Betz")
        # No pin for v0 — auditor reports via inbox + audit Deliverable.
        self.assertIsNone(runner.config.pin_settings_key)
        self.assertIsNone(runner.config.primary_chat_id)

    def test_runner_has_five_steps_in_canonical_order(self):
        from core.jobs.platform_audit import build_platform_audit_runner

        runner = build_platform_audit_runner()
        names = [s.name for s in runner.steps]
        self.assertEqual(
            names,
            [
                "step_1_read_docs",
                "step_2_inventory_integrations",
                "step_3_check_env_config",
                "step_4_count_database_models",
                "step_5_generate_audit_report",
            ],
        )

    def test_runner_has_no_preflight_or_postflight(self):
        """Platform audit doesn't need before/after probes or drift."""
        from core.jobs.platform_audit import build_platform_audit_runner

        runner = build_platform_audit_runner()
        self.assertIsNone(runner.preflight_fn)
        self.assertIsNone(runner.postflight_fn)

    def test_runner_has_no_pa_post_hook(self):
        """v0: auditor has no primary_chat_id → no PA post."""
        from core.jobs.platform_audit import build_platform_audit_runner

        runner = build_platform_audit_runner()
        self.assertIsNone(runner.pa_post_fn)

    def test_runner_has_shift_report_hook(self):
        from core.jobs.platform_audit import build_platform_audit_runner

        runner = build_platform_audit_runner()
        self.assertIsNotNone(runner.shift_report_fn)


# ═════════════════════════════════════════════════════════════════════
# Routine — success path end-to-end
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditSuccessPathTests(TestCase):

    def setUp(self):
        _setup_user_and_workspace()

    def test_successful_run_returns_certified_envelope(self):
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            result = platform_auditor_run()

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["verdict"], "certified")
        self.assertFalse(result["already_ran"])

    def test_ops_run_has_correct_domain_and_run_kind(self):
        from core.models_ops_runs import OpsRun
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            result = platform_auditor_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        self.assertEqual(run.domain, "mission")
        self.assertEqual(run.run_kind, "platform_audit")
        self.assertEqual(run.status, "passed")

    def test_event_timeline_success_path(self):
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            result = platform_auditor_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .order_by("created_at", "id")
            .values_list("label", flat=True)
        )
        # Expected: run_started + 5 (started/passed pairs) + verdict
        expected = [
            "run_started",
            "step_1_read_docs_started", "step_1_read_docs_passed",
            "step_2_inventory_integrations_started",
            "step_2_inventory_integrations_passed",
            "step_3_check_env_config_started",
            "step_3_check_env_config_passed",
            "step_4_count_database_models_started",
            "step_4_count_database_models_passed",
            "step_5_generate_audit_report_started",
            "step_5_generate_audit_report_passed",
            "verdict_issued:certified",
        ]
        self.assertEqual(labels, expected)

    def test_summary_contains_all_required_keys(self):
        from core.models_ops_runs import OpsRun
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            result = platform_auditor_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        for key in PLATFORM_AUDIT_JOB.required_summary_keys:
            self.assertIn(
                key, run.summary,
                f"summary missing required key {key!r}; "
                f"got keys: {sorted(run.summary.keys())}",
            )

    def test_audit_deliverable_persisted(self):
        from core.models_deliverables import Deliverable
        from core.models_ops_runs import OpsRun
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            result = platform_auditor_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        deliv_id = run.summary.get("report_deliverable_id")
        self.assertIsNotNone(deliv_id)
        deliv = Deliverable.objects.get(id=deliv_id)
        self.assertTrue(deliv.title.startswith("Platform Audit"))
        self.assertEqual(deliv.deliverable_type, "analysis")
        self.assertEqual(deliv.category, "Platform Audit")
        self.assertEqual(deliv.status, "ready")
        # Body has the 6 contract sections.
        for section in (
            "Executive Summary",
            "Integration Health",
            "Configuration Status",
            "Database Health",
            "Top Risks",
            "Green Checks",
        ):
            self.assertIn(section, deliv.content)

    def test_no_llm_calls_during_task(self):
        """The cascade calls tool methods directly — no LLM should fire."""
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            # Patch the OpenAI client factory; if any step calls it,
            # this test fails because get_openai_client was invoked.
            ai_call = stack.enter_context(
                patch(
                    "core.services.openai_client_factory.get_openai_client"
                )
            )
            anthropic_call = stack.enter_context(
                patch(
                    "core.services.anthropic_client_factory."
                    "get_anthropic_client"
                )
            )
            platform_auditor_run()

        self.assertFalse(
            ai_call.called,
            "OpenAI client was constructed during platform_auditor_run "
            "— PR 2.2 should not call any LLM.",
        )
        self.assertFalse(
            anthropic_call.called,
            "Anthropic client was constructed during platform_auditor_run "
            "— PR 2.2 should not call any LLM.",
        )


# ═════════════════════════════════════════════════════════════════════
# Routine — failure path end-to-end
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditFailurePathTests(TestCase):

    def setUp(self):
        _setup_user_and_workspace()

    def test_failure_emits_rejected_verdict(self):
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_step_fails(stack, "inventory_integrations")
            result = platform_auditor_run()

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["verdict"], "rejected")

    def test_failure_creates_escalation_deliverable_separate_from_audit(self):
        from core.models_deliverables import Deliverable
        from core.models_ops_runs import OpsRun
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_step_fails(stack, "check_env_config")
            result = platform_auditor_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        # Escalation Deliverable is created by MissionRunner.
        esc_id = run.summary.get("escalation_deliverable_id")
        self.assertIsNotNone(esc_id)
        esc = Deliverable.objects.get(id=esc_id)
        self.assertTrue(esc.title.startswith("Platform Audit Escalation"))
        # Audit Deliverable was NOT created — step 5 never ran.
        self.assertIsNone(run.summary.get("report_deliverable_id"))

    def test_failure_skips_subsequent_steps(self):
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_step_fails(stack, "check_env_config")
            result = platform_auditor_run()

        run = OpsRun.objects.get(id=result["mission_id"])
        labels = list(
            OpsRunEvent.objects.filter(run=run)
            .values_list("label", flat=True)
        )
        # step 3 failed; steps 4 + 5 should be skipped.
        self.assertIn("step_3_check_env_config_failed", labels)
        self.assertIn("step_4_count_database_models_skipped", labels)
        self.assertIn("step_5_generate_audit_report_skipped", labels)
        self.assertIn("escalation_emitted", labels)
        self.assertIn("verdict_issued:rejected", labels)


# ═════════════════════════════════════════════════════════════════════
# Idempotency — daily + shift-report
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditIdempotencyTests(TestCase):

    def setUp(self):
        _setup_user_and_workspace()

    def test_second_run_returns_already_ran(self):
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            first = platform_auditor_run()
            second = platform_auditor_run()

        self.assertFalse(first["already_ran"])
        self.assertTrue(second["already_ran"])
        self.assertEqual(first["mission_id"], second["mission_id"])

    def test_shift_report_dm_posted_once_per_mission(self):
        from core.models_messaging import DirectMessage
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            result = platform_auditor_run()

        mission_id = result["mission_id"]
        dm_count = DirectMessage.objects.filter(
            metadata__mission_id=mission_id
        ).count()
        self.assertEqual(dm_count, 1)

    def test_shift_report_idempotent_on_re_dispatch(self):
        """Repeated dispatches (cached envelope path) should NOT
        create additional DMs — the shift-report is gated by the
        `(thread, mission_id)` lookup in comms.py."""
        from core.models_messaging import DirectMessage
        from core.tasks_platform_audit import platform_auditor_run

        with ExitStack() as stack:
            _mock_all_steps_pass(stack)
            result = platform_auditor_run()
            # Second dispatch returns cached envelope; runner skips
            # the shift_report hook on cached re-runs.
            platform_auditor_run()

        mission_id = result["mission_id"]
        dm_count = DirectMessage.objects.filter(
            metadata__mission_id=mission_id
        ).count()
        self.assertEqual(dm_count, 1)


# ═════════════════════════════════════════════════════════════════════
# Production-callers contract — MissionRunner has exactly two
# ═════════════════════════════════════════════════════════════════════


class TwoProductionCallersTests(TestCase):
    """PR 2.2 promotes MissionRunner from 1 to 2 production callers.

    Defines a 'production caller' as: a non-test module that calls
    ``MissionRunner(...)`` or a ``build_*_runner()`` factory.
    """

    def test_exactly_two_production_callers(self):
        import ast
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[2]
        core_dir = repo_root / "core"

        callers = set()
        for py in core_dir.rglob("*.py"):
            # Skip tests.
            if "/tests/" in str(py):
                continue
            # Skip the runner module itself (the docstring example
            # references MissionRunner but doesn't instantiate).
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
                    ):
                        callers.add(str(py.relative_to(repo_root)))

        # The factory modules themselves call MissionRunner(...) —
        # those count as PART of the production caller they back.
        # Group them by job.
        job_to_factory = {
            "docs_manager": {
                "core/tasks_documentation_manager.py",
                "core/jobs/docs_cascade.py",
            },
            "platform_audit": {
                "core/tasks_platform_audit.py",
                "core/jobs/platform_audit.py",
            },
        }
        observed_jobs = set()
        for path in callers:
            for job, files in job_to_factory.items():
                if path in files:
                    observed_jobs.add(job)
        self.assertEqual(
            observed_jobs,
            {"docs_manager", "platform_audit"},
            f"Expected exactly 2 production callers (docs_manager + "
            f"platform_audit); observed call sites: {sorted(callers)}",
        )


# ═════════════════════════════════════════════════════════════════════
# No PeriodicTask added by PR 2.2
# ═════════════════════════════════════════════════════════════════════


class NoBeatScheduleTests(TestCase):

    def test_no_periodic_task_for_platform_auditor(self):
        from django_celery_beat.models import PeriodicTask

        # The beat schedule lands in PR 2.3; PR 2.2 must NOT register
        # any PeriodicTask for the platform_auditor_run task.
        count = PeriodicTask.objects.filter(
            task="platform_auditor_run"
        ).count()
        self.assertEqual(
            count, 0,
            "PR 2.2 must not register a PeriodicTask for "
            "platform_auditor_run — the beat schedule lands in PR 2.3.",
        )
