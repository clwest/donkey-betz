"""
Session 703: CIRCULATORY SYSTEM Views

API endpoints for monitoring data flow health - the circulation of the AI body.
Tracks Redis queues, Celery tasks, WebSocket channels, and event streams.

Endpoints:
- /api/circulatory/circulate/     - Run full circulation check
- /api/circulatory/status/        - Get cached flow status
- /api/circulatory/routes/        - List all monitored routes
- /api/circulatory/routes/<id>/   - Get specific route status
- /api/circulatory/bottlenecks/   - Get current bottlenecks
- /api/circulatory/velocity/      - Get flow velocity metrics
- /api/circulatory/history/       - Get circulation pulse history
- /api/circulatory/is-flowing/    - Quick alive check
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from core.models_circulatory import FlowRoute, CirculationPulse, FlowStatus

logger = logging.getLogger(__name__)


def get_circulatory_service():
    """Lazy import to avoid circular imports."""
    from core.services.circulatory import get_circulatory_system
    return get_circulatory_system()


@csrf_exempt
@require_http_methods(["GET"])
def circulate_view(request):
    """
    Run full circulation check - monitor all data flows.

    GET /api/circulatory/circulate/

    Returns comprehensive circulation status including all routes,
    bottlenecks, and flow metrics.
    """
    try:
        circulatory = get_circulatory_service()
        result = circulatory.circulate()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Circulation check failed: {e}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'overall_status': 'blocked',
            'flow_score': 0,
            'is_flowing': False,
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def status_view(request):
    """
    Get cached flow status - quick snapshot without running checks.

    GET /api/circulatory/status/

    Returns the most recent circulation pulse and current route statuses.
    """
    try:
        circulatory = get_circulatory_service()
        vitals = circulatory.get_vitals()
        return JsonResponse(vitals)
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'overall_status': 'unknown',
            'flow_score': 0,
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def routes_list_view(request):
    """
    List all monitored flow routes.

    GET /api/circulatory/routes/

    Query params:
    - type: Filter by route type (redis_queue, celery_queue, websocket, event_stream)
    - active: Filter by active status (true/false)
    - critical: Filter by critical status (true/false)

    Returns list of routes with their current status.
    """
    try:
        routes = FlowRoute.objects.filter(is_active=True)

        # Apply filters
        route_type = request.GET.get('type')
        if route_type:
            routes = routes.filter(route_type=route_type)

        active = request.GET.get('active')
        if active is not None:
            routes = routes.filter(is_active=active.lower() == 'true')

        critical = request.GET.get('critical')
        if critical is not None:
            routes = routes.filter(is_critical=critical.lower() == 'true')

        route_list = []
        for route in routes:
            route_data = {
                'id': str(route.id),
                'name': route.name,
                'display_name': route.display_name,
                'route_type': route.route_type,
                'identifier': route.identifier,
                'max_depth': route.max_depth,
                'max_latency_ms': route.max_latency_ms,
                'min_throughput': route.min_throughput,
                'is_active': route.is_active,
                'is_critical': route.is_critical,
                'description': route.description,
            }

            # Add current status if available
            try:
                status = route.current_status
                route_data['current_status'] = {
                    'status': status.status,
                    'is_healthy': status.is_healthy,
                    'health_score': status.health_score,
                    'current_depth': status.current_depth,
                    'current_throughput': status.current_throughput,
                    'current_latency_ms': status.current_latency_ms,
                    'last_check': status.last_check.isoformat() if status.last_check else None,
                    'last_activity': status.last_activity.isoformat() if status.last_activity else None,
                }
            except FlowStatus.DoesNotExist:
                route_data['current_status'] = None

            route_list.append(route_data)

        return JsonResponse({
            'routes': route_list,
            'total': len(route_list),
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        logger.error(f"Routes list failed: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def route_detail_view(request, route_id):
    """
    Get detailed status for a specific route.

    GET /api/circulatory/routes/<route_id>/

    Returns route configuration and detailed current status.
    """
    try:
        route = FlowRoute.objects.get(id=route_id)

        route_data = {
            'id': str(route.id),
            'name': route.name,
            'display_name': route.display_name,
            'route_type': route.route_type,
            'identifier': route.identifier,
            'max_depth': route.max_depth,
            'max_latency_ms': route.max_latency_ms,
            'min_throughput': route.min_throughput,
            'is_active': route.is_active,
            'is_critical': route.is_critical,
            'description': route.description,
            'created_at': route.created_at.isoformat(),
            'updated_at': route.updated_at.isoformat(),
        }

        # Add current status
        try:
            status = route.current_status
            route_data['current_status'] = {
                'status': status.status,
                'status_emoji': status.get_status_display_emoji(),
                'is_healthy': status.is_healthy,
                'health_score': status.health_score,
                'current_depth': status.current_depth,
                'current_throughput': status.current_throughput,
                'current_latency_ms': status.current_latency_ms,
                'items_processed_24h': status.items_processed_24h,
                'errors_24h': status.errors_24h,
                'avg_latency_24h_ms': status.avg_latency_24h_ms,
                'peak_depth_24h': status.peak_depth_24h,
                'peak_latency_24h_ms': status.peak_latency_24h_ms,
                'active_workers': status.active_workers,
                'active_tasks': status.active_tasks,
                'reserved_tasks': status.reserved_tasks,
                'last_activity': status.last_activity.isoformat() if status.last_activity else None,
                'last_check': status.last_check.isoformat() if status.last_check else None,
                'status_changed_at': status.status_changed_at.isoformat() if status.status_changed_at else None,
                'congestion_alert_sent': status.congestion_alert_sent,
                'blocked_alert_sent': status.blocked_alert_sent,
                'details': status.details,
                'error_message': status.error_message,
            }
        except FlowStatus.DoesNotExist:
            route_data['current_status'] = None

        return JsonResponse(route_data)
    except FlowRoute.DoesNotExist:
        return JsonResponse({'error': 'Route not found'}, status=404)
    except Exception as e:
        logger.error(f"Route detail failed: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def bottlenecks_view(request):
    """
    Get current bottlenecks in data flow.

    GET /api/circulatory/bottlenecks/

    Query params:
    - severity: Filter by severity (critical, warning, info)

    Returns list of detected bottlenecks with details.
    """
    try:
        circulatory = get_circulatory_service()
        bottlenecks = circulatory.detect_bottlenecks()

        # Filter by severity if requested
        severity = request.GET.get('severity')
        if severity:
            bottlenecks = [b for b in bottlenecks if b.get('severity') == severity]

        # Get latest pulse for context
        latest_pulse = CirculationPulse.objects.first()

        return JsonResponse({
            'bottlenecks': bottlenecks,
            'total': len(bottlenecks),
            'has_critical': any(b.get('severity') == 'critical' for b in bottlenecks),
            'has_warning': any(b.get('severity') == 'warning' for b in bottlenecks),
            'overall_status': latest_pulse.overall_status if latest_pulse else 'unknown',
            'flow_score': latest_pulse.flow_score if latest_pulse else 0,
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        logger.error(f"Bottlenecks check failed: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def velocity_view(request):
    """
    Get flow velocity metrics.

    GET /api/circulatory/velocity/

    Query params:
    - hours: Time window in hours (default: 1)

    Returns throughput and latency trends.
    """
    try:
        hours = int(request.GET.get('hours', 1))
        hours = min(max(hours, 1), 24)  # Clamp between 1-24 hours

        circulatory = get_circulatory_service()
        velocity = circulatory.get_flow_velocity(hours=hours)

        return JsonResponse(velocity)
    except ValueError:
        return JsonResponse({'error': 'Invalid hours parameter'}, status=400)
    except Exception as e:
        logger.error(f"Velocity check failed: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def history_view(request):
    """
    Get circulation pulse history.

    GET /api/circulatory/history/

    Query params:
    - hours: Time window in hours (default: 24)
    - limit: Maximum records to return (default: 100)
    - status: Filter by overall_status (flowing, slow, congested, blocked)

    Returns time-series of circulation pulses.
    """
    try:
        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 100))
        status_filter = request.GET.get('status')

        # Clamp values
        hours = min(max(hours, 1), 168)  # 1 hour to 1 week
        limit = min(max(limit, 1), 1000)  # 1 to 1000 records

        circulatory = get_circulatory_service()
        history = circulatory.get_history(hours=hours, limit=limit)

        # Filter by status if requested
        if status_filter:
            history = [h for h in history if h.get('overall_status') == status_filter]

        # Calculate summary stats
        if history:
            flow_scores = [h['flow_score'] for h in history]
            summary = {
                'avg_flow_score': sum(flow_scores) / len(flow_scores),
                'min_flow_score': min(flow_scores),
                'max_flow_score': max(flow_scores),
                'status_counts': {},
            }
            for h in history:
                status = h['overall_status']
                summary['status_counts'][status] = summary['status_counts'].get(status, 0) + 1
        else:
            summary = {
                'avg_flow_score': 0,
                'min_flow_score': 0,
                'max_flow_score': 0,
                'status_counts': {},
            }

        return JsonResponse({
            'history': history,
            'total': len(history),
            'hours': hours,
            'summary': summary,
            'timestamp': timezone.now().isoformat(),
        })
    except ValueError:
        return JsonResponse({'error': 'Invalid parameter value'}, status=400)
    except Exception as e:
        logger.error(f"History check failed: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def is_flowing_view(request):
    """
    Quick alive check - is data flowing normally?

    GET /api/circulatory/is-flowing/

    Returns simple boolean status for health checks.
    Lightweight endpoint suitable for load balancer checks.
    """
    try:
        circulatory = get_circulatory_service()
        is_flowing = circulatory.is_flowing()

        # Get cached vitals for additional context
        vitals = circulatory.get_vitals()

        return JsonResponse({
            'is_flowing': is_flowing,
            'overall_status': vitals.get('overall_status', 'unknown'),
            'flow_score': vitals.get('flow_score', 0),
            'timestamp': timezone.now().isoformat(),
        })
    except Exception as e:
        logger.error(f"Is-flowing check failed: {e}", exc_info=True)
        return JsonResponse({
            'is_flowing': False,
            'overall_status': 'blocked',
            'flow_score': 0,
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)
