"""
Deploy Lightweight Spider Army
===============================

A management command that deploys functional, non-blocking spiders.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import asyncio
import logging
import sys
import os

# Add project to path
sys.path.append('/Users/donkeyking/Donkey_Betz/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

from ai_core.spiders.lightweight_spider_system import (
    create_lightweight_orchestrator
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Deploy lightweight, functional spider army'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            default='deploy',
            choices=['deploy', 'status', 'test'],
            help='Action to perform'
        )
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Run a single test cycle and exit'
        )

    def handle(self, *args, **options):
        action = options['action']

        # Get Redis configuration
        redis_config = {
            'host': settings.REDIS_HOST,
            'port': settings.REDIS_PORT,
            'db': settings.REDIS_DB,
            'decode_responses': True
        }

        self.stdout.write(self.style.SUCCESS('🕷️ Lightweight Spider Army Manager'))

        if action == 'deploy':
            self.deploy_spiders(redis_config, options.get('test_only', False))
        elif action == 'status':
            self.show_status(redis_config)
        elif action == 'test':
            self.test_spiders(redis_config)

    def deploy_spiders(self, redis_config, test_only=False):
        """Deploy the lightweight spider army"""
        self.stdout.write('🚀 Deploying lightweight spider army...')

        orchestrator = create_lightweight_orchestrator(redis_config)

        self.stdout.write(f'✅ Registered {len(orchestrator.spiders)} spiders:')
        for name, spider in orchestrator.spiders.items():
            self.stdout.write(f'  • {name} ({spider.spider_type})')

        if test_only:
            self.stdout.write('\n🧪 Running test cycle...')
            asyncio.run(self.run_test_cycle(orchestrator))
        else:
            self.stdout.write('\n⚡ Starting continuous spider execution...')
            self.stdout.write('Press Ctrl+C to stop\n')

            try:
                asyncio.run(orchestrator.deploy_spiders())
            except KeyboardInterrupt:
                self.stdout.write('\n🛑 Shutting down spider army...')
                asyncio.run(orchestrator.shutdown())

    async def run_test_cycle(self, orchestrator):
        """Run a single test cycle"""
        # Initialize spiders
        for spider in orchestrator.spiders.values():
            await spider.initialize()

        # Run once
        tasks = []
        for spider in orchestrator.spiders.values():
            result = await spider.execute()
            spider.store_result(result)

            if result.success:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {spider.name}: Success')
                )
                # Show sample data
                if spider.spider_type == 'sports' and 'nfl' in result.data:
                    games = result.data['nfl']
                    if games:
                        self.stdout.write(f'   Found {len(games)} NFL games')
                        self.stdout.write(f'   Best bet: {games[0]["best_bet"]}')
                elif spider.spider_type == 'jobs' and 'freelance' in result.data:
                    jobs = result.data['freelance']
                    if jobs:
                        self.stdout.write(f'   Found {len(jobs)} job opportunities')
                        self.stdout.write(f'   Top match: {jobs[0]["title"]}')
                elif spider.spider_type == 'crypto' and 'market_trends' in result.data:
                    trends = result.data['market_trends']
                    self.stdout.write(f'   BTC: ${trends["btc_price"]:,} ({trends["btc_24h_change"]:+.1f}%)')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {spider.name}: {result.error}')
                )

        # Cleanup
        for spider in orchestrator.spiders.values():
            await spider.cleanup()

    def show_status(self, redis_config):
        """Show spider army status"""
        orchestrator = create_lightweight_orchestrator(redis_config)
        status = orchestrator.get_status()

        self.stdout.write('\n📊 Spider Army Status:')
        self.stdout.write(f'Spider count: {status["spider_count"]}')
        self.stdout.write(f'Running: {status["is_running"]}')

        if status.get('stats'):
            stats = status['stats']
            self.stdout.write('\n📈 Statistics:')
            self.stdout.write(f'  Total spiders: {stats.get("total_spiders", 0)}')
            self.stdout.write(f'  Successful runs: {stats.get("successful_runs", 0)}')
            self.stdout.write(f'  Failed runs: {stats.get("failed_runs", 0)}')

            if 'spider_types' in stats:
                self.stdout.write('\n🕷️ Spider Types:')
                for stype, count in stats['spider_types'].items():
                    self.stdout.write(f'  {stype}: {count} spiders')

        if status.get('latest_results'):
            self.stdout.write('\n🔍 Latest Results:')
            for spider_name, result in status['latest_results'].items():
                timestamp = result.get('timestamp', 'Unknown')
                success = '✅' if result.get('success') else '❌'
                self.stdout.write(f'  {spider_name}: {success} ({timestamp})')

    def test_spiders(self, redis_config):
        """Test spider functionality"""
        self.stdout.write('🧪 Testing lightweight spider system...')
        self.deploy_spiders(redis_config, test_only=True)