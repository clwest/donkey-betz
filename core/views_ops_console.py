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


@require_GET
@login_required
def health_summary(request):
    """GET /api/ops/health-summary/ — S2761 Command Center Ops Health tile.

    Composes the three S2755→S2760 operational-diagnostic surfaces into a
    single last-mile UI payload: current freshness verdict + accumulated
    tenant-boundary violations (I-0303) + accumulated staleness warnings
    (S2759). Window fixed at 24h to match the Rigby round-trip protocol.
    """
    from core.services.td_handlers_ops import OpsHandlersMixin

    class _Proxy(OpsHandlersMixin):
        pass

    proxy = _Proxy()
    user_id = request.user.id
    trace_id = 'ops-console-health'

    def _safe_call(payload, error_key):
        try:
            return proxy._handle_ops('ops_tool', payload, user_id=user_id, trace_id=trace_id)
        except Exception as e:  # noqa: BLE001 — surface degradation, not 500
            logger.warning(f"health_summary {payload.get('action')} failed: {e}")
            return {'error': str(e), '_source': error_key}

    version = _safe_call({'action': 'version'}, 'version')
    tbv = _safe_call({'action': 'tenant_boundary_violations', 'window': '24h', 'limit': 0}, 'tbv')
    stw = _safe_call({'action': 'staleness_warnings', 'window': '24h', 'limit': 0}, 'stw')

    head_sha = (version.get('head_commit_sha') or '')[:12] if isinstance(version, dict) else ''
    return JsonResponse({
        'window': '24h',
        'verdict': (version.get('staleness_verdict') if isinstance(version, dict) else None) or 'UNKNOWN',
        'head_commit_sha_short': head_sha,
        'tenant_boundary_violations': {
            'total': tbv.get('total_count', 0) if isinstance(tbv, dict) else 0,
            'by_task_name': tbv.get('by_task_name', {}) if isinstance(tbv, dict) else {},
            'by_failure_kind': tbv.get('by_failure_kind', {}) if isinstance(tbv, dict) else {},
        },
        'staleness_warnings': {
            'total': stw.get('total_count', 0) if isinstance(stw, dict) else 0,
            'by_verdict': stw.get('by_verdict', {}) if isinstance(stw, dict) else {},
        },
    })
