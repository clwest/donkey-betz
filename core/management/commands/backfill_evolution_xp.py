"""
Session 748: Management command to backfill XP for historical agent activity.

This command awards XP retroactively for all past conversations, dreams, and learning
records that were missed because the Celery task had field name mismatches.

Usage:
    python manage.py backfill_evolution_xp          # Full backfill
    python manage.py backfill_evolution_xp --dry-run  # See what would happen
    python manage.py backfill_evolution_xp --days=30  # Only last 30 days
"""

from django.core.management.base import BaseCommand
from django.db.models import Count
from core.models_unified_system import (
    Agent, AgentEvolution, AgentConversation, AgentDream, AgentLearning, XPHistory
)


class Command(BaseCommand):
    help = 'Backfill XP for historical agent activity (conversations, dreams, learning)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Only process activity from the last N days (default: all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made\n'))

        # Track XP awards to avoid duplicates
        already_awarded = set()

        # Get existing XP history to avoid duplicates
        existing_xp = XPHistory.objects.values_list('agent_id', 'source', 'details')
        for agent_id, source, details in existing_xp:
            already_awarded.add((str(agent_id), source, details[:50] if details else ''))

        total_xp = 0
        total_awards = 0

        # 1. Process Conversations
        self.stdout.write('\n📝 Processing Conversations...')
        conversations = AgentConversation.objects.prefetch_related('participants')
        if days:
            from django.utils import timezone
            from datetime import timedelta
            cutoff = timezone.now() - timedelta(days=days)
            conversations = conversations.filter(started_at__gte=cutoff)

        conv_count = conversations.count()
        self.stdout.write(f'   Found {conv_count} conversations')

        conv_xp = 0
        conv_awards = 0
        for convo in conversations.iterator(chunk_size=100):
            for agent in convo.participants.all():
                key = (str(agent.id), 'conversation', f'Backfill: {convo.topic[:30] if convo.topic else "conv"}'[:50])
                if key not in already_awarded:
                    if not dry_run:
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)
                        evolution.award_xp(5, 'conversation', f'Backfill: {convo.topic[:50] if convo.topic else "Agent conversation"}')
                    conv_xp += 5
                    conv_awards += 1
                    already_awarded.add(key)

        self.stdout.write(f'   Awards: {conv_awards} | XP: {conv_xp}')
        total_xp += conv_xp
        total_awards += conv_awards

        # 2. Process Dreams
        self.stdout.write('\n💭 Processing Dreams...')
        dreams = AgentDream.objects.select_related('agent').exclude(agent__isnull=True)
        if days:
            dreams = dreams.filter(dreamed_at__gte=cutoff)

        dream_count = dreams.count()
        self.stdout.write(f'   Found {dream_count} dreams')

        dream_xp = 0
        dream_awards = 0
        for dream in dreams.iterator(chunk_size=100):
            key = (str(dream.agent.id), 'dream', f'Backfill: {dream.title[:30] if dream.title else "dream"}'[:50])
            if key not in already_awarded:
                if not dry_run:
                    evolution, _ = AgentEvolution.objects.get_or_create(agent=dream.agent)
                    evolution.award_xp(3, 'dream', f'Backfill: {dream.title[:50] if dream.title else "Creative dream"}')
                dream_xp += 3
                dream_awards += 1
                already_awarded.add(key)

        self.stdout.write(f'   Awards: {dream_awards} | XP: {dream_xp}')
        total_xp += dream_xp
        total_awards += dream_awards

        # 3. Process Learning (teacher gets mentorship XP, student gets learning XP)
        self.stdout.write('\n📚 Processing Learning Records...')
        learning = AgentLearning.objects.select_related('teacher_agent', 'student_agent')
        if days:
            learning = learning.filter(created_at__gte=cutoff)

        learning_count = learning.count()
        self.stdout.write(f'   Found {learning_count} learning records')

        learning_xp = 0
        learning_awards = 0
        for record in learning.iterator(chunk_size=100):
            # Award teacher
            if record.teacher_agent:
                key = (str(record.teacher_agent.id), 'mentorship', f'Backfill: Taught {record.learning_type}'[:50])
                if key not in already_awarded:
                    if not dry_run:
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=record.teacher_agent)
                        evolution.award_xp(8, 'mentorship', f'Backfill: Taught {record.learning_type}')
                    learning_xp += 8
                    learning_awards += 1
                    already_awarded.add(key)

            # Award student
            if record.student_agent:
                key = (str(record.student_agent.id), 'learning', f'Backfill: Learned {record.learning_type}'[:50])
                if key not in already_awarded:
                    if not dry_run:
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=record.student_agent)
                        evolution.award_xp(8, 'learning', f'Backfill: Learned {record.learning_type}')
                    learning_xp += 8
                    learning_awards += 1
                    already_awarded.add(key)

        self.stdout.write(f'   Awards: {learning_awards} | XP: {learning_xp}')
        total_xp += learning_xp
        total_awards += learning_awards

        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'TOTAL: {total_awards} awards | {total_xp} XP'))

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - Run without --dry-run to apply changes'))
        else:
            # Show level distribution after backfill
            self.stdout.write('\n📊 Level Distribution After Backfill:')
            level_dist = AgentEvolution.objects.values('current_level').annotate(
                count=Count('id')
            ).order_by('current_level')
            for level in level_dist:
                self.stdout.write(f'   Level {level["current_level"]}: {level["count"]} agents')
