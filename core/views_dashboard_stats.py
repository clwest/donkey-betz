"""
Dashboard Statistics API - The Heart of the Unified System
This aggregates REAL data from all 149 agents, 25 advisors, and user activities
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import (
    Agent, AgentExecution, UserProfile,
    Revenue, Opportunity, Application,
    SpiderData, Advisor, Collaboration
)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@vary_on_cookie
@cache_page(30)  # 30s — high-traffic dashboard endpoint (19 queries)
def dashboard_stats(request):
    """
    Get real-time dashboard statistics for the unified command center.
    This is where ALL the data flows together!
    """
    user = request.user

    # Get real revenue data
    total_revenue = Revenue.objects.filter(
        user=user,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Get active opportunities from Income Builder
    active_opportunities = Opportunity.objects.filter(
        Q(status='active') | Q(status='pending'),
        user=user
    ).count()

    # Calculate success rate from applications
    total_applications = Application.objects.filter(user=user).count()
    successful_applications = Application.objects.filter(
        user=user,
        status='accepted'
    ).count()

    success_rate = 0
    if total_applications > 0:
        success_rate = int((successful_applications / total_applications) * 100)

    # Get active agents count
    active_agents = Agent.objects.filter(
        user_assignments=user,
        is_active=True
    ).count()

    # Get advisor insights count
    active_advisors = Advisor.objects.filter(
        is_active=True
    ).count()

    # Get spider network data points
    spider_data_points = SpiderData.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()

    # Get recent collaborations
    recent_collaborations = Collaboration.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    # Get agent execution stats
    agent_executions_24h = AgentExecution.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()

    # Get opportunities by category
    opportunities_by_type = Opportunity.objects.filter(
        user=user,
        status='active'
    ).values('opportunity_type').annotate(
        count=Count('id'),
        potential_revenue=Sum('potential_revenue')
    )

    # Get revenue trend (last 7 days)
    revenue_trend = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        day_revenue = Revenue.objects.filter(
            user=user,
            created_at__date=date,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        revenue_trend.append({
            'date': date.isoformat(),
            'amount': float(day_revenue)
        })
    revenue_trend.reverse()

    # Get top performing agents
    top_agents = Agent.objects.filter(
        user_assignments=user,
        is_active=True
    ).annotate(
        execution_count=Count('executions'),
        success_count=Count('executions', filter=Q(executions__status='completed'))
    ).order_by('-execution_count')[:5]

    top_agents_data = [
        {
            'name': agent.name,
            'type': agent.agent_type,
            'executions': agent.execution_count,
            'success_rate': (agent.success_count / agent.execution_count * 100) if agent.execution_count > 0 else 0
        }
        for agent in top_agents
    ]

    # Calculate AI token usage and costs
    token_usage_24h = AgentExecution.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).aggregate(
        total_tokens=Sum('tokens_used'),
        total_cost=Sum('cost')
    )

    # Get user profile completion
    profile = UserProfile.objects.filter(user=user).first()
    profile_completion = 0
    if profile:
        completed_fields = 0
        total_fields = 10  # Adjust based on your profile fields
        if profile.skills: completed_fields += 1
        if profile.experience_years: completed_fields += 1
        if profile.current_role: completed_fields += 1
        if profile.industries: completed_fields += 1
        if profile.resume_id: completed_fields += 1
        if profile.linkedin_url: completed_fields += 1
        if profile.github_url: completed_fields += 1
        if profile.portfolio_url: completed_fields += 1
        if profile.bio: completed_fields += 1
        if profile.location: completed_fields += 1
        profile_completion = int((completed_fields / total_fields) * 100)

    # Build the response
    stats = {
        # Core metrics for summary bar
        'total_revenue': float(total_revenue),
        'active_opportunities': active_opportunities,
        'success_rate': success_rate,
        'active_agents': active_agents,

        # Extended metrics
        'active_advisors': active_advisors,
        'spider_data_points': spider_data_points,
        'recent_collaborations': recent_collaborations,
        'agent_executions_24h': agent_executions_24h,
        'profile_completion': profile_completion,

        # Detailed breakdowns
        'opportunities_by_type': list(opportunities_by_type),
        'revenue_trend': revenue_trend,
        'top_agents': top_agents_data,

        # AI usage metrics
        'token_usage_24h': token_usage_24h['total_tokens'] or 0,
        'ai_cost_24h': float(token_usage_24h['total_cost'] or 0),

        # System health
        'system_status': 'operational',
        'last_sync': timezone.now().isoformat(),

        # User context
        'user': {
            'username': user.username,
            'email': user.email,
            'is_premium': getattr(user, 'is_premium', False),
            'joined_date': user.date_joined.isoformat() if hasattr(user, 'date_joined') else None
        }
    }

    return Response(stats)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_agent_activity(request):
    """
    Get real-time agent activity for Neural Orchestra visualization
    Session 780: Fixed field names, timezone issues, and auth decorators
    """
    user = request.user
    now = timezone.now()

    # Get all active agents assigned to this user
    active_agents = Agent.objects.filter(
        is_active=True,
        user_assignments=user
    ).prefetch_related('executions')

    agent_data = []
    for agent in active_agents:
        # Get current in-progress execution
        current_execution = agent.executions.filter(
            status='in_progress'
        ).first()

        # Get recent collaborations where this agent participated
        # Session 780: Fixed - collaborations uses collaborating_agents M2M, not collaborator FK
        recent_collabs = Collaboration.objects.filter(
            collaborating_agents=agent,
            created_at__gte=now - timedelta(minutes=5)
        ).select_related('lead_agent')

        collab_names = [c.lead_agent.name for c in recent_collabs if c.lead_agent != agent]

        agent_data.append({
            'id': agent.id,
            'name': agent.name,
            'type': agent.agent_type,
            'status': 'active' if current_execution else 'idle',
            'current_task': current_execution.task if current_execution else None,
            'collaborating_with': collab_names,
            'last_active': agent.last_active.isoformat() if agent.last_active else None,
            'metrics': {
                'tasks_completed': agent.executions.filter(status='completed').count(),
                'success_rate': getattr(agent, 'success_rate', 0) or 0,
                'specialization': getattr(agent, 'specialization', None) or agent.agent_type
            }
        })

    return Response({
        'agents': agent_data,
        'total_agents': len(agent_data),
        'timestamp': now.isoformat()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def advisor_insights(request):
    """
    Get insights and recommendations from legendary advisors
    Session 780: Fixed timezone issues, correct model, and auth decorators
    """
    from core.models_unified_system import AdvisorInsight

    user = request.user
    now = timezone.now()

    # Get active advisors
    advisors = Advisor.objects.filter(is_active=True)

    insights = []
    for advisor in advisors:
        # Session 780: Use AdvisorInsight model (has related_name='insights' on Advisor)
        try:
            recent_insights = AdvisorInsight.objects.filter(
                advisor=advisor,
                user=user,
                created_at__gte=now - timedelta(days=1)
            ).order_by('-created_at')[:3]

            for insight in recent_insights:
                insights.append({
                    'advisor': {
                        'name': advisor.name,
                        'title': getattr(advisor, 'title', advisor.expertise),
                        'expertise': advisor.expertise,
                        'avatar': getattr(advisor, 'avatar_url', None)
                    },
                    'insight': insight.content,
                    'confidence': getattr(insight, 'confidence', 0.8),
                    'category': getattr(insight, 'category', 'general'),
                    'actionable': getattr(insight, 'is_actionable', True),
                    'created_at': insight.created_at.isoformat()
                })
        except Exception:
            # If there's any issue with this advisor, skip it
            continue

    return Response({
        'insights': insights,
        'total_advisors': advisors.count(),
        'timestamp': now.isoformat()
    })


# =============================================================================
# Session 459: Personalized Dashboard Summary + "While You Were Away"
# =============================================================================

@require_http_methods(["GET"])
def dashboard_summary(request):
    """
    Get personalized greeting data and "While You Were Away" summary.
    This powers the Assistant Tab landing page personalization.

    Returns:
    - user_name: First name or username for personalized greeting
    - last_visit: When user last visited (for "while you were away" calculation)
    - while_away: Stats on activity since last visit
    """
    from django.utils import timezone
    from content.models import ImageHistory

    # Allow unauthenticated users (will get generic greeting)
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    user = request.user

    # Get user's display name
    user_name = user.first_name or user.username or 'there'

    # Try to get last visit time from session or profile
    last_visit = None
    try:
        # Check session for last visit
        last_visit_str = request.session.get('last_dashboard_visit')
        if last_visit_str:
            last_visit = datetime.fromisoformat(last_visit_str)
        else:
            # Default to 24 hours ago for first visit
            last_visit = timezone.now() - timedelta(hours=24)
    except Exception:
        last_visit = timezone.now() - timedelta(hours=24)

    # Update last visit timestamp
    request.session['last_dashboard_visit'] = timezone.now().isoformat()

    # Calculate "While You Were Away" stats
    while_away = {
        'new_spider_data': 0,
        'agent_dreams': 0,
        'agent_conversations': 0,
        'new_opportunities': 0,
        'images_created': 0,
    }

    try:
        # Spider data since last visit
        while_away['new_spider_data'] = SpiderData.objects.filter(
            created_at__gte=last_visit
        ).count()
    except Exception:
        pass

    try:
        # Agent dreams since last visit
        from core.models_unified_system import AgentDream
        while_away['agent_dreams'] = AgentDream.objects.filter(
            created_at__gte=last_visit
        ).count()
    except Exception:
        pass

    try:
        # Agent conversations since last visit
        from core.models_unified_system import AgentConversation
        while_away['agent_conversations'] = AgentConversation.objects.filter(
            created_at__gte=last_visit
        ).count()
    except Exception:
        pass

    try:
        # New opportunities since last visit
        while_away['new_opportunities'] = Opportunity.objects.filter(
            created_at__gte=last_visit
        ).count()
    except Exception:
        pass

    try:
        # Images created by this user since last visit
        while_away['images_created'] = ImageHistory.objects.filter(
            user=user,
            created_at__gte=last_visit
        ).count()
    except Exception:
        pass

    return JsonResponse({
        'success': True,
        'user_name': user_name,
        'last_visit': last_visit.isoformat() if last_visit else None,
        'while_away': while_away,
    })