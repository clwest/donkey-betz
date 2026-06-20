"""Tests for the Session 1169 idempotent enforce-disabled helper.

Rigby's late add from Session 1168 close. The PR #2314 filter prevents
NEW denylisted ``PeriodicTask`` rows from being materialized; this
helper closes the loop by re-asserting ``enabled=False`` on any rows
that already exist with ``enabled=True``.

Run::

    python manage.py test core.tests.test_enforce_disabled_local -v2
"""
from __future__ import annotations

import os
from unittest import mock

from django.test import TestCase
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from core.management.commands.add_critical_celery_tasks import (
    LOCAL_DENY_TASKS,
    _enforce_disabled_local,
)


class EnforceDisabledLocalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.interval, _ = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.SECONDS,
        )

    def _make_periodic_task(self, name, task='core.tasks.noop', enabled=True):
        return PeriodicTask.objects.create(
            name=name,
            task=task,
            interval=self.interval,
            enabled=enabled,
        )

    # ── No-op on non-local environments ────────────────────────────────

    def test_production_env_is_noop(self):
        """On RAILWAY_ENVIRONMENT=production, the helper does nothing
        even if denylisted rows are enabled."""
        self._make_periodic_task('scan-income-spider-orchestrator', enabled=True)
        with mock.patch.dict(os.environ, {'RAILWAY_ENVIRONMENT': 'production'}, clear=False):
            count, names = _enforce_disabled_local()
        self.assertEqual(count, 0)
        self.assertEqual(names, [])
        # Row still enabled
        self.assertTrue(
            PeriodicTask.objects.get(name='scan-income-spider-orchestrator').enabled
        )

    # ── Happy path on local ────────────────────────────────────────────

    def test_local_disables_existing_enabled_denylisted_rows(self):
        self._make_periodic_task('scan-income-spider-orchestrator', enabled=True)
        self._make_periodic_task('run-spider-network', enabled=True)
        self._make_periodic_task('safe-housekeeping-task', enabled=True)  # not in deny

        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            os.environ.pop('ENABLE_BEAT_TASKS', None)
            count, names = _enforce_disabled_local()

        self.assertEqual(count, 2)
        self.assertEqual(names, sorted(['scan-income-spider-orchestrator', 'run-spider-network']))
        # Denied rows toggled
        self.assertFalse(
            PeriodicTask.objects.get(name='scan-income-spider-orchestrator').enabled
        )
        self.assertFalse(
            PeriodicTask.objects.get(name='run-spider-network').enabled
        )
        # Safe row untouched
        self.assertTrue(
            PeriodicTask.objects.get(name='safe-housekeeping-task').enabled
        )

    def test_local_is_idempotent_on_already_disabled_rows(self):
        """Rows already at enabled=False are not toggled (or counted)."""
        self._make_periodic_task('scan-income-spider-orchestrator', enabled=False)
        self._make_periodic_task('run-spider-network', enabled=True)

        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            os.environ.pop('ENABLE_BEAT_TASKS', None)
            count, names = _enforce_disabled_local()

        # Only the enabled one shows up
        self.assertEqual(count, 1)
        self.assertEqual(names, ['run-spider-network'])

    def test_local_with_no_denylisted_rows_in_db(self):
        """If the DB has no denylisted rows at all, returns (0, [])."""
        self._make_periodic_task('safe-task-only', enabled=True)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            os.environ.pop('ENABLE_BEAT_TASKS', None)
            count, names = _enforce_disabled_local()
        self.assertEqual(count, 0)
        self.assertEqual(names, [])

    # ── Dry-run preview ────────────────────────────────────────────────

    def test_dry_run_reports_but_does_not_toggle(self):
        self._make_periodic_task('scan-income-spider-orchestrator', enabled=True)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            os.environ.pop('ENABLE_BEAT_TASKS', None)
            count, names = _enforce_disabled_local(dry_run=True)
        self.assertEqual(count, 1)
        self.assertEqual(names, ['scan-income-spider-orchestrator'])
        # Row still enabled — dry-run didn't touch it
        self.assertTrue(
            PeriodicTask.objects.get(name='scan-income-spider-orchestrator').enabled
        )

    # ── ENABLE_BEAT_TASKS override ─────────────────────────────────────

    def test_local_with_override_skips_opted_in_task(self):
        """When ENABLE_BEAT_TASKS opts a task back in, the helper
        leaves it enabled — symmetric to _filter_local_safe behavior."""
        self._make_periodic_task('scan-income-spider-orchestrator', enabled=True)
        self._make_periodic_task('run-spider-network', enabled=True)

        with mock.patch.dict(
            os.environ,
            {'ENABLE_BEAT_TASKS': 'scan-income-spider-orchestrator'},
            clear=False,
        ):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            count, names = _enforce_disabled_local()

        # Only the non-overridden task gets disabled
        self.assertEqual(count, 1)
        self.assertEqual(names, ['run-spider-network'])
        # Override target untouched
        self.assertTrue(
            PeriodicTask.objects.get(name='scan-income-spider-orchestrator').enabled
        )
        # Non-override denylisted task toggled
        self.assertFalse(
            PeriodicTask.objects.get(name='run-spider-network').enabled
        )

    def test_local_with_override_for_all_denylist_is_noop(self):
        """If ENABLE_BEAT_TASKS includes every denylist entry, the
        helper has nothing to do."""
        self._make_periodic_task('scan-income-spider-orchestrator', enabled=True)
        all_overrides = ','.join(LOCAL_DENY_TASKS)
        with mock.patch.dict(
            os.environ,
            {'ENABLE_BEAT_TASKS': all_overrides},
            clear=False,
        ):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            count, names = _enforce_disabled_local()
        self.assertEqual(count, 0)
        self.assertEqual(names, [])
        self.assertTrue(
            PeriodicTask.objects.get(name='scan-income-spider-orchestrator').enabled
        )
