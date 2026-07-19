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

S2829 stop-writer hardening (Chris + Rigby joint SIGN 2026-07-19):
    At S2829 open, sanity checks re-surfaced 870 rows in the same drift
    class after S2828 close asserted 0 mismatches. The bulk-update
    signature (866 rows sharing microsecond-identical updated_at =
    2026-07-19T03:17:40.403387 UTC) matched THIS command's
    fixed-timestamp `.update()` shape at the mid-flight `_index.json`
    moment. Rigby SIGN D6.1: writer must not be reachable unattended.
    D6.2: snapshot `_index.json` at start so mid-flight regeneration is
    detectable. This module implements both.

Execution contract (post-S2829):
    python manage.py backfill_document_status_from_docs_index --dry-run
    # verify counts match investigation
    python manage.py backfill_document_status_from_docs_index --apply
    # execute — --apply is REQUIRED for writes since S2829
    python manage.py backfill_document_status_from_docs_index --dry-run
    # must report zero remaining mismatches

A bare invocation (`... backfill_document_status_from_docs_index` with
neither --dry-run nor --apply) exits with an error. This closes the
"unattended manual bulk sweep at the wrong _index.json moment" writer
class that caused the S2829 recurrence.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
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
            '--apply',
            action='store_true',
            help=(
                'Required for writes. S2829 stop-writer guard: prevents '
                'unattended bulk sweeps. Bare invocations (no --dry-run, no '
                '--apply) exit with an error.'
            ),
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Cap the number of rows fixed (for staged rollouts).',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        apply = options['apply']
        limit = options.get('limit')

        # S2829 stop-writer guard: must pick a mode explicitly.
        if dry_run and apply:
            raise CommandError(
                "--dry-run and --apply are mutually exclusive. Pick one."
            )
        if not dry_run and not apply:
            raise CommandError(
                "Explicit mode required: pass --dry-run to preview or --apply "
                "to write. Bare invocations rejected since S2829 to prevent "
                "unattended bulk sweeps at mid-flight _index.json moments."
            )

        index_path = Path(settings.BASE_DIR) / 'docs' / '_index.json'
        if not index_path.exists():
            self.stderr.write(self.style.ERROR(
                f"docs/_index.json not found at {index_path}"
            ))
            return

        # S2829 snapshot: read _index.json bytes ONCE, hash them, then parse.
        # Any subsequent regeneration during this command's run is invisible
        # to us — we operate on the frozen snapshot. Log the hash so
        # divergence between what backfill saw and current disk is
        # detectable in post-hoc audits.
        index_bytes = index_path.read_bytes()
        index_hash = hashlib.sha256(index_bytes).hexdigest()
        index = json.loads(index_bytes)

        docs_by_path = {d['path']: d for d in index.get('documents', [])}
        self.stdout.write(
            f"docs/_index.json snapshot: {len(docs_by_path)} entries "
            f"(sha256={index_hash[:16]}...)"
        )

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
