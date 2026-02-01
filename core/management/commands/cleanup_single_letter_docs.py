"""
Session 893: Cleanup single-letter title documents caused by deliverables string bug.

The bug: ThinkingAgent's LLM sometimes output "deliverables": "summary.json"
instead of "deliverables": ["summary.json"]. When iterating over a string,
each character became a separate document title.

This command finds and deletes those documents.
"""

from django.core.management.base import BaseCommand
from core.models_unified_system import SelfBlog


class Command(BaseCommand):
    help = 'Delete SelfBlog documents with single-letter titles (Session 893 bug fix)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--include-orphaned',
            action='store_true',
            help='Also delete documents with just a stage prefix and no real title',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        include_orphaned = options['include_orphaned']

        # Find documents with single-letter titles after the stage prefix
        bad_docs = []
        for doc in SelfBlog.objects.all():
            title = doc.title or ''
            is_bad = False
            reason = ''

            # Pattern 1: "[Stage X - Name] <single char>"
            if '[Stage ' in title:
                parts = title.split('] ')
                if len(parts) > 1:
                    after_bracket = parts[-1].strip()
                    if len(after_bracket) == 1:
                        is_bad = True
                        reason = f'single letter after stage prefix: {after_bracket!r}'
                    elif include_orphaned and len(after_bracket) == 0:
                        is_bad = True
                        reason = 'empty title after stage prefix'

            # Pattern 2: Just a single character
            elif len(title.strip()) == 1:
                is_bad = True
                reason = f'single character title: {title!r}'

            if is_bad:
                bad_docs.append((doc, reason))

        if not bad_docs:
            self.stdout.write(self.style.SUCCESS('No single-letter title documents found.'))
            return

        self.stdout.write(f'Found {len(bad_docs)} documents to delete:')
        for doc, reason in bad_docs[:50]:
            self.stdout.write(f'  ID {doc.id}: {doc.title!r} ({reason})')

        if len(bad_docs) > 50:
            self.stdout.write(f'  ... and {len(bad_docs) - 50} more')

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nDRY RUN: Would delete {len(bad_docs)} documents. '
                'Run without --dry-run to actually delete.'
            ))
            return

        # Delete the bad documents
        doc_ids = [doc.id for doc, _ in bad_docs]
        deleted_count, _ = SelfBlog.objects.filter(id__in=doc_ids).delete()

        self.stdout.write(self.style.SUCCESS(
            f'\nDeleted {deleted_count} single-letter title documents.'
        ))
