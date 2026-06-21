"""
Research Demo API - Session 550

Provides data for the Research Demo tab with D3.js network visualization
showing the knowledge pipeline: Spiders -> Agents -> Learning Network -> Mythology Gate -> Outcomes
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
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


def infer_category_from_name(name: str) -> str:
    """
    Session 552: Infer agent category from name since category field may be NULL.
    """
    name_lower = name.lower()

    # Creation agents
    if any(x in name_lower for x in ['image', 'video', 'audio', '3d', 'threed']):
        return 'creation'

    # Editing agents
    if 'editing' in name_lower:
        return 'editing'

    # Research agents
    if any(x in name_lower for x in ['research', 'trend', 'opportunity', 'scoring']):
        return 'research'

    # Strategy agents
    if any(x in name_lower for x in ['strategy', 'brand', 'seo', 'social']):
        return 'strategy'

    # Business agents
    if any(x in name_lower for x in ['competitor', 'customer', 'marketing', 'business']):
        return 'business'

    # Executive agents
    if any(x in name_lower for x in ['cto', 'coo', 'director', 'meeting', 'coordinator']):
        return 'executive'

    # Development agents
    if any(x in name_lower for x in ['code', 'developer', 'fullstack', 'devops', 'review']):
        return 'development'

    # Content Studio agents
    if any(x in name_lower for x in ['content', 'topic', 'contrarian', 'performance', 'autonomous']):
        return 'content_studio'

    # Specialized agents
    if any(x in name_lower for x in ['legal', 'resolve', 'podcast', 'series', 'workflow']):
        return 'specialized'

    # Training agents
    if any(x in name_lower for x in ['training', 'trained', 'character']):
        return 'training'

    # Orchestration agents
    if any(x in name_lower for x in ['orchestrat', 'campaign', 'workflow']):
        return 'orchestration'

    # Entry point agents
    if any(x in name_lower for x in ['personal', 'assistant']):
        return 'entry_point'

    return 'default'


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
            # Session 552: Infer category from name since category field may be NULL
            if agent.category:
                category = str(agent.category)
            else:
                category = infer_category_from_name(agent.name)
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
                'is_active': agent.is_active,  # Session 564: Add is_active for Agent Details card
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
            # Session 564: Use content as fallback when title is empty
            dream_title = d.title.strip() if d.title else ''
            if not dream_title and d.content:
                # Extract first sentence or first 60 chars as title
                content_preview = d.content.strip()[:80]
                if '. ' in content_preview:
                    dream_title = content_preview.split('. ')[0]
                elif ': ' in content_preview:
                    dream_title = content_preview.split(': ')[0]
                else:
                    dream_title = content_preview[:60] + '...'
            dream_title = dream_title or 'Untitled dream'

            events.append({
                'type': 'dream',
                'icon': 'sparkles',
                'timestamp': d.dreamed_at.isoformat(),
                'title': f"Agent Dream",
                'description': f"{d.agent.name if d.agent else 'Unknown'} dreamed",
                'details': dream_title[:80],
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
        SpiderData, AgentKnowledgeSource, MythologyQuarantine
    )
    from django.db.models import Count, Avg, Sum
    from ai_core.spiders.spider_registry import spider_registry

    try:
        now = timezone.now()
        today = now - timedelta(hours=24)
        last_1h = now - timedelta(hours=1)

        # Spider stats
        spider_count = len(spider_registry.list_spiders()) if hasattr(spider_registry, 'list_spiders') else 77
        spider_data_24h = SpiderData.objects.filter(created_at__gte=today).count()

        # Agent stats (show all agents, not just active)
        total_agents = Agent.objects.count()
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
    Session 543: Get the latest self-blog written by the system about itself.
    Session 552: Restored from Session 543 (was accidentally replaced with stub).
    """
    try:
        from core.models_unified_system import SelfBlog

        # Get latest blog
        latest = SelfBlog.objects.first()

        # Get list of all blogs
        all_blogs = list(
            SelfBlog.objects.values('id', 'title', 'tone', 'word_count', 'created_at')[:10]
        )

        if latest:
            return JsonResponse({
                'success': True,
                'has_blog': True,
                'latest': {
                    'id': str(latest.id),
                    'title': latest.title,
                    'meta_description': latest.meta_description,
                    'intro': latest.intro,
                    'sections': latest.sections,
                    'conclusion': latest.conclusion,
                    'tags': latest.tags,
                    'full_text': latest.full_text,
                    'tone': latest.tone,
                    'word_count': latest.word_count,
                    'stats_snapshot': latest.stats_snapshot,
                    'created_at': latest.created_at.isoformat(),
                },
                'all_blogs': [
                    {
                        'id': str(b['id']),
                        'title': b['title'],
                        'tone': b['tone'],
                        'word_count': b['word_count'],
                        'created_at': b['created_at'].isoformat(),
                    }
                    for b in all_blogs
                ],
            })
        else:
            return JsonResponse({
                'success': True,
                'has_blog': False,
                'message': 'No self-blogs generated yet. Run: python manage.py write_self_blog',
                'all_blogs': [],
            })

    except Exception as e:
        logger.error(f"Error in self_blog_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def self_blog_list_api(request):
    """
    Session 780: Get paginated list of all self-blog posts.
    Session 814: Added category filtering for technical documents/audits.
    Session 833: Added status filtering for approval workflow.
    Supports pagination, search, category, and status filtering.
    """
    try:
        from core.models_unified_system import SelfBlog

        # Pagination params
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()  # Session 814
        status = request.GET.get('status', '').strip()  # Session 833

        # Build query
        queryset = SelfBlog.objects.all().order_by('-created_at')

        # Workspace scoping: show workspace content + unlinked content
        workspace_id = request.GET.get('workspace', '').strip()
        if workspace_id:
            queryset = queryset.filter(
                models.Q(workspace_id=workspace_id) | models.Q(workspace__isnull=True)
            )

        # Session 814: Filter by category if specified
        if category:
            if category == 'documents':
                # Show all non-blog categories (technical docs, audits, etc.)
                queryset = queryset.exclude(category='blog')
            else:
                queryset = queryset.filter(category=category)

        # Session 833: Filter by status if specified
        if status:
            queryset = queryset.filter(status=status)

        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(intro__icontains=search) |
                models.Q(tags__icontains=search)
            )

        total = queryset.count()

        # Session 814: Get category counts for UI tabs
        category_counts = {
            'all': SelfBlog.objects.count(),
            'blog': SelfBlog.objects.filter(category='blog').count(),
            'documents': SelfBlog.objects.exclude(category='blog').count(),
        }

        # Session 833: Get status counts for UI tabs
        status_counts = {
            'all': SelfBlog.objects.count(),
            'draft': SelfBlog.objects.filter(status='draft').count(),
            'approved': SelfBlog.objects.filter(status='approved').count(),
            'published': SelfBlog.objects.filter(status='published').count(),
        }

        # Paginate
        start = (page - 1) * per_page
        end = start + per_page
        blogs = queryset[start:end]

        # Session 865: Get needs_enhancement count for UI
        needs_enhancement_count = SelfBlog.objects.filter(
            publish_ready=False,
            quality_score__isnull=False,
            quality_score__gte=0.5  # Has been evaluated, decent quality
        ).exclude(
            title__istartswith='[Research]'
        ).exclude(
            title__istartswith='[Stage'
        ).exclude(
            title__istartswith='[Report]'
        ).count()

        return JsonResponse({
            'success': True,
            'blogs': [
                {
                    'id': str(b.id),
                    'title': b.title,
                    'category': getattr(b, 'category', 'blog'),  # Session 814
                    'status': getattr(b, 'status', 'draft'),  # Session 833
                    'meta_description': b.meta_description,
                    'intro': b.intro[:200] + '...' if len(b.intro) > 200 else b.intro,
                    'tags': b.tags or [],
                    'tone': b.tone,
                    'word_count': b.word_count,
                    'created_at': b.created_at.isoformat(),
                    # Session 865: PublishGate scores for enhancement UI
                    'quality_score': b.quality_score,
                    'novelty_score': b.novelty_score,
                    'structure_score': b.structure_score,
                    'publish_ready': b.publish_ready,
                    'gate_notes': b.gate_notes[:100] if b.gate_notes else None,
                }
                for b in blogs
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page,
                'has_next': end < total,
                'has_prev': page > 1,
            },
            'category_counts': category_counts,  # Session 814
            'status_counts': status_counts,  # Session 833
            'needs_enhancement_count': needs_enhancement_count,  # Session 865
        })

    except Exception as e:
        logger.error(f"Error in self_blog_list_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def self_blog_by_id_api(request, blog_id):
    """
    Session 570: Get a specific self-blog by ID.
    Session 833: Added status field for approval workflow.
    """
    try:
        from core.models_unified_system import SelfBlog

        blog = SelfBlog.objects.filter(id=blog_id).first()

        if blog:
            return JsonResponse({
                'success': True,
                'blog': {
                    'id': str(blog.id),
                    'title': blog.title,
                    'category': getattr(blog, 'category', 'blog'),  # Session 814
                    'status': getattr(blog, 'status', 'draft'),  # Session 833
                    'meta_description': blog.meta_description,
                    'intro': blog.intro,
                    'sections': blog.sections,
                    'conclusion': blog.conclusion,
                    'tags': blog.tags,
                    'full_text': blog.full_text,
                    'tone': blog.tone,
                    'word_count': blog.word_count,
                    'stats_snapshot': blog.stats_snapshot,
                    'created_at': blog.created_at.isoformat(),
                },
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Blog not found'
            }, status=404)

    except Exception as e:
        logger.error(f"Error in self_blog_by_id_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def related_self_blogs_api(request, blog_id):
    """
    Session 971: Find blogs related to a given blog.
    Uses 3 signals: same initiative, tag overlap (Jaccard), title keyword overlap.
    """
    try:
        from core.models_unified_system import SelfBlog
        from django.db.models import Q

        limit = int(request.GET.get('limit', 6))
        source = SelfBlog.objects.filter(id=blog_id).first()
        if not source:
            return JsonResponse({'success': False, 'error': 'Blog not found'}, status=404)

        # Stop words for title matching
        STOP_WORDS = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'it', 'its', 'are', 'was', 'were',
            'be', 'been', 'has', 'had', 'have', 'how', 'what', 'when', 'where',
            'who', 'why', 'this', 'that', 'these', 'those', 'not', 'can', 'will',
            'just', 'more', 'also', 'than', 'into', 'over', 'such', 'our', 'your',
        }

        import re

        def title_keywords(title):
            words = re.findall(r'[a-z]+', (title or '').lower())
            return {w for w in words if len(w) >= 4 and w not in STOP_WORDS}

        scored = {}  # blog_id -> (score, reason, blog)

        # Signal 1: Same initiative (score 1.0)
        if source.initiative_id:
            siblings = SelfBlog.objects.filter(
                initiative_id=source.initiative_id
            ).exclude(id=blog_id).select_related()[:20]
            for b in siblings:
                scored[b.id] = (1.0, 'same_initiative', b)

        # Signal 2: Tag overlap - Jaccard > 0.3 (score = jaccard * 0.8)
        source_tags = set(source.tags or [])
        if source_tags:
            tag_q = Q()
            for tag in source_tags:
                tag_q |= Q(tags__contains=[tag])
            tag_candidates = SelfBlog.objects.filter(
                tag_q
            ).exclude(id=blog_id).exclude(id__in=scored.keys())[:50]
            for b in tag_candidates:
                b_tags = set(b.tags or [])
                if b_tags:
                    intersection = source_tags & b_tags
                    union = source_tags | b_tags
                    jaccard = len(intersection) / len(union) if union else 0
                    if jaccard > 0.3:
                        scored[b.id] = (jaccard * 0.8, 'tag_overlap', b)

        # Signal 3: Title keyword overlap (score = ratio * 0.5)
        src_keywords = title_keywords(source.title)
        if src_keywords:
            kw_q = Q()
            for kw in list(src_keywords)[:5]:
                kw_q |= Q(title__icontains=kw)
            title_candidates = SelfBlog.objects.filter(
                kw_q
            ).exclude(id=blog_id).exclude(id__in=scored.keys())[:50]
            for b in title_candidates:
                b_keywords = title_keywords(b.title)
                if b_keywords:
                    shared = src_keywords & b_keywords
                    total = src_keywords | b_keywords
                    ratio = len(shared) / len(total) if total else 0
                    if ratio > 0.15:
                        scored[b.id] = (ratio * 0.5, 'title_keywords', b)

        # Sort by score descending, take top N
        top = sorted(scored.values(), key=lambda x: x[0], reverse=True)[:limit]

        related = []
        for score, reason, b in top:
            related.append({
                'id': str(b.id),
                'title': b.title,
                'category': getattr(b, 'category', 'blog'),
                'status': getattr(b, 'status', 'draft'),
                'intro': (b.intro or '')[:200],
                'tags': b.tags or [],
                'word_count': b.word_count or 0,
                'created_at': b.created_at.isoformat(),
                'quality_score': b.quality_score,
                'relatedness_score': round(score, 3),
                'relatedness_reason': reason,
            })

        return JsonResponse({
            'success': True,
            'blog_id': str(blog_id),
            'blog_title': source.title,
            'related': related,
            'count': len(related),
        })

    except Exception as e:
        logger.error(f"Error in related_self_blogs_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
def delete_self_blog_api(request, blog_id):
    """
    Session 814: Delete a self-blog by ID.
    Allows cleanup of empty or unwanted blog posts.
    """
    try:
        from core.models_unified_system import SelfBlog

        blog = SelfBlog.objects.filter(id=blog_id).first()

        if blog:
            title = blog.title
            blog.delete()
            logger.info(f"Deleted self-blog: {title} (ID: {blog_id})")
            return JsonResponse({
                'success': True,
                'message': f'Blog "{title}" deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Blog not found'
            }, status=404)

    except Exception as e:
        logger.error(f"Error in delete_self_blog_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def approve_self_blog_api(request, blog_id):
    """
    Session 833: Approve a self-blog for publishing.
    Changes status from 'draft' to 'approved'.
    """
    try:
        from core.models_unified_system import SelfBlog

        blog = SelfBlog.objects.filter(id=blog_id).first()

        if blog:
            if blog.status == 'published':
                return JsonResponse({
                    'success': False,
                    'error': 'Blog is already published'
                }, status=400)

            blog.status = 'approved'
            blog.save()

            logger.info(f"Approved self-blog: {blog.title} (ID: {blog_id})")
            return JsonResponse({
                'success': True,
                'message': f'Blog "{blog.title}" approved',
                'blog': {
                    'id': str(blog.id),
                    'title': blog.title,
                    'status': blog.status,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Blog not found'
            }, status=404)

    except Exception as e:
        logger.error(f"Error in approve_self_blog_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def publish_self_blog_api(request, blog_id):
    """
    Session 833: Publish an approved self-blog.
    Changes status from 'approved' to 'published'.
    Can also directly publish a draft if force=true.
    """
    try:
        import json
        from core.models_unified_system import SelfBlog

        body = json.loads(request.body) if request.body else {}
        force = body.get('force', False)

        blog = SelfBlog.objects.filter(id=blog_id).first()

        if blog:
            if blog.status == 'published':
                return JsonResponse({
                    'success': False,
                    'error': 'Blog is already published'
                }, status=400)

            # Session 998: PublishGate enforcement — block publishing unless gate passed
            if not force and not blog.publish_ready:
                return JsonResponse({
                    'success': False,
                    'error': 'Blog has not passed PublishGate quality checks. Use force=true to override.',
                    'gate_notes': blog.gate_notes or 'Not yet evaluated',
                }, status=400)

            if blog.status == 'draft' and not force:
                return JsonResponse({
                    'success': False,
                    'error': 'Blog must be approved before publishing. Use force=true to skip approval.'
                }, status=400)

            blog.status = 'published'
            blog.save()

            logger.info(f"Published self-blog: {blog.title} (ID: {blog_id})")
            return JsonResponse({
                'success': True,
                'message': f'Blog "{blog.title}" published',
                'blog': {
                    'id': str(blog.id),
                    'title': blog.title,
                    'status': blog.status,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Blog not found'
            }, status=404)

    except Exception as e:
        logger.error(f"Error in publish_self_blog_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def enhance_self_blog_api(request, blog_id):
    """
    Session 865: Trigger EditorAgent enhancement for a blog.
    Uses the enhance_blog_task Celery task to improve structure,
    hooks, headers, and conclusion.
    """
    try:
        import json
        from core.models_unified_system import SelfBlog
        from core.tasks import enhance_blog_task

        body = json.loads(request.body) if request.body else {}
        focus_areas = body.get('focus_areas', None)  # Optional: ['structure', 'hooks', 'conclusion']
        save = body.get('save', True)  # Default to saving the changes

        blog = SelfBlog.objects.filter(id=blog_id).first()

        if not blog:
            return JsonResponse({
                'success': False,
                'error': 'Blog not found'
            }, status=404)

        # Trigger the enhancement task asynchronously
        task = enhance_blog_task.delay(
            blog_id=str(blog_id),
            focus_areas=focus_areas,
            save=save
        )

        logger.info(f"Triggered enhancement for blog: {blog.title} (ID: {blog_id}), task_id: {task.id}")
        return JsonResponse({
            'success': True,
            'message': f'Enhancement started for "{blog.title}"',
            'task_id': task.id,
            'blog': {
                'id': str(blog.id),
                'title': blog.title,
            }
        })

    except Exception as e:
        logger.error(f"Error in enhance_self_blog_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def generate_self_blog_api(request):
    """
    Session 643: Trigger self-blog generation via Celery task.

    POST body:
    {
        "tone": "enthusiastic",  # optional, default "enthusiastic"
        "word_count": 1500,      # optional, default 1500
        "topic_category": null   # optional
    }

    Returns:
    {
        "success": true,
        "task_id": "uuid-string"
    }
    """
    try:
        import json
        from core.tasks import generate_self_blog_task

        # Parse request body
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        tone = data.get('tone', 'enthusiastic')
        word_count = data.get('word_count', 1500)
        topic_category = data.get('topic_category')

        # Queue the Celery task
        task = generate_self_blog_task.delay(
            tone=tone,
            word_count=word_count,
            topic_category=topic_category
        )

        logger.info(f"Self-blog generation task queued: {task.id}")

        return JsonResponse({
            'success': True,
            'task_id': str(task.id),
            'message': 'Self-blog generation started'
        })

    except Exception as e:
        logger.error(f"Error triggering self-blog generation: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def generate_v2_blog_api(request):
    """
    Phase 4: Trigger v2 blog generation via deliberation pipeline.

    POST body: same as generate_self_blog_api
    Returns: {success, task_id, message}
    """
    try:
        import json
        from core.tasks import generate_self_blog_deliberation_task

        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}

        tone = data.get('tone', 'enthusiastic')
        word_count = data.get('word_count', 1500)
        topic_category = data.get('topic_category')

        task = generate_self_blog_deliberation_task.delay(
            tone=tone,
            word_count=word_count,
            topic_category=topic_category,
        )

        logger.info(f"[Phase 4] Deliberation blog task queued: {task.id}")

        return JsonResponse({
            'success': True,
            'task_id': str(task.id),
            'message': 'Deliberation blog generation started',
        })

    except Exception as e:
        logger.error(f"[Phase 4] Error triggering deliberation blog: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@require_http_methods(["GET"])
def self_blog_task_status_api(request, task_id):
    """
    Session 643: Check the status of a self-blog generation task.

    Returns:
    {
        "success": true,
        "status": "pending|started|completed|failed",
        "title": "...",  # if completed
        "blog_id": "...", # if completed
        "error": "..."   # if failed
    }
    """
    try:
        from celery.result import AsyncResult
        from core.celery import app

        result = AsyncResult(task_id, app=app)

        response = {
            'success': True,
            'task_id': task_id,
            'status': result.status.lower() if result.status else 'pending'
        }

        if result.successful():
            # Task completed successfully
            task_result = result.result or {}
            if isinstance(task_result, dict):
                response['status'] = 'completed'
                response['blog_id'] = task_result.get('blog_id')
                response['title'] = task_result.get('title', 'Self-Blog Generated')
            else:
                response['status'] = 'completed'
                response['title'] = 'Self-Blog Generated'
        elif result.failed():
            response['status'] = 'failed'
            response['error'] = str(result.result) if result.result else 'Unknown error'
        elif result.status == 'PENDING':
            response['status'] = 'pending'
        elif result.status == 'STARTED':
            response['status'] = 'started'

        return JsonResponse(response)

    except Exception as e:
        logger.error(f"Error checking self-blog task status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def system_insights_api(request):
    """
    Session 588: Get System Insights reports - AI-generated analysis of system state.
    These are auto-generated reports from the ThinkingAgent, distinct from regular self-blogs.
    """
    try:
        from core.models_unified_system import SelfBlog

        # Get all System Insights (auto_generated = True in stats_snapshot)
        # Session 590: Order by created_at descending so latest is first
        all_blogs = SelfBlog.objects.order_by('-created_at')

        # Filter for System Insights
        system_insights = []
        for blog in all_blogs:
            if blog.stats_snapshot and blog.stats_snapshot.get('auto_generated'):
                system_insights.append({
                    'id': str(blog.id),
                    'title': blog.title,
                    'meta_description': blog.meta_description,
                    'intro': blog.intro,
                    'sections': blog.sections,
                    'conclusion': blog.conclusion,
                    'tags': blog.tags,
                    'full_text': blog.full_text,
                    'tone': blog.tone,
                    'word_count': blog.word_count,
                    'stats_snapshot': blog.stats_snapshot,
                    'created_at': blog.created_at.isoformat(),
                })

        if system_insights:
            return JsonResponse({
                'success': True,
                'has_insights': True,
                'count': len(system_insights),
                'latest': system_insights[0],
                'all_insights': system_insights[:20],  # Limit to 20 most recent
            })
        else:
            return JsonResponse({
                'success': True,
                'has_insights': False,
                'count': 0,
                'message': 'No System Insights generated yet. These are created by the ThinkingAgent.',
                'all_insights': [],
            })

    except Exception as e:
        logger.error(f"Error in system_insights_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def deliverables_api(request):
    """
    Session 622: Get synthesized deliverables from the research pipeline.
    These are documents created by TechnicalDocumentAgent after ResearchAgent completes research.
    Session 622.2: Updated to support both legacy [Deliverable] and new [Stage X - ...] formats.
    """
    try:
        from django.db.models import Q
        from core.models_unified_system import SelfBlog
        import re

        # Get all deliverables - both legacy and new stage-based formats
        deliverables = SelfBlog.objects.filter(
            Q(title__startswith='[Deliverable]') |
            Q(title__startswith='[Stage 1 -') |
            Q(title__startswith='[Stage 2 -') |
            Q(title__startswith='[Stage 3 -') |
            Q(title__startswith='[Stage 4 -') |
            Q(title__startswith='[Stage 5 -')
        ).order_by('-created_at')

        deliverables_list = []
        for d in deliverables[:50]:  # Limit to 50 most recent
            # Extract parent topic and stage info from stats_snapshot if available
            parent_topic = None
            doc_type = None
            stage = None
            stage_name = None
            if d.stats_snapshot:
                parent_topic = d.stats_snapshot.get('parent_topic')
                doc_type = d.stats_snapshot.get('doc_type')
                stage = d.stats_snapshot.get('stage')
                stage_name = d.stats_snapshot.get('stage_name')

            # Clean title for display - handle both formats
            display_title = d.title
            display_title = re.sub(r'^\[Deliverable\]\s*', '', display_title)
            display_title = re.sub(r'^\[Stage \d+ - [^\]]+\]\s*', '', display_title)

            deliverables_list.append({
                'id': str(d.id),
                'title': display_title,
                'full_title': d.title,
                'intro': d.intro,
                'full_text': d.full_text,
                'tone': d.tone,
                'word_count': len(d.full_text) if d.full_text else 0,
                'parent_topic': parent_topic,
                'doc_type': doc_type,
                'stage': stage,
                'stage_name': stage_name,
                'created_at': d.created_at.isoformat(),
            })

        if deliverables_list:
            return JsonResponse({
                'success': True,
                'has_deliverables': True,
                'count': len(deliverables_list),
                'total_in_db': deliverables.count(),
                'latest': deliverables_list[0],
                'all_deliverables': deliverables_list,
            })
        else:
            return JsonResponse({
                'success': True,
                'has_deliverables': False,
                'count': 0,
                'message': 'No deliverables yet. These are created when ThinkingAgent requests research with deliverables.',
                'all_deliverables': [],
            })

    except Exception as e:
        logger.error(f"Error in deliverables_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def initiatives_api(request):
    """
    Session 622: Get all initiatives with their stage status.
    Session 848: Added health calculation.
    Session 897: PERFORMANCE FIX - prefetch_related to eliminate N+1 queries.
    Session 901: Added priority sorting, program/purpose filtering, portfolio grouping.
    Provides a single source of truth for document lifecycle tracking.
    """
    try:
        from core.models_document_registry import Initiative, InitiativeStage, STAGE_NAMES
        from django.utils import timezone
        from django.db.models import Prefetch, F, Value, FloatField
        from django.db.models.functions import Coalesce

        # Session 884: Support limit and status filter query params
        # Session 897: Reduced default from 200 to 50 for performance
        # Session 902: Increased to 500 - frontend does tab filtering, needs all initiatives
        limit = int(request.GET.get('limit', 500))
        status_filter = request.GET.get('status')  # Optional: ACTIVE, COMPLETED, etc.
        # Session 901: New filters
        program_filter = request.GET.get('program')  # Optional: growth_intelligence, etc.
        purpose_filter = request.GET.get('purpose')  # Optional: revenue, stability, etc.
        workspace_filter = request.GET.get('workspace')  # Filter by target_workspace FK
        sort_by = request.GET.get('sort', 'priority')  # 'priority' (default) or 'updated'

        # Session 897: Use prefetch_related to batch load stages and decisions
        # This reduces ~3000 queries to just 3 queries total
        initiatives = Initiative.objects.all().prefetch_related(
            Prefetch('stages', queryset=InitiativeStage.objects.all()),
            Prefetch('source_decisions'),
        )

        # Workspace filter — scope to project when specified
        if workspace_filter:
            initiatives = initiatives.filter(target_workspace_id=workspace_filter)

        if status_filter:
            initiatives = initiatives.filter(status=status_filter)
        if program_filter:
            initiatives = initiatives.filter(program=program_filter)
        if purpose_filter:
            initiatives = initiatives.filter(purpose=purpose_filter)

        # Session 901: Sort by priority score (computed) or updated_at
        if sort_by == 'priority':
            # Annotate with computed priority score for database sorting
            # priority = impact_score * 0.4 + urgency * 0.2 + confidence * 0.2 + revenue_potential * 0.2
            initiatives = initiatives.annotate(
                computed_priority=Coalesce(F('impact_score'), Value(0.5)) * 0.4 +
                                  Coalesce(F('urgency'), Value(0.5)) * 0.2 +
                                  Coalesce(F('confidence'), Value(0.5)) * 0.2 +
                                  Coalesce(F('revenue_potential'), Value(0.0)) * 0.2
            ).order_by('-computed_priority', '-updated_at')
        else:
            initiatives = initiatives.order_by('-updated_at')

        # Get total count before slicing (uses cached queryset)
        total_count = initiatives.count()

        now = timezone.now()
        initiatives_list = []

        # Session 897: Status weights for completion calculation
        status_weights = {
            'APPROVED': 1.0,
            'IN_REVIEW': 0.8,
            'DRAFT': 0.6,
            'PENDING': 0.0,
            'REJECTED': 0.0,
            'SUPERSEDED': 0.0,
        }

        for init in initiatives[:limit]:
            # Session 897: Use prefetched stages (no extra queries)
            prefetched_stages = list(init.stages.all())
            stages_by_num = {s.stage: s for s in prefetched_stages}

            # Build stage status from prefetched data
            stages = {}
            for i in range(1, 6):
                stage_doc = stages_by_num.get(i)
                if stage_doc:
                    stages[i] = {
                        'status': stage_doc.status,
                        'stage_name': stage_doc.stage_name,
                        'document_id': str(stage_doc.document_id) if stage_doc.document_id else None,
                        'approved_at': stage_doc.approved_at.isoformat() if stage_doc.approved_at else None,
                    }
                else:
                    stages[i] = {
                        'status': 'NOT_STARTED',
                        'stage_name': STAGE_NAMES.get(i, 'Unknown'),
                        'document_id': None,
                        'approved_at': None,
                    }

            # Session 897: Calculate metrics from prefetched stages (no extra queries)
            total_weight = sum(status_weights.get(s.status, 0.0) for s in prefetched_stages)
            completion_percentage = int((total_weight / 5.0) * 100)
            approved_count = sum(1 for s in prefetched_stages if s.status == 'APPROVED')
            approved_percentage = int((approved_count / 5) * 100)
            stages_with_work = sum(1 for s in prefetched_stages if s.status != 'PENDING')

            # Session 897: Calculate health from prefetched data (no extra queries)
            days_since_update = (now - init.updated_at).days
            health = 'healthy'
            health_issues = []

            if days_since_update > 14:
                health = 'stale'
                health_issues.append(f'No updates for {days_since_update} days')

            rejected_count = sum(1 for s in prefetched_stages if s.status == 'REJECTED')
            if rejected_count > 0:
                health = 'blocked'
                health_issues.append(f'{rejected_count} stage(s) rejected')

            current_stage = stages_by_num.get(init.current_stage)
            if current_stage and not current_stage.document_id:
                stage_age = (now - current_stage.created_at).days
                if stage_age > 7:
                    health = 'blocked'
                    health_issues.append(f'Stage {init.current_stage} needs document')

            # Session 897: Use prefetched source_decisions (no extra queries)
            source_decisions = []
            for decision in list(init.source_decisions.all())[:5]:
                source_decisions.append({
                    'id': str(decision.id),
                    'topic': decision.topic,
                    'artifact_type': decision.artifact_type,
                    'suggested_feature': decision.suggested_feature[:200] if decision.suggested_feature else '',
                    'conversation_id': str(decision.conversation_id) if decision.conversation_id else None,
                    'hive_session_id': str(decision.hive_session_id) if decision.hive_session_id else None,
                    'created_at': decision.created_at.isoformat(),
                })

            # Session 901: Compute priority score and level
            priority_score = (
                (init.impact_score or 0.5) * 0.4 +
                (init.urgency or 0.5) * 0.2 +
                (init.confidence or 0.5) * 0.2 +
                (init.revenue_potential or 0.0) * 0.2
            )
            if priority_score >= 0.8:
                priority_level = 'critical'
            elif priority_score >= 0.6:
                priority_level = 'high'
            elif priority_score >= 0.4:
                priority_level = 'medium'
            else:
                priority_level = 'low'

            initiatives_list.append({
                'id': str(init.id),
                'human_id': init.human_id or None,
                'name': init.name,
                'description': init.description,
                'status': init.status,
                'current_stage': init.current_stage,
                'completion_percentage': completion_percentage,
                # Session 857: Additional progress metrics
                'approved_percentage': approved_percentage,
                'stages_with_work': stages_with_work,
                'stages': stages,
                'health': health,
                'health_issues': health_issues,
                'days_since_update': days_since_update,
                # Session 849: Trace data
                'source_decision_id': str(init.source_decision_id) if init.source_decision_id else None,
                'parent_topic': init.parent_topic,
                'source_decisions': source_decisions,
                # Session 901: Priority and categorization
                'purpose': init.purpose,
                'purpose_display': init.get_purpose_display() if hasattr(init, 'get_purpose_display') else init.purpose,
                'program': init.program,
                'program_display': init.get_program_display() if hasattr(init, 'get_program_display') else init.program,
                'priority_score': round(priority_score, 2),
                'priority_level': priority_level,
                'impact_score': init.impact_score,
                'urgency': init.urgency,
                'confidence': init.confidence,
                'revenue_potential': init.revenue_potential,
                'created_at': init.created_at.isoformat(),
                'updated_at': init.updated_at.isoformat(),
            })

        # Session 901: Calculate portfolio stats for tabs
        all_initiatives = Initiative.objects.all()
        stats = {
            'total': all_initiatives.count(),
            'active': all_initiatives.filter(status='ACTIVE').count(),
            'completed': all_initiatives.filter(status='COMPLETED').count(),
            'archived': all_initiatives.filter(status='ARCHIVED').count(),
            'on_hold': all_initiatives.filter(status='ON_HOLD').count(),
            # Program breakdown
            'by_program': {},
            # Purpose breakdown
            'by_purpose': {},
            # Priority breakdown
            'by_priority': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
            },
        }

        # Count by program
        for init in all_initiatives:
            prog = init.program or 'uncategorized'
            if prog not in stats['by_program']:
                stats['by_program'][prog] = 0
            stats['by_program'][prog] += 1

            purp = init.purpose or 'learning'
            if purp not in stats['by_purpose']:
                stats['by_purpose'][purp] = 0
            stats['by_purpose'][purp] += 1

            # Priority level
            priority_score = (
                (init.impact_score or 0.5) * 0.4 +
                (init.urgency or 0.5) * 0.2 +
                (init.confidence or 0.5) * 0.2 +
                (init.revenue_potential or 0.0) * 0.2
            )
            if priority_score >= 0.8:
                stats['by_priority']['critical'] += 1
            elif priority_score >= 0.6:
                stats['by_priority']['high'] += 1
            elif priority_score >= 0.4:
                stats['by_priority']['medium'] += 1
            else:
                stats['by_priority']['low'] += 1

        return JsonResponse({
            'success': True,
            'count': len(initiatives_list),
            'total_count': total_count,
            'limit': limit,
            'initiatives': initiatives_list,
            'stats': stats,
        })

    except Exception as e:
        logger.error(f"Error in initiatives_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def initiative_origin_trace_api(request, initiative_id):
    """
    Session 898: Get the complete origin trace for an initiative.

    This endpoint returns the entire chain:
    Trigger → Conversation → Decision → Initiative → Stages → Deliverable

    ChatGPT feedback: "This is the 'holy shit' moment in the video."
    """
    try:
        from core.models_document_registry import Initiative, InitiativeStage, STAGE_NAMES
        from core.models import AgentDecisionSummary, Deliverable
        import uuid as uuid_module

        # Handle both string and UUID for initiative_id
        if isinstance(initiative_id, str):
            try:
                initiative_id = uuid_module.UUID(initiative_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid initiative ID format'}, status=400)

        # Get the initiative
        try:
            initiative = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Initiative not found'}, status=404)

        # Build the trace response
        trace = {
            'initiative': {
                'id': str(initiative.id),
                'name': initiative.name,
                'description': initiative.description,
                'status': initiative.status,
                'current_stage': initiative.current_stage,
                'created_at': initiative.created_at.isoformat(),
                'updated_at': initiative.updated_at.isoformat(),
            },
            'decision': None,
            'conversation': None,
            'trigger': None,
            'origin_signals': None,  # Session 900: Signal provenance
            'agents': [],
            'stages': [],
            'deliverable': None,
        }

        # Get source decision(s)
        decisions = initiative.source_decisions.all()
        if decisions.exists():
            decision = decisions.first()
            trace['decision'] = {
                'id': str(decision.id),
                'decision_type': decision.decision_type,
                'artifact_type': decision.artifact_type,
                'topic': decision.topic,
                'key_insights': decision.key_insights[:3] if decision.key_insights else [],
                'recommended_stance': decision.recommended_stance,
                'suggested_feature': decision.suggested_feature[:500] if decision.suggested_feature else None,
                'rationale': decision.rationale,
                'participants': decision.participants,
                'status': decision.status,
                'created_at': decision.created_at.isoformat(),
            }
            trace['agents'] = decision.participants or []

            # Get source conversation (legacy AgentConversation or HiveMindSession)
            if decision.conversation:
                conv = decision.conversation
                trace['conversation'] = {
                    'id': str(conv.id),
                    'type': 'AgentConversation',
                    'topic': conv.topic,
                    'conversation_type': conv.conversation_type,
                    'trigger_type': conv.trigger_type,
                    'status': conv.status,
                    'message_count': conv.message_count,
                    'quality_score': conv.quality_score,
                    'conclusion': conv.conclusion[:500] if conv.conclusion else None,
                    'started_at': conv.started_at.isoformat() if conv.started_at else None,
                    'ended_at': conv.ended_at.isoformat() if conv.ended_at else None,
                    # Session 899: Include actual conversation messages
                    'messages': [],
                }
                # Session 899: Get conversation messages
                messages = conv.messages.select_related('agent').order_by('sequence_number')[:50]
                for msg in messages:
                    trace['conversation']['messages'].append({
                        'id': str(msg.id),
                        'agent_name': msg.agent.name if msg.agent else 'Unknown',
                        'content': msg.content,
                        'message_type': msg.message_type,
                        'sequence_number': msg.sequence_number,
                    })
                trace['trigger'] = {
                    'type': conv.trigger_type or 'unknown',
                    'description': f'{conv.trigger_type} triggered conversation' if conv.trigger_type else 'Unknown trigger',
                }
                # Get participants from conversation
                if hasattr(conv, 'participants') and conv.participants.exists():
                    trace['agents'] = [p.name for p in conv.participants.all()]

            elif decision.hive_session:
                hive = decision.hive_session
                trace['conversation'] = {
                    'id': str(hive.id),
                    'type': 'HiveMindSession',
                    'topic': hive.conversation_topic or hive.question[:100] if hive.question else None,
                    'conversation_type': hive.conversation_type if hasattr(hive, 'conversation_type') else hive.session_mode,
                    'status': hive.status,
                    'contribution_count': hive.contribution_count,
                    'total_thinking_time': hive.total_thinking_time,
                    'synthesis_summary': hive.synthesis_summary[:500] if hive.synthesis_summary else None,
                    'started_at': hive.started_at.isoformat() if hive.started_at else None,
                    'completed_at': hive.completed_at.isoformat() if hive.completed_at else None,
                    # Session 904: Include objective and success criteria
                    'objective': hive.objective if hasattr(hive, 'objective') else None,
                    'success_criteria': hive.success_criteria if hasattr(hive, 'success_criteria') else None,
                    # Session 899: Include actual contributions as messages
                    'messages': [],
                }
                # Session 899: Get HiveMind contributions (similar to messages)
                contributions = hive.contributions.select_related('agent').order_by('created_at')[:50]
                for idx, contrib in enumerate(contributions, 1):
                    trace['conversation']['messages'].append({
                        'id': str(contrib.id),
                        'agent_name': contrib.agent.name if contrib.agent else 'Unknown',
                        'content': contrib.contribution,
                        'message_type': contrib.perspective_type or 'contribution',
                        'sequence_number': idx,
                    })

                # Session 900: Signal Intelligence - WHY this conversation happened
                trace['trigger'] = {
                    'type': 'scheduled' if hive.auto_selected_agents else 'manual',
                    'description': 'Scheduled autonomous discussion' if hive.auto_selected_agents else 'Manual conversation',
                }

                # Session 900: Add signal provenance if available
                trace['origin_signals'] = None
                if hasattr(hive, 'signal_cluster') and hive.signal_cluster:
                    cluster = hive.signal_cluster
                    trace['origin_signals'] = {
                        'signal_cluster': {
                            'id': str(cluster.id),
                            'name': cluster.name,
                            'pattern_type': cluster.pattern_type,
                            'source_breakdown': cluster.source_breakdown,
                            'strength': cluster.strength,
                            'confidence': cluster.confidence,
                            'novelty': cluster.novelty,
                            'keywords': cluster.keywords,
                            'sample_signals': cluster.sample_signals[:3] if cluster.sample_signals else [],
                            'total_signals': cluster.total_signals,
                            'detected_at': cluster.detected_at.isoformat() if cluster.detected_at else None,
                        },
                        'auto_topic': None,
                    }
                    # Update trigger to be signal-driven
                    trace['trigger'] = {
                        'type': 'signal_driven',
                        'description': f'Signal-driven: {cluster.name}',
                        'confidence': hive.trigger_confidence,
                    }

                if hasattr(hive, 'auto_topic') and hive.auto_topic:
                    topic = hive.auto_topic
                    if trace['origin_signals'] is None:
                        trace['origin_signals'] = {'signal_cluster': None, 'auto_topic': None}
                    trace['origin_signals']['auto_topic'] = {
                        'id': str(topic.id),
                        'name': topic.name,
                        'description': topic.description,
                        'derived_from_pattern': topic.derived_from_pattern,
                        'rationale': topic.rationale,
                        'confidence': topic.confidence,
                        'urgency': topic.urgency,
                        'suggested_agents': topic.suggested_agent_names,
                        'suggested_conversation_type': topic.suggested_conversation_type,
                        'created_at': topic.created_at.isoformat() if topic.created_at else None,
                        'triggered_at': topic.triggered_at.isoformat() if topic.triggered_at else None,
                    }

        # Get stages with document content info
        # Session 907: Include content_length for each stage
        stages = InitiativeStage.objects.filter(initiative=initiative).select_related('document').order_by('stage')
        for stage in stages:
            # Get document content length if document exists
            content_length = 0
            if stage.document:
                content_length = len(stage.document.full_text or '') if hasattr(stage.document, 'full_text') else 0

            trace['stages'].append({
                'stage': stage.stage,
                'name': STAGE_NAMES.get(stage.stage, f'Stage {stage.stage}'),
                'status': stage.status,
                'document_id': str(stage.document_id) if stage.document_id else None,
                'content_length': content_length,  # Session 907: Add for Content (chars) metric
                'approved_at': stage.approved_at.isoformat() if stage.approved_at else None,
                'approved_by': stage.approved_by,
            })

        # Get deliverable
        deliverables = Deliverable.objects.filter(initiative=initiative).order_by('-created_at')
        if deliverables.exists():
            deliv = deliverables.first()
            trace['deliverable'] = {
                'id': str(deliv.id),
                'title': deliv.title,
                'deliverable_type': deliv.deliverable_type,
                'status': deliv.status,
                'content_length': len(deliv.content) if deliv.content else 0,
                'created_at': deliv.created_at.isoformat(),
            }

        # Calculate trace completeness
        # Session 904: Get active agent work on this initiative
        trace['active_work'] = []
        try:
            from core.models.agents_registry.models import AgentExecution
            # Find any running or recent executions for this initiative
            active_executions = AgentExecution.objects.filter(
                status__in=['running', 'initializing', 'pending'],
            ).order_by('-started_at')[:20]

            for exec in active_executions:
                ctx = exec.context or {}
                # Check if this execution is for our initiative
                if ctx.get('initiative_id') == str(initiative_id) or ctx.get('initiative_id') == initiative_id:
                    trace['active_work'].append({
                        'id': str(exec.id),
                        'agent_name': exec.template.name if exec.template else 'Unknown Agent',
                        'status': exec.status,
                        'stage_num': ctx.get('stage_num'),
                        'progress_percentage': exec.progress_percentage or 0,
                        'current_step': exec.current_step or '',
                        'started_at': exec.started_at.isoformat() if exec.started_at else None,
                        'task_description': (exec.input_data or {}).get('task', '')[:200] if exec.input_data else '',
                    })

            # Also check for recent completed work (last hour) to show what just finished
            from django.utils import timezone
            from datetime import timedelta
            recent_completed = AgentExecution.objects.filter(
                status='completed',
                completed_at__gte=timezone.now() - timedelta(hours=1),
            ).order_by('-completed_at')[:10]

            for exec in recent_completed:
                ctx = exec.context or {}
                if ctx.get('initiative_id') == str(initiative_id) or ctx.get('initiative_id') == initiative_id:
                    trace['active_work'].append({
                        'id': str(exec.id),
                        'agent_name': exec.template.name if exec.template else 'Unknown Agent',
                        'status': 'completed',
                        'stage_num': ctx.get('stage_num'),
                        'progress_percentage': 100,
                        'current_step': 'Completed',
                        'started_at': exec.started_at.isoformat() if exec.started_at else None,
                        'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
                        'execution_time_seconds': exec.execution_time_seconds,
                        'task_description': (exec.input_data or {}).get('task', '')[:200] if exec.input_data else '',
                    })
        except Exception as e:
            logger.warning(f"Could not fetch active work: {e}")

        # Session 900: Added origin_signals to completeness
        has_origin_signals = trace.get('origin_signals') is not None
        trace['trace_completeness'] = {
            'has_decision': trace['decision'] is not None,
            'has_conversation': trace['conversation'] is not None,
            'has_trigger': trace['trigger'] is not None,
            'has_agents': len(trace['agents']) > 0,
            'has_stages': len(trace['stages']) > 0,
            'has_deliverable': trace['deliverable'] is not None,
            'has_origin_signals': has_origin_signals,  # Session 900
            'completeness_score': sum([
                1 if trace['decision'] else 0,
                1 if trace['conversation'] else 0,
                1 if trace['trigger'] else 0,
                1 if trace['agents'] else 0,
                1 if trace['stages'] else 0,
                1 if trace['deliverable'] else 0,
                1 if has_origin_signals else 0,  # Session 900: Bonus for signal provenance
            ]) / 7 * 100,
        }

        return JsonResponse({
            'success': True,
            'trace': trace,
        })

    except Exception as e:
        logger.error(f"Error in initiative_origin_trace_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def populate_initiatives_api(request):
    """
    Session 1085: Auto-populate initiatives from unlinked deliverables.

    Groups unlinked deliverables by workspace + category and creates
    one initiative per group (if no matching initiative already exists).
    Links the deliverables to the new initiative.
    """
    try:
        from django.db.models import Count
        from core.models_deliverables import Deliverable
        from core.models import Initiative

        # Find deliverables not yet linked to any initiative, grouped by workspace+category
        unlinked = (
            Deliverable.objects
            .filter(initiative__isnull=True, workspace__isnull=False)
            .exclude(category='')
            .values('workspace__name', 'workspace_id', 'category')
            .annotate(count=Count('id'))
            .filter(count__gte=3)  # Only create initiative if 3+ deliverables
            .order_by('-count')
        )

        created_initiatives = []
        linked_count = 0

        for group in unlinked:
            ws_name = group['workspace__name']
            category = group['category']
            ws_id = group['workspace_id']
            name = f"{ws_name}: {category.replace('_', ' ').title()}"

            # Skip if initiative with this name already exists
            if Initiative.objects.filter(name=name).exists():
                continue

            initiative = Initiative.objects.create(
                name=name,
                description=f"Auto-populated from {group['count']} {category} deliverables in {ws_name}",
                status='ACTIVE',
                created_by='auto_populate',
                current_stage=1,
            )

            # Session 1191: bootstrap last_activity_at so freshly-created
            # auto-populated Initiatives aren't born with NULL. Without this,
            # the initiative_activity_tick beat task would treat every new
            # auto-populated row as cold-stale and pick it up on first sweep
            # — wasteful churn. update_activity() writes timezone.now()
            # which is correct for "this row was just created."
            initiative.update_activity(reason='auto_populate_create')

            # Link the deliverables
            updated = Deliverable.objects.filter(
                initiative__isnull=True,
                workspace_id=ws_id,
                category=category,
            ).update(initiative=initiative)

            linked_count += updated
            created_initiatives.append({
                'name': name,
                'deliverables_linked': updated,
            })

        return JsonResponse({
            'success': True,
            'message': f'Created {len(created_initiatives)} initiatives, linked {linked_count} deliverables',
            'created_count': len(created_initiatives),
            'created_initiatives': created_initiatives,
        })

    except Exception as e:
        logger.error(f"Error in populate_initiatives_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def trigger_initiative_pipeline_api(request):
    """
    Session 880: Manually trigger the initiative pipeline advancement task.

    This endpoint allows immediate execution of the initiative pipeline
    instead of waiting for the scheduled hourly task.

    Query params:
        limit: Max initiatives to process (default 10)
        auto_approve: Auto-approve generated documents (default true)
    """
    try:
        import json
        from core.tasks import advance_initiative_pipeline

        # Parse request body if present
        body = {}
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                pass

        # Get parameters
        limit = int(body.get('limit', request.GET.get('limit', 10)))
        auto_approve = body.get('auto_approve', request.GET.get('auto_approve', 'true'))
        if isinstance(auto_approve, str):
            auto_approve = auto_approve.lower() in ('true', '1', 'yes')

        # Queue the task for immediate execution
        task = advance_initiative_pipeline.delay(limit=limit, auto_approve=auto_approve)

        return JsonResponse({
            'success': True,
            'message': f'Initiative pipeline triggered (limit={limit}, auto_approve={auto_approve})',
            'task_id': task.id,
            'status': 'queued',
        })

    except Exception as e:
        logger.error(f"Error triggering initiative pipeline: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Session 902: Initiative Action Items API
# =============================================================================

@require_http_methods(["GET"])
def initiative_action_items_api(request, initiative_id):
    """
    Session 902: Get action items for an initiative.

    Query params:
    - status: Filter by status (pending, in_progress, completed, blocked, cancelled)
    - priority: Filter by priority (critical, high, medium, low)
    """
    try:
        from core.models_document_registry import Initiative, InitiativeActionItem
        import uuid as uuid_module

        # Handle UUID
        if isinstance(initiative_id, str):
            try:
                initiative_id = uuid_module.UUID(initiative_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid initiative ID'}, status=400)

        # Verify initiative exists
        try:
            initiative = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Initiative not found'}, status=404)

        # Get action items with optional filters
        items = InitiativeActionItem.objects.filter(initiative=initiative)

        status_filter = request.GET.get('status')
        if status_filter:
            items = items.filter(status=status_filter)

        priority_filter = request.GET.get('priority')
        if priority_filter:
            items = items.filter(priority=priority_filter)

        items = items.order_by('order', '-priority', 'created_at')

        # Calculate stats
        all_items = InitiativeActionItem.objects.filter(initiative=initiative)
        stats = {
            'total': all_items.count(),
            'pending': all_items.filter(status='pending').count(),
            'in_progress': all_items.filter(status='in_progress').count(),
            'completed': all_items.filter(status='completed').count(),
            'blocked': all_items.filter(status='blocked').count(),
            'completion_rate': 0,
        }
        if stats['total'] > 0:
            stats['completion_rate'] = round(stats['completed'] / stats['total'] * 100, 1)

        items_list = []
        for item in items:
            items_list.append({
                'id': str(item.id),
                'title': item.title,
                'description': item.description,
                'assigned_agent': item.assigned_agent,
                'assigned_user_id': item.assigned_user_id,
                'timeline_text': item.timeline_text,
                'due_date': item.due_date.isoformat() if item.due_date else None,
                'estimated_hours': item.estimated_hours,
                'status': item.status,
                'priority': item.priority,
                'started_at': item.started_at.isoformat() if item.started_at else None,
                'completed_at': item.completed_at.isoformat() if item.completed_at else None,
                'completed_by': item.completed_by,
                'completion_notes': item.completion_notes,
                'blocked_reason': item.blocked_reason,
                'is_overdue': item.is_overdue,
                'days_until_due': item.days_until_due,
                'source_conversation_id': str(item.source_conversation_id) if item.source_conversation_id else None,
                'source_text': item.source_text,
                'order': item.order,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'initiative_id': str(initiative_id),
            'initiative_name': initiative.name,
            'count': len(items_list),
            'stats': stats,
            'action_items': items_list,
        })

    except Exception as e:
        logger.error(f"Error in initiative_action_items_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def action_item_update_api(request, item_id):
    """
    Session 902: Update an action item's status or details.

    POST body (JSON):
    - status: 'pending', 'in_progress', 'completed', 'blocked', 'cancelled'
    - priority: 'critical', 'high', 'medium', 'low'
    - title: Updated title
    - description: Updated description
    - assigned_agent: Agent name
    - due_date: 'YYYY-MM-DD'
    - completion_notes: Notes when completing
    - blocked_reason: Reason when blocking
    """
    try:
        import json
        from core.models_document_registry import InitiativeActionItem
        from django.utils import timezone
        import uuid as uuid_module

        # Handle UUID
        if isinstance(item_id, str):
            try:
                item_id = uuid_module.UUID(item_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid item ID'}, status=400)

        # Get the action item
        try:
            item = InitiativeActionItem.objects.get(id=item_id)
        except InitiativeActionItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Action item not found'}, status=404)

        # Parse request body
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # Track what was updated
        updated_fields = []

        # Update status with side effects
        if 'status' in body:
            new_status = body['status']
            if new_status in ['pending', 'in_progress', 'completed', 'blocked', 'cancelled']:
                old_status = item.status
                item.status = new_status

                # Handle status-specific logic
                if new_status == 'in_progress' and old_status == 'pending':
                    item.started_at = timezone.now()
                    updated_fields.append('started_at')
                elif new_status == 'completed':
                    item.completed_at = timezone.now()
                    item.completed_by = body.get('completed_by', 'user')
                    if 'completion_notes' in body:
                        item.completion_notes = body['completion_notes']
                    updated_fields.extend(['completed_at', 'completed_by', 'completion_notes'])
                elif new_status == 'blocked' and 'blocked_reason' in body:
                    item.blocked_reason = body['blocked_reason']
                    updated_fields.append('blocked_reason')

                updated_fields.append('status')

        # Update other fields
        if 'priority' in body and body['priority'] in ['critical', 'high', 'medium', 'low']:
            item.priority = body['priority']
            updated_fields.append('priority')

        if 'title' in body:
            item.title = body['title'][:300]
            updated_fields.append('title')

        if 'description' in body:
            item.description = body['description']
            updated_fields.append('description')

        if 'assigned_agent' in body:
            item.assigned_agent = body['assigned_agent'][:100]
            updated_fields.append('assigned_agent')

        if 'due_date' in body:
            if body['due_date']:
                from datetime import datetime
                try:
                    item.due_date = datetime.strptime(body['due_date'], '%Y-%m-%d').date()
                    updated_fields.append('due_date')
                except ValueError:
                    pass
            else:
                item.due_date = None
                updated_fields.append('due_date')

        if 'estimated_hours' in body:
            item.estimated_hours = float(body['estimated_hours']) if body['estimated_hours'] else None
            updated_fields.append('estimated_hours')

        if 'order' in body:
            item.order = int(body['order'])
            updated_fields.append('order')

        # Save if anything changed
        if updated_fields:
            item.save()

        return JsonResponse({
            'success': True,
            'item_id': str(item.id),
            'updated_fields': updated_fields,
            'action_item': {
                'id': str(item.id),
                'title': item.title,
                'status': item.status,
                'priority': item.priority,
                'is_overdue': item.is_overdue,
            }
        })

    except Exception as e:
        logger.error(f"Error in action_item_update_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def action_item_create_api(request, initiative_id):
    """
    Session 902: Create a new action item for an initiative.

    POST body (JSON):
    - title: Required
    - description: Optional
    - assigned_agent: Optional agent name
    - priority: Optional (default: medium)
    - due_date: Optional 'YYYY-MM-DD'
    - timeline_text: Optional
    """
    try:
        import json
        from core.models_document_registry import Initiative, InitiativeActionItem
        import uuid as uuid_module

        # Handle UUID
        if isinstance(initiative_id, str):
            try:
                initiative_id = uuid_module.UUID(initiative_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid initiative ID'}, status=400)

        # Verify initiative exists
        try:
            initiative = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Initiative not found'}, status=404)

        # Parse request body
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        if not body.get('title'):
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)

        # Get next order number
        max_order = InitiativeActionItem.objects.filter(
            initiative=initiative
        ).values_list('order', flat=True).order_by('-order').first() or 0

        # Parse due_date if provided
        due_date = None
        if body.get('due_date'):
            from datetime import datetime
            try:
                due_date = datetime.strptime(body['due_date'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # Create the action item
        item = InitiativeActionItem.objects.create(
            initiative=initiative,
            title=body['title'][:300],
            description=body.get('description', ''),
            assigned_agent=body.get('assigned_agent', '')[:100] if body.get('assigned_agent') else '',
            priority=body.get('priority', 'medium'),
            due_date=due_date,
            timeline_text=body.get('timeline_text', '')[:50] if body.get('timeline_text') else '',
            estimated_hours=float(body['estimated_hours']) if body.get('estimated_hours') else None,
            order=max_order + 1,
            created_by='user',
        )

        return JsonResponse({
            'success': True,
            'message': 'Action item created',
            'action_item': {
                'id': str(item.id),
                'title': item.title,
                'status': item.status,
                'priority': item.priority,
                'order': item.order,
            }
        })

    except Exception as e:
        logger.error(f"Error in action_item_create_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
def action_item_delete_api(request, item_id):
    """Session 902: Delete an action item."""
    try:
        from core.models_document_registry import InitiativeActionItem
        import uuid as uuid_module

        # Handle UUID
        if isinstance(item_id, str):
            try:
                item_id = uuid_module.UUID(item_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid item ID'}, status=400)

        # Get and delete the action item
        try:
            item = InitiativeActionItem.objects.get(id=item_id)
            title = item.title
            item.delete()
        except InitiativeActionItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Action item not found'}, status=404)

        return JsonResponse({
            'success': True,
            'message': f'Action item "{title}" deleted',
        })

    except Exception as e:
        logger.error(f"Error in action_item_delete_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def extract_action_items_api(request, initiative_id=None):
    """
    Session 902: Extract action items from conversation conclusions.

    If initiative_id provided: Extract from conversations linked to that initiative
    If no initiative_id: Bulk extract from recent conversations (limit param)
    """
    try:
        import json
        from core.services.action_item_parser import (
            extract_action_items_from_conversation,
            bulk_extract_action_items
        )

        body = {}
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                pass

        if initiative_id:
            # Extract from specific initiative's conversations
            from core.models_document_registry import Initiative
            import uuid as uuid_module

            if isinstance(initiative_id, str):
                try:
                    initiative_id = uuid_module.UUID(initiative_id)
                except ValueError:
                    return JsonResponse({'success': False, 'error': 'Invalid initiative ID'}, status=400)

            try:
                initiative = Initiative.objects.get(id=initiative_id)
            except Initiative.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Initiative not found'}, status=404)

            # Find conversations linked to this initiative via decisions
            from core.models import AgentDecisionSummary
            decisions = AgentDecisionSummary.objects.filter(initiative=initiative)
            session_ids = set()
            for d in decisions:
                if d.hive_session_id:
                    session_ids.add(str(d.hive_session_id))

            items_created = 0
            for session_id in session_ids:
                items = extract_action_items_from_conversation(session_id)
                items_created += len(items)

            return JsonResponse({
                'success': True,
                'initiative_id': str(initiative_id),
                'sessions_processed': len(session_ids),
                'items_created': items_created,
            })
        else:
            # Bulk extract
            limit = int(body.get('limit', 50))
            stats = bulk_extract_action_items(limit=limit)

            return JsonResponse({
                'success': True,
                'stats': stats,
            })

    except Exception as e:
        logger.error(f"Error in extract_action_items_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Session 914.7: Operating Rhythm API
# =============================================================================

@require_http_methods(["GET"])
def operating_rhythm_api(request):
    """
    Session 914.7: Get operating rhythm status including daily priorities,
    weekly report summary, and rhythm recommendations.
    """
    try:
        from core.services.operating_rhythm import (
            get_rhythm_status,
            get_daily_priorities,
            generate_weekly_report,
        )

        status = get_rhythm_status()
        daily = get_daily_priorities()

        # Get compact weekly report summary
        report = generate_weekly_report()
        weekly_summary = report.get('summary', {})

        return JsonResponse({
            'success': True,
            'daily_priorities': {
                'priorities': daily.get('priorities', []),
                'date': daily.get('date'),
                'is_current': daily.get('is_current', False),
                'needs_update': daily.get('needs_update', True),
            },
            'weekly_summary': {
                'week_start': report.get('week_start'),
                'week_end': report.get('week_end'),
                'shipped_count': weekly_summary.get('shipped_count', 0),
                'deliverables_created': weekly_summary.get('deliverables_created', 0),
                'learned_count': weekly_summary.get('learned_count', 0),
                'blocked_count': weekly_summary.get('blocked_count', 0),
                'kill_candidates_count': weekly_summary.get('kill_candidates_count', 0),
                'needs_decision_count': weekly_summary.get('needs_decision_count', 0),
            },
            'initiative_summary': status.get('initiative_summary', {}),
            'recommendations': status.get('recommendations', []),
            'last_weekly_feedback': status.get('last_weekly_feedback'),
        })

    except Exception as e:
        logger.error(f"[Session 914.7] Error in operating_rhythm_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def initiative_rhythm_api(request, initiative_id):
    """
    Session 914.7: Get operating rhythm data for a specific initiative.
    Shows if it's in daily focus, mapped to a priority, etc.
    """
    try:
        from core.models_document_registry import Initiative
        from core.services.operating_rhythm import (
            get_daily_priorities,
            check_initiative_priority_mapping,
        )
        import uuid as uuid_module

        if isinstance(initiative_id, str):
            try:
                initiative_id = uuid_module.UUID(initiative_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid initiative ID'}, status=400)

        try:
            initiative = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Initiative not found'}, status=404)

        # Get daily priorities
        daily = get_daily_priorities()
        priority_mapping = check_initiative_priority_mapping(initiative)

        # Get founder intent status
        founder_intent = {
            'set': initiative.founder_intent_set,
            'execution_speed': initiative.execution_speed if initiative.founder_intent_set else None,
            'risk_tolerance': initiative.risk_tolerance if initiative.founder_intent_set else None,
            'stop_rule': initiative.stop_rule if initiative.founder_intent_set else None,
        }

        # Get boardroom approval status
        boardroom = {
            'required': initiative.requires_boardroom_approval,
            'approved': initiative.boardroom_approved,
            'approved_by': initiative.boardroom_approved_by if initiative.boardroom_approved else None,
            'approved_at': initiative.boardroom_approved_at.isoformat() if initiative.boardroom_approved_at else None,
        }

        return JsonResponse({
            'success': True,
            'initiative_id': str(initiative_id),
            'is_daily_focus': initiative.is_daily_focus,
            'daily_focus_date': initiative.daily_focus_date.isoformat() if initiative.daily_focus_date else None,
            'manual_priority_rank': initiative.manual_priority_rank,
            'manual_priority_reason': initiative.manual_priority_reason or '',
            'priority_mapping': priority_mapping,
            'daily_priorities': {
                'priorities': daily.get('priorities', []),
                'is_current': daily.get('is_current', False),
            },
            'founder_intent': founder_intent,
            'boardroom': boardroom,
            'can_auto_progress': initiative.can_auto_progress,
            'progression_blocked_reason': initiative.progression_blocked_reason or '',
            'execution_track': initiative.execution_track or 'not_set',
        })

    except Exception as e:
        logger.error(f"[Session 914.7] Error in initiative_rhythm_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def set_founder_intent_api(request, initiative_id):
    """
    Session 919: Set founder intent for an initiative via API.

    POST body:
    {
        "execution_speed": "fast" | "balanced" | "thorough",
        "risk_tolerance": "low" | "medium" | "high",
        "stop_rule": "optional stop rule text"
    }
    """
    try:
        import json
        from core.models_document_registry import Initiative
        import uuid as uuid_module

        if isinstance(initiative_id, str):
            try:
                initiative_id = uuid_module.UUID(initiative_id)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid initiative ID'}, status=400)

        try:
            initiative = Initiative.objects.get(id=initiative_id)
        except Initiative.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Initiative not found'}, status=404)

        body = {}
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        # Get values with defaults
        execution_speed = body.get('execution_speed', 'balanced')
        risk_tolerance = body.get('risk_tolerance', 'medium')
        stop_rule = body.get('stop_rule', '')

        # Validate choices
        valid_speeds = ['fast', 'balanced', 'thorough']
        valid_risks = ['low', 'medium', 'high']

        if execution_speed not in valid_speeds:
            return JsonResponse({
                'success': False,
                'error': f'Invalid execution_speed. Must be one of: {valid_speeds}'
            }, status=400)

        if risk_tolerance not in valid_risks:
            return JsonResponse({
                'success': False,
                'error': f'Invalid risk_tolerance. Must be one of: {valid_risks}'
            }, status=400)

        # Set founder intent using the model method
        initiative.set_founder_intent(
            execution_speed=execution_speed,
            risk_tolerance=risk_tolerance,
            stop_rule=stop_rule,
            set_by='api'
        )

        return JsonResponse({
            'success': True,
            'message': 'Founder intent set successfully',
            'initiative_id': str(initiative_id),
            'founder_intent': {
                'execution_speed': initiative.execution_speed,
                'risk_tolerance': initiative.risk_tolerance,
                'stop_rule': initiative.stop_rule,
                'set': initiative.founder_intent_set,
                'can_auto_progress': initiative.can_auto_progress,
            }
        })

    except Exception as e:
        logger.error(f"[Session 919] Error in set_founder_intent_api: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
