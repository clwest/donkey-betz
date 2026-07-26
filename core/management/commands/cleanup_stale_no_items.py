"""
S2975: Flag historical ghost NO_ITEMS rows so they stop dominating the
30d intake-quality metric.

Problem: pre-2026-07-19, a cross-spider ingestion bug dropped response
bodies, leaving ~10.7K LegacySpiderData rows with `raw_data={}` that got
correctly marked `embedding_text='[NO_ITEMS]'` but represent an
artifact — the extractor is doing its job, the *data* is missing.

Sampling in S2975 showed these ghosts dominate the 30d NO_ITEMS rate
(~89.5% of the 8,183 30d NO_ITEMS rows) while the underlying bug fully
self-resolved by 2026-07-19 (last day with any n>0 was 2026-07-19; before
that: 2026-07-18 n=22, 2026-07-17 n=150, 2026-07-16+ n=200+/day).

This command bumps matching rows to a distinct
`[NO_ITEMS_STALE_EMPTY_RAW]` sentinel so:

  - backfill still skips them (via `BACKFILL_SKIP_SENTINELS` — no risk
    of the next backfill pass re-marking them as `[NO_ITEMS]` and undoing
    the flag);
  - `get_embedding_stats` reports them in a separate `stale_empty_raw_data_total`
    bucket instead of counting them as NO_ITEMS;
  - the operation is reversible (bump back to `[NO_ITEMS]` if we ever
    need to).

Non-destructive; dry-run default.

Usage:
  # dry-run all spiders with the default cutoff (2026-07-19)
  python manage.py cleanup_stale_no_items

  # actually flag them
  python manage.py cleanup_stale_no_items --apply

  # scope to one spider
  python manage.py cleanup_stale_no_items --spider legislation --apply

  # override cutoff (rows with created_at strictly BEFORE this date qualify)
  python manage.py cleanup_stale_no_items --before 2026-07-15 --apply

  # cap the row count (e.g. for staged rollouts)
  python manage.py cleanup_stale_no_items --limit 500 --apply
"""

from datetime import datetime
from datetime import timezone as dt_timezone

from django.core.management.base import BaseCommand, CommandError


DEFAULT_CUTOFF_ISO = '2026-07-19'


class Command(BaseCommand):
    help = (
        'Flag historical ghost NO_ITEMS rows (raw_data={} pre-cutoff) with a '
        'distinct sentinel so they stop distorting the NO_ITEMS metric.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--spider',
            default=None,
            help='Optional spider_name filter (default: all spiders).',
        )
        parser.add_argument(
            '--before',
            default=DEFAULT_CUTOFF_ISO,
            help=(
                'ISO date (YYYY-MM-DD). Rows with created_at strictly BEFORE '
                f'this date qualify. Default: {DEFAULT_CUTOFF_ISO} (empirically '
                'observed bug-resolved date).'
            ),
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually bump the sentinel. Without this flag, dry-run only.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Cap the number of rows flagged (default: no cap).',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import LegacySpiderData
        from core.services.no_items_policy import (
            NO_ITEMS_SENTINEL,
            STALE_EMPTY_SENTINEL,
        )

        try:
            naive = datetime.strptime(options['before'], '%Y-%m-%d')
        except ValueError as exc:
            raise CommandError(
                f"--before must be YYYY-MM-DD, got: {options['before']!r}"
            ) from exc
        cutoff = naive.replace(tzinfo=dt_timezone.utc)

        base_qs = LegacySpiderData.objects.filter(
            embedding__isnull=True,
            embedding_text=NO_ITEMS_SENTINEL,
            raw_data={},
            created_at__lt=cutoff,  # strictly BEFORE
        )
        if options['spider']:
            base_qs = base_qs.filter(spider_name=options['spider'])

        candidate_count = base_qs.count()
        mode = 'APPLY' if options['apply'] else 'DRY RUN'
        scope = options['spider'] or 'all spiders'

        self.stdout.write(
            f"\n=== cleanup_stale_no_items scope={scope} "
            f"before={cutoff.isoformat()} mode={mode} ==="
        )
        self.stdout.write(f'  candidates:  {candidate_count:,}')

        limit = options['limit']
        will_flag_qs = base_qs
        if limit is not None:
            # QuerySet slices don't support .update(); resolve to pk__in.
            pks = list(base_qs.order_by('-created_at').values_list('pk', flat=True)[:limit])
            will_flag_qs = LegacySpiderData.objects.filter(pk__in=pks)
            self.stdout.write(f'  limited to:  {len(pks):,}')

        if not options['apply']:
            self.stdout.write(self.style.WARNING(
                '\n[dry-run] no rows modified. Re-run with --apply to flag.'
            ))
            return

        flagged = will_flag_qs.update(embedding_text=STALE_EMPTY_SENTINEL)
        self.stdout.write(self.style.SUCCESS(f'  flagged:     {flagged:,}'))
        self.stdout.write(
            f"\nNext step: check /api/signals/embedding-coverage/ — the 30d "
            f"no_items_rate should drop by roughly this many rows; the new "
            f"'stale_empty_raw_data_total' bucket exposes them separately."
        )
