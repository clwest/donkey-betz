"""
Session 912: Fix Stuck Initiative Documents

Management command to fix documents that are stuck showing "Insufficient Data"
even though their research has completed or their content shows completion.

The problem: Documents were created with "⚠️ Insufficient Data" markers, and when
research completed, the markers weren't updated. This causes:
1. UI shows "Awaiting Data Collection" banner
2. Auto-progression blocks on "insufficient data" text check

Usage:
    python manage.py fix_stuck_initiatives --dry-run
    python manage.py fix_stuck_initiatives --fix
"""

import logging
from django.core.management.base import BaseCommand
from django.db.models import Q

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix stuck initiative documents that have contradictory data status markers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually fix the stuck documents'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each document'
        )

    def handle(self, *args, **options):
        from core.models_unified_system import SelfBlog
        from core.models_document_registry import InitiativeStage
        from core.models_research import ResearchResult

        dry_run = options['dry_run']
        fix = options['fix']
        verbose = options['verbose']

        if not dry_run and not fix:
            self.stdout.write(self.style.WARNING(
                'Please specify --dry-run or --fix'
            ))
            return

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 912: Fix Stuck Initiative Documents'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # Find documents with "Insufficient Data" marker
        stuck_docs = SelfBlog.objects.filter(
            full_text__icontains='⚠️ Insufficient Data'
        )

        total = stuck_docs.count()
        self.stdout.write(f"\nFound {total} documents with 'Insufficient Data' marker\n")

        fixed_count = 0
        research_complete_count = 0
        has_findings_count = 0

        for doc in stuck_docs:
            # Check if document also has completion markers (contradictory state)
            has_completion = any([
                'Research completed' in (doc.full_text or ''),
                'data gathered' in (doc.full_text or ''),
                'Research Findings' in (doc.full_text or ''),
            ])

            # Check if associated research is complete
            research_complete = False
            if doc.initiative_stage:
                try:
                    stage = doc.initiative_stage
                    research = ResearchResult.objects.filter(
                        initiative_stage=stage,
                        status='complete'
                    ).first()
                    if research:
                        research_complete = True
                        research_complete_count += 1
                except Exception as _e:
                    logger.warning(
                        "fix_stuck_initiatives.handle: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            # Check if document has actual findings content
            has_findings = len(doc.full_text or '') > 500 and has_completion
            if has_findings:
                has_findings_count += 1

            should_fix = research_complete or has_findings or has_completion

            if verbose or should_fix:
                status = "⚠️ STUCK" if should_fix else "🔄 Waiting"
                self.stdout.write(f"\n{status} Document: {doc.title[:60]}...")
                self.stdout.write(f"   ID: {doc.id}")
                self.stdout.write(f"   Has completion markers: {has_completion}")
                self.stdout.write(f"   Research complete: {research_complete}")
                self.stdout.write(f"   Has substantial content: {has_findings}")

            if should_fix and fix:
                # Update document to mark data as available
                doc.full_text = doc.full_text.replace(
                    '⚠️ Insufficient Data - DataExportAgent may be needed',
                    '✅ Data Available - Fixed by Session 912'
                )
                doc.full_text = doc.full_text.replace(
                    '⚠️ Insufficient Data',
                    '✅ Data Available'
                )
                doc.save(update_fields=['full_text'])

                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f"   ✅ FIXED"))

        # Also update stage statuses from BLOCKED to DRAFT where appropriate
        if fix:
            self.stdout.write(f"\n{'=' * 60}")
            self.stdout.write("Checking blocked stages...")

            blocked_stages = InitiativeStage.objects.filter(status='BLOCKED')
            stages_unblocked = 0

            for stage in blocked_stages:
                # Check if stage has a document with content
                if stage.document and stage.document.full_text:
                    content_length = len(stage.document.full_text)
                    has_insufficient_marker = '⚠️ Insufficient Data' in stage.document.full_text

                    # If document has content and no longer has insufficient marker, unblock
                    if content_length > 500 and not has_insufficient_marker:
                        stage.status = 'DRAFT'
                        stage.notes = f"[Session 912] Unblocked - document has {content_length} chars of content"
                        stage.save(update_fields=['status', 'notes'])
                        stages_unblocked += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"   ✅ Unblocked stage {stage.stage} for initiative {stage.initiative.id if stage.initiative else 'unknown'}"
                        ))

            self.stdout.write(f"\nUnblocked {stages_unblocked} stages")

        # Summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(self.style.HTTP_INFO('SUMMARY'))
        self.stdout.write(f"{'=' * 60}")
        self.stdout.write(f"Total documents with 'Insufficient Data' marker: {total}")
        self.stdout.write(f"Documents with completed research: {research_complete_count}")
        self.stdout.write(f"Documents with substantial content: {has_findings_count}")

        if fix:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Fixed {fixed_count} documents"))
        else:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️ DRY RUN - Would fix approximately {research_complete_count + has_findings_count} documents"
            ))
            self.stdout.write(self.style.WARNING("Run with --fix to apply changes"))
