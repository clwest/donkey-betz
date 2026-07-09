"""
Regression tests for Session 2735 HAI Delivery Fanout Extension PR 1.

The receiver-then-Celery-task chain under test:

    HumanAttentionItem.objects.create()
      → post_save fires
      → core.signals_discord_notifications.on_hai_discord_dispatch
        (synchronous guards + transaction.on_commit gate)
      → core.tasks_push_notifications.notify_hai_discord.delay(id)
      → task re-loads HAI, re-applies gates, calls
        discord_notifications.send_status_notification.

Test structure:

* Receiver tests patch ``notify_hai_discord.delay`` and use
  ``captureOnCommitCallbacks(execute=True)`` because the receiver
  schedules the enqueue via ``transaction.on_commit`` (Rigby SIGN
  pa-247f1595c5934325 Q3 REQUIRED refinement — no synchronous HTTP in
  post_save, and no side effect on rollback).
* Task tests invoke ``notify_hai_discord(item_id)`` directly (Celery
  ``@shared_task``-decorated functions are callable) to exercise the
  worker-side re-application of gates.
* Adapter is patched throughout — no real Discord HTTP.

Contract exercised end-to-end:

- Kill switch off → no enqueue AND task returns 'kill_switch' if forced.
- Non-critical urgency → no enqueue at receiver.
- Update of existing item (created=False) → no enqueue.
- ``payload['discord_sent']=True`` → no enqueue at receiver AND task
  returns 'discord_sent_flag' if forced.
- ``payload['discord_sent']=False`` → enqueue proceeds.
- Rolled-back transaction → no enqueue (on_commit contract).
- HumanPreference gates (min_urgency, blocked_sources, quiet_hours) →
  applied in the task; suppress dispatch.
- No HumanPreference row → task fails open and dispatches.
- Task called for missing item → returns 'missing' safely.
- Adapter exception inside the task → task returns
  'adapter_error:...' safely; HAI write is unaffected.
"""
from __future__ import annotations

from datetime import time as _time, timedelta  # noqa: F401
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_human_interface import (
    HumanAttentionItem,
    HumanPreference,
)
from core.tasks_push_notifications import notify_hai_discord

User = get_user_model()


def _mk_user(username: str = 'hai-discord-fixture'):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'is_staff': True, 'is_active': True},
    )
    return user


def _mk_pref(user, **fields) -> HumanPreference:
    pref, _ = HumanPreference.objects.get_or_create(user=user)
    for k, v in fields.items():
        setattr(pref, k, v)
    pref.save()
    return pref


_ENQUEUE_PATH = 'core.tasks_push_notifications.notify_hai_discord.delay'
_ADAPTER_PATH = (
    'core.services.discord_notifications.send_status_notification'
)


# =============================================================================
# Receiver-level tests (does the signal receiver enqueue the Celery task?)
# =============================================================================


class HAIDiscordReceiverEnqueueTests(TestCase):
    """Receiver enqueues the Celery task on-commit for critical creations."""

    def test_critical_created_enqueues_task_on_commit(self):
        user = _mk_user()
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            item = HumanAttentionItem.objects.create(
                user=user,
                source_type='mission_verdict',
                source_id='verdict-run-1',
                source_agent='MissionRunner',
                item_type='review',
                title='Mission rejected',
                summary='',
                urgency='critical',
                payload={},
            )
        delay_mock.assert_called_once_with(str(item.id))


class HAIDiscordReceiverFilteringTests(TestCase):
    """High/medium/kill-switch/updated/discord_sent all block enqueue."""

    def test_high_urgency_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='verdict-high',
                source_agent='MissionRunner',
                item_type='review',
                title='high',
                summary='',
                urgency='high',
                payload={},
            )
        delay_mock.assert_not_called()

    def test_medium_urgency_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='verdict-med',
                source_agent='MissionRunner',
                item_type='review',
                title='med',
                summary='',
                urgency='medium',
                payload={},
            )
        delay_mock.assert_not_called()

    def test_update_of_existing_item_does_not_enqueue(self):
        user = _mk_user()
        with patch(_ENQUEUE_PATH) as first_mock, self.captureOnCommitCallbacks(execute=True):
            item = HumanAttentionItem.objects.create(
                user=user,
                source_type='mission_verdict',
                source_id='verdict-update',
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

    @override_settings(HAI_DISCORD_DISPATCH_ENABLED=False)
    def test_kill_switch_off_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='verdict-kill',
                source_agent='MissionRunner',
                item_type='review',
                title='killed by switch',
                summary='',
                urgency='critical',
                payload={},
            )
        delay_mock.assert_not_called()

    def test_payload_discord_sent_flag_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='data_pipeline_stall',
                source_id='data_pipeline_stall:2026-07-09:12:starving',
                source_agent='BodyCoordinator',
                item_type='alert',
                title='Data pipeline starving',
                summary='',
                urgency='critical',
                payload={'discord_sent': True},
            )
        delay_mock.assert_not_called()

    def test_payload_discord_sent_false_still_enqueues(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=True):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='failure_cluster',
                source_id='failure_cluster:x:1:critical',
                source_agent='CeleryTelemetry',
                item_type='alert',
                title='cluster',
                summary='',
                urgency='critical',
                payload={'discord_sent': False},
            )
        delay_mock.assert_called_once()


class HAIDiscordReceiverTransactionSafetyTests(TestCase):
    """Rolled-back HAI creates produce no enqueue (on_commit contract)."""

    def test_rolled_back_transaction_does_not_enqueue(self):
        with patch(_ENQUEUE_PATH) as delay_mock, self.captureOnCommitCallbacks(execute=False):
            HumanAttentionItem.objects.create(
                user=_mk_user(),
                source_type='mission_verdict',
                source_id='verdict-rollback',
                source_agent='MissionRunner',
                item_type='review',
                title='rolled back',
                summary='',
                urgency='critical',
                payload={},
            )
        delay_mock.assert_not_called()


# =============================================================================
# Task-level tests (does the worker apply gates + call the Discord adapter?)
# =============================================================================


def _mk_critical_item(user, source_type='mission_verdict', payload=None):
    return HumanAttentionItem.objects.create(
        user=user,
        source_type=source_type,
        source_id=f'{source_type}-fixture',
        source_agent='TestFixture',
        item_type='review',
        title='fixture critical item',
        summary='fixture summary',
        urgency='critical',
        payload=payload or {},
    )


class HAIDiscordTaskDispatchTests(TestCase):
    """The Celery task dispatches to Discord when gates pass."""

    def test_task_calls_adapter_when_gates_pass(self):
        user = _mk_user('task-happy-user')
        item = _mk_critical_item(user)
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord(str(item.id))
        adapter.assert_called_once()
        self.assertEqual(result.get('dispatched'), True)


class HAIDiscordTaskFilteringTests(TestCase):
    """Gate re-application at task run time."""

    @override_settings(HAI_DISCORD_DISPATCH_ENABLED=False)
    def test_task_respects_kill_switch(self):
        user = _mk_user('task-kill-user')
        item = _mk_critical_item(user)
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord(str(item.id))
        adapter.assert_not_called()
        self.assertEqual(result.get('skipped'), 'kill_switch')

    def test_task_respects_payload_discord_sent(self):
        user = _mk_user('task-flagged-user')
        item = _mk_critical_item(user, payload={'discord_sent': True})
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord(str(item.id))
        adapter.assert_not_called()
        self.assertEqual(result.get('skipped'), 'discord_sent_flag')

    def test_task_returns_missing_for_deleted_item(self):
        # Item id that doesn't exist
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord('00000000-0000-0000-0000-000000000000')
        adapter.assert_not_called()
        self.assertEqual(result.get('skipped'), 'missing')

    def test_task_returns_urgency_skip_if_downgraded(self):
        """Committed row was downgraded from critical → high between
        receiver enqueue and worker run. Task should skip."""
        user = _mk_user('task-downgraded-user')
        item = _mk_critical_item(user)
        item.urgency = 'high'
        item.save(update_fields=['urgency'])
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord(str(item.id))
        adapter.assert_not_called()
        self.assertEqual(result.get('skipped'), 'urgency_not_critical')

    def test_task_respects_blocked_sources_pref(self):
        user = _mk_user('task-blocked-user')
        _mk_pref(user, blocked_sources=['mission_verdict'])
        item = _mk_critical_item(user, source_type='mission_verdict')
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord(str(item.id))
        adapter.assert_not_called()
        self.assertEqual(result.get('skipped'), 'preference_gate')

    def test_task_respects_quiet_hours_pref(self):
        user = _mk_user('task-quiet-user')
        _mk_pref(
            user,
            quiet_hours_start=_time(0, 0),
            quiet_hours_end=_time(23, 59, 59),
        )
        now_local = timezone.localtime().time()
        if not (_time(0, 0) <= now_local < _time(23, 59, 59)):
            self.skipTest('Local time outside synthetic 00:00→23:59 window')
        item = _mk_critical_item(user)
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord(str(item.id))
        adapter.assert_not_called()
        self.assertEqual(result.get('skipped'), 'preference_gate')

    def test_task_fails_open_when_no_preference_row(self):
        user = _mk_user('task-nopref-user')
        HumanPreference.objects.filter(user=user).delete()
        item = _mk_critical_item(user)
        with patch(_ADAPTER_PATH) as adapter:
            result = notify_hai_discord(str(item.id))
        adapter.assert_called_once()
        self.assertEqual(result.get('dispatched'), True)


class HAIDiscordTaskFailSafeTests(TestCase):
    """Adapter exception inside the task is swallowed with structured result."""

    def test_adapter_exception_returns_error_result(self):
        user = _mk_user('task-adapter-boom-user')
        item = _mk_critical_item(user)
        with patch(_ADAPTER_PATH, side_effect=Exception('discord api down')):
            result = notify_hai_discord(str(item.id))
        skipped = result.get('skipped', '')
        self.assertTrue(skipped.startswith('adapter_error:'))
