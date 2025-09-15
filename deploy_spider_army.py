#!/usr/bin/env python3
"""
Spider Army Deployment Script
============================

Master deployment script for the complete Spider Army intelligence network.
This script deploys thousands of specialized spiders feeding real-time
intelligence to 102 agents and 25 legendary advisors.

Usage:
    python deploy_spider_army.py --mode full
    python deploy_spider_army.py --mode orchestrator --scale 0.5
    python deploy_spider_army.py --dry-run
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

# Import spider components
from backend.spiders.spider_army_orchestrator import SpiderArmyOrchestrator
from backend.spiders.data_pipeline import RealTimeDataPipeline, get_data_pipeline
from backend.spiders.command_center import SpiderCommandCenter, get_command_center
from backend.spiders.integration import SpiderPlatformIntegration, get_spider_integration


class SpiderArmyDeployer:
    """
    Master deployer for the Spider Army intelligence network.

    Coordinates deployment of:
    - 1,770+ specialized spiders across 10 swarm types
    - Real-time data pipeline processing millions of data points
    - Command center for monitoring and control
    - Integration with 102 agents and 25 advisors
    """

    def __init__(self):
        self.logger = self._setup_logging()
        self.deployment_start = datetime.now()

    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f'spider_army_deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
        return logging.getLogger(__name__)

    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='Deploy the complete Spider Army intelligence network',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --mode full                    # Deploy complete stack
  %(prog)s --mode orchestrator --scale 0.5  # Deploy orchestrator at 50% scale
  %(prog)s --mode pipeline               # Deploy only data pipeline
  %(prog)s --dry-run                     # Show deployment plan without deploying
  %(prog)s --redis-host redis.example.com  # Use custom Redis host
            """
        )

        parser.add_argument(
            '--mode',
            choices=['full', 'orchestrator', 'pipeline', 'command_center', 'integration'],
            default='full',
            help='Deployment mode (default: full)'
        )

        parser.add_argument(
            '--scale',
            type=float,
            default=1.0,
            help='Scale factor for spider deployment (default: 1.0)'
        )

        parser.add_argument(
            '--redis-host',
            default='localhost',
            help='Redis host (default: localhost)'
        )

        parser.add_argument(
            '--redis-port',
            type=int,
            default=6379,
            help='Redis port (default: 6379)'
        )

        parser.add_argument(
            '--command-center-port',
            type=int,
            default=5000,
            help='Command center web interface port (default: 5000)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show deployment plan without actually deploying'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

        parser.add_argument(
            '--background',
            action='store_true',
            help='Run in background (daemon mode)'
        )

        return parser.parse_args()

    def show_deployment_banner(self, args):
        """Show deployment banner with ASCII art"""
        banner = """
██╗   ██╗███╗   ██╗██╗███████╗██╗███████╗██████╗     ██████╗  ██████╗ ███╗   ██╗██╗  ██╗███████╗██╗   ██╗
██║   ██║████╗  ██║██║██╔════╝██║██╔════╝██╔══██╗    ██╔══██╗██╔═══██╗████╗  ██║██║ ██╔╝██╔════╝╚██╗ ██╔╝
██║   ██║██╔██╗ ██║██║█████╗  ██║█████╗  ██║  ██║    ██║  ██║██║   ██║██╔██╗ ██║█████╔╝ █████╗   ╚████╔╝
██║   ██║██║╚██╗██║██║██╔══╝  ██║██╔══╝  ██║  ██║    ██║  ██║██║   ██║██║╚██╗██║██╔═██╗ ██╔══╝    ╚██╔╝
╚██████╔╝██║ ╚████║██║██║     ██║███████╗██████╔╝    ██████╔╝╚██████╔╝██║ ╚████║██║  ██╗███████╗   ██║
 ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝╚═════╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝   ╚═╝

                         🕷️ SPIDER ARMY INTELLIGENCE NETWORK 🕷️
                    Deploying thousands of AI spiders for maximum intelligence
        """

        print(banner)
        print("=" * 100)
        print(f"🚀 DEPLOYMENT MODE: {args.mode.upper()}")
        print(f"⚖️  SCALE FACTOR: {args.scale}")
        print(f"🔗 REDIS: {args.redis_host}:{args.redis_port}")
        print(f"🎯 COMMAND CENTER: http://localhost:{args.command_center_port}")
        print(f"🕐 START TIME: {self.deployment_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)

    def show_deployment_plan(self, args):
        """Show detailed deployment plan"""
        print("\n📋 DEPLOYMENT PLAN")
        print("-" * 50)

        # Calculate spider counts
        base_spider_counts = {
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
        print("🕷️  Spider Army Composition:")
        for spider_type, base_count in base_spider_counts.items():
            scaled_count = int(base_count * args.scale)
            total_spiders += scaled_count
            print(f"   • {spider_type}: {scaled_count:,}")

        print(f"\n📊 Total Spiders: {total_spiders:,}")
        print(f"🤖 Target Agents: 102")
        print(f"🧠 Target Advisors: 25")
        print(f"⚡ Intelligence Channels: ~{total_spiders * 2:,}")

        # Infrastructure components
        print(f"\n🏗️  Infrastructure Components:")
        if args.mode in ['full', 'orchestrator']:
            print("   ✅ Spider Army Orchestrator")
            print("      - Deploys and manages spider swarms")
            print("      - Auto-scaling and health monitoring")
            print("      - Performance optimization")

        if args.mode in ['full', 'pipeline']:
            print("   ✅ Real-Time Data Pipeline")
            print("      - Quality filtering and validation")
            print("      - Intelligent routing to agents/advisors")
            print("      - Message deduplication and aggregation")

        if args.mode in ['full', 'command_center']:
            print("   ✅ Spider Command Center")
            print(f"      - Web interface: http://localhost:{args.command_center_port}")
            print("      - Real-time monitoring and control")
            print("      - Performance analytics and alerts")

        if args.mode in ['full', 'integration']:
            print("   ✅ Platform Integration")
            print("      - Agent intelligence routing")
            print("      - Advisor feed management")
            print("      - Django model integration")

        # Resource requirements
        print(f"\n💻 Estimated Resource Requirements:")
        memory_mb = total_spiders * 2  # ~2MB per spider
        cpu_cores = max(4, total_spiders // 500)  # 1 core per 500 spiders
        disk_gb = max(10, total_spiders // 100)  # Storage for intelligence data

        print(f"   • Memory: ~{memory_mb:,} MB")
        print(f"   • CPU Cores: ~{cpu_cores}")
        print(f"   • Disk Space: ~{disk_gb} GB")

        # Target intelligence rates
        print(f"\n📈 Expected Intelligence Rates:")
        intelligence_per_hour = total_spiders * 10  # ~10 data points per spider per hour
        print(f"   • Intelligence/Hour: ~{intelligence_per_hour:,}")
        print(f"   • Intelligence/Day: ~{intelligence_per_hour * 24:,}")
        print(f"   • Intelligence/Month: ~{intelligence_per_hour * 24 * 30:,}")

    async def deploy(self, args):
        """Main deployment orchestration"""
        try:
            if args.dry_run:
                self.show_deployment_plan(args)
                return

            # Redis configuration
            redis_config = {
                'host': args.redis_host,
                'port': args.redis_port,
                'db': 0
            }

            # Deploy based on mode
            if args.mode == 'full':
                await self._deploy_full_stack(redis_config, args)
            elif args.mode == 'orchestrator':
                await self._deploy_orchestrator(redis_config, args)
            elif args.mode == 'pipeline':
                await self._deploy_pipeline(redis_config, args)
            elif args.mode == 'command_center':
                await self._deploy_command_center(redis_config, args)
            elif args.mode == 'integration':
                await self._deploy_integration(redis_config, args)

        except KeyboardInterrupt:
            self.logger.warning("🛑 Deployment interrupted by user")
        except Exception as e:
            self.logger.error(f"💥 Deployment failed: {e}")
            raise

    async def _deploy_full_stack(self, redis_config, args):
        """Deploy the complete spider army stack"""
        self.logger.info("🚀 Deploying Complete Spider Army Stack...")

        # Create components
        orchestrator = SpiderArmyOrchestrator(redis_config)
        pipeline = get_data_pipeline(redis_config)
        command_center = get_command_center(orchestrator)
        integration = get_spider_integration(redis_config)

        # Apply scale factor
        if args.scale != 1.0:
            self._apply_scale_factor(orchestrator, args.scale)

        # Configure command center
        command_center.port = args.command_center_port

        self.logger.info("🔧 Starting all components...")

        # Start all components concurrently
        tasks = [
            asyncio.create_task(pipeline.start(), name="DataPipeline"),
            asyncio.create_task(orchestrator.deploy_spider_army(), name="SpiderArmy"),
            asyncio.create_task(command_center.start_command_center(), name="CommandCenter"),
            asyncio.create_task(integration.start_integration(), name="PlatformIntegration")
        ]

        self.logger.info("✅ All components deployed successfully!")
        self.logger.info(f"🎯 Command Center: http://localhost:{command_center.port}")
        self.logger.info("🔄 Spider Army is now operational")

        # Wait for all components
        await asyncio.gather(*tasks)

    async def _deploy_orchestrator(self, redis_config, args):
        """Deploy spider army orchestrator only"""
        self.logger.info("🕷️ Deploying Spider Army Orchestrator...")

        orchestrator = SpiderArmyOrchestrator(redis_config)

        if args.scale != 1.0:
            self._apply_scale_factor(orchestrator, args.scale)

        await orchestrator.deploy_spider_army()

    async def _deploy_pipeline(self, redis_config, args):
        """Deploy data pipeline only"""
        self.logger.info("🔄 Deploying Real-Time Data Pipeline...")

        pipeline = get_data_pipeline(redis_config)
        await pipeline.start()

    async def _deploy_command_center(self, redis_config, args):
        """Deploy command center only"""
        self.logger.info("🎯 Deploying Spider Command Center...")

        # Create minimal orchestrator for command center
        orchestrator = SpiderArmyOrchestrator(redis_config)
        command_center = get_command_center(orchestrator)
        command_center.port = args.command_center_port

        self.logger.info(f"🎯 Command Center: http://localhost:{command_center.port}")

        await command_center.start_command_center()

    async def _deploy_integration(self, redis_config, args):
        """Deploy platform integration only"""
        self.logger.info("🔗 Deploying Platform Integration...")

        integration = get_spider_integration(redis_config)
        await integration.start_integration()

    def _apply_scale_factor(self, orchestrator, scale_factor):
        """Apply scale factor to spider deployment"""
        self.logger.info(f"⚖️ Applying scale factor: {scale_factor}")

        for swarm_id, config in orchestrator.swarm_configs.items():
            original_count = config.spider_count
            new_count = max(1, int(original_count * scale_factor))
            config.spider_count = new_count

            self.logger.info(f"   • {swarm_id}: {original_count} → {new_count}")

    def run(self):
        """Main entry point"""
        try:
            args = self.parse_arguments()

            # Configure verbose logging
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)

            # Show banner
            self.show_deployment_banner(args)

            # Run deployment
            if args.background:
                # TODO: Implement daemon mode
                self.logger.warning("Background mode not yet implemented")

            asyncio.run(self.deploy(args))

        except KeyboardInterrupt:
            print("\n🛑 Deployment interrupted")
        except Exception as e:
            print(f"\n💥 Deployment failed: {e}")
            sys.exit(1)


def main():
    """Main function"""
    deployer = SpiderArmyDeployer()
    deployer.run()


if __name__ == '__main__':
    main()