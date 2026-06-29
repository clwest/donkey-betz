"""
Tests for Session 1253 PR 4 — Employee Communications shift-report DM.

Real-DB tests against PostgreSQL. Covers:

  * Persistent thread per (employee, job) — deterministic lookup,
    no duplicates.
  * One DM per terminal mission. Idempotency by mission_id +
    thread_id. Re-call is a no-op.
  * Non-terminal mission produces no DM.
  * Body templates per Rigby's exact spec.
  * Bounded metadata (no error_tail leak).
  * messaging_tool schema is read-only in v0 (send_message removed).
  * messaging_tool handler defense-in-depth guard refuses
    send_message unless settings.MESSAGING_TOOL_ALLOW_SEND=True.

Run::

    python manage.py test core.tests.test_employees_comms --keepdb -v2
"""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any, Dict, Optional

from django.test import TestCase, override_settings
from django.utils import timezone


# ── Helpers ──────────────────────────────────────────────────────────


def _ensure_chris_user():
    """Make sure the recipient user exists (Rigby reports to chris)."""
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()
    user, _ = UserModel.objects.get_or_create(
        username="chris",
        defaults={"is_active": True},
    )
    return user


def _seed_mission(
    *,
    status: str = "passed",
    verdict: Optional[str] = "certified",
    wall_time_ms: Optional[int] = 42870,
    drift_count: Optional[int] = 5,
    failed_step: Optional[str] = None,
    escalation_deliverable_id: Optional[str] = None,
    verdict_confidence: Optional[float] = 0.95,
    error_tail: Optional[str] = None,
):
    """Create an OpsRun(domain=mission, run_kind=docs_cascade) row."""
    from core.models_ops_runs import OpsRun

    summary: Dict[str, Any] = {
        "verdict": verdict,
        "verdict_confidence": verdict_confidence,
        "verdict_issued_by": "rigby",
        "wall_time_ms": wall_time_ms,
        "failed_step": failed_step,
        "drift_count": drift_count,
        "drift_items_count": drift_count,
        "degraded_evidence": False,
        "error_tail": error_tail,
        "docs_indexed_count": 2754,
        "documents_count_before": 2756,
        "documents_count_after": 2756,
        "embeddings_count_before": 37682,
        "embeddings_count_after": 37682,
        "embedding_delta": 0,
    }
    if escalation_deliverable_id:
        summary["escalation_deliverable_id"] = escalation_deliverable_id

    return OpsRun.objects.create(
        title="docs_cascade",
        run_type="manual",
        domain="mission",
        run_kind="docs_cascade",
        status=status,
        triggered_by="beat",
        summary=summary,
        finished_at=timezone.now(),
    )


# ── Thread + DM creation, persistence, idempotency ───────────────────


class ShiftReportCreationTests(TestCase):

    def setUp(self):
        _ensure_chris_user()

    def test_first_shift_report_creates_one_thread(self):
        from core.employees.comms import (
            post_shift_report,
            EMPLOYEE_KEY,
            JOB_KEY,
            THREAD_SUBJECT,
        )
        from core.models_messaging import MessageThread, DirectMessage

        self.assertEqual(MessageThread.objects.count(), 0)
        mission = _seed_mission()

        result = post_shift_report(mission)
        self.assertTrue(result["ok"])
        self.assertTrue(result["created"])
        self.assertIsNone(result["skipped_reason"])
        self.assertIsNotNone(result["thread_id"])
        self.assertIsNotNone(result["message_id"])

        self.assertEqual(MessageThread.objects.count(), 1)
        thread = MessageThread.objects.first()
        self.assertEqual(thread.subject, THREAD_SUBJECT)
        self.assertEqual(thread.thread_type, "dm")
        self.assertEqual(thread.metadata["employee"], EMPLOYEE_KEY)
        self.assertEqual(thread.metadata["job"], JOB_KEY)

        self.assertEqual(DirectMessage.objects.count(), 1)
        dm = DirectMessage.objects.first()
        self.assertEqual(dm.sender_type, "rigby")
        self.assertIsNone(dm.sender)  # Rigby has no User row

    def test_second_mission_reuses_same_thread(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import MessageThread, DirectMessage

        m1 = _seed_mission()
        m2 = _seed_mission()

        post_shift_report(m1)
        post_shift_report(m2)

        self.assertEqual(MessageThread.objects.count(), 1)
        self.assertEqual(DirectMessage.objects.count(), 2)

        thread = MessageThread.objects.first()
        bodies = list(
            DirectMessage.objects.filter(thread=thread)
            .values_list("metadata", flat=True)
        )
        mission_ids = {b["mission_id"] for b in bodies}
        self.assertEqual(
            mission_ids, {str(m1.id), str(m2.id)}
        )

    def test_same_mission_id_no_duplicate_dm(self):
        """Re-calling post_shift_report for the same mission is a no-op."""
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage, MessageThread

        mission = _seed_mission()
        r1 = post_shift_report(mission)
        r2 = post_shift_report(mission)

        self.assertTrue(r1["created"])
        self.assertFalse(r2["created"])
        self.assertEqual(r2["skipped_reason"], "duplicate")
        # Same message_id returned the second time.
        self.assertEqual(r1["message_id"], r2["message_id"])

        self.assertEqual(MessageThread.objects.count(), 1)
        self.assertEqual(DirectMessage.objects.count(), 1)

    def test_chris_is_added_as_thread_participant(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import ThreadParticipant

        mission = _seed_mission()
        post_shift_report(mission)

        participants = ThreadParticipant.objects.all()
        self.assertEqual(participants.count(), 1)
        self.assertEqual(participants.first().user.username, "chris")


# ── Body + metadata templates ────────────────────────────────────────


class ShiftReportBodyTests(TestCase):

    def setUp(self):
        _ensure_chris_user()

    def test_passed_body_uses_template(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        mission = _seed_mission(
            status="passed",
            verdict="certified",
            wall_time_ms=42870,
            drift_count=5,
        )
        post_shift_report(mission)

        dm = DirectMessage.objects.get()
        self.assertIn(f"mission {mission.id} passed", dm.body)
        self.assertIn("42.9s", dm.body)
        self.assertIn("Drift 5 items observed", dm.body)
        self.assertIn("No escalation", dm.body)

    def test_passed_metadata_is_bounded(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        mission = _seed_mission(
            status="passed",
            verdict="certified",
            wall_time_ms=42870,
            drift_count=5,
            error_tail="this should never appear in metadata",
        )
        post_shift_report(mission)

        dm = DirectMessage.objects.get()
        keys = set(dm.metadata.keys())
        self.assertEqual(keys, {
            "employee", "job",
            "mission_id", "verdict", "status",
            "wall_time_ms", "drift_count",
            "failed_step", "escalation_deliverable_id",
        })
        self.assertEqual(dm.metadata["verdict"], "certified")
        self.assertEqual(dm.metadata["mission_id"], str(mission.id))
        self.assertEqual(dm.metadata["status"], "passed")
        self.assertEqual(dm.metadata["wall_time_ms"], 42870)
        self.assertEqual(dm.metadata["drift_count"], 5)
        self.assertIsNone(dm.metadata["failed_step"])
        self.assertIsNone(dm.metadata["escalation_deliverable_id"])
        self.assertEqual(dm.metadata["employee"], "rigby")
        self.assertEqual(dm.metadata["job"], "docs_manager")
        # Defense: 'error_tail' must never be in the metadata.
        self.assertNotIn("error_tail", dm.metadata)
        self.assertNotIn("error_tail", str(dm.metadata))

    def test_failed_body_includes_failed_step_and_deliverable(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        deliv_id = str(uuid.uuid4())
        mission = _seed_mission(
            status="failed",
            verdict="rejected",
            failed_step="build_docs_index",
            escalation_deliverable_id=deliv_id,
            verdict_confidence=0.0,
        )
        post_shift_report(mission)

        dm = DirectMessage.objects.get()
        self.assertIn(f"mission {mission.id} failed", dm.body)
        self.assertIn("build_docs_index", dm.body)
        self.assertIn(f"deliverable {deliv_id}", dm.body)
        self.assertEqual(
            dm.metadata["escalation_deliverable_id"], deliv_id
        )
        self.assertEqual(dm.metadata["failed_step"], "build_docs_index")
        self.assertEqual(dm.metadata["verdict"], "rejected")

    def test_failed_without_escalation_id_still_works(self):
        """If escalation_deliverable_id is missing, fall back to the
        'No escalation deliverable recorded.' sentence."""
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        mission = _seed_mission(
            status="failed",
            verdict="rejected",
            failed_step="step_3_sync",
            escalation_deliverable_id=None,
        )
        post_shift_report(mission)

        dm = DirectMessage.objects.get()
        self.assertIn("No escalation deliverable recorded", dm.body)
        self.assertIsNone(dm.metadata["escalation_deliverable_id"])

    def test_deferred_body_uses_template(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        mission = _seed_mission(
            status="partial",
            verdict="deferred",
        )
        post_shift_report(mission)

        dm = DirectMessage.objects.get()
        self.assertIn(f"mission {mission.id} deferred", dm.body)
        self.assertEqual(dm.metadata["verdict"], "deferred")


# ── Non-terminal gating ──────────────────────────────────────────────


class ShiftReportTerminalGatingTests(TestCase):

    def setUp(self):
        _ensure_chris_user()

    def test_running_mission_creates_no_dm(self):
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage, MessageThread

        # status=running and no verdict in summary
        mission = _seed_mission(status="running", verdict=None)

        result = post_shift_report(mission)
        self.assertTrue(result["ok"])
        self.assertFalse(result["created"])
        self.assertEqual(result["skipped_reason"], "non_terminal")
        self.assertEqual(DirectMessage.objects.count(), 0)
        self.assertEqual(MessageThread.objects.count(), 0)

    def test_running_status_but_terminal_verdict_still_posts(self):
        """Verdict alone is sufficient for terminal — protects against
        the caller having a stale status field while summary.verdict
        already landed."""
        from core.employees.comms import post_shift_report
        from core.models_messaging import DirectMessage

        mission = _seed_mission(status="running", verdict="certified")

        result = post_shift_report(mission)
        self.assertTrue(result["created"])
        self.assertEqual(DirectMessage.objects.count(), 1)


# ── Thread lookup determinism (no duplicates) ────────────────────────


class ThreadLookupDeterminismTests(TestCase):

    def setUp(self):
        _ensure_chris_user()

    def test_lookup_is_keyed_by_metadata_not_subject(self):
        """A thread with the same metadata key but a different subject
        is still found by the helper — subject typos cannot create
        duplicates."""
        from core.employees.comms import post_shift_report
        from core.models_messaging import MessageThread, DirectMessage

        # Pre-seed a thread with the canonical metadata but a typo
        # subject. The helper should reuse it.
        existing = MessageThread.objects.create(
            subject="Rigby - Documentation Manager",  # typo (hyphen vs em-dash)
            thread_type="dm",
            metadata={
                "employee": "rigby",
                "job": "docs_manager",
                "thread_kind": "employee_shift_report",
            },
        )

        mission = _seed_mission()
        result = post_shift_report(mission)
        self.assertEqual(result["thread_id"], str(existing.id))
        self.assertEqual(MessageThread.objects.count(), 1)

    def test_archived_thread_is_ignored(self):
        """If the canonical thread is archived, the helper creates a
        fresh one rather than reactivating it."""
        from core.employees.comms import post_shift_report
        from core.models_messaging import MessageThread

        MessageThread.objects.create(
            subject="Rigby — Documentation Manager",
            thread_type="dm",
            metadata={
                "employee": "rigby",
                "job": "docs_manager",
                "thread_kind": "employee_shift_report",
            },
            is_archived=True,
        )
        mission = _seed_mission()
        result = post_shift_report(mission)
        # Two threads total: the archived old one + the new live one.
        self.assertEqual(MessageThread.objects.count(), 2)
        self.assertNotEqual(
            result["thread_id"],
            str(MessageThread.objects.filter(is_archived=True).first().id),
        )


# ── messaging_tool schema is read-only in v0 ────────────────────────


class MessagingToolSchemaTests(TestCase):

    def test_schema_action_enum_excludes_send_message(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        msg_schema = next(
            t for t in PA_TOOL_SCHEMAS if t["name"] == "messaging_tool"
        )
        enum = msg_schema["parameters"]["properties"]["action"]["enum"]
        self.assertEqual(
            sorted(enum),
            ["get_thread", "list_threads", "unread_count"],
        )
        self.assertNotIn("send_message", enum)

    def test_schema_does_not_carry_send_message_only_params(self):
        """Recipient/message/subject params only existed to support
        send_message. They should be gone from v0 surface."""
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        msg_schema = next(
            t for t in PA_TOOL_SCHEMAS if t["name"] == "messaging_tool"
        )
        properties = msg_schema["parameters"]["properties"]
        self.assertNotIn("recipient_username", properties)
        self.assertNotIn("message", properties)
        self.assertNotIn("subject", properties)


# ── messaging_tool handler defense-in-depth guard ───────────────────


class MessagingToolHandlerGuardTests(TestCase):

    def setUp(self):
        self.user = _ensure_chris_user()

    def _call_messaging(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        from core.services.tool_dispatcher import ToolDispatcher

        # Bare dispatcher (mixin attached at construction).
        dispatcher = ToolDispatcher()
        return dispatcher._handle_messaging(
            "messaging_tool", payload, self.user.id, "test-trace"
        )

    def test_send_message_refused_by_default(self):
        result = self._call_messaging({
            "action": "send_message",
            "recipient_username": "anyone",
            "message": "hi",
        })
        self.assertIn("error", result)
        self.assertEqual(
            result.get("error_code"), "MESSAGING_SEND_DISABLED"
        )

    @override_settings(MESSAGING_TOOL_ALLOW_SEND=True)
    def test_send_message_allowed_when_flag_set(self):
        # Create a second user to receive the message.
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        recipient = UserModel.objects.create_user(
            username=f"recipient-{uuid.uuid4()}",
            password="x",
        )
        result = self._call_messaging({
            "action": "send_message",
            "recipient_username": recipient.username,
            "message": "test under override",
        })
        self.assertNotIn("error", result)
        self.assertEqual(result["status"], "sent")

    def test_list_threads_always_allowed(self):
        result = self._call_messaging({"action": "list_threads"})
        self.assertNotIn("error", result)
        self.assertEqual(result["action"], "list_threads")


# ── End-to-end: helper writes match what messaging_tool reads ───────


class MessagingReadIntegrationTests(TestCase):

    def setUp(self):
        self.user = _ensure_chris_user()

    def _call_messaging(self, payload):
        from core.services.tool_dispatcher import ToolDispatcher
        dispatcher = ToolDispatcher()
        return dispatcher._handle_messaging(
            "messaging_tool", payload, self.user.id, "test-trace"
        )

    def test_list_threads_surfaces_shift_report_thread(self):
        from core.employees.comms import post_shift_report

        mission = _seed_mission()
        post_shift_report(mission)

        result = self._call_messaging({"action": "list_threads"})
        self.assertEqual(result["thread_count"], 1)
        thread = result["threads"][0]
        self.assertEqual(thread["unread_count"], 1)
        self.assertIn("passed", thread["last_message"])

    def test_get_thread_surfaces_shift_report_dm(self):
        from core.employees.comms import post_shift_report

        mission = _seed_mission()
        result = post_shift_report(mission)
        thread_id = result["thread_id"]

        getr = self._call_messaging({
            "action": "get_thread",
            "thread_id": thread_id,
        })
        self.assertEqual(len(getr["messages"]), 1)
        msg = getr["messages"][0]
        self.assertEqual(msg["sender_type"], "rigby")
        self.assertIn(f"mission {mission.id}", msg["body"])

    def test_unread_count_reflects_shift_reports(self):
        from core.employees.comms import post_shift_report

        for _ in range(3):
            post_shift_report(_seed_mission())
        result = self._call_messaging({"action": "unread_count"})
        # 3 DMs created, all unread (no last_read_at advance).
        self.assertEqual(result["unread_count"], 3)


# ── Robustness: helper never crashes the docs cascade ────────────────


class HelperRobustnessTests(TestCase):

    def test_no_recipient_user_returns_skipped_not_raises(self):
        """If chris user doesn't exist (unusual), helper soft-skips."""
        from core.employees.comms import post_shift_report
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        UserModel.objects.filter(username="chris").delete()

        mission = _seed_mission()
        result = post_shift_report(mission)
        self.assertTrue(result["ok"])
        self.assertFalse(result["created"])
        self.assertEqual(result["skipped_reason"], "no_recipient")
