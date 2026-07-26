"""
S2974: Re-triage `[NO_ITEMS]` rows against the current `get_searchable_text`.

Problem: rows marked `embedding_text='[NO_ITEMS]'` are excluded from backfill by
design (prevents thrash). When the extractor is improved, existing rows stay
marked forever unless something clears the sentinel.

This command scans a targeted set of `[NO_ITEMS]` rows, recomputes
`get_searchable_text()`, and clears the sentinel only where the new extractor
produces non-empty text. Backfill then picks them up on its next cycle.

Usage:
  # dry-run for one spider (default: legislation)
  python manage.py retriage_no_items --spider legislation

  # actually clear the sentinel
  python manage.py retriage_no_items --spider legislation --apply

  # limit scan window (default: all-time)
  python manage.py retriage_no_items --spider legislation --days 30 --apply
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Re-triage [NO_ITEMS] rows: clear the sentinel where the current extractor now returns text.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--spider',
            required=True,
            help='spider_name to re-triage (e.g. "legislation")',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually clear the sentinel. Without this flag, dry-run only.',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Only consider rows created within the last N days (default: all-time)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Cap the number of rows scanned (default: no cap)',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import LegacySpiderData

        spider = options['spider']
        apply = options['apply']
        days = options['days']
        limit = options['limit']

        qs = LegacySpiderData.objects.filter(
            spider_name=spider,
            embedding__isnull=True,
            embedding_text='[NO_ITEMS]',
        )
        if days is not None:
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=days))
        qs = qs.order_by('-created_at')
        if limit is not None:
            qs = qs[:limit]

        mode = 'APPLY' if apply else 'DRY RUN'
        window = f'{days}d' if days is not None else 'all-time'
        self.stdout.write(f'\n=== retriage_no_items spider={spider} window={window} mode={mode} ===')

        scanned = 0
        would_clear = 0
        still_empty = 0
        cleared = 0

        for row in qs.iterator(chunk_size=200):
            scanned += 1
            text = row.get_searchable_text()
            if text and text.strip():
                would_clear += 1
                if apply:
                    # Clear only the sentinel; backfill will re-embed on next cycle.
                    LegacySpiderData.objects.filter(pk=row.pk).update(embedding_text='')
                    cleared += 1
            else:
                still_empty += 1

        self.stdout.write('')
        self.stdout.write(f'  scanned:      {scanned:,}')
        self.stdout.write(f'  would clear:  {would_clear:,}  (extractor now returns text)')
        self.stdout.write(f'  still empty:  {still_empty:,}  (extractor still returns nothing)')
        if apply:
            self.stdout.write(self.style.SUCCESS(f'  cleared:      {cleared:,}'))
            self.stdout.write('\nNext step: run `make celery-recycle` (or wait for the next '
                              'backfill-spider-embeddings beat tick) so cleared rows re-embed.')
        else:
            self.stdout.write(self.style.WARNING('\n[dry-run] no rows modified. Re-run with --apply to clear.'))
