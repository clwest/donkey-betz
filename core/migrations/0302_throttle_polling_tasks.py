"""
Session 1103: Throttle high-frequency polling tasks from 30s to 120s.

poll_pending_trainings and poll_pending_3d_models were running every 30s
(238 runs / 2 hours). Trainings take minutes-to-hours, so 120s polling
is more than sufficient. Reduces MUSCULAR/LUNGS body system fatigue.
"""
from django.db import migrations


def throttle_polling_tasks(apps, schema_editor):
    IntervalSchedule = apps.get_model('django_celery_beat', 'IntervalSchedule')
    PeriodicTask = apps.get_model('django_celery_beat', 'PeriodicTask')

    interval, _ = IntervalSchedule.objects.get_or_create(
        every=120, period='seconds'
    )

    PeriodicTask.objects.filter(
        name__in=['poll-pending-trainings', 'poll-pending-3d-models']
    ).update(interval=interval)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0301_agentexecution_last_heartbeat_at"),
        ("django_celery_beat", "0018_improve_crontab_helptext"),
    ]

    operations = [
        migrations.RunPython(throttle_polling_tasks, migrations.RunPython.noop),
    ]
