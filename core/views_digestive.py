"""
Session 706: DIGESTIVE SYSTEM - API Views

REST API endpoints for the DIGESTIVE system which monitors data ingestion
from spiders and transformation into actionable intelligence.

Endpoints:
- /api/digestive/digest/          - Run full digestion check
- /api/digestive/status/          - Get cached digestion status
- /api/digestive/routes/          - List all ingestion routes
- /api/digestive/routes/<id>/     - Get specific route status
- /api/digestive/bottlenecks/     - Get current bottlenecks
- /api/digestive/metabolism/      - Get throughput metrics
- /api/digestive/history/         - Get digestion pulse history
- /api/digestive/is-digesting/    - Quick alive check
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def digestive_digest_view(request):
    """
    Run full digestion check.

    GET /api/digestive/digest/
    Query params:
        - force: Force fresh check (ignore cache)

    Returns:
        Complete digestion status including all stages.
    """
    from core.services.digestive import get_digestive_system

    try:
        force = request.GET.get('force', '').lower() == 'true'
        digestive = get_digestive_system()
        result = digestive.digest(force=force)

        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error in digestive_digest_view: {e}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'overall_status': 'error',
            'is_digesting': False,
        }, status=500)


@require_http_methods(["GET"])
def digestive_status_view(request):
    """
    Get cached digestion status (fast).

    GET /api/digestive/status/

    Returns:
        Cached digestion vitals.
    """
    from core.services.digestive import get_digestive_system

    try:
        digestive = get_digestive_system()
        result = digestive.get_vitals()

        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error in digestive_status_view: {e}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'overall_status': 'error',
        }, status=500)


@require_http_methods(["GET"])
def digestive_routes_list_view(request):
    """
    List all ingestion routes.

    GET /api/digestive/routes/
    Query params:
        - route_type: Filter by type (spider, api, stream, etc.)
        - stage: Filter by stage (intake, processing, enrichment, routing)
        - active_only: Only show active routes (default: true)

    Returns:
        List of monitored ingestion routes.
    """
    from core.services.digestive import get_digestive_system

    try:
        route_type = request.GET.get('route_type')
        stage = request.GET.get('stage')
        active_only = request.GET.get('active_only', 'true').lower() != 'false'

        digestive = get_digestive_system()
        routes = digestive.get_routes(
            route_type=route_type,
            stage=stage,
            active_only=active_only
        )

        return JsonResponse({
            'count': len(routes),
            'route_type_filter': route_type,
            'stage_filter': stage,
            'active_only': active_only,
            'routes': routes,
        })
    except Exception as e:
        logger.error(f"Error in digestive_routes_list_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def digestive_route_detail_view(request, route_id):
    """
    Get specific route status.

    GET /api/digestive/routes/<route_id>/

    Returns:
        Detailed status for the specified route.
    """
    from core.models_digestive import IngestionRoute, DigestionStatus

    try:
        try:
            route = IngestionRoute.objects.get(pk=route_id)
        except IngestionRoute.DoesNotExist:
            return JsonResponse({
                'error': 'Route not found',
                'route_id': str(route_id),
            }, status=404)

        # Get status if exists
        status_data = {}
        try:
            status = route.status
            status_data = {
                'status': status.status,
                'is_healthy': status.is_healthy,
                'current_queue_depth': status.current_queue_depth,
                'current_throughput': status.current_throughput,
                'current_latency_ms': status.current_latency_ms,
                'items_ingested_24h': status.items_ingested_24h,
                'items_processed_24h': status.items_processed_24h,
                'items_output_24h': status.items_output_24h,
                'errors_24h': status.errors_24h,
                'success_rate_24h': status.success_rate_24h,
                'last_intake': status.last_intake.isoformat() if status.last_intake else None,
                'last_output': status.last_output.isoformat() if status.last_output else None,
                'last_check': status.last_check.isoformat() if status.last_check else None,
            }
        except DigestionStatus.DoesNotExist:
            status_data = {'status': 'unknown', 'is_healthy': True}

        return JsonResponse({
            'id': str(route.id),
            'name': route.name,
            'display_name': route.display_name,
            'route_type': route.route_type,
            'stage': route.stage,
            'identifier': route.identifier,
            'description': route.description,
            'is_active': route.is_active,
            'is_critical': route.is_critical,
            'is_builtin': route.is_builtin,
            'thresholds': {
                'max_queue_depth': route.max_queue_depth,
                'target_throughput': route.target_throughput,
                'max_processing_time_ms': route.max_processing_time_ms,
            },
            'statistics': {
                'total_items_processed': route.total_items_processed,
                'total_errors': route.total_errors,
                'last_activity': route.last_activity.isoformat() if route.last_activity else None,
            },
            'current_status': status_data,
            'created_at': route.created_at.isoformat(),
        })
    except Exception as e:
        logger.error(f"Error in digestive_route_detail_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def digestive_bottlenecks_view(request):
    """
    Get current bottlenecks in the digestion pipeline.

    GET /api/digestive/bottlenecks/
    Query params:
        - severity: Filter by severity (critical, warning, info)

    Returns:
        List of detected bottlenecks.
    """
    from core.services.digestive import get_digestive_system

    try:
        digestive = get_digestive_system()

        # Get fresh data
        intake = digestive.check_intake()
        processing = digestive.check_processing()
        enrichment = digestive.check_enrichment()
        routing = digestive.check_routing()

        bottlenecks = digestive.detect_bottlenecks(
            intake, processing, enrichment, routing
        )

        # Filter by severity if requested
        severity_filter = request.GET.get('severity')
        if severity_filter:
            bottlenecks = [b for b in bottlenecks if b.get('severity') == severity_filter]

        # Categorize by severity
        critical = [b for b in bottlenecks if b.get('severity') == 'critical']
        warnings = [b for b in bottlenecks if b.get('severity') == 'warning']
        info = [b for b in bottlenecks if b.get('severity') == 'info']

        return JsonResponse({
            'total_bottlenecks': len(bottlenecks),
            'severity_filter': severity_filter,
            'summary': {
                'critical': len(critical),
                'warning': len(warnings),
                'info': len(info),
            },
            'bottlenecks': bottlenecks,
        })
    except Exception as e:
        logger.error(f"Error in digestive_bottlenecks_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def digestive_metabolism_view(request):
    """
    Get metabolism metrics (throughput rates).

    GET /api/digestive/metabolism/

    Returns:
        Current intake, processing, and output rates.
    """
    from core.services.digestive import get_digestive_system

    try:
        digestive = get_digestive_system()
        metabolism = digestive.get_metabolism_rate()

        # Determine metabolism status
        intake_rate = metabolism.get('intake_rate', 0)
        processing_rate = metabolism.get('processing_rate', 0)
        output_rate = metabolism.get('output_rate', 0)

        # Check for imbalances
        warnings = []
        if intake_rate > processing_rate * 1.5 and intake_rate > 1:
            warnings.append({
                'type': 'backlog_risk',
                'message': 'Intake rate exceeds processing rate - backlog may form',
            })
        if processing_rate > output_rate * 2 and processing_rate > 1:
            warnings.append({
                'type': 'routing_bottleneck',
                'message': 'Processing faster than routing - check routing pipeline',
            })
        if intake_rate < 0.5 and output_rate < 0.5:
            warnings.append({
                'type': 'low_activity',
                'message': 'Low overall metabolism - check spider health',
            })

        # Calculate efficiency
        efficiency = (output_rate / intake_rate * 100) if intake_rate > 0 else 100

        return JsonResponse({
            'rates': {
                'intake_rate': round(intake_rate, 3),
                'intake_rate_per_hour': round(intake_rate * 60, 1),
                'processing_rate': round(processing_rate, 3),
                'processing_rate_per_hour': round(processing_rate * 60, 1),
                'output_rate': round(output_rate, 3),
                'output_rate_per_hour': round(output_rate * 60, 1),
            },
            'efficiency_pct': round(efficiency, 1),
            'warnings': warnings,
            'summary': {
                'intake': f'{round(intake_rate * 60, 1)} items/hour',
                'processing': f'{round(processing_rate * 60, 1)} items/hour',
                'output': f'{round(output_rate * 60, 1)} items/hour',
            },
        })
    except Exception as e:
        logger.error(f"Error in digestive_metabolism_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def digestive_history_view(request):
    """
    Get digestion pulse history.

    GET /api/digestive/history/
    Query params:
        - hours: Lookback period (default: 24)
        - limit: Max records to return (default: 100)

    Returns:
        Historical digestion pulses.
    """
    from core.services.digestive import get_digestive_system

    try:
        hours = int(request.GET.get('hours', 24))
        limit = min(int(request.GET.get('limit', 100)), 500)

        digestive = get_digestive_system()
        history = digestive.get_history(hours=hours, limit=limit)

        return JsonResponse({
            'hours': hours,
            'limit': limit,
            'count': len(history),
            'history': history,
        })
    except ValueError as e:
        return JsonResponse({'error': f'Invalid parameter: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error in digestive_history_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def digestive_is_digesting_view(request):
    """
    Quick alive check.

    GET /api/digestive/is-digesting/

    Returns:
        Simple boolean indicating if system is digesting normally.
    """
    from core.services.digestive import get_digestive_system

    try:
        digestive = get_digestive_system()
        is_digesting = digestive.is_digesting()
        emoji = digestive.get_status_emoji()

        return JsonResponse({
            'is_digesting': is_digesting,
            'emoji': emoji,
            'message': 'Digestive system operating normally' if is_digesting else 'Digestive system has issues',
        })
    except Exception as e:
        logger.error(f"Error in digestive_is_digesting_view: {e}", exc_info=True)
        return JsonResponse({
            'is_digesting': False,
            'emoji': '❓',
            'message': f'Error checking digestion: {str(e)}',
        }, status=500)
