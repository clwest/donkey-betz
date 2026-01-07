"""
Session 701: HEART Service API Views

Provides REST API endpoints for system health monitoring:
- /api/heart/pulse/ - Run full health check
- /api/heart/status/ - Get current vitals (cached)
- /api/heart/history/ - Get heartbeat history
- /api/heart/component/<name>/ - Get specific component status
"""

import logging

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def heart_pulse(request):
    """
    Run a full health check on all system components.

    Returns comprehensive health status of the entire AI body:
    - Brain (ThinkingAgent)
    - Nervous System (LLM/ML Routers)
    - Organs (72 Agents)
    - Sensory (77 Spiders)
    - Skin (Workspace Manager)
    - Memory (Database & Redis)
    """
    try:
        from core.services.heart import get_heart_monitor

        heart = get_heart_monitor()
        pulse = heart.pulse()

        # Record to database
        heart.record_heartbeat(pulse)

        # Alert if critical
        heart.alert_if_critical(pulse)

        return Response({
            'success': True,
            **pulse,
        })

    except Exception as e:
        logger.exception(f"Heart pulse failed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def heart_status(request):
    """
    Get current system vitals from cache (fast).

    Returns the most recent status of each component without
    running a new health check.
    """
    try:
        from core.services.heart import get_heart_monitor
        from core.models_heart import HeartBeat

        heart = get_heart_monitor()
        vitals = heart.get_vitals()

        # Get most recent heartbeat for overall status
        latest_heartbeat = HeartBeat.objects.order_by('-recorded_at').first()

        overall = {
            'health_score': 0,
            'overall_status': 'unknown',
            'is_alive': False,
            'last_check': None,
        }

        if latest_heartbeat:
            overall = {
                'health_score': latest_heartbeat.health_score,
                'overall_status': latest_heartbeat.overall_status,
                'is_alive': latest_heartbeat.is_alive,
                'last_check': latest_heartbeat.recorded_at.isoformat(),
            }

        return Response({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            **overall,
            'components': vitals,
        })

    except Exception as e:
        logger.exception(f"Heart status failed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def heart_history(request):
    """
    Get heartbeat history.

    Query params:
    - hours: Number of hours to look back (default: 24)
    - limit: Maximum records to return (default: 100)
    """
    try:
        from core.services.heart import get_heart_monitor

        hours = int(request.query_params.get('hours', 24))
        limit = int(request.query_params.get('limit', 100))

        # Clamp values
        hours = min(max(hours, 1), 168)  # 1 hour to 7 days
        limit = min(max(limit, 1), 1000)

        heart = get_heart_monitor()
        history = heart.get_history(hours=hours, limit=limit)

        return Response({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'query': {
                'hours': hours,
                'limit': limit,
            },
            'count': len(history),
            'heartbeats': history,
        })

    except Exception as e:
        logger.exception(f"Heart history failed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def heart_component(request, component_name):
    """
    Get detailed status for a specific component.

    Path params:
    - component_name: One of brain, nervous_system, organs, sensory, skin, memory
    """
    try:
        from core.models_heart import ComponentStatus

        valid_components = ['brain', 'nervous_system', 'organs', 'sensory', 'skin', 'memory']

        if component_name not in valid_components:
            return Response({
                'success': False,
                'error': f"Invalid component: {component_name}",
                'valid_components': valid_components,
            }, status=400)

        try:
            component = ComponentStatus.objects.get(component=component_name)
            data = {
                'component': component.component,
                'name': component.display_name,
                'description': component.description,
                'status': component.status,
                'is_healthy': component.is_healthy,
                'last_check': component.last_check.isoformat() if component.last_check else None,
                'last_healthy': component.last_healthy.isoformat() if component.last_healthy else None,
                'response_time_ms': component.response_time_ms,
                'error_count_24h': component.error_count_24h,
                'check_count_24h': component.check_count_24h,
                'uptime_percent_24h': component.uptime_percent_24h,
                'details': component.details,
                'last_error': component.last_error,
            }
        except ComponentStatus.DoesNotExist:
            # Component hasn't been checked yet
            data = {
                'component': component_name,
                'status': 'unknown',
                'is_healthy': None,
                'message': 'Component has not been checked yet. Run /api/heart/pulse/ first.',
            }

        return Response({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            **data,
        })

    except Exception as e:
        logger.exception(f"Heart component status failed: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def heart_is_alive(request):
    """
    Quick health check - is the system alive?

    Lightweight endpoint for load balancers and monitoring.
    """
    try:
        from core.services.heart import get_heart_monitor

        heart = get_heart_monitor()
        alive = heart.is_alive()

        return Response({
            'alive': alive,
            'timestamp': timezone.now().isoformat(),
        }, status=200 if alive else 503)

    except Exception as e:
        return Response({
            'alive': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }, status=503)
