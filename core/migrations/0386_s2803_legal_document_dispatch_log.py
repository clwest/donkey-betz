# Generated for S2803 Phase 3.0 — Colorado Family Law drafting compliance audit.
# Scope-only migration: creates LegalDocumentDispatchLog and its indexes/FKs.
# Unrelated pending schema drift (Narrative*, HAIDispatchLog renames, RigbyWorkItem,
# FleetPAChatAuditRow field docs, etc.) intentionally NOT included — those belong
# to their own arcs' PRs.

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0385_s2794_tenant_boundary_health_report"),
    ]

    operations = [
        migrations.CreateModel(
            name="LegalDocumentDispatchLog",
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
                ("task_id", models.CharField(db_index=True, max_length=64)),
                (
                    "task_description",
                    models.TextField(help_text="The user's original drafting request"),
                ),
                ("dispatched_at", models.DateTimeField(auto_now_add=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=500)),
                (
                    "client_session_pin",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        help_text="PA conversation pin if dispatch came via _handle_legal_agent; empty for UI dispatches",
                        max_length=64,
                    ),
                ),
                (
                    "disclaimer_acknowledged",
                    models.BooleanField(
                        default=False,
                        help_text="Whether the caller explicitly acknowledged the not-legal-advice disclaimer",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("dispatched", "Dispatched"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="dispatched",
                        max_length=16,
                    ),
                ),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True)),
                (
                    "resulting_document",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="dispatch_log",
                        to="core.legaldocument",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="legal_dispatch_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Legal Document Dispatch Log",
                "verbose_name_plural": "Legal Document Dispatch Logs",
                "ordering": ["-dispatched_at"],
            },
        ),
        migrations.AddIndex(
            model_name="legaldocumentdispatchlog",
            index=models.Index(
                fields=["user", "-dispatched_at"], name="core_legald_user_id_bcdcc8_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="legaldocumentdispatchlog",
            index=models.Index(
                fields=["task_id"], name="core_legald_task_id_bdea77_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="legaldocumentdispatchlog",
            index=models.Index(fields=["status"], name="core_legald_status_93d256_idx"),
        ),
    ]
