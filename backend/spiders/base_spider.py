"""
Base Intelligence Spider - Foundation for All Spider Operations
==============================================================

This module provides the foundational base class for all intelligence gathering
spiders in the Spider Army. Each spider inherits from this base to ensure
consistent operation, data quality, and integration with the unified platform.
"""

import asyncio
import aiohttp
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse
import redis
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class SpiderMetrics:
    """Performance metrics for spider operations"""
    spider_id: str
    data_points_collected: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_active: Optional[datetime] = None
    uptime_percentage: float = 100.0
    rate_limit_hits: int = 0
    data_quality_score: float = 0.0


@dataclass
class SpiderTarget:
    """Target configuration for spider operations"""
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    rate_limit: float = 1.0  # requests per second
    priority: int = 1  # 1=highest, 10=lowest
    retry_count: int = 3
    timeout: int = 30


@dataclass
class IntelligenceData:
    """Structured intelligence data from spider operations"""
    spider_id: str
    source_url: str
    data_type: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float
    timestamp: datetime
    relevance_tags: List[str] = field(default_factory=list)
    target_agents: List[str] = field(default_factory=list)
    target_advisors: List[str] = field(default_factory=list)


class BaseIntelligenceSpider(ABC):
    """
    Base class for all intelligence gathering spiders.

    Features:
    - Async operation for high performance
    - Rate limiting and request management
    - Data quality validation
    - Intelligent caching
    - Error handling and recovery
    - Performance monitoring
    - Real-time data distribution
    """

    def __init__(self,
                 spider_id: str,
                 targets: List[SpiderTarget],
                 subscribers: List[str] = None,
                 redis_config: Dict[str, Any] = None):
        """
        Initialize the base spider.

        Args:
            spider_id: Unique identifier for this spider
            targets: List of targets to monitor
            subscribers: List of agent/advisor IDs to feed data to
            redis_config: Redis configuration for data distribution
        """
        self.spider_id = spider_id
        self.targets = targets
        self.subscribers = subscribers or []
        self.metrics = SpiderMetrics(spider_id=spider_id)

        # Logger (initialize early so it's available for error messages)
        self.logger = logging.getLogger(f"spider.{spider_id}")

        # Redis connection for data distribution
        redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}
        try:
            # Filter out any extra parameters that Redis doesn't accept
            safe_config = {
                'host': redis_config.get('host', 'localhost'),
                'port': redis_config.get('port', 6379),
                'db': redis_config.get('db', 0)
            }
            self.redis_client = redis.Redis(**safe_config)
        except Exception as e:
            self.logger.warning(f"Failed to create Redis client: {e}")
            self.redis_client = None

        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_running = False
        self.start_time = datetime.now(timezone.utc)

        # Data cache
        self.data_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes

    async def start(self):
        """Start the spider operations"""
        try:
            self.is_running = True
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=100)
            )

            self.logger.info(f"Spider {self.spider_id} started with {len(self.targets)} targets")

            # Start monitoring tasks
            tasks = [
                asyncio.create_task(self._monitor_target(target)) for target in self.targets
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Spider {self.spider_id} failed to start: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop spider operations gracefully"""
        self.is_running = False
        if self.session:
            await self.session.close()
        self.logger.info(f"Spider {self.spider_id} stopped")

    async def _monitor_target(self, target: SpiderTarget):
        """Monitor a specific target continuously"""
        while self.is_running:
            try:
                # Rate limiting
                await asyncio.sleep(1.0 / target.rate_limit)

                # Fetch data
                start_time = time.time()
                data = await self._fetch_data(target)
                response_time = time.time() - start_time

                if data:
                    # Process and validate data
                    intelligence = await self.process_data(data, target)

                    if intelligence and intelligence.quality_score >= 0.5:
                        # Distribute to subscribers
                        await self._distribute_intelligence(intelligence)

                        # Update metrics
                        self.metrics.data_points_collected += 1
                        self.metrics.successful_requests += 1
                        self.metrics.avg_response_time = (
                            (self.metrics.avg_response_time * (self.metrics.successful_requests - 1) + response_time)
                            / self.metrics.successful_requests
                        )

                self.metrics.last_active = datetime.now(timezone.utc)

            except Exception as e:
                self.metrics.failed_requests += 1
                self.logger.error(f"Error monitoring target {target.url}: {e}")

                # Exponential backoff on errors
                await asyncio.sleep(min(60, 2 ** self.metrics.failed_requests))

    async def _fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch data from target URL"""
        try:
            # Check cache first
            cache_key = self._get_cache_key(target.url)
            cached_data = self.data_cache.get(cache_key)

            if cached_data and (datetime.now(timezone.utc) - cached_data['timestamp']).seconds < self.cache_ttl:
                return cached_data['data']

            # Fetch fresh data
            async with self.session.get(
                target.url,
                headers=target.headers,
                cookies=target.cookies,
                timeout=target.timeout
            ) as response:

                if response.status == 200:
                    content_type = response.headers.get('content-type', '')

                    if 'application/json' in content_type:
                        data = await response.json()
                    else:
                        text = await response.text()
                        data = {'content': text, 'content_type': content_type}

                    # Cache the data
                    self.data_cache[cache_key] = {
                        'data': data,
                        'timestamp': datetime.now(timezone.utc)
                    }

                    return data

                elif response.status == 429:  # Rate limited
                    self.metrics.rate_limit_hits += 1
                    await asyncio.sleep(60)  # Wait 1 minute

                return None

        except Exception as e:
            self.logger.error(f"Failed to fetch data from {target.url}: {e}")
            return None

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()

    @abstractmethod
    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """
        Process raw data into structured intelligence.

        Must be implemented by specific spider types.

        Args:
            raw_data: Raw data from the target
            target: Target configuration

        Returns:
            Structured intelligence data or None if invalid
        """
        pass

    async def _distribute_intelligence(self, intelligence: IntelligenceData):
        """Distribute intelligence to subscribers via Redis"""
        try:
            # Send to specific subscribers
            for subscriber in self.subscribers:
                channel = f"intelligence:{subscriber}"
                message = {
                    'spider_id': intelligence.spider_id,
                    'data_type': intelligence.data_type,
                    'content': intelligence.content,
                    'metadata': intelligence.metadata,
                    'quality_score': intelligence.quality_score,
                    'timestamp': intelligence.timestamp.isoformat(),
                    'source_url': intelligence.source_url,
                    'relevance_tags': intelligence.relevance_tags
                }

                await self._publish_async(channel, json.dumps(message))

            # Send to general intelligence feed
            general_channel = f"intelligence:general:{intelligence.data_type}"
            await self._publish_async(general_channel, json.dumps(message))

            self.logger.debug(f"Distributed intelligence to {len(self.subscribers)} subscribers")

        except Exception as e:
            self.logger.error(f"Failed to distribute intelligence: {e}")

    async def _publish_async(self, channel: str, message: str):
        """Async wrapper for Redis publish"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.redis_client.publish, channel, message)

    def calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0.0 - 1.0).

        Factors:
        - Completeness (are required fields present?)
        - Freshness (how recent is the data?)
        - Accuracy (does data pass validation?)
        - Relevance (does data match target criteria?)
        """
        try:
            score = 0.0

            # Completeness (40% of score)
            required_fields = self.get_required_fields()
            if required_fields:
                present_fields = sum(1 for field in required_fields if data.get(field))
                completeness = present_fields / len(required_fields)
                score += completeness * 0.4
            else:
                score += 0.4  # No required fields = full completeness score

            # Freshness (30% of score)
            timestamp_field = self.get_timestamp_field()
            if timestamp_field and data.get(timestamp_field):
                try:
                    data_time = datetime.fromisoformat(str(data[timestamp_field]).replace('Z', '+00:00'))
                    age_hours = (datetime.now(timezone.utc) - data_time).total_seconds() / 3600
                    freshness = max(0, 1 - (age_hours / 24))  # Decay over 24 hours
                    score += freshness * 0.3
                except:
                    score += 0.15  # Partial score if timestamp parsing fails
            else:
                score += 0.3  # No timestamp requirement = full freshness score

            # Accuracy (20% of score)
            if self.validate_data_accuracy(data):
                score += 0.2

            # Relevance (10% of score)
            relevance_keywords = self.get_relevance_keywords()
            if relevance_keywords:
                content_str = json.dumps(data).lower()
                keyword_matches = sum(1 for keyword in relevance_keywords if keyword.lower() in content_str)
                relevance = min(1.0, keyword_matches / len(relevance_keywords))
                score += relevance * 0.1
            else:
                score += 0.1  # No relevance keywords = full relevance score

            return min(1.0, score)

        except Exception as e:
            self.logger.error(f"Error calculating data quality: {e}")
            return 0.0

    def get_required_fields(self) -> List[str]:
        """Override in subclasses to specify required fields"""
        return []

    def get_timestamp_field(self) -> Optional[str]:
        """Override in subclasses to specify timestamp field"""
        return None

    def get_relevance_keywords(self) -> List[str]:
        """Override in subclasses to specify relevance keywords"""
        return []

    def validate_data_accuracy(self, data: Dict[str, Any]) -> bool:
        """Override in subclasses to implement data validation"""
        return True

    async def get_collected_data(self) -> List[Dict[str, Any]]:
        """
        Get all collected data from this spider.
        This is a simple implementation that returns cached data.
        Subclasses can override for more sophisticated data retrieval.
        """
        # For now, return mock data to demonstrate the flow
        # Real spiders would fetch actual data from their targets
        return []

    def get_metrics(self) -> SpiderMetrics:
        """Get current spider performance metrics"""
        # Update uptime percentage
        if self.start_time:
            total_time = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            if total_time > 0:
                downtime = self.metrics.failed_requests * 60  # Assume 1 minute downtime per failure
                self.metrics.uptime_percentage = max(0, 100 * (1 - downtime / total_time))

        return self.metrics

    def add_subscriber(self, subscriber_id: str):
        """Add a new subscriber to receive intelligence"""
        if subscriber_id not in self.subscribers:
            self.subscribers.append(subscriber_id)
            self.logger.info(f"Added subscriber: {subscriber_id}")

    def remove_subscriber(self, subscriber_id: str):
        """Remove a subscriber"""
        if subscriber_id in self.subscribers:
            self.subscribers.remove(subscriber_id)
            self.logger.info(f"Removed subscriber: {subscriber_id}")

    def update_targets(self, new_targets: List[SpiderTarget]):
        """Update spider targets dynamically"""
        self.targets = new_targets
        self.logger.info(f"Updated targets: {len(new_targets)} targets")


class AdaptiveSpider(BaseIntelligenceSpider):
    """
    Adaptive spider that learns and evolves its targeting based on
    subscriber feedback and data quality metrics.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.learning_rate = 0.1
        self.target_weights: Dict[str, float] = {}
        self.feedback_scores: Dict[str, List[float]] = {}

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Generic data processing with learning capabilities"""
        try:
            # Calculate quality score
            quality_score = self.calculate_data_quality(raw_data)

            # Create intelligence data
            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="adaptive",
                content=raw_data,
                metadata={
                    'target_priority': target.priority,
                    'processing_method': 'adaptive',
                    'spider_type': 'adaptive'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=self._extract_tags(raw_data),
                target_agents=self.subscribers,
                target_advisors=[]
            )

            # Update learning weights based on quality
            self._update_learning_weights(target.url, quality_score)

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing adaptive data: {e}")
            return None

    def _extract_tags(self, data: Dict[str, Any]) -> List[str]:
        """Extract relevance tags from data"""
        tags = []

        # Extract from keys
        for key in data.keys():
            if isinstance(key, str) and len(key) > 2:
                tags.append(key.lower())

        # Extract from string values
        for value in data.values():
            if isinstance(value, str) and 5 <= len(value) <= 50:
                tags.extend(value.lower().split()[:3])  # First 3 words

        return list(set(tags))[:10]  # Max 10 unique tags

    def _update_learning_weights(self, url: str, quality_score: float):
        """Update learning weights based on data quality feedback"""
        if url not in self.target_weights:
            self.target_weights[url] = 1.0

        # Simple learning: increase weight for high quality, decrease for low quality
        adjustment = (quality_score - 0.5) * self.learning_rate
        self.target_weights[url] = max(0.1, min(2.0, self.target_weights[url] + adjustment))

        # Store feedback for analysis
        if url not in self.feedback_scores:
            self.feedback_scores[url] = []
        self.feedback_scores[url].append(quality_score)

        # Keep only recent feedback (last 100 data points)
        if len(self.feedback_scores[url]) > 100:
            self.feedback_scores[url] = self.feedback_scores[url][-100:]