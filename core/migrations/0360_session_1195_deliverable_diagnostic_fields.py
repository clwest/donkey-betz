# Session 1195 — Plan C Phase 1 (Initiatives-First Backbone).
# Adds the annotation layer for the no-orphan-deliverable contract:
# diagnostic_status + diagnostic_code + diagnostic_payload + the two
# TTL timestamps. Composite index drives the daily sweep query. The
# canonical `status` field stays the lifecycle owner — the sweep flips
# status='archived' and records the reason inside diagnostic_payload.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0359_session_1180_followup_subscription_nullable_expires"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverable",
            name="diagnostic_status",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="NULL = ok; 'diagnostic' = flagged for Initiative-alignment violation",
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="deliverable",
            name="diagnostic_code",
            field=models.CharField(
                blank=True,
                help_text="e.g. 'missing_initiative_id', 'workspace_mismatch'",
                max_length=64,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="deliverable",
            name="diagnostic_payload",
            field=models.JSONField(
                blank=True,
                help_text="Structured details: expected/actual workspace, agent, tool, trace, caller, archive reason",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="deliverable",
            name="diagnostic_marked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="deliverable",
            name="diagnostic_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="deliverable",
            index=models.Index(
                fields=["diagnostic_status", "diagnostic_expires_at"],
                name="deliv_diag_sweep_idx",
            ),
        ),
    ]
