"""Session 1257 PR 2.1 — Platform Auditor employee registration tests.

Proves that the second AI employee (Platform Auditor) appears in the
registry and that ``employee_tool action=describe`` surfaces both the
employee profile and the ``platform_audit`` JobContract.

Scope discipline (per PR 2.1):
- No task runner is implemented yet; this PR is contract/registry only.
- No MissionRunner changes were made; an AST contract test asserts
  that no employee-specific symbols leaked into MissionRunner.
- Existing Rigby / Documentation Manager behavior unchanged.

Run::

    .venv/bin/python manage.py test core.tests.test_employees_platform_auditor -v2
"""

from __future__ import annotations

import ast
from pathlib import Path

from django.test import SimpleTestCase

from core.employees import (
    AuthorityLevel,
    DOCUMENTATION_MANAGER,
    PLATFORM_AUDITOR,
    PLATFORM_AUDIT_JOB,
    RIGBY,
    get_employee,
    get_job,
    list_employees,
    list_job_keys_for_employee,
    list_jobs_for_employee,
    list_jobs_with_keys,
)
from core.services.td_handlers_employee import EmployeeHandlersMixin


MISSION_RUNNER_PATH = (
    Path(__file__).resolve().parents[1] / "employees" / "mission_runner.py"
)


def _call_describe(payload: dict) -> dict:
    """Invoke `_handle_employee_tool` on a bare mixin instance."""
    handler = EmployeeHandlersMixin()
    return handler._handle_employee_tool(
        tool_name="employee_tool",
        payload=payload,
        user_id=None,
        trace_id="test-trace-id",
    )


# ═════════════════════════════════════════════════════════════════════
# Registry — Platform Auditor exists alongside Rigby
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditorRegistryTests(SimpleTestCase):

    def test_platform_auditor_appears_in_list_employees(self):
        handles = {e.handle for e in list_employees()}
        self.assertIn("platform_auditor", handles)
        # Rigby still present.
        self.assertIn("rigby", handles)

    def test_get_employee_resolves_platform_auditor(self):
        self.assertIs(get_employee("platform_auditor"), PLATFORM_AUDITOR)

    def test_get_employee_case_insensitive(self):
        self.assertIs(get_employee("Platform_Auditor"), PLATFORM_AUDITOR)
        self.assertIs(get_employee("PLATFORM_AUDITOR"), PLATFORM_AUDITOR)

    def test_get_job_resolves_platform_audit(self):
        self.assertIs(
            get_job("platform_auditor", "platform_audit"),
            PLATFORM_AUDIT_JOB,
        )

    def test_get_job_case_insensitive(self):
        self.assertIs(
            get_job("Platform_Auditor", "Platform_Audit"),
            PLATFORM_AUDIT_JOB,
        )

    def test_list_jobs_for_employee_returns_platform_audit(self):
        jobs = list_jobs_for_employee("platform_auditor")
        self.assertEqual(len(jobs), 1)
        self.assertIs(jobs[0], PLATFORM_AUDIT_JOB)

    def test_list_jobs_with_keys_returns_platform_audit(self):
        items = list_jobs_with_keys("platform_auditor")
        self.assertEqual(len(items), 1)
        key, contract = items[0]
        self.assertEqual(key, "platform_audit")
        self.assertIs(contract, PLATFORM_AUDIT_JOB)

    def test_list_job_keys_for_employee_returns_platform_audit(self):
        self.assertEqual(
            list_job_keys_for_employee("platform_auditor"),
            ["platform_audit"],
        )

    def test_unknown_employee_returns_none(self):
        self.assertIsNone(get_employee("not-an-employee"))

    def test_unknown_job_returns_none(self):
        self.assertIsNone(
            get_job("platform_auditor", "not-a-job")
        )


# ═════════════════════════════════════════════════════════════════════
# Registry — Rigby / Documentation Manager unchanged
# ═════════════════════════════════════════════════════════════════════


class RigbyRegistryUnchangedTests(SimpleTestCase):
    """Adding Employee #2 must not break Employee #1."""

    def test_rigby_still_resolves(self):
        self.assertIs(get_employee("rigby"), RIGBY)

    def test_docs_manager_still_resolves(self):
        self.assertIs(
            get_job("rigby", "docs_manager"), DOCUMENTATION_MANAGER
        )

    def test_rigby_jobs_unchanged(self):
        self.assertEqual(
            list_job_keys_for_employee("rigby"),
            ["docs_manager"],
        )

    def test_rigby_list_jobs_with_keys_unchanged(self):
        items = list_jobs_with_keys("rigby")
        self.assertEqual(len(items), 1)
        key, contract = items[0]
        self.assertEqual(key, "docs_manager")
        self.assertIs(contract, DOCUMENTATION_MANAGER)


# ═════════════════════════════════════════════════════════════════════
# describe handler surfaces Platform Auditor
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditorDescribeHandlerTests(SimpleTestCase):

    def test_describe_platform_auditor_no_job_arg(self):
        """``employee_tool action=describe employee=platform_auditor``
        returns the employee profile + the platform_audit job."""
        result = _call_describe(
            {"action": "describe", "employee": "platform_auditor"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "describe")
        self.assertEqual(result["employee"]["handle"], "platform_auditor")
        self.assertEqual(
            result["employee"]["display_name"], "Platform Auditor"
        )
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(len(result["jobs"]), 1)
        self.assertEqual(result["jobs"][0]["key"], "platform_audit")

    def test_describe_platform_auditor_with_job_arg(self):
        result = _call_describe(
            {
                "action": "describe",
                "employee": "platform_auditor",
                "job": "platform_audit",
            }
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["key"], "platform_audit")
        contract = result["jobs"][0]["contract"]
        self.assertEqual(contract["title"], "Platform Audit")
        self.assertEqual(
            contract["mission_run_kind"], "platform_audit"
        )

    def test_describe_platform_auditor_employee_block(self):
        result = _call_describe(
            {"action": "describe", "employee": "platform_auditor"}
        )
        emp = result["employee"]
        self.assertEqual(emp["handle"], "platform_auditor")
        self.assertEqual(emp["display_name"], "Platform Auditor")
        self.assertEqual(emp["runs_as_username"], "chris")
        self.assertIsNone(emp["primary_chat_id"])

    def test_describe_platform_auditor_contract_surface(self):
        """Spot-check key contract fields surface correctly."""
        result = _call_describe(
            {"action": "describe", "employee": "platform_auditor"}
        )
        contract = result["jobs"][0]["contract"]

        # Mission text mentions read-only intent.
        self.assertIn("read-only", contract["mission"].lower())

        # Authority dict has the read-only set + the prohibited set.
        authority = contract["authority"]
        self.assertEqual(
            authority["read_platform_docs"],
            AuthorityLevel.EXECUTE.value,
        )
        self.assertEqual(
            authority["check_env_config_status"],
            AuthorityLevel.OBSERVE.value,
        )
        self.assertEqual(
            authority["modify_any_file"],
            AuthorityLevel.PROHIBITED.value,
        )
        self.assertEqual(
            authority["access_secret_values"],
            AuthorityLevel.PROHIBITED.value,
        )

        # required_summary_keys contains the audit-specific evidence
        # contract from PR 2.1.
        keys = set(contract["required_summary_keys"])
        for k in (
            "audit_type",
            "findings_count",
            "report_deliverable_id",
            "wall_time_ms",
            "failed_step",
            "error_tail",
            "degraded_evidence",
        ):
            self.assertIn(
                k, keys, f"required_summary_keys missing {k!r}"
            )

        # Evidence tables include the platform_audit OpsRun key.
        evidence = contract["evidence_tables"]
        self.assertTrue(
            any("run_kind=platform_audit" in e for e in evidence),
            f"evidence_tables missing run_kind=platform_audit: {evidence}",
        )

    def test_describe_unknown_job_returns_actual_known_jobs(self):
        """PR 2.1 generalized the unknown-job error to surface the
        actual registry-held keys instead of hardcoded ``docs_manager``."""
        result = _call_describe(
            {
                "action": "describe",
                "employee": "platform_auditor",
                "job": "not-a-real-job",
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["known_jobs"], ["platform_audit"])

    def test_describe_rigby_still_returns_docs_manager(self):
        """Rigby's describe surface unchanged after the generalization."""
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["key"], "docs_manager")

    def test_describe_rigby_unknown_job_lists_docs_manager(self):
        """Rigby's unknown-job error still lists docs_manager."""
        result = _call_describe(
            {
                "action": "describe",
                "employee": "rigby",
                "job": "not-a-real-job",
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["known_jobs"], ["docs_manager"])


# ═════════════════════════════════════════════════════════════════════
# Contract — no MissionRunner changes in PR 2.1
# ═════════════════════════════════════════════════════════════════════


class NoMissionRunnerChangesTests(SimpleTestCase):
    """PR 2.1 must not touch ``core/employees/mission_runner.py``
    semantics. AST scan asserts MissionRunner does not import any
    employee-specific symbol.
    """

    @classmethod
    def _load_module_ast(cls):
        source = MISSION_RUNNER_PATH.read_text()
        return ast.parse(source, filename=str(MISSION_RUNNER_PATH))

    def test_mission_runner_does_not_import_platform_auditor(self):
        tree = self._load_module_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    self.assertNotIn(
                        alias.name,
                        {
                            "PLATFORM_AUDITOR",
                            "PLATFORM_AUDIT_JOB",
                            "RIGBY",
                            "DOCUMENTATION_MANAGER",
                        },
                        f"MissionRunner illegally imports {alias.name!r}",
                    )

    def test_mission_runner_does_not_reference_platform_auditor(self):
        """No bare references to employee constants in runner code."""
        tree = self._load_module_ast()
        forbidden = {
            "PLATFORM_AUDITOR",
            "PLATFORM_AUDIT_JOB",
            "RIGBY",
            "DOCUMENTATION_MANAGER",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in forbidden:
                self.fail(
                    f"MissionRunner references forbidden employee "
                    f"symbol {node.id!r} in code"
                )


# ═════════════════════════════════════════════════════════════════════
# JobContract dataclass shape — frozen + required fields populated
# ═════════════════════════════════════════════════════════════════════


class PlatformAuditJobContractShapeTests(SimpleTestCase):

    def test_contract_is_frozen(self):
        with self.assertRaises(Exception):
            PLATFORM_AUDIT_JOB.mission = "different"  # type: ignore

    def test_contract_identity_fields(self):
        self.assertEqual(PLATFORM_AUDIT_JOB.title, "Platform Audit")
        self.assertEqual(
            PLATFORM_AUDIT_JOB.employee_handle, "platform_auditor"
        )
        self.assertEqual(PLATFORM_AUDIT_JOB.manager, "chris")
        self.assertEqual(
            PLATFORM_AUDIT_JOB.mission_run_kind, "platform_audit"
        )

    def test_contract_authority_is_read_only_dominated(self):
        """Every WRITE-shaped action must be PROHIBITED, not EXECUTE."""
        authority = PLATFORM_AUDIT_JOB.authority
        for key in (
            "modify_any_file",
            "modify_env_config",
            "delete_database_rows",
            "execute_arbitrary_code",
            "access_secret_values",
            "open_pull_request",
            "modify_settings",
        ):
            self.assertEqual(
                authority.get(key),
                AuthorityLevel.PROHIBITED.value,
                f"authority[{key!r}] should be PROHIBITED for a "
                f"read-only auditor; got {authority.get(key)!r}",
            )

    def test_contract_prohibited_actions_match_authority_prohibitions(self):
        """The prohibited_actions tuple should describe the same
        denials that authority['<x>'] = PROHIBITED encodes."""
        prohibited_text = "\n".join(
            PLATFORM_AUDIT_JOB.prohibited_actions
        ).lower()
        # Each prohibited concern named in authority should appear in
        # the human-readable prohibited_actions tuple.
        for fragment in (
            "modify any file",
            "execute arbitrary code",
            "secret",
            "pull request",
        ):
            self.assertIn(
                fragment, prohibited_text,
                f"prohibited_actions missing reference to {fragment!r}",
            )

    def test_contract_required_summary_keys_covers_evidence(self):
        keys = set(PLATFORM_AUDIT_JOB.required_summary_keys)
        # Audit shape + step evidence + synthesis + timing/failure.
        for k in (
            "audit_type",
            "findings_count",
            "issues_found_count",
            "docs_audited",
            "integrations_audited_count",
            "env_vars_checked_count",
            "models_counted",
            "report_deliverable_id",
            "report_chars",
            "wall_time_ms",
            "failed_step",
            "error_tail",
            "degraded_evidence",
        ):
            self.assertIn(k, keys)
