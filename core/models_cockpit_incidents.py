"""
Cockpit Incidents — lightweight incident management for the Focus Cockpit.
Session P17: Incident Commander.
"""
import uuid
from django.db import models
from django.conf import settings  # noqa: F401


class CockpitIncident(models.Model):
    """A declared incident tracking an operational issue."""
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('mitigating', 'Mitigating'),
        ('resolved', 'Resolved'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    owner = models.CharField(max_length=100, blank=True, default='')
    resolution_summary = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title} ({self.status})"


class CockpitIncidentEvent(models.Model):
    """An event in an incident's timeline: note, link, or status change."""
    EVENT_TYPE_CHOICES = [
        ('note', 'Note'),
        ('link', 'Link'),
        ('status_change', 'Status Change'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(
        CockpitIncident,
        on_delete=models.CASCADE,
        related_name='events',
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    actor = models.CharField(max_length=100, default='operator')
    content = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type} on {self.incident_id} @ {self.created_at}"
