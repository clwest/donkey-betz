"""
Session 770: Content Quality Cleanup Command

This command:
1. Adds known bad topics to the ContentQualityBlacklist
2. Cleans up polluted dreams and knowledge sources (marks as archived)
3. Reports on what was cleaned up

Usage:
    python manage.py cleanup_content_quality --dry-run  # See what would be cleaned
    python manage.py cleanup_content_quality            # Actually clean up
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Session 770: Clean up content quality issues - add blacklist entries and remove polluted data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually cleaning',
        )
        parser.add_argument(
            '--skip-blacklist',
            action='store_true',
            help='Skip adding blacklist entries',
        )
        parser.add_argument(
            '--skip-cleanup',
            action='store_true',
            help='Skip cleaning up polluted data',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        skip_blacklist = options['skip_blacklist']
        skip_cleanup = options['skip_cleanup']

        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN MODE - No changes will be made ===\n'))

        stats = {
            'blacklist_entries_added': 0,
            'dreams_archived': 0,
            'knowledge_archived': 0,
        }

        # Part 1: Add blacklist entries
        if not skip_blacklist:
            stats['blacklist_entries_added'] = self._add_blacklist_entries(dry_run)

        # Part 2: Clean up polluted data
        if not skip_cleanup:
            dreams, knowledge = self._cleanup_polluted_data(dry_run)
            stats['dreams_archived'] = dreams
            stats['knowledge_archived'] = knowledge

        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('CONTENT QUALITY CLEANUP SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write(f"  Blacklist entries added: {stats['blacklist_entries_added']}")
        self.stdout.write(f"  Dreams archived: {stats['dreams_archived']}")
        self.stdout.write(f"  Knowledge sources archived: {stats['knowledge_archived']}")
        if dry_run:
            self.stdout.write(self.style.WARNING('\n  [DRY RUN - No changes were made]'))
        self.stdout.write('=' * 60 + '\n')

    def _add_blacklist_entries(self, dry_run: bool) -> int:
        """Add known bad topics to the blacklist."""
        from core.models_unified_system import ContentQualityBlacklist

        self.stdout.write('\n--- Adding Blacklist Entries ---\n')

        # Define blacklist entries to add
        entries = [
            # Test probes
            {
                'pattern': 'raw onion bar',
                'block_type': 'topic',
                'reason': 'test_probe',
                'reason_detail': 'Test topic used to probe system quality. Should never be used for real content.',
            },
            {
                'pattern': 'onion bar',
                'block_type': 'topic',
                'reason': 'test_probe',
                'reason_detail': 'Test topic (variant). Should never be used for real content.',
            },
            # Generic placeholder patterns
            {
                'pattern': r'50 data points from huggingface',
                'block_type': 'pattern',
                'reason': 'low_quality',
                'reason_detail': 'Generic placeholder without specific details. Content should explain WHAT data points.',
            },
            {
                'pattern': r'train.*huggingface.*on',
                'block_type': 'pattern',
                'reason': 'low_quality',
                'reason_detail': 'Generic AI training template without specifics.',
            },
            {
                'pattern': r'data points from huggingface',
                'block_type': 'pattern',
                'reason': 'low_quality',
                'reason_detail': 'Vague reference to data without explaining what data or how selected.',
            },
            # Over-recycled topics (add more as discovered)
            {
                'pattern': 'Quantum Computing in Agriculture',
                'block_type': 'topic',
                'reason': 'recycled',
                'reason_detail': 'Overused mashup concept appearing in too many dreams.',
            },
        ]

        count = 0
        for entry in entries:
            # Check if already exists
            existing = ContentQualityBlacklist.objects.filter(
                pattern_normalized=entry['pattern'].lower().strip(),
                is_active=True
            ).first()

            if existing:
                self.stdout.write(f"  [EXISTS] {entry['pattern']} - already in blacklist")
                continue

            if dry_run:
                self.stdout.write(f"  [WOULD ADD] {entry['pattern']} ({entry['reason']})")
            else:
                ContentQualityBlacklist.objects.create(
                    pattern=entry['pattern'],
                    pattern_normalized=entry['pattern'].lower().strip(),
                    block_type=entry['block_type'],
                    reason=entry['reason'],
                    reason_detail=entry['reason_detail'],
                    is_global=True,
                )
                self.stdout.write(self.style.SUCCESS(f"  [ADDED] {entry['pattern']} ({entry['reason']})"))
            count += 1

        return count

    def _cleanup_polluted_data(self, dry_run: bool) -> tuple:
        """Clean up dreams and knowledge with polluted content."""
        from core.models import AgentDream, AgentKnowledgeSource
        from django.db.models import Q

        self.stdout.write('\n--- Cleaning Up Polluted Data ---\n')

        # Patterns to match for cleanup
        polluted_patterns = [
            'raw onion bar',
            'onion bar',
            '50 data points from huggingface',
        ]

        # Build query for dreams
        dream_query = Q()
        for pattern in polluted_patterns:
            dream_query |= Q(title__icontains=pattern)
            dream_query |= Q(content__icontains=pattern)
            dream_query |= Q(inspiration_source__icontains=pattern)

        polluted_dreams = AgentDream.objects.filter(dream_query)
        dream_count = polluted_dreams.count()

        self.stdout.write(f"\n  Found {dream_count} polluted dreams:")
        for dream in polluted_dreams[:10]:  # Show first 10
            self.stdout.write(f"    - {dream.title[:60]}... (by {dream.agent.name if dream.agent else 'unknown'})")
        if dream_count > 10:
            self.stdout.write(f"    ... and {dream_count - 10} more")

        # Build query for knowledge
        knowledge_query = Q()
        for pattern in polluted_patterns:
            knowledge_query |= Q(title__icontains=pattern)
            knowledge_query |= Q(summary__icontains=pattern)

        polluted_knowledge = AgentKnowledgeSource.objects.filter(knowledge_query)
        knowledge_count = polluted_knowledge.count()

        self.stdout.write(f"\n  Found {knowledge_count} polluted knowledge sources:")
        for knowledge in polluted_knowledge[:10]:  # Show first 10
            self.stdout.write(f"    - {knowledge.title[:60]}... ({knowledge.knowledge_type})")
        if knowledge_count > 10:
            self.stdout.write(f"    ... and {knowledge_count - 10} more")

        # Archive the polluted data
        if not dry_run:
            # For dreams: mark as archived by setting is_hidden=True or similar
            # Since AgentDream may not have is_hidden, we'll add a prefix to mark them
            for dream in polluted_dreams:
                if not dream.title.startswith('[ARCHIVED]'):
                    dream.title = f"[ARCHIVED] {dream.title}"
                    dream.save(update_fields=['title'])

            # For knowledge: mark as archived
            for knowledge in polluted_knowledge:
                if not knowledge.title.startswith('[ARCHIVED]'):
                    knowledge.title = f"[ARCHIVED] {knowledge.title}"
                    knowledge.save(update_fields=['title'])

            self.stdout.write(self.style.SUCCESS(f"\n  Archived {dream_count} dreams and {knowledge_count} knowledge sources"))
        else:
            self.stdout.write(f"\n  [DRY RUN] Would archive {dream_count} dreams and {knowledge_count} knowledge sources")

        return dream_count, knowledge_count
