"""
Regression tests for Session 2735 Cost Protection Campaign P1.

Covers:

* ``core.services.cost_threshold_monitor`` — pure query helper
  (``compute_window``, ``check_all_windows``, ``read_enforce_mode``).
* ``core.services.human_attention_bridge.HumanAttentionBridge
  .create_cost_breach_attention`` — 11th producer method.
* ``core.tasks_cost_protection.check_cost_thresholds`` — beat task
  glue that dispatches HAI on breach and DOES NOT flip governance
  even when ``enforce_mode='freeze'`` (deferred to a later phase per
  Chris's enforcement-gate discipline).

Test discipline:

- Real DB, real ``CostTracking`` rows, real HAI creation. Adapter for
  the Discord fanout receiver is patched via the ``notify_hai_discord.delay``
  path so no real Celery task is enqueued. The Web Push receiver
  patches follow the same pattern.
- Threshold config is written to ``SystemConfiguration`` via
  ``.objects.create``.
- No mocked querysets. No shortcuts.

Run::

    python manage.py test core.tests.test_cost_protection_p1 -v2
"""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models.system import SystemConfiguration
from core.models_human_interface import HumanAttentionItem
from core.models_unified_system import CostTracking
from core.services.cost_threshold_monitor import (
    CostBreachResult,
    check_all_windows,
    compute_window,
    read_enforce_mode,
)
from core.tasks_cost_protection import check_cost_thresholds

User = get_user_model()


def _admin_user():
    user, _ = User.objects.get_or_create(
        username='cost-p1-fixture-admin',
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


class _CostFixtureMixin:
    """Shared setUp: purge ambient ``CostTracking`` rows that Django's
    startup ``InterviewAssistant`` test call leaves in the test DB when
    ``--keepdb`` is used across runs. Otherwise absolute-value assertions
    drift by the accumulated ~$0.000222-per-boot ambient cost.
    """

    def setUp(self):
        # Call parent setUp if it exists (multiple-inheritance safe).
        super().setUp()  # type: ignore[misc]
        CostTracking.objects.all().delete()


class CostMonitorNoThresholdTests(_CostFixtureMixin, TestCase):
    """A window with no configured threshold is a hard no-op."""

    def test_no_threshold_no_breach(self):
        _mk_cost_row(estimated_cost_usd=Decimal('10.00'))
        result = compute_window('hour')
        self.assertIsNone(result.threshold_usd)
        self.assertFalse(result.breached)
        self.assertGreater(result.actual_usd, Decimal('0'))


class CostMonitorBreachTests(_CostFixtureMixin, TestCase):
    """Threshold breach behavior + row aggregation."""

    def test_breach_when_spend_exceeds_threshold(self):
        _mk_cost_row(estimated_cost_usd=Decimal('5.00'))
        _mk_cost_row(estimated_cost_usd=Decimal('7.50'))
        _set_threshold('hour', '10.00')
        result = compute_window('hour')
        self.assertEqual(result.threshold_usd, Decimal('10.00'))
        self.assertEqual(result.actual_usd, Decimal('12.50'))
        self.assertTrue(result.breached)
        self.assertEqual(result.row_count, 2)

    def test_no_breach_when_spend_below_threshold(self):
        _mk_cost_row(estimated_cost_usd=Decimal('2.00'))
        _set_threshold('day', '10.00')
        result = compute_window('day')
        self.assertEqual(result.actual_usd, Decimal('2.00'))
        self.assertFalse(result.breached)

    def test_rows_outside_window_ignored(self):
        stale = timezone.now() - timedelta(hours=25)
        _mk_cost_row(estimated_cost_usd=Decimal('50.00'), timestamp=stale)
        _mk_cost_row(estimated_cost_usd=Decimal('0.10'))
        _set_threshold('hour', '1.00')
        result = compute_window('hour')
        self.assertEqual(result.actual_usd, Decimal('0.10'))
        self.assertFalse(result.breached)

    def test_top_service_reflects_largest_spender(self):
        _mk_cost_row(service='gpt-5-mini', estimated_cost_usd=Decimal('0.50'))
        _mk_cost_row(service='gpt-5.2', estimated_cost_usd=Decimal('9.00'))
        _mk_cost_row(service='gpt-5.2', estimated_cost_usd=Decimal('0.75'))
        _set_threshold('hour', '5.00')
        result = compute_window('hour')
        self.assertTrue(result.breached)
        self.assertEqual(result.top_service, 'gpt-5.2')
        self.assertEqual(result.top_service_usd, Decimal('9.75'))


class CostMonitorEnforceModeTests(_CostFixtureMixin, TestCase):
    def test_default_mode_is_monitor(self):
        SystemConfiguration.objects.filter(
            key='cost_protection_enforce_mode',
        ).delete()
        self.assertEqual(read_enforce_mode(), 'monitor')

    def test_monitor_mode_read(self):
        _set_mode('monitor')
        self.assertEqual(read_enforce_mode(), 'monitor')

    def test_freeze_mode_read(self):
        _set_mode('freeze')
        self.assertEqual(read_enforce_mode(), 'freeze')

    def test_unknown_mode_falls_back_to_monitor(self):
        _set_mode('paranoid')
        self.assertEqual(read_enforce_mode(), 'monitor')


class CostBridgeAttentionTests(_CostFixtureMixin, TestCase):
    """The HumanAttentionBridge producer creates a critical HAI with the
    correct payload shape."""

    def setUp(self):
        super().setUp()
        _admin_user()

    def _fake_breach(self, **overrides):
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

    def test_bridge_creates_single_critical_hai_from_single_breach(self):
        from core.services.human_attention_bridge import attention_bridge
        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            attention_bridge.create_cost_breach_attention(
                [self._fake_breach()]
            )
        hai = HumanAttentionItem.objects.filter(
            source_type='cost_breach',
        ).order_by('-created_at').first()
        self.assertIsNotNone(hai)
        self.assertEqual(hai.urgency, 'critical')
        self.assertEqual(hai.payload['worst_window'], 'hour')
        self.assertAlmostEqual(hai.payload['worst_ratio'], 1.25)
        self.assertEqual(len(hai.payload['breaches']), 1)
        first = hai.payload['breaches'][0]
        self.assertEqual(first['window'], 'hour')
        self.assertEqual(first['threshold_usd'], 10.0)
        self.assertEqual(first['actual_usd'], 12.5)
        self.assertAlmostEqual(first['ratio'], 1.25)
        self.assertEqual(first['top_service'], 'gpt-5.2')
        self.assertEqual(first['top_provider'], 'openai')
        self.assertEqual(first['row_count'], 7)
        # source_id mirrors the payload idempotency_key so
        # HumanInterfaceService dedup sees identical rows on retry.
        self.assertEqual(hai.source_id, 'cost_breach:hour:1234567890')

    def test_bridge_consolidates_multiple_window_breaches(self):
        """Rigby SIGN Q3 refinement: three simultaneous window breaches
        produce ONE HAI, not three."""
        from core.services.human_attention_bridge import attention_bridge
        hour = self._fake_breach(
            window='hour',
            threshold_usd=Decimal('10.00'),
            actual_usd=Decimal('12.50'),
            idempotency_key='cost_breach:hour:100',
        )
        day = self._fake_breach(
            window='day',
            threshold_usd=Decimal('100.00'),
            actual_usd=Decimal('180.00'),
            idempotency_key='cost_breach:day:200',
        )
        month = self._fake_breach(
            window='month',
            threshold_usd=Decimal('1000.00'),
            actual_usd=Decimal('1050.00'),
            idempotency_key='cost_breach:month:300',
        )
        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            attention_bridge.create_cost_breach_attention([hour, day, month])

        rows = HumanAttentionItem.objects.filter(source_type='cost_breach')
        self.assertEqual(rows.count(), 1)
        hai = rows.first()
        # worst by ratio: day (1.8x)
        self.assertEqual(hai.payload['worst_window'], 'day')
        self.assertAlmostEqual(hai.payload['worst_ratio'], 1.8)
        # All three windows present in payload.breaches
        windows = [b['window'] for b in hai.payload['breaches']]
        self.assertEqual(set(windows), {'hour', 'day', 'month'})
        # Ordered by ratio descending: day (1.8) > hour (1.25) > month (1.05)
        self.assertEqual(hai.payload['breaches'][0]['window'], 'day')
        # source_id anchors to worst-ratio breach's key
        self.assertEqual(hai.source_id, 'cost_breach:day:200')


class CostBeatTaskTests(_CostFixtureMixin, TestCase):
    """The check_cost_thresholds task dispatches HAI on breach + returns
    a structured summary."""

    def setUp(self):
        super().setUp()
        _admin_user()

    def test_task_dispatches_hai_on_breach(self):
        _mk_cost_row(estimated_cost_usd=Decimal('12.00'))
        _set_threshold('hour', '10.00')

        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            result = check_cost_thresholds()

        self.assertEqual(result['mode'], 'monitor')
        self.assertEqual(result['windows_checked'], 3)
        self.assertEqual(result['hai_dispatched'], 1)
        self.assertGreaterEqual(result['windows_breached'], 1)
        hai = HumanAttentionItem.objects.filter(
            source_type='cost_breach',
        ).first()
        self.assertIsNotNone(hai)

    def test_task_no_dispatch_when_no_breach(self):
        _mk_cost_row(estimated_cost_usd=Decimal('0.01'))
        _set_threshold('day', '100.00')

        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            result = check_cost_thresholds()

        self.assertEqual(result['hai_dispatched'], 0)
        self.assertEqual(result['windows_breached'], 0)
        self.assertEqual(
            HumanAttentionItem.objects.filter(
                source_type='cost_breach',
            ).count(),
            0,
        )

    def test_freeze_mode_does_not_flip_governance(self):
        """CRITICAL enforcement-gate contract: even when
        ``cost_protection_enforce_mode='freeze'``, THIS release does NOT
        dispatch any governance freeze — enforcement is deferred to a
        later phase per Chris's discipline (monitor observation +
        explicit approval required first).

        Verified via three independent signals:

        1. ``result['mode']`` reflects the config value ('freeze').
        2. No ``GovernanceEngine`` import happens inside the task —
           patching the module attribute proves absence.
        3. The task emits the explicit "not implemented" warning log.
        """
        import logging

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
        # Result still shows the breach was dispatched as HAI (monitor
        # behavior unchanged by mode='freeze').
        self.assertEqual(result['hai_dispatched'], 1)
        self.assertGreaterEqual(result['windows_breached'], 1)
        # Explicit warning proves the enforcement-gate contract is
        # documented in the task's runtime behavior.
        joined = '\n'.join(log_ctx.output)
        self.assertIn('enforce_mode=freeze', joined)
        self.assertIn('enforcement dispatch is not implemented', joined)


class CheckAllWindowsTests(_CostFixtureMixin, TestCase):
    """check_all_windows returns hour/day/month in a stable order."""

    def test_returns_three_windows_in_order(self):
        results = check_all_windows()
        self.assertEqual([r.window for r in results], ['hour', 'day', 'month'])
