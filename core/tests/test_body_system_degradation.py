"""
Regression tests for Session 2734 — Capability Chain §14 Platform Health.

Exercises ``core.signals.body_system_degradation_signals.escalate_body_system_degradation``:
the post_save receiver on ``HeartBeat`` that escalates
``overall_status in {'critical', 'offline'}`` to
``HumanAttentionItem`` via ``HumanAttentionBridge`` with a 1-hour
dedup gate.

Test discipline:
- Real DB. No mocked querysets.
- ``HumanAttentionBridge.create_body_system_degradation_attention``
  is patched so we assert the *receiver's* contract (status filter,
  dedup, kill switch, on_commit gating) without touching the
  ``HumanInterfaceService`` write path.
- Uses ``captureOnCommitCallbacks(execute=True)`` because the
  receiver schedules the escalation via ``transaction.on_commit``.

Run::

    python manage.py test core.tests.test_body_system_degradation -v2
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_heart import HeartBeat
from core.models_human_interface import HumanAttentionItem

User = get_user_model()


def _admin_user():
    """Return a persistent admin user for HAI rows in dedup tests."""
    user, _ = User.objects.get_or_create(
        username='dedup-fixture-admin',
        defaults={'is_staff': True, 'is_active': True},
    )
    return user


_BRIDGE_PATH = (
    "core.services.human_attention_bridge.HumanAttentionBridge."
    "create_body_system_degradation_attention"
)


def _make_heartbeat(**overrides) -> HeartBeat:
    defaults = dict(
        health_score=25.0,
        overall_status='critical',
        is_alive=True,
        components={'brain': {'status': 'critical'}, 'organs': {'status': 'healthy'}},
        check_duration_ms=120,
        components_checked=6,
        components_healthy=3,
    )
    defaults.update(overrides)
    return HeartBeat.objects.create(**defaults)


class BodySystemDegradationHappyPathTests(TestCase):
    """Critical and offline statuses escalate exactly once."""

    def test_critical_status_escalates(self):
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            heartbeat = _make_heartbeat(overall_status='critical', health_score=25.0)
        mock_bridge.assert_called_once()
        (dispatched,) = mock_bridge.call_args.args
        self.assertEqual(dispatched.id, heartbeat.id)
        self.assertEqual(dispatched.overall_status, 'critical')

    def test_offline_status_escalates(self):
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_heartbeat(overall_status='offline', is_alive=False, health_score=0.0)
        mock_bridge.assert_called_once()


class BodySystemDegradationFilteringTests(TestCase):
    """Receiver rejects healthy / degraded / update / kill switch."""

    def test_healthy_status_does_not_escalate(self):
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_heartbeat(overall_status='healthy', health_score=95.0)
        mock_bridge.assert_not_called()

    def test_degraded_status_does_not_escalate(self):
        """Degraded is intentionally excluded — audit §2.2 wants only
        wake-someone-up states in the inbox to avoid ~144-per-day noise.
        """
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_heartbeat(overall_status='degraded', health_score=65.0)
        mock_bridge.assert_not_called()

    def test_update_of_existing_heartbeat_does_not_escalate(self):
        """The receiver requires ``created=True``. Editing an existing
        HeartBeat (rare in practice — HeartBeat rows are effectively
        immutable) must not re-fire the escalation.
        """
        with patch(_BRIDGE_PATH) as first_bridge, self.captureOnCommitCallbacks(execute=True):
            heartbeat = _make_heartbeat(overall_status='healthy', health_score=95.0)
        first_bridge.assert_not_called()

        with patch(_BRIDGE_PATH) as second_bridge, self.captureOnCommitCallbacks(execute=True):
            heartbeat.overall_status = 'critical'
            heartbeat.health_score = 10.0
            heartbeat.save()
        second_bridge.assert_not_called()

    @override_settings(BODY_SYSTEM_DEGRADATION_HAI_ENABLED=False)
    def test_kill_switch_disables_escalation(self):
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_heartbeat(overall_status='critical', health_score=10.0)
        mock_bridge.assert_not_called()


class BodySystemDegradationDedupTests(TestCase):
    """1-hour dedup gate prevents duplicate HAI on persistent critical."""

    def test_recent_open_hai_suppresses_escalation(self):
        """Simulate an existing open HAI from 30 min ago — the receiver
        must NOT dispatch a second escalation.
        """
        # Insert a synthetic open HAI 30 min in the past.
        past = timezone.now() - timedelta(minutes=30)
        HumanAttentionItem.objects.create(
            user=_admin_user(),
            source_type='body_system_degradation',
            source_id='synthetic',
            source_agent='BodyCoordinator',
            item_type='alert',
            title='pre-existing critical',
            summary='pre-existing open HAI within 1h window',
            urgency='critical',
        )
        HumanAttentionItem.objects.filter(source_id='synthetic').update(created_at=past)

        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_heartbeat(overall_status='critical', health_score=10.0)
        mock_bridge.assert_not_called()

    def test_stale_open_hai_beyond_window_does_not_suppress(self):
        """An open HAI from 2h ago is beyond the dedup window — new
        critical HeartBeat must still escalate.
        """
        past = timezone.now() - timedelta(hours=2)
        HumanAttentionItem.objects.create(
            user=_admin_user(),
            source_type='body_system_degradation',
            source_id='synthetic-stale',
            source_agent='BodyCoordinator',
            item_type='alert',
            title='stale critical',
            summary='beyond 1h window',
            urgency='critical',
        )
        HumanAttentionItem.objects.filter(source_id='synthetic-stale').update(created_at=past)

        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_heartbeat(overall_status='critical', health_score=10.0)
        mock_bridge.assert_called_once()

    def test_decided_hai_does_not_suppress(self):
        """A decided (closed) HAI must NOT suppress a new critical
        escalation even if it is within the 1h window — the whole point
        of the dedup is 'don't page the user twice for the SAME open
        incident', not 'don't page them at all today'.
        """
        HumanAttentionItem.objects.create(
            user=_admin_user(),
            source_type='body_system_degradation',
            source_id='synthetic-decided',
            source_agent='BodyCoordinator',
            item_type='alert',
            title='decided critical',
            summary='already handled',
            urgency='critical',
            decided_at=timezone.now() - timedelta(minutes=10),
        )

        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_heartbeat(overall_status='critical', health_score=10.0)
        mock_bridge.assert_called_once()


class BodySystemDegradationTransactionSafetyTests(TestCase):
    """Escalation is scheduled on_commit — no phantom items."""

    def test_rolled_back_transaction_does_not_escalate(self):
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=False):
            _make_heartbeat(overall_status='critical', health_score=10.0)
        mock_bridge.assert_not_called()

    def test_dedup_lookup_failure_defaults_to_escalation(self):
        """If the ``HumanAttentionItem.objects.filter`` call raises
        (simulated DB failure), ``_open_hai_exists_within_window``
        returns False and the receiver escalates. Safer to duplicate
        than to swallow a critical alert.
        """
        raising_manager = MagicMock()
        raising_manager.filter.side_effect = Exception("simulated DB failure")

        with patch(
            "core.models_human_interface.HumanAttentionItem.objects",
            new=raising_manager,
        ):
            with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
                _make_heartbeat(overall_status='critical', health_score=10.0)
        mock_bridge.assert_called_once()
