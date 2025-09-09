"""
URL patterns for Self-Awareness module
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SelfAwarenessAPIView,
    SystemMetricsViewSet,
    CodeSearchAPIView,
    CodebaseAnalysisAPIView,
    ArchitectureAnalysisAPIView,
    SelfAnalysisAPIView,
    SystemEvolutionAPIView,
    OptimizationAPIView,
    SelfHealingAPIView,
    dashboard_view,
    realtime_status,
)

app_name = 'self_awareness'

# Router for ViewSets
router = DefaultRouter()
router.register(r'metrics', SystemMetricsViewSet, basename='metrics')

urlpatterns = [
    # API Router (prefix removed as it's added in main urls.py)
    path('', include(router.urls)),
    
    # Main self-awareness API endpoints
    path('status/', SelfAwarenessAPIView.as_view(), name='status'),
    path('realtime/', realtime_status, name='realtime_status'),
    
    # Code search and analysis
    path('code/search/', CodeSearchAPIView.as_view(), name='code_search'),
    path('codebase/analysis/', CodebaseAnalysisAPIView.as_view(), name='codebase_analysis'),
    path('architecture/analysis/', ArchitectureAnalysisAPIView.as_view(), name='architecture_analysis'),
    
    # Self-analysis
    path('analysis/', SelfAnalysisAPIView.as_view(), name='self_analysis'),
    
    # System evolution
    path('evolution/', SystemEvolutionAPIView.as_view(), name='system_evolution'),
    
    # Optimization
    path('optimization/', OptimizationAPIView.as_view(), name='optimization'),
    
    # Self-healing
    path('healing/', SelfHealingAPIView.as_view(), name='self_healing'),
    
    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),
]