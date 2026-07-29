"""Session 3030: backfill AgentDecisionSummary rows with canonical drift.

**What this heals.** From ~Session 988 through Session 3029, the scheduled
boardroom-auto-approve task (`_impl_auto_approve_boardroom_items` in
`core/tasks_ops.py`) used bulk `QuerySet.update(status='canonical')` to
promote decisions. `.update()` bypasses model save/signals, leaving rows
with `status='canonical'` but `is_canonical=False`, `promoted_at=NULL`,
`promoted_by=''`. Session 3029 PR #3747 fixed the source (all six
canonical-promotion paths now go through
`AgentDecisionSummary.promote_to_canonical`). This command backfills
the accumulated drift rows that pre-date that fix.

**Why the query is safe.** `filter(status='canonical', is_canonical=False)`
only matches rows that were promoted the broken way. Any correctly
promoted row (broadcast paths post-S3026 or the AI/Rules/PA services)
sets `is_canonical=True` at promotion and is naturally excluded — this
command is idempotent and safe to re-run.

**Why we override promoted_at back to updated_at.** The true promotion
moment is lost. `.update()` bumps `auto_now` on `updated_at`, so it is
the closest surviving proxy. `promote_to_canonical()` sets
`promoted_at=timezone.now()`; we intentionally overwrite that with the
pre-heal `updated_at` so the backfilled timestamp reflects "sometime
around when this row was promoted the broken way," not "now." Callers
of `promoted_at` should treat backfilled values as approximate; the
`promoted_by='backfill-s3030-tasks-ops-drift'` marker makes them
identifiable.

**Why we do NOT broadcast.** The six canonical-promotion paths in
production emit `canonical_decision_promoted` broadcasts at the caller
site (e.g. `tasks_ops.py:301` after `promote_to_canonical()` returns).
The model method itself does not broadcast. This command deliberately
does not call `emit_canonical_promotion_broadcast()` because the drift
rows are up to five years old — waking WebSocket/Discord subscribers on
belated "freshly promoted" events would be misleading. Downstream
consumers that filter `is_canonical=True` (policy_context.py,
views_project_intelligence.py, views_agent_learning.py,
project_intelligence_consumer.py, agent_intelligence_context.py,
auto_kpi_tracking.py, pa_intelligence_enricher.py,
experiment_suggestion.py) start seeing the healed rows immediately via
polling/query paths, which is the correct behavior for backfill.

**S3036 note.** Because this command does not emit lifecycle broadcasts,
it also does NOT appear in the `CANONICAL_LIFECYCLE_ACTORS` taxonomy in
`core/services/canonical_decision_broadcast.py`. There is no
`ACTOR_BACKFILL` — silence in the actor taxonomy is the correct signal
that a code path is out-of-scope for the lifecycle broadcast (and
therefore also out-of-scope for the BoardroomTab lifecycle activity
panel).

Usage:
    python manage.py backfill_canonical_drift              # dry-run (default)
    python manage.py backfill_canonical_drift --apply       # perform heal
    python manage.py backfill_canonical_drift --apply --limit 100
"""

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models_unified_system import AgentDecisionSummary

logger = logging.getLogger(__name__)

BACKFILL_MARKER = 'backfill-s3030-tasks-ops-drift'
DEFAULT_LIMIT = 500
PROGRESS_EVERY = 100
SAMPLE_ROWS = 5


class Command(BaseCommand):
    help = (
        "Backfill AgentDecisionSummary rows with status='canonical' but "
        "is_canonical=False (drift from pre-S3029 bulk .update() bug)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually perform the backfill. Without this flag, runs dry-run.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=DEFAULT_LIMIT,
            help=f'Maximum drift rows to process per run (default: {DEFAULT_LIMIT}).',
        )

    def handle(self, *args, **options):
        apply_ = options['apply']
        limit = options['limit']

        drift_qs = (
            AgentDecisionSummary.objects
            .filter(status='canonical', is_canonical=False)
            .order_by('created_at')
        )
        total_drift = drift_qs.count()

        mode = 'APPLY' if apply_ else 'DRY-RUN'
        self.stdout.write(
            f"[backfill_canonical_drift] mode={mode} total_drift={total_drift} limit={limit}"
        )

        if total_drift == 0:
            self.stdout.write(self.style.SUCCESS("No drift rows — nothing to do."))
            return

        sample = list(drift_qs.values(
            'id', 'topic', 'decision_type', 'created_at', 'updated_at'
        )[:SAMPLE_ROWS])
        self.stdout.write(f"Sample (first {len(sample)} of {total_drift}):")
        for row in sample:
            self.stdout.write(
                f"  {row['id']} [{row['decision_type']}] {row['topic'][:60]!r} "
                f"created={row['created_at']} updated={row['updated_at']}"
            )

        if not apply_:
            self.stdout.write(self.style.WARNING(
                "(dry-run — no writes. Re-run with --apply to heal.)"
            ))
            return

        healed = 0
        errors = 0
        batch = list(drift_qs[:limit])

        for decision in batch:
            original_updated_at = decision.updated_at
            try:
                with transaction.atomic():
                    decision.promote_to_canonical(promoted_by=BACKFILL_MARKER)
                    decision.promoted_at = original_updated_at
                    decision.save(update_fields=['promoted_at'])
                healed += 1
            except Exception as exc:
                errors += 1
                if errors <= 3:
                    logger.exception(
                        "[backfill_canonical_drift] row %s heal failed: %s",
                        decision.id, exc,
                    )
            if (healed + errors) % PROGRESS_EVERY == 0:
                self.stdout.write(
                    f"  progress: healed={healed} errors={errors}"
                )

        processed = healed + errors
        remaining = total_drift - processed
        self.stdout.write(self.style.SUCCESS(
            f"Done. processed={processed} healed={healed} errors={errors} "
            f"remaining={remaining} (re-run to continue if remaining > 0)"
        ))
