# S2992 v2 item #2 — PR (b): backfill finding_type on existing rows.
#
# Migration 0400 added the finding_type column with default 'unknown'.
# Rigby A2 SIGN on PR #3650 verified dry-run distribution (139
# decision_evidence / 138 executable / 623 unknown = 15.4/15.3/69.2%
# over 900 rows, 277 flips). This migration persists that classification
# by re-running the same _classify_finding_type helper over every row.
#
# Reverse migration is a no-op safety: rolling back would need to
# restore per-row prior finding_type, which was uniformly 'unknown' at
# migration 0400 time. We take the pragmatic route and reset all rows
# to 'unknown' on reverse.
#
# Idempotent: safe to re-run (though only relevant during the initial
# S2992 backfill window). For future reclassifications after signal
# tweaks, use `python manage.py index_doc_research_findings
# --reclassify-existing --apply` instead of writing a new migration.

from django.db import migrations

from core.management.commands.index_doc_research_findings import (
    _classify_finding_type,
)


def backfill_finding_type(apps, schema_editor):
    Finding = apps.get_model("core", "DocResearchFinding")
    qs = Finding.objects.all().only(
        "id", "text", "source_heading", "finding_type"
    )
    flipped = 0
    for row in qs.iterator(chunk_size=500):
        new_type = _classify_finding_type(row.text, row.source_heading)
        if new_type != row.finding_type:
            Finding.objects.filter(id=row.id).update(finding_type=new_type)
            flipped += 1
    # No stdout in migrations by convention; the classifier is
    # deterministic + regex-only so re-running is safe.


def reset_finding_type_to_unknown(apps, schema_editor):
    Finding = apps.get_model("core", "DocResearchFinding")
    Finding.objects.exclude(finding_type="unknown").update(
        finding_type="unknown"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0400_s2992_doc_research_finding_finding_type"),
    ]

    operations = [
        migrations.RunPython(backfill_finding_type, reset_finding_type_to_unknown),
    ]
