"""
Phase 3.2: pg_trgm GIN indexes on LearningPattern.

Enables the pg_trgm extension and creates conditional GIN indexes on
`description` and `pattern_type` (filtered to is_active=True) so that
`__icontains` lookups use index scans instead of sequential scans.
"""

from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.indexes import GinIndex
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0232_phase1_deliberation_persistence"),
    ]

    operations = [
        TrigramExtension(),
        migrations.AddIndex(
            model_name="learningpattern",
            index=GinIndex(
                fields=["description"],
                name="lp_desc_trgm_active",
                opclasses=["gin_trgm_ops"],
                condition=Q(is_active=True),
            ),
        ),
        migrations.AddIndex(
            model_name="learningpattern",
            index=GinIndex(
                fields=["pattern_type"],
                name="lp_type_trgm_active",
                opclasses=["gin_trgm_ops"],
                condition=Q(is_active=True),
            ),
        ),
    ]
