"""
Phase 4 Spider Orchestrator - Command & Control for 1,000+ Spiders
Phase 4: Scale & Optimize - Massive Spider Army Management

This module orchestrates the entire spider ecosystem, coordinating
pool management, caching, routing, and performance optimization.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import json
import random
from django.core.cache import cache

# Import all Phase 4 components
from .pool_manager import spider_pool, get_spider_for_task, release_spider, scale_pool
from .cache_layer import smart_cache, cache_get, cache_set, optimize_cache
from .metrics import (
    metrics_tracker,
    record_spider_request,
    record_data_collection,
    record_api_call,
    get_performance_metrics
)

# Import Phase 3 components for integration
from .agent_router import router, route_spider_data
from .advisor_feed import advisor_feed, feed_advisors
from .realtime_publisher import publisher, broadcast_spider_discovery

logger = logging.getLogger(__name__)


class Phase4SpiderOrchestrator:
    """
    Master orchestrator for managing 1,000+ spiders at scale.
    Coordinates all aspects of spider operations including:
    - Task distribution
    - Load balancing
    - Performance optimization
    - Cache management
    - Data routing
    - Real-time monitoring
    """

    def __init__(self, target_spider_count: int = 1000):
        self.target_spider_count = target_spider_count
        self.active_tasks = {}
        self.task_queue = asyncio.Queue(maxsize=10000)
        self.priority_queue = asyncio.PriorityQueue(maxsize=1000)

        # Orchestration state
        self.orchestration_mode = 'balanced'  # 'aggressive', 'conservative', 'balanced'
        self.is_running = False
        self.workers = []

        # Performance tracking
        self.orchestration_stats = {
            'total_tasks_processed': 0,
            'total_data_collected': 0,
            'total_opportunities_found': 0,
            'total_revenue_potential': 0,
            'orchestration_start_time': None,
            'current_efficiency': 0.0
        }

        # Task distribution strategy
        self.distribution_weights = {
            'job': 0.25,
            'financial': 0.20,
            'news': 0.15,
            'freelance': 0.15,
            'business': 0.10,
            'social': 0.05,
            'crypto': 0.05,
            'real_estate': 0.03,
            'research': 0.02
        }

        logger.info(f"🎯 Phase 4 Spider Orchestrator initialized for {target_spider_count} spiders")

    async def initialize(self):
        """Initialize the orchestrator and all subsystems"""
        logger.info("🚀 Initializing Phase 4 Spider Orchestrator...")

        # Scale spider pool to target size
        await scale_pool(self.target_spider_count)

        # Warm up cache
        await smart_cache.optimize()

        # Reset metrics for fresh start
        metrics_tracker.reset_api_quotas()

        # Start background workers
        self.is_running = True
        self.orchestration_stats['orchestration_start_time'] = datetime.now()

        # Start worker tasks
        for i in range(10):  # 10 concurrent workers
            worker = asyncio.create_task(self._task_worker(i))
            self.workers.append(worker)

        # Start monitoring tasks
        asyncio.create_task(self._monitor_performance())
        asyncio.create_task(self._auto_optimize())
        asyncio.create_task(self._process_priority_tasks())

        logger.info("✅ Phase 4 Spider Orchestrator initialized and running")

    async def orchestrate_collection(self, duration_minutes: int = 60):
        """
        Orchestrate mass data collection for specified duration

        Args:
            duration_minutes: How long to run collection

        Returns:
            Collection results summary
        """
        logger.info(f"🎪 Starting orchestrated collection for {duration_minutes} minutes")

        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        # Generate collection tasks based on distribution
        total_tasks = 0
        while datetime.now() < end_time:
            # Generate batch of tasks
            batch_size = min(100, self.target_spider_count // 10)

            for _ in range(batch_size):
                task_type = self._select_task_type()
                task = self._generate_task(task_type)

                # Add to appropriate queue
                if task.get('priority', 5) >= 8:
                    await self.priority_queue.put((10 - task['priority'], task))
                else:
                    await self.task_queue.put(task)

                total_tasks += 1

            # Pace task generation
            await asyncio.sleep(1)

            # Check if we should adjust strategy
            if total_tasks % 1000 == 0:
                await self._adjust_strategy()

        # Wait for all tasks to complete
        await self.task_queue.join()
        await self.priority_queue.join()

        # Generate summary
        duration = (datetime.now() - start_time).total_seconds() / 60
        return {
            'duration_minutes': duration,
            'total_tasks': total_tasks,
            'total_data_collected': self.orchestration_stats['total_data_collected'],
            'opportunities_found': self.orchestration_stats['total_opportunities_found'],
            'revenue_potential': self.orchestration_stats['total_revenue_potential'],
            'efficiency': self.orchestration_stats['current_efficiency']
        }

    def _select_task_type(self) -> str:
        """Select task type based on distribution weights"""
        choices = list(self.distribution_weights.keys())
        weights = list(self.distribution_weights.values())
        return random.choices(choices, weights=weights)[0]

    def _generate_task(self, task_type: str) -> Dict:
        """Generate a collection task"""
        task = {
            'id': f"task_{datetime.now().timestamp()}_{random.randint(1000, 9999)}",
            'type': task_type,
            'created_at': datetime.now().isoformat(),
            'priority': self._calculate_priority(task_type),
            'parameters': self._get_task_parameters(task_type),
            'retry_count': 0,
            'max_retries': 3
        }

        return task

    def _calculate_priority(self, task_type: str) -> int:
        """Calculate task priority (1-10, 10 being highest)"""
        # High-value task types get higher priority
        priority_map = {
            'job': 7,
            'freelance': 7,
            'financial': 8,
            'business': 6,
            'crypto': 8,
            'news': 5,
            'social': 4,
            'real_estate': 6,
            'research': 3
        }

        base_priority = priority_map.get(task_type, 5)

        # Adjust based on current mode
        if self.orchestration_mode == 'aggressive':
            base_priority = min(10, base_priority + 2)
        elif self.orchestration_mode == 'conservative':
            base_priority = max(1, base_priority - 1)

        return base_priority

    def _get_task_parameters(self, task_type: str) -> Dict:
        """Get parameters for task type"""
        params = {
            'job': {
                'keywords': ['remote', 'developer', 'engineer', 'data', 'AI'],
                'sources': ['remoteok', 'weworkremotely', 'github'],
                'limit': 50
            },
            'financial': {
                'symbols': ['BTC', 'ETH', 'AAPL', 'GOOGL', 'MSFT'],
                'metrics': ['price', 'volume', 'market_cap'],
                'interval': '1h'
            },
            'news': {
                'categories': ['technology', 'business', 'finance'],
                'sources': ['newsapi', 'hackernews', 'reddit'],
                'limit': 30
            },
            'freelance': {
                'categories': ['programming', 'design', 'writing'],
                'min_budget': 500,
                'limit': 40
            },
            'business': {
                'industries': ['tech', 'saas', 'ai', 'fintech'],
                'data_points': ['funding', 'revenue', 'growth'],
                'limit': 25
            },
            'social': {
                'platforms': ['bluesky', 'mastodon', 'reddit'],
                'topics': ['tech', 'startup', 'ai'],
                'limit': 100
            },
            'crypto': {
                'coins': ['bitcoin', 'ethereum', 'solana', 'cardano'],
                'metrics': ['price', 'volume', 'sentiment'],
                'limit': 20
            },
            'real_estate': {
                'locations': ['San Francisco', 'Austin', 'Miami'],
                'property_types': ['residential', 'commercial'],
                'limit': 20
            },
            'research': {
                'topics': ['artificial intelligence', 'machine learning', 'blockchain'],
                'sources': ['arxiv', 'papers', 'patents'],
                'limit': 15
            }
        }

        return params.get(task_type, {})

    async def _task_worker(self, worker_id: int):
        """Worker coroutine for processing tasks"""
        logger.info(f"🔧 Worker {worker_id} started")

        while self.is_running:
            try:
                # Get task from queue with longer timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=5.0)

                # Process task
                await self._process_task(task, worker_id)

                # Mark task as done
                self.task_queue.task_done()

            except asyncio.TimeoutError:
                # No tasks available, continue
                await asyncio.sleep(0.1)
                continue
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                # Try to mark task as done even if processing failed
                try:
                    self.task_queue.task_done()
                except:
                    pass
                await asyncio.sleep(1)

    async def _process_priority_tasks(self):
        """Process high-priority tasks"""
        while self.is_running:
            try:
                # Get priority task
                priority, task = await asyncio.wait_for(
                    self.priority_queue.get(),
                    timeout=1.0
                )

                # Process immediately
                await self._process_task(task, worker_id=999)  # Special worker ID

                self.priority_queue.task_done()

            except asyncio.TimeoutError:
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"❌ Priority processor error: {e}")

    async def _process_task(self, task: Dict, worker_id: int):
        """Process a single task"""
        start_time = datetime.now()
        spider_id = None

        try:
            # Check cache first
            cache_key = f"task_result_{task['type']}_{json.dumps(task['parameters'], sort_keys=True)}"
            cached_result = await cache_get(cache_key)

            if cached_result:
                logger.debug(f"📦 Cache hit for task {task['id']}")
                await self._handle_task_result(task, cached_result, from_cache=True)
                return

            # Get spider for task
            spider_id = await get_spider_for_task(task)

            if not spider_id:
                logger.warning(f"⚠️ No spider available for task {task['id']}")
                # Requeue task
                if task['retry_count'] < task['max_retries']:
                    task['retry_count'] += 1
                    await self.task_queue.put(task)
                return

            # Execute task (simulated - in reality would call actual spider)
            result = await self._execute_spider_task(spider_id, task)

            # Cache result
            await cache_set(cache_key, result, ttl=3600)

            # Handle result
            await self._handle_task_result(task, result)

            # Record metrics
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            record_spider_request(
                spider_id,
                success=True,
                response_time_ms=response_time,
                data_collected=len(result.get('data', []))
            )

            # Release spider
            await release_spider(spider_id, result)

        except Exception as e:
            logger.error(f"❌ Task {task['id']} failed: {e}")

            if spider_id:
                record_spider_request(spider_id, success=False, response_time_ms=0)
                await release_spider(spider_id, {'success': False})

            # Retry if possible
            if task['retry_count'] < task['max_retries']:
                task['retry_count'] += 1
                await self.task_queue.put(task)

    async def _execute_spider_task(self, spider_id: str, task: Dict) -> Dict:
        """Execute spider task (simulated)"""
        # In reality, this would call the actual spider
        # For now, simulate data collection

        task_type = task.get('type')
        parameters = task.get('parameters', {})

        # Simulate different data based on task type
        if task_type == 'job':
            data = [
                {
                    'id': f"job_{i}",
                    'title': f"Remote {random.choice(['Developer', 'Engineer', 'Analyst'])}",
                    'company': f"Company {i}",
                    'salary': random.randint(80000, 200000),
                    'url': f"https://example.com/job/{i}"
                }
                for i in range(parameters.get('limit', 10))
            ]
        elif task_type == 'financial':
            data = [
                {
                    'symbol': symbol,
                    'price': random.uniform(100, 50000),
                    'volume': random.randint(1000000, 100000000),
                    'change_24h': random.uniform(-10, 10)
                }
                for symbol in parameters.get('symbols', ['BTC'])
            ]
        else:
            # Generic data
            data = [
                {'id': f"{task_type}_{i}", 'value': random.random()}
                for i in range(parameters.get('limit', 10))
            ]

        return {
            'success': True,
            'spider_id': spider_id,
            'task_id': task['id'],
            'data': data,
            'data_count': len(data),
            'timestamp': datetime.now().isoformat()
        }

    async def _handle_task_result(self, task: Dict, result: Dict, from_cache: bool = False):
        """Handle task result"""
        try:
            # Update statistics
            self.orchestration_stats['total_tasks_processed'] += 1
            self.orchestration_stats['total_data_collected'] += len(result.get('data', []))

            # Analyze for opportunities
            opportunities = self._identify_opportunities(task['type'], result.get('data', []))
            self.orchestration_stats['total_opportunities_found'] += len(opportunities)

            # Calculate revenue potential
            revenue_potential = self._calculate_revenue_potential(opportunities)
            self.orchestration_stats['total_revenue_potential'] += revenue_potential

            if not from_cache and result.get('data'):
                try:
                    # Route to agents (Phase 3 integration)
                    await route_spider_data(task['type'], result)
                except Exception as e:
                    logger.warning(f"⚠️ Agent routing failed: {e}")

                try:
                    # Feed to advisors (Phase 3 integration)
                    await feed_advisors(result)
                except Exception as e:
                    logger.warning(f"⚠️ Advisor feeding failed: {e}")

                try:
                    # Broadcast discovery (Phase 3 integration)
                    await broadcast_spider_discovery(task['type'], result)
                except Exception as e:
                    logger.warning(f"⚠️ WebSocket broadcasting failed: {e}")

                try:
                    # Record data collection
                    record_data_collection(
                        result.get('spider_id', 'unknown'),
                        task['type'],
                        len(result.get('data', [])),
                        unique_items=[str(d.get('id')) for d in result.get('data', []) if 'id' in d]
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Data collection recording failed: {e}")

        except Exception as e:
            logger.error(f"❌ Error handling task result: {e}")

    def _identify_opportunities(self, task_type: str, data: List[Dict]) -> List[Dict]:
        """Identify opportunities in collected data"""
        opportunities = []

        if task_type == 'job':
            # High-paying remote jobs
            for item in data:
                if item.get('salary', 0) > 150000:
                    opportunities.append({
                        'type': 'high_paying_job',
                        'value': item['salary'],
                        'details': item
                    })

        elif task_type == 'financial':
            # Large price movements
            for item in data:
                if abs(item.get('change_24h', 0)) > 5:
                    opportunities.append({
                        'type': 'price_movement',
                        'value': item.get('price', 0) * abs(item['change_24h']) / 100,
                        'details': item
                    })

        elif task_type == 'freelance':
            # High-budget projects
            for item in data:
                if item.get('budget', 0) > 5000:
                    opportunities.append({
                        'type': 'high_budget_project',
                        'value': item['budget'],
                        'details': item
                    })

        return opportunities

    def _calculate_revenue_potential(self, opportunities: List[Dict]) -> float:
        """Calculate total revenue potential from opportunities"""
        return sum(opp.get('value', 0) for opp in opportunities)

    async def _monitor_performance(self):
        """Monitor and report performance periodically"""
        while self.is_running:
            try:
                # Get current metrics
                metrics = get_performance_metrics()
                pool_stats = spider_pool.get_pool_stats()
                cache_stats = smart_cache.get_statistics()

                # Calculate efficiency
                if self.orchestration_stats['total_tasks_processed'] > 0:
                    self.orchestration_stats['current_efficiency'] = \
                        self.orchestration_stats['total_opportunities_found'] / \
                        self.orchestration_stats['total_tasks_processed']

                # Log status
                logger.info(f"""
                📊 Orchestration Status:
                - Tasks: {self.orchestration_stats['total_tasks_processed']}
                - Data: {self.orchestration_stats['total_data_collected']}
                - Opportunities: {self.orchestration_stats['total_opportunities_found']}
                - Revenue Potential: ${self.orchestration_stats['total_revenue_potential']:,.2f}
                - Efficiency: {self.orchestration_stats['current_efficiency']:.2%}
                - Active Spiders: {pool_stats['active']}/{pool_stats['total_spiders']}
                - Cache Hit Rate: {cache_stats['hit_rate']:.1f}%
                - RPS: {metrics['requests_per_second']:.2f}
                """)

                # Cache status for dashboard
                cache.set('orchestration_status', {
                    'stats': self.orchestration_stats,
                    'metrics': metrics,
                    'pool': pool_stats,
                    'cache': cache_stats
                }, 60)

                await asyncio.sleep(30)  # Report every 30 seconds

            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)

    async def _auto_optimize(self):
        """Automatically optimize based on performance"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Optimize every 5 minutes

                # Get current metrics
                metrics = get_performance_metrics()

                # Adjust orchestration mode based on performance
                if metrics['error_rate_percent'] > 10:
                    self.orchestration_mode = 'conservative'
                    logger.info("📉 Switched to conservative mode due to high errors")
                elif metrics['requests_per_second'] < 10:
                    self.orchestration_mode = 'aggressive'
                    logger.info("📈 Switched to aggressive mode to increase throughput")
                else:
                    self.orchestration_mode = 'balanced'

                # Auto-scale pool if needed
                await spider_pool.auto_scale()

                # Optimize cache
                await smart_cache.optimize()

                # Adjust task distribution based on success rates
                await self._adjust_distribution()

            except Exception as e:
                logger.error(f"❌ Auto-optimize error: {e}")

    async def _adjust_distribution(self):
        """Adjust task distribution based on performance"""
        # Get performance by task type
        # In a real implementation, would analyze success rates per type
        # For now, slight random adjustments
        for task_type in self.distribution_weights:
            current = self.distribution_weights[task_type]
            adjustment = random.uniform(-0.02, 0.02)
            self.distribution_weights[task_type] = max(0.01, min(0.5, current + adjustment))

        # Normalize weights
        total = sum(self.distribution_weights.values())
        for task_type in self.distribution_weights:
            self.distribution_weights[task_type] /= total

    async def _adjust_strategy(self):
        """Adjust collection strategy based on results"""
        efficiency = self.orchestration_stats['current_efficiency']

        if efficiency < 0.1:
            # Poor efficiency, focus on high-value tasks
            self.distribution_weights['job'] = 0.35
            self.distribution_weights['freelance'] = 0.25
            self.distribution_weights['financial'] = 0.20
            logger.info("🎯 Adjusted strategy: Focus on high-value tasks")

        elif efficiency > 0.3:
            # Good efficiency, diversify more
            for task_type in self.distribution_weights:
                self.distribution_weights[task_type] = 1.0 / len(self.distribution_weights)
            logger.info("🎯 Adjusted strategy: Diversifying collection")

    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        logger.info("🛑 Shutting down Phase 4 Spider Orchestrator...")

        self.is_running = False

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)

        # Final statistics
        duration = (datetime.now() - self.orchestration_stats['orchestration_start_time']).total_seconds() / 3600
        logger.info(f"""
        📊 Final Orchestration Statistics:
        - Duration: {duration:.2f} hours
        - Total Tasks: {self.orchestration_stats['total_tasks_processed']}
        - Total Data: {self.orchestration_stats['total_data_collected']}
        - Opportunities: {self.orchestration_stats['total_opportunities_found']}
        - Revenue Potential: ${self.orchestration_stats['total_revenue_potential']:,.2f}
        - Final Efficiency: {self.orchestration_stats['current_efficiency']:.2%}
        """)

        logger.info("✅ Phase 4 Spider Orchestrator shutdown complete")


# Singleton instance
phase4_orchestrator = Phase4SpiderOrchestrator(target_spider_count=1000)


# Public API functions
async def start_phase4_orchestration(duration_minutes: int = 60) -> Dict:
    """Start Phase 4 orchestrated collection"""
    await phase4_orchestrator.initialize()
    return await phase4_orchestrator.orchestrate_collection(duration_minutes)


async def get_phase4_status() -> Dict:
    """Get current Phase 4 orchestration status"""
    return {
        'is_running': phase4_orchestrator.is_running,
        'mode': phase4_orchestrator.orchestration_mode,
        'stats': phase4_orchestrator.orchestration_stats,
        'distribution': phase4_orchestrator.distribution_weights
    }


async def stop_phase4_orchestration():
    """Stop Phase 4 orchestration"""
    await phase4_orchestrator.shutdown()