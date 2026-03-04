"""
PolicyExperiment — A/B testing framework for OpsAutopilot policy parameters.

Session 1090: Autonomy #11 — Experiment Engine

Experiments test policy parameter changes safely:
- Baseline: current production parameters
- Treatment: proposed new parameters
- Metrics: captured at start and periodically during the experiment
- Decision: auto-promote if treatment improves key metrics,
  auto-rollback if it degrades them

Each experiment targets a single policy and parameter set.
Only one active experiment per policy at a time.
"""

import uuid
from django.db import models
from django.utils import timezone


class PolicyExperiment(models.Model):
    """
    A single policy parameter experiment (A/B test).

    Lifecycle: draft → active → (promoted | rolled_back | expired)
    """

    STATUS_CHOICES = [
        ('draft', 'Draft — not yet started'),
        ('active', 'Active — treatment parameters in effect'),
        ('promoted', 'Promoted — treatment became new default'),
        ('rolled_back', 'Rolled Back — reverted to baseline'),
        ('expired', 'Expired — ended without decision'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # What is being tested
    policy_name = models.CharField(
        max_length=60, db_index=True,
        help_text="OpsAutopilot policy name (e.g., 'portfolio_allocator', 'roi_throttle')",
    )
    description = models.TextField(
        blank=True,
        help_text="Human-readable description of what this experiment tests",
    )

    # Parameters
    baseline_params = models.JSONField(
        help_text="Current production parameters (snapshot at experiment start)",
    )
    treatment_params = models.JSONField(
        help_text="Proposed new parameters to test",
    )

    # Success criteria
    success_metric = models.CharField(
        max_length=60,
        help_text="Metric to evaluate (e.g., 'iqroi', 'publish_pass_rate', 'error_rate')",
    )
    success_threshold_pct = models.FloatField(
        default=5.0,
        help_text="Treatment must beat baseline by this % to promote",
    )
    failure_threshold_pct = models.FloatField(
        default=-10.0,
        help_text="If treatment underperforms by this %, auto-rollback",
    )
    min_duration_hours = models.IntegerField(
        default=24,
        help_text="Minimum hours before auto-decision (collect enough data)",
    )
    max_duration_hours = models.IntegerField(
        default=168,
        help_text="Maximum hours — expires if no clear winner (default 7 days)",
    )

    # Metrics snapshots
    baseline_metrics = models.JSONField(
        default=dict, blank=True,
        help_text="Metrics captured at experiment start (baseline period)",
    )
    treatment_metrics = models.JSONField(
        default=dict, blank=True,
        help_text="Latest metrics under treatment parameters",
    )

    # Lifecycle
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    decision_reason = models.TextField(
        blank=True,
        help_text="Why the experiment was promoted/rolled back/expired",
    )

    # Attribution
    created_by = models.CharField(
        max_length=100, blank=True,
        help_text="Who created this experiment (user, PA, autopilot)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_policy_experiment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['policy_name', 'status']),
            models.Index(fields=['-created_at']),
        ]
        constraints = [
            # Only one active experiment per policy
            models.UniqueConstraint(
                fields=['policy_name'],
                condition=models.Q(status='active'),
                name='unique_active_experiment_per_policy',
            ),
        ]

    def __str__(self):
        return (
            f"{self.policy_name} | {self.status} | "
            f"{self.description[:50] if self.description else 'no desc'}"
        )

    def start(self):
        """Activate the experiment — treatment params take effect."""
        self.status = 'active'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def promote(self, reason: str = ''):
        """Treatment won — make it the new default."""
        self.status = 'promoted'
        self.ended_at = timezone.now()
        self.decision_reason = reason or 'Treatment outperformed baseline'
        self.save(update_fields=[
            'status', 'ended_at', 'decision_reason', 'updated_at',
        ])

    def rollback(self, reason: str = ''):
        """Treatment lost — revert to baseline."""
        self.status = 'rolled_back'
        self.ended_at = timezone.now()
        self.decision_reason = reason or 'Treatment underperformed baseline'
        self.save(update_fields=[
            'status', 'ended_at', 'decision_reason', 'updated_at',
        ])

    def expire(self, reason: str = ''):
        """Experiment ran too long without a clear winner."""
        self.status = 'expired'
        self.ended_at = timezone.now()
        self.decision_reason = reason or 'No clear winner within max duration'
        self.save(update_fields=[
            'status', 'ended_at', 'decision_reason', 'updated_at',
        ])

    @property
    def is_mature(self) -> bool:
        """Has the experiment run long enough for a decision?"""
        if not self.started_at:
            return False
        elapsed = (timezone.now() - self.started_at).total_seconds() / 3600
        return elapsed >= self.min_duration_hours

    @property
    def is_expired(self) -> bool:
        """Has the experiment exceeded its max duration?"""
        if not self.started_at:
            return False
        elapsed = (timezone.now() - self.started_at).total_seconds() / 3600
        return elapsed >= self.max_duration_hours
