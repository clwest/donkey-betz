"""
Django Management Command: Activate Spider-Agent Bridge System
==============================================================

This management command activates the complete spider-agent orchestration system,
connecting the 13 working spiders to the 149 agents for real-time intelligence flow.

Usage:
    python manage.py activate_spider_agent_bridge
    python manage.py activate_spider_agent_bridge --spiders toptal guru flexjobs
    python manage.py activate_spider_agent_bridge --status
    python manage.py activate_spider_agent_bridge --stop
"""

from django.core.management.base import BaseCommand, CommandError
import asyncio
import logging
import sys
import os
from typing import List

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from spiders.spider_connector_orchestrator import (
    get_spider_connector_orchestrator
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Activate the complete Spider-Agent Bridge System for real-time intelligence flow'

    def add_arguments(self, parser):
        parser.add_argument(
            '--spiders',
            nargs='+',
            help='Specific spiders to activate (default: all)',
            default=None
        )

        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current orchestration status'
        )

        parser.add_argument(
            '--stop',
            action='store_true',
            help='Stop the orchestration system'
        )

        parser.add_argument(
            '--config',
            type=str,
            help='Path to custom configuration file',
            default=None
        )

        parser.add_argument(
            '--redis-host',
            type=str,
            help='Redis host (default: localhost)',
            default='localhost'
        )

        parser.add_argument(
            '--redis-port',
            type=int,
            help='Redis port (default: 6379)',
            default=6379
        )

        parser.add_argument(
            '--redis-db',
            type=int,
            help='Redis database number (default: 0)',
            default=0
        )

        parser.add_argument(
            '--monitor',
            action='store_true',
            help='Start with monitoring dashboard'
        )

    def handle(self, *args, **options):
        """Handle the management command"""
        try:
            # Setup logging
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

            # Get Redis configuration
            redis_config = {
                'host': options['redis_host'],
                'port': options['redis_port'],
                'db': options['redis_db']
            }

            # Execute based on options
            if options['status']:
                self._show_status(redis_config)
            elif options['stop']:
                self._stop_orchestration(redis_config)
            elif options['spiders']:
                self._activate_specific_spiders(options['spiders'], redis_config)
            else:
                self._activate_complete_system(redis_config, options)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('🛑 Spider-Agent Bridge activation interrupted by user')
            )
        except Exception as e:
            raise CommandError(f'Failed to activate Spider-Agent Bridge: {e}')

    def _show_status(self, redis_config):
        """Show current orchestration status"""
        self.stdout.write(
            self.style.HTTP_INFO('📊 Checking Spider-Agent Bridge Status...')
        )

        try:
            orchestrator = get_spider_connector_orchestrator(redis_config)
            status = orchestrator.get_orchestration_status()

            self.stdout.write('\n' + '='*60)
            self.stdout.write(self.style.SUCCESS('🕷️ SPIDER-AGENT BRIDGE STATUS'))
            self.stdout.write('='*60)

            # System info
            system_info = status['system_info']
            self.stdout.write(f"Orchestrating: {system_info['is_orchestrating']}")
            self.stdout.write(f"Version: {system_info['orchestrator_version']}")

            # Spider network
            spider_network = status['spider_network']
            self.stdout.write(f"\n🕷️ Spider Network:")
            self.stdout.write(f"  Configured: {spider_network['total_configured']}")
            self.stdout.write(f"  Activated: {spider_network['total_activated']}")
            self.stdout.write(f"  Active: {', '.join(spider_network['active_spiders'])}")

            # Agent network
            agent_network = status['agent_network']
            self.stdout.write(f"\n🤖 Agent Network:")
            self.stdout.write(f"  Configured: {agent_network['total_configured']}")
            self.stdout.write(f"  Connected: {agent_network['total_connected']}")

            # Performance metrics
            metrics = status['performance_metrics']
            self.stdout.write(f"\n📊 Performance:")
            self.stdout.write(f"  Data Flows: {metrics['total_data_flows']}")
            self.stdout.write(f"  Flow Rate: {metrics['data_flow_rate_per_minute']:.1f}/min")
            self.stdout.write(f"  Connection Health: {metrics['avg_connection_health']:.1f}%")
            self.stdout.write(f"  System Uptime: {metrics['system_uptime_percentage']:.1f}%")

            self.stdout.write('='*60)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to get status: {e}')
            )

    def _stop_orchestration(self, redis_config):
        """Stop the orchestration system"""
        self.stdout.write(
            self.style.WARNING('🛑 Stopping Spider-Agent Bridge System...')
        )

        try:
            async def stop_system():
                orchestrator = get_spider_connector_orchestrator(redis_config)
                await orchestrator.shutdown_orchestration()

            asyncio.run(stop_system())

            self.stdout.write(
                self.style.SUCCESS('✅ Spider-Agent Bridge System stopped')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to stop system: {e}')
            )

    def _activate_specific_spiders(self, spider_names: List[str], redis_config):
        """Activate specific spiders"""
        self.stdout.write(
            self.style.HTTP_INFO(f'🎯 Activating specific spiders: {", ".join(spider_names)}')
        )

        try:
            async def activate_spiders():
                orchestrator = get_spider_connector_orchestrator(redis_config)
                result = await orchestrator.activate_targeted_spiders(spider_names)
                return result

            result = asyncio.run(activate_spiders())

            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Activated {result["activated"]}/{result["total_requested"]} spiders')
                )

                for spider_result in result['results']:
                    status_style = self.style.SUCCESS if spider_result['status'] == 'activated' else self.style.WARNING
                    self.stdout.write(
                        status_style(f"  {spider_result['spider']}: {spider_result['status']}")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Failed to activate spiders: {result.get("error", "Unknown error")}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to activate spiders: {e}')
            )

    def _activate_complete_system(self, redis_config, options):
        """Activate the complete spider-agent system"""
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Activating Complete Spider-Agent Bridge System...')
        )

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🕷️ SPIDER-AGENT BRIDGE ACTIVATION'))
        self.stdout.write('='*60)

        self.stdout.write('Connecting 13 Working Spiders to 149 Agents...')
        self.stdout.write('')

        # List the 13 working spiders
        working_spiders = [
            'Financial Intelligence Spider',
            'Innovation Tracking Spider',
            'Social Sentiment Spider',
            'Market Data Spider',
            'News Harvester Spider',
            'Toptal Intelligence Spider',
            'Guru Intelligence Spider',
            'PeoplePerHour Intelligence Spider',
            '99Designs Intelligence Spider',
            'FlexJobs Intelligence Spider',
            'RemoteOK Intelligence Spider',
            'Medium Intelligence Spider',
            'Gumroad Intelligence Spider'
        ]

        self.stdout.write('🕷️ Working Spiders:')
        for i, spider in enumerate(working_spiders, 1):
            self.stdout.write(f'  {i:2d}. {spider}')

        self.stdout.write('')
        self.stdout.write('🤖 Target Agents:')
        target_agents = [
            'Job Application Agent',
            'Intelligent Job Matcher',
            'Content Marketplace Agent',
            'Real Content Creator',
            'Zero Capital Income Generator'
        ]

        for i, agent in enumerate(target_agents, 1):
            self.stdout.write(f'  {i}. {agent}')

        self.stdout.write('')
        self.stdout.write('📡 Data Flow: Spider Collection → Intelligent Routing → Agent Processing')
        self.stdout.write('')

        try:
            async def run_complete_orchestration():
                orchestrator = get_spider_connector_orchestrator(redis_config)

                # Log the activation process
                self.stdout.write(self.style.HTTP_INFO('Phase 1: Activating Spider Networks...'))

                # Start orchestration (this will run indefinitely)
                await orchestrator.start_complete_orchestration()

            # Show startup message
            self.stdout.write(self.style.SUCCESS('✅ Initialization complete! Starting orchestration...'))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Press Ctrl+C to stop the system'))
            self.stdout.write('='*60)

            # Run the orchestration system
            asyncio.run(run_complete_orchestration())

        except KeyboardInterrupt:
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('🛑 Orchestration stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Orchestration failed: {e}')
            )
            raise