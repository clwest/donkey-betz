"""
Core views for the Unified Donkey Betz Platform.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import SystemConfiguration, PlatformMetrics
import json
from datetime import datetime

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def platform_status(request):
    """
    Return comprehensive platform status information.
    
    This endpoint provides a health check and status overview
    of all platform components.
    """
    
    # Gather system statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_configs = SystemConfiguration.objects.count()
    active_configs = SystemConfiguration.objects.filter(is_active=True).count()
    total_metrics = PlatformMetrics.objects.count()
    
    # Get key configuration values
    max_agents = SystemConfiguration.get_config('max_concurrent_agents', 100)
    ai_provider = SystemConfiguration.get_config('default_ai_provider', 'openai')
    self_awareness = SystemConfiguration.get_config('enable_self_awareness', True)
    
    # Calculate uptime (simplified - from platform initialization)
    init_metric = PlatformMetrics.objects.filter(
        metric_name='platform_initialized'
    ).first()
    
    uptime_seconds = 0
    if init_metric:
        delta = datetime.now(init_metric.timestamp.tzinfo) - init_metric.timestamp
        uptime_seconds = int(delta.total_seconds())
    
    # System health indicators
    health_status = {
        'database': 'healthy',  # If we got here, DB is working
        'configuration': 'healthy' if active_configs > 0 else 'warning',
        'users': 'healthy' if total_users > 0 else 'warning',
        'metrics': 'healthy' if total_metrics > 0 else 'warning',
    }
    
    overall_health = 'healthy'
    if 'warning' in health_status.values():
        overall_health = 'warning'
    
    status_data = {
        'platform': 'Unified Donkey Betz',
        'version': '1.0.0-alpha',
        'status': overall_health,
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': uptime_seconds,
        
        'statistics': {
            'users': {
                'total': total_users,
                'active': active_users,
            },
            'configuration': {
                'total_settings': total_configs,
                'active_settings': active_configs,
            },
            'metrics': {
                'total_recorded': total_metrics,
            },
        },
        
        'key_settings': {
            'max_concurrent_agents': max_agents,
            'default_ai_provider': ai_provider,
            'self_awareness_enabled': self_awareness,
        },
        
        'health': health_status,
        
        'subsystems': {
            'agents': {'status': 'ready', 'description': 'Agent orchestration system'},
            'sports': {'status': 'ready', 'description': 'Sports analytics engine'},
            'content': {'status': 'ready', 'description': 'Content generation system'},
            'ai_services': {'status': 'ready', 'description': 'AI provider interface'},
            'self_awareness': {'status': 'ready', 'description': 'System introspection'},
        },
        
        'api': {
            'version': 'v1',
            'base_url': request.build_absolute_uri('/api/v1/'),
            'documentation': request.build_absolute_uri('/api/docs/'),
        }
    }
    
    return Response(status_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def platform_info(request):
    """
    Return basic platform information.
    
    Simple endpoint for checking if the platform is running.
    """
    
    return Response({
        'name': 'Unified Donkey Betz Platform',
        'description': 'Self-aware mega-platform combining AI content generation, sports analytics, and agent orchestration',
        'version': '1.0.0-alpha',
        'status': 'operational',
        'capabilities': [
            'Agent Orchestration (500+ agents)',
            'Sports Betting Analytics',
            'AI Content Generation',
            'Real-time Communication',
            'Self-Awareness & Code Modification',
            'Multi-Provider AI Integration',
        ],
        'architecture': {
            'backend': 'Django + DRF',
            'database': 'PostgreSQL + SQLite (dev)',
            'cache': 'Redis',
            'websockets': 'Django Channels',
            'ai_providers': ['OpenAI', 'Anthropic', 'Google', 'Local Models'],
        },
        'links': {
            'status': request.build_absolute_uri('/api/status/'),
            'admin': request.build_absolute_uri('/admin/'),
            'api_docs': request.build_absolute_uri('/api/docs/'),
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def record_metric(request):
    """
    Record a platform metric.
    
    Allows external systems to record metrics into the platform.
    """
    try:
        data = json.loads(request.body)
        
        metric = PlatformMetrics.record_metric(
            name=data.get('name'),
            value=float(data.get('value', 0)),
            metric_type=data.get('type', 'gauge'),
            subsystem=data.get('subsystem', 'system'),
            labels=data.get('labels', {})
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Metric recorded successfully',
            'metric_id': str(metric.id),
            'timestamp': metric.timestamp.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)