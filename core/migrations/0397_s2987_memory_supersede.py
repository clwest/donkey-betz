# S2987 (spec ba968ac1 PR2) — supersede-not-delete semantics for UserMemoryContext.
#
# Isolated migration: intentionally scoped to the three new UserMemoryContext
# fields + one composite index. The auto-generated diff picked up unrelated
# pre-existing model drift (Narrative, HAIDispatchLog, FleetPAChatAuditRow,
# CuratedSignalEntry, RigbyWorkItem index renames) — those belong to their
# own arcs and must not ship inside a memory-hygiene migration.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0396_s2965_golden_eval_evidence_source_ledger_health"),
    ]

    operations = [
        migrations.AddField(
            model_name="usermemorycontext",
            name="is_active",
            field=models.BooleanField(
                db_index=True,
                default=True,
                help_text="False means superseded/inactive; excluded from prompt injection + cap counts.",
            ),
        ),
        migrations.AddField(
            model_name="usermemorycontext",
            name="superseded_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When this row was marked inactive.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="usermemorycontext",
            name="superseded_by",
            field=models.ForeignKey(
                blank=True,
                help_text="If this row was replaced, points at the replacement row.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="supersedes",
                to="core.usermemorycontext",
            ),
        ),
        migrations.AddIndex(
            model_name="usermemorycontext",
            index=models.Index(
                fields=["user", "is_active", "-created_at"],
                name="core_userme_user_ac_idx",
            ),
        ),
    ]
