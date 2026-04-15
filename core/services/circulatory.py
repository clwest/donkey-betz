"""
Session 703: CIRCULATORY SYSTEM Service

The circulation of the AI body - monitors data flow health across:
- Redis queues (cache, broker, results)
- Celery task queues (default, long_running, broadcast)
- WebSocket channels
- Event streams (spider_data, opportunity_scored, etc.)

Human Body Metaphor:
- Blood = Data flowing through the system
- Arteries = Outbound channels (Redis pub, Celery, WebSocket broadcasts)
- Veins = Inbound channels (Spider data, API requests, consumers)
- Blood Pressure = Queue depth / backpressure
- Circulation Time = End-to-end latency
- Clot/Blockage = Stuck queue, bottleneck
"""

import logging
import os
import time
from datetime import timedelta
from typing import Dict, List, Optional, Tuple

import redis
from django.conf import settings
from django.db.models import Avg, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

# Singleton instance
_circulatory_instance: Optional['CirculatorySystemService'] = None


def get_circulatory_system() -> 'CirculatorySystemService':
    """Get the singleton CirculatorySystemService instance."""
    global _circulatory_instance
    if _circulatory_instance is None:
        _circulatory_instance = CirculatorySystemService()
    return _circulatory_instance


class CirculatorySystemService:
    """
    Data flow monitoring service - the circulation of the AI body.

    Monitors Redis queues, Celery task queues, WebSocket channels,
    and event streams for health, throughput, and bottlenecks.
    """

    # Status thresholds
    FLOWING_THRESHOLD = 80    # 80-100% = flowing
    SLOW_THRESHOLD = 50       # 50-79% = slow
    CONGESTED_THRESHOLD = 20  # 20-49% = congested
    # 0-19% = blocked

    def __init__(self):
        self._initialized = False
        self._last_result: Optional[Dict] = None
        self._redis_clients: Dict[str, redis.Redis] = {}
        self._initialize()

    def _initialize(self):
        """Initialize service and Redis connections."""
        if self._initialized:
            return

        logger.info("🩸 CirculatorySystemService initializing...")

        # Initialize Redis clients for each database
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            self._redis_clients = {
                'cache': redis.Redis.from_url(redis_url, db=1, decode_responses=True),
                'broker': redis.Redis.from_url(redis_url, db=2, decode_responses=True),
                'results': redis.Redis.from_url(redis_url, db=3, decode_responses=True),
                'channels': redis.Redis.from_url(redis_url, db=0, decode_responses=True),
            }
        except Exception as e:
            logger.warning(f"🩸 Redis connection setup warning: {e}")

        self._initialized = True
        logger.info("🩸 CirculatorySystemService ready")

    def circulate(self) -> Dict:
        """
        Run full circulation check - monitor all data flows.

        Returns comprehensive status including:
        - Overall flow score
        - Per-route status
        - Detected bottlenecks
        - Flow metrics (throughput, latency, depth)
        """
        from core.models_circulatory import FlowRoute, CirculationPulse, FlowStatus

        start_time = time.time()
        logger.info("🩸 Running circulation check...")

        route_results = {}
        total_depth = 0
        total_throughput = 0.0
        latencies = []
        bottlenecks = []

        # Get all active routes
        routes = FlowRoute.objects.filter(is_active=True)

        for route in routes:
            try:
                result = self._check_route(route)
                route_results[route.name] = result

                # Aggregate metrics
                total_depth += result.get('current_depth', 0)
                total_throughput += result.get('throughput', 0)
                if result.get('latency_ms', 0) > 0:
                    latencies.append(result['latency_ms'])

                # Update FlowStatus
                self._update_flow_status(route, result)

                # Check for bottlenecks
                if result.get('bottleneck'):
                    bottlenecks.append(result['bottleneck'])

            except Exception as e:
                logger.error(f"🩸 Error checking route {route.name}: {e}")
                route_results[route.name] = {
                    'status': 'blocked',
                    'is_healthy': False,
                    'health_score': 0,
                    'error': str(e),
                }
                bottlenecks.append({
                    'route': route.name,
                    'issue': f'Check failed: {e}',
                    'severity': 'critical',
                })

        # Calculate overall metrics
        routes_by_status = {
            'flowing': 0,
            'slow': 0,
            'congested': 0,
            'blocked': 0,
        }
        health_scores = []

        for name, result in route_results.items():
            status = result.get('status', 'blocked')
            routes_by_status[status] = routes_by_status.get(status, 0) + 1
            health_scores.append(result.get('health_score', 0))

        # Calculate flow score (weighted average)
        flow_score = sum(health_scores) / len(health_scores) if health_scores else 100.0

        # Determine overall status
        if flow_score >= self.FLOWING_THRESHOLD:
            overall_status = 'flowing'
        elif flow_score >= self.SLOW_THRESHOLD:
            overall_status = 'slow'
        elif flow_score >= self.CONGESTED_THRESHOLD:
            overall_status = 'congested'
        else:
            overall_status = 'blocked'

        # Calculate check duration
        check_duration_ms = int((time.time() - start_time) * 1000)

        # Build result
        result = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': overall_status,
            'flow_score': round(flow_score, 1),
            'is_flowing': overall_status in ('flowing', 'slow'),
            'check_duration_ms': check_duration_ms,
            'routes_checked': len(routes),
            'routes_healthy': routes_by_status['flowing'],
            'routes_slow': routes_by_status['slow'],
            'routes_congested': routes_by_status['congested'],
            'routes_blocked': routes_by_status['blocked'],
            'flow_metrics': {
                'total_items_in_transit': total_depth,
                'total_throughput': round(total_throughput, 2),
                'avg_latency_ms': round(sum(latencies) / len(latencies), 2) if latencies else 0,
                'max_latency_ms': max(latencies) if latencies else 0,
            },
            'routes': route_results,
            'bottlenecks': bottlenecks,
            'bottleneck_count': len(bottlenecks),
        }

        # Record pulse
        self._record_pulse(result)

        # Alert if needed
        self._check_and_alert(result)

        self._last_result = result
        logger.info(f"🩸 Circulation check complete: {overall_status} ({flow_score:.1f}%) - {check_duration_ms}ms")

        return result

    def _check_route(self, route) -> Dict:
        """Check a specific route's health."""
        if route.route_type == 'redis_queue':
            return self._check_redis_route(route)
        elif route.route_type == 'celery_queue':
            return self._check_celery_route(route)
        elif route.route_type == 'websocket':
            return self._check_websocket_route(route)
        elif route.route_type == 'event_stream':
            return self._check_event_stream_route(route)
        else:
            return {'status': 'blocked', 'is_healthy': False, 'error': f'Unknown route type: {route.route_type}'}

    def _check_redis_route(self, route) -> Dict:
        """Check Redis queue health."""
        try:
            # Determine which Redis client to use
            if 'db:1' in route.identifier or 'cache' in route.name:
                client = self._redis_clients.get('cache')
            elif 'db:2' in route.identifier or 'broker' in route.name:
                client = self._redis_clients.get('broker')
            elif 'db:3' in route.identifier or 'results' in route.name:
                client = self._redis_clients.get('results')
            else:
                client = self._redis_clients.get('cache')

            if not client:
                return {'status': 'blocked', 'is_healthy': False, 'health_score': 0, 'error': 'No Redis client'}

            # Ping to check connectivity
            start = time.time()
            client.ping()
            latency_ms = (time.time() - start) * 1000

            # Get info
            info = client.info('memory')
            used_memory = info.get('used_memory', 0)
            used_memory_human = info.get('used_memory_human', 'N/A')

            # Get connection count
            client_info = client.info('clients')
            connected_clients = client_info.get('connected_clients', 0)

            # Get DB-specific info
            db_info = client.info('keyspace')
            keys = 0
            for db_name, db_data in db_info.items():
                if isinstance(db_data, dict):
                    keys += db_data.get('keys', 0)

            # Calculate health score
            health_score = 100.0
            status = 'flowing'
            bottleneck = None

            # Latency check
            if latency_ms > route.max_latency_ms:
                health_score -= 40
                status = 'slow'
                bottleneck = {
                    'route': route.name,
                    'issue': f'High latency: {latency_ms:.0f}ms (max: {route.max_latency_ms}ms)',
                    'severity': 'warning',
                }

            # Memory check (if over 1GB, start deducting)
            if used_memory > 1_000_000_000:  # 1GB
                health_score -= 20
                if status == 'flowing':
                    status = 'slow'

            return {
                'status': status,
                'is_healthy': status in ('flowing', 'slow'),
                'health_score': max(0, health_score),
                'current_depth': keys,
                'throughput': 0,  # Redis doesn't easily expose this
                'latency_ms': round(latency_ms, 2),
                'details': {
                    'used_memory': used_memory_human,
                    'connected_clients': connected_clients,
                    'keys': keys,
                },
                'bottleneck': bottleneck,
            }

        except Exception as e:
            return {
                'status': 'blocked',
                'is_healthy': False,
                'health_score': 0,
                'error': str(e),
                'bottleneck': {
                    'route': route.name,
                    'issue': f'Redis connection failed: {e}',
                    'severity': 'critical',
                },
            }

    def _check_celery_route(self, route) -> Dict:
        """Check Celery queue health."""
        try:
            from celery import current_app

            queue_name = route.identifier

            # Get queue depth from Redis broker
            broker_client = self._redis_clients.get('broker')
            if broker_client:
                # Celery uses a list for the queue
                queue_key = queue_name if queue_name != 'celery' else 'celery'
                depth = broker_client.llen(queue_key)
            else:
                depth = 0

            # Try to get worker info (may timeout)
            active_workers = 0
            active_tasks = 0
            reserved_tasks = 0

            try:
                inspect = current_app.control.inspect(timeout=1.0)

                # Get active workers
                ping_result = inspect.ping()
                if ping_result:
                    active_workers = len(ping_result)

                # Get active tasks
                active = inspect.active()
                if active:
                    for worker_tasks in active.values():
                        if worker_tasks:
                            active_tasks += len(worker_tasks)

                # Get reserved tasks
                reserved = inspect.reserved()
                if reserved:
                    for worker_tasks in reserved.values():
                        if worker_tasks:
                            reserved_tasks += len(worker_tasks)

            except Exception as e:
                logger.debug(f"Celery inspect failed (workers may be offline): {e}")

            # Calculate health score
            health_score = 100.0
            status = 'flowing'
            bottleneck = None

            # Queue depth check
            if depth > route.max_depth:
                health_score -= 50
                status = 'congested'
                bottleneck = {
                    'route': route.name,
                    'issue': f'High queue depth: {depth}/{route.max_depth}',
                    'severity': 'warning' if depth < route.max_depth * 2 else 'critical',
                }
            elif depth > route.max_depth * 0.8:
                health_score -= 20
                status = 'slow'

            # Worker availability check
            if active_workers == 0 and depth > 0:
                health_score -= 30
                if status != 'congested':
                    status = 'slow'
                if not bottleneck:
                    bottleneck = {
                        'route': route.name,
                        'issue': f'No active workers with {depth} tasks queued',
                        'severity': 'warning',
                    }

            return {
                'status': status,
                'is_healthy': status in ('flowing', 'slow'),
                'health_score': max(0, health_score),
                'current_depth': depth,
                'throughput': 0,  # Would need historical data
                'latency_ms': 0,  # Would need task timing
                'active_workers': active_workers,
                'active_tasks': active_tasks,
                'reserved_tasks': reserved_tasks,
                'details': {
                    'queue_name': queue_name,
                    'workers': active_workers,
                    'processing': active_tasks,
                    'reserved': reserved_tasks,
                },
                'bottleneck': bottleneck,
            }

        except Exception as e:
            return {
                'status': 'blocked',
                'is_healthy': False,
                'health_score': 0,
                'error': str(e),
                'bottleneck': {
                    'route': route.name,
                    'issue': f'Celery check failed: {e}',
                    'severity': 'critical',
                },
            }

    def _check_websocket_route(self, route) -> Dict:
        """Check WebSocket channel layer health."""
        try:
            # Check Redis channel layer connectivity
            channels_client = self._redis_clients.get('channels')
            if not channels_client:
                return {
                    'status': 'blocked',
                    'is_healthy': False,
                    'health_score': 0,
                    'error': 'No channel layer client',
                }

            # Ping
            start = time.time()
            channels_client.ping()
            latency_ms = (time.time() - start) * 1000

            # Get channel info
            info = channels_client.info('clients')
            connected_clients = info.get('connected_clients', 0)

            # Check pubsub channels
            pubsub_info = channels_client.info('stats')
            pubsub_channels = pubsub_info.get('pubsub_channels', 0)

            # Calculate health
            health_score = 100.0
            status = 'flowing'

            if latency_ms > route.max_latency_ms:
                health_score -= 30
                status = 'slow'

            return {
                'status': status,
                'is_healthy': True,
                'health_score': health_score,
                'current_depth': pubsub_channels,
                'throughput': 0,
                'latency_ms': round(latency_ms, 2),
                'details': {
                    'connected_clients': connected_clients,
                    'pubsub_channels': pubsub_channels,
                },
                'bottleneck': None,
            }

        except Exception as e:
            return {
                'status': 'blocked',
                'is_healthy': False,
                'health_score': 0,
                'error': str(e),
            }

    def _check_event_stream_route(self, route) -> Dict:
        """Check Redis event stream health."""
        try:
            # Event streams are on broker Redis (db 2) or channels (db 0)
            client = self._redis_clients.get('broker') or self._redis_clients.get('cache')
            if not client:
                return {
                    'status': 'blocked',
                    'is_healthy': False,
                    'health_score': 0,
                    'error': 'No Redis client for event streams',
                }

            stream_name = route.identifier

            # Get stream length
            try:
                length = client.xlen(stream_name)
            except redis.ResponseError:
                # Stream might not exist yet
                length = 0

            # Get consumer groups and pending
            pending_count = 0
            try:
                groups = client.xinfo_groups(stream_name)
                for group in groups:
                    pending_count += group.get('pending', 0)
            except redis.ResponseError:
                # No consumer groups
                pass

            # Calculate health
            health_score = 100.0
            status = 'flowing'
            bottleneck = None

            if length > route.max_depth:
                health_score -= 40
                status = 'congested'
                bottleneck = {
                    'route': route.name,
                    'issue': f'Event stream backlog: {length}/{route.max_depth}',
                    'severity': 'warning',
                }
            elif length > route.max_depth * 0.8:
                health_score -= 20
                status = 'slow'

            # High pending count indicates slow consumers
            if pending_count > 100:
                health_score -= 20
                if status == 'flowing':
                    status = 'slow'

            return {
                'status': status,
                'is_healthy': status in ('flowing', 'slow'),
                'health_score': max(0, health_score),
                'current_depth': length,
                'throughput': 0,
                'latency_ms': 0,
                'details': {
                    'stream_length': length,
                    'pending_messages': pending_count,
                },
                'bottleneck': bottleneck,
            }

        except Exception as e:
            return {
                'status': 'blocked',
                'is_healthy': False,
                'health_score': 0,
                'error': str(e),
            }

    def _update_flow_status(self, route, result: Dict):
        """Update FlowStatus cache for a route."""
        from core.models_circulatory import FlowStatus

        try:
            status, created = FlowStatus.objects.get_or_create(
                route=route,
                defaults={
                    'status': result.get('status', 'flowing'),
                    'is_healthy': result.get('is_healthy', True),
                    'health_score': result.get('health_score', 100),
                }
            )

            if not created:
                status.update_status(
                    result.get('status', 'flowing'),
                    result.get('health_score', 100)
                )
                status.current_depth = result.get('current_depth', 0)
                status.current_throughput = result.get('throughput', 0)
                status.current_latency_ms = result.get('latency_ms', 0)
                status.active_workers = result.get('active_workers', 0)
                status.active_tasks = result.get('active_tasks', 0)
                status.reserved_tasks = result.get('reserved_tasks', 0)
                status.details = result.get('details', {})
                status.error_message = result.get('error', '')
                status.last_activity = timezone.now()
                status.save()

        except Exception as e:
            logger.error(f"Error updating FlowStatus for {route.name}: {e}")

    def _record_pulse(self, result: Dict):
        """Record circulation pulse to time-series table."""
        from core.models_circulatory import CirculationPulse

        try:
            CirculationPulse.objects.create(
                overall_status=result['overall_status'],
                flow_score=result['flow_score'],
                total_routes_checked=result['routes_checked'],
                routes_healthy=result['routes_healthy'],
                routes_slow=result['routes_slow'],
                routes_congested=result['routes_congested'],
                routes_blocked=result['routes_blocked'],
                total_items_in_transit=result['flow_metrics']['total_items_in_transit'],
                total_throughput=result['flow_metrics']['total_throughput'],
                avg_latency_ms=result['flow_metrics']['avg_latency_ms'],
                max_latency_ms=result['flow_metrics']['max_latency_ms'],
                bottlenecks=result['bottlenecks'],
                bottleneck_count=result['bottleneck_count'],
                route_details=result['routes'],
                check_duration_ms=result['check_duration_ms'],
            )
        except Exception as e:
            logger.error(f"Error recording circulation pulse: {e}")

    def _check_and_alert(self, result: Dict):
        """Send Discord alerts if critical issues detected."""
        if result['overall_status'] not in ('congested', 'blocked'):
            return

        # Check if we should alert (avoid spam)
        if result['overall_status'] == 'blocked':
            try:
                from core.services.discord_notifications import DiscordNotificationService
                discord = DiscordNotificationService()

                bottleneck_summary = '\n'.join([
                    f"- {b['route']}: {b['issue']}"
                    for b in result['bottlenecks'][:5]
                ])

                discord.send_system_alert(
                    f"🚨 **CIRCULATORY SYSTEM BLOCKED**\n\n"
                    f"Flow Score: {result['flow_score']:.1f}%\n"
                    f"Blocked Routes: {result['routes_blocked']}\n\n"
                    f"**Bottlenecks:**\n{bottleneck_summary}"
                )
            except Exception as e:
                logger.error(f"Failed to send Discord alert: {e}")

    # Public API methods

    def is_flowing(self) -> bool:
        """Quick check - is data flowing normally?"""
        from core.models_circulatory import FlowStatus

        try:
            blocked_count = FlowStatus.objects.filter(status='blocked').count()
            return blocked_count == 0
        except Exception as _e:
            logger.warning(
                "circulatory.is_flowing: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def get_vitals(self) -> Dict:
        """Get current flow vitals (cached status)."""
        from core.models_circulatory import FlowStatus, FlowRoute

        vitals = {
            'timestamp': timezone.now().isoformat(),
            'routes': {},
        }

        for status in FlowStatus.objects.select_related('route').all():
            vitals['routes'][status.route.name] = {
                'display_name': status.route.display_name,
                'status': status.status,
                'is_healthy': status.is_healthy,
                'health_score': status.health_score,
                'current_depth': status.current_depth,
                'throughput': status.current_throughput,
                'latency_ms': status.current_latency_ms,
                'last_check': status.last_check.isoformat() if status.last_check else None,
            }

        # Calculate overall
        statuses = FlowStatus.objects.all()
        if statuses.exists():
            avg_score = statuses.aggregate(avg=Avg('health_score'))['avg'] or 100
            vitals['overall_score'] = round(avg_score, 1)
            vitals['is_flowing'] = not statuses.filter(status='blocked').exists()
        else:
            vitals['overall_score'] = 100.0
            vitals['is_flowing'] = True

        # Session 712: Add overall_status for body_vitals compatibility
        vitals['overall_status'] = 'flowing' if vitals['is_flowing'] else 'blocked'
        vitals['flow_score'] = vitals['overall_score']

        return vitals

    def get_status(self) -> Dict:
        """Get current status for body coordinator integration."""
        vitals = self.get_vitals()
        # Convert is_flowing to overall_status string
        vitals['overall_status'] = 'flowing' if vitals.get('is_flowing', True) else 'blocked'
        return vitals

    def get_history(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get circulation pulse history."""
        from core.models_circulatory import CirculationPulse

        hours = max(1, min(168, hours))  # 1 hour to 1 week
        limit = max(1, min(1000, limit))

        since = timezone.now() - timedelta(hours=hours)
        pulses = CirculationPulse.objects.filter(
            recorded_at__gte=since
        ).order_by('-recorded_at')[:limit]

        return [
            {
                'recorded_at': p.recorded_at.isoformat(),
                'overall_status': p.overall_status,
                'flow_score': p.flow_score,
                'routes_checked': p.total_routes_checked,
                'routes_healthy': p.routes_healthy,
                'routes_blocked': p.routes_blocked,
                'total_items_in_transit': p.total_items_in_transit,
                'bottleneck_count': p.bottleneck_count,
                'check_duration_ms': p.check_duration_ms,
            }
            for p in pulses
        ]

    def detect_bottlenecks(self) -> List[Dict]:
        """Get current bottlenecks from cached status."""
        from core.models_circulatory import FlowStatus

        bottlenecks = []
        for status in FlowStatus.objects.select_related('route').filter(
            status__in=['congested', 'blocked']
        ):
            bottlenecks.append({
                'route': status.route.name,
                'display_name': status.route.display_name,
                'status': status.status,
                'health_score': status.health_score,
                'current_depth': status.current_depth,
                'error': status.error_message,
                'severity': 'critical' if status.status == 'blocked' else 'warning',
            })

        return bottlenecks

    def get_flow_velocity(self, hours: int = 1) -> Dict:
        """Calculate flow velocity metrics over the specified period."""
        from core.models_circulatory import CirculationPulse

        hours = max(1, min(24, hours))
        since = timezone.now() - timedelta(hours=hours)

        pulses = CirculationPulse.objects.filter(recorded_at__gte=since)
        count = pulses.count()

        if count == 0:
            return {
                'period_hours': hours,
                'samples': 0,
                'avg_flow_score': 100.0,
                'avg_throughput': 0,
                'avg_latency_ms': 0,
                'total_items_processed': 0,
            }

        agg = pulses.aggregate(
            avg_score=Avg('flow_score'),
            avg_throughput=Avg('total_throughput'),
            avg_latency=Avg('avg_latency_ms'),
            total_items=Sum('total_items_in_transit'),
        )

        return {
            'period_hours': hours,
            'samples': count,
            'avg_flow_score': round(agg['avg_score'] or 100, 1),
            'avg_throughput': round(agg['avg_throughput'] or 0, 2),
            'avg_latency_ms': round(agg['avg_latency'] or 0, 2),
            'total_items_processed': agg['total_items'] or 0,
        }

    def get_routes(self) -> List[Dict]:
        """Get all configured routes."""
        from core.models_circulatory import FlowRoute

        return [
            {
                'id': str(r.id),
                'name': r.name,
                'display_name': r.display_name,
                'route_type': r.route_type,
                'identifier': r.identifier,
                'max_depth': r.max_depth,
                'max_latency_ms': r.max_latency_ms,
                'is_active': r.is_active,
                'is_critical': r.is_critical,
            }
            for r in FlowRoute.objects.all()
        ]
