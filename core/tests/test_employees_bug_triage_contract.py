"""Session 1267 PR 4.1 — Bug Triage Specialist employee registration tests.

Proves that the fourth AI employee (Bug Triage Specialist) appears in
the registry and that ``employee_tool action=describe`` surfaces both
the employee profile and the ``triage_daily`` JobContract.

Scope discipline (per PR 4.1):
- No task runner is implemented yet; this PR is contract/registry only.
- No MissionRunner changes; an AST contract test asserts that no
  employee-specific symbols leaked into MissionRunner.
- Existing Rigby / Documentation Manager + Platform Auditor + Chief of
  Staff behavior unchanged — registry + describe surface for each is
  asserted explicitly.

Rigby SIGN-clean design locks asserted at the contract level:
- D1: NO ``mission_verdict`` step in ``daily_routine`` (v0 does not
  auto-certify; certification stays with Rigby/human).
- D2: Authority table has exactly 17 entries
  (4 OBSERVE + 3 EXECUTE + 1 RECOMMEND + 9 PROHIBITED).
- D5: bounded summary keys — ``error_tail_preview`` +
  ``has_full_error_tail`` present; raw ``error_tail`` absent.
- D7: ``evidence_tables`` includes ``LLMCallEvent`` +
  ``CeleryTaskEvent``; no ``FailureDetection`` reference.
- D8: ``dedupe_rule`` names ``MissionRunner.make_error_signature``
  + explicit 24h window.

Run::

    .venv/bin/python manage.py test core.tests.test_employees_bug_triage_contract -v2
"""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

from django.test import SimpleTestCase

from core.employees import (
    AIEmployee,
    AuthorityLevel,
    BUG_TRIAGE_JOB,
    BUG_TRIAGE_SPECIALIST,
    CHIEF_OF_STAFF,
    DOCUMENTATION_MANAGER,
    JobContract,
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
    """Invoke ``_handle_employee_tool`` on a bare mixin instance."""
    handler = EmployeeHandlersMixin()
    return handler._handle_employee_tool(
        tool_name="employee_tool",
        payload=payload,
        user_id=None,
        trace_id="test-trace-id",
    )


# ═════════════════════════════════════════════════════════════════════
# Module surface — constants importable
# ═════════════════════════════════════════════════════════════════════


class BugTriageSurfaceTests(SimpleTestCase):
    """Sanity: ``from core.employees import BUG_TRIAGE_*`` works."""

    def test_employee_constant_importable(self):
        self.assertIsInstance(BUG_TRIAGE_SPECIALIST, AIEmployee)

    def test_job_constant_importable(self):
        self.assertIsInstance(BUG_TRIAGE_JOB, JobContract)

    def test_constants_are_frozen(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            BUG_TRIAGE_SPECIALIST.handle = "mutated"  # type: ignore[misc]
        with self.assertRaises(dataclasses.FrozenInstanceError):
            BUG_TRIAGE_JOB.title = "mutated"  # type: ignore[misc]

    def test_employee_identity_fields(self):
        self.assertEqual(BUG_TRIAGE_SPECIALIST.handle, "bug_triage_specialist")
        self.assertEqual(
            BUG_TRIAGE_SPECIALIST.display_name, "Bug Triage Specialist"
        )
        # Honest v0: acts as ``chris`` server-side (matches RIGBY / PA / CoS).
        self.assertEqual(BUG_TRIAGE_SPECIALIST.runs_as_username, "chris")
        # No pinned PA chat — visibility via Deliverable + shift-report DM.
        self.assertIsNone(BUG_TRIAGE_SPECIALIST.primary_chat_id)


# ═════════════════════════════════════════════════════════════════════
# Registry — Bug Triage exists alongside the other three employees
# ═════════════════════════════════════════════════════════════════════


class BugTriageRegistryTests(SimpleTestCase):

    def test_bug_triage_specialist_appears_in_list_employees(self):
        handles = {e.handle for e in list_employees()}
        self.assertIn("bug_triage_specialist", handles)
        # Existing three still present.
        self.assertIn("rigby", handles)
        self.assertIn("platform_auditor", handles)
        self.assertIn("chief_of_staff", handles)

    def test_list_employees_has_four_entries(self):
        # Bug Triage is Employee #4; registry must have exactly four.
        self.assertEqual(len(list_employees()), 4)

    def test_get_employee_resolves_bug_triage(self):
        self.assertIs(
            get_employee("bug_triage_specialist"), BUG_TRIAGE_SPECIALIST
        )

    def test_get_employee_case_insensitive(self):
        self.assertIs(
            get_employee("Bug_Triage_Specialist"), BUG_TRIAGE_SPECIALIST
        )
        self.assertIs(
            get_employee("BUG_TRIAGE_SPECIALIST"), BUG_TRIAGE_SPECIALIST
        )

    def test_get_job_resolves_triage_daily(self):
        self.assertIs(
            get_job("bug_triage_specialist", "triage_daily"),
            BUG_TRIAGE_JOB,
        )

    def test_get_job_case_insensitive(self):
        self.assertIs(
            get_job("Bug_Triage_Specialist", "Triage_Daily"),
            BUG_TRIAGE_JOB,
        )

    def test_list_jobs_for_employee_returns_triage_daily(self):
        jobs = list_jobs_for_employee("bug_triage_specialist")
        self.assertEqual(len(jobs), 1)
        self.assertIs(jobs[0], BUG_TRIAGE_JOB)

    def test_list_jobs_with_keys_returns_triage_daily(self):
        # Verification gate V1 from S1266 handoff.
        items = list_jobs_with_keys("bug_triage_specialist")
        self.assertEqual(len(items), 1)
        key, contract = items[0]
        self.assertEqual(key, "triage_daily")
        self.assertIs(contract, BUG_TRIAGE_JOB)

    def test_list_job_keys_for_employee_returns_triage_daily(self):
        self.assertEqual(
            list_job_keys_for_employee("bug_triage_specialist"),
            ["triage_daily"],
        )

    def test_unknown_job_returns_none(self):
        self.assertIsNone(
            get_job("bug_triage_specialist", "not-a-job")
        )


# ═════════════════════════════════════════════════════════════════════
# Registry — existing three employees unchanged
# ═════════════════════════════════════════════════════════════════════


class ExistingEmployeesUnchangedTests(SimpleTestCase):
    """Adding Employee #4 must not break Employees #1-#3."""

    def test_rigby_still_resolves(self):
        self.assertIs(get_employee("rigby"), RIGBY)
        self.assertIs(get_job("rigby", "docs_manager"), DOCUMENTATION_MANAGER)
        self.assertEqual(
            list_job_keys_for_employee("rigby"), ["docs_manager"]
        )

    def test_platform_auditor_still_resolves(self):
        self.assertIs(get_employee("platform_auditor"), PLATFORM_AUDITOR)
        self.assertIs(
            get_job("platform_auditor", "platform_audit"), PLATFORM_AUDIT_JOB
        )
        self.assertEqual(
            list_job_keys_for_employee("platform_auditor"),
            ["platform_audit"],
        )

    def test_chief_of_staff_still_resolves(self):
        self.assertIs(get_employee("chief_of_staff"), CHIEF_OF_STAFF)
        self.assertIs(
            get_job("chief_of_staff", "morning_brief"), MORNING_BRIEF_JOB
        )
        self.assertEqual(
            list_job_keys_for_employee("chief_of_staff"),
            ["morning_brief"],
        )


# ═════════════════════════════════════════════════════════════════════
# Contract shape — Rigby SIGN-clean design locks
# ═════════════════════════════════════════════════════════════════════


class BugTriageContractShapeTests(SimpleTestCase):
    """Asserts the locked design decisions from Rigby SIGN at S1266.

    Each assertion has a comment naming the decision it locks in so
    future edits land aware of the contract.
    """

    def test_mission_run_kind_is_bug_triage_daily(self):
        # Locks the OpsRun.run_kind value the PR 4.2 task runner uses.
        self.assertEqual(BUG_TRIAGE_JOB.mission_run_kind, "bug_triage_daily")

    def test_employee_handle_matches_specialist(self):
        self.assertEqual(
            BUG_TRIAGE_JOB.employee_handle,
            BUG_TRIAGE_SPECIALIST.handle,
        )

    def test_manager_is_chris(self):
        self.assertEqual(BUG_TRIAGE_JOB.manager, "chris")

    def test_daily_routine_has_seven_steps(self):
        self.assertEqual(len(BUG_TRIAGE_JOB.daily_routine), 7)

    def test_weekly_routine_is_empty_daily_only_v0(self):
        # Bug Triage is daily-only in v0; weekly is explicit empty.
        self.assertEqual(BUG_TRIAGE_JOB.weekly_routine, ())

    def test_d1_no_emit_mission_verdict_step(self):
        """Rigby SIGN D1: v0 does NOT auto-certify.

        PA + CoS daily_routines both end with a step phrased
        "Step N — emit verdict via mission_verdict." (PA: step 6;
        CoS: step 9). Bug Triage's last step is "Step 7 — record
        run summary + mark OpsRun.status=passed/failed. NO
        auto-certification in v0" — the verdict-emission action is
        explicitly absent. Certification stays with Rigby/human
        review of the daily Deliverable.

        Note: the word "mission_verdict" still appears in Bug
        Triage's routine — in Step 3's *read* of other employees'
        verdicts (``collect_mission_verdicts``) and in Step 7's
        own no-auto-cert disclaimer. Both are correct; the lock is
        on the *emit verdict* action.
        """
        # No step is phrased as the verdict-emission action.
        joined = " ".join(BUG_TRIAGE_JOB.daily_routine).lower()
        self.assertNotIn("emit verdict via mission_verdict", joined)
        # Last step instead marks status only.
        last_step = BUG_TRIAGE_JOB.daily_routine[-1].lower()
        self.assertIn("opsrun.status=passed/failed", last_step)
        self.assertIn("no auto-certification", last_step)
        # Step 7's text + the employee notes name the no-auto-cert
        # constraint explicitly so a future reader sees the policy
        # without inferring it from the absence of "emit verdict".
        self.assertIn(
            "left to rigby/human review", last_step,
        )
        self.assertIn(
            "v0 does not auto-certify",
            BUG_TRIAGE_SPECIALIST.notes.lower(),
        )
        # Bug Triage's "what_rigby_can_do_alone" hands the
        # mission_verdict authority back to Rigby (matches the PA
        # tool gate that keeps mission_verdict on a speaker=Rigby
        # path, not a server-side call).
        rigby_capabilities = " ".join(
            BUG_TRIAGE_JOB.what_rigby_can_do_alone
        ).lower()
        self.assertIn("mission_verdict", rigby_capabilities)

    def test_d2_authority_table_has_seventeen_entries(self):
        """Rigby SIGN D2: 17 = 4 OBSERVE + 3 EXECUTE + 1 RECOMMEND
        + 9 PROHIBITED. The earlier buggy 16-claim was recounted to
        17 in the SIGN-clean discovery package."""
        self.assertEqual(len(BUG_TRIAGE_JOB.authority), 17)

        by_level = {lvl.value: 0 for lvl in AuthorityLevel}
        for value in BUG_TRIAGE_JOB.authority.values():
            by_level[value] += 1

        self.assertEqual(by_level[AuthorityLevel.OBSERVE.value], 4)
        self.assertEqual(by_level[AuthorityLevel.EXECUTE.value], 3)
        self.assertEqual(by_level[AuthorityLevel.RECOMMEND.value], 1)
        self.assertEqual(by_level[AuthorityLevel.PROHIBITED.value], 9)

    def test_authority_prohibits_remediation_pathways(self):
        # Every remediation pathway must be PROHIBITED.
        for action in (
            "modify_any_file",
            "open_pull_request",
            "restart_worker",
            "dispatch_other_employee_mission",
            "delete_database_rows",
            "execute_arbitrary_code",
            "kill_celery_task",
            "modify_periodic_task_enabled",
            "modify_settings",
        ):
            self.assertEqual(
                BUG_TRIAGE_JOB.authority[action],
                AuthorityLevel.PROHIBITED.value,
                f"{action!r} should be PROHIBITED",
            )

    def test_authority_grants_read_only_observe(self):
        # All four telemetry reads are OBSERVE.
        for action in (
            "read_celery_task_events",
            "read_agent_executions",
            "read_ops_runs",
            "read_ops_run_events",
        ):
            self.assertEqual(
                BUG_TRIAGE_JOB.authority[action],
                AuthorityLevel.OBSERVE.value,
                f"{action!r} should be OBSERVE",
            )

    def test_d5_summary_keys_use_bounded_error_tail(self):
        """Rigby SIGN D5: never persist the full ``error_tail`` into
        ``summary``. Use ``error_tail_preview`` (last N lines) +
        ``has_full_error_tail`` (bool); full tail lives in
        ``OpsRunEvent.detail``."""
        keys = set(BUG_TRIAGE_JOB.required_summary_keys)
        self.assertIn("error_tail_preview", keys)
        self.assertIn("has_full_error_tail", keys)
        self.assertNotIn("error_tail", keys)

    def test_required_summary_keys_include_window_shape(self):
        keys = set(BUG_TRIAGE_JOB.required_summary_keys)
        for k in (
            "window_start_iso",
            "window_end_iso",
            "celery_failures_count",
            "agent_failures_count",
            "missions_today_total",
            "authority_events_count",
            "authority_events_by_employee",
            "cluster_count",
            "top_cluster_signature",
            "top_cluster_occurrences",
            "report_deliverable_id",
            "report_chars",
            "recommendations_count",
            "wall_time_ms",
            "failed_step",
            "degraded_evidence",
        ):
            self.assertIn(k, keys, f"required_summary_keys missing {k!r}")

    def test_d7_evidence_tables_include_llm_and_celery_no_failure_detection(
        self,
    ):
        """Rigby SIGN D7: evidence_tables must include LLMCallEvent +
        CeleryTaskEvent; no FailureDetection reference."""
        evidence_joined = " ".join(BUG_TRIAGE_JOB.evidence_tables)
        self.assertIn("LLMCallEvent", evidence_joined)
        self.assertIn("CeleryTaskEvent", evidence_joined)
        # FailureDetection is the rejected sibling — must not be cited.
        self.assertNotIn("FailureDetection", evidence_joined)
        # OpsRun pinned to bug_triage_daily run_kind.
        self.assertTrue(
            any("run_kind=bug_triage_daily" in e
                for e in BUG_TRIAGE_JOB.evidence_tables),
            f"evidence_tables missing run_kind=bug_triage_daily: "
            f"{BUG_TRIAGE_JOB.evidence_tables}",
        )

    def test_d8_dedupe_rule_names_canonical_signature_and_24h_window(self):
        """Rigby SIGN D8: dedupe MUST reference
        ``MissionRunner.make_error_signature`` and an explicit 24h
        window. Matches PA + CoS dedupe conventions."""
        rule = BUG_TRIAGE_JOB.dedupe_rule
        self.assertIn("MissionRunner.make_error_signature", rule)
        self.assertIn("24h", rule)

    def test_escalation_visibility_mentions_donkey_betz_workspace(self):
        # Workspace pin from EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME.
        joined = " ".join(BUG_TRIAGE_JOB.escalation_visibility)
        self.assertIn("Donkey Betz", joined)

    def test_escalation_visibility_no_pa_chat_post_for_v0(self):
        # No pinned PA chat → escalations surface via shift-report DM,
        # not via a chat post.
        joined = " ".join(BUG_TRIAGE_JOB.escalation_visibility).lower()
        self.assertIn("no pa chat post", joined)
        self.assertIn("shift-report dm", joined)

    def test_summary_field_for_error_signature_default_inherited(self):
        # Inherits the dataclass default; PR 4.2 dedupe code reads
        # this single source of truth.
        self.assertEqual(
            BUG_TRIAGE_JOB.summary_field_for_error_signature,
            "error_signature",
        )


# ═════════════════════════════════════════════════════════════════════
# describe handler surfaces Bug Triage Specialist
# ═════════════════════════════════════════════════════════════════════


class BugTriageDescribeHandlerTests(SimpleTestCase):

    def test_describe_bug_triage_no_job_arg(self):
        result = _call_describe(
            {"action": "describe", "employee": "bug_triage_specialist"}
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "describe")
        self.assertEqual(
            result["employee"]["handle"], "bug_triage_specialist"
        )
        self.assertEqual(
            result["employee"]["display_name"], "Bug Triage Specialist"
        )
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(len(result["jobs"]), 1)
        self.assertEqual(result["jobs"][0]["key"], "triage_daily")

    def test_describe_bug_triage_with_job_arg(self):
        result = _call_describe(
            {
                "action": "describe",
                "employee": "bug_triage_specialist",
                "job": "triage_daily",
            }
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["key"], "triage_daily")
        contract = result["jobs"][0]["contract"]
        self.assertEqual(contract["title"], "Daily Bug Triage")
        self.assertEqual(contract["mission_run_kind"], "bug_triage_daily")

    def test_describe_bug_triage_employee_block(self):
        result = _call_describe(
            {"action": "describe", "employee": "bug_triage_specialist"}
        )
        emp = result["employee"]
        self.assertEqual(emp["handle"], "bug_triage_specialist")
        self.assertEqual(emp["display_name"], "Bug Triage Specialist")
        self.assertEqual(emp["runs_as_username"], "chris")
        self.assertIsNone(emp["primary_chat_id"])

    def test_describe_bug_triage_contract_surface(self):
        """Spot-check key contract fields surface correctly."""
        result = _call_describe(
            {"action": "describe", "employee": "bug_triage_specialist"}
        )
        contract = result["jobs"][0]["contract"]

        # Mission text mentions read-only intent.
        self.assertIn("read-only", contract["mission"].lower())

        # Authority dict has the read-only OBSERVE set + the
        # prohibited remediation set.
        authority = contract["authority"]
        self.assertEqual(
            authority["read_celery_task_events"],
            AuthorityLevel.OBSERVE.value,
        )
        self.assertEqual(
            authority["save_triage_to_deliverable"],
            AuthorityLevel.EXECUTE.value,
        )
        self.assertEqual(
            authority["modify_any_file"],
            AuthorityLevel.PROHIBITED.value,
        )
        self.assertEqual(
            authority["dispatch_other_employee_mission"],
            AuthorityLevel.PROHIBITED.value,
        )

        # required_summary_keys carries the Bug Triage evidence
        # contract — D5 bounded summary uses preview + flag.
        keys = set(contract["required_summary_keys"])
        for k in (
            "cluster_count",
            "top_cluster_signature",
            "top_cluster_occurrences",
            "report_deliverable_id",
            "error_tail_preview",
            "has_full_error_tail",
        ):
            self.assertIn(k, keys, f"required_summary_keys missing {k!r}")
        # D5 negative: raw error_tail must NOT be in the summary
        # contract for Bug Triage (PA + CoS still use error_tail; the
        # change is Bug-Triage-specific).
        self.assertNotIn("error_tail", keys)

        # Evidence tables include the bug_triage_daily OpsRun key.
        evidence = contract["evidence_tables"]
        self.assertTrue(
            any("run_kind=bug_triage_daily" in e for e in evidence),
            f"evidence_tables missing run_kind=bug_triage_daily: {evidence}",
        )

    def test_describe_unknown_job_lists_triage_daily(self):
        """The generalized unknown-job error surfaces ``triage_daily``."""
        result = _call_describe(
            {
                "action": "describe",
                "employee": "bug_triage_specialist",
                "job": "not-a-real-job",
            }
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["known_jobs"], ["triage_daily"])

    def test_describe_existing_employees_unchanged(self):
        """Describe surface for each prior employee is intact."""
        for handle, expected_job_key in (
            ("rigby", "docs_manager"),
            ("platform_auditor", "platform_audit"),
            ("chief_of_staff", "morning_brief"),
        ):
            with self.subTest(employee=handle):
                result = _call_describe(
                    {"action": "describe", "employee": handle}
                )
                self.assertTrue(result["ok"])
                self.assertEqual(result["job_count"], 1)
                self.assertEqual(result["jobs"][0]["key"], expected_job_key)


# ═════════════════════════════════════════════════════════════════════
# Contract — no MissionRunner changes in PR 4.1
# ═════════════════════════════════════════════════════════════════════


class NoMissionRunnerChangesTests(SimpleTestCase):
    """PR 4.1 must not touch ``core/employees/mission_runner.py``
    semantics. AST scan asserts MissionRunner does not import any
    Bug-Triage-specific symbol.
    """

    @classmethod
    def _load_module_ast(cls):
        source = MISSION_RUNNER_PATH.read_text()
        return ast.parse(source, filename=str(MISSION_RUNNER_PATH))

    def test_mission_runner_does_not_import_bug_triage_constants(self):
        tree = self._load_module_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    self.assertNotIn(
                        alias.name,
                        ("BUG_TRIAGE_SPECIALIST", "BUG_TRIAGE_JOB"),
                        f"MissionRunner must not import "
                        f"{alias.name!r} — keep mission runner "
                        f"employee-agnostic.",
                    )
