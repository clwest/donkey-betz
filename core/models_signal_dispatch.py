"""
Signal Dispatch audit model — Session 2933 A3 (v1).

Records every attempt to fire a mapped agent in reaction to a
``SignalCluster`` crossing a rule's threshold. The mapping table itself
is deliberately kept in Python code (``core.services.signal_dispatch_service``)
per S2933 Rigby zoom-out — this table is the audit + observability
surface, not a business-rules store.

Contract (S2933 SIGN):
    * `outcome` and `error_summary` are load-bearing — they exist so a
      transient failure never strands a cluster silently. Manual retry
      via ``manage.py resend_signal_dispatch --dispatch-id <id>``.
    * `agent_execution_id` is a raw UUID (not FK) so the audit row
      survives ``cleanup_stale_agent_executions``-style retention sweeps.
    * `rule_key` is the stable identifier for a (pattern_type, agent) pairing;
      queries "how many dispatches did rule X fire today" are one filter.
    * Dedup gate for the scanner: a cluster is skipped for a rule when a
      prior succeeded-or-in-flight ``SignalDispatch(cluster, rule_key)``
      exists. Failed dispatches do NOT gate — they permit retry.
"""
import uuid

from django.db import models


class SignalDispatch(models.Model):
    """Audit row for a signal-triggered agent dispatch (S2933 A3 v1)."""

    OUTCOME_CHOICES = [
        ('queued', 'Queued'),
        ('dispatched', 'Dispatched'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('skipped_cap', 'Skipped — cap reached'),
        ('skipped_not_actionable', 'Skipped — cluster not actionable'),
        ('rejected_agent_missing', 'Rejected — agent not in registry'),
        ('rejected_unknown_rule', 'Rejected — rule key not registered'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    rule_key = models.CharField(
        max_length=100,
        db_index=True,
        help_text=(
            "Stable identifier of the (pattern_type, agent) rule that "
            "produced this dispatch. Sourced from "
            "``core.services.signal_dispatch_service.SIGNAL_DISPATCH_RULES``."
        ),
    )
    pattern_type = models.CharField(
        max_length=30,
        db_index=True,
        help_text="Copied from the triggering SignalCluster for post-hoc queries.",
    )
    agent_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="AGENT_MAP key that was dispatched (or would have been).",
    )
    signal_cluster = models.ForeignKey(
        'core.SignalCluster',
        on_delete=models.CASCADE,
        related_name='dispatches',
        help_text="The cluster whose threshold crossing triggered this dispatch.",
    )
    outcome = models.CharField(
        max_length=30,
        choices=OUTCOME_CHOICES,
        default='queued',
        db_index=True,
    )
    error_summary = models.TextField(
        blank=True,
        default='',
        help_text=(
            "Short human-readable failure reason when outcome != succeeded. "
            "Populated for failed / rejected_* outcomes."
        ),
    )
    input_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Frozen context handed to AgentRouter.route (cluster snapshot: "
            "keywords / strength / confidence / summary / rule_key)."
        ),
    )
    agent_execution_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "AgentExecution.id captured from AgentResult.execution_id when "
            "the dispatch produced one. Raw UUID (not FK) so the audit row "
            "survives execution-row cleanup."
        ),
    )
    scan_run_id = models.CharField(
        max_length=64,
        blank=True,
        default='',
        db_index=True,
        help_text=(
            "Correlation id shared by all dispatches enqueued in one scan tick. "
            "Blank for manual dispatches via ``resend_signal_dispatch``."
        ),
    )
    dispatched_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Signal Dispatch'
        verbose_name_plural = 'Signal Dispatches'
        ordering = ['-dispatched_at']
        indexes = [
            models.Index(fields=['rule_key', '-dispatched_at']),
            models.Index(fields=['signal_cluster', 'rule_key']),
        ]

    def __str__(self):
        return f"SignalDispatch({self.rule_key} -> {self.agent_name} = {self.outcome})"
