# Session 1196 — Plan C side-quest (Initiatives-First Backbone, P0).
# Adds the annotation layer for the no-target_workspace_id contract.
# Mirrors Session 1195 PR #2402 (deliverable_diagnostic_fields) so the
# same sweep + clear mental model applies. Initiative.status stays the
# lifecycle owner — the daily sweep flips status='ARCHIVED' and records
# the reason inside diagnostic_payload. 3-column composite index per
# Rigby's PR #1 refinement (vs Plan C's 2-column on Deliverable): the
# extra diagnostic_code key keeps the sweep query selective when future
# diagnostic codes are added.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0360_session_1195_deliverable_diagnostic_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="initiative",
            name="diagnostic_status",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="NULL = ok; 'diagnostic' = flagged for missing target_workspace_id",
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="initiative",
            name="diagnostic_code",
            field=models.CharField(
                blank=True,
                help_text="e.g. 'missing_target_workspace_id'",
                max_length=64,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="initiative",
            name="diagnostic_payload",
            field=models.JSONField(
                blank=True,
                help_text="Structured details: created_by, callsite_hint, status_at_mark, trace, archive reason",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="initiative",
            name="diagnostic_marked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="initiative",
            name="diagnostic_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="initiative",
            index=models.Index(
                fields=["diagnostic_status", "diagnostic_code", "diagnostic_expires_at"],
                name="init_diag_sweep_idx",
            ),
        ),
    ]
