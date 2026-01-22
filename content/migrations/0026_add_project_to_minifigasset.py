# Generated manually for Session 137
# NOTE: This migration was originally adding project FK to MiniFigAsset,
# but migration 0021 already adds this field. Making this a no-op.
from django.db import migrations


class Migration(migrations.Migration):
    """
    No-op migration - field already added in 0021_add_project_to_minifig.
    Kept for migration history continuity.
    """

    dependencies = [
        ("content", "0025_fix_seed_bigint"),
    ]

    operations = [
        # Field already exists from migration 0021, so no operations needed
    ]
