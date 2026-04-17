# Session 1098: Per-LLM-call telemetry. See core/models_llm_telemetry.py
# and conversation pa-3c7ddc058db1 for context (Rigby's boardroom-
# dispatch-hang remediation, PR #1).

import uuid

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0333_add_deliverable_publish_intent"),
    ]

    operations = [
        migrations.CreateModel(
            name="LLMCallEvent",
            fields=[
                (
                    "call_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "execution_id",
                    models.UUIDField(
                        blank=True,
                        db_index=True,
                        help_text=(
                            "UUID of owning AgentExecution "
                            "(core_agentexecution). NULL for detached "
                            "calls (tests, scripts, PA flows with no "
                            "execution record)."
                        ),
                        null=True,
                    ),
                ),
                (
                    "agent_name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text=(
                            "Agent that initiated this LLM call "
                            "(dashboards filter here)."
                        ),
                        max_length=120,
                    ),
                ),
                (
                    "provider",
                    models.CharField(blank=True, default="", max_length=50),
                ),
                (
                    "model",
                    models.CharField(blank=True, default="", max_length=120),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("STARTED", "Started"),
                            ("SUCCESS", "Success"),
                            ("FAILED", "Failed"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        db_index=True,
                        default="STARTED",
                        max_length=20,
                    ),
                ),
                (
                    "started_at",
                    models.DateTimeField(db_index=True, default=timezone.now),
                ),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("duration_ms", models.IntegerField(blank=True, null=True)),
                ("tokens_in", models.IntegerField(blank=True, null=True)),
                ("tokens_out", models.IntegerField(blank=True, null=True)),
                ("retry_count", models.IntegerField(default=0)),
                (
                    "error_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "None"),
                            ("timeout", "Timeout"),
                            ("rate_limit", "Rate Limit"),
                            ("auth", "Auth Error"),
                            ("api_error", "API Error"),
                            ("client_error", "Client Error"),
                            ("cancelled", "Cancelled"),
                            ("unknown", "Unknown"),
                        ],
                        default="",
                        max_length=50,
                    ),
                ),
                ("error_message", models.TextField(blank=True, default="")),
                (
                    "cancelled",
                    models.BooleanField(db_index=True, default=False),
                ),
                ("metadata", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["-started_at"],
            },
        ),
        migrations.AddIndex(
            model_name="llmcallevent",
            index=models.Index(
                fields=["execution_id", "-started_at"],
                name="llm_call_exec_time",
            ),
        ),
        migrations.AddIndex(
            model_name="llmcallevent",
            index=models.Index(
                fields=["provider", "-started_at"],
                name="llm_call_provider_time",
            ),
        ),
        migrations.AddIndex(
            model_name="llmcallevent",
            index=models.Index(
                fields=["-started_at", "status"],
                name="llm_call_time_status",
            ),
        ),
    ]
