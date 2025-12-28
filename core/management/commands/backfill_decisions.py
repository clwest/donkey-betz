"""
Backfill Decision Summaries from Existing Conversations
Session 323: Boardroom Decisions (original)
Session 412: Updated to support both AgentConversation and HiveMindSession

This command processes existing concluded conversations/sessions that have conclusions
but no associated decision summaries yet.

Supports both:
- AgentConversation (legacy, ~2,899 records)
- HiveMindSession (new, session_mode='conversation')
"""

from django.core.management.base import BaseCommand
from core.models_unified_system import AgentConversation, HiveMindSession, AgentDecisionSummary
from core.services.decision_extractor import get_decision_extractor
import time


class Command(BaseCommand):
    help = 'Backfill decision summaries from existing agent conversations and hive sessions'

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
        parser.add_argument(
            '--source',
            type=str,
            choices=['all', 'conversations', 'hive_sessions'],
            default='all',
            help='Which source to backfill from (default: all)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        verbose = options['verbose']
        source = options['source']

        self.stdout.write(self.style.NOTICE(f"Backfilling decision summaries (limit: {limit}, source: {source})..."))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - no decisions will be created"))

        extractor = get_decision_extractor()

        created = 0
        skipped = 0
        errors = 0

        # Process AgentConversation (legacy)
        if source in ['all', 'conversations']:
            self.stdout.write(self.style.NOTICE("\n=== Processing AgentConversation (legacy) ==="))
            conv_created, conv_skipped, conv_errors = self._process_conversations(
                extractor, limit, dry_run, verbose
            )
            created += conv_created
            skipped += conv_skipped
            errors += conv_errors

        # Process HiveMindSession (new)
        if source in ['all', 'hive_sessions']:
            self.stdout.write(self.style.NOTICE("\n=== Processing HiveMindSession (new) ==="))
            hive_created, hive_skipped, hive_errors = self._process_hive_sessions(
                extractor, limit, dry_run, verbose
            )
            created += hive_created
            skipped += hive_skipped
            errors += hive_errors

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Backfill complete!"))
        self.stdout.write(f"  Created: {created}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Errors: {errors}")

        # Show total decisions in database
        total_decisions = AgentDecisionSummary.objects.count()
        canonical_count = AgentDecisionSummary.objects.filter(is_canonical=True).count()
        conv_decisions = AgentDecisionSummary.objects.filter(conversation__isnull=False).count()
        hive_decisions = AgentDecisionSummary.objects.filter(hive_session__isnull=False).count()

        self.stdout.write(f"\nTotal decisions in database: {total_decisions}")
        self.stdout.write(f"  From AgentConversation: {conv_decisions}")
        self.stdout.write(f"  From HiveMindSession: {hive_decisions}")
        self.stdout.write(f"  Canonical policies: {canonical_count}")

    def _process_conversations(self, extractor, limit, dry_run, verbose):
        """Process legacy AgentConversation records."""
        created = 0
        skipped = 0
        errors = 0

        # Get conversations with conclusions that don't have decisions yet
        conversations = AgentConversation.objects.filter(
            status='concluded',
            conclusion__isnull=False
        ).exclude(
            conclusion=''
        ).exclude(
            decisions__isnull=False  # Already has a decision
        ).order_by('-started_at')[:limit]

        total = conversations.count()
        self.stdout.write(f"Found {total} AgentConversation records to process")

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

        return created, skipped, errors

    def _process_hive_sessions(self, extractor, limit, dry_run, verbose):
        """Process new HiveMindSession records."""
        created = 0
        skipped = 0
        errors = 0

        # Get sessions with synthesis that don't have decisions yet
        # HiveMindSession uses `synthesis` field for the final output
        sessions = HiveMindSession.objects.filter(
            status='completed'
        ).exclude(
            synthesis=''
        ).exclude(
            synthesis__isnull=True
        ).exclude(
            decisions__isnull=False  # Already has a decision
        ).order_by('-started_at')[:limit]

        total = sessions.count()
        self.stdout.write(f"Found {total} HiveMindSession records to process")

        for i, session in enumerate(sessions, 1):
            conclusion = session.synthesis
            conclusion_len = len(conclusion) if conclusion else 0
            # Use conversation_topic for conversation mode, question for hive_mind mode
            topic = session.conversation_topic or session.question or 'Unknown Topic'

            if verbose:
                self.stdout.write(f"\n[{i}/{total}] Processing: {topic[:60]}...")
                self.stdout.write(f"  Conclusion length: {conclusion_len} chars")

            # Skip very short conclusions
            if conclusion_len < 50:
                if verbose:
                    self.stdout.write(self.style.WARNING("  Skipped: conclusion too short"))
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"  Would create decision for: {topic[:60]}..."))
                created += 1
                continue

            try:
                decision = extractor.create_decision_from_hive_session(session)
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

        return created, skipped, errors
