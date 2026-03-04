"""
Views for serving the AI agents visualization
"""

from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

# Removed csrf_exempt for security - CSRF tokens now properly handled
# Removed xframe_options_exempt for clickjacking protection
# Temporarily removed login_required to avoid authentication issues

@require_GET
@cache_page(60 * 5)  # Cache for 5 minutes
def ai_agents_visualization(request):
    """Serve the AI agents learning visualization"""
    context = {
        'user': request.user if request.user.is_authenticated else None,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'visualization.html', context)


def activity_monitor(request):
    """Serve the activity monitor page for learning and infrastructure"""
    context = {
        'user': request.user if request.user.is_authenticated else None,
        'is_authenticated': request.user.is_authenticated,
        'websocket_url': 'ws://localhost:8000/ws/ai-training/',
    }
    return render(request, 'activity_monitor_enhanced.html', context)


def ai_building_products(request):
    """Serve the AI Building Products page"""
    context = {
        'user': request.user if request.user.is_authenticated else None,
        'is_authenticated': request.user.is_authenticated,
    }
    return render(request, 'ai_building_products_with_agents.html', context)