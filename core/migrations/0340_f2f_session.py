"""Create the F2FSession table for Session 1118 F2F.2.

Hand-authored narrow migration — ``makemigrations`` autodetector wants
to bundle in unrelated Narrative model + agentexecution drift left
over from Session 1116/1117. We only own the F2FSession ``CreateModel``
here; the Narrative work belongs to whoever is shepherding it.

Schema mirrors ``core/models_f2f.py`` exactly. See model docstring for
design context (Rigby memory_id 5 + F2F.2 design pass).
"""
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0339_skin_body_columns_comprehensive"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="F2FSession",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="F2F session UUID. Also keys the Redis session_key entry.",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "provider_name",
                    models.CharField(
                        db_index=True,
                        help_text="Realtime avatar provider — 'heygen' or 'mock'.",
                        max_length=32,
                    ),
                ),
                (
                    "provider_session_id",
                    models.CharField(
                        db_index=True,
                        help_text="Provider's own session id (returned by create_session).",
                        max_length=255,
                    ),
                ),
                (
                    "mock_mode",
                    models.BooleanField(
                        db_index=True,
                        default=False,
                        help_text=(
                            "True when F2F_PROVIDER_MOCK is on. Mock sessions log usage "
                            "but do not move cost caps."
                        ),
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("ended", "Ended (normal)"),
                            ("cap_exceeded_daily", "Cap exceeded — daily"),
                            ("cap_exceeded_monthly", "Cap exceeded — monthly"),
                            (
                                "cap_exceeded_session_spend",
                                "Cap exceeded — session spend",
                            ),
                            (
                                "cap_exceeded_session_duration",
                                "Cap exceeded — session duration",
                            ),
                            ("provider_error", "Provider error"),
                            ("broker_error", "Broker error"),
                        ],
                        db_index=True,
                        default="active",
                        max_length=40,
                    ),
                ),
                (
                    "ended_reason",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Human-readable reason for the terminal status.",
                    ),
                ),
                (
                    "error_message",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Provider or broker error detail. Never operator-visible.",
                    ),
                ),
                (
                    "started_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        help_text="Session creation timestamp. Drives the duration cap.",
                    ),
                ),
                (
                    "last_activity_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Updated on every speak() / poll_session() call.",
                    ),
                ),
                (
                    "ended_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Set when status transitions to a terminal value.",
                        null=True,
                    ),
                ),
                (
                    "total_chars_spoken",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Sum of characters successfully sent via speak().",
                    ),
                ),
                (
                    "total_cost_cents",
                    models.PositiveIntegerField(
                        default=0,
                        help_text=(
                            "Realized spend across all cost buckets "
                            "(stt+llm+tts+avatar) in whole cents. Source of truth "
                            "for reconciliation."
                        ),
                    ),
                ),
                (
                    "speak_call_count",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Number of speak() invocations that returned accepted=True.",
                    ),
                ),
                (
                    "avatar_id",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Provider's avatar identifier — HeyGen avatar persona id, etc.",
                        max_length=128,
                    ),
                ),
                (
                    "voice_id",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Provider's voice identifier (when TTS is provider-side).",
                        max_length=128,
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            "Free-form provider extras (HeyGen region, Cartesia voice "
                            "params, request_id seeds for future idempotency, etc.). "
                            "Never PII; never the session_key."
                        ),
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User who opened this session.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="f2f_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        help_text="Workspace this session bills against.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="f2f_sessions",
                        to="core.projectworkspace",
                    ),
                ),
            ],
            options={
                "ordering": ("-started_at",),
                "indexes": [
                    models.Index(
                        fields=("workspace", "started_at"),
                        name="f2f_ws_started_idx",
                    ),
                    models.Index(
                        fields=("workspace", "status"),
                        name="f2f_ws_status_idx",
                    ),
                    models.Index(
                        fields=("user", "started_at"),
                        name="f2f_user_started_idx",
                    ),
                ],
            },
        ),
    ]
