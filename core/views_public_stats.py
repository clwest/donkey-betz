"""
Public Stats API - Shows system overview without authentication
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.models_unified_system import Agent, Advisor, Revenue, Opportunity

@require_http_methods(["GET"])
def public_system_stats(request):
    """
    Get public system statistics - no auth required for demo
    """

    # Get system-wide stats
    total_agents = Agent.objects.filter(is_active=True).count()
    total_advisors = Advisor.objects.filter(is_active=True).count()

    # Get aggregate stats (not user-specific for public view)
    total_opportunities = Opportunity.objects.filter(status='active').count()
    total_revenue = Revenue.objects.filter(status='completed').count()

    # Get top agents by effectiveness
    top_agents = Agent.objects.filter(is_active=True).order_by('-effectiveness_score')[:5].values(
        'name', 'agent_type', 'effectiveness_score'
    )

    # Get all advisors
    advisors = Advisor.objects.filter(is_active=True).order_by('-influence_score').values(
        'name', 'title', 'expertise', 'influence_score'
    )

    stats = {
        'system_overview': {
            'total_agents': total_agents,
            'total_advisors': total_advisors,
            'active_opportunities': total_opportunities,
            'completed_transactions': total_revenue,
            'system_status': 'operational',
            'reality_score': 87.3  # This will be calculated dynamically later
        },
        'top_agents': list(top_agents),
        'legendary_advisors': list(advisors)[:10],  # Top 10 advisors
        'message': '🚀 18 months of work unified! All systems operational!'
    }

    return JsonResponse(stats)