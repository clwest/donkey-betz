# Session 1129 — Move 3 Round 1: Fleet event (MLC scope).
# Hand-edited from `makemigrations core` output to drop unrelated pending
# drift (agentexecution AlterField, Narrative* model creates). Only the
# FleetEvent CreateModel from `core/models/fleet.py` lands here.

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0344_fleetartifact_ttl"),
    ]

    operations = [
        migrations.CreateModel(
            name="FleetEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Universal unique identifier",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When this record was created"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, help_text="When this record was last updated"
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Flexible metadata storage for extensibility",
                    ),
                ),
                (
                    "version",
                    models.PositiveIntegerField(
                        default=1, help_text="Version number for optimistic locking"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True, help_text="Whether this record is active/enabled"
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        db_index=True,
                        help_text="Dotted event name (e.g. 'artifact.created', 'artifact.expired')",
                        max_length=64,
                    ),
                ),
                (
                    "app_slug",
                    models.CharField(
                        db_index=True,
                        help_text="The fleet app this event belongs to (matches FleetServiceIdentity.app_slug)",
                        max_length=100,
                    ),
                ),
                (
                    "payload",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            "Event body — caller-defined per event_type. Should include "
                            "enough context for subscribers to act without a separate fetch."
                        ),
                    ),
                ),
                (
                    "source_artifact",
                    models.ForeignKey(
                        blank=True,
                        help_text="Optional FK to the source artifact (for lifecycle events).",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="events",
                        to="core.fleetartifact",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fleet Event",
                "verbose_name_plural": "Fleet Events",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["app_slug", "-created_at"],
                        name="core_fleete_app_recent_idx",
                    ),
                    models.Index(
                        fields=["event_type", "-created_at"],
                        name="core_fleete_type_recent_idx",
                    ),
                ],
            },
        ),
    ]
