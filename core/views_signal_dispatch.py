"""Signal Dispatch endpoints — Session 2934 A4 (list) + Session 2947 A8
(manual dispatch + cluster resolve).

Backs the Workspace "Signal Dispatches" tab. Read-only list surface
over ``core.models_signal_dispatch.SignalDispatch``; write surface
mirrors the ``dispatch_signal`` mgmt command via
``SignalDispatchService.create_manual_dispatch``.

S2947 A8 v1 policy: no ``force`` param exposed to the API — UI is
safer than CLI by default. The CLI ``--force`` flag remains for
operator-level overrides.
"""
import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def signal_dispatches_list(request):
    """List SignalDispatch rows for the Workspace observability tab.

    Query params:
        limit (int, default 25, max 200)
        offset (int, default 0)
        pattern_type (str) — filter by SignalCluster.pattern_type
        outcome (str) — filter by SignalDispatch.outcome
        rule_key (str) — filter by SIGNAL_DISPATCH_RULES key
    """
    try:
        from core.models_signal_dispatch import SignalDispatch

        limit = max(1, min(int(request.GET.get('limit', 25)), 200))
        offset = max(0, int(request.GET.get('offset', 0)))
        pattern_type = request.GET.get('pattern_type')
        outcome = request.GET.get('outcome')
        rule_key = request.GET.get('rule_key')

        qs = SignalDispatch.objects.select_related('signal_cluster').order_by('-dispatched_at')
        if pattern_type:
            qs = qs.filter(pattern_type=pattern_type)
        if outcome:
            qs = qs.filter(outcome=outcome)
        if rule_key:
            qs = qs.filter(rule_key=rule_key)

        total_count = qs.count()
        rows = list(qs[offset:offset + limit])
        has_more = (offset + len(rows)) < total_count

        return Response({
            'success': True,
            'data': {
                'dispatches': [
                    {
                        'id': str(d.id),
                        'rule_key': d.rule_key,
                        'pattern_type': d.pattern_type,
                        'agent_name': d.agent_name,
                        'outcome': d.outcome,
                        'error_summary': d.error_summary or '',
                        'signal_cluster_id': str(d.signal_cluster.pk) if d.signal_cluster else None,
                        'signal_cluster_name': d.signal_cluster.name if d.signal_cluster else None,
                        'agent_execution_id': str(d.agent_execution_id) if d.agent_execution_id else None,
                        'scan_run_id': d.scan_run_id or '',
                        'dispatched_at': d.dispatched_at.isoformat(),
                        'completed_at': d.completed_at.isoformat() if d.completed_at else None,
                        'input_payload': d.input_payload or {},
                    }
                    for d in rows
                ],
                'count': len(rows),
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': has_more,
            },
        })
    except Exception as e:
        logger.error(f"signal_dispatches_list failed: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


# S2947 A8: manual-dispatch button backend ────────────────────────────

_ERROR_CODE_STATUS = {
    'cluster_not_found': 404,
    'unknown_rule_key': 400,
    'rule_pattern_mismatch': 400,
    'no_matching_rule': 400,
    'multiple_matching_rules': 400,
    'guard_blocked': 409,
    'missing_cluster_id': 400,
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signal_dispatches_manual(request):
    """Manually create a SignalDispatch for a specific cluster.

    Belt-and-suspenders auth: the site-wide auth middleware gates
    unauthenticated requests, and this DRF permission enforces it a
    second time at the view layer — appropriate for a mutation that
    fans out to Celery + LLM spend.

    Body:
        cluster_id (str, required) — SignalCluster UUID
        rule_key (str, optional) — rule to fire; auto-picks if omitted
                                   and cluster.pattern_type matches exactly 1

    v1 does NOT expose ``force``. The 5-minute idempotent guard is
    always active. Operators needing override use the
    ``python manage.py dispatch_signal --force`` CLI.

    Returns 201 on success. See SignalDispatchService.create_manual_dispatch
    for the full error_code catalog.
    """
    try:
        from core.services.signal_dispatch_service import SignalDispatchService

        cluster_id = (request.data.get('cluster_id') or '').strip()
        rule_key = (request.data.get('rule_key') or '').strip() or None

        if not cluster_id:
            return Response(
                {
                    'success': False,
                    'error_code': 'missing_cluster_id',
                    'error': 'cluster_id is required',
                },
                status=400,
            )

        service = SignalDispatchService()
        result = service.create_manual_dispatch(
            cluster_id=cluster_id,
            rule_key=rule_key,
        )

        if not result.get('success'):
            status_code = _ERROR_CODE_STATUS.get(result.get('error_code', ''), 400)
            return Response(result, status=status_code)

        return Response(result, status=201)
    except Exception as e:
        logger.error(f"signal_dispatches_manual failed: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def signal_dispatch_resolve_cluster(request, cluster_id):
    """Resolve a cluster UUID for the manual-dispatch modal preview.

    Returns the cluster's identifying metadata plus which
    SIGNAL_DISPATCH_RULES currently match its pattern_type, so the
    frontend can inline-preview what a dispatch would do and
    auto-select the rule when there's only one match.
    """
    try:
        from core.models_signal_intelligence import SignalCluster
        from core.services.signal_dispatch_service import SIGNAL_DISPATCH_RULES

        try:
            cluster = SignalCluster.objects.get(id=cluster_id)
        except SignalCluster.DoesNotExist:
            return Response(
                {'success': False, 'error_code': 'cluster_not_found',
                 'error': f'SignalCluster {cluster_id} not found'},
                status=404,
            )

        matching = [
            {'key': r.key, 'agent_name': r.agent_name}
            for r in SIGNAL_DISPATCH_RULES
            if r.pattern_type == cluster.pattern_type
        ]

        return Response({
            'success': True,
            'data': {
                'id': str(cluster.id),
                'name': cluster.name,
                'pattern_type': cluster.pattern_type,
                'strength': float(cluster.strength or 0.0),
                'confidence': float(cluster.confidence or 0.0),
                'status': cluster.status,
                'is_actionable': cluster.is_actionable,
                'matching_rules': matching,
            },
        })
    except Exception as e:
        logger.error(f"signal_dispatch_resolve_cluster failed: {e}")
        return Response({'success': False, 'error': str(e)}, status=500)
