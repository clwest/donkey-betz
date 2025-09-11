"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

@api_view(['GET'])
@permission_classes([AllowAny])
def platform_info(request):
    """Unified platform information endpoint"""
    return Response({
        'success': True,
        'data': {
            'platform': 'Unified Donkey Betz Platform',
            'version': '1.0.0',
            'status': 'operational',
            'timestamp': '2025-01-20T00:00:00Z',
            'components': {
                'core': 'active',
                'agents': 'active',
                'sports': 'active',
                'content': 'active',
                'self_awareness': 'active',
                'api': 'active',
                'websockets': 'active'
            },
            'endpoints': {
                'admin': '/admin/',
                'api_root': '/api/',
                'api_v1': '/api/v1/',
                'agents_api': '/api/v1/agents/',
                'sports_api': '/api/v1/sports/',
                'content_api': '/api/v1/content/',
                'self_awareness_api': '/api/v1/self-awareness/',
                'api_docs': '/api/docs/',
                'api_schema': '/api/schema/',
                'api_auth': '/api-auth/'
            },
            'features': {
                'unified_api_versioning': 'enabled',
                'jwt_authentication': 'enabled',
                'rate_limiting': 'enabled',
                'api_documentation': 'enabled',
                'cors_configured': 'enabled',
                'security_headers': 'enabled',
                'odds_ingestion': 'enabled',
                'line_movement_tracking': 'enabled',
                'kelly_criterion': 'enabled',
                'arbitrage_detection': 'enabled',
                'betting_recommendations': 'enabled',
                'real_time_updates': 'enabled',
                'agent_orchestration': 'enabled',
                'content_generation': 'enabled',
                'self_awareness': 'enabled'
            }
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint with available versions and endpoints"""
    return Response({
        'success': True,
        'data': {
            'message': 'Welcome to Unified Donkey Betz Platform API',
            'api_version': 'v1',
            'available_versions': ['v1'],
            'endpoints': {
                'v1': {
                    'base': request.build_absolute_uri('/api/v1/'),
                    'agents': request.build_absolute_uri('/api/v1/agents/'),
                    'sports': request.build_absolute_uri('/api/v1/sports/'),
                    'content': request.build_absolute_uri('/api/v1/content/'),
                    'self_awareness': request.build_absolute_uri('/api/v1/self-awareness/'),
                }
            },
            'documentation': {
                'swagger': request.build_absolute_uri('/api/docs/'),
                'redoc': request.build_absolute_uri('/api/redoc/'),
                'schema': request.build_absolute_uri('/api/schema/')
            },
            'authentication': {
                'login': request.build_absolute_uri('/api-auth/login/'),
                'logout': request.build_absolute_uri('/api-auth/logout/')
            }
        }
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Root and API root endpoints
    path('', platform_info, name='platform-info'),
    path('api/', api_root, name='api-root'),
    
    # Core endpoints (auth, profile, assistant, etc.)
    path('', include('core.urls')),
    
    # Dashboard endpoints (for compatibility with frontend)
    path('api/dashboard/', include('dashboard.urls')),
    
    # Style Memory endpoints (for frontend compatibility)
    path('api/style-memory/', include('style_memory.urls')),
    
    # Unified API v1 endpoints
    path('api/v1/agents/', include('agents.urls')),
    path('api/v1/sports/', include('sports.urls')),
    path('api/v1/content/', include('content.urls')),
    path('api/v1/self-awareness/', include('self_awareness.urls')),
    
    # API Documentation (OpenAPI/Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API authentication (for browsable API)
    path('api-auth/', include('rest_framework.urls')),
]
