"""
Regression tests for Session 2735 Beat Schedule Health Campaign P1.

Covers:

* ``core.services.beat_health_monitor`` — pure query helper
  (``compute_snapshot``, ``read_allowlist``, ``enabled``).
* ``core.services.human_attention_bridge.HumanAttentionBridge
  .create_beat_health_attention`` — 12th producer method.
* ``core.tasks_beat_health.check_beat_health`` — beat task glue that
  dispatches HAI on any missing allowlisted beat.

Test discipline:

- Real DB, real ``CeleryTaskEvent`` rows, real HAI creation.
- ``app.conf.beat_schedule`` patched via a synthetic dict so tests are
  independent of the production beat entries (which change often).
- HAI Fanout receiver enqueue paths patched so no real Celery tasks are
  enqueued.

Contract exercised:

- Disabled kill switch → task returns 'kill_switch'.
- Allowlist read from ``SystemConfiguration`` JSON list; missing key →
  starter set; empty list → monitor nothing (no missing beats can be
  reported); invalid JSON → fall back to starter set.
- ``compute_snapshot`` returns zero-missing when every allowlisted beat
  fired at least ``min_expected_fires`` times in the window.
- Returns missing entries when a beat fired below the threshold.
- Ignores fires outside the lookback window.
- Ignores tasks not in the allowlist.
- Bridge consolidates all missing beats into ONE HAI per tick.
- Beat entries in the allowlist that are absent from
  ``app.conf.beat_schedule`` are skipped without erroring.
"""
from __future__ import annotations

import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models.system import SystemConfiguration
from core.models_celery_telemetry import CeleryTaskEvent
from core.models_human_interface import HumanAttentionItem
from core.services.beat_health_monitor import (
    BeatHealthSnapshot,
    MissingBeat,
    compute_snapshot,
    read_allowlist,
    enabled,
)
from core.tasks_beat_health import check_beat_health

User = get_user_model()


def _admin_user():
    user, _ = User.objects.get_or_create(
        username='beat-health-fixture-admin',
        defaults={'is_staff': True, 'is_active': True},
    )
    return user


def _mk_fire(
    *,
    task_name: str,
    at=None,
) -> CeleryTaskEvent:
    """Insert a synthetic CeleryTaskEvent row."""
    at = at or timezone.now()
    return CeleryTaskEvent.objects.create(
        task_id=f'sim-{task_name}-{at.timestamp()}',
        task_name=task_name,
        status='SUCCESS',
        started_at=at,
        finished_at=at,
    )


def _set_config(key: str, value: str):
    SystemConfiguration.objects.update_or_create(
        key=key,
        defaults={'value': value, 'is_active': True},
    )


class _BeatFixtureMixin:
    """Purge ambient CeleryTaskEvent rows between tests so the
    lookback-window counts reflect only what each test wrote."""

    def setUp(self):
        super().setUp()  # type: ignore[misc]
        CeleryTaskEvent.objects.all().delete()


# =============================================================================
# read_allowlist / enabled
# =============================================================================


class BeatHealthConfigReadTests(_BeatFixtureMixin, TestCase):
    def test_missing_key_returns_starter_set(self):
        SystemConfiguration.objects.filter(key='beat_health_allowlist').delete()
        allow = read_allowlist()
        self.assertIn('heart-service-heartbeat', allow)
        self.assertIn('check-celery-health', allow)
        self.assertIn('monitor-celery-health', allow)

    def test_empty_list_returns_empty_tuple(self):
        _set_config('beat_health_allowlist', '[]')
        allow = read_allowlist()
        self.assertEqual(allow, tuple())

    def test_valid_json_list_returned_verbatim(self):
        _set_config(
            'beat_health_allowlist',
            json.dumps(['beat-a', 'beat-b']),
        )
        allow = read_allowlist()
        self.assertEqual(allow, ('beat-a', 'beat-b'))

    def test_invalid_json_falls_back_to_starter(self):
        _set_config('beat_health_allowlist', 'this is not json')
        allow = read_allowlist()
        self.assertIn('heart-service-heartbeat', allow)

    def test_non_list_json_falls_back_to_starter(self):
        _set_config('beat_health_allowlist', '{"nope": true}')
        allow = read_allowlist()
        self.assertIn('heart-service-heartbeat', allow)

    def test_enabled_default_true(self):
        SystemConfiguration.objects.filter(key='beat_health_enabled').delete()
        self.assertTrue(enabled())

    def test_enabled_false_string(self):
        _set_config('beat_health_enabled', 'false')
        self.assertFalse(enabled())


# =============================================================================
# compute_snapshot
# =============================================================================


_SCHEDULE_PATCH = 'core.services.beat_health_monitor._beat_schedule_entries'


def _synthetic_schedule() -> dict[str, dict]:
    return {
        'heart-service-heartbeat': {
            'task': 'core.tasks.run_heartbeat',
            'schedule': 600,
        },
        'check-celery-health': {
            'task': 'core.tasks.check_celery_health',
            'schedule': 600,
        },
        'monitor-celery-health': {
            'task': 'core.tasks.monitor_celery_health',
            'schedule': 1800,
        },
        # Not in the starter allowlist — should not affect results.
        'other-beat': {
            'task': 'core.tasks.other_task',
            'schedule': 3600,
        },
    }


class BeatHealthSnapshotTests(_BeatFixtureMixin, TestCase):
    def test_all_allowlisted_fired_no_missing(self):
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            _mk_fire(task_name='core.tasks.run_heartbeat')
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            snap = compute_snapshot()
        self.assertFalse(snap.any_missing)
        self.assertEqual(snap.checked, 3)
        self.assertEqual(snap.missing_count, 0)

    def test_one_allowlisted_did_not_fire(self):
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            _mk_fire(task_name='core.tasks.run_heartbeat')
            _mk_fire(task_name='core.tasks.check_celery_health')
            # monitor-celery-health silent
            snap = compute_snapshot()
        self.assertTrue(snap.any_missing)
        self.assertEqual(snap.missing_count, 1)
        m = snap.missing[0]
        self.assertEqual(m.beat_entry_name, 'monitor-celery-health')
        self.assertEqual(m.task_name, 'core.tasks.monitor_celery_health')
        self.assertEqual(m.observed_count, 0)

    def test_stale_fires_outside_window_ignored(self):
        old = timezone.now() - timedelta(days=5)
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            _mk_fire(task_name='core.tasks.run_heartbeat', at=old)
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            snap = compute_snapshot(lookback_days=1)
        # run_heartbeat's only fire is stale → missing
        self.assertTrue(snap.any_missing)
        names = {m.beat_entry_name for m in snap.missing}
        self.assertIn('heart-service-heartbeat', names)

    def test_non_allowlisted_beats_ignored(self):
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            # Fire ALL beats including the non-allowlisted 'other-beat'
            for tn in [
                'core.tasks.run_heartbeat',
                'core.tasks.check_celery_health',
                'core.tasks.monitor_celery_health',
                'core.tasks.other_task',
            ]:
                _mk_fire(task_name=tn)
            snap = compute_snapshot()
        self.assertFalse(snap.any_missing)
        self.assertEqual(snap.checked, 3)  # other-beat not counted

    def test_allowlist_entry_absent_from_schedule_skipped(self):
        """Config bug: allowlist includes a beat entry that doesn't
        exist in app.conf.beat_schedule. Monitor logs + skips."""
        _set_config(
            'beat_health_allowlist',
            json.dumps(['heart-service-heartbeat', 'does-not-exist']),
        )
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            _mk_fire(task_name='core.tasks.run_heartbeat')
            snap = compute_snapshot()
        # Only one is present in schedule; both silently OK.
        self.assertEqual(snap.checked, 1)
        self.assertFalse(snap.any_missing)

    def test_empty_allowlist_empty_snapshot(self):
        _set_config('beat_health_allowlist', '[]')
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            _mk_fire(task_name='core.tasks.run_heartbeat')
            snap = compute_snapshot()
        self.assertEqual(snap.checked, 0)
        self.assertFalse(snap.any_missing)

    def test_min_expected_fires_gates(self):
        """min_expected_fires=5 → a task that fired only 2 times is missing."""
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            _mk_fire(task_name='core.tasks.run_heartbeat')
            _mk_fire(task_name='core.tasks.run_heartbeat')
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            snap = compute_snapshot(min_expected_fires=5)
        # heart fired 2 (< 5) → missing; others fired 5 (>= 5) → not missing
        self.assertTrue(snap.any_missing)
        names = {m.beat_entry_name for m in snap.missing}
        self.assertEqual(names, {'heart-service-heartbeat'})


# =============================================================================
# Bridge attention method
# =============================================================================


class BeatHealthBridgeTests(_BeatFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()
        _admin_user()

    def _snap_with_missing(self) -> BeatHealthSnapshot:
        now = timezone.now()
        return BeatHealthSnapshot(
            lookback_days=1,
            min_expected_fires=1,
            now=now,
            cutoff=now - timedelta(days=1),
            allowlist_size=3,
            checked=3,
            missing=(
                MissingBeat(
                    beat_entry_name='check-celery-health',
                    task_name='core.tasks.check_celery_health',
                    schedule_hint='600',
                    expected_min=1,
                    observed_count=0,
                ),
                MissingBeat(
                    beat_entry_name='monitor-celery-health',
                    task_name='core.tasks.monitor_celery_health',
                    schedule_hint='1800',
                    expected_min=1,
                    observed_count=0,
                ),
            ),
            idempotency_key='beat_health:1d:2026-07-09',
        )

    def test_bridge_creates_single_consolidated_hai(self):
        from core.services.human_attention_bridge import attention_bridge
        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            attention_bridge.create_beat_health_attention(
                self._snap_with_missing()
            )
        rows = HumanAttentionItem.objects.filter(source_type='beat_health')
        self.assertEqual(rows.count(), 1)
        hai = rows.first()
        self.assertEqual(hai.urgency, 'critical')
        self.assertEqual(hai.payload['missing_count'], 2)
        self.assertEqual(len(hai.payload['missing']), 2)
        names = {m['beat_entry_name'] for m in hai.payload['missing']}
        self.assertEqual(
            names, {'check-celery-health', 'monitor-celery-health'},
        )
        # source_id anchors to the daily idempotency key
        self.assertEqual(hai.source_id, 'beat_health:1d:2026-07-09')

    def test_bridge_no_op_on_empty_snapshot(self):
        from core.services.human_attention_bridge import attention_bridge
        empty = BeatHealthSnapshot(
            lookback_days=1,
            min_expected_fires=1,
            now=timezone.now(),
            cutoff=timezone.now() - timedelta(days=1),
            allowlist_size=3,
            checked=3,
            missing=(),
            idempotency_key='beat_health:1d:2026-07-09',
        )
        with patch(
            'core.tasks_push_notifications.notify_hai_discord.delay'
        ), patch(
            'core.tasks_push_notifications.notify_hai_webpush.delay'
        ), self.captureOnCommitCallbacks(execute=True):
            attention_bridge.create_beat_health_attention(empty)
        self.assertEqual(
            HumanAttentionItem.objects.filter(source_type='beat_health').count(),
            0,
        )


# =============================================================================
# Beat task glue
# =============================================================================


class BeatHealthTaskTests(_BeatFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()
        _admin_user()

    def test_task_dispatches_hai_when_beats_missing(self):
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            # Fire ONE beat; other two allowlisted beats stay silent.
            _mk_fire(task_name='core.tasks.run_heartbeat')
            with patch(
                'core.tasks_push_notifications.notify_hai_discord.delay'
            ), patch(
                'core.tasks_push_notifications.notify_hai_webpush.delay'
            ), self.captureOnCommitCallbacks(execute=True):
                result = check_beat_health()
        self.assertEqual(result['missing_count'], 2)
        self.assertEqual(result['hai_dispatched'], 1)
        rows = HumanAttentionItem.objects.filter(source_type='beat_health')
        self.assertEqual(rows.count(), 1)

    def test_task_no_dispatch_when_all_fire(self):
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            _mk_fire(task_name='core.tasks.run_heartbeat')
            _mk_fire(task_name='core.tasks.check_celery_health')
            _mk_fire(task_name='core.tasks.monitor_celery_health')
            with patch(
                'core.tasks_push_notifications.notify_hai_discord.delay'
            ), patch(
                'core.tasks_push_notifications.notify_hai_webpush.delay'
            ), self.captureOnCommitCallbacks(execute=True):
                result = check_beat_health()
        self.assertEqual(result['missing_count'], 0)
        self.assertEqual(result['hai_dispatched'], 0)
        self.assertEqual(
            HumanAttentionItem.objects.filter(source_type='beat_health').count(),
            0,
        )

    def test_kill_switch_short_circuits(self):
        _set_config('beat_health_enabled', 'false')
        with patch(_SCHEDULE_PATCH, return_value=_synthetic_schedule()):
            with patch(
                'core.tasks_push_notifications.notify_hai_discord.delay'
            ), patch(
                'core.tasks_push_notifications.notify_hai_webpush.delay'
            ), self.captureOnCommitCallbacks(execute=True):
                result = check_beat_health()
        self.assertEqual(result, {'skipped': 'kill_switch'})
        self.assertEqual(
            HumanAttentionItem.objects.filter(source_type='beat_health').count(),
            0,
        )
