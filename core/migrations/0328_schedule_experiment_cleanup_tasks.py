"""
Session 1103c: schedule cleanup_stale_running_experiments and
reconcile_experiment_status_outcome so Experiment rows stop piling
up in the running/pending split forever.

Root cause (found this session): gate_progression_pipeline creates
an Experiment with status='running'+outcome='pending' every time
a decision is promoted, and auto_kpi_tracking is the only path
that transitions it → but that path requires a live KPI value
being fed in, which never happens for Discussion/Panel-category
decisions. Result: Experiments pile up and pilots_tool stats
shows permanently alarming "n running / n pending" numbers.

Added two new Celery tasks this session:
  - cleanup_stale_running_experiments(hours_old, dry_run) —
    marks Experiments older than `hours_old` with status='running'
    and outcome='pending' as status='inconclusive' outcome='learn'.
  - reconcile_experiment_status_outcome(dry_run) — fixes the
    separate inconsistency where outcome had been set but status
    was never bumped.

Schedules:
  - cleanup_stale_running_experiments: every 6 hours with hours_old=72
  - reconcile_experiment_status_outcome: every hour
"""
from django.db import migrations
import json


def schedule_experiment_cleanup(apps, schema_editor):
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')

    every_6h, _ = IntervalSchedule.objects.get_or_create(
        every=6, period='hours',
    )
    every_1h, _ = IntervalSchedule.objects.get_or_create(
        every=1, period='hours',
    )

    PeriodicTask.objects.update_or_create(
        name='cleanup-stale-running-experiments',
        defaults={
            'task': 'core.tasks.cleanup_stale_running_experiments',
            'interval': every_6h,
            'enabled': True,
            'kwargs': json.dumps({'hours_old': 72, 'dry_run': False}),
            'description': (
                'Session 1103c: mark Experiments >72h in running+pending '
                'as inconclusive/learn so pilots_tool stats reflects '
                'reality. Fixes the pattern where Discussion-category '
                'decisions create experiments that never transition.'
            ),
            'queue': 'long_running',
        },
    )

    PeriodicTask.objects.update_or_create(
        name='reconcile-experiment-status-outcome',
        defaults={
            'task': 'core.tasks.reconcile_experiment_status_outcome',
            'interval': every_1h,
            'enabled': True,
            'kwargs': json.dumps({'dry_run': False}),
            'description': (
                'Session 1103c: bump Experiment.status when '
                'outcome_classification has been set but status '
                'is still running. Fixes a separate state drift '
                'between the KPI completer and the reporting view.'
            ),
            'queue': 'long_running',
        },
    )


def unschedule_experiment_cleanup(apps, schema_editor):
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')
    PeriodicTask.objects.filter(
        name__in=[
            'cleanup-stale-running-experiments',
            'reconcile-experiment-status-outcome',
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0327_projectworkspace_allow_autonomous_writes'),
        ('django_celery_beat', '0018_improve_crontab_helptext'),
    ]

    operations = [
        migrations.RunPython(
            schedule_experiment_cleanup,
            unschedule_experiment_cleanup,
        ),
    ]
