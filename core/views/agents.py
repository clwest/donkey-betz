"""
API Views for the Agent Registry System

Session 728: Migrated from agents/views.py to core/views/agents.py
"""

import logging
from django.utils import timezone
from django.db.models import Q, Count, Avg
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
import django_filters

# Session 392: Updated to use canonical import path
from core.models.agents_registry import (
    UnifiedAgentTemplate,
    AgentExecution,
    AgentOrchestration,
    AgentTool,
    AgentRegistry,
    AgentChannel,
    AgentChannelMessage,
    AgentChannelMembership
)
from core.serializers_agents import (
    UnifiedAgentTemplateSerializer,
    UnifiedAgentTemplateListSerializer,
    AgentExecutionSerializer,
    AgentExecutionListSerializer,
    AgentOrchestrationSerializer,
    AgentToolSerializer,
    AgentRegistrySerializer,
    AgentChannelSerializer,
    AgentChannelListSerializer,
    AgentChannelMessageSerializer,
    AgentChannelMessageListSerializer,
    AgentChannelMembershipSerializer,
    CreateChannelSerializer,
    PostMessageSerializer
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200


class AgentExecutionFilter(django_filters.FilterSet):
    """Custom filter for AgentExecution to support JSON field filtering"""
    input_data__game_id = django_filters.CharFilter(
        field_name='input_data',
        lookup_expr='game_id__iexact',
        method='filter_game_id'
    )
    
    def filter_game_id(self, queryset, name, value):
        """Filter by game_id in the input_data JSON field"""
        if value:
            return queryset.filter(input_data__game_id=value)
        return queryset
    
    class Meta:
        model = AgentExecution
        fields = ['status', 'priority', 'template__specialization', 'input_data__game_id']


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
        from core.tasks_agents import execute_agent
        from agents.tasks_enhanced import execute_agent_with_tools
        
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
        
        # Use enhanced execution for sports agents with tools
        if 'sports' in agent_template.domain_tags or agent_template.required_tools:
            logger.info(f"Using enhanced execution with tools for {agent_template.name}")
            execute_agent_with_tools.delay(execution_id=execution.execution_id)
        else:
            # Use standard execution for other agents
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = AgentExecutionFilter  # Use custom filter class
    
    def get_permissions(self):
        """Dynamic permissions based on query params"""
        # If querying by game_id, allow any access
        if self.request.query_params.get('input_data__game_id'):
            return [permissions.AllowAny()]
        # Otherwise require authentication
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgentExecutionListSerializer
        return AgentExecutionSerializer
    
    def get_queryset(self):
        queryset = self.queryset.select_related('template', 'user', 'parent_orchestration')
        
        # Don't filter by user if querying by game_id
        game_id = self.request.query_params.get('input_data__game_id')
        
        if not game_id and self.request.user.is_authenticated:
            # Only filter by user if not querying by game_id
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def with_results(self, request):
        """Get executions with full results included"""
        # Apply same filtering as get_queryset
        queryset = self.queryset.select_related('template', 'user', 'parent_orchestration')
        
        # Don't filter by user if querying by game_id
        game_id = self.request.query_params.get('input_data__game_id')
        
        if not game_id and self.request.user.is_authenticated:
            # Only filter by user if not querying by game_id
            queryset = queryset.filter(user=self.request.user)
        
        # Apply ordering and other filters
        queryset = queryset.order_by('-created_at')
        
        # Apply filters from query params
        status = request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Apply game_id filter if provided
        if game_id:
            queryset = queryset.filter(input_data__game_id=game_id)
            
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Use full serializer to include results
            serializer = AgentExecutionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Use full serializer to include results
        serializer = AgentExecutionSerializer(queryset, many=True)
        return Response(serializer.data)


class AgentOrchestrationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent orchestrations"""

    queryset = AgentOrchestration.objects.all()
    serializer_class = AgentOrchestrationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]  # Require authentication
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'execution_strategy']

    def get_queryset(self):
        # Filter by authenticated user or show all for staff
        if self.request.user.is_staff:
            return self.queryset.select_related('user').order_by('-created_at')
        return self.queryset.filter(user=self.request.user).select_related('user').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Execute an orchestration - run all agents in sequence/parallel.
        Session 735: Added execute action for orchestrations.
        """
        from core.tasks_agents import execute_orchestration

        orchestration = self.get_object()

        # Check if already running
        if orchestration.status == 'running':
            return Response({
                'success': False,
                'error': 'Orchestration is already running'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update status to running
        orchestration.status = 'running'
        orchestration.current_agent_index = 0
        orchestration.progress_percentage = 0
        orchestration.save()

        # Queue the orchestration execution
        try:
            execute_orchestration.delay(orchestration_id=str(orchestration.id))
            logger.info(f"Queued orchestration execution: {orchestration.name}")

            return Response({
                'success': True,
                'orchestration_id': str(orchestration.id),
                'name': orchestration.name,
                'status': 'running',
                'message': f'Orchestration "{orchestration.name}" has been started'
            }, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logger.error(f"Failed to queue orchestration: {e}")
            orchestration.status = 'failed'
            orchestration.save()
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """
        Reset an orchestration to pending status so it can be run again.
        Session 735: Added reset action for orchestrations.
        """
        orchestration = self.get_object()

        # Can't reset if currently running
        if orchestration.status == 'running':
            return Response({
                'success': False,
                'error': 'Cannot reset a running orchestration. Wait for it to complete or fail.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Reset to initial state
        from decimal import Decimal
        orchestration.status = 'pending'
        orchestration.current_agent_index = 0
        orchestration.progress_percentage = 0
        orchestration.intermediate_results = []
        orchestration.final_result = None
        orchestration.total_execution_time = None
        orchestration.total_cost = Decimal('0.000000')  # Reset to 0, not None (NOT NULL constraint)
        orchestration.save()

        logger.info(f"Reset orchestration: {orchestration.name}")

        return Response({
            'success': True,
            'orchestration_id': str(orchestration.id),
            'name': orchestration.name,
            'status': 'pending',
            'message': f'Orchestration "{orchestration.name}" has been reset and is ready to run'
        })

    @action(detail=True, methods=['get'])
    def output(self, request, pk=None):
        """
        Session 735: Get full orchestration output including all agent results.
        Returns the complete intermediate_results and individual agent outputs.
        """
        orchestration = self.get_object()

        # Get all agent executions for this orchestration
        executions = AgentExecution.objects.filter(
            parent_orchestration=orchestration
        ).order_by('created_at')

        agent_outputs = []
        for exec in executions:
            result = exec.result or {}
            agent_outputs.append({
                'agent_name': exec.template.name if exec.template else 'Unknown',
                'execution_id': exec.execution_id,
                'status': exec.status,
                'task_description': exec.task_description,
                'full_output': result.get('message', ''),
                'data': result.get('data'),
                'execution_time_ms': result.get('execution_time_ms', 0),
                'cost': result.get('cost', 0.0),
                'tokens_used': result.get('tokens_used', 0),
                'created_at': exec.created_at.isoformat(),
                'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
            })

        return Response({
            'success': True,
            'orchestration': {
                'id': str(orchestration.id),
                'name': orchestration.name,
                'status': orchestration.status,
                'total_execution_time': orchestration.total_execution_time,
                'total_cost': float(orchestration.total_cost) if orchestration.total_cost else 0.0,
                'created_at': orchestration.created_at.isoformat(),
            },
            'agent_outputs': agent_outputs,
            'intermediate_results': orchestration.intermediate_results or [],
            'final_result': orchestration.final_result,
            'output_count': len(agent_outputs),
        })


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
def game_executions(request, game_id):
    """
    Get agent executions for a specific game.
    """
    try:
        executions = AgentExecution.objects.filter(
            input_data__game_id=game_id
        ).select_related('template').order_by('-created_at')
        
        # Serialize the executions
        data = []
        for execution in executions[:20]:  # Limit to 20 most recent
            data.append({
                'execution_id': execution.execution_id,
                'template': {
                    'name': execution.template.name if execution.template else None,
                    'display_name': execution.template.display_name if execution.template else None,
                    'specialization': execution.template.specialization if execution.template else None,
                },
                'status': execution.status,
                'task_description': execution.task_description,
                'result': execution.result,
                'created_at': execution.created_at.isoformat(),
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'error_message': execution.error_message,
            })
        
        return Response({
            'game_id': game_id,
            'executions': data,
            'total_count': executions.count()
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch game executions: {e}")
        return Response({
            'error': str(e)
        }, status=500)


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


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  # Allow any for now
def execute_agent(request):
    """
    Execute an agent by name or type.
    This is a simplified endpoint for quick agent execution.
    """
    import uuid
    from core.tasks_agents import execute_agent as execute_agent_task
    
    agent_type = request.data.get('agent_type', '')
    agent_name = request.data.get('agent_name', '')
    task = request.data.get('task', '')
    parameters = request.data.get('parameters', {})
    
    logger.info(f"Execute agent request: type={agent_type}, name={agent_name}")
    
    # Try to find the agent by type (name field) or display_name
    agent_template = None
    
    # First try by exact name match
    if agent_type:
        agent_template = UnifiedAgentTemplate.objects.filter(
            Q(name=agent_type) | Q(name=agent_type.replace('-', '_'))
        ).first()
    
    # If not found, try by display name
    if not agent_template and agent_name:
        agent_template = UnifiedAgentTemplate.objects.filter(
            display_name__iexact=agent_name
        ).first()
    
    # If still not found, try a fuzzy match
    if not agent_template and agent_type:
        # Try with underscores instead of hyphens
        clean_type = agent_type.lower().replace('-', '_')
        agent_template = UnifiedAgentTemplate.objects.filter(
            Q(name__icontains=clean_type) |
            Q(display_name__icontains=agent_type.replace('-', ' '))
        ).first()
    
    if not agent_template:
        # Create a basic agent on the fly if it doesn't exist
        logger.warning(f"Agent not found, creating on the fly: {agent_type}")
        agent_template = UnifiedAgentTemplate.objects.create(
            name=agent_type.replace('-', '_'),
            display_name=agent_type.replace('-', ' ').title(),
            description=f"Auto-generated agent for {agent_type}",
            specialization='general',
            system_prompt="You are a helpful AI assistant.",
            llm_provider='openai',
            llm_model='gpt-5-nano',
            is_active=True,
            is_public=True
        )
    
    # Generate unique execution ID
    execution_id = f"exec_{agent_template.name}_{uuid.uuid4().hex[:8]}"
    
    # Create execution instance
    execution = AgentExecution.objects.create(
        template=agent_template,
        user=request.user if request.user.is_authenticated else None,
        execution_id=execution_id,
        task_description=task,
        task_type='betting_analysis' if 'betting' in agent_type.lower() else 'general',
        context={'parameters': parameters},
        input_data=parameters,
        priority='normal',
        websocket_channel=parameters.get('game_id', '') if parameters else ''
    )
    
    logger.info(f"Created agent execution {execution.execution_id} for agent {agent_template.name}")
    
    # Send initial WebSocket notification that agent is queued
    if parameters.get('game_id'):
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            try:
                game_id = parameters.get('game_id')
                
                # Send queued message
                async_to_sync(channel_layer.group_send)(
                    f"agents_general",
                    {
                        "type": "agent_progress",
                        "data": {
                            "game_id": game_id,
                            "agent_id": agent_type,
                            "agent_name": agent_template.display_name,
                            "execution_id": execution.execution_id,
                            "message_type": "queued",
                            "content": f"⏳ {agent_template.display_name} queued for execution...",
                            "phase": "queued",
                            "status": "queued",
                            "timestamp": timezone.now().isoformat()
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send WebSocket notification: {e}")
    
    # Actually execute the agent using Celery
    try:
        execute_agent_task.delay(execution_id=execution.execution_id)
        logger.info(f"Queued agent execution task for {execution.execution_id}")
        execution_status = 'queued'
        message = f'{agent_template.display_name} has been queued for execution'
    except Exception as e:
        logger.error(f"Failed to queue agent execution: {e}")
        execution_status = 'failed'
        message = f'Failed to queue {agent_template.display_name}: {str(e)}'
    
    return Response({
        'success': execution_status == 'queued',
        'execution_id': execution.execution_id,
        'agent_name': agent_template.display_name,
        'status': execution_status,
        'message': message
    }, status=status.HTTP_201_CREATED)


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


# =============================================================================
# Agent Channel ViewSets - "Slack for AI Agents"
# =============================================================================

class AgentChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for managing agent channels"""
    
    queryset = AgentChannel.objects.all()
    serializer_class = AgentChannelSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['channel_type', 'is_active', 'is_archived', 'is_public']

    def get_serializer_class(self):
        if self.action == 'list':
            return AgentChannelListSerializer
        elif self.action == 'create':
            return CreateChannelSerializer
        return AgentChannelSerializer

    def get_queryset(self):
        """Filter channels based on user access"""
        # Session 735: Fixed - AgentChannel uses is_archived, not is_active
        queryset = self.queryset.filter(is_archived=False)
        
        # Filter by search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(display_name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Include only channels user has access to
        # For now, show all active channels (we can add privacy later)
        # In future, filter by membership if needed
        user = self.request.user
        if not user.is_staff:
            # Show all active channels for now
            # Can add membership filtering later if needed
            pass
        
        return queryset.select_related('created_by', 'orchestration').order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new channel"""
        # Get data from request
        data = request.data.copy()
        
        # Create the channel directly
        channel = AgentChannel.objects.create(
            name=data.get('name'),
            display_name=data.get('display_name'),
            description=data.get('description', ''),
            channel_type=data.get('channel_type', 'general'),
            created_by=request.user,
            is_active=True,
            is_public=data.get('is_public', True)
        )
        
        # Add creator as admin member
        AgentChannelMembership.objects.create(
            channel=channel,
            user=request.user,
            role='admin',
            notification_level='all',
            is_active=True
        )
        
        # Serialize and return
        serializer = self.get_serializer(channel)
        return Response(serializer.data, status=201)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a channel"""
        channel = self.get_object()
        
        # For now, allow joining any channel
        # Can add privacy checks later when is_private field is added
        
        # Create or reactivate membership
        membership, created = AgentChannelMembership.objects.get_or_create(
            channel=channel,
            user=request.user,
            defaults={
                'role': 'member',
                'notification_level': 'all',
                'is_active': True
            }
        )
        
        if not created and not membership.is_active:
            membership.is_active = True
            membership.left_at = None
            membership.save()
        
        return Response({
            'message': 'Successfully joined channel',
            'membership_id': membership.id
        })
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a channel"""
        channel = self.get_object()
        
        try:
            membership = AgentChannelMembership.objects.get(
                channel=channel,
                user=request.user,
                is_active=True
            )
            membership.is_active = False
            membership.left_at = timezone.now()
            membership.save()
            
            return Response({'message': 'Successfully left channel'})
        except AgentChannelMembership.DoesNotExist:
            return Response(
                {'error': 'Not a member of this channel'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a channel"""
        channel = self.get_object()
        
        # Check if user has access
        # For now, allow access to all channels
        # Can add privacy checks later when is_private field is added
        
        # Get messages with pagination
        messages = channel.messages.filter(is_active=True).order_by('-created_at')
        
        # Filter by thread if specified
        thread_id = request.query_params.get('thread_id')
        if thread_id:
            messages = messages.filter(thread_id=thread_id)
        
        # Paginate
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(messages, request)
        
        serializer = AgentChannelMessageListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def post_message(self, request, pk=None):
        """Post a message to a channel"""
        channel = self.get_object()
        
        # Check if user is a member
        # For now, allow posting in all channels
        # Can add privacy checks later when is_private field is added
        
        serializer = PostMessageSerializer(data=request.data)
        if serializer.is_valid():
            # Create the message
            message = AgentChannelMessage.objects.create(
                channel=channel,
                user=request.user,
                message_type=serializer.validated_data.get('message_type', 'user_message'),
                content=serializer.validated_data['content'],
                rich_content=serializer.validated_data.get('rich_content', {}),
                thread_id=serializer.validated_data.get('thread_id'),
                parent_message_id=serializer.validated_data.get('parent_message')
            )
            
            # Broadcast via WebSocket (if available)
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                group_name = f'channel_{channel.id}'
                
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'channel_message',
                        'data': AgentChannelMessageSerializer(message).data
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to broadcast message via WebSocket: {e}")
            
            return Response(
                AgentChannelMessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get members of a channel"""
        channel = self.get_object()
        
        # Check if user has access
        # For now, allow access to all channel members
        # Can add privacy checks later when is_private field is added
        
        memberships = channel.memberships.filter(is_active=True).select_related(
            'user', 'agent_template'
        )
        
        serializer = AgentChannelMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class AgentChannelMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing channel messages"""
    
    queryset = AgentChannelMessage.objects.all()
    serializer_class = AgentChannelMessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['channel', 'message_type', 'thread_id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgentChannelMessageListSerializer
        return AgentChannelMessageSerializer
    
    def get_queryset(self):
        """Filter messages based on channel access"""
        queryset = self.queryset.filter(is_active=True)
        
        # Filter by channels user has access to
        user = self.request.user
        if not user.is_staff:
            # Get channels user can access
            # For now, allow access to all channels
            accessible_channels = AgentChannel.objects.all().values_list('id', flat=True)
            
            queryset = queryset.filter(channel_id__in=accessible_channels)
        
        return queryset.select_related(
            'channel', 'user', 'agent_instance__template', 'parent_message'
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a message with user context"""
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete messages"""
        instance.is_active = False
        instance.updated_at = timezone.now()
        instance.save()
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add a reaction to a message"""
        message = self.get_object()
        emoji = request.data.get('emoji', '👍')
        
        if not message.reactions:
            message.reactions = {}
        
        if emoji not in message.reactions:
            message.reactions[emoji] = []
        
        user_id = str(request.user.id)
        if user_id not in message.reactions[emoji]:
            message.reactions[emoji].append(user_id)
        else:
            # Toggle reaction off
            message.reactions[emoji].remove(user_id)
            if not message.reactions[emoji]:
                del message.reactions[emoji]
        
        message.save()
        
        return Response({'reactions': message.reactions})


class AgentChannelMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for managing channel memberships"""
    
    queryset = AgentChannelMembership.objects.all()
    serializer_class = AgentChannelMembershipSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['channel', 'role', 'is_active', 'is_watching']
    
    def get_queryset(self):
        """Filter memberships based on user"""
        queryset = self.queryset.all()
        
        # Filter by user's own memberships unless staff
        user = self.request.user
        if not user.is_staff:
            # Show user's own memberships and memberships in channels they're admin of
            admin_channels = queryset.filter(
                user=user,
                role='admin',
                is_active=True
            ).values_list('channel_id', flat=True)
            
            queryset = queryset.filter(
                Q(user=user) |
                Q(channel_id__in=admin_channels)
            )
        
        return queryset.select_related(
            'channel', 'user', 'agent_template'
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mute(self, request, pk=None):
        """Mute notifications for a membership"""
        membership = self.get_object()
        
        # Check if user owns this membership
        if membership.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Cannot modify another user\'s membership'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        membership.is_muted = True
        membership.notification_level = 'none'
        membership.save()
        
        return Response({'message': 'Channel muted successfully'})
    
    @action(detail=True, methods=['post'])
    def unmute(self, request, pk=None):
        """Unmute notifications for a membership"""
        membership = self.get_object()
        
        # Check if user owns this membership
        if membership.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Cannot modify another user\'s membership'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        membership.is_muted = False
        membership.notification_level = request.data.get('notification_level', 'mentions')
        membership.save()
        
        return Response({'message': 'Channel unmuted successfully'})
