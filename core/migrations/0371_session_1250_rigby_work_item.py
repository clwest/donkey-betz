# Session 1250 PR 6: RigbyWorkItem — Rigby's internal operational queue.
#
# Additive migration. New model only. No changes to existing tables.
# See docs/EVENT_SYSTEM_INVENTORY.md §13.

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0370_session_1250_opsrun_mission_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="RigbyWorkItem",
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
                    "source_event_ref",
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "Canonical '<source>:<source_id>' handle for "
                            "the originating event."
                        ),
                        max_length=200,
                    ),
                ),
                (
                    "decision",
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "One of: monitor / notify (v0 actionable). "
                            "Closed vocab matches DECISION_VOCAB."
                        ),
                        max_length=30,
                    ),
                ),
                (
                    "severity",
                    models.CharField(
                        help_text=(
                            "PR 2 closed vocab: debug / info / notice / "
                            "warn / error / critical / unknown."
                        ),
                        max_length=20,
                    ),
                ),
                (
                    "mission_impact",
                    models.CharField(
                        help_text=(
                            "PR 4 closed vocab: unknown / low / medium / high."
                        ),
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        db_index=True,
                        default=1,
                        help_text=(
                            "Computed from mission_impact "
                            "(unknown=1, low=3, medium=5, high=8). "
                            "Higher = sooner Rigby should look at it."
                        ),
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("summary", models.TextField(blank=True, default="")),
                (
                    "recommended_next_action",
                    models.TextField(blank=True, default=""),
                ),
                (
                    "evidence",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            "Evidence dict: at minimum "
                            "{event_ref, rules_fired, decision_reason}. "
                            "May include adapter-specific payload "
                            "snippets in future PRs."
                        ),
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("acknowledged", "Acknowledged"),
                            ("resolved", "Resolved"),
                            ("ignored", "Ignored"),
                        ],
                        db_index=True,
                        default="open",
                        max_length=20,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "resolved_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "source_mission_run",
                    models.ForeignKey(
                        help_text=(
                            "The MissionRun (OpsRun with domain='mission') "
                            "that produced this work item."
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rigby_work_items",
                        to="core.opsrun",
                    ),
                ),
            ],
            options={
                "ordering": ["-priority", "-created_at"],
                "unique_together": {("source_event_ref", "decision")},
            },
        ),
        migrations.AddIndex(
            model_name="rigbyworkitem",
            index=models.Index(
                fields=["status", "-priority", "-created_at"],
                name="core_rigbyw_status_p_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="rigbyworkitem",
            index=models.Index(
                fields=["decision", "-created_at"],
                name="core_rigbyw_decisio_idx",
            ),
        ),
    ]
