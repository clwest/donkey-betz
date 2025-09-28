"""
Income Builder Template View
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


def income_builder_view(request):
    """
    Render the Income Builder template with WebSocket connection
    """
    # Use hardcoded localhost for development
    context = {
        'websocket_url': "ws://localhost:8000/ws/income-builder/",
    }
    return render(request, 'income_builder.html', context)