"""
Session 1163 B-style follow-on — create FinalAppliedOverrides per-cycle
history model + backfill the existing single-row SystemConfiguration
snapshot into it.

Closes the mechanism drift recorded in Disclosure L §14 and narrative
SELF_TUNING_AND_EXPERIMENTATION.md §6.4. The original
`record_overrides_snapshot` writer overwrote a single
`SystemConfiguration(key='policy_arbitrator_snapshot')` row each
cycle — no per-cycle history, no time-travel queries possible.

This migration:
1. Creates the FinalAppliedOverrides model (per-cycle append-only).
2. Backfills the existing SystemConfiguration row (if present) into
   the new model so `latest_overrides_snapshot` does not return
   `found: false` immediately after deploy/restart.

Per Rigby's design call: the backfill is idempotent — runs only when
the new table is empty AND a SystemConfiguration row exists. Operators
running this migration repeatedly (e.g., during local dev) will not
get duplicate backfill rows.

The legacy SystemConfiguration row is NOT deleted by this migration;
that is a separate cleanup PR after one new-model cycle has been
observed in prod (per Rigby's "Pick (b) + later (c)" recommendation).
"""

import json
import uuid

from django.db import migrations, models
from django.utils.dateparse import parse_datetime


def backfill_latest_snapshot_into_new_model(apps, schema_editor):
    """
    Copy the single SystemConfiguration(key='policy_arbitrator_snapshot')
    row (if it exists) into the new FinalAppliedOverrides table.

    Idempotent: skips if any FinalAppliedOverrides row already exists.
    """
    SystemConfiguration = apps.get_model('core', 'SystemConfiguration')
    FinalAppliedOverrides = apps.get_model('core', 'FinalAppliedOverrides')

    if FinalAppliedOverrides.objects.exists():
        # Already backfilled (or new-model already producing rows).
        return

    entry = SystemConfiguration.objects.filter(
        key='policy_arbitrator_snapshot',
    ).first()
    if entry is None:
        # Nothing to backfill; new model starts empty.
        return

    try:
        payload = json.loads(entry.value) if entry.value else {}
    except (ValueError, TypeError):
        payload = {}

    # cycle_ts preference order:
    # 1. payload['ts'] if present + parseable (matches the original
    #    arbitrator capture timestamp);
    # 2. SystemConfiguration row's updated_at (the DB row's mtime).
    cycle_ts = None
    ts_str = payload.get('ts')
    if isinstance(ts_str, str):
        cycle_ts = parse_datetime(ts_str)
    if cycle_ts is None:
        cycle_ts = entry.updated_at

    knobs = payload.get('knobs') or {}
    if not isinstance(knobs, dict):
        knobs = {}

    # cycle_id preference:
    # 1. payload's cycle_id if it parses as a UUID;
    # 2. new uuid4.
    cycle_id_str = payload.get('cycle_id')
    cycle_id = None
    if isinstance(cycle_id_str, str):
        try:
            cycle_id = uuid.UUID(cycle_id_str)
        except (ValueError, TypeError, AttributeError):
            cycle_id = None
    if cycle_id is None:
        cycle_id = uuid.uuid4()

    knob_count_payload = payload.get('knob_count')
    knob_count = (
        knob_count_payload
        if isinstance(knob_count_payload, int) else len(knobs)
    )

    FinalAppliedOverrides.objects.create(
        cycle_id=cycle_id,
        cycle_ts=cycle_ts,
        knob_count=knob_count,
        applied_values=knobs,
    )


def reverse_backfill(apps, schema_editor):
    """
    No-op reverse migration. The backfill row carries no special
    sentinel that distinguishes it from a real cycle row, and
    deleting "the backfill row" after later cycles have written
    additional rows would be a guess. Reverse is intentionally
    empty; running the migration forward again is idempotent
    (skips when rows exist).
    """
    return


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0353_session_1140_action_status_needs_regen'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalAppliedOverrides',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    'cycle_id',
                    models.UUIDField(
                        help_text=(
                            'UUID identifying the autopilot cycle '
                            'that produced this snapshot. Useful for '
                            'joining against AutopilotAction records '
                            'emitted during the same cycle.'
                        ),
                        unique=True,
                    ),
                ),
                (
                    'cycle_ts',
                    models.DateTimeField(
                        db_index=True,
                        help_text=(
                            'Wall-clock time the arbitrator captured '
                            'the snapshot, passed in by the cycle '
                            'wrapper via `now` (typically '
                            'django.utils.timezone.now()). Indexed '
                            'for time-travel queries via '
                            '`.filter(cycle_ts__lte=t).order_by'
                            "('-cycle_ts').first()`."
                        ),
                    ),
                ),
                (
                    'knob_count',
                    models.IntegerField(
                        help_text=(
                            'Number of knobs in the applied_values '
                            'dict at the time of capture. Stored '
                            'explicitly to avoid a JSONB parse on '
                            'every summary query.'
                        ),
                    ),
                ),
                (
                    'applied_values',
                    models.JSONField(
                        default=dict,
                        help_text=(
                            'Knob name -> {value, owner, priority} '
                            'dict. The owner field identifies the '
                            'policy that wrote the knob; priority is '
                            'the merge precedence the arbitrator '
                            'used to resolve any same-cycle '
                            'conflicts.'
                        ),
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text=(
                            'Django-managed row creation timestamp. '
                            'Usually within milliseconds of cycle_ts; '
                            'significant divergence between the two '
                            'is itself a debugging signal.'
                        ),
                    ),
                ),
            ],
            options={
                'verbose_name': 'Final Applied Overrides Snapshot',
                'verbose_name_plural': 'Final Applied Overrides Snapshots',
                'db_table': 'core_final_applied_overrides',
                'ordering': ['-cycle_ts'],
            },
        ),
        migrations.AddIndex(
            model_name='finalappliedoverrides',
            index=models.Index(
                fields=['-cycle_ts'],
                name='fao_cycle_ts_desc',
            ),
        ),
        migrations.RunPython(
            backfill_latest_snapshot_into_new_model,
            reverse_backfill,
        ),
    ]
