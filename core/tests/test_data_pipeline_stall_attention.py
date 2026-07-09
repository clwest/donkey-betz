"""
Regression tests for Session 2735 — Platform Closure §5 Spider Discovery Item 14.

Exercises the data_pipeline_stall escalation chain built on top of the
pre-existing BodyCoordinator autonomic-reflex layer:

    digestive.check_intake() → 'starving' status (spider drought)
      → BodyCoordinator._detect_digestive_events
      → CoordinationEvent(DIGESTIVE_BLOCKED, severity='critical')
      → BodyCoordinator._handle_digestive_blocked
      → Discord alert path (pre-existing)
      → HumanAttentionBridge.create_data_pipeline_stall_attention (Session 2735)
      → HumanAttentionItem(source_type='data_pipeline_stall', urgency='critical')

Test discipline:

* Real DB. No mocked querysets.
* Exercises ``BodyCoordinator._handle_digestive_blocked`` directly with
  a synthetic ``CoordinationEvent`` so we don't need to run the full
  autonomic tick (which spins up 9 body systems + Discord + queue
  telemetry). The handler contract is:

    1. Send Discord alert (mocked).
    2. If kill switch on AND no open HAI in dedup window → dispatch to
       ``HumanAttentionBridge.create_data_pipeline_stall_attention``.
    3. Return actions list including the HAI-dispatch action string.

* Uses the real ``HumanInterfaceService`` write path — bridge dispatch
  is asserted end-to-end so a genuine ``HumanAttentionItem`` row lands.

Run::

    python manage.py test core.tests.test_data_pipeline_stall_attention -v2
"""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_human_interface import HumanAttentionItem
from core.services.body_coordinator import (
    BodyCoordinator,
    CoordinationEvent,
    CoordinationEventType,
)

User = get_user_model()


def _admin_user():
    user, _ = User.objects.get_or_create(
        username='data-pipeline-stall-fixture-admin',
        defaults={'is_staff': True, 'is_active': True},
    )
    return user


def _stall_event(
    *,
    status: str = 'starving',
    items_pending: int = 0,
    items_24h: int = 0,
    recent_intake: int = 0,
    when: datetime | None = None,
) -> CoordinationEvent:
    """Construct a synthetic DIGESTIVE_BLOCKED event.

    Mirrors ``BodyCoordinator._detect_digestive_events`` line 468 shape,
    plus optional items_24h / recent_intake fields the Session 2735
    handler consumes to enrich the HAI payload.
    """
    return CoordinationEvent(
        event_type=CoordinationEventType.DIGESTIVE_BLOCKED,
        source_system='digestive',
        severity='critical',
        message=f'Data pipeline {status}',
        data={
            'status': status,
            'items_pending': items_pending,
            'items_24h': items_24h,
            'recent_intake': recent_intake,
        },
        timestamp=when or timezone.now(),
    )


class DataPipelineStallHappyPathTests(TestCase):
    """Handler dispatches HAI when DIGESTIVE_BLOCKED fires and dedup is clean."""

    def setUp(self):
        _admin_user()
        self.bc = BodyCoordinator()

    def test_starving_creates_hai(self):
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ) as discord:
            actions = self.bc._handle_digestive_blocked(
                _stall_event(
                    status='starving',
                    items_24h=42,
                    recent_intake=0,
                )
            )
        discord.assert_called_once()
        self.assertIn('Sent pipeline blocked alert', actions)
        self.assertIn('Created data_pipeline_stall HumanAttentionItem', actions)

        hai = HumanAttentionItem.objects.filter(
            source_type='data_pipeline_stall',
        ).first()
        self.assertIsNotNone(hai)
        self.assertEqual(hai.urgency, 'critical')
        self.assertEqual(hai.payload['digestive_status'], 'starving')
        self.assertEqual(hai.payload['items_24h'], 42)
        self.assertEqual(hai.payload['recent_intake'], 0)
        self.assertTrue(
            hai.payload['idempotency_key'].startswith(
                'data_pipeline_stall:'
            )
        )
        self.assertTrue(
            hai.payload['idempotency_key'].endswith(':starving')
        )
        self.assertEqual(hai.source_id, hai.payload['idempotency_key'])

    def test_blocked_creates_hai(self):
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ) as discord:
            actions = self.bc._handle_digestive_blocked(
                _stall_event(
                    status='blocked',
                    items_pending=1500,
                    recent_intake=3,
                )
            )
        discord.assert_called_once()
        hai = HumanAttentionItem.objects.filter(
            source_type='data_pipeline_stall',
        ).first()
        self.assertIsNotNone(hai)
        self.assertEqual(hai.payload['digestive_status'], 'blocked')
        self.assertEqual(hai.payload['items_pending'], 1500)
        self.assertEqual(hai.payload['recent_intake'], 3)


class DataPipelineStallFilteringTests(TestCase):
    """Kill switch off, missing data → HAI does not fire."""

    def setUp(self):
        _admin_user()
        self.bc = BodyCoordinator()

    @override_settings(DATA_PIPELINE_STALL_HAI_ENABLED=False)
    def test_kill_switch_disables_hai(self):
        """Discord alert still fires; HAI dispatch skipped."""
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ) as discord:
            actions = self.bc._handle_digestive_blocked(_stall_event())
        discord.assert_called_once()
        self.assertNotIn(
            'Created data_pipeline_stall HumanAttentionItem', actions
        )
        self.assertEqual(
            HumanAttentionItem.objects.filter(
                source_type='data_pipeline_stall'
            ).count(),
            0,
        )

    def test_bridge_failure_does_not_break_handler(self):
        """A raising bridge dispatch must NOT break the handler — the
        autonomic reflex tick has to keep going."""
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ):
            with patch(
                'core.services.human_attention_bridge.HumanAttentionBridge.'
                'create_data_pipeline_stall_attention',
                side_effect=Exception('synthetic bridge failure'),
            ):
                # Should not raise
                actions = self.bc._handle_digestive_blocked(_stall_event())
        self.assertIn(
            'Signaled spider coordinator to pause execution', actions
        )


class DataPipelineStallDedupTests(TestCase):
    """1-hour dedup prevents 6x duplicate HAI across persistent-critical hour."""

    def setUp(self):
        _admin_user()
        self.bc = BodyCoordinator()

    def _synthetic_hai(
        self,
        *,
        created_ago: timedelta,
        decided: bool = False,
    ) -> HumanAttentionItem:
        item = HumanAttentionItem.objects.create(
            user=_admin_user(),
            source_type='data_pipeline_stall',
            source_id='synthetic',
            source_agent='BodyCoordinator',
            item_type='alert',
            title='synthetic prior stall',
            summary='prior open stall HAI',
            urgency='critical',
            payload={
                'digestive_status': 'starving',
                'idempotency_key': 'data_pipeline_stall:synthetic:starving',
            },
            decided_at=timezone.now() - timedelta(minutes=1) if decided else None,
        )
        HumanAttentionItem.objects.filter(id=item.id).update(
            created_at=timezone.now() - created_ago,
        )
        return item

    def test_recent_open_hai_suppresses(self):
        self._synthetic_hai(created_ago=timedelta(minutes=30))
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ):
            actions = self.bc._handle_digestive_blocked(_stall_event())
        self.assertIn(
            'Skipped HAI dispatch — open data_pipeline_stall attention '
            'already present within 1h dedup window',
            actions,
        )
        # Only the synthetic remains — no new HAI was created.
        self.assertEqual(
            HumanAttentionItem.objects.filter(
                source_type='data_pipeline_stall',
            ).count(),
            1,
        )

    def test_stale_open_hai_beyond_window_does_not_suppress(self):
        self._synthetic_hai(created_ago=timedelta(hours=2))
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ):
            actions = self.bc._handle_digestive_blocked(_stall_event())
        self.assertIn(
            'Created data_pipeline_stall HumanAttentionItem', actions
        )
        self.assertEqual(
            HumanAttentionItem.objects.filter(
                source_type='data_pipeline_stall',
            ).count(),
            2,
        )

    def test_decided_hai_does_not_suppress(self):
        self._synthetic_hai(created_ago=timedelta(minutes=15), decided=True)
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ):
            actions = self.bc._handle_digestive_blocked(_stall_event())
        self.assertIn(
            'Created data_pipeline_stall HumanAttentionItem', actions
        )
        self.assertEqual(
            HumanAttentionItem.objects.filter(
                source_type='data_pipeline_stall',
            ).count(),
            2,
        )

    def test_dedup_lookup_failure_defaults_to_escalation(self):
        """A raising HumanAttentionItem.objects from the dedup gate
        must NOT swallow the escalation — safer to duplicate than to
        miss a critical alert."""
        raising_manager = MagicMock()
        raising_manager.filter.side_effect = Exception('simulated DB failure')

        with patch(
            'core.services.discord_notifications.send_status_notification'
        ):
            with patch(
                'core.models_human_interface.HumanAttentionItem.objects',
                new=raising_manager,
            ):
                actions = self.bc._handle_digestive_blocked(_stall_event())
        self.assertIn(
            'Created data_pipeline_stall HumanAttentionItem', actions
        )


class DataPipelineStallIdempotencyKeyTests(TestCase):
    """Window bucket rounds to the hour → same key across multiple ticks
    inside the same clock hour."""

    def setUp(self):
        _admin_user()
        self.bc = BodyCoordinator()

    def test_bucket_hour_precision(self):
        """Two events in the same hour → the bridge is called with the
        same idempotency_key. Proves the dedup key would collide on
        retries even if the coordinator-side dedup gate misses.

        The service-layer upsert on ``source_id`` (which we set to the
        idempotency_key) also collapses same-key items, so only one
        DB row survives across the two calls.
        """
        base = timezone.now().replace(minute=5, second=0, microsecond=0)
        e1 = _stall_event(when=base)
        e2 = _stall_event(when=base + timedelta(minutes=30))
        bridge_path = (
            'core.services.human_attention_bridge.HumanAttentionBridge.'
            'create_data_pipeline_stall_attention'
        )
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ):
            with patch(bridge_path) as mock_bridge:
                self.bc._handle_digestive_blocked(e1)
                # First dispatch already opened a HAI — clear it so the
                # coordinator-side dedup gate doesn't block dispatch #2.
                HumanAttentionItem.objects.all().delete()
                self.bc._handle_digestive_blocked(e2)

        self.assertEqual(mock_bridge.call_count, 2)
        b1 = mock_bridge.call_args_list[0].kwargs['window_bucket']
        b2 = mock_bridge.call_args_list[1].kwargs['window_bucket']
        self.assertEqual(b1, b2)

    def test_bucket_hour_boundary(self):
        """Events in different hours → distinct window_bucket."""
        base = timezone.now().replace(minute=5, second=0, microsecond=0)
        e_hour_a = _stall_event(when=base)
        e_hour_b = _stall_event(when=base + timedelta(hours=2))
        bridge_path = (
            'core.services.human_attention_bridge.HumanAttentionBridge.'
            'create_data_pipeline_stall_attention'
        )
        with patch(
            'core.services.discord_notifications.send_status_notification'
        ):
            with patch(bridge_path) as mock_bridge:
                self.bc._handle_digestive_blocked(e_hour_a)
                HumanAttentionItem.objects.all().delete()
                self.bc._handle_digestive_blocked(e_hour_b)

        self.assertEqual(mock_bridge.call_count, 2)
        b1 = mock_bridge.call_args_list[0].kwargs['window_bucket']
        b2 = mock_bridge.call_args_list[1].kwargs['window_bucket']
        self.assertNotEqual(b1, b2)
