"""Session 1264 — MissionRunner authority warn-mode tests.

Locks in the smallest honest implementation: a single
``authority_contract_observed`` OpsRunEvent emitted per mission right
after ``run_started``, capturing contract SHAPE only (counts + version
hash). NOT violation detection — see the S1264 discovery doc and
mission_runner.py module-top comments.

Five contract tests covering Rigby S1264 SIGN-WITH-EDITS guarantees:

1. Event is emitted with the full expected metadata shape (Rigby
   edit #1: explicit metadata contract).
2. Event is emitted exactly ONCE per mission (Rigby edit #2:
   single emission right after run_started).
3. No-op when ``config.job_contract`` is None (legacy callers
   unchanged; Rigby S1264 SIGN edit #3 / backward-compat).
4. Malformed contract shape raises ``_AuthorityContractMalformedError``
   inside the helper; the wrapping ``_run_mission`` logs ERROR + sets
   ``degraded_evidence=True`` but does NOT block the mission (Rigby
   edit #5: hard-fail only on shape, never on policy).
5. All 3 production factories pass their JobContract, so warn-mode
   is live for every existing employee with no additional opt-in.

Real PostgreSQL (per the S1234 memory rule).

Run::

    .venv/bin/python manage.py test \\
        core.tests.test_mission_runner_authority_warn_mode_s1264 \\
        -v 2 --keepdb
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.employees.jobs import (
    DOCUMENTATION_MANAGER,
    MORNING_BRIEF_JOB,
    PLATFORM_AUDIT_JOB,
    AuthorityLevel,
)
from core.employees.mission_runner import (
    AUTHORITY_CONTRACT_OBSERVED_LABEL,
    AUTHORITY_CONTRACT_SCHEMA_VERSION,
    MissionRunner,
    MissionRunnerConfig,
    Step,
    StepResult,
    _AuthorityContractMalformedError,
    _hash_contract_shape,
)


User = get_user_model()


# ═════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════


def _passing_step(name: str = "noop_step") -> Step:
    """Build a trivial Step that always passes."""

    def fn(_mission):
        return StepResult(passed=True, output="ok", duration_ms=0)

    return Step(name=name, fn=fn)


def _build_minimal_runner(
    *, job_contract=None, employee_handle="test-employee"
) -> MissionRunner:
    """Build a MissionRunner with the smallest possible config so the
    test focuses on the warn-mode behavior, not the lifecycle internals.
    """
    config = MissionRunnerConfig(
        employee_handle=employee_handle,
        employee_display_name=employee_handle.title(),
        runs_as_username="chris",
        mission_run_kind="warn_mode_test",
        job_title="warn-mode test",
        job_contract=job_contract,
    )
    return MissionRunner(
        config=config,
        steps=[_passing_step()],
    )


def _events_for(mission) -> List:
    from core.models_ops_runs import OpsRunEvent

    return list(
        OpsRunEvent.objects.filter(run=mission).order_by("created_at")
    )


# ═════════════════════════════════════════════════════════════════════
# §1 — Contract observation event shape
# ═════════════════════════════════════════════════════════════════════


class AuthorityContractEventShapeTests(TestCase):
    """Rigby S1264 SIGN edit #1 — explicit metadata contract."""

    def test_event_carries_expected_metadata_keys(self):
        runner = _build_minimal_runner(job_contract=DOCUMENTATION_MANAGER)
        result = runner.run()
        self.assertTrue(result.ok)

        from core.models_ops_runs import OpsRun, OpsRunEvent

        mission = OpsRun.objects.get(id=result.mission_id)
        event = OpsRunEvent.objects.get(
            run=mission, label=AUTHORITY_CONTRACT_OBSERVED_LABEL,
        )
        detail = event.detail or {}

        # Required keys per Rigby edit #1.
        self.assertEqual(
            detail.get("schema_version"), AUTHORITY_CONTRACT_SCHEMA_VERSION
        )
        self.assertEqual(
            detail.get("employee_handle"), "test-employee"
        )
        self.assertEqual(
            detail.get("contract_title"), DOCUMENTATION_MANAGER.title
        )
        # contract_version_tag is a 16-char hex string (sha256 prefix).
        tag = detail.get("contract_version_tag", "")
        self.assertEqual(len(tag), 16)
        self.assertTrue(all(c in "0123456789abcdef" for c in tag))

        # Counts shape.
        self.assertEqual(
            detail.get("authority_entries_total"),
            len(DOCUMENTATION_MANAGER.authority),
        )
        self.assertEqual(
            detail.get("prohibited_actions_count"),
            len(DOCUMENTATION_MANAGER.prohibited_actions),
        )

        # Level counts cover all 4 AuthorityLevel values.
        level_counts = detail.get("authority_level_counts", {})
        self.assertEqual(
            set(level_counts.keys()),
            {
                AuthorityLevel.EXECUTE.value,
                AuthorityLevel.OBSERVE.value,
                AuthorityLevel.RECOMMEND.value,
                AuthorityLevel.PROHIBITED.value,
            },
        )
        self.assertEqual(
            sum(level_counts.values()),
            len(DOCUMENTATION_MANAGER.authority),
        )

        # Warn-mode label.
        self.assertEqual(detail.get("mode"), "warn")
        self.assertEqual(event.event_type, "info")


# ═════════════════════════════════════════════════════════════════════
# §2 — Emission timing + idempotency
# ═════════════════════════════════════════════════════════════════════


class AuthorityContractEventTimingTests(TestCase):
    """Rigby S1264 SIGN edit #2 — single emission right after run_started."""

    def test_event_emitted_exactly_once_per_mission(self):
        runner = _build_minimal_runner(job_contract=DOCUMENTATION_MANAGER)
        result = runner.run()
        self.assertTrue(result.ok)

        from core.models_ops_runs import OpsRunEvent

        n = OpsRunEvent.objects.filter(
            run_id=result.mission_id,
            label=AUTHORITY_CONTRACT_OBSERVED_LABEL,
        ).count()
        self.assertEqual(n, 1)

    def test_event_emitted_immediately_after_run_started(self):
        runner = _build_minimal_runner(job_contract=DOCUMENTATION_MANAGER)
        result = runner.run()

        from core.models_ops_runs import OpsRun

        mission = OpsRun.objects.get(id=result.mission_id)
        events = _events_for(mission)
        labels = [e.label for e in events]
        # run_started is index 0; authority_contract_observed is next.
        self.assertEqual(labels[0], "run_started")
        self.assertEqual(labels[1], AUTHORITY_CONTRACT_OBSERVED_LABEL)


# ═════════════════════════════════════════════════════════════════════
# §3 — Backward compatibility (job_contract=None is a no-op)
# ═════════════════════════════════════════════════════════════════════


class AuthorityContractBackwardCompatTests(TestCase):
    """Pre-S1264 callers that don't pass job_contract see no behavior change."""

    def test_no_event_emitted_when_contract_is_none(self):
        runner = _build_minimal_runner(job_contract=None)
        result = runner.run()
        self.assertTrue(result.ok)

        from core.models_ops_runs import OpsRunEvent

        n = OpsRunEvent.objects.filter(
            run_id=result.mission_id,
            label=AUTHORITY_CONTRACT_OBSERVED_LABEL,
        ).count()
        self.assertEqual(n, 0)


# ═════════════════════════════════════════════════════════════════════
# §4 — Malformed contract shape (Rigby SIGN edit #5)
# ═════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class _MalformedContract:
    """Mimics JobContract but with a wrong-typed authority field."""

    title: str = "malformed"
    authority: Any = "not a dict"  # SHOULD be dict
    prohibited_actions: tuple = ()


@dataclass(frozen=True)
class _MalformedProhibited:
    title: str = "malformed-prohibited"
    authority: Dict[str, str] = None  # type: ignore
    prohibited_actions: Any = "not a tuple"

    def __post_init__(self):
        object.__setattr__(self, "authority", {})


class AuthorityContractMalformedShapeTests(TestCase):
    """Malformed shape IS signal — log ERROR, mission continues."""

    def test_malformed_authority_field_does_not_block_mission(self):
        runner = _build_minimal_runner(job_contract=_MalformedContract())
        with self.assertLogs(
            "core.employees.mission_runner", level="ERROR"
        ) as cm:
            result = runner.run()
        # Mission STILL completes; warn-mode never blocks.
        self.assertTrue(result.ok)
        # ERROR log recorded.
        joined = " ".join(cm.output)
        self.assertIn("authority contract malformed", joined)
        # degraded_evidence + error reason persisted in summary.
        self.assertTrue(result.summary.get("degraded_evidence"))
        self.assertIn(
            "authority must be dict",
            result.summary.get("authority_contract_error", ""),
        )

    def test_helper_raises_specific_exception_for_dict_violation(self):
        runner = _build_minimal_runner(job_contract=_MalformedContract())
        # Probe the helper directly to confirm the exception type.
        # Build a stub mission row first.
        from core.models_ops_runs import OpsRun

        mission = OpsRun.objects.create(
            title="probe",
            domain="mission",
            run_kind="warn_mode_test",
            run_type="manual",
            status="running",
        )
        with self.assertRaises(_AuthorityContractMalformedError):
            runner._emit_authority_contract_event(mission)

    def test_helper_raises_specific_exception_for_tuple_violation(self):
        runner = _build_minimal_runner(
            job_contract=_MalformedProhibited()
        )
        from core.models_ops_runs import OpsRun

        mission = OpsRun.objects.create(
            title="probe",
            domain="mission",
            run_kind="warn_mode_test",
            run_type="manual",
            status="running",
        )
        with self.assertRaises(_AuthorityContractMalformedError) as ctx:
            runner._emit_authority_contract_event(mission)
        self.assertIn(
            "prohibited_actions must be tuple/list", str(ctx.exception)
        )


# ═════════════════════════════════════════════════════════════════════
# §5 — All 3 production factories opt in
# ═════════════════════════════════════════════════════════════════════


class AllProductionEmployeesOptInTests(TestCase):
    """Rigby S1264 SIGN edit #4 — include factory opt-ins in this PR.

    Without these, warn-mode is dead code and the production employees
    never emit the observation event. Lock in the wiring.
    """

    def test_docs_manager_factory_passes_contract(self):
        from core.jobs.docs_cascade import build_docs_manager_runner

        runner = build_docs_manager_runner()
        self.assertIs(
            runner.config.job_contract, DOCUMENTATION_MANAGER
        )

    def test_platform_audit_factory_passes_contract(self):
        from core.jobs.platform_audit import build_platform_audit_runner

        runner = build_platform_audit_runner()
        self.assertIs(runner.config.job_contract, PLATFORM_AUDIT_JOB)

    def test_chief_of_staff_factory_passes_contract(self):
        from core.jobs.morning_brief import build_chief_of_staff_runner

        runner = build_chief_of_staff_runner()
        self.assertIs(runner.config.job_contract, MORNING_BRIEF_JOB)


# ═════════════════════════════════════════════════════════════════════
# §6 — Contract version tag stability + uniqueness
# ═════════════════════════════════════════════════════════════════════


class ContractVersionTagTests(TestCase):
    """The hash tag groups missions by contract shape across time."""

    def test_hash_stable_across_calls(self):
        h1 = _hash_contract_shape(
            DOCUMENTATION_MANAGER.authority,
            DOCUMENTATION_MANAGER.prohibited_actions,
        )
        h2 = _hash_contract_shape(
            DOCUMENTATION_MANAGER.authority,
            DOCUMENTATION_MANAGER.prohibited_actions,
        )
        self.assertEqual(h1, h2)

    def test_hash_differs_across_contracts(self):
        """3 production contracts must produce 3 distinct hashes."""
        hashes = {
            _hash_contract_shape(
                c.authority, c.prohibited_actions
            )
            for c in (
                DOCUMENTATION_MANAGER,
                PLATFORM_AUDIT_JOB,
                MORNING_BRIEF_JOB,
            )
        }
        self.assertEqual(len(hashes), 3)

    def test_hash_invariant_to_dict_insertion_order(self):
        """Adding entries in different order must produce same hash."""
        a = {"x": "execute", "y": "observe", "z": "prohibited"}
        b = {"z": "prohibited", "x": "execute", "y": "observe"}
        self.assertEqual(
            _hash_contract_shape(a, ()),
            _hash_contract_shape(b, ()),
        )
