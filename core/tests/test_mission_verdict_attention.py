"""
Regression tests for Session 2734 Platform Closure Category B —
Capability Chain §1 Item 9 HAI on mission verdict.

Exercises
``core.signals.mission_verdict_attention_signals.escalate_mission_verdict_to_hai``:
the second post_save receiver on ``OpsRunEvent`` that escalates
``verdict_issued:rejected`` and ``verdict_issued:deferred`` to
``HumanAttentionItem`` via ``HumanAttentionBridge``.

Test discipline:
- Real DB. No mocked querysets.
- ``HumanAttentionBridge.create_mission_verdict_attention`` is patched
  so we assert the *receiver's* contract (label parsing, verdict
  filter, kill switch, on_commit gating) without touching the
  ``HumanInterfaceService`` write path.
- Coexists with the pre-existing broadcast_mission_verdict receiver
  (S2734 §1) — this suite proves the two dispatch_uids do not conflict.

Run::

    python manage.py test core.tests.test_mission_verdict_attention -v2
"""
from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings

from core.employees.mission_verdict import (
    VERDICT_CERTIFIED,
    VERDICT_DEFERRED,
    VERDICT_REJECTED,
    emit_mission_verdict,
)
from core.models_ops_runs import OpsRun, OpsRunEvent


_BRIDGE_PATH = (
    "core.services.human_attention_bridge.HumanAttentionBridge."
    "create_mission_verdict_attention"
)


def _make_mission(**overrides) -> OpsRun:
    defaults = dict(
        title="mission-verdict-hai-test",
        run_type="manual",
        domain="mission",
        run_kind="docs_cascade",
        mission_id=uuid.uuid4(),
        status="running",
    )
    defaults.update(overrides)
    return OpsRun.objects.create(**defaults)


def _make_ops_run(**overrides) -> OpsRun:
    defaults = dict(
        title="ops-run-hai-test",
        run_type="ops_loop",
        domain="ops",
        status="running",
    )
    defaults.update(overrides)
    return OpsRun.objects.create(**defaults)


class MissionVerdictAttentionHappyPathTests(TestCase):
    """Rejected and deferred verdicts escalate; certified does not."""

    def test_rejected_verdict_escalates(self):
        mission = _make_mission()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_REJECTED)
        mock_bridge.assert_called_once()
        args = mock_bridge.call_args.args
        dispatched_run, dispatched_verdict = args[0], args[1]
        self.assertEqual(dispatched_run.id, mission.id)
        self.assertEqual(dispatched_verdict, 'rejected')

    def test_deferred_verdict_escalates(self):
        mission = _make_mission()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_DEFERRED)
        mock_bridge.assert_called_once()
        _, dispatched_verdict = mock_bridge.call_args.args[0], mock_bridge.call_args.args[1]
        self.assertEqual(dispatched_verdict, 'deferred')

    def test_certified_verdict_does_not_escalate(self):
        """Certified is success — no HAI needed."""
        mission = _make_mission()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_CERTIFIED)
        mock_bridge.assert_not_called()


class MissionVerdictAttentionFilteringTests(TestCase):
    """Receiver rejects ops-domain / non-verdict / update / kill switch."""

    def test_ops_domain_run_does_not_escalate(self):
        ops = _make_ops_run()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            OpsRunEvent.objects.create(
                run=ops,
                event_type="step_fail",
                label="verdict_issued:rejected",
            )
        mock_bridge.assert_not_called()

    def test_non_verdict_label_does_not_escalate(self):
        mission = _make_mission()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            OpsRunEvent.objects.create(
                run=mission,
                event_type="step_fail",
                label="preflight_ok",
            )
        mock_bridge.assert_not_called()

    def test_update_of_verdict_row_does_not_re_escalate(self):
        mission = _make_mission()
        with patch(_BRIDGE_PATH) as first_bridge, self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_REJECTED)
        first_bridge.assert_called_once()

        verdict_row = OpsRunEvent.objects.get(
            run=mission, label="verdict_issued:rejected"
        )
        with patch(_BRIDGE_PATH) as second_bridge, self.captureOnCommitCallbacks(execute=True):
            verdict_row.detail = {"touched_by_test": True}
            verdict_row.save()
        second_bridge.assert_not_called()

    @override_settings(MISSION_VERDICT_HAI_ENABLED=False)
    def test_kill_switch_disables_escalation(self):
        mission = _make_mission()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_REJECTED)
        mock_bridge.assert_not_called()


class MissionVerdictAttentionTransactionSafetyTests(TestCase):
    """Escalation is scheduled on_commit — no phantom items."""

    def test_rolled_back_transaction_does_not_escalate(self):
        mission = _make_mission()
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=False):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_REJECTED)
        mock_bridge.assert_not_called()


class MissionVerdictAttentionCoexistenceTests(TestCase):
    """Both broadcast + HAI receivers fire on the same OpsRunEvent row."""

    def test_broadcast_failure_does_not_prevent_hai(self):
        """Failure isolation (Rigby SIGN PC-006 Q4 refinement fold):
        if the WS broadcast side raises, the HAI receiver must still
        fire and vice versa. Both are wrapped in try/except inside
        their own ``_broadcast_verdict`` / ``_create_attention``
        helpers so the exception is swallowed locally — but the
        on_commit callbacks are registered independently, proving
        isolation.
        """
        mission = _make_mission()
        broadcast_path = (
            "core.consumers.system_events_consumer.emit_system_event_sync"
        )
        with patch(broadcast_path, side_effect=Exception("boom")) as mock_broadcast, \
             patch(_BRIDGE_PATH) as mock_bridge, \
             self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_REJECTED)
        # Broadcast was called (and raised); the internal try/except
        # in _broadcast_verdict swallowed it so save() completed.
        mock_broadcast.assert_called_once()
        # HAI bridge still fired — isolation proved.
        mock_bridge.assert_called_once()

    def test_hai_failure_does_not_prevent_broadcast(self):
        """Symmetric isolation: HAI bridge failure must not prevent
        WS broadcast on the same OpsRunEvent row.
        """
        mission = _make_mission()
        broadcast_path = (
            "core.consumers.system_events_consumer.emit_system_event_sync"
        )
        with patch(_BRIDGE_PATH, side_effect=Exception("boom")) as mock_bridge, \
             patch(broadcast_path) as mock_broadcast, \
             self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_REJECTED)
        mock_bridge.assert_called_once()
        mock_broadcast.assert_called_once()

    def test_ws_broadcast_and_hai_both_fire_on_rejected(self):
        """The pre-existing broadcast_mission_verdict receiver (S2734
        §1) uses one dispatch_uid; this suite's escalate_mission_verdict_to_hai
        uses another. Both must fire independently on the same row.
        """
        mission = _make_mission()
        broadcast_path = (
            "core.consumers.system_events_consumer.emit_system_event_sync"
        )
        with patch(_BRIDGE_PATH) as mock_bridge, \
             patch(broadcast_path) as mock_broadcast, \
             self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_REJECTED)
        mock_bridge.assert_called_once()
        mock_broadcast.assert_called_once()
        event_name, payload = mock_broadcast.call_args.args
        self.assertEqual(event_name, "mission_verdict")
        self.assertEqual(payload["verdict"], "rejected")
