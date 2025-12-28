"""
Start Monitoring Dashboard Management Command
============================================

This Django management command starts the real-time monitoring dashboard
for the Spider-Agent-Connector-Orchestrator system, providing comprehensive
visualization of data flow, performance metrics, and system health.

Usage:
    python manage.py start_monitoring_dashboard

Features:
- Real-time network monitoring
- Spider army performance tracking
- Agent/advisor connection status
- Data flow visualization
- Health alerts and notifications
"""

import asyncio
import logging
import signal
import sys
import threading
from django.core.management.base import BaseCommand

from ...monitoring_dashboard import create_monitoring_dashboard, create_network_monitor

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start the Spider Network Monitoring Dashboard'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = None
        self.dashboard = None
        self.monitor_task = None
        self.is_running = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='0.0.0.0',
            help='Dashboard host address (default: 0.0.0.0)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=5001,
            help='Dashboard port (default: 5001)'
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
            help='Redis port for data pipeline'
        )
        parser.add_argument(
            '--redis-db',
            type=int,
            default=0,
            help='Redis database number'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Run dashboard in debug mode'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        try:
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # Configure Redis
            redis_config = {
                'host': options['redis_host'],
                'port': options['redis_port'],
                'db': options['redis_db']
            }

            self.stdout.write(
                self.style.SUCCESS(
                    "🖥️  Starting Spider Network Monitoring Dashboard"
                )
            )

            # Run the monitoring system
            self._run_monitoring_system(options, redis_config)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Shutdown requested by user"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Fatal error: {e}"))
            logger.error(f"Fatal error in monitoring dashboard: {e}")
            sys.exit(1)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stdout.write(self.style.WARNING(f"\n🛑 Received signal {signum}, initiating shutdown..."))
        self.is_running = False

    def _run_monitoring_system(self, options, redis_config):
        """Run the complete monitoring system"""
        try:
            self.is_running = True

            # Phase 1: Initialize Monitor
            self.stdout.write(self.style.HTTP_INFO("📊 Phase 1: Monitor Initialization"))
            self._initialize_monitor(redis_config)

            # Phase 2: Start Background Monitoring
            self.stdout.write(self.style.HTTP_INFO("🔍 Phase 2: Background Monitoring"))
            self._start_background_monitoring()

            # Phase 3: Initialize Dashboard
            self.stdout.write(self.style.HTTP_INFO("🖥️  Phase 3: Dashboard Initialization"))
            self._initialize_dashboard(options, redis_config)

            # Phase 4: Start Dashboard Server
            self.stdout.write(self.style.HTTP_INFO("🚀 Phase 4: Starting Dashboard Server"))
            self._start_dashboard_server(options)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error in monitoring system: {e}"))
            raise
        finally:
            self._shutdown_monitoring_system()

    def _initialize_monitor(self, redis_config):
        """Initialize the network monitor"""
        try:
            self.monitor = create_network_monitor(redis_config)

            # Test Redis connectivity
            self.monitor.redis_client.ping()

            self.stdout.write("  ✅ Network monitor initialized")
            self.stdout.write("  ✅ Redis connectivity verified")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Monitor initialization failed: {e}"))
            raise

    def _start_background_monitoring(self):
        """Start background monitoring in a separate thread"""
        try:
            def run_monitor():
                """Run the monitor in an asyncio event loop"""
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.monitor.start_monitoring())
                except Exception as e:
                    logger.error(f"Error in background monitoring: {e}")

            # Start monitoring in background thread
            monitor_thread = threading.Thread(target=run_monitor, daemon=True)
            monitor_thread.start()

            # Give it a moment to initialize
            import time
            time.sleep(2)

            self.stdout.write("  ✅ Background monitoring started")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Background monitoring failed: {e}"))
            raise

    def _initialize_dashboard(self, options, redis_config):
        """Initialize the dashboard"""
        try:
            self.dashboard = create_monitoring_dashboard(
                redis_config=redis_config,
                host=options['host'],
                port=options['port']
            )

            self.stdout.write(f"  ✅ Dashboard initialized on {options['host']}:{options['port']}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Dashboard initialization failed: {e}"))
            raise

    def _start_dashboard_server(self, options):
        """Start the dashboard web server"""
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n🎉 MONITORING DASHBOARD READY!\n"
                )
            )

            self.stdout.write("🌐 DASHBOARD ACCESS")
            self.stdout.write("=" * 40)
            self.stdout.write(f"🖥️  Dashboard URL: http://{options['host']}:{options['port']}")
            self.stdout.write(f"📊 Real-time Metrics: Available")
            self.stdout.write(f"🔍 Network Monitoring: Active")
            self.stdout.write(f"⚡ Live Updates: Enabled")
            self.stdout.write("")

            self.stdout.write("📈 MONITORING FEATURES")
            self.stdout.write("-" * 30)
            self.stdout.write("🕷️  Spider Army Performance")
            self.stdout.write("🤖 Agent Connection Status")
            self.stdout.write("🧠 Advisor Analytics")
            self.stdout.write("🔄 Data Flow Visualization")
            self.stdout.write("💚 Health Monitoring")
            self.stdout.write("🚨 Real-time Alerts")
            self.stdout.write("")

            self.stdout.write("📋 DASHBOARD ENDPOINTS")
            self.stdout.write("-" * 30)
            self.stdout.write(f"📊 Current Metrics: http://{options['host']}:{options['port']}/api/metrics/current")
            self.stdout.write(f"📈 Metrics History: http://{options['host']}:{options['port']}/api/metrics/history")
            self.stdout.write(f"🚨 Alerts: http://{options['host']}:{options['port']}/api/alerts")
            self.stdout.write("")

            self.stdout.write(self.style.WARNING("Press Ctrl+C to stop the dashboard"))
            self.stdout.write("")

            # Run the dashboard (this blocks)
            self.dashboard.run(debug=options['debug'])

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Dashboard server failed: {e}"))
            raise

    def _shutdown_monitoring_system(self):
        """Shutdown the monitoring system"""
        try:
            self.stdout.write("\n🛑 Shutting down monitoring system...")

            # The monitor will shutdown automatically when the main thread exits
            # since it's running in a daemon thread

            self.stdout.write(
                self.style.SUCCESS("✅ Monitoring system shutdown complete")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Shutdown error: {e}"))
            logger.error(f"Shutdown error: {e}")