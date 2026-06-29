"""
Tests for the Session 1252 PR 1 ``employee_tool`` PA tool handler.

Covers:
- action=describe employee=rigby returns the full Rigby + Documentation
  Manager contract as structured JSON
- response is concise (under 2KB target — but loose enough to allow
  the contract text to grow with future Rigby edits without breaking
  the test)
- unknown employee returns a clean error + known_employees list
- unknown job returns a clean error
- unknown action returns a clean error + valid_actions list
- missing employee arg returns a clean error
- dataclass → JSON coercion is recursive (no leftover dataclass
  instances or enum objects in the response payload)
- the AuthorityLevel str-enum coerces to its underlying string value

Run::

    python manage.py test core.tests.test_employee_tool_describe -v2
"""

from __future__ import annotations

import json

from django.test import SimpleTestCase

from core.services.td_handlers_employee import EmployeeHandlersMixin


def _call_describe(payload: dict) -> dict:
    """Invoke ``_handle_employee_tool`` on a bare mixin instance.

    The handler is pure (no dispatcher self-state), so a bare mixin
    instance is sufficient for unit-level testing of the handler
    contract.
    """
    handler = EmployeeHandlersMixin()
    return handler._handle_employee_tool(
        tool_name="employee_tool",
        payload=payload,
        user_id=None,
        trace_id="test-trace-id",
    )


class EmployeeToolDescribeHappyPathTests(SimpleTestCase):

    def test_describe_rigby_returns_one_job(self):
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "describe")
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(len(result["jobs"]), 1)
        self.assertEqual(result["jobs"][0]["key"], "docs_manager")

    def test_describe_employee_block_includes_identity(self):
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        emp = result["employee"]
        self.assertEqual(emp["handle"], "rigby")
        self.assertEqual(emp["display_name"], "Rigby")
        self.assertEqual(emp["runs_as_username"], "chris")
        self.assertEqual(emp["primary_chat_id"], "pa-3901b70e61934df7")

    def test_describe_contract_includes_rigby_edits(self):
        """The single-job describe surface returns the full contract."""
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        contract = result["jobs"][0]["contract"]

        # Edit #1
        self.assertIn("best-effort", contract["mission"].lower())

        # Edit #2 — required_summary_keys must include all 12 fields
        keys = set(contract["required_summary_keys"])
        for k in (
            "drift_count",
            "embedding_delta",
            "wall_time_ms",
            "failed_step",
            "degraded_evidence",
        ):
            self.assertIn(k, keys)

        # Edit #4 — timeout dict
        self.assertEqual(
            contract["embed_step_timeout"]["warning_seconds"], 600
        )
        self.assertEqual(
            contract["embed_step_timeout"]["hard_seconds"], 1800
        )

        # Edit #5 — escalation visibility mentions publish_candidate
        joined = " ".join(contract["escalation_visibility"]).lower()
        self.assertIn("publish_candidate", joined)

        # Edit #6 — dedupe by failure signature
        self.assertIn(
            "failure signature", contract["dedupe_rule"].lower()
        )

    def test_describe_with_explicit_job_key(self):
        result = _call_describe(
            {
                "action": "describe",
                "employee": "rigby",
                "job": "docs_manager",
            }
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["key"], "docs_manager")

    def test_employee_case_insensitive(self):
        result = _call_describe(
            {"action": "describe", "employee": "RIGBY"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["employee"]["handle"], "rigby")


class EmployeeToolDescribeJsonShapeTests(SimpleTestCase):
    """Coercion + serialization safety."""

    def test_response_is_json_serializable(self):
        """No leftover dataclass instances or enum objects."""
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        try:
            json.dumps(result)
        except TypeError as exc:
            self.fail(f"describe response not JSON-serializable: {exc}")

    def test_authority_levels_coerced_to_strings(self):
        """str-enum members must come through as their .value, not as
        'AuthorityLevel.EXECUTE' or as an enum instance."""
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        authority = result["jobs"][0]["contract"]["authority"]
        valid_levels = {"observe", "recommend", "execute", "prohibited"}
        for action_name, level in authority.items():
            self.assertIn(
                level,
                valid_levels,
                f"{action_name!r} got non-canonical level {level!r}",
            )

    def test_response_size_runaway_guard(self):
        """Regression guard, not a hard size target.

        PR 1 acceptance criteria #5 said "ideally under 2KB unless
        there is a strong reason." Rigby's six required edits added
        prose-heavy fields (mission disclaimer language,
        drift_count_definition, dedupe_rule, escalation_visibility
        triplet) — those ARE the strong reason. As of PR 1 the full
        describe payload is ~6.6KB. We cap the regression guard at
        8KB so future small edits don't accidentally break the test,
        but a doubling of the contract surface would.

        For routine reading, PR 3's ``employee_tool action=status``
        will be the daily-check surface; ``describe`` is the
        deep-inspection surface for contract review.
        """
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        payload = json.dumps(result)
        self.assertLess(
            len(payload),
            8192,
            f"describe payload is {len(payload)} bytes — likely a "
            "runaway addition rather than a deliberate Rigby edit",
        )


class EmployeeToolDescribeErrorPathTests(SimpleTestCase):

    def test_unknown_action_returns_error(self):
        result = _call_describe({"action": "fire", "employee": "rigby"})
        self.assertFalse(result["ok"])
        self.assertIn("Unknown employee_tool action", result["error"])
        # Session 1252 PR 2 added 'run_now' to the action vocabulary.
        self.assertEqual(
            sorted(result["valid_actions"]),
            ["describe", "run_now"],
        )

    def test_missing_employee_returns_error_with_known_list(self):
        result = _call_describe({"action": "describe"})
        self.assertFalse(result["ok"])
        self.assertIn("Missing required arg 'employee'", result["error"])
        self.assertIn("rigby", result["known_employees"])

    def test_unknown_employee_returns_error_with_known_list(self):
        result = _call_describe(
            {"action": "describe", "employee": "ghost-employee"}
        )
        self.assertFalse(result["ok"])
        self.assertIn("Unknown employee", result["error"])
        self.assertIn("rigby", result["known_employees"])

    def test_unknown_job_returns_error(self):
        result = _call_describe(
            {
                "action": "describe",
                "employee": "rigby",
                "job": "not-a-real-job",
            }
        )
        self.assertFalse(result["ok"])
        self.assertIn("no job keyed", result["error"])

    def test_default_action_is_describe(self):
        """Calling without explicit action falls back to describe."""
        result = _call_describe({"employee": "rigby"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "describe")
