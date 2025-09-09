"""
URL configuration for Unified Donkey Betz Platform.

Main URL routing for the unified mega-platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Import core views
from core.views import platform_status, platform_info, record_metric

# Create API router
router = DefaultRouter()

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Core platform APIs
    path('api/status/', platform_status, name='platform-status'),
    path('api/info/', platform_info, name='platform-info'),
    path('api/metrics/', record_metric, name='record-metric'),
    
    # API router
    path('api/v1/', include(router.urls)),
    
    # App-specific APIs
    path('api/v1/agents/', include('agents.urls')),
    path('api/v1/sports/', include('sports.urls')),
    path('api/v1/content/', include('content.urls')),
    path('api/v1/self-awareness/', include('self_awareness.urls')),
    
    # REST framework browsable API (development only)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
