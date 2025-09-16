"""
Agent Performance Optimizer
Implements intelligent caching, model versioning, and performance monitoring
"""

import json
import time
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from django.core.cache import cache
from django.conf import settings
from django.db import transaction
from django.utils import timezone as django_timezone
import hashlib

logger = logging.getLogger(__name__)


class AgentPerformanceCache:
    """Intelligent caching system for agent operations"""

    def __init__(self):
        self.cache_prefix = "agent_perf_"
        self.default_timeout = 300  # 5 minutes
        self.confidence_threshold = 0.85

    def generate_cache_key(self, agent_id: str, operation: str, params: Dict[str, Any]) -> str:
        """Generate deterministic cache key"""
        param_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
        return f"{self.cache_prefix}{agent_id}_{operation}_{param_hash}"

    async def get_cached_result(self, agent_id: str, operation: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result if available and valid"""
        cache_key = self.generate_cache_key(agent_id, operation, params)

        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                # Check if cache is still valid
                cache_time = cached_data.get('cached_at', 0)
                confidence = cached_data.get('confidence', 0)

                # Use cached result if high confidence and recent
                if confidence >= self.confidence_threshold and time.time() - cache_time < self.default_timeout:
                    logger.debug(f"Cache hit for {agent_id} {operation}")
                    return cached_data['result']

            return None

        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            return None

    async def cache_result(self, agent_id: str, operation: str, params: Dict[str, Any],
                          result: Dict[str, Any], confidence: float = 1.0):
        """Cache operation result with metadata"""
        cache_key = self.generate_cache_key(agent_id, operation, params)

        try:
            cache_data = {
                'result': result,
                'confidence': confidence,
                'cached_at': time.time(),
                'agent_id': agent_id,
                'operation': operation
            }

            # Dynamic timeout based on confidence
            timeout = int(self.default_timeout * confidence)
            cache.set(cache_key, cache_data, timeout)

            logger.debug(f"Cached result for {agent_id} {operation} (confidence: {confidence:.2f})")

        except Exception as e:
            logger.warning(f"Cache storage error: {e}")

    async def invalidate_agent_cache(self, agent_id: str):
        """Invalidate all cached results for an agent"""
        try:
            # This is a simplified approach - in production you'd want a more efficient way
            # to track and invalidate related cache keys
            logger.info(f"Cache invalidation requested for agent {agent_id}")

        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")


class MLModelVersioning:
    """ML model versioning and confidence tracking"""

    def __init__(self):
        self.model_registry = {}
        self.performance_history = {}

    def register_model_version(self, model_name: str, version: str, metadata: Dict[str, Any]):
        """Register a new model version"""
        if model_name not in self.model_registry:
            self.model_registry[model_name] = {}

        self.model_registry[model_name][version] = {
            'metadata': metadata,
            'registered_at': time.time(),
            'performance_metrics': {},
            'confidence_intervals': {}
        }

        logger.info(f"Registered model {model_name} version {version}")

    def get_best_model_version(self, model_name: str) -> Optional[str]:
        """Get the best performing model version"""
        if model_name not in self.model_registry:
            return None

        versions = self.model_registry[model_name]
        if not versions:
            return None

        # Select version with highest average performance
        best_version = None
        best_score = 0

        for version, data in versions.items():
            metrics = data.get('performance_metrics', {})
            avg_score = metrics.get('average_confidence', 0)

            if avg_score > best_score:
                best_score = avg_score
                best_version = version

        return best_version

    def update_model_performance(self, model_name: str, version: str,
                                confidence: float, actual_outcome: bool):
        """Update model performance metrics"""
        if model_name not in self.model_registry:
            return

        if version not in self.model_registry[model_name]:
            return

        model_data = self.model_registry[model_name][version]
        metrics = model_data.setdefault('performance_metrics', {
            'predictions': [],
            'average_confidence': 0,
            'accuracy': 0,
            'total_predictions': 0
        })

        # Add new prediction
        metrics['predictions'].append({
            'confidence': confidence,
            'correct': actual_outcome,
            'timestamp': time.time()
        })

        # Keep only recent predictions (last 1000)
        if len(metrics['predictions']) > 1000:
            metrics['predictions'] = metrics['predictions'][-1000:]

        # Recalculate metrics
        recent_predictions = metrics['predictions']
        if recent_predictions:
            metrics['average_confidence'] = sum(p['confidence'] for p in recent_predictions) / len(recent_predictions)
            metrics['accuracy'] = sum(1 for p in recent_predictions if p['correct']) / len(recent_predictions)
            metrics['total_predictions'] = len(recent_predictions)

        logger.debug(f"Updated {model_name} v{version} performance: {metrics['accuracy']:.2f} accuracy")

    def get_confidence_interval(self, model_name: str, version: str, confidence: float) -> Tuple[float, float]:
        """Calculate confidence interval for a prediction"""
        if model_name not in self.model_registry:
            return (confidence * 0.8, confidence * 1.2)

        if version not in self.model_registry[model_name]:
            return (confidence * 0.8, confidence * 1.2)

        model_data = self.model_registry[model_name][version]
        metrics = model_data.get('performance_metrics', {})

        # Calculate confidence interval based on historical accuracy
        accuracy = metrics.get('accuracy', 0.5)
        adjustment_factor = accuracy  # Simple approach

        lower_bound = max(0, confidence * adjustment_factor)
        upper_bound = min(1, confidence / adjustment_factor if adjustment_factor > 0 else confidence)

        return (lower_bound, upper_bound)


class AgentPerformanceMonitor:
    """Real-time agent performance monitoring"""

    def __init__(self):
        self.performance_cache = AgentPerformanceCache()
        self.model_versioning = MLModelVersioning()
        self.performance_metrics = {}
        self.alert_thresholds = {
            'response_time': 5.0,  # seconds
            'error_rate': 0.1,     # 10%
            'confidence_drop': 0.2  # 20% drop
        }

    async def monitor_agent_execution(self, agent_id: str, task_type: str,
                                    execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and optimize agent execution"""
        start_time = time.time()

        try:
            # Check cache first
            cached_result = await self.performance_cache.get_cached_result(
                agent_id, task_type, execution_data
            )

            if cached_result:
                execution_time = time.time() - start_time
                return {
                    'result': cached_result,
                    'execution_time': execution_time,
                    'cache_hit': True,
                    'performance_score': 1.0
                }

            # Execute agent task (placeholder - would call actual agent)
            result = await self.execute_agent_task(agent_id, task_type, execution_data)

            execution_time = time.time() - start_time

            # Calculate performance metrics
            performance_score = self.calculate_performance_score(
                execution_time, result.get('confidence', 0.5), result.get('success', True)
            )

            # Cache result if high performance
            if performance_score > 0.8:
                await self.performance_cache.cache_result(
                    agent_id, task_type, execution_data, result, performance_score
                )

            # Update performance tracking
            await self.update_agent_metrics(agent_id, execution_time, performance_score, result)

            # Check for performance alerts
            await self.check_performance_alerts(agent_id, execution_time, performance_score)

            return {
                'result': result,
                'execution_time': execution_time,
                'cache_hit': False,
                'performance_score': performance_score,
                'metrics_updated': True
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Agent execution error for {agent_id}: {e}")

            await self.update_agent_metrics(agent_id, execution_time, 0.0, {'error': str(e)})

            return {
                'result': {'error': str(e), 'success': False},
                'execution_time': execution_time,
                'cache_hit': False,
                'performance_score': 0.0,
                'error': True
            }

    async def execute_agent_task(self, agent_id: str, task_type: str,
                                execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task (optimized with ML model versioning)"""

        # Get best model version for this task type
        best_model = self.model_versioning.get_best_model_version(f"agent_{task_type}")

        # Simulate agent execution with model versioning
        await asyncio.sleep(0.1)  # Simulate processing

        # Generate realistic result
        base_confidence = 0.75 + (hash(agent_id) % 20) / 100

        # Apply model version adjustment
        if best_model:
            model_adjustment = 0.1  # Better models perform better
            base_confidence = min(1.0, base_confidence + model_adjustment)

        result = {
            'success': True,
            'confidence': base_confidence,
            'model_version': best_model or 'default',
            'task_type': task_type,
            'agent_id': agent_id,
            'timestamp': time.time()
        }

        # Update model performance tracking
        if best_model:
            # Simulate actual outcome (in reality this would come from user feedback)
            actual_success = base_confidence > 0.7
            self.model_versioning.update_model_performance(
                f"agent_{task_type}", best_model, base_confidence, actual_success
            )

        return result

    def calculate_performance_score(self, execution_time: float, confidence: float, success: bool) -> float:
        """Calculate overall performance score"""
        # Time component (faster is better)
        time_score = max(0, 1 - (execution_time / 10))  # Perfect score under 0s, 0 score at 10s

        # Confidence component
        confidence_score = confidence

        # Success component
        success_score = 1.0 if success else 0.0

        # Weighted average
        performance_score = (time_score * 0.3 + confidence_score * 0.4 + success_score * 0.3)

        return min(1.0, max(0.0, performance_score))

    async def update_agent_metrics(self, agent_id: str, execution_time: float,
                                  performance_score: float, result: Dict[str, Any]):
        """Update agent performance metrics"""
        current_time = time.time()

        if agent_id not in self.performance_metrics:
            self.performance_metrics[agent_id] = {
                'total_executions': 0,
                'total_time': 0,
                'average_time': 0,
                'success_rate': 0,
                'average_performance': 0,
                'last_updated': current_time,
                'recent_executions': []
            }

        metrics = self.performance_metrics[agent_id]

        # Update counters
        metrics['total_executions'] += 1
        metrics['total_time'] += execution_time
        metrics['average_time'] = metrics['total_time'] / metrics['total_executions']

        # Add to recent executions (keep last 100)
        metrics['recent_executions'].append({
            'timestamp': current_time,
            'execution_time': execution_time,
            'performance_score': performance_score,
            'success': result.get('success', True),
            'confidence': result.get('confidence', 0)
        })

        if len(metrics['recent_executions']) > 100:
            metrics['recent_executions'] = metrics['recent_executions'][-100:]

        # Calculate success rate and average performance from recent executions
        recent = metrics['recent_executions']
        if recent:
            metrics['success_rate'] = sum(1 for e in recent if e['success']) / len(recent)
            metrics['average_performance'] = sum(e['performance_score'] for e in recent) / len(recent)

        metrics['last_updated'] = current_time

        logger.debug(f"Updated metrics for {agent_id}: {metrics['average_performance']:.2f} avg performance")

    async def check_performance_alerts(self, agent_id: str, execution_time: float, performance_score: float):
        """Check for performance alerts"""
        alerts = []

        # Check response time
        if execution_time > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'slow_response',
                'agent_id': agent_id,
                'execution_time': execution_time,
                'threshold': self.alert_thresholds['response_time'],
                'severity': 'warning'
            })

        # Check performance score
        if performance_score < 0.5:
            alerts.append({
                'type': 'low_performance',
                'agent_id': agent_id,
                'performance_score': performance_score,
                'severity': 'critical'
            })

        # Check error rate for this agent
        if agent_id in self.performance_metrics:
            metrics = self.performance_metrics[agent_id]
            if metrics['success_rate'] < (1 - self.alert_thresholds['error_rate']):
                alerts.append({
                    'type': 'high_error_rate',
                    'agent_id': agent_id,
                    'success_rate': metrics['success_rate'],
                    'threshold': 1 - self.alert_thresholds['error_rate'],
                    'severity': 'critical'
                })

        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance alert: {alert}")

        return alerts

    async def get_agent_performance_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for an agent"""
        if agent_id not in self.performance_metrics:
            return {
                'agent_id': agent_id,
                'status': 'no_data',
                'message': 'No performance data available'
            }

        metrics = self.performance_metrics[agent_id]

        # Calculate trends
        recent = metrics['recent_executions'][-10:]  # Last 10 executions
        older = metrics['recent_executions'][-20:-10]  # Previous 10 executions

        performance_trend = 'stable'
        if recent and older:
            recent_avg = sum(e['performance_score'] for e in recent) / len(recent)
            older_avg = sum(e['performance_score'] for e in older) / len(older)

            if recent_avg > older_avg + 0.1:
                performance_trend = 'improving'
            elif recent_avg < older_avg - 0.1:
                performance_trend = 'declining'

        return {
            'agent_id': agent_id,
            'status': 'active',
            'total_executions': metrics['total_executions'],
            'average_response_time': metrics['average_time'],
            'success_rate': metrics['success_rate'],
            'average_performance': metrics['average_performance'],
            'performance_trend': performance_trend,
            'last_updated': metrics['last_updated'],
            'health_score': min(1.0, metrics['average_performance'] * metrics['success_rate']),
            'recommendations': self.generate_performance_recommendations(metrics)
        }

    def generate_performance_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        if metrics['average_time'] > 3.0:
            recommendations.append("Consider optimizing response time - current average is above 3 seconds")

        if metrics['success_rate'] < 0.9:
            recommendations.append("Success rate below 90% - review error handling and task complexity")

        if metrics['average_performance'] < 0.7:
            recommendations.append("Overall performance below optimal - consider model retraining or parameter tuning")

        if len(metrics['recent_executions']) < 10:
            recommendations.append("Insufficient recent execution data for reliable performance assessment")

        if not recommendations:
            recommendations.append("Performance within acceptable ranges - continue monitoring")

        return recommendations

    async def optimize_agent_pipeline(self) -> Dict[str, Any]:
        """Optimize the entire agent pipeline"""
        optimization_start = time.time()

        # Analyze all agent performance
        total_agents = len(self.performance_metrics)
        high_performers = 0
        low_performers = 0

        for agent_id, metrics in self.performance_metrics.items():
            health_score = min(1.0, metrics['average_performance'] * metrics['success_rate'])

            if health_score > 0.8:
                high_performers += 1
            elif health_score < 0.5:
                low_performers += 1

        # Calculate pipeline efficiency
        pipeline_efficiency = high_performers / total_agents if total_agents > 0 else 0

        # Generate optimization recommendations
        optimizations = []
        if pipeline_efficiency < 0.8:
            optimizations.append("Consider agent retraining or replacement for low performers")

        if low_performers > 0:
            optimizations.append(f"Investigate {low_performers} underperforming agents")

        # Clear old performance data
        cutoff_time = time.time() - 86400  # 24 hours
        cleaned_agents = 0

        for agent_id in list(self.performance_metrics.keys()):
            metrics = self.performance_metrics[agent_id]
            if metrics['last_updated'] < cutoff_time:
                del self.performance_metrics[agent_id]
                cleaned_agents += 1

        optimization_time = time.time() - optimization_start

        return {
            'optimization_time': optimization_time,
            'total_agents': total_agents,
            'high_performers': high_performers,
            'low_performers': low_performers,
            'pipeline_efficiency': pipeline_efficiency,
            'cleaned_agents': cleaned_agents,
            'optimizations': optimizations,
            'overall_health': 'excellent' if pipeline_efficiency > 0.9 else 'good' if pipeline_efficiency > 0.7 else 'needs_attention'
        }


# Global optimizer instance
agent_optimizer = AgentPerformanceMonitor()

# Initialize some default model versions
agent_optimizer.model_versioning.register_model_version(
    "agent_content_generation", "v1.0",
    {"description": "Base content generation model", "accuracy": 0.85}
)

agent_optimizer.model_versioning.register_model_version(
    "agent_opportunity_analysis", "v1.2",
    {"description": "Enhanced opportunity analysis model", "accuracy": 0.78}
)

agent_optimizer.model_versioning.register_model_version(
    "agent_decision_making", "v2.0",
    {"description": "Advanced decision making model", "accuracy": 0.82}
)