"""Session 1257 PR 3.1 — Chief of Staff employee registration tests.

Proves that the third AI employee (Chief of Staff) appears in the
registry and that ``employee_tool action=describe`` surfaces both the
employee profile and the ``morning_brief`` JobContract.

Scope discipline (per PR 3.1):
- No task runner is implemented yet; this PR is contract/registry only.
- No MissionRunner changes were made; an AST contract test asserts
  that no employee-specific symbols leaked into MissionRunner.
- No new MissionRunner production callers — count stays at exactly
  two (Documentation Manager + Platform Auditor).
- Existing Rigby / Documentation Manager + Platform Auditor surfaces
  unchanged.

Authority boundary (verified by 12 PROHIBITED + 11 EXECUTE/OBSERVE/
RECOMMEND assertions): Chief of Staff is v0 read-only synthesis +
Deliverable persistence ONLY. Per Chris's PR 3.1 directive:
- No external sends
- No source doc edits
- No schedule changes
- No decision approvals
- No business action execution
- No public posts
- No financial edits
- No user/account/settings modifications

Run::

    .venv/bin/python manage.py test core.tests.test_employees_chief_of_staff -v2
"""

from __future__ import annotations

import ast
from pathlib import Path

from django.test import SimpleTestCase

from core.employees import (
    AuthorityLevel,
    CHIEF_OF_STAFF,
    DOCUMENTATION_MANAGER,
    MORNING_BRIEF_JOB,
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
    handler = EmployeeHandlersMixin()
    return handler._handle_employee_tool(
        tool_name="employee_tool",
        payload=payload,
        user_id=None,
        trace_id="test-trace-id",
    )


# ═════════════════════════════════════════════════════════════════════
# Registry — Chief of Staff exists alongside Rigby + Platform Auditor
# ═════════════════════════════════════════════════════════════════════


class ChiefOfStaffRegistryTests(SimpleTestCase):

    def test_chief_of_staff_appears_in_list_employees(self):
        handles = {e.handle for e in list_employees()}
        self.assertIn("chief_of_staff", handles)
        # Prior employees still present.
        self.assertIn("rigby", handles)
        self.assertIn("platform_auditor", handles)

    def test_get_employee_resolves_chief_of_staff(self):
        self.assertIs(get_employee("chief_of_staff"), CHIEF_OF_STAFF)

    def test_get_employee_case_insensitive(self):
        self.assertIs(get_employee("Chief_Of_Staff"), CHIEF_OF_STAFF)
        self.assertIs(get_employee("CHIEF_OF_STAFF"), CHIEF_OF_STAFF)

    def test_get_job_resolves_morning_brief(self):
        self.assertIs(
            get_job("chief_of_staff", "morning_brief"),
            MORNING_BRIEF_JOB,
        )

    def test_get_job_case_insensitive(self):
        self.assertIs(
            get_job("Chief_Of_Staff", "Morning_Brief"),
            MORNING_BRIEF_JOB,
        )

    def test_list_jobs_for_employee_returns_morning_brief(self):
        jobs = list_jobs_for_employee("chief_of_staff")
        self.assertEqual(len(jobs), 1)
        self.assertIs(jobs[0], MORNING_BRIEF_JOB)

    def test_list_jobs_with_keys_returns_morning_brief(self):
        items = list_jobs_with_keys("chief_of_staff")
        self.assertEqual(len(items), 1)
        key, contract = items[0]
        self.assertEqual(key, "morning_brief")
        self.assertIs(contract, MORNING_BRIEF_JOB)

    def test_list_job_keys_for_employee_returns_morning_brief(self):
        self.assertEqual(
            list_job_keys_for_employee("chief_of_staff"),
            ["morning_brief"],
        )

    def test_unknown_employee_returns_none(self):
        self.assertIsNone(get_employee("not-an-employee"))

    def test_unknown_job_returns_none(self):
        self.assertIsNone(get_job("chief_of_staff", "not-a-job"))


# ═════════════════════════════════════════════════════════════════════
# Registry — existing employees unchanged
# ═════════════════════════════════════════════════════════════════════


class ExistingEmployeesUnchangedTests(SimpleTestCase):
    """Adding Employee #3 must not break Employees #1 or #2."""

    def test_rigby_still_resolves(self):
        self.assertIs(get_employee("rigby"), RIGBY)

    def test_docs_manager_still_resolves(self):
        self.assertIs(
            get_job("rigby", "docs_manager"), DOCUMENTATION_MANAGER
        )

    def test_platform_auditor_still_resolves(self):
        self.assertIs(get_employee("platform_auditor"), PLATFORM_AUDITOR)

    def test_platform_audit_still_resolves(self):
        self.assertIs(
            get_job("platform_auditor", "platform_audit"),
            PLATFORM_AUDIT_JOB,
        )

    def test_rigby_jobs_unchanged(self):
        self.assertEqual(
            list_job_keys_for_employee("rigby"),
            ["docs_manager"],
        )

    def test_platform_auditor_jobs_unchanged(self):
        self.assertEqual(
            list_job_keys_for_employee("platform_auditor"),
            ["platform_audit"],
        )

    def test_registry_now_has_four_employees(self):
        # Bug Triage Specialist (S1267 PR 4.1) became Employee #4.
        # Each new employee PR bumps this count.
        employees = list_employees()
        self.assertEqual(len(employees), 4)


# ═════════════════════════════════════════════════════════════════════
# describe handler surfaces Chief of Staff
# ═════════════════════════════════════════════════════════════════════


class ChiefOfStaffDescribeHandlerTests(SimpleTestCase):

    def test_describe_chief_of_staff_no_job_arg(self):
        result = _call_describe(
            {"action": "describe", "employee": "chief_of_staff"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "describe")
        self.assertEqual(result["employee"]["handle"], "chief_of_staff")
        self.assertEqual(
            result["employee"]["display_name"], "Chief of Staff"
        )
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(len(result["jobs"]), 1)
        self.assertEqual(result["jobs"][0]["key"], "morning_brief")

    def test_describe_chief_of_staff_with_job_arg(self):
        result = _call_describe(
            {
                "action": "describe",
                "employee": "chief_of_staff",
                "job": "morning_brief",
            }
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["key"], "morning_brief")
        contract = result["jobs"][0]["contract"]
        self.assertEqual(contract["title"], "Daily Morning Brief")
        self.assertEqual(contract["mission_run_kind"], "morning_brief")

    def test_describe_chief_of_staff_employee_block(self):
        result = _call_describe(
            {"action": "describe", "employee": "chief_of_staff"}
        )
        emp = result["employee"]
        self.assertEqual(emp["handle"], "chief_of_staff")
        self.assertEqual(emp["display_name"], "Chief of Staff")
        self.assertEqual(emp["runs_as_username"], "chris")
        self.assertIsNone(emp["primary_chat_id"])

    def test_describe_unknown_job_returns_actual_known_jobs(self):
        """PR 2.1's generalized unknown-job error surfaces the actual
        registry contents for the new employee too."""
        result = _call_describe(
            {
                "action": "describe",
                "employee": "chief_of_staff",
                "job": "not-a-real-job",
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["known_jobs"], ["morning_brief"])

    def test_describe_rigby_still_returns_docs_manager(self):
        """Existing Rigby describe surface unchanged after PR 3.1."""
        result = _call_describe(
            {"action": "describe", "employee": "rigby"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["key"], "docs_manager")

    def test_describe_platform_auditor_still_returns_platform_audit(self):
        """Existing Platform Auditor describe surface unchanged."""
        result = _call_describe(
            {"action": "describe", "employee": "platform_auditor"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["key"], "platform_audit")


# ═════════════════════════════════════════════════════════════════════
# Authority boundary — Chris's read-only-synthesis directive
# ═════════════════════════════════════════════════════════════════════


class ChiefOfStaffAuthorityBoundaryTests(SimpleTestCase):
    """PR 3.1 directive: v0 is read-only synthesis + Deliverable
    persistence ONLY. Every category Chris named as PROHIBITED must
    appear as ``AuthorityLevel.PROHIBITED`` in the contract."""

    REQUIRED_PROHIBITED_KEYS = (
        "send_emails_externally",
        "send_external_messages",
        "modify_source_documents",
        "change_schedules",
        "approve_decisions",
        "execute_business_actions",
        "post_publicly",
        "edit_financial_records",
        "create_or_modify_users",
        "create_or_modify_accounts",
        "modify_platform_settings",
        "open_pull_request",
    )

    REQUIRED_OBSERVE_KEYS = (
        "read_platform_readiness_telemetry",
        "read_build_focus_delta",
        "read_competitive_landscape_snapshot",
        "read_rotating_market_signals",
        "read_governance_state",
        "read_recent_action_items",
    )

    REQUIRED_EXECUTE_KEYS = (
        "resolve_rotation_slot",
        "synthesize_decision_card",
        "synthesize_strategic_brief",
        "save_brief_to_deliverable",
        "certify_mission_run",
    )

    REQUIRED_RECOMMEND_KEYS = (
        "recommend_daily_priorities",
        "recommend_remediations",
    )

    def test_all_chris_directive_prohibitions_present(self):
        authority = MORNING_BRIEF_JOB.authority
        for key in self.REQUIRED_PROHIBITED_KEYS:
            self.assertEqual(
                authority.get(key),
                AuthorityLevel.PROHIBITED.value,
                f"authority[{key!r}] must be PROHIBITED per PR 3.1 "
                f"directive; got {authority.get(key)!r}",
            )

    def test_read_only_lane_authorities_are_observe(self):
        authority = MORNING_BRIEF_JOB.authority
        for key in self.REQUIRED_OBSERVE_KEYS:
            self.assertEqual(
                authority.get(key),
                AuthorityLevel.OBSERVE.value,
                f"authority[{key!r}] should be OBSERVE; got "
                f"{authority.get(key)!r}",
            )

    def test_synthesis_authorities_are_execute(self):
        authority = MORNING_BRIEF_JOB.authority
        for key in self.REQUIRED_EXECUTE_KEYS:
            self.assertEqual(
                authority.get(key),
                AuthorityLevel.EXECUTE.value,
                f"authority[{key!r}] should be EXECUTE; got "
                f"{authority.get(key)!r}",
            )

    def test_priority_recommendations_are_recommend_only(self):
        authority = MORNING_BRIEF_JOB.authority
        for key in self.REQUIRED_RECOMMEND_KEYS:
            self.assertEqual(
                authority.get(key),
                AuthorityLevel.RECOMMEND.value,
                f"authority[{key!r}] should be RECOMMEND; got "
                f"{authority.get(key)!r}",
            )

    def test_no_write_actions_are_execute(self):
        """Defensive: any action whose key implies write semantics
        must NOT be EXECUTE level."""
        authority = MORNING_BRIEF_JOB.authority
        for key, level in authority.items():
            if level == AuthorityLevel.EXECUTE.value:
                self.assertNotIn(
                    "send_", key,
                    f"EXECUTE authority for {key!r} contradicts the "
                    "no-send PR 3.1 directive"
                )
                self.assertNotIn(
                    "modify_", key,
                    f"EXECUTE authority for {key!r} contradicts the "
                    "no-modify PR 3.1 directive"
                )
                self.assertNotIn(
                    "approve_", key,
                    f"EXECUTE authority for {key!r} contradicts the "
                    "no-approve PR 3.1 directive"
                )

    def test_prohibited_actions_tuple_aligned_with_authority(self):
        """The prohibited_actions tuple should describe the same
        denials encoded in authority PROHIBITED entries."""
        prohibited_text = "\n".join(
            MORNING_BRIEF_JOB.prohibited_actions
        ).lower()
        for fragment in (
            "send emails",
            "send",
            "modify source documentation",
            "change schedules",
            "approve decisions",
            "execute business actions",
            "post publicly",
            "edit financial records",
            "create or modify user",
        ):
            self.assertIn(
                fragment, prohibited_text,
                f"prohibited_actions missing reference to {fragment!r}",
            )


# ═════════════════════════════════════════════════════════════════════
# JobContract shape — frozen + required_summary_keys + evidence_tables
# ═════════════════════════════════════════════════════════════════════


class MorningBriefJobContractShapeTests(SimpleTestCase):

    def test_contract_is_frozen(self):
        with self.assertRaises(Exception):
            MORNING_BRIEF_JOB.mission = "different"  # type: ignore

    def test_contract_identity_fields(self):
        self.assertEqual(MORNING_BRIEF_JOB.title, "Daily Morning Brief")
        self.assertEqual(
            MORNING_BRIEF_JOB.employee_handle, "chief_of_staff"
        )
        self.assertEqual(MORNING_BRIEF_JOB.manager, "chris")
        self.assertEqual(
            MORNING_BRIEF_JOB.mission_run_kind, "morning_brief"
        )

    def test_required_summary_keys_cover_evidence(self):
        keys = set(MORNING_BRIEF_JOB.required_summary_keys)
        for k in (
            "rotation_slot",
            "lane_4_slot_used",
            "lanes_completed_count",
            "decision_count",
            "decision_card_chars",
            "deliverable_id",
            "workspace_id",
            "brief_chars",
            "wall_time_ms",
            "failed_step",
            "error_tail",
            "degraded_evidence",
        ):
            self.assertIn(k, keys, f"missing required_summary_key {k!r}")

    def test_evidence_tables_name_morning_brief_run_kind(self):
        evidence = MORNING_BRIEF_JOB.evidence_tables
        self.assertTrue(
            any("run_kind=morning_brief" in e for e in evidence),
            f"evidence_tables missing run_kind=morning_brief: {evidence}",
        )
        self.assertTrue(
            any("Morning Brief" in e for e in evidence),
            f"evidence_tables missing 'Morning Brief' workspace ref: "
            f"{evidence}",
        )

    def test_daily_routine_has_eight_lane_steps_plus_verdict(self):
        """The morning_brief workflow has 8 steps + verdict emission."""
        routine = MORNING_BRIEF_JOB.daily_routine
        self.assertEqual(len(routine), 9)
        # Spot-check the step labels for stability.
        joined = " ".join(routine).lower()
        for label in (
            "rotation_slot_resolve",
            "lane_1_platform_readiness",
            "lane_2_build_focus",
            "lane_3_competitive_landscape",
            "lane_4_rotating_focus",
            "decision_card_synthesis",
            "strategic_synthesis",
            "create_deliverable",
            "mission_verdict",
        ):
            self.assertIn(label, joined)

    def test_weekly_routine_is_empty(self):
        """morning_brief is a daily job, not a weekly one."""
        self.assertEqual(MORNING_BRIEF_JOB.weekly_routine, ())

    def test_mission_text_mentions_read_only(self):
        self.assertIn("read-only", MORNING_BRIEF_JOB.mission.lower())


# ═════════════════════════════════════════════════════════════════════
# Contract — no MissionRunner changes in PR 3.1
# ═════════════════════════════════════════════════════════════════════


class NoMissionRunnerChangesTests(SimpleTestCase):
    """PR 3.1 must not touch ``core/employees/mission_runner.py``
    semantics. AST scan asserts MissionRunner does not import any
    employee-specific symbol (including the new Chief of Staff constants).
    """

    @classmethod
    def _load_module_ast(cls):
        source = MISSION_RUNNER_PATH.read_text()
        return ast.parse(source, filename=str(MISSION_RUNNER_PATH))

    def test_mission_runner_does_not_import_chief_of_staff(self):
        tree = self._load_module_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    self.assertNotIn(
                        alias.name,
                        {
                            "CHIEF_OF_STAFF",
                            "MORNING_BRIEF_JOB",
                            "PLATFORM_AUDITOR",
                            "PLATFORM_AUDIT_JOB",
                            "RIGBY",
                            "DOCUMENTATION_MANAGER",
                        },
                        f"MissionRunner illegally imports {alias.name!r}",
                    )

    def test_mission_runner_does_not_reference_chief_of_staff(self):
        tree = self._load_module_ast()
        forbidden = {
            "CHIEF_OF_STAFF",
            "MORNING_BRIEF_JOB",
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
# Contract — production caller count is exactly 3 after PR 3.2.
# Session 1257 PR 3.2 promotes MissionRunner from 2 → 3 production
# callers (docs_manager + platform_audit + chief_of_staff).
# Pre-PR-3.2 wording of this test class asserted "stays exactly 2"
# and "no chief_of_staff factory exists"; flipped here per the PR 3.2
# contract (test_chief_of_staff_routine.ThreeProductionCallersTests is
# the canonical assertion now — this class kept as the PR 3.1 baseline
# guardrail, updated to the new ground truth).
# ═════════════════════════════════════════════════════════════════════


class ProductionCallerCountUnchangedTests(SimpleTestCase):
    """Post-PR-3.2 production caller contract.

    MissionRunner caller set must contain exactly Documentation Manager
    + Platform Auditor + Chief of Staff. Adds or removes from this
    surface must update both this baseline class and
    ``test_chief_of_staff_routine.ThreeProductionCallersTests``.
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
            "Post-PR-3.2 production caller set must be exactly "
            "{docs_manager, platform_audit, morning_brief}; "
            f"observed call sites: {sorted(callers)}",
        )

    def test_chief_of_staff_runner_factory_exists(self):
        """PR 3.2 ships the build_chief_of_staff_runner factory in
        core/jobs/morning_brief.py."""
        from core.jobs.morning_brief import build_chief_of_staff_runner

        # Importable + callable.
        self.assertTrue(callable(build_chief_of_staff_runner))

    def test_chief_of_staff_celery_task_exists(self):
        """PR 3.2 ships chief_of_staff_morning_brief_run in
        core/tasks_chief_of_staff.py."""
        repo_root = Path(__file__).resolve().parents[2]
        tasks_file = repo_root / "core" / "tasks_chief_of_staff.py"
        self.assertTrue(
            tasks_file.exists(),
            "core/tasks_chief_of_staff.py missing — PR 3.2 ships the "
            "Celery task module.",
        )
        # And the task name itself is registered.
        from core.celery import app
        import core.tasks_chief_of_staff  # noqa: F401
        self.assertIn(
            "chief_of_staff_morning_brief_run", app.tasks,
        )
