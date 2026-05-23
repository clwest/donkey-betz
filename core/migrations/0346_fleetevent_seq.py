# Session 1130 — Move 3 Round 2: Monotonic seq column on FleetEvent.
#
# Per Rigby's lock #1 (conversation pa-d19c1674b936): the canonical
# replay cursor is a Postgres-managed BIGINT sequence, not
# `timestamp + uuid`. We add a `seq` column backed by a dedicated
# sequence (`core_fleetevent_seq`) so:
#
#   - `ORDER BY seq ASC` is monotonic + tie-free.
#   - `?since=<seq>` cursor semantics are "strictly greater than".
#   - Backfilled rows (the 12 existing artifact.created events from
#     Session 1129) get assigned seq values in `created_at` order so
#     replay starts from a coherent baseline.
#
# We mix raw SQL (sequence + default) with Django state operations so
# the ORM knows about the field. The unique index and app_slug+seq
# composite both land here as the canonical replay index.

from django.db import migrations, models


CREATE_SEQUENCE_SQL = """
CREATE SEQUENCE IF NOT EXISTS core_fleetevent_seq;
"""

DROP_SEQUENCE_SQL = """
DROP SEQUENCE IF EXISTS core_fleetevent_seq;
"""

# Add the column, backfill existing rows in created_at order, attach
# the sequence default + ownership, set NOT NULL.
ADD_COLUMN_SQL = """
ALTER TABLE core_fleetevent ADD COLUMN IF NOT EXISTS seq BIGINT;

WITH ordered AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY created_at, id) AS rn
    FROM core_fleetevent
    WHERE seq IS NULL
)
UPDATE core_fleetevent f
SET seq = ordered.rn
FROM ordered
WHERE f.id = ordered.id;

-- Bump the sequence past whatever we just backfilled so the next
-- INSERT picks up from max(seq) + 1. setval(..., is_called=true) means
-- the next nextval() returns max(seq) + 1.
SELECT setval(
    'core_fleetevent_seq',
    COALESCE((SELECT MAX(seq) FROM core_fleetevent), 0) + 1,
    false
);

ALTER TABLE core_fleetevent
    ALTER COLUMN seq SET DEFAULT nextval('core_fleetevent_seq');

ALTER TABLE core_fleetevent
    ALTER COLUMN seq SET NOT NULL;

ALTER SEQUENCE core_fleetevent_seq OWNED BY core_fleetevent.seq;
"""

DROP_COLUMN_SQL = """
ALTER TABLE core_fleetevent DROP COLUMN IF EXISTS seq;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0345_fleetevent"),
    ]

    operations = [
        # Sequence first — column DEFAULT references it.
        migrations.RunSQL(
            sql=CREATE_SEQUENCE_SQL,
            reverse_sql=DROP_SEQUENCE_SQL,
        ),
        # Column + backfill via raw SQL; state op tells Django about
        # the new field so the ORM treats it as a real column.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=ADD_COLUMN_SQL,
                    reverse_sql=DROP_COLUMN_SQL,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="fleetevent",
                    name="seq",
                    field=models.BigIntegerField(
                        db_default=models.expressions.RawSQL(
                            "nextval('core_fleetevent_seq')", []
                        ),
                        editable=False,
                        help_text=(
                            "Monotonic event sequence number assigned by "
                            "Postgres at INSERT via the `core_fleetevent_seq` "
                            "sequence. Canonical ordering cursor for SSE "
                            "replay (`?since=<seq>` is exclusive). Django 5 "
                            "`db_default` omits this column from INSERTs so "
                            "the sequence fires server-side."
                        ),
                        unique=True,
                    ),
                ),
            ],
        ),
        # Indexes + Meta updates. AlterModelOptions sets ordering=["seq"]
        # to match Rigby's lock that cursor reads are seq-ordered.
        migrations.AlterModelOptions(
            name="fleetevent",
            options={
                "ordering": ["seq"],
                "verbose_name": "Fleet Event",
                "verbose_name_plural": "Fleet Events",
            },
        ),
        migrations.AddIndex(
            model_name="fleetevent",
            index=models.Index(
                fields=["app_slug", "seq"],
                name="core_fleete_app_seq_idx",
            ),
        ),
    ]
