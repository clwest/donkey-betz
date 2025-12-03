"""
Backfill Decision Summaries from Existing Conversations
Session 323: Boardroom Decisions

This command processes existing concluded conversations that have conclusions
but no associated decision summaries yet.
"""

from django.core.management.base import BaseCommand
from core.models_unified_system import AgentConversation, AgentDecisionSummary
from core.services.decision_extractor import get_decision_extractor
import time


class Command(BaseCommand):
    help = 'Backfill decision summaries from existing agent conversations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of conversations to process (default: 50)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without creating decisions'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each conversation'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        verbose = options['verbose']

        self.stdout.write(self.style.NOTICE(f"Backfilling decision summaries (limit: {limit})..."))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - no decisions will be created"))

        extractor = get_decision_extractor()

        # Get conversations with conclusions that don't have decisions yet
        # and have a conclusion of at least 50 characters
        conversations = AgentConversation.objects.filter(
            status='concluded',
            conclusion__isnull=False
        ).exclude(
            conclusion=''
        ).exclude(
            decisions__isnull=False  # Already has a decision
        ).order_by('-started_at')[:limit]

        total = conversations.count()
        self.stdout.write(f"Found {total} conversations to process")

        created = 0
        skipped = 0
        errors = 0

        for i, conv in enumerate(conversations, 1):
            conclusion_len = len(conv.conclusion) if conv.conclusion else 0

            if verbose:
                self.stdout.write(f"\n[{i}/{total}] Processing: {conv.topic[:60]}...")
                self.stdout.write(f"  Conclusion length: {conclusion_len} chars")

            # Skip very short conclusions
            if conclusion_len < 50:
                if verbose:
                    self.stdout.write(self.style.WARNING("  Skipped: conclusion too short"))
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"  Would create decision for: {conv.topic[:60]}..."))
                created += 1
                continue

            try:
                decision = extractor.create_decision_from_conversation(conv)
                if decision:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"  Created: [{decision.decision_type}] {decision.topic[:50]}..."))
                else:
                    skipped += 1
                    if verbose:
                        self.stdout.write(self.style.WARNING("  Skipped: no clear decision extracted"))

                # Rate limiting to avoid API throttling
                time.sleep(0.5)

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Backfill complete!"))
        self.stdout.write(f"  Created: {created}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Errors: {errors}")

        # Show total decisions in database
        total_decisions = AgentDecisionSummary.objects.count()
        canonical_count = AgentDecisionSummary.objects.filter(is_canonical=True).count()
        self.stdout.write(f"\nTotal decisions in database: {total_decisions}")
        self.stdout.write(f"Canonical policies: {canonical_count}")
