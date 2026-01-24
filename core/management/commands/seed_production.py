"""
Session 799: Production Seeding Command

Creates essential infrastructure for production without demo data:
1. Content Channels - for autonomous content generation
2. System configurations - basic platform settings
3. Initial opportunities structure

Run with: python manage.py seed_production
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Seed production database with essential infrastructure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--skip-channels',
            action='store_true',
            help='Skip creating content channels',
        )
        parser.add_argument(
            '--skip-agents',
            action='store_true',
            help='Skip syncing agents',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS(
            '🚀 Session 799: Production Seeding Command'
        ))

        if self.dry_run:
            self.stdout.write(self.style.WARNING('  DRY RUN - No changes will be made'))

        self.stdout.write('')

        # Get or create system user
        user = self._get_system_user()
        if not user:
            self.stdout.write(self.style.ERROR('❌ No user found. Create a superuser first.'))
            return

        # Sync agents
        if not options['skip_agents']:
            self._sync_agents()

        # Create content channels
        if not options['skip_channels']:
            self._create_content_channels(user)

        # Create system configurations
        self._create_system_configs()

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Production seeding complete!'))
        self._display_summary()

    def _get_system_user(self):
        """Get the first superuser or any user."""
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.first()

        if user:
            self.stdout.write(f'👤 Using user: {user.username}')
        return user

    def _sync_agents(self):
        """Sync all agents to database."""
        self.stdout.write('')
        self.stdout.write('🤖 Syncing agents...')

        if self.dry_run:
            self.stdout.write('  Would sync all agents from registry')
            return

        try:
            from django.core.management import call_command
            call_command('sync_agents', verbosity=0)

            from core.models_unified_system import Agent
            count = Agent.objects.count()
            self.stdout.write(self.style.SUCCESS(f'  ✓ {count} agents synced'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Agent sync failed: {e}'))

    def _create_content_channels(self, user):
        """Create essential content channels for autonomous content generation."""
        self.stdout.write('')
        self.stdout.write('📺 Creating content channels...')

        from core.models_autonomous_studio import ContentChannel

        # Define essential channels
        channels = [
            {
                'name': 'Tech & AI Insights',
                'topic_domain': 'artificial intelligence, machine learning, tech trends, software development, automation',
                'target_audience': 'Tech professionals, developers, AI enthusiasts',
                'content_frequency': 'daily',
                'visual_style': 'modern, tech-forward, clean',
                'platform': 'blog',
            },
            {
                'name': 'Market Intelligence',
                'topic_domain': 'stock market, crypto, financial trends, economic indicators, investment opportunities',
                'target_audience': 'Investors, traders, financial analysts',
                'content_frequency': 'daily',
                'visual_style': 'professional, data-driven, charts',
                'platform': 'blog',
            },
            {
                'name': 'Sports Analytics',
                'topic_domain': 'sports betting, odds analysis, game predictions, player stats, team performance',
                'target_audience': 'Sports bettors, fantasy sports players, sports analysts',
                'content_frequency': 'daily',
                'visual_style': 'dynamic, sports-themed, statistical',
                'platform': 'blog',
            },
            {
                'name': 'Career & Jobs',
                'topic_domain': 'job market trends, career advice, remote work, salary insights, hiring patterns',
                'target_audience': 'Job seekers, professionals, HR managers',
                'content_frequency': 'weekly',
                'visual_style': 'professional, approachable, actionable',
                'platform': 'blog',
            },
            {
                'name': 'AI Podcast Studio',
                'topic_domain': 'AI discussions, tech debates, industry interviews, future predictions',
                'target_audience': 'Tech enthusiasts, podcast listeners, industry professionals',
                'content_frequency': 'weekly',
                'visual_style': 'conversational, engaging, thought-provoking',
                'platform': 'podcast',
            },
        ]

        created_count = 0
        existing_count = 0

        for channel_data in channels:
            if self.dry_run:
                self.stdout.write(f"  Would create: {channel_data['name']}")
                created_count += 1
                continue

            channel, created = ContentChannel.objects.get_or_create(
                name=channel_data['name'],
                defaults={
                    'user': user,
                    'topic_domain': channel_data['topic_domain'],
                    'target_audience': channel_data['target_audience'],
                    'content_frequency': channel_data['content_frequency'],
                    'visual_style': channel_data['visual_style'],
                    'platform': channel_data.get('platform', 'blog'),
                    'voice_name': 'Default',
                    'status': 'active',
                    'publish_automatically': False,
                    'next_content_due': timezone.now(),
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Created: {channel.name}")
            else:
                existing_count += 1
                self.stdout.write(f"  · Exists: {channel.name}")

        self.stdout.write(self.style.SUCCESS(
            f'  Created {created_count}, existing {existing_count}'
        ))

    def _create_system_configs(self):
        """Create essential system configurations."""
        self.stdout.write('')
        self.stdout.write('⚙️ Creating system configurations...')

        try:
            from core.models import SystemConfiguration

            configs = [
                ('autonomous_content_enabled', True, 'Enable autonomous content generation', 'content'),
                ('spider_network_enabled', True, 'Enable spider data collection', 'spiders'),
                ('agent_learning_enabled', True, 'Enable agent learning from executions', 'agents'),
                ('dream_generation_enabled', True, 'Enable agent dream generation', 'scifi'),
                ('opportunity_scoring_enabled', True, 'Enable opportunity scoring', 'intelligence'),
                ('max_daily_content_items', 50, 'Maximum content items per day', 'content'),
                ('spider_refresh_interval_minutes', 30, 'Spider data refresh interval', 'spiders'),
            ]

            created_count = 0
            for key, value, description, category in configs:
                if self.dry_run:
                    self.stdout.write(f"  Would create: {key} = {value}")
                    created_count += 1
                    continue

                config, created = SystemConfiguration.objects.get_or_create(
                    key=key,
                    defaults={
                        'value': str(value),
                        'description': description,
                        'category': category,
                    }
                )
                if created:
                    created_count += 1

            self.stdout.write(self.style.SUCCESS(f'  ✓ {created_count} configs created'))

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Config creation skipped: {e}'))

    def _display_summary(self):
        """Display summary of what was created."""
        self.stdout.write('')
        self.stdout.write('=' * 50)
        self.stdout.write('PRODUCTION DATABASE STATUS')
        self.stdout.write('=' * 50)

        if self.dry_run:
            self.stdout.write('(Dry run - no actual counts)')
            return

        try:
            from core.models_unified_system import Agent, AgentExecution, Opportunity
            from core.models_autonomous_studio import ContentChannel, ChannelEpisode

            self.stdout.write(f"Agents:          {Agent.objects.count()}")
            self.stdout.write(f"Content Channels: {ContentChannel.objects.count()}")
            self.stdout.write(f"Episodes:        {ChannelEpisode.objects.count()}")
            self.stdout.write(f"Executions:      {AgentExecution.objects.count()}")
            self.stdout.write(f"Opportunities:   {Opportunity.objects.count()}")

        except Exception as e:
            self.stdout.write(f"Error getting counts: {e}")

        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Verify Celery Beat is running for scheduled tasks')
        self.stdout.write('2. Check API keys are configured (OPENAI_API_KEY, etc.)')
        self.stdout.write('3. Content will start generating on next scheduled run')
