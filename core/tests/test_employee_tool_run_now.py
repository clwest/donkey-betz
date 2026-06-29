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
        result = _call_run_now(
            {"action": "run_now", "employee": "ghost", "job": "docs_manager"},
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("supports only employee='rigby'", result["error"])

    def test_run_now_rejects_unknown_job(self):
        result = _call_run_now(
            {"action": "run_now", "employee": "rigby", "job": "not-a-job"},
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("supports only job='docs_manager'", result["error"])
        self.assertIn("docs_manager", result["known_jobs"])

    def test_run_now_missing_job_returns_error(self):
        result = _call_run_now(
            {"action": "run_now", "employee": "rigby"},
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("supports only job='docs_manager'", result["error"])


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
            "core.tasks_documentation_manager.call_command"
        ) as cc_mock, patch(
            "core.tasks_documentation_manager.subprocess.run"
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
