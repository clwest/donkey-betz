"""
Session 906: Backfill links between SelfBlog research briefs and InitiativeStages.

Problem: 269 out of 288 research briefs are not linked to InitiativeStages,
preventing them from progressing through the pipeline.

Usage:
    # Dry run - show what would be linked
    python manage.py backfill_research_brief_links

    # Actually link them
    python manage.py backfill_research_brief_links --fix

    # Limit batch size
    python manage.py backfill_research_brief_links --fix --limit=50
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill links between SelfBlog research briefs and InitiativeStages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually create the links (default is dry run)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Maximum number of briefs to process (default: 500)',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import SelfBlog
        from core.models_document_registry import InitiativeStage
        from core.services.initiative_integration_service import get_initiative_integration_service

        fix = options['fix']
        limit = options['limit']

        self.stdout.write(self.style.NOTICE(
            f"{'FIXING' if fix else 'DRY RUN'}: Backfilling research brief links (limit: {limit})"
        ))

        # Find research briefs that are NOT linked to any stage
        linked_ids = set(
            InitiativeStage.objects.filter(document__isnull=False)
            .values_list('document_id', flat=True)
        )

        unlinked_briefs = SelfBlog.objects.filter(
            category='research_brief'
        ).exclude(
            id__in=linked_ids
        ).order_by('-created_at')[:limit]

        self.stdout.write(f"Found {unlinked_briefs.count()} unlinked research briefs")

        linked_count = 0
        skipped_count = 0
        error_count = 0

        service = get_initiative_integration_service() if fix else None

        for brief in unlinked_briefs:
            # Extract topic from stats_snapshot
            topic = None
            if brief.stats_snapshot:
                topic = brief.stats_snapshot.get('parent_topic')

            if not topic:
                # Try to extract from title
                title = brief.title or ''
                if title.startswith('[Research] '):
                    topic = title[11:]  # Remove prefix

            if not topic:
                self.stdout.write(self.style.WARNING(
                    f"SKIP: {brief.id} - No topic found"
                ))
                skipped_count += 1
                continue

            # Truncate topic if too long
            topic = topic[:200]

            if fix:
                try:
                    stage = service.link_document_to_stage(
                        document=brief,
                        initiative=None,  # Auto-create/find
                        force_stage=1  # Research briefs go to Stage 1
                    )
                    if stage:
                        linked_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"LINKED: {brief.id} → {stage.initiative.name[:40]} Stage 1"
                        ))
                    else:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(
                            f"FAIL: {brief.id} - link_document_to_stage returned None"
                        ))
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(
                        f"ERROR: {brief.id} - {e}"
                    ))
            else:
                # Dry run
                self.stdout.write(
                    f"WOULD LINK: {brief.id} | {topic[:50]} → Stage 1"
                )
                linked_count += 1

        self.stdout.write(self.style.SUCCESS(f"\n{'FIXED' if fix else 'WOULD FIX'}: {linked_count}"))
        self.stdout.write(self.style.WARNING(f"SKIPPED: {skipped_count}"))
        if error_count:
            self.stdout.write(self.style.ERROR(f"ERRORS: {error_count}"))
