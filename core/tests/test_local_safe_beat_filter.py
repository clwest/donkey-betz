"""Tests for the Session 1168 local-safe beat filter.

chris-personal Known Bugs Queue item 7c332f0d. Verifies that
``add_critical_celery_tasks._filter_local_safe`` correctly removes
prod-noise tasks when running on a dev laptop (RAILWAY_ENVIRONMENT
unset) and leaves the schedule untouched on prod / staging. Covers the
``ENABLE_BEAT_TASKS`` escape-hatch override too.

Run::

    python manage.py test core.tests.test_local_safe_beat_filter -v2
"""
from __future__ import annotations

import os
from unittest import mock

from django.test import SimpleTestCase

from core.management.commands.add_critical_celery_tasks import (
    LOCAL_DENY_TASKS,
    _filter_local_safe,
    _is_local_env,
)


def _canonical():
    """Minimal canonical schedule mixing denied + allowed entries."""
    # Use a couple of real denied names + invented safe names so we can
    # assert the filter touches the right ones without binding the test
    # to the exact production allowlist.
    return {
        # Denied (prod-noise)
        'scan-income-spider-orchestrator': {'task': 't1', 'interval': 60},
        'run-spider-network': {'task': 't2', 'interval': 60},
        'warm-up-spiders': {'task': 't3', 'interval': 60},
        # Allowed (housekeeping / monitor / cheap)
        'cleanup-stale-content': {'task': 't4', 'interval': 60},
        'monitor-celery-health': {'task': 't5', 'interval': 60},
        'worker-memory-capture': {'task': 't6', 'interval': 300},
    }


class IsLocalEnvTests(SimpleTestCase):
    def test_unset_railway_environment_is_local(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            self.assertTrue(_is_local_env())

    def test_empty_railway_environment_is_local(self):
        with mock.patch.dict(os.environ, {'RAILWAY_ENVIRONMENT': ''}, clear=False):
            self.assertTrue(_is_local_env())

    def test_production_railway_environment_is_not_local(self):
        with mock.patch.dict(os.environ, {'RAILWAY_ENVIRONMENT': 'production'}, clear=False):
            self.assertFalse(_is_local_env())

    def test_staging_railway_environment_is_not_local(self):
        with mock.patch.dict(os.environ, {'RAILWAY_ENVIRONMENT': 'staging'}, clear=False):
            self.assertFalse(_is_local_env())


class FilterLocalSafeTests(SimpleTestCase):
    def test_production_keeps_full_schedule(self):
        with mock.patch.dict(os.environ, {'RAILWAY_ENVIRONMENT': 'production'}, clear=False):
            filtered, skipped = _filter_local_safe(_canonical())
        self.assertEqual(len(filtered), 6)
        self.assertEqual(skipped, [])

    def test_staging_keeps_full_schedule(self):
        with mock.patch.dict(os.environ, {'RAILWAY_ENVIRONMENT': 'staging'}, clear=False):
            filtered, skipped = _filter_local_safe(_canonical())
        self.assertEqual(len(filtered), 6)
        self.assertEqual(skipped, [])

    def test_local_strips_denied_tasks(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            os.environ.pop('ENABLE_BEAT_TASKS', None)
            filtered, skipped = _filter_local_safe(_canonical())
        # Allowed tasks pass through
        self.assertIn('cleanup-stale-content', filtered)
        self.assertIn('monitor-celery-health', filtered)
        self.assertIn('worker-memory-capture', filtered)
        # Denied tasks dropped
        self.assertNotIn('scan-income-spider-orchestrator', filtered)
        self.assertNotIn('run-spider-network', filtered)
        self.assertNotIn('warm-up-spiders', filtered)
        # Skipped list is sorted
        self.assertEqual(
            skipped,
            sorted([
                'scan-income-spider-orchestrator',
                'run-spider-network',
                'warm-up-spiders',
            ]),
        )

    def test_local_with_override_opts_specific_task_back_in(self):
        with mock.patch.dict(
            os.environ,
            {'ENABLE_BEAT_TASKS': 'scan-income-spider-orchestrator'},
            clear=False,
        ):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            filtered, skipped = _filter_local_safe(_canonical())
        # Override re-enables the named task
        self.assertIn('scan-income-spider-orchestrator', filtered)
        # Other denied tasks still skipped
        self.assertNotIn('run-spider-network', filtered)
        self.assertNotIn('warm-up-spiders', filtered)
        # Skipped list reflects only the un-overridden denies
        self.assertEqual(skipped, ['run-spider-network', 'warm-up-spiders'])

    def test_local_with_csv_override_multiple_tasks(self):
        with mock.patch.dict(
            os.environ,
            {'ENABLE_BEAT_TASKS': 'scan-income-spider-orchestrator, run-spider-network ,  '},
            clear=False,
        ):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            filtered, skipped = _filter_local_safe(_canonical())
        # Whitespace + trailing empty values handled
        self.assertIn('scan-income-spider-orchestrator', filtered)
        self.assertIn('run-spider-network', filtered)
        self.assertNotIn('warm-up-spiders', filtered)
        self.assertEqual(skipped, ['warm-up-spiders'])

    def test_filter_does_not_touch_non_denied_tasks(self):
        """Sanity: only LOCAL_DENY_TASKS entries should ever be filtered."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('RAILWAY_ENVIRONMENT', None)
            os.environ.pop('ENABLE_BEAT_TASKS', None)
            sched = {
                'monitor-celery-health': {'task': 'a', 'interval': 60},
                'cleanup-stale-content': {'task': 'b', 'interval': 60},
                'worker-memory-capture': {'task': 'c', 'interval': 300},
            }
            filtered, skipped = _filter_local_safe(sched)
        self.assertEqual(len(filtered), 3)
        self.assertEqual(skipped, [])

    def test_deny_list_has_expected_v1_entries(self):
        """Lock in the v1 denylist so additions/removals require an
        explicit code change + a touch to this test (and ideally a
        Rigby sign-off)."""
        expected = {
            'scan-income-spider-orchestrator',
            'scan-spider-opportunities',
            'run-spider-network',
            'warm-up-spiders',
            'backfill-spider-embeddings',
            'generate-operator-edge-newsletter',
        }
        self.assertEqual(LOCAL_DENY_TASKS, expected)
