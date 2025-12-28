"""
Deploy Spider Army Management Command
====================================

Django management command to deploy the complete spider army infrastructure
with thousands of specialized spiders feeding intelligence to 102 agents
and 25 legendary advisors.
"""

import asyncio
import logging
from django.core.management.base import BaseCommand, CommandError

from ai_core.spiders.spider_army_orchestrator import SpiderArmyOrchestrator
from ai_core.spiders.command_center import get_command_center
from ai_core.spiders.data_pipeline import get_data_pipeline


class Command(BaseCommand):
    help = 'Deploy the complete Spider Army intelligence network'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['full', 'orchestrator', 'pipeline', 'command_center'],
            default='full',
            help='Deployment mode'
        )

        parser.add_argument(
            '--redis-host',
            type=str,
            default='localhost',
            help='Redis host for data pipeline'
        )

        parser.add_argument(
            '--redis-port',
            type=int,
            default=6379,
            help='Redis port'
        )

        parser.add_argument(
            '--command-center-port',
            type=int,
            default=5000,
            help='Port for Spider Command Center web interface'
        )

        parser.add_argument(
            '--scale-factor',
            type=float,
            default=1.0,
            help='Scale factor for spider deployment (0.1 = 10%, 2.0 = 200%)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deployed without actually deploying'
        )

    def handle(self, *args, **options):
        """Handle the deployment command"""

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Redis configuration
        redis_config = {
            'host': options['redis_host'],
            'port': options['redis_port'],
            'db': 0
        }

        self.stdout.write(
            self.style.SUCCESS('🕷️ DEPLOYING SPIDER ARMY INTELLIGENCE NETWORK 🕷️')
        )

        if options['dry_run']:
            self._show_deployment_plan(options)
            return

        # Run deployment based on mode
        mode = options['mode']

        try:
            if mode == 'full':
                asyncio.run(self._deploy_full_stack(redis_config, options))
            elif mode == 'orchestrator':
                asyncio.run(self._deploy_orchestrator_only(redis_config, options))
            elif mode == 'pipeline':
                asyncio.run(self._deploy_pipeline_only(redis_config, options))
            elif mode == 'command_center':
                asyncio.run(self._deploy_command_center_only(redis_config, options))

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Deployment interrupted by user')
            )
        except Exception as e:
            raise CommandError(f'Deployment failed: {e}')

    def _show_deployment_plan(self, options):
        """Show what would be deployed"""
        self.stdout.write(self.style.WARNING('DRY RUN - Deployment Plan:'))
        self.stdout.write('')

        scale_factor = options['scale_factor']

        # Calculate spider counts
        base_counts = {
            'Financial Intelligence Spiders': 500,
            'Innovation Tracking Spiders': 300,
            'Market Data Spiders': 200,
            'Social Sentiment Spiders': 150,
            'News Harvesting Spiders': 120,
            'Research Paper Spiders': 100,
            'Patent Monitoring Spiders': 80,
            'Regulatory Tracking Spiders': 70,
            'Competitive Intelligence Spiders': 50,
            'Adaptive General Purpose Spiders': 200
        }

        total_spiders = 0

        self.stdout.write('📊 Spider Army Composition:')
        for spider_type, base_count in base_counts.items():
            scaled_count = int(base_count * scale_factor)
            total_spiders += scaled_count
            self.stdout.write(f'  • {spider_type}: {scaled_count:,}')

        self.stdout.write('')
        self.stdout.write(f'🎯 Total Spiders: {total_spiders:,}')
        self.stdout.write(f'🤖 Target Agents: 102')
        self.stdout.write(f'🧠 Target Advisors: 25')
        self.stdout.write(f'⚡ Intelligence Channels: ~{total_spiders * 2}')

        self.stdout.write('')
        self.stdout.write('🏗️ Infrastructure Components:')

        if options['mode'] in ['full', 'orchestrator']:
            self.stdout.write('  ✅ Spider Army Orchestrator')

        if options['mode'] in ['full', 'pipeline']:
            self.stdout.write('  ✅ Real-Time Data Pipeline')

        if options['mode'] in ['full', 'command_center']:
            self.stdout.write(f"  ✅ Command Center (port {options['command_center_port']})")

        self.stdout.write('')
        self.stdout.write(f"🔗 Redis Connection: {options['redis_host']}:{options['redis_port']}")

    async def _deploy_full_stack(self, redis_config, options):
        """Deploy the complete spider army stack"""
        self.stdout.write('🚀 Deploying Full Spider Army Stack...')

        # Create orchestrator
        orchestrator = SpiderArmyOrchestrator(redis_config)

        # Apply scale factor
        scale_factor = options['scale_factor']
        if scale_factor != 1.0:
            self._apply_scale_factor(orchestrator, scale_factor)

        # Create data pipeline
        pipeline = get_data_pipeline(redis_config)

        # Create command center
        command_center = get_command_center(orchestrator)
        command_center.port = options['command_center_port']

        # Start all components
        tasks = [
            asyncio.create_task(pipeline.start(), name="DataPipeline"),
            asyncio.create_task(orchestrator.deploy_spider_army(), name="SpiderArmy"),
            asyncio.create_task(command_center.start_command_center(), name="CommandCenter")
        ]

        self.stdout.write('✅ All components starting...')
        self.stdout.write(f'🎯 Command Center available at: http://localhost:{command_center.port}')

        # Wait for all components
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Component failed: {e}'))
            raise

    async def _deploy_orchestrator_only(self, redis_config, options):
        """Deploy only the spider army orchestrator"""
        self.stdout.write('🕷️ Deploying Spider Army Orchestrator...')

        orchestrator = SpiderArmyOrchestrator(redis_config)

        # Apply scale factor
        scale_factor = options['scale_factor']
        if scale_factor != 1.0:
            self._apply_scale_factor(orchestrator, scale_factor)

        await orchestrator.deploy_spider_army()

    async def _deploy_pipeline_only(self, redis_config, options):
        """Deploy only the data pipeline"""
        self.stdout.write('🔄 Deploying Real-Time Data Pipeline...')

        pipeline = get_data_pipeline(redis_config)
        await pipeline.start()

    async def _deploy_command_center_only(self, redis_config, options):
        """Deploy only the command center"""
        self.stdout.write('🎯 Deploying Spider Command Center...')

        # Create a minimal orchestrator for the command center
        orchestrator = SpiderArmyOrchestrator(redis_config)
        command_center = get_command_center(orchestrator)
        command_center.port = options['command_center_port']

        self.stdout.write(f'🎯 Command Center available at: http://localhost:{command_center.port}')

        await command_center.start_command_center()

    def _apply_scale_factor(self, orchestrator, scale_factor):
        """Apply scale factor to spider counts"""
        self.stdout.write(f'⚖️ Applying scale factor: {scale_factor}')

        for swarm_id, config in orchestrator.swarm_configs.items():
            original_count = config.spider_count
            new_count = max(1, int(original_count * scale_factor))
            config.spider_count = new_count

            self.stdout.write(f'  • {swarm_id}: {original_count} → {new_count}')

    def _get_deployment_summary(self, orchestrator, pipeline, command_center):
        """Get deployment summary"""
        total_spiders = sum(
            config.spider_count
            for config in orchestrator.swarm_configs.values()
        )

        return {
            'total_spiders': total_spiders,
            'swarm_count': len(orchestrator.swarm_configs),
            'pipeline_status': pipeline.status.value if pipeline else 'not_deployed',
            'command_center_port': command_center.port if command_center else None
        }