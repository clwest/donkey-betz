"""
Tests for the Session 1252 PR 1 ``mission_verdict`` PA tool +
``emit_mission_verdict`` helper. Real-DB integration — exercises real
OpsRun + OpsRunEvent rows per the S1234 memory rule (no mocked
querysets for QS-heavy code).

Covers:

Helper (``emit_mission_verdict``):
- happy path: certify flips status running → passed + writes one event
- reject flips status running → failed
- defer flips status running → partial
- idempotency: same (mission_id, verdict) twice → event_created=False
- terminal status preservation: pre-certified mission re-certified
  does NOT overwrite status; status_changed=False
- unknown mission_id raises ValueError
- unknown verdict raises ValueError
- confidence is clamped to [0.0, 1.0]
- evidence_refs round-trips through OpsRunEvent.detail

Handler (``_handle_mission_verdict``):
- non-Rigby caller is rejected with TOOL_PERMISSION_DENIED
- Rigby caller (chris user) certifies successfully
- unknown mission_id returns clean error (not exception)
- missing mission_id returns clean error
- unknown action returns clean error + valid_actions list

Run::

    python manage.py test core.tests.test_mission_verdict -v2
"""

from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.employees.mission_verdict import (
    LABEL_VERDICT_PREFIX,
    VERDICT_CERTIFIED,
    VERDICT_DEFERRED,
    VERDICT_REJECTED,
    emit_mission_verdict,
    verdict_label,
)
from core.models_ops_runs import OpsRun, OpsRunEvent
from core.services.td_handlers_employee import EmployeeHandlersMixin


User = get_user_model()


def _make_mission(**overrides) -> OpsRun:
    """Create a fresh MissionRun in status='running' for verdict tests."""
    defaults = dict(
        title="test mission",
        run_type="manual",
        domain="mission",
        run_kind="docs_cascade",
        mission_id=uuid.uuid4(),
        status="running",
    )
    defaults.update(overrides)
    return OpsRun.objects.create(**defaults)


# ── emit_mission_verdict helper ──────────────────────────────────────


class EmitMissionVerdictHappyPathTests(TestCase):

    def test_certify_flips_status_to_passed(self):
        mission = _make_mission()
        result = emit_mission_verdict(
            mission_id=mission.id,
            verdict=VERDICT_CERTIFIED,
            confidence=0.92,
        )
        mission.refresh_from_db()
        self.assertEqual(mission.status, "passed")
        self.assertIsNotNone(mission.finished_at)
        self.assertEqual(result["current_status"], "passed")
        self.assertEqual(result["previous_status"], "running")
        self.assertTrue(result["status_changed"])
        self.assertTrue(result["event_created"])

    def test_reject_flips_status_to_failed(self):
        mission = _make_mission()
        emit_mission_verdict(
            mission_id=mission.id, verdict=VERDICT_REJECTED
        )
        mission.refresh_from_db()
        self.assertEqual(mission.status, "failed")

    def test_defer_flips_status_to_partial(self):
        mission = _make_mission()
        emit_mission_verdict(
            mission_id=mission.id, verdict=VERDICT_DEFERRED
        )
        mission.refresh_from_db()
        self.assertEqual(mission.status, "partial")

    def test_event_row_written_with_correct_label(self):
        mission = _make_mission()
        emit_mission_verdict(
            mission_id=mission.id,
            verdict=VERDICT_CERTIFIED,
            confidence=0.8,
            evidence_refs=["llm_call:abc-123", "deliverable:def-456"],
            notes="all cascade steps clean",
        )
        events = OpsRunEvent.objects.filter(
            run=mission, label__startswith=LABEL_VERDICT_PREFIX
        )
        self.assertEqual(events.count(), 1)
        evt = events.first()
        self.assertEqual(evt.label, "verdict_issued:certified")
        self.assertEqual(evt.event_type, "step_pass")
        detail = evt.detail
        self.assertEqual(detail["verdict"], "certified")
        self.assertEqual(detail["issued_by"], "rigby")
        self.assertEqual(detail["confidence"], 0.8)
        self.assertEqual(detail["notes"], "all cascade steps clean")
        self.assertEqual(
            detail["evidence_refs"],
            ["llm_call:abc-123", "deliverable:def-456"],
        )

    def test_summary_is_extended_not_replaced(self):
        """OpsRun.summary should merge verdict fields on top of any
        pre-existing keys, not nuke them. PR 2 populates summary keys
        like wall_time_ms before calling emit_mission_verdict; they
        must survive."""
        mission = _make_mission(
            summary={"wall_time_ms": 4500, "docs_indexed_count": 1820}
        )
        emit_mission_verdict(
            mission_id=mission.id,
            verdict=VERDICT_CERTIFIED,
            confidence=0.9,
        )
        mission.refresh_from_db()
        self.assertEqual(mission.summary["wall_time_ms"], 4500)
        self.assertEqual(mission.summary["docs_indexed_count"], 1820)
        self.assertEqual(mission.summary["verdict"], "certified")
        self.assertEqual(mission.summary["verdict_confidence"], 0.9)


class EmitMissionVerdictIdempotencyTests(TestCase):

    def test_same_verdict_twice_creates_one_event(self):
        mission = _make_mission()
        r1 = emit_mission_verdict(
            mission_id=mission.id, verdict=VERDICT_CERTIFIED
        )
        r2 = emit_mission_verdict(
            mission_id=mission.id, verdict=VERDICT_CERTIFIED
        )
        self.assertTrue(r1["event_created"])
        self.assertFalse(r2["event_created"])
        self.assertEqual(r1["event_id"], r2["event_id"])
        self.assertEqual(
            OpsRunEvent.objects.filter(
                run=mission, label="verdict_issued:certified"
            ).count(),
            1,
        )

    def test_terminal_status_not_overwritten_by_second_verdict(self):
        """Once a MissionRun is in a terminal status, a subsequent
        *different* verdict still gets its OpsRunEvent row but MUST
        NOT mutate the OpsRun.status (preserves the audit trail of
        what actually happened first)."""
        mission = _make_mission()
        first = emit_mission_verdict(
            mission_id=mission.id, verdict=VERDICT_CERTIFIED
        )
        self.assertTrue(first["status_changed"])
        self.assertEqual(first["current_status"], "passed")

        # Now try to reject the same mission. New event row appears;
        # status stays 'passed'.
        second = emit_mission_verdict(
            mission_id=mission.id, verdict=VERDICT_REJECTED
        )
        self.assertTrue(second["event_created"])
        self.assertFalse(second["status_changed"])
        self.assertEqual(second["previous_status"], "passed")
        self.assertEqual(second["current_status"], "passed")
        mission.refresh_from_db()
        self.assertEqual(mission.status, "passed")
        # Both events exist on the timeline.
        self.assertEqual(
            OpsRunEvent.objects.filter(
                run=mission, label__startswith=LABEL_VERDICT_PREFIX
            ).count(),
            2,
        )


class EmitMissionVerdictErrorPathTests(TestCase):

    def test_unknown_mission_id_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            emit_mission_verdict(
                mission_id=uuid.uuid4(),  # nothing with this id
                verdict=VERDICT_CERTIFIED,
            )
        self.assertIn("No MissionRun", str(ctx.exception))

    def test_unknown_verdict_raises_value_error(self):
        mission = _make_mission()
        with self.assertRaises(ValueError) as ctx:
            emit_mission_verdict(
                mission_id=mission.id, verdict="approve"  # not in vocab
            )
        self.assertIn("Unknown verdict", str(ctx.exception))

    def test_ops_domain_row_not_eligible(self):
        """``emit_mission_verdict`` only operates on mission-domain
        rows. An ops-domain row with the same UUID lookup must raise."""
        ops_run = OpsRun.objects.create(
            title="ops run",
            run_type="manual",
            domain="ops",
        )
        with self.assertRaises(ValueError):
            emit_mission_verdict(
                mission_id=ops_run.id, verdict=VERDICT_CERTIFIED
            )

    def test_confidence_clamped_to_range(self):
        mission = _make_mission()
        result = emit_mission_verdict(
            mission_id=mission.id,
            verdict=VERDICT_CERTIFIED,
            confidence=2.5,  # over the max
        )
        self.assertEqual(result["confidence"], 1.0)

    def test_negative_confidence_clamped_to_zero(self):
        mission = _make_mission()
        result = emit_mission_verdict(
            mission_id=mission.id,
            verdict=VERDICT_REJECTED,
            confidence=-0.7,
        )
        self.assertEqual(result["confidence"], 0.0)


# ── Verdict label helper ─────────────────────────────────────────────


class VerdictLabelTests(TestCase):

    def test_label_per_verdict(self):
        self.assertEqual(
            verdict_label(VERDICT_CERTIFIED), "verdict_issued:certified"
        )
        self.assertEqual(
            verdict_label(VERDICT_REJECTED), "verdict_issued:rejected"
        )
        self.assertEqual(
            verdict_label(VERDICT_DEFERRED), "verdict_issued:deferred"
        )


# ── PA tool handler ──────────────────────────────────────────────────


def _call_verdict_handler(
    payload: dict, user_id=None
) -> dict:
    handler = EmployeeHandlersMixin()
    return handler._handle_mission_verdict(
        tool_name="mission_verdict",
        payload=payload,
        user_id=user_id,
        trace_id="test-trace-id",
    )


class MissionVerdictHandlerAuthTests(TestCase):
    """v0 auth gate — caller must resolve to Rigby's runs_as user."""

    @classmethod
    def setUpTestData(cls):
        # Rigby runs as the 'chris' user; create one + an 'imposter'.
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

    def test_no_user_id_is_rejected(self):
        mission = _make_mission()
        result = _call_verdict_handler(
            {"action": "certify", "mission_id": str(mission.id)},
            user_id=None,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "TOOL_PERMISSION_DENIED")
        self.assertIn("auth_gate", result)

    def test_imposter_user_rejected(self):
        mission = _make_mission()
        result = _call_verdict_handler(
            {"action": "certify", "mission_id": str(mission.id)},
            user_id=self.imposter.id,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "TOOL_PERMISSION_DENIED")
        self.assertIn("imposter", result["error"])

    def test_chris_user_accepted(self):
        mission = _make_mission()
        result = _call_verdict_handler(
            {
                "action": "certify",
                "mission_id": str(mission.id),
                "confidence": 0.95,
            },
            user_id=self.chris.id,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["verdict"], "certified")
        self.assertEqual(result["current_status"], "passed")

    def test_unknown_user_id_rejected(self):
        mission = _make_mission()
        result = _call_verdict_handler(
            {"action": "certify", "mission_id": str(mission.id)},
            user_id=uuid.uuid4(),  # no such user
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error_code"], "TOOL_PERMISSION_DENIED")


class MissionVerdictHandlerArgsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.chris = User.objects.create_user(
            username="chris",
            email="chris@test.donkey",
            password="x",
        )

    def test_unknown_action_returns_clean_error(self):
        result = _call_verdict_handler(
            {"action": "approve", "mission_id": str(uuid.uuid4())},
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("Unknown mission_verdict action", result["error"])
        self.assertEqual(
            sorted(result["valid_actions"]),
            ["certify", "defer", "reject"],
        )

    def test_missing_mission_id_returns_clean_error(self):
        result = _call_verdict_handler(
            {"action": "certify"},  # no mission_id
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("Missing required arg 'mission_id'", result["error"])

    def test_unknown_mission_id_returns_clean_error_not_exception(self):
        result = _call_verdict_handler(
            {
                "action": "certify",
                "mission_id": str(uuid.uuid4()),  # nonexistent
            },
            user_id=self.chris.id,
        )
        self.assertFalse(result["ok"])
        self.assertIn("No MissionRun", result["error"])

    def test_certify_idempotent_via_handler_path(self):
        mission = _make_mission()
        r1 = _call_verdict_handler(
            {"action": "certify", "mission_id": str(mission.id)},
            user_id=self.chris.id,
        )
        r2 = _call_verdict_handler(
            {"action": "certify", "mission_id": str(mission.id)},
            user_id=self.chris.id,
        )
        self.assertTrue(r1["ok"])
        self.assertTrue(r2["ok"])
        self.assertTrue(r1["event_created"])
        self.assertFalse(r2["event_created"])
