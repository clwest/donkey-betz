"""Session 1094: bulk-archive historical ACTIVE initiative sediment.

The COOAgent daily diagnostic surfaced 147 initiatives in `status='ACTIVE'`
that hadn't been updated in 30+ days (oldest 76d). They're dead — started
in earlier sessions and abandoned, but never transitioned out of ACTIVE.
Keeping them ACTIVE is lying to the model: every scheduled gate, every
agent that reads active-initiative state, sees them as live work.

This command transitions such sediment to `status='ARCHIVED'` so they're
preserved (not deleted) but no longer show up as active.

Usage
-----

Dry-run (preview without writing) — default mode:

    python manage.py cleanup_stale_initiatives --older-than-days 30

Apply the archive:

    python manage.py cleanup_stale_initiatives --older-than-days 30 --apply

Limit the per-stage scope (e.g. only archive stage-1 sediment):

    python manage.py cleanup_stale_initiatives \\
        --older-than-days 30 \\
        --only-stage 1 \\
        --apply

Idempotent — safe to re-run. Already-archived initiatives are skipped.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from core.models import Initiative


class Command(BaseCommand):
    help = (
        "Archive ACTIVE initiatives whose updated_at is older than N days. "
        "Preserves rows; transitions status='ACTIVE' → status='ARCHIVED'."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than-days",
            type=int,
            required=True,
            help="Archive ACTIVE initiatives with updated_at older than this many days.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually perform the archive. Default is dry-run (preview only).",
        )
        parser.add_argument(
            "--only-stage",
            type=int,
            default=None,
            help="Restrict to a single current_stage value (e.g. 1 for sediment stuck at ResearchStage).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Cap the number of rows processed (useful for incremental cleanups).",
        )

    def handle(self, *args, **options):
        days = options["older_than_days"]
        apply_changes = options["apply"]
        only_stage = options["only_stage"]
        limit = options["limit"]

        if days <= 0:
            raise CommandError("--older-than-days must be a positive integer")

        cutoff = timezone.now() - timedelta(days=days)

        qs = Initiative.objects.filter(
            status='ACTIVE',
            updated_at__lte=cutoff,
        )
        if only_stage is not None:
            qs = qs.filter(current_stage=only_stage)

        qs = qs.order_by('updated_at')
        total_candidates = qs.count()

        if limit is not None:
            qs = qs[:limit]

        candidates = list(qs.values('id', 'name', 'current_stage', 'updated_at'))

        mode = "APPLY" if apply_changes else "DRY-RUN"
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"cleanup_stale_initiatives [{mode}] — cutoff={cutoff.date()} (>{days}d)"
        ))
        self.stdout.write(f"  Candidates matching filter: {total_candidates}")
        if limit is not None and limit < total_candidates:
            self.stdout.write(f"  Limited to first: {len(candidates)}")

        if only_stage is not None:
            self.stdout.write(f"  Stage filter: current_stage={only_stage}")

        if not candidates:
            self.stdout.write(self.style.SUCCESS(
                "No stale initiatives found — nothing to do."
            ))
            return

        # Breakdown by stage
        by_stage: dict = {}
        for row in candidates:
            stage = row.get('current_stage')
            by_stage[stage] = by_stage.get(stage, 0) + 1
        self.stdout.write("  Breakdown by stage:")
        for stage in sorted(by_stage.keys(), key=lambda s: (s is None, s)):
            self.stdout.write(f"    stage {stage}: {by_stage[stage]}")

        # Oldest + newest in the batch
        oldest = candidates[0]
        newest = candidates[-1]
        self.stdout.write(f"  Oldest in batch: {(timezone.now() - oldest['updated_at']).days}d — {(oldest['name'] or '')[:60]}")
        self.stdout.write(f"  Newest in batch: {(timezone.now() - newest['updated_at']).days}d — {(newest['name'] or '')[:60]}")

        if not apply_changes:
            self.stdout.write(self.style.WARNING(
                "\nDry-run complete. Re-run with --apply to archive these initiatives."
            ))
            return

        # Apply — use a bulk update for speed, then log individual results
        ids = [row['id'] for row in candidates]
        updated_count = Initiative.objects.filter(id__in=ids).update(
            status='ARCHIVED',
            updated_at=timezone.now(),
        )

        self.stdout.write(self.style.SUCCESS(
            f"\nArchived {updated_count} initiatives. Status transitioned "
            f"'ACTIVE' → 'ARCHIVED' (rows preserved)."
        ))
