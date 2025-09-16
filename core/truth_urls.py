"""
URL routing for Truth Dashboard and Reality Checking APIs
========================================================

This module provides URL routing for the System Reality Self-Awareness Engine,
including web dashboard access and JSON APIs for programmatic access.
"""

from django.urls import path, include
from .truth_dashboard import (
    TruthDashboardView,
    TruthDashboardAPIView,
    ComponentDetailAPIView
)

app_name = 'truth'

urlpatterns = [
    # Web Dashboard
    path('', TruthDashboardView.as_view(), name='dashboard'),
    path('dashboard/', TruthDashboardView.as_view(), name='dashboard_alt'),

    # JSON API Endpoints
    path('api/', TruthDashboardAPIView.as_view(), name='api'),
    path('api/dashboard/', TruthDashboardAPIView.as_view(), name='api_dashboard'),
    path('api/component/<str:component_name>/', ComponentDetailAPIView.as_view(), name='api_component_detail'),

    # Reality Check Endpoints
    path('api/reality/', include([
        path('check/', TruthDashboardAPIView.as_view(), name='reality_check'),
        path('components/', TruthDashboardAPIView.as_view(), name='component_status'),
        path('flows/', TruthDashboardAPIView.as_view(), name='flow_status'),
    ])),
]