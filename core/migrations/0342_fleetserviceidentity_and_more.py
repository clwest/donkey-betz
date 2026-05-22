# Session 1129 — Move 1: Fleet service identity + signed-request audit
# Hand-edited from `makemigrations core` output to drop unrelated pending
# model drift (agentexecution AlterField, Narrative* models) that the
# autogen bundled in. Only the four fleet models from
# `core/models/fleet.py` should land here.

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0341_chat_conversation_columns_idempotent"),
    ]

    operations = [
        migrations.CreateModel(
            name="FleetServiceIdentity",
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
                    "app_slug",
                    models.CharField(
                        help_text="Fleet app identifier; matches fleet_agent_routing.json keys",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="Human-readable label", max_length=200),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("disabled", "Disabled"),
                            ("rotating", "Rotating"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                (
                    "capabilities",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Per-spec capability dict (routing/artifacts/events)",
                    ),
                ),
                (
                    "allowed_routes",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Explicit route allowlist; empty list = no fleet routes allowed",
                    ),
                ),
                (
                    "last_used_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Updated on any successful verify",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "Fleet Service Identity",
                "verbose_name_plural": "Fleet Service Identities",
                "ordering": ["app_slug"],
            },
        ),
        migrations.CreateModel(
            name="FleetAuthAuditLog",
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
                ("occurred_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "request_id",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=64
                    ),
                ),
                ("method", models.CharField(max_length=10)),
                ("path", models.CharField(max_length=512)),
                ("query", models.CharField(blank=True, default="", max_length=2048)),
                ("status_code", models.PositiveSmallIntegerField()),
                (
                    "result",
                    models.CharField(
                        choices=[("allow", "Allow"), ("deny", "Deny")], max_length=8
                    ),
                ),
                (
                    "deny_code",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="One of the canonical error codes; empty on allow",
                        max_length=64,
                    ),
                ),
                (
                    "key_id",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=120
                    ),
                ),
                (
                    "app_slug_claimed",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=100
                    ),
                ),
                (
                    "app_slug_resolved",
                    models.CharField(
                        blank=True, db_index=True, default="", max_length=100
                    ),
                ),
                ("timestamp_claimed", models.BigIntegerField(blank=True, null=True)),
                ("timestamp_delta_seconds", models.IntegerField(blank=True, null=True)),
                ("nonce", models.CharField(blank=True, default="", max_length=64)),
                ("replay_detected", models.BooleanField(default=False)),
                (
                    "body_sha256",
                    models.CharField(blank=True, default="", max_length=64),
                ),
                ("sig_present", models.BooleanField(default=False)),
                ("ip", models.GenericIPAddressField(blank=True, null=True)),
                (
                    "user_agent",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("latency_ms", models.PositiveIntegerField(default=0)),
                ("notes", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "verbose_name": "Fleet Auth Audit Log",
                "verbose_name_plural": "Fleet Auth Audit Logs",
                "ordering": ["-occurred_at"],
                "indexes": [
                    models.Index(
                        fields=["-occurred_at"], name="core_fleeta_occurre_e6f0e2_idx"
                    ),
                    models.Index(
                        fields=["result", "deny_code"],
                        name="core_fleeta_result_e76c03_idx",
                    ),
                    models.Index(
                        fields=["app_slug_resolved", "-occurred_at"],
                        name="core_fleeta_app_slu_f26ecc_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="FleetServiceKey",
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
                    "key_id",
                    models.CharField(
                        help_text="Public key identifier (e.g. fs_contractconcierge_k1)",
                        max_length=120,
                        unique=True,
                    ),
                ),
                (
                    "secret_hash",
                    models.CharField(
                        help_text="SHA256(secret); raw secret never persisted",
                        max_length=64,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("draining", "Draining"),
                            ("disabled", "Disabled"),
                        ],
                        default="active",
                        max_length=16,
                    ),
                ),
                ("not_before", models.DateTimeField(blank=True, null=True)),
                ("not_after", models.DateTimeField(blank=True, null=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True)),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="keys",
                        to="core.fleetserviceidentity",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fleet Service Key",
                "verbose_name_plural": "Fleet Service Keys",
                "ordering": ["service__app_slug", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="FleetServiceRotation",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("planned", "Planned"),
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("aborted", "Aborted"),
                        ],
                        default="planned",
                        max_length=16,
                    ),
                ),
                ("starts_at", models.DateTimeField(blank=True, null=True)),
                ("ends_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, default="")),
                (
                    "new_key",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="rotations_as_new",
                        to="core.fleetservicekey",
                    ),
                ),
                (
                    "old_key",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="rotations_as_old",
                        to="core.fleetservicekey",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rotations",
                        to="core.fleetserviceidentity",
                    ),
                ),
            ],
            options={
                "verbose_name": "Fleet Service Rotation",
                "verbose_name_plural": "Fleet Service Rotations",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="fleetservicekey",
            index=models.Index(fields=["status"], name="core_fleets_status_2eec8a_idx"),
        ),
        migrations.AddIndex(
            model_name="fleetservicekey",
            index=models.Index(
                fields=["service", "status"], name="core_fleets_service_c5b130_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="fleetservicerotation",
            index=models.Index(
                fields=["service", "status"], name="core_fleets_service_ca6518_idx"
            ),
        ),
    ]
