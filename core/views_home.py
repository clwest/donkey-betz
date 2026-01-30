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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Agent, SpiderData, UserProfile
from core.models_document_registry import Initiative
from core.models_unified_system import AgentDream, AgentDecisionSummary


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
    spider_findings = SpiderData.objects.filter(
        created_at__gte=last_visit
    ).count()

    # High-score dreams (composite_score >= 0.7, not yet promoted)
    high_score_dreams = AgentDream.objects.filter(
        dreamed_at__gte=last_visit,
        composite_score__gte=0.7,
        promoted_to_decision=False,
    ).count()

    # Initiatives that progressed (updated_at since last visit, but created before)
    initiatives_progressed = Initiative.objects.filter(
        updated_at__gte=last_visit,
        created_at__lt=last_visit,
        status='ACTIVE',
    ).count()

    # Pending decisions (boardroom decisions awaiting user input)
    pending_decisions = AgentDecisionSummary.objects.filter(
        is_canonical=False,
        created_at__gte=now - timedelta(days=7),
    ).count()

    while_away = {
        'spider_findings': spider_findings,
        'high_score_dreams': high_score_dreams,
        'initiatives_progressed': initiatives_progressed,
        'pending_decisions': pending_decisions,
        'hours_since_visit': round(hours_since_visit, 1),
    }

    # --- Active Projects ---
    # Get active initiatives with their stages
    active_initiatives = Initiative.objects.filter(
        status='ACTIVE'
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
    recent_spider_data = SpiderData.objects.filter(
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
