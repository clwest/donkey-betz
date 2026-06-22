# Session 1198 — AgentInitiativeAffinity model for §6.2 Phase 2 inference.
#
# Trimmed-by-hand from the makemigrations auto-output (same Session 1196
# parked drift pattern as Session 1197 migration 0362). Drift removed:
# 16 AlterField ops + 4 Narrative* CreateModel ops belonging to the
# Session 1196 parked migration drift audit (Set A + Set B). Those get
# their own follow-up.

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0362_session_1197_initiative_kind"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgentInitiativeAffinity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "agent_name",
                    models.CharField(
                        db_index=True,
                        help_text='Canonical agent name (matches AgentExecution.owner_agent / actor labels like "Rigby", "ClaudeCode").',
                        max_length=100,
                    ),
                ),
                (
                    "confidence",
                    models.FloatField(
                        default=0.9,
                        help_text="Confidence floor 0-1. Phase 2 cascade requires confidence >= 0.90 for kind=project attaches and >= 0.70 for kind=investigation attaches. Static seeds default to 0.90; manual pins typically 0.95-1.00; learned suggestions land 0.50-0.85.",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            (
                                "static_seed",
                                "Static seed (hand-curated, ships in code)",
                            ),
                            ("manual_pin", "Manual pin (operator-set via admin/cmd)"),
                            (
                                "learned_suggestion",
                                "Learned suggestion (non-authoritative until reviewed)",
                            ),
                        ],
                        db_index=True,
                        default="static_seed",
                        help_text="Provenance of the affinity row. Phase 2 v1 only uses static_seed + manual_pin as authoritative for inference; learned_suggestion rows surface in operator reports but do not attach automatically.",
                        max_length=24,
                    ),
                ),
                (
                    "expires_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Optional TTL. NULL = never expires (static_seed / manual_pin default). Learned suggestions SHOULD have an expiry to prevent stale auto-attachments.",
                        null=True,
                    ),
                ),
                (
                    "last_reviewed_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Last operator review timestamp. Reports surface rows un-reviewed for >N days.",
                        null=True,
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text='Free-form rationale (e.g., "ResearchAgent → SpiderContextUtilizationRetune because PR-3B was tagged so").',
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "initiative",
                    models.ForeignKey(
                        help_text="Target Initiative the agent's output gets attached to when no explicit/propagated initiative_id is supplied.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="agent_affinities",
                        to="core.initiative",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        help_text="Workspace this affinity applies in. Affinity is workspace-scoped — same agent can have different defaults per workspace.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="agent_initiative_affinities",
                        to="core.projectworkspace",
                    ),
                ),
            ],
            options={
                "verbose_name": "Agent → Initiative Affinity",
                "verbose_name_plural": "Agent → Initiative Affinities",
                "ordering": ["workspace", "agent_name", "-confidence"],
                "indexes": [
                    models.Index(
                        fields=["workspace", "agent_name", "expires_at"],
                        name="affinity_inference_lookup_idx",
                    )
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="agentinitiativeaffinity",
            constraint=models.UniqueConstraint(
                fields=("workspace", "agent_name", "initiative"),
                name="affinity_unique_per_workspace_agent_initiative",
            ),
        ),
    ]
