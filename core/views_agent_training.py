"""
Agent Training API Views
========================

Session 217B: REST API endpoints for agent training and configuration.

Provides endpoints for:
- Agent configuration management
- Capability management
- Agent templates
- Training history and stats
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.services.agent_training import get_agent_training_service

logger = logging.getLogger(__name__)


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_agents(request):
    """
    GET /api/training/agents/

    Get all agent configurations.
    """
    service = get_agent_training_service(request.user)
    agents = service.get_all_agents()

    return Response({
        'agents': agents,
        'total': len(agents)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent(request, agent_name):
    """
    GET /api/training/agents/{agent_name}/

    Get configuration for a specific agent.
    """
    service = get_agent_training_service(request.user)
    config = service.get_agent_config(agent_name)

    if not config:
        return Response(
            {'error': f'Agent not found: {agent_name}'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(config)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_agent(request, agent_name):
    """
    PUT/PATCH /api/training/agents/{agent_name}/

    Update agent configuration.

    Body:
        display_name: Optional display name
        description: Optional description
        capabilities: Optional list of capability IDs
        is_active: Optional active status
    """
    data = request.data
    service = get_agent_training_service(request.user)

    result = service.update_agent_config(
        agent_name=agent_name,
        display_name=data.get('display_name'),
        description=data.get('description'),
        capabilities=data.get('capabilities'),
        is_active=data.get('is_active')
    )

    if result.get('success'):
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# CAPABILITIES
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_capabilities(request):
    """
    GET /api/training/capabilities/

    Get all available capabilities.
    """
    service = get_agent_training_service(request.user)
    capabilities = service.get_available_capabilities()

    return Response({
        'capabilities': capabilities,
        'total': len(capabilities)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_capability(request, agent_name):
    """
    POST /api/training/agents/{agent_name}/capabilities/

    Add a capability to an agent.

    Body:
        capability_id: ID of the capability to add
    """
    capability_id = request.data.get('capability_id')

    if not capability_id:
        return Response(
            {'error': 'capability_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = get_agent_training_service(request.user)
    result = service.add_capability(agent_name, capability_id)

    if result.get('success'):
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_capability(request, agent_name, capability_id):
    """
    DELETE /api/training/agents/{agent_name}/capabilities/{capability_id}/

    Remove a capability from an agent.
    """
    service = get_agent_training_service(request.user)
    result = service.remove_capability(agent_name, capability_id)

    if result.get('success'):
        return Response(result)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# TEMPLATES
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    """
    GET /api/training/templates/

    Get available agent templates.
    """
    service = get_agent_training_service(request.user)
    templates = service.get_agent_templates()

    return Response({
        'templates': templates,
        'total': len(templates)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_from_template(request):
    """
    POST /api/training/agents/from-template/

    Create a new agent from a template.

    Body:
        template_id: ID of the template to use
        custom_name: Optional custom name for the agent
    """
    template_id = request.data.get('template_id')

    if not template_id:
        return Response(
            {'error': 'template_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = get_agent_training_service(request.user)
    result = service.create_agent_from_template(
        template_id=template_id,
        custom_name=request.data.get('custom_name')
    )

    if result.get('success'):
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# TRAINING HISTORY & STATS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def training_history(request):
    """
    GET /api/training/history/

    Get training history for agents.

    Query params:
        agent_name: Optional filter by agent
    """
    agent_name = request.GET.get('agent_name')

    service = get_agent_training_service(request.user)
    history = service.get_training_history(agent_name)

    return Response({
        'history': history,
        'total': len(history)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def training_stats(request):
    """
    GET /api/training/stats/

    Get overall training statistics.
    """
    service = get_agent_training_service(request.user)
    stats = service.get_training_stats()

    return Response(stats)


# =============================================================================
# DASHBOARD
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def training_dashboard(request):
    """
    GET /api/training/dashboard/

    Get all data for training dashboard.
    """
    service = get_agent_training_service(request.user)

    return Response({
        'agents': service.get_all_agents(),
        'capabilities': service.get_available_capabilities(),
        'templates': service.get_agent_templates(),
        'stats': service.get_training_stats(),
        'recent_history': service.get_training_history()[:10]
    })
