"""
Spider Army Command Center - Central Control Interface
=====================================================

The Spider Army Command Center provides centralized control, monitoring,
and management of the entire spider army. This is the nerve center that
coordinates thousands of spiders feeding intelligence to 102 agents and
25 legendary advisors.

Features:
- Real-time spider army monitoring
- Performance analytics and optimization
- Dynamic spider deployment and scaling
- Health monitoring and auto-recovery
- Intelligence flow visualization
- Command and control interface
"""

import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import redis
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask, render_template, jsonify, request
import threading

from .spider_army_orchestrator import SpiderArmyOrchestrator, ArmyStats, SpiderType
from .base_spider import SpiderMetrics

logger = logging.getLogger(__name__)


@dataclass
class CommandCenterStats:
    """Comprehensive command center statistics"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Spider Army Metrics
    total_spiders_deployed: int = 0
    active_spiders: int = 0
    failed_spiders: int = 0
    dormant_spiders: int = 0

    # Intelligence Metrics
    total_intelligence_gathered: int = 0
    intelligence_per_hour: float = 0.0
    avg_data_quality: float = 0.0

    # Distribution Metrics
    agents_fed: int = 0
    advisors_fed: int = 0
    intelligence_channels_active: int = 0

    # Performance Metrics
    avg_response_time: float = 0.0
    uptime_percentage: float = 100.0
    error_rate: float = 0.0

    # Specialized Swarm Performance
    swarm_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Top Performers
    top_performing_spiders: List[str] = field(default_factory=list)
    top_intelligence_sources: List[str] = field(default_factory=list)


class SpiderCommandCenter:
    """
    Central command and control center for the spider army.

    This is the mission control that oversees the entire intelligence
    gathering operation, providing real-time monitoring, control,
    and optimization of the spider army.
    """

    def __init__(self, orchestrator: SpiderArmyOrchestrator, port: int = 5000):
        """Initialize the Spider Command Center"""
        self.orchestrator = orchestrator
        self.port = port

        # Redis for real-time data
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

        # Flask app for web interface
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.setup_routes()

        # Command center state
        self.is_running = False
        self.stats_history: List[CommandCenterStats] = []
        self.alerts: List[Dict[str, Any]] = []
        self.commands_queue: List[Dict[str, Any]] = []

        # Performance monitoring
        self.performance_thresholds = {
            'min_uptime': 95.0,  # Minimum uptime percentage
            'max_error_rate': 5.0,  # Maximum error rate percentage
            'min_data_quality': 0.7,  # Minimum data quality score
            'max_response_time': 10.0  # Maximum response time in seconds
        }

        self.logger = logging.getLogger(__name__)

    def setup_routes(self):
        """Setup Flask routes for the web interface"""

        @self.app.route('/')
        def dashboard():
            """Main dashboard view"""
            return render_template('spider_command_center.html')

        @self.app.route('/api/status')
        def api_status():
            """Get current spider army status"""
            return jsonify(self.get_real_time_status())

        @self.app.route('/api/stats')
        def api_stats():
            """Get comprehensive statistics"""
            return jsonify(self.get_comprehensive_stats())

        @self.app.route('/api/performance')
        def api_performance():
            """Get performance analytics"""
            return jsonify(self.get_performance_analytics())

        @self.app.route('/api/swarms')
        def api_swarms():
            """Get swarm-level information"""
            return jsonify(self.get_swarm_information())

        @self.app.route('/api/intelligence_flow')
        def api_intelligence_flow():
            """Get intelligence flow data"""
            return jsonify(self.get_intelligence_flow_data())

        @self.app.route('/api/alerts')
        def api_alerts():
            """Get current alerts"""
            return jsonify(self.get_alerts())

        @self.app.route('/api/command', methods=['POST'])
        def api_command():
            """Execute command"""
            command = request.json
            result = self.execute_command(command)
            return jsonify(result)

        @self.app.route('/api/spider/<spider_id>')
        def api_spider_details(spider_id):
            """Get detailed spider information"""
            return jsonify(self.get_spider_details(spider_id))

        @self.app.route('/api/charts/performance')
        def api_performance_chart():
            """Get performance chart data"""
            return jsonify(self.generate_performance_charts())

        @self.app.route('/api/charts/intelligence_flow')
        def api_intelligence_flow_chart():
            """Get intelligence flow visualization"""
            return jsonify(self.generate_intelligence_flow_chart())

    async def start_command_center(self):
        """Start the command center operations"""
        try:
            self.is_running = True
            self.logger.info("🕷️ Spider Army Command Center starting up...")

            # Start monitoring tasks
            monitoring_tasks = [
                asyncio.create_task(self._monitor_spider_army()),
                asyncio.create_task(self._collect_intelligence_metrics()),
                asyncio.create_task(self._health_monitoring()),
                asyncio.create_task(self._alert_system()),
                asyncio.create_task(self._performance_optimization()),
                asyncio.create_task(self._generate_reports())
            ]

            # Start Flask app in a separate thread
            flask_thread = threading.Thread(
                target=lambda: self.app.run(
                    host='0.0.0.0',
                    port=self.port,
                    debug=False,
                    threaded=True
                )
            )
            flask_thread.daemon = True
            flask_thread.start()

            self.logger.info(f"🎯 Command Center UI available at http://localhost:{self.port}")

            # Wait for monitoring tasks
            await asyncio.gather(*monitoring_tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"Command Center startup failed: {e}")
        finally:
            self.is_running = False

    async def _monitor_spider_army(self):
        """Continuously monitor the spider army"""
        while self.is_running:
            try:
                # Collect current stats
                current_stats = await self._collect_current_stats()

                # Store in history
                self.stats_history.append(current_stats)

                # Keep only last 24 hours of history (288 entries at 5-minute intervals)
                if len(self.stats_history) > 288:
                    self.stats_history = self.stats_history[-288:]

                # Check for alerts
                await self._check_for_alerts(current_stats)

                # Log summary
                self.logger.info(
                    f"📊 Army Status: {current_stats.active_spiders}/{current_stats.total_spiders_deployed} active, "
                    f"Quality: {current_stats.avg_data_quality:.2f}, "
                    f"Intel/hour: {current_stats.intelligence_per_hour:.0f}"
                )

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in spider army monitoring: {e}")
                await asyncio.sleep(60)

    async def _collect_current_stats(self) -> CommandCenterStats:
        """Collect current comprehensive statistics"""
        try:
            # Get army status from orchestrator
            army_status = self.orchestrator.get_army_status()
            army_stats = army_status.get('army_stats', {})

            # Calculate intelligence metrics
            intelligence_metrics = await self._calculate_intelligence_metrics()

            # Calculate distribution metrics
            distribution_metrics = await self._calculate_distribution_metrics()

            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics()

            # Get swarm performance
            swarm_performance = await self._calculate_swarm_performance()

            # Create comprehensive stats
            stats = CommandCenterStats(
                timestamp=datetime.now(timezone.utc),

                # Spider metrics
                total_spiders_deployed=army_stats.get('total_spiders', 0),
                active_spiders=army_stats.get('active_spiders', 0),
                failed_spiders=max(0, army_stats.get('total_spiders', 0) - army_stats.get('active_spiders', 0)),
                dormant_spiders=0,  # Would be calculated based on activity

                # Intelligence metrics
                total_intelligence_gathered=army_stats.get('total_data_points', 0),
                intelligence_per_hour=intelligence_metrics.get('per_hour', 0.0),
                avg_data_quality=army_stats.get('avg_quality_score', 0.0),

                # Distribution metrics
                agents_fed=distribution_metrics.get('agents_fed', 0),
                advisors_fed=distribution_metrics.get('advisors_fed', 0),
                intelligence_channels_active=distribution_metrics.get('channels_active', 0),

                # Performance metrics
                avg_response_time=performance_metrics.get('avg_response_time', 0.0),
                uptime_percentage=army_stats.get('uptime_percentage', 100.0),
                error_rate=performance_metrics.get('error_rate', 0.0),

                # Specialized metrics
                swarm_performance=swarm_performance,
                top_performing_spiders=army_stats.get('top_performing_spiders', []),
                top_intelligence_sources=intelligence_metrics.get('top_sources', [])
            )

            return stats

        except Exception as e:
            self.logger.error(f"Error collecting current stats: {e}")
            return CommandCenterStats()

    async def _calculate_intelligence_metrics(self) -> Dict[str, Any]:
        """Calculate intelligence gathering metrics"""
        try:
            # Get intelligence data from Redis
            intelligence_keys = self.redis_client.keys('intelligence:*')

            # Calculate hourly rate
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_intelligence = 0

            for key in intelligence_keys[:100]:  # Sample to avoid overwhelming Redis
                try:
                    data = self.redis_client.get(key)
                    if data:
                        intel_data = json.loads(data)
                        timestamp_str = intel_data.get('timestamp', '')
                        if timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            if timestamp >= one_hour_ago:
                                recent_intelligence += 1
                except:
                    continue

            return {
                'per_hour': recent_intelligence,
                'total_channels': len(intelligence_keys),
                'top_sources': []  # Would be calculated from source analysis
            }

        except Exception as e:
            self.logger.error(f"Error calculating intelligence metrics: {e}")
            return {'per_hour': 0.0, 'total_channels': 0, 'top_sources': []}

    async def _calculate_distribution_metrics(self) -> Dict[str, Any]:
        """Calculate intelligence distribution metrics"""
        try:
            # Count active intelligence channels
            agent_channels = len(self.redis_client.keys('intelligence:agent:*'))
            advisor_channels = len(self.redis_client.keys('intelligence:advisor:*'))
            general_channels = len(self.redis_client.keys('intelligence:general:*'))

            return {
                'agents_fed': agent_channels,
                'advisors_fed': advisor_channels,
                'channels_active': agent_channels + advisor_channels + general_channels
            }

        except Exception as e:
            self.logger.error(f"Error calculating distribution metrics: {e}")
            return {'agents_fed': 0, 'advisors_fed': 0, 'channels_active': 0}

    async def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        try:
            # Get spider metrics from orchestrator
            active_spiders = self.orchestrator.active_spiders

            total_response_time = 0.0
            total_errors = 0
            total_requests = 0
            spider_count = 0

            for spider_id, spider in active_spiders.items():
                try:
                    metrics = spider.get_metrics()
                    total_response_time += metrics.avg_response_time
                    total_errors += metrics.failed_requests
                    total_requests += metrics.successful_requests + metrics.failed_requests
                    spider_count += 1
                except:
                    continue

            avg_response_time = total_response_time / spider_count if spider_count > 0 else 0.0
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

            return {
                'avg_response_time': avg_response_time,
                'error_rate': error_rate,
                'total_requests': total_requests
            }

        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {'avg_response_time': 0.0, 'error_rate': 0.0, 'total_requests': 0}

    async def _calculate_swarm_performance(self) -> Dict[str, Dict[str, float]]:
        """Calculate performance metrics for each swarm"""
        try:
            swarm_performance = {}

            for swarm_id, config in self.orchestrator.swarm_configs.items():
                swarm_spiders = [
                    spider for spider_id, spider in self.orchestrator.active_spiders.items()
                    if spider_id.startswith(f"{swarm_id}_")
                ]

                if swarm_spiders:
                    total_data_points = sum(spider.get_metrics().data_points_collected for spider in swarm_spiders)
                    avg_uptime = sum(spider.get_metrics().uptime_percentage for spider in swarm_spiders) / len(swarm_spiders)
                    avg_response_time = sum(spider.get_metrics().avg_response_time for spider in swarm_spiders) / len(swarm_spiders)

                    swarm_performance[swarm_id] = {
                        'active_spiders': len(swarm_spiders),
                        'total_data_points': total_data_points,
                        'avg_uptime': avg_uptime,
                        'avg_response_time': avg_response_time,
                        'efficiency_score': (total_data_points * avg_uptime) / 1000  # Composite efficiency
                    }

            return swarm_performance

        except Exception as e:
            self.logger.error(f"Error calculating swarm performance: {e}")
            return {}

    async def _check_for_alerts(self, stats: CommandCenterStats):
        """Check for conditions that require alerts"""
        try:
            alerts = []

            # Check uptime
            if stats.uptime_percentage < self.performance_thresholds['min_uptime']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'high',
                    'message': f"Army uptime below threshold: {stats.uptime_percentage:.1f}%",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'metric': 'uptime',
                    'value': stats.uptime_percentage,
                    'threshold': self.performance_thresholds['min_uptime']
                })

            # Check error rate
            if stats.error_rate > self.performance_thresholds['max_error_rate']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'medium',
                    'message': f"Error rate above threshold: {stats.error_rate:.1f}%",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'metric': 'error_rate',
                    'value': stats.error_rate,
                    'threshold': self.performance_thresholds['max_error_rate']
                })

            # Check data quality
            if stats.avg_data_quality < self.performance_thresholds['min_data_quality']:
                alerts.append({
                    'type': 'quality',
                    'severity': 'medium',
                    'message': f"Data quality below threshold: {stats.avg_data_quality:.2f}",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'metric': 'data_quality',
                    'value': stats.avg_data_quality,
                    'threshold': self.performance_thresholds['min_data_quality']
                })

            # Check response time
            if stats.avg_response_time > self.performance_thresholds['max_response_time']:
                alerts.append({
                    'type': 'performance',
                    'severity': 'low',
                    'message': f"Response time above threshold: {stats.avg_response_time:.1f}s",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'metric': 'response_time',
                    'value': stats.avg_response_time,
                    'threshold': self.performance_thresholds['max_response_time']
                })

            # Check spider failures
            if stats.failed_spiders > stats.total_spiders_deployed * 0.1:  # More than 10% failed
                alerts.append({
                    'type': 'infrastructure',
                    'severity': 'high',
                    'message': f"High spider failure rate: {stats.failed_spiders} failed",
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'metric': 'spider_failures',
                    'value': stats.failed_spiders,
                    'threshold': stats.total_spiders_deployed * 0.1
                })

            # Add new alerts
            self.alerts.extend(alerts)

            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]

            # Log high severity alerts
            for alert in alerts:
                if alert['severity'] == 'high':
                    self.logger.warning(f"🚨 HIGH ALERT: {alert['message']}")

        except Exception as e:
            self.logger.error(f"Error checking for alerts: {e}")

    async def _collect_intelligence_metrics(self):
        """Collect intelligence flow metrics"""
        while self.is_running:
            try:
                # Monitor intelligence flow rates
                await self._monitor_intelligence_flow()
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error collecting intelligence metrics: {e}")
                await asyncio.sleep(60)

    async def _monitor_intelligence_flow(self):
        """Monitor the flow of intelligence through the system"""
        try:
            # Get recent intelligence activity
            channels = self.redis_client.keys('intelligence:*')

            flow_stats = {
                'total_channels': len(channels),
                'active_channels': 0,
                'messages_per_minute': 0,
                'channel_activity': {}
            }

            # Check activity for each channel
            for channel in channels[:50]:  # Sample to prevent overload
                try:
                    # This would be implemented based on your Redis pub/sub setup
                    # For now, we'll simulate activity detection
                    channel_name = channel.decode('utf-8')
                    flow_stats['channel_activity'][channel_name] = {
                        'messages': 0,  # Would count actual messages
                        'last_activity': datetime.now(timezone.utc).isoformat()
                    }
                except:
                    continue

            # Store flow stats in Redis for API access
            self.redis_client.setex(
                'command_center:intelligence_flow',
                300,  # 5 minute expiry
                json.dumps(flow_stats)
            )

        except Exception as e:
            self.logger.error(f"Error monitoring intelligence flow: {e}")

    async def _health_monitoring(self):
        """Continuous health monitoring"""
        while self.is_running:
            try:
                # Check spider health
                await self._check_spider_health()

                # Check Redis connectivity
                await self._check_redis_health()

                # Check system resources
                await self._check_system_resources()

                await asyncio.sleep(120)  # Check every 2 minutes

            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(60)

    async def _check_spider_health(self):
        """Check health of individual spiders"""
        try:
            unhealthy_spiders = []

            for spider_id, spider in self.orchestrator.active_spiders.items():
                try:
                    metrics = spider.get_metrics()

                    # Check if spider is responsive
                    if metrics.last_active:
                        time_since_active = (datetime.now(timezone.utc) - metrics.last_active).total_seconds()
                        if time_since_active > 600:  # 10 minutes
                            unhealthy_spiders.append({
                                'spider_id': spider_id,
                                'issue': 'unresponsive',
                                'last_active': metrics.last_active.isoformat()
                            })

                    # Check error rate
                    total_requests = metrics.successful_requests + metrics.failed_requests
                    if total_requests > 10:  # Minimum sample size
                        error_rate = (metrics.failed_requests / total_requests) * 100
                        if error_rate > 50:  # High error rate
                            unhealthy_spiders.append({
                                'spider_id': spider_id,
                                'issue': 'high_error_rate',
                                'error_rate': error_rate
                            })

                except Exception as e:
                    unhealthy_spiders.append({
                        'spider_id': spider_id,
                        'issue': 'metrics_error',
                        'error': str(e)
                    })

            # Store health status
            health_status = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_spiders': len(self.orchestrator.active_spiders),
                'unhealthy_spiders': unhealthy_spiders,
                'health_score': max(0, 100 - (len(unhealthy_spiders) / len(self.orchestrator.active_spiders) * 100))
            }

            self.redis_client.setex(
                'command_center:spider_health',
                300,
                json.dumps(health_status)
            )

        except Exception as e:
            self.logger.error(f"Error checking spider health: {e}")

    async def _check_redis_health(self):
        """Check Redis connectivity and performance"""
        try:
            start_time = datetime.now()

            # Test Redis operations
            test_key = 'health_check:redis'
            self.redis_client.set(test_key, 'test', ex=60)
            value = self.redis_client.get(test_key)
            self.redis_client.delete(test_key)

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            redis_health = {
                'status': 'healthy' if value == b'test' else 'unhealthy',
                'response_time_ms': response_time,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            self.redis_client.setex(
                'command_center:redis_health',
                300,
                json.dumps(redis_health)
            )

        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            redis_health = {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            # Try to store error status
            try:
                self.redis_client.setex(
                    'command_center:redis_health',
                    300,
                    json.dumps(redis_health)
                )
            except:
                pass  # Redis is really down

    async def _check_system_resources(self):
        """Check system resource usage"""
        try:
            import psutil

            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            resource_status = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'healthy'
            }

            # Check thresholds
            if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                resource_status['status'] = 'warning'

            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                resource_status['status'] = 'critical'

            self.redis_client.setex(
                'command_center:system_resources',
                300,
                json.dumps(resource_status)
            )

        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            self.logger.error(f"Error checking system resources: {e}")

    async def _alert_system(self):
        """Process and manage alerts"""
        while self.is_running:
            try:
                # Process alert queue
                await self._process_alert_queue()

                # Auto-resolve old alerts
                await self._auto_resolve_alerts()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in alert system: {e}")
                await asyncio.sleep(60)

    async def _process_alert_queue(self):
        """Process pending alerts"""
        try:
            # Get alerts from Redis queue
            alert_queue_key = 'command_center:alert_queue'

            while True:
                alert_data = self.redis_client.lpop(alert_queue_key)
                if not alert_data:
                    break

                try:
                    alert = json.loads(alert_data)
                    await self._handle_alert(alert)
                except json.JSONDecodeError:
                    self.logger.warning("Invalid alert data in queue")

        except Exception as e:
            self.logger.error(f"Error processing alert queue: {e}")

    async def _handle_alert(self, alert: Dict[str, Any]):
        """Handle a specific alert"""
        try:
            alert_type = alert.get('type', 'unknown')
            severity = alert.get('severity', 'low')

            self.logger.info(f"🔔 Alert [{severity.upper()}]: {alert.get('message', 'Unknown alert')}")

            # Auto-remediation for certain alert types
            if alert_type == 'spider_failure' and severity == 'high':
                await self._auto_restart_failed_spiders()
            elif alert_type == 'performance' and alert.get('metric') == 'error_rate':
                await self._auto_scale_struggling_swarms()

        except Exception as e:
            self.logger.error(f"Error handling alert: {e}")

    async def _auto_restart_failed_spiders(self):
        """Automatically restart failed spiders"""
        try:
            # This would integrate with the orchestrator's restart functionality
            self.logger.info("🔄 Auto-restarting failed spiders...")
            # Implementation would call orchestrator restart methods

        except Exception as e:
            self.logger.error(f"Error auto-restarting spiders: {e}")

    async def _auto_scale_struggling_swarms(self):
        """Automatically scale up struggling swarms"""
        try:
            # This would integrate with the orchestrator's scaling functionality
            self.logger.info("📈 Auto-scaling struggling swarms...")
            # Implementation would call orchestrator scaling methods

        except Exception as e:
            self.logger.error(f"Error auto-scaling swarms: {e}")

    async def _auto_resolve_alerts(self):
        """Auto-resolve old alerts"""
        try:
            current_time = datetime.now(timezone.utc)

            # Remove alerts older than 24 hours
            self.alerts = [
                alert for alert in self.alerts
                if (current_time - datetime.fromisoformat(alert['timestamp'])).total_seconds() < 86400
            ]

        except Exception as e:
            self.logger.error(f"Error auto-resolving alerts: {e}")

    async def _performance_optimization(self):
        """Continuous performance optimization"""
        while self.is_running:
            try:
                # Analyze performance trends
                await self._analyze_performance_trends()

                # Optimize spider allocation
                await self._optimize_spider_allocation()

                await asyncio.sleep(900)  # Optimize every 15 minutes

            except Exception as e:
                self.logger.error(f"Error in performance optimization: {e}")
                await asyncio.sleep(600)

    async def _analyze_performance_trends(self):
        """Analyze performance trends and predict issues"""
        try:
            if len(self.stats_history) < 10:
                return  # Not enough data

            # Get recent stats
            recent_stats = self.stats_history[-10:]

            # Analyze trends
            trends = {
                'uptime_trend': self._calculate_trend([s.uptime_percentage for s in recent_stats]),
                'quality_trend': self._calculate_trend([s.avg_data_quality for s in recent_stats]),
                'intelligence_trend': self._calculate_trend([s.intelligence_per_hour for s in recent_stats]),
                'error_rate_trend': self._calculate_trend([s.error_rate for s in recent_stats])
            }

            # Store trend analysis
            trend_analysis = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'trends': trends,
                'predictions': self._generate_predictions(trends)
            }

            self.redis_client.setex(
                'command_center:performance_trends',
                3600,  # 1 hour expiry
                json.dumps(trend_analysis)
            )

        except Exception as e:
            self.logger.error(f"Error analyzing performance trends: {e}")

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values"""
        if len(values) < 2:
            return 'stable'

        # Simple linear regression
        x = list(range(len(values)))
        n = len(values)

        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'

    def _generate_predictions(self, trends: Dict[str, str]) -> Dict[str, str]:
        """Generate predictions based on trends"""
        predictions = {}

        if trends['uptime_trend'] == 'decreasing':
            predictions['uptime'] = 'System stability may decline in next hour'

        if trends['quality_trend'] == 'decreasing':
            predictions['quality'] = 'Data quality may need attention'

        if trends['error_rate_trend'] == 'increasing':
            predictions['errors'] = 'Error rate trending up, investigate sources'

        return predictions

    async def _optimize_spider_allocation(self):
        """Optimize spider allocation based on performance"""
        try:
            # This would implement intelligent spider allocation
            # based on current performance metrics and demand

            self.logger.debug("🎯 Optimizing spider allocation...")

            # Analysis would include:
            # - Identifying underperforming swarms
            # - Reallocating spiders to high-demand areas
            # - Adjusting rate limits based on source capacity
            # - Optimizing geographical distribution

        except Exception as e:
            self.logger.error(f"Error optimizing spider allocation: {e}")

    async def _generate_reports(self):
        """Generate periodic reports"""
        while self.is_running:
            try:
                # Generate hourly summary
                await self._generate_hourly_report()

                await asyncio.sleep(3600)  # Generate every hour

            except Exception as e:
                self.logger.error(f"Error generating reports: {e}")
                await asyncio.sleep(3600)

    async def _generate_hourly_report(self):
        """Generate hourly performance report"""
        try:
            if not self.stats_history:
                return

            # Get last hour's stats
            one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
            recent_stats = [
                s for s in self.stats_history
                if s.timestamp >= one_hour_ago
            ]

            if not recent_stats:
                return

            # Calculate hourly metrics
            avg_uptime = sum(s.uptime_percentage for s in recent_stats) / len(recent_stats)
            avg_quality = sum(s.avg_data_quality for s in recent_stats) / len(recent_stats)
            total_intelligence = sum(s.intelligence_per_hour for s in recent_stats)

            # Generate report
            report = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'period': 'hourly',
                'metrics': {
                    'avg_uptime': avg_uptime,
                    'avg_quality': avg_quality,
                    'total_intelligence': total_intelligence,
                    'data_points': len(recent_stats)
                },
                'summary': f"Hourly Report: {avg_uptime:.1f}% uptime, {avg_quality:.2f} quality score, {total_intelligence:.0f} intelligence gathered"
            }

            # Store report
            self.redis_client.lpush('command_center:reports', json.dumps(report))
            self.redis_client.ltrim('command_center:reports', 0, 167)  # Keep last week (24*7)

            self.logger.info(f"📊 {report['summary']}")

        except Exception as e:
            self.logger.error(f"Error generating hourly report: {e}")

    # API methods for web interface

    def get_real_time_status(self) -> Dict[str, Any]:
        """Get real-time status for the dashboard"""
        try:
            current_stats = self.stats_history[-1] if self.stats_history else CommandCenterStats()
            army_status = self.orchestrator.get_army_status()

            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'spider_army': {
                    'total_spiders': current_stats.total_spiders_deployed,
                    'active_spiders': current_stats.active_spiders,
                    'failed_spiders': current_stats.failed_spiders,
                    'uptime_percentage': current_stats.uptime_percentage
                },
                'intelligence': {
                    'total_gathered': current_stats.total_intelligence_gathered,
                    'per_hour': current_stats.intelligence_per_hour,
                    'avg_quality': current_stats.avg_data_quality
                },
                'distribution': {
                    'agents_fed': current_stats.agents_fed,
                    'advisors_fed': current_stats.advisors_fed,
                    'channels_active': current_stats.intelligence_channels_active
                },
                'performance': {
                    'avg_response_time': current_stats.avg_response_time,
                    'error_rate': current_stats.error_rate
                },
                'is_running': self.orchestrator.is_running
            }

        except Exception as e:
            self.logger.error(f"Error getting real-time status: {e}")
            return {'error': str(e)}

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        try:
            current_stats = self.stats_history[-1] if self.stats_history else CommandCenterStats()

            return {
                'current': current_stats.__dict__,
                'history_points': len(self.stats_history),
                'swarm_performance': current_stats.swarm_performance,
                'top_performers': current_stats.top_performing_spiders,
                'army_config': {
                    swarm_id: {
                        'spider_count': config.spider_count,
                        'spider_type': config.spider_type.value,
                        'auto_scale': config.auto_scale,
                        'max_spiders': config.max_spiders
                    }
                    for swarm_id, config in self.orchestrator.swarm_configs.items()
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting comprehensive stats: {e}")
            return {'error': str(e)}

    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics data"""
        try:
            if len(self.stats_history) < 2:
                return {'error': 'Insufficient data for analytics'}

            # Calculate performance metrics over time
            timestamps = [s.timestamp.isoformat() for s in self.stats_history]
            uptimes = [s.uptime_percentage for s in self.stats_history]
            quality_scores = [s.avg_data_quality for s in self.stats_history]
            intelligence_rates = [s.intelligence_per_hour for s in self.stats_history]
            error_rates = [s.error_rate for s in self.stats_history]

            return {
                'time_series': {
                    'timestamps': timestamps,
                    'uptime': uptimes,
                    'quality': quality_scores,
                    'intelligence_rate': intelligence_rates,
                    'error_rate': error_rates
                },
                'trends': {
                    'uptime_trend': self._calculate_trend(uptimes[-10:]) if len(uptimes) >= 10 else 'stable',
                    'quality_trend': self._calculate_trend(quality_scores[-10:]) if len(quality_scores) >= 10 else 'stable',
                    'intelligence_trend': self._calculate_trend(intelligence_rates[-10:]) if len(intelligence_rates) >= 10 else 'stable'
                },
                'aggregates': {
                    'avg_uptime': sum(uptimes) / len(uptimes),
                    'avg_quality': sum(quality_scores) / len(quality_scores),
                    'avg_intelligence_rate': sum(intelligence_rates) / len(intelligence_rates),
                    'avg_error_rate': sum(error_rates) / len(error_rates)
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting performance analytics: {e}")
            return {'error': str(e)}

    def get_swarm_information(self) -> Dict[str, Any]:
        """Get detailed swarm information"""
        try:
            current_stats = self.stats_history[-1] if self.stats_history else CommandCenterStats()
            swarm_performance = current_stats.swarm_performance

            swarm_info = {}

            for swarm_id, config in self.orchestrator.swarm_configs.items():
                performance = swarm_performance.get(swarm_id, {})

                swarm_info[swarm_id] = {
                    'config': {
                        'spider_type': config.spider_type.value,
                        'configured_count': config.spider_count,
                        'max_spiders': config.max_spiders,
                        'auto_scale': config.auto_scale,
                        'priority': config.priority,
                        'target_count': len(config.targets),
                        'subscriber_count': len(config.subscribers)
                    },
                    'performance': performance,
                    'status': self._calculate_swarm_status(performance)
                }

            return swarm_info

        except Exception as e:
            self.logger.error(f"Error getting swarm information: {e}")
            return {'error': str(e)}

    def _calculate_swarm_status(self, performance: Dict[str, float]) -> str:
        """Calculate swarm status based on performance"""
        if not performance:
            return 'unknown'

        uptime = performance.get('avg_uptime', 0)
        efficiency = performance.get('efficiency_score', 0)

        if uptime > 95 and efficiency > 100:
            return 'excellent'
        elif uptime > 90 and efficiency > 50:
            return 'good'
        elif uptime > 80:
            return 'fair'
        else:
            return 'poor'

    def get_intelligence_flow_data(self) -> Dict[str, Any]:
        """Get intelligence flow data"""
        try:
            # Get flow data from Redis
            flow_data = self.redis_client.get('command_center:intelligence_flow')
            if flow_data:
                return json.loads(flow_data)
            else:
                return {
                    'total_channels': 0,
                    'active_channels': 0,
                    'messages_per_minute': 0,
                    'channel_activity': {}
                }

        except Exception as e:
            self.logger.error(f"Error getting intelligence flow data: {e}")
            return {'error': str(e)}

    def get_alerts(self) -> Dict[str, Any]:
        """Get current alerts"""
        try:
            # Sort alerts by severity and time
            severity_order = {'high': 3, 'medium': 2, 'low': 1}

            sorted_alerts = sorted(
                self.alerts,
                key=lambda x: (
                    severity_order.get(x.get('severity', 'low'), 0),
                    datetime.fromisoformat(x.get('timestamp', '2000-01-01T00:00:00+00:00'))
                ),
                reverse=True
            )

            return {
                'alerts': sorted_alerts[:50],  # Last 50 alerts
                'summary': {
                    'total': len(self.alerts),
                    'high': len([a for a in self.alerts if a.get('severity') == 'high']),
                    'medium': len([a for a in self.alerts if a.get('severity') == 'medium']),
                    'low': len([a for a in self.alerts if a.get('severity') == 'low'])
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return {'error': str(e)}

    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command"""
        try:
            command_type = command.get('type')

            if command_type == 'restart_spider':
                return self._execute_restart_spider(command)
            elif command_type == 'scale_swarm':
                return self._execute_scale_swarm(command)
            elif command_type == 'update_config':
                return self._execute_update_config(command)
            elif command_type == 'clear_alerts':
                return self._execute_clear_alerts(command)
            else:
                return {'success': False, 'error': f'Unknown command type: {command_type}'}

        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_restart_spider(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute spider restart command"""
        spider_id = command.get('spider_id')
        if not spider_id:
            return {'success': False, 'error': 'spider_id required'}

        try:
            # This would integrate with orchestrator restart functionality
            # For now, simulate the command
            self.commands_queue.append({
                'type': 'restart_spider',
                'spider_id': spider_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'queued'
            })

            return {'success': True, 'message': f'Spider {spider_id} restart queued'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_scale_swarm(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute swarm scaling command"""
        swarm_id = command.get('swarm_id')
        scale_factor = command.get('scale_factor', 1.0)

        if not swarm_id:
            return {'success': False, 'error': 'swarm_id required'}

        try:
            # This would integrate with orchestrator scaling functionality
            self.commands_queue.append({
                'type': 'scale_swarm',
                'swarm_id': swarm_id,
                'scale_factor': scale_factor,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'queued'
            })

            return {'success': True, 'message': f'Swarm {swarm_id} scaling queued (factor: {scale_factor})'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_update_config(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute configuration update command"""
        config_type = command.get('config_type')
        config_data = command.get('config_data', {})

        if not config_type:
            return {'success': False, 'error': 'config_type required'}

        try:
            if config_type == 'thresholds':
                # Update performance thresholds
                self.performance_thresholds.update(config_data)
                return {'success': True, 'message': 'Performance thresholds updated'}
            else:
                return {'success': False, 'error': f'Unknown config type: {config_type}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _execute_clear_alerts(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute clear alerts command"""
        try:
            severity = command.get('severity')  # Optional filter

            if severity:
                # Clear alerts of specific severity
                self.alerts = [a for a in self.alerts if a.get('severity') != severity]
                return {'success': True, 'message': f'Cleared {severity} alerts'}
            else:
                # Clear all alerts
                cleared_count = len(self.alerts)
                self.alerts.clear()
                return {'success': True, 'message': f'Cleared {cleared_count} alerts'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_spider_details(self, spider_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific spider"""
        try:
            spider = self.orchestrator.active_spiders.get(spider_id)

            if not spider:
                return {'error': f'Spider {spider_id} not found'}

            metrics = spider.get_metrics()

            return {
                'spider_id': spider_id,
                'metrics': {
                    'data_points_collected': metrics.data_points_collected,
                    'successful_requests': metrics.successful_requests,
                    'failed_requests': metrics.failed_requests,
                    'avg_response_time': metrics.avg_response_time,
                    'uptime_percentage': metrics.uptime_percentage,
                    'last_active': metrics.last_active.isoformat() if metrics.last_active else None,
                    'rate_limit_hits': metrics.rate_limit_hits
                },
                'config': {
                    'targets': len(spider.targets),
                    'subscribers': len(spider.subscribers),
                    'cache_size': len(spider.data_cache)
                },
                'status': 'active' if spider.is_running else 'inactive'
            }

        except Exception as e:
            self.logger.error(f"Error getting spider details: {e}")
            return {'error': str(e)}

    def generate_performance_charts(self) -> Dict[str, Any]:
        """Generate performance chart data"""
        try:
            if len(self.stats_history) < 2:
                return {'error': 'Insufficient data for charts'}

            # Prepare data for charts
            timestamps = [s.timestamp.isoformat() for s in self.stats_history[-24:]]  # Last 24 data points

            charts = {
                'uptime_chart': {
                    'x': timestamps,
                    'y': [s.uptime_percentage for s in self.stats_history[-24:]],
                    'type': 'line',
                    'name': 'Uptime %'
                },
                'quality_chart': {
                    'x': timestamps,
                    'y': [s.avg_data_quality for s in self.stats_history[-24:]],
                    'type': 'line',
                    'name': 'Data Quality'
                },
                'intelligence_chart': {
                    'x': timestamps,
                    'y': [s.intelligence_per_hour for s in self.stats_history[-24:]],
                    'type': 'bar',
                    'name': 'Intelligence/Hour'
                },
                'spider_status_chart': {
                    'labels': ['Active', 'Failed', 'Dormant'],
                    'values': [
                        self.stats_history[-1].active_spiders if self.stats_history else 0,
                        self.stats_history[-1].failed_spiders if self.stats_history else 0,
                        self.stats_history[-1].dormant_spiders if self.stats_history else 0
                    ],
                    'type': 'pie',
                    'name': 'Spider Status Distribution'
                }
            }

            return charts

        except Exception as e:
            self.logger.error(f"Error generating performance charts: {e}")
            return {'error': str(e)}

    def generate_intelligence_flow_chart(self) -> Dict[str, Any]:
        """Generate intelligence flow visualization"""
        try:
            # Get swarm performance data
            current_stats = self.stats_history[-1] if self.stats_history else CommandCenterStats()
            swarm_performance = current_stats.swarm_performance

            # Create flow chart data
            flow_chart = {
                'nodes': [],
                'links': []
            }

            # Add spider swarm nodes
            for swarm_id, performance in swarm_performance.items():
                flow_chart['nodes'].append({
                    'id': swarm_id,
                    'name': swarm_id.replace('_', ' ').title(),
                    'type': 'swarm',
                    'value': performance.get('total_data_points', 0),
                    'status': self._calculate_swarm_status(performance)
                })

            # Add agent/advisor nodes (simplified)
            flow_chart['nodes'].extend([
                {'id': 'agents', 'name': '102 Agents', 'type': 'consumer', 'value': current_stats.agents_fed},
                {'id': 'advisors', 'name': '25 Advisors', 'type': 'consumer', 'value': current_stats.advisors_fed}
            ])

            # Add links (data flow)
            for swarm_id in swarm_performance.keys():
                flow_chart['links'].extend([
                    {'source': swarm_id, 'target': 'agents', 'value': 50},  # Simplified
                    {'source': swarm_id, 'target': 'advisors', 'value': 25}
                ])

            return flow_chart

        except Exception as e:
            self.logger.error(f"Error generating intelligence flow chart: {e}")
            return {'error': str(e)}

    async def shutdown(self):
        """Shutdown the command center"""
        try:
            self.is_running = False
            self.logger.info("🛑 Spider Army Command Center shutting down...")

            # Final report
            if self.stats_history:
                final_stats = self.stats_history[-1]
                self.logger.info(
                    f"📊 Final Stats: {final_stats.active_spiders} active spiders, "
                    f"{final_stats.total_intelligence_gathered} total intelligence gathered"
                )

        except Exception as e:
            self.logger.error(f"Error during command center shutdown: {e}")


# Global command center instance
_command_center_instance = None

def get_command_center(orchestrator: SpiderArmyOrchestrator) -> SpiderCommandCenter:
    """Get the global command center instance"""
    global _command_center_instance
    if _command_center_instance is None:
        _command_center_instance = SpiderCommandCenter(orchestrator)
    return _command_center_instance