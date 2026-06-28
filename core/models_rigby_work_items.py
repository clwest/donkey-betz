"""
RigbyWorkItem — Rigby's internal operational queue.

Session 1250 PR 6. Created when Rigby Event Intake reaches an
actionable decision (``monitor`` / ``notify`` in v0). This is **NOT**
a notification surface for Chris — see
``docs/EVENT_SYSTEM_INVENTORY.md`` §13. Chris becomes the exception
handler when Rigby decides human judgment is needed; the default
target is Rigby's own queue.
"""
from __future__ import annotations

import uuid

from django.db import models


class RigbyWorkItem(models.Model):
    """One row per actionable intake decision. Rigby reviews her queue
    asynchronously; humans are notified later, only when Rigby decides
    she needs them.

    Idempotency: ``unique_together = ('source_event_ref', 'decision')``
    prevents duplicates when the intake task re-runs on the same
    ``event_ref``. Different decisions on the same ``event_ref`` (would
    only happen if rules change between runs — not in v0) get distinct
    rows.
    """

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Source linkage. ``source_mission_run`` points at the OpsRun where
    # the intake decision was recorded; ``source_event_ref`` is the
    # canonical handle for the originating event.
    source_mission_run = models.ForeignKey(
        'core.OpsRun',
        on_delete=models.CASCADE,
        related_name='rigby_work_items',
        help_text="The MissionRun (OpsRun with domain='mission') that produced this work item.",
    )
    source_event_ref = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Canonical '<source>:<source_id>' handle for the originating event.",
    )

    # Classification — mirrors the intake decision so the queue can be
    # filtered without joining to OpsRun.summary JSON.
    decision = models.CharField(
        max_length=30,
        db_index=True,
        help_text="One of: monitor / notify (v0 actionable). Closed vocab matches DECISION_VOCAB.",
    )
    severity = models.CharField(
        max_length=20,
        help_text="PR 2 closed vocab: debug / info / notice / warn / error / critical / unknown.",
    )
    mission_impact = models.CharField(
        max_length=20,
        help_text="PR 4 closed vocab: unknown / low / medium / high.",
    )
    priority = models.PositiveSmallIntegerField(
        default=1,
        db_index=True,
        help_text=(
            "Computed from mission_impact (unknown=1, low=3, medium=5, "
            "high=8). Higher = sooner Rigby should look at it."
        ),
    )

    # Human-readable surface for Rigby's queue UI.
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True, default='')
    recommended_next_action = models.TextField(blank=True, default='')
    evidence = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Evidence dict: at minimum {event_ref, rules_fired, "
            "decision_reason}. May include adapter-specific payload "
            "snippets in future PRs."
        ),
    )

    # Lifecycle.
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-priority', '-created_at']
        unique_together = [('source_event_ref', 'decision')]
        indexes = [
            models.Index(fields=['status', '-priority', '-created_at']),
            models.Index(fields=['decision', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.decision}] {self.title} ({self.status})"
