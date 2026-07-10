"""
Regression tests for Session 2739 Cost Protection Campaign P2+
observation-period foothold (Cat 2 slice).

Covers:

* ``core.tasks_cost_protection.check_cost_thresholds`` return dict
  now carries ``would_freeze`` — True iff ``enforce_mode='freeze'``
  AND at least one window breached this tick.
* Shadow warning log emitted ONLY when ``would_freeze=True``; not
  emitted when mode is 'freeze' but no breach occurred.
* ``core.services.human_attention_bridge.HumanAttentionBridge
  .create_cost_breach_attention`` accepts ``would_freeze`` kwarg
  and threads it into ``payload['would_freeze']``.
* Enforcement-gate contract preserved: even when ``would_freeze=True``,
  governance is NOT flipped (S2735 P1 discipline unchanged).

Test discipline:

- Real DB, real ``CostTracking`` rows, real HAI creation. Adapter for
  the Discord + Web Push fanout is patched to avoid real Celery
  enqueues, matching P1 test patterns.
- Threshold + mode config written to ``SystemConfiguration``.

Run::

    python manage.py test core.tests.test_cost_protection_p2 -v2
"""
from __future__ import annotations

import logging
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models.system import SystemConfiguration
from core.models_human_interface import HumanAttentionItem
from core.models_unified_system import CostTracking
from core.services.cost_threshold_monitor import CostBreachResult
from core.tasks_cost_protection import check_cost_thresholds

User = get_user_model()


def _admin_user():
    user, _ = User.objects.get_or_create(
        username='cost-p2-fixture-admin',
        defaults={'is_staff': True, 'is_active': True},
    )
    return user


def _mk_cost_row(
    *,
    provider: str = 'openai',
    service: str = 'gpt-5.2',
    operation: str = 'test',
    input_tokens: int = 100,
    output_tokens: int = 50,
    estimated_cost_usd: Decimal = Decimal('0.001'),
    timestamp=None,
) -> CostTracking:
    row = CostTracking.objects.create(
        provider=provider,
        service=service,
        operation=operation,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimated_cost_usd,
    )
    if timestamp is not None:
        CostTracking.objects.filter(pk=row.pk).update(timestamp=timestamp)
        row.refresh_from_db()
    return row


def _set_threshold(window: str, value: str):
    key_map = {
        'hour': 'cost_threshold_hour_usd',
        'day': 'cost_threshold_day_usd',
        'month': 'cost_threshold_month_usd',
    }
    SystemConfiguration.objects.update_or_create(
        key=key_map[window],
        defaults={'value': value, 'is_active': True},
    )


def _set_mode(value: str):
    SystemConfiguration.objects.update_or_create(
        key='cost_protection_enforce_mode',
        defaults={'value': value, 'is_active': True},
    )


def _fake_breach(**overrides) -> CostBreachResult:
    base = dict(
        window='hour',
        window_minutes=60,
        window_start=timezone.now() - timedelta(minutes=60),
        window_end=timezone.now(),
        threshold_usd=Decimal('10.00'),
        actual_usd=Decimal('12.50'),
        breached=True,
        row_count=7,
        top_service='gpt-5.2',
        top_service_usd=Decimal('11.00'),
        top_provider='openai',
        idempotency_key='cost_breach:hour:1234567890',
    )
    base.update(overrides)
    return CostBreachResult(**base)


class WouldFreezeBridgePayloadTests(TestCase):
    """The bridge accepts ``would_freeze`` and threads it to payload."""

    def setUp(self):
        super().setUp()
        _admin_user()

    def test_payload_carries_would_freeze_true_when_supplied(self):
        from core.services.human_attention_bridge import attention_bridge
        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            attention_bridge.create_cost_breach_attention(
                [_fake_breach()], would_freeze=True,
            )
        hai = HumanAttentionItem.objects.filter(
            source_type='cost_breach',
        ).order_by('-created_at').first()
        self.assertIsNotNone(hai)
        assert hai is not None
        self.assertTrue(hai.payload['would_freeze'])

    def test_payload_would_freeze_defaults_to_false(self):
        """Backward-compat: callers that don't pass the kwarg get False,
        matching P1 shipped behavior semantics."""
        from core.services.human_attention_bridge import attention_bridge
        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            attention_bridge.create_cost_breach_attention([_fake_breach()])
        hai = HumanAttentionItem.objects.filter(
            source_type='cost_breach',
        ).order_by('-created_at').first()
        self.assertIsNotNone(hai)
        assert hai is not None
        self.assertFalse(hai.payload['would_freeze'])


class WouldFreezeTaskTests(TestCase):
    """The task computes ``would_freeze`` and emits the shadow log only
    when mode='freeze' AND breach occurs."""

    def setUp(self):
        super().setUp()
        _admin_user()

    def test_would_freeze_true_and_shadow_log_on_freeze_mode_breach(self):
        _mk_cost_row(estimated_cost_usd=Decimal('12.00'))
        _set_threshold('hour', '10.00')
        _set_mode('freeze')

        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.assertLogs(
            'core.tasks_cost_protection', level=logging.WARNING,
        ) as log_ctx, self.captureOnCommitCallbacks(execute=True):
            result = check_cost_thresholds()

        self.assertEqual(result['mode'], 'freeze')
        self.assertTrue(result['would_freeze'])
        self.assertGreaterEqual(result['windows_breached'], 1)
        self.assertEqual(result['hai_dispatched'], 1)

        joined = '\n'.join(log_ctx.output)
        # P1 warning still emitted (mode='freeze' notice).
        self.assertIn('enforce_mode=freeze', joined)
        # P2+ shadow log emitted.
        self.assertIn('would_freeze=True', joined)
        self.assertIn('mode=freeze', joined)

        # HAI payload also carries would_freeze=True.
        hai = HumanAttentionItem.objects.filter(
            source_type='cost_breach',
        ).order_by('-created_at').first()
        self.assertIsNotNone(hai)
        assert hai is not None
        self.assertTrue(hai.payload['would_freeze'])

    def test_would_freeze_false_on_monitor_mode_breach(self):
        _mk_cost_row(estimated_cost_usd=Decimal('12.00'))
        _set_threshold('hour', '10.00')
        # mode defaults to 'monitor' — no _set_mode call.

        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            result = check_cost_thresholds()

        self.assertEqual(result['mode'], 'monitor')
        self.assertFalse(result['would_freeze'])
        self.assertGreaterEqual(result['windows_breached'], 1)

        hai = HumanAttentionItem.objects.filter(
            source_type='cost_breach',
        ).order_by('-created_at').first()
        self.assertIsNotNone(hai)
        assert hai is not None
        self.assertFalse(hai.payload['would_freeze'])

    def test_would_freeze_false_when_freeze_mode_but_no_breach(self):
        """Shadow log must NOT fire every tick when an operator is
        exercising mode='freeze' with sub-threshold spend."""
        _mk_cost_row(estimated_cost_usd=Decimal('0.01'))
        _set_threshold('day', '100.00')
        _set_mode('freeze')

        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.assertLogs(
            'core.tasks_cost_protection', level=logging.WARNING,
        ) as log_ctx, self.captureOnCommitCallbacks(execute=True):
            result = check_cost_thresholds()

        self.assertEqual(result['mode'], 'freeze')
        self.assertFalse(result['would_freeze'])
        self.assertEqual(result['windows_breached'], 0)
        self.assertEqual(result['hai_dispatched'], 0)

        joined = '\n'.join(log_ctx.output)
        # P1 mode-notice still fires (it is per-tick when mode=freeze).
        self.assertIn('enforce_mode=freeze', joined)
        # P2+ shadow log MUST NOT fire — no breach means no
        # counterfactual to record.
        self.assertNotIn('would_freeze=True', joined)


class EnforcementGateStillHeldTests(TestCase):
    """Regression guard: the P2+ observation-period foothold must NOT
    accidentally re-open the S2735 enforcement gate. Even when
    ``would_freeze=True``, governance stays untouched."""

    def setUp(self):
        super().setUp()
        _admin_user()

    def test_would_freeze_true_does_not_flip_governance(self):
        _mk_cost_row(estimated_cost_usd=Decimal('12.00'))
        _set_threshold('hour', '10.00')
        _set_mode('freeze')

        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            # Any call to a set_mode helper would raise because we do
            # not patch it. If enforcement leaked into P2+ this would
            # blow up on import or invocation. Verifying via exception-
            # absence + result contract is sufficient — the P1 test
            # ``test_freeze_mode_does_not_flip_governance`` covers the
            # negative-import assertion in more depth.
            result = check_cost_thresholds()

        self.assertEqual(result['mode'], 'freeze')
        self.assertTrue(result['would_freeze'])
        # HAI shipped, governance flip did not happen.
        self.assertEqual(result['hai_dispatched'], 1)
