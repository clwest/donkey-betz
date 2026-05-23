# Session 1132 (B-scaffold) — Warn-only audit table for PA-chat auth posture.
#
# Rigby's lock (conversation pa-d19c1674b936): no new bearer-token
# scheme. The existing fleet HMAC signature path (Session 1129 Move 1)
# is the canonical mechanism for binding `app_slug` to a request. We
# record per-call audit rows so we can measure how many fleet apps
# are still calling /api/pa/chat/ with bearer-only auth before flipping
# enforcement.

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0348_curated_signal_snapshot"),
    ]

    operations = [
        migrations.CreateModel(
            name="FleetPAChatAuditRow",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                # UnifiedBaseModel-inherited fields:
                ("metadata", models.JSONField(default=dict, blank=True)),
                ("version", models.PositiveIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "auth_mode",
                    models.CharField(
                        max_length=24,
                        choices=[
                            ("fleet_signature", "Fleet HMAC signature"),
                            ("bearer_only", "Bearer token only (no fleet signature)"),
                            ("session_user", "Django session user"),
                            ("api_user_token", "DRF token (user-scoped)"),
                            ("anonymous", "Anonymous / unauthenticated"),
                        ],
                        db_index=True,
                    ),
                ),
                ("has_fleet_identity", models.BooleanField(default=False, db_index=True)),
                (
                    "verified_app_slug",
                    models.CharField(
                        max_length=100, blank=True, default="", db_index=True
                    ),
                ),
                (
                    "claimed_app_slug",
                    models.CharField(max_length=100, blank=True, default=""),
                ),
                ("match", models.BooleanField(null=True, blank=True, db_index=True)),
                ("request_path", models.CharField(max_length=200, blank=True, default="")),
                ("remote_addr", models.GenericIPAddressField(null=True, blank=True)),
                ("user_agent", models.CharField(max_length=500, blank=True, default="")),
                ("request_id", models.CharField(max_length=64, blank=True, default="")),
            ],
            options={
                "verbose_name": "Fleet PA-Chat Audit Row",
                "verbose_name_plural": "Fleet PA-Chat Audit Rows",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="fleetpachatauditrow",
            index=models.Index(
                fields=["auth_mode", "-created_at"],
                name="pa_chat_audit_mode_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="fleetpachatauditrow",
            index=models.Index(
                fields=["match", "-created_at"],
                name="pa_chat_audit_match_idx",
            ),
        ),
    ]
