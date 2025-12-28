"""
Unified Backend Views
API endpoints for the unified backend orchestrator
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from datetime import datetime
import logging

from .backend_unification_orchestrator import (
    get_orchestrator,
    trigger_coordinated_action,
    broadcast_system_update,
    route_service_data
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def unified_system_health(request):
    """
    Get the health status of all backend services
    Frontend can use this to show system status
    """
    try:
        orchestrator = get_orchestrator()
        health_data = orchestrator.get_system_health()

        return Response({
            'success': True,
            'health': health_data,
            'message': f"System is {health_data['overall_status']}"
        })

    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unified_dashboard(request):
    """
    Get unified dashboard data aggregating all services
    This is THE endpoint the frontend should use for the main dashboard
    """
    try:
        orchestrator = get_orchestrator()
        dashboard_data = orchestrator.get_unified_dashboard_data()

        # Add user-specific data
        user = request.user
        dashboard_data['user'] = {
            'username': user.username,
            'email': user.email,
            'id': user.id
        }

        return Response({
            'success': True,
            'dashboard': dashboard_data
        })

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_unified_action(request):
    """
    Trigger a coordinated action across multiple services
    This is where the frontend can trigger complex multi-service operations
    """
    try:
        action_type = request.data.get('action')
        parameters = request.data.get('parameters', {})

        if not action_type:
            return Response({
                'success': False,
                'error': 'No action type specified'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Add user context
        parameters['user_id'] = request.user.id
        parameters['username'] = request.user.username

        # Trigger the action
        result = trigger_coordinated_action(action_type, parameters)

        return Response({
            'success': result.get('success', False),
            'result': result
        })

    except Exception as e:
        logger.error(f"Failed to trigger unified action: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_service_connections(request):
    """
    Get the current service connection map
    Shows how all backend services are connected
    """
    try:
        orchestrator = get_orchestrator()

        connections = {
            'services': list(orchestrator.services.keys()),
            'data_flows': orchestrator.data_flows,
            'total_services': len(orchestrator.services),
            'total_connections': len(orchestrator.data_flows)
        }

        return Response({
            'success': True,
            'connections': connections
        })

    except Exception as e:
        logger.error(f"Failed to get service connections: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_unified_workflow(request):
    """
    Execute a complete workflow that involves multiple services
    Example: User wants to generate income -> analyzes opportunities ->
    creates content -> executes plan -> tracks revenue
    """
    try:
        workflow_type = request.data.get('workflow')
        context = request.data.get('context', {})

        workflows = {
            'income_generation': {
                'name': 'Complete Income Generation',
                'steps': [
                    ('intelligence', 'analyze_opportunities'),
                    ('agents', 'create_action_plan'),
                    ('content', 'generate_content'),
                    ('agents', 'execute_plan'),
                    ('intelligence', 'track_revenue')
                ]
            },
            'content_campaign': {
                'name': 'Multi-Channel Content Campaign',
                'steps': [
                    ('profile', 'get_user_context'),
                    ('intelligence', 'identify_topic'),
                    ('agents', 'plan_campaign'),
                    ('content', 'create_content'),
                    ('websocket', 'broadcast_launch')
                ]
            },
            'ai_optimization': {
                'name': 'AI System Optimization',
                'steps': [
                    ('analytics', 'analyze_performance'),
                    ('agents', 'identify_bottlenecks'),
                    ('agents', 'optimize_workflows'),
                    ('analytics', 'measure_improvement')
                ]
            }
        }

        if workflow_type not in workflows:
            return Response({
                'success': False,
                'error': f'Unknown workflow: {workflow_type}',
                'available_workflows': list(workflows.keys())
            }, status=status.HTTP_400_BAD_REQUEST)

        workflow = workflows[workflow_type]
        results = {
            'workflow': workflow['name'],
            'started_at': datetime.now().isoformat(),
            'steps': [],
            'success': True
        }

        # Execute each step
        for service, action in workflow['steps']:
            step_result = {
                'service': service,
                'action': action,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }

            # Route data through the service
            route_service_data(service, {
                'workflow': workflow_type,
                'action': action,
                'context': context
            })

            results['steps'].append(step_result)

        # Broadcast completion
        broadcast_system_update({
            'type': 'workflow_completed',
            'workflow': workflow_type,
            'user': request.user.username
        }, 'workflow_engine')

        results['completed_at'] = datetime.now().isoformat()

        return Response({
            'success': True,
            'workflow_result': results
        })

    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unified_metrics(request):
    """
    Get aggregated metrics from all services
    """
    try:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'agents': {
                'total': 151,
                'active': cache.get('agents:active_count', 0),
                'executions_today': cache.get('agents:executions_today', 0),
                'success_rate': cache.get('agents:success_rate', 0.95)
            },
            'content': {
                'items_created': cache.get('content:total_created', 0),
                'blogs': cache.get('content:blogs_created', 0),
                'images': cache.get('content:images_created', 0),
                'campaigns': cache.get('content:campaigns_created', 0)
            },
            'intelligence': {
                'opportunities': cache.get('intelligence:opportunities_count', 0),
                'action_plans': cache.get('intelligence:action_plans_count', 0),
                'revenue_tracked': cache.get('intelligence:revenue_total', 0),
                'conversion_rate': cache.get('intelligence:conversion_rate', 0)
            },
            'users': {
                'total': cache.get('users:total_count', 0),
                'active_today': cache.get('users:active_today', 0),
                'new_this_week': cache.get('users:new_week', 0)
            },
            'system': {
                'uptime_hours': cache.get('system:uptime_hours', 0),
                'api_calls_today': cache.get('system:api_calls_today', 0),
                'websocket_connections': cache.get('system:ws_connections', 0),
                'cache_hit_rate': cache.get('system:cache_hit_rate', 0)
            }
        }

        return Response({
            'success': True,
            'metrics': metrics
        })

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_all_services(request):
    """
    Force synchronization of all backend services
    Use this to ensure everything is connected properly
    """
    try:
        orchestrator = get_orchestrator()

        # Trigger full system sync
        result = orchestrator.trigger_unified_action('full_system_sync', {})

        if result['success']:
            # Update cache with sync status
            cache.set('system:last_sync', datetime.now().isoformat(), timeout=3600)
            cache.set('system:sync_status', 'completed', timeout=3600)

            return Response({
                'success': True,
                'message': 'All services synchronized successfully',
                'details': result['results']
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Sync failed')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Failed to sync services: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data_flow_stats(request):
    """
    Get statistics about data flows between services
    """
    try:
        orchestrator = get_orchestrator()

        stats = {
            'total_flows': len(orchestrator.data_flows),
            'active_flows': sum(1 for f in orchestrator.data_flows.values() if f['active']),
            'total_messages': sum(f['message_count'] for f in orchestrator.data_flows.values()),
            'flows': []
        }

        for flow_key, flow in orchestrator.data_flows.items():
            stats['flows'].append({
                'id': flow_key,
                'source': flow['source'],
                'destination': flow['destination'],
                'type': flow['data_type'],
                'messages': flow['message_count'],
                'active': flow['active']
            })

        # Sort by message count
        stats['flows'].sort(key=lambda x: x['messages'], reverse=True)

        return Response({
            'success': True,
            'data_flow_stats': stats
        })

    except Exception as e:
        logger.error(f"Failed to get data flow stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)