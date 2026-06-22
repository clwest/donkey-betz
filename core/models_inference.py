"""Session 1198 — Initiative attribution inference models (§6.2 Phase 2).

Holds the lookup tables that power the inference cascade in
``core/services/initiative_inference.py``. Currently a single model:
``AgentInitiativeAffinity`` — maps ``(workspace_id, agent_name) → initiative_id``
so that orphan-prone create paths can deduce the correct Initiative
when callers omit ``initiative_id``.

Design memo: docs/specs/INITIATIVES_FIRST_BACKBONE.md §6.2 (Phase 2
inference design). Rigby's draft was locked in conversation
``pa-ea12236c83eb4826``.

Why a model (not config / on-the-fly compute):
- **Pinning + expiry + provenance** for free.
- Queryable from inference path with cheap composite index hit.
- Static seeds can coexist with future learned suggestions without
  schema churn (different ``source`` values, same row shape).
- See QA1 in the design memo for the full options trade-off.
"""

import uuid

from django.db import models


class AgentInitiativeAffinity(models.Model):
    """Pinned association between (workspace, agent) and an Initiative.

    Used by the §6.2 cascade Step 3 to attach orphan-bound deliverables
    when the callsite omitted ``initiative_id`` and tool-context didn't
    carry one either. Kind-policy gating is applied at decision time
    by ``initiative_inference.infer_initiative_id`` — this model does
    NOT enforce kind constraints (it's a pure lookup table; policy
    lives in the inference function so it can be tuned without
    migrations).

    Uniqueness: one row per ``(workspace, agent_name, initiative)``
    triple. Multiple affinities for the same ``(workspace, agent_name)``
    pointing at different initiatives ARE allowed — at inference time
    we filter to one valid candidate by kind/recency/confidence rules.
    """

    class Source(models.TextChoices):
        STATIC_SEED = 'static_seed', 'Static seed (hand-curated, ships in code)'
        MANUAL_PIN = 'manual_pin', 'Manual pin (operator-set via admin/cmd)'
        LEARNED_SUGGESTION = 'learned_suggestion', 'Learned suggestion (non-authoritative until reviewed)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    workspace = models.ForeignKey(
        'core.ProjectWorkspace',
        on_delete=models.CASCADE,
        related_name='agent_initiative_affinities',
        help_text='Workspace this affinity applies in. Affinity is workspace-scoped — same agent can have different defaults per workspace.',
    )
    agent_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Canonical agent name (matches AgentExecution.owner_agent / actor labels like "Rigby", "ClaudeCode").',
    )
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.CASCADE,
        related_name='agent_affinities',
        help_text='Target Initiative the agent\'s output gets attached to when no explicit/propagated initiative_id is supplied.',
    )

    confidence = models.FloatField(
        default=0.90,
        help_text=(
            'Confidence floor 0-1. Phase 2 cascade requires '
            'confidence >= 0.90 for kind=project attaches and >= 0.70 '
            'for kind=investigation attaches. Static seeds default '
            'to 0.90; manual pins typically 0.95-1.00; learned '
            'suggestions land 0.50-0.85.'
        ),
    )

    source = models.CharField(
        max_length=24,
        choices=Source.choices,
        default=Source.STATIC_SEED,
        db_index=True,
        help_text=(
            'Provenance of the affinity row. Phase 2 v1 only uses '
            'static_seed + manual_pin as authoritative for inference; '
            'learned_suggestion rows surface in operator reports but '
            'do not attach automatically.'
        ),
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            'Optional TTL. NULL = never expires (static_seed / manual_pin '
            'default). Learned suggestions SHOULD have an expiry to '
            'prevent stale auto-attachments.'
        ),
    )
    last_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last operator review timestamp. Reports surface rows un-reviewed for >N days.',
    )

    notes = models.TextField(
        blank=True,
        default='',
        help_text='Free-form rationale (e.g., "ResearchAgent → SpiderContextUtilizationRetune because PR-3B was tagged so").',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['workspace', 'agent_name', '-confidence']
        verbose_name = 'Agent → Initiative Affinity'
        verbose_name_plural = 'Agent → Initiative Affinities'
        constraints = [
            models.UniqueConstraint(
                fields=['workspace', 'agent_name', 'initiative'],
                name='affinity_unique_per_workspace_agent_initiative',
            ),
        ]
        indexes = [
            # Primary inference-time lookup hits this composite.
            models.Index(
                fields=['workspace', 'agent_name', 'expires_at'],
                name='affinity_inference_lookup_idx',
            ),
        ]

    def __str__(self):
        return (
            f'{self.agent_name} → {self.initiative.name[:40]} '
            f'(ws={str(self.workspace_id)[:8]}, conf={self.confidence}, src={self.source})'
        )
