"""
Views for serving the AI agents visualization
"""

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

@csrf_exempt
@xframe_options_exempt
def ai_agents_visualization(request):
    """Serve the AI agents learning visualization"""
    return render(request, 'visualization.html')