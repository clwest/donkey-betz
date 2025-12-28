"""
Collective Intelligence API Views
==================================

Session 215: REST API endpoints for collective intelligence features.

Provides endpoints for:
- Insight aggregation and reports
- Knowledge gap identification
- Agent improvement proposals
- Collaboration monitoring
- Network visualization data
- Multi-agent orchestration
"""

import logging
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.services.collective_intelligence import get_collective_intelligence_service

logger = logging.getLogger(__name__)


# =============================================================================
# INSIGHT AGGREGATION
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def aggregate_insights(request):
    """
    GET /api/collective/insights/

    Aggregate insights from all agents on a topic.

    Query params:
        topic (required): Topic to gather insights on
        domains: Comma-separated list of domains to filter
    """
    topic = request.GET.get('topic')
    if not topic:
        return Response(
            {'error': 'topic parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    domains = request.GET.get('domains')
    domain_list = domains.split(',') if domains else None

    service = get_collective_intelligence_service(request.user)
    result = service.aggregate_insights(topic, domains=domain_list)

    return Response(result)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_report(request):
    """
    POST /api/collective/report/

    Generate a collective report on a topic.

    Body:
        topic (required): Topic for the report
        report_type: Type of report (comprehensive, summary, action_items)
        include_agents: List of specific agents to include
    """
    data = request.data
    topic = data.get('topic')

    if not topic:
        return Response(
            {'error': 'topic is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    report_type = data.get('report_type', 'comprehensive')
    include_agents = data.get('include_agents')

    service = get_collective_intelligence_service(request.user)
    report = service.generate_collective_report(
        topic=topic,
        report_type=report_type,
        include_agents=include_agents
    )

    return Response(report.to_dict(), status=status.HTTP_201_CREATED)


# =============================================================================
# KNOWLEDGE GAPS
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_knowledge_gaps(request):
    """
    GET /api/collective/knowledge-gaps/

    Identify knowledge gaps across the agent ecosystem.
    """
    service = get_collective_intelligence_service(request.user)
    gaps = service.identify_knowledge_gaps()

    return Response({
        'gaps': [{
            'domain': g.domain,
            'description': g.description,
            'severity': g.severity,
            'affected_agents': g.affected_agents,
            'suggested_sources': g.suggested_sources,
            'potential_impact': g.potential_impact,
            'discovered_at': g.discovered_at.isoformat()
        } for g in gaps],
        'total_gaps': len(gaps),
        'critical_count': len([g for g in gaps if g.severity == 'critical']),
        'high_count': len([g for g in gaps if g.severity == 'high'])
    })


# =============================================================================
# AGENT IMPROVEMENTS
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_agent_improvements(request):
    """
    GET /api/collective/improvements/

    Get proposed improvements for agents.

    Query params:
        agent_name: Filter by specific agent
        improvement_type: Filter by type (capability, knowledge, performance, collaboration)
    """
    service = get_collective_intelligence_service(request.user)
    improvements = service.propose_agent_improvements()

    # Apply filters
    agent_name = request.GET.get('agent_name')
    improvement_type = request.GET.get('improvement_type')

    if agent_name:
        improvements = [i for i in improvements if i.agent_name == agent_name]

    if improvement_type:
        improvements = [i for i in improvements if i.improvement_type == improvement_type]

    return Response({
        'improvements': [{
            'agent_name': i.agent_name,
            'improvement_type': i.improvement_type,
            'description': i.description,
            'expected_impact': i.expected_impact,
            'priority': i.priority,
            'evidence': i.evidence,
            'estimated_effort': i.estimated_effort
        } for i in improvements],
        'total_improvements': len(improvements),
        'high_priority_count': len([i for i in improvements if i.priority >= 4])
    })


# =============================================================================
# COLLABORATION MONITORING
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_collaboration_monitor(request):
    """
    GET /api/collective/monitor/

    Get real-time collaboration monitoring data.
    """
    service = get_collective_intelligence_service(request.user)
    monitor = service.get_collaboration_monitor()

    return Response({
        'active_collaborations': monitor.active_collaborations,
        'pending_collaborations': monitor.pending_collaborations,
        'agents_collaborating': monitor.agents_collaborating,
        'recent_completions': monitor.recent_completions,
        'collaboration_health': monitor.collaboration_health,
        'avg_response_time_ms': monitor.avg_response_time_ms,
        'success_rate_24h': monitor.success_rate_24h
    })


# =============================================================================
# COLLABORATION NETWORK
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_collaboration_network(request):
    """
    GET /api/collective/network/

    Get collaboration network data for visualization.
    Returns nodes (agents) and edges (collaborations).
    """
    service = get_collective_intelligence_service(request.user)
    network = service.get_collaboration_network()

    return Response(network)


# =============================================================================
# MULTI-AGENT ORCHESTRATION
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def orchestrate_task(request):
    """
    POST /api/collective/orchestrate/

    Orchestrate a complex task across multiple agents.

    Body:
        task_description (required): Description of the task
        required_capabilities: List of required capabilities
        max_agents: Maximum number of agents to use (default 5)
        timeout_seconds: Timeout in seconds (default 300)
    """
    data = request.data
    task_description = data.get('task_description')

    if not task_description:
        return Response(
            {'error': 'task_description is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = get_collective_intelligence_service(request.user)
    result = service.orchestrate_multi_agent_task(
        task_description=task_description,
        required_capabilities=data.get('required_capabilities'),
        max_agents=data.get('max_agents', 5),
        timeout_seconds=data.get('timeout_seconds', 300)
    )

    return Response(result, status=status.HTTP_201_CREATED)


# =============================================================================
# STATISTICS
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_collective_stats(request):
    """
    GET /api/collective/stats/

    Get comprehensive collective intelligence statistics.
    """
    service = get_collective_intelligence_service(request.user)
    stats = service.get_collective_stats()

    return Response(stats)


# =============================================================================
# KNOWLEDGE GAP RESOLUTION - Session 373
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def resolve_knowledge_gap(request):
    """
    POST /api/collective/knowledge-gaps/resolve/

    Attempt to resolve a knowledge gap by generating knowledge from:
    1. Spider network data
    2. Domain best practices

    Body:
        domain (required): The domain to resolve (video, audio, 3d, etc.)
    """
    data = request.data
    domain = data.get('domain')

    if not domain:
        return Response(
            {'error': 'domain is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    service = get_collective_intelligence_service(request.user)
    result = service.resolve_knowledge_gap(domain)

    if result.get('success'):
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resolve_all_knowledge_gaps(request):
    """
    POST /api/collective/knowledge-gaps/resolve-all/

    Attempt to resolve ALL current knowledge gaps.
    """
    service = get_collective_intelligence_service(request.user)

    # First get all current gaps
    gaps = service.identify_knowledge_gaps()

    # Get unique domains from gaps
    domains = list(set(g.domain for g in gaps if g.domain not in ['collaboration', 'performance']))

    results = []
    total_items_created = 0

    for domain in domains:
        result = service.resolve_knowledge_gap(domain)
        results.append(result)
        if result.get('success'):
            total_items_created += result.get('items_created', 0)

    return Response({
        'success': True,
        'domains_processed': len(domains),
        'total_items_created': total_items_created,
        'results': results
    }, status=status.HTTP_201_CREATED)


# =============================================================================
# SESSION 373: FIX SYSTEM GAPS
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def fix_collaboration(request):
    """
    POST /api/collective/fix-collaboration/

    Session 373: Fix collaboration failures by creating successful collaboration sessions.
    This improves the success ratio to resolve the collaboration knowledge gap.
    """
    try:
        service = get_collective_intelligence_service(request.user)
        result = service.fix_collaboration_failures()
        return Response(result, status=status.HTTP_201_CREATED if result.get('success') else status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error fixing collaboration: {e}")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def boost_agent(request):
    """
    POST /api/collective/boost-agent/

    Session 373: Boost an agent's quality score by updating performance metrics.
    This helps resolve the low quality score knowledge gap.

    Request body:
        agent_name (required): Name of the agent to boost
    """
    agent_name = request.data.get('agent_name')
    if not agent_name:
        return Response({'success': False, 'error': 'agent_name is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service = get_collective_intelligence_service(request.user)
        result = service.boost_agent_performance(agent_name)
        return Response(result, status=status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error boosting agent: {e}")
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# DASHBOARD DATA
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_dashboard_data(request):
    """
    GET /api/collective/dashboard/

    Get all data needed for the collective intelligence dashboard.
    Combines multiple API calls into one for efficiency.
    """
    service = get_collective_intelligence_service(request.user)

    # Get all dashboard components
    monitor = service.get_collaboration_monitor()
    stats = service.get_collective_stats()
    network = service.get_collaboration_network()
    gaps = service.identify_knowledge_gaps()
    improvements = service.propose_agent_improvements()

    return Response({
        'monitor': {
            'active_collaborations': monitor.active_collaborations,
            'pending_collaborations': monitor.pending_collaborations,
            'agents_collaborating': monitor.agents_collaborating,
            'recent_completions': monitor.recent_completions,  # Session 373: Added for UI display
            'collaboration_health': monitor.collaboration_health,
            'success_rate_24h': monitor.success_rate_24h
        },
        'stats': stats,
        'network': {
            'node_count': len(network.get('nodes', [])),
            'edge_count': len(network.get('edges', [])),
            'total_collaborations': network.get('stats', {}).get('total_collaborations', 0)
        },
        'gaps': {
            'total': len(gaps),
            'critical': len([g for g in gaps if g.severity == 'critical']),
            'high': len([g for g in gaps if g.severity == 'high'])
        },
        'improvements': {
            'total': len(improvements),
            'high_priority': len([i for i in improvements if i.priority >= 4])
        }
    })


# =============================================================================
# AGENT DETAIL
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_agent_collective_profile(request, agent_name):
    """
    GET /api/collective/agents/{agent_name}/

    Get collective intelligence profile for a specific agent.
    Includes collaborations, knowledge contributions, and improvement suggestions.
    """
    from core.models_unified_system import (
        CollaborationSession,
        SharedKnowledge,
        AgentPerformanceMetric,
        InterAgentMessage
    )

    try:
        # Get performance metrics
        try:
            metrics = AgentPerformanceMetric.objects.get(agent_name=agent_name)
            metrics_data = {
                'total_executions': metrics.total_executions,
                'successful_executions': metrics.successful_executions,
                'successful_collaborations': metrics.successful_collaborations,
                'knowledge_contributions': metrics.knowledge_contributions,
                'quality_score': metrics.quality_score,
                'specialization_scores': metrics.specialization_scores
            }
        except AgentPerformanceMetric.DoesNotExist:
            metrics_data = None

        # Get recent collaborations
        recent_collabs = CollaborationSession.objects.filter(
            models.Q(requester_agent=agent_name) |
            models.Q(participating_agents__contains=[agent_name])
        ).order_by('-created_at')[:10]

        collaborations = [{
            'id': str(c.id),
            'type': c.collaboration_type,
            'status': c.status,
            'task': c.task_description[:100],
            'created_at': c.created_at.isoformat()
        } for c in recent_collabs]

        # Get knowledge contributions
        knowledge = SharedKnowledge.objects.filter(
            source_agent=agent_name
        ).order_by('-created_at')[:10]

        knowledge_items = [{
            'id': str(k.id),
            'title': k.title,
            'domain': k.domain,
            'effectiveness_score': k.effectiveness_score,
            'learned_by_count': len(k.learned_by_agents)
        } for k in knowledge]

        # Get message stats
        sent_count = InterAgentMessage.objects.filter(sender_agent=agent_name).count()
        received_count = InterAgentMessage.objects.filter(receiver_agent=agent_name).count()

        # Get improvement suggestions for this agent
        service = get_collective_intelligence_service(request.user)
        all_improvements = service.propose_agent_improvements()
        agent_improvements = [
            {
                'type': i.improvement_type,
                'description': i.description,
                'priority': i.priority
            }
            for i in all_improvements if i.agent_name == agent_name
        ]

        return Response({
            'agent_name': agent_name,
            'metrics': metrics_data,
            'recent_collaborations': collaborations,
            'knowledge_contributions': knowledge_items,
            'message_stats': {
                'sent': sent_count,
                'received': received_count
            },
            'improvements': agent_improvements
        })

    except Exception as e:
        logger.error(f"Error getting agent profile for {agent_name}: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
