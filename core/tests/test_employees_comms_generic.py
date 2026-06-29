"""
Generic shift-report helper tests (Session 1253 PR-A).

Proves the helper signature ``post_shift_report(employee, job, mission)``
works for a second, fake employee/job pair WITHOUT relying on any
docs_manager defaults, subject, body template, or metadata keys.

This is the load-bearing acceptance criterion for PR-A:

  "A generic second employee/job test can produce a shift report
   through the same helper."

Run::

    python manage.py test core.tests.test_employees_comms_generic \
        --keepdb -v2
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Optional

from django.test import TestCase
from django.utils import timezone


# ── Local fake employee (NOT registered in the global AIEmployee
#    registry — keeps the test isolated to the helper) ────────────────


@dataclass(frozen=True)
class _FakeAIEmployee:
    handle: str
    display_name: str
    runs_as_username: str
    primary_chat_id: Optional[str] = None
    notes: str = ""


FAKE_EMPLOYEE = _FakeAIEmployee(
    handle="auditor_bot",            # different handle from rigby
    display_name="Auditor Bot",
    runs_as_username="chris",
)


def _ensure_chris_user():
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()
    u, _ = UserModel.objects.get_or_create(
        username="chris", defaults={"is_active": True}
    )
    return u


def _seed_terminal_mission(
    *,
    verdict: str = "certified",
    status: str = "passed",
    wall_time_ms: int = 1234,
    extras: Optional[Dict[str, Any]] = None,
):
    """Create a terminal-state OpsRun.

    Uses ``run_kind='fake_job_kind'`` so the mission row is unambiguously
    NOT a docs_cascade and the test cannot be tricked by accidental
    overlap with the docs_manager dataset.
    """
    from core.models_ops_runs import OpsRun

    summary: Dict[str, Any] = {
        "verdict": verdict,
        "wall_time_ms": wall_time_ms,
    }
    if extras:
        summary.update(extras)

    return OpsRun.objects.create(
        title="fake_job",
        run_type="manual",
        domain="mission",
        run_kind="fake_job_kind",
        status=status,
        triggered_by="manual",
        summary=summary,
        finished_at=timezone.now(),
    )


# ── Generic helper tests ─────────────────────────────────────────────


class GenericShiftReportTests(TestCase):

    def setUp(self):
        _ensure_chris_user()

    def test_second_employee_can_reuse_helper(self):
        """The helper accepts an arbitrary employee+job, creates its
        own thread, and writes one DM."""
        from core.employees.comms import post_shift_report
        from core.models_messaging import MessageThread, DirectMessage

        mission = _seed_terminal_mission()
        result = post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["created"])
        self.assertIsNone(result["skipped_reason"])

        # Exactly one thread keyed to the fake employee/job — not a
        # docs_manager thread.
        threads = MessageThread.objects.filter(
            metadata__employee="auditor_bot",
            metadata__job="fake_audit_job",
        )
        self.assertEqual(threads.count(), 1)
        thread = threads.first()
        # Default subject derives from employee.display_name + job key.
        self.assertEqual(thread.subject, "Auditor Bot — fake_audit_job")
        # No accidental docs_manager metadata.
        self.assertNotEqual(thread.metadata.get("employee"), "rigby")
        self.assertNotEqual(thread.metadata.get("job"), "docs_manager")

        dms = DirectMessage.objects.filter(thread=thread)
        self.assertEqual(dms.count(), 1)
        dm = dms.first()
        # sender_type defaults to 'system' for non-docs employees
        # (matches DirectMessage.SENDER_TYPE_CHOICES).
        self.assertEqual(dm.sender_type, "system")
        # Generic body — does NOT mention "Docs Manager" / cascade.
        self.assertIn(str(mission.id), dm.body)
        self.assertIn("terminal verdict", dm.body)
        self.assertNotIn("Docs Manager", dm.body)
        self.assertNotIn("cascade", dm.body.lower())
        self.assertNotIn("drift", dm.body.lower())

    def test_metadata_only_carries_base_keys_when_no_extras(self):
        """Without ``extra_metadata_keys``, metadata is exactly
        ``BASE_METADATA_KEYS`` — no docs-cascade leak."""
        from core.employees.comms import post_shift_report, BASE_METADATA_KEYS
        from core.models_messaging import DirectMessage

        mission = _seed_terminal_mission(
            extras={
                # These keys exist in the summary but are NOT in the
                # base key set — they must NOT bleed into the metadata.
                "drift_count": 99,
                "failed_step": "should_not_appear",
                "escalation_deliverable_id": "should_not_appear",
                "error_tail": "should_NEVER_appear",
            },
        )
        post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
        )
        dm = DirectMessage.objects.filter(
            metadata__mission_id=str(mission.id)
        ).first()
        keys = set(dm.metadata.keys())
        self.assertEqual(keys, set(BASE_METADATA_KEYS))
        # Defense: no docs-cascade-specific values leaked.
        self.assertNotIn("drift_count", dm.metadata)
        self.assertNotIn("failed_step", dm.metadata)
        self.assertNotIn("escalation_deliverable_id", dm.metadata)
        self.assertNotIn("error_tail", dm.metadata)
        import json
        flat = json.dumps(dm.metadata, default=str)
        self.assertNotIn("should_not_appear", flat)
        self.assertNotIn("should_NEVER_appear", flat)

    def test_caller_can_supply_custom_body_formatter(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        def custom_body(mission, summary):
            return f"AUDIT REPORT // mission={mission.id} verdict={summary.get('verdict')}"

        mission = _seed_terminal_mission()
        post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
            body_formatter=custom_body,
        )
        dm = DirectMessage.objects.filter(
            metadata__mission_id=str(mission.id)
        ).first()
        self.assertTrue(dm.body.startswith("AUDIT REPORT //"))
        self.assertIn("certified", dm.body)

    def test_caller_can_supply_extra_metadata_keys(self):
        """``extra_metadata_keys`` extends the base set; missing keys
        in summary become null."""
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        mission = _seed_terminal_mission(
            extras={"audit_score": 88, "findings_count": 3},
        )
        post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
            extra_metadata_keys=("audit_score", "findings_count", "missing_one"),
        )
        dm = DirectMessage.objects.filter(
            metadata__mission_id=str(mission.id)
        ).first()
        self.assertEqual(dm.metadata["audit_score"], 88)
        self.assertEqual(dm.metadata["findings_count"], 3)
        self.assertIsNone(dm.metadata["missing_one"])  # absent → null
        # Base keys still present.
        self.assertEqual(dm.metadata["employee"], "auditor_bot")
        self.assertEqual(dm.metadata["job"], "fake_audit_job")

    def test_caller_can_override_thread_subject(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import MessageThread

        mission = _seed_terminal_mission()
        post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
            thread_subject="Quarterly Audit Report",
        )
        thread = MessageThread.objects.filter(
            metadata__employee="auditor_bot",
            metadata__job="fake_audit_job",
        ).first()
        self.assertEqual(thread.subject, "Quarterly Audit Report")

    def test_terminal_gate_still_applies_for_non_docs_jobs(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage, MessageThread

        mission = _seed_terminal_mission(verdict=None, status="running")
        result = post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
        )
        self.assertFalse(result["created"])
        self.assertEqual(result["skipped_reason"], "non_terminal")
        self.assertEqual(DirectMessage.objects.count(), 0)
        self.assertEqual(MessageThread.objects.count(), 0)

    def test_idempotency_still_applies_for_non_docs_jobs(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        mission = _seed_terminal_mission()
        r1 = post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
        )
        r2 = post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=mission,
        )
        self.assertTrue(r1["created"])
        self.assertFalse(r2["created"])
        self.assertEqual(r2["skipped_reason"], "duplicate")
        self.assertEqual(r1["message_id"], r2["message_id"])
        self.assertEqual(DirectMessage.objects.count(), 1)


# ── Isolation: docs_manager thread is not shared with fake job ──────


class GenericThreadIsolationTests(TestCase):

    def setUp(self):
        _ensure_chris_user()

    def test_fake_job_does_not_reuse_docs_manager_thread(self):
        """Two distinct (employee, job) pairs produce two threads —
        never one shared thread."""
        from core.employees.comms import post_shift_report
        from core.employees.comms_docs_manager import (
            post_docs_manager_shift_report,
        )
        from core.models_messaging import MessageThread

        # Seed one docs_manager mission + one fake-employee mission.
        from core.models_ops_runs import OpsRun
        docs_mission = OpsRun.objects.create(
            title="docs_cascade",
            run_type="manual",
            domain="mission",
            run_kind="docs_cascade",
            status="passed",
            triggered_by="manual",
            summary={
                "verdict": "certified", "wall_time_ms": 5000,
                "drift_count": 0,
            },
            finished_at=timezone.now(),
        )
        post_docs_manager_shift_report(docs_mission)

        fake_mission = _seed_terminal_mission()
        post_shift_report(
            employee=FAKE_EMPLOYEE,
            job="fake_audit_job",
            mission=fake_mission,
        )

        threads = MessageThread.objects.all()
        self.assertEqual(threads.count(), 2)

        docs_thread = MessageThread.objects.filter(
            metadata__employee="rigby",
            metadata__job="docs_manager",
        ).first()
        fake_thread = MessageThread.objects.filter(
            metadata__employee="auditor_bot",
            metadata__job="fake_audit_job",
        ).first()

        self.assertIsNotNone(docs_thread)
        self.assertIsNotNone(fake_thread)
        self.assertNotEqual(docs_thread.id, fake_thread.id)
        # Each thread has exactly one DM (no cross-pollination).
        self.assertEqual(docs_thread.messages.count(), 1)
        self.assertEqual(fake_thread.messages.count(), 1)
        # Body assertions: docs body mentions cascade; fake body does not.
        self.assertIn("Docs Manager", docs_thread.messages.first().body)
        self.assertNotIn(
            "Docs Manager", fake_thread.messages.first().body
        )
