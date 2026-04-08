"""
One-time triage of the spider embedding backlog.

Problem: 86,500+ SpiderData records have no embedding. Most are duplicate
spider runs (same content fetched every 15-30 min) or noise spiders
(weather, GIFs, stock photos) with zero intelligence value.

Strategy:
  1. NOISE spiders → mark [NO_ITEMS] (never embed)
  2. STALE SNAPSHOT spiders (odds/quotes) → keep newest per day, mark rest
  3. VALUABLE spiders → keep newest per spider per day, mark rest
  4. Remaining survivors get embedded by the normal backfill task

Usage:
  python manage.py triage_spider_embeddings              # dry run
  python manage.py triage_spider_embeddings --apply       # do it
"""

from django.core.management.base import BaseCommand
from django.db.models import Max
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta


# Zero intelligence value — no searchable text or irrelevant content
NOISE_SPIDERS = {
    'openmeteo',         # weather forecasts, 0 searchable text
    'giphy',             # GIF titles ("Dog Hello GIF")
    'unsplash',          # stock photo descriptions
    'discord_training',  # training data blobs, 0 searchable text
}

# Time-sensitive snapshots — stale within minutes/hours of collection
STALE_SNAPSHOT_SPIDERS = {
    'theodds',    # sports odds snapshots
    'finnhub',    # stock price quotes
    'coingecko',  # crypto price snapshots
    'kalshi',     # prediction market prices
}


class Command(BaseCommand):
    help = 'Triage spider embedding backlog: mark noise/dupes as [NO_ITEMS], keep best record per spider-day'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually mark records. Without this flag, dry-run only.',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import SpiderData

        apply = options['apply']
        mode = 'APPLY' if apply else 'DRY RUN'
        self.stdout.write(f'\n=== Spider Embedding Triage ({mode}) ===\n')

        # Scope: unembedded records older than 7 days, not already marked
        backlog = SpiderData.objects.filter(
            embedding__isnull=True,
            created_at__lt=timezone.now() - timedelta(hours=168),
        ).exclude(embedding_text='[NO_ITEMS]')

        total = backlog.count()
        self.stdout.write(f'Backlog: {total:,} unembedded records older than 7 days\n')

        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nothing to triage.'))
            return

        marked_total = 0

        # ── Step 1: Noise spiders ────────────────────────────────────────
        self.stdout.write(f'\n── Step 1: Noise Spiders ──')
        noise_qs = backlog.filter(spider_name__in=NOISE_SPIDERS)
        noise_count = noise_qs.count()
        self.stdout.write(f'  Spiders: {", ".join(sorted(NOISE_SPIDERS))}')
        self.stdout.write(f'  Records to mark [NO_ITEMS]: {noise_count:,}')

        if apply and noise_count:
            marked = noise_qs.update(embedding_text='[NO_ITEMS]')
            marked_total += marked
            self.stdout.write(self.style.SUCCESS(f'  ✓ Marked {marked:,}'))

        # ── Step 2: Stale snapshot spiders ───────────────────────────────
        self.stdout.write(f'\n── Step 2: Stale Snapshot Spiders ──')
        stale_qs = backlog.filter(spider_name__in=STALE_SNAPSHOT_SPIDERS)
        stale_count = stale_qs.count()
        self.stdout.write(f'  Spiders: {", ".join(sorted(STALE_SNAPSHOT_SPIDERS))}')
        self.stdout.write(f'  Total records: {stale_count:,}')

        stale_keep, stale_mark = self._dedup_spider_days(
            backlog, STALE_SNAPSHOT_SPIDERS, apply
        )
        marked_total += stale_mark

        # ── Step 3: Valuable spiders (everything else) ───────────────────
        self.stdout.write(f'\n── Step 3: Valuable Spiders (dedup) ──')
        valuable_spiders = set(
            backlog.exclude(spider_name__in=NOISE_SPIDERS)
            .exclude(spider_name__in=STALE_SNAPSHOT_SPIDERS)
            .values_list('spider_name', flat=True)
            .distinct()
        )
        valuable_count = backlog.filter(spider_name__in=valuable_spiders).count()
        self.stdout.write(f'  Spiders: {len(valuable_spiders)} unique')
        self.stdout.write(f'  Total records: {valuable_count:,}')

        valuable_keep, valuable_mark = self._dedup_spider_days(
            backlog, valuable_spiders, apply
        )
        marked_total += valuable_mark

        # ── Summary ──────────────────────────────────────────────────────
        survivors = total - (noise_count + stale_mark + valuable_mark)
        # In dry-run, calculate expected survivors
        if not apply:
            survivors = stale_keep + valuable_keep

        self.stdout.write(f'\n{"=" * 50}')
        self.stdout.write(f'  SUMMARY ({mode})')
        self.stdout.write(f'{"=" * 50}')
        self.stdout.write(f'  Backlog total:          {total:>8,}')
        self.stdout.write(f'  Noise (mark skip):      {noise_count:>8,}')
        self.stdout.write(f'  Stale dupes (mark skip):{stale_mark if apply else (stale_count - stale_keep):>8,}')
        self.stdout.write(f'  Valuable dupes (mark):  {valuable_mark if apply else (valuable_count - valuable_keep):>8,}')
        self.stdout.write(f'  ─────────────────────────────────')
        self.stdout.write(self.style.SUCCESS(
            f'  SURVIVORS to embed:     {survivors:>8,}'
        ))

        est_tokens = survivors * 200  # ~200 tokens avg per record
        est_cost = est_tokens / 1_000_000 * 0.02
        est_minutes = survivors / 500 * 15  # 500/batch every 15 min
        self.stdout.write(f'\n  Estimated embedding cost: ~${est_cost:.2f}')
        self.stdout.write(f'  Estimated backfill time:  ~{est_minutes:.0f} min ({est_minutes/60:.1f} hrs)')

        if not apply:
            self.stdout.write(self.style.WARNING(
                f'\n  This was a dry run. Use --apply to execute.'
            ))

    def _dedup_spider_days(self, backlog, spider_names, apply):
        """
        For each spider in spider_names, keep the newest record per calendar day.
        Mark all others as [NO_ITEMS].

        Returns (keep_count, mark_count).
        """
        from core.models_unified_system import SpiderData

        scoped = backlog.filter(spider_name__in=spider_names)

        # UUID PK — can't use Max('id'). Use DISTINCT ON + latest created_at.
        # Get the newest created_at per (spider_name, day), then resolve to IDs.
        newest_per_day = (
            scoped.annotate(day=TruncDate('created_at'))
            .values('spider_name', 'day')
            .annotate(newest_ts=Max('created_at'))
        )

        # Collect the keeper IDs by matching spider_name + created_at
        keep_ids = set()
        for row in newest_per_day:
            record = scoped.filter(
                spider_name=row['spider_name'],
                created_at=row['newest_ts'],
            ).values_list('id', flat=True).first()
            if record:
                keep_ids.add(record)

        total_scoped = scoped.count()
        keep_count = len(keep_ids)
        mark_count = total_scoped - keep_count

        self.stdout.write(f'  Keep (newest per spider-day): {keep_count:,}')
        self.stdout.write(f'  Mark as [NO_ITEMS]:           {mark_count:,}')

        if apply and mark_count > 0:
            # Mark in batches to avoid huge IN queries
            to_mark = scoped.exclude(id__in=keep_ids)
            batch_size = 5000
            total_marked = 0
            while True:
                batch_ids = list(to_mark.values_list('id', flat=True)[:batch_size])
                if not batch_ids:
                    break
                marked = SpiderData.objects.filter(id__in=batch_ids).update(
                    embedding_text='[NO_ITEMS]'
                )
                total_marked += marked
                self.stdout.write(f'    ... marked {total_marked:,}/{mark_count:,}')

            self.stdout.write(self.style.SUCCESS(f'  ✓ Marked {total_marked:,}'))
            return keep_count, total_marked

        return keep_count, 0
