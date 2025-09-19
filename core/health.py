"""
Health check endpoint for frontend to verify backend is ready
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import redis
from django.db import connection


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint that verifies all services are ready
    Used by frontend to know when to initialize WebSocket connections
    """
    health_status = {
        'status': 'healthy',
        'services': {},
        'websocket_ready': False,
        'timestamp': request.META.get('HTTP_DATE', ''),
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['services']['database'] = 'ok'
    except Exception as e:
        health_status['services']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Check Redis
    try:
        r = redis.from_url('redis://localhost:6379/0')
        r.ping()
        health_status['services']['redis'] = 'ok'
    except Exception as e:
        health_status['services']['redis'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check if WebSocket consumers are loaded
    try:
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        if channel_layer:
            health_status['websocket_ready'] = True
            health_status['services']['websocket'] = 'ok'
        else:
            health_status['services']['websocket'] = 'not configured'
    except Exception as e:
        health_status['services']['websocket'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Determine overall health
    if all(v == 'ok' for v in health_status['services'].values()):
        health_status['status'] = 'healthy'
        status_code = 200
    elif health_status['services'].get('database') == 'ok':
        health_status['status'] = 'degraded'
        status_code = 200
    else:
        health_status['status'] = 'unhealthy'
        status_code = 503
    
    return JsonResponse(health_status, status=status_code)


@csrf_exempt
@require_http_methods(["GET"])
def websocket_test(request):
    """
    Test endpoint to verify WebSocket configuration
    """
    from core.routing import websocket_urlpatterns
    
    endpoints = []
    for pattern in websocket_urlpatterns[:10]:  # First 10 endpoints
        if hasattr(pattern, 'pattern'):
            endpoints.append(str(pattern.pattern))
    
    return JsonResponse({
        'websocket_configured': bool(endpoints),
        'endpoints_count': len(websocket_urlpatterns),
        'sample_endpoints': endpoints,
        'server_type': 'daphne' if 'daphne' in request.META.get('SERVER_SOFTWARE', '').lower() else 'runserver'
    })
