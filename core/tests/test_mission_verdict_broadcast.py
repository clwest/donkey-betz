"""
Regression tests for Session 2734 — Capability Chain §1 Mission Completion.

Exercises ``core.signals.mission_verdict_signals.broadcast_mission_verdict``:
the post_save receiver on ``OpsRunEvent`` that emits a ``mission_verdict``
system event when a MissionRunner writes a terminal verdict.

Test discipline:
- Real DB. No mocked querysets.
- ``emit_system_event_sync`` is patched so we assert the *receiver's*
  contract (label parsing, payload shape, on_commit gating) without
  needing a live channel layer.
- Uses ``captureOnCommitCallbacks(execute=True)`` because the receiver
  schedules the broadcast via ``transaction.on_commit`` — under
  ``TestCase`` the outer transaction is rolled back so on_commit
  callbacks are never invoked unless explicitly captured.

Chain being tested:

    emit_mission_verdict(mission_id=..., verdict='certified')
    → OpsRunEvent(label='verdict_issued:certified')  [pre-existing]
    → broadcast_mission_verdict  [new — this file]
    → emit_system_event_sync('mission_verdict', payload)  [asserted here]
    → SystemEventsConsumer 'mission_verdict' handler  [not exercised in unit test]
    → Frontend NowHub invalidates ['active-work']  [not exercised in unit test]

Run::

    python manage.py test core.tests.test_mission_verdict_broadcast -v2
"""
from __future__ import annotations

import uuid
from unittest.mock import patch

from django.test import TestCase

from core.employees.mission_verdict import (
    VERDICT_CERTIFIED,
    VERDICT_DEFERRED,
    VERDICT_REJECTED,
    emit_mission_verdict,
)
from core.models_ops_runs import OpsRun, OpsRunEvent


_EMIT_PATH = "core.consumers.system_events_consumer.emit_system_event_sync"


def _make_mission(**overrides) -> OpsRun:
    defaults = dict(
        title="mission-verdict-broadcast-test",
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
        title="ops-run-broadcast-test",
        run_type="ops_loop",
        domain="ops",
        status="running",
    )
    defaults.update(overrides)
    return OpsRun.objects.create(**defaults)


class BroadcastMissionVerdictHappyPathTests(TestCase):
    """The receiver fires for each of the 3 mission verdicts."""

    def _run_and_capture(self, verdict: str):
        mission = _make_mission()
        with patch(_EMIT_PATH) as mock_emit, self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=verdict)
        return mission, mock_emit

    def test_certified_verdict_broadcasts(self):
        mission, mock_emit = self._run_and_capture(VERDICT_CERTIFIED)
        mock_emit.assert_called_once()
        event_name, payload = mock_emit.call_args.args
        self.assertEqual(event_name, "mission_verdict")
        self.assertEqual(payload["verdict"], "certified")
        self.assertEqual(payload["mission_id"], str(mission.mission_id))
        self.assertEqual(payload["run_id"], str(mission.id))
        self.assertEqual(payload["label"], "verdict_issued:certified")

    def test_rejected_verdict_broadcasts(self):
        _mission, mock_emit = self._run_and_capture(VERDICT_REJECTED)
        mock_emit.assert_called_once()
        _event_name, payload = mock_emit.call_args.args
        self.assertEqual(payload["verdict"], "rejected")

    def test_deferred_verdict_broadcasts(self):
        _mission, mock_emit = self._run_and_capture(VERDICT_DEFERRED)
        mock_emit.assert_called_once()
        _event_name, payload = mock_emit.call_args.args
        self.assertEqual(payload["verdict"], "deferred")


class BroadcastMissionVerdictFilteringTests(TestCase):
    """The receiver ignores anything that isn't a mission-domain verdict."""

    def test_ops_domain_run_does_not_broadcast(self):
        """An ops-loop OpsRun that writes ``verdict_issued:*`` (defensive
        edge case — no known caller does this today) must not trigger the
        mission-verdict broadcast. Mission-verdict is a mission-domain
        capability, not an ops-domain one.
        """
        ops = _make_ops_run()
        with patch(_EMIT_PATH) as mock_emit, self.captureOnCommitCallbacks(execute=True):
            OpsRunEvent.objects.create(
                run=ops,
                event_type="step_pass",
                label="verdict_issued:certified",
            )
        mock_emit.assert_not_called()

    def test_non_verdict_label_does_not_broadcast(self):
        """The receiver filters on ``label.startswith('verdict_issued:')`` — a
        plain ``step_pass`` / ``step_fail`` event on a mission run must not
        broadcast. MissionRunner writes many such events per mission; only
        the terminal verdict should reach the WS layer.
        """
        mission = _make_mission()
        with patch(_EMIT_PATH) as mock_emit, self.captureOnCommitCallbacks(execute=True):
            OpsRunEvent.objects.create(
                run=mission,
                event_type="step_pass",
                label="preflight_ok",
            )
            OpsRunEvent.objects.create(
                run=mission,
                event_type="step_pass",
                label="postflight_summary",
            )
        mock_emit.assert_not_called()

    def test_blank_label_does_not_broadcast(self):
        """Line 70 of the receiver: ``label = getattr(instance, "label", "") or ""``.
        A blank / missing label must return silently — no broadcast, no
        raised exception. Added per Rigby SIGN Q4 refinement (pin
        pa-61d34c7bfd4749f4).
        """
        mission = _make_mission()
        with patch(_EMIT_PATH) as mock_emit, self.captureOnCommitCallbacks(execute=True):
            # ``OpsRunEvent.label`` is a CharField; empty string is the
            # closest realistic edge case at the ORM boundary.
            OpsRunEvent.objects.create(
                run=mission,
                event_type="info",
                label="",
            )
        mock_emit.assert_not_called()

    def test_updating_verdict_row_does_not_re_broadcast(self):
        """The receiver requires ``created=True``. Idempotency:
        ``emit_mission_verdict`` re-called for the same (run, label)
        no-ops at the model layer, but the raw update path must also not
        re-fire the WS event even if a caller edits the row directly.
        """
        mission = _make_mission()
        with patch(_EMIT_PATH) as first_emit, self.captureOnCommitCallbacks(execute=True):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_CERTIFIED)
        first_emit.assert_called_once()

        # Now touch the existing row — receiver should not fire.
        verdict_row = OpsRunEvent.objects.get(
            run=mission, label="verdict_issued:certified"
        )
        with patch(_EMIT_PATH) as second_emit, self.captureOnCommitCallbacks(execute=True):
            verdict_row.detail = {"touched_by_test": True}
            verdict_row.save()
        second_emit.assert_not_called()


class BroadcastMissionVerdictTransactionSafetyTests(TestCase):
    """The broadcast is scheduled on_commit — no phantom events."""

    def test_rolled_back_transaction_does_not_broadcast(self):
        """If ``captureOnCommitCallbacks`` is used WITHOUT execute=True
        the callbacks are captured but not fired — mirroring what happens
        when the outer transaction rolls back. Under that condition the
        broadcast must not fire.
        """
        mission = _make_mission()
        with patch(_EMIT_PATH) as mock_emit, self.captureOnCommitCallbacks(execute=False):
            emit_mission_verdict(mission_id=mission.id, verdict=VERDICT_CERTIFIED)
        mock_emit.assert_not_called()
