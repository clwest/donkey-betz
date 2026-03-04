"""
ImpactCredit — Multi-touch attribution for impact events.

Session: Autonomy #17 — Policy 21

When an ImpactEvent is recorded, credit is allocated:
- 70% last-touch: the agent/desk that directly produced the impact
- 30% assist: upstream agents/desks linked via trace_id, initiative,
  or deliverable chain

Guardrails:
- Max 2 hops upstream
- Assist credit capped at 30% total
- Only explicit links (no guessing)
"""

import uuid
from django.db import models


class ImpactCredit(models.Model):
    """
    One credit allocation row for a single ImpactEvent.

    Each ImpactEvent produces 1 last_touch row and 0-N assist rows.
    GoalAwareAllocator reads credited impact (not raw) for fair
    desk utility computation.
    """

    CREDIT_TYPES = [
        ('last_touch', 'Last Touch (70%)'),
        ('assist', 'Assist (30% split)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to source impact event
    impact_event = models.ForeignKey(
        'core.ImpactEvent',
        on_delete=models.CASCADE,
        related_name='credits',
        help_text="The impact event being attributed",
    )

    # Who gets credit
    desk = models.CharField(max_length=20, db_index=True)
    agent_name = models.CharField(max_length=100, blank=True, db_index=True)

    # Credit values
    credit_type = models.CharField(
        max_length=20, choices=CREDIT_TYPES, db_index=True,
    )
    credit_usd = models.DecimalField(
        max_digits=12, decimal_places=4, default=0,
        help_text="Dollar credit allocated",
    )
    credit_points = models.IntegerField(
        default=0,
        help_text="Impact point credit allocated",
    )
    credit_share = models.FloatField(
        default=0,
        help_text="Fraction of total credit (0.0 to 1.0)",
    )

    # Attribution chain
    hop_distance = models.IntegerField(
        default=0,
        help_text="0 = last touch, 1 = direct upstream, 2 = second hop",
    )
    link_type = models.CharField(
        max_length=30, blank=True,
        help_text="How the link was established (trace_id, initiative, dream, agent_chain)",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = 'core'
        db_table = 'core_impact_credit'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['desk', '-created_at']),
            models.Index(fields=['credit_type', '-created_at']),
            models.Index(fields=['impact_event', 'credit_type']),
        ]

    def __str__(self):
        return (
            f"{self.credit_type} | {self.desk} | "
            f"${self.credit_usd} | {self.agent_name}"
        )
