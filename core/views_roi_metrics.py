"""
ROI Metrics API Views - Phase 6 Market Intelligence Architecture

Provides REST API endpoints for ROI tracking, conversion events,
attribution analysis, and weekly intelligence briefs.

Session 472: December 17, 2025
"""

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator

import json

from django.db.models import Count  # Session 1083

logger = logging.getLogger(__name__)


# ============================================================================
# ROI Summary Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def roi_summary(request):
    """
    Get ROI summary metrics.

    GET /api/mi/roi/summary/
    Query params:
        - period_type: hourly, daily, weekly, monthly (default: daily)
        - dimension: overall, spider_source, etc. (default: overall)
        - limit: Number of periods (default: 30)
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        period_type = request.GET.get('period_type', 'daily')
        dimension = request.GET.get('dimension', 'overall')
        limit = int(request.GET.get('limit', 30))

        tracker = get_roi_tracker()
        summary = tracker.get_roi_summary(
            period_type=period_type,
            dimension=dimension,
            limit=limit
        )

        return JsonResponse({
            'success': True,
            'period_type': period_type,
            'dimension': dimension,
            'count': len(summary),
            'data': summary
        })

    except Exception as e:
        logger.error(f"Error getting ROI summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def roi_aggregate(request):
    """
    Trigger ROI metrics aggregation.

    POST /api/mi/roi/aggregate/
    Body:
        - period_type: hourly, daily, weekly, monthly
        - dimension: overall, spider_source, etc.
        - target_date: ISO date string (optional)
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        data = json.loads(request.body) if request.body else {}

        period_type = data.get('period_type', 'daily')
        dimension = data.get('dimension', 'overall')
        target_date_str = data.get('target_date')

        target_date = None
        if target_date_str:
            target_date = datetime.fromisoformat(target_date_str.replace('Z', '+00:00'))

        tracker = get_roi_tracker()
        success = tracker.aggregate_roi_metrics(
            period_type=period_type,
            dimension=dimension,
            target_date=target_date
        )

        return JsonResponse({
            'success': success,
            'period_type': period_type,
            'dimension': dimension,
            'message': 'Aggregation complete' if success else 'Aggregation failed'
        })

    except Exception as e:
        logger.error(f"Error aggregating ROI metrics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# Conversion Event Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def record_conversion(request):
    """
    Record a conversion event.

    POST /api/mi/conversion/record/
    Body:
        - event_type: view, click, apply, submit, interview, offer, convert, revenue
        - opportunity_id: UUID (optional)
        - spider_data_id: UUID (optional)
        - value: Decimal value (optional, required for revenue)
        - currency: Currency code (default: USD)
        - session_id: Browser session ID (optional)
        - attribution_source: Source name (optional)
        - attribution_medium: Medium (optional)
        - attribution_campaign: Campaign ID (optional)
        - previous_event_id: UUID of previous event in path (optional)
        - metadata: Additional JSON metadata (optional)
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        data = json.loads(request.body) if request.body else {}

        event_type = data.get('event_type')
        if not event_type:
            return JsonResponse({
                'success': False,
                'error': 'event_type is required'
            }, status=400)

        # Parse value if present
        value = None
        if data.get('value'):
            try:
                value = Decimal(str(data['value']))
            except InvalidOperation:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid value format'
                }, status=400)

        # Get user from request
        user_id = None
        if request.user and request.user.is_authenticated:
            user_id = request.user.id
        elif data.get('user_id'):
            user_id = int(data['user_id'])

        tracker = get_roi_tracker()
        result = tracker.record_conversion_event(
            event_type=event_type,
            opportunity_id=data.get('opportunity_id'),
            spider_data_id=data.get('spider_data_id'),
            user_id=user_id,
            value=value,
            currency=data.get('currency', 'USD'),
            session_id=data.get('session_id'),
            attribution_source=data.get('attribution_source'),
            attribution_medium=data.get('attribution_medium'),
            attribution_campaign=data.get('attribution_campaign'),
            metadata=data.get('metadata'),
            previous_event_id=data.get('previous_event_id')
        )

        return JsonResponse({
            'success': result.success,
            'event_id': result.event_id,
            'event_type': result.event_type,
            'value': str(result.value) if result.value else None,
            'attribution_source': result.attribution_source,
            'path_length': result.path_length,
            'error': result.error
        })

    except Exception as e:
        logger.error(f"Error recording conversion: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def conversion_events_list(request):
    """
    List conversion events with filters.

    GET /api/mi/conversion/events/
    Query params:
        - event_type: Filter by type
        - source: Filter by attribution source
        - start_date: Filter after date
        - end_date: Filter before date
        - opportunity_id: Filter by opportunity
        - page: Page number (default: 1)
        - page_size: Items per page (default: 50)
    """
    try:
        from core.models_unified_system import ConversionEvent
        from django.db.models import Q

        filters = Q()

        if request.GET.get('event_type'):
            filters &= Q(event_type=request.GET['event_type'])

        if request.GET.get('source'):
            filters &= Q(attribution_source=request.GET['source'])

        if request.GET.get('opportunity_id'):
            filters &= Q(opportunity_id=request.GET['opportunity_id'])

        if request.GET.get('start_date'):
            start = datetime.fromisoformat(
                request.GET['start_date'].replace('Z', '+00:00')
            )
            filters &= Q(event_timestamp__gte=start)

        if request.GET.get('end_date'):
            end = datetime.fromisoformat(
                request.GET['end_date'].replace('Z', '+00:00')
            )
            filters &= Q(event_timestamp__lte=end)

        events = ConversionEvent.objects.filter(filters).order_by('-event_timestamp')

        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 50)), 100)

        paginator = Paginator(events, page_size)
        page_obj = paginator.get_page(page)

        data = [
            {
                'id': str(e.id),
                'event_type': e.event_type,
                'event_type_display': e.get_event_type_display(),
                'opportunity_id': str(e.opportunity_id) if e.opportunity_id else None,
                'value': str(e.value) if e.value else None,
                'currency': e.currency,
                'attribution_source': e.attribution_source,
                'attribution_medium': e.attribution_medium,
                'session_id': e.session_id,
                'event_timestamp': e.event_timestamp.isoformat(),
                'has_previous': e.previous_event_id is not None
            }
            for e in page_obj
        ]

        return JsonResponse({
            'success': True,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'data': data
        })

    except Exception as e:
        logger.error(f"Error listing conversion events: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def conversion_path(request, event_id):
    """
    Get conversion path leading to an event.

    GET /api/mi/conversion/<event_id>/path/
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        include_metadata = request.GET.get('include_metadata', '').lower() == 'true'

        tracker = get_roi_tracker()
        path = tracker.get_conversion_path(
            event_id=event_id,
            include_metadata=include_metadata
        )

        return JsonResponse({
            'success': True,
            'event_id': event_id,
            'path_length': len(path),
            'path': path
        })

    except Exception as e:
        logger.error(f"Error getting conversion path: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# Funnel Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def funnel_metrics(request):
    """
    Get funnel metrics showing conversion rates between stages.

    GET /api/mi/funnel/
    Query params:
        - start_date: Filter after date
        - end_date: Filter before date
        - source: Filter by attribution source
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        start_date = None
        end_date = None

        if request.GET.get('start_date'):
            start_date = datetime.fromisoformat(
                request.GET['start_date'].replace('Z', '+00:00')
            )

        if request.GET.get('end_date'):
            end_date = datetime.fromisoformat(
                request.GET['end_date'].replace('Z', '+00:00')
            )

        source = request.GET.get('source')

        tracker = get_roi_tracker()
        metrics = tracker.get_funnel_metrics(
            start_date=start_date,
            end_date=end_date,
            source=source
        )

        return JsonResponse({
            'success': True,
            **metrics
        })

    except Exception as e:
        logger.error(f"Error getting funnel metrics: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# Attribution Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def attribution_by_source(request):
    """
    Get attribution summary grouped by source.

    GET /api/mi/attribution/by-source/
    Query params:
        - start_date: Filter after date
        - end_date: Filter before date
        - model: Attribution model filter
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        start_date = None
        end_date = None

        if request.GET.get('start_date'):
            start_date = datetime.fromisoformat(
                request.GET['start_date'].replace('Z', '+00:00')
            )

        if request.GET.get('end_date'):
            end_date = datetime.fromisoformat(
                request.GET['end_date'].replace('Z', '+00:00')
            )

        model = request.GET.get('model')

        tracker = get_roi_tracker()
        results = tracker.get_attribution_by_source(
            start_date=start_date,
            end_date=end_date,
            model=model
        )

        return JsonResponse({
            'success': True,
            'count': len(results),
            'data': results
        })

    except Exception as e:
        logger.error(f"Error getting attribution by source: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def attribution_paths(request):
    """
    List attribution paths.

    GET /api/mi/attribution/paths/
    Query params:
        - model: Filter by attribution model
        - source: Filter by primary source
        - page: Page number
        - page_size: Items per page
    """
    try:
        from core.models_unified_system import AttributionPath
        from django.db.models import Q

        filters = Q()

        if request.GET.get('model'):
            filters &= Q(attribution_model=request.GET['model'])

        if request.GET.get('source'):
            filters &= Q(primary_source=request.GET['source'])

        paths = AttributionPath.objects.filter(filters).order_by('-created_at')

        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 50)), 100)

        paginator = Paginator(paths, page_size)
        page_obj = paginator.get_page(page)

        data = [
            {
                'id': str(p.id),
                'conversion_event_id': str(p.conversion_event_id),
                'attribution_model': p.attribution_model,
                'path_length': p.path_length,
                'time_to_conversion_hours': str(p.time_to_conversion_hours) if p.time_to_conversion_hours else None,
                'primary_source': p.primary_source,
                'primary_source_credit': str(p.primary_source_credit),
                'attributed_value': str(p.attributed_value) if p.attributed_value else None,
                'created_at': p.created_at.isoformat()
            }
            for p in page_obj
        ]

        return JsonResponse({
            'success': True,
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'data': data
        })

    except Exception as e:
        logger.error(f"Error listing attribution paths: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def attribution_path_detail(request, path_id):
    """
    Get attribution path details.

    GET /api/mi/attribution/<path_id>/
    """
    try:
        from core.models_unified_system import AttributionPath

        path = AttributionPath.objects.get(id=path_id)

        return JsonResponse({
            'success': True,
            'data': {
                'id': str(path.id),
                'conversion_event_id': str(path.conversion_event_id),
                'attribution_model': path.attribution_model,
                'path_data': path.path_data,
                'path_length': path.path_length,
                'time_to_conversion_hours': str(path.time_to_conversion_hours) if path.time_to_conversion_hours else None,
                'attribution_credits': path.attribution_credits,
                'primary_source': path.primary_source,
                'primary_source_credit': str(path.primary_source_credit),
                'attributed_value': str(path.attributed_value) if path.attributed_value else None,
                'created_at': path.created_at.isoformat(),
                'updated_at': path.updated_at.isoformat()
            }
        })

    except AttributionPath.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Attribution path not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting attribution path detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# Weekly Brief Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def weekly_briefs_list(request):
    """
    List weekly intelligence briefs.

    GET /api/mi/briefs/
    Query params:
        - limit: Number of briefs (default: 10)
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        limit = min(int(request.GET.get('limit', 10)), 52)

        tracker = get_roi_tracker()
        briefs = tracker.get_weekly_briefs(limit=limit)

        return JsonResponse({
            'success': True,
            'count': len(briefs),
            'data': briefs
        })

    except Exception as e:
        logger.error(f"Error listing weekly briefs: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_weekly_brief(request):
    """
    Generate or get weekly intelligence brief.

    POST /api/mi/briefs/generate/
    Body:
        - week_start: ISO date string for start of week (optional)
    """
    try:
        from core.services.roi_tracker import get_roi_tracker

        data = json.loads(request.body) if request.body else {}

        week_start = None
        if data.get('week_start'):
            week_start = datetime.fromisoformat(
                data['week_start'].replace('Z', '+00:00')
            )

        tracker = get_roi_tracker()
        brief = tracker.generate_weekly_brief(week_start=week_start)

        return JsonResponse({
            'success': True,
            **brief
        })

    except Exception as e:
        logger.error(f"Error generating weekly brief: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def weekly_brief_detail(request, brief_id):
    """
    Get weekly brief details.

    GET /api/mi/briefs/<brief_id>/
    """
    try:
        from core.models_unified_system import WeeklyIntelligenceBrief

        brief = WeeklyIntelligenceBrief.objects.get(id=brief_id)

        return JsonResponse({
            'success': True,
            'data': {
                'id': str(brief.id),
                'week_start': brief.week_start.isoformat(),
                'week_end': brief.week_end.isoformat(),
                'status': brief.status,
                'total_revenue': str(brief.total_revenue),
                'total_conversions': brief.total_conversions,
                'total_opportunities': brief.total_opportunities,
                'total_spider_records': brief.total_spider_records,
                'revenue_change_pct': str(brief.revenue_change_pct) if brief.revenue_change_pct else None,
                'conversions_change_pct': str(brief.conversions_change_pct) if brief.conversions_change_pct else None,
                'top_spider_sources': brief.top_spider_sources,
                'top_opportunity_categories': brief.top_opportunity_categories,
                'top_agents': brief.top_agents,
                'key_insights': brief.key_insights,
                'recommendations': brief.recommendations,
                'executive_summary': brief.executive_summary,
                'detailed_report': brief.detailed_report,
                'generated_at': brief.generated_at.isoformat() if brief.generated_at else None,
                'created_at': brief.created_at.isoformat()
            }
        })

    except WeeklyIntelligenceBrief.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Brief not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting brief detail: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================================
# Dashboard / Stats Endpoints
# ============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def roi_dashboard(request):
    """
    Get ROI dashboard overview.

    GET /api/mi/roi/dashboard/
    """
    try:
        from core.models_unified_system import (
            ConversionEvent, AttributionPath, WeeklyIntelligenceBrief
        )
        from django.db.models import Sum
        from datetime import timedelta

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        # Today's stats
        today_events = ConversionEvent.objects.filter(
            event_timestamp__gte=today_start
        )
        today_revenue = today_events.filter(event_type='revenue').aggregate(
            total=Sum('value')
        )['total'] or 0
        today_conversions = today_events.filter(event_type='convert').count()

        # This week stats
        week_events = ConversionEvent.objects.filter(
            event_timestamp__gte=week_start
        )
        week_revenue = week_events.filter(event_type='revenue').aggregate(
            total=Sum('value')
        )['total'] or 0
        week_conversions = week_events.filter(event_type='convert').count()

        # This month stats
        month_events = ConversionEvent.objects.filter(
            event_timestamp__gte=month_start
        )
        month_revenue = month_events.filter(event_type='revenue').aggregate(
            total=Sum('value')
        )['total'] or 0
        month_conversions = month_events.filter(event_type='convert').count()

        # All-time stats
        total_events = ConversionEvent.objects.count()
        total_revenue = ConversionEvent.objects.filter(
            event_type='revenue'
        ).aggregate(total=Sum('value'))['total'] or 0
        total_conversions = ConversionEvent.objects.filter(
            event_type='convert'
        ).count()

        # Attribution stats
        attribution_count = AttributionPath.objects.count()

        # Latest weekly brief
        latest_brief = WeeklyIntelligenceBrief.objects.filter(
            status='complete'
        ).first()

        return JsonResponse({
            'success': True,
            'dashboard': {
                'today': {
                    'revenue': str(today_revenue),
                    'conversions': today_conversions,
                    'events': today_events.count()
                },
                'this_week': {
                    'revenue': str(week_revenue),
                    'conversions': week_conversions,
                    'events': week_events.count()
                },
                'this_month': {
                    'revenue': str(month_revenue),
                    'conversions': month_conversions,
                    'events': month_events.count()
                },
                'all_time': {
                    'total_events': total_events,
                    'total_revenue': str(total_revenue),
                    'total_conversions': total_conversions,
                    'attribution_paths': attribution_count
                },
                'latest_brief': {
                    'week_start': latest_brief.week_start.isoformat() if latest_brief else None,
                    'executive_summary': latest_brief.executive_summary if latest_brief else None
                } if latest_brief else None,
                'generated_at': now.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error getting ROI dashboard: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def roi_stats(request):
    """
    Get ROI statistics.

    GET /api/mi/roi/stats/
    """
    try:
        from core.models_unified_system import (
            ConversionEvent, ROIMetric, AttributionPath, WeeklyIntelligenceBrief
        )

        stats = {
            'conversion_events': ConversionEvent.objects.count(),
            'roi_metrics': ROIMetric.objects.count(),
            'attribution_paths': AttributionPath.objects.count(),
            'weekly_briefs': WeeklyIntelligenceBrief.objects.count(),
            'complete_briefs': WeeklyIntelligenceBrief.objects.filter(
                status='complete'
            ).count(),
            'event_types': dict(
                ConversionEvent.objects.values('event_type').annotate(
                    count=Count('id')
                ).values_list('event_type', 'count')
            ),
            'attribution_models': dict(
                AttributionPath.objects.values('attribution_model').annotate(
                    count=Count('id')
                ).values_list('attribution_model', 'count')
            )
        }

        return JsonResponse({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"Error getting ROI stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
