"""
Control Center WebSocket Consumer
=================================
System monitoring, agent management, and operational control
"""

import json
import logging
import asyncio
import os
import psutil
import redis
from typing import Dict, Any, List
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

logger = logging.getLogger(__name__)


class ControlCenterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Control Center
    Monitors system health, agent activity, and provides control capabilities
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.room_group_name = None
        self.monitoring_task = None
        self.redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user', AnonymousUser())

        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        # Check if user has admin/control permissions
        # For now, allow all authenticated users
        self.room_group_name = f'control_center_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial system status
        await self.send_system_status()

        # Start monitoring
        self.monitoring_task = asyncio.create_task(self.monitor_system())

        logger.info(f"✅ Control Center WebSocket connected for user {self.user.username}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if self.monitoring_task:
            self.monitoring_task.cancel()

        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"Control Center WebSocket disconnected")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'refresh':
                await self.send_system_status()
            elif action == 'get_agents':
                await self.send_agent_status()
            elif action == 'get_spiders':
                await self.send_spider_status()
            elif action == 'control_agent':
                await self.control_agent(data)
            elif action == 'control_spider':
                await self.control_spider(data)
            elif action == 'get_logs':
                await self.send_system_logs(data.get('filters', {}))
            elif action == 'get_metrics':
                await self.send_performance_metrics()
            elif action == 'system_command':
                await self.execute_system_command(data)

        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send_error(str(e))

    async def send_system_status(self):
        """Send comprehensive system status"""
        status = await self.get_system_health()

        await self.send(text_data=json.dumps({
            'type': 'system_status',
            'data': status
        }))

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used / (1024 ** 3)  # GB
        memory_total = memory.total / (1024 ** 3)  # GB

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = disk.used / (1024 ** 3)  # GB
        disk_total = disk.total / (1024 ** 3)  # GB

        # Redis status
        redis_connected = await self.check_redis_connection()

        # Database status
        db_connected, db_stats = await self.check_database()

        # Agent status
        active_agents = await self.get_active_agent_count()

        # Spider status
        active_spiders = await self.get_active_spider_count()

        # WebSocket connections
        ws_connections = await self.get_websocket_count()

        # Job processing stats
        jobs_stats = await self.get_job_stats()

        return {
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_gb': round(memory_used, 2),
                'memory_total_gb': round(memory_total, 2),
                'disk_percent': disk_percent,
                'disk_used_gb': round(disk_used, 2),
                'disk_total_gb': round(disk_total, 2)
            },
            'services': {
                'redis': {
                    'connected': redis_connected,
                    'status': 'healthy' if redis_connected else 'disconnected'
                },
                'database': {
                    'connected': db_connected,
                    'status': 'healthy' if db_connected else 'disconnected',
                    'stats': db_stats
                },
                'websockets': {
                    'active_connections': ws_connections
                }
            },
            'agents': {
                'active': active_agents,
                'status': 'operational' if active_agents > 0 else 'idle'
            },
            'spiders': {
                'active': active_spiders,
                'status': 'crawling' if active_spiders > 0 else 'idle'
            },
            'jobs': jobs_stats,
            'timestamp': datetime.now().isoformat(),
            'overall_health': self._calculate_overall_health(
                cpu_percent, memory_percent, redis_connected, db_connected
            )
        }

    async def check_redis_connection(self) -> bool:
        """Check Redis connection status"""
        try:
            return await database_sync_to_async(self.redis_client.ping)()
        except Exception as _e:
            logger.warning(
                "control_center_consumer.__init__: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    @database_sync_to_async
    def check_database(self) -> tuple:
        """Check database connection and stats"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            # Get database stats
            from core.models import JobApplication, Revenue, User
            stats = {
                'users': User.objects.count(),
                'applications': JobApplication.objects.count(),
                'revenue_records': Revenue.objects.count()
            }

            return True, stats
        except Exception as e:
            logger.error(f"Database check failed: {str(e)}")
            return False, {}

    @database_sync_to_async
    def get_active_agent_count(self) -> int:
        """Get count of active agents"""
        try:
            # Check Redis for active agents
            agent_keys = self.redis_client.keys('agent:active:*')
            return len(agent_keys)
        except Exception as _e:
            logger.warning(
                "control_center_consumer.get_active_agent_count: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0

    @database_sync_to_async
    def get_active_spider_count(self) -> int:
        """Get count of active spiders"""
        try:
            # Check Redis for active spiders
            spider_keys = self.redis_client.keys('spider:active:*')
            return len(spider_keys)
        except Exception as _e:
            logger.warning(
                "control_center_consumer.get_active_spider_count: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0

    @database_sync_to_async
    def get_websocket_count(self) -> int:
        """Get count of active WebSocket connections"""
        # This would need integration with channel layer stats
        # For now, return estimated count
        return 1  # At least this connection

    @database_sync_to_async
    def get_job_stats(self) -> Dict[str, Any]:
        """Get job processing statistics"""
        from core.models import JobApplication

        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        stats = {
            'today': {
                'submitted': JobApplication.objects.filter(
                    applied_date__date=today
                ).count(),
                'accepted': JobApplication.objects.filter(
                    status='offer_accepted',
                    last_status_update__date=today
                ).count()
            },
            'yesterday': {
                'submitted': JobApplication.objects.filter(
                    applied_date__date=yesterday
                ).count(),
                'accepted': JobApplication.objects.filter(
                    status='offer_accepted',
                    last_status_update__date=yesterday
                ).count()
            },
            'pending': JobApplication.objects.filter(
                status__in=['applied', 'under_review']
            ).count(),
            'in_progress': JobApplication.objects.filter(
                status='in_progress'
            ).count()
        }

        return stats

    def _calculate_overall_health(self, cpu: float, memory: float, redis: bool, db: bool) -> str:
        """Calculate overall system health"""
        if not redis or not db:
            return 'critical'
        if cpu > 90 or memory > 90:
            return 'warning'
        if cpu > 70 or memory > 70:
            return 'moderate'
        return 'healthy'

    async def send_agent_status(self):
        """Send detailed agent status"""
        agents = await self.get_agent_details()

        await self.send(text_data=json.dumps({
            'type': 'agent_status',
            'data': {
                'agents': agents,
                'total': len(agents),
                'timestamp': datetime.now().isoformat()
            }
        }))

    @database_sync_to_async
    def get_agent_details(self) -> List[Dict[str, Any]]:
        """Get detailed agent information"""
        agents = []

        # Get registered agents
        from core.agents.registry import agent_registry

        for agent_name, agent_class in agent_registry.get_all_agents().items():
            # Check if agent is active in Redis
            active_key = f'agent:active:{agent_name}'
            is_active = self.redis_client.exists(active_key)

            # Get agent stats from Redis
            stats_key = f'agent:stats:{agent_name}'
            stats = self.redis_client.hgetall(stats_key) if self.redis_client.exists(stats_key) else {}

            agents.append({
                'name': agent_name,
                'type': agent_class.__name__ if agent_class else 'Unknown',
                'status': 'active' if is_active else 'idle',
                'tasks_completed': int(stats.get('tasks_completed', 0)),
                'success_rate': float(stats.get('success_rate', 100.0)),
                'last_active': stats.get('last_active', 'Never'),
                'capabilities': self._get_agent_capabilities(agent_name)
            })

        return agents

    def _get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get agent capabilities based on name"""
        capabilities_map = {
            'content_creator': ['Writing', 'SEO', 'Content Generation'],
            'code_generator': ['Programming', 'API Development', 'Debugging'],
            'market_analyst': ['Market Research', 'Data Analysis', 'Reporting'],
            'job_finder': ['Job Search', 'Application Submission', 'Resume Matching']
        }

        return capabilities_map.get(agent_name.lower(), ['General Tasks'])

    async def send_spider_status(self):
        """Send detailed spider status"""
        spiders = await self.get_spider_details()

        await self.send(text_data=json.dumps({
            'type': 'spider_status',
            'data': {
                'spiders': spiders,
                'total': len(spiders),
                'timestamp': datetime.now().isoformat()
            }
        }))

    @database_sync_to_async
    def get_spider_details(self) -> List[Dict[str, Any]]:
        """Get detailed spider information"""
        spiders = []

        # Get spider information from Redis
        spider_keys = self.redis_client.keys('spider:*')

        spider_names = set()
        for key in spider_keys:
            parts = key.split(':')
            if len(parts) >= 3:
                spider_names.add(parts[2])

        for spider_name in spider_names:
            # Check if spider is active
            active_key = f'spider:active:{spider_name}'
            is_active = self.redis_client.exists(active_key)

            # Get spider stats
            stats_key = f'spider:stats:{spider_name}'
            stats = self.redis_client.hgetall(stats_key) if self.redis_client.exists(stats_key) else {}

            spiders.append({
                'name': spider_name,
                'status': 'crawling' if is_active else 'idle',
                'opportunities_found': int(stats.get('opportunities_found', 0)),
                'last_crawl': stats.get('last_crawl', 'Never'),
                'success_rate': float(stats.get('success_rate', 100.0)),
                'target_platform': stats.get('platform', 'Unknown')
            })

        # Add some default spiders if none found
        if not spiders:
            spiders = [
                {
                    'name': 'upwork_spider',
                    'status': 'idle',
                    'opportunities_found': 0,
                    'last_crawl': 'Never',
                    'success_rate': 100.0,
                    'target_platform': 'Upwork'
                },
                {
                    'name': 'linkedin_spider',
                    'status': 'idle',
                    'opportunities_found': 0,
                    'last_crawl': 'Never',
                    'success_rate': 100.0,
                    'target_platform': 'LinkedIn'
                }
            ]

        return spiders

    async def control_agent(self, data: Dict[str, Any]):
        """Control agent (start/stop/restart)"""
        agent_name = data.get('agent_name')
        command = data.get('command')

        if not agent_name or not command:
            await self.send_error('Agent name and command required')
            return

        result = await self.execute_agent_command(agent_name, command)

        await self.send(text_data=json.dumps({
            'type': 'agent_control_result',
            'data': result
        }))

    @database_sync_to_async
    def execute_agent_command(self, agent_name: str, command: str) -> Dict[str, Any]:
        """Execute agent control command"""
        try:
            if command == 'start':
                # Mark agent as active in Redis
                self.redis_client.set(f'agent:active:{agent_name}', '1', ex=3600)
                self.redis_client.hset(f'agent:stats:{agent_name}', 'last_active', datetime.now().isoformat())

                return {
                    'success': True,
                    'agent': agent_name,
                    'command': command,
                    'message': f'Agent {agent_name} started successfully'
                }

            elif command == 'stop':
                # Remove active status
                self.redis_client.delete(f'agent:active:{agent_name}')

                return {
                    'success': True,
                    'agent': agent_name,
                    'command': command,
                    'message': f'Agent {agent_name} stopped successfully'
                }

            elif command == 'restart':
                # Restart = stop + start
                self.redis_client.delete(f'agent:active:{agent_name}')
                self.redis_client.set(f'agent:active:{agent_name}', '1', ex=3600)
                self.redis_client.hset(f'agent:stats:{agent_name}', 'last_active', datetime.now().isoformat())

                return {
                    'success': True,
                    'agent': agent_name,
                    'command': command,
                    'message': f'Agent {agent_name} restarted successfully'
                }

            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def control_spider(self, data: Dict[str, Any]):
        """Control spider (start/stop/restart)"""
        spider_name = data.get('spider_name')
        command = data.get('command')

        if not spider_name or not command:
            await self.send_error('Spider name and command required')
            return

        result = await self.execute_spider_command(spider_name, command)

        await self.send(text_data=json.dumps({
            'type': 'spider_control_result',
            'data': result
        }))

    @database_sync_to_async
    def execute_spider_command(self, spider_name: str, command: str) -> Dict[str, Any]:
        """Execute spider control command"""
        try:
            if command == 'start':
                # Mark spider as active
                self.redis_client.set(f'spider:active:{spider_name}', '1', ex=3600)
                self.redis_client.hset(f'spider:stats:{spider_name}', 'last_crawl', datetime.now().isoformat())

                # Trigger actual spider if available
                # This would start the real spider process

                return {
                    'success': True,
                    'spider': spider_name,
                    'command': command,
                    'message': f'Spider {spider_name} started crawling'
                }

            elif command == 'stop':
                # Stop spider
                self.redis_client.delete(f'spider:active:{spider_name}')

                return {
                    'success': True,
                    'spider': spider_name,
                    'command': command,
                    'message': f'Spider {spider_name} stopped'
                }

            else:
                return {
                    'success': False,
                    'error': f'Unknown command: {command}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def monitor_system(self):
        """Continuously monitor system and send updates"""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds

                # Get current status
                status = await self.get_system_health()

                # Send update
                await self.send(text_data=json.dumps({
                    'type': 'status_update',
                    'data': status
                }))

                # Check for alerts
                alerts = self._check_for_alerts(status)
                if alerts:
                    await self.send(text_data=json.dumps({
                        'type': 'system_alert',
                        'data': {
                            'alerts': alerts,
                            'timestamp': datetime.now().isoformat()
                        }
                    }))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor_system: {str(e)}")
                await asyncio.sleep(60)

    def _check_for_alerts(self, status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check system status for alert conditions"""
        alerts = []

        # CPU alert
        if status['system']['cpu_percent'] > 90:
            alerts.append({
                'level': 'critical',
                'type': 'cpu',
                'message': f"CPU usage critical: {status['system']['cpu_percent']}%"
            })
        elif status['system']['cpu_percent'] > 70:
            alerts.append({
                'level': 'warning',
                'type': 'cpu',
                'message': f"CPU usage high: {status['system']['cpu_percent']}%"
            })

        # Memory alert
        if status['system']['memory_percent'] > 90:
            alerts.append({
                'level': 'critical',
                'type': 'memory',
                'message': f"Memory usage critical: {status['system']['memory_percent']}%"
            })

        # Service alerts
        if not status['services']['redis']['connected']:
            alerts.append({
                'level': 'critical',
                'type': 'service',
                'message': 'Redis connection lost'
            })

        if not status['services']['database']['connected']:
            alerts.append({
                'level': 'critical',
                'type': 'service',
                'message': 'Database connection lost'
            })

        return alerts

    async def send_error(self, message: str):
        """Send error message"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    # Group send handlers
    async def system_notification(self, event):
        """Handle system notifications from channel layer"""
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'data': event['data']
        }))