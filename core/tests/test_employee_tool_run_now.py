"""
Session 1252 PR 2 — employee_tool action=run_now handler tests.

Real-DB integration. Mocks the Celery dispatch so tests don't fire
the actual cascade — the surface under test is the handler's
arg validation, auth gate, and wiring to the task dispatch path.

Run::

    python manage.py test core.tests.test_employee_tool_run_now -v2
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
from core.services.td_handlers_employee import EmployeeHandlersMixin


User = get_user_model()


def _call_run_now(payload: dict, user_id=None) -> dict:
    handler = EmployeeHandlersMixin()
    return handler._handle_employee_tool(
        tool_name="employee_tool",
        payload=payload,
        user_id=user_id,
        trace_id="test-trace-id",
    )


class RunNowSchemaTests(TestCase):
    """Ensure the PA tool schema advertises the run_now action."""

    def test_run_now_advertised_in_employee_tool_schema(self):
        schema = next(
            s for s in PA_TOOL_SCHEMAS
            if s.get("name") == "employee_tool"
        )
        self.assertIn("run_now", schema["parameters"]["properties"]["action"]["enum"])

    def test_wait_for_result_advertised_in_schema(self):
        schema = next(
            s for s in PA_TOOL_SCHEMAS
            if s.get("name") == "employee_tool"
        )
        self.assertIn(
            "wait_for_result", schema["parameters"]["properties"]
        )


class RunNowAuthTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chris = User.objects.create_user(
            username="chris",
            email="chris@test.donkey",
            password="x",
        )
        cls.imposter = User.objects.create_user(
            username="imposter",
            email="imposter@test.donkey",
            password="x",
        )

    def test_run_now_rejects_no_user_id(self):
        result = _call_run_now(
            {"action": "run_now", "employee": "rigby", "job": "docs_manager"},
            user_id=None,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "TOOL_PERMISSION_DENIED")

    def test_run_now_rejects_imposter(self):
        result = _call_run_now(
            {"action": "run_now", "employee": "rigby", "job": "docs_manager"},
            user_id=self.imposter.id,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "TOOL_PERMISSION_DENIED")

    def test_run_now_rejects_unknown_user_id(self):
        result = _call_run_now(
            {"action": "run_now", "employee": "rigby", "job": "docs_manager"},
            user_id=uuid.uuid4(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "TOOL_PERMISSION_DENIED")


class RunNowArgValidationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chris = User.objects.create_user(
            username="chris",
            email="chris@test.donkey",
            password="x",
        )

    def test_run_now_rejects_unknown_employee(self):
        """Session 1257 PR 2.2: error shape generalized to name the
        (employee, job) pair + advertise the supported pairs."""
        result = _call_run_now(
            {"action": "run_now", "employee": "ghost", "job": "docs_manager"},
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("employee='ghost'", result["error"])
        self.assertIn("does not support", result["error"])
        # supported_pairs surfaces the registry contents
        pairs = result["supported_pairs"]
        self.assertIn(
            {"employee": "rigby", "job": "docs_manager"}, pairs
        )

    def test_run_now_rejects_unknown_job(self):
        result = _call_run_now(
            {"action": "run_now", "employee": "rigby", "job": "not-a-job"},
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("job='not-a-job'", result["error"])
        self.assertIn("does not support", result["error"])
        pairs = result["supported_pairs"]
        self.assertIn(
            {"employee": "rigby", "job": "docs_manager"}, pairs
        )

    def test_run_now_missing_job_returns_error(self):
        result = _call_run_now(
            {"action": "run_now", "employee": "rigby"},
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("job=''", result["error"])
        self.assertIn("does not support", result["error"])


class RunNowDispatchTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chris = User.objects.create_user(
            username="chris",
            email="chris@test.donkey",
            password="x",
        )

    def test_run_now_dispatches_task_and_returns_task_id(self):
        with patch(
            "core.tasks_documentation_manager."
            "rigby_documentation_manager_daily.delay"
        ) as delay_mock:
            delay_mock.return_value = MagicMock(id="celery-task-uuid")
            result = _call_run_now(
                {
                    "action": "run_now",
                    "employee": "rigby",
                    "job": "docs_manager",
                },
                user_id=self.chris.id,
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "run_now")
        self.assertEqual(result["dispatch_status"], "queued")
        self.assertEqual(result["task_id"], "celery-task-uuid")
        self.assertFalse(result["wait_for_result"])
        delay_mock.assert_called_once()

    def test_run_now_does_not_block_when_wait_false(self):
        """Default path returns immediately without polling."""
        with patch(
            "core.tasks_documentation_manager."
            "rigby_documentation_manager_daily.delay"
        ) as delay_mock:
            delay_mock.return_value = MagicMock(id="abc")
            result = _call_run_now(
                {
                    "action": "run_now",
                    "employee": "rigby",
                    "job": "docs_manager",
                    # wait_for_result omitted → default False
                },
                user_id=self.chris.id,
            )
        self.assertFalse(result.get("wait_timeout", False))
        self.assertNotIn("status", result)

    def test_run_now_wait_returns_mission_when_terminal_available(self):
        """When wait_for_result=True and a mission already exists in a
        terminal state, returns it immediately on the first poll."""
        from core.models_ops_runs import OpsRun

        # Seed a terminal mission so the wait loop's first poll matches.
        OpsRun.objects.create(
            title="seeded terminal",
            run_type="manual",
            domain="mission",
            run_kind="docs_cascade",
            mission_id=uuid.uuid4(),
            status="passed",
            summary={"verdict": "certified"},
        )
        with patch(
            "core.tasks_documentation_manager."
            "rigby_documentation_manager_daily.delay"
        ) as delay_mock:
            delay_mock.return_value = MagicMock(id="abc")
            result = _call_run_now(
                {
                    "action": "run_now",
                    "employee": "rigby",
                    "job": "docs_manager",
                    "wait_for_result": True,
                },
                user_id=self.chris.id,
            )
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "passed")
        self.assertIn("mission_id", result)
        self.assertEqual(result["summary"], {"verdict": "certified"})

    def test_run_now_wait_returns_timeout_when_no_terminal_mission(self):
        """When wait_for_result=True and the mission never reaches
        terminal status, helper times out cleanly."""
        with patch(
            "core.tasks_documentation_manager."
            "rigby_documentation_manager_daily.delay"
        ) as delay_mock, patch(
            "core.services.td_handlers_employee._wait_for_terminal_mission",
            return_value=None,
        ):
            delay_mock.return_value = MagicMock(id="abc")
            result = _call_run_now(
                {
                    "action": "run_now",
                    "employee": "rigby",
                    "job": "docs_manager",
                    "wait_for_result": True,
                },
                user_id=self.chris.id,
            )
        self.assertTrue(result["ok"])
        self.assertTrue(result.get("wait_timeout"))

    def test_run_now_does_not_run_cascade_inline(self):
        """Handler dispatches but does NOT execute the cascade
        commands during the dispatch call itself."""
        with patch(
            "core.tasks_documentation_manager."
            "rigby_documentation_manager_daily.delay"
        ) as delay_mock, patch(
            "core.jobs.docs_cascade.call_command"
        ) as cc_mock, patch(
            "core.jobs.docs_cascade.subprocess.run"
        ) as sp_mock:
            delay_mock.return_value = MagicMock(id="abc")
            _call_run_now(
                {
                    "action": "run_now",
                    "employee": "rigby",
                    "job": "docs_manager",
                },
                user_id=self.chris.id,
            )
        # call_command + subprocess.run must NOT have been called
        # synchronously — that would mean the cascade ran inline
        # rather than being queued.
        cc_mock.assert_not_called()
        sp_mock.assert_not_called()


# ═════════════════════════════════════════════════════════════════════
# Session 1257 PR 2.2 — Platform Auditor run_now path
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditorRunNowDispatchTests(TestCase):
    """run_now dispatches platform_auditor_run for the new employee."""

    @classmethod
    def setUpTestData(cls):
        cls.chris = User.objects.create_user(
            username="chris",
            email="chris@test.donkey",
            password="x",
        )

    def test_run_now_dispatches_platform_auditor_run(self):
        with patch(
            "core.tasks_platform_audit."
            "platform_auditor_run.delay"
        ) as delay_mock:
            delay_mock.return_value = MagicMock(id="celery-pa-task")
            result = _call_run_now(
                {
                    "action": "run_now",
                    "employee": "platform_auditor",
                    "job": "platform_audit",
                },
                user_id=self.chris.id,
            )
        delay_mock.assert_called_once_with()
        self.assertTrue(result["ok"])
        self.assertEqual(result["employee"], "platform_auditor")
        self.assertEqual(result["job"], "platform_audit")
        self.assertEqual(result["task_id"], "celery-pa-task")
        self.assertEqual(result["dispatch_status"], "queued")

    def test_run_now_does_not_run_audit_inline(self):
        """Calling run_now for platform_auditor must NOT invoke any of
        the agent's tool methods synchronously — the cascade runs in
        the worker, not in the dispatcher."""
        with patch(
            "core.tasks_platform_audit."
            "platform_auditor_run.delay"
        ) as delay_mock, patch(
            "core.agents.platform_audit_agent."
            "PlatformAuditAgent._inventory_integrations"
        ) as inv_mock, patch(
            "core.agents.platform_audit_agent."
            "PlatformAuditAgent._count_database_models"
        ) as count_mock:
            delay_mock.return_value = MagicMock(id="celery-pa-task")
            _call_run_now(
                {
                    "action": "run_now",
                    "employee": "platform_auditor",
                    "job": "platform_audit",
                },
                user_id=self.chris.id,
            )
        inv_mock.assert_not_called()
        count_mock.assert_not_called()

    def test_rigby_run_now_still_dispatches_docs_manager(self):
        """Regression check — generalization must not break Rigby."""
        with patch(
            "core.tasks_documentation_manager."
            "rigby_documentation_manager_daily.delay"
        ) as delay_mock:
            delay_mock.return_value = MagicMock(id="celery-rigby-task")
            result = _call_run_now(
                {
                    "action": "run_now",
                    "employee": "rigby",
                    "job": "docs_manager",
                },
                user_id=self.chris.id,
            )
        delay_mock.assert_called_once_with()
        self.assertEqual(result["employee"], "rigby")
        self.assertEqual(result["job"], "docs_manager")

    def test_supported_pairs_includes_both_employees(self):
        """Unknown employee error advertises the supported pairs."""
        result = _call_run_now(
            {
                "action": "run_now",
                "employee": "unknown_employee",
                "job": "something",
            },
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        pairs = result["supported_pairs"]
        self.assertIn(
            {"employee": "rigby", "job": "docs_manager"}, pairs
        )
        self.assertIn(
            {"employee": "platform_auditor", "job": "platform_audit"},
            pairs,
        )

    def test_wait_for_result_polls_platform_audit_run_kind(self):
        """When wait_for_result=True, the polling helper queries
        run_kind='platform_audit' (not the docs_cascade default)."""
        terminal = MagicMock(id="ops-uuid", status="passed", summary={})
        with patch(
            "core.tasks_platform_audit."
            "platform_auditor_run.delay"
        ) as delay_mock, patch(
            "core.services.td_handlers_employee._wait_for_terminal_mission",
            return_value=terminal,
        ) as poll_mock:
            delay_mock.return_value = MagicMock(id="celery-pa-task")
            _call_run_now(
                {
                    "action": "run_now",
                    "employee": "platform_auditor",
                    "job": "platform_audit",
                    "wait_for_result": True,
                },
                user_id=self.chris.id,
            )
        # The polling call must have passed run_kind='platform_audit'
        poll_kwargs = poll_mock.call_args.kwargs
        self.assertEqual(poll_kwargs.get("run_kind"), "platform_audit")
