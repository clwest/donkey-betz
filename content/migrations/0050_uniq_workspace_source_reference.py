"""Cycle 1A KFI-1 (ADR-0110) — mirror identity uniqueness.

Adds a partial unique constraint on ``Document(source, source_reference)``
scoped to ``source='workspace'``. Enforces the mirror identity invariant
at the database layer so concurrent mirror tasks cannot create duplicate
workspace-mirrored Documents.

Pre-migration data safety (verified 2026-07-08 at HEAD 5a878768):
0 existing rows with source='workspace' → constraint is trivially
satisfiable at migrate time.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0049_add_canonical_authority'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(
                fields=('source', 'source_reference'),
                condition=models.Q(source='workspace'),
                name='uniq_workspace_source_reference',
            ),
        ),
    ]
