"""Signal Dispatch list endpoint — Session 2934 A4.

Backs the Workspace "Signal Dispatches" tab. Read-only surface over
``core.models_signal_dispatch.SignalDispatch``; no mutation endpoints.
"""
import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
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
