"""
I-0302 Phase 3 Sub-phase A1 — schema migration: flip Initiative.owner to
NOT NULL with on_delete=PROTECT.

Depends on 0381 backfill; must not run before every null-owner row has
been resolved (0381 gates on that internally).

Rationale for on_delete=PROTECT (per Rigby SIGN Q2 2026-07-10):
- SET_NULL is no longer valid once the column is NOT NULL.
- CASCADE would drop Initiative rows if the owning user is ever deleted —
  unacceptable data loss for a per-user model with ratified predicates.
- PROTECT preserves rows and forces an explicit decision if user deletion
  is ever attempted. Safest replacement for the single-user pre-prod era;
  survives to Phase 0 multi-tenant without semantic change.

Field-level ``help_text`` records the Session 996 origin + I-0302 Phase 3
Sub-phase A1 enforcement flip, so future readers see the provenance
without opening the ratification record.
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0381_i0302_backfill_initiative_owners'),
    ]

    operations = [
        migrations.AlterField(
            model_name='initiative',
            name='owner',
            field=models.ForeignKey(
                to='core.UnifiedUser',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='owned_initiatives',
                help_text=(
                    'Session 996: Human owner responsible for this initiative. '
                    'NOT NULL enforced via I-0302 Phase 3 Sub-phase A1 '
                    '(2026-07-10). PROTECT preserves initiatives on user '
                    'deletion attempts (chose over CASCADE to prevent data loss).'
                ),
            ),
        ),
    ]
