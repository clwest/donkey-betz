"""
Income Builder Template View
"""

from django.shortcuts import render


def income_builder_view(request):
    """
    Render the Income Builder template with WebSocket connection
    """
    # Use hardcoded localhost for development
    context = {
        'websocket_url': "ws://localhost:8000/ws/income-builder/",
    }
    return render(request, 'income_builder.html', context)