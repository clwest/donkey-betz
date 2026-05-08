from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class CelerySyncCommandTests(SimpleTestCase):
    def test_sync_celery_schedules_raises_on_sync_error(self):
        with patch(
            'core.management.commands.sync_celery_schedules.Command._parse_celery_py_schedules',
            return_value={
                'test-task': {
                    'task': 'core.tasks.run_heartbeat',
                    'schedule': 60,
                }
            },
        ), patch(
            'core.management.commands.sync_celery_schedules.PeriodicTask.objects.values_list',
            return_value=[],
        ), patch(
            'core.management.commands.sync_celery_schedules.IntervalSchedule.objects.get_or_create',
            return_value=(object(), True),
        ), patch(
            'core.management.commands.sync_celery_schedules.PeriodicTask.objects.update_or_create',
            side_effect=Exception('db write failed'),
        ):
            with self.assertRaises(CommandError):
                call_command('sync_celery_schedules', source='celery')

    def test_add_critical_celery_tasks_raises_on_critical_sync_error(self):
        with patch(
            'core.management.commands.add_critical_celery_tasks.CRITICAL_TASKS',
            {
                'critical-test-task': {
                    'task': 'core.tasks.run_heartbeat',
                    'interval': 60,
                    'queue': 'broadcast',
                }
            },
        ), patch(
            'core.management.commands.add_critical_celery_tasks.PeriodicTask.objects.values_list',
            return_value=[],
        ), patch(
            'core.management.commands.add_critical_celery_tasks.IntervalSchedule.objects.get_or_create',
            return_value=(object(), True),
        ), patch(
            'core.management.commands.add_critical_celery_tasks.PeriodicTask.objects.update_or_create',
            side_effect=Exception('db write failed'),
        ), patch(
            'core.management.commands.add_critical_celery_tasks.PeriodicTask.objects.filter',
        ) as mock_filter:
            mock_filter.return_value.count.return_value = 0
            mock_filter.return_value.exists.return_value = False
            with self.assertRaises(CommandError):
                call_command('add_critical_celery_tasks')
