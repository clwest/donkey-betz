"""
Session 704: SPINE - Central API Router Views

API endpoints for the SPINE service - the backbone of the AI body.

Endpoints:
    GET /api/spine/align/              - Run full alignment check
    GET /api/spine/status/             - Get cached spine status
    GET /api/spine/patterns/           - List all route patterns
    GET /api/spine/patterns/<id>/      - Get specific pattern details
    GET /api/spine/metrics/<pattern>/  - Get metrics for a pattern
    GET /api/spine/history/            - Get alignment history
    GET /api/spine/can-route/          - Check if path can be routed
    GET /api/spine/is-aligned/         - Quick health check
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def align_view(request):
    """
    Run full spine alignment check.

    GET /api/spine/align/
    Query params:
        force (bool): Force fresh check (ignore cache)

    Returns full alignment status including all pattern health,
    integration status with HEART/LUNGS/CIRCULATORY, and routing metrics.
    """
    try:
        from core.services.spine import get_spine_router

        force = request.GET.get('force', 'false').lower() == 'true'

        spine = get_spine_router()
        result = spine.align(force=force)

        return JsonResponse(result)

    except Exception as e:
        logger.exception(f"Error in spine align: {e}")
        return JsonResponse({
            'error': str(e),
            'overall_status': 'injured',
            'health_score': 0,
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def spine_status_view(request):
    """
    Get cached spine status.

    GET /api/spine/status/

    Returns current cached status without running a full check.
    Use /align/ for a fresh check.
    """
    try:
        from core.services.spine import get_spine_router

        spine = get_spine_router()
        vitals = spine.get_vitals()

        return JsonResponse(vitals)

    except Exception as e:
        logger.exception(f"Error getting spine status: {e}")
        return JsonResponse({
            'error': str(e),
            'overall_status': 'injured',
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def patterns_list_view(request):
    """
    List all route patterns.

    GET /api/spine/patterns/
    Query params:
        category (str): Filter by category (agents, spiders, monitoring, etc.)
        active (bool): Filter by active status (default: true)

    Returns list of all configured route patterns with their settings.
    """
    try:
        from core.services.spine import get_spine_router

        category = request.GET.get('category')
        active_only = request.GET.get('active', 'true').lower() == 'true'

        spine = get_spine_router()
        patterns = spine.get_patterns(category=category, active_only=active_only)

        return JsonResponse({
            'count': len(patterns),
            'category_filter': category,
            'active_only': active_only,
            'patterns': patterns,
        })

    except Exception as e:
        logger.exception(f"Error listing patterns: {e}")
        return JsonResponse({
            'error': str(e),
            'patterns': [],
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pattern_detail_view(request, pattern_id):
    """
    Get specific pattern details with metrics.

    GET /api/spine/patterns/<uuid:pattern_id>/
    Query params:
        hours (int): Metrics lookback period (default: 24)

    Returns pattern configuration and recent metrics.
    """
    try:
        from core.models_spine import RoutePattern
        from core.services.spine import get_spine_router

        hours = int(request.GET.get('hours', 24))

        # Get pattern
        try:
            pattern = RoutePattern.objects.get(pk=pattern_id)
        except RoutePattern.DoesNotExist:
            return JsonResponse({
                'error': f'Pattern not found: {pattern_id}',
            }, status=404)

        # Get metrics
        spine = get_spine_router()
        metrics = spine.get_route_metrics(pattern.pattern, hours=hours)

        return JsonResponse({
            'id': str(pattern.id),
            'pattern': pattern.pattern,
            'display_name': pattern.display_name,
            'category': pattern.category,
            'priority': pattern.priority,
            'description': pattern.description,
            'is_active': pattern.is_active,
            'is_monitored': pattern.is_monitored,
            'thresholds': {
                'max_latency_ms': pattern.max_latency_ms,
                'max_error_rate': pattern.max_error_rate,
                'min_availability': pattern.min_availability,
            },
            'rate_limits': {
                'per_minute': pattern.rate_limit_per_minute,
                'per_hour': pattern.rate_limit_per_hour,
            },
            'requirements': {
                'healthy_heart': pattern.requires_healthy_heart,
                'healthy_lungs': pattern.requires_healthy_lungs,
            },
            'fallback_configured': bool(pattern.fallback_response),
            'created_at': pattern.created_at.isoformat(),
            'updated_at': pattern.updated_at.isoformat(),
            'metrics': metrics.get('metrics', {}),
        })

    except Exception as e:
        logger.exception(f"Error getting pattern details: {e}")
        return JsonResponse({
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def route_metrics_view(request):
    """
    Get metrics for a specific route path.

    GET /api/spine/metrics/
    Query params:
        path (str): The route path to check (required)
        hours (int): Lookback period in hours (default: 24)

    Returns metrics for the matching route pattern.
    """
    try:
        from core.services.spine import get_spine_router

        path = request.GET.get('path')
        if not path:
            return JsonResponse({
                'error': 'path parameter is required',
            }, status=400)

        hours = int(request.GET.get('hours', 24))

        spine = get_spine_router()
        metrics = spine.get_route_metrics(path, hours=hours)

        return JsonResponse(metrics)

    except Exception as e:
        logger.exception(f"Error getting route metrics: {e}")
        return JsonResponse({
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def history_view(request):
    """
    Get spine alignment history.

    GET /api/spine/history/
    Query params:
        hours (int): Lookback period (default: 24)
        limit (int): Max records to return (default: 100)

    Returns time-series alignment data.
    """
    try:
        from core.services.spine import get_spine_router

        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 100))

        spine = get_spine_router()
        history = spine.get_history(hours=hours, limit=limit)

        return JsonResponse({
            'period_hours': hours,
            'count': len(history),
            'history': history,
        })

    except Exception as e:
        logger.exception(f"Error getting spine history: {e}")
        return JsonResponse({
            'error': str(e),
            'history': [],
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def can_route_view(request):
    """
    Check if a path can be routed.

    GET /api/spine/can-route/
    Query params:
        path (str): The route path to check (required)
        method (str): HTTP method (default: GET)

    Returns routing decision and reason.
    """
    try:
        from core.services.spine import get_spine_router

        path = request.GET.get('path')
        if not path:
            return JsonResponse({
                'error': 'path parameter is required',
            }, status=400)

        method = request.GET.get('method', 'GET').upper()

        spine = get_spine_router()
        can_route, reason = spine.can_route(path, method=method)

        return JsonResponse({
            'path': path,
            'method': method,
            'can_route': can_route,
            'reason': reason,
        })

    except Exception as e:
        logger.exception(f"Error checking route: {e}")
        return JsonResponse({
            'error': str(e),
            'can_route': False,
            'reason': 'Error checking route',
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def is_aligned_view(request):
    """
    Quick health check - is the spine aligned?

    GET /api/spine/is-aligned/

    Returns simple boolean status for health checks.
    """
    try:
        from core.services.spine import get_spine_router

        spine = get_spine_router()
        is_aligned = spine.is_aligned()
        emoji = spine.get_status_emoji()

        return JsonResponse({
            'is_aligned': is_aligned,
            'emoji': emoji,
            'message': 'Spine is aligned' if is_aligned else 'Spine needs attention',
        })

    except Exception as e:
        logger.exception(f"Error checking spine alignment: {e}")
        return JsonResponse({
            'is_aligned': False,
            'emoji': '🚨',
            'message': f'Error: {str(e)}',
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def categories_view(request):
    """
    Get pattern counts by category.

    GET /api/spine/categories/

    Returns category breakdown with pattern counts and health.
    """
    try:
        from core.services.spine import get_spine_router

        spine = get_spine_router()
        vitals = spine.get_vitals()

        category_health = vitals.get('category_health', {})

        return JsonResponse({
            'categories': category_health,
            'total_categories': len(category_health),
        })

    except Exception as e:
        logger.exception(f"Error getting categories: {e}")
        return JsonResponse({
            'error': str(e),
            'categories': {},
        }, status=500)
