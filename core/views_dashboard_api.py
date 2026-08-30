"""
Dashboard API Views
==================
Real API endpoints for the unified learning dashboard frontend
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Import our dashboard API
import sys
sys.path.append('/Users/donkeyking/Donkey_Betz/unified-donkey-betz')
# from api_unified_learning_dashboard import dashboard_api  # Removed in cleanup
dashboard_api = lambda: {"error": "Module removed during cleanup"}

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_all_data(request):
    """Get all dashboard data in one call"""
    try:
        data = dashboard_api.get_all_dashboard_data()
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_learning_data(request):
    """Get learning overview data"""
    try:
        data = dashboard_api.get_learning_overview()
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_collaboration_data(request):
    """Get collaboration data"""
    try:
        data = dashboard_api.get_collaboration_data()
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_cost_data(request):
    """Get cost metrics"""
    try:
        data = dashboard_api.get_cost_metrics()
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_health_data(request):
    """Get system health data"""
    try:
        data = dashboard_api.get_system_health()
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_feed_data(request):
    """Get learning activity feed"""
    try:
        data = dashboard_api.get_learning_feed()
        response = JsonResponse(data, safe=False)  # safe=False for list response
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_verification_data(request):
    """Get verification samples"""
    try:
        data = dashboard_api.get_verification_samples()
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({'error': str(e)}, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response