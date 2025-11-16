"""
Content Management System URLs

URL routing for content management APIs and WebSocket endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ContentTemplateViewSet, DocumentViewSet, KnowledgeBaseViewSet,
    ContentGenerationViewSet, ContentWorkflowViewSet, WorkflowExecutionViewSet,
    ContentAnalyticsViewSet, blog_list
)
from . import minifig_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'templates', ContentTemplateViewSet, basename='content-template')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'knowledge-bases', KnowledgeBaseViewSet, basename='knowledge-base')
router.register(r'generations', ContentGenerationViewSet, basename='content-generation')
router.register(r'workflows', ContentWorkflowViewSet, basename='content-workflow')
router.register(r'executions', WorkflowExecutionViewSet, basename='workflow-execution')
router.register(r'analytics', ContentAnalyticsViewSet, basename='content-analytics')

app_name = 'content'

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    # Additional endpoints
    path('blog/list/', blog_list, name='blog-list'),
    path('social/list/', blog_list, name='social-list'),  # Using same view for now
    # MiniFig Assets API (Session 111)
    path('minifigs/<uuid:minifig_id>/', minifig_views.get_minifig_detail, name='minifig-detail'),
    path('minifigs/', minifig_views.list_minifigs, name='minifig-list'),
]

# WebSocket URL patterns (to be included in core routing)
# Note: These are defined separately and should be imported in the main ASGI routing
# websocket_urlpatterns = [
#     path('ws/content/processing/', 'content.consumers.ContentProcessingConsumer'),
#     path('ws/content/analytics/', 'content.consumers.ContentAnalyticsConsumer'),
# ]