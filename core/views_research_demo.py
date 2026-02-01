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
    Provides a single source of truth for document lifecycle tracking.
    """
    try:
        from core.models_document_registry import Initiative, InitiativeStage, STAGE_NAMES
        from django.utils import timezone
        from django.db.models import Prefetch

        # Session 884: Support limit and status filter query params
        # Session 897: Reduced default from 200 to 50 for performance
        limit = int(request.GET.get('limit', 50))
        status_filter = request.GET.get('status')  # Optional: ACTIVE, COMPLETED, etc.

        # Session 897: Use prefetch_related to batch load stages and decisions
        # This reduces ~3000 queries to just 3 queries total
        initiatives = Initiative.objects.all().order_by('-updated_at').prefetch_related(
            Prefetch('stages', queryset=InitiativeStage.objects.all()),
            Prefetch('source_decisions'),
        )
        if status_filter:
            initiatives = initiatives.filter(status=status_filter)

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

            initiatives_list.append({
                'id': str(init.id),
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
                'created_at': init.created_at.isoformat(),
                'updated_at': init.updated_at.isoformat(),
            })

        return JsonResponse({
            'success': True,
            'count': len(initiatives_list),
            'total_count': total_count,
            'limit': limit,
            'initiatives': initiatives_list,
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
                }
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
                }
                trace['trigger'] = {
                    'type': 'scheduled' if hive.auto_selected_agents else 'manual',
                    'description': 'Scheduled autonomous discussion' if hive.auto_selected_agents else 'Manual conversation',
                }

        # Get stages
        stages = InitiativeStage.objects.filter(initiative=initiative).order_by('stage')
        for stage in stages:
            trace['stages'].append({
                'stage': stage.stage,
                'name': STAGE_NAMES.get(stage.stage, f'Stage {stage.stage}'),
                'status': stage.status,
                'document_id': str(stage.document_id) if stage.document_id else None,
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
        trace['trace_completeness'] = {
            'has_decision': trace['decision'] is not None,
            'has_conversation': trace['conversation'] is not None,
            'has_trigger': trace['trigger'] is not None,
            'has_agents': len(trace['agents']) > 0,
            'has_stages': len(trace['stages']) > 0,
            'has_deliverable': trace['deliverable'] is not None,
            'completeness_score': sum([
                1 if trace['decision'] else 0,
                1 if trace['conversation'] else 0,
                1 if trace['trigger'] else 0,
                1 if trace['agents'] else 0,
                1 if trace['stages'] else 0,
                1 if trace['deliverable'] else 0,
            ]) / 6 * 100,
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
    Session 622: Auto-populate initiatives from existing deliverables.
    Creates Initiative records and links existing stage documents.
    """
    try:
        from django.db.models import Q
        from core.models_unified_system import SelfBlog
        from core.models_document_registry import Initiative, InitiativeStage

        # Find all unique parent topics from deliverables
        deliverables = SelfBlog.objects.filter(
            Q(title__startswith='[Stage 1 -') |
            Q(title__startswith='[Stage 2 -') |
            Q(title__startswith='[Stage 3 -') |
            Q(title__startswith='[Stage 4 -') |
            Q(title__startswith='[Stage 5 -')
        )

        # Group by parent topic
        topics = {}
        for doc in deliverables:
            if doc.stats_snapshot and doc.stats_snapshot.get('parent_topic'):
                topic = doc.stats_snapshot['parent_topic']
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(doc)

        created_initiatives = []
        for topic, docs in topics.items():
            # Create or get initiative
            initiative, created = Initiative.objects.get_or_create(
                name=topic,
                defaults={
                    'description': f'Auto-populated from {len(docs)} deliverables',
                    'created_by': 'auto_populate',
                    'parent_topic': topic,
                }
            )

            if created:
                # Link documents to stages
                for doc in docs:
                    stage_num = doc.stats_snapshot.get('stage') if doc.stats_snapshot else None
                    if stage_num:
                        InitiativeStage.objects.get_or_create(
                            initiative=initiative,
                            stage=stage_num,
                            defaults={
                                'document': doc,
                                'status': 'APPROVED',
                                'approved_by': 'auto_populate',
                                'approved_at': doc.created_at,
                            }
                        )

                # Update current stage
                max_stage = max([d.stats_snapshot.get('stage', 0) for d in docs if d.stats_snapshot])
                initiative.current_stage = min(max_stage + 1, 5)
                initiative.save()

                created_initiatives.append({
                    'name': topic,
                    'stages_linked': len(docs),
                    'current_stage': initiative.current_stage,
                })

        return JsonResponse({
            'success': True,
            'message': f'Created {len(created_initiatives)} new initiatives',
            'created': created_initiatives,
            'existing_topics': [t for t in topics.keys() if t not in [i['name'] for i in created_initiatives]],
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
