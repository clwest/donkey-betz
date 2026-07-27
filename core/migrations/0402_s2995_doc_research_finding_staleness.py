# Generated for S2995 v2 item #4 — staleness detector at ingest.
#
# Schema-only. New rows default to `fresh` (no signal, no claim). The
# existing 900 rows also default to `fresh` via this default; the PR (b)
# backfill migration (0403) re-runs `_check_staleness_at_head` over
# every existing row and flips suspected ones.
#
# Kept surgical (matches the S2992 pattern): this migration only touches
# DocResearchFinding.staleness. Django's autodetector swept up unrelated
# model drift (Narrative*, HAI dispatch log help_text updates, index
# renames) into the initial pass; those are pre-existing state and
# should get their own migration if they matter.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0401_s2992_finding_type_backfill"),
    ]

    operations = [
        migrations.AddField(
            model_name="docresearchfinding",
            name="staleness",
            field=models.CharField(
                choices=[("fresh", "Fresh"), ("suspected", "Suspected stale")],
                db_index=True,
                default="fresh",
                max_length=16,
            ),
        ),
    ]
