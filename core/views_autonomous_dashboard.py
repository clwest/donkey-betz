"""
Autonomous Systems Dashboard API - Session 484

Provides visibility into the 19 autonomous situations running 24/7.

API Endpoints:
- GET /api/autonomous/situations/ - List all situations with status
- GET /api/autonomous/situations/<type>/ - Situation detail
- POST /api/autonomous/situations/<type>/toggle/ - Enable/disable
- POST /api/autonomous/situations/<type>/run-now/ - Manual trigger
- GET /api/autonomous/triggers/ - List all triggers
- GET /api/autonomous/trigger-events/ - Recent trigger events
- GET /api/autonomous/analytics/summary/ - Dashboard summary stats
"""

import logging
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count

import json  # Session 1083

from core.models_autonomous_situations import (
    AutonomousSituationSession,
    ViralContentPrediction,
    SkillGapAnalysis,
)
from core.models_situation_triggers import (
    SituationTrigger,
    TriggerEvent
)

logger = logging.getLogger(__name__)


# =============================================================================
# SITUATION DEFINITIONS
# =============================================================================

# Map situation types to their details
SITUATION_CATALOG = {
    # Content Domain
    'content_studio': {
        'name': 'Autonomous Content Studio',
        'domain': 'content',
        'description': 'Auto-generates content for channels with 3-agent debates',
        'schedule': 'Every hour',  # Session 539: Updated from 4h to 1h
        'celery_task': 'autonomous_studio.run_main_loop',
        'model': 'ContentChannel',
    },
    'narrative_drift': {
        'name': 'Narrative Drift Detector',
        'domain': 'content',
        'description': 'Detects significant narrative shifts in news topics',
        'schedule': 'Every hour',  # Session 539: Updated from 4h to 1h
        'celery_task': 'core.tasks.run_narrative_drift_detection',
        'model': 'NarrativeDriftTopic',
    },
    'viral_prediction': {
        'name': 'Viral Content Predictor',
        'domain': 'content',
        'description': 'Scores content ideas by viral potential',
        'schedule': 'Every hour',  # Session 539: Updated from 4h to 1h
        'celery_task': 'core.tasks.run_viral_prediction',
        'model': 'ViralContentPrediction',
    },

    # Creative Domain
    'design_trends': {
        'name': 'Design Trends Monitor',
        'domain': 'creative',
        'description': 'Tracks design trends from Dribbble, Behance, Awwwards',
        'schedule': 'Every 2 hours',  # Session 539: Updated from 6h to 2h
        'celery_task': 'core.tasks.run_design_trend_analysis',
        'model': 'DesignTrend',
    },
    'thumbnail_optimization': {
        'name': 'Thumbnail A/B Optimizer',
        'domain': 'creative',
        'description': 'Auto-generates and tests thumbnails',
        'schedule': 'On-demand',
        'celery_task': 'core.tasks.run_thumbnail_optimization',
        'model': 'ThumbnailVariant',
    },

    # Income Domain
    'job_matching': {
        'name': 'Job Match Intelligence',
        'domain': 'income',
        'description': 'Monitors jobs, scores matches to user profile',
        'schedule': 'Every 2 hours',
        'celery_task': 'core.tasks.run_job_matching',
        'model': 'JobMatch',
    },
    'freelance_scout': {
        'name': 'Freelance Opportunity Scout',
        'domain': 'income',
        'description': 'Tracks freelance gigs across platforms',
        'schedule': 'Every hour',  # Session 539: Updated from 4h to 1h
        'celery_task': 'core.tasks.run_freelance_scout',
        'model': 'FreelanceOpportunity',
    },
    'side_hustle': {
        'name': 'Side Hustle Detector',
        'domain': 'income',
        'description': 'Finds trending micro-opportunities',
        'schedule': 'Every 4 hours',  # Session 539: Updated from 8h to 4h
        'celery_task': 'core.tasks.run_side_hustle_detection',
        'model': 'SideHustle',
    },

    # Financial Domain
    'market_intelligence': {
        'name': 'Market Intelligence Desk',
        'domain': 'financial',
        'description': 'Creates market intelligence briefs',
        'schedule': 'Every hour',  # Session 539: Updated from 4h to 1h
        'celery_task': 'core.tasks.run_market_intelligence',
        'model': 'MarketIntelligenceBrief',
    },
    'sec_filing': {
        'name': 'SEC Filing Analyzer',
        'domain': 'financial',
        'description': 'Deep analysis of institutional filings',
        'schedule': 'Every hour',  # Session 539: Updated from 4h to 1h
        'celery_task': 'core.tasks.run_sec_filing_analysis',
        'model': 'SECFilingAnalysis',
    },
    'earnings_prediction': {
        'name': 'Earnings Surprise Predictor',
        'domain': 'financial',
        'description': 'Pre-earnings analysis with predictions',
        'schedule': 'Every hour',  # Session 539: Updated from 4h to 1h
        'celery_task': 'core.tasks.run_earnings_prediction',
        'model': 'EarningsPrediction',
    },
    'crypto_sentiment': {
        'name': 'Crypto Sentiment Monitor',
        'domain': 'financial',
        'description': 'Tracks sentiment across crypto communities',
        'schedule': 'Every hour',  # Session 539: Updated from 2h to 1h
        'celery_task': 'core.tasks.run_crypto_sentiment',
        'model': 'CryptoSentiment',
    },
    'blockchain': {
        'name': 'Blockchain Security Monitor',
        'domain': 'financial',
        'description': 'Monitors whale movements and security events',
        'schedule': 'Every hour',  # Session 539: Updated from 2h to 1h
        'celery_task': 'autonomous.blockchain_security_monitor',
        'model': 'BlockchainSecurityAlert',
    },
    'stock_market': {
        'name': 'Stock Market Intelligence',
        'domain': 'financial',
        'description': 'Analyzes stock market with Bull vs Bear debate',
        'schedule': '3x daily (9,12,16 M-F)',
        'celery_task': 'core.tasks.run_stock_market_intelligence',
        'model': 'StockMarketAlert',
    },

    # Research Domain
    'tech_stack': {
        'name': 'Tech Stack Evolution Tracker',
        'domain': 'research',
        'description': 'Monitors rising/falling technologies',
        'schedule': 'Every 4 hours',  # Session 539: Updated from 8h to 4h
        'celery_task': 'core.tasks.run_tech_stack_analysis',
        'model': 'TechStackTrend',
    },
    'ai_model': {
        'name': 'AI Model Release Monitor',
        'domain': 'research',
        'description': 'Alerts on new AI model releases',
        'schedule': 'Every 2 hours',  # Session 539: Updated from 6h to 2h
        'celery_task': 'core.tasks.run_ai_model_monitoring',
        'model': 'AIModelRelease',
    },
    'skill_gap': {
        'name': 'Skill Gap Analyzer',
        'domain': 'research',
        'description': 'Matches trending skills to courses',
        'schedule': 'Every 6 hours',
        'celery_task': 'core.tasks.run_skill_gap_analysis',
        'model': 'SkillGapAnalysis',
    },

    # Legal Domain
    'case_law': {
        'name': 'Case Law Monitor',
        'domain': 'legal',
        'description': 'Tracks relevant case decisions',
        'schedule': 'Every 6 hours',
        'celery_task': 'core.tasks.run_case_law_monitoring',
        'model': 'CaseLawUpdate',
    },
    'regulatory': {
        'name': 'Regulatory Change Detector',
        'domain': 'legal',
        'description': 'Monitors regulatory changes',
        'schedule': 'Every 8 hours',
        'celery_task': 'core.tasks.run_regulatory_monitoring',
        'model': 'RegulatoryChange',
    },
}

# Domain colors for UI
DOMAIN_COLORS = {
    'content': '#8B5CF6',     # Purple
    'creative': '#EC4899',     # Pink
    'income': '#10B981',       # Green
    'financial': '#F59E0B',    # Amber
    'research': '#3B82F6',     # Blue
    'legal': '#6B7280',        # Gray
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_situation_status(situation_type: str) -> dict:
    """Get the current status of a situation."""
    info = SITUATION_CATALOG.get(situation_type, {})

    # Get last session
    last_session = AutonomousSituationSession.objects.filter(
        situation_type=situation_type
    ).order_by('-started_at').first()

    # Count sessions in different time periods
    now = timezone.now()
    runs_24h = AutonomousSituationSession.objects.filter(
        situation_type=situation_type,
        started_at__gte=now - timedelta(hours=24)
    ).count()
    runs_7d = AutonomousSituationSession.objects.filter(
        situation_type=situation_type,
        started_at__gte=now - timedelta(days=7)
    ).count()
    runs_30d = AutonomousSituationSession.objects.filter(
        situation_type=situation_type,
        started_at__gte=now - timedelta(days=30)
    ).count()

    # Calculate success rate
    total_sessions = AutonomousSituationSession.objects.filter(
        situation_type=situation_type,
        started_at__gte=now - timedelta(days=30)
    ).count()
    successful_sessions = AutonomousSituationSession.objects.filter(
        situation_type=situation_type,
        started_at__gte=now - timedelta(days=30),
        status='completed'
    ).count()
    success_rate = (successful_sessions / total_sessions * 100) if total_sessions > 0 else 0

    # Get trigger count for this situation
    trigger_count = SituationTrigger.objects.filter(
        situation_type=situation_type,
        is_active=True
    ).count()

    # Get recent trigger events
    recent_trigger_fires = TriggerEvent.objects.filter(
        trigger__situation_type=situation_type,
        fired_at__gte=now - timedelta(hours=24)
    ).count()

    # Determine status
    if last_session:
        if last_session.status == 'failed':
            status = 'error'
        elif last_session.status == 'running':
            status = 'running'
        else:
            # Check if it's stale (hasn't run when expected)
            status = 'active'
    else:
        status = 'inactive'

    return {
        'type': situation_type,
        'name': info.get('name', situation_type),
        'domain': info.get('domain', 'unknown'),
        'domain_color': DOMAIN_COLORS.get(info.get('domain', ''), '#6B7280'),
        'description': info.get('description', ''),
        'schedule': info.get('schedule', 'Unknown'),
        'celery_task': info.get('celery_task', ''),
        'status': status,
        'last_run': last_session.started_at.isoformat() if last_session else None,
        'last_run_status': last_session.status if last_session else None,
        'last_run_duration': last_session.duration_seconds if last_session else None,
        'next_run': None,  # Would need to query Celery Beat
        'runs_24h': runs_24h,
        'runs_7d': runs_7d,
        'runs_30d': runs_30d,
        'success_rate': round(success_rate, 1),
        'trigger_count': trigger_count,
        'trigger_fires_24h': recent_trigger_fires,
        'items_processed': last_session.items_processed if last_session else 0,
        'items_created': last_session.items_created if last_session else 0,
        'alerts_generated': last_session.alerts_generated if last_session else 0,
    }


# =============================================================================
# API ENDPOINTS
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def list_situations(request):
    """
    GET /api/autonomous/situations/

    List all 19 autonomous situations with their current status.
    """
    try:
        situations = []
        for situation_type in SITUATION_CATALOG.keys():
            situations.append(get_situation_status(situation_type))

        # Sort by domain, then by name
        situations.sort(key=lambda x: (x['domain'], x['name']))

        # Group by domain for frontend
        by_domain = {}
        for s in situations:
            domain = s['domain']
            if domain not in by_domain:
                by_domain[domain] = {
                    'name': domain.title(),
                    'color': DOMAIN_COLORS.get(domain, '#6B7280'),
                    'situations': [],
                    'total_runs_24h': 0,
                    'active_count': 0,
                }
            by_domain[domain]['situations'].append(s)
            by_domain[domain]['total_runs_24h'] += s['runs_24h']
            if s['status'] in ['active', 'running']:
                by_domain[domain]['active_count'] += 1

        return JsonResponse({
            'success': True,
            'situations': situations,
            'by_domain': by_domain,
            'total_count': len(situations),
        })
    except Exception as e:
        logger.exception("Error listing situations")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def situation_detail(request, situation_type):
    """
    GET /api/autonomous/situations/<type>/

    Get detailed information about a specific situation.
    """
    try:
        if situation_type not in SITUATION_CATALOG:
            return JsonResponse({
                'success': False,
                'error': f'Unknown situation type: {situation_type}'
            }, status=404)

        status = get_situation_status(situation_type)

        # Get recent sessions
        recent_sessions = AutonomousSituationSession.objects.filter(
            situation_type=situation_type
        ).order_by('-started_at')[:10]

        status['recent_sessions'] = [
            {
                'id': str(s.id),
                'started_at': s.started_at.isoformat(),
                'completed_at': s.completed_at.isoformat() if s.completed_at else None,
                'status': s.status,
                'duration_seconds': s.duration_seconds,
                'items_processed': s.items_processed,
                'items_created': s.items_created,
                'alerts_generated': s.alerts_generated,
                'error_message': s.error_message,
            }
            for s in recent_sessions
        ]

        # Get triggers for this situation
        triggers = SituationTrigger.objects.filter(
            situation_type=situation_type
        ).order_by('-priority')

        status['triggers'] = [
            {
                'id': str(t.id),
                'name': t.name,
                'trigger_type': t.trigger_type,
                'trigger_type_display': t.get_trigger_type_display(),
                'severity': t.severity,
                'is_active': t.is_active,
                'total_fires': t.total_fires,
                'last_triggered_at': t.last_triggered_at.isoformat() if t.last_triggered_at else None,
                'cooldown_minutes': t.cooldown_minutes,
                'is_on_cooldown': t.is_on_cooldown(),
            }
            for t in triggers
        ]

        return JsonResponse({'success': True, 'situation': status})
    except Exception as e:
        logger.exception(f"Error getting situation detail for {situation_type}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_situation(request, situation_type):
    """
    POST /api/autonomous/situations/<type>/toggle/

    Enable or disable a situation.
    Note: This requires Celery Beat dynamic schedule modification.
    For now, we track the intent but actual schedule changes need admin.
    """
    try:
        if situation_type not in SITUATION_CATALOG:
            return JsonResponse({
                'success': False,
                'error': f'Unknown situation type: {situation_type}'
            }, status=404)

        # For now, just acknowledge - actual implementation requires
        # dynamic Celery Beat schedule modification
        return JsonResponse({
            'success': True,
            'message': f'Toggle request received for {situation_type}. Manual admin action required to modify Celery Beat schedule.',
            'situation_type': situation_type,
        })
    except Exception as e:
        logger.exception(f"Error toggling situation {situation_type}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_situation_now(request, situation_type):
    """
    POST /api/autonomous/situations/<type>/run-now/

    Manually trigger a situation to run immediately.
    """
    try:
        if situation_type not in SITUATION_CATALOG:
            return JsonResponse({
                'success': False,
                'error': f'Unknown situation type: {situation_type}'
            }, status=404)

        info = SITUATION_CATALOG[situation_type]
        celery_task = info.get('celery_task')

        if not celery_task:
            return JsonResponse({
                'success': False,
                'error': f'No Celery task configured for {situation_type}'
            }, status=400)

        # Import and trigger the Celery task
        from celery import current_app
        task = current_app.send_task(celery_task)

        return JsonResponse({
            'success': True,
            'message': f'Triggered {info["name"]} to run now',
            'task_id': task.id,
            'situation_type': situation_type,
        })
    except Exception as e:
        logger.exception(f"Error running situation {situation_type}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_triggers(request):
    """
    GET /api/autonomous/triggers/

    List all configured triggers.
    """
    try:
        # Optional filters
        situation_type = request.GET.get('situation_type')
        is_active = request.GET.get('is_active')

        queryset = SituationTrigger.objects.all()

        if situation_type:
            queryset = queryset.filter(situation_type=situation_type)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        queryset = queryset.order_by('-priority', 'name')

        triggers = [
            {
                'id': str(t.id),
                'name': t.name,
                'description': t.description,
                'situation_type': t.situation_type,
                'situation_type_display': t.get_situation_type_display(),
                'trigger_type': t.trigger_type,
                'trigger_type_display': t.get_trigger_type_display(),
                'target_field': t.target_field,
                'operator': t.operator,
                'threshold_value': t.threshold_value,
                'severity': t.severity,
                'is_active': t.is_active,
                'priority': t.priority,
                'total_fires': t.total_fires,
                'total_alerts_generated': t.total_alerts_generated,
                'last_triggered_at': t.last_triggered_at.isoformat() if t.last_triggered_at else None,
                'cooldown_minutes': t.cooldown_minutes,
                'is_on_cooldown': t.is_on_cooldown(),
            }
            for t in queryset
        ]

        # Group by situation type
        by_situation = {}
        for t in triggers:
            st = t['situation_type']
            if st not in by_situation:
                by_situation[st] = []
            by_situation[st].append(t)

        return JsonResponse({
            'success': True,
            'triggers': triggers,
            'by_situation': by_situation,
            'total_count': len(triggers),
            'active_count': sum(1 for t in triggers if t['is_active']),
        })
    except Exception as e:
        logger.exception("Error listing triggers")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def list_trigger_events(request):
    """
    GET /api/autonomous/trigger-events/

    List recent trigger fire events.
    Query params:
    - limit: Number of events (default 50, max 200)
    - situation_type: Filter by situation
    - severity: Filter by severity
    - hours: Time range in hours (default 24)
    """
    try:
        limit = min(int(request.GET.get('limit', 50)), 200)
        situation_type = request.GET.get('situation_type')
        severity = request.GET.get('severity')
        hours = int(request.GET.get('hours', 24))

        queryset = TriggerEvent.objects.select_related('trigger').filter(
            fired_at__gte=timezone.now() - timedelta(hours=hours)
        )

        if situation_type:
            queryset = queryset.filter(trigger__situation_type=situation_type)
        if severity:
            queryset = queryset.filter(trigger__severity=severity)

        queryset = queryset.order_by('-fired_at')[:limit]

        events = []
        for e in queryset:
            # Session 539: Extract article URL from raw_data_snapshot
            article_url = None
            if e.raw_data_snapshot:
                # Try to find the matched item in the items array
                items = e.raw_data_snapshot.get('items', [])
                for item in items:
                    item_title = item.get('title', '')
                    if item_title and e.matched_value and item_title in e.matched_value:
                        article_url = item.get('link') or item.get('url') or item.get('href')
                        break
                # If not found in items, check top-level
                if not article_url:
                    article_url = e.raw_data_snapshot.get('link') or e.raw_data_snapshot.get('url')

            events.append({
                'id': str(e.id),
                'trigger_id': str(e.trigger.id),
                'trigger_name': e.trigger.name,
                'trigger_type': e.trigger.trigger_type,
                'situation_type': e.trigger.situation_type,
                'severity': e.trigger.severity,
                'spider_name': e.spider_name,
                'matched_field': e.matched_field,
                'matched_value': e.matched_value,
                'article_url': article_url,  # Session 539: Direct link to article
                'status': e.status,
                'alert_generated': e.alert_generated,
                'discord_sent': e.discord_sent,
                'fired_at': e.fired_at.isoformat(),
            })

        # Stats
        now = timezone.now()
        stats = {
            'total_events': len(events),
            'by_severity': {},
            'by_situation': {},
        }

        for e in events:
            sev = e['severity']
            sit = e['situation_type']
            stats['by_severity'][sev] = stats['by_severity'].get(sev, 0) + 1
            stats['by_situation'][sit] = stats['by_situation'].get(sit, 0) + 1

        return JsonResponse({
            'success': True,
            'events': events,
            'stats': stats,
            'time_range_hours': hours,
        })
    except Exception as e:
        logger.exception("Error listing trigger events")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def analytics_summary(request):
    """
    GET /api/autonomous/analytics/summary/

    Get summary analytics for the dashboard.
    """
    try:
        now = timezone.now()

        # Situation stats
        total_situations = len(SITUATION_CATALOG)

        # Recent runs
        runs_24h = AutonomousSituationSession.objects.filter(
            started_at__gte=now - timedelta(hours=24)
        ).count()
        runs_7d = AutonomousSituationSession.objects.filter(
            started_at__gte=now - timedelta(days=7)
        ).count()

        # Success rate
        completed_24h = AutonomousSituationSession.objects.filter(
            started_at__gte=now - timedelta(hours=24),
            status='completed'
        ).count()
        success_rate = (completed_24h / runs_24h * 100) if runs_24h > 0 else 0

        # Failed situations
        failed_24h = AutonomousSituationSession.objects.filter(
            started_at__gte=now - timedelta(hours=24),
            status='failed'
        ).count()

        # Trigger stats
        total_triggers = SituationTrigger.objects.count()
        active_triggers = SituationTrigger.objects.filter(is_active=True).count()

        trigger_fires_24h = TriggerEvent.objects.filter(
            fired_at__gte=now - timedelta(hours=24)
        ).count()
        trigger_fires_7d = TriggerEvent.objects.filter(
            fired_at__gte=now - timedelta(days=7)
        ).count()

        # Alerts sent
        alerts_24h = TriggerEvent.objects.filter(
            fired_at__gte=now - timedelta(hours=24),
            alert_generated=True
        ).count()
        discord_sent_24h = TriggerEvent.objects.filter(
            fired_at__gte=now - timedelta(hours=24),
            discord_sent=True
        ).count()

        # By domain
        domain_stats = {}
        for sit_type, info in SITUATION_CATALOG.items():
            domain = info['domain']
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'name': domain.title(),
                    'color': DOMAIN_COLORS.get(domain, '#6B7280'),
                    'situations': 0,
                    'runs_24h': 0,
                    'triggers': 0,
                    'trigger_fires_24h': 0,
                }
            domain_stats[domain]['situations'] += 1
            domain_stats[domain]['runs_24h'] += AutonomousSituationSession.objects.filter(
                situation_type=sit_type,
                started_at__gte=now - timedelta(hours=24)
            ).count()
            domain_stats[domain]['triggers'] += SituationTrigger.objects.filter(
                situation_type=sit_type,
                is_active=True
            ).count()
            domain_stats[domain]['trigger_fires_24h'] += TriggerEvent.objects.filter(
                trigger__situation_type=sit_type,
                fired_at__gte=now - timedelta(hours=24)
            ).count()

        # Most active situations (last 24h)
        most_active = AutonomousSituationSession.objects.filter(
            started_at__gte=now - timedelta(hours=24)
        ).values('situation_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        most_active_list = [
            {
                'situation_type': item['situation_type'],
                'name': SITUATION_CATALOG.get(item['situation_type'], {}).get('name', item['situation_type']),
                'runs': item['count'],
            }
            for item in most_active
        ]

        # Recent critical events
        critical_events = TriggerEvent.objects.filter(
            trigger__severity='critical',
            fired_at__gte=now - timedelta(hours=24)
        ).select_related('trigger').order_by('-fired_at')[:5]

        critical_list = [
            {
                'id': str(e.id),
                'trigger_name': e.trigger.name,
                'matched_value': e.matched_value[:100],
                'fired_at': e.fired_at.isoformat(),
            }
            for e in critical_events
        ]

        return JsonResponse({
            'success': True,
            'summary': {
                'total_situations': total_situations,
                'runs_24h': runs_24h,
                'runs_7d': runs_7d,
                'success_rate': round(success_rate, 1),
                'failed_24h': failed_24h,
                'total_triggers': total_triggers,
                'active_triggers': active_triggers,
                'trigger_fires_24h': trigger_fires_24h,
                'trigger_fires_7d': trigger_fires_7d,
                'alerts_24h': alerts_24h,
                'discord_sent_24h': discord_sent_24h,
            },
            'by_domain': domain_stats,
            'most_active': most_active_list,
            'critical_events': critical_list,
        })
    except Exception as e:
        logger.exception("Error getting analytics summary")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Session 484: TRIGGER TUNING API ENDPOINTS
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def trigger_detail(request, trigger_id):
    """
    GET /api/autonomous/triggers/<trigger_id>/

    Get detailed info for a single trigger including recent events.
    """
    try:
        trigger = SituationTrigger.objects.get(id=trigger_id)

        # Get recent events for this trigger
        recent_events = TriggerEvent.objects.filter(
            trigger=trigger
        ).order_by('-fired_at')[:20]

        events_list = [
            {
                'id': str(e.id),
                'spider_name': e.spider_name,
                'matched_value': e.matched_value[:200],
                'status': e.status,
                'alert_generated': e.alert_generated,
                'discord_sent': e.discord_sent,
                'fired_at': e.fired_at.isoformat(),
            }
            for e in recent_events
        ]

        # Fire frequency stats
        now = timezone.now()
        fires_1h = TriggerEvent.objects.filter(
            trigger=trigger,
            fired_at__gte=now - timedelta(hours=1)
        ).count()
        fires_24h = TriggerEvent.objects.filter(
            trigger=trigger,
            fired_at__gte=now - timedelta(hours=24)
        ).count()
        fires_7d = TriggerEvent.objects.filter(
            trigger=trigger,
            fired_at__gte=now - timedelta(days=7)
        ).count()
        fires_30d = TriggerEvent.objects.filter(
            trigger=trigger,
            fired_at__gte=now - timedelta(days=30)
        ).count()

        return JsonResponse({
            'success': True,
            'trigger': {
                'id': str(trigger.id),
                'name': trigger.name,
                'description': trigger.description,
                'situation_type': trigger.situation_type,
                'situation_type_display': trigger.get_situation_type_display(),
                'trigger_type': trigger.trigger_type,
                'trigger_type_display': trigger.get_trigger_type_display(),
                'target_spiders': trigger.target_spiders,
                'target_field': trigger.target_field,
                'operator': trigger.operator,
                'operator_display': trigger.get_operator_display(),
                'threshold_value': trigger.threshold_value,
                'severity': trigger.severity,
                'alert_title_template': trigger.alert_title_template,
                'cooldown_minutes': trigger.cooldown_minutes,
                'is_active': trigger.is_active,
                'priority': trigger.priority,
                'total_fires': trigger.total_fires,
                'total_alerts_generated': trigger.total_alerts_generated,
                'last_triggered_at': trigger.last_triggered_at.isoformat() if trigger.last_triggered_at else None,
                'is_on_cooldown': trigger.is_on_cooldown(),
                'created_at': trigger.created_at.isoformat(),
                'updated_at': trigger.updated_at.isoformat(),
            },
            'recent_events': events_list,
            'fire_stats': {
                'fires_1h': fires_1h,
                'fires_24h': fires_24h,
                'fires_7d': fires_7d,
                'fires_30d': fires_30d,
            },
        })
    except SituationTrigger.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Trigger not found'}, status=404)
    except Exception as e:
        logger.exception(f"Error getting trigger detail: {trigger_id}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_trigger(request, trigger_id):
    """
    POST /api/autonomous/triggers/<trigger_id>/update/

    Update trigger configuration.
    Allowed fields: threshold_value, cooldown_minutes, severity, priority,
                   is_active, description, alert_title_template
    """
    try:
        trigger = SituationTrigger.objects.get(id=trigger_id)

        data = json.loads(request.body) if request.body else {}

        # Allowed editable fields
        editable_fields = [
            'threshold_value', 'cooldown_minutes', 'severity', 'priority',
            'is_active', 'description', 'alert_title_template'
        ]

        updated_fields = []

        for field in editable_fields:
            if field in data:
                value = data[field]

                # Validate specific fields
                if field == 'cooldown_minutes':
                    value = max(1, min(1440, int(value)))  # 1 min to 24 hours
                elif field == 'priority':
                    value = max(0, min(100, int(value)))  # 0-100
                elif field == 'severity':
                    if value not in ['critical', 'high', 'medium', 'low']:
                        continue
                elif field == 'is_active':
                    value = bool(value)

                setattr(trigger, field, value)
                updated_fields.append(field)

        if updated_fields:
            trigger.save()
            logger.info(f"Trigger {trigger.name} updated: {updated_fields}")

        return JsonResponse({
            'success': True,
            'message': f"Updated {len(updated_fields)} field(s)",
            'updated_fields': updated_fields,
            'trigger': {
                'id': str(trigger.id),
                'name': trigger.name,
                'threshold_value': trigger.threshold_value,
                'cooldown_minutes': trigger.cooldown_minutes,
                'severity': trigger.severity,
                'priority': trigger.priority,
                'is_active': trigger.is_active,
            }
        })
    except SituationTrigger.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Trigger not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception(f"Error updating trigger: {trigger_id}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_trigger(request, trigger_id):
    """
    POST /api/autonomous/triggers/<trigger_id>/toggle/

    Toggle trigger active status.
    """
    try:
        trigger = SituationTrigger.objects.get(id=trigger_id)

        trigger.is_active = not trigger.is_active
        trigger.save(update_fields=['is_active', 'updated_at'])

        status = 'enabled' if trigger.is_active else 'disabled'
        logger.info(f"Trigger {trigger.name} {status}")

        return JsonResponse({
            'success': True,
            'message': f"Trigger {status}",
            'trigger': {
                'id': str(trigger.id),
                'name': trigger.name,
                'is_active': trigger.is_active,
            }
        })
    except SituationTrigger.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Trigger not found'}, status=404)
    except Exception as e:
        logger.exception(f"Error toggling trigger: {trigger_id}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reset_trigger_cooldown(request, trigger_id):
    """
    POST /api/autonomous/triggers/<trigger_id>/reset-cooldown/

    Reset the cooldown timer for a trigger.
    """
    try:
        trigger = SituationTrigger.objects.get(id=trigger_id)

        trigger.last_triggered_at = None
        trigger.save(update_fields=['last_triggered_at', 'updated_at'])

        logger.info(f"Trigger {trigger.name} cooldown reset")

        return JsonResponse({
            'success': True,
            'message': "Cooldown reset",
            'trigger': {
                'id': str(trigger.id),
                'name': trigger.name,
                'is_on_cooldown': False,
            }
        })
    except SituationTrigger.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Trigger not found'}, status=404)
    except Exception as e:
        logger.exception(f"Error resetting trigger cooldown: {trigger_id}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def trigger_analytics(request, trigger_id):
    """
    GET /api/autonomous/triggers/<trigger_id>/analytics/

    Get detailed analytics for a specific trigger.
    """
    try:
        trigger = SituationTrigger.objects.get(id=trigger_id)
        now = timezone.now()

        # Hourly breakdown for last 24 hours
        hourly_fires = []
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            count = TriggerEvent.objects.filter(
                trigger=trigger,
                fired_at__gte=hour_start,
                fired_at__lt=hour_end
            ).count()
            hourly_fires.append({
                'hour': hour_start.strftime('%H:%M'),
                'count': count
            })
        hourly_fires.reverse()

        # Daily breakdown for last 30 days
        daily_fires = []
        for i in range(30):
            day_start = (now - timedelta(days=i+1)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            count = TriggerEvent.objects.filter(
                trigger=trigger,
                fired_at__gte=day_start,
                fired_at__lt=day_end
            ).count()
            daily_fires.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': count
            })
        daily_fires.reverse()

        # Top matched values
        top_values = TriggerEvent.objects.filter(
            trigger=trigger,
            fired_at__gte=now - timedelta(days=7)
        ).values('matched_value').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Alert vs no-alert ratio
        total_events = TriggerEvent.objects.filter(trigger=trigger).count()
        alerts_generated = TriggerEvent.objects.filter(trigger=trigger, alert_generated=True).count()
        discord_sent = TriggerEvent.objects.filter(trigger=trigger, discord_sent=True).count()

        # Spider breakdown
        spider_breakdown = TriggerEvent.objects.filter(
            trigger=trigger,
            fired_at__gte=now - timedelta(days=7)
        ).values('spider_name').annotate(
            count=Count('id')
        ).order_by('-count')

        return JsonResponse({
            'success': True,
            'trigger_id': str(trigger.id),
            'trigger_name': trigger.name,
            'analytics': {
                'hourly_fires': hourly_fires,
                'daily_fires': daily_fires,
                'top_matched_values': list(top_values),
                'spider_breakdown': list(spider_breakdown),
                'totals': {
                    'total_fires': trigger.total_fires,
                    'alerts_generated': alerts_generated,
                    'discord_sent': discord_sent,
                    'alert_rate': round(alerts_generated / total_events * 100, 1) if total_events > 0 else 0,
                }
            }
        })
    except SituationTrigger.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Trigger not found'}, status=404)
    except Exception as e:
        logger.exception(f"Error getting trigger analytics: {trigger_id}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# ORPHAN DATA SURFACES — Predictions & Analyses
# =============================================================================

@require_http_methods(["GET"])
def viral_predictions_api(request):
    """GET /api/autonomous/viral-predictions/ — Surface ViralContentPrediction data."""
    try:
        limit = min(int(request.GET.get('limit', 50)), 200)
        offset = int(request.GET.get('offset', 0))
        min_score = float(request.GET.get('min_score', 0))

        qs = ViralContentPrediction.objects.all()
        if min_score > 0:
            qs = qs.filter(viral_score__gte=min_score)

        total = qs.count()
        items = list(
            qs.order_by('-viral_score', '-created_at')[offset:offset + limit]
            .values(
                'id', 'title', 'content_type', 'topic', 'keywords',
                'viral_score', 'engagement_potential', 'shareability_score',
                'timing_score', 'trend_alignment', 'emotional_trigger',
                'recommended_platforms', 'suggested_hashtags',
                'created_at', 'prediction_expires', 'content_created',
            )
        )

        return JsonResponse({
            'success': True,
            'total': total,
            'items': items,
            'offset': offset,
            'limit': limit,
        })
    except Exception as e:
        logger.exception("Error fetching viral predictions")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def skill_gap_api(request):
    """GET /api/autonomous/skill-gaps/ — Surface SkillGapAnalysis data."""
    try:
        limit = min(int(request.GET.get('limit', 50)), 200)
        offset = int(request.GET.get('offset', 0))
        category = request.GET.get('category', '')

        qs = SkillGapAnalysis.objects.all()
        if category:
            qs = qs.filter(category=category)

        total = qs.count()
        items = list(
            qs.order_by('-demand_score')[offset:offset + limit]
            .values(
                'id', 'skill_name', 'category', 'demand_score',
                'demand_trend', 'avg_salary_premium', 'gap_score',
                'estimated_learning_time', 'source_spiders',
                'analyzed_at',
            )
        )

        return JsonResponse({
            'success': True,
            'total': total,
            'items': items,
            'offset': offset,
            'limit': limit,
        })
    except Exception as e:
        logger.exception("Error fetching skill gaps")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
