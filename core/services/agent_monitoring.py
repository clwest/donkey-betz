# Session 728: Migrated from agents/monitoring.py
"""
Agent Execution Monitoring and Performance Tracking
Provides detailed metrics and logging for agent performance analysis
"""

import logging
import os
import time
import traceback
from datetime import datetime, timedelta
from functools import wraps
from django.core.cache import cache
from django.db import models, connection
from django.utils import timezone

logger = logging.getLogger(__name__)

# Metrics configuration
METRICS_CONFIG = {
    'enable_monitoring': True,
    'enable_detailed_logging': True,
    'track_database_queries': True,
    'track_memory_usage': True,
    'track_api_calls': True,
    'alert_thresholds': {
        'execution_time': 30,  # seconds
        'memory_usage': 100,  # MB
        'database_queries': 50,  # queries
        'error_rate': 0.1,  # 10%
        'api_response_time': 5,  # seconds
    }
}


class AgentMonitor:
    """
    Monitor and track agent execution performance
    """
    
    def __init__(self, agent_name=None, execution_id=None):
        self.agent_name = agent_name
        self.execution_id = execution_id
        self.start_time = None
        self.end_time = None
        self.metrics = {
            'execution_time': 0,
            'database_queries': 0,
            'memory_usage': 0,
            'api_calls': 0,
            'errors': [],
            'warnings': [],
            'steps': [],
            'resources': {}
        }
    
    def start(self):
        """Start monitoring"""
        self.start_time = time.time()
        self.metrics['start_timestamp'] = datetime.now().isoformat()
        
        # Track initial memory usage
        if METRICS_CONFIG['track_memory_usage']:
            self.metrics['initial_memory'] = self._get_memory_usage()
        
        # Track initial database query count
        if METRICS_CONFIG['track_database_queries']:
            self.metrics['initial_queries'] = len(connection.queries)
        
        logger.info(f"Started monitoring agent: {self.agent_name} (ID: {self.execution_id})")
    
    def stop(self):
        """Stop monitoring and calculate final metrics"""
        self.end_time = time.time()
        self.metrics['end_timestamp'] = datetime.now().isoformat()
        self.metrics['execution_time'] = self.end_time - self.start_time
        
        # Calculate memory usage
        if METRICS_CONFIG['track_memory_usage']:
            final_memory = self._get_memory_usage()
            self.metrics['final_memory'] = final_memory
            self.metrics['memory_usage'] = final_memory - self.metrics.get('initial_memory', 0)
        
        # Calculate database queries
        if METRICS_CONFIG['track_database_queries']:
            final_queries = len(connection.queries)
            self.metrics['database_queries'] = final_queries - self.metrics.get('initial_queries', 0)
            
            # Log slow queries
            if METRICS_CONFIG['enable_detailed_logging']:
                self._log_slow_queries()
        
        # Check alert thresholds
        self._check_thresholds()
        
        # Store metrics
        self._store_metrics()
        
        logger.info(
            f"Stopped monitoring agent: {self.agent_name} "
            f"(Time: {self.metrics['execution_time']:.2f}s, "
            f"Queries: {self.metrics['database_queries']}, "
            f"Memory: {self.metrics['memory_usage']:.2f}MB)"
        )
    
    def log_step(self, step_name, data=None):
        """Log a step in agent execution"""
        step_info = {
            'name': step_name,
            'timestamp': datetime.now().isoformat(),
            'duration': time.time() - self.start_time if self.start_time else 0
        }
        
        if data:
            step_info['data'] = data
        
        self.metrics['steps'].append(step_info)
        
        if METRICS_CONFIG['enable_detailed_logging']:
            logger.debug(f"Agent step: {self.agent_name} - {step_name}")
    
    def log_error(self, error, context=None):
        """Log an error during execution"""
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'timestamp': datetime.now().isoformat(),
            'traceback': traceback.format_exc()
        }
        
        if context:
            error_info['context'] = context
        
        self.metrics['errors'].append(error_info)
        
        logger.error(
            f"Agent error: {self.agent_name} - {error_info['type']}: {error_info['message']}"
        )
    
    def log_warning(self, message, data=None):
        """Log a warning during execution"""
        warning_info = {
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if data:
            warning_info['data'] = data
        
        self.metrics['warnings'].append(warning_info)
        
        logger.warning(f"Agent warning: {self.agent_name} - {message}")
    
    def log_api_call(self, api_name, response_time, status_code=None):
        """Log an API call made by the agent"""
        self.metrics['api_calls'] += 1
        
        if 'api_details' not in self.metrics:
            self.metrics['api_details'] = []
        
        self.metrics['api_details'].append({
            'api': api_name,
            'response_time': response_time,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check if API response time exceeds threshold
        threshold = METRICS_CONFIG['alert_thresholds']['api_response_time']
        if response_time > threshold:
            self.log_warning(
                f"Slow API response from {api_name}: {response_time:.2f}s",
                {'threshold': threshold}
            )
    
    def _get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0
    
    def _log_slow_queries(self):
        """Log database queries that are slow"""
        if not connection.queries:
            return
        
        slow_queries = []
        for query in connection.queries[-self.metrics['database_queries']:]:
            query_time = float(query.get('time', 0))
            if query_time > 0.1:  # Queries taking more than 100ms
                slow_queries.append({
                    'sql': query['sql'][:200],  # Truncate long queries
                    'time': query_time
                })
        
        if slow_queries:
            self.metrics['slow_queries'] = slow_queries
            logger.warning(
                f"Agent {self.agent_name} executed {len(slow_queries)} slow queries"
            )
    
    def _check_thresholds(self):
        """Check if metrics exceed alert thresholds"""
        thresholds = METRICS_CONFIG['alert_thresholds']
        alerts = []
        
        if self.metrics['execution_time'] > thresholds['execution_time']:
            alerts.append(f"Execution time ({self.metrics['execution_time']:.2f}s) exceeds threshold ({thresholds['execution_time']}s)")
        
        if self.metrics['memory_usage'] > thresholds['memory_usage']:
            alerts.append(f"Memory usage ({self.metrics['memory_usage']:.2f}MB) exceeds threshold ({thresholds['memory_usage']}MB)")
        
        if self.metrics['database_queries'] > thresholds['database_queries']:
            alerts.append(f"Database queries ({self.metrics['database_queries']}) exceed threshold ({thresholds['database_queries']})")
        
        if alerts:
            self.metrics['alerts'] = alerts
            for alert in alerts:
                logger.warning(f"Performance alert for {self.agent_name}: {alert}")
    
    def _store_metrics(self):
        """Store metrics for analysis"""
        # Store in cache for real-time dashboard
        cache_key = f"agent_metrics:{self.execution_id}"
        cache.set(cache_key, self.metrics, 3600)  # Keep for 1 hour
        
        # Store summary in database (if model exists)
        try:
            from core.models.agents_registry import AgentExecution

            AgentExecution.objects.filter(id=self.execution_id).update(
                performance_metrics=self.metrics,
                execution_time=self.metrics['execution_time'],
                status='completed' if not self.metrics['errors'] else 'failed'
            )
        except ImportError as e:
            # Previously swallowed silently; AgentExecution lives in
            # core/models/agents_registry and always exists, so an
            # ImportError here means a transitive dependency failed to
            # load and that's worth knowing about.
            logger.warning(
                "agent_monitoring: AgentExecution import failed (%s: %s) — "
                "per-execution metrics will not be persisted this run",
                type(e).__name__, e,
            )
        except Exception as e:
            logger.warning(f"Failed to save execution metrics for {self.execution_id}: {e}")
    
    def get_metrics(self):
        """Get current metrics"""
        return self.metrics


def monitor_agent_execution(agent_name=None):
    """
    Decorator to monitor agent execution
    
    Usage:
        @monitor_agent_execution(agent_name="sports_analyzer")
        def execute_agent(request):
            # Agent execution code
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract execution ID if available
            execution_id = kwargs.get('execution_id') or \
                          getattr(args[0], 'execution_id', None) if args else None
            
            # Create monitor
            monitor = AgentMonitor(
                agent_name=agent_name or func.__name__,
                execution_id=execution_id
            )
            
            # Start monitoring
            monitor.start()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log successful completion
                monitor.log_step('execution_completed', {'success': True})
                
                return result
                
            except Exception as e:
                # Log error
                monitor.log_error(e)
                raise
                
            finally:
                # Stop monitoring
                monitor.stop()
        
        return wrapper
    return decorator


class PerformanceAnalyzer:
    """
    Analyze agent performance metrics
    """
    
    @staticmethod
    def get_agent_stats(agent_name, time_period=None):
        """Get performance statistics for an agent"""
        try:
            from core.models.agents_registry import AgentExecution
            from django.db.models import Avg, Count, Max, Min, Q
            
            query = AgentExecution.objects.filter(
                template__name=agent_name
            )
            
            if time_period:
                start_date = timezone.now() - time_period
                query = query.filter(created_at__gte=start_date)
            
            stats = query.aggregate(
                total_executions=Count('id'),
                avg_execution_time=Avg('execution_time_seconds'),
                max_execution_time=Max('execution_time_seconds'),
                min_execution_time=Min('execution_time_seconds'),
                success_count=Count('id', filter=Q(status='completed')),
                failure_count=Count('id', filter=Q(status='failed'))
            )
            
            # Calculate success rate
            total = stats['total_executions']
            if total > 0:
                stats['success_rate'] = stats['success_count'] / total
                stats['failure_rate'] = stats['failure_count'] / total
            else:
                stats['success_rate'] = 0
                stats['failure_rate'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting agent stats: {e}")
            return {}
    
    @staticmethod
    def get_system_metrics():
        """Get overall system performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'agents': {},
            'system': {}
        }
        
        # Get metrics for each agent type
        try:
            from core.models.agents_registry import UnifiedAgentTemplate

            for template in UnifiedAgentTemplate.objects.filter(is_active=True):
                agent_stats = PerformanceAnalyzer.get_agent_stats(
                    template.name,
                    time_period=timedelta(hours=24)
                )
                metrics['agents'][template.name] = agent_stats
        except ImportError as e:
            # Previously swallowed silently. System-wide agent metrics
            # collection vanishes on any transitive import failure, which
            # left /api/monitoring/agents/ showing stale data with no
            # visible cause.
            logger.warning(
                "agent_monitoring.get_system_metrics: UnifiedAgentTemplate "
                "import failed (%s: %s) — agent metrics section will be empty",
                type(e).__name__, e,
            )
        except Exception as e:
            logger.warning(f"Failed to collect agent metrics: {e}")
        
        # Get system metrics
        try:
            import psutil

            # Calculate uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            if days > 0:
                uptime_str = f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = f"{minutes}m"

            metrics['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'uptime': uptime_str,
                'uptime_seconds': uptime_seconds
            }
        except Exception as e:
            logger.warning(f"Could not get system metrics: {e}")

        # Get cache statistics from Redis
        try:
            import redis
            redis_conn = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
            info = redis_conn.info()

            # Calculate hit rate
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0

            metrics['cache'] = {
                'hit_rate': round(hit_rate, 1),
                'hits': hits,
                'misses': misses,
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_keys': redis_conn.dbsize()
            }
        except Exception as e:
            logger.warning(f"Could not get cache stats: {e}")
            metrics['cache'] = {'hit_rate': 0, 'hits': 0, 'misses': 0}

        return metrics
    
    @staticmethod
    def generate_performance_report(time_period=None):
        """Generate a comprehensive performance report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'period': str(time_period) if time_period else 'all_time',
            'summary': {},
            'details': {},
            'recommendations': []
        }
        
        # Get metrics for all agents
        try:
            from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution

            # Overall statistics
            total_executions = AgentExecution.objects.count()
            successful_executions = AgentExecution.objects.filter(
                status='completed'
            ).count()

            report['summary'] = {
                'total_executions': total_executions,
                'successful_executions': successful_executions,
                'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
                'total_agents': UnifiedAgentTemplate.objects.filter(is_active=True).count()
            }
            
            # Per-agent details
            for template in UnifiedAgentTemplate.objects.filter(is_active=True):
                stats = PerformanceAnalyzer.get_agent_stats(
                    template.name,
                    time_period
                )
                report['details'][template.name] = stats
                
                # Generate recommendations
                avg_exec_time = stats.get('avg_execution_time') or 0
                failure_rate = stats.get('failure_rate') or 0

                if avg_exec_time > 30:
                    report['recommendations'].append(
                        f"Agent '{template.name}' has high average execution time "
                        f"({avg_exec_time:.2f}s). Consider optimization."
                    )

                if failure_rate > 0.1:
                    report['recommendations'].append(
                        f"Agent '{template.name}' has high failure rate "
                        f"({failure_rate:.1%}). Investigate errors."
                    )
        
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
        
        return report


# Monitoring utilities
def log_agent_metric(agent_name, metric_name, value):
    """Log a custom metric for an agent"""
    cache_key = f"agent_metric:{agent_name}:{metric_name}"
    
    # Store in cache with timestamp
    metric_data = {
        'value': value,
        'timestamp': datetime.now().isoformat()
    }
    
    # Append to metrics list (keep last 100)
    metrics_list = cache.get(cache_key, [])
    metrics_list.append(metric_data)
    metrics_list = metrics_list[-100:]  # Keep only last 100
    
    cache.set(cache_key, metrics_list, 86400)  # Keep for 24 hours
    
    logger.debug(f"Logged metric for {agent_name}: {metric_name}={value}")


def get_agent_metrics_summary():
    """Get summary of all agent metrics"""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'active_agents': 0,
        'total_executions_24h': 0,
        'average_execution_time': 0,
        'error_rate': 0,
        'top_performers': [],
        'needs_attention': []
    }
    
    try:
        from core.models.agents_registry import AgentExecution
        from django.db.models import Avg, Count
        
        # Get 24-hour statistics
        since = timezone.now() - timedelta(hours=24)
        recent_executions = AgentExecution.objects.filter(
            created_at__gte=since
        )

        summary['total_executions_24h'] = recent_executions.count()

        # Count active/running agents
        active_count = AgentExecution.objects.filter(
            status__in=['running', 'in_progress', 'pending']
        ).count()
        summary['active_agents'] = active_count

        # Calculate averages
        stats = recent_executions.aggregate(
            avg_time=Avg('execution_time_seconds'),
            error_count=Count('id', filter=models.Q(status='failed'))
        )

        summary['average_execution_time'] = stats['avg_time'] or 0

        if summary['total_executions_24h'] > 0:
            summary['error_rate'] = stats['error_count'] / summary['total_executions_24h']

        # Identify top performers and problematic agents
        agent_stats = recent_executions.values('template__name').annotate(
            avg_time=Avg('execution_time_seconds'),
            count=Count('id'),
            errors=Count('id', filter=models.Q(status='failed'))
        ).order_by('avg_time')
        
        # Top 3 fastest agents
        summary['top_performers'] = list(agent_stats[:3])
        
        # Agents with high error rates
        for stat in agent_stats:
            if stat['count'] > 0:
                error_rate = stat['errors'] / stat['count']
                if error_rate > 0.1:  # More than 10% error rate
                    summary['needs_attention'].append({
                        'agent': stat['template__name'],
                        'error_rate': error_rate,
                        'total_errors': stat['errors']
                    })
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
    
    return summary
