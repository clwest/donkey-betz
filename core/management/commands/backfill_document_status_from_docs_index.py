"""S2826 metadata restoration — backfill Document.status from docs/_index.json.

Chris D-verdict 2026-07-19 (S2826 D1, 1A + 2A): the Phase-0.5 retrieval
failure (0/16 strict top-1 hits) traced not to embedding quality, semantic
similarity, authority weighting, or ranking composition, but to a
synchronization defect in `sync_docs_index_to_documents.py` — the update
path refreshes 12 fields but never `Document.status`. Docs that started
their sync lifecycle as `superseded` (→ ARCHIVED) and were later promoted
to `active` in the source stayed ARCHIVED forever in the DB, hiding them
from every default-mode retrieval call (`include_superseded=False` filter).

Root-cause investigation established:
- 870 rows with source=`active` but DB=`archived` (main drift class)
- 6 rows with source=`draft` but DB=`processed`
- 5 rows with source=`draft` but DB=`failed`
- 0 rows in the reverse direction (confirms one-way defect signature)
- 13 rows in DB not in docs/_index.json (separate concern; out of scope
  per Chris D6)

This command is the idempotent restoration side of the S2826 repair. It
must ship in the same PR as the sync command fix (Chris D2) so there is
no production window where restored metadata can immediately re-drift.

Execution contract (per Chris D1):
    python manage.py backfill_document_status_from_docs_index --dry-run
    # verify counts match investigation
    python manage.py backfill_document_status_from_docs_index
    # execute
    python manage.py backfill_document_status_from_docs_index --dry-run
    # must report zero remaining mismatches
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from content.models import ContentStatus, Document


# Mirrors STATUS_MAPPING in sync_docs_index_to_documents.py. Kept in sync
# with that source of truth — if sync mapping changes, this must change too.
STATUS_MAP = {
    'active': ContentStatus.PROCESSED,
    'superseded': ContentStatus.ARCHIVED,
    'deprecated': ContentStatus.ARCHIVED,
    'draft': ContentStatus.PENDING,
}


class Command(BaseCommand):
    help = (
        "S2826 — reconcile Document.status with docs/_index.json ground truth. "
        "Fixes the sync-defect drift where the update path never refreshed status. "
        "Ships in the same PR as the sync command fix."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report mismatches without writing changes.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Cap the number of rows fixed (for staged rollouts).',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options.get('limit')

        index_path = Path(settings.BASE_DIR) / 'docs' / '_index.json'
        if not index_path.exists():
            self.stderr.write(self.style.ERROR(
                f"docs/_index.json not found at {index_path}"
            ))
            return

        with open(index_path) as f:
            index = json.load(f)

        docs_by_path = {d['path']: d for d in index.get('documents', [])}
        self.stdout.write(f"docs/_index.json loaded: {len(docs_by_path)} entries")

        # Walk every Document row; compare against index truth.
        mismatches = Counter()
        planned_updates: list[tuple] = []  # (doc_id, file_path, from_status, to_status)
        docs_not_in_index = 0
        total_examined = 0

        # Only fields we actually need — keeps memory bounded on ~3k rows.
        for doc in Document.objects.all().only('id', 'file_path', 'status').iterator():
            total_examined += 1
            source = docs_by_path.get(doc.file_path)
            if not source:
                docs_not_in_index += 1
                continue
            src_status = (source.get('status') or 'active').strip().lower()
            expected = STATUS_MAP.get(src_status, ContentStatus.PROCESSED)
            if doc.status != expected:
                mismatches[(src_status, doc.status, str(expected))] += 1
                planned_updates.append((doc.id, doc.file_path, doc.status, expected))

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("MISMATCH INVENTORY")
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Total Document rows examined: {total_examined}")
        self.stdout.write(f"  Rows in docs/_index.json:     {total_examined - docs_not_in_index}")
        self.stdout.write(
            f"  Rows NOT in docs/_index.json: {docs_not_in_index} "
            f"(out of scope per Chris D6)"
        )
        self.stdout.write(f"  Total mismatches:             {sum(mismatches.values())}")
        self.stdout.write("")
        self.stdout.write("  Breakdown (src_index_status → db_status, expected):")
        for (src, actual, expected), n in sorted(
            mismatches.items(), key=lambda kv: -kv[1]
        ):
            self.stdout.write(
                f"    src={src!r:12s} actual={actual!r:12s} → expected={expected}: "
                f"{n:5d} rows"
            )

        if dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING(
                "DRY RUN — no writes performed. Re-run without --dry-run to execute."
            ))
            return

        # Execute restoration inside a single transaction. update_fields
        # limited to status + updated_at so unrelated column drift is
        # impossible from this command.
        if not planned_updates:
            self.stdout.write(self.style.SUCCESS(
                "Zero mismatches — metadata layer is already correct."
            ))
            return

        if limit is not None and len(planned_updates) > limit:
            self.stdout.write(self.style.WARNING(
                f"--limit={limit} applied — restricting to first {limit} of "
                f"{len(planned_updates)} planned updates."
            ))
            planned_updates = planned_updates[:limit]

        self.stdout.write("")
        self.stdout.write("Executing restoration...")

        applied = 0
        now = timezone.now()
        with transaction.atomic():
            for doc_id, file_path, from_status, to_status in planned_updates:
                Document.objects.filter(id=doc_id).update(
                    status=to_status,
                    updated_at=now,
                )
                applied += 1

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("RESTORATION COMPLETE"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Rows updated: {applied}")
        self.stdout.write("")
        self.stdout.write(
            "Chris D1 next step: re-run this command with --dry-run. "
            "Zero remaining mismatches confirms restoration."
        )
