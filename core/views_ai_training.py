"""
Views for AI Job Market Intelligence Training Dashboard
"""
from django.http import HttpResponse
import os


def ai_job_market_dashboard(request):
    """Serve the AI Job Market Intelligence dashboard"""
    # Read the HTML file
    dashboard_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'ai_job_market_dashboard.html'
    )

    try:
        with open(dashboard_path, 'r') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(
            '<h1>Dashboard not found</h1><p>Please ensure ai_job_market_dashboard.html exists.</p>',
            status=404
        )