"""
Session 230: Revenue Analytics for Smart Distribution
======================================================

This module implements comprehensive revenue tracking and analytics:
- Platform-specific revenue tracking
- Best performing platform analysis
- ROI calculations
- Revenue forecasting
- Performance comparisons
"""

import json
import logging
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import TruncDate, TruncMonth

from core.models_unified_system import (
    DistributionPlatform,
    UserPlatformAccount,
    ContentDistribution,
    OpportunityRevenue,
)
from core.api_responses import api_success, api_error

logger = logging.getLogger(__name__)


# =============================================================================
# Revenue Dashboard
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def revenue_dashboard(request):
    """
    GET /api/distribution/revenue/dashboard/

    Get comprehensive revenue dashboard data.
    """
    # Session 688: Handle anonymous users - return empty dashboard data
    if not request.user.is_authenticated:
        return api_success({
            'distribution': {
                'total_revenue': 0,
                'total_sales': 0,
                'total_views': 0,
                'total_downloads': 0,
                'total_listings': 0,
            },
            'opportunities': {
                'total_amount': 0,
                'total_net': 0,
                'total_fees': 0,
                'count': 0,
            },
            'platform_breakdown': [],
            'daily_trend': [],
            'top_performers': [],
            'best_platform': None,
        })

    # Time range
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    # Get distribution revenue
    distribution_revenue = ContentDistribution.objects.filter(
        user=request.user,
        status='live',
    ).aggregate(
        total_revenue=Sum('revenue'),
        total_sales=Sum('sales'),
        total_views=Sum('views'),
        total_downloads=Sum('downloads'),
        total_listings=Count('id'),
    )

    # Get opportunity revenue
    opportunity_revenue = OpportunityRevenue.objects.filter(
        user=request.user,
        sale_date__gte=since,
        status='received',
    ).aggregate(
        total_amount=Sum('amount'),
        total_net=Sum('net_amount'),
        total_fees=Sum('platform_fee'),
        count=Count('id'),
    )

    # Revenue by platform
    platform_breakdown = ContentDistribution.objects.filter(
        user=request.user,
        status='live',
        revenue__gt=0,
    ).values(
        'platform_account__platform__name'
    ).annotate(
        total_revenue=Sum('revenue'),
        total_sales=Sum('sales'),
        item_count=Count('id'),
        avg_price=Avg('price'),
    ).order_by('-total_revenue')

    # Daily revenue trend
    daily_trend = ContentDistribution.objects.filter(
        user=request.user,
        listed_at__gte=since,
    ).annotate(
        date=TruncDate('listed_at')
    ).values('date').annotate(
        revenue=Sum('revenue'),
        sales=Sum('sales'),
        new_listings=Count('id'),
    ).order_by('date')

    # Top performing content
    top_content = ContentDistribution.objects.filter(
        user=request.user,
        status='live',
    ).order_by('-revenue')[:10].values(
        'id', 'title', 'revenue', 'sales', 'views',
        'platform_account__platform__name'
    )

    # Calculate metrics
    total_revenue = (distribution_revenue.get('total_revenue') or Decimal('0'))
    total_sales = distribution_revenue.get('total_sales') or 0
    avg_revenue_per_sale = total_revenue / total_sales if total_sales > 0 else Decimal('0')

    return api_success({
        'summary': {
            'total_revenue': float(total_revenue),
            'total_sales': total_sales,
            'total_views': distribution_revenue.get('total_views') or 0,
            'total_downloads': distribution_revenue.get('total_downloads') or 0,
            'total_listings': distribution_revenue.get('total_listings') or 0,
            'avg_revenue_per_sale': float(avg_revenue_per_sale),
        },
        'opportunity_revenue': {
            'total': float(opportunity_revenue.get('total_amount') or 0),
            'net': float(opportunity_revenue.get('total_net') or 0),
            'fees': float(opportunity_revenue.get('total_fees') or 0),
            'count': opportunity_revenue.get('count') or 0,
        },
        'by_platform': list(platform_breakdown),
        'daily_trend': list(daily_trend),
        'top_content': list(top_content),
        'period_days': days,
    })


# =============================================================================
# Platform-Specific Analytics
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def platform_revenue_detail(request, platform_name):
    """
    GET /api/distribution/revenue/platform/<platform_name>/

    Get detailed revenue analytics for a specific platform.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    # Find platform
    platform = DistributionPlatform.objects.filter(
        name__icontains=platform_name
    ).first()

    if not platform:
        return api_error(f"Platform '{platform_name}' not found", status_code=404)

    # Get user's account on this platform
    account = UserPlatformAccount.objects.filter(
        user=request.user,
        platform=platform
    ).first()

    if not account:
        return api_error(f"No account connected for {platform.name}")

    # Time range
    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    # Get distributions on this platform
    distributions = ContentDistribution.objects.filter(
        user=request.user,
        platform_account=account,
    )

    # Overall stats
    overall = distributions.aggregate(
        total_revenue=Sum('revenue'),
        total_sales=Sum('sales'),
        total_views=Sum('views'),
        total_downloads=Sum('downloads'),
        total_listings=Count('id'),
        live_listings=Count('id', filter=Q(status='live')),
        avg_price=Avg('price'),
    )

    # Recent activity
    recent_sales = distributions.filter(
        last_sale_at__gte=since
    ).order_by('-last_sale_at')[:10].values(
        'id', 'title', 'revenue', 'sales', 'last_sale_at'
    )

    # Performance by content type
    by_content_type = distributions.values('content_type').annotate(
        total_revenue=Sum('revenue'),
        total_sales=Sum('sales'),
        count=Count('id'),
    )

    # Performance by tag
    # Note: This is a simplified version - tags are stored as JSON
    top_tags = {}
    for dist in distributions.filter(tags__isnull=False):
        for tag in dist.tags[:5]:  # First 5 tags per item
            if tag not in top_tags:
                top_tags[tag] = {'count': 0, 'revenue': Decimal('0'), 'sales': 0}
            top_tags[tag]['count'] += 1
            top_tags[tag]['revenue'] += dist.revenue or Decimal('0')
            top_tags[tag]['sales'] += dist.sales or 0

    # Sort tags by revenue
    sorted_tags = sorted(
        [{'tag': k, **v} for k, v in top_tags.items()],
        key=lambda x: x['revenue'],
        reverse=True
    )[:10]

    # Monthly trend
    monthly_trend = distributions.filter(
        listed_at__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month=TruncMonth('listed_at')
    ).values('month').annotate(
        revenue=Sum('revenue'),
        sales=Sum('sales'),
        new_listings=Count('id'),
    ).order_by('month')

    # ROI calculation
    commission_rate = float(platform.commission_percent) / 100
    gross_revenue = float(overall.get('total_revenue') or 0)
    platform_fees = gross_revenue * commission_rate
    net_revenue = gross_revenue - platform_fees

    return api_success({
        'platform': {
            'id': str(platform.id),
            'name': platform.name,
            'type': platform.platform_type,
            'commission_percent': float(platform.commission_percent),
        },
        'account': {
            'username': account.account_username,
            'status': account.account_status,
            'connected_at': account.created_at.isoformat(),
        },
        'stats': {
            'total_revenue': float(overall.get('total_revenue') or 0),
            'total_sales': overall.get('total_sales') or 0,
            'total_views': overall.get('total_views') or 0,
            'total_downloads': overall.get('total_downloads') or 0,
            'total_listings': overall.get('total_listings') or 0,
            'live_listings': overall.get('live_listings') or 0,
            'avg_price': float(overall.get('avg_price') or 0),
        },
        'roi': {
            'gross_revenue': gross_revenue,
            'platform_fees': platform_fees,
            'net_revenue': net_revenue,
            'roi_percent': (net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0,
        },
        'recent_sales': list(recent_sales),
        'by_content_type': list(by_content_type),
        'top_tags': sorted_tags,
        'monthly_trend': list(monthly_trend),
        'period_days': days,
    })


# =============================================================================
# Platform Comparison
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def compare_platforms(request):
    """
    GET /api/distribution/revenue/compare/

    Compare revenue performance across all connected platforms.
    """
    # Session 745: Return empty data for anonymous users instead of 401
    if not request.user.is_authenticated:
        return api_success({'platforms': [], 'summary': {'total_revenue': 0, 'total_sales': 0}})

    days = int(request.GET.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    # Get all connected accounts with their platforms
    accounts = UserPlatformAccount.objects.filter(
        user=request.user,
        account_status='active'
    ).select_related('platform')

    comparisons = []

    for account in accounts:
        distributions = ContentDistribution.objects.filter(
            user=request.user,
            platform_account=account,
            status='live',
        )

        stats = distributions.aggregate(
            total_revenue=Sum('revenue'),
            total_sales=Sum('sales'),
            total_views=Sum('views'),
            item_count=Count('id'),
            avg_price=Avg('price'),
        )

        recent_stats = distributions.filter(listed_at__gte=since).aggregate(
            recent_revenue=Sum('revenue'),
            recent_sales=Sum('sales'),
        )

        total_revenue = float(stats.get('total_revenue') or 0)
        total_sales = stats.get('total_sales') or 0
        commission = float(account.platform.commission_percent) / 100
        net_revenue = total_revenue * (1 - commission)

        comparisons.append({
            'platform': {
                'name': account.platform.name,
                'type': account.platform.platform_type,
                'commission': float(account.platform.commission_percent),
            },
            'total_revenue': total_revenue,
            'net_revenue': net_revenue,
            'total_sales': total_sales,
            'total_views': stats.get('total_views') or 0,
            'item_count': stats.get('item_count') or 0,
            'avg_price': float(stats.get('avg_price') or 0),
            'recent_revenue': float(recent_stats.get('recent_revenue') or 0),
            'recent_sales': recent_stats.get('recent_sales') or 0,
            'revenue_per_item': total_revenue / stats['item_count'] if stats.get('item_count') else 0,
            'conversion_rate': (total_sales / stats['total_views'] * 100) if stats.get('total_views') else 0,
        })

    # Sort by total revenue
    comparisons.sort(key=lambda x: x['total_revenue'], reverse=True)

    # Calculate totals
    totals = {
        'total_revenue': sum(c['total_revenue'] for c in comparisons),
        'net_revenue': sum(c['net_revenue'] for c in comparisons),
        'total_sales': sum(c['total_sales'] for c in comparisons),
        'total_items': sum(c['item_count'] for c in comparisons),
    }

    # Best performing platform
    best_platform = comparisons[0] if comparisons else None

    # Recommendations
    recommendations = []
    if comparisons:
        # Find platform with best conversion rate
        best_conversion = max(comparisons, key=lambda x: x['conversion_rate'])
        if best_conversion['conversion_rate'] > 0:
            recommendations.append({
                'type': 'best_conversion',
                'platform': best_conversion['platform']['name'],
                'message': f"{best_conversion['platform']['name']} has the highest conversion rate ({best_conversion['conversion_rate']:.1f}%)",
            })

        # Find platform with lowest commission
        lowest_commission = min(comparisons, key=lambda x: x['platform']['commission'])
        recommendations.append({
            'type': 'lowest_commission',
            'platform': lowest_commission['platform']['name'],
            'message': f"{lowest_commission['platform']['name']} has the lowest commission ({lowest_commission['platform']['commission']}%)",
        })

        # Revenue concentration warning
        if best_platform and totals['total_revenue'] > 0:
            concentration = best_platform['total_revenue'] / totals['total_revenue']
            if concentration > 0.8:
                recommendations.append({
                    'type': 'diversification',
                    'message': f"{concentration*100:.0f}% of revenue comes from {best_platform['platform']['name']}. Consider diversifying.",
                })

    return api_success({
        'comparisons': comparisons,
        'totals': totals,
        'best_platform': best_platform,
        'recommendations': recommendations,
        'period_days': days,
    })


# =============================================================================
# ROI Calculator
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def calculate_roi(request):
    """
    GET/POST /api/distribution/revenue/roi/

    Calculate ROI for distributions.

    POST body (optional):
    {
        "content_id": "uuid",  // Specific content
        "platform": "etsy",    // Specific platform
        "include_costs": true  // Include production costs
    }
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    filters = {}
    include_costs = False

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if data.get('content_id'):
                filters['id'] = data['content_id']
            if data.get('platform'):
                filters['platform_account__platform__name__icontains'] = data['platform']
            include_costs = data.get('include_costs', False)
        except json.JSONDecodeError:
            pass

    # Get distributions
    distributions = ContentDistribution.objects.filter(
        user=request.user,
        status='live',
        **filters
    ).select_related('platform_account__platform')

    roi_data = []

    for dist in distributions:
        platform = dist.platform_account.platform
        commission = float(platform.commission_percent) / 100

        gross_revenue = float(dist.revenue or 0)
        platform_fees = gross_revenue * commission
        net_revenue = gross_revenue - platform_fees

        # Production cost (if we track it)
        production_cost = Decimal('0')
        if include_costs and dist.opportunity:
            # Get production cost from linked content
            content_records = dist.opportunity.created_content.all()
            for content in content_records:
                production_cost += content.production_cost or Decimal('0')

        profit = net_revenue - float(production_cost)
        roi_percent = (profit / float(production_cost) * 100) if production_cost > 0 else None

        roi_data.append({
            'distribution_id': str(dist.id),
            'title': dist.title,
            'platform': platform.name,
            'gross_revenue': gross_revenue,
            'platform_fees': platform_fees,
            'net_revenue': net_revenue,
            'production_cost': float(production_cost) if include_costs else None,
            'profit': profit if include_costs else net_revenue,
            'roi_percent': roi_percent,
            'sales': dist.sales,
            'revenue_per_sale': gross_revenue / dist.sales if dist.sales > 0 else 0,
        })

    # Sort by profit
    roi_data.sort(key=lambda x: x['profit'], reverse=True)

    # Calculate totals
    total_gross = sum(r['gross_revenue'] for r in roi_data)
    total_fees = sum(r['platform_fees'] for r in roi_data)
    total_net = sum(r['net_revenue'] for r in roi_data)

    return api_success({
        'roi_data': roi_data[:50],  # First 50
        'totals': {
            'gross_revenue': total_gross,
            'platform_fees': total_fees,
            'net_revenue': total_net,
            'fee_percentage': (total_fees / total_gross * 100) if total_gross > 0 else 0,
        },
        'count': len(roi_data),
    })


# =============================================================================
# Revenue Forecasting
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def revenue_forecast(request):
    """
    GET /api/distribution/revenue/forecast/

    Generate revenue forecasts based on historical data.
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    # Historical data (last 90 days)
    since = timezone.now() - timedelta(days=90)

    daily_revenue = ContentDistribution.objects.filter(
        user=request.user,
        listed_at__gte=since,
    ).annotate(
        date=TruncDate('listed_at')
    ).values('date').annotate(
        revenue=Sum('revenue'),
        sales=Sum('sales'),
    ).order_by('date')

    # Convert to list and calculate averages
    revenue_data = list(daily_revenue)

    if not revenue_data:
        return api_success({
            'message': 'Insufficient historical data for forecasting',
            'forecast': None,
        })

    # Calculate moving averages
    revenues = [float(d['revenue'] or 0) for d in revenue_data]
    sales = [d['sales'] or 0 for d in revenue_data]

    # Simple forecasting based on recent trends
    recent_days = 14
    recent_revenues = revenues[-recent_days:] if len(revenues) >= recent_days else revenues

    avg_daily_revenue = sum(recent_revenues) / len(recent_revenues) if recent_revenues else 0
    avg_daily_sales = sum(sales[-recent_days:]) / len(sales[-recent_days:]) if sales else 0

    # Trend calculation (simple linear)
    if len(revenues) >= 30:
        first_half = sum(revenues[:len(revenues)//2]) / (len(revenues)//2)
        second_half = sum(revenues[len(revenues)//2:]) / (len(revenues)//2)
        trend = (second_half - first_half) / first_half if first_half > 0 else 0
    else:
        trend = 0

    # Forecasts
    forecasts = {
        '7_day': {
            'revenue': avg_daily_revenue * 7 * (1 + trend * 0.5),
            'sales': int(avg_daily_sales * 7),
        },
        '30_day': {
            'revenue': avg_daily_revenue * 30 * (1 + trend),
            'sales': int(avg_daily_sales * 30),
        },
        '90_day': {
            'revenue': avg_daily_revenue * 90 * (1 + trend * 1.5),
            'sales': int(avg_daily_sales * 90),
        },
    }

    # Confidence level based on data volume
    confidence = min(len(revenues) / 90, 1.0)  # 90 days = 100% confidence

    return api_success({
        'historical': {
            'days_analyzed': len(revenues),
            'avg_daily_revenue': avg_daily_revenue,
            'avg_daily_sales': avg_daily_sales,
            'trend_percent': trend * 100,
        },
        'forecasts': forecasts,
        'confidence': confidence,
        'note': 'Forecasts are estimates based on historical performance',
    })


# =============================================================================
# Revenue Goals
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def revenue_goals(request):
    """
    GET/POST /api/distribution/revenue/goals/

    GET: Get current revenue goals and progress
    POST: Set revenue goals

    POST body:
    {
        "monthly_goal": 1000,
        "yearly_goal": 12000
    }
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    # Store goals in user profile or session for now
    # In production, create a proper model for this

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Store in session
            request.session['revenue_goals'] = {
                'monthly': data.get('monthly_goal', 0),
                'yearly': data.get('yearly_goal', 0),
                'set_at': timezone.now().isoformat(),
            }
            return api_success({'message': 'Goals updated successfully'})
        except json.JSONDecodeError:
            return api_error("Invalid JSON")

    # Get current goals
    goals = request.session.get('revenue_goals', {
        'monthly': 0,
        'yearly': 0,
    })

    # Calculate progress
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_revenue = ContentDistribution.objects.filter(
        user=request.user,
        listed_at__gte=month_start,
    ).aggregate(total=Sum('revenue'))['total'] or Decimal('0')

    yearly_revenue = ContentDistribution.objects.filter(
        user=request.user,
        listed_at__gte=year_start,
    ).aggregate(total=Sum('revenue'))['total'] or Decimal('0')

    monthly_goal = goals.get('monthly', 0)
    yearly_goal = goals.get('yearly', 0)

    return api_success({
        'goals': {
            'monthly': monthly_goal,
            'yearly': yearly_goal,
        },
        'progress': {
            'monthly': {
                'current': float(monthly_revenue),
                'goal': monthly_goal,
                'percent': (float(monthly_revenue) / monthly_goal * 100) if monthly_goal > 0 else 0,
                'remaining': max(0, monthly_goal - float(monthly_revenue)),
            },
            'yearly': {
                'current': float(yearly_revenue),
                'goal': yearly_goal,
                'percent': (float(yearly_revenue) / yearly_goal * 100) if yearly_goal > 0 else 0,
                'remaining': max(0, yearly_goal - float(yearly_revenue)),
            },
        },
        'period': {
            'month': now.strftime('%B %Y'),
            'year': now.year,
        },
    })


# =============================================================================
# Export Revenue Data
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def export_revenue_data(request):
    """
    GET /api/distribution/revenue/export/

    Export revenue data in JSON format.
    Query params:
    - format: json (default)
    - days: number of days to include (default: 365)
    """
    if not request.user.is_authenticated:
        return api_error("Authentication required", status_code=401)

    days = int(request.GET.get('days', 365))
    since = timezone.now() - timedelta(days=days)

    # Get all distributions with revenue
    distributions = ContentDistribution.objects.filter(
        user=request.user,
        listed_at__gte=since,
    ).select_related('platform_account__platform').order_by('-listed_at')

    export_data = []

    for dist in distributions:
        export_data.append({
            'id': str(dist.id),
            'title': dist.title,
            'platform': dist.platform_account.platform.name,
            'content_type': dist.content_type,
            'status': dist.status,
            'price': float(dist.price or 0),
            'revenue': float(dist.revenue or 0),
            'sales': dist.sales,
            'views': dist.views,
            'downloads': dist.downloads,
            'listed_at': dist.listed_at.isoformat() if dist.listed_at else None,
            'last_sale_at': dist.last_sale_at.isoformat() if dist.last_sale_at else None,
            'tags': dist.tags,
        })

    # Summary
    summary = {
        'total_items': len(export_data),
        'total_revenue': sum(d['revenue'] for d in export_data),
        'total_sales': sum(d['sales'] for d in export_data),
        'date_range': {
            'from': since.isoformat(),
            'to': timezone.now().isoformat(),
        },
        'exported_at': timezone.now().isoformat(),
    }

    return api_success({
        'summary': summary,
        'data': export_data,
    })
