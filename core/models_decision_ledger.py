"""
Decision Ledger — structured record of every autopilot policy decision.

Session 1090: Autonomy #12 — Decision Ledger

Each OpsAutopilot cycle creates one DecisionLedgerEntry per policy
evaluated. Unlike AutopilotAction (which logs *actions taken*), the
ledger records *every decision* including no-ops, with structured
inputs and outputs for queryability, debugging, and replay.

Key fields:
- cycle_id: groups all entries from one autopilot cycle
- policy: which policy was evaluated
- inputs: structured dict of what the policy saw (metrics, thresholds)
- decision: what the policy decided (action, reason, affected agents/desks)
- counterfactual: what would have happened under alternative params
"""

import uuid
from django.db import models


class DecisionLedgerEntry(models.Model):
    """
    One policy evaluation result within an autopilot cycle.

    Queryable by cycle_id, policy, desk, decision_type for trend analysis.
    """

    DECISION_TYPES = [
        ('no_op', 'No action needed'),
        ('action_taken', 'Action executed'),
        ('dry_run', 'Would have acted (dry run)'),
        ('blocked', 'Action blocked by guardrail'),
        ('skipped', 'Policy skipped (error/disabled)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Cycle grouping
    cycle_id = models.UUIDField(
        db_index=True,
        help_text="Groups all entries from one autopilot cycle",
    )
    cycle_ts = models.DateTimeField(
        db_index=True,
        help_text="When this cycle ran",
    )

    # What was evaluated
    policy = models.CharField(
        max_length=60, db_index=True,
        help_text="Policy name (e.g., 'timeout_spike', 'budget_controller')",
    )
    desk = models.CharField(
        max_length=20, blank=True, db_index=True,
        help_text="Desk affected (if applicable)",
    )

    # Decision
    decision_type = models.CharField(
        max_length=20, choices=DECISION_TYPES, db_index=True,
    )
    decision_summary = models.CharField(
        max_length=200, blank=True,
        help_text="One-line human-readable summary",
    )

    # Structured data
    inputs = models.JSONField(
        default=dict,
        help_text="Policy inputs: metrics, thresholds, current state",
    )
    outputs = models.JSONField(
        default=dict,
        help_text="Policy outputs: actions, changes, recommendations",
    )
    counterfactual = models.JSONField(
        default=dict, blank=True,
        help_text="What would have happened under different params",
    )

    # Experiment context
    experiment_id = models.UUIDField(
        null=True, blank=True, db_index=True,
        help_text="Active experiment ID (if policy params are under test)",
    )
    params_used = models.JSONField(
        default=dict, blank=True,
        help_text="Actual parameter values used for this decision",
    )

    # Performance
    duration_ms = models.IntegerField(
        default=0,
        help_text="How long this policy evaluation took",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_decision_ledger'
        ordering = ['-cycle_ts', 'policy']
        indexes = [
            models.Index(fields=['cycle_id', 'policy']),
            models.Index(fields=['policy', '-cycle_ts']),
            models.Index(fields=['decision_type', '-cycle_ts']),
            models.Index(fields=['-cycle_ts']),
        ]

    def __str__(self):
        return (
            f"{self.policy} | {self.decision_type} | "
            f"{self.decision_summary[:60]}"
        )
