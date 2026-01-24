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
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncHour

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
            ContentChannel, ChannelEpisode, TopicPerformance,
            ContentDebate
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
                'last_run': channel.last_content_created.isoformat() if channel.last_content_created else None,
                'next_run': channel.next_content_due.isoformat() if channel.next_content_due else None,
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
        top_topics = TopicPerformance.objects.order_by('-avg_performance_score')[:5]
        topic_data = [{
            'topic': tp.topic,
            'success_rate': float(tp.avg_performance_score) if tp.avg_performance_score else 0,
            'times_used': tp.episode_count,
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
            NarrativeAlert
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

        # Session 509: Include verification status and unique sources in shift data
        from urllib.parse import urlparse
        shift_data = []
        for s in recent_shifts:
            # Calculate unique sources for this shift's evidence
            unique_sources = 0
            if s.old_narrative:
                evidence = NarrativeEvidence.objects.filter(narrative=s.old_narrative)
                source_domains = set()
                for e in evidence:
                    if e.source_url:
                        try:
                            parsed = urlparse(e.source_url)
                            source_domains.add(parsed.netloc)
                        except Exception:
                            pass
                unique_sources = len(source_domains)

            shift_data.append({
                'id': str(s.id),
                'narrative': s.old_narrative.title if s.old_narrative else 'Unknown',
                'domain': s.domain,
                'importance': float(s.importance),
                'confidence': float(s.confidence),
                'verified': s.verified,
                'unique_sources': unique_sources,
                'detected_at': s.detected_at.isoformat(),
                'summary': s.shift_summary[:100] if s.shift_summary else '',
            })

        # Active alerts (not dismissed)
        active_alerts = NarrativeAlert.objects.filter(
            dismissed=False
        ).count()

        # Session 509: Mythology validation stats
        verified_shifts = NarrativeShift.objects.filter(verified=True).count()
        unverified_shifts = NarrativeShift.objects.filter(verified=False).count()

        # Get evidence with authoritative sources (rough count based on .gov/.edu)
        authoritative_evidence = NarrativeEvidence.objects.filter(
            source_url__icontains='.gov'
        ).count() + NarrativeEvidence.objects.filter(
            source_url__icontains='.edu'
        ).count()

        # Get mythology validator stats if available
        mythology_stats = {}
        try:
            from core.agents.narrative.narrative_mythology_validator import (
                narrative_mythology_validator
            )
            mythology_stats = narrative_mythology_validator.get_stats()
        except Exception:
            pass

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
                # Session 509: Mythology validation data
                'mythology': {
                    'verified_shifts': verified_shifts,
                    'unverified_shifts': unverified_shifts,
                    'authoritative_evidence': authoritative_evidence,
                    'total_evidence': NarrativeEvidence.objects.count(),
                    'validator_stats': mythology_stats,
                }
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
        from core.models_unified_system import SpiderData, Opportunity

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

        # Get avg opportunity score from Opportunity.overall_score field
        avg_score = Opportunity.objects.filter(
            created_at__gte=day_ago
        ).aggregate(avg=Avg('overall_score'))['avg'] or 0

        return JsonResponse({
            'success': True,
            'data': {
                'spider_data_24h': spider_24h,
                'spider_data_total': SpiderData.objects.count(),
                'spider_by_source': list(spider_by_source),
                'opportunities_24h': opportunities_24h,
                'opportunities_total': Opportunity.objects.count(),
                'opp_by_category': list(opp_by_category),
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
        from core.models_unified_system import ConversionEvent

        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        # Conversion funnel
        # Note: Database uses 'apply' not 'application'
        funnel_stages = ['view', 'click', 'apply', 'revenue']
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
        ).values('attribution_source').annotate(
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
            'hash': p.content_hash[:16] + '...' if hasattr(p, 'content_hash') and p.content_hash else None,
            'has_parent': bool(p.parent_id),
        } for p in recent]

        # Chain depth stats
        total_records = DataProvenance.objects.count()
        records_with_parent = DataProvenance.objects.filter(
            parent__isnull=False
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

    Session 477: Extended time window from 1 hour to 6 hours,
    plus fallback to show most recent items if window is empty.
    """
    try:
        from core.models_autonomous_studio import ChannelEpisode
        from core.models_narrative_drift import NarrativeEvidence, NarrativeShift
        from core.models_unified_system import SpiderData, ConversionEvent
        from core.models_situation_triggers import TriggerEvent
        from core.models_autonomous_alerts import BlockchainSecurityAlert, StockMarketAlert

        now = timezone.now()
        # Session 477: Extended from 1 hour to 6 hours for better visibility
        time_window = now - timedelta(hours=6)

        activities = []

        # Recent episodes (or most recent 3 if none in window)
        episodes = ChannelEpisode.objects.filter(publish_date__gte=time_window).order_by('-publish_date')[:5]
        if not episodes.exists():
            episodes = ChannelEpisode.objects.order_by('-publish_date')[:3]
        for ep in episodes:
            activities.append({
                'type': 'episode',
                'icon': '📺',
                'title': f"New episode: {ep.title[:50]}",
                'source': 'Content Studio',
                'timestamp': ep.publish_date.isoformat(),
            })

        # Recent evidence (or most recent 3 if none in window)
        evidence = NarrativeEvidence.objects.filter(created_at__gte=time_window).order_by('-created_at')[:5]
        if not evidence.exists():
            evidence = NarrativeEvidence.objects.order_by('-created_at')[:3]
        for ev in evidence:
            activities.append({
                'type': 'evidence',
                'icon': '📊',
                'title': f"Evidence for: {ev.narrative.title[:40] if ev.narrative else 'Unknown'}",
                'source': 'Narrative Drift',
                'timestamp': ev.created_at.isoformat(),
            })

        # Recent shifts
        for sh in NarrativeShift.objects.filter(detected_at__gte=time_window).order_by('-detected_at')[:3]:
            activities.append({
                'type': 'shift',
                'icon': '⚡',
                'title': f"Shift detected: {sh.shift_summary[:50] if sh.shift_summary else 'New shift'}",
                'source': 'Narrative Drift',
                'timestamp': sh.detected_at.isoformat(),
            })

        # Recent spider data (or most recent 5 if none in window)
        # Session 807: Defer embedding fields to reduce egress costs
        spider_data = SpiderData.objects.filter(created_at__gte=time_window).defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:10]
        if not spider_data.exists():
            spider_data = SpiderData.objects.defer('embedding', 'item_embeddings', 'embedding_text').order_by('-created_at')[:5]
        for sd in spider_data:
            activities.append({
                'type': 'spider',
                'icon': '🕷️',
                'title': f"Data from {sd.spider_name}: {sd.data_type or 'data'}",
                'source': 'Market Intelligence',
                'timestamp': sd.created_at.isoformat(),
            })

        # Recent conversions
        for ce in ConversionEvent.objects.filter(created_at__gte=time_window).order_by('-created_at')[:3]:
            activities.append({
                'type': 'conversion',
                'icon': '💰',
                'title': f"Conversion: {ce.event_type}",
                'source': 'ROI Tracking',
                'timestamp': ce.created_at.isoformat(),
            })

        # Session 477: Add trigger events (event-driven alerts)
        for te in TriggerEvent.objects.filter(fired_at__gte=time_window).order_by('-fired_at')[:5]:
            activities.append({
                'type': 'trigger',
                'icon': '🎯',
                'title': f"Trigger fired: {te.trigger.name}",
                'source': 'Event Triggers',
                'timestamp': te.fired_at.isoformat(),
            })

        # Session 477: Add blockchain alerts
        for ba in BlockchainSecurityAlert.objects.filter(detected_at__gte=time_window).order_by('-detected_at')[:3]:
            activities.append({
                'type': 'blockchain_alert',
                'icon': '🔗',
                'title': f"Blockchain Alert: {ba.title[:50]}",
                'source': 'Blockchain Security',
                'timestamp': ba.detected_at.isoformat(),
            })

        # Session 477: Add stock alerts
        for sa in StockMarketAlert.objects.filter(detected_at__gte=time_window).order_by('-detected_at')[:3]:
            activities.append({
                'type': 'stock_alert',
                'icon': '📈',
                'title': f"Stock Alert: {sa.title[:50]}",
                'source': 'Stock Intelligence',
                'timestamp': sa.detected_at.isoformat(),
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        return JsonResponse({
            'success': True,
            'data': {
                'activities': activities[:25],  # Increased from 20 to 25
                'count': len(activities),
                'time_window_hours': 6,
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


# ============================================================
# Session 497: ML Scoring Status API
# Session 511: Enhanced with training status, feature importance,
#              performance trends, model comparison, and SHAP explanations
# ============================================================

@require_GET
def api_ml_scoring_status(request):
    """
    Get ML Scoring Engine status.
    Returns model version, accuracy, feature importance, and recent predictions.

    Session 511 enhancements:
    - model_training: Training status with last trained, samples, can_train_now
    - feature_importance: Top 10 features from active model
    - performance_trends: R² and MSE over model versions
    - model_comparison: All model versions for comparison
    - recent_high_score: Enhanced with SHAP explanations
    """
    try:
        from core.models_unified_system import (
            Opportunity, OpportunityOutcome, MLModelVersion,
            ScoringExplanation
        )
        from core.services.ml_scoring_engine import get_ml_scoring_engine

        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)

        # Initialize scoring engine and get status
        engine = get_ml_scoring_engine()
        model_status = {
            'trained': engine.is_trained,
            'version': getattr(engine, 'model_version', 1),
        }

        # Get scoring statistics
        total_opportunities = Opportunity.objects.count()
        opportunities_24h = Opportunity.objects.filter(created_at__gte=day_ago).count()

        # Score distribution (last 7 days)
        recent_opportunities = Opportunity.objects.filter(
            created_at__gte=week_ago
        ).values('overall_score')

        score_distribution = {
            'high': 0,      # 70-100
            'medium': 0,    # 40-69
            'low': 0,       # 0-39
        }
        for opp in recent_opportunities:
            score = opp.get('overall_score') or 0
            if score >= 70:
                score_distribution['high'] += 1
            elif score >= 40:
                score_distribution['medium'] += 1
            else:
                score_distribution['low'] += 1

        # Get outcome statistics for model accuracy tracking
        outcome_counts = OpportunityOutcome.objects.values('outcome').annotate(
            count=Count('id')
        )
        outcome_map = {o['outcome']: o['count'] for o in outcome_counts}

        total_outcomes = sum(outcome_map.values())
        # Count successful outcomes (won, success, partial, partial_success)
        success_outcomes = (
            outcome_map.get('won', 0) +
            outcome_map.get('success', 0) +
            outcome_map.get('partial', 0) +
            outcome_map.get('partial_success', 0)
        )
        accuracy_estimate = round((success_outcomes / total_outcomes * 100), 1) if total_outcomes > 0 else 0

        # ============================================================
        # Session 511: Model Training Status
        # ============================================================
        active_model = MLModelVersion.objects.filter(is_active=True).first()
        model_training = {
            'last_trained': active_model.trained_at.isoformat() if active_model and active_model.trained_at else None,
            'training_samples': active_model.training_samples if active_model else 0,
            'training_duration_seconds': active_model.training_duration_seconds if active_model else 0,
            'min_samples_required': 100,
            'can_train_now': total_outcomes >= 100,
            'active_version': active_model.version if active_model else None,
        }

        # ============================================================
        # Session 511: Feature Importance from Active Model
        # ============================================================
        feature_importance = []
        if active_model and active_model.feature_importance:
            # feature_importance is stored as list of {'feature': name, 'importance': score}
            feature_importance = active_model.feature_importance[:10] if isinstance(
                active_model.feature_importance, list
            ) else []

        # ============================================================
        # Session 511: Performance Trends (all model versions)
        # ============================================================
        all_versions = MLModelVersion.objects.order_by('trained_at')[:10]
        performance_trends = [{
            'version': v.version,
            'trained_at': v.trained_at.isoformat() if v.trained_at else None,
            'test_r2': float(v.test_r2) if v.test_r2 is not None else None,
            'test_mse': float(v.test_mse) if v.test_mse is not None else None,
            'training_samples': v.training_samples,
        } for v in all_versions]

        # ============================================================
        # Session 511: Model Comparison
        # ============================================================
        all_versions_list = list(MLModelVersion.objects.order_by('-trained_at')[:5])
        model_comparison = {
            'versions_count': MLModelVersion.objects.count(),
            'active_version': active_model.version if active_model else None,
            'versions': [{
                'version': v.version,
                'is_active': v.is_active,
                'trained_at': v.trained_at.isoformat() if v.trained_at else None,
                'test_r2': float(v.test_r2) if v.test_r2 is not None else None,
                'test_mse': float(v.test_mse) if v.test_mse is not None else None,
                'training_samples': v.training_samples,
            } for v in all_versions_list]
        }

        # ============================================================
        # Session 511: Enhanced high-score opportunities with SHAP
        # ============================================================
        recent_high_score = Opportunity.objects.filter(
            created_at__gte=day_ago,
            overall_score__gte=70
        ).select_related('spider_data').order_by('-overall_score')[:5]

        high_score_data = []
        for opp in recent_high_score:
            opp_data = {
                'id': str(opp.id),
                'title': opp.title[:150] if opp.title else 'Untitled',
                'score': opp.overall_score or 0,
                'source': getattr(opp.spider_data, 'spider_name', 'Unknown') if opp.spider_data else 'Unknown',
                'created_at': opp.created_at.isoformat(),
                'explanation': None,
            }

            # Try to get SHAP explanation
            try:
                explanation = ScoringExplanation.objects.filter(
                    opportunity_id=opp.id
                ).first()
                if explanation:
                    opp_data['explanation'] = {
                        'top_positive': explanation.top_positive_features[:3] if explanation.top_positive_features else [],
                        'top_negative': explanation.top_negative_features[:2] if explanation.top_negative_features else [],
                        'confidence': float(explanation.confidence) if explanation.confidence else 0,
                        'ml_score': float(explanation.ml_score) if explanation.ml_score else 0,
                        'rule_score': float(explanation.rule_score) if explanation.rule_score else 0,
                    }
            except Exception:
                pass  # No explanation available

            high_score_data.append(opp_data)

        return JsonResponse({
            'success': True,
            'data': {
                'model_status': model_status,
                'total_opportunities': total_opportunities,
                'opportunities_24h': opportunities_24h,
                'score_distribution': score_distribution,
                'outcomes': {
                    'total': total_outcomes,
                    'breakdown': outcome_map,
                    'accuracy_estimate': accuracy_estimate,
                },
                'recent_high_score': high_score_data,
                'training_data_count': total_outcomes,
                'ready_for_training': total_outcomes >= 100,
                # Session 511 additions
                'model_training': model_training,
                'feature_importance': feature_importance,
                'performance_trends': performance_trends,
                'model_comparison': model_comparison,
            }
        })
    except Exception as e:
        logger.error(f"ML Scoring status error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================
# Session 511: ML Model Training Trigger
# ============================================================

@csrf_exempt
@require_POST
def api_ml_scoring_train(request):
    """
    Trigger ML model training manually.
    POST /api/monitoring/ml-scoring/train/

    Returns task_id for async training job.
    """
    import json
    try:
        from core.models_unified_system import OpportunityOutcome

        # Check if we have enough training data
        total_outcomes = OpportunityOutcome.objects.count()
        min_required = 100

        if total_outcomes < min_required:
            return JsonResponse({
                'success': False,
                'error': f'Insufficient training data: {total_outcomes} samples (need {min_required}+)'
            }, status=400)

        # Parse request body for options
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body = {}

        force_retrain = body.get('force_retrain', True)

        # Queue the training task
        from core.tasks import train_ml_scoring_model
        result = train_ml_scoring_model.delay(force_retrain=force_retrain)

        logger.info(f"ML model training triggered: task_id={result.id}")

        return JsonResponse({
            'success': True,
            'message': 'Training task queued successfully',
            'task_id': str(result.id),
            'training_samples': total_outcomes,
        })

    except Exception as e:
        logger.error(f"ML training trigger error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================
# Session 511: Score Explanation Endpoint
# ============================================================

@require_GET
def api_ml_scoring_explanation(request, opportunity_id):
    """
    Get detailed SHAP explanation for a specific opportunity.
    GET /api/monitoring/ml-scoring/opportunity/<uuid>/explanation/

    Returns full SHAP breakdown + rule reasoning.
    """
    try:
        from core.models_unified_system import (
            Opportunity, ScoringExplanation
        )

        # Get the opportunity
        try:
            opportunity = Opportunity.objects.select_related('spider_data').get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Opportunity not found'
            }, status=404)

        # Get the scoring explanation
        explanation = ScoringExplanation.objects.filter(
            opportunity_id=opportunity_id
        ).first()

        if not explanation:
            return JsonResponse({
                'success': False,
                'error': 'No ML explanation available for this opportunity'
            }, status=404)

        # Build feature details from SHAP values
        features = []
        if explanation.feature_names and explanation.shap_values:
            for i, name in enumerate(explanation.feature_names):
                shap_value = explanation.shap_values[i] if i < len(explanation.shap_values) else 0
                feature_value = explanation.feature_values[i] if explanation.feature_values and i < len(explanation.feature_values) else None
                features.append({
                    'name': name,
                    'value': feature_value,
                    'shap_value': round(float(shap_value), 4) if shap_value else 0,
                    'impact': 'positive' if shap_value and shap_value > 0 else 'negative'
                })

        # Sort by absolute SHAP value
        features.sort(key=lambda x: abs(x['shap_value']), reverse=True)

        return JsonResponse({
            'success': True,
            'data': {
                'opportunity_id': str(opportunity.id),
                'title': opportunity.title or 'Untitled',
                'source': getattr(opportunity.spider_data, 'spider_name', 'Unknown') if opportunity.spider_data else 'Unknown',
                'scores': {
                    'ml_score': round(float(explanation.ml_score), 2) if explanation.ml_score else 0,
                    'rule_score': round(float(explanation.rule_score), 2) if explanation.rule_score else 0,
                    'hybrid_score': round(float(explanation.hybrid_score), 2) if explanation.hybrid_score else 0,
                    'confidence': round(float(explanation.confidence), 2) if explanation.confidence else 0,
                },
                'shap_explanation': {
                    'base_value': round(float(explanation.shap_base_value), 4) if explanation.shap_base_value else 0,
                    'features': features,
                },
                'rule_reasoning': explanation.rule_reasoning or {},
                'model_version': explanation.model_version.version if explanation.model_version else 'unknown',
                'scored_at': explanation.created_at.isoformat() if explanation.created_at else None,
            }
        })

    except Exception as e:
        logger.error(f"ML explanation error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
