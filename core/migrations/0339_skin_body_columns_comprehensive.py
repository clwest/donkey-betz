"""Restore all `SkinStatus` + `SkinPulse` columns dropped by migration 0185.

Session 1115 finding 15 (continued). After migration 0338 fixed the two
most-immediately-failing columns, a deeper diff revealed 13 additional
columns missing from the two skin body-system tables:

`core_skin_status` (6 missing):
  - avg_operation_time_ms (FloatField default=0)
  - error_rate_24h (FloatField default=0)
  - last_error_at (DateTimeField, null=True)
  - last_successful_operation_at (DateTimeField, null=True)
  - operations_per_hour (FloatField default=0)
  - pending_reviews (IntegerField default=0)

`core_skin_pulses` (9 missing):
  - agent_operation_counts (JSONField default=dict)
  - avg_operation_time_ms (FloatField default=0)
  - commands_executed_24h (IntegerField default=0)
  - git_operations_24h (IntegerField default=0)
  - lines_changed_24h (IntegerField default=0)
  - most_active_agent (CharField max_length=100; no model default — use '')
  - pending_reviews (IntegerField default=0)
  - permission_denials (IntegerField default=0)
  - rollbacks_performed_24h (IntegerField default=0)

Same root cause as 0338: migration `0185_fix_body_system_tables.py` used
raw `CREATE TABLE IF NOT EXISTS` with an inline column list that
predated several model additions. On fresh DBs the table got created
without these columns; on long-lived DBs the prior CREATE+ALTER history
had already added them so IF NOT EXISTS was a no-op.

All operations use `ADD COLUMN IF NOT EXISTS` so this is idempotent —
safe on any prior DB state.
"""
from django.db import migrations


SQL = '''
-- core_skin_status fixes
ALTER TABLE core_skin_status ADD COLUMN IF NOT EXISTS avg_operation_time_ms DOUBLE PRECISION DEFAULT 0;
ALTER TABLE core_skin_status ADD COLUMN IF NOT EXISTS error_rate_24h DOUBLE PRECISION DEFAULT 0;
ALTER TABLE core_skin_status ADD COLUMN IF NOT EXISTS last_error_at TIMESTAMPTZ NULL;
ALTER TABLE core_skin_status ADD COLUMN IF NOT EXISTS last_successful_operation_at TIMESTAMPTZ NULL;
ALTER TABLE core_skin_status ADD COLUMN IF NOT EXISTS operations_per_hour DOUBLE PRECISION DEFAULT 0;
ALTER TABLE core_skin_status ADD COLUMN IF NOT EXISTS pending_reviews INTEGER DEFAULT 0;

-- core_skin_pulses fixes
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS agent_operation_counts JSONB DEFAULT '{}'::jsonb;
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS avg_operation_time_ms DOUBLE PRECISION DEFAULT 0;
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS commands_executed_24h INTEGER DEFAULT 0;
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS git_operations_24h INTEGER DEFAULT 0;
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS lines_changed_24h INTEGER DEFAULT 0;
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS most_active_agent VARCHAR(100) DEFAULT '';
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS pending_reviews INTEGER DEFAULT 0;
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS permission_denials INTEGER DEFAULT 0;
ALTER TABLE core_skin_pulses ADD COLUMN IF NOT EXISTS rollbacks_performed_24h INTEGER DEFAULT 0;
'''


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0338_skin_status_missing_columns'),
    ]

    operations = [
        migrations.RunSQL(sql=SQL, reverse_sql=migrations.RunSQL.noop),
    ]
