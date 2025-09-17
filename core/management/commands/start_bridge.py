"""
Django Management Command: Start System Integration Bridge
=========================================================

Start the unified nervous system that connects everything:
python manage.py start_bridge

This starts the bridge that orchestrates:
- Spider deployment
- Agent execution
- WebSocket communication
- Real-time data flow
"""

from django.core.management.base import BaseCommand
import asyncio
import logging
from intelligence.system_integration_bridge import get_system_bridge

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start the System Integration Bridge - The Unified Nervous System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging',
        )

    def handle(self, *args, **options):
        """Handle the command"""
        if options['debug']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        self.stdout.write(
            self.style.SUCCESS('🚀 STARTING SYSTEM INTEGRATION BRIDGE')
        )
        self.stdout.write('=' * 60)
        self.stdout.write('The UNIFIED NERVOUS SYSTEM that connects:')
        self.stdout.write('Frontend → Bridge → Spiders → Agents → WebSocket → Frontend')
        self.stdout.write('=' * 60)

        try:
            # Get the bridge instance
            bridge = get_system_bridge()

            # Run the bridge
            asyncio.run(bridge.start_bridge())

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Bridge shutdown requested')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Bridge error: {e}')
            )
        finally:
            self.stdout.write(
                self.style.SUCCESS('✅ Bridge shutdown complete')
            )