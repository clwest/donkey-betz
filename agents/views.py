"""
API Views for the Agent Registry System
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache

from .models import (
    UnifiedAgentTemplate,
    AgentExecution,
    AgentOrchestration,
    AgentTool,
    AgentRegistry
)
from .serializers import (
    UnifiedAgentTemplateSerializer,
    UnifiedAgentTemplateListSerializer,
    AgentExecutionSerializer,
    AgentExecutionListSerializer,
    AgentOrchestrationSerializer,
    AgentToolSerializer,
    AgentRegistrySerializer,
    AgentTaskMatchSerializer,
    AgentTaskMatchResultSerializer,
    ExecuteAgentSerializer,
    CreateOrchestrationSerializer,
    AgentRegistryStatsSerializer
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200


class UnifiedAgentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent templates"""
    
    queryset = UnifiedAgentTemplate.objects.all()
    serializer_class = UnifiedAgentTemplateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]  # Require authentication
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'specialization', 'llm_provider', 'is_active', 
        'is_public', 'is_verified', 'learning_enabled'
    ]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UnifiedAgentTemplateListSerializer
        return UnifiedAgentTemplateSerializer
    
    def get_queryset(self):
        # Show all active agents (including system agents without a creator)
        queryset = self.queryset.filter(is_active=True)
        
        # Filter by search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(display_name__icontains=search) |
                Q(description__icontains=search) |
                Q(capabilities__icontains=search) |
                Q(routing_keywords__icontains=search)
            )
        
        # Order by usage and success rate by default
        return queryset.select_related('creator', 'parent_template').order_by(
            '-usage_count', '-success_rate', 'name'
        )
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute an agent with the given parameters"""
        from .tasks import execute_agent
        
        agent_template = self.get_object()
        
        # Generate unique execution ID
        import uuid
        execution_id = f"exec_{agent_template.name}_{uuid.uuid4().hex[:8]}"
        
        # Create execution instance
        execution = AgentExecution.objects.create(
            template=agent_template,
            user=request.user if request.user.is_authenticated else None,
            execution_id=execution_id,
            task_description=request.data.get('task_description', ''),
            task_type=request.data.get('task_type', ''),
            context=request.data.get('context', {}),
            input_data=request.data.get('input_data', {}),
            priority=request.data.get('priority', 'normal'),
            websocket_channel=request.data.get('websocket_channel', '')
        )
        
        logger.info(f"Created agent execution {execution.execution_id}")
        
        # Trigger the Celery task
        execute_agent.delay(execution_id=execution.execution_id)
        
        return Response({
            'execution_id': execution.execution_id,
            'status': execution.status,
            'message': 'Agent execution queued successfully'
        }, status=status.HTTP_201_CREATED)


class AgentExecutionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent executions"""
    
    queryset = AgentExecution.objects.all()
    serializer_class = AgentExecutionSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]  # Require authentication
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'template__specialization']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgentExecutionListSerializer
        return AgentExecutionSerializer
    
    def get_queryset(self):
        # Filter by authenticated user
        return self.queryset.filter(user=self.request.user).select_related('template', 'user', 'parent_orchestration').order_by('-created_at')


class AgentOrchestrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent orchestrations"""
    
    queryset = AgentOrchestration.objects.all()
    serializer_class = AgentOrchestrationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]  # Require authentication
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'execution_strategy']
    
    def get_queryset(self):
        # Filter by authenticated user
        return self.queryset.filter(user=self.request.user).select_related('user').order_by('-created_at')


class AgentToolViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent tools"""
    
    queryset = AgentTool.objects.all()
    serializer_class = AgentToolSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tool_type', 'is_active']
    
    def get_queryset(self):
        return self.queryset.prefetch_related('compatible_agents').order_by('name')


class AgentRegistryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for agent registry operations"""
    
    queryset = AgentRegistry.objects.all()
    serializer_class = AgentRegistrySerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive registry statistics"""
        # Get basic statistics
        agents = UnifiedAgentTemplate.objects.filter(is_active=True)
        executions = AgentExecution.objects.all()
        
        stats = {
            'total_agents': agents.count(),
            'active_agents': agents.filter(is_active=True).count(),
            'total_executions': executions.count(),
            'total_orchestrations': AgentOrchestration.objects.count(),
            'avg_success_rate': agents.aggregate(avg_rate=Avg('success_rate'))['avg_rate'] or 0.0,
            'avg_execution_time': agents.aggregate(avg_time=Avg('avg_completion_time'))['avg_time'] or 0,
            'specialization_breakdown': dict(agents.values_list('specialization').annotate(count=Count('specialization'))),
            'provider_breakdown': dict(agents.values_list('llm_provider').annotate(count=Count('llm_provider'))),
            'recent_activity': [],
            'top_performing_agents': [],
            'capability_coverage': {'total_capabilities': 0, 'top_capabilities': []}
        }
        
        return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Health check endpoint for the agent system.
    Returns system status and basic statistics.
    """
    try:
        # Check database connectivity
        agent_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()
        active_executions = AgentExecution.objects.filter(
            status__in=['pending', 'running', 'initializing']
        ).count()
        
        # Check cache connectivity
        cache_key = 'agent_health_check'
        cache.set(cache_key, timezone.now().isoformat(), 60)
        cache_value = cache.get(cache_key)
        cache_status = 'healthy' if cache_value else 'unhealthy'
        
        # Get registry stats
        try:
            registry = AgentRegistry.objects.get(registry_name='unified_agent_registry')
            registry_stats = {
                'total_agents': registry.total_agents,
                'active_agents': registry.active_agents,
                'total_executions': registry.total_executions,
                'last_updated': registry.last_updated.isoformat() if registry.last_updated else None
            }
        except AgentRegistry.DoesNotExist:
            registry_stats = {
                'total_agents': agent_count,
                'active_agents': agent_count,
                'total_executions': 0,
                'last_updated': None
            }
        
        # Get tool registry stats
        from core.tools import ToolRegistry
        available_tools = ToolRegistry.list_tools()
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'cache': cache_status,
            'statistics': {
                'total_agents': agent_count,
                'active_executions': active_executions,
                'available_tools': len(available_tools),
                'tools': available_tools
            },
            'registry': registry_stats,
            'version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return Response({
            'status': 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def discover_agents(request):
    """
    Discover available agents.
    """
    agents = UnifiedAgentTemplate.objects.filter(is_active=True).values(
        'id', 'name', 'display_name', 'description', 
        'specialization', 'capabilities', 'usage_count'
    )
    
    return Response({
        'agents': list(agents),
        'total_count': UnifiedAgentTemplate.objects.filter(is_active=True).count()
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def orchestrations_list(request):
    """
    List active orchestrations.
    """
    orchestrations = AgentOrchestration.objects.filter(
        status__in=['pending', 'running']
    ).values(
        'id', 'name', 'status', 
        'execution_strategy', 'created_at'
    )[:10]
    
    return Response({
        'orchestrations': list(orchestrations),
        'total_count': AgentOrchestration.objects.filter(
            status__in=['pending', 'running']
        ).count()
    })
