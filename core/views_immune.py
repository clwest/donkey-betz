"""
Session 705: IMMUNE SYSTEM - Security & Threat Detection Views

API endpoints for the IMMUNE service - the defense layer of the AI body.

Endpoints:
    GET  /api/immune/scan/              - Run full immune scan
    GET  /api/immune/status/            - Get cached immune status
    GET  /api/immune/patterns/          - List threat patterns
    GET  /api/immune/patterns/<id>/     - Get specific pattern
    GET  /api/immune/threats/           - Get recent threat events
    GET  /api/immune/quarantine/        - Get quarantine list
    POST /api/immune/quarantine/        - Add to quarantine
    DELETE /api/immune/quarantine/<id>/ - Release from quarantine
    GET  /api/immune/is-healthy/        - Quick health check
    POST /api/immune/check-request/     - Check if request is allowed
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def scan_view(request):
    """
    Run full immune system scan.

    GET /api/immune/scan/
    Query params:
        force (bool): Force fresh scan (ignore cache)

    Returns full immune status including threat counts, quarantine status,
    and pattern activity.
    """
    try:
        from core.services.immune import get_immune_system

        force = request.GET.get('force', 'false').lower() == 'true'

        immune = get_immune_system()
        result = immune.scan(force=force)

        return JsonResponse(result)

    except Exception as e:
        logger.exception(f"Error in immune scan: {e}")
        return JsonResponse({
            'error': str(e),
            'overall_status': 'compromised',
            'health_score': 0,
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def immune_status_view(request):
    """
    Get cached immune status.

    GET /api/immune/status/

    Returns current cached status without running a full scan.
    Use /scan/ for a fresh check.
    """
    try:
        from core.services.immune import get_immune_system

        immune = get_immune_system()
        vitals = immune.get_vitals()

        return JsonResponse(vitals)

    except Exception as e:
        logger.exception(f"Error getting immune status: {e}")
        return JsonResponse({
            'error': str(e),
            'overall_status': 'compromised',
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def patterns_list_view(request):
    """
    List threat patterns.

    GET /api/immune/patterns/
    Query params:
        category (str): Filter by category
        active (bool): Filter by active status (default: true)

    Returns list of all configured threat patterns.
    """
    try:
        from core.services.immune import get_immune_system

        category = request.GET.get('category')
        active_only = request.GET.get('active', 'true').lower() == 'true'

        immune = get_immune_system()
        patterns = immune.get_patterns(category=category, active_only=active_only)

        return JsonResponse({
            'count': len(patterns),
            'category_filter': category,
            'active_only': active_only,
            'patterns': patterns,
        })

    except Exception as e:
        logger.exception(f"Error listing patterns: {e}")
        return JsonResponse({
            'error': str(e),
            'patterns': [],
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pattern_detail_view(request, pattern_id):
    """
    Get specific threat pattern details.

    GET /api/immune/patterns/<uuid:pattern_id>/

    Returns pattern configuration and statistics.
    """
    try:
        from core.models_immune import ThreatPattern

        try:
            pattern = ThreatPattern.objects.get(pk=pattern_id)
        except ThreatPattern.DoesNotExist:
            return JsonResponse({
                'error': f'Pattern not found: {pattern_id}',
            }, status=404)

        return JsonResponse({
            'id': str(pattern.id),
            'name': pattern.name,
            'display_name': pattern.display_name,
            'category': pattern.category,
            'severity': pattern.severity,
            'detection_type': pattern.detection_type,
            'pattern': pattern.pattern,
            'description': pattern.description,
            'threshold_count': pattern.threshold_count,
            'threshold_window_seconds': pattern.threshold_window_seconds,
            'auto_respond': pattern.auto_respond,
            'response_action': pattern.response_action,
            'block_duration_minutes': pattern.block_duration_minutes,
            'is_active': pattern.is_active,
            'is_builtin': pattern.is_builtin,
            'total_detections': pattern.total_detections,
            'last_detection': pattern.last_detection.isoformat() if pattern.last_detection else None,
            'created_at': pattern.created_at.isoformat(),
            'updated_at': pattern.updated_at.isoformat(),
        })

    except Exception as e:
        logger.exception(f"Error getting pattern details: {e}")
        return JsonResponse({
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def threats_list_view(request):
    """
    Get recent threat events.

    GET /api/immune/threats/
    Query params:
        hours (int): Lookback period (default: 24)
        limit (int): Max records to return (default: 100)
        severity (str): Filter by severity
        category (str): Filter by category

    Returns list of recent threat events.
    """
    try:
        from core.services.immune import get_immune_system

        hours = int(request.GET.get('hours', 24))
        limit = int(request.GET.get('limit', 100))
        severity = request.GET.get('severity')
        category = request.GET.get('category')

        immune = get_immune_system()
        threats = immune.get_recent_threats(
            hours=hours,
            limit=limit,
            severity=severity,
            category=category,
        )

        return JsonResponse({
            'period_hours': hours,
            'count': len(threats),
            'severity_filter': severity,
            'category_filter': category,
            'threats': threats,
        })

    except Exception as e:
        logger.exception(f"Error listing threats: {e}")
        return JsonResponse({
            'error': str(e),
            'threats': [],
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def quarantine_list_view(request):
    """
    Get quarantine list or add to quarantine.

    GET /api/immune/quarantine/
    Query params:
        entity_type (str): Filter by type (ip, user, user_agent)
        active (bool): Filter by active status (default: true)

    POST /api/immune/quarantine/
    Body:
        entity_type (str): ip, user, or user_agent
        entity_value (str): The value to quarantine
        reason (str): Reason for quarantine
        duration_minutes (int): Duration (optional, 0 = permanent)
        notes (str): Additional notes
    """
    try:
        from core.services.immune import get_immune_system

        immune = get_immune_system()

        if request.method == 'GET':
            entity_type = request.GET.get('entity_type')
            active_only = request.GET.get('active', 'true').lower() == 'true'

            quarantine_list = immune.get_quarantine_list(
                entity_type=entity_type,
                active_only=active_only,
            )

            return JsonResponse({
                'count': len(quarantine_list),
                'entity_type_filter': entity_type,
                'active_only': active_only,
                'quarantine': quarantine_list,
            })

        else:  # POST
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON body',
                }, status=400)

            entity_type = data.get('entity_type')
            entity_value = data.get('entity_value')
            reason = data.get('reason', 'manual')
            duration_minutes = data.get('duration_minutes')
            notes = data.get('notes', '')

            if not entity_type or not entity_value:
                return JsonResponse({
                    'error': 'entity_type and entity_value are required',
                }, status=400)

            is_permanent = duration_minutes == 0 or duration_minutes is None

            if entity_type == 'ip':
                quarantine = immune.quarantine_ip(
                    ip=entity_value,
                    reason=reason,
                    duration_minutes=duration_minutes,
                    is_permanent=is_permanent,
                    notes=notes,
                )
            elif entity_type == 'user':
                quarantine = immune.quarantine_user(
                    user_id=int(entity_value),
                    reason=reason,
                    duration_minutes=duration_minutes,
                    is_permanent=is_permanent,
                    notes=notes,
                )
            else:
                return JsonResponse({
                    'error': f'Unsupported entity_type: {entity_type}',
                }, status=400)

            return JsonResponse({
                'success': True,
                'id': str(quarantine.id),
                'entity_type': quarantine.entity_type,
                'entity_value': quarantine.entity_value,
                'is_permanent': quarantine.is_permanent,
                'expires_at': quarantine.expires_at.isoformat() if quarantine.expires_at else None,
            })

    except Exception as e:
        logger.exception(f"Error with quarantine: {e}")
        return JsonResponse({
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def quarantine_release_view(request, entity_type, entity_value):
    """
    Release an entity from quarantine.

    DELETE /api/immune/quarantine/<entity_type>/<entity_value>/

    Returns success or failure status.
    """
    try:
        from core.services.immune import get_immune_system

        immune = get_immune_system()
        success = immune.release_from_quarantine(entity_type, entity_value)

        if success:
            return JsonResponse({
                'success': True,
                'message': f'Released {entity_type}:{entity_value} from quarantine',
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Entity not found in quarantine: {entity_type}:{entity_value}',
            }, status=404)

    except Exception as e:
        logger.exception(f"Error releasing from quarantine: {e}")
        return JsonResponse({
            'error': str(e),
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def is_healthy_view(request):
    """
    Quick health check - is the immune system healthy?

    GET /api/immune/is-healthy/

    Returns simple boolean status for health checks.
    """
    try:
        from core.services.immune import get_immune_system

        immune = get_immune_system()
        is_healthy = immune.is_healthy()
        emoji = immune.get_status_emoji()

        return JsonResponse({
            'is_healthy': is_healthy,
            'emoji': emoji,
            'message': 'Immune system healthy' if is_healthy else 'Immune system needs attention',
        })

    except Exception as e:
        logger.exception(f"Error checking immune health: {e}")
        return JsonResponse({
            'is_healthy': False,
            'emoji': '💀',
            'message': f'Error: {str(e)}',
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def check_request_view(request):
    """
    Check if a request should be allowed.

    POST /api/immune/check-request/
    Body:
        ip (str): Client IP address
        user_id (int): User ID (optional)
        user_agent (str): User agent string (optional)
        path (str): Request path (optional)

    Returns whether the request is allowed and reason.
    """
    try:
        from core.services.immune import get_immune_system

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON body',
            }, status=400)

        immune = get_immune_system()
        allowed, reason = immune.check_request(
            ip=data.get('ip'),
            user_id=data.get('user_id'),
            path=data.get('path'),
            user_agent=data.get('user_agent'),
        )

        return JsonResponse({
            'allowed': allowed,
            'reason': reason,
        })

    except Exception as e:
        logger.exception(f"Error checking request: {e}")
        return JsonResponse({
            'allowed': True,  # Fail open to avoid blocking legitimate traffic
            'reason': f'Error checking: {str(e)}',
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def categories_view(request):
    """
    Get threat statistics by category.

    GET /api/immune/categories/

    Returns breakdown of threats by category with counts.
    """
    try:
        from core.services.immune import get_immune_system

        immune = get_immune_system()
        vitals = immune.get_vitals()

        return JsonResponse({
            'threats_by_category': vitals.get('threats_by_category', {}),
            'threats_by_severity': vitals.get('threats_by_severity', {}),
        })

    except Exception as e:
        logger.exception(f"Error getting categories: {e}")
        return JsonResponse({
            'error': str(e),
            'threats_by_category': {},
            'threats_by_severity': {},
        }, status=500)
