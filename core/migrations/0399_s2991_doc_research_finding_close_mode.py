# S2991 v2 item #1 — additive close_mode column on DocResearchFinding.
# Rigby SIGN caught axis confusion in Claude's original 6-value status
# replacement proposal; joint agreement (Chris ratified) landed on an
# additive orthogonal column: status stays lifecycle, close_mode carries
# closure mechanism. Freshness deferred until 2nd trigger.
#
# Backfills the 3 S2990 canonical rows:
#   4b92f6f0-b84b-47d1-976a-30246f3dbd3d — drf-spectacular PRs #3642+#3643 → fixed_via_pr
#   023d3301-df86-4879-893f-8fd5b0c460c8 — undeclared endpoints report PR #3644 → evidence_delivered
#   3a89fddc-7b62-4093-afaa-1a9896c540f8 — permission_classes report PR #3645 → evidence_delivered

from django.db import migrations, models


S2990_BACKFILL = [
    ("4b92f6f0-b84b-47d1-976a-30246f3dbd3d", "fixed_via_pr"),
    ("023d3301-df86-4879-893f-8fd5b0c460c8", "evidence_delivered"),
    ("3a89fddc-7b62-4093-afaa-1a9896c540f8", "evidence_delivered"),
]


def backfill_s2990_rows(apps, schema_editor):
    Finding = apps.get_model("core", "DocResearchFinding")
    for finding_id, close_mode in S2990_BACKFILL:
        Finding.objects.filter(id=finding_id).update(close_mode=close_mode)


def unbackfill_s2990_rows(apps, schema_editor):
    Finding = apps.get_model("core", "DocResearchFinding")
    ids = [row[0] for row in S2990_BACKFILL]
    Finding.objects.filter(id__in=ids).update(close_mode=None)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0398_s2989_doc_research_finding"),
    ]

    operations = [
        migrations.AddField(
            model_name="docresearchfinding",
            name="close_mode",
            field=models.CharField(
                blank=True,
                choices=[
                    ("fixed_via_pr", "Fixed via PR"),
                    ("evidence_delivered", "Evidence delivered"),
                    ("deferred_to_arc", "Deferred to arc"),
                    ("informational", "Informational"),
                ],
                default=None,
                max_length=32,
                null=True,
            ),
        ),
        migrations.RunPython(backfill_s2990_rows, unbackfill_s2990_rows),
    ]
