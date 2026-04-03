"""
Session 786: Backfill DecisionSummary blocks for existing conversations.

This command regenerates DecisionSummary blocks for:
- HiveMindSession records with synthesis but no DecisionSummary
- AgentConversation final messages without DecisionSummary

Usage:
    python manage.py backfill_decision_summaries
    python manage.py backfill_decision_summaries --limit 100
    python manage.py backfill_decision_summaries --dry-run
    python manage.py backfill_decision_summaries --type hivemind
    python manage.py backfill_decision_summaries --type legacy
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from openai import OpenAI
import os

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill DecisionSummary blocks for existing conversations'

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
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--type',
            choices=['all', 'hivemind', 'legacy'],
            default='all',
            help='Type of conversations to backfill (default: all)'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        conv_type = options['type']

        self.stdout.write(f"Backfilling DecisionSummary blocks (limit={limit}, dry_run={dry_run}, type={conv_type})")

        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        total_processed = 0
        total_updated = 0

        if conv_type in ['all', 'hivemind']:
            processed, updated = self._backfill_hivemind(client, limit, dry_run)
            total_processed += processed
            total_updated += updated

        if conv_type in ['all', 'legacy']:
            remaining_limit = limit - total_processed if conv_type == 'all' else limit
            if remaining_limit > 0:
                processed, updated = self._backfill_legacy(client, remaining_limit, dry_run)
                total_processed += processed
                total_updated += updated

        self.stdout.write(self.style.SUCCESS(
            f"Done! Processed {total_processed} conversations, updated {total_updated}"
        ))

    def _backfill_hivemind(self, client, limit, dry_run):
        """Backfill HiveMindSession synthesis with DecisionSummary."""
        from core.models_unified_system import HiveMindSession

        self.stdout.write("\n--- HiveMind Sessions ---")

        # Find sessions with synthesis but no DecisionSummary
        sessions = HiveMindSession.objects.filter(
            session_mode='conversation',
            status='completed'
        ).exclude(
            synthesis=''
        ).exclude(
            synthesis__isnull=True
        ).exclude(
            synthesis__contains='=== DecisionSummary ==='
        ).order_by('-created_at')[:limit]

        count = sessions.count()
        self.stdout.write(f"Found {count} HiveMind sessions without DecisionSummary")

        processed = 0
        updated = 0

        for session in sessions:
            processed += 1
            self.stdout.write(f"  [{processed}/{count}] {session.conversation_topic or session.question[:50]}...")

            if dry_run:
                self.stdout.write(f"    Would generate DecisionSummary (dry-run)")
                continue

            try:
                # Generate DecisionSummary based on existing synthesis
                decision_summary = self._generate_decision_summary(
                    client,
                    session.synthesis,
                    session.question
                )

                if decision_summary:
                    # Append to synthesis
                    session.synthesis = session.synthesis.rstrip() + "\n\n" + decision_summary
                    session.save(update_fields=['synthesis'])
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"    ✓ DecisionSummary added"))
                else:
                    self.stdout.write(self.style.WARNING(f"    ✗ Failed to generate"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ✗ Error: {e}"))

        return processed, updated

    def _backfill_legacy(self, client, limit, dry_run):
        """Backfill AgentConversation final messages with DecisionSummary."""
        from core.models_unified_system import AgentConversation, ConversationMessage

        self.stdout.write("\n--- Legacy Conversations ---")

        # Find conversations where final message doesn't have DecisionSummary
        conversations = AgentConversation.objects.filter(
            status='concluded'
        ).exclude(
            messages__content__contains='=== DecisionSummary ==='
        ).order_by('-started_at')[:limit * 2]  # Get more since we filter by final message

        count = 0
        to_process = []

        for conv in conversations:
            final_msg = conv.messages.order_by('-sequence_number').first()
            if final_msg and '=== DecisionSummary ===' not in (final_msg.content or ''):
                to_process.append((conv, final_msg))
                count += 1
                if count >= limit:
                    break

        self.stdout.write(f"Found {count} legacy conversations without DecisionSummary")

        processed = 0
        updated = 0

        for conv, final_msg in to_process:
            processed += 1
            self.stdout.write(f"  [{processed}/{count}] {conv.topic[:50] if conv.topic else 'No topic'}...")

            if dry_run:
                self.stdout.write(f"    Would generate DecisionSummary (dry-run)")
                continue

            try:
                # Get all messages for context
                messages = conv.messages.order_by('sequence_number')
                combined_content = "\n\n".join([
                    f"{m.agent.name if m.agent else 'Agent'}: {m.content}"
                    for m in messages if m.content
                ])

                # Generate DecisionSummary
                decision_summary = self._generate_decision_summary(
                    client,
                    combined_content,
                    conv.topic
                )

                if decision_summary:
                    # Append to final message
                    final_msg.content = (final_msg.content or '').rstrip() + "\n\n" + decision_summary
                    final_msg.save(update_fields=['content'])
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f"    ✓ DecisionSummary added"))
                else:
                    self.stdout.write(self.style.WARNING(f"    ✗ Failed to generate"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ✗ Error: {e}"))

        return processed, updated

    def _generate_decision_summary(self, client, content: str, topic: str) -> str:
        """Generate a DecisionSummary block based on conversation content."""
        prompt = f"""Based on the following conversation content, generate a DecisionSummary block.

CONVERSATION TOPIC: {topic}

CONVERSATION CONTENT:
{content[:4000]}  # Limit to avoid token limits

Generate ONLY the DecisionSummary block in this EXACT format:

=== DecisionSummary ===
Insights:
1. [First key insight from the conversation - be specific]
2. [Second insight about the approach or implementation]
3. [Third insight about considerations or trade-offs]

Proposed Feature:
- Name: [Specific feature name that emerged from the discussion]
- Inputs: [What data or content the feature needs]
- Outputs: [What the feature produces or enables]
- Where it plugs into the system: [Component like dashboard, API, workflow, agent, etc.]

Next Steps:
1. [First concrete action with owner if mentioned]
2. [Second concrete action with owner if mentioned]

Output ONLY the DecisionSummary block, nothing else."""

        try:
            response = client.chat.completions.create(
                model="gpt-5.2",  # Use faster model for backfill
                messages=[
                    {
                        "role": "system",
                        "content": "You extract and structure decision summaries from conversation transcripts. Output only the DecisionSummary block."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=500,
            )

            result = response.choices[0].message.content.strip()

            # Validate it has the marker
            if "=== DecisionSummary ===" in result:
                return result
            else:
                # Try to fix by adding marker
                if "Insights:" in result:
                    return "=== DecisionSummary ===\n" + result

            return None

        except Exception as e:
            logger.error(f"Failed to generate DecisionSummary: {e}")
            return None
