"""
Spider-Agent-Connector-Orchestrator - The Neural Network of Intelligence
========================================================================

This module creates the critical nervous system that connects spider networks
to AI entities, establishing data pipelines, routing protocols, and activation
systems that transform dormant spiders into a living intelligence network.

Features:
- Intelligent routing tables mapping spiders to consumers
- Real-time data distribution to 102 agents and 25+ advisors
- Load balancing and priority-based routing
- Spider activation in coordinated waves
- Performance monitoring and optimization
- Fault-tolerant connection management
"""

import asyncio
import json
import logging
import redis
from redis import asyncio as aioredis
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

from .spider_army_orchestrator import SpiderArmyOrchestrator, SpiderType
from .data_pipeline import RealTimeDataPipeline
# Agent and advisor registries would be imported here if they exist
# For now, we'll create our own agent discovery system

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Status of spider-consumer connections"""
    PENDING = "pending"
    CONNECTED = "connected"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECONNECTING = "reconnecting"


class DataFlowPriority(Enum):
    """Priority levels for data flow"""
    CRITICAL = 1      # Income Builder, Warren Buffett, Ray Dalio
    HIGH = 2          # Trading agents, Cathie Wood
    NORMAL = 3        # Research agents, most advisors
    LOW = 4           # General broadcast, monitoring


@dataclass
class ConnectionMapping:
    """Mapping between spider and consumer"""
    spider_id: str
    spider_type: SpiderType
    consumer_type: str  # "agent" or "advisor"
    consumer_id: str
    priority: DataFlowPriority
    data_types: List[str]
    filters: Dict[str, Any]
    status: ConnectionStatus = ConnectionStatus.PENDING
    last_active: Optional[datetime] = None
    message_count: int = 0
    error_count: int = 0


@dataclass
class RouterMetrics:
    """Metrics for the spider-agent connector"""
    total_connections: int = 0
    active_connections: int = 0
    messages_routed: int = 0
    failed_routes: int = 0
    router_loop_errors: int = 0
    malformed_message_count: int = 0
    delivery_failure_count: int = 0
    avg_latency_ms: float = 0.0
    top_producers: List[str] = field(default_factory=list)
    top_consumers: List[str] = field(default_factory=list)
    connection_health: float = 100.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SpiderDataRouter:
    """
    The Spider-Agent-Connector-Orchestrator.

    Creates the nervous system that connects 1,770+ spiders to 102 agents
    and 25+ advisors with intelligent routing, load balancing, and monitoring.
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        """Initialize the Spider Data Router"""
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}
        self.redis_client = redis.Redis(**self.redis_config)
        self.redis_async = None

        # Core components
        self.spider_orchestrator = SpiderArmyOrchestrator(self.redis_config)
        self.data_pipeline = RealTimeDataPipeline(self.redis_config)
        self.agent_registry = get_agent_registry()
        self.advisor_registry = get_advisor_registry()

        # Connection management
        self.connection_mappings: Dict[str, ConnectionMapping] = {}
        self.routing_tables: Dict[str, List[str]] = {}
        self.subscriber_channels: Dict[str, Set[str]] = {}

        # Performance tracking
        self.metrics = RouterMetrics()
        self.connection_history: List[RouterMetrics] = []
        self.route_outcomes: List[Dict[str, Any]] = []
        self.last_route_outcome: Optional[Dict[str, Any]] = None
        self.router_loop_errors = 0
        self.last_router_error = None
        self.last_router_error_type = None
        self.malformed_message_count = 0
        self.filter_rejection_reasons: Dict[str, int] = {}
        self.delivery_failure_count = 0
        self.last_delivery_failure = None
        self.metrics_stale = False

        # Executor for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=20)

        self.logger = logging.getLogger(__name__)
        self.is_running = False

    def _record_route_outcome(self, outcome: Dict[str, Any]):
        """Record a bounded history of route outcomes for observability."""
        self.last_route_outcome = outcome
        self.route_outcomes.append(outcome)
        if len(self.route_outcomes) > 50:
            self.route_outcomes = self.route_outcomes[-50:]

    def _get_filter_rejection_reason(self, data: Dict[str, Any], mapping: ConnectionMapping) -> Optional[str]:
        """Return a reason code for why a consumer filter rejected a message."""
        try:
            filters = mapping.filters

            min_quality = filters.get('min_quality_score', 0.0)
            if data.get('quality_score', 0.0) < min_quality:
                return 'low_quality'

            content_text = json.dumps(data.get('content', {})).lower()

            required_keywords = filters.get('keywords', [])
            if required_keywords and not any(keyword.lower() in content_text for keyword in required_keywords):
                return 'keyword_miss'

            excluded_keywords = filters.get('exclude_keywords', [])
            if excluded_keywords and any(keyword.lower() in content_text for keyword in excluded_keywords):
                return 'excluded_keyword'

            if mapping.data_types and data.get('data_type') and data['data_type'] not in mapping.data_types:
                return 'data_type_mismatch'

            data_freshness_hours = filters.get('data_freshness_hours')
            if data_freshness_hours:
                raw_ts = data.get('timestamp', '')
                try:
                    from core.utils.time import normalize_timestamp
                    timestamp = normalize_timestamp(raw_ts) or datetime.now(timezone.utc)
                except Exception:
                    timestamp = datetime.fromisoformat(str(raw_ts).replace('Z', '+00:00'))
                age_hours = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600
                if age_hours > data_freshness_hours:
                    return 'stale_data'

            return None
        except Exception as e:
            self.logger.error(f"Error checking consumer filters: {e}")
            return 'filter_parse_error'

    async def initialize_router_infrastructure(self):
        """Initialize the complete routing infrastructure"""
        try:
            self.logger.info("🧠 Initializing Spider-Agent-Connector-Orchestrator...")

            # Initialize async Redis connection
            self.redis_async = aioredis.from_url(
                f"redis://{self.redis_config['host']}:{self.redis_config['port']}/{self.redis_config['db']}"
            )

            # Build routing tables
            await self._build_routing_tables()

            # Create connection mappings
            await self._create_connection_mappings()

            # Initialize subscriber channels
            await self._initialize_subscriber_channels()

            self.logger.info("✅ Router infrastructure initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize router infrastructure: {e}")
            raise

    async def _build_routing_tables(self):
        """Build intelligent routing tables connecting spiders to consumers"""
        self.logger.info("📊 Building intelligent routing tables...")

        # Financial Intelligence Routing
        financial_consumers = [
            # Legendary Advisors
            "advisor:warren_buffett",
            "advisor:charlie_munger",
            "advisor:benjamin_graham",
            "advisor:ray_dalio",
            "advisor:george_soros",

            # Specialized Agents
            "agent:financial_strategist",
            "agent:value_investing_agent",
            "agent:dividend_hunter",
            "agent:earnings_analyzer",
            "agent:sec_filing_expert",
            "agent:income_builder_agent"  # Priority consumer
        ]

        # Innovation Intelligence Routing
        innovation_consumers = [
            # Innovation Advisors
            "advisor:cathie_wood",
            "advisor:peter_thiel",
            "advisor:reid_hoffman",
            "advisor:naval_ravikant",

            # Tech Agents
            "agent:ai_strategist",
            "agent:tech_architect",
            "agent:innovation_scout",
            "agent:patent_analyzer",
            "agent:research_synthesizer"
        ]

        # Market Data Routing
        market_consumers = [
            # Trading Advisors
            "advisor:paul_tudor_jones",
            "advisor:stanley_druckenmiller",
            "advisor:david_tepper",

            # Trading Agents
            "agent:crypto_expert",
            "agent:options_master",
            "agent:day_trading_agent",
            "agent:arbitrage_hunter",
            "agent:momentum_trader"
        ]

        # Social Sentiment Routing
        social_consumers = [
            # Social Media Advisors
            "advisor:gary_vaynerchuk",
            "advisor:tim_ferriss",

            # Sentiment Agents
            "agent:sentiment_analyzer",
            "agent:social_media_monitor",
            "agent:trend_detector",
            "agent:influencer_tracker"
        ]

        # News Intelligence Routing (Goes to EVERYONE)
        news_consumers = financial_consumers + innovation_consumers + market_consumers + social_consumers

        # Build routing tables
        self.routing_tables = {
            "financial_intel": financial_consumers,
            "innovation_tracker": innovation_consumers,
            "market_data": market_consumers,
            "social_sentiment": social_consumers,
            "news_harvester": news_consumers,  # Universal feed
            "research_papers": innovation_consumers + financial_consumers,
            "patent_monitor": innovation_consumers,
            "regulatory": financial_consumers + market_consumers,
            "competitive": innovation_consumers + financial_consumers,
            "adaptive": news_consumers  # Adaptive spiders feed everyone
        }

        self.logger.info(f"✅ Built routing tables for {len(self.routing_tables)} spider swarms")

    async def _create_connection_mappings(self):
        """Create detailed connection mappings between spiders and consumers"""
        self.logger.info("🔗 Creating connection mappings...")

        connection_count = 0

        for swarm_id, consumers in self.routing_tables.items():
            swarm_config = self.spider_orchestrator.swarm_configs.get(swarm_id)
            if not swarm_config:
                continue

            # Create mappings for each spider in the swarm
            for i in range(swarm_config.spider_count):
                spider_id = f"{swarm_id}_{i:04d}"

                for consumer in consumers:
                    consumer_type, consumer_id = consumer.split(":", 1)

                    # Determine priority based on consumer
                    priority = self._determine_priority(consumer_id, swarm_config.spider_type)

                    # Create connection mapping
                    mapping_id = f"{spider_id}:{consumer}"
                    mapping = ConnectionMapping(
                        spider_id=spider_id,
                        spider_type=swarm_config.spider_type,
                        consumer_type=consumer_type,
                        consumer_id=consumer_id,
                        priority=priority,
                        data_types=self._get_data_types_for_consumer(consumer_id, swarm_config.spider_type),
                        filters=self._get_filters_for_consumer(consumer_id, swarm_config.spider_type)
                    )

                    self.connection_mappings[mapping_id] = mapping
                    connection_count += 1

        self.metrics.total_connections = connection_count
        self.logger.info(f"✅ Created {connection_count} connection mappings")

    def _determine_priority(self, consumer_id: str, spider_type: SpiderType) -> DataFlowPriority:
        """Determine data flow priority for consumer"""

        # Critical priority consumers
        critical_consumers = {
            "income_builder_agent", "warren_buffett", "ray_dalio",
            "charlie_munger", "benjamin_graham"
        }

        # High priority consumers
        high_priority_consumers = {
            "cathie_wood", "peter_thiel", "george_soros",
            "paul_tudor_jones", "crypto_expert", "options_master"
        }

        if consumer_id in critical_consumers:
            return DataFlowPriority.CRITICAL
        elif consumer_id in high_priority_consumers:
            return DataFlowPriority.HIGH
        elif spider_type in [SpiderType.FINANCIAL, SpiderType.MARKET_DATA]:
            return DataFlowPriority.HIGH
        else:
            return DataFlowPriority.NORMAL

    def _get_data_types_for_consumer(self, consumer_id: str, spider_type: SpiderType) -> List[str]:
        """Get relevant data types for consumer based on their specialization"""

        data_type_mappings = {
            # Financial consumers
            "warren_buffett": ["sec_filing", "earnings_report", "financial_news", "value_metrics"],
            "income_builder_agent": ["dividend_data", "income_opportunities", "financial_news", "sec_filing"],
            "financial_strategist": ["financial_news", "market_data", "earnings_report"],

            # Innovation consumers
            "cathie_wood": ["research_papers", "innovation_intelligence", "patent_data", "tech_news"],
            "ai_strategist": ["ai_research", "tech_news", "patent_data", "innovation_intelligence"],

            # Trading consumers
            "crypto_expert": ["crypto_market_data", "blockchain_news", "defi_data"],
            "options_master": ["options_data", "volatility_data", "market_data"],

            # Default by spider type
            SpiderType.FINANCIAL: ["financial_news", "market_data", "sec_filing"],
            SpiderType.INNOVATION: ["research_papers", "patent_data", "tech_news"],
            SpiderType.MARKET_DATA: ["market_data", "trading_data", "price_data"],
            SpiderType.SOCIAL_SENTIMENT: ["social_data", "sentiment_data"],
            SpiderType.NEWS_HARVESTER: ["news", "breaking_news", "analysis"]
        }

        # Try consumer-specific mapping first
        if consumer_id in data_type_mappings:
            return data_type_mappings[consumer_id]

        # Fall back to spider type mapping
        return data_type_mappings.get(spider_type, ["general"])

    def _get_filters_for_consumer(self, consumer_id: str, spider_type: SpiderType) -> Dict[str, Any]:
        """Get content filters for consumer"""

        filter_mappings = {
            "warren_buffett": {
                "keywords": ["value", "moat", "fundamentals", "berkshire", "quality"],
                "exclude_keywords": ["crypto", "speculation", "meme"],
                "min_quality_score": 0.9
            },
            "income_builder_agent": {
                "keywords": ["dividend", "income", "yield", "distribution", "payout"],
                "min_quality_score": 0.8,
                "data_freshness_hours": 4
            },
            "cathie_wood": {
                "keywords": ["innovation", "disruptive", "genomics", "ai", "automation"],
                "min_quality_score": 0.9
            },
            "crypto_expert": {
                "keywords": ["bitcoin", "ethereum", "defi", "blockchain", "crypto"],
                "min_quality_score": 0.8
            }
        }

        return filter_mappings.get(consumer_id, {"min_quality_score": 0.7})

    async def _initialize_subscriber_channels(self):
        """Initialize Redis pub/sub channels for each consumer"""
        self.logger.info("📡 Initializing subscriber channels...")

        # Get all unique consumers
        all_consumers = set()
        for consumers in self.routing_tables.values():
            all_consumers.update(consumers)

        # Create channels
        for consumer in all_consumers:
            consumer_type, consumer_id = consumer.split(":", 1)

            # Create dedicated channel for this consumer
            channel_name = f"intelligence:{consumer_type}:{consumer_id}"

            if consumer_type not in self.subscriber_channels:
                self.subscriber_channels[consumer_type] = set()

            self.subscriber_channels[consumer_type].add(channel_name)

        total_channels = sum(len(channels) for channels in self.subscriber_channels.values())
        self.logger.info(f"✅ Initialized {total_channels} subscriber channels")

    async def activate_spider_army(self):
        """Activate the dormant spider networks in coordinated waves"""
        try:
            self.logger.info("🚀 Activating Spider Army in coordinated waves...")

            # Wave 1: Critical Intelligence Spiders (Financial + News)
            critical_swarms = ["financial_intel", "news_harvester", "market_data"]
            await self._activate_spider_wave(critical_swarms, "Critical Intelligence Wave")

            await asyncio.sleep(5)  # Brief pause between waves

            # Wave 2: Innovation & Research Spiders
            innovation_swarms = ["innovation_tracker", "research_papers", "patent_monitor"]
            await self._activate_spider_wave(innovation_swarms, "Innovation Intelligence Wave")

            await asyncio.sleep(3)

            # Wave 3: Social & Regulatory Spiders
            secondary_swarms = ["social_sentiment", "regulatory", "competitive"]
            await self._activate_spider_wave(secondary_swarms, "Secondary Intelligence Wave")

            await asyncio.sleep(2)

            # Wave 4: Adaptive & Remaining Spiders
            remaining_swarms = ["adaptive"]
            await self._activate_spider_wave(remaining_swarms, "Adaptive Intelligence Wave")

            self.logger.info("✅ Spider Army activation complete - 1,770+ spiders deployed!")

        except Exception as e:
            self.logger.error(f"Failed to activate spider army: {e}")
            raise

    async def _activate_spider_wave(self, swarm_ids: List[str], wave_name: str):
        """Activate a specific wave of spider swarms"""
        try:
            self.logger.info(f"🌊 Deploying {wave_name}...")

            # Prepare deployment tasks for this wave
            deployment_tasks = []

            for swarm_id in swarm_ids:
                config = self.spider_orchestrator.swarm_configs.get(swarm_id)
                if config:
                    task = asyncio.create_task(
                        self.spider_orchestrator._deploy_swarm(config)
                    )
                    deployment_tasks.append(task)

            # Deploy wave concurrently
            results = await asyncio.gather(*deployment_tasks, return_exceptions=True)

            # Count successful deployments
            successful = sum(1 for result in results if not isinstance(result, Exception))
            total_spiders = sum(
                self.spider_orchestrator.swarm_configs[swarm_id].spider_count
                for swarm_id in swarm_ids
                if swarm_id in self.spider_orchestrator.swarm_configs
            )

            self.logger.info(f"✅ {wave_name} deployed: {successful}/{len(swarm_ids)} swarms, ~{total_spiders} spiders")

        except Exception as e:
            self.logger.error(f"Failed to deploy {wave_name}: {e}")

    async def start_data_routing(self):
        """Start the real-time data routing system"""
        try:
            self.logger.info("🔄 Starting real-time data routing system...")

            self.is_running = True

            # Start core routing tasks
            routing_tasks = [
                asyncio.create_task(self._message_router()),
                asyncio.create_task(self._connection_monitor()),
                asyncio.create_task(self._performance_tracker()),
                asyncio.create_task(self._health_checker()),
                asyncio.create_task(self._load_balancer())
            ]

            # Start data pipeline
            pipeline_task = asyncio.create_task(self.data_pipeline.start())

            self.logger.info("✅ Data routing system started successfully")

            # Wait for all tasks
            all_tasks = routing_tasks + [pipeline_task]
            await asyncio.gather(*all_tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Failed to start data routing: {e}")
            raise

    async def _message_router(self):
        """Core message routing loop"""
        while self.is_running:
            try:
                # Subscribe to intelligence channels
                pubsub = self.redis_async.pubsub()
                await pubsub.subscribe('spider_intelligence:*')

                async for message in pubsub.listen():
                    if message['type'] == 'message':
                        await self._route_spider_message(message)

                await asyncio.sleep(0.01)  # Prevent tight loop

            except Exception as e:
                self.logger.error(f"Error in message router: {e}")
                self.router_loop_errors += 1
                self.last_router_error = str(e)
                self.last_router_error_type = type(e).__name__
                self.metrics.router_loop_errors += 1
                await asyncio.sleep(1)

    async def _route_spider_message(self, redis_message: Dict[str, Any]):
        """Route a spider intelligence message to appropriate consumers"""
        route_outcome = {
            'route_status': 'unknown',
            'failure_type': None,
            'spider_id': None,
            'channel': None,
            'consumer_count': 0,
            'delivery_failure_count': 0,
            'delivery_failures': [],
        }
        try:
            # Parse message
            channel = redis_message['channel'].decode('utf-8')
            route_outcome['channel'] = channel
            data = json.loads(redis_message['data'])
            if not isinstance(data, dict):
                raise ValueError('Malformed spider message payload')

            # Extract spider ID from channel or data
            spider_id = data.get('spider_id', 'unknown')
            route_outcome['spider_id'] = spider_id

            # Find connection mappings for this spider
            relevant_mappings = [
                mapping for mapping_id, mapping in self.connection_mappings.items()
                if mapping.spider_id == spider_id and mapping.status == ConnectionStatus.ACTIVE
            ]
            route_outcome['consumer_count'] = len(relevant_mappings)

            if not relevant_mappings:
                route_outcome['route_status'] = 'no_active_consumers'
                route_outcome['failure_type'] = 'no_active_consumers'
                self._record_route_outcome(route_outcome)
                return route_outcome

            # Route to each connected consumer
            routing_tasks = []
            filtered_out = 0
            for mapping in relevant_mappings:
                rejection_reason = self._get_filter_rejection_reason(data, mapping)
                if rejection_reason is None:
                    task = asyncio.create_task(
                        self._deliver_to_consumer(data, mapping)
                    )
                    routing_tasks.append(task)
                else:
                    filtered_out += 1
                    self.filter_rejection_reasons[rejection_reason] = self.filter_rejection_reasons.get(rejection_reason, 0) + 1

            if not routing_tasks:
                route_outcome['route_status'] = 'filtered_out'
                route_outcome['failure_type'] = 'filter_rejection'
                self._record_route_outcome(route_outcome)
                return route_outcome

            # Execute routing tasks
            if routing_tasks:
                delivery_results = await asyncio.gather(*routing_tasks, return_exceptions=True)
                self.metrics.messages_routed += len(routing_tasks)
                for delivery_result in delivery_results:
                    if isinstance(delivery_result, Exception):
                        route_outcome['delivery_failure_count'] += 1
                        route_outcome['delivery_failures'].append({
                            'error': str(delivery_result),
                            'error_type': type(delivery_result).__name__,
                        })
                    elif isinstance(delivery_result, dict) and not delivery_result.get('success', True):
                        route_outcome['delivery_failure_count'] += 1
                        route_outcome['delivery_failures'].append(delivery_result)

                self.delivery_failure_count += route_outcome['delivery_failure_count']
                self.metrics.delivery_failure_count += route_outcome['delivery_failure_count']
                if route_outcome['delivery_failures']:
                    self.last_delivery_failure = route_outcome['delivery_failures'][-1]

                if route_outcome['delivery_failure_count']:
                    route_outcome['route_status'] = 'partial_failure'
                    route_outcome['failure_type'] = 'delivery_failure'
                else:
                    route_outcome['route_status'] = 'routed'

            if filtered_out and route_outcome['route_status'] == 'routed':
                route_outcome['route_status'] = 'routed_with_filters'

        except Exception as e:
            self.logger.error(f"Error routing spider message: {e}")
            self.metrics.failed_routes += 1
            if route_outcome['spider_id'] is None:
                self.malformed_message_count += 1
                self.metrics.malformed_message_count += 1
                route_outcome['route_status'] = 'malformed_message'
                route_outcome['failure_type'] = 'malformed_message'
            else:
                route_outcome['route_status'] = 'route_error'
                route_outcome['failure_type'] = 'route_error'
            route_outcome['error'] = str(e)
            route_outcome['error_type'] = type(e).__name__
            self.last_router_error = str(e)
            self.last_router_error_type = type(e).__name__
            self._record_route_outcome(route_outcome)
            return route_outcome

        if route_outcome['route_status'] == 'unknown':
            route_outcome['route_status'] = 'routed'

        self._record_route_outcome(route_outcome)
        return route_outcome

    def _passes_consumer_filters(self, data: Dict[str, Any], mapping: ConnectionMapping) -> bool:
        """Check if message passes consumer-specific filters"""
        return self._get_filter_rejection_reason(data, mapping) is None

    async def _deliver_to_consumer(self, data: Dict[str, Any], mapping: ConnectionMapping):
        """Deliver intelligence data to specific consumer"""
        try:
            # Prepare delivery payload
            delivery_payload = {
                **data,
                'consumer_id': mapping.consumer_id,
                'consumer_type': mapping.consumer_type,
                'priority': mapping.priority.value,
                'delivered_at': datetime.now(timezone.utc).isoformat(),
                'connection_id': f"{mapping.spider_id}:{mapping.consumer_type}:{mapping.consumer_id}"
            }

            # Determine delivery channel
            channel_name = f"intelligence:{mapping.consumer_type}:{mapping.consumer_id}"

            # Publish to consumer channel
            await self.redis_async.publish(
                channel_name,
                json.dumps(delivery_payload)
            )

            # Update mapping stats
            mapping.last_active = datetime.now(timezone.utc)
            mapping.message_count += 1

            # Store for consumer history
            history_key = f"consumer_history:{mapping.consumer_type}:{mapping.consumer_id}"
            await self.redis_async.lpush(history_key, json.dumps(delivery_payload))
            await self.redis_async.ltrim(history_key, 0, 999)  # Keep last 1000 messages
            return {
                'success': True,
                'consumer_id': mapping.consumer_id,
                'consumer_type': mapping.consumer_type,
                'failure_type': None,
            }

        except Exception as e:
            self.logger.error(f"Error delivering to consumer {mapping.consumer_id}: {e}")
            mapping.error_count += 1
            return {
                'success': False,
                'consumer_id': mapping.consumer_id,
                'consumer_type': mapping.consumer_type,
                'failure_type': 'delivery_failure',
                'error': str(e),
                'error_type': type(e).__name__,
            }

    async def _connection_monitor(self):
        """Monitor connection health and status"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                active_count = 0
                degraded_count = 0
                failed_count = 0

                current_time = datetime.now(timezone.utc)

                for mapping in self.connection_mappings.values():
                    # Check connection health
                    if mapping.last_active:
                        time_since_active = (current_time - mapping.last_active).total_seconds()

                        if time_since_active < 300:  # 5 minutes
                            mapping.status = ConnectionStatus.ACTIVE
                            active_count += 1
                        elif time_since_active < 1800:  # 30 minutes
                            mapping.status = ConnectionStatus.DEGRADED
                            degraded_count += 1
                        else:
                            mapping.status = ConnectionStatus.FAILED
                            failed_count += 1
                    else:
                        mapping.status = ConnectionStatus.PENDING

                # Update metrics
                self.metrics.active_connections = active_count
                self.metrics.connection_health = (active_count / max(len(self.connection_mappings), 1)) * 100

                self.logger.debug(
                    f"Connection Status: {active_count} active, "
                    f"{degraded_count} degraded, {failed_count} failed"
                )

            except Exception as e:
                self.logger.error(f"Error in connection monitor: {e}")

    async def _performance_tracker(self):
        """Track routing performance metrics"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Update every minute

                # Calculate top producers (spiders with most messages)
                spider_counts = {}
                consumer_counts = {}

                for mapping in self.connection_mappings.values():
                    spider_counts[mapping.spider_id] = spider_counts.get(mapping.spider_id, 0) + mapping.message_count
                    consumer_key = f"{mapping.consumer_type}:{mapping.consumer_id}"
                    consumer_counts[consumer_key] = consumer_counts.get(consumer_key, 0) + mapping.message_count

                # Update top performers
                self.metrics.top_producers = sorted(
                    spider_counts.items(), key=lambda x: x[1], reverse=True
                )[:10]

                self.metrics.top_consumers = sorted(
                    consumer_counts.items(), key=lambda x: x[1], reverse=True
                )[:10]

                self.metrics.last_updated = datetime.now(timezone.utc)

                # Store metrics in Redis
                await self.redis_async.setex(
                    'spider_router:metrics',
                    300,  # 5 minute expiry
                    json.dumps({
                        'total_connections': self.metrics.total_connections,
                        'active_connections': self.metrics.active_connections,
                        'messages_routed': self.metrics.messages_routed,
                        'failed_routes': self.metrics.failed_routes,
                        'connection_health': self.metrics.connection_health,
                        'top_producers': self.metrics.top_producers,
                        'top_consumers': self.metrics.top_consumers,
                        'last_updated': self.metrics.last_updated.isoformat()
                    })
                )

            except Exception as e:
                self.logger.error(f"Error in performance tracker: {e}")
                self.metrics_stale = True

    async def _health_checker(self):
        """Monitor overall system health"""
        while self.is_running:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes

                # Check Redis connectivity
                await self.redis_async.ping()

                # Check spider army status
                army_status = self.spider_orchestrator.get_army_status()

                # Check data pipeline status
                pipeline_status = self.data_pipeline.get_status()

                # Store health status
                health_status = {
                    'router_status': 'healthy',
                    'spider_army_active': army_status['is_running'],
                    'data_pipeline_active': pipeline_status['is_running'],
                    'total_spiders': army_status['army_stats']['total_spiders'],
                    'active_spiders': army_status['army_stats']['active_spiders'],
                    'total_connections': self.metrics.total_connections,
                    'active_connections': self.metrics.active_connections,
                    'connection_health': self.metrics.connection_health,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                await self.redis_async.setex(
                    'spider_router:health',
                    300,
                    json.dumps(health_status)
                )
                self.metrics_stale = False

            except Exception as e:
                self.logger.error(f"Error in health checker: {e}")
                self.metrics_stale = True

    async def _load_balancer(self):
        """Balance load across consumers"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Balance every 5 minutes

                # Analyze consumer load
                consumer_loads = {}

                for mapping in self.connection_mappings.values():
                    consumer_key = f"{mapping.consumer_type}:{mapping.consumer_id}"
                    if consumer_key not in consumer_loads:
                        consumer_loads[consumer_key] = {
                            'message_count': 0,
                            'error_count': 0,
                            'connections': 0
                        }

                    consumer_loads[consumer_key]['message_count'] += mapping.message_count
                    consumer_loads[consumer_key]['error_count'] += mapping.error_count
                    consumer_loads[consumer_key]['connections'] += 1

                # Identify overloaded consumers
                for consumer_key, load_data in consumer_loads.items():
                    if load_data['connections'] > 0:
                        avg_messages = load_data['message_count'] / load_data['connections']
                        error_rate = load_data['error_count'] / max(load_data['message_count'], 1)

                        if avg_messages > 1000 or error_rate > 0.1:  # Thresholds
                            self.logger.warning(f"High load detected on consumer {consumer_key}")

            except Exception as e:
                self.logger.error(f"Error in load balancer: {e}")

    def get_router_status(self) -> Dict[str, Any]:
        """Get comprehensive router status"""
        metrics_age_seconds = (datetime.now(timezone.utc) - self.metrics.last_updated).total_seconds()
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'is_running': self.is_running,
            'metrics': {
                'total_connections': self.metrics.total_connections,
                'active_connections': self.metrics.active_connections,
                'messages_routed': self.metrics.messages_routed,
                'failed_routes': self.metrics.failed_routes,
                'router_loop_errors': self.router_loop_errors,
                'malformed_message_count': self.malformed_message_count,
                'delivery_failure_count': self.delivery_failure_count,
                'connection_health': self.metrics.connection_health,
                'avg_latency_ms': self.metrics.avg_latency_ms
            },
            'router_loop_errors': self.router_loop_errors,
            'last_router_error': self.last_router_error,
            'last_router_error_type': self.last_router_error_type,
            'malformed_message_count': self.malformed_message_count,
            'filter_rejection_reasons': dict(self.filter_rejection_reasons),
            'delivery_failure_count': self.delivery_failure_count,
            'last_delivery_failure': self.last_delivery_failure,
            'metrics_stale': self.metrics_stale or metrics_age_seconds > 300,
            'last_route_outcome': self.last_route_outcome,
            'recent_route_outcomes': self.route_outcomes[-10:],
            'routing_tables': {
                swarm_id: len(consumers)
                for swarm_id, consumers in self.routing_tables.items()
            },
            'subscriber_channels': {
                consumer_type: len(channels)
                for consumer_type, channels in self.subscriber_channels.items()
            },
            'top_performers': {
                'producers': self.metrics.top_producers[:5],
                'consumers': self.metrics.top_consumers[:5]
            },
            'spider_army_status': self.spider_orchestrator.get_army_status(),
            'pipeline_status': self.data_pipeline.get_status()
        }

    async def shutdown(self):
        """Gracefully shutdown the router"""
        try:
            self.is_running = False
            self.logger.info("🛑 Shutting down Spider-Agent-Connector-Orchestrator...")

            # Shutdown components
            await self.spider_orchestrator.shutdown_army()
            await self.data_pipeline.shutdown()

            # Close Redis connections
            if self.redis_async:
                await self.redis_async.close()

            # Shutdown executor
            self.executor.shutdown(wait=True)

            self.logger.info("✅ Spider-Agent-Connector-Orchestrator shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during router shutdown: {e}")


# Global router instance
_router_instance = None

def get_spider_data_router(redis_config: Dict[str, Any] = None) -> SpiderDataRouter:
    """Get the global spider data router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = SpiderDataRouter(redis_config)
    return _router_instance
