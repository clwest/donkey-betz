"""
Models for Intelligence System - Action Plans and Execution
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class ActionPlan(models.Model):
    """Store and track action plan execution"""

    STATUS_CHOICES = [
        ('created', 'Created'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_plans', null=True, blank=True)

    # Opportunity details
    opportunity_id = models.CharField(max_length=100)
    opportunity_title = models.CharField(max_length=255)
    opportunity_data = models.JSONField(default=dict)

    # Plan details
    plan_data = models.JSONField(default=dict)  # Full plan from AI
    steps = models.JSONField(default=list)  # Extracted steps
    resources = models.JSONField(default=list)
    timeline = models.CharField(max_length=255, blank=True)
    expected_outcome = models.TextField(blank=True)

    # Execution tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    progress = models.IntegerField(default=0)  # 0-100
    current_step = models.IntegerField(default=0)
    completed_steps = models.JSONField(default=list)

    # Execution details
    execution_logs = models.JSONField(default=list)
    agent_tasks = models.JSONField(default=list)  # Track which agents are working
    results = models.JSONField(default=dict)  # Store results from each step

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    # Celery task tracking
    celery_task_id = models.CharField(max_length=255, blank=True)

    class Meta:
        app_label = 'intelligence'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['opportunity_id']),
        ]

    def __str__(self):
        return f"{self.opportunity_title} - {self.status} ({self.progress}%)"

    def start_execution(self):
        """Start executing this plan"""
        from intelligence.tasks import execute_action_plan

        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()

        # Launch Celery task
        result = execute_action_plan.delay(str(self.id))
        self.celery_task_id = result.id
        self.save()

        return result.id

    def add_log(self, message, level='info', agent=None):
        """Add execution log entry"""
        log_entry = {
            'timestamp': timezone.now().isoformat(),
            'level': level,
            'message': message,
            'agent': agent
        }
        self.execution_logs.append(log_entry)
        self.save()

    def update_progress(self, step_number=None, step_completed=False):
        """Update execution progress"""
        if step_number:
            self.current_step = step_number

        if step_completed and step_number not in self.completed_steps:
            self.completed_steps.append(step_number)

        # Calculate progress based on completed steps
        if self.steps:
            self.progress = int((len(self.completed_steps) / len(self.steps)) * 100)

        self.last_activity = timezone.now()
        self.save()

    def mark_completed(self):
        """Mark plan as completed"""
        self.status = 'completed'
        self.progress = 100
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message):
        """Mark plan as failed"""
        self.status = 'failed'
        self.add_log(f"Execution failed: {error_message}", level='error')
        self.save()


class ActionPlanStep(models.Model):
    """Individual step in an action plan"""

    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='step_details')
    step_number = models.IntegerField()
    description = models.TextField()

    # Agent assignment
    assigned_agent = models.CharField(max_length=100, blank=True)
    agent_task_data = models.JSONField(default=dict)

    # Execution
    status = models.CharField(max_length=20, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(default=dict)

    class Meta:
        app_label = 'intelligence'
        ordering = ['action_plan', 'step_number']
        unique_together = ['action_plan', 'step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.description[:50]}..."


class ActionPlanExecution(models.Model):
    """Action-plan execution record (renamed from AgentExecution in S1243).

    Was previously named `AgentExecution`, which collided in the Django model
    registry with `core.AgentExecution` (canonical orchestration model, 984 live
    rows) and `agents.AgentExecution` (dormant rich-execution surface). Renamed
    here to remove the class-name collision and clarify intent: this model
    tracks per-step execution of `ActionPlan` flows, not generic agent runs.
    """
    action_plan = models.ForeignKey(ActionPlan, on_delete=models.CASCADE, related_name='agent_executions')
    agent_name = models.CharField(max_length=100)
    status = models.CharField(max_length=32, default='started')  # e.g. started, running, success, failed
    step_number = models.IntegerField(null=True, blank=True)
    payload = models.JSONField(default=dict)  # arbitrary task/execution metadata
    logs = models.JSONField(default=list)     # optional log lines for this execution

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'intelligence'
        indexes = [
            models.Index(fields=['agent_name']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.agent_name} [{self.status}] (step={self.step_number})"

