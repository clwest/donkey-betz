"""
Regression tests for Session 2735 HAI Delivery Fanout Extension PR 2.

Web Push receiver + Celery task, mirrors the PR 1 (Discord) shape with
per-subscription fan-out and NotificationLog auditing.

Test structure:

* Receiver tests patch ``notify_hai_webpush.delay`` inside
  ``captureOnCommitCallbacks(execute=True)`` — verify the on_commit
  enqueue contract and the fast synchronous guard filters.
* Task tests invoke ``notify_hai_webpush(item_id)`` directly to
  exercise per-subscription dispatch, ``NotificationLog`` writes, and
  gate re-application against the committed row.

Contract exercised:

- Receiver enqueues on critical creation; skips on high/medium, kill
  switch off, updated (not created), ``payload['webpush_sent']=True``.
- Rollback → no enqueue.
- Task iterates the item.user's active ``PushSubscription`` rows and
  calls ``PushNotificationService.send_notification`` once per
  subscription.
- Each dispatch writes a ``NotificationLog`` row with
  ``notification_type='system'`` and ``delivered`` reflecting the
  adapter result.
- Success → ``PushSubscription.mark_success()``; failure → ``mark_failed()``.
- No active subscriptions → task returns ``no_active_subscriptions``.
- No user → task returns ``no_user``.
- Kill switch off at task time → returns ``kill_switch``.
- Missing item → returns ``missing``.
- Downgraded urgency → returns ``urgency_not_critical``.
- ``payload['webpush_sent']=True`` at task time → returns
  ``webpush_sent_flag``.
- ``HumanPreference.blocked_sources`` covering source_type → returns
  ``preference_gate``.
- Quiet hours covering current time → returns ``preference_gate``.
- No preference row → fails open and dispatches.
"""
from __future__ import annotations

from datetime import time as _time
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_human_interface import (
    HumanAttentionItem,
    HumanPreference,
)
from core.models_push_notifications import (
    NotificationLog,
    PushSubscription,
)
from core.tasks_push_notifications import notify_hai_webpush

User = get_user_model()


def _mk_user(username: str = 'hai-webpush-fixture'):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'is_staff': True, 'is_active': True},
    )
    return user


def _mk_sub(user, endpoint_suffix: str = '', is_active: bool = True) -> PushSubscription:
    return PushSubscription.objects.create(
        user=user,
        endpoint=f'https://push.example.com/sub-{user.id}-{endpoint_suffix}',
        p256dh_key='dummy_p256dh',
        auth_key='dummy_auth',
        browser='chrome',
        device_type='desktop',
        is_active=is_active,
    )


def _mk_pref(user, **fields) -> HumanPreference:
    pref, _ = HumanPreference.objects.get_or_create(user=user)
    for k, v in fields.items():
        setattr(pref, k, v)
    pref.save()
    return pref


def _mk_critical_item(user, source_type='mission_verdict', payload=None, source_id_suffix=''):
    return HumanAttentionItem.objects.create(
        user=user,
        source_type=source_type,
        source_id=f'{source_type}-fixture{source_id_suffix}',
        source_agent='TestFixture',
        item_type='review',
        title='fixture critical item',
        summary='fixture summary',
        urgency='critical',
        payload=payload or {},
    )


_ENQUEUE_PATH = 'core.tasks_push_notifications.notify_hai_webpush.delay'
_PUSH_SERVICE_PATH = 'core.services.push_notification_service.get_push_service'


# =============================================================================
# Receiver-level tests
# =============================================================================


class HAIWebPushReceiverEnqueueTests(TestCase):
    def test_critical_created_enqueues_on_commit(self):
        user = _mk_user()
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            item = HumanAttentionItem.objects.create(
                user=user,
                source_type='mission_verdict',
                source_id='verdict-webpush-a',
                source_agent='MissionRunner',
                item_type='review',
                title='Mission rejected',
                summary='',
                urgency='critical',
                payload={},
            )
        delay_mock.assert_called_once_with(str(item.id))


class HAIWebPushReceiverFilteringTests(TestCase):
    def test_high_urgency_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='hai-webpush-high',
                source_agent='MissionRunner',
                item_type='review',
                title='high',
                summary='',
                urgency='high',
                payload={},
            )
        delay_mock.assert_not_called()

    def test_update_of_existing_does_not_re_enqueue(self):
        user = _mk_user()
        with patch(_ENQUEUE_PATH) as first_mock, self.captureOnCommitCallbacks(execute=True):
            item = HumanAttentionItem.objects.create(
                user=user,
                source_type='mission_verdict',
                source_id='hai-webpush-update',
                source_agent='MissionRunner',
                item_type='review',
                title='initially high',
                summary='',
                urgency='high',
                payload={},
            )
        first_mock.assert_not_called()

        with patch(_ENQUEUE_PATH) as second_mock, self.captureOnCommitCallbacks(execute=True):
            item.urgency = 'critical'
            item.save(update_fields=['urgency'])
        second_mock.assert_not_called()

    @override_settings(HAI_WEBPUSH_DISPATCH_ENABLED=False)
    def test_kill_switch_off_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='hai-webpush-kill',
                source_agent='MissionRunner',
                item_type='review',
                title='killed by switch',
                summary='',
                urgency='critical',
                payload={},
            )
        delay_mock.assert_not_called()

    def test_payload_webpush_sent_true_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='hai-webpush-flag',
                source_agent='MissionRunner',
                item_type='review',
                title='flagged',
                summary='',
                urgency='critical',
                payload={'webpush_sent': True},
            )
        delay_mock.assert_not_called()


class HAIWebPushReceiverTransactionSafetyTests(TestCase):
    def test_rolled_back_transaction_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=False):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='hai-webpush-rollback',
                source_agent='MissionRunner',
                item_type='review',
                title='rolled back',
                summary='',
                urgency='critical',
                payload={},
            )
        delay_mock.assert_not_called()


# =============================================================================
# Task-level tests
# =============================================================================


def _stub_push_service(send_result=True):
    """Return a MagicMock configured to look like PushNotificationService."""
    svc = MagicMock()
    svc.send_notification.return_value = send_result
    return svc


class HAIWebPushTaskDispatchTests(TestCase):
    def test_task_dispatches_to_each_active_subscription(self):
        user = _mk_user('webpush-multi-sub')
        _mk_sub(user, endpoint_suffix='chrome')
        _mk_sub(user, endpoint_suffix='firefox')
        _mk_sub(user, endpoint_suffix='inactive-safari', is_active=False)
        item = _mk_critical_item(user)

        svc = _stub_push_service(send_result=True)
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))

        # Two active subscriptions → two send_notification calls
        self.assertEqual(svc.send_notification.call_count, 2)
        self.assertEqual(result.get('dispatched'), 2)
        self.assertEqual(result.get('failed'), 0)

        # Two NotificationLog rows written with type='system' + delivered=True
        logs = NotificationLog.objects.filter(
            subscription__user=user,
            notification_type='system',
        )
        self.assertEqual(logs.count(), 2)
        for log in logs:
            self.assertTrue(log.delivered)

    def test_task_handles_partial_send_failure(self):
        user = _mk_user('webpush-partial-fail')
        sub_ok = _mk_sub(user, endpoint_suffix='ok')
        sub_fail = _mk_sub(user, endpoint_suffix='fail')
        item = _mk_critical_item(user)

        svc = MagicMock()
        svc.send_notification.side_effect = [True, False]  # First OK, second fails
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))

        self.assertEqual(result.get('dispatched'), 1)
        self.assertEqual(result.get('failed'), 1)
        logs = NotificationLog.objects.filter(subscription__user=user)
        self.assertEqual(logs.count(), 2)
        delivered_flags = sorted(list(logs.values_list('delivered', flat=True)))
        self.assertEqual(delivered_flags, [False, True])

        sub_ok.refresh_from_db()
        sub_fail.refresh_from_db()
        # mark_success resets to 0; mark_failed increments to 1
        self.assertEqual(sub_ok.failed_count, 0)
        self.assertEqual(sub_fail.failed_count, 1)


class HAIWebPushTaskFilteringTests(TestCase):
    @override_settings(HAI_WEBPUSH_DISPATCH_ENABLED=False)
    def test_task_respects_kill_switch(self):
        user = _mk_user('webpush-kill-user')
        _mk_sub(user)
        item = _mk_critical_item(user)
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'kill_switch')

    def test_task_respects_webpush_sent_flag(self):
        user = _mk_user('webpush-flag-user')
        _mk_sub(user)
        item = _mk_critical_item(user, payload={'webpush_sent': True})
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'webpush_sent_flag')

    def test_task_returns_missing_for_deleted_item(self):
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush('00000000-0000-0000-0000-000000000000')
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'missing')

    def test_task_returns_urgency_skip_if_downgraded(self):
        user = _mk_user('webpush-downgrade-user')
        _mk_sub(user)
        item = _mk_critical_item(user)
        item.urgency = 'high'
        item.save(update_fields=['urgency'])
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'urgency_not_critical')

    def test_task_returns_no_active_subscriptions_when_none_exist(self):
        user = _mk_user('webpush-no-subs-user')
        # No PushSubscription rows for this user
        item = _mk_critical_item(user)
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'no_active_subscriptions')

    def test_task_returns_no_active_subscriptions_when_all_inactive(self):
        user = _mk_user('webpush-all-inactive-user')
        _mk_sub(user, is_active=False)
        item = _mk_critical_item(user)
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'no_active_subscriptions')

    def test_task_respects_blocked_sources_pref(self):
        user = _mk_user('webpush-blocked-user')
        _mk_pref(user, blocked_sources=['mission_verdict'])
        _mk_sub(user)
        item = _mk_critical_item(user, source_type='mission_verdict')
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'preference_gate')

    def test_task_respects_quiet_hours_pref(self):
        user = _mk_user('webpush-quiet-user')
        _mk_pref(
            user,
            quiet_hours_start=_time(0, 0),
            quiet_hours_end=_time(23, 59, 59),
        )
        now_local = timezone.localtime().time()
        if not (_time(0, 0) <= now_local < _time(23, 59, 59)):
            self.skipTest('Local time outside synthetic 00:00→23:59 window')
        _mk_sub(user)
        item = _mk_critical_item(user)
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_not_called()
        self.assertEqual(result.get('skipped'), 'preference_gate')

    def test_task_fails_open_when_no_preference_row(self):
        user = _mk_user('webpush-nopref-user')
        HumanPreference.objects.filter(user=user).delete()
        _mk_sub(user)
        item = _mk_critical_item(user)
        svc = _stub_push_service()
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        svc.send_notification.assert_called_once()
        self.assertEqual(result.get('dispatched'), 1)


class HAIWebPushTaskFailSafeTests(TestCase):
    def test_push_service_init_failure_returns_service_error(self):
        user = _mk_user('webpush-svc-init-boom-user')
        _mk_sub(user)
        item = _mk_critical_item(user)
        with patch(
            _PUSH_SERVICE_PATH,
            side_effect=Exception('service init failed'),
        ):
            result = notify_hai_webpush(str(item.id))
        skipped = result.get('skipped', '')
        self.assertTrue(skipped.startswith('service_error:'))

    def test_per_subscription_exception_does_not_break_loop(self):
        user = _mk_user('webpush-loop-exception-user')
        _mk_sub(user, endpoint_suffix='raises')
        _mk_sub(user, endpoint_suffix='ok')
        item = _mk_critical_item(user)

        svc = MagicMock()
        # First send raises; second succeeds.
        svc.send_notification.side_effect = [
            Exception('network flake'),
            True,
        ]
        with patch(_PUSH_SERVICE_PATH, return_value=svc):
            result = notify_hai_webpush(str(item.id))
        self.assertEqual(result.get('dispatched'), 1)
        self.assertEqual(result.get('failed'), 1)
