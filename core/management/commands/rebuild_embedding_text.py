"""
S2977: Re-extract `embedding_text` for existing rows using the CURRENT
`get_searchable_text()` output, without touching the stored embedding vector.

Problem: when the extractor (or an upstream spider) is fixed so that
`get_searchable_text()` returns more/different text than before, existing
rows keep their old (stale) `embedding_text`. The user-facing Feed Explorer
keyword search hits `embedding_text__icontains` (see
`core/services/spider_feed.query_spider_feed`), so stale text = stale hits.

This command scans a bounded window, recomputes `get_searchable_text()`,
and updates `embedding_text` only where the new value differs and is
non-empty. It never touches the `embedding` vector column — the stored
vector remains what it was (which is fine: `spider_semantic_search.semantic_search`
regenerates query/candidate embeddings on-the-fly from `raw_data`, so no
real search path depends on the persisted vector matching the current text).

Non-destructive; dry-run default; bounded window required (default 7d);
prints a diff sample so the operator can eyeball the shape of the change.

Usage:
  # dry-run 7d for sec_edgar (default window)
  python manage.py rebuild_embedding_text --spider sec_edgar

  # apply
  python manage.py rebuild_embedding_text --spider sec_edgar --apply

  # scope wider
  python manage.py rebuild_embedding_text --spider sec_edgar --days 30 --apply

  # cap the row count (staged rollout)
  python manage.py rebuild_embedding_text --spider sec_edgar --limit 50 --apply
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Re-extract embedding_text via current get_searchable_text() without touching vectors.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--spider',
            required=True,
            help='spider_name to rebuild (e.g. "sec_edgar")',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually update rows. Without this flag, dry-run only.',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Only consider rows created within the last N days (default: 7)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Cap the number of rows scanned (default: no cap)',
        )

    @staticmethod
    def _extract_text(row) -> str:
        """Return the current get_searchable_text output, spider-aware.

        For sec_edgar, apply the same form_type round-robin the fixed spider
        now uses at fetch time — otherwise pre-fix rows (raw_data stored in
        filed_at desc order) would re-extract to the same 8K-dominated text
        as before, and Path B (refresh embedding_text without re-embedding)
        would be a no-op for existing rows.
        """
        if row.spider_name != 'sec_edgar':
            return row.get_searchable_text()

        from ai_core.spiders.specialized.sec_spider import SECSpider
        from core.models_unified_system import LegacySpiderData

        raw = row.raw_data_dict
        items = raw.get('items', [])
        if not isinstance(items, list) or not items:
            return row.get_searchable_text()

        interleaved = SECSpider._interleave_by_form_type(items)
        texts = []
        for item in interleaved[:20]:
            if not isinstance(item, dict):
                continue
            text = LegacySpiderData._extract_item_text(item)
            if text:
                texts.append(text)
        return "\n".join(texts)[:4000]

    def handle(self, *args, **options):
        from core.models_unified_system import LegacySpiderData
        from core.services.no_items_policy import BACKFILL_SKIP_SENTINELS

        spider = options['spider']
        apply = options['apply']
        days = options['days']
        limit = options['limit']

        cutoff = timezone.now() - timedelta(days=days)
        # Only touch rows that already have SOME embedding_text (i.e. were
        # embedded / triaged). Skip sentinels — cleanup_stale_no_items /
        # retriage_no_items own those. Skip rows with no embedding_text at
        # all — those are the pending_eligible backfill queue, not our lane.
        qs = (
            LegacySpiderData.objects
            .filter(spider_name=spider, created_at__gte=cutoff)
            .exclude(embedding_text__isnull=True)
            .exclude(embedding_text='')
            .exclude(embedding_text__in=BACKFILL_SKIP_SENTINELS)
            .order_by('-created_at')
        )
        if limit is not None:
            qs = qs[:limit]

        mode = 'APPLY' if apply else 'DRY RUN'
        self.stdout.write(f'\n=== rebuild_embedding_text spider={spider} window={days}d mode={mode} ===')

        scanned = 0
        unchanged = 0
        would_update = 0
        updated = 0
        would_empty = 0
        samples = []

        for row in qs.iterator(chunk_size=200):
            scanned += 1
            raw_text = self._extract_text(row)
            if not raw_text or not raw_text.strip():
                # The new extractor returns nothing — leaving embedding_text
                # unchanged is safer than overwriting with empty (would look
                # like the row lost its text).
                would_empty += 1
                continue
            # Match backfill semantics: `generate_entry_embedding` stores
            # `text[:1000]` (core/services/spider_semantic_search.py:419).
            # Truncating here keeps existing-row text consistent with what a
            # fresh embed would produce, so future backfill / re-embed cycles
            # don't churn.
            new_text = raw_text[:1000]
            if new_text == row.embedding_text:
                unchanged += 1
                continue
            would_update += 1
            if len(samples) < 3:
                samples.append({
                    'id': str(row.id),
                    'old_len': len(row.embedding_text or ''),
                    'new_len': len(new_text),
                    'old_head': (row.embedding_text or '')[:120],
                    'new_head': new_text[:120],
                })
            if apply:
                LegacySpiderData.objects.filter(pk=row.pk).update(embedding_text=new_text)
                updated += 1

        self.stdout.write('')
        self.stdout.write(f'  scanned:       {scanned:,}')
        self.stdout.write(f'  unchanged:     {unchanged:,}  (new text == old text)')
        self.stdout.write(f'  would update:  {would_update:,}  (new text differs and is non-empty)')
        self.stdout.write(f'  would empty:   {would_empty:,}  (new extractor returns nothing — SKIPPED)')

        if samples:
            self.stdout.write('\n  diff samples (up to 3):')
            for s in samples:
                self.stdout.write(
                    f'    id={s["id"]}  '
                    f'{s["old_len"]}ch -> {s["new_len"]}ch'
                )
                self.stdout.write(f'      old: {s["old_head"]!r}')
                self.stdout.write(f'      new: {s["new_head"]!r}')

        if apply:
            self.stdout.write(self.style.SUCCESS(f'\n  updated: {updated:,}'))
        else:
            self.stdout.write(self.style.WARNING('\n[dry-run] no rows modified. Re-run with --apply.'))
