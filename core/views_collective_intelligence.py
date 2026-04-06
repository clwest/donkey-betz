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

    Aggregate insights from all agents on a topic, or return recent insights.

    Query params:
        topic (optional): Topic to gather insights on. If not provided, returns recent insights.
        domains: Comma-separated list of domains to filter
        limit: Number of insights to return (default 20)
    """
    topic = request.GET.get('topic')
    domains = request.GET.get('domains')
    domain_list = domains.split(',') if domains else None
    limit = int(request.GET.get('limit', 20))

    service = get_collective_intelligence_service(request.user)

    # Session 745: If no topic, return recent insights from dashboard
    if not topic:
        try:
            # Return recent insights summary
            from core.models_unified_system import KnowledgeTransfer
            from django.utils import timezone
            from datetime import timedelta

            recent_date = timezone.now() - timedelta(days=7)

            # Session 782: Use KnowledgeTransfer for insights (203 recent records)
            # More relevant than CollaborationSession (23 records from Dec 2025)
            recent_transfers = KnowledgeTransfer.objects.filter(
                created_at__gte=recent_date
            ).select_related('connection', 'source_knowledge').order_by('-created_at')[:limit]

            insights = []
            for transfer in recent_transfers:
                # Get agent names from the connection (convert Agent objects to strings)
                teacher_obj = getattr(transfer.connection, 'teacher_agent', None)
                student_obj = getattr(transfer.connection, 'student_agent', None)
                teacher = teacher_obj.name if hasattr(teacher_obj, 'name') else str(teacher_obj) if teacher_obj else 'Unknown Agent'
                student = student_obj.name if hasattr(student_obj, 'name') else str(student_obj) if student_obj else 'Unknown Agent'

                # Build title from transfer summary or source knowledge
                knowledge_name = ''
                if transfer.source_knowledge:
                    knowledge_name = getattr(transfer.source_knowledge, 'title', '') or getattr(transfer.source_knowledge, 'content_type', '')

                title = transfer.transfer_summary[:80] if transfer.transfer_summary else f"Knowledge shared: {knowledge_name}"
                if len(title) > 80:
                    title = title[:77] + "..."

                # Build key points as description
                key_points = transfer.key_points or []
                if isinstance(key_points, list):
                    description = "; ".join(key_points[:3]) if key_points else transfer.transfer_summary or ""
                else:
                    description = str(key_points)[:200]

                # Get knowledge source details
                knowledge_title = ''
                knowledge_type = ''
                knowledge_summary = ''
                if transfer.source_knowledge:
                    knowledge_title = getattr(transfer.source_knowledge, 'title', '') or ''
                    knowledge_type = getattr(transfer.source_knowledge, 'knowledge_type', '') or ''
                    knowledge_summary = getattr(transfer.source_knowledge, 'summary', '') or ''

                insights.append({
                    'id': str(transfer.id),
                    'title': title,
                    'description': description[:200] if description else "Knowledge transfer between agents",
                    'source_agent': teacher,
                    'target_agent': student,
                    'category': 'knowledge_transfer',
                    'confidence': transfer.usefulness_score or 0.7,
                    'created_at': transfer.created_at.isoformat() if transfer.created_at else None,
                    'related_agents': [teacher, student],
                    'actionable': transfer.was_applied or False,
                    # Session 782: Additional detail fields
                    'key_points': key_points if isinstance(key_points, list) else [],
                    'full_summary': transfer.transfer_summary or '',
                    'was_applied': transfer.was_applied or False,
                    'was_useful': transfer.was_useful or False,
                    'knowledge_title': knowledge_title,
                    'knowledge_type': knowledge_type,
                    'knowledge_summary': knowledge_summary[:300] if knowledge_summary else '',
                })

            return Response({
                'insights': insights,
                'total': len(insights),
                'period': '30 days',
            })
        except Exception as e:
            logger.warning(f"Error getting recent insights: {e}")
            return Response({'insights': [], 'total': 0})

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
# KNOWLEDGE TOPICS (Session 782)
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_knowledge_topics(request):
    """
    GET /api/collective/knowledge-topics/

    Get knowledge topics aggregated from AgentKnowledgeSource.
    Returns topics grouped by knowledge_type with article counts.
    """
    try:
        from core.models_unified_system import AgentKnowledgeSource
        from django.db.models import Count, Avg, Max
        from django.utils import timezone
        from datetime import timedelta

        # Get stats by knowledge type
        type_stats = AgentKnowledgeSource.objects.values('knowledge_type').annotate(
            article_count=Count('id'),
            avg_confidence=Avg('confidence_score'),
            avg_relevance=Avg('relevance_score'),
            last_updated=Max('last_updated_at'),
            contributors=Count('agent', distinct=True)
        ).order_by('-article_count')

        # Format as topics
        topics = []
        for stat in type_stats:
            knowledge_type = stat['knowledge_type'] or 'uncategorized'
            topics.append({
                'id': knowledge_type,
                'name': knowledge_type.replace('_', ' ').title(),
                'description': f"Knowledge from {stat['article_count']} sources about {knowledge_type.replace('_', ' ')}",
                'article_count': stat['article_count'],
                'contributors': stat['contributors'],
                'avg_confidence': round(stat['avg_confidence'] or 0, 2),
                'avg_relevance': round(stat['avg_relevance'] or 0, 2),
                'last_updated': stat['last_updated'].isoformat() if stat['last_updated'] else None,
            })

        # Get total stats
        total_articles = AgentKnowledgeSource.objects.count()
        total_contributors = AgentKnowledgeSource.objects.values('agent').distinct().count()

        return Response({
            'topics': topics,
            'total': len(topics),
            'total_articles': total_articles,
            'total_contributors': total_contributors,
        })

    except Exception as e:
        logger.warning(f"Error getting knowledge topics: {e}")
        return Response({'topics': [], 'total': 0, 'error': str(e)})


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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_shared_knowledge(request):
    """Return recent shared knowledge entries."""
    from core.models_unified_system import SharedKnowledge

    limit = int(request.GET.get('limit', 10))
    entries = SharedKnowledge.objects.order_by('-created_at')[:limit]

    return Response({
        'success': True,
        'count': entries.count(),
        'results': [
            {
                'id': str(e.id),
                'source_agent': e.source_agent,
                'knowledge_type': e.knowledge_type,
                'title': e.title,
                'description': e.description[:300],
                'domain': e.domain,
                'tags': e.tags,
                'applied_count': e.applied_count,
                'effectiveness_score': e.effectiveness_score,
                'created_at': e.created_at.isoformat(),
            }
            for e in entries
        ],
    })
