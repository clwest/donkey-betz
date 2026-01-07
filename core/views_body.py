"""
Session 710: Body Health Dashboard API Views

Unified API endpoints for the Body Health Dashboard.
Aggregates data from all 7 body systems into a single interface.
"""

import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone

logger = logging.getLogger(__name__)


@require_GET
def body_vitals_view(request):
    """
    GET /api/body/vitals/

    Returns unified health status for all 7 body systems.

    Query params:
        include_details: bool - Include detailed metrics per system
    """
    try:
        from core.services.body_vitals import get_body_vitals_service

        service = get_body_vitals_service()
        include_details = request.GET.get('include_details', 'false').lower() == 'true'

        vitals = service.get_all_vitals(include_details=include_details)

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            **vitals
        })
    except Exception as e:
        logger.error(f"Error getting body vitals: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def body_alerts_view(request):
    """
    GET /api/body/alerts/

    Returns all active alerts from body systems.

    Query params:
        severity: str - Filter by severity (info, warning, critical)
        limit: int - Max number of alerts to return
    """
    try:
        from core.services.body_vitals import get_body_vitals_service

        service = get_body_vitals_service()
        severity_threshold = request.GET.get('severity', 'info')
        limit = int(request.GET.get('limit', '50'))

        alerts = service.get_alerts(severity_threshold=severity_threshold)

        # Apply limit
        alerts = alerts[:limit]

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'count': len(alerts),
            'alerts': alerts
        })
    except Exception as e:
        logger.error(f"Error getting body alerts: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def body_history_view(request):
    """
    GET /api/body/history/

    Returns historical health data for trend analysis.

    Query params:
        hours: int - Hours of history to return (default 24)
        system: str - Filter to specific system (optional)
    """
    try:
        hours = int(request.GET.get('hours', '24'))
        system_filter = request.GET.get('system')

        history = []
        cutoff = timezone.now() - timedelta(hours=hours)

        # Collect history from each body system
        systems_data = {}

        # HEART history
        try:
            from core.models_heart import HeartPulse
            heart_pulses = HeartPulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('recorded_at').values(
                'recorded_at', 'overall_status', 'health_score'
            )[:100]
            systems_data['heart'] = [
                {
                    'timestamp': p['recorded_at'].isoformat(),
                    'status': p['overall_status'],
                    'score': float(p['health_score'])
                }
                for p in heart_pulses
            ]
        except Exception as e:
            logger.warning(f"Could not get HEART history: {e}")
            systems_data['heart'] = []

        # LUNGS history
        try:
            from core.models_lungs import LungsPulse
            lungs_pulses = LungsPulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('recorded_at').values(
                'recorded_at', 'overall_status', 'oxygen_level'
            )[:100]
            systems_data['lungs'] = [
                {
                    'timestamp': p['recorded_at'].isoformat(),
                    'status': p['overall_status'],
                    'score': float(p['oxygen_level'])
                }
                for p in lungs_pulses
            ]
        except Exception as e:
            logger.warning(f"Could not get LUNGS history: {e}")
            systems_data['lungs'] = []

        # CIRCULATORY history
        try:
            from core.models_circulatory import CirculatoryPulse
            circ_pulses = CirculatoryPulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('recorded_at').values(
                'recorded_at', 'overall_status', 'flow_score'
            )[:100]
            systems_data['circulatory'] = [
                {
                    'timestamp': p['recorded_at'].isoformat(),
                    'status': p['overall_status'],
                    'score': float(p['flow_score'])
                }
                for p in circ_pulses
            ]
        except Exception as e:
            logger.warning(f"Could not get CIRCULATORY history: {e}")
            systems_data['circulatory'] = []

        # SPINE history
        try:
            from core.models_spine import SpinePulse
            spine_pulses = SpinePulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('recorded_at').values(
                'recorded_at', 'overall_status', 'alignment_score'
            )[:100]
            systems_data['spine'] = [
                {
                    'timestamp': p['recorded_at'].isoformat(),
                    'status': p['overall_status'],
                    'score': float(p['alignment_score'])
                }
                for p in spine_pulses
            ]
        except Exception as e:
            logger.warning(f"Could not get SPINE history: {e}")
            systems_data['spine'] = []

        # IMMUNE history
        try:
            from core.models_immune import ImmunePulse
            immune_pulses = ImmunePulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('recorded_at').values(
                'recorded_at', 'overall_status', 'immune_score'
            )[:100]
            systems_data['immune'] = [
                {
                    'timestamp': p['recorded_at'].isoformat(),
                    'status': p['overall_status'],
                    'score': float(p['immune_score'])
                }
                for p in immune_pulses
            ]
        except Exception as e:
            logger.warning(f"Could not get IMMUNE history: {e}")
            systems_data['immune'] = []

        # DIGESTIVE history
        try:
            from core.models_digestive import DigestivePulse
            digestive_pulses = DigestivePulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('recorded_at').values(
                'recorded_at', 'overall_status', 'digestion_score'
            )[:100]
            systems_data['digestive'] = [
                {
                    'timestamp': p['recorded_at'].isoformat(),
                    'status': p['overall_status'],
                    'score': float(p['digestion_score'])
                }
                for p in digestive_pulses
            ]
        except Exception as e:
            logger.warning(f"Could not get DIGESTIVE history: {e}")
            systems_data['digestive'] = []

        # MUSCULAR history
        try:
            from core.models_muscular import MuscularPulse
            muscular_pulses = MuscularPulse.objects.filter(
                recorded_at__gte=cutoff
            ).order_by('recorded_at').values(
                'recorded_at', 'overall_status', 'strength_score'
            )[:100]
            systems_data['muscular'] = [
                {
                    'timestamp': p['recorded_at'].isoformat(),
                    'status': p['overall_status'],
                    'score': float(p['strength_score'])
                }
                for p in muscular_pulses
            ]
        except Exception as e:
            logger.warning(f"Could not get MUSCULAR history: {e}")
            systems_data['muscular'] = []

        # Filter to specific system if requested
        if system_filter and system_filter in systems_data:
            systems_data = {system_filter: systems_data[system_filter]}

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'hours': hours,
            'systems': systems_data
        })
    except Exception as e:
        logger.error(f"Error getting body history: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def body_system_detail_view(request, system_name: str):
    """
    GET /api/body/<system_name>/

    Returns detailed information for a specific body system.
    """
    try:
        from core.services.body_vitals import get_body_vitals_service

        service = get_body_vitals_service()
        vitals = service.get_system_vitals(system_name, include_details=True)

        if 'error' in vitals:
            return JsonResponse({
                'success': False,
                'error': vitals['error'],
                'valid_systems': vitals.get('valid_systems', [])
            }, status=400)

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'system': system_name,
            **vitals
        })
    except Exception as e:
        logger.error(f"Error getting {system_name} details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def body_summary_view(request):
    """
    GET /api/body/summary/

    Returns a compact summary suitable for status bars and headers.
    """
    try:
        from core.services.body_vitals import get_body_vitals_service

        service = get_body_vitals_service()
        vitals = service.get_all_vitals(include_details=False)

        # Create compact summary
        systems_summary = {}
        for name, data in vitals.get('systems', {}).items():
            systems_summary[name] = {
                'status': data.get('status', 'unknown'),
                'emoji': data.get('emoji', '❓'),
                'healthy': data.get('status') not in ['error', 'critical', 'blocked', 'paralyzed', 'compromised', 'starving']
            }

        # Count healthy vs unhealthy
        healthy_count = sum(1 for s in systems_summary.values() if s['healthy'])
        total_count = len(systems_summary)

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'overall_health': vitals.get('overall_health', 'unknown'),
            'health_score': vitals.get('health_score', 0),
            'healthy_systems': healthy_count,
            'total_systems': total_count,
            'systems': systems_summary,
            'alert_count': len(vitals.get('alerts', []))
        })
    except Exception as e:
        logger.error(f"Error getting body summary: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 711: Body Coordinator API Endpoints
# =============================================================================

@require_GET
def body_coordination_status_view(request):
    """
    GET /api/body/coordination/status/

    Returns the current body coordination status.
    """
    try:
        from core.services.body_coordinator import get_body_coordinator

        coordinator = get_body_coordinator()
        status = coordinator.get_status()

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            **status
        })
    except Exception as e:
        logger.error(f"Error getting coordination status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def body_coordination_run_view(request):
    """
    GET /api/body/coordination/run/

    Manually trigger a coordination check.
    """
    try:
        from core.services.body_coordinator import get_body_coordinator

        coordinator = get_body_coordinator()
        result = coordinator.coordinate(force=True)

        return JsonResponse({
            'success': True,
            **result
        })
    except Exception as e:
        logger.error(f"Error running coordination: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def body_coordination_log_view(request):
    """
    GET /api/body/coordination/log/

    Returns recent coordination responses.

    Query params:
        limit: int - Number of responses to return (default 20)
    """
    try:
        from core.services.body_coordinator import get_body_coordinator

        limit = int(request.GET.get('limit', '20'))
        coordinator = get_body_coordinator()
        log = coordinator.get_response_log(limit=limit)

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'count': len(log),
            'responses': log
        })
    except Exception as e:
        logger.error(f"Error getting coordination log: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def body_throttle_status_view(request):
    """
    GET /api/body/throttle/

    Returns the current throttle status.
    """
    try:
        from core.services.body_coordinator import get_body_coordinator

        coordinator = get_body_coordinator()

        return JsonResponse({
            'success': True,
            'timestamp': timezone.now().isoformat(),
            'is_throttled': coordinator.is_throttled(),
            'throttle_factor': coordinator.get_throttle_factor()
        })
    except Exception as e:
        logger.error(f"Error getting throttle status: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
