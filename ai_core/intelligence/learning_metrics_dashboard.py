"""
Learning Metrics Dashboard - Monitor Learning Effectiveness
===========================================================

This module provides comprehensive metrics and monitoring for the
spider-to-learning pipeline, tracking:

- Learning effectiveness per agent
- Data flow rates and quality
- Knowledge accumulation metrics
- Pipeline performance indicators
- ROI on learning investments
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import numpy as np
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class LearningMetrics:
    """Comprehensive learning metrics"""
    # Time period metrics
    period_start: datetime
    period_end: datetime

    # Data flow metrics
    total_spider_signals: int = 0
    signals_transformed: int = 0
    learning_updates_generated: int = 0
    successful_learning_applications: int = 0

    # Agent learning metrics
    agents_actively_learning: int = 0
    total_knowledge_items_learned: int = 0
    total_patterns_recognized: int = 0
    total_skills_improved: int = 0

    # Quality metrics
    average_signal_quality: float = 0.0
    average_learning_confidence: float = 0.0
    learning_success_rate: float = 0.0

    # Performance metrics
    average_processing_latency: float = 0.0
    throughput_per_hour: float = 0.0
    error_rate: float = 0.0

    # Effectiveness metrics
    agent_performance_improvement: float = 0.0
    knowledge_retention_rate: float = 0.0
    cross_domain_learning_rate: float = 0.0


@dataclass
class AgentLearningMetrics:
    """Learning metrics for individual agents"""
    agent_id: str
    agent_name: str
    specialization: str

    # Learning volume metrics
    signals_processed: int = 0
    knowledge_items_acquired: int = 0
    patterns_learned: int = 0
    skills_enhanced: int = 0

    # Quality metrics
    average_learning_confidence: float = 0.0
    learning_retention_score: float = 0.0
    cross_domain_learning_count: int = 0

    # Performance metrics
    learning_velocity: float = 0.0  # learning items per hour
    improvement_rate: float = 0.0   # performance improvement rate
    adaptation_speed: float = 0.0   # how quickly agent adapts to new info

    # Effectiveness indicators
    knowledge_application_rate: float = 0.0
    decision_accuracy_improvement: float = 0.0
    task_completion_improvement: float = 0.0


@dataclass
class PipelineHealth:
    """Pipeline health indicators"""
    overall_health_score: float = 0.0
    component_health: Dict[str, float] = None
    data_flow_health: float = 0.0
    learning_pipeline_health: float = 0.0
    system_resource_health: float = 0.0

    # Health issues
    critical_issues: List[str] = None
    warnings: List[str] = None
    recommendations: List[str] = None


class LearningMetricsDashboard:
    """
    Comprehensive metrics dashboard for learning effectiveness.
    Tracks all aspects of the spider-to-learning pipeline.
    """

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.monitoring_active = False

        # Metrics storage
        self.current_metrics = LearningMetrics(
            period_start=datetime.now(timezone.utc),
            period_end=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        self.agent_metrics: Dict[str, AgentLearningMetrics] = {}
        self.historical_metrics: List[LearningMetrics] = []

        # Monitoring configuration
        self.metrics_update_interval = 60  # seconds
        self.health_check_interval = 30   # seconds
        self.retention_period = timedelta(days=30)

    async def initialize(self):
        """Initialize the metrics dashboard"""
        try:
            # Setup Redis connection - use DB 3 for metrics
            base_redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            redis_url = base_redis_url.rsplit('/', 1)[0] + '/3' if '/' in base_redis_url else base_redis_url + '/3'
            self.redis_client = await redis.from_url(
                redis_url,
                encoding='utf-8',
                decode_responses=True
            )
            await self.redis_client.ping()

            # Load historical metrics
            await self._load_historical_metrics()

            # Initialize agent metrics
            await self._initialize_agent_metrics()

            # Start monitoring
            self.monitoring_active = True
            asyncio.create_task(self._continuous_monitoring())

            logger.info("📊 Learning metrics dashboard initialized")

        except Exception as e:
            logger.error(f"Failed to initialize metrics dashboard: {e}")
            raise

    async def _load_historical_metrics(self):
        """Load historical metrics from Redis"""
        try:
            # Load last 30 days of metrics
            keys = await self.redis_client.keys('metrics:learning:*')

            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    try:
                        metrics_data = json.loads(data)
                        # Convert datetime strings back to datetime objects
                        metrics_data['period_start'] = datetime.fromisoformat(metrics_data['period_start'])
                        metrics_data['period_end'] = datetime.fromisoformat(metrics_data['period_end'])

                        metrics = LearningMetrics(**metrics_data)
                        self.historical_metrics.append(metrics)
                    except Exception as e:
                        logger.warning(f"Could not load historical metric {key}: {e}")

            # Sort by time
            self.historical_metrics.sort(key=lambda m: m.period_start)

            # Keep only recent metrics
            cutoff = datetime.now(timezone.utc) - self.retention_period
            self.historical_metrics = [m for m in self.historical_metrics if m.period_start > cutoff]

            logger.info(f"Loaded {len(self.historical_metrics)} historical metric records")

        except Exception as e:
            logger.error(f"Error loading historical metrics: {e}")

    async def _initialize_agent_metrics(self):
        """Initialize metrics tracking for all agents"""
        try:
            # Get agent learning engine to access agent profiles
            from .agent_learning_engine import get_learning_engine
            learning_engine = get_learning_engine()

            # Initialize metrics for each agent
            for agent_id, profile in learning_engine.agent_profiles.items():
                self.agent_metrics[agent_id] = AgentLearningMetrics(
                    agent_id=agent_id,
                    agent_name=profile.agent_name,
                    specialization=profile.specialization
                )

            logger.info(f"Initialized metrics for {len(self.agent_metrics)} agents")

        except Exception as e:
            logger.error(f"Error initializing agent metrics: {e}")

    async def _continuous_monitoring(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Update current metrics
                await self._update_current_metrics()

                # Update agent metrics
                await self._update_agent_metrics()

                # Save metrics to Redis
                await self._save_metrics()

                # Clean up old metrics
                await self._cleanup_old_metrics()

                await asyncio.sleep(self.metrics_update_interval)

            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on errors

    async def _update_current_metrics(self):
        """Update current learning metrics"""
        try:
            # Get metrics from pipeline components
            from .unified_learning_pipeline import get_unified_pipeline
            pipeline = get_unified_pipeline()

            pipeline_metrics = await pipeline.get_pipeline_metrics()

            if 'component_metrics' in pipeline_metrics:
                components = pipeline_metrics['component_metrics']

                # Spider orchestrator metrics
                if 'spider_orchestrator' in components:
                    spider_stats = components['spider_orchestrator']
                    self.current_metrics.total_spider_signals = spider_stats.get('signals_processed', 0)

                # Transformation pipeline metrics
                if 'transformation_pipeline' in components:
                    transform_stats = components['transformation_pipeline']
                    self.current_metrics.signals_transformed = transform_stats.get('signals_generated', 0)
                    self.current_metrics.average_signal_quality = transform_stats.get('average_quality_score', 0.0)

                # Learning engine metrics
                if 'learning_engine' in components:
                    learning_stats = components['learning_engine']
                    self.current_metrics.learning_updates_generated = learning_stats.get('total_learning_updates', 0)
                    self.current_metrics.agents_actively_learning = learning_stats.get('agents_tracked', 0)
                    self.current_metrics.total_knowledge_items_learned = learning_stats.get('knowledge_items_added', 0)
                    self.current_metrics.total_patterns_recognized = learning_stats.get('patterns_learned', 0)
                    self.current_metrics.total_skills_improved = learning_stats.get('skills_enhanced', 0)

            # Calculate derived metrics
            self._calculate_derived_metrics()

        except Exception as e:
            logger.error(f"Error updating current metrics: {e}")

    def _calculate_derived_metrics(self):
        """Calculate derived metrics from raw data"""
        try:
            # Learning success rate
            if self.current_metrics.learning_updates_generated > 0:
                self.current_metrics.learning_success_rate = (
                    self.current_metrics.successful_learning_applications /
                    self.current_metrics.learning_updates_generated
                )

            # Throughput per hour
            time_elapsed = (datetime.now(timezone.utc) - self.current_metrics.period_start).total_seconds() / 3600
            if time_elapsed > 0:
                self.current_metrics.throughput_per_hour = (
                    self.current_metrics.signals_transformed / time_elapsed
                )

            # Error rate (simplified calculation)
            total_operations = self.current_metrics.total_spider_signals
            failed_operations = total_operations - self.current_metrics.signals_transformed
            if total_operations > 0:
                self.current_metrics.error_rate = failed_operations / total_operations

        except Exception as e:
            logger.error(f"Error calculating derived metrics: {e}")

    async def _update_agent_metrics(self):
        """Update metrics for individual agents"""
        try:
            from .agent_learning_engine import get_learning_engine
            learning_engine = get_learning_engine()

            for agent_id in self.agent_metrics.keys():
                try:
                    # Get agent learning status
                    agent_status = await learning_engine.get_agent_learning_status(agent_id)

                    if 'error' not in agent_status:
                        agent_metrics = self.agent_metrics[agent_id]

                        # Update basic metrics
                        agent_metrics.signals_processed = agent_status.get('total_signals_processed', 0)
                        agent_metrics.knowledge_items_acquired = agent_status.get('knowledge_items', 0)
                        agent_metrics.patterns_learned = len(agent_status.get('learned_patterns', []))
                        agent_metrics.skills_enhanced = len(agent_status.get('skill_improvements', {}))

                        # Calculate learning velocity (items per hour)
                        time_active = (datetime.now(timezone.utc) - self.current_metrics.period_start).total_seconds() / 3600
                        if time_active > 0:
                            total_learning_items = (
                                agent_metrics.knowledge_items_acquired +
                                agent_metrics.patterns_learned +
                                agent_metrics.skills_enhanced
                            )
                            agent_metrics.learning_velocity = total_learning_items / time_active

                except Exception as e:
                    logger.error(f"Error updating metrics for agent {agent_id}: {e}")

        except Exception as e:
            logger.error(f"Error updating agent metrics: {e}")

    async def _save_metrics(self):
        """Save current metrics to Redis"""
        try:
            # Save current metrics
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')
            key = f"metrics:learning:{timestamp}"

            metrics_data = asdict(self.current_metrics)
            metrics_data['period_start'] = self.current_metrics.period_start.isoformat()
            metrics_data['period_end'] = self.current_metrics.period_end.isoformat()

            await self.redis_client.setex(
                key,
                86400 * 7,  # 7 day TTL
                json.dumps(metrics_data)
            )

            # Save agent metrics
            for agent_id, agent_metrics in self.agent_metrics.items():
                agent_key = f"metrics:agent:{agent_id}:{timestamp}"
                await self.redis_client.setex(
                    agent_key,
                    86400 * 7,
                    json.dumps(asdict(agent_metrics))
                )

            # Save dashboard status
            status_key = "metrics:dashboard:status"
            status = {
                'last_update': datetime.now(timezone.utc).isoformat(),
                'monitoring_active': self.monitoring_active,
                'agents_tracked': len(self.agent_metrics),
                'metrics_health': 'good'
            }
            await self.redis_client.setex(status_key, 300, json.dumps(status))

        except Exception as e:
            logger.error(f"Error saving metrics: {e}")

    async def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        try:
            cutoff = datetime.now(timezone.utc) - self.retention_period
            cutoff_str = cutoff.strftime('%Y%m%d_%H%M')

            # Clean up old learning metrics
            keys = await self.redis_client.keys('metrics:learning:*')
            for key in keys:
                timestamp_str = key.split(':')[-1]
                if timestamp_str < cutoff_str:
                    await self.redis_client.delete(key)

            # Clean up old agent metrics
            keys = await self.redis_client.keys('metrics:agent:*')
            for key in keys:
                timestamp_str = key.split(':')[-1]
                if timestamp_str < cutoff_str:
                    await self.redis_client.delete(key)

        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")

    async def get_learning_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive learning dashboard data"""
        try:
            # Calculate pipeline health
            health = await self._calculate_pipeline_health()

            # Get top performing agents
            top_agents = self._get_top_performing_agents()

            # Get learning trends
            trends = self._calculate_learning_trends()

            # Get learning effectiveness score
            effectiveness_score = self._calculate_learning_effectiveness()

            dashboard = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'current_metrics': asdict(self.current_metrics),
                'pipeline_health': asdict(health),
                'top_agents': top_agents,
                'learning_trends': trends,
                'effectiveness_score': effectiveness_score,
                'agent_count': len(self.agent_metrics),
                'monitoring_active': self.monitoring_active,
                'system_status': {
                    'redis_connected': self.redis_client is not None,
                    'metrics_age_minutes': (
                        datetime.now(timezone.utc) - self.current_metrics.period_start
                    ).total_seconds() / 60
                }
            }

            return dashboard

        except Exception as e:
            logger.error(f"Error generating learning dashboard: {e}")
            return {'error': str(e)}

    async def _calculate_pipeline_health(self) -> PipelineHealth:
        """Calculate overall pipeline health"""
        try:
            health = PipelineHealth(
                component_health={},
                critical_issues=[],
                warnings=[],
                recommendations=[]
            )

            # Component health checks
            from .unified_learning_pipeline import get_unified_pipeline
            pipeline = get_unified_pipeline()
            status = await pipeline.get_pipeline_status()

            components = {
                'spider_orchestrator': status.spider_orchestrator_active,
                'transformation_pipeline': status.transformation_pipeline_active,
                'learning_engine': status.learning_engine_active,
                'learning_loop': status.learning_loop_active,
                'redis': status.redis_connected
            }

            health.component_health = {name: 1.0 if active else 0.0 for name, active in components.items()}

            # Data flow health
            if self.current_metrics.total_spider_signals > 0:
                health.data_flow_health = min(1.0, self.current_metrics.signals_transformed / self.current_metrics.total_spider_signals)
            else:
                health.data_flow_health = 0.0

            # Learning pipeline health
            if self.current_metrics.learning_updates_generated > 0:
                health.learning_pipeline_health = min(1.0, self.current_metrics.successful_learning_applications / self.current_metrics.learning_updates_generated)
            else:
                health.learning_pipeline_health = 0.0

            # Overall health score
            health.overall_health_score = np.mean([
                np.mean(list(health.component_health.values())),
                health.data_flow_health,
                health.learning_pipeline_health
            ])

            # Generate issues and recommendations
            if health.overall_health_score < 0.5:
                health.critical_issues.append("Pipeline health critically degraded")
            elif health.overall_health_score < 0.8:
                health.warnings.append("Pipeline performance below optimal")

            if health.data_flow_health < 0.7:
                health.recommendations.append("Check spider data collection rates")

            if health.learning_pipeline_health < 0.7:
                health.recommendations.append("Review agent learning configurations")

            return health

        except Exception as e:
            logger.error(f"Error calculating pipeline health: {e}")
            return PipelineHealth()

    def _get_top_performing_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing agents by learning metrics"""
        try:
            agent_scores = []

            for agent_id, metrics in self.agent_metrics.items():
                # Calculate composite performance score
                score = (
                    metrics.learning_velocity * 0.3 +
                    metrics.knowledge_items_acquired * 0.2 +
                    metrics.patterns_learned * 0.2 +
                    metrics.skills_enhanced * 0.2 +
                    metrics.average_learning_confidence * 0.1
                )

                agent_scores.append({
                    'agent_id': agent_id,
                    'agent_name': metrics.agent_name,
                    'specialization': metrics.specialization,
                    'performance_score': score,
                    'learning_velocity': metrics.learning_velocity,
                    'total_learning_items': (
                        metrics.knowledge_items_acquired +
                        metrics.patterns_learned +
                        metrics.skills_enhanced
                    )
                })

            # Sort by performance score
            agent_scores.sort(key=lambda x: x['performance_score'], reverse=True)

            return agent_scores[:limit]

        except Exception as e:
            logger.error(f"Error getting top performing agents: {e}")
            return []

    def _calculate_learning_trends(self) -> Dict[str, Any]:
        """Calculate learning trends over time"""
        try:
            if len(self.historical_metrics) < 2:
                return {'insufficient_data': True}

            # Get recent metrics for trend calculation
            recent_metrics = self.historical_metrics[-10:]  # Last 10 periods

            # Calculate trends
            trends = {
                'learning_velocity_trend': self._calculate_trend([m.total_knowledge_items_learned for m in recent_metrics]),
                'signal_quality_trend': self._calculate_trend([m.average_signal_quality for m in recent_metrics]),
                'throughput_trend': self._calculate_trend([m.throughput_per_hour for m in recent_metrics]),
                'error_rate_trend': self._calculate_trend([m.error_rate for m in recent_metrics], inverse=True),
                'agent_learning_trend': self._calculate_trend([m.agents_actively_learning for m in recent_metrics])
            }

            return trends

        except Exception as e:
            logger.error(f"Error calculating learning trends: {e}")
            return {'error': str(e)}

    def _calculate_trend(self, values: List[float], inverse: bool = False) -> Dict[str, Any]:
        """Calculate trend for a series of values"""
        try:
            if len(values) < 2:
                return {'trend': 'insufficient_data', 'direction': 'unknown', 'rate': 0.0}

            # Calculate linear trend
            x = np.arange(len(values))
            coefficients = np.polyfit(x, values, 1)
            slope = coefficients[0]

            # Invert for metrics where lower is better (like error rate)
            if inverse:
                slope = -slope

            # Determine trend direction
            if slope > 0.01:
                direction = 'improving'
            elif slope < -0.01:
                direction = 'declining'
            else:
                direction = 'stable'

            return {
                'trend': direction,
                'direction': direction,
                'rate': abs(slope),
                'current_value': values[-1] if values else 0,
                'change_from_previous': values[-1] - values[-2] if len(values) >= 2 else 0
            }

        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return {'trend': 'error', 'direction': 'unknown', 'rate': 0.0}

    def _calculate_learning_effectiveness(self) -> float:
        """Calculate overall learning effectiveness score"""
        try:
            # Factors for effectiveness score
            factors = []

            # Learning success rate
            if self.current_metrics.learning_success_rate > 0:
                factors.append(min(1.0, self.current_metrics.learning_success_rate))

            # Signal quality
            if self.current_metrics.average_signal_quality > 0:
                factors.append(self.current_metrics.average_signal_quality)

            # Throughput efficiency
            if self.current_metrics.throughput_per_hour > 0:
                # Normalize throughput (assuming 100 signals/hour is good performance)
                throughput_score = min(1.0, self.current_metrics.throughput_per_hour / 100)
                factors.append(throughput_score)

            # Error rate (inverted)
            error_score = 1.0 - min(1.0, self.current_metrics.error_rate)
            factors.append(error_score)

            # Agent learning activity
            if len(self.agent_metrics) > 0:
                learning_agents_ratio = self.current_metrics.agents_actively_learning / len(self.agent_metrics)
                factors.append(learning_agents_ratio)

            # Calculate weighted average
            if factors:
                return np.mean(factors)
            else:
                return 0.0

        except Exception as e:
            logger.error(f"Error calculating learning effectiveness: {e}")
            return 0.0

    async def get_agent_learning_report(self, agent_id: str) -> Dict[str, Any]:
        """Get detailed learning report for a specific agent"""
        try:
            if agent_id not in self.agent_metrics:
                return {'error': 'Agent not found'}

            metrics = self.agent_metrics[agent_id]

            # Get enhanced data from learning engine
            from .agent_learning_engine import get_learning_engine
            learning_engine = get_learning_engine()
            agent_status = await learning_engine.get_agent_learning_status(agent_id)

            report = {
                'agent_info': {
                    'agent_id': agent_id,
                    'agent_name': metrics.agent_name,
                    'specialization': metrics.specialization
                },
                'learning_metrics': asdict(metrics),
                'current_status': agent_status,
                'performance_analysis': {
                    'learning_rank': self._get_agent_learning_rank(agent_id),
                    'specialization_rank': self._get_agent_specialization_rank(agent_id),
                    'improvement_suggestions': self._get_agent_improvement_suggestions(agent_id)
                },
                'generated_at': datetime.now(timezone.utc).isoformat()
            }

            return report

        except Exception as e:
            logger.error(f"Error generating agent learning report: {e}")
            return {'error': str(e)}

    def _get_agent_learning_rank(self, agent_id: str) -> int:
        """Get agent's rank among all agents by learning performance"""
        try:
            agent_scores = [(aid, self._calculate_agent_score(aid)) for aid in self.agent_metrics.keys()]
            agent_scores.sort(key=lambda x: x[1], reverse=True)

            for rank, (aid, score) in enumerate(agent_scores, 1):
                if aid == agent_id:
                    return rank

            return len(agent_scores)

        except Exception as e:
            logger.error(f"Error getting agent learning rank: {e}")
            return -1

    def _get_agent_specialization_rank(self, agent_id: str) -> int:
        """Get agent's rank within their specialization"""
        try:
            if agent_id not in self.agent_metrics:
                return -1

            specialization = self.agent_metrics[agent_id].specialization
            spec_agents = [aid for aid, metrics in self.agent_metrics.items()
                          if metrics.specialization == specialization]

            spec_scores = [(aid, self._calculate_agent_score(aid)) for aid in spec_agents]
            spec_scores.sort(key=lambda x: x[1], reverse=True)

            for rank, (aid, score) in enumerate(spec_scores, 1):
                if aid == agent_id:
                    return rank

            return len(spec_scores)

        except Exception as e:
            logger.error(f"Error getting agent specialization rank: {e}")
            return -1

    def _calculate_agent_score(self, agent_id: str) -> float:
        """Calculate composite score for an agent"""
        if agent_id not in self.agent_metrics:
            return 0.0

        metrics = self.agent_metrics[agent_id]
        return (
            metrics.learning_velocity * 0.3 +
            metrics.knowledge_items_acquired * 0.2 +
            metrics.patterns_learned * 0.2 +
            metrics.skills_enhanced * 0.2 +
            metrics.average_learning_confidence * 0.1
        )

    def _get_agent_improvement_suggestions(self, agent_id: str) -> List[str]:
        """Get improvement suggestions for an agent"""
        if agent_id not in self.agent_metrics:
            return ['Agent not found']

        metrics = self.agent_metrics[agent_id]
        suggestions = []

        if metrics.learning_velocity < 1.0:
            suggestions.append("Increase learning signal processing rate")

        if metrics.average_learning_confidence < 0.7:
            suggestions.append("Focus on higher quality learning signals")

        if metrics.cross_domain_learning_count < 5:
            suggestions.append("Explore cross-domain learning opportunities")

        if metrics.patterns_learned < 10:
            suggestions.append("Enhance pattern recognition capabilities")

        if not suggestions:
            suggestions.append("Performance is excellent - maintain current approach")

        return suggestions

    async def cleanup(self):
        """Cleanup dashboard resources"""
        self.monitoring_active = False
        if self.redis_client:
            await self.redis_client.close()


# Global dashboard instance
_metrics_dashboard = None

def get_metrics_dashboard() -> LearningMetricsDashboard:
    """Get or create the global metrics dashboard instance"""
    global _metrics_dashboard
    if _metrics_dashboard is None:
        _metrics_dashboard = LearningMetricsDashboard()
    return _metrics_dashboard


# Convenience functions
async def start_learning_metrics():
    """Start the learning metrics dashboard"""
    dashboard = get_metrics_dashboard()
    await dashboard.initialize()
    return dashboard


async def get_learning_dashboard_data() -> Dict[str, Any]:
    """Get learning dashboard data"""
    dashboard = get_metrics_dashboard()
    return await dashboard.get_learning_dashboard()


async def get_agent_report(agent_id: str) -> Dict[str, Any]:
    """Get detailed report for an agent"""
    dashboard = get_metrics_dashboard()
    return await dashboard.get_agent_learning_report(agent_id)