"""
Management command to discover and propagate learning cohorts
Run nightly via cron: python manage.py discover_learning_cohorts
"""

import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg
from core.models import UserAgentLearning

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Discover learning cohorts and propagate high-confidence learnings between similar users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-confidence',
            type=float,
            default=0.75,
            help='Minimum confidence threshold for sharing learnings (default: 0.75)'
        )
        parser.add_argument(
            '--min-similarity',
            type=float,
            default=0.5,
            help='Minimum similarity score for cohort membership (default: 0.5)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be shared without actually sharing'
        )

    def handle(self, *args, **options):
        min_confidence = options['min_confidence']
        min_similarity = options['min_similarity']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS(f'\n🔍 Starting cohort discovery...'))
        self.stdout.write(f'   Min confidence: {min_confidence:.0%}')
        self.stdout.write(f'   Min similarity: {min_similarity:.0%}')
        self.stdout.write(f'   Mode: {"DRY RUN" if dry_run else "LIVE"}\n')

        User = get_user_model()

        # Get all users with learnings
        users_with_learnings = User.objects.filter(
            useragentlearning__is_active=True
        ).distinct()

        total_users = users_with_learnings.count()
        self.stdout.write(f'📊 Found {total_users} users with active learnings\n')

        if total_users < 2:
            self.stdout.write(self.style.WARNING('⚠️  Not enough users for cohort discovery'))
            return

        # Track statistics
        cohorts_discovered = 0
        learnings_shared = 0
        domains_processed = set()

        # Group users by learning domains
        learning_domains = UserAgentLearning.objects.filter(
            is_active=True,
            confidence_score__gte=min_confidence
        ).values_list('learning_domain', flat=True).distinct()

        self.stdout.write(f'🎯 Processing {len(learning_domains)} learning domains:\n')

        for domain in learning_domains:
            domains_processed.add(domain)

            self.stdout.write(f'\n📚 Domain: {domain}')

            # Find users with high-confidence learnings in this domain
            source_users = User.objects.filter(
                useragentlearning__learning_domain=domain,
                useragentlearning__is_active=True,
                useragentlearning__confidence_score__gte=min_confidence
            ).annotate(
                avg_confidence=Avg('useragentlearning__confidence_score')
            ).order_by('-avg_confidence')[:10]  # Top 10 confident users

            for source_user in source_users:
                # Get one of their high-confidence learnings to access cohort method
                source_learning = UserAgentLearning.objects.filter(
                    user=source_user,
                    learning_domain=domain,
                    is_active=True,
                    confidence_score__gte=min_confidence
                ).first()

                if not source_learning:
                    continue

                # Find similar users
                similar_users = source_learning.get_learning_cohort(
                    min_similarity=min_similarity
                )

                if not similar_users:
                    continue

                cohorts_discovered += 1
                target_users = [su['user'] for su in similar_users[:5]]  # Top 5 similar users

                self.stdout.write(
                    f'   👥 {source_user.username} → {len(target_users)} similar users '
                    f'(similarity: {similar_users[0]["similarity"]:.0%})'
                )

                if not dry_run:
                    # Share learnings
                    shared_count = UserAgentLearning.share_learning_between_agents(
                        source_user=source_user,
                        target_users=target_users,
                        domain=domain,
                        min_confidence=min_confidence
                    )
                    learnings_shared += shared_count
                    self.stdout.write(f'      ✅ Shared {shared_count} learnings')
                else:
                    # Calculate what would be shared
                    shareable = UserAgentLearning.objects.filter(
                        user=source_user,
                        learning_domain=domain,
                        is_active=True,
                        confidence_score__gte=min_confidence
                    ).count()
                    potential_shares = shareable * len(target_users)
                    self.stdout.write(f'      📋 Would share {potential_shares} learnings')

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n\n✨ Cohort Discovery Complete!'))
        self.stdout.write(f'   Cohorts discovered: {cohorts_discovered}')
        self.stdout.write(f'   Domains processed: {len(domains_processed)}')

        if not dry_run:
            self.stdout.write(f'   Learnings shared: {learnings_shared}')
            self.stdout.write(self.style.SUCCESS('\n✅ Learnings propagated successfully\n'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN - No changes made\n'))

        # Recommendations
        self.stdout.write('\n💡 Next steps:')
        self.stdout.write('   1. Schedule this command to run nightly:')
        self.stdout.write('      0 2 * * * cd /path/to/project && python manage.py discover_learning_cohorts')
        self.stdout.write('   2. Monitor learning propagation effectiveness')
        self.stdout.write('   3. Adjust thresholds based on results\n')
