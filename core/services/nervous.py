"""
Session 724: NERVOUS SYSTEM Service - WebSocket Communication Monitoring

The NERVOUS system monitors real-time WebSocket communication - tracking
connections, message throughput, latency, and channel layer health.

Human Body Metaphor:
- Nerves = WebSocket connections
- Nerve signals = WebSocket messages
- Synapses = Redis channel layer
- Neural pathways = Message routing
"""

import logging
import time
import re
from datetime import datetime, timedelta
from typing import Optional
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


_nervous_instance: Optional['NervousService'] = None


def get_nervous_service() -> 'NervousService':
    """Get the singleton NervousService instance."""
    global _nervous_instance
    if _nervous_instance is None:
        _nervous_instance = NervousService()
    return _nervous_instance


class NervousService:
    """
    WebSocket communication monitoring - the nervous system of the AI body.

    Monitors:
    - WebSocket connection health
    - Message throughput
    - Channel layer (Redis) connectivity
    - Consumer activity and errors
    """

    # Status thresholds (based on health score)
    RESPONSIVE_THRESHOLD = 80.0   # 80-100%
    ACTIVE_THRESHOLD = 60.0       # 60-79%
    SLUGGISH_THRESHOLD = 40.0     # 40-59%
    NUMB_THRESHOLD = 20.0         # 20-39%
    # Below 20% = damaged/dormant

    # Cache duration
    CACHE_DURATION = timedelta(seconds=60)

    def __init__(self):
        self._cache = None
        self._cache_time = None

    def feel(self, force: bool = False) -> dict:
        """
        Run full nervous system check.

        Returns comprehensive metrics about WebSocket health.
        """
        start_time = time.time()

        try:
            # Gather all metrics
            channel_layer_status = self._check_channel_layer()
            consumer_stats = self._get_consumer_stats()
            connection_stats = self._get_connection_stats()
            message_stats = self._get_message_stats()

            # Calculate health score
            health_score = self._calculate_health_score(
                channel_layer_status,
                consumer_stats,
                connection_stats,
                message_stats
            )

            # Determine status
            status = self._determine_status(health_score, connection_stats, message_stats)

            # Calculate check duration
            check_duration_ms = int((time.time() - start_time) * 1000)

            result = {
                'timestamp': timezone.now().isoformat(),
                'status': status,
                'health_score': round(health_score, 1),
                'is_healthy': health_score >= self.SLUGGISH_THRESHOLD,
                'check_duration_ms': check_duration_ms,

                # Channel layer (Redis)
                'channel_layer': channel_layer_status,

                # Consumers
                'consumers': consumer_stats,

                # Connections
                'connections': connection_stats,

                # Messages
                'messages': message_stats,

                # Activity level
                'activity_level': self._determine_activity_level(message_stats),

                # Issues detected
                'issues': self._detect_issues(
                    channel_layer_status,
                    consumer_stats,
                    connection_stats,
                    message_stats
                ),
            }

            # Save to database
            self._save_pulse(result)
            self._update_status(result)

            # Cache result
            self._cache = result
            self._cache_time = timezone.now()

            return result

        except Exception as e:
            logger.error(f"[NERVOUS] Feel check failed: {e}")
            return {
                'timestamp': timezone.now().isoformat(),
                'status': 'damaged',
                'health_score': 0,
                'is_healthy': False,
                'error': str(e),
                'check_duration_ms': int((time.time() - start_time) * 1000),
            }

    def get_status(self) -> dict:
        """Get cached nervous status (fast)."""
        # Return cached if fresh
        if (self._cache is not None and self._cache_time is not None and
                timezone.now() - self._cache_time < self.CACHE_DURATION):
            return self._cache

        # Try to get from database
        try:
            from core.models_nervous import NervousStatus
            status = NervousStatus.get_current()
            return {
                'timestamp': status.last_check.isoformat() if status.last_check else None,
                'status': status.status,
                'health_score': status.health_score,
                'is_healthy': status.is_healthy,
                'total_consumers': status.total_consumers,
                'active_connections': status.active_connections,
                'messages_24h': status.messages_24h,
                'messages_per_second': status.messages_per_second,
                'avg_latency_ms': status.avg_latency_ms,
                'channel_layer_healthy': status.channel_layer_healthy,
                'activity_level': status.activity_level,
                'error_rate': status.error_rate,
            }
        except Exception as e:
            logger.error(f"[NERVOUS] Failed to get status: {e}")
            return self.feel()

    def is_responsive(self) -> bool:
        """Quick check - is the nervous system responsive?"""
        try:
            status = self.get_status()
            return status.get('is_healthy', False)
        except Exception as _e:
            logger.warning(
                "nervous.is_responsive: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return False

    def get_vitals(self) -> dict:
        """Get current nervous vitals for body coordinator."""
        status = self.get_status()
        return {
            'status': status.get('status', 'unknown'),
            'health_score': status.get('health_score', 0),
            'is_healthy': status.get('is_healthy', False),
            'active_connections': status.get('active_connections', 0),
            'messages_per_second': status.get('messages_per_second', 0),
            'channel_layer_healthy': status.get('channel_layer_healthy', False),
        }

    def get_history(self, hours: int = 24, limit: int = 100) -> list:
        """Get nervous pulse history."""
        try:
            from core.models_nervous import NervousPulse

            cutoff = timezone.now() - timedelta(hours=hours)
            pulses = NervousPulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('-recorded_at')[:limit]

            return [
                {
                    'id': str(p.id),
                    'timestamp': p.recorded_at.isoformat(),
                    'status': p.status,
                    'health_score': p.health_score,
                    'active_connections': p.active_connections,
                    'messages_sent_24h': p.messages_sent_24h,
                    'avg_latency_ms': p.avg_latency_ms,
                    'channel_layer_connected': p.channel_layer_connected,
                }
                for p in pulses
            ]
        except Exception as e:
            logger.error(f"[NERVOUS] Failed to get history: {e}")
            return []

    def get_consumers_summary(self) -> dict:
        """Get summary of all WebSocket consumers."""
        return self._get_consumer_stats()

    def _check_channel_layer(self) -> dict:
        """Check Redis channel layer connectivity."""
        try:
            from channels.layers import get_channel_layer
            import asyncio

            channel_layer = get_channel_layer()

            if channel_layer is None:
                return {
                    'connected': False,
                    'error': 'No channel layer configured',
                    'redis_ping_ms': 0,
                }

            # Test Redis connectivity
            start = time.time()
            try:
                import redis
                hosts = getattr(settings, 'CHANNEL_LAYERS', {}).get('default', {}).get('CONFIG', {}).get('hosts', [('127.0.0.1', 6379)])

                r = None
                display_host = 'unknown'

                if isinstance(hosts, list) and hosts:
                    first = hosts[0]
                    if isinstance(first, str):
                        # URL string (e.g. from REDIS_URL env var)
                        r = redis.from_url(first, socket_timeout=2)
                        # Mask credentials in URL for display
                        _cred_pattern = r'://.*@'
                        display_host = re.sub(_cred_pattern, '://***@', first).split('?')[0]
                    elif isinstance(first, tuple) and len(first) >= 2:
                        # Tuple like ('127.0.0.1', 6379)
                        r = redis.Redis(host=first[0], port=first[1], socket_timeout=2)
                        display_host = f"{first[0]}:{first[1]}"

                if r is None:
                    # Fallback: try REDIS_URL from settings or localhost
                    fallback_url = getattr(settings, 'REDIS_URL', None)
                    if fallback_url:
                        r = redis.from_url(fallback_url, socket_timeout=2)
                    else:
                        r = redis.Redis(host='127.0.0.1', port=6379, socket_timeout=2)
                    display_host = 'redis-fallback'

                r.ping()
                ping_ms = (time.time() - start) * 1000

                # Get some Redis stats
                info = r.info('clients')
                connected_clients = info.get('connected_clients', 0)

                return {
                    'connected': True,
                    'redis_ping_ms': round(ping_ms, 2),
                    'redis_clients': connected_clients,
                    'host': display_host,
                }
            except Exception as e:
                return {
                    'connected': False,
                    'error': str(e),
                    'redis_ping_ms': 0,
                }

        except Exception as e:
            logger.error(f"[NERVOUS] Channel layer check failed: {e}")
            return {
                'connected': False,
                'error': str(e),
                'redis_ping_ms': 0,
            }

    def _get_consumer_stats(self) -> dict:
        """Get statistics about WebSocket consumers.

        Session 1000B: Avoid importing core.routing — it triggers a cascade
        that loads all consumer classes, PA system, and SentenceTransformer
        (~80MB+), which OOM kills Celery workers. Instead, use sys.modules
        to read the routing only if already loaded (i.e. in Daphne/ASGI),
        otherwise return lightweight static counts.
        """
        import sys

        try:
            # Only inspect routing if already imported (ASGI server context)
            routing = sys.modules.get('core.routing')
            if routing is None:
                # In Celery context — return static counts to avoid heavy imports
                return {
                    'total_routes': 24,
                    'unique_consumers': 18,
                    'consumer_list': [],
                    'note': 'static_counts_celery_context',
                }

            patterns = getattr(routing, 'websocket_urlpatterns', [])
            total_routes = len(patterns)

            # Extract unique consumer classes
            consumers = set()
            for pattern in patterns:
                callback = getattr(pattern, 'callback', None)
                if callback:
                    cls = getattr(callback, 'cls', None) or callback
                    if cls:
                        name = cls.__name__ if hasattr(cls, '__name__') else str(cls)
                        consumers.add(name)

            return {
                'total_routes': total_routes,
                'unique_consumers': len(consumers),
                'consumer_list': sorted(list(consumers)),
            }

        except Exception as e:
            logger.error(f"[NERVOUS] Consumer stats failed: {e}")
            return {
                'total_routes': 0,
                'unique_consumers': 0,
                'error': str(e),
            }

    def _get_connection_stats(self) -> dict:
        """Get WebSocket connection statistics."""
        try:
            from core.models_nervous import WebSocketConnectionLog

            now = timezone.now()
            day_ago = now - timedelta(hours=24)

            # Get connection logs from last 24h
            logs = WebSocketConnectionLog.objects.filter(created_at__gte=day_ago)

            connects = logs.filter(event='connect').count()
            disconnects = logs.filter(event='disconnect').count()
            errors = logs.filter(event='error').count()

            # Estimate active connections (connects - disconnects)
            # This is approximate since we don't track persistent state
            active_estimate = max(0, connects - disconnects)

            # Get most active consumers
            from django.db.models import Count
            top_consumers = logs.values('consumer_name').annotate(
                count=Count('id')
            ).order_by('-count')[:5]

            return {
                'active_estimate': active_estimate,
                'connects_24h': connects,
                'disconnects_24h': disconnects,
                'errors_24h': errors,
                'error_rate': round(errors / max(1, connects) * 100, 2),
                'top_consumers': list(top_consumers),
                'has_data': logs.exists(),
            }

        except Exception as e:
            logger.error(f"[NERVOUS] Connection stats failed: {e}")
            # Return estimated stats based on routes
            return {
                'active_estimate': 0,
                'connects_24h': 0,
                'disconnects_24h': 0,
                'errors_24h': 0,
                'error_rate': 0,
                'has_data': False,
                'note': 'Connection logging not yet active',
            }

    def _get_message_stats(self) -> dict:
        """Get message throughput statistics from CeleryTaskEvent."""
        try:
            from core.models_celery_telemetry import CeleryTaskEvent

            now = timezone.now()
            day_ago = now - timedelta(hours=24)
            count_24h = CeleryTaskEvent.objects.filter(started_at__gte=day_ago).count()
            mps = round(count_24h / 86400, 4) if count_24h > 0 else 0

            return {
                'messages_24h': count_24h,
                'messages_per_second': mps,
                'avg_latency_ms': 0,
            }
        except Exception as e:
            logger.warning(f"[NERVOUS] CeleryTaskEvent query failed (table may not exist): {e}")
            return {
                'messages_24h': 0,
                'messages_per_second': 0,
                'avg_latency_ms': 0,
                'note': 'CeleryTaskEvent unavailable',
            }

    def _calculate_health_score(
        self,
        channel_layer: dict,
        consumers: dict,
        connections: dict,
        messages: dict
    ) -> float:
        """Calculate overall nervous system health score."""
        score = 100.0

        # Channel layer health (40% weight)
        if not channel_layer.get('connected', False):
            score -= 40  # Critical - no Redis
        else:
            # Penalize high latency
            ping_ms = channel_layer.get('redis_ping_ms', 0)
            if ping_ms > 100:
                score -= 10
            elif ping_ms > 50:
                score -= 5

        # Consumer availability (20% weight)
        total_consumers = consumers.get('unique_consumers', 0)
        if total_consumers == 0:
            score -= 20  # No consumers registered
        elif total_consumers < 10:
            score -= 10  # Few consumers

        # Connection health (20% weight)
        error_rate = connections.get('error_rate', 0)
        if error_rate > 20:
            score -= 20
        elif error_rate > 10:
            score -= 10
        elif error_rate > 5:
            score -= 5

        # Activity (20% weight)
        if messages.get('messages_24h', 0) == 0 and 'note' not in messages:
            # Genuinely zero activity (tracking is wired but nothing happened)
            score -= 10

        return max(0, min(100, score))

    def _determine_status(
        self,
        health_score: float,
        connections: dict,
        messages: dict
    ) -> str:
        """Determine nervous system status from metrics."""
        if health_score >= self.RESPONSIVE_THRESHOLD:
            return 'responsive'
        elif health_score >= self.ACTIVE_THRESHOLD:
            return 'active'
        elif health_score >= self.SLUGGISH_THRESHOLD:
            return 'sluggish'
        elif health_score >= self.NUMB_THRESHOLD:
            return 'numb'
        elif health_score > 0:
            return 'damaged'
        else:
            return 'dormant'

    def _determine_activity_level(self, messages: dict) -> str:
        """Determine activity level from message throughput."""
        mps = messages.get('messages_per_second', 0)
        if mps == 0:
            return 'dormant'
        elif mps < 1:
            return 'low'
        elif mps < 10:
            return 'normal'
        elif mps < 50:
            return 'high'
        else:
            return 'intense'

    def _detect_issues(
        self,
        channel_layer: dict,
        consumers: dict,
        connections: dict,
        messages: dict
    ) -> list:
        """Detect issues with the nervous system."""
        issues = []

        # Channel layer issues
        if not channel_layer.get('connected', False):
            issues.append({
                'severity': 'critical',
                'component': 'channel_layer',
                'message': 'Redis channel layer disconnected - WebSockets will not work',
            })
        elif channel_layer.get('redis_ping_ms', 0) > 100:
            issues.append({
                'severity': 'warning',
                'component': 'channel_layer',
                'message': f"High Redis latency: {channel_layer.get('redis_ping_ms')}ms",
            })

        # Consumer issues
        if consumers.get('unique_consumers', 0) == 0:
            issues.append({
                'severity': 'critical',
                'component': 'consumers',
                'message': 'No WebSocket consumers registered',
            })

        # Connection issues
        error_rate = connections.get('error_rate', 0)
        if error_rate > 10:
            issues.append({
                'severity': 'warning',
                'component': 'connections',
                'message': f"High connection error rate: {error_rate}%",
            })

        return issues

    def _save_pulse(self, result: dict) -> None:
        """Save nervous pulse to database."""
        try:
            from core.models_nervous import NervousPulse

            NervousPulse.objects.create(
                status=result.get('status', 'unknown'),
                health_score=result.get('health_score', 0),
                total_consumers=result.get('consumers', {}).get('unique_consumers', 0),
                active_connections=result.get('connections', {}).get('active_estimate', 0),
                disconnections_24h=result.get('connections', {}).get('disconnects_24h', 0),
                connection_errors_24h=result.get('connections', {}).get('errors_24h', 0),
                messages_sent_24h=result.get('messages', {}).get('messages_24h', 0),
                messages_per_second=result.get('messages', {}).get('messages_per_second', 0),
                avg_latency_ms=result.get('messages', {}).get('avg_latency_ms', 0),
                channel_layer_connected=result.get('channel_layer', {}).get('connected', False),
                redis_ping_ms=result.get('channel_layer', {}).get('redis_ping_ms', 0),
                consumer_stats=result.get('consumers', {}),
                check_duration_ms=result.get('check_duration_ms', 0),
            )
        except Exception as e:
            logger.error(f"[NERVOUS] Failed to save pulse: {e}")

    def _update_status(self, result: dict) -> None:
        """Update cached nervous status."""
        try:
            from core.models_nervous import NervousStatus

            status = NervousStatus.get_current()
            status.status = result.get('status', 'unknown')
            status.is_healthy = result.get('is_healthy', False)
            status.health_score = result.get('health_score', 0)
            status.total_consumers = result.get('consumers', {}).get('unique_consumers', 0)
            status.active_connections = result.get('connections', {}).get('active_estimate', 0)
            status.messages_24h = result.get('messages', {}).get('messages_24h', 0)
            status.messages_per_second = result.get('messages', {}).get('messages_per_second', 0)
            status.avg_latency_ms = result.get('messages', {}).get('avg_latency_ms', 0)
            status.channel_layer_healthy = result.get('channel_layer', {}).get('connected', False)
            status.redis_latency_ms = result.get('channel_layer', {}).get('redis_ping_ms', 0)
            status.activity_level = result.get('activity_level', 'normal')
            status.error_rate = result.get('connections', {}).get('error_rate', 0)
            status.disconnections_24h = result.get('connections', {}).get('disconnects_24h', 0)
            status.save()
        except Exception as e:
            logger.error(f"[NERVOUS] Failed to update status: {e}")
