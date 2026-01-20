"""
Agent Collaboration API Views
==============================

Session 214: REST API endpoints for agent collaboration management.

Endpoints:
- POST /api/collaboration/request/           - Request a collaboration
- GET  /api/collaboration/{id}/              - Get collaboration status
- POST /api/collaboration/{id}/respond/      - Respond to collaboration
- GET  /api/collaboration/history/           - Get collaboration history

Messages:
- POST /api/collaboration/messages/send/     - Send agent message
- GET  /api/collaboration/messages/          - Get messages for agent

Knowledge:
- POST /api/collaboration/knowledge/share/   - Share knowledge
- GET  /api/collaboration/knowledge/         - Search knowledge
- POST /api/collaboration/knowledge/{id}/learn/ - Learn knowledge
- POST /api/collaboration/knowledge/{id}/rate/  - Rate effectiveness

Performance:
- GET  /api/collaboration/performance/       - Get agent performance
- GET  /api/collaboration/top-performers/    - Get top performers
- GET  /api/collaboration/stats/             - Get overall stats

Utilities:
- GET  /api/collaboration/find-collaborator/ - Find best collaborator
"""

import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.services.agent_collaboration import (
    get_collaboration_service,
    CollaborationType,
    MessageType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# COLLABORATION ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_collaboration(request):
    """
    Request a collaboration between agents.

    POST body:
    {
        "requester": "image_agent",
        "target_agents": ["research_agent", "video_agent"],
        "collaboration_type": "parallel",  # delegation, consultation, etc.
        "task_description": "Create a brand identity package",
        "input_data": {"topic": "AI Startup"},
        "context": {}
    }
    """
    service = get_collaboration_service(request.user)
    data = request.data

    requester = data.get('requester')
    target_agents = data.get('target_agents', [])
    collab_type_str = data.get('collaboration_type', 'delegation')
    task_description = data.get('task_description', '')
    input_data = data.get('input_data', {})
    context = data.get('context', {})

    if not requester:
        return Response({
            'success': False,
            'error': 'requester is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not target_agents:
        return Response({
            'success': False,
            'error': 'target_agents is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        collab_type = CollaborationType(collab_type_str)
    except ValueError:
        return Response({
            'success': False,
            'error': f'Invalid collaboration_type. Valid types: {[ct.value for ct in CollaborationType]}'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        collaboration_id = service.request_collaboration(
            requester=requester,
            target_agents=target_agents,
            collaboration_type=collab_type,
            task_description=task_description,
            input_data=input_data,
            context=context
        )

        return Response({
            'success': True,
            'collaboration_id': collaboration_id,
            'message': f'Collaboration requested with {len(target_agents)} agents'
        })

    except Exception as e:
        logger.error(f"Failed to request collaboration: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_collaboration(request, collaboration_id):
    """Get the status of a collaboration."""
    service = get_collaboration_service(request.user)

    result = service.get_collaboration_status(collaboration_id)

    if not result:
        return Response({
            'success': False,
            'error': 'Collaboration not found'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'collaboration': result
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_collaboration(request, collaboration_id):
    """
    Respond to a collaboration request.

    POST body:
    {
        "agent_name": "research_agent",
        "response_data": {"research_results": [...]},
        "success": true
    }
    """
    service = get_collaboration_service(request.user)
    data = request.data

    agent_name = data.get('agent_name')
    response_data = data.get('response_data', {})
    success = data.get('success', True)

    if not agent_name:
        return Response({
            'success': False,
            'error': 'agent_name is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    result = service.respond_to_collaboration(
        collaboration_id=collaboration_id,
        agent_name=agent_name,
        response_data=response_data,
        success=success
    )

    if not result:
        return Response({
            'success': False,
            'error': 'Failed to respond to collaboration'
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'success': True,
        'message': 'Response recorded'
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # Session 782: Allow public access for Network tab
def collaboration_history(request):
    """Get collaboration history."""
    # Session 782: Use None for anonymous users
    user = request.user if request.user.is_authenticated else None
    service = get_collaboration_service(user)

    agent_name = request.query_params.get('agent')
    collab_type = request.query_params.get('type')
    status_filter = request.query_params.get('status')
    limit = int(request.query_params.get('limit', 50))

    history = service.get_collaboration_history(
        agent_name=agent_name,
        collaboration_type=collab_type,
        status=status_filter,
        limit=limit
    )

    return Response({
        'success': True,
        'count': len(history),
        'collaborations': history
    })


# =============================================================================
# MESSAGE ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    """
    Send a message from one agent to another.

    POST body:
    {
        "sender": "image_agent",
        "receiver": "research_agent",
        "message_type": "request",
        "content": {"task": "Find trending topics"},
        "context": {},
        "priority": 5
    }
    """
    service = get_collaboration_service(request.user)
    data = request.data

    sender = data.get('sender')
    receiver = data.get('receiver')
    msg_type_str = data.get('message_type', 'notification')
    content = data.get('content', {})
    context = data.get('context', {})
    priority = data.get('priority', 5)
    correlation_id = data.get('correlation_id')
    response_to = data.get('response_to')

    if not sender or not receiver:
        return Response({
            'success': False,
            'error': 'sender and receiver are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        msg_type = MessageType(msg_type_str)
    except ValueError:
        return Response({
            'success': False,
            'error': f'Invalid message_type. Valid types: {[mt.value for mt in MessageType]}'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        message = service.send_message(
            sender=sender,
            receiver=receiver,
            message_type=msg_type,
            content=content,
            context=context,
            priority=priority,
            correlation_id=correlation_id,
            response_to=response_to
        )

        return Response({
            'success': True,
            'message_id': str(message.id),
            'message': f'Message sent from {sender} to {receiver}'
        })

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    """Get messages for an agent."""
    service = get_collaboration_service(request.user)

    agent_name = request.query_params.get('agent')
    unread_only = request.query_params.get('unread', 'true').lower() == 'true'
    limit = int(request.query_params.get('limit', 50))

    if not agent_name:
        return Response({
            'success': False,
            'error': 'agent query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    messages = service.get_messages(
        agent_name=agent_name,
        unread_only=unread_only,
        limit=limit
    )

    return Response({
        'success': True,
        'count': len(messages),
        'messages': messages
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_processed(request, message_id):
    """Mark a message as processed."""
    service = get_collaboration_service(request.user)

    result = service.mark_message_processed(message_id)

    if not result:
        return Response({
            'success': False,
            'error': 'Message not found'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'message': 'Message marked as processed'
    })


# =============================================================================
# KNOWLEDGE ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_knowledge(request):
    """
    Share knowledge from an agent to the knowledge base.

    POST body:
    {
        "source_agent": "image_agent",
        "knowledge_type": "technique",
        "title": "Optimal prompt structure for logos",
        "description": "...",
        "content": {"pattern": "...", "examples": [...]},
        "domain": "image",
        "tags": ["logos", "prompting", "style"]
    }
    """
    service = get_collaboration_service(request.user)
    data = request.data

    source_agent = data.get('source_agent')
    knowledge_type = data.get('knowledge_type')
    title = data.get('title')
    description = data.get('description', '')
    content = data.get('content', {})
    domain = data.get('domain')
    tags = data.get('tags', [])

    if not all([source_agent, knowledge_type, title, domain]):
        return Response({
            'success': False,
            'error': 'source_agent, knowledge_type, title, and domain are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        knowledge_id = service.share_knowledge(
            source_agent=source_agent,
            knowledge_type=knowledge_type,
            title=title,
            description=description,
            content=content,
            domain=domain,
            tags=tags
        )

        return Response({
            'success': True,
            'knowledge_id': knowledge_id,
            'message': f'Knowledge shared by {source_agent}'
        })

    except Exception as e:
        logger.error(f"Failed to share knowledge: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_knowledge(request):
    """Search the knowledge base."""
    service = get_collaboration_service(request.user)

    query = request.query_params.get('q')
    domain = request.query_params.get('domain')
    knowledge_type = request.query_params.get('type')
    limit = int(request.query_params.get('limit', 20))

    knowledge = service.search_knowledge(
        query=query,
        domain=domain,
        knowledge_type=knowledge_type,
        limit=limit
    )

    return Response({
        'success': True,
        'count': len(knowledge),
        'knowledge': knowledge
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def learn_knowledge(request, knowledge_id):
    """Agent learns knowledge from the knowledge base."""
    service = get_collaboration_service(request.user)
    data = request.data

    agent_name = data.get('agent_name')

    if not agent_name:
        return Response({
            'success': False,
            'error': 'agent_name is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    knowledge = service.learn_knowledge(agent_name, knowledge_id)

    if not knowledge:
        return Response({
            'success': False,
            'error': 'Knowledge not found'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'message': f'{agent_name} learned: {knowledge["title"]}',
        'knowledge': knowledge
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_knowledge(request, knowledge_id):
    """Rate the effectiveness of knowledge."""
    service = get_collaboration_service(request.user)
    data = request.data

    effectiveness = data.get('effectiveness')
    agent_name = data.get('agent_name')

    if effectiveness is None:
        return Response({
            'success': False,
            'error': 'effectiveness (0-100) is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    result = service.rate_knowledge_effectiveness(
        knowledge_id=knowledge_id,
        effectiveness=float(effectiveness),
        agent_name=agent_name
    )

    if not result:
        return Response({
            'success': False,
            'error': 'Knowledge not found'
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'success': True,
        'message': 'Effectiveness rating recorded'
    })


# =============================================================================
# PERFORMANCE ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agent_performance(request):
    """Get performance metrics for an agent."""
    service = get_collaboration_service(request.user)

    agent_name = request.query_params.get('agent')

    if not agent_name:
        return Response({
            'success': False,
            'error': 'agent query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    metrics = service.get_agent_performance(agent_name)

    if not metrics:
        return Response({
            'success': True,
            'metrics': None,
            'message': 'No metrics found for this agent yet'
        })

    return Response({
        'success': True,
        'metrics': {
            'agent_name': metrics.agent_name,
            'total_executions': metrics.total_executions,
            'successful_executions': metrics.successful_executions,
            'failed_executions': metrics.failed_executions,
            'total_collaborations': metrics.total_collaborations,
            'collaboration_success_rate': metrics.collaboration_success_rate,
            'avg_response_time_ms': metrics.avg_response_time_ms,
            'knowledge_contributions': metrics.knowledge_contributions,
            'knowledge_consumed': metrics.knowledge_consumed,
            'delegation_count': metrics.delegation_count,
            'consultation_count': metrics.consultation_count,
            'specialization_scores': metrics.specialization_scores,
            'last_active': metrics.last_active.isoformat() if metrics.last_active else None
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_top_performers(request):
    """Get top performing agents."""
    service = get_collaboration_service(request.user)

    domain = request.query_params.get('domain')
    limit = int(request.query_params.get('limit', 10))

    performers = service.get_top_performers(domain=domain, limit=limit)

    return Response({
        'success': True,
        'count': len(performers),
        'performers': performers
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_collaboration_stats(request):
    """Get overall collaboration statistics."""
    service = get_collaboration_service(request.user)

    stats = service.get_collaboration_stats()

    return Response({
        'success': True,
        'stats': stats
    })


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_collaborator(request):
    """Find the best collaborator for a task."""
    service = get_collaboration_service(request.user)

    task = request.query_params.get('task', '')
    capabilities = request.query_params.getlist('capabilities')
    domain = request.query_params.get('domain')
    exclude = request.query_params.getlist('exclude')

    if not task:
        return Response({
            'success': False,
            'error': 'task query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    best_agent = service.find_best_collaborator(
        task_description=task,
        required_capabilities=capabilities if capabilities else None,
        preferred_domain=domain,
        exclude_agents=exclude if exclude else None
    )

    return Response({
        'success': True,
        'best_collaborator': best_agent,
        'message': f'Recommended: {best_agent}' if best_agent else 'No suitable collaborator found'
    })


# =============================================================================
# DELEGATION HELPERS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delegate_task(request):
    """Delegate a task to another agent."""
    service = get_collaboration_service(request.user)
    data = request.data

    delegator = data.get('delegator')
    delegate_to = data.get('delegate_to')
    task = data.get('task', '')
    input_data = data.get('input_data', {})
    context = data.get('context', {})

    if not delegator or not delegate_to:
        return Response({
            'success': False,
            'error': 'delegator and delegate_to are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    collaboration_id = service.delegate_task(
        delegator=delegator,
        delegate_to=delegate_to,
        task=task,
        input_data=input_data,
        context=context
    )

    return Response({
        'success': True,
        'collaboration_id': collaboration_id,
        'message': f'Task delegated from {delegator} to {delegate_to}'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_consultation(request):
    """Request consultation from expert agents."""
    service = get_collaboration_service(request.user)
    data = request.data

    requester = data.get('requester')
    experts = data.get('experts', [])
    question = data.get('question', '')
    context_data = data.get('context_data', {})

    if not requester or not experts:
        return Response({
            'success': False,
            'error': 'requester and experts are required'
        }, status=status.HTTP_400_BAD_REQUEST)

    collaboration_id = service.request_consultation(
        requester=requester,
        experts=experts,
        question=question,
        context_data=context_data
    )

    return Response({
        'success': True,
        'collaboration_id': collaboration_id,
        'message': f'Consultation requested with {len(experts)} experts'
    })
