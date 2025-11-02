# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from api_unified_learning_dashboard import dashboard_api

@csrf_exempt
@require_http_methods(["GET"])
def test_dashboard_data(request):
    """Test endpoint for frontend data"""
    try:
        data = dashboard_api.get_all_dashboard_data()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def test_learning_data(request):
    """Test endpoint for learning data only"""
    try:
        data = dashboard_api.get_learning_overview()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
