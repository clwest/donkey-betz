# Session 1131 — signal-studio Phase 1 (Rigby's path B):
# Monotonic seq column on SignalCluster.
#
# Mirrors the Move 3 R2 FleetEvent.seq pattern (migration 0346): a
# Postgres-managed BIGINT sequence powering an exclusive-cursor replay
# endpoint at GET /api/fleet/signals/clusters?since=<seq>&limit=<n>.
#
# Why a dedicated `seq` and not reuse `detected_at`:
#   - `ORDER BY seq ASC` is monotonic + tie-free (timestamps can collide
#     under bulk inserts; UUID `id` is unordered).
#   - `?since=<seq>` semantics are "strictly greater than" — same
#     contract signal-studio backfills against in Phase 1 Step 3.
#   - Existing 307 rows get assigned seq in `detected_at` order so the
#     first signal-studio backfill replays from a coherent baseline.
#
# Django 5 `db_default=RawSQL("nextval(...)")` is mandatory here —
# `null=True` alone would make Django pass NULL in INSERT, which would
# override the DB DEFAULT and trip NOT NULL. Memory rule from Session
# 1130 (feedback_db_default_for_db_managed_columns).

from django.db import migrations, models


CREATE_SEQUENCE_SQL = """
CREATE SEQUENCE IF NOT EXISTS core_signalcluster_seq;
"""

DROP_SEQUENCE_SQL = """
DROP SEQUENCE IF EXISTS core_signalcluster_seq;
"""

# Add column, backfill in detected_at order, attach sequence default,
# set NOT NULL, set sequence ownership. Mirrors 0346_fleetevent_seq.
ADD_COLUMN_SQL = """
ALTER TABLE core_signalcluster ADD COLUMN IF NOT EXISTS seq BIGINT;

WITH ordered AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY detected_at, id) AS rn
    FROM core_signalcluster
    WHERE seq IS NULL
)
UPDATE core_signalcluster c
SET seq = ordered.rn
FROM ordered
WHERE c.id = ordered.id;

SELECT setval(
    'core_signalcluster_seq',
    COALESCE((SELECT MAX(seq) FROM core_signalcluster), 0) + 1,
    false
);

ALTER TABLE core_signalcluster
    ALTER COLUMN seq SET DEFAULT nextval('core_signalcluster_seq');

ALTER TABLE core_signalcluster
    ALTER COLUMN seq SET NOT NULL;

ALTER SEQUENCE core_signalcluster_seq OWNED BY core_signalcluster.seq;
"""

DROP_COLUMN_SQL = """
ALTER TABLE core_signalcluster DROP COLUMN IF EXISTS seq;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0346_fleetevent_seq"),
    ]

    operations = [
        # Sequence first — column DEFAULT references it.
        migrations.RunSQL(
            sql=CREATE_SEQUENCE_SQL,
            reverse_sql=DROP_SEQUENCE_SQL,
        ),
        # Column + backfill via raw SQL; state op informs Django ORM.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=ADD_COLUMN_SQL,
                    reverse_sql=DROP_COLUMN_SQL,
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name="signalcluster",
                    name="seq",
                    field=models.BigIntegerField(
                        db_default=models.expressions.RawSQL(
                            "nextval('core_signalcluster_seq')", []
                        ),
                        editable=False,
                        help_text=(
                            "Monotonic cluster sequence number assigned by "
                            "Postgres at INSERT via the "
                            "`core_signalcluster_seq` sequence. Canonical "
                            "ordering cursor for the signal-studio replay "
                            "endpoint (`?since=<seq>` is exclusive). Django 5 "
                            "`db_default` omits this column from INSERTs so "
                            "the sequence fires server-side."
                        ),
                        unique=True,
                    ),
                ),
            ],
        ),
        # Composite index for the replay path (no app_slug column on
        # SignalCluster — only signal-studio is allowlisted to call the
        # endpoint, so a plain seq filter is the workload). The unique
        # constraint above already provides the btree on seq; no
        # additional index needed for Phase 1.
    ]
