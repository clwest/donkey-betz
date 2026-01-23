"""
Agent Collaboration API Views

Session 794: REST API endpoints for the Production Agent Collaboration page.
Provides data for all 213 agents (74 core + 139 persona) + 25 advisors.
"""

import logging
from datetime import timedelta
from collections import Counter
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count, Avg

logger = logging.getLogger(__name__)


def get_agent_status(agent) -> str:
    """Determine agent's current status"""
    from core.models_unified_system import CollaborationSession

    # Check if agent is in any active collaboration
    active_count = CollaborationSession.objects.filter(
        status__in=['pending', 'active'],
        participating_agents__contains=[agent.name]
    ).count()

    if active_count > 0:
        return 'collaborating'

    # Check recent activity
    if agent.updated_at:
        if (timezone.now() - agent.updated_at).total_seconds() < 300:  # 5 minutes
            return 'active'

    return 'idle'


@require_http_methods(["GET"])
def agents_list(request):
    """Get all agents with their current status"""
    from core.models import Agent, Advisor
    from core.agent_router import AgentRouter

    include_persona = request.GET.get('include_persona', 'true').lower() == 'true'
    include_advisors = request.GET.get('include_advisors', 'true').lower() == 'true'

    agents = []
    router = AgentRouter()
    routable_names = set(router.AGENT_MAP.keys())

    # Get all agents from DB
    for agent in Agent.objects.filter(is_active=True):
        is_core = agent.name in routable_names

        if not include_persona and not is_core:
            continue

        agents.append({
            'id': str(agent.id),
            'name': agent.name,
            'type': 'core' if is_core else 'persona',
            'category': agent.agent_type or 'general',
            'description': agent.description or '',
            'status': get_agent_status(agent),
            'effectiveness_score': agent.effectiveness_score or 0,
            'last_active': agent.updated_at.isoformat() if agent.updated_at else None,
        })

    # Add advisors if requested
    if include_advisors:
        for advisor in Advisor.objects.filter(is_active=True):
            agents.append({
                'id': f'advisor_{advisor.id}',
                'name': advisor.name,
                'type': 'advisor',
                'category': advisor.category or 'advisor',
                'description': advisor.expertise or '',
                'status': 'available',
                'effectiveness_score': advisor.influence_score or 0,
                'last_active': advisor.updated_at.isoformat() if advisor.updated_at else None,
            })

    # Calculate counts
    counts = {
        'total': len(agents),
        'core': sum(1 for a in agents if a['type'] == 'core'),
        'persona': sum(1 for a in agents if a['type'] == 'persona'),
        'advisors': sum(1 for a in agents if a['type'] == 'advisor'),
    }

    return JsonResponse({
        'agents': agents,
        'counts': counts,
        'timestamp': timezone.now().isoformat()
    })


@require_http_methods(["GET"])
def active_collaborations(request):
    """Get all currently active collaborations"""
    from core.models_unified_system import CollaborationSession

    active = CollaborationSession.objects.filter(
        status__in=['pending', 'active']
    ).order_by('-started_at')[:50]

    collaborations = [{
        'id': str(c.id),
        'requester_agent': c.requester_agent,
        'collaboration_type': c.collaboration_type,
        'participating_agents': c.participating_agents or [],
        'status': c.status,
        'task_description': c.task_description[:200] if c.task_description else '',
        'started_at': c.started_at.isoformat(),
        'completed_at': c.completed_at.isoformat() if c.completed_at else None,
    } for c in active]

    return JsonResponse({
        'collaborations': collaborations,
        'count': len(collaborations),
        'timestamp': timezone.now().isoformat()
    })


@require_http_methods(["GET"])
def collaboration_stats(request):
    """Get collaboration statistics for the given time period"""
    from core.models_unified_system import CollaborationSession, InterAgentMessage

    hours = int(request.GET.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)

    # Collaboration stats
    collabs = CollaborationSession.objects.filter(started_at__gte=since)

    total = collabs.count()
    completed = collabs.filter(status='completed').count()
    failed = collabs.filter(status='failed').count()
    active = collabs.filter(status__in=['pending', 'active']).count()

    # Average quality score
    avg_quality = collabs.filter(
        status='completed',
        quality_score__isnull=False
    ).aggregate(avg=Avg('quality_score'))['avg'] or 0

    # By type breakdown
    by_type = dict(collabs.values('collaboration_type').annotate(
        count=Count('id')
    ).values_list('collaboration_type', 'count'))

    # Message stats
    messages = InterAgentMessage.objects.filter(created_at__gte=since)
    message_count = messages.count()

    # Most active agents
    agent_counts = Counter()
    for collab in collabs:
        if collab.participating_agents:
            for agent in collab.participating_agents:
                agent_counts[agent] += 1

    most_active = [{'name': name, 'count': count}
                   for name, count in agent_counts.most_common(10)]

    stats = {
        'total_collaborations': total,
        'completed': completed,
        'failed': failed,
        'active': active,
        'success_rate': round((completed / total * 100), 1) if total > 0 else 0,
        'average_quality_score': round(avg_quality, 1),
        'by_type': by_type,
        'total_messages': message_count,
        'most_active_agents': most_active,
    }

    return JsonResponse({
        'stats': stats,
        'period_hours': hours,
        'timestamp': timezone.now().isoformat()
    })


@require_http_methods(["GET"])
def recent_messages(request):
    """Get recent inter-agent messages"""
    from core.models_unified_system import InterAgentMessage

    limit = int(request.GET.get('limit', 50))
    messages = InterAgentMessage.objects.order_by('-created_at')[:limit]

    message_list = [{
        'id': str(m.id),
        'from_agent': m.sender_agent,
        'to_agent': m.receiver_agent,
        'message_type': m.message_type,
        'content_preview': str(m.content or '')[:200] if m.content else '',
        'priority': m.priority,
        'is_read': m.is_read,
        'created_at': m.created_at.isoformat(),
    } for m in messages]

    return JsonResponse({
        'messages': message_list,
        'count': len(message_list),
        'timestamp': timezone.now().isoformat()
    })


@require_http_methods(["GET"])
def collaboration_detail(request, collaboration_id):
    """Get detailed information about a specific collaboration"""
    from core.models_unified_system import CollaborationSession, InterAgentMessage

    try:
        collab = CollaborationSession.objects.get(id=collaboration_id)
    except CollaborationSession.DoesNotExist:
        return JsonResponse({'error': 'Collaboration not found'}, status=404)

    # Get messages for this collaboration
    messages = InterAgentMessage.objects.filter(
        correlation_id=collaboration_id
    ).order_by('created_at')

    detail = {
        'id': str(collab.id),
        'requester_agent': collab.requester_agent,
        'collaboration_type': collab.collaboration_type,
        'participating_agents': collab.participating_agents or [],
        'status': collab.status,
        'task_description': collab.task_description,
        'input_data': collab.input_data,
        'output_data': collab.output_data,
        'quality_score': collab.quality_score,
        'execution_time_ms': collab.execution_time_ms,
        'started_at': collab.started_at.isoformat(),
        'completed_at': collab.completed_at.isoformat() if collab.completed_at else None,
        'messages': [{
            'id': str(m.id),
            'from_agent': m.sender_agent,
            'to_agent': m.receiver_agent,
            'message_type': m.message_type,
            'content': m.content,
            'created_at': m.created_at.isoformat(),
        } for m in messages],
    }

    return JsonResponse({
        'collaboration': detail,
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
@require_http_methods(["POST"])
def initiate_collaboration(request):
    """Initiate a new collaboration (for testing)"""
    import json
    from core.models_unified_system import CollaborationSession

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    requester = data.get('requester_agent')
    collab_type = data.get('collaboration_type', 'consultation')
    task_desc = data.get('task_description', '')
    participants = data.get('participating_agents', [])

    if not requester or not task_desc:
        return JsonResponse({'error': 'requester_agent and task_description required'}, status=400)

    # Create collaboration session
    collab = CollaborationSession.objects.create(
        requester_agent=requester,
        collaboration_type=collab_type,
        task_description=task_desc,
        participating_agents=participants,
        status='pending',
        input_data={},
    )

    return JsonResponse({
        'collaboration': {
            'id': str(collab.id),
            'requester_agent': collab.requester_agent,
            'status': collab.status,
        },
        'message': 'Collaboration initiated',
        'timestamp': timezone.now().isoformat()
    }, status=201)
