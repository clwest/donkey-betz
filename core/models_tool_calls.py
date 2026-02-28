"""
Session 861: Tool Call Recording System

Provides audit trail for agent tool calls. Every time an agent executes a tool,
the call is recorded including parameters, results, and timing data.

This addresses the HIGH RISK data persistence gap where tool call results
were previously 100% ephemeral with no audit trail.
"""

import uuid
import hashlib
import json
from typing import Any, Optional
from django.db import models
from django.utils import timezone


class ToolCallRecord(models.Model):
    """
    Records individual tool calls made by agents during execution.

    Provides:
    - Audit trail of what tools were called
    - Parameter tracking for debugging
    - Result summaries and hashes for verification
    - Performance metrics (latency)
    - Error tracking

    Example:
        record = ToolCallRecord.objects.create(
            trace_id=uuid.uuid4(),
            agent_name='StockAnalystAgent',
            tool_name='analyze_filing',
            parameters={'ticker': 'AAPL', 'filing_type': '10-K'},
            result_summary='{"success": true, "analysis": "..."}',
            result_hash='sha256:abc123...',
            latency_ms=1234,
            success=True
        )
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tracing
    trace_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Session trace ID for linking related tool calls"
    )
    conversation_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Conversation ID if from chat context"
    )

    # Agent info
    agent_name = models.CharField(
        max_length=255, db_index=True,
        help_text="Name of the agent that made the tool call"
    )

    # Tool info
    tool_name = models.CharField(
        max_length=100, db_index=True,
        help_text="Name of the tool that was called"
    )
    parameters = models.JSONField(
        default=dict,
        help_text="Parameters passed to the tool"
    )

    # Result info
    result_summary = models.TextField(
        blank=True,
        help_text="First 4KB of the result (for quick viewing)"
    )
    result_hash = models.CharField(
        max_length=72, blank=True,
        help_text="SHA256 hash of full result for verification (sha256:...)"
    )
    full_result = models.TextField(
        blank=True,
        help_text="Full result if under 64KB, otherwise empty"
    )
    result_size_bytes = models.IntegerField(
        default=0,
        help_text="Size of the full result in bytes"
    )

    # Status
    success = models.BooleanField(
        default=True,
        help_text="Whether the tool call succeeded"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if the tool call failed"
    )
    error_type = models.CharField(
        max_length=100, blank=True,
        help_text="Exception class name if failed"
    )

    # Performance
    latency_ms = models.IntegerField(
        default=0, db_index=True,
        help_text="Tool execution time in milliseconds"
    )

    # Context
    task_summary = models.CharField(
        max_length=500, blank=True,
        help_text="Summary of the task being executed"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'core_tool_call_record'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['agent_name', 'created_at']),
            models.Index(fields=['tool_name', 'created_at']),
            models.Index(fields=['success', 'created_at']),
            models.Index(fields=['trace_id', 'created_at']),
        ]

    def __str__(self):
        status = "OK" if self.success else "FAIL"
        return f"[{status}] {self.agent_name}.{self.tool_name} ({self.latency_ms}ms)"

    @classmethod
    def record(
        cls,
        agent_name: str,
        tool_name: str,
        parameters: dict,
        result: Any,
        latency_ms: int,
        success: bool = True,
        error_message: str = '',
        error_type: str = '',
        trace_id: str = None,
        conversation_id: str = None,
        task_summary: str = '',
    ) -> 'ToolCallRecord':
        """
        Convenience method to record a tool call.

        Args:
            agent_name: Name of the calling agent
            tool_name: Name of the tool called
            parameters: Dict of parameters passed to tool
            result: The tool's result (will be serialized)
            latency_ms: Execution time in milliseconds
            success: Whether the call succeeded
            error_message: Error message if failed
            error_type: Exception class name if failed
            trace_id: Optional trace ID for linking
            conversation_id: Optional conversation ID
            task_summary: Optional summary of the task

        Returns:
            ToolCallRecord instance
        """
        # Serialize result
        try:
            result_str = json.dumps(result, default=str)
        except Exception:
            result_str = str(result)

        result_bytes = result_str.encode('utf-8')
        result_size = len(result_bytes)

        # Create summary (first 4KB)
        result_summary = result_str[:4096]
        if len(result_str) > 4096:
            result_summary += '... [truncated]'

        # Hash the full result
        result_hash = f"sha256:{hashlib.sha256(result_bytes).hexdigest()}"

        # Store full result only if under 64KB
        full_result = result_str if result_size < 65536 else ''

        # Parse UUIDs if strings
        trace_uuid = None
        if trace_id:
            try:
                trace_uuid = uuid.UUID(str(trace_id))
            except (ValueError, TypeError):
                pass

        conv_uuid = None
        if conversation_id:
            try:
                conv_uuid = uuid.UUID(str(conversation_id))
            except (ValueError, TypeError):
                pass

        return cls.objects.create(
            agent_name=agent_name,
            tool_name=tool_name,
            parameters=parameters or {},
            result_summary=result_summary,
            result_hash=result_hash,
            full_result=full_result,
            result_size_bytes=result_size,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message or '',
            error_type=error_type or '',
            trace_id=trace_uuid,
            conversation_id=conv_uuid,
            task_summary=task_summary[:500] if task_summary else '',
        )


class ToolCallAggregate(models.Model):
    """
    Aggregated statistics for tool calls.

    Updated periodically to provide quick access to:
    - Call counts per agent/tool
    - Average latency
    - Success rates
    - Error patterns
    """

    # Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Aggregation key
    agent_name = models.CharField(max_length=255, db_index=True)
    tool_name = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)

    # Counts
    total_calls = models.IntegerField(default=0)
    success_calls = models.IntegerField(default=0)
    failed_calls = models.IntegerField(default=0)

    # Latency stats (in ms)
    avg_latency_ms = models.IntegerField(default=0)
    min_latency_ms = models.IntegerField(default=0)
    max_latency_ms = models.IntegerField(default=0)
    p95_latency_ms = models.IntegerField(default=0)

    # Error tracking
    top_errors = models.JSONField(
        default=list,
        help_text="List of top error types with counts"
    )

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_tool_call_aggregate'
        unique_together = ['agent_name', 'tool_name', 'date']
        ordering = ['-date', 'agent_name', 'tool_name']

    def __str__(self):
        rate = (self.success_calls / self.total_calls * 100) if self.total_calls > 0 else 0
        return f"{self.agent_name}.{self.tool_name} ({self.date}): {self.total_calls} calls, {rate:.1f}% success"

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_calls == 0:
            return 0.0
        return (self.success_calls / self.total_calls) * 100


class PAToolInsight(models.Model):
    """
    Learned insights from PA tool usage patterns.

    Mined from ToolCallRecord data by the analyze_pa_tool_patterns Celery task.
    Approved insights are injected into the PA system prompt to improve
    tool usage over time without manual schema fixes.

    Safety gating: insights start as 'candidate' and must reach 'approved'
    (either manually or via auto-promotion) before they affect PA behavior.
    """

    INSIGHT_TYPES = [
        ('param_correction', 'Parameter Correction'),
        ('error_pattern', 'Error Pattern'),
        ('success_pattern', 'Success Pattern'),
        ('follow_up', 'Follow-up Pattern'),
    ]
    SAFETY_CLASSES = [
        ('candidate', 'Candidate'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tool_name = models.CharField(max_length=100, db_index=True)
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    safety_class = models.CharField(max_length=20, choices=SAFETY_CLASSES, default='candidate')
    pattern = models.JSONField(help_text="Structured pattern data (used for dedup via unique_together)")
    prompt_snippet = models.TextField(help_text="Ready-to-inject text for PA system prompt")
    evidence_count = models.PositiveIntegerField(default=1)
    confidence = models.FloatField(default=0.0, help_text="0.0–1.0")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_pa_tool_insight'
        indexes = [
            models.Index(fields=['safety_class', 'tool_name']),
        ]

    def __str__(self):
        return f"[{self.safety_class}] {self.tool_name}/{self.insight_type} (n={self.evidence_count}, conf={self.confidence:.2f})"
