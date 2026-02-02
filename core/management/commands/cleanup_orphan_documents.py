"""
Session 906: Clean up orphan research brief documents.

Problem: Many duplicate research briefs were generated but never linked to
InitiativeStages, creating clutter:
- 236/351 research docs are orphans (not linked to any stage)
- 25 copies of "root_cause_report", 10 copies of "root_cause_summary", etc.

This script safely removes orphan documents while preserving linked ones.

Usage:
    # Dry run - show what would be deleted
    python manage.py cleanup_orphan_documents

    # Actually delete orphans
    python manage.py cleanup_orphan_documents --delete

    # Target specific title patterns
    python manage.py cleanup_orphan_documents --delete --pattern="root_cause"
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up orphan research brief documents not linked to any InitiativeStage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete orphan documents (default is dry run)',
        )
        parser.add_argument(
            '--pattern',
            type=str,
            default=None,
            help='Only process documents matching this title pattern',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Maximum documents to process (default: 500)',
        )
        parser.add_argument(
            '--keep-newest',
            action='store_true',
            help='For duplicate titles, keep the newest one even if orphan',
        )

    def handle(self, *args, **options):
        from core.models import SelfBlog
        from core.models_document_registry import InitiativeStage

        delete = options['delete']
        pattern = options.get('pattern')
        limit = options['limit']
        keep_newest = options['keep_newest']

        self.stdout.write(self.style.NOTICE(
            f"{'DELETING' if delete else 'DRY RUN'}: Finding orphan research documents"
        ))

        # Get all document IDs that ARE linked to stages
        linked_doc_ids = set(
            InitiativeStage.objects.exclude(document__isnull=True)
            .values_list('document_id', flat=True)
        )
        self.stdout.write(f"Documents linked to stages: {len(linked_doc_ids)}")

        # Find research-related documents
        research_docs = SelfBlog.objects.filter(
            title__icontains='Research'
        )

        if pattern:
            research_docs = research_docs.filter(title__icontains=pattern)
            self.stdout.write(f"Filtering by pattern: '{pattern}'")

        research_docs = research_docs.order_by('-created_at')[:limit]

        total_docs = research_docs.count()
        self.stdout.write(f"Total research documents to analyze: {total_docs}")

        # Categorize documents
        orphan_docs = []
        linked_docs = []

        for doc in research_docs:
            if doc.id in linked_doc_ids:
                linked_docs.append(doc)
            else:
                orphan_docs.append(doc)

        self.stdout.write(f"\nOrphan documents (not linked to any stage): {len(orphan_docs)}")
        self.stdout.write(f"Linked documents (attached to stages): {len(linked_docs)}")

        # If keep_newest, identify which orphans to keep
        keep_ids = set()
        if keep_newest:
            # Group by title, keep newest per title
            title_groups = {}
            for doc in orphan_docs:
                title = doc.title
                if title not in title_groups:
                    title_groups[title] = doc
                elif doc.created_at > title_groups[title].created_at:
                    title_groups[title] = doc

            keep_ids = {doc.id for doc in title_groups.values()}
            self.stdout.write(f"Keeping newest orphan per title: {len(keep_ids)}")

        # Show duplicate summary
        self.stdout.write(self.style.WARNING("\n--- Duplicate Title Summary ---"))
        title_counts = {}
        for doc in orphan_docs:
            title_counts[doc.title] = title_counts.get(doc.title, 0) + 1

        sorted_titles = sorted(title_counts.items(), key=lambda x: -x[1])[:15]
        for title, count in sorted_titles:
            if count > 1:
                self.stdout.write(f"  {count}x: {title[:60]}")

        # Process deletions
        deleted_count = 0
        skipped_count = 0
        kept_count = 0

        self.stdout.write(self.style.WARNING("\n--- Processing Orphans ---"))

        for doc in orphan_docs:
            if doc.id in keep_ids:
                kept_count += 1
                if not delete:
                    self.stdout.write(f"KEEP (newest): {doc.title[:50]}")
                continue

            if delete:
                try:
                    doc_title = doc.title[:50]
                    doc.delete()
                    deleted_count += 1
                    if deleted_count <= 10:  # Show first 10
                        self.stdout.write(self.style.SUCCESS(f"DELETED: {doc_title}"))
                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.ERROR(f"ERROR: {doc.title[:50]} - {e}"))
            else:
                deleted_count += 1
                if deleted_count <= 20:  # Show first 20 in dry run
                    self.stdout.write(f"WOULD DELETE: {doc.title[:50]}")

        self.stdout.write(self.style.NOTICE("\n--- Summary ---"))
        self.stdout.write(self.style.SUCCESS(
            f"{'Deleted' if delete else 'Would delete'}: {deleted_count}"
        ))
        if keep_newest:
            self.stdout.write(f"Kept (newest per title): {kept_count}")
        self.stdout.write(f"Linked (preserved): {len(linked_docs)}")
        if skipped_count:
            self.stdout.write(self.style.ERROR(f"Errors: {skipped_count}"))

        # Show space savings estimate
        if not delete:
            self.stdout.write(self.style.NOTICE(
                f"\nTo actually delete, run with --delete flag"
            ))
