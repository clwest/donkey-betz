"""
React app serving view.

Session 688: Full UI deprecation - Django serves the React SPA.
This view serves the React app's index.html for all frontend routes.
"""

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie


@never_cache
@ensure_csrf_cookie
def react_app(request):
    """
    Serve the React Single Page Application.

    This view serves the built React app's index.html file.
    React Router handles all frontend routing on the client side.

    The @never_cache decorator ensures the latest version is always served.
    The @ensure_csrf_cookie decorator ensures CSRF protection for API calls.
    """
    return render(request, 'index.html')


@never_cache
def react_app_public(request):
    """
    Serve React app for public routes (login, etc).
    No authentication required.
    """
    return render(request, 'index.html')
