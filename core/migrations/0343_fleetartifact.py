# Session 1129 — Move 2 Round 1: Fleet artifact (MLC scope)
# Hand-edited from `makemigrations core` output to drop unrelated pending
# model drift (agentexecution AlterField, Narrative* models). Only the
# FleetArtifact CreateModel from `core/models/fleet.py` should land here.

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0342_fleetserviceidentity_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="FleetArtifact",
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
                    "artifact_type",
                    models.CharField(
                        db_index=True,
                        help_text="Caller-chosen type tag (e.g. 'contract_draft', 'lead_list')",
                        max_length=50,
                    ),
                ),
                (
                    "payload",
                    models.JSONField(
                        help_text="The artifact's contents — caller-controlled JSON"
                    ),
                ),
                (
                    "caller_metadata",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            "Optional caller-supplied tags. Separate from `metadata` "
                            "which is system-flexible storage on UnifiedBaseModel."
                        ),
                    ),
                ),
                (
                    "sha256",
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "Hex SHA-256 of canonical JSON payload. Computed "
                            "server-side; clients can verify after a pull."
                        ),
                        max_length=64,
                    ),
                ),
                (
                    "size_bytes",
                    models.PositiveIntegerField(
                        default=0,
                        help_text=(
                            "Bytes of canonical JSON payload — used for "
                            "max_payload_kb capability gating."
                        ),
                    ),
                ),
                (
                    "created_by_key_id",
                    models.CharField(
                        help_text=(
                            "The specific signing key used at create time (may "
                            "differ from the identity's current active key "
                            "after a rotation)"
                        ),
                        max_length=120,
                    ),
                ),
                (
                    "request_id",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text=(
                            "X-Request-Id from the signing headers; joins to "
                            "FleetAuthAuditLog for full trace."
                        ),
                        max_length=64,
                    ),
                ),
                (
                    "created_by_identity",
                    models.ForeignKey(
                        help_text="The fleet service that pushed this artifact",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="artifacts",
                        to="core.fleetserviceidentity",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fleet Artifact",
                "verbose_name_plural": "Fleet Artifacts",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["created_by_identity", "-created_at"],
                        name="core_fleeta_created_b6b731_idx",
                    ),
                    models.Index(
                        fields=["artifact_type", "-created_at"],
                        name="core_fleeta_artifac_4f3ddb_idx",
                    ),
                ],
            },
        ),
    ]
