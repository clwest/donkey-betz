"""
Management command to initialize the Unified Donkey Betz Platform.

This command sets up initial configuration, creates system defaults,
and prepares the platform for first use.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import SystemConfiguration, PlatformMetrics

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize the Unified Donkey Betz Platform with default settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all existing configuration (WARNING: destructive)',
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Initializing Unified Donkey Betz Platform...')
        )

        if options['reset']:
            self.stdout.write('⚠️  Resetting existing configuration...')
            SystemConfiguration.objects.all().delete()
            PlatformMetrics.objects.all().delete()

        # Initialize system configurations
        self._init_system_configs()
        
        # Record initial metrics
        self._record_initial_metrics()
        
        # Optionally create superuser
        if options['create_superuser']:
            self._create_superuser()

        self.stdout.write(
            self.style.SUCCESS('✅ Platform initialization complete!')
        )
        
        self._display_status()

    def _init_system_configs(self):
        """Initialize default system configurations."""
        configs = [
            # Agent Orchestration Settings
            ('max_concurrent_agents', 100, 'Maximum number of agents that can run concurrently', 'agents'),
            ('agent_timeout_seconds', 300, 'Default timeout for agent execution in seconds', 'agents'),
            ('enable_cross_domain_agents', True, 'Allow agents to work across different domains', 'agents'),
            ('agent_registry_cache_ttl', 900, 'Agent registry cache time-to-live in seconds', 'agents'),
            
            # AI Services Settings
            ('default_ai_provider', 'openai', 'Default AI provider for content generation', 'ai_services'),
            ('max_tokens_per_request', 4000, 'Maximum tokens allowed per AI request', 'ai_services'),
            ('ai_request_timeout', 30, 'Timeout for AI API requests in seconds', 'ai_services'),
            
            # Sports Analytics Settings
            ('sports_confidence_threshold', 0.6, 'Minimum confidence threshold for sports predictions', 'sports'),
            ('sports_min_edge', 0.04, 'Minimum edge required for sports betting recommendations', 'sports'),
            ('max_concurrent_sports_analyses', 5, 'Maximum concurrent sports analysis tasks', 'sports'),
            
            # Content Generation Settings
            ('content_generation_temperature', 0.7, 'Default temperature for content generation', 'content'),
            ('max_content_items_per_batch', 10, 'Maximum content items to generate in one batch', 'content'),
            
            # System Performance Settings
            ('api_rate_limit_per_hour', 1000, 'Default API rate limit per hour per user', 'performance'),
            ('max_database_connections', 50, 'Maximum database connection pool size', 'performance'),
            ('cache_ttl_default', 300, 'Default cache time-to-live in seconds', 'performance'),
            
            # Security Settings
            ('api_key_length', 64, 'Length of generated API keys', 'security'),
            ('session_timeout_minutes', 60, 'User session timeout in minutes', 'security'),
            ('enable_request_logging', True, 'Enable detailed request logging', 'security'),
            
            # Self-Awareness Settings
            ('enable_self_awareness', True, 'Enable system self-awareness features', 'system'),
            ('self_awareness_scan_interval', 3600, 'Self-awareness scan interval in seconds', 'system'),
            ('enable_code_embedding', True, 'Enable code embedding for self-understanding', 'system'),
            ('enable_self_modification', False, 'Enable system self-modification (DANGEROUS)', 'system'),
        ]
        
        created_count = 0
        updated_count = 0
        
        for key, value, description, category in configs:
            config, created = SystemConfiguration.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': description,
                    'category': category,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ Created config: {key}')
            else:
                updated_count += 1
                self.stdout.write(f'  ℹ️  Config exists: {key}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'📝 Configuration: {created_count} created, {updated_count} existing'
            )
        )

    def _record_initial_metrics(self):
        """Record initial platform metrics."""
        initial_metrics = [
            ('platform_initialized', 1, 'counter', 'system'),
            ('total_users', User.objects.count(), 'gauge', 'system'),
            ('active_configurations', SystemConfiguration.objects.filter(is_active=True).count(), 'gauge', 'system'),
        ]
        
        for name, value, metric_type, subsystem in initial_metrics:
            PlatformMetrics.record_metric(name, value, metric_type, subsystem)
            self.stdout.write(f'  📊 Recorded metric: {name} = {value}')
        
        self.stdout.write(
            self.style.SUCCESS('📈 Initial metrics recorded')
        )

    def _create_superuser(self):
        """Create a superuser if none exists."""
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write('👤 Superuser already exists')
            return
        
        try:
            user = User.objects.create_superuser(
                username='admin',
                email='admin@unified-donkey-betz.com',
                password='admin123',  # Should be changed in production
                platform_role='admin',
                subscription_tier='enterprise'
            )
            self.stdout.write(
                self.style.SUCCESS('👤 Created superuser: admin / admin123')
            )
            self.stdout.write(
                self.style.WARNING('⚠️  Change the default password in production!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to create superuser: {e}')
            )

    def _display_status(self):
        """Display platform status summary."""
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🏆 UNIFIED DONKEY BETZ PLATFORM STATUS'))
        self.stdout.write('=' * 50)
        
        # Users
        total_users = User.objects.count()
        admin_users = User.objects.filter(platform_role='admin').count()
        self.stdout.write(f'👥 Users: {total_users} total, {admin_users} admins')
        
        # Configuration
        total_configs = SystemConfiguration.objects.count()
        active_configs = SystemConfiguration.objects.filter(is_active=True).count()
        self.stdout.write(f'⚙️  Configuration: {active_configs}/{total_configs} active')
        
        # Metrics
        total_metrics = PlatformMetrics.objects.count()
        self.stdout.write(f'📊 Metrics: {total_metrics} recorded')
        
        # Next steps
        self.stdout.write('\n📋 Next Steps:')
        self.stdout.write('   1. Start development server: make run')
        self.stdout.write('   2. Access admin: http://localhost:8000/admin/')
        self.stdout.write('   3. Create your first agent: make agents-sync')
        self.stdout.write('   4. Test the platform: make test')
        
        self.stdout.write('\n' + '=' * 50)