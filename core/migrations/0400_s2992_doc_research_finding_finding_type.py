# S2992 v2 item #2 — schema-only finding_type column.
# Additive CharField with default 'unknown'; auto-populates 897 open + 3
# fixed rows without a data migration. Classification of existing rows
# is deferred to PR (b): `python manage.py index_doc_research_findings
# --reclassify-existing --apply` after Rigby A2 SIGN verifies the
# dry-run distribution.
#
# Rigby T1 SIGN framing (real tool_runs on 10-row sample) validated:
# - finding_type does NOT collide with any existing field
# - decision_evidence precedence over executable is right on ambiguous rows
# - executable signal set widened beyond .py:line per corpus reality

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0399_s2991_doc_research_finding_close_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="docresearchfinding",
            name="finding_type",
            field=models.CharField(
                choices=[
                    ("decision_evidence", "Decision Evidence"),
                    ("executable", "Executable"),
                    ("unknown", "Unknown"),
                ],
                db_index=True,
                default="unknown",
                max_length=32,
            ),
        ),
    ]
