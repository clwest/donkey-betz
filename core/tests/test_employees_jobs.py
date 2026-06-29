"""
Tests for the Session 1252 PR 1 AI Employee framework — jobs module.

Covers:
- module imports cleanly (RIGBY + DOCUMENTATION_MANAGER constants)
- frozen dataclasses are actually frozen
- DOCUMENTATION_MANAGER reflects Rigby's six contract edits:
    1. Best-effort sync wording in mission
    2. Required summary stats schema
    3. drift_count definition
    4. Step 4 timeout requirement (warning + hard thresholds)
    5. Escalation visibility guarantee (publish_candidate + status flip + PA post)
    6. Failure-signature dedupe rule
- Registry helpers (list_employees / get_employee / list_jobs_for_employee / get_job)
- AuthorityLevel enum coverage

Run::

    python manage.py test core.tests.test_employees_jobs -v2
"""

from __future__ import annotations

import dataclasses

from django.test import SimpleTestCase, TestCase

from core.employees import (
    AIEmployee,
    AuthorityLevel,
    DOCUMENTATION_MANAGER,
    JobContract,
    RIGBY,
    get_employee,
    get_job,
    list_employees,
    list_jobs_for_employee,
)


# ── Module surface ───────────────────────────────────────────────────


class EmployeeModuleSurfaceTests(SimpleTestCase):
    """Sanity checks: the import contract advertised by __init__ works."""

    def test_constants_importable(self):
        self.assertIsInstance(RIGBY, AIEmployee)
        self.assertIsInstance(DOCUMENTATION_MANAGER, JobContract)

    def test_authority_level_enum_values(self):
        self.assertEqual(AuthorityLevel.OBSERVE.value, "observe")
        self.assertEqual(AuthorityLevel.RECOMMEND.value, "recommend")
        self.assertEqual(AuthorityLevel.EXECUTE.value, "execute")
        self.assertEqual(AuthorityLevel.PROHIBITED.value, "prohibited")

    def test_dataclasses_are_frozen(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):
            RIGBY.handle = "not-rigby"  # type: ignore[misc]
        with self.assertRaises(dataclasses.FrozenInstanceError):
            DOCUMENTATION_MANAGER.title = "Other Title"  # type: ignore[misc]


# ── Rigby employee identity ──────────────────────────────────────────


class RigbyIdentityTests(SimpleTestCase):

    def test_handle_and_display_name(self):
        self.assertEqual(RIGBY.handle, "rigby")
        self.assertEqual(RIGBY.display_name, "Rigby")

    def test_runs_as_username_honest_v0(self):
        # v0 honest design — Rigby acts as `chris` server-side because she
        # has no dedicated User row. Tracked in the discovery report.
        self.assertEqual(RIGBY.runs_as_username, "chris")

    def test_primary_chat_pinned(self):
        self.assertEqual(RIGBY.primary_chat_id, "pa-3901b70e61934df7")


# ── Documentation Manager contract: Rigby's 6 required edits ─────────


class DocumentationManagerContractTests(SimpleTestCase):

    def test_title_and_owner(self):
        self.assertEqual(DOCUMENTATION_MANAGER.title, "Documentation Manager")
        self.assertEqual(DOCUMENTATION_MANAGER.employee_handle, "rigby")
        self.assertEqual(DOCUMENTATION_MANAGER.manager, "chris")

    # ── Rigby edit #1: best-effort sync wording ──────────────────────

    def test_mission_contains_best_effort_wording(self):
        mission = DOCUMENTATION_MANAGER.mission.lower()
        self.assertIn("best-effort", mission)
        self.assertIn("contingent on the cascade commands succeeding", mission)
        # Negative: previous over-strong wording must NOT appear.
        self.assertNotIn(
            "every weekday morning, the docs index", mission
        )

    def test_mission_disclaims_magical_responsibilities(self):
        mission = DOCUMENTATION_MANAGER.mission.lower()
        # Rigby is not on the hook for these failure modes.
        for term in ("schema drift", "db outages", "storage failures"):
            self.assertIn(term, mission, f"missing disclaimer: {term!r}")

    # ── Rigby edit #2: required summary stats schema ─────────────────

    def test_required_summary_keys_complete(self):
        required = set(DOCUMENTATION_MANAGER.required_summary_keys)
        expected = {
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
            "error_tail",
        }
        missing = expected - required
        self.assertFalse(
            missing, f"required_summary_keys missing: {missing}"
        )

    def test_evidence_tables_named(self):
        tables = " ".join(DOCUMENTATION_MANAGER.evidence_tables).lower()
        for needle in (
            "opsrun",
            "opsrunevent",
            "llmcallevent",
            "toolcallrecord",
            "deliverable",
        ):
            self.assertIn(needle, tables, f"missing evidence table: {needle}")

    # ── Rigby edit #3: drift_count definition ────────────────────────

    def test_drift_count_definition_documented(self):
        defn = DOCUMENTATION_MANAGER.drift_count_definition.lower()
        self.assertIn("verify_doc_claims", defn)
        self.assertIn("--only-drift", defn)
        # Must explicitly call out the null-with-degraded-evidence fallback.
        self.assertIn("null with", defn)
        self.assertIn("degraded_evidence", defn)

    # ── Rigby edit #4: Step 4 timeout contract ───────────────────────

    def test_embed_step_timeout_defined(self):
        self.assertEqual(
            DOCUMENTATION_MANAGER.embed_step_timeout["warning_seconds"],
            600,
        )
        self.assertEqual(
            DOCUMENTATION_MANAGER.embed_step_timeout["hard_seconds"],
            1800,
        )

    # ── Rigby edit #5: escalation visibility guarantee ───────────────

    def test_escalation_visibility_includes_three_required_steps(self):
        joined = " ".join(DOCUMENTATION_MANAGER.escalation_visibility).lower()
        self.assertIn("publish_candidate", joined)
        # Status-flip clause must reference the canonical status path.
        self.assertIn("canonical status path", joined)
        # PA chat post requirement must reference the primary_chat_id.
        self.assertIn(RIGBY.primary_chat_id.lower(), joined)

    # ── Rigby edit #6: failure-signature dedupe rule ─────────────────

    def test_dedupe_rule_uses_failure_signature_not_deliverable_status(self):
        rule = DOCUMENTATION_MANAGER.dedupe_rule.lower()
        self.assertIn("failure signature", rule)
        self.assertIn("opsrun", rule)
        self.assertIn("not deliverable status", rule)
        # 24h window must be present.
        self.assertIn("24h", rule)


class DocumentationManagerAuthorityTests(SimpleTestCase):
    """Authority assignments cover both grant + prohibit directions."""

    def test_execute_actions_present(self):
        auth = DOCUMENTATION_MANAGER.authority
        self.assertEqual(
            auth["run_docs_cascade_commands"], AuthorityLevel.EXECUTE.value
        )
        self.assertEqual(
            auth["certify_mission_run"], AuthorityLevel.EXECUTE.value
        )
        self.assertEqual(
            auth["post_escalation_to_pa_chat"], AuthorityLevel.EXECUTE.value
        )

    def test_prohibited_actions_present(self):
        auth = DOCUMENTATION_MANAGER.authority
        for prohibited in (
            "modify_docs_files",
            "open_pull_request",
            "delete_document_rows",
            "delete_document_embedding_rows",
        ):
            self.assertEqual(
                auth[prohibited],
                AuthorityLevel.PROHIBITED.value,
                f"{prohibited} should be prohibited",
            )

    def test_observe_and_recommend_present(self):
        auth = DOCUMENTATION_MANAGER.authority
        self.assertEqual(
            auth["run_drift_observation"], AuthorityLevel.OBSERVE.value
        )
        self.assertEqual(
            auth["broken_link_sweep"], AuthorityLevel.RECOMMEND.value
        )


class DocumentationManagerBoundaryTests(SimpleTestCase):
    """Each boundary statement (Chris / Claude / Rigby) is non-empty."""

    def test_what_chris_approves_non_empty(self):
        self.assertGreater(len(DOCUMENTATION_MANAGER.what_chris_approves), 0)

    def test_what_claude_handles_non_empty(self):
        self.assertGreater(len(DOCUMENTATION_MANAGER.what_claude_handles), 0)

    def test_what_rigby_can_do_alone_non_empty(self):
        self.assertGreater(
            len(DOCUMENTATION_MANAGER.what_rigby_can_do_alone), 0
        )

    def test_mission_run_kind_is_docs_cascade(self):
        # PR 2 will write OpsRun rows with this run_kind; lock it now.
        self.assertEqual(
            DOCUMENTATION_MANAGER.mission_run_kind, "docs_cascade"
        )


# ── Registry helpers ─────────────────────────────────────────────────


class RegistryHelperTests(SimpleTestCase):

    def test_list_employees_contains_rigby(self):
        """Rigby remains the first registered employee.

        Session 1257 PR 2.1: PLATFORM_AUDITOR joined the registry.
        Test broadened from "has one employee" to "contains rigby" so
        it stays correct as the registry grows.
        """
        employees = list_employees()
        handles = {e.handle for e in employees}
        self.assertIn("rigby", handles)
        self.assertGreaterEqual(len(employees), 1)

    def test_get_employee_known(self):
        self.assertIs(get_employee("rigby"), RIGBY)

    def test_get_employee_case_insensitive(self):
        self.assertIs(get_employee("RIGBY"), RIGBY)
        self.assertIs(get_employee("Rigby"), RIGBY)

    def test_get_employee_unknown_returns_none(self):
        self.assertIsNone(get_employee("not-an-employee"))
        self.assertIsNone(get_employee(""))

    def test_list_jobs_for_employee_has_one_job(self):
        jobs = list_jobs_for_employee("rigby")
        self.assertEqual(len(jobs), 1)
        self.assertIs(jobs[0], DOCUMENTATION_MANAGER)

    def test_list_jobs_for_unknown_employee_empty(self):
        self.assertEqual(list_jobs_for_employee("not-an-employee"), [])
        self.assertEqual(list_jobs_for_employee(""), [])

    def test_get_job_known(self):
        self.assertIs(
            get_job("rigby", "docs_manager"), DOCUMENTATION_MANAGER
        )

    def test_get_job_case_insensitive(self):
        self.assertIs(
            get_job("RIGBY", "DOCS_MANAGER"), DOCUMENTATION_MANAGER
        )

    def test_get_job_unknown(self):
        self.assertIsNone(get_job("rigby", "not-a-job"))
        self.assertIsNone(get_job("rigby", ""))
        self.assertIsNone(get_job("", "docs_manager"))
