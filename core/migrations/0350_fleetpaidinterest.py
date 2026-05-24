# Session 1138 — Decision 13 implementation: paid-interest signal table.
# Hand-edited from `makemigrations core` output to drop unrelated pending
# drift (agentexecution AlterField, FleetPAChatAuditRow AlterFields,
# Narrative* model creates). Only the FleetPaidInterest CreateModel from
# `core/models/fleet.py` should land here.

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0349_fleet_pa_chat_audit_row"),
    ]

    operations = [
        migrations.CreateModel(
            name="FleetPaidInterest",
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
                        auto_now_add=True,
                        help_text="When this record was created",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When this record was last updated",
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
                        default=1,
                        help_text="Version number for optimistic locking",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this record is active/enabled",
                    ),
                ),
                (
                    "app_slug",
                    models.CharField(
                        db_index=True,
                        help_text=(
                            "The fleet app this paid-interest signal belongs "
                            "to (matches FleetServiceIdentity.app_slug)"
                        ),
                        max_length=100,
                    ),
                ),
                (
                    "email",
                    models.CharField(
                        help_text="Submitter's email, lowercased pre-save for dedup",
                        max_length=320,
                    ),
                ),
                (
                    "use_case",
                    models.CharField(
                        help_text="One-line description of intended use (≤140 chars per spec)",
                        max_length=140,
                    ),
                ),
                (
                    "willing_pay",
                    models.PositiveIntegerField(
                        blank=True,
                        null=True,
                        help_text=(
                            "Optional monthly $ the user said they'd pay. "
                            "NULL when the form field was left blank. Triggers "
                            "Decision 13 condition 2 when >= the app's Pro "
                            "tier price."
                        ),
                    ),
                ),
                (
                    "workspace_size",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("solo", "Solo"),
                            ("2-5", "2-5 people"),
                            ("6-20", "6-20 people"),
                            ("20+", "20+ people"),
                        ],
                        default="",
                        help_text="Optional sizing signal: solo / 2-5 / 6-20 / 20+",
                        max_length=8,
                    ),
                ),
                (
                    "user_id_claim",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text=(
                            "If the submitter was signed in on the fleet app "
                            "side, their user id from that app's user model. "
                            "Empty for anonymous submissions."
                        ),
                        max_length=120,
                    ),
                ),
                (
                    "notified_at",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        null=True,
                        help_text=(
                            "Set when a launch-notification email is sent. "
                            "NULL until then. Operator-driven; no automated "
                            "emails ship in the MLC scope."
                        ),
                    ),
                ),
                (
                    "submitted_by_key_id",
                    models.CharField(
                        help_text="The specific signing key used at submission time",
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
                            "FleetAuthAuditLog."
                        ),
                        max_length=64,
                    ),
                ),
                (
                    "submitted_by_identity",
                    models.ForeignKey(
                        help_text=(
                            "The fleet service identity that signed this "
                            "submission"
                        ),
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="paid_interest_submissions",
                        to="core.fleetserviceidentity",
                    ),
                ),
            ],
            options={
                "db_table": "core_fleetpaidinterest",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["app_slug", "-created_at"],
                        name="fpi_app_recent_idx",
                    ),
                    models.Index(
                        fields=["app_slug", "email"],
                        name="fpi_app_email_idx",
                    ),
                    models.Index(
                        fields=["app_slug", "willing_pay"],
                        name="fpi_app_pay_idx",
                    ),
                ],
            },
        ),
    ]
