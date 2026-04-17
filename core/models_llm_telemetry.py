"""
Session 1098: LLM Call Telemetry

Per-LLM-invocation telemetry model. Records one row per model API call
with execution_id correlation, provider/model, duration, token counts,
retry count, error type, and cancellation flag.

Intended sink for ``core.services.llm_call_wrapper``. See that module
for the wrapper that writes these rows around every LLM call, and the
broader plan in conversation pa-3c7ddc058db1 (Rigby's boardroom-dispatch
remediation, PR #1 of 4):

    #1 (this + wrapper): execution_id + per-call telemetry
    #2: CI lint forbidding direct SDK calls outside the wrapper
    #3: Cooperative cancel_token end-to-end (provider aborts)
    #4: Nested dispatch budget (parent token propagates to children)

``execution_id`` is stored as a plain UUIDField (not a FK to
AgentExecution) so telemetry survives AgentExecution row deletion — the
cleanup watchdog occasionally prunes old executions and we still want
the LLM call history for postmortem.
"""

import uuid

from django.db import models
from django.utils import timezone


class LLMCallEvent(models.Model):
    """One row per LLM API call, correlated to an AgentExecution."""

    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    ERROR_TYPE_CHOICES = [
        ('', 'None'),
        ('timeout', 'Timeout'),
        ('rate_limit', 'Rate Limit'),
        ('auth', 'Auth Error'),
        ('api_error', 'API Error'),
        ('client_error', 'Client Error'),
        ('cancelled', 'Cancelled'),
        ('unknown', 'Unknown'),
    ]

    call_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False,
    )
    execution_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text=(
            'UUID of owning AgentExecution (core_agentexecution). NULL '
            'for detached calls (tests, scripts, PA flows with no '
            'execution record).'
        ),
    )
    agent_name = models.CharField(
        max_length=120, blank=True, default='', db_index=True,
        help_text='Agent that initiated this LLM call (dashboards filter here).',
    )
    provider = models.CharField(max_length=50, blank=True, default='')
    model = models.CharField(max_length=120, blank=True, default='')

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='STARTED', db_index=True,
    )
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)

    tokens_in = models.IntegerField(null=True, blank=True)
    tokens_out = models.IntegerField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)

    error_type = models.CharField(
        max_length=50, blank=True, default='',
        choices=ERROR_TYPE_CHOICES,
    )
    error_message = models.TextField(blank=True, default='')
    cancelled = models.BooleanField(default=False, db_index=True)

    # Freeform metadata: caller-supplied context (task_id, parent_trace_id,
    # provider-specific options). Kept small — the per-execution
    # AgentExecution.output_data is the place for large payloads.
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'core'
        ordering = ['-started_at']
        indexes = [
            models.Index(
                fields=['execution_id', '-started_at'],
                name='llm_call_exec_time',
            ),
            models.Index(
                fields=['provider', '-started_at'],
                name='llm_call_provider_time',
            ),
            models.Index(
                fields=['-started_at', 'status'],
                name='llm_call_time_status',
            ),
        ]

    def __str__(self):
        return (
            f"{self.provider}/{self.model} [{self.status}] "
            f"call={str(self.call_id)[:8]}"
        )
