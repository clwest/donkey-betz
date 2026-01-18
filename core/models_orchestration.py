"""
Orchestration Layer Models
==========================

Session 764: Multi-agent workflow orchestration with checkpointing,
human-in-the-loop approval gates, retry logic, and Celery integration.

Architecture:
    CustomWorkflow → OrchestrationExecution → OrchestrationStepExecution
                                           → OrchestrationApprovalGate
"""

import uuid
import logging
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class OrchestrationExecution(models.Model):
    """
    Tracks a single execution run of a CustomWorkflow.

    Contains checkpoint data for resume capability and aggregated
    cost tracking across all step executions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Workflow reference
    workflow = models.ForeignKey(
        'core.CustomWorkflow',
        on_delete=models.CASCADE,
        related_name='orchestration_executions'
    )

    # Who triggered
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orchestration_executions'
    )

    # Execution parameters
    input_data = models.JSONField(default=dict)  # Initial input to workflow

    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('paused', 'Paused'),  # Waiting for approval
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timed_out', 'Timed Out'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Progress tracking
    current_step = models.IntegerField(default=0)  # 0 = not started
    total_steps = models.IntegerField(default=0)

    # Checkpoint data - JSON snapshot of execution state
    checkpoint_data = models.JSONField(default=dict)
    # Example:
    # {
    #     "step_outputs": {1: {...}, 2: {...}},
    #     "accumulated_context": {...},
    #     "retry_counts": {3: 2},  # step 3 retried twice
    # }

    # Cost tracking (LLM costs)
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal('0.0000')
    )
    total_tokens = models.IntegerField(default=0)

    # Session 769: External API costs (ElevenLabs, Stability, Runway, etc.)
    total_external_cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal('0.0000'),
        help_text="Total cost from external APIs (TTS, images, video)"
    )
    external_cost_breakdown = models.JSONField(
        default=dict,
        help_text="Breakdown of external costs by API/service"
    )
    # Example:
    # {
    #     "elevenlabs_tts": 0.0432,
    #     "stability_ai": 0.065,
    #     "runway_ml": 0.0,
    #     "trained_voice": 0.05,
    # }

    # Error handling
    error_message = models.TextField(blank=True)
    error_step = models.IntegerField(null=True, blank=True)  # Which step failed

    # Output
    final_output = models.JSONField(default=dict)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    timeout_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Orchestration Execution'
        verbose_name_plural = 'Orchestration Executions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['triggered_by', 'status']),
        ]

    def __str__(self):
        return f"{self.workflow.name} - {self.status} ({self.current_step}/{self.total_steps})"

    def save_checkpoint(self, step_number: int, step_output: dict, context: dict = None) -> None:
        """Save checkpoint after successful step execution."""
        checkpoint = self.checkpoint_data or {}

        if 'step_outputs' not in checkpoint:
            checkpoint['step_outputs'] = {}
        checkpoint['step_outputs'][str(step_number)] = step_output

        if context:
            checkpoint['accumulated_context'] = context

        checkpoint['last_checkpoint_at'] = timezone.now().isoformat()

        self.checkpoint_data = checkpoint
        self.current_step = step_number
        self.save(update_fields=['checkpoint_data', 'current_step', 'updated_at'])

    def get_step_output(self, step_number: int) -> dict:
        """Get the output from a previously executed step."""
        checkpoint = self.checkpoint_data or {}
        step_outputs = checkpoint.get('step_outputs', {})
        return step_outputs.get(str(step_number), {})

    def increment_retry_count(self, step_number: int) -> int:
        """Increment and return retry count for a step."""
        checkpoint = self.checkpoint_data or {}

        if 'retry_counts' not in checkpoint:
            checkpoint['retry_counts'] = {}

        current = checkpoint['retry_counts'].get(str(step_number), 0)
        checkpoint['retry_counts'][str(step_number)] = current + 1

        self.checkpoint_data = checkpoint
        self.save(update_fields=['checkpoint_data', 'updated_at'])

        return current + 1

    def get_retry_count(self, step_number: int) -> int:
        """Get current retry count for a step."""
        checkpoint = self.checkpoint_data or {}
        retry_counts = checkpoint.get('retry_counts', {})
        return retry_counts.get(str(step_number), 0)

    def add_cost(self, cost: Decimal, tokens: int = 0, external_cost: Decimal = None, external_breakdown: dict = None):
        """
        Add cost from a step execution.

        Session 769: Now tracks both LLM costs and external API costs.

        Args:
            cost: LLM cost for this step
            tokens: Token count for this step
            external_cost: Total external API cost for this step
            external_breakdown: Dict of external costs by API (e.g., {'elevenlabs_tts': 0.05})
        """
        self.total_cost = (self.total_cost or Decimal('0.0000')) + cost
        self.total_tokens = (self.total_tokens or 0) + tokens

        # Session 769: Track external costs
        if external_cost:
            self.total_external_cost = (self.total_external_cost or Decimal('0.0000')) + external_cost

        if external_breakdown:
            current_breakdown = self.external_cost_breakdown or {}
            for api, api_cost in external_breakdown.items():
                current_breakdown[api] = current_breakdown.get(api, 0) + float(api_cost)
            self.external_cost_breakdown = current_breakdown

        save_fields = ['total_cost', 'total_tokens', 'updated_at']
        if external_cost:
            save_fields.append('total_external_cost')
        if external_breakdown:
            save_fields.append('external_cost_breakdown')
        self.save(update_fields=save_fields)

    def mark_paused(self, reason: str = 'Waiting for approval'):
        """Mark execution as paused (waiting for approval)."""
        self.status = 'paused'
        self.paused_at = timezone.now()
        self.checkpoint_data = {
            **(self.checkpoint_data or {}),
            'pause_reason': reason
        }
        self.save(update_fields=['status', 'paused_at', 'checkpoint_data', 'updated_at'])

    def mark_running(self):
        """Resume execution from paused state."""
        self.status = 'running'
        self.paused_at = None
        self.save(update_fields=['status', 'paused_at', 'updated_at'])

    def mark_completed(self, final_output: dict = None):
        """Mark execution as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if final_output:
            self.final_output = final_output
            # Session 769: Sync total_tokens from final_output to model field
            if 'total_tokens' in final_output:
                self.total_tokens = final_output['total_tokens']
        self.save(update_fields=['status', 'completed_at', 'final_output', 'total_tokens', 'updated_at'])

    def mark_failed(self, error_message: str, error_step: int = None):
        """Mark execution as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.error_step = error_step
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'error_step', 'completed_at', 'updated_at'])


class OrchestrationStepExecution(models.Model):
    """
    Tracks individual step execution within an orchestration run.

    Links to the parent OrchestrationExecution and records
    timing, agent output, cost, and retry information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Parent execution
    orchestration = models.ForeignKey(
        OrchestrationExecution,
        on_delete=models.CASCADE,
        related_name='step_executions'
    )

    # Step reference
    workflow_step = models.ForeignKey(
        'core.CustomWorkflowStep',
        on_delete=models.SET_NULL,
        null=True,
        related_name='orchestration_executions'
    )
    step_number = models.IntegerField()

    # Agent information
    agent_name = models.CharField(max_length=100)

    # Session 765: Link to underlying AgentExecution for intelligence data
    execution_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the AgentExecution record for accessing memories, learning, and full execution data"
    )

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('waiting_approval', 'Waiting Approval'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('rolled_back', 'Rolled Back'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Input/Output
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)

    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    # Cost tracking (LLM costs)
    cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal('0.0000')
    )
    tokens_used = models.IntegerField(default=0)

    # Session 769: External API costs (ElevenLabs, Stability, Runway, etc.)
    external_cost = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal('0.0000'),
        help_text="External API costs for this step (TTS, images, video)"
    )
    external_cost_breakdown = models.JSONField(
        default=dict,
        help_text="Breakdown of external costs by API for this step"
    )

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Orchestration Step Execution'
        verbose_name_plural = 'Orchestration Step Executions'
        ordering = ['orchestration', 'step_number']
        indexes = [
            models.Index(fields=['orchestration', 'step_number']),
            models.Index(fields=['status']),
            models.Index(fields=['agent_name', 'status']),
        ]

    def __str__(self):
        return f"Step {self.step_number}: {self.agent_name} ({self.status})"

    def mark_running(self):
        """Mark step as running."""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def mark_completed(
        self,
        output_data: dict,
        cost: Decimal = None,
        tokens: int = 0,
        external_cost: Decimal = None,
        external_breakdown: dict = None
    ):
        """
        Mark step as completed with output.

        Session 769: Now tracks external API costs.
        """
        self.status = 'completed'
        self.output_data = output_data
        self.completed_at = timezone.now()

        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

        if cost:
            self.cost = cost
        self.tokens_used = tokens

        # Session 769: Track external costs
        if external_cost:
            self.external_cost = external_cost
        if external_breakdown:
            self.external_cost_breakdown = external_breakdown

        self.save(update_fields=[
            'status', 'output_data', 'completed_at',
            'duration_seconds', 'cost', 'tokens_used',
            'external_cost', 'external_cost_breakdown', 'updated_at'
        ])

    def mark_failed(self, error_message: str):
        """Mark step as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()

        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()

        self.save(update_fields=[
            'status', 'error_message', 'completed_at', 'duration_seconds', 'updated_at'
        ])

    def increment_retry(self) -> int:
        """Increment retry count and return new value."""
        self.retry_count += 1
        self.save(update_fields=['retry_count', 'updated_at'])
        return self.retry_count


class OrchestrationApprovalGate(models.Model):
    """
    Links orchestration step to human approval via HumanAttentionItem.

    When a step requires approval, this gate is created and linked
    to both the step execution and the HumanAttentionItem in the
    Mission Control system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Orchestration references
    orchestration = models.ForeignKey(
        OrchestrationExecution,
        on_delete=models.CASCADE,
        related_name='approval_gates'
    )
    step_execution = models.ForeignKey(
        OrchestrationStepExecution,
        on_delete=models.CASCADE,
        related_name='approval_gates'
    )

    # Link to Human Interface (UUID reference for flexibility)
    attention_item_id = models.UUIDField(null=True, blank=True)

    # Gate status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('modified', 'Modified'),  # Approved with changes
        ('auto_approved', 'Auto-Approved'),  # Timed out with auto-approve
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Approval config (from step)
    approval_config = models.JSONField(default=dict)
    # Example:
    # {
    #     "approval_timeout_hours": 24,
    #     "auto_approve_on_timeout": False,
    #     "required_role": "admin",
    #     "approval_message": "Please review the research output",
    # }

    # Decision data
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orchestration_approvals'
    )
    decision_notes = models.TextField(blank=True)
    modifications = models.JSONField(default=dict)  # For 'modified' status

    # Timing
    expires_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Orchestration Approval Gate'
        verbose_name_plural = 'Orchestration Approval Gates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['orchestration', 'status']),
        ]

    def __str__(self):
        return f"Approval Gate for Step {self.step_execution.step_number} ({self.status})"

    def approve(self, user, notes: str = ''):
        """Approve this gate."""
        self.status = 'approved'
        self.decided_by = user
        self.decision_notes = notes
        self.decided_at = timezone.now()
        self.save(update_fields=['status', 'decided_by', 'decision_notes', 'decided_at', 'updated_at'])

    def reject(self, user, notes: str = ''):
        """Reject this gate."""
        self.status = 'rejected'
        self.decided_by = user
        self.decision_notes = notes
        self.decided_at = timezone.now()
        self.save(update_fields=['status', 'decided_by', 'decision_notes', 'decided_at', 'updated_at'])

    def modify(self, user, modifications: dict, notes: str = ''):
        """Approve with modifications."""
        self.status = 'modified'
        self.decided_by = user
        self.modifications = modifications
        self.decision_notes = notes
        self.decided_at = timezone.now()
        self.save(update_fields=[
            'status', 'decided_by', 'modifications',
            'decision_notes', 'decided_at', 'updated_at'
        ])

    def auto_approve(self):
        """Auto-approve due to timeout (if configured)."""
        self.status = 'auto_approved'
        self.decision_notes = 'Auto-approved due to timeout'
        self.decided_at = timezone.now()
        self.save(update_fields=['status', 'decision_notes', 'decided_at', 'updated_at'])

    def is_expired(self) -> bool:
        """Check if approval window has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def attention_item(self):
        """Get the HumanAttentionItem by UUID."""
        if not self.attention_item_id:
            return None
        from core.models_human_interface import HumanAttentionItem
        try:
            return HumanAttentionItem.objects.get(id=self.attention_item_id)
        except HumanAttentionItem.DoesNotExist:
            return None

    def set_attention_item(self, item):
        """Set the attention item by object or UUID."""
        if item is None:
            self.attention_item_id = None
        elif hasattr(item, 'id'):
            self.attention_item_id = item.id
        else:
            self.attention_item_id = item
