"""
Real-Time Intelligence Data Pipeline
===================================

This module implements the real-time data pipeline that routes intelligence
from thousands of spiders to 102 agents and 25 legendary advisors. The pipeline
ensures low-latency, high-throughput intelligence distribution with quality
filtering and load balancing.

Features:
- Real-time intelligence streaming
- Quality filtering and validation
- Intelligent routing based on subscriber preferences
- Load balancing and failover
- Message deduplication and aggregation
- Performance monitoring and optimization
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
import redis
from redis import asyncio as aioredis
from enum import Enum
import hashlib
import uuid

logger = logging.getLogger(__name__)


def _safe_parse_timestamp(value) -> Optional[datetime]:
    """Parse a timestamp string to timezone-aware UTC datetime, or None."""
    if not value:
        return None
    try:
        from core.utils.time import normalize_timestamp
        return normalize_timestamp(value)
    except Exception:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except Exception:
                pass
        return None


class PipelineStatus(Enum):
    """Pipeline status states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class IntelligenceChannel(Enum):
    """Types of intelligence channels"""
    AGENT_DIRECT = "agent_direct"          # Direct to specific agent
    ADVISOR_DIRECT = "advisor_direct"      # Direct to specific advisor
    CATEGORY_BROADCAST = "category_broadcast"  # Broadcast to category
    GENERAL_FEED = "general_feed"          # General intelligence feed
    ALERT_CHANNEL = "alert_channel"        # High-priority alerts
    ANALYSIS_QUEUE = "analysis_queue"      # For further analysis


@dataclass
class PipelineMetrics:
    """Real-time pipeline performance metrics"""
    messages_processed: int = 0
    messages_routed: int = 0
    messages_filtered: int = 0
    messages_failed: int = 0
    avg_latency_ms: float = 0.0
    throughput_per_second: float = 0.0
    active_channels: int = 0
    subscriber_count: int = 0
    quality_score: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class IntelligenceMessage:
    """Structured intelligence message for pipeline"""
    id: str
    spider_id: str
    data_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float
    timestamp: datetime
    source_url: str
    relevance_tags: List[str]
    target_agents: List[str]
    target_advisors: List[str]
    priority: int = 1  # 1=highest, 10=lowest
    expiry: Optional[datetime] = None
    checksum: str = field(default="")

    def __post_init__(self):
        """Calculate message checksum for deduplication"""
        if not self.checksum:
            content_str = json.dumps(self.content, sort_keys=True)
            self.checksum = hashlib.md5(content_str.encode()).hexdigest()


class IntelligenceRouter:
    """Intelligent routing engine for intelligence messages"""

    def __init__(self):
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}
        self.advisor_profiles: Dict[str, Dict[str, Any]] = {}
        self.routing_rules: List[Dict[str, Any]] = []
        self.load_balancer: Dict[str, float] = {}  # Track load per subscriber

    def initialize_routing_profiles(self):
        """Initialize routing profiles for agents and advisors"""

        # Agent routing profiles (simplified - would be loaded from registry)
        self.agent_profiles = {
            "financial_analysis_agent": {
                "keywords": ["financial", "earnings", "revenue", "profit", "sec"],
                "data_types": ["sec_filing", "financial_news", "market_data"],
                "quality_threshold": 0.7,
                "max_load": 100
            },
            "crypto_trading_agent": {
                "keywords": ["crypto", "bitcoin", "ethereum", "blockchain", "defi"],
                "data_types": ["crypto_market_data", "crypto_news"],
                "quality_threshold": 0.8,
                "max_load": 200
            },
            "sentiment_analysis_agent": {
                "keywords": ["sentiment", "social", "reddit", "twitter"],
                "data_types": ["social_sentiment", "news_sentiment"],
                "quality_threshold": 0.6,
                "max_load": 150
            },
            "innovation_scout_agent": {
                "keywords": ["innovation", "patent", "research", "breakthrough"],
                "data_types": ["research_papers", "patent_intelligence", "tech_news"],
                "quality_threshold": 0.8,
                "max_load": 80
            }
        }

        # Advisor routing profiles
        self.advisor_profiles = {
            "warren_buffett": {
                "keywords": ["value", "fundamentals", "moat", "management", "berkshire"],
                "data_types": ["sec_filing", "financial_news", "earnings"],
                "quality_threshold": 0.9,
                "max_load": 50
            },
            "cathie_wood": {
                "keywords": ["innovation", "disruptive", "genomics", "ai", "ark"],
                "data_types": ["research_papers", "innovation_intelligence", "tech_news"],
                "quality_threshold": 0.9,
                "max_load": 50
            },
            "ray_dalio": {
                "keywords": ["macro", "economy", "debt", "cycles", "fed"],
                "data_types": ["economic_data", "fed_news", "market_data"],
                "quality_threshold": 0.9,
                "max_load": 50
            },
            "crypto_expert": {
                "keywords": ["crypto", "blockchain", "defi", "bitcoin", "ethereum"],
                "data_types": ["crypto_market_data", "blockchain_news"],
                "quality_threshold": 0.8,
                "max_load": 75
            }
        }

    def route_message(self, message: IntelligenceMessage) -> List[str]:
        """Route intelligence message to appropriate subscribers"""
        try:
            routes = []

            # Direct routing (highest priority)
            routes.extend(self._route_direct_targets(message))

            # Intelligent routing based on content
            routes.extend(self._route_by_content_analysis(message))

            # Broadcast routing for general intelligence
            routes.extend(self._route_general_broadcast(message))

            # Remove duplicates and apply load balancing
            return self._apply_load_balancing(list(set(routes)))

        except Exception as e:
            logger.error(f"Error routing message {message.id}: {e}")
            return []

    def _route_direct_targets(self, message: IntelligenceMessage) -> List[str]:
        """Route to directly specified targets"""
        routes = []

        # Add agent targets
        for agent in message.target_agents:
            if agent in self.agent_profiles:
                routes.append(f"agent:{agent}")

        # Add advisor targets
        for advisor in message.target_advisors:
            if advisor in self.advisor_profiles:
                routes.append(f"advisor:{advisor}")

        return routes

    def _route_by_content_analysis(self, message: IntelligenceMessage) -> List[str]:
        """Route based on content analysis and relevance"""
        routes = []

        # Analyze message content
        content_text = json.dumps(message.content).lower()
        tags_text = " ".join(message.relevance_tags).lower()
        combined_text = f"{content_text} {tags_text}"

        # Match against agent profiles
        for agent_id, profile in self.agent_profiles.items():
            if self._calculate_relevance_score(message, profile) > 0.5:
                if message.quality_score >= profile.get("quality_threshold", 0.7):
                    routes.append(f"agent:{agent_id}")

        # Match against advisor profiles
        for advisor_id, profile in self.advisor_profiles.items():
            if self._calculate_relevance_score(message, profile) > 0.7:  # Higher threshold for advisors
                if message.quality_score >= profile.get("quality_threshold", 0.8):
                    routes.append(f"advisor:{advisor_id}")

        return routes

    def _calculate_relevance_score(self, message: IntelligenceMessage, profile: Dict[str, Any]) -> float:
        """Calculate relevance score between message and subscriber profile"""
        score = 0.0

        # Content analysis
        content_text = json.dumps(message.content).lower()
        tags_text = " ".join(message.relevance_tags).lower()
        combined_text = f"{content_text} {tags_text}"

        # Keyword matching
        keywords = profile.get("keywords", [])
        keyword_matches = sum(1 for keyword in keywords if keyword in combined_text)
        if keywords:
            score += (keyword_matches / len(keywords)) * 0.6

        # Data type matching
        data_types = profile.get("data_types", [])
        if message.data_type in data_types:
            score += 0.4

        return min(1.0, score)

    def _route_general_broadcast(self, message: IntelligenceMessage) -> List[str]:
        """Route to general broadcast channels"""
        routes = []

        # High-quality general intelligence goes to category feeds
        if message.quality_score > 0.8:
            category = self._determine_category(message)
            routes.append(f"category:{category}")

        # Breaking news or alerts
        if message.priority <= 2 or "breaking" in message.relevance_tags:
            routes.append("alert:high_priority")

        return routes

    def _determine_category(self, message: IntelligenceMessage) -> str:
        """Determine the category for broadcast routing"""
        data_type = message.data_type

        if "financial" in data_type or "market" in data_type:
            return "financial"
        elif "crypto" in data_type or "blockchain" in data_type:
            return "crypto"
        elif "social" in data_type or "sentiment" in data_type:
            return "social"
        elif "research" in data_type or "innovation" in data_type:
            return "research"
        elif "news" in data_type:
            return "news"
        else:
            return "general"

    def _apply_load_balancing(self, routes: List[str]) -> List[str]:
        """Apply load balancing to prevent overwhelming subscribers"""
        balanced_routes = []

        for route in routes:
            current_load = self.load_balancer.get(route, 0)
            max_load = self._get_max_load_for_route(route)

            if current_load < max_load:
                balanced_routes.append(route)
                self.load_balancer[route] = current_load + 1

        return balanced_routes

    def _get_max_load_for_route(self, route: str) -> int:
        """Get maximum load threshold for a route"""
        route_type, route_id = route.split(":", 1)

        if route_type == "agent":
            return self.agent_profiles.get(route_id, {}).get("max_load", 100)
        elif route_type == "advisor":
            return self.advisor_profiles.get(route_id, {}).get("max_load", 50)
        else:
            return 1000  # High limit for broadcast channels

    def reset_load_counters(self):
        """Reset load counters (called periodically)"""
        self.load_balancer.clear()


class RealTimeDataPipeline:
    """
    Real-time intelligence data pipeline.

    Handles the flow of intelligence from spiders to agents and advisors
    with quality filtering, intelligent routing, and performance optimization.
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        """Initialize the data pipeline"""
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}

        # Redis connections
        self.redis_client = redis.Redis(**self.redis_config)
        self.redis_async = None  # Will be initialized in start()

        # Pipeline components
        self.router = IntelligenceRouter()
        self.message_cache: Dict[str, IntelligenceMessage] = {}
        self.processed_checksums: Set[str] = set()

        # Pipeline state
        self.status = PipelineStatus.INITIALIZING
        self.metrics = PipelineMetrics()
        self.is_running = False

        # Configuration
        self.max_cache_size = 10000
        self.deduplication_window = 3600  # 1 hour
        self.quality_threshold = 0.5
        self.batch_size = 100

        # Performance tracking
        self.message_timestamps: List[datetime] = []
        self.processing_times: List[float] = []

        self.logger = logging.getLogger(__name__)

    async def start(self):
        """Start the real-time data pipeline"""
        try:
            self.logger.info("🚀 Starting Real-Time Intelligence Data Pipeline...")

            # Initialize async Redis connection
            self.redis_async = aioredis.from_url(
                f"redis://{self.redis_config['host']}:{self.redis_config['port']}/{self.redis_config['db']}"
            )

            # Initialize routing profiles
            self.router.initialize_routing_profiles()

            # Set status
            self.status = PipelineStatus.RUNNING
            self.is_running = True

            # Start pipeline tasks
            tasks = [
                asyncio.create_task(self._message_processor()),
                asyncio.create_task(self._quality_filter()),
                asyncio.create_task(self._routing_engine()),
                asyncio.create_task(self._delivery_manager()),
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._cache_manager()),
                asyncio.create_task(self._health_monitor())
            ]

            self.logger.info("✅ Data Pipeline started successfully")

            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Failed to start data pipeline: {e}")
            self.status = PipelineStatus.ERROR
        finally:
            await self.shutdown()

    async def _message_processor(self):
        """Main message processing loop"""
        while self.is_running:
            try:
                # Get messages from spider input queue
                messages = await self._get_incoming_messages()

                if messages:
                    # Process batch
                    await self._process_message_batch(messages)

                    # Update metrics
                    self.metrics.messages_processed += len(messages)

                else:
                    # No messages, brief sleep
                    await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Error in message processor: {e}")
                await asyncio.sleep(1)

    async def _get_incoming_messages(self) -> List[IntelligenceMessage]:
        """Get incoming messages from spider input queue"""
        try:
            messages = []

            # Get messages from Redis list (blocking pop with timeout)
            for _ in range(self.batch_size):
                message_data = await self.redis_async.blpop(
                    'pipeline:input',
                    timeout=0.1  # Non-blocking with short timeout
                )

                if message_data:
                    _, message_json = message_data
                    try:
                        message_dict = json.loads(message_json)
                        message = self._dict_to_message(message_dict)
                        messages.append(message)
                    except json.JSONDecodeError:
                        self.logger.warning("Invalid message JSON in input queue")
                        self.metrics.messages_failed += 1
                else:
                    break

            return messages

        except Exception as e:
            self.logger.error(f"Error getting incoming messages: {e}")
            return []

    def _dict_to_message(self, message_dict: Dict[str, Any]) -> IntelligenceMessage:
        """Convert dictionary to IntelligenceMessage"""
        return IntelligenceMessage(
            id=message_dict.get('id', str(uuid.uuid4())),
            spider_id=message_dict.get('spider_id', ''),
            data_type=message_dict.get('data_type', ''),
            content=message_dict.get('content', {}),
            metadata=message_dict.get('metadata', {}),
            quality_score=message_dict.get('quality_score', 0.0),
            timestamp=_safe_parse_timestamp(message_dict.get('timestamp')) or datetime.now(timezone.utc),
            source_url=message_dict.get('source_url', ''),
            relevance_tags=message_dict.get('relevance_tags', []),
            target_agents=message_dict.get('target_agents', []),
            target_advisors=message_dict.get('target_advisors', []),
            priority=message_dict.get('priority', 5),
            expiry=_safe_parse_timestamp(message_dict.get('expiry')),
            checksum=message_dict.get('checksum', '')
        )

    async def _process_message_batch(self, messages: List[IntelligenceMessage]):
        """Process a batch of messages"""
        try:
            start_time = datetime.now()

            for message in messages:
                # Store in cache for processing
                self.message_cache[message.id] = message

                # Add to quality filter queue
                await self.redis_async.rpush('pipeline:quality_filter', message.id)

            # Track processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_times.append(processing_time)

            # Keep only recent processing times
            if len(self.processing_times) > 1000:
                self.processing_times = self.processing_times[-1000:]

        except Exception as e:
            self.logger.error(f"Error processing message batch: {e}")

    async def _quality_filter(self):
        """Quality filtering stage of the pipeline"""
        while self.is_running:
            try:
                # Get message ID from quality filter queue
                message_id_data = await self.redis_async.blpop(
                    'pipeline:quality_filter',
                    timeout=1
                )

                if message_id_data:
                    _, message_id = message_id_data
                    message_id = message_id.decode('utf-8')

                    message = self.message_cache.get(message_id)
                    if message:
                        if await self._passes_quality_filter(message):
                            # Passed quality filter, send to routing
                            await self.redis_async.rpush('pipeline:routing', message_id)
                        else:
                            # Failed quality filter
                            self.metrics.messages_filtered += 1
                            self._remove_from_cache(message_id)

            except Exception as e:
                self.logger.error(f"Error in quality filter: {e}")
                await asyncio.sleep(1)

    async def _passes_quality_filter(self, message: IntelligenceMessage) -> bool:
        """Check if message passes quality filters"""
        try:
            # Quality score threshold
            if message.quality_score < self.quality_threshold:
                return False

            # Deduplication check
            if message.checksum in self.processed_checksums:
                return False

            # Expiry check
            if message.expiry and datetime.now(timezone.utc) > message.expiry:
                return False

            # Content validation
            if not message.content or not message.data_type:
                return False

            # Add to processed checksums
            self.processed_checksums.add(message.checksum)

            # Limit checksum cache size
            if len(self.processed_checksums) > 50000:
                # Remove old checksums (simplified - would use LRU)
                old_checksums = list(self.processed_checksums)[:10000]
                self.processed_checksums -= set(old_checksums)

            return True

        except Exception as e:
            self.logger.error(f"Error in quality filter for message {message.id}: {e}")
            return False

    async def _routing_engine(self):
        """Message routing stage of the pipeline"""
        while self.is_running:
            try:
                # Get message ID from routing queue
                message_id_data = await self.redis_async.blpop(
                    'pipeline:routing',
                    timeout=1
                )

                if message_id_data:
                    _, message_id = message_id_data
                    message_id = message_id.decode('utf-8')

                    message = self.message_cache.get(message_id)
                    if message:
                        # Route message
                        routes = self.router.route_message(message)

                        if routes:
                            # Create routing tasks
                            for route in routes:
                                routing_task = {
                                    'message_id': message_id,
                                    'route': route,
                                    'timestamp': datetime.now(timezone.utc).isoformat()
                                }

                                await self.redis_async.rpush(
                                    'pipeline:delivery',
                                    json.dumps(routing_task)
                                )

                            self.metrics.messages_routed += 1
                        else:
                            # No routes found
                            self.logger.debug(f"No routes found for message {message_id}")
                            self._remove_from_cache(message_id)

            except Exception as e:
                self.logger.error(f"Error in routing engine: {e}")
                await asyncio.sleep(1)

    async def _delivery_manager(self):
        """Message delivery stage of the pipeline"""
        while self.is_running:
            try:
                # Get routing task from delivery queue
                task_data = await self.redis_async.blpop(
                    'pipeline:delivery',
                    timeout=1
                )

                if task_data:
                    _, task_json = task_data
                    try:
                        routing_task = json.loads(task_json)
                        await self._deliver_message(routing_task)
                    except json.JSONDecodeError:
                        self.logger.warning("Invalid routing task JSON")

            except Exception as e:
                self.logger.error(f"Error in delivery manager: {e}")
                await asyncio.sleep(1)

    async def _deliver_message(self, routing_task: Dict[str, Any]):
        """Deliver message to specific route"""
        try:
            message_id = routing_task['message_id']
            route = routing_task['route']

            message = self.message_cache.get(message_id)
            if not message:
                return

            # Prepare delivery payload
            delivery_payload = {
                'id': message.id,
                'spider_id': message.spider_id,
                'data_type': message.data_type,
                'content': message.content,
                'metadata': message.metadata,
                'quality_score': message.quality_score,
                'timestamp': message.timestamp.isoformat(),
                'source_url': message.source_url,
                'relevance_tags': message.relevance_tags,
                'priority': message.priority,
                'delivered_at': datetime.now(timezone.utc).isoformat(),
                'route': route
            }

            # Deliver to specific channel
            channel_name = f"intelligence:{route}"
            await self.redis_async.publish(
                channel_name,
                json.dumps(delivery_payload)
            )

            # Also store in Redis for historical access
            await self.redis_async.setex(
                f"intelligence:history:{message.id}",
                3600,  # 1 hour expiry
                json.dumps(delivery_payload)
            )

            self.logger.debug(f"Delivered message {message_id} to {route}")

            # Clean up cache
            self._remove_from_cache(message_id)

        except Exception as e:
            self.logger.error(f"Error delivering message {routing_task.get('message_id')}: {e}")

    def _remove_from_cache(self, message_id: str):
        """Remove message from cache"""
        if message_id in self.message_cache:
            del self.message_cache[message_id]

    async def _metrics_collector(self):
        """Collect and update pipeline metrics"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Update every minute

                # Calculate throughput
                current_time = datetime.now(timezone.utc)
                one_minute_ago = current_time - timedelta(minutes=1)

                # Count recent messages
                recent_messages = [
                    ts for ts in self.message_timestamps
                    if ts >= one_minute_ago
                ]

                self.metrics.throughput_per_second = len(recent_messages) / 60

                # Calculate average latency
                if self.processing_times:
                    self.metrics.avg_latency_ms = (sum(self.processing_times) / len(self.processing_times)) * 1000

                # Count active channels
                channel_pattern = "intelligence:*"
                channels = await self.redis_async.keys(channel_pattern)
                self.metrics.active_channels = len(channels)

                # Update timestamp
                self.metrics.last_updated = current_time

                # Store metrics in Redis
                await self.redis_async.setex(
                    'pipeline:metrics',
                    300,  # 5 minute expiry
                    json.dumps({
                        'messages_processed': self.metrics.messages_processed,
                        'messages_routed': self.metrics.messages_routed,
                        'messages_filtered': self.metrics.messages_filtered,
                        'messages_failed': self.metrics.messages_failed,
                        'avg_latency_ms': self.metrics.avg_latency_ms,
                        'throughput_per_second': self.metrics.throughput_per_second,
                        'active_channels': self.metrics.active_channels,
                        'quality_score': self.metrics.quality_score,
                        'last_updated': self.metrics.last_updated.isoformat()
                    })
                )

                # Clean old timestamps
                self.message_timestamps = [ts for ts in self.message_timestamps if ts >= one_minute_ago]

            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")

    async def _cache_manager(self):
        """Manage message cache size and cleanup"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes

                # Check cache size
                if len(self.message_cache) > self.max_cache_size:
                    # Remove oldest messages
                    sorted_messages = sorted(
                        self.message_cache.items(),
                        key=lambda x: x[1].timestamp
                    )

                    # Remove oldest 10%
                    remove_count = len(sorted_messages) // 10
                    for message_id, _ in sorted_messages[:remove_count]:
                        self._remove_from_cache(message_id)

                    self.logger.info(f"Cleaned {remove_count} old messages from cache")

                # Reset router load counters
                self.router.reset_load_counters()

            except Exception as e:
                self.logger.error(f"Error in cache manager: {e}")

    async def _health_monitor(self):
        """Monitor pipeline health and performance"""
        while self.is_running:
            try:
                await asyncio.sleep(120)  # Check every 2 minutes

                # Check queue sizes
                queue_sizes = {
                    'input': await self.redis_async.llen('pipeline:input'),
                    'quality_filter': await self.redis_async.llen('pipeline:quality_filter'),
                    'routing': await self.redis_async.llen('pipeline:routing'),
                    'delivery': await self.redis_async.llen('pipeline:delivery')
                }

                # Check for bottlenecks
                for queue_name, size in queue_sizes.items():
                    if size > 1000:  # High queue size threshold
                        self.logger.warning(f"High queue size detected: {queue_name} = {size}")

                # Store health status
                health_status = {
                    'status': self.status.value,
                    'queue_sizes': queue_sizes,
                    'cache_size': len(self.message_cache),
                    'processed_checksums': len(self.processed_checksums),
                    'is_running': self.is_running,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

                await self.redis_async.setex(
                    'pipeline:health',
                    300,
                    json.dumps(health_status)
                )

            except Exception as e:
                self.logger.error(f"Error in health monitor: {e}")

    async def inject_message(self, message: IntelligenceMessage):
        """Inject a message into the pipeline (for testing or manual input)"""
        try:
            message_dict = {
                'id': message.id,
                'spider_id': message.spider_id,
                'data_type': message.data_type,
                'content': message.content,
                'metadata': message.metadata,
                'quality_score': message.quality_score,
                'timestamp': message.timestamp.isoformat(),
                'source_url': message.source_url,
                'relevance_tags': message.relevance_tags,
                'target_agents': message.target_agents,
                'target_advisors': message.target_advisors,
                'priority': message.priority,
                'expiry': message.expiry.isoformat() if message.expiry else None,
                'checksum': message.checksum
            }

            await self.redis_async.rpush(
                'pipeline:input',
                json.dumps(message_dict)
            )

            self.logger.debug(f"Injected message {message.id} into pipeline")

        except Exception as e:
            self.logger.error(f"Error injecting message: {e}")

    def get_metrics(self) -> PipelineMetrics:
        """Get current pipeline metrics"""
        return self.metrics

    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            'status': self.status.value,
            'is_running': self.is_running,
            'metrics': {
                'messages_processed': self.metrics.messages_processed,
                'messages_routed': self.metrics.messages_routed,
                'messages_filtered': self.metrics.messages_filtered,
                'throughput_per_second': self.metrics.throughput_per_second,
                'active_channels': self.metrics.active_channels
            },
            'cache_size': len(self.message_cache),
            'queue_health': 'healthy',  # Would check queue sizes
            'last_updated': self.metrics.last_updated.isoformat()
        }

    async def pause(self):
        """Pause the pipeline"""
        self.status = PipelineStatus.PAUSED
        self.logger.info("🛑 Data pipeline paused")

    async def resume(self):
        """Resume the pipeline"""
        self.status = PipelineStatus.RUNNING
        self.logger.info("▶️ Data pipeline resumed")

    async def shutdown(self):
        """Shutdown the pipeline gracefully"""
        try:
            self.is_running = False
            self.status = PipelineStatus.SHUTDOWN

            # Close Redis connections
            if self.redis_async:
                await self.redis_async.close()

            self.logger.info("🛑 Data Pipeline shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during pipeline shutdown: {e}")


# Global pipeline instance
_pipeline_instance = None

def get_data_pipeline(redis_config: Dict[str, Any] = None) -> RealTimeDataPipeline:
    """Get the global data pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RealTimeDataPipeline(redis_config)
    return _pipeline_instance