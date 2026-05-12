"""Re-add columns dropped by migration 0185's raw CREATE TABLE IF NOT EXISTS.

Session 1115 finding 15: `core/services/skin.py::get_vitals()` raises
`ProgrammingError: column core_skin_status.total_files_tracked does not
exist` on freshly-bootstrapped local databases.

Root cause: migration `0185_fix_body_system_tables.py:141` uses raw
`CREATE TABLE IF NOT EXISTS core_skin_status (...)` but the inline column
list is missing two fields that exist on `core.models_skin.SkinStatus`:

- `total_files_tracked` (IntegerField default=0)
- `total_operations_all_time` (IntegerField default=0)

On long-lived DBs the prior migration 0182 had already added these
columns, so `CREATE TABLE IF NOT EXISTS` was a no-op and the columns
survived. On fresh DBs the table didn't exist yet, so 0185 created it
without those two fields, and now skin vitals queries fail.

The fix is idempotent — `ADD COLUMN IF NOT EXISTS` so it's safe to run
against any prior DB state.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0337_deliverable_appends'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE core_skin_status '
                'ADD COLUMN IF NOT EXISTS total_files_tracked INTEGER DEFAULT 0;'
                ' '
                'ALTER TABLE core_skin_status '
                'ADD COLUMN IF NOT EXISTS total_operations_all_time INTEGER DEFAULT 0;'
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
