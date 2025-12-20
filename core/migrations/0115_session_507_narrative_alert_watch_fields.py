# Generated manually for Session 507 - Discord /narrative-watch command support
# Note: Columns already added via direct SQL, this migration is now a no-op
# Session 513: Converted to RunPython no-op to fix state reconstruction issue

from django.db import migrations


def noop(apps, schema_editor):
    """No-op migration - columns already exist in database."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0114_alter_autonomoussituationsession_situation_type'),
    ]

    operations = [
        # Original state-only operations caused migration state reconstruction issues.
        # The columns already exist in the database, so this is now a no-op.
        migrations.RunPython(noop, noop),
    ]
