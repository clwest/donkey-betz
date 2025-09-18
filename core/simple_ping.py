"""
Simple ping endpoint for testing basic Django functionality
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from datetime import datetime


@never_cache
@csrf_exempt
def ping_dev(request):
    """Ultra-simple endpoint to test basic Django functionality"""
    return JsonResponse({
        'success': True,
        'message': 'Ping successful',
        'timestamp': str(datetime.now()),
        'server_status': 'healthy'
    })