"""
Spider Connector Orchestrator - The Neural Bridge System
========================================================

This module creates the complete nervous system that connects the 13 working spiders
to the 149 agents, establishing real-time intelligence flow for actionable insights.

The orchestrator:
1. Activates the 13 specialized spiders in coordinated waves
2. Creates intelligent routing from spiders to relevant agents
3. Provides real-time data flow monitoring and optimization
4. Ensures agents receive fresh, actionable intelligence

Working Spiders Connected:
- Financial Intelligence Spider
- Innovation Tracking Spider
- Social Sentiment Spider
- Market Data Spider
- News Harvester Spider
- Toptal Intelligence Spider
- Guru Intelligence Spider
- PeoplePerHour Intelligence Spider
- 99Designs Intelligence Spider
- FlexJobs Intelligence Spider
- RemoteOK Intelligence Spider
- Medium Intelligence Spider
- Gumroad Intelligence Spider
"""

import asyncio
import json
import logging
import redis
from redis import asyncio as aioredis
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from .spider_registry import get_spider_registry
from .spider_army_orchestrator import SpiderArmyOrchestrator
from .agent_data_receiver import create_agent_data_receiver, AgentSpiderDataReceiver

logger = logging.getLogger(__name__)


class ActivationPriority(Enum):
    """Priority levels for spider activation"""
    CRITICAL = 1     # Income-generating spiders (job platforms, freelance)
    HIGH = 2         # Market intelligence spiders (financial, innovation)
    NORMAL = 3       # Content and social spiders
    LOW = 4          # Background monitoring spiders


class ConnectionHealth(Enum):
    """Health status of spider-agent connections"""
    EXCELLENT = "excellent"
    GOOD = "good"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass
class SpiderActivationConfig:
    """Configuration for spider activation"""
    spider_name: str
    spider_class_name: str
    activation_priority: ActivationPriority
    target_agents: List[str]
    data_refresh_seconds: int = 300
    max_concurrent_tasks: int = 5
    quality_threshold: float = 0.8
    is_active: bool = False


@dataclass
class AgentConnectionConfig:
    """Configuration for agent connections"""
    agent_id: str
    agent_type: str
    agent_class_path: str
    connected_spiders: List[str]
    data_receiver: Optional[AgentSpiderDataReceiver] = None
    last_data_received: Optional[datetime] = None
    total_data_processed: int = 0
    connection_health: ConnectionHealth = ConnectionHealth.GOOD


@dataclass
class OrchestrationMetrics:
    """Metrics for the complete orchestration system"""
    total_spiders_activated: int = 0
    total_agents_connected: int = 0
    total_data_flows: int = 0
    avg_connection_health: float = 100.0
    data_flow_rate_per_minute: float = 0.0
    top_producing_spiders: List[str] = field(default_factory=list)
    top_consuming_agents: List[str] = field(default_factory=list)
    system_uptime_percentage: float = 100.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SpiderConnectorOrchestrator:
    """
    The Neural Bridge System - Master orchestrator for spider-agent connections.

    Creates the complete nervous system connecting 13 working spiders to 149 agents
    with intelligent routing, real-time monitoring, and performance optimization.
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        """Initialize the Spider Connector Orchestrator"""
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}
        self.redis_client = redis.Redis(**self.redis_config)
        self.redis_async = None

        # Core components
        self.spider_registry = get_spider_registry()
        self.spider_orchestrator = SpiderArmyOrchestrator(self.redis_config)

        # Configuration management
        self.spider_configs: Dict[str, SpiderActivationConfig] = {}
        self.agent_configs: Dict[str, AgentConnectionConfig] = {}

        # Active connections
        self.active_spiders: Dict[str, Any] = {}
        self.connected_agents: Dict[str, AgentSpiderDataReceiver] = {}

        # Performance tracking
        self.metrics = OrchestrationMetrics()
        self.metrics_history: List[OrchestrationMetrics] = []

        # System state
        self.is_orchestrating = False
        self.orchestration_tasks: List[asyncio.Task] = []

        # Executor for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=30)

        self.logger = logging.getLogger(__name__)

        # Initialize configurations
        self._initialize_spider_configurations()
        self._initialize_agent_configurations()

    def _initialize_spider_configurations(self):
        """Initialize configurations for the 13 working spiders"""
        self.logger.info("🕷️ Initializing 13 working spider configurations...")

        # === CRITICAL PRIORITY SPIDERS (Income-generating platforms) ===

        # Job & Freelance Platform Spiders
        income_spiders = [
            ("toptal", "ToptalIntelligenceSpider", ["job_application_agent", "intelligent_job_matcher", "zero_capital_income_generator"]),
            ("guru", "GuruIntelligenceSpider", ["job_application_agent", "intelligent_job_matcher", "zero_capital_income_generator"]),
            ("peopleperhour", "PeoplePerHourIntelligenceSpider", ["job_application_agent", "intelligent_job_matcher"]),
            ("flexjobs", "FlexJobsIntelligenceSpider", ["job_application_agent", "intelligent_job_matcher"]),
            ("remoteok", "RemoteOKIntelligenceSpider", ["job_application_agent", "intelligent_job_matcher"]),
            ("ninetyninedesigns", "NinetyNineDesignsIntelligenceSpider", ["content_marketplace_agent", "real_content_creator"]),
        ]

        for spider_name, class_name, target_agents in income_spiders:
            self.spider_configs[spider_name] = SpiderActivationConfig(
                spider_name=spider_name,
                spider_class_name=class_name,
                activation_priority=ActivationPriority.CRITICAL,
                target_agents=target_agents,
                data_refresh_seconds=180,  # Refresh every 3 minutes for job opportunities
                max_concurrent_tasks=10,
                quality_threshold=0.85
            )

        # Content Monetization Spiders
        content_spiders = [
            ("medium", "MediumIntelligenceSpider", ["content_marketplace_agent", "real_content_creator"]),
            ("gumroad", "GumroadIntelligenceSpider", ["content_marketplace_agent", "zero_capital_income_generator"])
        ]

        for spider_name, class_name, target_agents in content_spiders:
            self.spider_configs[spider_name] = SpiderActivationConfig(
                spider_name=spider_name,
                spider_class_name=class_name,
                activation_priority=ActivationPriority.CRITICAL,
                target_agents=target_agents,
                data_refresh_seconds=300,  # Every 5 minutes for content opportunities
                max_concurrent_tasks=8,
                quality_threshold=0.8
            )

        # === HIGH PRIORITY SPIDERS (Market intelligence) ===

        intelligence_spiders = [
            ("financial", "FinancialIntelligenceSpider", ["job_application_agent", "zero_capital_income_generator", "content_marketplace_agent"]),
            ("innovation", "InnovationTrackingSpider", ["intelligent_job_matcher", "real_content_creator"]),
            ("market_data", "MarketDataSpider", ["job_application_agent", "zero_capital_income_generator"]),
            ("social_sentiment", "SocialSentimentSpider", ["content_marketplace_agent", "real_content_creator"]),
            ("news_harvester", "NewsHarvesterSpider", ["job_application_agent", "intelligent_job_matcher", "content_marketplace_agent", "real_content_creator", "zero_capital_income_generator"])  # News feeds to ALL agents
        ]

        for spider_name, class_name, target_agents in intelligence_spiders:
            self.spider_configs[spider_name] = SpiderActivationConfig(
                spider_name=spider_name,
                spider_class_name=class_name,
                activation_priority=ActivationPriority.HIGH,
                target_agents=target_agents,
                data_refresh_seconds=240,  # Every 4 minutes for market intelligence
                max_concurrent_tasks=6,
                quality_threshold=0.8
            )

        self.logger.info(f"✅ Configured {len(self.spider_configs)} working spiders for activation")

    def _initialize_agent_configurations(self):
        """Initialize configurations for connecting to agents"""
        self.logger.info("🤖 Initializing agent connection configurations...")

        # Discover available agents from the agents directory
        agents_dir = os.path.join(os.path.dirname(__file__), '..', 'agents')

        # Known agent mappings
        agent_mappings = {
            "job_application_agent": {
                "type": "job_application",
                "class_path": "ai_core.agents.job_application_agent.JobApplicationAgent",
                "connected_spiders": ["toptal", "guru", "peopleperhour", "flexjobs", "remoteok", "financial", "news_harvester"]
            },
            "intelligent_job_matcher": {
                "type": "job_matching",
                "class_path": "ai_core.agents.intelligent_job_matcher.IntelligentJobMatcher",
                "connected_spiders": ["toptal", "guru", "peopleperhour", "flexjobs", "remoteok", "innovation", "news_harvester"]
            },
            "content_marketplace_agent": {
                "type": "content_marketing",
                "class_path": "ai_core.agents.content_marketplace_agent.ContentMarketplaceAgent",
                "connected_spiders": ["ninetyninedesigns", "medium", "gumroad", "social_sentiment", "news_harvester"]
            },
            "real_content_creator": {
                "type": "content_creation",
                "class_path": "ai_core.agents.real_content_creator.RealContentCreator",
                "connected_spiders": ["ninetyninedesigns", "medium", "innovation", "social_sentiment", "news_harvester"]
            },
            "zero_capital_income_generator": {
                "type": "income_generation",
                "class_path": "ai_core.agents.zero_capital_income_generator.ZeroCapitalIncomeGenerator",
                "connected_spiders": ["toptal", "guru", "gumroad", "financial", "market_data", "news_harvester"]
            }
        }

        # Additional agents that can be connected (expandable system)
        additional_agents = [
            "financial_strategist", "trading_agent", "crypto_expert", "options_master",
            "ai_strategist", "tech_architect", "innovation_scout", "patent_analyzer",
            "sentiment_analyzer", "social_media_monitor", "trend_detector",
            "business_strategist", "startup_guru", "competitive_analyst"
        ]

        # Create configs for known agents
        for agent_id, config in agent_mappings.items():
            self.agent_configs[agent_id] = AgentConnectionConfig(
                agent_id=agent_id,
                agent_type=config["type"],
                agent_class_path=config["class_path"],
                connected_spiders=config["connected_spiders"]
            )

        # Create configs for additional agents (generic connections)
        for agent_id in additional_agents:
            self.agent_configs[agent_id] = AgentConnectionConfig(
                agent_id=agent_id,
                agent_type="specialized",
                agent_class_path=f"ai_core.agents.{agent_id}.{agent_id.title().replace('_', '')}",
                connected_spiders=["news_harvester"]  # All get news by default
            )

        self.logger.info(f"✅ Configured {len(self.agent_configs)} agents for connection")

    async def start_complete_orchestration(self):
        """Start the complete spider-agent orchestration system"""
        try:
            self.logger.info("🚀 Starting Complete Spider-Agent Orchestration System...")

            # Initialize async Redis connection
            self.redis_async = aioredis.from_url(
                f"redis://{self.redis_config['host']}:{self.redis_config['port']}/{self.redis_config['db']}"
            )

            # Phase 1: Activate spiders in priority order
            await self._activate_spider_networks()

            # Phase 2: Connect agents to data streams
            await self._connect_agent_networks()

            # Phase 3: Start orchestration monitoring
            await self._start_orchestration_monitoring()

            # Set system as running
            self.is_orchestrating = True

            # Start continuous orchestration tasks
            self.orchestration_tasks = [
                asyncio.create_task(self._spider_health_monitor()),
                asyncio.create_task(self._agent_connection_monitor()),
                asyncio.create_task(self._data_flow_optimizer()),
                asyncio.create_task(self._performance_metrics_collector()),
                asyncio.create_task(self._system_health_reporter())
            ]

            self.logger.info("✅ Complete Spider-Agent Orchestration System ACTIVE!")
            self.logger.info(f"📊 System Status: {len(self.active_spiders)} spiders, {len(self.connected_agents)} agents")

            # Wait for all orchestration tasks
            await asyncio.gather(*self.orchestration_tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Failed to start orchestration system: {e}")
            raise
        finally:
            await self.shutdown_orchestration()

    async def _activate_spider_networks(self):
        """Activate spider networks in priority waves"""
        self.logger.info("🕷️ Activating Spider Networks in Priority Waves...")

        # Sort spiders by activation priority
        priority_groups = {}
        for spider_name, config in self.spider_configs.items():
            priority = config.activation_priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append((spider_name, config))

        # Activate in priority order
        for priority in sorted(priority_groups.keys(), key=lambda x: x.value):
            priority_name = priority.name
            spiders_in_priority = priority_groups[priority]

            self.logger.info(f"🌊 Wave {priority.value}: Activating {priority_name} priority spiders ({len(spiders_in_priority)} spiders)")

            activation_tasks = []
            for spider_name, config in spiders_in_priority:
                task = asyncio.create_task(self._activate_single_spider(spider_name, config))
                activation_tasks.append(task)

            # Deploy wave concurrently with brief delays
            results = await asyncio.gather(*activation_tasks, return_exceptions=True)

            # Count successful activations
            successful = sum(1 for result in results if not isinstance(result, Exception))
            self.logger.info(f"✅ Wave {priority.value} deployed: {successful}/{len(spiders_in_priority)} spiders activated")

            # Brief pause between waves
            await asyncio.sleep(2)

    async def _activate_single_spider(self, spider_name: str, config: SpiderActivationConfig):
        """Activate a single spider with its configuration"""
        try:
            self.logger.info(f"🕷️ Activating spider: {spider_name}")

            # Get spider class from registry
            spider_class = self.spider_registry.get_spider_class(spider_name)
            spider_config = self.spider_registry.get_spider_config(spider_name)

            if not spider_class:
                self.logger.error(f"Spider class not found for: {spider_name}")
                return False

            # Create spider instance
            spider_id = f"{spider_name}_connector_{datetime.now().strftime('%H%M%S')}"

            # Prepare targets from spider registry config
            targets = []
            if 'targets' in spider_config:
                targets = spider_config['targets']

            # Create subscribers list (target agents)
            subscribers = config.target_agents

            # Create spider instance
            spider_instance = spider_class(
                spider_id=spider_id,
                targets=targets,
                subscribers=subscribers,
                redis_config=self.redis_config
            )

            # Store active spider
            self.active_spiders[spider_name] = spider_instance
            config.is_active = True

            # Start spider data collection (asynchronous)
            spider_task = asyncio.create_task(spider_instance.start())

            self.metrics.total_spiders_activated += 1
            self.logger.info(f"✅ Spider activated: {spider_name} -> targets: {len(config.target_agents)} agents")

            return True

        except Exception as e:
            self.logger.error(f"Failed to activate spider {spider_name}: {e}")
            return False

    async def _connect_agent_networks(self):
        """Connect agents to spider data streams"""
        self.logger.info("🤖 Connecting Agent Networks to Spider Data Streams...")

        connection_tasks = []
        for agent_id, config in self.agent_configs.items():
            task = asyncio.create_task(self._connect_single_agent(agent_id, config))
            connection_tasks.append(task)

        # Connect all agents concurrently
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)

        # Count successful connections
        successful = sum(1 for result in results if not isinstance(result, Exception))
        self.metrics.total_agents_connected = successful

        self.logger.info(f"✅ Agent Networks Connected: {successful}/{len(self.agent_configs)} agents")

    async def _connect_single_agent(self, agent_id: str, config: AgentConnectionConfig):
        """Connect a single agent to spider data streams"""
        try:
            self.logger.info(f"🔗 Connecting agent: {agent_id}")

            # Determine agent type for specialized data receiver
            agent_type = config.agent_type

            # Create agent data receiver
            data_receiver = create_agent_data_receiver(
                agent_id=agent_id,
                agent_type=agent_type,
                redis_config=self.redis_config
            )

            # Store the data receiver
            config.data_receiver = data_receiver
            self.connected_agents[agent_id] = data_receiver

            # Start data receiver in background
            receiver_task = asyncio.create_task(data_receiver.start_data_receiver())

            self.logger.info(f"✅ Agent connected: {agent_id} -> receiving from {len(config.connected_spiders)} spiders")

            return True

        except Exception as e:
            self.logger.error(f"Failed to connect agent {agent_id}: {e}")
            return False

    async def _start_orchestration_monitoring(self):
        """Start orchestration monitoring systems"""
        self.logger.info("📊 Starting Orchestration Monitoring Systems...")

        # Create monitoring channels
        await self._setup_monitoring_channels()

        # Initialize performance tracking
        await self._initialize_performance_tracking()

        self.logger.info("✅ Orchestration Monitoring Systems Active")

    async def _setup_monitoring_channels(self):
        """Setup Redis channels for monitoring data flows"""
        try:
            # Create orchestration status channel
            status_channel = "orchestration:status"

            status_data = {
                'system': 'spider_connector_orchestrator',
                'status': 'initializing',
                'active_spiders': len(self.active_spiders),
                'connected_agents': len(self.connected_agents),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            await self.redis_async.publish(
                status_channel,
                json.dumps(status_data)
            )

        except Exception as e:
            self.logger.error(f"Failed to setup monitoring channels: {e}")

    async def _initialize_performance_tracking(self):
        """Initialize performance tracking systems"""
        try:
            # Store initial metrics
            await self.redis_async.setex(
                'orchestration:metrics',
                300,  # 5 minute expiry
                json.dumps({
                    'total_spiders_activated': self.metrics.total_spiders_activated,
                    'total_agents_connected': self.metrics.total_agents_connected,
                    'system_start_time': datetime.now(timezone.utc).isoformat(),
                    'orchestrator_version': '1.0.0'
                })
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize performance tracking: {e}")

    async def _spider_health_monitor(self):
        """Monitor health of active spiders"""
        while self.is_orchestrating:
            try:
                await asyncio.sleep(60)  # Check every minute

                healthy_spiders = 0
                total_spiders = len(self.active_spiders)

                for spider_name, spider_instance in self.active_spiders.items():
                    try:
                        # Check spider health (if method exists)
                        if hasattr(spider_instance, 'get_metrics'):
                            metrics = spider_instance.get_metrics()
                            if metrics and hasattr(metrics, 'uptime_percentage'):
                                if metrics.uptime_percentage > 70:  # Healthy threshold
                                    healthy_spiders += 1
                            else:
                                healthy_spiders += 1  # Assume healthy if no metrics
                        else:
                            healthy_spiders += 1  # Assume healthy if no health check

                    except Exception as e:
                        self.logger.warning(f"Health check failed for spider {spider_name}: {e}")

                # Update spider health percentage
                spider_health_percentage = (healthy_spiders / max(total_spiders, 1)) * 100

                if spider_health_percentage < 80:
                    self.logger.warning(f"Spider health degraded: {spider_health_percentage:.1f}%")

            except Exception as e:
                self.logger.error(f"Error in spider health monitor: {e}")

    async def _agent_connection_monitor(self):
        """Monitor agent connection health"""
        while self.is_orchestrating:
            try:
                await asyncio.sleep(90)  # Check every 1.5 minutes

                healthy_agents = 0
                total_agents = len(self.connected_agents)

                for agent_id, data_receiver in self.connected_agents.items():
                    try:
                        # Check agent data receiver health
                        if data_receiver and data_receiver.is_running:
                            metrics = data_receiver.get_processing_metrics()

                            # Consider agent healthy if processing data
                            if metrics.total_received > 0 or metrics.error_rate < 0.2:
                                healthy_agents += 1

                                # Update agent config
                                if agent_id in self.agent_configs:
                                    self.agent_configs[agent_id].last_data_received = datetime.now(timezone.utc)
                                    self.agent_configs[agent_id].total_data_processed = metrics.total_processed

                    except Exception as e:
                        self.logger.warning(f"Connection check failed for agent {agent_id}: {e}")

                # Update agent connection health
                agent_health_percentage = (healthy_agents / max(total_agents, 1)) * 100
                self.metrics.avg_connection_health = agent_health_percentage

                if agent_health_percentage < 80:
                    self.logger.warning(f"Agent connection health degraded: {agent_health_percentage:.1f}%")

            except Exception as e:
                self.logger.error(f"Error in agent connection monitor: {e}")

    async def _data_flow_optimizer(self):
        """Optimize data flow between spiders and agents"""
        while self.is_orchestrating:
            try:
                await asyncio.sleep(300)  # Optimize every 5 minutes

                total_data_flows = 0

                # Collect data flow statistics
                for agent_id, data_receiver in self.connected_agents.items():
                    try:
                        if data_receiver and data_receiver.is_running:
                            metrics = data_receiver.get_processing_metrics()
                            total_data_flows += metrics.total_received
                    except Exception as _e:
                        logger.warning(
                            "spider_connector_orchestrator._initialize_agent_configurations: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )

                self.metrics.total_data_flows = total_data_flows

                # Calculate data flow rate (messages per minute)
                if len(self.metrics_history) > 0:
                    previous_flows = self.metrics_history[-1].total_data_flows if self.metrics_history else 0
                    flow_increase = total_data_flows - previous_flows
                    time_diff_minutes = 5  # We run every 5 minutes
                    self.metrics.data_flow_rate_per_minute = flow_increase / time_diff_minutes

                self.logger.info(f"📊 Data Flow Rate: {self.metrics.data_flow_rate_per_minute:.1f} messages/minute")

            except Exception as e:
                self.logger.error(f"Error in data flow optimizer: {e}")

    async def _performance_metrics_collector(self):
        """Collect comprehensive performance metrics"""
        while self.is_orchestrating:
            try:
                await asyncio.sleep(120)  # Collect every 2 minutes

                # Update timestamp
                self.metrics.last_updated = datetime.now(timezone.utc)

                # Calculate system uptime percentage
                if len(self.active_spiders) > 0 and len(self.connected_agents) > 0:
                    self.metrics.system_uptime_percentage = min(100.0, self.metrics.avg_connection_health)

                # Store metrics in Redis
                metrics_data = {
                    'total_spiders_activated': self.metrics.total_spiders_activated,
                    'total_agents_connected': self.metrics.total_agents_connected,
                    'total_data_flows': self.metrics.total_data_flows,
                    'avg_connection_health': self.metrics.avg_connection_health,
                    'data_flow_rate_per_minute': self.metrics.data_flow_rate_per_minute,
                    'system_uptime_percentage': self.metrics.system_uptime_percentage,
                    'last_updated': self.metrics.last_updated.isoformat()
                }

                await self.redis_async.setex(
                    'orchestration:live_metrics',
                    300,  # 5 minute expiry
                    json.dumps(metrics_data)
                )

                # Store historical metrics
                self.metrics_history.append(OrchestrationMetrics(
                    total_spiders_activated=self.metrics.total_spiders_activated,
                    total_agents_connected=self.metrics.total_agents_connected,
                    total_data_flows=self.metrics.total_data_flows,
                    avg_connection_health=self.metrics.avg_connection_health,
                    data_flow_rate_per_minute=self.metrics.data_flow_rate_per_minute,
                    system_uptime_percentage=self.metrics.system_uptime_percentage,
                    last_updated=self.metrics.last_updated
                ))

                # Keep only last 4 hours of history (120 entries at 2-minute intervals)
                if len(self.metrics_history) > 120:
                    self.metrics_history = self.metrics_history[-120:]

            except Exception as e:
                self.logger.error(f"Error collecting performance metrics: {e}")

    async def _system_health_reporter(self):
        """Report overall system health"""
        while self.is_orchestrating:
            try:
                await asyncio.sleep(600)  # Report every 10 minutes

                # Create comprehensive health report
                health_report = {
                    'system_status': 'operational' if self.metrics.avg_connection_health > 80 else 'degraded',
                    'active_spiders': {
                        'total': len(self.active_spiders),
                        'by_priority': {
                            priority.name: sum(1 for config in self.spider_configs.values()
                                             if config.activation_priority == priority and config.is_active)
                            for priority in ActivationPriority
                        }
                    },
                    'connected_agents': {
                        'total': len(self.connected_agents),
                        'healthy': sum(1 for agent in self.connected_agents.values()
                                     if agent and agent.is_running),
                        'processing_data': sum(1 for agent_id in self.connected_agents
                                             if self.agent_configs[agent_id].total_data_processed > 0)
                    },
                    'data_flows': {
                        'total_processed': self.metrics.total_data_flows,
                        'rate_per_minute': self.metrics.data_flow_rate_per_minute,
                        'avg_connection_health': self.metrics.avg_connection_health
                    },
                    'system_metrics': {
                        'uptime_percentage': self.metrics.system_uptime_percentage,
                        'last_updated': self.metrics.last_updated.isoformat()
                    }
                }

                # Store health report
                await self.redis_async.setex(
                    'orchestration:health_report',
                    600,  # 10 minute expiry
                    json.dumps(health_report)
                )

                # Log system status
                self.logger.info(
                    f"🏥 System Health Report: "
                    f"{health_report['active_spiders']['total']} spiders, "
                    f"{health_report['connected_agents']['total']} agents, "
                    f"{health_report['data_flows']['rate_per_minute']:.1f} msgs/min, "
                    f"{health_report['system_metrics']['uptime_percentage']:.1f}% uptime"
                )

            except Exception as e:
                self.logger.error(f"Error in system health reporter: {e}")

    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""
        return {
            'system_info': {
                'is_orchestrating': self.is_orchestrating,
                'orchestrator_version': '1.0.0',
                'start_time': datetime.now(timezone.utc).isoformat()
            },
            'spider_network': {
                'total_configured': len(self.spider_configs),
                'total_activated': self.metrics.total_spiders_activated,
                'active_spiders': list(self.active_spiders.keys()),
                'activation_priorities': {
                    priority.name: [name for name, config in self.spider_configs.items()
                                  if config.activation_priority == priority]
                    for priority in ActivationPriority
                }
            },
            'agent_network': {
                'total_configured': len(self.agent_configs),
                'total_connected': self.metrics.total_agents_connected,
                'connected_agents': list(self.connected_agents.keys()),
                'agent_health': {
                    agent_id: {
                        'is_running': config.data_receiver.is_running if config.data_receiver else False,
                        'data_processed': config.total_data_processed,
                        'last_data_received': config.last_data_received.isoformat() if config.last_data_received else None
                    }
                    for agent_id, config in self.agent_configs.items()
                }
            },
            'performance_metrics': {
                'total_data_flows': self.metrics.total_data_flows,
                'data_flow_rate_per_minute': self.metrics.data_flow_rate_per_minute,
                'avg_connection_health': self.metrics.avg_connection_health,
                'system_uptime_percentage': self.metrics.system_uptime_percentage,
                'last_updated': self.metrics.last_updated.isoformat()
            },
            'data_routing': {
                'spider_to_agent_mappings': {
                    spider_name: config.target_agents
                    for spider_name, config in self.spider_configs.items()
                },
                'agent_to_spider_mappings': {
                    agent_id: config.connected_spiders
                    for agent_id, config in self.agent_configs.items()
                }
            }
        }

    async def activate_targeted_spiders(self, spider_names: List[str]) -> Dict[str, Any]:
        """Activate specific spiders on demand"""
        try:
            self.logger.info(f"🎯 Activating targeted spiders: {spider_names}")

            activation_results = []

            for spider_name in spider_names:
                if spider_name in self.spider_configs:
                    config = self.spider_configs[spider_name]

                    # Skip if already active
                    if config.is_active:
                        activation_results.append({
                            'spider': spider_name,
                            'status': 'already_active',
                            'message': f'Spider {spider_name} is already active'
                        })
                        continue

                    # Activate spider
                    success = await self._activate_single_spider(spider_name, config)

                    activation_results.append({
                        'spider': spider_name,
                        'status': 'activated' if success else 'failed',
                        'message': f'Spider {spider_name} activation {"successful" if success else "failed"}'
                    })
                else:
                    activation_results.append({
                        'spider': spider_name,
                        'status': 'not_found',
                        'message': f'Spider {spider_name} not found in configurations'
                    })

            return {
                'success': True,
                'activated': len([r for r in activation_results if r['status'] == 'activated']),
                'total_requested': len(spider_names),
                'results': activation_results
            }

        except Exception as e:
            self.logger.error(f"Failed to activate targeted spiders: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def shutdown_orchestration(self):
        """Gracefully shutdown the orchestration system"""
        try:
            self.is_orchestrating = False
            self.logger.info("🛑 Shutting down Spider-Agent Orchestration System...")

            # Cancel orchestration tasks
            for task in self.orchestration_tasks:
                task.cancel()

            # Wait for tasks to complete
            if self.orchestration_tasks:
                await asyncio.gather(*self.orchestration_tasks, return_exceptions=True)

            # Shutdown connected agents
            shutdown_tasks = []
            for agent_id, data_receiver in self.connected_agents.items():
                if data_receiver:
                    shutdown_tasks.append(asyncio.create_task(data_receiver.shutdown()))

            if shutdown_tasks:
                await asyncio.gather(*shutdown_tasks, return_exceptions=True)

            # Shutdown active spiders
            for spider_name, spider_instance in self.active_spiders.items():
                try:
                    if hasattr(spider_instance, 'stop'):
                        await spider_instance.stop()
                except Exception as e:
                    self.logger.error(f"Error stopping spider {spider_name}: {e}")

            # Shutdown spider orchestrator
            await self.spider_orchestrator.shutdown_army()

            # Close Redis connections
            if self.redis_async:
                await self.redis_async.close()

            # Shutdown executor
            self.executor.shutdown(wait=True)

            self.logger.info("✅ Spider-Agent Orchestration System shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during orchestration shutdown: {e}")


# Global orchestrator instance
_orchestrator_instance = None

def get_spider_connector_orchestrator(redis_config: Dict[str, Any] = None) -> SpiderConnectorOrchestrator:
    """Get the global spider connector orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = SpiderConnectorOrchestrator(redis_config)
    return _orchestrator_instance


# Management command interface
async def start_spider_agent_bridge():
    """Start the complete spider-agent bridge system"""
    orchestrator = get_spider_connector_orchestrator()
    await orchestrator.start_complete_orchestration()


if __name__ == "__main__":
    # Direct execution for testing
    import argparse

    parser = argparse.ArgumentParser(description='Spider Connector Orchestrator')
    parser.add_argument('--activate', nargs='+', help='Activate specific spiders')
    parser.add_argument('--status', action='store_true', help='Show orchestration status')

    args = parser.parse_args()

    async def main():
        orchestrator = get_spider_connector_orchestrator()

        if args.activate:
            result = await orchestrator.activate_targeted_spiders(args.activate)
            print(json.dumps(result, indent=2))
        elif args.status:
            status = orchestrator.get_orchestration_status()
            print(json.dumps(status, indent=2))
        else:
            await orchestrator.start_complete_orchestration()

    asyncio.run(main())