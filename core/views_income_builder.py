"""
Income Builder Template View
"""

from django.shortcuts import render


def income_builder_view(request):
    """
    Render the Income Builder template with WebSocket connection
    """
    # Build WebSocket URL dynamically from request
    ws_scheme = 'wss' if request.is_secure() else 'ws'
    ws_host = request.get_host()
    context = {
        'websocket_url': f"{ws_scheme}://{ws_host}/ws/income-builder/",
    }
    return render(request, 'income_builder.html', context)