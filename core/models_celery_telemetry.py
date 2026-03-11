"""
Session 983: Celery Task Telemetry

Lightweight telemetry model for Celery task executions. Populated via
Celery signals (task_prerun, task_postrun, task_failure) so we own the
observability data instead of depending on django_celery_results which
requires CELERY_RESULT_BACKEND='django-db'.

This solves the "Celery tasks: 0" false-negative in status_snapshot_tool
when the result backend is Redis.
"""

from django.db import models
from django.utils import timezone


class CeleryTaskEvent(models.Model):
    """
    One row per Celery task execution.

    Created on task_prerun (status=STARTED), updated on task_postrun
    (status=SUCCESS) or task_failure (status=FAILURE).
    """

    STATUS_CHOICES = [
        ('QUEUED', 'Queued'),
        ('STARTED', 'Started'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure'),
        ('REVOKED', 'Revoked'),
    ]

    task_id = models.CharField(max_length=255, unique=True, db_index=True)
    task_name = models.CharField(max_length=255, db_index=True)
    queue = models.CharField(max_length=100, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED', db_index=True)
    worker = models.CharField(max_length=255, blank=True, default='')
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    rss_mb_start = models.FloatField(null=True, blank=True, help_text='RSS in MB when task began')
    rss_mb_end = models.FloatField(null=True, blank=True, help_text='RSS in MB when task finished')
    rss_delta_mb = models.FloatField(null=True, blank=True, help_text='RSS growth during task (end - start)')
    error_type = models.CharField(max_length=255, blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['-started_at', 'status'], name='celery_evt_time_status'),
            models.Index(fields=['task_name', '-started_at'], name='celery_evt_name_time'),
        ]

    def __str__(self):
        return f"{self.task_name} [{self.status}] {self.task_id[:12]}"
