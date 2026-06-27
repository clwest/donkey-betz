"""Session 1243 — rebuild PaMessageFeedback after Session 1085 stillborn.

PR #2679 tombstoned the shadowed `core/models.py` monolith. PaMessageFeedback
was discovered to be a stillborn endpoint: `/api/pa/feedback/` URL + view live
since Session 1085, but the model class lived only in the shadowed file
(unregistered with Django) and no migration was ever created. Every POST
500'd with `relation "core_pamessagefeedback" does not exist`.

This migration creates the missing table so the endpoint works. The model
itself was added under `core/models/conversations/models.py` in the same PR.

Scope-limited migration: only PaMessageFeedback. Drift from other
unmigrated models (Narrative*, FleetPaChatAuditRow) is out of scope and
should be addressed by their owners in dedicated migrations.
"""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0365_session_1226_agent_name_canonicalization"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PaMessageFeedback",
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
                    "conversation_id_str",
                    models.CharField(
                        db_index=True,
                        help_text="Conversation ID string (e.g., 'pa-xxx') — string, not FK.",
                        max_length=255,
                    ),
                ),
                (
                    "message_index",
                    models.IntegerField(
                        default=0,
                        help_text="Index of the assistant message within the conversation.",
                    ),
                ),
                (
                    "rating",
                    models.SmallIntegerField(
                        help_text="+1 (thumbs up) or -1 (thumbs down)"
                    ),
                ),
                (
                    "note",
                    models.TextField(blank=True, help_text="Optional feedback text."),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pa_message_feedback",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "core_pamessagefeedback",
                "indexes": [
                    models.Index(
                        fields=["user", "-created_at"],
                        name="core_pamess_user_id_69a7b6_idx",
                    ),
                    models.Index(
                        fields=["rating"],
                        name="core_pamess_rating_b1474e_idx",
                    ),
                ],
                "unique_together": {
                    ("user", "conversation_id_str", "message_index")
                },
            },
        ),
    ]
