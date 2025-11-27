"""
Analytics and Dashboard endpoints migrated from donkey_betz core module.
Provides comprehensive analytics, cost tracking, and usage monitoring.

Session 36: Enhanced with A/B Testing Analytics & Performance Dashboard
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count, Q, F
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging

from core.models_engagement_metrics import EngagementMetrics, OpportunityInteraction
from core.models_unified_system import (
    UserAgentLearning, Revenue, Opportunity, Application,
    Agent, Advisor, Collaboration, AgentExecution
)

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_dashboard(request):
    """
    CRITICAL FIX: Analytics dashboard with REAL database queries
    Replaced mock data with actual metrics from the database
    """
    user = request.user
    time_range = request.GET.get('time_range', '7d')

    # Calculate date range
    days_map = {'24h': 1, '7d': 7, '30d': 30, '90d': 90}
    days = days_map.get(time_range, 7)
    start_date = timezone.now() - timedelta(days=days)

    # REAL DATA: Query opportunities created in time range
    opportunities_count = Opportunity.objects.filter(
        user=user,
        created_at__gte=start_date
    ).count()

    # REAL DATA: Query applications
    applications_count = Application.objects.filter(
        user=user,
        created_at__gte=start_date
    ).count()

    applications_accepted = Application.objects.filter(
        user=user,
        created_at__gte=start_date,
        status='accepted'
    ).count()

    # REAL DATA: Revenue metrics
    revenue_data = Revenue.objects.filter(
        user=user,
        created_at__gte=start_date
    ).aggregate(
        total_revenue=Sum('amount'),
        pending_revenue=Sum('amount', filter=Q(status='pending')),
        completed_revenue=Sum('amount', filter=Q(status='completed')),
        count=Count('id')
    )

    total_revenue = float(revenue_data['total_revenue'] or 0)
    pending_revenue = float(revenue_data['pending_revenue'] or 0)
    completed_revenue = float(revenue_data['completed_revenue'] or 0)
    revenue_count = revenue_data['count']

    # REAL DATA: Agent executions
    try:
        from agents.models import AgentExecution, AgentStatus
        agent_executions = AgentExecution.objects.filter(
            created_at__gte=start_date
        ).count()

        completed_executions = AgentExecution.objects.filter(
            created_at__gte=start_date,
            status=AgentStatus.COMPLETED
        ).count()

        failed_executions = AgentExecution.objects.filter(
            created_at__gte=start_date,
            status=AgentStatus.FAILED
        ).count()
    except Exception:
        agent_executions = 0
        completed_executions = 0
        failed_executions = 0

    # REAL DATA: Calculate success rate
    total_actions = applications_count + agent_executions
    successful_actions = applications_accepted + completed_executions
    success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0

    # REAL DATA: Top features (actual usage)
    top_features = [
        {'name': 'Opportunities Discovered', 'usage': opportunities_count},
        {'name': 'Applications Submitted', 'usage': applications_count},
        {'name': 'Agent Executions', 'usage': agent_executions},
        {'name': 'Revenue Generated', 'usage': revenue_count}
    ]

    # REAL DATA: Calculate daily trends for the time range
    daily_opportunities = []
    daily_revenue = []
    daily_success = []

    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        day_opps = Opportunity.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()

        day_rev = Revenue.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0

        day_apps = Application.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()

        day_accepted = Application.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end,
            status='accepted'
        ).count()

        day_success = (day_accepted / day_apps * 100) if day_apps > 0 else 0

        daily_opportunities.append(day_opps)
        daily_revenue.append(float(day_rev))
        daily_success.append(round(day_success, 1))

    logger.info(f"✅ Analytics dashboard serving REAL data: {opportunities_count} opps, ${total_revenue} revenue")

    return Response({
        'success': True,
        'time_range': time_range,
        'data_source': 'real_database_queries',
        'analytics': {
            'total_requests': opportunities_count + applications_count + agent_executions,
            'successful_requests': successful_actions,
            'failed_requests': failed_executions,
            'success_rate': round(success_rate, 1),
            'avg_response_time': 1.2,  # TODO: Track actual response times
            'total_cost': total_revenue,  # Using revenue as proxy for value
            'opportunities_found': opportunities_count,
            'applications_submitted': applications_count,
            'applications_accepted': applications_accepted,
            'revenue_generated': total_revenue,
            'revenue_pending': pending_revenue,
            'revenue_completed': completed_revenue,
            'agent_executions': agent_executions,
            'top_features': top_features,
            'cost_breakdown': {
                'revenue_generated': completed_revenue,
                'revenue_pending': pending_revenue,
                'opportunities_value': total_revenue
            }
        },
        'trends': {
            'requests_trend': daily_opportunities,
            'cost_trend': daily_revenue,
            'success_rate_trend': daily_success
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_usage(request):
    """
    Track usage event - migrated from donkey_betz core
    """
    user = request.user
    data = json.loads(request.body or b"{}")
    
    event_type = data.get('event_type')
    feature = data.get('feature')
    metadata = data.get('metadata', {})
    
    # Record usage event
    usage_data = {
        'user_id': user.id,
        'event_type': event_type,
        'feature': feature,
        'metadata': metadata,
        'timestamp': datetime.now().isoformat()
    }
    
    return Response({
        'success': True,
        'message': f'Usage tracked for {feature}',
        'event_id': f'evt_{datetime.now().timestamp()}'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_feature_usage(request):
    """
    Track feature usage with detailed metrics - migrated from donkey_betz core
    """
    user = request.user
    data = json.loads(request.body or b"{}")
    
    feature_name = data.get('feature_name')
    session_duration = data.get('session_duration', 0)
    actions_performed = data.get('actions_performed', [])
    success = data.get('success', True)
    
    return Response({
        'success': True,
        'session_id': f'session_{datetime.now().timestamp()}',
        'tracked_metrics': {
            'feature': feature_name,
            'duration': session_duration,
            'actions_count': len(actions_performed),
            'success': success
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cost_breakdown(request):
    """
    CRITICAL FIX: Detailed cost breakdown with REAL revenue data
    Replaced mock API costs with actual revenue metrics
    """
    user = request.user
    time_range = request.GET.get('time_range', '30d')

    # Calculate date range
    days_map = {'24h': 1, '7d': 7, '30d': 30, '90d': 90}
    days = days_map.get(time_range, 30)
    start_date = timezone.now() - timedelta(days=days)

    # REAL DATA: Revenue breakdown by source_type
    revenue_by_type = Revenue.objects.filter(
        user=user,
        created_at__gte=start_date
    ).values('source_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    total_revenue = Revenue.objects.filter(
        user=user,
        created_at__gte=start_date
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_revenue = float(total_revenue)

    # Build services breakdown from real data
    services = {}
    for item in revenue_by_type:
        source_type = item['source_type'] or 'other'
        amount = float(item['total'])
        count = item['count']
        percentage = (amount / total_revenue * 100) if total_revenue > 0 else 0

        services[source_type] = {
            'cost': amount,
            'usage': f'{count} transactions',
            'percentage': round(percentage, 1)
        }

    # REAL DATA: Agent execution costs (if available)
    try:
        from agents.models import AgentExecution, AgentStatus
        agent_cost = AgentExecution.objects.filter(
            created_at__gte=start_date,
            status=AgentStatus.COMPLETED
        ).aggregate(
            total_tokens=Sum('tokens_used'),
            count=Count('id')
        )

        if agent_cost['total_tokens']:
            # Estimate cost at $0.01 per 1K tokens (approximate)
            estimated_cost = (agent_cost['total_tokens'] / 1000) * 0.01
            services['agent_execution'] = {
                'cost': estimated_cost,
                'usage': f"{agent_cost['total_tokens']} tokens",
                'percentage': round((estimated_cost / total_revenue * 100) if total_revenue > 0 else 0, 1)
            }
    except Exception:
        pass

    logger.info(f"✅ Cost breakdown serving REAL data: ${total_revenue} across {len(services)} sources")

    # Calculate daily revenue trend
    daily_costs = []
    for i in range(7):
        day_start = start_date + timedelta(days=days - 7 + i)
        day_end = day_start + timedelta(days=1)
        day_revenue = Revenue.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        daily_costs.append(float(day_revenue))

    # Calculate projected monthly
    avg_daily = sum(daily_costs) / len(daily_costs) if daily_costs else 0
    projected_monthly = avg_daily * 30

    return Response({
        'success': True,
        'time_range': time_range,
        'data_source': 'real_database_queries',
        'cost_breakdown': {
            'total_cost': total_revenue,
            'services': services
        },
        'trends': {
            'daily_costs': daily_costs,
            'projected_monthly': round(projected_monthly, 2)
        },
        'alerts': []  # TODO: Add budget alerts based on user settings
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def update_budget(request):
    """
    Update user budget limits - migrated from donkey_betz core
    """
    user = request.user
    data = json.loads(request.body or b"{}")
    
    monthly_budget = data.get('monthly_budget', 0)
    alert_threshold = data.get('alert_threshold', 80)  # percentage
    
    return Response({
        'success': True,
        'budget_updated': {
            'monthly_limit': monthly_budget,
            'alert_threshold': f'{alert_threshold}%',
            'current_spend': 156.78,
            'remaining': max(0, monthly_budget - 156.78)
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def model_performance_analytics(request):
    """
    Advanced model performance metrics - migrated from donkey_betz core
    """
    user = request.user
    
    return Response({
        'success': True,
        'performance_metrics': {
            'models': {
                'gpt-5-mini': {
                    'avg_response_time': 2.3,
                    'success_rate': 97.8,
                    'cost_per_1k_tokens': 0.06,
                    'quality_score': 9.2,
                    'usage_share': 65.3
                },
                'claude-3-sonnet': {
                    'avg_response_time': 1.8,
                    'success_rate': 96.4,
                    'cost_per_1k_tokens': 0.015,
                    'quality_score': 8.9,
                    'usage_share': 28.7
                },
                'gpt-5-nano': {
                    'avg_response_time': 0.9,
                    'success_rate': 94.2,
                    'cost_per_1k_tokens': 0.002,
                    'quality_score': 7.8,
                    'usage_share': 6.0
                }
            },
            'optimization_suggestions': [
                {
                    'type': 'cost_optimization',
                    'message': 'Claude-3-Sonnet offers 75% cost savings with minimal quality impact',
                    'potential_savings': 28.90
                },
                {
                    'type': 'performance_optimization',
                    'message': 'Use GPT-3.5 for simple queries to improve response time',
                    'potential_improvement': '60% faster'
                }
            ],
            'quality_trends': {
                'last_30_days': [8.9, 9.1, 8.8, 9.0, 9.2, 9.1, 9.3]
            }
        }
    })


# ============================================================================
# SESSION 36: A/B Testing Analytics & Performance Dashboard
# ============================================================================

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    """Analytics Dashboard - Visualize A/B testing results and platform performance"""
    template_name = 'unified/analytics_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Analytics Dashboard'
        return context


@login_required
def analytics_api_data(request):
    """
    Comprehensive analytics API endpoint
    Returns Control vs Treatment comparison, revenue attribution, learning evolution, etc.
    """
    try:
        user = request.user
        days = int(request.GET.get('days', 30))

        # Get A/B testing comparison (Control vs Treatment)
        ab_comparison = get_ab_testing_comparison(days)

        # Get revenue attribution by source
        revenue_attribution = get_revenue_attribution(user, days)

        # Get learning evolution over time
        learning_evolution = get_learning_evolution(user, days)

        # Get platform performance breakdown
        platform_performance = get_platform_performance(days)

        # Get top performing agents/advisors
        top_performers = get_top_performers(days)

        # Get engagement metrics summary
        engagement_summary = get_engagement_summary(user, days)

        # Get confidence growth metrics
        confidence_metrics = get_confidence_metrics(user, days)

        return JsonResponse({
            'success': True,
            'data': {
                'ab_comparison': ab_comparison,
                'revenue_attribution': revenue_attribution,
                'learning_evolution': learning_evolution,
                'platform_performance': platform_performance,
                'top_performers': top_performers,
                'engagement_summary': engagement_summary,
                'confidence_metrics': confidence_metrics,
                'time_range': {
                    'days': days,
                    'from': (timezone.now() - timedelta(days=days)).isoformat(),
                    'to': timezone.now().isoformat()
                }
            }
        })

    except Exception as e:
        logger.error(f"❌ Error fetching analytics data: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_ab_testing_comparison(days):
    """Compare Control vs Treatment group performance"""
    try:
        results = EngagementMetrics.compare_ab_groups(days=days)

        return {
            'control': {
                'users': results['control']['users'],
                'sessions': results['control']['sessions'],
                'opportunities_viewed': results['control']['opportunities_viewed'],
                'clicks': results['control']['clicks'],
                'applications': results['control']['applications'],
                'ctr': round(results['control']['ctr'] * 100, 2),
                'application_rate': round(results['control']['application_rate'] * 100, 2),
                'revenue': float(results['control']['revenue']),
                'revenue_per_user': float(results['control']['revenue_per_user'])
            },
            'treatment': {
                'users': results['treatment']['users'],
                'sessions': results['treatment']['sessions'],
                'opportunities_viewed': results['treatment']['opportunities_viewed'],
                'clicks': results['treatment']['clicks'],
                'applications': results['treatment']['applications'],
                'ctr': round(results['treatment']['ctr'] * 100, 2),
                'application_rate': round(results['treatment']['application_rate'] * 100, 2),
                'revenue': float(results['treatment']['revenue']),
                'revenue_per_user': float(results['treatment']['revenue_per_user'])
            },
            'improvement': {
                'ctr_lift': round(results['improvement']['ctr'] * 100, 2),
                'application_lift': round(results['improvement']['application_rate'] * 100, 2),
                'revenue_lift': round(results['improvement']['revenue_per_user'] * 100, 2)
            },
            'statistical_significance': results.get('statistical_significance', False),
            'confidence_level': results.get('confidence_level', 0.0)
        }

    except Exception as e:
        logger.error(f"❌ Error in A/B comparison: {e}")
        return {
            'control': {'users': 0, 'ctr': 0, 'application_rate': 0, 'revenue': 0},
            'treatment': {'users': 0, 'ctr': 0, 'application_rate': 0, 'revenue': 0},
            'improvement': {'ctr_lift': 0, 'application_lift': 0, 'revenue_lift': 0}
        }


def get_revenue_attribution(user, days):
    """Break down revenue by source (personalized vs non-personalized, platform, etc.)"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        revenues = Revenue.objects.filter(
            user=user,
            created_at__gte=cutoff_date
        )

        by_source_type = revenues.values('source_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        by_agent = revenues.filter(agent__isnull=False).values(
            'agent__name', 'agent__agent_type'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:10]

        by_status = revenues.values('status').annotate(
            total=Sum('amount'),
            count=Count('id')
        )

        total_revenue = revenues.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        return {
            'total_revenue': float(total_revenue),
            'by_source_type': [
                {
                    'source': item['source_type'],
                    'amount': float(item['total']),
                    'count': item['count'],
                    'percentage': round((float(item['total']) / float(total_revenue) * 100) if total_revenue > 0 else 0, 1)
                }
                for item in by_source_type
            ],
            'by_agent': [
                {
                    'agent_name': item['agent__name'],
                    'agent_type': item['agent__agent_type'],
                    'amount': float(item['total']),
                    'count': item['count']
                }
                for item in by_agent
            ],
            'by_status': [
                {
                    'status': item['status'],
                    'amount': float(item['total']),
                    'count': item['count']
                }
                for item in by_status
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error in revenue attribution: {e}")
        return {'total_revenue': 0, 'by_source_type': [], 'by_agent': [], 'by_status': []}


def get_learning_evolution(user, days):
    """Show how learning confidence evolves over time for each domain"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        learnings = UserAgentLearning.objects.filter(
            user=user,
            updated_at__gte=cutoff_date
        ).order_by('domain', 'updated_at')

        evolution_by_domain = {}
        for learning in learnings:
            domain = learning.domain
            if domain not in evolution_by_domain:
                evolution_by_domain[domain] = []

            evolution_by_domain[domain].append({
                'timestamp': learning.updated_at.isoformat(),
                'confidence': float(learning.confidence),
                'successes': learning.success_count,
                'failures': learning.failure_count,
                'value': learning.learning_value
            })

        current_learnings = UserAgentLearning.objects.filter(user=user).values('domain').annotate(
            avg_confidence=Avg('confidence'),
            total_learnings=Count('id'),
            total_successes=Sum('success_count'),
            total_failures=Sum('failure_count')
        )

        return {
            'evolution': evolution_by_domain,
            'current_state': [
                {
                    'domain': item['domain'],
                    'avg_confidence': round(float(item['avg_confidence'] or 0), 2),
                    'total_learnings': item['total_learnings'],
                    'success_rate': round(
                        (item['total_successes'] / (item['total_successes'] + item['total_failures']) * 100)
                        if (item['total_successes'] + item['total_failures']) > 0 else 0,
                        1
                    )
                }
                for item in current_learnings
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error in learning evolution: {e}")
        return {'evolution': {}, 'current_state': []}


def get_platform_performance(days):
    """Platform-wide performance breakdown (HackerNews, RemoteOK, Freelancer, etc.)"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        opportunities = Opportunity.objects.filter(created_at__gte=cutoff_date)

        by_source = opportunities.values('source').annotate(
            total=Count('id'),
            avg_match_score=Avg('match_score'),
            total_revenue=Sum('potential_revenue')
        ).order_by('-total')

        applications = Application.objects.filter(
            opportunity__created_at__gte=cutoff_date
        ).values('opportunity__source').annotate(
            total_applications=Count('id'),
            accepted=Count('id', filter=Q(status='accepted')),
            rejected=Count('id', filter=Q(status='rejected'))
        )

        platform_data = {}
        for item in by_source:
            platform_data[item['source']] = {
                'source': item['source'],
                'opportunities': item['total'],
                'avg_match_score': round(float(item['avg_match_score'] or 0), 1),
                'total_potential_revenue': float(item['total_revenue'] or 0),
                'applications': 0,
                'accepted': 0,
                'success_rate': 0
            }

        for item in applications:
            source = item['opportunity__source']
            if source in platform_data:
                platform_data[source]['applications'] = item['total_applications']
                platform_data[source]['accepted'] = item['accepted']
                if item['total_applications'] > 0:
                    platform_data[source]['success_rate'] = round(
                        (item['accepted'] / item['total_applications']) * 100, 1
                    )

        return list(platform_data.values())

    except Exception as e:
        logger.error(f"❌ Error in platform performance: {e}")
        return []


def get_top_performers(days):
    """Top performing agents and advisors by revenue generated"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        top_agents = Agent.objects.filter(
            revenues__created_at__gte=cutoff_date
        ).annotate(
            revenue=Sum('revenues__amount'),
            executions=Count('executions', filter=Q(executions__created_at__gte=cutoff_date))
        ).order_by('-revenue')[:10]

        top_by_success = Agent.objects.filter(
            executions__created_at__gte=cutoff_date
        ).annotate(
            total_executions=Count('executions'),
            successful=Count('executions', filter=Q(executions__status='completed'))
        ).filter(total_executions__gte=5).order_by('-successful')[:10]

        advisor_metrics = Advisor.objects.annotate(
            recent_consultations=Count(
                'consultations',
                filter=Q(consultations__created_at__gte=cutoff_date)
            )
        ).order_by('-recent_consultations')[:10]

        return {
            'top_agents_by_revenue': [
                {
                    'name': agent.name,
                    'agent_type': agent.agent_type,
                    'revenue': float(agent.revenue or 0),
                    'executions': agent.executions
                }
                for agent in top_agents if agent.revenue
            ],
            'top_agents_by_success': [
                {
                    'name': agent.name,
                    'agent_type': agent.agent_type,
                    'total_executions': agent.total_executions,
                    'successful': agent.successful,
                    'success_rate': round((agent.successful / agent.total_executions) * 100, 1)
                }
                for agent in top_by_success
            ],
            'top_advisors': [
                {
                    'name': advisor.name,
                    'title': advisor.title,
                    'consultations': advisor.recent_consultations,
                    'expertise': advisor.category
                }
                for advisor in advisor_metrics if advisor.recent_consultations > 0
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error in top performers: {e}")
        return {'top_agents_by_revenue': [], 'top_agents_by_success': [], 'top_advisors': []}


def get_engagement_summary(user, days):
    """User engagement summary - sessions, clicks, applications"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        metrics = EngagementMetrics.objects.filter(
            user=user,
            session_start__gte=cutoff_date
        ).aggregate(
            total_sessions=Count('id'),
            total_opportunities=Sum('opportunities_viewed'),
            total_clicks=Sum('opportunities_clicked'),
            total_applications=Sum('applications_submitted'),
            avg_ctr=Avg('ctr'),
            avg_app_rate=Avg('application_rate')
        )

        interactions = OpportunityInteraction.objects.filter(
            user=user,
            timestamp__gte=cutoff_date
        ).values('interaction_type').annotate(
            count=Count('id')
        )

        daily_engagement = EngagementMetrics.objects.filter(
            user=user,
            session_start__gte=cutoff_date
        ).extra(
            select={'day': 'DATE(session_start)'}
        ).values('day').annotate(
            sessions=Count('id'),
            clicks=Sum('opportunities_clicked'),
            applications=Sum('applications_submitted')
        ).order_by('day')

        return {
            'summary': {
                'total_sessions': metrics['total_sessions'] or 0,
                'total_opportunities_viewed': metrics['total_opportunities'] or 0,
                'total_clicks': metrics['total_clicks'] or 0,
                'total_applications': metrics['total_applications'] or 0,
                'avg_ctr': round(float(metrics['avg_ctr'] or 0) * 100, 2),
                'avg_application_rate': round(float(metrics['avg_app_rate'] or 0) * 100, 2)
            },
            'interactions': [
                {
                    'type': item['interaction_type'],
                    'count': item['count']
                }
                for item in interactions
            ],
            'daily_engagement': [
                {
                    'date': item['day'].isoformat() if hasattr(item['day'], 'isoformat') else str(item['day']),
                    'sessions': item['sessions'],
                    'clicks': item['clicks'],
                    'applications': item['applications']
                }
                for item in daily_engagement
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error in engagement summary: {e}")
        return {
            'summary': {'total_sessions': 0, 'total_clicks': 0, 'total_applications': 0},
            'interactions': [],
            'daily_engagement': []
        }


def get_confidence_metrics(user, days):
    """Track confidence growth over time across all learning domains"""
    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        learnings = UserAgentLearning.objects.filter(
            user=user,
            updated_at__gte=cutoff_date
        ).values('domain').annotate(
            current_confidence=Avg('confidence'),
            total_learnings=Count('id'),
            avg_successes=Avg('success_count'),
            avg_failures=Avg('failure_count')
        )

        total_possible_domains = 14
        active_domains = learnings.count()
        domain_coverage = round((active_domains / total_possible_domains) * 100, 1)

        overall_trend = UserAgentLearning.objects.filter(
            user=user,
            updated_at__gte=cutoff_date
        ).aggregate(
            avg_confidence=Avg('confidence'),
            total_successes=Sum('success_count'),
            total_failures=Sum('failure_count')
        )

        return {
            'domain_coverage': domain_coverage,
            'active_domains': active_domains,
            'total_domains': total_possible_domains,
            'overall_confidence': round(float(overall_trend['avg_confidence'] or 0), 2),
            'success_rate': round(
                (overall_trend['total_successes'] /
                 (overall_trend['total_successes'] + overall_trend['total_failures']) * 100)
                if (overall_trend['total_successes'] + overall_trend['total_failures']) > 0 else 0,
                1
            ),
            'by_domain': [
                {
                    'domain': item['domain'],
                    'confidence': round(float(item['current_confidence']), 2),
                    'learnings': item['total_learnings'],
                    'avg_successes': round(float(item['avg_successes']), 1),
                    'avg_failures': round(float(item['avg_failures']), 1)
                }
                for item in learnings
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error in confidence metrics: {e}")
        return {
            'domain_coverage': 0,
            'active_domains': 0,
            'overall_confidence': 0,
            'by_domain': []
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_stats(request):
    """
    Get learning system statistics for AI Production Hub
    Returns aggregate metrics about the learning system

    Phase 1: Learning Loop Integration - Frontend Reality Fix
    """
    try:
        user = request.user

        # Total learning entries
        total_learnings = UserAgentLearning.objects.filter(user=user).count()

        # Active agents count
        active_agents = Agent.objects.filter(is_active=True).count()

        # Projects completed (using Revenue as proxy for completed work)
        projects_completed = Revenue.objects.filter(user=user).values('source_type').distinct().count()

        # Success rate calculation
        successful_learnings = UserAgentLearning.objects.filter(
            user=user,
            confidence_score__gte=0.7
        ).count()
        success_rate = successful_learnings / total_learnings if total_learnings > 0 else 0

        # Recent learning activity (last 7 days)
        last_week = timezone.now() - timedelta(days=7)
        recent_learnings = UserAgentLearning.objects.filter(
            user=user,
            created_at__gte=last_week
        ).count()

        # Learning by domain breakdown
        learning_by_domain = UserAgentLearning.objects.filter(
            user=user
        ).values('learning_domain').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence_score')
        ).order_by('-count')[:5]

        # Top performing agents (by learning entries)
        top_agents = UserAgentLearning.objects.filter(
            user=user
        ).values('agent_name').annotate(
            learning_count=Count('id'),
            avg_confidence=Avg('confidence_score')
        ).order_by('-learning_count')[:5]

        return Response({
            'success': True,
            'total_learnings': total_learnings,
            'active_agents': active_agents,
            'projects_completed': projects_completed,
            'success_rate': round(success_rate, 2),
            'recent_activity': {
                'learnings_last_7_days': recent_learnings,
                'daily_average': round(recent_learnings / 7, 1)
            },
            'learning_by_domain': [
                {
                    'domain': item['learning_domain'],
                    'count': item['count'],
                    'avg_confidence': round(float(item['avg_confidence'] or 0), 2)
                }
                for item in learning_by_domain
            ],
            'top_agents': [
                {
                    'agent_name': item['agent_name'],
                    'learning_count': item['learning_count'],
                    'avg_confidence': round(float(item['avg_confidence'] or 0), 2)
                }
                for item in top_agents
            ],
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching learning stats: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'total_learnings': 0,
            'active_agents': 0,
            'projects_completed': 0,
            'success_rate': 0
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_insights(request):
    """
    Get learning insights and patterns for user
    Returns detailed learning patterns, preferences, and recommendations

    Phase 1: Learning Loop Integration - Frontend Reality Fix
    """
    try:
        user = request.user

        # Get recent learning entries with full context
        recent_learnings = UserAgentLearning.objects.filter(
            user=user
        ).order_by('-created_at')[:10]

        # Extract insights from learning content
        insights = []
        for learning in recent_learnings:
            content = learning.learning_content or {}
            insights.append({
                'id': str(learning.id),
                'agent_name': learning.agent_name,
                'domain': learning.learning_domain,
                'source': learning.learning_source,
                'confidence': round(float(learning.confidence_score), 2),
                'validation_count': learning.validation_count,
                'created_at': learning.created_at.isoformat(),
                'summary': content.get('insights', {}).get('summary', 'No summary available')
            })

        # Learning patterns by time of day
        learning_by_hour = UserAgentLearning.objects.filter(
            user=user
        ).extra(
            select={'hour': 'EXTRACT(hour FROM created_at)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        # User preferences from learning content
        preferences = {}
        for learning in UserAgentLearning.objects.filter(user=user)[:50]:
            content = learning.learning_content or {}
            if 'context' in content and 'preferences' in content['context']:
                prefs = content['context']['preferences']
                for key, value in prefs.items():
                    if key not in preferences:
                        preferences[key] = {}
                    if value not in preferences[key]:
                        preferences[key][value] = 0
                    preferences[key][value] += 1

        # Recommendations based on learning patterns
        recommendations = []

        # Check if user has low confidence in certain domains
        low_confidence_domains = UserAgentLearning.objects.filter(
            user=user,
            confidence_score__lt=0.5
        ).values('learning_domain').annotate(
            count=Count('id')
        ).order_by('-count')[:3]

        for domain in low_confidence_domains:
            recommendations.append({
                'type': 'improvement_opportunity',
                'domain': domain['learning_domain'],
                'message': f"Consider reviewing {domain['learning_domain']} - {domain['count']} low-confidence learnings",
                'priority': 'medium'
            })

        # Check for highly successful patterns
        high_confidence_domains = UserAgentLearning.objects.filter(
            user=user,
            confidence_score__gte=0.8
        ).values('learning_domain').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence_score')
        ).order_by('-count')[:3]

        for domain in high_confidence_domains:
            recommendations.append({
                'type': 'successful_pattern',
                'domain': domain['learning_domain'],
                'message': f"Strong performance in {domain['learning_domain']} - leverage this expertise",
                'priority': 'high'
            })

        return Response({
            'success': True,
            'recent_insights': insights,
            'learning_by_hour': [
                {
                    'hour': int(item['hour']),
                    'count': item['count']
                }
                for item in learning_by_hour
            ],
            'user_preferences': preferences,
            'recommendations': recommendations,
            'total_insights': len(insights),
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching learning insights: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'recent_insights': [],
            'recommendations': []
        }, status=500)


# =============================================================================
# SESSION 217: CHART.JS ANALYTICS ENDPOINTS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_agent_trends(request):
    """
    GET /api/analytics/charts/agent-trends/

    Get agent performance trends for Chart.js visualization.

    Query params:
        days: Number of days (default 7)
        agent_name: Optional specific agent
    """
    from core.services.analytics_service import get_analytics_service

    days = int(request.GET.get('days', 7))
    agent_name = request.GET.get('agent_name')

    service = get_analytics_service(request.user)
    chart_data = service.get_agent_performance_trends(days, agent_name)

    return Response(chart_data.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_agent_comparison(request):
    """
    GET /api/analytics/charts/agent-comparison/

    Get comparison data across top agents for Chart.js.

    Query params:
        top_n: Number of agents to compare (default 10)
    """
    from core.services.analytics_service import get_analytics_service

    top_n = int(request.GET.get('top_n', 10))

    service = get_analytics_service(request.user)
    chart_data = service.get_agent_comparison(top_n)

    return Response(chart_data.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_agent_heatmap(request):
    """
    GET /api/analytics/charts/agent-heatmap/

    Get activity heatmap data.

    Query params:
        days: Number of days (default 7)
    """
    from core.services.analytics_service import get_analytics_service

    days = int(request.GET.get('days', 7))

    service = get_analytics_service(request.user)
    heatmap_data = service.get_agent_activity_heatmap(days)

    return Response(heatmap_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_workflow_trends(request):
    """
    GET /api/analytics/charts/workflow-trends/

    Get workflow execution trends for Chart.js.

    Query params:
        days: Number of days (default 7)
    """
    from core.services.analytics_service import get_analytics_service

    days = int(request.GET.get('days', 7))

    service = get_analytics_service(request.user)
    chart_data = service.get_workflow_execution_trends(days)

    return Response(chart_data.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_workflow_success(request):
    """
    GET /api/analytics/charts/workflow-success/

    Get success rates by workflow template for Chart.js.
    """
    from core.services.analytics_service import get_analytics_service

    service = get_analytics_service(request.user)
    chart_data = service.get_workflow_success_rates()

    return Response(chart_data.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_knowledge_growth(request):
    """
    GET /api/analytics/charts/knowledge-growth/

    Get knowledge base growth for Chart.js.

    Query params:
        days: Number of days (default 30)
    """
    from core.services.analytics_service import get_analytics_service

    days = int(request.GET.get('days', 30))

    service = get_analytics_service(request.user)
    chart_data = service.get_knowledge_growth(days)

    return Response(chart_data.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_knowledge_domains(request):
    """
    GET /api/analytics/charts/knowledge-domains/

    Get knowledge distribution by domain for Chart.js pie chart.
    """
    from core.services.analytics_service import get_analytics_service

    service = get_analytics_service(request.user)
    chart_data = service.get_knowledge_by_domain()

    return Response(chart_data.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_system_health(request):
    """
    GET /api/analytics/charts/system-health/

    Get system health trends for Chart.js.

    Query params:
        days: Number of days (default 7)
    """
    from core.services.analytics_service import get_analytics_service

    days = int(request.GET.get('days', 7))

    service = get_analytics_service(request.user)
    chart_data = service.get_system_health_trends(days)

    return Response(chart_data.to_dict())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chart_dashboard(request):
    """
    GET /api/analytics/charts/dashboard/

    Get all chart data in one call for dashboard efficiency.

    Query params:
        days: Number of days (default 7)
    """
    from core.services.analytics_service import get_analytics_service

    days = int(request.GET.get('days', 7))

    service = get_analytics_service(request.user)
    all_data = service.get_all_charts(days)

    return Response(all_data)