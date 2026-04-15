"""
Agent Spider Data Receiver - Real-Time Intelligence Integration
===============================================================

This module provides mixins and base classes that enable agents to receive
and process real-time intelligence data from spider networks. Agents can
subscribe to specific data streams, process intelligence with their unique
capabilities, and integrate spider data into their decision-making processes.

Features:
- Real-time data stream subscription
- Agent-specific data filtering and processing
- Asynchronous message handling
- Performance monitoring and optimization
- Error handling and reconnection logic
"""

import asyncio
import json
import logging
import redis
from redis import asyncio as aioredis
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from enum import Enum
import uuid


def _safe_parse_ts(value) -> Optional[datetime]:
    """Parse timestamp to timezone-aware UTC, or None."""
    if not value:
        return None
    try:
        from core.utils.time import normalize_timestamp
        return normalize_timestamp(value)
    except Exception:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except Exception as _e:
                logger.warning(
                    "agent_data_receiver._safe_parse_ts: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        return None

logger = logging.getLogger(__name__)


class DataProcessingPriority(Enum):
    """Priority levels for data processing"""
    IMMEDIATE = 1    # Critical data requiring instant processing
    HIGH = 2         # Important data processed within minutes
    NORMAL = 3       # Standard data processed within hours
    LOW = 4          # Background data processed when idle


class ProcessingStatus(Enum):
    """Status of data processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class IntelligenceData:
    """Structured intelligence data for agent processing"""
    id: str
    spider_id: str
    data_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float
    timestamp: datetime
    source_url: str
    relevance_tags: List[str]
    priority: DataProcessingPriority
    agent_id: str
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    processed_at: Optional[datetime] = None
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class AgentDataSubscription:
    """Agent subscription configuration"""
    agent_id: str
    channel_pattern: str
    data_types: List[str]
    keywords: List[str]
    quality_threshold: float
    max_queue_size: int = 1000
    processing_timeout_seconds: int = 300
    retry_attempts: int = 3
    is_active: bool = True


@dataclass
class ProcessingMetrics:
    """Metrics for agent data processing"""
    total_received: int = 0
    total_processed: int = 0
    total_failed: int = 0
    total_skipped: int = 0
    avg_processing_time_ms: float = 0.0
    avg_quality_score: float = 0.0
    last_processed_at: Optional[datetime] = None
    queue_size: int = 0
    error_rate: float = 0.0


class AgentSpiderDataReceiver(ABC):
    """
    Abstract base class for agents that receive spider intelligence data.

    Provides the core infrastructure for subscribing to data streams,
    processing intelligence, and integrating with agent workflows.
    """

    def __init__(self, agent_id: str, redis_config: Dict[str, Any] = None):
        """Initialize the agent data receiver"""
        self.agent_id = agent_id
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}

        # Redis connections
        self.redis_client = redis.Redis(**self.redis_config)
        self.redis_async = None

        # Data management
        self.subscriptions: Dict[str, AgentDataSubscription] = {}
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.processed_data: Dict[str, IntelligenceData] = {}

        # Performance tracking
        self.metrics = ProcessingMetrics()
        self.processing_history: List[ProcessingMetrics] = []

        # Configuration
        self.max_processed_data_cache = 1000
        self.cleanup_interval_seconds = 300

        # State management
        self.is_running = False
        self.processing_tasks: List[asyncio.Task] = []

        self.logger = logging.getLogger(f"{__name__}.{agent_id}")

    async def start_data_receiver(self):
        """Start the agent data receiver"""
        try:
            self.logger.info(f"🚀 Starting data receiver for agent: {self.agent_id}")

            # Initialize async Redis connection
            self.redis_async = aioredis.from_url(
                f"redis://{self.redis_config['host']}:{self.redis_config['port']}/{self.redis_config['db']}"
            )

            # Initialize subscriptions
            await self._initialize_agent_subscriptions()

            # Set running state
            self.is_running = True

            # Start processing tasks
            self.processing_tasks = [
                asyncio.create_task(self._subscription_listener()),
                asyncio.create_task(self._data_processor()),
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._cleanup_manager())
            ]

            self.logger.info(f"✅ Data receiver started for agent: {self.agent_id}")

            # Wait for all tasks
            await asyncio.gather(*self.processing_tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Failed to start data receiver for {self.agent_id}: {e}")
            raise
        finally:
            await self.shutdown()

    @abstractmethod
    async def _initialize_agent_subscriptions(self):
        """Initialize agent-specific subscriptions (implemented by each agent)"""

    @abstractmethod
    async def process_intelligence_data(self, data: IntelligenceData) -> Dict[str, Any]:
        """Process intelligence data (implemented by each agent)"""

    def add_subscription(self, subscription: AgentDataSubscription):
        """Add a data subscription for this agent"""
        self.subscriptions[subscription.channel_pattern] = subscription
        self.logger.info(f"Added subscription for channel: {subscription.channel_pattern}")

    async def _subscription_listener(self):
        """Listen to subscribed channels for incoming data"""
        while self.is_running:
            try:
                # Create pubsub client
                pubsub = self.redis_async.pubsub()

                # Subscribe to all configured channels
                channel_patterns = list(self.subscriptions.keys())
                if channel_patterns:
                    await pubsub.psubscribe(*channel_patterns)

                    self.logger.info(f"Subscribed to {len(channel_patterns)} channels")

                    # Listen for messages
                    async for message in pubsub.listen():
                        if message['type'] == 'pmessage':
                            await self._handle_incoming_message(message)

                await asyncio.sleep(1)  # Brief pause before reconnecting

            except Exception as e:
                self.logger.error(f"Error in subscription listener: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _handle_incoming_message(self, message: Dict[str, Any]):
        """Handle incoming intelligence message"""
        try:
            # Parse message
            channel = message['channel'].decode('utf-8')
            data_json = message['data'].decode('utf-8')
            data_dict = json.loads(data_json)

            # Find matching subscription
            subscription = self._find_matching_subscription(channel)
            if not subscription:
                return

            # Validate data against subscription criteria
            if not self._validate_data_for_subscription(data_dict, subscription):
                self.metrics.total_skipped += 1
                return

            # Create intelligence data object
            intelligence_data = IntelligenceData(
                id=data_dict.get('id', str(uuid.uuid4())),
                spider_id=data_dict.get('spider_id', ''),
                data_type=data_dict.get('data_type', ''),
                content=data_dict.get('content', {}),
                metadata=data_dict.get('metadata', {}),
                quality_score=data_dict.get('quality_score', 0.0),
                timestamp=_safe_parse_ts(data_dict.get('timestamp')) or datetime.now(timezone.utc),
                source_url=data_dict.get('source_url', ''),
                relevance_tags=data_dict.get('relevance_tags', []),
                priority=DataProcessingPriority(data_dict.get('priority', 3)),
                agent_id=self.agent_id
            )

            # Add to processing queue
            await self.processing_queue.put(intelligence_data)
            self.metrics.total_received += 1
            self.metrics.queue_size = self.processing_queue.qsize()

        except Exception as e:
            self.logger.error(f"Error handling incoming message: {e}")

    def _find_matching_subscription(self, channel: str) -> Optional[AgentDataSubscription]:
        """Find subscription that matches the channel"""
        for pattern, subscription in self.subscriptions.items():
            if subscription.is_active:
                # Simple pattern matching (could be enhanced with regex)
                if channel.startswith(pattern.replace('*', '')):
                    return subscription
        return None

    def _validate_data_for_subscription(self, data: Dict[str, Any], subscription: AgentDataSubscription) -> bool:
        """Validate data against subscription criteria"""
        try:
            # Quality threshold check
            quality_score = data.get('quality_score', 0.0)
            if quality_score < subscription.quality_threshold:
                return False

            # Data type filter
            data_type = data.get('data_type', '')
            if subscription.data_types and data_type not in subscription.data_types:
                return False

            # Keyword filter
            if subscription.keywords:
                content_text = json.dumps(data.get('content', {})).lower()
                if not any(keyword.lower() in content_text for keyword in subscription.keywords):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
            return False

    async def _data_processor(self):
        """Process queued intelligence data"""
        while self.is_running:
            try:
                # Get data from queue with timeout
                try:
                    data = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                # Process the data
                await self._process_single_data(data)

            except Exception as e:
                self.logger.error(f"Error in data processor: {e}")
                await asyncio.sleep(1)

    async def _process_single_data(self, data: IntelligenceData):
        """Process a single intelligence data item"""
        try:
            start_time = datetime.now()
            data.processing_status = ProcessingStatus.PROCESSING

            # Call agent-specific processing
            result = await self.process_intelligence_data(data)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            data.processing_time_ms = processing_time
            data.processed_at = datetime.now(timezone.utc)
            data.processing_status = ProcessingStatus.COMPLETED

            # Store processed data
            self.processed_data[data.id] = data

            # Update metrics
            self.metrics.total_processed += 1
            self.metrics.last_processed_at = data.processed_at

            # Update average processing time
            if self.metrics.avg_processing_time_ms == 0:
                self.metrics.avg_processing_time_ms = processing_time
            else:
                self.metrics.avg_processing_time_ms = (
                    self.metrics.avg_processing_time_ms * 0.9 + processing_time * 0.1
                )

            # Update average quality score
            if self.metrics.avg_quality_score == 0:
                self.metrics.avg_quality_score = data.quality_score
            else:
                self.metrics.avg_quality_score = (
                    self.metrics.avg_quality_score * 0.9 + data.quality_score * 0.1
                )

            # Store processing result if provided
            if result:
                await self._store_processing_result(data.id, result)

            self.logger.debug(f"Processed data {data.id} in {processing_time:.2f}ms")

        except Exception as e:
            data.processing_status = ProcessingStatus.FAILED
            data.error_message = str(e)
            self.metrics.total_failed += 1
            self.logger.error(f"Failed to process data {data.id}: {e}")

    async def _store_processing_result(self, data_id: str, result: Dict[str, Any]):
        """Store processing result in Redis"""
        try:
            result_key = f"agent_processing:{self.agent_id}:{data_id}"
            await self.redis_async.setex(
                result_key,
                3600,  # 1 hour expiry
                json.dumps(result)
            )
        except Exception as e:
            self.logger.error(f"Failed to store processing result: {e}")

    async def _metrics_collector(self):
        """Collect and update processing metrics"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Update every minute

                # Calculate error rate
                total_processed = self.metrics.total_processed + self.metrics.total_failed
                if total_processed > 0:
                    self.metrics.error_rate = self.metrics.total_failed / total_processed

                # Update queue size
                self.metrics.queue_size = self.processing_queue.qsize()

                # Store metrics in Redis
                metrics_data = {
                    'agent_id': self.agent_id,
                    'total_received': self.metrics.total_received,
                    'total_processed': self.metrics.total_processed,
                    'total_failed': self.metrics.total_failed,
                    'total_skipped': self.metrics.total_skipped,
                    'avg_processing_time_ms': self.metrics.avg_processing_time_ms,
                    'avg_quality_score': self.metrics.avg_quality_score,
                    'queue_size': self.metrics.queue_size,
                    'error_rate': self.metrics.error_rate,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }

                await self.redis_async.setex(
                    f"agent_metrics:{self.agent_id}",
                    300,  # 5 minute expiry
                    json.dumps(metrics_data)
                )

                # Store historical metrics
                self.processing_history.append(ProcessingMetrics(
                    total_received=self.metrics.total_received,
                    total_processed=self.metrics.total_processed,
                    total_failed=self.metrics.total_failed,
                    total_skipped=self.metrics.total_skipped,
                    avg_processing_time_ms=self.metrics.avg_processing_time_ms,
                    avg_quality_score=self.metrics.avg_quality_score,
                    queue_size=self.metrics.queue_size,
                    error_rate=self.metrics.error_rate
                ))

                # Keep only last 24 hours of history
                if len(self.processing_history) > 1440:  # 24 hours of minute-by-minute data
                    self.processing_history = self.processing_history[-1440:]

            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")

    async def _cleanup_manager(self):
        """Manage data cleanup and cache size"""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval_seconds)

                # Clean processed data cache if too large
                if len(self.processed_data) > self.max_processed_data_cache:
                    # Remove oldest processed data
                    sorted_data = sorted(
                        self.processed_data.items(),
                        key=lambda x: x[1].processed_at or datetime.min.replace(tzinfo=timezone.utc)
                    )

                    # Remove oldest 20%
                    remove_count = len(sorted_data) // 5
                    for data_id, _ in sorted_data[:remove_count]:
                        del self.processed_data[data_id]

                    self.logger.info(f"Cleaned {remove_count} old processed data items")

            except Exception as e:
                self.logger.error(f"Error in cleanup manager: {e}")

    def get_processing_metrics(self) -> ProcessingMetrics:
        """Get current processing metrics"""
        return self.metrics

    def get_processed_data(self, limit: int = 100) -> List[IntelligenceData]:
        """Get recently processed data"""
        sorted_data = sorted(
            self.processed_data.values(),
            key=lambda x: x.processed_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True
        )
        return sorted_data[:limit]

    def get_status(self) -> Dict[str, Any]:
        """Get current agent data receiver status"""
        return {
            'agent_id': self.agent_id,
            'is_running': self.is_running,
            'subscriptions': {
                pattern: {
                    'data_types': sub.data_types,
                    'keywords': sub.keywords,
                    'quality_threshold': sub.quality_threshold,
                    'is_active': sub.is_active
                }
                for pattern, sub in self.subscriptions.items()
            },
            'metrics': {
                'total_received': self.metrics.total_received,
                'total_processed': self.metrics.total_processed,
                'total_failed': self.metrics.total_failed,
                'total_skipped': self.metrics.total_skipped,
                'queue_size': self.metrics.queue_size,
                'error_rate': self.metrics.error_rate,
                'avg_processing_time_ms': self.metrics.avg_processing_time_ms,
                'avg_quality_score': self.metrics.avg_quality_score
            },
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

    async def shutdown(self):
        """Shutdown the agent data receiver"""
        try:
            self.is_running = False

            # Cancel processing tasks
            for task in self.processing_tasks:
                task.cancel()

            # Wait for tasks to complete
            if self.processing_tasks:
                await asyncio.gather(*self.processing_tasks, return_exceptions=True)

            # Close Redis connection
            if self.redis_async:
                await self.redis_async.close()

            self.logger.info(f"✅ Data receiver shutdown complete for agent: {self.agent_id}")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


class FinancialAgentDataReceiver(AgentSpiderDataReceiver):
    """Specialized data receiver for financial agents"""

    async def _initialize_agent_subscriptions(self):
        """Initialize financial agent subscriptions"""
        financial_subscription = AgentDataSubscription(
            agent_id=self.agent_id,
            channel_pattern="intelligence:agent:*",
            data_types=["financial_news", "sec_filing", "earnings_report", "market_data"],
            keywords=["financial", "earnings", "revenue", "profit", "dividend"],
            quality_threshold=0.8,
            max_queue_size=2000,
            processing_timeout_seconds=600
        )

        self.add_subscription(financial_subscription)

    async def process_intelligence_data(self, data: IntelligenceData) -> Dict[str, Any]:
        """Process financial intelligence data"""
        try:
            # Extract financial metrics
            content = data.content

            # Basic financial data processing
            processed_result = {
                'agent_id': self.agent_id,
                'data_id': data.id,
                'processing_type': 'financial_analysis',
                'extracted_metrics': {},
                'insights': [],
                'recommendations': [],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            # Extract common financial metrics
            if 'revenue' in str(content).lower():
                processed_result['extracted_metrics']['has_revenue_data'] = True

            if 'profit' in str(content).lower():
                processed_result['extracted_metrics']['has_profit_data'] = True

            if 'dividend' in str(content).lower():
                processed_result['extracted_metrics']['has_dividend_data'] = True

            # Add quality-based insights
            if data.quality_score > 0.9:
                processed_result['insights'].append('High-quality financial intelligence')

            return processed_result

        except Exception as e:
            self.logger.error(f"Error processing financial data: {e}")
            return {'error': str(e)}


class InnovationAgentDataReceiver(AgentSpiderDataReceiver):
    """Specialized data receiver for innovation agents"""

    async def _initialize_agent_subscriptions(self):
        """Initialize innovation agent subscriptions"""
        innovation_subscription = AgentDataSubscription(
            agent_id=self.agent_id,
            channel_pattern="intelligence:agent:*",
            data_types=["research_papers", "patent_data", "tech_news", "innovation_intelligence"],
            keywords=["innovation", "research", "patent", "technology", "breakthrough"],
            quality_threshold=0.85,
            max_queue_size=1500
        )

        self.add_subscription(innovation_subscription)

    async def process_intelligence_data(self, data: IntelligenceData) -> Dict[str, Any]:
        """Process innovation intelligence data"""
        try:
            content = data.content

            processed_result = {
                'agent_id': self.agent_id,
                'data_id': data.id,
                'processing_type': 'innovation_analysis',
                'innovation_indicators': {},
                'technology_trends': [],
                'research_insights': [],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            # Identify innovation indicators
            content_text = str(content).lower()

            if 'patent' in content_text:
                processed_result['innovation_indicators']['patent_activity'] = True

            if 'research' in content_text:
                processed_result['innovation_indicators']['research_activity'] = True

            if any(term in content_text for term in ['ai', 'artificial intelligence', 'machine learning']):
                processed_result['technology_trends'].append('AI/ML')

            if any(term in content_text for term in ['blockchain', 'crypto', 'defi']):
                processed_result['technology_trends'].append('Blockchain')

            return processed_result

        except Exception as e:
            self.logger.error(f"Error processing innovation data: {e}")
            return {'error': str(e)}


# Factory function for creating agent data receivers
def create_agent_data_receiver(agent_id: str, agent_type: str, redis_config: Dict[str, Any] = None) -> AgentSpiderDataReceiver:
    """Create appropriate data receiver based on agent type"""

    if agent_type in ['financial', 'financial_strategist', 'income_builder', 'dividend_hunter']:
        return FinancialAgentDataReceiver(agent_id, redis_config)
    elif agent_type in ['innovation', 'ai_strategist', 'tech_architect', 'patent_analyzer']:
        return InnovationAgentDataReceiver(agent_id, redis_config)
    else:
        # Default receiver for other agent types
        class DefaultAgentDataReceiver(AgentSpiderDataReceiver):
            async def _initialize_agent_subscriptions(self):
                subscription = AgentDataSubscription(
                    agent_id=self.agent_id,
                    channel_pattern="intelligence:agent:*",
                    data_types=[],  # Accept all data types
                    keywords=[],    # Accept all keywords
                    quality_threshold=0.7
                )
                self.add_subscription(subscription)

            async def process_intelligence_data(self, data: IntelligenceData) -> Dict[str, Any]:
                return {
                    'agent_id': self.agent_id,
                    'data_id': data.id,
                    'processing_type': 'generic_analysis',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }

        return DefaultAgentDataReceiver(agent_id, redis_config)