# Generated for Session 807 - Restore Body System Tables (v2)
"""
THIS MIGRATION IS NOW A NO-OP.

Original purpose: Restore body system tables deleted by migration 0183.
However, this migration failed in production because some tables still existed.

The actual table creation is now handled by migration 0185 which uses
IF NOT EXISTS to safely create only missing tables.

Session 807: Converted to no-op after partial failure in production.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0183_delete_brainpulse_delete_cognitivechannel_and_more'),
    ]

    operations = [
        # No-op - actual work done in 0185
        migrations.RunSQL(
            sql="SELECT 1;",  # No-op
            reverse_sql="SELECT 1;",
        ),
    ]
