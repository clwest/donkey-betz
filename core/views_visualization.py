"""
Views for serving the AI agents visualization.

Session 1110 (PR fix/mounted-broken-route-fallbacks):
The legacy Django templates (visualization.html, activity_monitor_enhanced.html,
ai_building_products_with_agents.html) are gone — the surfaces moved to the
React SPA. These views now redirect to their closest SPA equivalents instead
of 500-ing on TemplateDoesNotExist.
"""

from django.shortcuts import redirect
from django.views.decorators.http import require_GET


@require_GET
def ai_agents_visualization(request):
    """Redirect legacy /visualization/ to the React Neural Orchestra page."""
    return redirect('/neural-orchestra')


def activity_monitor(request):
    """Redirect legacy activity monitor (defensive — no current URL mount)."""
    return redirect('/')


def ai_building_products(request):
    """Redirect legacy /ai-building-products/ to the React Agents page."""
    return redirect('/agents')