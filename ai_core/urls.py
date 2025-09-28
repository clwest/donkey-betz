"""
AI Core app URL configuration
This app contains agents, spiders, intelligence, and consciousness systems
"""

from django.urls import path, include

app_name = 'ai_core'

urlpatterns = [
    # AI Core API routes
    path('api/agents/', include('ai_core.agents.urls')),
    path('api/spiders/', include('ai_core.spiders.urls')),
    path('api/intelligence/', include('ai_core.intelligence.urls')),

    # Keep any ai_core-specific views here if needed
    # Example: path('status/', ai_core_status_view, name='status'),
]