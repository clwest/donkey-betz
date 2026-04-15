"""
Session 701: HEART Service - The Central Heartbeat of the AI Body

HeartMonitorService performs continuous health monitoring of all system components,
using the human body metaphor:
- BRAIN: ThinkingAgent (reasoning)
- NERVOUS SYSTEM: LLM/ML Routers (signal routing)
- ORGANS: 72 Specialized Agents (work execution)
- SENSORY: 77 Spiders (data gathering)
- SKIN: Workspace Manager (touching reality)
- MEMORY: Database & Redis (persistence)
"""

import logging
import os
import time
from datetime import timedelta
from typing import Dict, Optional

from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


# Singleton instance
_heart_monitor_instance: Optional['HeartMonitorService'] = None


def get_heart_monitor() -> 'HeartMonitorService':
    """Get the singleton HeartMonitorService instance."""
    global _heart_monitor_instance
    if _heart_monitor_instance is None:
        _heart_monitor_instance = HeartMonitorService()
    return _heart_monitor_instance


class HeartMonitorService:
    """
    The central heartbeat of the AI body.

    Monitors health of all components and provides real-time system status.
    Following singleton pattern (like AgentLLMRouter).
    """

    # Component definitions (human body metaphor)
    # Session 744: Added 'celery' component for task execution monitoring
    COMPONENTS = {
        'brain': {
            'name': 'Brain (ThinkingAgent)',
            'description': 'Autonomous reasoning and decision-making',
        },
        'nervous_system': {
            'name': 'Nervous System (LLM/ML Routers)',
            'description': 'Signal routing for tasks to appropriate models',
        },
        'organs': {
            'name': 'Organs (72 Agents)',
            'description': 'Specialized work execution agents',
        },
        'sensory': {
            'name': 'Sensory (77 Spiders)',
            'description': 'Data gathering from external world',
        },
        'skin': {
            'name': 'Skin (Workspace Manager)',
            'description': 'Interface for writing to real projects',
        },
        'memory': {
            'name': 'Memory (Database & Redis)',
            'description': 'Persistence and caching layer',
        },
        'celery': {
            'name': 'Celery (Task Workers)',
            'description': 'Background task execution - 150+ scheduled tasks',
        },
        'resolve_node': {
            'name': 'Resolve Node (DaVinci)',
            'description': 'DaVinci Resolve render server for video processing',
        },
    }

    def __init__(self):
        self._initialized = False
        self._last_pulse: Optional[Dict] = None
        self._initialize()

    def _initialize(self):
        """Initialize the heart monitor."""
        if self._initialized:
            return

        logger.info("❤️ HeartMonitorService initializing...")

        # Initialize component status records if they don't exist
        try:
            self._ensure_component_records()
        except Exception as e:
            logger.warning(f"❤️ Could not initialize component records: {e}")

        self._initialized = True
        logger.info("❤️ HeartMonitorService ready - monitoring 6 body components")

    def _ensure_component_records(self):
        """Ensure all component status records exist in database."""
        from core.models_heart import ComponentStatus

        for component_id, info in self.COMPONENTS.items():
            ComponentStatus.objects.get_or_create(
                component=component_id,
                defaults={
                    'display_name': info['name'],
                    'description': info['description'],
                    'status': 'healthy',
                    'is_healthy': True,
                    'last_check': timezone.now(),
                    'last_healthy': timezone.now(),
                }
            )

    def pulse(self) -> Dict:
        """
        Run full health check on all components.

        Returns comprehensive health status of the entire AI body.
        """
        start_time = time.time()
        logger.info("💓 Running system pulse check...")

        components = {}
        components_healthy = 0
        components_checked = 0

        # Check each body component
        # Session 744: Added celery to critical components
        check_methods = {
            'brain': self.check_brain,
            'nervous_system': self.check_nervous_system,
            'organs': self.check_organs,
            'sensory': self.check_sensory,
            'skin': self.check_skin,
            'memory': self.check_memory,
            'celery': self.check_celery,
            'resolve_node': self.check_resolve_node,
        }

        for component_id, check_method in check_methods.items():
            try:
                result = check_method()
                components[component_id] = result
                components_checked += 1
                if result.get('is_healthy', False):
                    components_healthy += 1

                # Update component status in database
                self._update_component_status(component_id, result)

            except Exception as e:
                logger.error(f"💔 Error checking {component_id}: {e}")
                components[component_id] = {
                    'name': self.COMPONENTS[component_id]['name'],
                    'status': 'critical',
                    'is_healthy': False,
                    'error': str(e),
                    'response_time_ms': 0,
                    'details': {},
                }
                components_checked += 1

        # Calculate overall health
        check_duration_ms = int((time.time() - start_time) * 1000)
        health_score = (components_healthy / components_checked * 100) if components_checked > 0 else 0

        # Determine overall status
        if health_score >= 80:
            overall_status = 'healthy'
        elif health_score >= 50:
            overall_status = 'degraded'
        else:
            overall_status = 'critical'

        pulse_result = {
            'timestamp': timezone.now().isoformat(),
            'health_score': round(health_score, 1),
            'overall_status': overall_status,
            'is_alive': health_score > 0,
            'check_duration_ms': check_duration_ms,
            'components_checked': components_checked,
            'components_healthy': components_healthy,
            'components': components,
        }

        self._last_pulse = pulse_result

        logger.info(
            f"💓 Pulse complete: {overall_status.upper()} "
            f"({health_score:.1f}%) - {components_healthy}/{components_checked} components healthy "
            f"[{check_duration_ms}ms]"
        )

        return pulse_result

    def check_brain(self) -> Dict:
        """Check ThinkingAgent availability."""
        start = time.time()
        try:
            from core.agents.thinking_agent import ThinkingAgent

            # Verify it can be instantiated
            agent = ThinkingAgent()

            response_time_ms = int((time.time() - start) * 1000)

            return {
                'name': self.COMPONENTS['brain']['name'],
                'status': 'healthy',
                'is_healthy': True,
                'response_time_ms': response_time_ms,
                'details': {
                    'agent_class': 'ThinkingAgent',
                    'model': getattr(agent, 'model', 'claude-opus-4'),
                },
            }
        except Exception as e:
            return {
                'name': self.COMPONENTS['brain']['name'],
                'status': 'critical',
                'is_healthy': False,
                'response_time_ms': int((time.time() - start) * 1000),
                'error': str(e),
                'details': {},
            }

    def check_nervous_system(self) -> Dict:
        """Check LLM/ML routing system."""
        start = time.time()
        try:
            from core.services.llm_provider_registry import get_llm_provider_registry

            registry = get_llm_provider_registry()
            available_providers = registry.get_available_providers()
            available_models = registry.get_available_models()

            providers_active = len(available_providers)
            models_count = len(available_models)

            is_healthy = providers_active >= 1
            status_level = 'healthy' if providers_active >= 3 else ('degraded' if providers_active >= 1 else 'critical')

            response_time_ms = int((time.time() - start) * 1000)

            return {
                'name': self.COMPONENTS['nervous_system']['name'],
                'status': status_level,
                'is_healthy': is_healthy,
                'response_time_ms': response_time_ms,
                'details': {
                    'providers_active': providers_active,
                    'providers': available_providers,
                    'models_available': models_count,
                },
            }
        except Exception as e:
            return {
                'name': self.COMPONENTS['nervous_system']['name'],
                'status': 'critical',
                'is_healthy': False,
                'response_time_ms': int((time.time() - start) * 1000),
                'error': str(e),
                'details': {},
            }

    def check_organs(self) -> Dict:
        """Check agent registry and recent activity."""
        start = time.time()
        try:
            from core.models_unified_system import Agent

            # Count total agents
            total_agents = Agent.objects.filter(is_active=True).count()

            # Check recent activity (last hour)
            one_hour_ago = timezone.now() - timedelta(hours=1)

            # Try to get recent agent activity.
            # Session 1083 (Rigby audit): was `from core.models import
            # AgentActivity` which doesn't exist (never did, or was
            # removed long ago). The import error was caught and
            # logged as WARNING every 10 min via the heart pulse
            # cycle. Swapped to AgentExecution which IS the actual
            # "agent did something" record type in this codebase.
            recent_activity = 0
            try:
                from core.models_unified_system import AgentExecution
                recent_activity = AgentExecution.objects.filter(
                    created_at__gte=one_hour_ago
                ).count()
            except Exception as e:
                logger.warning(f"AgentExecution activity check failed: {e}")

            is_healthy = total_agents >= 50
            status_level = 'healthy' if total_agents >= 70 else ('degraded' if total_agents >= 50 else 'critical')

            response_time_ms = int((time.time() - start) * 1000)

            return {
                'name': self.COMPONENTS['organs']['name'],
                'status': status_level,
                'is_healthy': is_healthy,
                'response_time_ms': response_time_ms,
                'details': {
                    'total_agents': total_agents,
                    'active_agents': total_agents,
                    'recent_activity_1h': recent_activity,
                },
            }
        except Exception as e:
            return {
                'name': self.COMPONENTS['organs']['name'],
                'status': 'critical',
                'is_healthy': False,
                'response_time_ms': int((time.time() - start) * 1000),
                'error': str(e),
                'details': {},
            }

    def check_sensory(self) -> Dict:
        """Check spider network activity."""
        start = time.time()
        try:
            from ai_core.spiders.spider_registry import get_spider_registry

            registry = get_spider_registry()
            spider_count_info = registry.get_spider_count()
            spider_count = spider_count_info.get('total', 0)

            # Check recent spider executions
            recent_executions = 0
            try:
                from core.models_unified_system import SpiderExecutionLog
                thirty_min_ago = timezone.now() - timedelta(minutes=30)
                recent_executions = SpiderExecutionLog.objects.filter(
                    started_at__gte=thirty_min_ago
                ).count()
            except Exception as e:
                logger.warning(f"SpiderExecutionLog check failed: {e}")

            is_healthy = spider_count >= 50
            status_level = 'healthy' if spider_count >= 70 else ('degraded' if spider_count >= 50 else 'critical')

            response_time_ms = int((time.time() - start) * 1000)

            return {
                'name': self.COMPONENTS['sensory']['name'],
                'status': status_level,
                'is_healthy': is_healthy,
                'response_time_ms': response_time_ms,
                'details': {
                    'total_spiders': spider_count,
                    'categories': spider_count_info.get('by_category', {}),
                    'recent_executions_30m': recent_executions,
                },
            }
        except Exception as e:
            return {
                'name': self.COMPONENTS['sensory']['name'],
                'status': 'critical',
                'is_healthy': False,
                'response_time_ms': int((time.time() - start) * 1000),
                'error': str(e),
                'details': {},
            }

    def check_skin(self) -> Dict:
        """Check workspace manager availability."""
        start = time.time()
        try:
            # Check that the workspace module can be imported
            from core.services.workspace_manager import WorkspaceManager  # noqa: F401

            # Count workspaces
            from core.models_skin_layer import ProjectWorkspace
            workspace_count = ProjectWorkspace.objects.filter(is_active=True).count()

            # Check recent workspace operations
            recent_ops = 0
            try:
                from core.models_skin_layer import WorkspaceOperation
                one_hour_ago = timezone.now() - timedelta(hours=1)
                recent_ops = WorkspaceOperation.objects.filter(
                    created_at__gte=one_hour_ago
                ).count()
            except Exception as e:
                logger.warning(f"WorkspaceOperation check failed: {e}")

            response_time_ms = int((time.time() - start) * 1000)

            return {
                'name': self.COMPONENTS['skin']['name'],
                'status': 'healthy',
                'is_healthy': True,
                'response_time_ms': response_time_ms,
                'details': {
                    'workspaces': workspace_count,
                    'recent_operations_1h': recent_ops,
                    'manager_available': True,
                },
            }
        except Exception as e:
            return {
                'name': self.COMPONENTS['skin']['name'],
                'status': 'degraded',
                'is_healthy': True,  # SKIN is optional, not critical
                'response_time_ms': int((time.time() - start) * 1000),
                'error': str(e),
                'details': {},
            }

    def check_memory(self) -> Dict:
        """Check database and Redis connectivity."""
        start = time.time()
        db_ok = False
        redis_ok = False
        errors = []

        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_ok = True
        except Exception as e:
            errors.append(f"Database: {e}")

        # Check Redis
        try:
            import redis
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
            r.ping()
            redis_ok = True
        except Exception as e:
            errors.append(f"Redis: {e}")

        is_healthy = db_ok and redis_ok
        if is_healthy:
            status_level = 'healthy'
        elif db_ok:  # DB ok, Redis down
            status_level = 'degraded'
        else:
            status_level = 'critical'

        response_time_ms = int((time.time() - start) * 1000)

        result = {
            'name': self.COMPONENTS['memory']['name'],
            'status': status_level,
            'is_healthy': is_healthy,
            'response_time_ms': response_time_ms,
            'details': {
                'database': 'connected' if db_ok else 'disconnected',
                'redis': 'connected' if redis_ok else 'disconnected',
            },
        }

        if errors:
            result['error'] = '; '.join(errors)

        return result

    def check_celery(self) -> Dict:
        """
        Session 744: Check Celery worker and beat scheduler health.

        This is CRITICAL - without healthy Celery, 150+ scheduled tasks
        cannot execute and the autonomous system is dormant.
        """
        start = time.time()
        try:
            from core.services.celery_health import get_celery_health_service

            celery_service = get_celery_health_service()
            status = celery_service.get_quick_status()

            workers_online = status.get('workers_online', 0)
            beat_running = status.get('beat_running', False)

            # Determine health status
            # Session 758: 1 worker + beat is healthy for solo pool setup
            if workers_online >= 1 and beat_running:
                status_level = 'healthy'
                is_healthy = True
            elif workers_online >= 1 or beat_running:
                status_level = 'degraded'
                is_healthy = True
            else:
                status_level = 'critical'
                is_healthy = False

            response_time_ms = int((time.time() - start) * 1000)

            return {
                'name': self.COMPONENTS['celery']['name'],
                'status': status_level,
                'is_healthy': is_healthy,
                'response_time_ms': response_time_ms,
                'details': {
                    'workers_online': workers_online,
                    'beat_running': beat_running,
                    'scheduled_tasks': 150,  # Approximate count
                },
            }
        except Exception as e:
            return {
                'name': self.COMPONENTS['celery']['name'],
                'status': 'critical',
                'is_healthy': False,
                'response_time_ms': int((time.time() - start) * 1000),
                'error': str(e),
                'details': {},
            }

    def check_resolve_node(self) -> Dict:
        """Check DaVinci Resolve render node health."""
        start = time.time()
        try:
            import json as _json
            import urllib.request

            resolve_url = os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001')
            req = urllib.request.Request(f'{resolve_url}/health', method='GET')
            req.add_header('Accept', 'application/json')
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = _json.loads(resp.read())

            queue_size = body.get('queue_size', 0)
            active_jobs = body.get('active_jobs', 0)
            demo_mode = body.get('demo_mode', False)
            response_time_ms = int((time.time() - start) * 1000)

            return {
                'name': self.COMPONENTS['resolve_node']['name'],
                'status': 'healthy',
                'is_healthy': True,
                'response_time_ms': response_time_ms,
                'details': {
                    'queue_size': queue_size,
                    'active_jobs': active_jobs,
                    'demo_mode': demo_mode,
                    'url': resolve_url,
                },
            }
        except Exception as e:
            response_time_ms = int((time.time() - start) * 1000)
            # Resolve node being unreachable is degraded, not critical —
            # the platform functions without it, just can't render videos
            return {
                'name': self.COMPONENTS['resolve_node']['name'],
                'status': 'degraded',
                'is_healthy': False,
                'response_time_ms': response_time_ms,
                'error': str(e)[:200],
                'details': {
                    'url': os.environ.get('RESOLVE_NODE_URL', 'http://localhost:5001'),
                },
            }

    def _update_component_status(self, component_id: str, result: Dict):
        """Update component status in database."""
        from core.models_heart import ComponentStatus

        try:
            status_record, _ = ComponentStatus.objects.get_or_create(
                component=component_id,
                defaults={
                    'display_name': result.get('name', component_id),
                    'description': self.COMPONENTS.get(component_id, {}).get('description', ''),
                }
            )

            now = timezone.now()
            status_record.status = result.get('status', 'healthy')
            status_record.is_healthy = result.get('is_healthy', False)
            status_record.last_check = now
            status_record.response_time_ms = result.get('response_time_ms')
            status_record.details = result.get('details', {})
            status_record.last_error = result.get('error', '')
            status_record.check_count_24h += 1

            if result.get('is_healthy'):
                status_record.last_healthy = now
            else:
                status_record.error_count_24h += 1

            status_record.save()

        except Exception as e:
            logger.error(f"Failed to update component status for {component_id}: {e}")

    def is_alive(self) -> bool:
        """Quick check - is system healthy enough to operate?"""
        if self._last_pulse:
            return self._last_pulse.get('is_alive', False)

        # Run quick check.
        # Session 1103c: was 'except Exception: return False' which
        # silently flipped HEART to "down" on any DB exception (even
        # transient connection-pool hiccups), and downstream gates
        # would block agent execution with no forensic trail. Now
        # logs the failure type so transient drops are visible.
        try:
            # Just check database
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.warning(
                "heart.is_alive: DB ping failed (%s: %s) — returning "
                "False, downstream is_alive gates will block",
                type(e).__name__, e,
            )
            return False

    def get_vitals(self) -> Dict:
        """Get current component statuses from cache (fast)."""
        from core.models_heart import ComponentStatus

        components = ComponentStatus.get_all_vitals()

        # Calculate overall status from component health
        total = len(components)
        healthy = sum(1 for c in components.values() if c.get('is_healthy', False))
        health_score = (healthy / total * 100) if total > 0 else 0

        # Determine overall status
        if health_score >= 80:
            overall_status = 'healthy'
        elif health_score >= 50:
            overall_status = 'degraded'
        else:
            overall_status = 'critical'

        return {
            'overall_status': overall_status,
            'health_score': health_score,
            'components_healthy': healthy,
            'components_checked': total,
            'components': components,
        }

    def record_heartbeat(self, pulse_result: Dict) -> 'HeartBeat':
        """Save heartbeat to database."""
        from core.models_heart import HeartBeat

        heartbeat = HeartBeat.objects.create(
            health_score=pulse_result['health_score'],
            overall_status=pulse_result['overall_status'],
            is_alive=pulse_result['is_alive'],
            components=pulse_result['components'],
            check_duration_ms=pulse_result['check_duration_ms'],
            components_checked=pulse_result['components_checked'],
            components_healthy=pulse_result['components_healthy'],
            recorded_at=timezone.now(),
        )

        logger.info(f"💓 Heartbeat recorded: {heartbeat.id}")
        return heartbeat

    def alert_if_critical(self, pulse_result: Dict) -> bool:
        """Send Discord alert if status is critical."""
        if pulse_result.get('overall_status') != 'critical':
            return False

        try:
            from core.services.discord_notifications import DiscordNotificationService

            # Find failing components
            failing = [
                f"• {c['name']}: {c.get('error', 'unhealthy')}"
                for cid, c in pulse_result.get('components', {}).items()
                if not c.get('is_healthy', True)
            ]

            message = (
                f"🚨 **CRITICAL: System Health Alert**\n\n"
                f"Health Score: {pulse_result['health_score']}%\n"
                f"Status: {pulse_result['overall_status'].upper()}\n\n"
                f"**Failing Components:**\n" + '\n'.join(failing)
            )

            discord = DiscordNotificationService()
            discord.send_system_alert(message)

            # Mark heartbeat as alerted
            logger.warning(f"🚨 CRITICAL health alert sent to Discord")
            return True

        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False

    def get_history(self, hours: int = 24, limit: int = 100) -> list:
        """Get heartbeat history for the last N hours."""
        from core.models_heart import HeartBeat

        cutoff = timezone.now() - timedelta(hours=hours)
        heartbeats = HeartBeat.objects.filter(
            recorded_at__gte=cutoff
        ).order_by('-recorded_at')[:limit]

        return [
            {
                'id': str(hb.id),
                'timestamp': hb.recorded_at.isoformat(),
                'health_score': hb.health_score,
                'overall_status': hb.overall_status,
                'is_alive': hb.is_alive,
                'components_healthy': hb.components_healthy,
                'components_checked': hb.components_checked,
                'check_duration_ms': hb.check_duration_ms,
            }
            for hb in heartbeats
        ]
