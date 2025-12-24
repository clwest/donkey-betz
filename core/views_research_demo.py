"""
Session 542: Research Demo API
Provides endpoints for the interactive D3.js visualization of the knowledge pipeline.

Endpoints:
- /api/v1/research/network-graph/ - Nodes and edges for D3 force graph
- /api/v1/research/live-feed/ - Recent learning events
- /api/v1/research/stats/ - Aggregate pipeline statistics
- /api/v1/research/mythology-gate/ - Quarantine data with trust decay
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q, F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)

# Category color mapping for D3.js visualization
CATEGORY_COLORS = {
    'creation': '#ec4899',      # Pink
    'editing': '#f472b6',       # Light pink
    'research': '#8b5cf6',      # Purple
    'strategy': '#06b6d4',      # Cyan
    'business': '#0ea5e9',      # Light blue
    'executive': '#f59e0b',     # Orange
    'development': '#22c55e',   # Green
    'content_studio': '#a855f7', # Violet
    'specialized': '#6366f1',   # Indigo
    'training': '#14b8a6',      # Teal
    'orchestration': '#ef4444', # Red
    'entry_point': '#fbbf24',   # Yellow
    'default': '#64748b'        # Gray
}

# Agent category mapping
AGENT_CATEGORIES = {
    'ImageAgent': 'creation',
    'VideoAgent': 'creation',
    'AudioAgent': 'creation',
    'ThreeDAgent': 'creation',
    'ImageEditingAgent': 'editing',
    'VideoEditingAgent': 'editing',
    'ResearchAgent': 'research',
    'TrendAnalysisAgent': 'research',
    'OpportunityScoringAgent': 'research',
    'ContentStrategyAgent': 'strategy',
    'BrandIdentityAgent': 'strategy',
    'SEOOptimizerAgent': 'strategy',
    'SocialMediaAgent': 'strategy',
    'CompetitorAnalysisAgent': 'business',
    'CustomerResearchAgent': 'business',
    'BrandStrategyAgent': 'business',
    'MarketingStrategyAgent': 'business',
    'BusinessContentStrategyAgent': 'business',
    'CTOAgent': 'executive',
    'COOAgent': 'executive',
    'CreativeDirectorAgent': 'executive',
    'MeetingCoordinatorAgent': 'executive',
    'CodeGeneratorAgent': 'development',
    'FullStackDeveloperAgent': 'development',
    'CodeReviewAgent': 'development',
    'DevOpsAgent': 'development',
    'AutonomousContentStudioCoordinator': 'content_studio',
    'TopicMinerAgent': 'content_studio',
    'ContrarianAgent': 'content_studio',
    'PerformanceAnalystAgent': 'content_studio',
    'LegalDocDrafterAgent': 'specialized',
    'ResolveAgent': 'specialized',
    'PodcastCoordinatorAgent': 'specialized',
    'CharacterTrainingAgent': 'training',
    'TrainedCreationAgent': 'training',
    'WorkflowAgent': 'orchestration',
    'CampaignOrchestratorAgent': 'orchestration',
    'PersonalAssistantAgent': 'entry_point',
}


def get_agent_category(agent_name):
    """Get category for an agent by name."""
    return AGENT_CATEGORIES.get(agent_name, 'default')


def get_category_color(category):
    """Get color for a category."""
    return CATEGORY_COLORS.get(category, CATEGORY_COLORS['default'])


@api_view(['GET'])
@permission_classes([AllowAny])
def network_graph_api(request):
    """
    Returns nodes and edges for D3.js force-directed graph.

    Response:
    {
        "success": true,
        "nodes": [{"id", "name", "category", "color", "knowledge_count", "mythology_blocks"}],
        "edges": [{"source", "target", "strength", "learning_type", "total_transfers", "mythology_blocks"}],
        "stats": {"total_agents", "total_connections", "total_transfers", "avg_strength"}
    }
    """
    try:
        from core.models_unified_system import Agent, AgentLearningConnection, AgentKnowledgeSource

        # Get all active agents
        agents = Agent.objects.filter(is_active=True)

        # Get knowledge counts per agent
        knowledge_counts = dict(
            AgentKnowledgeSource.objects.filter(is_active=True)
            .values('agent_id')
            .annotate(count=Count('id'))
            .values_list('agent_id', 'count')
        )

        # Get mythology blocks per agent (sum of blocks from connections where agent is teacher)
        mythology_blocks_by_agent = dict(
            AgentLearningConnection.objects.filter(is_active=True)
            .values('teacher_agent_id')
            .annotate(total_blocks=Sum('mythology_blocks'))
            .values_list('teacher_agent_id', 'total_blocks')
        )

        # Build nodes
        nodes = []
        agent_ids = set()
        for agent in agents:
            category = get_agent_category(agent.name)
            nodes.append({
                'id': str(agent.id),
                'name': agent.name,
                'category': category,
                'color': get_category_color(category),
                'knowledge_count': knowledge_counts.get(agent.id, 0),
                'mythology_blocks': mythology_blocks_by_agent.get(agent.id, 0) or 0,
                'effectiveness_score': agent.effectiveness_score if hasattr(agent, 'effectiveness_score') else 0,
                'is_active': agent.is_active,
            })
            agent_ids.add(agent.id)

        # Get all active learning connections
        connections = AgentLearningConnection.objects.filter(
            is_active=True,
            teacher_agent__is_active=True,
            student_agent__is_active=True
        ).select_related('teacher_agent', 'student_agent')

        # Build edges
        edges = []
        total_transfers = 0
        total_mythology_blocks = 0
        strengths = []

        for conn in connections:
            if conn.teacher_agent_id in agent_ids and conn.student_agent_id in agent_ids:
                edges.append({
                    'id': str(conn.id),
                    'source': str(conn.teacher_agent_id),
                    'target': str(conn.student_agent_id),
                    'strength': float(conn.strength),
                    'learning_type': conn.learning_type,
                    'total_transfers': conn.total_transfers,
                    'successful_transfers': conn.successful_transfers,
                    'mythology_blocks': conn.mythology_blocks,
                    'last_transfer_at': conn.last_transfer_at.isoformat() if conn.last_transfer_at else None,
                })
                total_transfers += conn.total_transfers
                total_mythology_blocks += conn.mythology_blocks
                strengths.append(conn.strength)

        # Calculate stats
        avg_strength = sum(strengths) / len(strengths) if strengths else 0

        return Response({
            'success': True,
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'total_agents': len(nodes),
                'total_connections': len(edges),
                'total_transfers': total_transfers,
                'total_mythology_blocks': total_mythology_blocks,
                'avg_strength': round(avg_strength, 3),
            }
        })

    except Exception as e:
        logger.error(f"Error in network_graph_api: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def live_feed_api(request):
    """
    Returns recent learning events for the live feed.

    Query params:
    - limit (default: 50)
    - hours (default: 24)
    - include_blocks (default: true)
    """
    try:
        from core.models_unified_system import KnowledgeTransfer, MythologyQuarantine

        limit = int(request.GET.get('limit', 50))
        hours = int(request.GET.get('hours', 24))
        include_blocks = request.GET.get('include_blocks', 'true').lower() == 'true'

        cutoff = timezone.now() - timedelta(hours=hours)
        events = []

        # Get recent knowledge transfers
        transfers = KnowledgeTransfer.objects.filter(
            created_at__gte=cutoff
        ).select_related(
            'connection__teacher_agent',
            'connection__student_agent',
            'source_knowledge'
        ).order_by('-created_at')[:limit]

        for transfer in transfers:
            events.append({
                'id': str(transfer.id),
                'timestamp': transfer.created_at.isoformat(),
                'event_type': 'knowledge_transfer',
                'teacher': {
                    'id': str(transfer.connection.teacher_agent_id),
                    'name': transfer.connection.teacher_agent.name,
                },
                'student': {
                    'id': str(transfer.connection.student_agent_id),
                    'name': transfer.connection.student_agent.name,
                },
                'title': transfer.source_knowledge.title if transfer.source_knowledge else transfer.transfer_summary[:100],
                'summary': transfer.transfer_summary[:200] if transfer.transfer_summary else '',
                'usefulness_score': float(transfer.usefulness_score) if transfer.usefulness_score else 0,
                'was_applied': transfer.was_applied,
            })

        # Get mythology blocks if requested
        if include_blocks:
            blocks = MythologyQuarantine.objects.filter(
                created_at__gte=cutoff
            ).select_related(
                'teacher_agent',
                'student_agent'
            ).order_by('-created_at')[:limit]

            for block in blocks:
                events.append({
                    'id': str(block.id),
                    'timestamp': block.created_at.isoformat(),
                    'event_type': 'mythology_block',
                    'teacher': {
                        'id': str(block.teacher_agent_id),
                        'name': block.teacher_agent.name,
                    },
                    'student': {
                        'id': str(block.student_agent_id),
                        'name': block.student_agent.name,
                    },
                    'title': block.blocked_title[:100],
                    'summary': block.blocked_summary[:200] if block.blocked_summary else '',
                    'violation_type': block.violation_type,
                    'status': block.status,
                })

        # Sort by timestamp descending
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        events = events[:limit]

        # Calculate stats
        transfers_count = len([e for e in events if e['event_type'] == 'knowledge_transfer'])
        blocks_count = len([e for e in events if e['event_type'] == 'mythology_block'])

        return Response({
            'success': True,
            'events': events,
            'stats': {
                'total_events': len(events),
                'transfers': transfers_count,
                'blocks': blocks_count,
                'hours_covered': hours,
            }
        })

    except Exception as e:
        logger.error(f"Error in live_feed_api: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def stats_api(request):
    """
    Returns aggregate pipeline statistics for the overview.

    Shows: Spiders -> Agents -> Learning Network -> Mythology Gate -> Outcomes
    """
    try:
        from core.models_unified_system import (
            Agent, AgentLearningConnection, AgentKnowledgeSource,
            KnowledgeTransfer, MythologyQuarantine, SpiderData
        )
        from ai_core.spiders.spider_registry import spider_registry

        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        # Spider stats
        spider_count = len(spider_registry.get_all_spiders()) if hasattr(spider_registry, 'get_all_spiders') else 72
        spider_data_24h = SpiderData.objects.filter(created_at__gte=last_24h).count()

        # Agent stats
        total_agents = Agent.objects.filter(is_active=True).count()
        agents_with_knowledge = AgentKnowledgeSource.objects.filter(
            is_active=True
        ).values('agent_id').distinct().count()

        # Learning network stats
        total_connections = AgentLearningConnection.objects.filter(is_active=True).count()
        total_transfers = KnowledgeTransfer.objects.count()
        transfers_24h = KnowledgeTransfer.objects.filter(created_at__gte=last_24h).count()
        avg_strength = AgentLearningConnection.objects.filter(
            is_active=True
        ).aggregate(avg=Avg('strength'))['avg'] or 0

        # Mythology gate stats
        quarantine_total = MythologyQuarantine.objects.count()
        quarantine_pending = MythologyQuarantine.objects.filter(status='pending').count()
        quarantine_approved = MythologyQuarantine.objects.filter(status='approved').count()
        quarantine_rejected = MythologyQuarantine.objects.filter(status='rejected').count()

        # Trust decay stats
        connections_with_blocks = AgentLearningConnection.objects.filter(
            mythology_blocks__gt=0
        ).count()
        total_blocks = AgentLearningConnection.objects.aggregate(
            total=Sum('mythology_blocks')
        )['total'] or 0

        # Outcomes stats
        total_knowledge = AgentKnowledgeSource.objects.filter(is_active=True).count()
        knowledge_24h = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=last_24h
        ).count()
        avg_confidence = AgentKnowledgeSource.objects.filter(
            is_active=True
        ).aggregate(avg=Avg('confidence_score'))['avg'] or 0

        # === NEW: Detailed Analytics ===

        # Transfers per hour (last 24h)
        last_1h = now - timedelta(hours=1)
        transfers_1h = KnowledgeTransfer.objects.filter(created_at__gte=last_1h).count()
        transfers_per_hour = round(transfers_24h / 24, 1) if transfers_24h else 0

        # Top knowledge topics (most shared across agents)
        top_topics = list(
            AgentKnowledgeSource.objects.filter(is_active=True)
            .values('title')
            .annotate(agent_count=Count('agent_id', distinct=True))
            .order_by('-agent_count')[:5]
        )

        # Most knowledgeable agents
        top_knowledgeable = list(
            AgentKnowledgeSource.objects.filter(is_active=True, agent__is_active=True)
            .values('agent__name')
            .annotate(knowledge_count=Count('id'))
            .order_by('-knowledge_count')[:5]
        )

        # Top teachers (most outgoing transfers)
        top_teachers = list(
            KnowledgeTransfer.objects.filter(created_at__gte=last_24h)
            .values('connection__teacher_agent__name')
            .annotate(transfer_count=Count('id'))
            .order_by('-transfer_count')[:5]
        )

        # Top students (most incoming transfers)
        top_students = list(
            KnowledgeTransfer.objects.filter(created_at__gte=last_24h)
            .values('connection__student_agent__name')
            .annotate(transfer_count=Count('id'))
            .order_by('-transfer_count')[:5]
        )

        # Most active connections
        top_connections = list(
            AgentLearningConnection.objects.filter(is_active=True)
            .select_related('teacher_agent', 'student_agent')
            .order_by('-total_transfers')[:5]
            .values('teacher_agent__name', 'student_agent__name', 'total_transfers', 'strength')
        )

        return Response({
            'success': True,
            'pipeline': {
                'spiders': {
                    'total': spider_count,
                    'data_points_24h': spider_data_24h,
                    'label': 'Spiders',
                    'icon': '🕷️',
                },
                'agents': {
                    'total': total_agents,
                    'with_knowledge': agents_with_knowledge,
                    'label': 'Agents',
                    'icon': '🤖',
                },
                'network': {
                    'connections': total_connections,
                    'total_transfers': total_transfers,
                    'transfers_24h': transfers_24h,
                    'avg_strength': round(avg_strength, 2),
                    'label': 'Learning Network',
                    'icon': '🔗',
                },
                'mythology_gate': {
                    'quarantined': quarantine_total,
                    'pending': quarantine_pending,
                    'approved': quarantine_approved,
                    'rejected': quarantine_rejected,
                    'connections_with_blocks': connections_with_blocks,
                    'total_blocks': total_blocks,
                    'label': 'Mythology Gate',
                    'icon': '🛡️',
                },
                'outcomes': {
                    'total_knowledge': total_knowledge,
                    'new_24h': knowledge_24h,
                    'avg_confidence': round(avg_confidence, 2),
                    'label': 'Knowledge',
                    'icon': '📚',
                }
            },
            'summary': {
                'spiders_feeding': spider_count,
                'agents_learning': total_agents,
                'knowledge_flowing': total_transfers,
                'myths_blocked': quarantine_total,
            },
            'analytics': {
                'transfers_per_hour': transfers_per_hour,
                'transfers_last_hour': transfers_1h,
                'top_topics': top_topics,
                'top_knowledgeable': top_knowledgeable,
                'top_teachers': top_teachers,
                'top_students': top_students,
                'top_connections': top_connections,
            }
        })

    except Exception as e:
        logger.error(f"Error in stats_api: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def mythology_gate_api(request):
    """
    Returns mythology quarantine data with trust decay information.
    """
    try:
        from core.models_unified_system import MythologyQuarantine, AgentLearningConnection

        limit = int(request.GET.get('limit', 20))
        status_filter = request.GET.get('status', None)

        # Get quarantine items
        queryset = MythologyQuarantine.objects.select_related(
            'teacher_agent',
            'student_agent',
            'connection'
        ).order_by('-created_at')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        items = []
        for q in queryset[:limit]:
            items.append({
                'id': str(q.id),
                'teacher': {
                    'id': str(q.teacher_agent_id),
                    'name': q.teacher_agent.name,
                },
                'student': {
                    'id': str(q.student_agent_id),
                    'name': q.student_agent.name,
                },
                'blocked_title': q.blocked_title,
                'blocked_summary': q.blocked_summary[:300] if q.blocked_summary else '',
                'violation_type': q.violation_type,
                'violation_count': q.violation_count,
                'spider_sources': q.spider_sources,
                'status': q.status,
                'created_at': q.created_at.isoformat(),
                'reviewed_at': q.reviewed_at.isoformat() if q.reviewed_at else None,
                'reviewed_by': q.reviewed_by,
                'connection_strength': float(q.connection.strength) if q.connection else None,
                'connection_blocks': q.connection.mythology_blocks if q.connection else 0,
            })

        # Get trust decay leaderboard (connections with most blocks)
        decay_leaderboard = AgentLearningConnection.objects.filter(
            mythology_blocks__gt=0,
            is_active=True
        ).select_related(
            'teacher_agent',
            'student_agent'
        ).order_by('-mythology_blocks')[:10]

        leaderboard = []
        for conn in decay_leaderboard:
            leaderboard.append({
                'teacher': conn.teacher_agent.name,
                'student': conn.student_agent.name,
                'mythology_blocks': conn.mythology_blocks,
                'strength': float(conn.strength),
                'trust_lost': round((1 - conn.strength) * 100, 1),  # Percentage lost
            })

        # Stats by violation type
        by_type = dict(
            MythologyQuarantine.objects.values('violation_type')
            .annotate(count=Count('id'))
            .values_list('violation_type', 'count')
        )

        # Stats by status
        by_status = dict(
            MythologyQuarantine.objects.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        return Response({
            'success': True,
            'quarantine': items,
            'trust_decay_leaderboard': leaderboard,
            'stats': {
                'total': MythologyQuarantine.objects.count(),
                'by_type': by_type,
                'by_status': by_status,
            }
        })

    except Exception as e:
        logger.error(f"Error in mythology_gate_api: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)
