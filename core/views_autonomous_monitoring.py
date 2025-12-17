"""
Autonomous Monitoring Dashboard - Session 476

Real-time monitoring dashboard for all Tier 1 Autonomous Situations:
1. Autonomous Content Studio
2. Narrative Drift Detector
3. Market Intelligence Desk

Plus unified pipeline health, ROI tracking, and provenance chain visualization.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncHour, TruncDay

logger = logging.getLogger(__name__)


def public_endpoint(view_func):
    """Decorator to make an endpoint publicly accessible without authentication."""
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    # Mark as public for middleware
    wrapper.public_endpoint = True
    return csrf_exempt(wrapper)


@require_GET
def autonomous_monitoring_dashboard(request):
    """Render the autonomous monitoring dashboard page."""
    return render(request, 'autonomous_monitoring.html')


@require_GET
def api_unified_health(request):
    """
    Get unified pipeline health status.
    Returns health for all 4 subsystems.
    """
    try:
        from core.tasks import unified_pipeline_health_check
        result = unified_pipeline_health_check()
        return JsonResponse({
            'success': True,
            'data': result
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_content_studio_status(request):
    """
    Get Autonomous Content Studio status.
    Returns channels, recent episodes, and performance metrics.
    """
    try:
        from core.models_autonomous_studio import (
            ContentChannel, ChannelEpisode, ChannelStatus,
            TopicPerformance, ContentDebate
        )

        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        # Channel stats
        channels = ContentChannel.objects.all()
        channel_data = []
        for channel in channels:
            recent_episodes = ChannelEpisode.objects.filter(
                channel=channel,
                publish_date__gte=day_ago
            ).count()

            channel_data.append({
                'id': str(channel.id),
                'name': channel.name,
                'status': channel.status,
                'episode_count': channel.episodes.count(),
                'episodes_24h': recent_episodes,
                'last_run': channel.last_run.isoformat() if channel.last_run else None,
                'next_run': channel.next_scheduled_run.isoformat() if channel.next_scheduled_run else None,
            })

        # Recent episodes
        recent_episodes = ChannelEpisode.objects.filter(
            publish_date__gte=day_ago
        ).order_by('-publish_date')[:10]

        episode_data = [{
            'id': str(ep.id),
            'title': ep.title,
            'channel': ep.channel.name,
            'publish_date': ep.publish_date.isoformat(),
            'performance_score': float(ep.performance_score) if ep.performance_score else 0,
        } for ep in recent_episodes]

        # Topic performance
        top_topics = TopicPerformance.objects.order_by('-success_rate')[:5]
        topic_data = [{
            'topic': tp.topic,
            'success_rate': float(tp.success_rate),
            'times_used': tp.times_used,
        } for tp in top_topics]

        # Recent debates
        recent_debates = ContentDebate.objects.filter(
            created_at__gte=day_ago
        ).count()

        return JsonResponse({
            'success': True,
            'data': {
                'channels': channel_data,
                'active_channels': sum(1 for c in channel_data if c['status'] == 'active'),
                'total_channels': len(channel_data),
                'recent_episodes': episode_data,
                'episodes_24h': len(episode_data),
                'top_topics': topic_data,
                'debates_24h': recent_debates,
            }
        })
    except Exception as e:
        logger.error(f"Content Studio status error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_narrative_drift_status(request):
    """
    Get Narrative Drift Detector status.
    Returns narratives, evidence, shifts, and domain coverage.
    """
    try:
        from core.models_narrative_drift import (
            Narrative, NarrativeEvidence, NarrativeShift,
            NarrativeStatus, NarrativeAlert
        )

        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        # Narrative stats by status
        status_counts = Narrative.objects.values('status').annotate(
            count=Count('id')
        )
        status_map = {s['status']: s['count'] for s in status_counts}

        # Domain coverage
        domain_counts = Narrative.objects.values('domain').annotate(
            count=Count('id')
        ).order_by('-count')

        # Recent evidence
        evidence_24h = NarrativeEvidence.objects.filter(
            created_at__gte=day_ago
        ).count()

        evidence_by_hour = NarrativeEvidence.objects.filter(
            created_at__gte=day_ago
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')

        # Recent shifts
        shifts_24h = NarrativeShift.objects.filter(
            detected_at__gte=day_ago
        ).count()

        recent_shifts = NarrativeShift.objects.filter(
            detected_at__gte=week_ago
        ).order_by('-detected_at')[:5]

        shift_data = [{
            'id': str(s.id),
            'narrative': s.narrative.title if s.narrative else 'Unknown',
            'direction': s.direction,
            'importance': s.importance,
            'detected_at': s.detected_at.isoformat(),
            'summary': s.summary[:100] if s.summary else '',
        } for s in recent_shifts]

        # Active alerts
        active_alerts = NarrativeAlert.objects.filter(
            status='active'
        ).count()

        return JsonResponse({
            'success': True,
            'data': {
                'total_narratives': Narrative.objects.count(),
                'status_breakdown': status_map,
                'domains': list(domain_counts[:8]),
                'evidence_24h': evidence_24h,
                'evidence_by_hour': list(evidence_by_hour),
                'shifts_24h': shifts_24h,
                'recent_shifts': shift_data,
                'active_alerts': active_alerts,
            }
        })
    except Exception as e:
        logger.error(f"Narrative Drift status error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_market_intelligence_status(request):
    """
    Get Market Intelligence Desk status.
    Returns spider data, opportunities, and scoring metrics.
    """
    try:
        from core.models_unified_system import (
            SpiderData, Opportunity, ScoringResult
        )

        now = timezone.now()
        day_ago = now - timedelta(hours=24)

        # Spider data stats
        spider_24h = SpiderData.objects.filter(
            created_at__gte=day_ago
        ).count()

        spider_by_source = SpiderData.objects.filter(
            created_at__gte=day_ago
        ).values('spider_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Opportunity stats
        opportunities_24h = Opportunity.objects.filter(
            created_at__gte=day_ago
        ).count()

        opp_by_category = Opportunity.objects.filter(
            created_at__gte=day_ago
        ).values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        # Scoring stats
        scoring_24h = ScoringResult.objects.filter(
            scored_at__gte=day_ago
        ).count()

        avg_score = ScoringResult.objects.filter(
            scored_at__gte=day_ago
        ).aggregate(avg=Avg('final_score'))['avg'] or 0

        return JsonResponse({
            'success': True,
            'data': {
                'spider_data_24h': spider_24h,
                'spider_data_total': SpiderData.objects.count(),
                'spider_by_source': list(spider_by_source),
                'opportunities_24h': opportunities_24h,
                'opportunities_total': Opportunity.objects.count(),
                'opp_by_category': list(opp_by_category),
                'scoring_24h': scoring_24h,
                'avg_score': round(float(avg_score), 2),
            }
        })
    except Exception as e:
        logger.error(f"Market Intelligence status error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_roi_metrics(request):
    """
    Get ROI funnel metrics.
    Returns conversion events and revenue tracking.
    """
    try:
        from core.models_unified_system import ConversionEvent, ROIMetrics

        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        # Conversion funnel
        funnel_stages = ['view', 'click', 'application', 'revenue']
        funnel_data = {}

        for stage in funnel_stages:
            count = ConversionEvent.objects.filter(
                event_type=stage,
                created_at__gte=day_ago
            ).count()
            funnel_data[stage] = count

        # Revenue total
        revenue_24h = ConversionEvent.objects.filter(
            event_type='revenue',
            created_at__gte=day_ago
        ).aggregate(total=Sum('value'))['total'] or 0

        revenue_week = ConversionEvent.objects.filter(
            event_type='revenue',
            created_at__gte=week_ago
        ).aggregate(total=Sum('value'))['total'] or 0

        # Conversion events over time
        events_by_hour = ConversionEvent.objects.filter(
            created_at__gte=day_ago
        ).annotate(
            hour=TruncHour('created_at')
        ).values('hour', 'event_type').annotate(
            count=Count('id')
        ).order_by('hour')

        # Top sources
        top_sources = ConversionEvent.objects.filter(
            created_at__gte=week_ago
        ).values('source').annotate(
            count=Count('id'),
            revenue=Sum('value')
        ).order_by('-count')[:5]

        return JsonResponse({
            'success': True,
            'data': {
                'funnel': funnel_data,
                'revenue_24h': float(revenue_24h),
                'revenue_week': float(revenue_week),
                'events_by_hour': list(events_by_hour),
                'top_sources': list(top_sources),
                'total_events': ConversionEvent.objects.count(),
            }
        })
    except Exception as e:
        logger.error(f"ROI metrics error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_provenance_chain(request):
    """
    Get provenance chain visualization data.
    Returns data lineage records.
    """
    try:
        from core.models_unified_system import DataProvenance

        now = timezone.now()
        day_ago = now - timedelta(hours=24)

        # Provenance by entity type
        by_type = DataProvenance.objects.values('entity_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Recent provenance records
        recent = DataProvenance.objects.filter(
            created_at__gte=day_ago
        ).order_by('-created_at')[:20]

        recent_data = [{
            'id': str(p.id),
            'entity_type': p.entity_type,
            'entity_id': p.entity_id,
            'created_at': p.created_at.isoformat(),
            'hash': p.content_hash[:16] + '...' if p.content_hash else None,
            'has_parent': bool(p.parent_provenance_id),
        } for p in recent]

        # Chain depth stats
        total_records = DataProvenance.objects.count()
        records_with_parent = DataProvenance.objects.filter(
            parent_provenance__isnull=False
        ).count()

        return JsonResponse({
            'success': True,
            'data': {
                'by_type': list(by_type),
                'recent_records': recent_data,
                'total_records': total_records,
                'records_with_parent': records_with_parent,
                'records_24h': len(recent_data),
            }
        })
    except Exception as e:
        logger.error(f"Provenance chain error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_activity_stream(request):
    """
    Get real-time activity stream.
    Returns recent events from all autonomous systems.
    """
    try:
        from core.models_autonomous_studio import ChannelEpisode
        from core.models_narrative_drift import NarrativeEvidence, NarrativeShift
        from core.models_unified_system import SpiderData, ConversionEvent, DataProvenance

        now = timezone.now()
        hour_ago = now - timedelta(hours=1)

        activities = []

        # Recent episodes
        for ep in ChannelEpisode.objects.filter(publish_date__gte=hour_ago).order_by('-publish_date')[:5]:
            activities.append({
                'type': 'episode',
                'icon': '📺',
                'title': f"New episode: {ep.title[:50]}",
                'source': 'Content Studio',
                'timestamp': ep.publish_date.isoformat(),
            })

        # Recent evidence
        for ev in NarrativeEvidence.objects.filter(created_at__gte=hour_ago).order_by('-created_at')[:5]:
            activities.append({
                'type': 'evidence',
                'icon': '📊',
                'title': f"Evidence for: {ev.narrative.title[:40] if ev.narrative else 'Unknown'}",
                'source': 'Narrative Drift',
                'timestamp': ev.created_at.isoformat(),
            })

        # Recent shifts
        for sh in NarrativeShift.objects.filter(detected_at__gte=hour_ago).order_by('-detected_at')[:3]:
            activities.append({
                'type': 'shift',
                'icon': '⚡',
                'title': f"Shift detected: {sh.summary[:50] if sh.summary else 'New shift'}",
                'source': 'Narrative Drift',
                'timestamp': sh.detected_at.isoformat(),
            })

        # Recent spider data
        for sd in SpiderData.objects.filter(created_at__gte=hour_ago).order_by('-created_at')[:5]:
            activities.append({
                'type': 'spider',
                'icon': '🕷️',
                'title': f"Data from {sd.spider_name}: {sd.title[:40] if sd.title else 'New data'}",
                'source': 'Market Intelligence',
                'timestamp': sd.created_at.isoformat(),
            })

        # Recent conversions
        for ce in ConversionEvent.objects.filter(created_at__gte=hour_ago).order_by('-created_at')[:3]:
            activities.append({
                'type': 'conversion',
                'icon': '💰',
                'title': f"Conversion: {ce.event_type}",
                'source': 'ROI Tracking',
                'timestamp': ce.created_at.isoformat(),
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        return JsonResponse({
            'success': True,
            'data': {
                'activities': activities[:20],
                'count': len(activities),
            }
        })
    except Exception as e:
        logger.error(f"Activity stream error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def api_celery_schedules(request):
    """
    Get Celery beat schedule status.
    Returns all active schedules.
    """
    try:
        from django.conf import settings

        schedules = settings.CELERY_BEAT_SCHEDULE

        schedule_data = []
        for name, config in schedules.items():
            schedule_data.append({
                'name': name,
                'task': config.get('task', 'unknown'),
                'schedule': str(config.get('schedule', 'unknown')),
            })

        # Group by category
        categories = {
            'content_studio': [s for s in schedule_data if 'content' in s['name'].lower() or 'studio' in s['name'].lower()],
            'narrative_drift': [s for s in schedule_data if 'narrative' in s['name'].lower()],
            'market_intelligence': [s for s in schedule_data if 'market' in s['name'].lower() or 'spider' in s['name'].lower()],
            'unified_pipeline': [s for s in schedule_data if 'unified' in s['name'].lower() or 'pipeline' in s['name'].lower()],
            'roi_metrics': [s for s in schedule_data if 'roi' in s['name'].lower()],
            'ml_scoring': [s for s in schedule_data if 'scoring' in s['name'].lower() or 'ml-' in s['name'].lower()],
            'agents': [s for s in schedule_data if 'agent' in s['name'].lower()],
            'other': [],
        }

        # Put uncategorized in 'other'
        categorized = set()
        for cat_schedules in categories.values():
            for s in cat_schedules:
                categorized.add(s['name'])

        categories['other'] = [s for s in schedule_data if s['name'] not in categorized]

        return JsonResponse({
            'success': True,
            'data': {
                'total': len(schedule_data),
                'schedules': schedule_data,
                'by_category': {k: len(v) for k, v in categories.items()},
                'categories': categories,
            }
        })
    except Exception as e:
        logger.error(f"Celery schedules error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
