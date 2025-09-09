"""
API Views for the Agent Registry System
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
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
    max_page_size = 100


class UnifiedAgentTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent templates"""
    
    queryset = UnifiedAgentTemplate.objects.all()
    serializer_class = UnifiedAgentTemplateSerializer
    pagination_class = StandardResultsSetPagination
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
        queryset = self.queryset
        
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
        agent_template = self.get_object()
        
        # Create execution instance
        execution = AgentExecution.objects.create(
            template=agent_template,
            user=request.user if request.user.is_authenticated else None,
            task_description=request.data.get('task_description', ''),
            task_type=request.data.get('task_type', ''),
            context=request.data.get('context', {}),
            input_data=request.data.get('input_data', {}),
            priority=request.data.get('priority', 'normal'),
            websocket_channel=request.data.get('websocket_channel', '')
        )
        
        logger.info(f"Created agent execution {execution.execution_id}")
        
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority', 'template__specialization']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgentExecutionListSerializer
        return AgentExecutionSerializer
    
    def get_queryset(self):
        return self.queryset.select_related('template', 'user', 'parent_orchestration').order_by('-created_at')


class AgentOrchestrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent orchestrations"""
    
    queryset = AgentOrchestration.objects.all()
    serializer_class = AgentOrchestrationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'execution_strategy']
    
    def get_queryset(self):
        return self.queryset.select_related('user').order_by('-created_at')


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
