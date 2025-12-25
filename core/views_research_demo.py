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
            # Session 552: Convert category to string (may be AgentCategory object)
            category = str(agent.category) if agent.category else 'default'
            color = CATEGORY_COLORS.get(category, CATEGORY_COLORS['default'])

            # Count knowledge for this agent (Session 552: Fixed field name)
            knowledge_count = KnowledgeTransfer.objects.filter(
                connection__student_agent=agent
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
        # Session 552: Fixed select_related - use connection.teacher_agent/student_agent
        transfers = KnowledgeTransfer.objects.filter(
            created_at__gte=since
        ).select_related(
            'connection__teacher_agent',
            'connection__student_agent',
            'source_knowledge'
        ).order_by('-created_at')[:limit]

        for t in transfers:
            teacher_name = t.connection.teacher_agent.name if t.connection and t.connection.teacher_agent else 'System'
            student_name = t.connection.student_agent.name if t.connection and t.connection.student_agent else 'Unknown'
            # Get title from source_knowledge or transfer_summary
            title = ''
            if t.source_knowledge and t.source_knowledge.title:
                title = t.source_knowledge.title[:100]
            elif t.transfer_summary:
                title = t.transfer_summary[:100]
            else:
                title = 'Knowledge transfer'

            events.append({
                'type': 'transfer',
                'icon': 'book',
                'timestamp': t.created_at.isoformat(),
                'title': f"Knowledge Transfer",
                'description': f"{teacher_name} taught {student_name}",
                'details': title,
                'quality_score': float(t.usefulness_score or 0),
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
                'quality_score': float(c.quality_score or 0),  # Session 552: Fixed field name
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
                'details': d.title[:80] if d.title else 'Untitled dream',  # Session 552: Fixed field name
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
    Session 552: Added analytics section with fixed top_topics query.
    """
    from core.models_unified_system import (
        Agent, AgentLearningConnection, KnowledgeTransfer,
        AgentConversation, AgentDream, SpiderData, AgentKnowledgeSource,
        MythologyQuarantine
    )
    from django.db.models import Count, Avg, Sum
    from ai_core.spiders.spider_registry import spider_registry

    try:
        now = timezone.now()
        today = now - timedelta(hours=24)
        last_1h = now - timedelta(hours=1)

        # Spider stats
        spider_count = len(spider_registry.get_all_spiders()) if hasattr(spider_registry, 'get_all_spiders') else 75
        spider_data_24h = SpiderData.objects.filter(created_at__gte=today).count()

        # Agent stats
        total_agents = Agent.objects.filter(is_active=True).count()
        agents_with_knowledge = AgentKnowledgeSource.objects.filter(
            is_active=True
        ).values('agent_id').distinct().count()

        # Learning network stats
        total_connections = AgentLearningConnection.objects.filter(is_active=True).count()
        total_transfers = KnowledgeTransfer.objects.count()
        transfers_24h = KnowledgeTransfer.objects.filter(created_at__gte=today).count()
        avg_strength = AgentLearningConnection.objects.filter(
            is_active=True
        ).aggregate(avg=Avg('strength'))['avg'] or 0

        # Mythology gate stats
        quarantine_total = MythologyQuarantine.objects.count()
        quarantine_pending = MythologyQuarantine.objects.filter(status='pending').count()
        connections_with_blocks = AgentLearningConnection.objects.filter(
            mythology_blocks__gt=0
        ).count()
        total_blocks = AgentLearningConnection.objects.aggregate(
            total=Sum('mythology_blocks')
        )['total'] or 0

        # Outcomes stats
        total_knowledge = AgentKnowledgeSource.objects.filter(is_active=True).count()
        knowledge_24h = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=today
        ).count()
        avg_confidence = AgentKnowledgeSource.objects.filter(
            is_active=True
        ).aggregate(avg=Avg('confidence_score'))['avg'] or 0

        # === Analytics Section (Session 552) ===

        # Transfers per hour
        transfers_1h = KnowledgeTransfer.objects.filter(created_at__gte=last_1h).count()
        transfers_per_hour = round(transfers_24h / 24, 1) if transfers_24h else 0

        # Session 552: Top topics - filter out garbage (short titles, single words)
        # Minimum 10 characters to filter out words like "each", "content", "this"
        top_topics_raw = list(
            AgentKnowledgeSource.objects.filter(is_active=True)
            .exclude(title='')
            .exclude(title__isnull=True)
            .values('title')
            .annotate(agent_count=Count('agent_id', distinct=True))
            .order_by('-agent_count')[:50]  # Get more to filter
        )

        # Filter and clean titles
        top_topics = []
        for item in top_topics_raw:
            title = item['title']

            # Strip "[Learned]" prefix if present
            if title.startswith('[Learned] '):
                title = title[10:]
            elif title.startswith('[Learned]'):
                title = title[9:]

            # Session 552: Skip titles that are too short (garbage data)
            # Minimum 10 chars filters out "each", "content", "this", "ai", etc.
            if not title or len(title) < 10:
                continue

            # Skip if it looks like a single word (no spaces, no hyphens)
            if ' ' not in title and '-' not in title and len(title) < 20:
                continue

            top_topics.append({
                'title': title[:80],  # Truncate for display
                'agent_count': item['agent_count']
            })

            if len(top_topics) >= 5:
                break

        # Most knowledgeable agents
        top_knowledgeable = list(
            AgentKnowledgeSource.objects.filter(is_active=True, agent__is_active=True)
            .values('agent__name')
            .annotate(knowledge_count=Count('id'))
            .order_by('-knowledge_count')[:5]
        )

        # Top teachers (most outgoing transfers in 24h)
        top_teachers = list(
            KnowledgeTransfer.objects.filter(created_at__gte=today)
            .values('connection__teacher_agent__name')
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

        return JsonResponse({
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
                    'avg_strength': round(float(avg_strength), 2),
                    'label': 'Learning Network',
                    'icon': '🔗',
                },
                'mythology_gate': {
                    'quarantined': quarantine_total,
                    'pending': quarantine_pending,
                    'connections_with_blocks': connections_with_blocks,
                    'total_blocks': total_blocks,
                    'label': 'Mythology Gate',
                    'icon': '🛡️',
                },
                'outcomes': {
                    'total_knowledge': total_knowledge,
                    'new_24h': knowledge_24h,
                    'avg_confidence': round(float(avg_confidence), 2),
                    'label': 'Knowledge',
                    'icon': '📚',
                },
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
                'top_connections': top_connections,
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


@require_http_methods(["GET"])
def self_blog_api(request):
    """
    Session 552: Stub API for self-blog feature.
    Returns empty data to prevent frontend errors.
    TODO: Implement full self-blog generation in future session.
    """
    return JsonResponse({
        'success': True,
        'posts': [],
        'total': 0,
        'message': 'Self-blog feature coming soon'
    })
