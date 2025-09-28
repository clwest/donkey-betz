"""
Performance Metrics Tracker
Phase 4: Scale & Optimize - Track Everything

This module monitors and tracks all performance metrics for the spider army,
providing real-time insights into system health and optimization opportunities.
"""

import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Deque
from datetime import datetime, timedelta
from collections import defaultdict, deque, Counter
from dataclasses import dataclass, field
import statistics
import json
from django.core.cache import cache
import psutil
import threading

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Point-in-time metric snapshot"""
    timestamp: datetime
    metric_name: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceWindow:
    """Rolling window for performance calculations"""
    name: str
    window_size: int  # seconds
    data_points: Deque[MetricSnapshot] = field(default_factory=lambda: deque(maxlen=1000))

    def add_point(self, value: float, tags: Dict = None):
        """Add a data point to the window"""
        snapshot = MetricSnapshot(
            timestamp=datetime.now(),
            metric_name=self.name,
            value=value,
            tags=tags or {}
        )
        self.data_points.append(snapshot)

    def get_stats(self) -> Dict:
        """Get statistics for the window"""
        if not self.data_points:
            return {}

        values = [p.value for p in self.data_points]
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'std_dev': statistics.stdev(values) if len(values) > 1 else 0
        }


class PerformanceMetricsTracker:
    """
    Comprehensive performance tracking for the spider ecosystem.
    Monitors requests, data collection, API usage, and system health.
    """

    def __init__(self):
        # Core metrics
        self.metrics = {
            'requests_per_second': Counter(),
            'data_points_collected': Counter(),
            'unique_opportunities': set(),
            'api_quota_remaining': defaultdict(int),
            'spider_health_scores': defaultdict(float),
            'error_counts': Counter(),
            'success_counts': Counter()
        }

        # Time-series data with rolling windows
        self.time_windows = {
            'rps_1min': PerformanceWindow('requests_per_second', 60),
            'rps_5min': PerformanceWindow('requests_per_second', 300),
            'rps_1hour': PerformanceWindow('requests_per_second', 3600),
            'data_rate_1min': PerformanceWindow('data_collection_rate', 60),
            'error_rate_1min': PerformanceWindow('error_rate', 60),
            'latency_1min': PerformanceWindow('latency_ms', 60)
        }

        # Performance tracking
        self.request_timings = deque(maxlen=10000)
        self.api_call_timings = defaultdict(deque)
        self.spider_performance = defaultdict(lambda: {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_data_collected': 0,
            'avg_response_time': 0,
            'last_active': None
        })

        # System metrics
        self.system_metrics = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'network_io': {'sent': 0, 'received': 0},
            'active_threads': 0
        }

        # API quota tracking
        self.api_quotas = {
            'newsapi': {'limit': 1000, 'used': 0, 'reset_time': None},
            'reddit': {'limit': 60, 'used': 0, 'reset_time': None},
            'github': {'limit': 5000, 'used': 0, 'reset_time': None},
            'coingecko': {'limit': 50, 'used': 0, 'reset_time': None},
            'remoteok': {'limit': 100, 'used': 0, 'reset_time': None}
        }

        # Alerts and thresholds
        self.alert_thresholds = {
            'error_rate': 0.1,  # 10% error rate
            'api_quota': 0.9,   # 90% of quota used
            'latency_ms': 5000, # 5 second latency
            'cpu_usage': 80,    # 80% CPU
            'memory_usage': 80  # 80% memory
        }

        self.active_alerts = []

        # Start monitoring
        self._start_monitoring()

        logger.info("📊 Performance metrics tracker initialized")

    def _start_monitoring(self):
        """Start background monitoring tasks"""
        # Start system metrics collection in background thread
        threading.Thread(target=self._collect_system_metrics, daemon=True).start()

    def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while True:
            try:
                # CPU usage
                self.system_metrics['cpu_usage'] = psutil.cpu_percent(interval=1)

                # Memory usage
                memory = psutil.virtual_memory()
                self.system_metrics['memory_usage'] = memory.percent

                # Disk usage
                disk = psutil.disk_usage('/')
                self.system_metrics['disk_usage'] = disk.percent

                # Network I/O
                net_io = psutil.net_io_counters()
                self.system_metrics['network_io'] = {
                    'sent': net_io.bytes_sent,
                    'received': net_io.bytes_recv
                }

                # Active threads
                self.system_metrics['active_threads'] = threading.active_count()

                # Check for alerts
                self._check_alerts()

                time.sleep(10)  # Update every 10 seconds

            except Exception as e:
                logger.error(f"❌ Error collecting system metrics: {e}")
                time.sleep(30)

    def record_request(self, spider_id: str, success: bool, response_time_ms: float,
                      data_collected: int = 0):
        """
        Record a spider request

        Args:
            spider_id: ID of the spider
            success: Whether request was successful
            response_time_ms: Response time in milliseconds
            data_collected: Number of data points collected
        """
        timestamp = datetime.now()

        # Update counters
        self.metrics['requests_per_second'][timestamp.second] += 1

        if success:
            self.metrics['success_counts'][spider_id] += 1
            self.spider_performance[spider_id]['successful_requests'] += 1
        else:
            self.metrics['error_counts'][spider_id] += 1
            self.spider_performance[spider_id]['failed_requests'] += 1

        # Update spider performance
        perf = self.spider_performance[spider_id]
        perf['total_requests'] += 1
        perf['total_data_collected'] += data_collected
        perf['last_active'] = timestamp

        # Update average response time
        current_avg = perf['avg_response_time']
        total_requests = perf['total_requests']
        perf['avg_response_time'] = ((current_avg * (total_requests - 1)) + response_time_ms) / total_requests

        # Record timing
        self.request_timings.append({
            'spider_id': spider_id,
            'timestamp': timestamp,
            'response_time': response_time_ms,
            'success': success
        })

        # Update time windows
        self.time_windows['rps_1min'].add_point(1)
        self.time_windows['rps_5min'].add_point(1)
        self.time_windows['rps_1hour'].add_point(1)
        self.time_windows['latency_1min'].add_point(response_time_ms)

        if not success:
            self.time_windows['error_rate_1min'].add_point(1)

        # Log if response time is high
        if response_time_ms > self.alert_thresholds['latency_ms']:
            logger.warning(f"⚠️ High latency: {spider_id} took {response_time_ms}ms")

    def record_data_collection(self, spider_id: str, data_type: str, count: int,
                              unique_items: List[str] = None):
        """
        Record data collection metrics

        Args:
            spider_id: ID of the spider
            data_type: Type of data collected
            count: Number of items collected
            unique_items: List of unique item IDs
        """
        self.metrics['data_points_collected'][data_type] += count

        if unique_items:
            self.metrics['unique_opportunities'].update(unique_items)

        self.time_windows['data_rate_1min'].add_point(count)

        logger.debug(f"📊 {spider_id} collected {count} {data_type} items")

    def record_api_call(self, api_name: str, success: bool, quota_used: int = 1,
                       response_time_ms: float = 0):
        """
        Record API call metrics

        Args:
            api_name: Name of the API
            success: Whether call was successful
            quota_used: Quota units consumed
            response_time_ms: Response time
        """
        if api_name in self.api_quotas:
            self.api_quotas[api_name]['used'] += quota_used

            # Check quota threshold
            quota_info = self.api_quotas[api_name]
            usage_ratio = quota_info['used'] / quota_info['limit']

            if usage_ratio > self.alert_thresholds['api_quota']:
                self._trigger_alert('api_quota', f"{api_name} quota at {usage_ratio:.1%}")

            self.metrics['api_quota_remaining'][api_name] = \
                quota_info['limit'] - quota_info['used']

        # Record timing
        if api_name not in self.api_call_timings:
            self.api_call_timings[api_name] = deque(maxlen=1000)

        self.api_call_timings[api_name].append({
            'timestamp': datetime.now(),
            'success': success,
            'response_time': response_time_ms
        })

    def update_spider_health(self, spider_id: str, health_score: float):
        """
        Update spider health score

        Args:
            spider_id: ID of the spider
            health_score: Health score (0.0 to 1.0)
        """
        self.metrics['spider_health_scores'][spider_id] = health_score

        # Alert if health is poor
        if health_score < 0.3:
            self._trigger_alert('spider_health', f"Spider {spider_id} health: {health_score:.2f}")

    def _check_alerts(self):
        """Check for alert conditions"""
        # CPU usage alert
        if self.system_metrics['cpu_usage'] > self.alert_thresholds['cpu_usage']:
            self._trigger_alert('cpu_usage', f"CPU at {self.system_metrics['cpu_usage']}%")

        # Memory usage alert
        if self.system_metrics['memory_usage'] > self.alert_thresholds['memory_usage']:
            self._trigger_alert('memory_usage', f"Memory at {self.system_metrics['memory_usage']}%")

        # Error rate alert
        error_stats = self.time_windows['error_rate_1min'].get_stats()
        if error_stats and error_stats.get('mean', 0) > self.alert_thresholds['error_rate']:
            self._trigger_alert('error_rate', f"Error rate: {error_stats['mean']:.2f}/min")

    def _trigger_alert(self, alert_type: str, message: str):
        """Trigger an alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': 'high' if alert_type in ['cpu_usage', 'memory_usage'] else 'medium'
        }

        self.active_alerts.append(alert)

        # Keep only recent alerts
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.active_alerts = [
            a for a in self.active_alerts
            if datetime.fromisoformat(a['timestamp']) > cutoff_time
        ]

        logger.warning(f"🚨 Alert: {message}")

        # Cache alert for dashboard
        cache.set(f"alert_{alert_type}", alert, 3600)

    def get_current_metrics(self) -> Dict:
        """Get current performance metrics"""
        # Calculate RPS
        rps_stats = self.time_windows['rps_1min'].get_stats()
        current_rps = rps_stats.get('mean', 0) if rps_stats else 0

        # Calculate error rate
        total_recent = sum(self.metrics['success_counts'].values())
        total_errors = sum(self.metrics['error_counts'].values())
        error_rate = (total_errors / max(total_recent + total_errors, 1)) * 100

        # Get latency stats
        latency_stats = self.time_windows['latency_1min'].get_stats()

        return {
            'requests_per_second': current_rps,
            'total_requests': sum(p['total_requests'] for p in self.spider_performance.values()),
            'data_points_collected': sum(self.metrics['data_points_collected'].values()),
            'unique_opportunities': len(self.metrics['unique_opportunities']),
            'error_rate_percent': error_rate,
            'avg_latency_ms': latency_stats.get('mean', 0) if latency_stats else 0,
            'active_spiders': len([s for s, p in self.spider_performance.items()
                                 if p['last_active'] and
                                 (datetime.now() - p['last_active']).seconds < 60]),
            'system_metrics': self.system_metrics,
            'api_quotas': self.api_quotas,
            'active_alerts': self.active_alerts[-10:]  # Last 10 alerts
        }

    def get_spider_rankings(self, limit: int = 10) -> List[Dict]:
        """Get top performing spiders"""
        rankings = []

        for spider_id, perf in self.spider_performance.items():
            if perf['total_requests'] == 0:
                continue

            success_rate = perf['successful_requests'] / perf['total_requests']
            efficiency = perf['total_data_collected'] / max(perf['total_requests'], 1)

            rankings.append({
                'spider_id': spider_id,
                'success_rate': success_rate,
                'efficiency': efficiency,
                'total_data': perf['total_data_collected'],
                'avg_response_time': perf['avg_response_time'],
                'score': success_rate * efficiency * 100  # Combined score
            })

        # Sort by score
        rankings.sort(key=lambda x: x['score'], reverse=True)

        return rankings[:limit]

    def get_time_series_data(self, metric: str, window: str = '1min') -> List[Dict]:
        """Get time series data for a metric"""
        window_key = f"{metric}_{window}"

        if window_key not in self.time_windows:
            return []

        window_data = self.time_windows[window_key]
        return [
            {
                'timestamp': point.timestamp.isoformat(),
                'value': point.value
            }
            for point in window_data.data_points
        ]

    def get_api_usage_summary(self) -> Dict:
        """Get API usage summary"""
        summary = {}

        for api_name, quota_info in self.api_quotas.items():
            usage_percent = (quota_info['used'] / quota_info['limit']) * 100 if quota_info['limit'] else 0

            # Get average response time
            if api_name in self.api_call_timings and self.api_call_timings[api_name]:
                timings = [t['response_time'] for t in self.api_call_timings[api_name]]
                avg_response = statistics.mean(timings)
            else:
                avg_response = 0

            summary[api_name] = {
                'used': quota_info['used'],
                'limit': quota_info['limit'],
                'remaining': quota_info['limit'] - quota_info['used'],
                'usage_percent': usage_percent,
                'avg_response_time_ms': avg_response,
                'reset_time': quota_info.get('reset_time')
            }

        return summary

    def reset_api_quotas(self):
        """Reset API quotas (called daily or as needed)"""
        for api_name in self.api_quotas:
            self.api_quotas[api_name]['used'] = 0
            self.api_quotas[api_name]['reset_time'] = datetime.now() + timedelta(days=1)

        logger.info("🔄 API quotas reset")

    def export_metrics(self) -> Dict:
        """Export all metrics for analysis or storage"""
        return {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': self.get_current_metrics(),
            'spider_rankings': self.get_spider_rankings(),
            'api_usage': self.get_api_usage_summary(),
            'time_series': {
                'rps_1min': self.get_time_series_data('rps', '1min'),
                'latency_1min': self.get_time_series_data('latency', '1min'),
                'error_rate_1min': self.get_time_series_data('error_rate', '1min')
            },
            'alerts': self.active_alerts
        }

    def clear_old_data(self, hours: int = 24):
        """Clear data older than specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)

        # Clear old request timings
        self.request_timings = deque(
            [t for t in self.request_timings if t['timestamp'] > cutoff],
            maxlen=10000
        )

        # Clear old API timings
        for api_name in self.api_call_timings:
            self.api_call_timings[api_name] = deque(
                [t for t in self.api_call_timings[api_name] if t['timestamp'] > cutoff],
                maxlen=1000
            )

        logger.info(f"🧹 Cleared metrics data older than {hours} hours")


# Singleton instance
metrics_tracker = PerformanceMetricsTracker()


# Public API functions
def record_spider_request(spider_id: str, success: bool, response_time_ms: float,
                         data_collected: int = 0):
    """Record a spider request"""
    metrics_tracker.record_request(spider_id, success, response_time_ms, data_collected)


def record_data_collection(spider_id: str, data_type: str, count: int,
                          unique_items: List[str] = None):
    """Record data collection"""
    metrics_tracker.record_data_collection(spider_id, data_type, count, unique_items)


def record_api_call(api_name: str, success: bool, quota_used: int = 1,
                   response_time_ms: float = 0):
    """Record API call"""
    metrics_tracker.record_api_call(api_name, success, quota_used, response_time_ms)


def update_spider_health(spider_id: str, health_score: float):
    """Update spider health score"""
    metrics_tracker.update_spider_health(spider_id, health_score)


def get_performance_metrics() -> Dict:
    """Get current performance metrics"""
    return metrics_tracker.get_current_metrics()


def get_spider_leaderboard() -> List[Dict]:
    """Get spider performance leaderboard"""
    return metrics_tracker.get_spider_rankings()


def export_all_metrics() -> Dict:
    """Export all metrics"""
    return metrics_tracker.export_metrics()