# Session 1131 Phase 2 — Curated signal snapshot tables.
#
# Two new tables (Rigby's lock from conversation pa-d19c1674b936):
#   - `CuratedSignalSnapshot` parent  — one row per curation run
#   - `CuratedSignalEntry` child      — one row per curated cluster
#
# Snapshot provenance fields (lock #4): scoring_formula_version,
# dedup_strategy, pattern_type_cap. excluded_duplicates lives on the
# snapshot row as JSON for v1 (cheap audit trail; promote to a child
# table later if we need to query "show me all dupe-eliminated rows").
#
# Entry rows snapshot the cluster's metrics AT THE TIME OF CURATION so
# we can explain "why was this picked" even after the cluster row's
# strength/size drift further.

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0347_signalcluster_seq"),
    ]

    operations = [
        migrations.CreateModel(
            name="CuratedSignalSnapshot",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "scoring_formula_version",
                    models.CharField(
                        max_length=80,
                        help_text=(
                            "Versioned identifier of the scoring formula used "
                            "to produce this snapshot (e.g. "
                            "'v1_strength_0.9_recency_0.1_tau72'). Changing the "
                            "formula bumps the version; the snapshot record "
                            "keeps the link to the formula it was scored with."
                        ),
                    ),
                ),
                (
                    "dedup_strategy",
                    models.CharField(
                        max_length=120,
                        help_text=(
                            "Human-readable dedup strategy identifier "
                            "(e.g. 'group_best_by(pattern_type, topic_key)'). "
                            "Lets the audit trail name HOW duplicates were "
                            "collapsed."
                        ),
                    ),
                ),
                (
                    "pattern_type_cap",
                    models.JSONField(
                        default=dict,
                        blank=True,
                        help_text=(
                            "Per-pattern_type diversity cap config "
                            "(e.g. {'cap': 3, 'rule': 'max(2, ceil(N/4))'}). "
                            "Empty dict means no per-type cap was applied."
                        ),
                    ),
                ),
                (
                    "pool_size",
                    models.IntegerField(
                        help_text=(
                            "Total cluster candidates scored before dedup "
                            "(everything matching the Phase 1 quality bar at "
                            "snapshot time)."
                        ),
                    ),
                ),
                (
                    "top_n",
                    models.IntegerField(
                        help_text="Number of entries actually persisted on this snapshot.",
                    ),
                ),
                (
                    "excluded_duplicates",
                    models.JSONField(
                        default=list,
                        blank=True,
                        help_text=(
                            "Audit list of clusters dropped by dedup grouping. "
                            "Shape per entry: "
                            "{cluster_id, group_key, score, lost_to_cluster_id}. "
                            "JSON for v1; promote to a child table if we ever "
                            "need to query historical exclusions across "
                            "snapshots."
                        ),
                    ),
                ),
            ],
            options={
                "verbose_name": "Curated Signal Snapshot",
                "verbose_name_plural": "Curated Signal Snapshots",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CuratedSignalEntry",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                (
                    "snapshot",
                    models.ForeignKey(
                        to="core.curatedsignalsnapshot",
                        on_delete=models.deletion.CASCADE,
                        related_name="entries",
                    ),
                ),
                (
                    "cluster",
                    models.ForeignKey(
                        to="core.signalcluster",
                        on_delete=models.deletion.CASCADE,
                        related_name="curated_entries",
                    ),
                ),
                (
                    "rank",
                    models.IntegerField(
                        help_text=(
                            "1-based rank within the snapshot. rank=1 is the "
                            "highest curated_score; ties broken by cluster.seq "
                            "ASC (older row wins) so ranking is deterministic."
                        ),
                    ),
                ),
                (
                    "curated_score",
                    models.FloatField(
                        help_text="Composite score this cluster earned in the snapshot run.",
                    ),
                ),
                (
                    "group_key",
                    models.CharField(
                        max_length=200,
                        help_text=(
                            "Dedup group key the cluster won "
                            "(e.g. 'demand_spike::react'). Stored verbatim so "
                            "we can trace which group it competed in."
                        ),
                    ),
                ),
                (
                    "strength_at_pick",
                    models.FloatField(
                        help_text="Cluster.strength at snapshot time (immutable record).",
                    ),
                ),
                (
                    "cluster_size_at_pick",
                    models.IntegerField(
                        help_text="sum(source_breakdown.values()) at snapshot time.",
                    ),
                ),
                (
                    "age_hours_at_pick",
                    models.FloatField(
                        help_text="Hours since detected_at when the snapshot ran.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Curated Signal Entry",
                "verbose_name_plural": "Curated Signal Entries",
                "ordering": ["snapshot", "rank"],
            },
        ),
        migrations.AddConstraint(
            model_name="curatedsignalentry",
            constraint=models.UniqueConstraint(
                fields=["snapshot", "rank"],
                name="curated_signal_entry_unique_rank_per_snapshot",
            ),
        ),
        migrations.AddIndex(
            model_name="curatedsignalentry",
            index=models.Index(
                fields=["cluster", "-snapshot"],
                name="curated_entry_cluster_idx",
            ),
        ),
    ]
