"""
Session G1: Competitor Comparison Model

Stores structured competitor analysis results generated from ingested
source documents via RAG + LLM pipeline.  Each record captures a
side-by-side comparison, gap backlog, tools/stack extraction, and all
evidence chunks used.
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class CompetitorComparison(models.Model):
    """On-demand competitor comparison generated from a source document."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]

    GENERATED_BY_CHOICES = [
        ('PA', 'Personal Assistant'),
        ('API', 'API'),
        ('manual', 'Manual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competitor_name = models.CharField(max_length=255)
    source_document = models.ForeignKey(
        'content.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='competitor_comparisons',
        help_text='Source document used for RAG evidence extraction',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, default='')

    # Structured output sections
    review_json = models.JSONField(default=dict, blank=True, help_text='What they built, with evidence')
    comparison_table_json = models.JSONField(default=dict, blank=True, help_text='Side-by-side comparison rows')
    gap_backlog_json = models.JSONField(default=dict, blank=True, help_text='Gaps + acceptance tests')
    tools_stack_json = models.JSONField(default=dict, blank=True, help_text='Extracted tools/stack')
    evidence_json = models.JSONField(default=list, blank=True, help_text='All evidence chunks used')
    summary = models.TextField(blank=True, default='')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='competitor_comparisons',
    )
    generated_by = models.CharField(max_length=20, choices=GENERATED_BY_CHOICES, default='PA')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True, help_text='Token costs, timing, etc.')

    class Meta:
        app_label = 'core'
        db_table = 'core_competitor_comparison'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['competitor_name', '-created_at']),
        ]

    def __str__(self):
        return f"CompetitorComparison: {self.competitor_name} ({self.status})"
