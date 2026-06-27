"""Session 1244 — rename ml.MLModelVersion → ml.SportsMLModelVersion.

Cat 2 dormant cleanup batch. Removes the cross-app naming collision with
`core.MLModelVersion` (in `core.models_unified_system`) by giving the ml
variant a more descriptive name that reflects its sport-specific schema.

The ml variant has fields like `sport_type`, `model_name`,
`training_start_date`, `training_end_date` — clearly tracking sports-
prediction ML model versions. The core variant is a generic ML model
versioning surface (different concept).

Both tables empty (0 rows). RenameModel is atomic and data-safe.

Audit: deliverable 86870fdd-… Finding 2.3.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ml", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="MLModelVersion",
            new_name="SportsMLModelVersion",
        ),
    ]
