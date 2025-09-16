"""
URL configuration for the Data Persistence API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UnifiedSearchView, AgentKnowledgeViewSet, SpiderDataViewSet,
    EmbeddingManagementView, SystemInsightsView,
    DocumentSearchView, ContentGenerationSearchView
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'agent-knowledge', AgentKnowledgeViewSet)
router.register(r'spider-data', SpiderDataViewSet)

app_name = 'persistence'

urlpatterns = [
    # ViewSet routes
    path('api/v1/', include(router.urls)),

    # Custom API endpoints
    path('api/v1/search/', UnifiedSearchView.as_view(), name='unified-search'),
    path('api/v1/embeddings/', EmbeddingManagementView.as_view(), name='embedding-management'),
    path('api/v1/insights/', SystemInsightsView.as_view(), name='system-insights'),

    # Content integration endpoints
    path('api/v1/search/documents/', DocumentSearchView.as_view(), name='document-search'),
    path('api/v1/search/generated-content/', ContentGenerationSearchView.as_view(), name='generated-content-search'),
]