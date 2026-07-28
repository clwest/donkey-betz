# S3022 U5b — backfill Initiative.signal_cluster FK from parent_topic
#
# S3021 (U5) fixed the writer path so new cluster→initiative creates set the
# Initiative.signal_cluster FK directly at create time (matching hivemind's
# direct-set-then-fallback pattern). This migration normalizes the pre-U5
# stranded rows.
#
# Pre-migration audit (2026-07-28, HEAD 68bc94510):
#   Total Initiatives with parent_topic starts 'signal_cluster:':  4
#     Already linked (FK set from S3021 live smoke):               1
#     Eligible for backfill (FK NULL):                             3
#       Valid UUID parse:                                          3 (100%)
#         Resolves to existing SignalCluster row:                  3 (100%)
#         Missing cluster (deleted / phantom):                     0
#       Malformed parent_topic:                                    0
#
# Zero parse-tail risk in the current dataset. Migration is written to be
# safely no-op on datasets where either (a) the parent_topic is malformed
# or (b) the referenced cluster was deleted — those rows are left as-is
# with the FK still NULL, matching Rigby's "skip-on-missing" guardrail.
#
# Idempotent: safe to re-run. Only touches rows where
# signal_cluster_id IS NULL AND parent_topic starts 'signal_cluster:' AND
# the parsed UUID resolves to an existing SignalCluster.
#
# Reverse: RunPython.noop. Reversing would need per-row prior-null tracking
# which we don't preserve; and the semantically correct rollback (set FK
# back to NULL) would silently drop the deterministic linkage the writer
# path is now establishing. A no-op reverse is the honest choice.

import re

from django.db import migrations


_UUID_RE = re.compile(
    r"^signal_cluster:([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$",
    re.IGNORECASE,
)


def backfill_signal_cluster_fk(apps, schema_editor):
    Initiative = apps.get_model("core", "Initiative")
    SignalCluster = apps.get_model("core", "SignalCluster")

    eligible = Initiative.objects.filter(
        parent_topic__startswith="signal_cluster:",
        signal_cluster__isnull=True,
    ).only("id", "parent_topic")

    linked = 0
    skipped_malformed = 0
    skipped_missing_cluster = 0

    for row in eligible.iterator(chunk_size=500):
        match = _UUID_RE.match(row.parent_topic or "")
        if not match:
            skipped_malformed += 1
            continue
        cluster_id = match.group(1)
        if not SignalCluster.objects.filter(id=cluster_id).exists():
            skipped_missing_cluster += 1
            continue
        Initiative.objects.filter(id=row.id).update(signal_cluster_id=cluster_id)
        linked += 1

    print(
        f"[s3022_u5b_backfill] linked={linked} "
        f"skipped_malformed={skipped_malformed} "
        f"skipped_missing_cluster={skipped_missing_cluster}"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0403_s2995_staleness_backfill"),
    ]

    operations = [
        migrations.RunPython(
            backfill_signal_cluster_fk,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
