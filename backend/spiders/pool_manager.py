"""
Spider Pool Manager
Phase 4: Scale & Optimize - Manage 1,000+ Spiders

This module handles dynamic scaling, load balancing, and health monitoring
for a massive spider army capable of collecting intelligence at scale.
"""

import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import random
from collections import defaultdict
from django.core.cache import cache
import json

logger = logging.getLogger(__name__)


class SpiderState(Enum):
    """Spider lifecycle states"""
    IDLE = "idle"
    ACTIVE = "active"
    HIBERNATING = "hibernating"
    FAILED = "failed"
    THROTTLED = "throttled"
    MAINTENANCE = "maintenance"


class SpiderType(Enum):
    """Types of spiders in the pool"""
    JOB = "job_spider"
    FINANCIAL = "financial_spider"
    NEWS = "news_spider"
    SOCIAL = "social_spider"
    REAL_ESTATE = "real_estate_spider"
    FREELANCE = "freelance_spider"
    BUSINESS = "business_spider"
    CRYPTO = "crypto_spider"
    ECOMMERCE = "ecommerce_spider"
    RESEARCH = "research_spider"


@dataclass
class SpiderInstance:
    """Individual spider instance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: SpiderType = SpiderType.JOB
    state: SpiderState = SpiderState.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    tasks_completed: int = 0
    errors_count: int = 0
    data_collected: int = 0
    performance_score: float = 1.0
    assigned_source: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class SpiderPoolManager:
    """
    Manages a pool of 1,000+ spider instances with dynamic scaling,
    load balancing, and health monitoring.
    """

    def __init__(self, initial_size: int = 100):
        self.pool: Dict[str, SpiderInstance] = {}
        self.active_spiders: Set[str] = set()
        self.hibernating_spiders: Set[str] = set()
        self.failed_spiders: Set[str] = set()

        # Configuration
        self.max_pool_size = 2000
        self.min_pool_size = 50
        self.scale_threshold_high = 0.8  # Scale up when 80% busy
        self.scale_threshold_low = 0.2   # Scale down when 20% busy
        self.health_check_interval = 30  # seconds

        # Metrics
        self.metrics = {
            'total_spawned': 0,
            'total_hibernated': 0,
            'total_failed': 0,
            'total_data_collected': 0,
            'avg_performance_score': 1.0,
            'last_scale_action': None,
            'current_load': 0.0
        }

        # Load balancing
        self.source_assignments = defaultdict(set)  # source -> spider_ids
        self.spider_load = defaultdict(int)  # spider_id -> current_tasks

        # Initialize pool
        self._initialize_pool(initial_size)

    def _initialize_pool(self, size: int):
        """Initialize the spider pool with specified size"""
        logger.info(f"🕷️ Initializing spider pool with {size} spiders")

        # Create diverse spider types
        spider_distribution = {
            SpiderType.JOB: 0.25,
            SpiderType.FINANCIAL: 0.15,
            SpiderType.NEWS: 0.15,
            SpiderType.SOCIAL: 0.10,
            SpiderType.FREELANCE: 0.10,
            SpiderType.BUSINESS: 0.10,
            SpiderType.CRYPTO: 0.05,
            SpiderType.ECOMMERCE: 0.05,
            SpiderType.REAL_ESTATE: 0.03,
            SpiderType.RESEARCH: 0.02
        }

        for spider_type, percentage in spider_distribution.items():
            count = int(size * percentage)
            for _ in range(count):
                spider = self._spawn_spider(spider_type)
                self.pool[spider.id] = spider

        logger.info(f"✅ Spider pool initialized: {len(self.pool)} spiders ready")

    def _spawn_spider(self, spider_type: SpiderType) -> SpiderInstance:
        """Spawn a new spider instance"""
        spider = SpiderInstance(
            type=spider_type,
            state=SpiderState.IDLE,
            metadata={
                'spawn_generation': self.metrics['total_spawned'] // 100,
                'capabilities': self._get_spider_capabilities(spider_type)
            }
        )

        self.metrics['total_spawned'] += 1
        logger.debug(f"🐣 Spawned new {spider_type.value} spider: {spider.id}")

        return spider

    def _get_spider_capabilities(self, spider_type: SpiderType) -> List[str]:
        """Get capabilities based on spider type"""
        capabilities_map = {
            SpiderType.JOB: ['remote_ok', 'indeed', 'linkedin', 'glassdoor'],
            SpiderType.FINANCIAL: ['yahoo_finance', 'coingecko', 'alpha_vantage', 'finnhub'],
            SpiderType.NEWS: ['newsapi', 'reddit', 'hackernews', 'reuters'],
            SpiderType.SOCIAL: ['bluesky', 'mastodon', 'reddit', 'discord'],
            SpiderType.FREELANCE: ['upwork', 'fiverr', 'toptal', 'freelancer'],
            SpiderType.BUSINESS: ['crunchbase', 'angellist', 'producthunt'],
            SpiderType.CRYPTO: ['coingecko', 'coinmarketcap', 'messari', 'glassnode'],
            SpiderType.ECOMMERCE: ['amazon', 'shopify', 'etsy', 'alibaba'],
            SpiderType.REAL_ESTATE: ['zillow', 'realtor', 'redfin', 'trulia'],
            SpiderType.RESEARCH: ['arxiv', 'pubmed', 'google_scholar', 'semantic_scholar']
        }

        return capabilities_map.get(spider_type, ['generic'])

    async def auto_scale(self):
        """Automatically scale the spider pool based on load"""
        current_load = self.calculate_load()
        self.metrics['current_load'] = current_load

        logger.info(f"📊 Current load: {current_load:.2%} ({len(self.active_spiders)}/{len(self.pool)} active)")

        # Scale up if load is too high
        if current_load > self.scale_threshold_high and len(self.pool) < self.max_pool_size:
            await self.scale_up(100)

        # Scale down if load is too low
        elif current_load < self.scale_threshold_low and len(self.pool) > self.min_pool_size:
            await self.scale_down(50)

        # Reactivate hibernating spiders if needed
        elif current_load > 0.6 and self.hibernating_spiders:
            await self.wake_hibernating_spiders(20)

    async def scale_up(self, count: int):
        """Scale up by spawning more spiders"""
        actual_count = min(count, self.max_pool_size - len(self.pool))

        if actual_count <= 0:
            logger.warning("⚠️ Cannot scale up: max pool size reached")
            return

        logger.info(f"⬆️ Scaling up: spawning {actual_count} new spiders")

        # Spawn new spiders based on current demand
        for _ in range(actual_count):
            # Choose type based on current workload
            spider_type = self._choose_spider_type_for_scaling()
            spider = self._spawn_spider(spider_type)
            self.pool[spider.id] = spider

        self.metrics['last_scale_action'] = {
            'type': 'scale_up',
            'count': actual_count,
            'timestamp': datetime.now().isoformat()
        }

        # Cache the updated pool info
        self._cache_pool_state()

    async def scale_down(self, count: int):
        """Scale down by hibernating idle spiders"""
        idle_spiders = [
            spider_id for spider_id, spider in self.pool.items()
            if spider.state == SpiderState.IDLE and spider_id not in self.hibernating_spiders
        ]

        to_hibernate = idle_spiders[:min(count, len(idle_spiders))]

        logger.info(f"⬇️ Scaling down: hibernating {len(to_hibernate)} spiders")

        for spider_id in to_hibernate:
            await self.hibernate_spider(spider_id)

        self.metrics['last_scale_action'] = {
            'type': 'scale_down',
            'count': len(to_hibernate),
            'timestamp': datetime.now().isoformat()
        }

    async def hibernate_spider(self, spider_id: str):
        """Put a spider into hibernation"""
        if spider_id not in self.pool:
            return

        spider = self.pool[spider_id]
        spider.state = SpiderState.HIBERNATING

        self.active_spiders.discard(spider_id)
        self.hibernating_spiders.add(spider_id)
        self.metrics['total_hibernated'] += 1

        logger.debug(f"💤 Spider {spider_id} hibernated")

    async def wake_hibernating_spiders(self, count: int):
        """Wake up hibernating spiders"""
        to_wake = list(self.hibernating_spiders)[:min(count, len(self.hibernating_spiders))]

        for spider_id in to_wake:
            spider = self.pool[spider_id]
            spider.state = SpiderState.IDLE
            self.hibernating_spiders.discard(spider_id)

        logger.info(f"☀️ Woke up {len(to_wake)} hibernating spiders")

    def _choose_spider_type_for_scaling(self) -> SpiderType:
        """Choose spider type based on current demand"""
        # Analyze current workload distribution
        type_counts = defaultdict(int)
        for spider in self.pool.values():
            if spider.state == SpiderState.ACTIVE:
                type_counts[spider.type] += 1

        # Find the most busy type
        if type_counts:
            most_busy = max(type_counts, key=type_counts.get)
            return most_busy

        # Default to job spiders
        return SpiderType.JOB

    def calculate_load(self) -> float:
        """Calculate current pool load (0.0 to 1.0)"""
        if not self.pool:
            return 0.0

        active_count = len(self.active_spiders)
        available_count = len(self.pool) - len(self.hibernating_spiders) - len(self.failed_spiders)

        if available_count == 0:
            return 1.0

        return active_count / available_count

    async def assign_task(self, task: Dict) -> Optional[str]:
        """
        Assign a task to an available spider

        Args:
            task: Task details including type and source

        Returns:
            Spider ID if assigned, None otherwise
        """
        task_type = task.get('type', 'general')
        source = task.get('source', 'unknown')

        # Find suitable idle spider
        suitable_spider = await self._find_suitable_spider(task_type)

        if not suitable_spider:
            logger.warning(f"⚠️ No suitable spider for task type: {task_type}")
            return None

        # Assign the task
        suitable_spider.state = SpiderState.ACTIVE
        suitable_spider.last_active = datetime.now()
        suitable_spider.assigned_source = source

        self.active_spiders.add(suitable_spider.id)
        self.source_assignments[source].add(suitable_spider.id)
        self.spider_load[suitable_spider.id] += 1

        logger.debug(f"✅ Assigned task to spider {suitable_spider.id}")

        return suitable_spider.id

    async def _find_suitable_spider(self, task_type: str) -> Optional[SpiderInstance]:
        """Find the most suitable spider for a task"""
        # Map task types to spider types
        task_spider_map = {
            'job': SpiderType.JOB,
            'finance': SpiderType.FINANCIAL,
            'news': SpiderType.NEWS,
            'social': SpiderType.SOCIAL,
            'freelance': SpiderType.FREELANCE,
            'business': SpiderType.BUSINESS,
            'crypto': SpiderType.CRYPTO,
            'ecommerce': SpiderType.ECOMMERCE,
            'real_estate': SpiderType.REAL_ESTATE,
            'research': SpiderType.RESEARCH
        }

        preferred_type = task_spider_map.get(task_type)

        # First, try to find idle spider of preferred type
        for spider in self.pool.values():
            if (spider.state == SpiderState.IDLE and
                (preferred_type is None or spider.type == preferred_type)):
                return spider

        # If no preferred type available, find any idle spider
        for spider in self.pool.values():
            if spider.state == SpiderState.IDLE:
                return spider

        return None

    async def complete_task(self, spider_id: str, results: Dict):
        """
        Mark a task as completed by a spider

        Args:
            spider_id: ID of the spider
            results: Task results including data collected
        """
        if spider_id not in self.pool:
            return

        spider = self.pool[spider_id]

        # Update spider stats
        spider.tasks_completed += 1
        spider.data_collected += results.get('data_count', 0)
        spider.state = SpiderState.IDLE
        spider.last_active = datetime.now()

        # Update performance score
        if results.get('success', True):
            spider.performance_score = min(1.0, spider.performance_score * 1.02)
        else:
            spider.errors_count += 1
            spider.performance_score = max(0.1, spider.performance_score * 0.95)

        # Update pool metrics
        self.metrics['total_data_collected'] += results.get('data_count', 0)

        # Remove from active set
        self.active_spiders.discard(spider_id)
        self.spider_load[spider_id] = max(0, self.spider_load[spider_id] - 1)

        # Clear source assignment if no more tasks
        if spider.assigned_source and self.spider_load[spider_id] == 0:
            self.source_assignments[spider.assigned_source].discard(spider_id)
            spider.assigned_source = None

        logger.debug(f"✅ Spider {spider_id} completed task")

    async def health_check(self):
        """Perform health check on all spiders"""
        logger.info("🏥 Running spider health check...")

        now = datetime.now()
        unhealthy_count = 0

        for spider in self.pool.values():
            # Check for stuck spiders (active for too long)
            if spider.state == SpiderState.ACTIVE:
                time_active = (now - spider.last_active).total_seconds()
                if time_active > 300:  # 5 minutes
                    logger.warning(f"⚠️ Spider {spider.id} stuck for {time_active}s")
                    spider.state = SpiderState.FAILED
                    spider.errors_count += 1
                    self.active_spiders.discard(spider.id)
                    self.failed_spiders.add(spider.id)
                    unhealthy_count += 1

            # Check for failed spiders
            if spider.errors_count > 5:
                spider.state = SpiderState.FAILED
                self.failed_spiders.add(spider.id)
                unhealthy_count += 1

            # Check performance degradation
            if spider.performance_score < 0.3:
                spider.state = SpiderState.MAINTENANCE
                unhealthy_count += 1

        # Calculate average performance
        if self.pool:
            avg_performance = sum(s.performance_score for s in self.pool.values()) / len(self.pool)
            self.metrics['avg_performance_score'] = avg_performance

        logger.info(f"🏥 Health check complete: {unhealthy_count} unhealthy spiders")

        # Replace failed spiders if needed
        if unhealthy_count > 10:
            await self.replace_failed_spiders()

    async def replace_failed_spiders(self):
        """Replace failed spiders with new ones"""
        to_remove = list(self.failed_spiders)[:20]  # Replace up to 20 at a time

        logger.info(f"🔄 Replacing {len(to_remove)} failed spiders")

        for spider_id in to_remove:
            # Remove failed spider
            if spider_id in self.pool:
                failed_spider = self.pool[spider_id]
                del self.pool[spider_id]

                # Spawn replacement
                new_spider = self._spawn_spider(failed_spider.type)
                self.pool[new_spider.id] = new_spider

            self.failed_spiders.discard(spider_id)
            self.active_spiders.discard(spider_id)

        self.metrics['total_failed'] += len(to_remove)

    def get_pool_stats(self) -> Dict:
        """Get current pool statistics"""
        type_distribution = defaultdict(int)
        state_distribution = defaultdict(int)

        for spider in self.pool.values():
            type_distribution[spider.type.value] += 1
            state_distribution[spider.state.value] += 1

        return {
            'total_spiders': len(self.pool),
            'active': len(self.active_spiders),
            'idle': state_distribution[SpiderState.IDLE.value],
            'hibernating': len(self.hibernating_spiders),
            'failed': len(self.failed_spiders),
            'load_percentage': self.calculate_load() * 100,
            'type_distribution': dict(type_distribution),
            'state_distribution': dict(state_distribution),
            'metrics': self.metrics,
            'top_performers': self._get_top_performers()
        }

    def _get_top_performers(self, limit: int = 10) -> List[Dict]:
        """Get top performing spiders"""
        sorted_spiders = sorted(
            self.pool.values(),
            key=lambda s: (s.performance_score, s.data_collected),
            reverse=True
        )

        return [
            {
                'id': spider.id,
                'type': spider.type.value,
                'tasks_completed': spider.tasks_completed,
                'data_collected': spider.data_collected,
                'performance_score': spider.performance_score
            }
            for spider in sorted_spiders[:limit]
        ]

    def _cache_pool_state(self):
        """Cache the current pool state"""
        cache.set('spider_pool_stats', self.get_pool_stats(), 60)
        cache.set('spider_pool_size', len(self.pool), 60)

    async def optimize_distribution(self):
        """Optimize spider distribution across sources"""
        logger.info("🎯 Optimizing spider distribution...")

        # Analyze source workloads
        source_loads = {}
        for source, spider_ids in self.source_assignments.items():
            active_count = len([sid for sid in spider_ids if sid in self.active_spiders])
            source_loads[source] = active_count

        # Rebalance if needed
        if source_loads:
            avg_load = sum(source_loads.values()) / len(source_loads)

            for source, load in source_loads.items():
                if load > avg_load * 1.5:
                    # This source is overloaded
                    logger.info(f"⚠️ Source {source} overloaded ({load} spiders)")
                    # Could trigger scaling or redistribution here

        return source_loads


# Singleton instance
spider_pool = SpiderPoolManager(initial_size=100)


async def get_spider_for_task(task: Dict) -> Optional[str]:
    """
    Public API to get a spider for a task

    Args:
        task: Task details

    Returns:
        Spider ID if available
    """
    # Auto-scale if needed
    await spider_pool.auto_scale()

    # Assign task
    return await spider_pool.assign_task(task)


async def release_spider(spider_id: str, results: Dict):
    """
    Release a spider after task completion

    Args:
        spider_id: ID of the spider
        results: Task results
    """
    await spider_pool.complete_task(spider_id, results)


def get_pool_statistics() -> Dict:
    """Get current pool statistics"""
    return spider_pool.get_pool_stats()


async def scale_pool(target_size: int):
    """
    Scale the pool to target size

    Args:
        target_size: Desired pool size
    """
    current_size = len(spider_pool.pool)

    if target_size > current_size:
        await spider_pool.scale_up(target_size - current_size)
    elif target_size < current_size:
        await spider_pool.scale_down(current_size - target_size)