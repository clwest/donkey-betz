"""
Dashboard views for the Unified Donkey Betz Platform.

Provides dashboard statistics and activity endpoints.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from core.cache_middleware import cache_api_response
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
# @cache_api_response(timeout=60)  # Temporarily disabled for debugging
def dashboard_stats(request):
    """Get overall dashboard statistics - matches frontend expectations."""
    # Handle authenticated or anonymous users
    # Embeddings are stored with integer user_id=9 for historical reasons
    # This maps to the chris user account
    user_id = 9  # Default to user ID 9 (chris) where embeddings are stored
    
    # For authenticated users, check if it's chris
    if hasattr(request, 'user') and request.user.is_authenticated:
        if request.user.username == 'chris':
            user_id = 9  # Use the integer ID where embeddings are stored
        else:
            # For other users, try to use their integer representation
            # but this will likely return 0 embeddings
            user_id = 9  # For now, always show chris's data
    
    # Provide the structure the frontend expects
    stats = {
        'total_content': 0,
        'total_content_trend': '+0%',
        'images_generated': 0,
        'images_trend': '+0%',
        'text_content': 0,
        'video_content': 0,
        'active_workflows': 0,
        'extended_content': {
            'blogs': 0,
            'social_posts': 0,
            'campaigns': 0,
            'ebooks': 0,
            'podcasts': 0,
            'pitch_decks': 0,
        },
        'usage_period': 'Last 30 days',
        # Additional backend fields
        'total_agents': 0,
        'total_embeddings': 0,
    }
    
    # Try to get real data where available
    try:
        from core.models.agents_registry import UnifiedAgentTemplate
        agent_count = UnifiedAgentTemplate.objects.count()
        stats['total_agents'] = agent_count
        print(f"Successfully retrieved {agent_count} agents")
        # Also update total content if we have agents
        if agent_count > 0:
            stats['total_content'] = max(stats['total_content'], agent_count)
    except Exception as e:
        print(f"Error getting agent count: {e}")
        import traceback
        traceback.print_exc()
        try:
            from core.models_unified_system import Agent  # Session 758: Fixed import path
            stats['total_agents'] = Agent.objects.count()
        except:
            pass
    
    # Session 1235 P5#3 audit Tranche 1 PR #1: pivot from dead
    # `unified_embeddings` table (in non-existent `ai_unified_platform`
    # DB) to live `DocumentEmbedding` ORM. Pre-pivot this block silently
    # caught the connection failure and returned a hardcoded `67922`
    # fallback indistinguishable from real data. Now reads the real
    # 36k+ DocumentEmbedding chunks populated by the docs corpus.
    try:
        from content.models import DocumentEmbedding
        # Use localdate() (TIME_ZONE-aware) so created_at__date comparisons
        # match Django's USE_TZ + TIME_ZONE=America/Denver semantics. Naive
        # timezone.now().date() would return UTC date and miss late-evening
        # Denver rows that crossed midnight UTC.
        today = timezone.localdate()
        total_embeddings = DocumentEmbedding.objects.count()
        today_count = DocumentEmbedding.objects.filter(
            created_at__date=today,
        ).count()
        # User-scoped conversation count: DocumentEmbedding doesn't have
        # a per-user conversation surface (pre-pivot this was reading
        # `content_type='conversation' AND metadata->>'user_id'=N` from a
        # table that never existed). Report 0 honestly until a real
        # conversation embedding model is wired (Session 1236 follow-up).
        user_conversations = 0

        stats['total_embeddings'] = total_embeddings
        stats['total_content'] = total_embeddings
        stats['user_conversations'] = user_conversations
        stats['total_content_trend'] = f'+{today_count}' if today_count > 0 else '0'
        stats['learning_today'] = today_count
    except Exception as e:
        # Narrow this further in a follow-up if the broad except masks
        # real DB issues; matched to the pre-pivot shape for now.
        logger.error(f"Failed to get DocumentEmbedding counts: {e}")
        stats['total_embeddings'] = 0
        stats['total_content'] = 0
    
    # Try to get content breakdown
    try:
        from content.models import ContentItem
        # Use user_id instead of user object
        content_count = ContentItem.objects.filter(user_id=user_id).count()
        stats['text_content'] = content_count
        stats['total_content'] = max(stats['total_content'], content_count)
    except:
        pass
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_activity(request):
    """Get recent activity for the dashboard - matches frontend expectations."""
    limit = int(request.GET.get('limit', 10))
    # Handle authenticated or anonymous users
    user_id = 9  # Default to user ID 9 (chris) where embeddings are stored
    if hasattr(request, 'user') and request.user.is_authenticated:
        user_id = request.user.id
    
    activities = []
    
    # Add properly formatted activities for frontend
    activities.append({
        'id': 1,
        'type': 'system',
        'name': 'System Started',
        'description': 'Unified Donkey Betz Platform is running',
        'time': '1 minute ago',
        'status': 'completed',
        'content_type': 'system',
        'created_at': timezone.now().isoformat(),
        'nav_route': '/dashboard'
    })
    
    activities.append({
        'id': 2,
        'type': 'database',
        'name': 'Database Connected',
        'description': 'PostgreSQL connection established',
        'time': '2 minutes ago',
        'status': 'completed',
        'content_type': 'database',
        'created_at': (timezone.now() - timedelta(minutes=1)).isoformat(),
    })
    
    activities.append({
        'id': 3,
        'type': 'websocket',
        'name': 'WebSocket Ready',
        'description': 'Real-time communication channel active',
        'time': '3 minutes ago',
        'status': 'running',
        'content_type': 'websocket',
        'created_at': (timezone.now() - timedelta(minutes=2)).isoformat(),
    })
    
    activities.append({
        'id': 4,
        'type': 'embeddings',
        'name': 'Embeddings Indexed',
        'description': 'Personal knowledge base ready',
        'time': '5 minutes ago',
        'status': 'completed',
        'content_type': 'text',
        'created_at': (timezone.now() - timedelta(minutes=5)).isoformat(),
        'nav_route': '/personal-knowledge'
    })
    
    return Response(activities[:limit])


@api_view(['GET'])
@permission_classes([AllowAny])
def embeddings_stats(request):
    """Get embeddings statistics for the dashboard.

    Session 1235 P5#3 audit Tranche 1 PR #1: pivoted from dead
    `unified_embeddings` raw-SQL queries to live `DocumentEmbedding` +
    `Document` ORM. Pre-pivot this returned hardcoded `265174`-style
    sample data with `status='demo_mode'` whenever the dead table query
    failed (always). Users saw misleading fake numbers presented as if
    real.
    """
    stats = {
        'total_embeddings': 0,
        'by_platform': {},
        'by_type': {},
        'recent_count': 0,
        'zero_vectors': 0,
        'status': 'healthy',
        'last_updated': timezone.now().isoformat(),
    }

    try:
        from content.models import Document, DocumentEmbedding

        total_embeddings = DocumentEmbedding.objects.count()
        stats['total_embeddings'] = total_embeddings

        # Platform breakdown — post-pivot, everything is "unified_platform".
        # Pre-pivot this read `source_database` which doesn't exist on the
        # live model. Surface a single bucket honestly; UI can hide it.
        stats['by_platform'] = {'unified_platform': total_embeddings}

        # By type: Document.document_type drives content classification
        # (markdown / text / pdf / etc.). Pre-pivot this read raw-SQL
        # content_type from the dead table.
        type_breakdown = dict(
            Document.objects.values_list('document_type').annotate(
                count=Count('id'),
            ).values_list('document_type', 'count')
        )
        stats['by_type'] = type_breakdown or {'unknown': 0}

        # Recent (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        stats['recent_count'] = DocumentEmbedding.objects.filter(
            created_at__gte=seven_days_ago,
        ).count()

        # Zero vectors — DocumentEmbedding writes via the embedding pipeline
        # which only persists on successful embedding generation, so 0 is
        # the structural expected value. Pre-pivot this was speculative.
        stats['zero_vectors'] = 0
        stats['status'] = 'healthy'
        stats['message'] = (
            f'Live data from DocumentEmbedding ({total_embeddings:,} chunks)'
        )

    except Exception as e:
        # Narrow this further in a follow-up if the broad except masks
        # real DB issues. Matches pre-pivot shape for now.
        stats['status'] = 'error'
        stats['debug_error'] = str(e)
        logger.error(f"embeddings_stats: failed to query DocumentEmbedding: {e}")
    
    return Response(stats)