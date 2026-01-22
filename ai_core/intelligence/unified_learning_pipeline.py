"""
Unified Learning Pipeline - Complete Spider-to-Agent Learning System
===================================================================

This module orchestrates the complete pipeline from spider data collection
to agent learning and improvement. It connects all components:

1. SpiderLearningOrchestrator - Collects data from 1,770+ spiders
2. DataTransformationPipeline - Transforms data to learning signals
3. AgentLearningEngine - Applies learning to 152 agents
4. LearningLoop - Provides feedback and optimization

Architecture:
Spider Data → Transform → Learning Signals → Agent Learning → Improvement
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class PipelineMetrics:
    """Metrics for the unified learning pipeline"""
    pipeline_start_time: datetime
    spiders_active: int = 0
    data_points_processed: int = 0
    signals_generated: int = 0
    agents_learning: int = 0
    learning_updates_applied: int = 0
    average_processing_time: float = 0.0
    pipeline_health_score: float = 0.0
    last_metric_update: Optional[datetime] = None


@dataclass
class PipelineStatus:
    """Status of pipeline components"""
    spider_orchestrator_active: bool = False
    transformation_pipeline_active: bool = False
    learning_engine_active: bool = False
    learning_loop_active: bool = False
    redis_connected: bool = False
    overall_status: str = 'stopped'


class UnifiedLearningPipeline:
    """
    Master orchestrator for the complete spider-to-learning pipeline.
    Manages all components and ensures continuous operation.
    """

    def __init__(self):
        self.pipeline_active = False
        self.redis_client: Optional[redis.Redis] = None

        # Component instances
        self.spider_orchestrator = None
        self.transformation_pipeline = None
        self.learning_engine = None
        self.learning_loop = None

        # Pipeline metrics
        self.metrics = PipelineMetrics(
            pipeline_start_time=datetime.now(timezone.utc)
        )

        # Monitoring tasks
        self.monitoring_tasks: List[asyncio.Task] = []

        # Health check configuration
        self.health_check_interval = 30  # seconds
        self.pipeline_timeout = 300  # 5 minutes timeout for initialization

    async def initialize(self):
        """Initialize the complete pipeline"""
        try:
            logger.info("🚀 Initializing Unified Learning Pipeline...")

            # Initialize Redis connection
            await self._initialize_redis()

            # Initialize all components
            await self._initialize_components()

            # Setup inter-component connections
            await self._setup_component_connections()

            # Start monitoring
            await self._start_monitoring()

            self.pipeline_active = True
            logger.info("✅ Unified Learning Pipeline initialized successfully")

            return await self.get_pipeline_status()

        except Exception as e:
            logger.error(f"❌ Failed to initialize pipeline: {e}")
            await self.cleanup()
            raise

    async def _initialize_redis(self):
        """Initialize Redis connections"""
        try:
            # Get base Redis URL and use DB 2 for pipeline coordination
            base_redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            # Replace the database number with /2
            redis_url = base_redis_url.rsplit('/', 1)[0] + '/2' if '/' in base_redis_url else base_redis_url + '/2'
            self.redis_client = await redis.from_url(
                redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Pipeline Redis connection established")

        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

    async def _initialize_components(self):
        """Initialize all pipeline components"""
        try:
            # Initialize Spider Learning Orchestrator
            logger.info("🕷️ Initializing Spider Learning Orchestrator...")
            from .spider_learning_orchestrator import get_spider_orchestrator
            self.spider_orchestrator = get_spider_orchestrator()
            await self.spider_orchestrator.start_orchestration()
            logger.info("✅ Spider Learning Orchestrator active")

            # Initialize Data Transformation Pipeline
            logger.info("🔄 Initializing Data Transformation Pipeline...")
            from .data_transformation_pipeline import get_transformation_pipeline
            self.transformation_pipeline = get_transformation_pipeline()
            await self.transformation_pipeline.initialize()
            logger.info("✅ Data Transformation Pipeline active")

            # Initialize Agent Learning Engine
            logger.info("🧠 Initializing Agent Learning Engine...")
            from .agent_learning_engine import get_learning_engine
            self.learning_engine = get_learning_engine()
            await self.learning_engine.initialize()
            logger.info("✅ Agent Learning Engine active")

            # Initialize Learning Loop
            logger.info("🔁 Initializing Learning Loop...")
            from .learning_loop import learning_loop
            self.learning_loop = learning_loop
            await self.learning_loop.start_learning()
            logger.info("✅ Learning Loop active")

        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            raise

    async def _setup_component_connections(self):
        """Setup connections between pipeline components"""
        try:
            logger.info("🔗 Setting up component connections...")

            # Setup data flow channels
            channels = {
                'spider_data': 'spider:data:*',
                'learning_signals': 'learning:signals:*',
                'agent_updates': 'agent:updates:*',
                'pipeline_control': 'pipeline:control'
            }

            # Ensure all components are subscribed to relevant channels
            # This is handled within each component's initialization

            # Setup pipeline coordination channel
            await self.redis_client.publish(
                'pipeline:control',
                json.dumps({
                    'action': 'pipeline_initialized',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'components': ['spider_orchestrator', 'transformation_pipeline', 'learning_engine', 'learning_loop']
                })
            )

            logger.info("✅ Component connections established")

        except Exception as e:
            logger.error(f"❌ Component connection setup failed: {e}")
            raise

    async def _start_monitoring(self):
        """Start monitoring tasks for pipeline health"""
        try:
            self.monitoring_tasks = [
                asyncio.create_task(self._monitor_pipeline_health()),
                asyncio.create_task(self._monitor_data_flow()),
                asyncio.create_task(self._monitor_component_status()),
                asyncio.create_task(self._update_metrics())
            ]

            logger.info("✅ Pipeline monitoring started")

        except Exception as e:
            logger.error(f"❌ Monitoring startup failed: {e}")
            raise

    async def _monitor_pipeline_health(self):
        """Monitor overall pipeline health"""
        while self.pipeline_active:
            try:
                # Check component health
                status = await self.get_pipeline_status()

                # Calculate health score
                health_components = [
                    status.spider_orchestrator_active,
                    status.transformation_pipeline_active,
                    status.learning_engine_active,
                    status.learning_loop_active,
                    status.redis_connected
                ]

                self.metrics.pipeline_health_score = sum(health_components) / len(health_components)

                # Log health issues
                if self.metrics.pipeline_health_score < 0.8:
                    logger.warning(f"⚠️ Pipeline health degraded: {self.metrics.pipeline_health_score:.2f}")

                # Update last metric time
                self.metrics.last_metric_update = datetime.now(timezone.utc)

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on errors

    async def _monitor_data_flow(self):
        """Monitor data flow through the pipeline"""
        while self.pipeline_active:
            try:
                # Get metrics from each component
                spider_stats = await self.spider_orchestrator.get_spider_statistics() if self.spider_orchestrator else {}
                transform_stats = await self.transformation_pipeline.get_transformation_statistics() if self.transformation_pipeline else {}
                learning_stats = await self.learning_engine.get_learning_engine_status() if self.learning_engine else {}

                # Update pipeline metrics
                self.metrics.spiders_active = spider_stats.get('total_spiders', 0)
                self.metrics.data_points_processed = transform_stats.get('data_processed', 0)
                self.metrics.signals_generated = transform_stats.get('signals_generated', 0)
                self.metrics.agents_learning = learning_stats.get('agents_tracked', 0)
                self.metrics.learning_updates_applied = learning_stats.get('total_learning_updates', 0)

                # Log data flow statistics
                logger.debug(f"📊 Data flow - Spiders: {self.metrics.spiders_active}, "
                           f"Signals: {self.metrics.signals_generated}, "
                           f"Learning Updates: {self.metrics.learning_updates_applied}")

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                logger.error(f"❌ Data flow monitoring error: {e}")
                await asyncio.sleep(120)

    async def _monitor_component_status(self):
        """Monitor individual component status"""
        while self.pipeline_active:
            try:
                # Check each component
                components_status = []

                if self.spider_orchestrator:
                    components_status.append("🕷️ Spider Orchestrator: Active")
                else:
                    components_status.append("❌ Spider Orchestrator: Inactive")

                if self.transformation_pipeline:
                    components_status.append("🔄 Transformation Pipeline: Active")
                else:
                    components_status.append("❌ Transformation Pipeline: Inactive")

                if self.learning_engine:
                    components_status.append("🧠 Learning Engine: Active")
                else:
                    components_status.append("❌ Learning Engine: Inactive")

                if self.learning_loop:
                    components_status.append("🔁 Learning Loop: Active")
                else:
                    components_status.append("❌ Learning Loop: Inactive")

                # Log component status
                logger.debug("📊 Component Status:\n" + "\n".join(components_status))

                await asyncio.sleep(120)  # Check every 2 minutes

            except Exception as e:
                logger.error(f"❌ Component status monitoring error: {e}")
                await asyncio.sleep(180)

    async def _update_metrics(self):
        """Update and persist pipeline metrics"""
        while self.pipeline_active:
            try:
                # Save metrics to Redis
                metrics_data = asdict(self.metrics)
                metrics_data['pipeline_start_time'] = self.metrics.pipeline_start_time.isoformat()
                if self.metrics.last_metric_update:
                    metrics_data['last_metric_update'] = self.metrics.last_metric_update.isoformat()

                await self.redis_client.setex(
                    'pipeline:metrics',
                    300,  # 5 minute TTL
                    json.dumps(metrics_data)
                )

                await asyncio.sleep(60)  # Update every minute

            except Exception as e:
                logger.error(f"❌ Metrics update error: {e}")
                await asyncio.sleep(120)

    async def get_pipeline_status(self) -> PipelineStatus:
        """Get current pipeline status"""
        try:
            status = PipelineStatus()

            # Check Redis connection
            try:
                await self.redis_client.ping()
                status.redis_connected = True
            except:
                status.redis_connected = False

            # Check component status
            status.spider_orchestrator_active = (
                self.spider_orchestrator is not None and
                hasattr(self.spider_orchestrator, 'orchestrator_active') and
                self.spider_orchestrator.orchestrator_active
            )

            status.transformation_pipeline_active = (
                self.transformation_pipeline is not None and
                hasattr(self.transformation_pipeline, 'redis_client') and
                self.transformation_pipeline.redis_client is not None
            )

            status.learning_engine_active = (
                self.learning_engine is not None and
                hasattr(self.learning_engine, 'learning_active') and
                self.learning_engine.learning_active
            )

            status.learning_loop_active = (
                self.learning_loop is not None and
                hasattr(self.learning_loop, 'learning_active') and
                self.learning_loop.learning_active
            )

            # Determine overall status
            active_components = sum([
                status.spider_orchestrator_active,
                status.transformation_pipeline_active,
                status.learning_engine_active,
                status.learning_loop_active,
                status.redis_connected
            ])

            if active_components >= 4:
                status.overall_status = 'fully_operational'
            elif active_components >= 3:
                status.overall_status = 'partially_operational'
            elif active_components >= 1:
                status.overall_status = 'degraded'
            else:
                status.overall_status = 'stopped'

            return status

        except Exception as e:
            logger.error(f"❌ Error getting pipeline status: {e}")
            return PipelineStatus(overall_status='error')

    async def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline metrics"""
        try:
            status = await self.get_pipeline_status()

            # Component-specific metrics
            component_metrics = {}

            if self.spider_orchestrator:
                component_metrics['spider_orchestrator'] = await self.spider_orchestrator.get_spider_statistics()

            if self.transformation_pipeline:
                component_metrics['transformation_pipeline'] = await self.transformation_pipeline.get_transformation_statistics()

            if self.learning_engine:
                component_metrics['learning_engine'] = await self.learning_engine.get_learning_engine_status()

            if self.learning_loop:
                component_metrics['learning_loop'] = self.learning_loop.get_learning_status()

            return {
                'pipeline_status': asdict(status),
                'pipeline_metrics': asdict(self.metrics),
                'component_metrics': component_metrics,
                'system_info': {
                    'uptime_seconds': (datetime.now(timezone.utc) - self.metrics.pipeline_start_time).total_seconds(),
                    'pipeline_active': self.pipeline_active,
                    'monitoring_tasks_active': len([t for t in self.monitoring_tasks if not t.done()]),
                    'redis_connected': status.redis_connected
                }
            }

        except Exception as e:
            logger.error(f"❌ Error getting pipeline metrics: {e}")
            return {'error': str(e)}

    async def trigger_full_pipeline_sweep(self) -> Dict[str, Any]:
        """Manually trigger a full pipeline data sweep"""
        try:
            logger.info("🧹 Triggering full pipeline sweep...")

            results = {
                'sweep_triggered_at': datetime.now(timezone.utc).isoformat(),
                'results': {}
            }

            # Trigger spider sweep
            if self.spider_orchestrator:
                spider_sweep = await self.spider_orchestrator.trigger_spider_sweep()
                results['results']['spider_sweep'] = f"Triggered sweep of {spider_sweep} spiders"

            # Allow time for data to flow through pipeline
            await asyncio.sleep(10)

            # Get updated metrics
            metrics = await self.get_pipeline_metrics()
            results['results']['metrics_after_sweep'] = metrics['pipeline_metrics']

            logger.info("✅ Full pipeline sweep completed")
            return results

        except Exception as e:
            logger.error(f"❌ Pipeline sweep failed: {e}")
            return {'error': str(e)}

    async def restart_component(self, component_name: str) -> Dict[str, Any]:
        """Restart a specific pipeline component"""
        try:
            logger.info(f"🔄 Restarting component: {component_name}")

            if component_name == 'spider_orchestrator':
                if self.spider_orchestrator:
                    await self.spider_orchestrator.stop_orchestration()

                from .spider_learning_orchestrator import get_spider_orchestrator
                self.spider_orchestrator = get_spider_orchestrator()
                await self.spider_orchestrator.start_orchestration()

            elif component_name == 'transformation_pipeline':
                if self.transformation_pipeline:
                    await self.transformation_pipeline.cleanup()

                from .data_transformation_pipeline import get_transformation_pipeline
                self.transformation_pipeline = get_transformation_pipeline()
                await self.transformation_pipeline.initialize()

            elif component_name == 'learning_engine':
                if self.learning_engine:
                    await self.learning_engine.cleanup()

                from .agent_learning_engine import get_learning_engine
                self.learning_engine = get_learning_engine()
                await self.learning_engine.initialize()

            elif component_name == 'learning_loop':
                if self.learning_loop:
                    await self.learning_loop.stop_learning()

                from .learning_loop import learning_loop
                self.learning_loop = learning_loop
                await self.learning_loop.start_learning()

            else:
                return {'error': f'Unknown component: {component_name}'}

            logger.info(f"✅ Component {component_name} restarted successfully")
            return {'success': True, 'component': component_name, 'restarted_at': datetime.now(timezone.utc).isoformat()}

        except Exception as e:
            logger.error(f"❌ Component restart failed: {e}")
            return {'error': str(e)}

    async def pause_pipeline(self):
        """Pause the pipeline (stop processing but keep connections)"""
        try:
            logger.info("⏸️ Pausing pipeline...")

            # Pause components without full shutdown
            if self.spider_orchestrator:
                self.spider_orchestrator.orchestrator_active = False

            if self.learning_engine:
                self.learning_engine.learning_active = False

            if self.learning_loop:
                self.learning_loop.learning_active = False

            logger.info("✅ Pipeline paused")

        except Exception as e:
            logger.error(f"❌ Pipeline pause failed: {e}")

    async def resume_pipeline(self):
        """Resume the pipeline from paused state"""
        try:
            logger.info("▶️ Resuming pipeline...")

            # Resume components
            if self.spider_orchestrator:
                self.spider_orchestrator.orchestrator_active = True

            if self.learning_engine:
                self.learning_engine.learning_active = True

            if self.learning_loop:
                self.learning_loop.learning_active = True

            logger.info("✅ Pipeline resumed")

        except Exception as e:
            logger.error(f"❌ Pipeline resume failed: {e}")

    async def cleanup(self):
        """Cleanup all pipeline resources"""
        try:
            logger.info("🧹 Cleaning up pipeline...")
            self.pipeline_active = False

            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()

            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)

            # Cleanup components
            if self.spider_orchestrator:
                await self.spider_orchestrator.cleanup()

            if self.transformation_pipeline:
                await self.transformation_pipeline.cleanup()

            if self.learning_engine:
                await self.learning_engine.cleanup()

            if self.learning_loop:
                await self.learning_loop.stop_learning()

            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()

            logger.info("✅ Pipeline cleanup completed")

        except Exception as e:
            logger.error(f"❌ Pipeline cleanup error: {e}")


# Global pipeline instance
_unified_pipeline = None

def get_unified_pipeline() -> UnifiedLearningPipeline:
    """Get or create the global unified pipeline instance"""
    global _unified_pipeline
    if _unified_pipeline is None:
        _unified_pipeline = UnifiedLearningPipeline()
    return _unified_pipeline


# Main pipeline functions
async def start_unified_learning_pipeline() -> Dict[str, Any]:
    """Start the complete unified learning pipeline"""
    pipeline = get_unified_pipeline()
    return await pipeline.initialize()


async def get_pipeline_status() -> Dict[str, Any]:
    """Get current pipeline status"""
    pipeline = get_unified_pipeline()
    return asdict(await pipeline.get_pipeline_status())


async def get_pipeline_metrics() -> Dict[str, Any]:
    """Get comprehensive pipeline metrics"""
    pipeline = get_unified_pipeline()
    return await pipeline.get_pipeline_metrics()


async def trigger_pipeline_sweep() -> Dict[str, Any]:
    """Trigger a full pipeline sweep"""
    pipeline = get_unified_pipeline()
    return await pipeline.trigger_full_pipeline_sweep()