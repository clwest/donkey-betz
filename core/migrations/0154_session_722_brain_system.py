# Generated manually for Session 722 - BRAIN System
"""
Session 722: BRAIN System - Cognitive Processing & Reasoning Models

Creates:
- CognitiveChannel: Configuration for monitored reasoning channels
- BrainPulse: Time-series records of cognitive state
- CognitiveStatus: Current cognitive status per channel (cached state)
"""

import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0153_session_707_muscular_system"),
    ]

    operations = [
        # 1. CognitiveChannel - Configuration for monitored cognitive channels
        migrations.CreateModel(
            name="CognitiveChannel",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("display_name", models.CharField(blank=True, max_length=150)),
                (
                    "channel_type",
                    models.CharField(
                        choices=[
                            ("llm", "LLM API Call"),
                            ("rag", "RAG Query"),
                            ("embedding", "Embedding Lookup"),
                            ("conversation", "PA Conversation"),
                            ("agent_think", "Agent Thinking"),
                            ("routing", "Model Routing"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("openai", "OpenAI"),
                            ("anthropic", "Anthropic"),
                            ("together_ai", "Together AI"),
                            ("ollama", "Ollama"),
                            ("deepseek", "DeepSeek"),
                            ("gemini", "Google Gemini"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "model_name",
                    models.CharField(
                        blank=True,
                        help_text="Specific model (e.g., gpt-5-mini)",
                        max_length=100,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "max_latency_ms",
                    models.IntegerField(
                        default=30000,
                        help_text="Max acceptable response time",
                    ),
                ),
                (
                    "target_success_rate",
                    models.FloatField(
                        default=95.0,
                        help_text="Target success rate %",
                    ),
                ),
                (
                    "max_concurrent",
                    models.IntegerField(
                        default=10,
                        help_text="Max concurrent requests",
                    ),
                ),
                (
                    "max_tokens_per_min",
                    models.IntegerField(
                        default=100000,
                        help_text="Token rate limit",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "is_critical",
                    models.BooleanField(
                        default=False,
                        help_text="Alert on failure",
                    ),
                ),
                (
                    "is_builtin",
                    models.BooleanField(
                        default=False,
                        help_text="System-defined channel",
                    ),
                ),
                ("total_calls", models.BigIntegerField(default=0)),
                ("total_tokens", models.BigIntegerField(default=0)),
                ("total_errors", models.BigIntegerField(default=0)),
                ("last_activity", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Cognitive Channel",
                "verbose_name_plural": "Cognitive Channels",
                "db_table": "core_cognitive_channel",
                "ordering": ["channel_type", "provider", "name"],
            },
        ),
        # 2. BrainPulse - Time-series records of cognitive state
        migrations.CreateModel(
            name="BrainPulse",
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
                    "overall_status",
                    models.CharField(
                        choices=[
                            ("focused", "Focused"),
                            ("thinking", "Thinking"),
                            ("overloaded", "Overloaded"),
                            ("foggy", "Foggy"),
                            ("resting", "Resting"),
                            ("offline", "Offline"),
                        ],
                        default="focused",
                        max_length=20,
                    ),
                ),
                (
                    "cognitive_score",
                    models.FloatField(
                        default=100.0,
                        help_text="0-100% brain health",
                    ),
                ),
                ("is_thinking", models.BooleanField(default=True)),
                ("llm_calls_24h", models.IntegerField(default=0)),
                ("llm_success_rate", models.FloatField(default=100.0)),
                ("llm_avg_latency_ms", models.FloatField(default=0)),
                ("llm_errors_24h", models.IntegerField(default=0)),
                ("llm_timeouts_24h", models.IntegerField(default=0)),
                ("tokens_input_24h", models.BigIntegerField(default=0)),
                ("tokens_output_24h", models.BigIntegerField(default=0)),
                ("tokens_total_24h", models.BigIntegerField(default=0)),
                ("active_conversations", models.IntegerField(default=0)),
                ("conversations_24h", models.IntegerField(default=0)),
                ("avg_conversation_turns", models.FloatField(default=0)),
                ("conversation_success_rate", models.FloatField(default=100.0)),
                ("rag_queries_24h", models.IntegerField(default=0)),
                ("rag_avg_latency_ms", models.FloatField(default=0)),
                ("embedding_lookups_24h", models.IntegerField(default=0)),
                (
                    "memory_hit_rate",
                    models.FloatField(
                        default=0,
                        help_text="% of queries with relevant results",
                    ),
                ),
                ("agent_thoughts_24h", models.IntegerField(default=0)),
                ("agent_tool_calls_24h", models.IntegerField(default=0)),
                ("agent_tool_success_rate", models.FloatField(default=100.0)),
                ("routing_decisions_24h", models.IntegerField(default=0)),
                ("fallback_count_24h", models.IntegerField(default=0)),
                ("primary_model_usage_pct", models.FloatField(default=100.0)),
                (
                    "provider_stats",
                    models.JSONField(
                        default=dict,
                        help_text="Per-provider call stats",
                    ),
                ),
                (
                    "model_stats",
                    models.JSONField(
                        default=dict,
                        help_text="Per-model call stats",
                    ),
                ),
                ("concurrent_tasks_peak", models.IntegerField(default=0)),
                ("queue_depth", models.IntegerField(default=0)),
                ("avg_think_time_ms", models.FloatField(default=0)),
                ("thoughts_per_minute", models.FloatField(default=0)),
                ("tokens_per_minute", models.FloatField(default=0)),
                ("channels_checked", models.IntegerField(default=0)),
                ("channels_healthy", models.IntegerField(default=0)),
                ("channels_degraded", models.IntegerField(default=0)),
                ("channels_offline", models.IntegerField(default=0)),
                ("heart_connected", models.BooleanField(default=False)),
                ("lungs_connected", models.BooleanField(default=False)),
                (
                    "cognitive_issues",
                    models.JSONField(
                        default=list,
                        help_text="Detected brain issues",
                    ),
                ),
                ("check_duration_ms", models.IntegerField(default=0)),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Brain Pulse",
                "verbose_name_plural": "Brain Pulses",
                "db_table": "core_brain_pulse",
                "ordering": ["-recorded_at"],
            },
        ),
        # 3. CognitiveStatus - Current cognitive status per channel
        migrations.CreateModel(
            name="CognitiveStatus",
            fields=[
                (
                    "channel",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="status",
                        serialize=False,
                        to="core.cognitivechannel",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("focused", "Focused"),
                            ("thinking", "Thinking"),
                            ("overloaded", "Overloaded"),
                            ("foggy", "Foggy"),
                            ("resting", "Resting"),
                            ("offline", "Offline"),
                        ],
                        default="focused",
                        max_length=20,
                    ),
                ),
                ("is_healthy", models.BooleanField(default=True)),
                ("current_latency_ms", models.FloatField(default=0)),
                ("current_concurrent", models.IntegerField(default=0)),
                ("current_queue_depth", models.IntegerField(default=0)),
                ("calls_24h", models.IntegerField(default=0)),
                ("tokens_24h", models.BigIntegerField(default=0)),
                ("errors_24h", models.IntegerField(default=0)),
                ("success_rate_24h", models.FloatField(default=100.0)),
                ("avg_latency_24h", models.FloatField(default=0)),
                ("throughput_per_min", models.FloatField(default=0)),
                ("tokens_per_min", models.FloatField(default=0)),
                ("last_call", models.DateTimeField(blank=True, null=True)),
                ("last_success", models.DateTimeField(blank=True, null=True)),
                ("last_error", models.DateTimeField(blank=True, null=True)),
                ("last_check", models.DateTimeField(auto_now=True)),
                ("warning_alert_sent", models.BooleanField(default=False)),
                ("critical_alert_sent", models.BooleanField(default=False)),
                ("last_alert_at", models.DateTimeField(blank=True, null=True)),
                ("last_error_message", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Cognitive Status",
                "verbose_name_plural": "Cognitive Statuses",
                "db_table": "core_cognitive_status",
            },
        ),
        # Add indexes for BrainPulse
        migrations.AddIndex(
            model_name="brainpulse",
            index=models.Index(
                fields=["-recorded_at"],
                name="core_brain__recorde_a8e3b3_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="brainpulse",
            index=models.Index(
                fields=["overall_status", "-recorded_at"],
                name="core_brain__overall_1d5c2c_idx",
            ),
        ),
    ]
