"""Session 1234 D10 — backfill the D9 enrichment fields on existing Documents.

Session 1234 D9 wired `sync_docs_index_to_documents` to populate the
type-aware retrieval enrichment fields (`category`, `tags`,
`document_class`, `is_pinned`, `retrieval_boost`) for newly synced
docs. But D9 only fires on create or content-change updates — the
2,732 docs synced earlier in Session 1234 (and the 912 from before)
still have flat values (`document_class='reference'`, `category=''`,
`tags=[]`, `is_pinned=False`, `retrieval_boost` at default).

D10 backfills those existing rows by:

1. Reading `docs/_index.json` (sole source of truth for frontmatter)
2. For each entry, finding the matching `Document` row by `file_path`
3. Applying the same `_enrichment_fields()` helper D9 uses
4. Updating only the 5 enrichment fields via `.save(update_fields=...)`

Idempotent: running twice produces the same end state. Use `--dry-run`
to preview without mutating. Cost: ~0 (no embeddings regenerated; no
LLM calls; pure DB UPDATE on ~2,700 rows).

Usage::

    python manage.py backfill_docs_enrichment --dry-run
    python manage.py backfill_docs_enrichment
    python manage.py backfill_docs_enrichment --index PATH
    python manage.py backfill_docs_enrichment --limit 100
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand

from content.models import Document
from core.management.commands.sync_docs_index_to_documents import (
    Command as SyncCommand,
)


class Command(BaseCommand):
    help = (
        "Backfill D9 enrichment fields (category/tags/document_class/"
        "is_pinned/retrieval_boost) on existing Document rows by replaying "
        "docs/_index.json against the D9 sync helper."
    )

    # The fields D9 populates. Listed here so the save() call below uses
    # update_fields= to skip post_save signal cascades on unrelated fields.
    _ENRICHMENT_FIELDS = (
        'category', 'tags', 'document_class', 'is_pinned', 'retrieval_boost',
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report what would change; no DB writes',
        )
        parser.add_argument(
            '--index',
            default=None,
            help='Alt path to _index.json (default: docs/_index.json)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Backfill only the first N matched rows',
        )

    def handle(self, *args, **options):
        dry_run: bool = options['dry_run']
        limit: Optional[int] = options['limit']

        index_path = options['index']
        if index_path is None:
            index_path = Path(settings.BASE_DIR) / 'docs' / '_index.json'
        else:
            index_path = Path(index_path)

        if not index_path.exists():
            self.stderr.write(
                self.style.ERROR(f'Index file not found: {index_path}')
            )
            return

        with open(index_path) as f:
            payload = json.load(f)
        documents = payload.get('documents', [])
        self.stdout.write(f'Loaded {len(documents)} entries from {index_path}')

        # Share D9's enrichment helper — single source of truth for the
        # field-derivation logic. The SyncCommand class is itself a
        # `BaseCommand`, but the helper is a pure function over doc_data
        # so no DB / I/O concerns.
        sync_helper = SyncCommand()._enrichment_fields  # type: ignore[attr-defined]

        stats = {
            'matched': 0,
            'updated': 0,
            'unchanged': 0,
            'missing_in_db': 0,
        }

        processed = 0
        for doc_data in documents:
            path = doc_data.get('path', '')
            if not path:
                continue

            existing = Document.objects.filter(file_path=path).first()
            if existing is None:
                stats['missing_in_db'] += 1
                continue

            stats['matched'] += 1

            target = sync_helper(doc_data)
            changed = []
            for field in self._ENRICHMENT_FIELDS:
                current = getattr(existing, field)
                desired = target[field]
                # Normalize tag-list comparisons: a saved []` may equal
                # the desired sorted [] but order doesn't matter for tags.
                if field == 'tags':
                    current_sorted = sorted(current or [])
                    desired_sorted = sorted(desired or [])
                    if current_sorted != desired_sorted:
                        changed.append(field)
                else:
                    if current != desired:
                        changed.append(field)

            if not changed:
                stats['unchanged'] += 1
                continue

            if not dry_run:
                for field in changed:
                    setattr(existing, field, target[field])
                existing.save(update_fields=list(changed))

            stats['updated'] += 1
            processed += 1

            if processed % 250 == 0:
                self.stdout.write(f'  Processed {processed} updates...')

            if limit is not None and processed >= limit:
                self.stdout.write(f'  Hit --limit={limit}; stopping early.')
                break

        verb = 'WOULD update' if dry_run else 'Updated'
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS('DRY RUN COMPLETE' if dry_run else 'BACKFILL COMPLETE')
        )
        self.stdout.write('=' * 50)
        self.stdout.write(f"  Matched (in DB):  {stats['matched']}")
        self.stdout.write(f"  {verb}:           {stats['updated']}")
        self.stdout.write(f"  Unchanged:        {stats['unchanged']}")
        self.stdout.write(f"  Missing in DB:    {stats['missing_in_db']}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\nRun without --dry-run to apply.'
                )
            )
