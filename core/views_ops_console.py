"""
Session 1077: Ops Console REST endpoints.

Exposes SLO status, failure signatures, and blocked agents as REST
endpoints for the frontend OpsConsoleTab. These were previously only
available through PA tool gateway (ops_tool).
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


@require_GET
@login_required
def slo_status(request):
    """GET /api/ops/slo-status/ — SLO dashboard data."""
    try:
        from core.services.td_handlers_ops import OpsHandlersMixin

        class _Proxy(OpsHandlersMixin):
            pass

        proxy = _Proxy()
        result = proxy._handle_ops(
            'ops_tool',
            {'action': 'slo_status', 'window': '24h'},
            user_id=request.user.id,
            trace_id='ops-console',
        )
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"SLO status error: {e}")
        return JsonResponse({'slos': [], 'error': str(e)})


@require_GET
@login_required
def failure_signatures(request):
    """GET /api/ops/failure-signatures/ — Recent failure patterns."""
    try:
        from core.services.td_handlers_ops import OpsHandlersMixin

        class _Proxy(OpsHandlersMixin):
            pass

        proxy = _Proxy()
        window = request.GET.get('window', '24h')
        limit = int(request.GET.get('limit', 10))
        result = proxy._handle_ops(
            'ops_tool',
            {'action': 'failure_signatures', 'window': window, 'limit': limit},
            user_id=request.user.id,
            trace_id='ops-console',
        )
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Failure signatures error: {e}")
        return JsonResponse({'signatures': [], 'error': str(e)})


@require_GET
@login_required
def blocked_agents(request):
    """GET /api/ops/blocked-agents/ — Currently blocked agents."""
    try:
        from core.models_unified_system import AgentControlEntry
        entries = AgentControlEntry.objects.filter(status='blocked').order_by('-blocked_at')
        blocked = []
        for e in entries:
            blocked.append({
                'agent_name': e.agent_name,
                'reason': e.reason,
                'blocked_by': e.blocked_by,
                'blocked_at': e.blocked_at.isoformat() if e.blocked_at else None,
                'ttl_hours': e.ttl_hours,
            })
        return JsonResponse({'blocked': blocked, 'count': len(blocked)})
    except Exception as e:
        logger.error(f"Blocked agents error: {e}")
        return JsonResponse({'blocked': [], 'error': str(e)})
