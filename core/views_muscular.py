"""
Session 707: MUSCULAR SYSTEM - API Views

REST API endpoints for the MUSCULAR system which monitors agent
work execution and performance.

Endpoints:
- /api/muscular/flex/             - Run full muscular check
- /api/muscular/status/           - Get cached muscular status
- /api/muscular/groups/           - List all muscle groups
- /api/muscular/groups/<id>/      - Get specific group status
- /api/muscular/weak/             - Get weak muscles (low success rate)
- /api/muscular/overworked/       - Get overworked muscles
- /api/muscular/history/          - Get muscular pulse history
- /api/muscular/is-strong/        - Quick alive check
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def muscular_flex_view(request):
    """
    Run full muscular check.

    GET /api/muscular/flex/
    Query params:
        - force: Force fresh check (ignore cache)

    Returns:
        Complete muscular status including all groups.
    """
    from core.services.muscular import get_muscular_system

    try:
        force = request.GET.get('force', '').lower() == 'true'
        muscular = get_muscular_system()
        result = muscular.flex(force=force)

        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error in muscular_flex_view: {e}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'overall_status': 'error',
            'is_strong': False,
        }, status=500)


@require_http_methods(["GET"])
def muscular_status_view(request):
    """
    Get cached muscular status (fast).

    GET /api/muscular/status/

    Returns:
        Cached muscular vitals.
    """
    from core.services.muscular import get_muscular_system

    try:
        muscular = get_muscular_system()
        result = muscular.get_vitals()

        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Error in muscular_status_view: {e}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'overall_status': 'error',
        }, status=500)


@require_http_methods(["GET"])
def muscular_groups_list_view(request):
    """
    List all muscle groups.

    GET /api/muscular/groups/
    Query params:
        - category: Filter by category (creation, research, strategy, etc.)
        - active_only: Only show active groups (default: true)

    Returns:
        List of monitored muscle groups.
    """
    from core.services.muscular import get_muscular_system

    try:
        category = request.GET.get('category')
        active_only = request.GET.get('active_only', 'true').lower() != 'false'

        muscular = get_muscular_system()
        groups = muscular.get_groups(
            category=category,
            active_only=active_only
        )

        return JsonResponse({
            'count': len(groups),
            'category_filter': category,
            'active_only': active_only,
            'groups': groups,
        })
    except Exception as e:
        logger.error(f"Error in muscular_groups_list_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def muscular_group_detail_view(request, group_id):
    """
    Get specific muscle group status.

    GET /api/muscular/groups/<group_id>/

    Returns:
        Detailed status for the specified muscle group.
    """
    from core.models_muscular import MuscleGroup, MuscleStatus

    try:
        try:
            group = MuscleGroup.objects.get(pk=group_id)
        except MuscleGroup.DoesNotExist:
            return JsonResponse({
                'error': 'Muscle group not found',
                'group_id': str(group_id),
            }, status=404)

        # Get status if exists
        status_data = {}
        try:
            status = group.status
            status_data = {
                'status': status.status,
                'is_healthy': status.is_healthy,
                'strength_score': status.strength_score,
                'fatigue_level': status.fatigue_level,
                'strain_level': status.strain_level,
                'executions_24h': status.executions_24h,
                'successful_24h': status.successful_24h,
                'failed_24h': status.failed_24h,
                'success_rate_24h': status.success_rate_24h,
                'avg_execution_time_ms': status.avg_execution_time_ms,
                'tokens_used_24h': status.tokens_used_24h,
                'cost_24h': float(status.cost_24h),
                'total_agents': status.total_agents,
                'active_agents': status.active_agents,
                'idle_agents': status.idle_agents,
                'top_performer': status.top_performer,
                'worst_performer': status.worst_performer,
                'last_execution': status.last_execution.isoformat() if status.last_execution else None,
                'last_check': status.last_check.isoformat() if status.last_check else None,
            }
        except MuscleStatus.DoesNotExist:
            status_data = {'status': 'unknown', 'is_healthy': True}

        return JsonResponse({
            'id': str(group.id),
            'name': group.name,
            'display_name': group.display_name,
            'category': group.category,
            'description': group.description,
            'agents': group.agent_names,
            'agent_count': len(group.agent_names) if group.agent_names else 0,
            'is_active': group.is_active,
            'is_critical': group.is_critical,
            'is_builtin': group.is_builtin,
            'thresholds': {
                'target_success_rate': group.target_success_rate,
                'max_avg_execution_time_ms': group.max_avg_execution_time_ms,
                'max_fatigue_level': group.max_fatigue_level,
                'max_daily_executions': group.max_daily_executions,
            },
            'statistics': {
                'total_executions': group.total_executions,
                'total_successful': group.total_successful,
                'total_failed': group.total_failed,
                'last_execution': group.last_execution.isoformat() if group.last_execution else None,
            },
            'current_status': status_data,
            'created_at': group.created_at.isoformat(),
        })
    except Exception as e:
        logger.error(f"Error in muscular_group_detail_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def muscular_weak_view(request):
    """
    Get weak muscles (agents with low success rates).

    GET /api/muscular/weak/
    Query params:
        - threshold: Success rate threshold (default: 80)
        - severity: Filter by severity (critical, warning)

    Returns:
        List of weak muscles (underperforming agents).
    """
    from core.services.muscular import get_muscular_system

    try:
        muscular = get_muscular_system()
        weak_muscles = muscular.detect_weak_muscles()

        # Filter by severity if requested
        severity_filter = request.GET.get('severity')
        if severity_filter:
            weak_muscles = [w for w in weak_muscles if w.get('severity') == severity_filter]

        # Categorize by severity
        critical = [w for w in weak_muscles if w.get('severity') == 'critical']
        warnings = [w for w in weak_muscles if w.get('severity') == 'warning']

        return JsonResponse({
            'total_weak_muscles': len(weak_muscles),
            'severity_filter': severity_filter,
            'summary': {
                'critical': len(critical),
                'warning': len(warnings),
            },
            'weak_muscles': weak_muscles,
        })
    except Exception as e:
        logger.error(f"Error in muscular_weak_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def muscular_overworked_view(request):
    """
    Get overworked muscles (agents with high execution counts).

    GET /api/muscular/overworked/
    Query params:
        - severity: Filter by severity (critical, warning)

    Returns:
        List of overworked muscles.
    """
    from core.services.muscular import get_muscular_system

    try:
        muscular = get_muscular_system()
        overworked = muscular.detect_overworked_muscles()

        # Filter by severity if requested
        severity_filter = request.GET.get('severity')
        if severity_filter:
            overworked = [o for o in overworked if o.get('severity') == severity_filter]

        # Categorize by severity
        critical = [o for o in overworked if o.get('severity') == 'critical']
        warnings = [o for o in overworked if o.get('severity') == 'warning']

        # Calculate total cost of overworked agents
        total_cost = sum(o.get('cost', 0) for o in overworked)
        total_tokens = sum(o.get('tokens_used', 0) for o in overworked)

        return JsonResponse({
            'total_overworked': len(overworked),
            'severity_filter': severity_filter,
            'summary': {
                'critical': len(critical),
                'warning': len(warnings),
                'total_tokens': total_tokens,
                'total_cost': round(total_cost, 4),
            },
            'overworked_muscles': overworked,
        })
    except Exception as e:
        logger.error(f"Error in muscular_overworked_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def muscular_history_view(request):
    """
    Get muscular pulse history.

    GET /api/muscular/history/
    Query params:
        - hours: Lookback period (default: 24)
        - limit: Max records to return (default: 100)

    Returns:
        Historical muscular pulses.
    """
    from core.services.muscular import get_muscular_system

    try:
        hours = int(request.GET.get('hours', 24))
        limit = min(int(request.GET.get('limit', 100)), 500)

        muscular = get_muscular_system()
        history = muscular.get_history(hours=hours, limit=limit)

        return JsonResponse({
            'hours': hours,
            'limit': limit,
            'count': len(history),
            'history': history,
        })
    except ValueError as e:
        return JsonResponse({'error': f'Invalid parameter: {e}'}, status=400)
    except Exception as e:
        logger.error(f"Error in muscular_history_view: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def muscular_is_strong_view(request):
    """
    Quick alive check.

    GET /api/muscular/is-strong/

    Returns:
        Simple boolean indicating if muscular system is strong.
    """
    from core.services.muscular import get_muscular_system

    try:
        muscular = get_muscular_system()
        is_strong = muscular.is_strong()
        emoji = muscular.get_status_emoji()

        return JsonResponse({
            'is_strong': is_strong,
            'emoji': emoji,
            'message': 'Muscular system operating strongly' if is_strong else 'Muscular system has issues',
        })
    except Exception as e:
        logger.error(f"Error in muscular_is_strong_view: {e}", exc_info=True)
        return JsonResponse({
            'is_strong': False,
            'emoji': '?',
            'message': f'Error checking muscular system: {str(e)}',
        }, status=500)
