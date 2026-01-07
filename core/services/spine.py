"""
Session 704: SPINE - Central API Router Service

The SPINE is the backbone of the AI body - central request routing and coordination.
Tracks API metrics, provides health-aware routing, and manages request flow.

Key Features:
- Route pattern matching and metrics collection
- Health-aware routing (checks HEART/LUNGS before routing)
- Request tracing with correlation IDs
- Integration with HEART/LUNGS/CIRCULATORY services

Usage:
    from core.services.spine import get_spine_router

    spine = get_spine_router()

    # Run full alignment check
    result = spine.align()

    # Quick health check
    if spine.is_aligned():
        print("Spine is healthy")

    # Check if route is healthy
    can_route, reason = spine.can_route('/api/agents/')

    # Get route metrics
    metrics = spine.get_route_metrics('/api/agents/')
"""

import logging
import re
import uuid
from datetime import timedelta
from typing import Optional, Tuple

from django.db import transaction
from django.db.models import Avg, Count, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


# Singleton instance
_spine_instance: Optional['SpineRouterService'] = None


def get_spine_router() -> 'SpineRouterService':
    """Get the singleton SpineRouterService instance."""
    global _spine_instance
    if _spine_instance is None:
        _spine_instance = SpineRouterService()
    return _spine_instance


class SpineRouterService:
    """
    Central API Router - the backbone of the AI body.

    Tracks API metrics, provides health-aware routing, and manages request flow.
    Integrates with HEART (health), LUNGS (resources), and CIRCULATORY (data flow).
    """

    # Status thresholds
    ALIGNED_THRESHOLD = 90.0      # 90%+ = aligned
    STRAINED_THRESHOLD = 70.0     # 70-90% = strained
    COMPRESSED_THRESHOLD = 50.0   # 50-70% = compressed
    # Below 50% = injured

    # Cache duration
    CACHE_DURATION_SECONDS = 30

    def __init__(self):
        self._cached_status = None
        self._cache_time = None
        self._route_pattern_cache = {}
        self._pattern_regex_cache = {}

    def align(self, force: bool = False) -> dict:
        """
        Run full spine alignment check - the main health check method.

        Returns:
            dict: Comprehensive alignment status including:
                - overall_status: aligned/strained/compressed/injured
                - health_score: 0-100%
                - route metrics and health
                - integration status with HEART/LUNGS/CIRCULATORY
        """
        from core.models_spine import RoutePattern, RouteMetrics, SpineStatus

        start_time = timezone.now()

        # Get or create spine status record
        status, created = SpineStatus.objects.get_or_create(
            pk=uuid.UUID('00000000-0000-0000-0000-000000000001'),
            defaults={
                'status': 'aligned',
                'health_score': 100.0,
            }
        )

        # Check integration services
        heart_status = self._check_heart_status()
        lungs_status = self._check_lungs_status()
        circulatory_status = self._check_circulatory_status()

        # Get all active route patterns
        patterns = RoutePattern.objects.filter(is_active=True)

        # Calculate metrics per pattern
        pattern_results = {}
        healthy_count = 0
        degraded_count = 0
        failed_count = 0
        total_requests = 0
        total_errors = 0
        latency_sum = 0.0
        latency_count = 0

        for pattern in patterns:
            pattern_health = self._check_pattern_health(pattern)
            pattern_results[pattern.pattern] = pattern_health

            if pattern_health['is_healthy']:
                healthy_count += 1
            elif pattern_health['health_score'] >= 50:
                degraded_count += 1
            else:
                failed_count += 1

            # Aggregate metrics
            total_requests += pattern_health.get('total_requests', 0)
            total_errors += pattern_health.get('failed_requests', 0)
            if pattern_health.get('avg_latency_ms', 0) > 0:
                latency_sum += pattern_health['avg_latency_ms']
                latency_count += 1

        total_patterns = patterns.count()

        # Calculate overall health score
        health_score = self._calculate_health_score(
            healthy_count, degraded_count, failed_count, total_patterns,
            heart_status, lungs_status, circulatory_status
        )

        # Determine status
        if health_score >= self.ALIGNED_THRESHOLD:
            overall_status = 'aligned'
        elif health_score >= self.STRAINED_THRESHOLD:
            overall_status = 'strained'
        elif health_score >= self.COMPRESSED_THRESHOLD:
            overall_status = 'compressed'
        else:
            overall_status = 'injured'

        # Count blocked/rate-limited routes
        routes_blocked = sum(1 for p in pattern_results.values() if not p.get('can_route', True))
        routes_rate_limited = sum(1 for p in pattern_results.values() if p.get('is_rate_limited', False))
        fallbacks_active = sum(1 for p in pattern_results.values() if p.get('using_fallback', False))

        # Calculate averages
        avg_latency = latency_sum / latency_count if latency_count > 0 else 0
        error_rate = total_errors / total_requests if total_requests > 0 else 0

        end_time = timezone.now()
        check_duration_ms = (end_time - start_time).total_seconds() * 1000

        # Update spine status
        status.update_status(overall_status, health_score)
        status.total_patterns = total_patterns
        status.healthy_patterns = healthy_count
        status.degraded_patterns = degraded_count
        status.failed_patterns = failed_count
        status.total_requests = total_requests
        status.avg_latency_ms = avg_latency
        status.error_rate = error_rate
        status.heart_status = heart_status.get('status', 'unknown')
        status.lungs_status = lungs_status.get('status', 'unknown')
        status.circulatory_status = circulatory_status.get('status', 'unknown')
        status.routes_blocked = routes_blocked
        status.routes_rate_limited = routes_rate_limited
        status.fallbacks_active = fallbacks_active
        status.category_health = self._calculate_category_health(patterns, pattern_results)
        status.save()

        # Cache result
        self._cached_status = status
        self._cache_time = timezone.now()

        result = {
            'timestamp': timezone.now().isoformat(),
            'overall_status': overall_status,
            'health_score': round(health_score, 1),
            'is_aligned': overall_status == 'aligned',
            'check_duration_ms': round(check_duration_ms, 2),

            # Pattern summary
            'total_patterns': total_patterns,
            'healthy_patterns': healthy_count,
            'degraded_patterns': degraded_count,
            'failed_patterns': failed_count,

            # Request metrics
            'metrics': {
                'total_requests': total_requests,
                'error_rate': round(error_rate, 4),
                'avg_latency_ms': round(avg_latency, 2),
            },

            # Routing status
            'routing': {
                'routes_blocked': routes_blocked,
                'routes_rate_limited': routes_rate_limited,
                'fallbacks_active': fallbacks_active,
            },

            # Integration status
            'integrations': {
                'heart': heart_status,
                'lungs': lungs_status,
                'circulatory': circulatory_status,
            },

            # Per-pattern results
            'patterns': pattern_results,

            # Category breakdown
            'category_health': status.category_health,
        }

        logger.info(f"SPINE align: {overall_status} ({health_score:.1f}%) - "
                   f"{healthy_count}/{total_patterns} healthy patterns")

        return result

    def is_aligned(self) -> bool:
        """Quick check - is the spine healthy?"""
        status = self._get_cached_status()
        return status.is_healthy if status else True

    def get_vitals(self) -> dict:
        """Get current spine vitals (cached)."""
        status = self._get_cached_status()
        if not status:
            return self.align()

        return {
            'timestamp': status.last_check.isoformat(),
            'overall_status': status.status,
            'health_score': status.health_score,
            'is_aligned': status.is_healthy,
            'total_patterns': status.total_patterns,
            'healthy_patterns': status.healthy_patterns,
            'degraded_patterns': status.degraded_patterns,
            'failed_patterns': status.failed_patterns,
            'routes_blocked': status.routes_blocked,
            'routes_rate_limited': status.routes_rate_limited,
            'fallbacks_active': status.fallbacks_active,
            'integrations': {
                'heart': status.heart_status,
                'lungs': status.lungs_status,
                'circulatory': status.circulatory_status,
            },
            'category_health': status.category_health,
        }

    def can_route(self, path: str, method: str = 'GET') -> Tuple[bool, str]:
        """
        Check if a request can be routed to the given path.

        Returns:
            Tuple[bool, str]: (can_route, reason)
        """
        from core.models_spine import RoutePattern

        # Find matching pattern
        pattern = self._find_matching_pattern(path)
        if not pattern:
            return True, "No pattern configured - allowing"

        # Check if pattern is active
        if not pattern.is_active:
            return False, f"Route pattern '{pattern.pattern}' is disabled"

        # Check HEART requirement
        if pattern.requires_healthy_heart:
            heart_status = self._check_heart_status()
            if heart_status.get('status') not in ('healthy', 'recovering'):
                if pattern.fallback_response:
                    return True, "Using fallback - HEART unhealthy"
                return False, f"HEART service unhealthy: {heart_status.get('status')}"

        # Check LUNGS requirement
        if pattern.requires_healthy_lungs:
            lungs_status = self._check_lungs_status()
            if lungs_status.get('status') not in ('full_capacity', 'normal'):
                if pattern.fallback_response:
                    return True, "Using fallback - LUNGS low capacity"
                return False, f"LUNGS service low capacity: {lungs_status.get('status')}"

        # Check rate limiting (if configured)
        if pattern.rate_limit_per_minute > 0:
            # Rate limiting would be implemented with Redis counters
            # For now, just track that it's configured
            pass

        return True, "Route healthy"

    def get_route_metrics(self, path: str, hours: int = 24) -> dict:
        """Get metrics for a specific route pattern."""
        from core.models_spine import RoutePattern, RouteMetrics

        pattern = self._find_matching_pattern(path)
        if not pattern:
            return {'error': 'No matching pattern found'}

        cutoff = timezone.now() - timedelta(hours=hours)

        metrics = RouteMetrics.objects.filter(
            pattern=pattern,
            recorded_at__gte=cutoff
        ).aggregate(
            total_requests=Sum('total_requests'),
            successful_requests=Sum('successful_requests'),
            failed_requests=Sum('failed_requests'),
            avg_latency=Avg('avg_latency_ms'),
            p95_latency=Avg('p95_latency_ms'),
            avg_health_score=Avg('health_score'),
        )

        return {
            'pattern': pattern.pattern,
            'display_name': pattern.display_name,
            'category': pattern.category,
            'priority': pattern.priority,
            'period_hours': hours,
            'metrics': {
                'total_requests': metrics['total_requests'] or 0,
                'successful_requests': metrics['successful_requests'] or 0,
                'failed_requests': metrics['failed_requests'] or 0,
                'success_rate': (
                    metrics['successful_requests'] / metrics['total_requests']
                    if metrics['total_requests'] else 1.0
                ),
                'avg_latency_ms': round(metrics['avg_latency'] or 0, 2),
                'p95_latency_ms': round(metrics['p95_latency'] or 0, 2),
                'avg_health_score': round(metrics['avg_health_score'] or 100, 1),
            },
            'thresholds': {
                'max_latency_ms': pattern.max_latency_ms,
                'max_error_rate': pattern.max_error_rate,
                'min_availability': pattern.min_availability,
            },
        }

    def get_history(self, hours: int = 24, limit: int = 100) -> list:
        """Get spine alignment history."""
        from core.models_spine import RouteMetrics

        cutoff = timezone.now() - timedelta(hours=hours)

        # Get aggregated metrics over time
        metrics = RouteMetrics.objects.filter(
            recorded_at__gte=cutoff
        ).order_by('-recorded_at')[:limit]

        return [
            {
                'timestamp': m.recorded_at.isoformat(),
                'pattern': m.pattern.pattern,
                'health_score': m.health_score,
                'is_healthy': m.is_healthy,
                'total_requests': m.total_requests,
                'error_rate': m.error_rate,
                'avg_latency_ms': m.avg_latency_ms,
            }
            for m in metrics
        ]

    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for request tracing."""
        return f"spine-{uuid.uuid4().hex[:16]}-{int(timezone.now().timestamp())}"

    def start_trace(self, method: str, path: str, user_id: int = None,
                    client_ip: str = None) -> 'RequestTrace':
        """Start tracing a request."""
        from core.models_spine import RequestTrace

        correlation_id = self.generate_correlation_id()
        pattern = self._find_matching_pattern(path)

        trace = RequestTrace.objects.create(
            correlation_id=correlation_id,
            method=method,
            path=path,
            pattern=pattern,
            user_id=user_id,
            is_authenticated=user_id is not None,
            client_ip=client_ip,
            started_at=timezone.now(),
        )

        return trace

    def complete_trace(self, correlation_id: str, status_code: int,
                      response_size: int = None, error_type: str = None,
                      error_message: str = None) -> Optional['RequestTrace']:
        """Complete a request trace."""
        from core.models_spine import RequestTrace

        try:
            trace = RequestTrace.objects.get(correlation_id=correlation_id)
            trace.status_code = status_code
            trace.response_size = response_size
            trace.ended_at = timezone.now()
            trace.duration_ms = (trace.ended_at - trace.started_at).total_seconds() * 1000

            if error_type:
                trace.error_type = error_type
                trace.error_message = error_message or ''

            trace.save()
            return trace
        except RequestTrace.DoesNotExist:
            logger.warning(f"Request trace not found: {correlation_id}")
            return None

    def record_metrics(self, pattern_id: uuid.UUID, metrics_data: dict) -> None:
        """Record metrics for a route pattern."""
        from core.models_spine import RoutePattern, RouteMetrics

        try:
            pattern = RoutePattern.objects.get(pk=pattern_id)
        except RoutePattern.DoesNotExist:
            logger.warning(f"Route pattern not found: {pattern_id}")
            return

        # Create metrics record
        metrics = RouteMetrics.objects.create(
            pattern=pattern,
            total_requests=metrics_data.get('total_requests', 0),
            successful_requests=metrics_data.get('successful_requests', 0),
            failed_requests=metrics_data.get('failed_requests', 0),
            rate_limited_requests=metrics_data.get('rate_limited_requests', 0),
            status_2xx=metrics_data.get('status_2xx', 0),
            status_3xx=metrics_data.get('status_3xx', 0),
            status_4xx=metrics_data.get('status_4xx', 0),
            status_5xx=metrics_data.get('status_5xx', 0),
            avg_latency_ms=metrics_data.get('avg_latency_ms', 0),
            p50_latency_ms=metrics_data.get('p50_latency_ms', 0),
            p95_latency_ms=metrics_data.get('p95_latency_ms', 0),
            p99_latency_ms=metrics_data.get('p99_latency_ms', 0),
            max_latency_ms=metrics_data.get('max_latency_ms', 0),
            period_start=metrics_data.get('period_start', timezone.now() - timedelta(minutes=1)),
            period_end=metrics_data.get('period_end', timezone.now()),
            period_duration_seconds=metrics_data.get('period_duration_seconds', 60),
        )

        # Calculate derived metrics
        if metrics.total_requests > 0:
            metrics.success_rate = metrics.successful_requests / metrics.total_requests
            metrics.error_rate = metrics.failed_requests / metrics.total_requests
            metrics.throughput = metrics.total_requests / metrics.period_duration_seconds

        # Calculate health score
        metrics.health_score = metrics.calculate_health_score()
        metrics.is_healthy = metrics.health_score >= 70

        metrics.save()

    def get_patterns(self, category: str = None, active_only: bool = True) -> list:
        """Get all route patterns, optionally filtered by category."""
        from core.models_spine import RoutePattern

        queryset = RoutePattern.objects.all()

        if active_only:
            queryset = queryset.filter(is_active=True)

        if category:
            queryset = queryset.filter(category=category)

        return [
            {
                'id': str(p.id),
                'pattern': p.pattern,
                'display_name': p.display_name,
                'category': p.category,
                'priority': p.priority,
                'is_active': p.is_active,
                'is_monitored': p.is_monitored,
                'thresholds': {
                    'max_latency_ms': p.max_latency_ms,
                    'max_error_rate': p.max_error_rate,
                    'min_availability': p.min_availability,
                },
                'rate_limits': {
                    'per_minute': p.rate_limit_per_minute,
                    'per_hour': p.rate_limit_per_hour,
                },
                'requires_healthy_heart': p.requires_healthy_heart,
                'requires_healthy_lungs': p.requires_healthy_lungs,
                'has_fallback': bool(p.fallback_response),
            }
            for p in queryset
        ]

    def get_status_emoji(self) -> str:
        """Get emoji for current status."""
        status = self._get_cached_status()
        if not status:
            return '❓'

        return {
            'aligned': '🦴',      # Healthy spine
            'strained': '⚡',     # Some stress
            'compressed': '🔧',   # Under pressure
            'injured': '🚨',      # Critical
        }.get(status.status, '❓')

    # Private methods

    def _get_cached_status(self) -> Optional['SpineStatus']:
        """Get cached status or fetch from DB."""
        from core.models_spine import SpineStatus

        # Check cache validity
        if (self._cached_status and self._cache_time and
            (timezone.now() - self._cache_time).total_seconds() < self.CACHE_DURATION_SECONDS):
            return self._cached_status

        # Fetch from DB
        try:
            status = SpineStatus.objects.get(
                pk=uuid.UUID('00000000-0000-0000-0000-000000000001')
            )
            self._cached_status = status
            self._cache_time = timezone.now()
            return status
        except SpineStatus.DoesNotExist:
            return None

    def _find_matching_pattern(self, path: str) -> Optional['RoutePattern']:
        """Find the route pattern that matches the given path."""
        from core.models_spine import RoutePattern

        # Check cache first
        if path in self._route_pattern_cache:
            pattern_id = self._route_pattern_cache[path]
            try:
                return RoutePattern.objects.get(pk=pattern_id)
            except RoutePattern.DoesNotExist:
                del self._route_pattern_cache[path]

        # Get all patterns ordered by specificity (longer patterns first)
        patterns = RoutePattern.objects.filter(is_active=True).order_by('-pattern')

        for pattern in patterns:
            # Try prefix match first
            if path.startswith(pattern.pattern.rstrip('*').rstrip('/')):
                self._route_pattern_cache[path] = pattern.pk
                return pattern

            # Try regex match
            if pattern.pattern not in self._pattern_regex_cache:
                try:
                    # Convert pattern to regex (simple wildcard support)
                    regex_pattern = pattern.pattern.replace('*', '.*')
                    self._pattern_regex_cache[pattern.pattern] = re.compile(f'^{regex_pattern}')
                except re.error:
                    self._pattern_regex_cache[pattern.pattern] = None

            regex = self._pattern_regex_cache.get(pattern.pattern)
            if regex and regex.match(path):
                self._route_pattern_cache[path] = pattern.pk
                return pattern

        return None

    def _check_pattern_health(self, pattern: 'RoutePattern') -> dict:
        """Check health of a specific route pattern."""
        from core.models_spine import RouteMetrics, RequestTrace

        # Get recent metrics (last hour)
        cutoff = timezone.now() - timedelta(hours=1)

        recent_metrics = RouteMetrics.objects.filter(
            pattern=pattern,
            recorded_at__gte=cutoff
        ).order_by('-recorded_at').first()

        # Get recent traces for real-time metrics
        recent_traces = RequestTrace.objects.filter(
            pattern=pattern,
            started_at__gte=cutoff
        ).aggregate(
            total=Count('id'),
            avg_duration=Avg('duration_ms'),
            errors=Count('id', filter=models.Q(status_code__gte=500)),
        )

        # Calculate health score
        if recent_metrics:
            health_score = recent_metrics.health_score
            is_healthy = recent_metrics.is_healthy
            total_requests = recent_metrics.total_requests
            failed_requests = recent_metrics.failed_requests
            avg_latency = recent_metrics.avg_latency_ms
        else:
            # No recent metrics - check traces
            total_requests = recent_traces['total'] or 0
            failed_requests = recent_traces['errors'] or 0
            avg_latency = recent_traces['avg_duration'] or 0

            # Calculate health score from traces
            health_score = 100.0
            if total_requests > 0:
                error_rate = failed_requests / total_requests
                health_score -= min(40, error_rate * 400)

                if pattern.max_latency_ms > 0 and avg_latency > pattern.max_latency_ms:
                    latency_ratio = avg_latency / pattern.max_latency_ms
                    health_score -= min(30, (latency_ratio - 1) * 30)

            is_healthy = health_score >= 70

        # Check routing ability
        can_route, route_reason = self.can_route(pattern.pattern)

        return {
            'pattern': pattern.pattern,
            'display_name': pattern.display_name,
            'category': pattern.category,
            'priority': pattern.priority,
            'is_healthy': is_healthy,
            'health_score': round(health_score, 1),
            'total_requests': total_requests,
            'failed_requests': failed_requests,
            'avg_latency_ms': round(avg_latency, 2),
            'can_route': can_route,
            'route_reason': route_reason,
            'is_rate_limited': False,  # Would be set by rate limiter
            'using_fallback': not can_route and bool(pattern.fallback_response),
        }

    def _check_heart_status(self) -> dict:
        """Check HEART service status."""
        try:
            from core.services.heart import get_heart_monitor
            heart = get_heart_monitor()
            vitals = heart.get_vitals()
            # vitals is a dict keyed by component name, calculate overall status
            if not vitals:
                return {'status': 'unknown', 'health_score': 0, 'is_healthy': False}

            healthy_count = sum(1 for c in vitals.values() if c.get('is_healthy', False))
            total_count = len(vitals)
            health_score = (healthy_count / total_count * 100) if total_count > 0 else 0

            # Determine overall status
            if healthy_count == total_count:
                status = 'healthy'
            elif healthy_count > total_count / 2:
                status = 'degraded'
            else:
                status = 'critical'

            return {
                'status': status,
                'health_score': round(health_score),
                'is_healthy': healthy_count == total_count,
            }
        except Exception as e:
            logger.warning(f"Failed to check HEART status: {e}")
            return {'status': 'unknown', 'health_score': 0, 'is_healthy': False, 'error': str(e)}

    def _check_lungs_status(self) -> dict:
        """Check LUNGS service status."""
        try:
            from core.services.lungs import get_lungs_monitor
            lungs = get_lungs_monitor()
            vitals = lungs.get_vitals()
            # vitals has system_status, system_oxygen, providers
            status = vitals.get('system_status', 'unknown')
            oxygen = vitals.get('system_oxygen', 0)
            return {
                'status': status,
                'capacity_score': round(oxygen),  # oxygen is 0-100%
                'is_healthy': status in ('full_capacity', 'normal') and oxygen >= 80,
            }
        except Exception as e:
            logger.warning(f"Failed to check LUNGS status: {e}")
            return {'status': 'unknown', 'capacity_score': 0, 'is_healthy': False, 'error': str(e)}

    def _check_circulatory_status(self) -> dict:
        """Check CIRCULATORY service status."""
        try:
            from core.services.circulatory import get_circulatory_system
            circulatory = get_circulatory_system()
            vitals = circulatory.get_vitals()
            # vitals has routes dict, calculate overall status from routes
            routes = vitals.get('routes', {})
            if not routes:
                return {'status': 'unknown', 'flow_score': 0, 'is_flowing': False}

            healthy_routes = sum(1 for r in routes.values() if r.get('is_healthy', False))
            total_routes = len(routes)
            flow_score = (healthy_routes / total_routes * 100) if total_routes > 0 else 0

            # Determine overall status
            if healthy_routes == total_routes:
                status = 'flowing'
            elif healthy_routes > total_routes / 2:
                status = 'reduced'
            else:
                status = 'blocked'

            return {
                'status': status,
                'flow_score': round(flow_score),
                'is_flowing': healthy_routes > 0,
            }
        except Exception as e:
            logger.warning(f"Failed to check CIRCULATORY status: {e}")
            return {'status': 'unknown', 'flow_score': 0, 'is_flowing': False, 'error': str(e)}

    def _calculate_health_score(self, healthy: int, degraded: int, failed: int,
                                total: int, heart: dict, lungs: dict,
                                circulatory: dict) -> float:
        """Calculate overall spine health score."""
        if total == 0:
            return 100.0

        score = 100.0

        # Pattern health (60% weight)
        pattern_score = ((healthy * 1.0) + (degraded * 0.5) + (failed * 0.0)) / total
        score = pattern_score * 60

        # Integration health (40% weight - 13.33% each)
        if heart.get('is_healthy', False):
            score += 13.33
        elif heart.get('status') != 'unknown':
            score += 6.67

        if lungs.get('is_healthy', False):
            score += 13.33
        elif lungs.get('status') != 'unknown':
            score += 6.67

        if circulatory.get('is_flowing', False):
            score += 13.33
        elif circulatory.get('status') != 'unknown':
            score += 6.67

        return min(100, max(0, score))

    def _calculate_category_health(self, patterns, pattern_results: dict) -> dict:
        """Calculate health score by category."""
        from core.models_spine import RoutePattern

        category_scores = {}

        for pattern in patterns:
            category = pattern.category
            result = pattern_results.get(pattern.pattern, {})
            score = result.get('health_score', 100)

            if category not in category_scores:
                category_scores[category] = {'scores': [], 'count': 0}

            category_scores[category]['scores'].append(score)
            category_scores[category]['count'] += 1

        return {
            category: {
                'health_score': round(sum(data['scores']) / len(data['scores']), 1),
                'pattern_count': data['count'],
            }
            for category, data in category_scores.items()
            if data['scores']
        }


# Import models for type hints
from django.db import models
