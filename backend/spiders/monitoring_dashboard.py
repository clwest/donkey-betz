"""
Spider-Agent-Connector Monitoring Dashboard
===========================================

Real-time monitoring dashboard for visualizing data flow between 1,770+ spiders,
102 agents, and 25+ advisors. Provides comprehensive metrics, health monitoring,
and performance analytics for the entire intelligence network.

Features:
- Real-time data flow visualization
- Spider army performance monitoring
- Agent/advisor connection status
- Network health metrics
- Performance analytics and alerts
- Interactive web dashboard
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
import redis
from redis import asyncio as aioredis
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time

logger = logging.getLogger(__name__)


@dataclass
class NetworkMetrics:
    """Comprehensive network metrics"""
    timestamp: datetime
    spider_metrics: Dict[str, Any]
    agent_metrics: Dict[str, Any]
    advisor_metrics: Dict[str, Any]
    routing_metrics: Dict[str, Any]
    pipeline_metrics: Dict[str, Any]
    connection_health: float
    total_data_flow: int
    error_rate: float


@dataclass
class ConnectionStatus:
    """Connection status between spider and consumer"""
    spider_id: str
    consumer_id: str
    consumer_type: str
    status: str
    last_message_time: Optional[datetime]
    message_count: int
    error_count: int
    latency_ms: float


class SpiderNetworkMonitor:
    """
    Real-time monitor for the spider-agent network.

    Collects metrics, analyzes performance, and provides
    health monitoring for the entire intelligence ecosystem.
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        self.redis_config = redis_config or {'host': 'localhost', 'port': 6379, 'db': 0}
        self.redis_client = redis.Redis(**self.redis_config)
        self.redis_async = None

        # Monitoring data
        self.current_metrics = None
        self.metrics_history: List[NetworkMetrics] = []
        self.connection_status: Dict[str, ConnectionStatus] = {}
        self.alerts: List[Dict[str, Any]] = []

        # Configuration
        self.metrics_interval = 30  # seconds
        self.history_retention_hours = 24
        self.alert_thresholds = {
            'error_rate': 0.1,
            'connection_health': 80.0,
            'response_time_ms': 5000
        }

        self.logger = logging.getLogger(__name__)
        self.is_running = False

    async def start_monitoring(self):
        """Start the network monitoring system"""
        try:
            self.logger.info("🖥️  Starting Spider Network Monitoring...")

            # Initialize async Redis connection
            self.redis_async = aioredis.from_url(
                f"redis://{self.redis_config['host']}:{self.redis_config['port']}/{self.redis_config['db']}"
            )

            self.is_running = True

            # Start monitoring tasks
            monitoring_tasks = [
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._connection_monitor()),
                asyncio.create_task(self._health_analyzer()),
                asyncio.create_task(self._alert_manager())
            ]

            self.logger.info("✅ Network monitoring started successfully")

            # Wait for all monitoring tasks
            await asyncio.gather(*monitoring_tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            raise

    async def _metrics_collector(self):
        """Collect comprehensive network metrics"""
        while self.is_running:
            try:
                await asyncio.sleep(self.metrics_interval)

                # Collect metrics from all components
                spider_metrics = await self._collect_spider_metrics()
                agent_metrics = await self._collect_agent_metrics()
                advisor_metrics = await self._collect_advisor_metrics()
                routing_metrics = await self._collect_routing_metrics()
                pipeline_metrics = await self._collect_pipeline_metrics()

                # Calculate overall health
                connection_health = await self._calculate_connection_health()
                total_data_flow = sum([
                    spider_metrics.get('total_data_points', 0),
                    routing_metrics.get('messages_routed', 0)
                ])
                error_rate = await self._calculate_error_rate()

                # Create metrics snapshot
                metrics = NetworkMetrics(
                    timestamp=datetime.now(timezone.utc),
                    spider_metrics=spider_metrics,
                    agent_metrics=agent_metrics,
                    advisor_metrics=advisor_metrics,
                    routing_metrics=routing_metrics,
                    pipeline_metrics=pipeline_metrics,
                    connection_health=connection_health,
                    total_data_flow=total_data_flow,
                    error_rate=error_rate
                )

                # Store current metrics
                self.current_metrics = metrics
                self.metrics_history.append(metrics)

                # Cleanup old metrics
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.history_retention_hours)
                self.metrics_history = [
                    m for m in self.metrics_history
                    if m.timestamp >= cutoff_time
                ]

                # Store in Redis for other components
                await self._store_metrics_in_redis(metrics)

            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")

    async def _collect_spider_metrics(self) -> Dict[str, Any]:
        """Collect spider army metrics"""
        try:
            # Get spider army status from Redis
            army_status_data = await self.redis_async.get('spider_army:status')
            if army_status_data:
                army_status = json.loads(army_status_data)
                return {
                    'total_spiders': army_status.get('total_spiders', 0),
                    'active_spiders': army_status.get('active_spiders', 0),
                    'total_data_points': army_status.get('total_data_points', 0),
                    'avg_quality_score': army_status.get('avg_quality_score', 0.0),
                    'swarm_distribution': army_status.get('swarm_distribution', {}),
                    'top_producers': army_status.get('top_performing_spiders', [])[:5]
                }
        except Exception as e:
            self.logger.error(f"Error collecting spider metrics: {e}")

        return {
            'total_spiders': 0,
            'active_spiders': 0,
            'total_data_points': 0,
            'avg_quality_score': 0.0,
            'swarm_distribution': {},
            'top_producers': []
        }

    async def _collect_agent_metrics(self) -> Dict[str, Any]:
        """Collect agent metrics"""
        try:
            agent_metrics = {
                'total_agents': 0,
                'active_agents': 0,
                'total_processed': 0,
                'avg_processing_time': 0.0,
                'top_performers': []
            }

            # Get metrics for all agents
            agent_keys = await self.redis_async.keys('agent_metrics:*')
            active_agents = 0
            total_processed = 0
            total_processing_time = 0
            agent_performance = []

            for key in agent_keys:
                try:
                    metrics_data = await self.redis_async.get(key)
                    if metrics_data:
                        metrics = json.loads(metrics_data)
                        agent_id = metrics.get('agent_id', '')

                        if metrics.get('total_processed', 0) > 0:
                            active_agents += 1
                            processed = metrics.get('total_processed', 0)
                            total_processed += processed
                            total_processing_time += metrics.get('avg_processing_time_ms', 0)

                            agent_performance.append((agent_id, processed))

                except Exception as e:
                    self.logger.warning(f"Error processing agent metrics for {key}: {e}")

            agent_metrics.update({
                'total_agents': len(agent_keys),
                'active_agents': active_agents,
                'total_processed': total_processed,
                'avg_processing_time': total_processing_time / max(active_agents, 1),
                'top_performers': sorted(agent_performance, key=lambda x: x[1], reverse=True)[:5]
            })

            return agent_metrics

        except Exception as e:
            self.logger.error(f"Error collecting agent metrics: {e}")
            return {
                'total_agents': 0,
                'active_agents': 0,
                'total_processed': 0,
                'avg_processing_time': 0.0,
                'top_performers': []
            }

    async def _collect_advisor_metrics(self) -> Dict[str, Any]:
        """Collect advisor metrics"""
        try:
            advisor_metrics = {
                'total_advisors': 0,
                'active_advisors': 0,
                'total_insights': 0,
                'total_recommendations': 0,
                'avg_confidence': 0.0
            }

            # Get advisor analysis keys
            advisor_keys = await self.redis_async.keys('advisor_analysis:*')
            active_advisors = set()
            total_insights = 0
            total_recommendations = 0
            confidence_scores = []

            for key in advisor_keys:
                try:
                    analysis_data = await self.redis_async.get(key)
                    if analysis_data:
                        analysis = json.loads(analysis_data)
                        advisor_id = analysis.get('advisor_id', '')
                        active_advisors.add(advisor_id)

                        insights = analysis.get('insights', [])
                        recommendations = analysis.get('recommendations', [])

                        total_insights += len(insights)
                        total_recommendations += len(recommendations)

                        # Collect confidence scores
                        for insight in insights:
                            if 'confidence_level' in insight:
                                confidence_scores.append(insight['confidence_level'])

                except Exception as e:
                    self.logger.warning(f"Error processing advisor analysis for {key}: {e}")

            avg_confidence = sum(confidence_scores) / max(len(confidence_scores), 1)

            advisor_metrics.update({
                'total_advisors': 25,  # Known number of advisors
                'active_advisors': len(active_advisors),
                'total_insights': total_insights,
                'total_recommendations': total_recommendations,
                'avg_confidence': avg_confidence
            })

            return advisor_metrics

        except Exception as e:
            self.logger.error(f"Error collecting advisor metrics: {e}")
            return {
                'total_advisors': 25,
                'active_advisors': 0,
                'total_insights': 0,
                'total_recommendations': 0,
                'avg_confidence': 0.0
            }

    async def _collect_routing_metrics(self) -> Dict[str, Any]:
        """Collect routing metrics"""
        try:
            router_metrics_data = await self.redis_async.get('spider_router:metrics')
            if router_metrics_data:
                return json.loads(router_metrics_data)
        except Exception as e:
            self.logger.error(f"Error collecting routing metrics: {e}")

        return {
            'total_connections': 0,
            'active_connections': 0,
            'messages_routed': 0,
            'failed_routes': 0,
            'connection_health': 0.0
        }

    async def _collect_pipeline_metrics(self) -> Dict[str, Any]:
        """Collect pipeline metrics"""
        try:
            pipeline_metrics_data = await self.redis_async.get('pipeline:metrics')
            if pipeline_metrics_data:
                return json.loads(pipeline_metrics_data)
        except Exception as e:
            self.logger.error(f"Error collecting pipeline metrics: {e}")

        return {
            'messages_processed': 0,
            'messages_filtered': 0,
            'throughput_per_second': 0.0,
            'avg_latency_ms': 0.0,
            'active_channels': 0
        }

    async def _calculate_connection_health(self) -> float:
        """Calculate overall connection health percentage"""
        try:
            router_metrics = await self._collect_routing_metrics()
            total_connections = router_metrics.get('total_connections', 0)
            active_connections = router_metrics.get('active_connections', 0)

            if total_connections == 0:
                return 100.0

            return (active_connections / total_connections) * 100.0

        except Exception as e:
            self.logger.error(f"Error calculating connection health: {e}")
            return 0.0

    async def _calculate_error_rate(self) -> float:
        """Calculate overall error rate"""
        try:
            routing_metrics = await self._collect_routing_metrics()
            pipeline_metrics = await self._collect_pipeline_metrics()

            total_messages = (
                routing_metrics.get('messages_routed', 0) +
                pipeline_metrics.get('messages_processed', 0)
            )
            total_errors = (
                routing_metrics.get('failed_routes', 0) +
                pipeline_metrics.get('messages_failed', 0)
            )

            if total_messages == 0:
                return 0.0

            return (total_errors / total_messages) * 100.0

        except Exception as e:
            self.logger.error(f"Error calculating error rate: {e}")
            return 0.0

    async def _store_metrics_in_redis(self, metrics: NetworkMetrics):
        """Store metrics in Redis for other components"""
        try:
            metrics_data = {
                'timestamp': metrics.timestamp.isoformat(),
                'spider_metrics': metrics.spider_metrics,
                'agent_metrics': metrics.agent_metrics,
                'advisor_metrics': metrics.advisor_metrics,
                'routing_metrics': metrics.routing_metrics,
                'pipeline_metrics': metrics.pipeline_metrics,
                'connection_health': metrics.connection_health,
                'total_data_flow': metrics.total_data_flow,
                'error_rate': metrics.error_rate
            }

            await self.redis_async.setex(
                'network_monitoring:current_metrics',
                300,  # 5 minute expiry
                json.dumps(metrics_data)
            )

        except Exception as e:
            self.logger.error(f"Error storing metrics in Redis: {e}")

    async def _connection_monitor(self):
        """Monitor individual connections"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Monitor connections would go here
                # This would track individual spider-to-consumer connections

            except Exception as e:
                self.logger.error(f"Error in connection monitor: {e}")

    async def _health_analyzer(self):
        """Analyze system health and detect issues"""
        while self.is_running:
            try:
                await asyncio.sleep(120)  # Analyze every 2 minutes

                if self.current_metrics:
                    # Check for health issues
                    health_issues = []

                    # Connection health check
                    if self.current_metrics.connection_health < self.alert_thresholds['connection_health']:
                        health_issues.append({
                            'type': 'connection_health',
                            'severity': 'warning',
                            'message': f"Connection health below threshold: {self.current_metrics.connection_health:.1f}%"
                        })

                    # Error rate check
                    if self.current_metrics.error_rate > self.alert_thresholds['error_rate']:
                        health_issues.append({
                            'type': 'error_rate',
                            'severity': 'critical',
                            'message': f"High error rate detected: {self.current_metrics.error_rate:.2f}%"
                        })

                    # Store health issues
                    for issue in health_issues:
                        await self._create_alert(issue)

            except Exception as e:
                self.logger.error(f"Error in health analyzer: {e}")

    async def _alert_manager(self):
        """Manage alerts and notifications"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                # Clean up old alerts
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                self.alerts = [
                    alert for alert in self.alerts
                    if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
                ]

            except Exception as e:
                self.logger.error(f"Error in alert manager: {e}")

    async def _create_alert(self, issue: Dict[str, Any]):
        """Create a new alert"""
        alert = {
            'id': f"alert_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': issue['type'],
            'severity': issue['severity'],
            'message': issue['message'],
            'acknowledged': False
        }

        self.alerts.append(alert)

        # Store in Redis for other components
        await self.redis_async.lpush(
            'network_alerts',
            json.dumps(alert)
        )
        await self.redis_async.ltrim('network_alerts', 0, 99)  # Keep last 100 alerts

    def get_current_metrics(self) -> Optional[NetworkMetrics]:
        """Get current network metrics"""
        return self.current_metrics

    def get_metrics_history(self, hours: int = 1) -> List[NetworkMetrics]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]

    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return sorted(
            self.alerts,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]

    async def shutdown(self):
        """Shutdown the monitor"""
        self.is_running = False
        if self.redis_async:
            await self.redis_async.close()


class MonitoringDashboard:
    """
    Web-based monitoring dashboard for the spider network.

    Provides real-time visualization of the entire intelligence ecosystem.
    """

    def __init__(self, monitor: SpiderNetworkMonitor, host='0.0.0.0', port=5001):
        self.monitor = monitor
        self.host = host
        self.port = port

        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'spider_monitoring_secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Setup routes
        self._setup_routes()
        self._setup_socketio_events()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('spider_monitoring_dashboard.html')

        @self.app.route('/api/metrics/current')
        def get_current_metrics():
            """Get current metrics"""
            metrics = self.monitor.get_current_metrics()
            if metrics:
                return jsonify({
                    'timestamp': metrics.timestamp.isoformat(),
                    'spider_metrics': metrics.spider_metrics,
                    'agent_metrics': metrics.agent_metrics,
                    'advisor_metrics': metrics.advisor_metrics,
                    'routing_metrics': metrics.routing_metrics,
                    'pipeline_metrics': metrics.pipeline_metrics,
                    'connection_health': metrics.connection_health,
                    'total_data_flow': metrics.total_data_flow,
                    'error_rate': metrics.error_rate
                })
            else:
                return jsonify({'error': 'No metrics available'})

        @self.app.route('/api/metrics/history')
        def get_metrics_history():
            """Get metrics history"""
            hours = request.args.get('hours', 1, type=int)
            history = self.monitor.get_metrics_history(hours)

            return jsonify([
                {
                    'timestamp': m.timestamp.isoformat(),
                    'connection_health': m.connection_health,
                    'total_data_flow': m.total_data_flow,
                    'error_rate': m.error_rate,
                    'active_spiders': m.spider_metrics.get('active_spiders', 0),
                    'active_agents': m.agent_metrics.get('active_agents', 0),
                    'active_advisors': m.advisor_metrics.get('active_advisors', 0)
                }
                for m in history
            ])

        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            limit = request.args.get('limit', 50, type=int)
            alerts = self.monitor.get_alerts(limit)
            return jsonify(alerts)

    def _setup_socketio_events(self):
        """Setup SocketIO events for real-time updates"""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info("Dashboard client connected")
            emit('connected', {'message': 'Connected to monitoring dashboard'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info("Dashboard client disconnected")

        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle real-time update request"""
            metrics = self.monitor.get_current_metrics()
            if metrics:
                self.socketio.emit('metrics_update', {
                    'timestamp': metrics.timestamp.isoformat(),
                    'connection_health': metrics.connection_health,
                    'total_data_flow': metrics.total_data_flow,
                    'error_rate': metrics.error_rate,
                    'spider_metrics': metrics.spider_metrics,
                    'agent_metrics': metrics.agent_metrics,
                    'advisor_metrics': metrics.advisor_metrics
                })

    def start_real_time_updates(self):
        """Start real-time updates to connected clients"""
        def update_loop():
            while True:
                time.sleep(30)  # Update every 30 seconds
                metrics = self.monitor.get_current_metrics()
                if metrics:
                    self.socketio.emit('metrics_update', {
                        'timestamp': metrics.timestamp.isoformat(),
                        'connection_health': metrics.connection_health,
                        'total_data_flow': metrics.total_data_flow,
                        'error_rate': metrics.error_rate,
                        'spider_metrics': metrics.spider_metrics,
                        'agent_metrics': metrics.agent_metrics,
                        'advisor_metrics': metrics.advisor_metrics
                    })

        # Start update thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

    def run(self, debug=False):
        """Run the dashboard"""
        logger.info(f"🖥️  Starting monitoring dashboard on {self.host}:{self.port}")

        # Start real-time updates
        self.start_real_time_updates()

        # Run Flask app
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=debug
        )


# Factory functions
def create_network_monitor(redis_config: Dict[str, Any] = None) -> SpiderNetworkMonitor:
    """Create network monitor instance"""
    return SpiderNetworkMonitor(redis_config)


def create_monitoring_dashboard(redis_config: Dict[str, Any] = None, host='0.0.0.0', port=5001) -> MonitoringDashboard:
    """Create monitoring dashboard instance"""
    monitor = create_network_monitor(redis_config)
    return MonitoringDashboard(monitor, host, port)