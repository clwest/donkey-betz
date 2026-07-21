"""Session 2864 slate #1 — enrich pre-S2862 HuggingFace items with title/url/description.

Pre-S2862 (before commit fbfe10ff7, 2026-07-21 09:28 CST), `huggingface` sat in
`SPIDER_TARGET_URLS`, routing HF ingestion through `parse_json_api` → `normalize_item`.
`normalize_item`'s generic field_mappings did not map HF Hub API fields
(`modelId`, `pipeline_tag`, `library_name`, `tags`, `downloads`, `likes`)
to `title`/`url`/`description`, so persisted items lack those. The view-layer
workaround at `core/views_spider_intelligence.py:1217-1233` reconstructs the
description at read time, but that pattern is the S2862 Q5.a bimodal-collector
fold surfacing again.

S2862 fixed forward: new HF ingestion routes through `HuggingFaceSpider.fetch_data`
which builds rich items. This command enriches the historical rows so the
view-layer workaround becomes truly dead and can be deleted in the same PR.

Idempotent — item-level guard (`if item.get('title'): skip`) means safe to re-run
on both historical and post-S2862 rich rows.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models_unified_system import LegacySpiderData


_TAG_PREFIX_SKIP = ('dataset:', 'arxiv:', 'region:', 'license:', 'deploy:', 'endpoints_', 'autotrain_')


def _reconstruct_description(item: dict) -> str:
    """Rebuild description in the view-layer workaround format.

    Matches `core/views_spider_intelligence.py:1217-1233` exactly so backfilled
    descriptions are visually identical to what the workaround produced at read
    time.
    """
    desc_parts = []
    if item.get('pipeline_tag'):
        desc_parts.append(f"Task: {item.get('pipeline_tag')}")
    if item.get('library_name'):
        desc_parts.append(f"Library: {item.get('library_name')}")
    tags = item.get('tags') or []
    useful_tags = [t for t in tags[:10] if not any(str(t).startswith(p) for p in _TAG_PREFIX_SKIP)]
    if useful_tags:
        desc_parts.append(f"Tags: {', '.join(useful_tags[:5])}")
    if item.get('downloads'):
        desc_parts.append(f"{item.get('downloads'):,} downloads")
    if item.get('likes'):
        desc_parts.append(f"{item.get('likes'):,} likes")
    return ' | '.join(desc_parts)


def enrich_item(item: dict) -> bool:
    """Enrich a single raw HF item in-place. Returns True if item was mutated.

    Skips items that already have `title` (post-S2862 class-path items + already-backfilled).
    Skips items with no `modelId` and no `id` (unknown shape, defensive).
    """
    if item.get('title'):
        return False
    hf_id = item.get('modelId') or item.get('id')
    if not hf_id:
        return False
    hf_id = str(hf_id)

    item['title'] = hf_id
    if item.get('sdk'):
        item['url'] = f"https://huggingface.co/spaces/{hf_id}"
    else:
        item['url'] = f"https://huggingface.co/{hf_id}"
    item['link'] = item['url']
    desc = _reconstruct_description(item)
    if desc:
        item['description'] = desc
        item['summary'] = desc
    return True


class Command(BaseCommand):
    help = (
        "Enrich pre-S2862 HuggingFace LegacySpiderData rows with title/url/description "
        "on each item so the view-layer workaround can be safely removed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report counts without persisting changes.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Cap the number of rows scanned (0 = all). Useful for sampling before a full run.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Rows per transaction commit (default 100).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        batch_size = options["batch_size"]

        qs = (
            LegacySpiderData.objects
            .filter(spider_name='huggingface')
            .exclude(raw_data__isnull=True)
            .order_by('created_at')
        )
        if limit:
            qs = qs[:limit]

        rows_scanned = 0
        rows_updated = 0
        items_enriched = 0
        items_skipped_has_title = 0
        items_skipped_no_id = 0

        batch = []
        for sd in qs.iterator():
            rows_scanned += 1
            items = sd.raw_data_dict.get('items') or []
            row_changed = False
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get('title'):
                    items_skipped_has_title += 1
                    continue
                if not (item.get('modelId') or item.get('id')):
                    items_skipped_no_id += 1
                    continue
                if enrich_item(item):
                    items_enriched += 1
                    row_changed = True

            if row_changed:
                rows_updated += 1
                if not dry_run:
                    batch.append(sd)
                    if len(batch) >= batch_size:
                        self._commit_batch(batch)
                        batch = []

        if batch and not dry_run:
            self._commit_batch(batch)

        style = self.style.WARNING if dry_run else self.style.SUCCESS
        self.stdout.write(style("=" * 70))
        self.stdout.write(style(f"S2864 HF backfill {'(DRY RUN)' if dry_run else 'COMPLETE'}"))
        self.stdout.write(style("=" * 70))
        self.stdout.write(f"  rows_scanned:            {rows_scanned}")
        self.stdout.write(f"  rows_updated:            {rows_updated}")
        self.stdout.write(f"  items_enriched:          {items_enriched}")
        self.stdout.write(f"  items_skipped_has_title: {items_skipped_has_title}")
        self.stdout.write(f"  items_skipped_no_id:     {items_skipped_no_id}")

    def _commit_batch(self, batch):
        with transaction.atomic():
            for sd in batch:
                sd.save(update_fields=['raw_data'])
