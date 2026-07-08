"""Cycle 1A KFI-1 (ADR-0110) — Deliverable → Document mirror mgmt command.

Historical-compatibility path (F2 refined, Chris directive 2026-07-08):
the live signal fires ONLY on future canonical
``deliverable_type='ratification_record'`` records. This command
compatibly handles historical records that were stored with
``deliverable_type='document'`` but titled ``RATIFICATION_*`` — the
5+ pre-KFI-1 records that predate the signal wiring.

Flags:
  --ratification-record-id <uuid>: process a single record (either
      canonical or historical).
  --all-historical: enumerate every workspace deliverable matching
      ``deliverable_type IN ('ratification_record','document')`` AND
      ``title__startswith='RATIFICATION_'`` and mirror each.
  --deliverable-id <uuid>: explicit target override (combines with
      --ratification-record-id for manual recovery per ADR §2.4 when
      body extraction fails).
  --purge-orphaned: delete mirror Documents whose source Deliverable
      no longer exists (recovery mechanism per ADR §2.5).
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Deliverable
from core.tasks import mirror_deliverable_to_document


class Command(BaseCommand):
    help = 'Mirror a workspace Deliverable into a content.Document (KFI-1 backfill).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ratification-record-id',
            dest='ratification_record_id',
            default=None,
            help='UUID of the ratification_record deliverable to process.',
        )
        parser.add_argument(
            '--deliverable-id',
            dest='deliverable_id',
            default=None,
            help='UUID of the target deliverable (bypasses body extraction).',
        )
        parser.add_argument(
            '--all-historical',
            dest='all_historical',
            action='store_true',
            help=(
                'Enumerate historical RATIFICATION_* records (both '
                'ratification_record- and document-typed) and mirror each.'
            ),
        )
        parser.add_argument(
            '--workspace-id',
            dest='workspace_id',
            default=None,
            help=(
                'Restrict --all-historical to a specific workspace UUID. '
                'Optional; if omitted, all workspaces are enumerated.'
            ),
        )
        parser.add_argument(
            '--purge-orphaned',
            dest='purge_orphaned',
            action='store_true',
            help='Delete mirror Documents whose source Deliverable is gone.',
        )

    def handle(self, *args, **options):
        rr_id = options.get('ratification_record_id')
        target_id = options.get('deliverable_id')
        all_historical = options.get('all_historical')
        workspace_id = options.get('workspace_id')
        purge_orphaned = options.get('purge_orphaned')

        if purge_orphaned:
            self._purge_orphaned()
            return

        if all_historical:
            self._process_all_historical(workspace_id)
            return

        if not rr_id:
            raise CommandError(
                'Provide --ratification-record-id, --all-historical, or '
                '--purge-orphaned.'
            )

        self._process_one(rr_id, target_id)

    def _process_one(self, ratification_record_id, target_deliverable_id=None):
        result = mirror_deliverable_to_document(
            ratification_record_id=ratification_record_id,
            target_deliverable_id=target_deliverable_id,
        )
        self.stdout.write(str(result))

    def _process_all_historical(self, workspace_id):
        # Broader-than-signal filter: historical records may have
        # deliverable_type='document' but a canonical RATIFICATION_ title.
        qs = Deliverable.objects.filter(
            title__startswith='RATIFICATION_',
            deliverable_type__in=('ratification_record', 'document'),
        )
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)

        count = qs.count()
        self.stdout.write(f'Enumerating {count} historical RATIFICATION_* records.')

        for rr in qs.iterator():
            result = mirror_deliverable_to_document(
                ratification_record_id=str(rr.id),
            )
            self.stdout.write(
                f'  rr={rr.id} title={rr.title[:60]!r} -> {result.get("status")}'
            )

    def _purge_orphaned(self):
        from content.models import Document

        # Enumerate mirror Documents whose source_reference no longer
        # resolves to a live Deliverable.
        candidates = Document.objects.filter(source='workspace')
        deleted = 0
        skipped = 0
        for doc in candidates.iterator():
            try:
                Deliverable.objects.get(id=doc.source_reference)
                skipped += 1
            except (Deliverable.DoesNotExist, ValueError):
                doc.delete()
                deleted += 1

        self.stdout.write(
            f'purge_orphaned: deleted={deleted} skipped={skipped}'
        )
