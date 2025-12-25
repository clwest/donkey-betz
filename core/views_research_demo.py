"""
Research Demo API - Session 550

Provides data for the Research Demo tab with D3.js network visualization
showing the knowledge pipeline: Spiders -> Agents -> Learning Network -> Mythology Gate -> Outcomes
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models
from datetime import timedelta

logger = logging.getLogger(__name__)

# Category colors for D3.js visualization
CATEGORY_COLORS = {
    'creation': '#ec4899',      # Pink
    'editing': '#f472b6',       # Light pink
    'research': '#8b5cf6',      # Purple
    'strategy': '#06b6d4',      # Cyan
    'business': '#14b8a6',      # Teal
    'executive': '#f59e0b',     # Amber
    'development': '#22c55e',   # Green
    'content_studio': '#a855f7', # Violet
    'specialized': '#6366f1',   # Indigo
    'training': '#ef4444',      # Red
    'orchestration': '#3b82f6', # Blue
    'entry_point': '#fbbf24',   # Yellow
    'default': '#64748b',       # Slate
}


@require_http_methods(["GET"])
def network_graph_api(request):
    """
    Returns nodes (agents) and edges (connections) for D3.js force-directed graph.
    """
    from core.models_unified_system import Agent, AgentLearningConnection, KnowledgeTransfer

    try:
        # Get all active agents as nodes
        agents = Agent.objects.filter(is_active=True)

        # Build nodes list
        nodes = []
        agent_ids = set()
        for agent in agents:
            category = agent.category or 'default'
            color = CATEGORY_COLORS.get(category, CATEGORY_COLORS['default'])

            # Count knowledge for this agent
            knowledge_count = KnowledgeTransfer.objects.filter(
                recipient_agent=agent
            ).count()

            # Count mythology blocks
            mythology_blocks = AgentLearningConnection.objects.filter(
                student_agent=agent,
                mythology_blocks__gt=0
            ).aggregate(total=models.Sum('mythology_blocks'))['total'] or 0

            nodes.append({
                'id': str(agent.id),
                'name': agent.name,
                'category': category,
                'color': color,
                'effectiveness': float(agent.effectiveness_score or 0),
                'knowledge_count': knowledge_count,
                'mythology_blocks': mythology_blocks,
                'total_executions': agent.total_executions or 0,
                'is_recently_active': agent.last_active and agent.last_active > timezone.now() - timedelta(hours=24),
            })
            agent_ids.add(str(agent.id))

        # Get all active learning connections as edges
        connections = AgentLearningConnection.objects.filter(is_active=True)

        edges = []
        for conn in connections:
            teacher_id = str(conn.teacher_agent_id)
            student_id = str(conn.student_agent_id)

            if teacher_id in agent_ids and student_id in agent_ids:
                edges.append({
                    'source': teacher_id,
                    'target': student_id,
                    'strength': float(conn.strength or 0.5),
                    'learning_type': conn.learning_type,
                    'total_transfers': conn.total_transfers or 0,
                    'mythology_blocks': conn.mythology_blocks or 0,
                    'has_recent_transfer': conn.last_transfer_at and conn.last_transfer_at > timezone.now() - timedelta(hours=24),
                })

        # Aggregate stats
        stats = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'total_transfers': KnowledgeTransfer.objects.count(),
            'active_connections': connections.filter(total_transfers__gt=0).count(),
            'mythology_blocked': connections.filter(mythology_blocks__gt=0).count(),
        }

        return JsonResponse({
            'success': True,
            'nodes': nodes,
            'edges': edges,
            'stats': stats,
        })

    except Exception as e:
        logger.error(f"Network graph API error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def live_feed_api(request):
    """
    Returns recent learning events for the live feed sub-tab.
    """
    from core.models_unified_system import KnowledgeTransfer, AgentConversation, AgentDream

    try:
        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 50))
        since = timezone.now() - timedelta(hours=hours)

        events = []

        # Recent knowledge transfers
        transfers = KnowledgeTransfer.objects.filter(
            created_at__gte=since
        ).select_related('source_agent', 'recipient_agent').order_by('-created_at')[:limit]

        for t in transfers:
            events.append({
                'type': 'transfer',
                'icon': 'book',
                'timestamp': t.created_at.isoformat(),
                'title': f"Knowledge Transfer",
                'description': f"{t.source_agent.name if t.source_agent else 'System'} taught {t.recipient_agent.name if t.recipient_agent else 'Unknown'}",
                'details': t.knowledge_title[:100] if t.knowledge_title else 'Untitled',
                'quality_score': float(t.quality_score or 0),
            })

        # Recent agent conversations
        conversations = AgentConversation.objects.filter(
            started_at__gte=since
        ).order_by('-started_at')[:limit//2]

        for c in conversations:
            events.append({
                'type': 'conversation',
                'icon': 'chat',
                'timestamp': c.started_at.isoformat(),
                'title': f"Agent Conversation",
                'description': c.topic[:80] if c.topic else 'General discussion',
                'details': f"{c.message_count or 0} messages",
                'quality_score': float(c.quality_rating or 0),
            })

        # Recent agent dreams
        dreams = AgentDream.objects.filter(
            dreamed_at__gte=since
        ).select_related('agent').order_by('-dreamed_at')[:limit//3]

        for d in dreams:
            events.append({
                'type': 'dream',
                'icon': 'sparkles',
                'timestamp': d.dreamed_at.isoformat(),
                'title': f"Agent Dream",
                'description': f"{d.agent.name if d.agent else 'Unknown'} dreamed",
                'details': d.dream_title[:80] if d.dream_title else 'Untitled dream',
                'quality_score': float(d.creativity_score or 0),
            })

        # Sort all events by timestamp
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        events = events[:limit]

        return JsonResponse({
            'success': True,
            'events': events,
            'total': len(events),
            'since': since.isoformat(),
        })

    except Exception as e:
        logger.error(f"Live feed API error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def stats_api(request):
    """
    Returns aggregate pipeline statistics for the overview sub-tab.
    """
    from core.models_unified_system import Agent, AgentLearningConnection, KnowledgeTransfer
    from core.models_unified_system import AgentConversation, AgentDream
    from ai_core.models import SpiderData

    try:
        now = timezone.now()
        today = now - timedelta(hours=24)

        # Spider stats
        total_spiders = 75
        spider_data_24h = SpiderData.objects.filter(created_at__gte=today).count()
        total_spider_data = SpiderData.objects.count()

        # Agent stats
        total_agents = Agent.objects.filter(is_active=True).count()
        active_agents_24h = Agent.objects.filter(last_active__gte=today).count()

        # Learning network stats
        total_connections = AgentLearningConnection.objects.filter(is_active=True).count()
        active_connections = AgentLearningConnection.objects.filter(
            is_active=True,
            last_transfer_at__gte=today
        ).count()

        # Transfer stats
        total_transfers = KnowledgeTransfer.objects.count()
        transfers_24h = KnowledgeTransfer.objects.filter(created_at__gte=today).count()

        # Mythology gate stats
        mythology_blocks_total = AgentLearningConnection.objects.aggregate(
            total=models.Sum('mythology_blocks')
        )['total'] or 0

        # Quality metrics
        avg_transfer_quality = KnowledgeTransfer.objects.aggregate(
            avg=models.Avg('quality_score')
        )['avg'] or 0

        # Conversation & dream stats
        conversations_24h = AgentConversation.objects.filter(started_at__gte=today).count()
        dreams_24h = AgentDream.objects.filter(dreamed_at__gte=today).count()

        return JsonResponse({
            'success': True,
            'pipeline': {
                'spiders': {
                    'total': total_spiders,
                    'data_24h': spider_data_24h,
                    'total_data': total_spider_data,
                },
                'agents': {
                    'total': total_agents,
                    'active_24h': active_agents_24h,
                },
                'network': {
                    'connections': total_connections,
                    'active_24h': active_connections,
                    'total_transfers': total_transfers,
                    'transfers_24h': transfers_24h,
                },
                'mythology_gate': {
                    'total_blocks': mythology_blocks_total,
                },
                'quality': {
                    'avg_transfer_quality': round(float(avg_transfer_quality), 2),
                },
                'activity': {
                    'conversations_24h': conversations_24h,
                    'dreams_24h': dreams_24h,
                },
            },
            'timestamp': now.isoformat(),
        })

    except Exception as e:
        logger.error(f"Stats API error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def mythology_gate_api(request):
    """
    Returns mythology gate data: quarantine queue, trust decay, blocked transfers.
    """
    from core.models_unified_system import AgentLearningConnection

    try:
        # Get connections with mythology blocks
        blocked_connections = AgentLearningConnection.objects.filter(
            mythology_blocks__gt=0
        ).select_related('teacher_agent', 'student_agent').order_by('-mythology_blocks')[:20]

        blocked_list = []
        for conn in blocked_connections:
            blocked_list.append({
                'id': str(conn.id),
                'teacher': conn.teacher_agent.name if conn.teacher_agent else 'Unknown',
                'student': conn.student_agent.name if conn.student_agent else 'Unknown',
                'blocks': conn.mythology_blocks,
                'last_block': conn.last_mythology_block_at.isoformat() if conn.last_mythology_block_at else None,
                'strength': float(conn.strength or 0),
                'total_transfers': conn.total_transfers or 0,
            })

        # Trust decay leaderboard
        trust_decay = AgentLearningConnection.objects.filter(
            is_active=True,
            strength__lt=0.5,
            total_transfers__gt=5,
        ).select_related('teacher_agent', 'student_agent').order_by('strength')[:10]

        decay_list = []
        for conn in trust_decay:
            decay_list.append({
                'id': str(conn.id),
                'teacher': conn.teacher_agent.name if conn.teacher_agent else 'Unknown',
                'student': conn.student_agent.name if conn.student_agent else 'Unknown',
                'strength': float(conn.strength or 0),
                'mythology_blocks': conn.mythology_blocks or 0,
            })

        stats = {
            'total_blocks': AgentLearningConnection.objects.aggregate(
                total=models.Sum('mythology_blocks')
            )['total'] or 0,
            'connections_with_blocks': AgentLearningConnection.objects.filter(
                mythology_blocks__gt=0
            ).count(),
            'low_trust_connections': AgentLearningConnection.objects.filter(
                strength__lt=0.5
            ).count(),
        }

        return JsonResponse({
            'success': True,
            'blocked': blocked_list,
            'trust_decay': decay_list,
            'stats': stats,
        })

    except Exception as e:
        logger.error(f"Mythology gate API error: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
