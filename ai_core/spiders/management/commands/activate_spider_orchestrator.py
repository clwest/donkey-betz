"""
Activate Spider-Agent-Connector-Orchestrator Management Command
===============================================================

This Django management command activates the complete spider-agent-connector
ecosystem, establishing connections between 1,770+ spiders and 102 agents
plus 25+ advisors with real-time intelligence distribution.

Usage:
    python manage.py activate_spider_orchestrator

Features:
- Coordinated spider army deployment in waves
- Real-time data pipeline activation
- Agent and advisor connection establishment
- Performance monitoring and health checks
- Graceful shutdown handling
"""

import asyncio
import logging
import signal
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from datetime import datetime, timezone

# Import our spider orchestration components
from ...spider_data_router import SpiderDataRouter, get_spider_data_router
from ...agent_data_receiver import create_agent_data_receiver
from ...advisor_data_processor import create_advisor_data_processor
from ....agents.registry import get_agent_registry
from ....advisors.registry import get_advisor_registry

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Activate the Spider-Agent-Connector-Orchestrator System'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.router = None
        self.agent_receivers = {}
        self.advisor_processors = {}
        self.is_running = False

    def add_arguments(self, parser):
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
            '--skip-spiders',
            action='store_true',
            help='Skip spider deployment (for testing routing only)'
        )
        parser.add_argument(
            '--target-agents',
            type=str,
            nargs='*',
            help='Specific agents to connect (default: all)'
        )
        parser.add_argument(
            '--target-advisors',
            type=str,
            nargs='*',
            help='Specific advisors to connect (default: all)'
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
                    "🚀 Activating Spider-Agent-Connector-Orchestrator System"
                )
            )

            # Run the orchestrator
            asyncio.run(self._run_orchestrator(options, redis_config))

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Shutdown requested by user"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Fatal error: {e}"))
            logger.error(f"Fatal error in orchestrator: {e}")
            sys.exit(1)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stdout.write(self.style.WARNING(f"\n🛑 Received signal {signum}, initiating shutdown..."))
        self.is_running = False

    async def _run_orchestrator(self, options, redis_config):
        """Run the complete orchestrator system"""
        try:
            self.is_running = True

            # Phase 1: Initialize Infrastructure
            self.stdout.write(self.style.HTTP_INFO("📋 Phase 1: Infrastructure Initialization"))
            await self._initialize_infrastructure(redis_config)

            # Phase 2: Deploy Spider Army (if not skipped)
            if not options['skip_spiders']:
                self.stdout.write(self.style.HTTP_INFO("🕷️  Phase 2: Spider Army Deployment"))
                await self._deploy_spider_army()
            else:
                self.stdout.write(self.style.WARNING("⏭️  Skipping spider deployment"))

            # Phase 3: Connect Agents
            self.stdout.write(self.style.HTTP_INFO("🤖 Phase 3: Agent Connection"))
            await self._connect_agents(options.get('target_agents'), redis_config)

            # Phase 4: Connect Advisors
            self.stdout.write(self.style.HTTP_INFO("🧠 Phase 4: Advisor Connection"))
            await self._connect_advisors(options.get('target_advisors'), redis_config)

            # Phase 5: Start Data Routing
            self.stdout.write(self.style.HTTP_INFO("🔄 Phase 5: Data Routing Activation"))
            await self._start_data_routing()

            # Phase 6: Monitoring and Maintenance
            self.stdout.write(self.style.SUCCESS("✅ All Systems Operational"))
            await self._monitoring_loop()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error in orchestrator: {e}"))
            raise
        finally:
            await self._shutdown_all_systems()

    async def _initialize_infrastructure(self, redis_config):
        """Initialize the core infrastructure"""
        try:
            # Initialize the main router
            self.router = get_spider_data_router(redis_config)
            await self.router.initialize_router_infrastructure()

            self.stdout.write("  ✅ Router infrastructure initialized")

            # Test Redis connectivity
            await self.router.redis_async.ping()
            self.stdout.write("  ✅ Redis connectivity verified")

            self.stdout.write(
                self.style.SUCCESS(
                    f"  📊 Routing tables: {len(self.router.routing_tables)} swarms"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  🔗 Connection mappings: {self.router.metrics.total_connections}"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Infrastructure initialization failed: {e}"))
            raise

    async def _deploy_spider_army(self):
        """Deploy the spider army in coordinated waves"""
        try:
            self.stdout.write("  🌊 Deploying spiders in coordinated waves...")

            # Deploy spider army
            await self.router.activate_spider_army()

            # Get deployment status
            army_status = self.router.spider_orchestrator.get_army_status()

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ Spider Army Deployed: {army_status['army_stats']['total_spiders']} total spiders"
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"  🎯 Active Spiders: {army_status['army_stats']['active_spiders']}"
                )
            )

            # Display swarm distribution
            for swarm_id, count in army_status['swarm_distribution'].items():
                self.stdout.write(f"    📡 {swarm_id}: {count} spiders")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Spider deployment failed: {e}"))
            raise

    async def _connect_agents(self, target_agents, redis_config):
        """Connect agents to spider data streams"""
        try:
            agent_registry = get_agent_registry()

            # Get agents to connect
            if target_agents:
                agents_to_connect = target_agents
                self.stdout.write(f"  🎯 Connecting specific agents: {', '.join(target_agents)}")
            else:
                # Get all active agents
                all_agents = agent_registry.list_agents()
                agents_to_connect = [agent['name'] for agent in all_agents[:20]]  # Limit for demo
                self.stdout.write(f"  🤖 Connecting {len(agents_to_connect)} agents")

            # Connect each agent
            connection_tasks = []
            for agent_name in agents_to_connect:
                task = asyncio.create_task(
                    self._connect_single_agent(agent_name, redis_config)
                )
                connection_tasks.append(task)

            # Wait for all agent connections
            results = await asyncio.gather(*connection_tasks, return_exceptions=True)

            # Count successful connections
            successful = sum(1 for result in results if not isinstance(result, Exception))

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ Agent Connections: {successful}/{len(agents_to_connect)} successful"
                )
            )

            # Display connection details
            for agent_name in list(self.agent_receivers.keys())[:5]:  # Show first 5
                self.stdout.write(f"    🔌 {agent_name}: Connected")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Agent connection failed: {e}"))
            raise

    async def _connect_single_agent(self, agent_name, redis_config):
        """Connect a single agent to data streams"""
        try:
            # Determine agent type (simplified - would use registry data)
            agent_type = self._determine_agent_type(agent_name)

            # Create agent data receiver
            agent_receiver = create_agent_data_receiver(agent_name, agent_type, redis_config)

            # Store reference
            self.agent_receivers[agent_name] = agent_receiver

            # Start the receiver (non-blocking)
            asyncio.create_task(agent_receiver.start_data_receiver())

            logger.info(f"Connected agent: {agent_name}")

        except Exception as e:
            logger.error(f"Failed to connect agent {agent_name}: {e}")
            raise

    async def _connect_advisors(self, target_advisors, redis_config):
        """Connect advisors to spider data streams"""
        try:
            advisor_registry = get_advisor_registry()

            # Get advisors to connect
            if target_advisors:
                advisors_to_connect = target_advisors
                self.stdout.write(f"  🎯 Connecting specific advisors: {', '.join(target_advisors)}")
            else:
                # Get all advisors
                all_advisors = advisor_registry.list_advisors()
                advisors_to_connect = [advisor.id for advisor in all_advisors[:10]]  # Limit for demo
                self.stdout.write(f"  🧠 Connecting {len(advisors_to_connect)} advisors")

            # Connect each advisor
            connection_tasks = []
            for advisor_id in advisors_to_connect:
                task = asyncio.create_task(
                    self._connect_single_advisor(advisor_id, redis_config)
                )
                connection_tasks.append(task)

            # Wait for all advisor connections
            results = await asyncio.gather(*connection_tasks, return_exceptions=True)

            # Count successful connections
            successful = sum(1 for result in results if not isinstance(result, Exception))

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✅ Advisor Connections: {successful}/{len(advisors_to_connect)} successful"
                )
            )

            # Highlight key advisors
            key_advisors = ['warren_buffett', 'cathie_wood', 'ray_dalio', 'crypto_expert']
            for advisor_id in key_advisors:
                if advisor_id in self.advisor_processors:
                    self.stdout.write(f"    🌟 {advisor_id}: Connected")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Advisor connection failed: {e}"))
            raise

    async def _connect_single_advisor(self, advisor_id, redis_config):
        """Connect a single advisor to data streams"""
        try:
            # Create advisor data processor
            advisor_processor = create_advisor_data_processor(advisor_id, redis_config)

            # Store reference
            self.advisor_processors[advisor_id] = advisor_processor

            # Start the processor (non-blocking)
            asyncio.create_task(advisor_processor.start_data_receiver())

            logger.info(f"Connected advisor: {advisor_id}")

        except Exception as e:
            logger.error(f"Failed to connect advisor {advisor_id}: {e}")
            raise

    async def _start_data_routing(self):
        """Start the real-time data routing system"""
        try:
            # Start data routing (non-blocking)
            asyncio.create_task(self.router.start_data_routing())

            self.stdout.write("  ✅ Data routing system activated")

            # Verify routing is working
            await asyncio.sleep(2)
            router_status = self.router.get_router_status()

            self.stdout.write(
                self.style.SUCCESS(
                    f"  📊 Router Status: {router_status['metrics']['total_connections']} connections"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Data routing startup failed: {e}"))
            raise

    async def _monitoring_loop(self):
        """Main monitoring and status reporting loop"""
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    "\n🎉 SPIDER-AGENT-CONNECTOR-ORCHESTRATOR ACTIVATED!\n"
                )
            )

            # Display system summary
            await self._display_system_summary()

            self.stdout.write("\n📊 Real-time monitoring active (Ctrl+C to stop)...")

            # Monitoring loop
            cycle = 0
            while self.is_running:
                await asyncio.sleep(30)  # Update every 30 seconds
                cycle += 1

                if cycle % 2 == 0:  # Every minute
                    await self._display_status_update()

                if cycle % 10 == 0:  # Every 5 minutes
                    await self._display_detailed_metrics()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Monitoring error: {e}"))

    async def _display_system_summary(self):
        """Display initial system summary"""
        try:
            router_status = self.router.get_router_status()

            self.stdout.write("🌐 SYSTEM OVERVIEW")
            self.stdout.write("=" * 50)
            self.stdout.write(f"🕷️  Total Spiders: {router_status['spider_army_status']['army_stats']['total_spiders']}")
            self.stdout.write(f"🤖 Connected Agents: {len(self.agent_receivers)}")
            self.stdout.write(f"🧠 Connected Advisors: {len(self.advisor_processors)}")
            self.stdout.write(f"🔗 Total Connections: {router_status['metrics']['total_connections']}")
            self.stdout.write(f"📡 Active Channels: {sum(router_status['subscriber_channels'].values())}")
            self.stdout.write("")

            # Show key connections
            self.stdout.write("🌟 KEY CONNECTIONS")
            self.stdout.write("-" * 30)

            # Income Builder connection
            if 'income_builder_agent' in self.agent_receivers:
                self.stdout.write("💰 Income Builder Agent: CONNECTED")

            # Warren Buffett connection
            if 'warren_buffett' in self.advisor_processors:
                self.stdout.write("📈 Warren Buffett Advisor: CONNECTED")

            # Cathie Wood connection
            if 'cathie_wood' in self.advisor_processors:
                self.stdout.write("🚀 Cathie Wood Advisor: CONNECTED")

            self.stdout.write("")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error displaying summary: {e}"))

    async def _display_status_update(self):
        """Display periodic status update"""
        try:
            router_status = self.router.get_router_status()
            current_time = datetime.now(timezone.utc).strftime("%H:%M:%S")

            # Short status line
            active_spiders = router_status['spider_army_status']['army_stats']['active_spiders']
            messages_routed = router_status['metrics']['messages_routed']
            connection_health = router_status['metrics']['connection_health']

            self.stdout.write(
                f"[{current_time}] 🕷️ {active_spiders} active | "
                f"📨 {messages_routed} routed | "
                f"💚 {connection_health:.1f}% health"
            )

        except Exception as e:
            self.stdout.write(f"Status update error: {e}")

    async def _display_detailed_metrics(self):
        """Display detailed performance metrics"""
        try:
            router_status = self.router.get_router_status()

            self.stdout.write("\n📊 DETAILED METRICS")
            self.stdout.write("-" * 40)

            # Spider metrics
            spider_stats = router_status['spider_army_status']['army_stats']
            self.stdout.write(f"🕷️  Spider Army: {spider_stats['active_spiders']}/{spider_stats['total_spiders']} active")

            # Routing metrics
            routing_metrics = router_status['metrics']
            self.stdout.write(f"📨 Messages Routed: {routing_metrics['messages_routed']}")
            self.stdout.write(f"❌ Failed Routes: {routing_metrics['failed_routes']}")

            # Top performers
            if router_status['top_performers']['producers']:
                top_producer = router_status['top_performers']['producers'][0]
                self.stdout.write(f"🥇 Top Producer: {top_producer[0]} ({top_producer[1]} messages)")

            if router_status['top_performers']['consumers']:
                top_consumer = router_status['top_performers']['consumers'][0]
                self.stdout.write(f"🏆 Top Consumer: {top_consumer[0]} ({top_consumer[1]} messages)")

            self.stdout.write("")

        except Exception as e:
            self.stdout.write(f"Detailed metrics error: {e}")

    def _determine_agent_type(self, agent_name):
        """Determine agent type from name (simplified)"""
        if any(term in agent_name.lower() for term in ['financial', 'income', 'dividend']):
            return 'financial'
        elif any(term in agent_name.lower() for term in ['innovation', 'ai', 'tech']):
            return 'innovation'
        else:
            return 'general'

    async def _shutdown_all_systems(self):
        """Gracefully shutdown all systems"""
        try:
            self.stdout.write("\n🛑 Initiating system shutdown...")

            # Shutdown agents
            if self.agent_receivers:
                self.stdout.write("  🤖 Shutting down agents...")
                for agent_name, receiver in self.agent_receivers.items():
                    try:
                        await receiver.shutdown()
                    except Exception as e:
                        logger.error(f"Error shutting down agent {agent_name}: {e}")

            # Shutdown advisors
            if self.advisor_processors:
                self.stdout.write("  🧠 Shutting down advisors...")
                for advisor_id, processor in self.advisor_processors.items():
                    try:
                        await processor.shutdown()
                    except Exception as e:
                        logger.error(f"Error shutting down advisor {advisor_id}: {e}")

            # Shutdown router
            if self.router:
                self.stdout.write("  🔄 Shutting down router...")
                await self.router.shutdown()

            self.stdout.write(
                self.style.SUCCESS("✅ All systems shutdown complete")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Shutdown error: {e}"))
            logger.error(f"Shutdown error: {e}")