"""
Session 2730 F-PS-2a + F-PS-2b (Batch C tool 2 of the Rigby Tool
Validation Engineering Campaign): add silent-truncation signals to
`ToolCallRecord`.

Previously:
- `result_summary` was silently truncated at 4096 chars with no
  boolean signal — analytics had to compare `result_size_bytes` to
  `len(result_summary)` to infer truncation.
- `full_result` was silently blanked when payload exceeded 64KB —
  analytics could not distinguish "oversize; blanked at cap" from
  "genuinely empty result" (both showed `full_result=''`).

Adds two booleans, both indexed since analytics filter on them:
- `summary_truncated` (F-PS-2a)
- `full_result_dropped` (F-PS-2b)

Backward-compatible: defaults False on existing rows (correct for
historical data below the caps; historical rows above the caps
receive the wrong default but no retroactive backfill runs because
the audit table is append-only and old rows are for reference only).
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0378_drop_refresh_docs_corpus_beat'),
    ]

    operations = [
        migrations.AddField(
            model_name='toolcallrecord',
            name='summary_truncated',
            field=models.BooleanField(
                default=False,
                db_index=True,
                help_text=(
                    "True when result_summary was truncated at 4096 chars "
                    "(i.e., result_size_bytes > 4096). Set by the dispatcher "
                    "at write time so analytics can filter for truncated rows "
                    "without comparing lengths."
                ),
            ),
        ),
        migrations.AddField(
            model_name='toolcallrecord',
            name='full_result_dropped',
            field=models.BooleanField(
                default=False,
                db_index=True,
                help_text=(
                    "True when full_result was blanked because the payload "
                    "exceeded the 64KB size cap. Distinguishes 'oversize; "
                    "recompute from tool call' from 'genuinely empty result' "
                    "(full_result='' AND result_size_bytes<=65536)."
                ),
            ),
        ),
    ]
