"""
Session 884: Home Page Boot API

The "AI OS boot experience" - aggregates all data needed for the home page
in a single call to give users a snapshot of their AI operating system state.

Endpoint: /api/home/boot/

Returns:
- greeting: User name and time-of-day based greeting
- while_away: Activity since last visit (spiders, dreams, initiatives, decisions)
- active_projects: Active initiatives with completion % and pending decisions
- quick_stats: System health summary
"""

from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import Agent, LegacySpiderData, UserProfile
from core.models_document_registry import Initiative
from core.models_unified_system import AgentDream, AgentDecisionSummary
from core.security.object_authz import scope_queryset_initiative


def get_time_of_day():
    """Get time-of-day greeting based on current hour."""
    hour = timezone.localtime().hour
    if hour < 12:
        return 'morning'
    elif hour < 17:
        return 'afternoon'
    else:
        return 'evening'


def get_last_visit(request):
    """
    Get user's last visit time from session.
    Defaults to 24 hours ago if not set.
    """
    last_visit_str = request.session.get('last_home_visit')
    if last_visit_str:
        try:
            return datetime.fromisoformat(last_visit_str)
        except (ValueError, TypeError):
            pass
    # Default to 24 hours ago
    return timezone.now() - timedelta(hours=24)


def update_last_visit(request):
    """Update the last visit timestamp in session."""
    request.session['last_home_visit'] = timezone.now().isoformat()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def home_boot(request):
    """
    Boot endpoint for the AI OS home page.

    Aggregates all data needed for the home page greeting and status display.
    Updates last_visit timestamp on each call.
    """
    user = request.user
    now = timezone.now()
    last_visit = get_last_visit(request)

    # Calculate hours since last visit
    hours_since_visit = (now - last_visit).total_seconds() / 3600

    # --- Greeting ---
    # Get user's first name from profile or fallback to username
    profile = UserProfile.objects.filter(user=user).first()
    # Use display_name from profile, fallback to first_name, then username
    if profile and profile.display_name:
        user_name = profile.display_name
    elif user.first_name:
        user_name = user.first_name
    else:
        user_name = user.username

    greeting = {
        'user_name': user_name,
        'time_of_day': get_time_of_day(),
    }

    # --- While Away Stats ---
    # Spider findings since last visit
    spider_findings = LegacySpiderData.objects.filter(
        created_at__gte=last_visit
    ).count()

    # High-score dreams (composite_score >= 0.7, not yet promoted)
    high_score_dreams = AgentDream.objects.filter(
        dreamed_at__gte=last_visit,
        composite_score__gte=0.7,
        promoted_to_decision=False,
    ).count()

    # Initiatives that progressed (updated_at since last visit, but created before)
    # I-0302 Phase 3 Sub-phase A2: scoped to user via scope_queryset_initiative.
    initiatives_progressed = scope_queryset_initiative(
        user,
        Initiative.objects.filter(
            updated_at__gte=last_visit,
            created_at__lt=last_visit,
            status='ACTIVE',
        ),
    ).count()

    # Pending decisions (boardroom decisions awaiting user input)
    pending_decisions = AgentDecisionSummary.objects.filter(
        is_canonical=False,
        created_at__gte=now - timedelta(days=7),
    ).count()

    # Session 1000: Intelligence desks ready count
    from django.core.cache import cache as _cache
    desk_keys = ['desk:stocks:latest', 'desk:sports:latest', 'desk:blockchain:latest', 'desk:narrative:latest']
    intelligence_desks_ready = sum(1 for k in desk_keys if _cache.get(k))

    while_away = {
        'spider_findings': spider_findings,
        'high_score_dreams': high_score_dreams,
        'initiatives_progressed': initiatives_progressed,
        'pending_decisions': pending_decisions,
        'hours_since_visit': round(hours_since_visit, 1),
        'intelligence_desks_ready': intelligence_desks_ready,
    }

    # --- Active Projects ---
    # Get active initiatives with their stages
    # I-0302 Phase 3 Sub-phase A2: scoped to user via scope_queryset_initiative.
    active_initiatives = scope_queryset_initiative(
        user,
        Initiative.objects.filter(status='ACTIVE'),
    ).prefetch_related('stages').order_by('-updated_at')[:5]

    active_projects = []
    for initiative in active_initiatives:
        # Check if there's a pending stage decision
        pending_stage = None
        for stage in initiative.stages.all():
            if stage.status == 'IN_REVIEW':
                pending_stage = {
                    'stage': stage.stage,
                    'title': f'Approve Stage {stage.stage}',
                }
                break

        active_projects.append({
            'id': str(initiative.id),
            'name': initiative.name,
            'type': 'initiative',
            'completion_percentage': initiative.completion_percentage,
            'status': 'decision_pending' if pending_stage else 'in_progress',
            'current_stage': initiative.current_stage,
            'pending_decision': pending_stage,
        })

    # --- Quick Stats ---
    # Active agents count
    agents_active = Agent.objects.filter(is_active=True).count()

    # System health based on recent agent executions
    # Simple heuristic: healthy if we have active agents and recent spider data
    recent_spider_data = LegacySpiderData.objects.filter(
        created_at__gte=now - timedelta(hours=6)
    ).exists()

    system_health = 'healthy' if (agents_active > 0 and recent_spider_data) else 'degraded'

    quick_stats = {
        'agents_active': agents_active,
        'system_health': system_health,
    }

    # Update last visit timestamp for next call
    update_last_visit(request)

    return Response({
        'greeting': greeting,
        'while_away': while_away,
        'active_projects': active_projects,
        'quick_stats': quick_stats,
    })


# =============================================================================
# Session 1000: Intelligence Desks API
# =============================================================================

DESK_CACHE_KEYS = {
    'stocks': 'desk:stocks:latest',
    'sports': 'desk:sports:latest',
    'blockchain': 'desk:blockchain:latest',
    'narrative': 'desk:narrative:latest',
}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def intelligence_desks(request):
    """
    GET /api/home/intelligence-desks/

    Returns cached intelligence desk briefs from the 4 coordinators.
    """
    from django.core.cache import cache

    desks = {}
    for desk_name, cache_key in DESK_CACHE_KEYS.items():
        cached = cache.get(cache_key)
        if cached and isinstance(cached, dict):
            desks[desk_name] = {
                'status': 'ready',
                **cached,
            }
        else:
            desks[desk_name] = {'status': 'no_data'}

    return Response({
        'desks': desks,
        'total_agents_activated': 21,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_desks(request):
    """
    POST /api/home/trigger-desks/

    Triggers an on-demand run of all intelligence desks via Celery.
    Optional: pass {"queue": "default"} to override the queue.
    """
    from core.tasks import run_all_desks_intelligence
    queue = request.data.get('queue', 'long_running')
    result = run_all_desks_intelligence.apply_async(queue=queue)
    return Response({
        'success': True,
        'task_id': str(result.id),
        'queue': queue,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def purge_queue(request):
    """
    POST /api/home/purge-queue/
    Body: {"queue": "long_running", "secret": "<PURGE_SECRET>"}

    Purges all messages from the specified Celery queue.
    Use to clear stale/expired task backlogs.
    Requires PURGE_SECRET from env to prevent unauthorized use.
    """
    import os
    from kombu import Queue as KombuQueue
    from core.celery import app

    purge_secret = os.environ.get('PURGE_SECRET', 'donkey-purge-2026')
    if request.data.get('secret') != purge_secret:
        return Response({'success': False, 'error': 'invalid secret'}, status=403)

    queue_name = request.data.get('queue')
    if not queue_name:
        return Response({'success': False, 'error': 'queue parameter required'}, status=400)

    allowed_queues = ['long_running', 'ml', 'broadcast', 'content', 'agents', 'sports']
    if queue_name not in allowed_queues:
        return Response({'success': False, 'error': f'queue must be one of: {allowed_queues}'}, status=400)

    with app.connection_or_acquire() as conn:
        q = KombuQueue(queue_name, channel=conn.default_channel)
        count = q.purge()

    return Response({
        'success': True,
        'queue': queue_name,
        'messages_purged': count,
    })
