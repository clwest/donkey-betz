"""S2780 N22 v3 — Governance REST endpoints.

Separate namespace from ``views_ops_console.py`` per S2779 V6 fold + S2780
T1 SIGN V7 fold A (semantic boundary erosion). Reads governance-scope
artifacts (SIGN discipline evidence, ratification-adjacent surfaces) —
distinct from ops-scope observability (SLO/staleness/worker health).

Same scope policy as ``views_ops_console.py`` (Rigby Q3 #1):

  1. Aggregate / read-only. No mutation endpoints.
  2. No raw DB dumps, no secrets, no user content.
  3. Reject unknown query parameters via ``_reject_unknown_query_params``.
  4. Require both ``@login_required`` AND staff-only.
  5. Fail soft on downstream error.
  6. Compose sub-calls via handler functions, never HTTP loops.
"""
import logging
from typing import Any, Dict
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required, user_passes_test

logger = logging.getLogger(__name__)

# ── Auth gate (mirrors _ops_staff_only) ──────────────────────────────────
_governance_staff_only = user_passes_test(
    lambda u: u.is_authenticated and u.is_staff,
)


# ── Query-param allowlists ───────────────────────────────────────────────
_GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER: frozenset[str] = frozenset({
    'session',
    'classification',
    'arc',
    'limit',
})


def _reject_unknown_query_params(
    request,
    allowed: frozenset[str],
) -> JsonResponse | None:
    """Match views_ops_console _reject_unknown_query_params contract."""
    supplied = set(request.GET.keys())
    unknown = supplied - allowed
    if not unknown:
        return None
    return JsonResponse(
        {
            'error': 'Unknown query parameter(s)',
            'code': 'unknown_query_params',
            'unknown': sorted(unknown),
            'allowed': sorted(allowed),
        },
        status=400,
    )


def _call_zoom_out_tool(
    request,
    payload: Dict[str, Any],
    trace_id: str = 'governance-console',
) -> Dict[str, Any]:
    """Shared zoom_out_tool dispatch helper (mirrors _call_ops_tool).

    Wraps the ``GovernanceHandlersMixin._handle_zoom_out`` entrypoint —
    the same dispatch that Rigby hits through the PA-tool surface. Keeps
    the endpoint free of handler details; if the handler evolves, the
    view stays stable.
    """
    from core.services.td_handlers_governance import GovernanceHandlersMixin

    class _Proxy(GovernanceHandlersMixin):
        pass

    proxy = _Proxy()
    result = proxy._handle_zoom_out(
        'zoom_out_tool',
        payload,
        user_id=getattr(request.user, 'id', None),
        trace_id=trace_id,
    )
    return result if isinstance(result, dict) else {}


# ── Views ────────────────────────────────────────────────────────────────
@require_GET
@login_required
@_governance_staff_only
def zoom_out_ledger(request):
    """GET /api/governance/zoom-out-ledger/ — Rigby SIGN zoom-out concern ledger.

    Reads ``logs/zoom_out_classifications.jsonl`` via ``zoom_out_tool.list``.
    Advisory-only surface per PLAYBOOK-6.10.8 — response embeds
    ``advisory`` header + ``is_gate: false`` + ``semantics`` marker.

    Query params (all optional):
      session: int — filter by originating session (exact match)
      classification: enum — same_pr_actionable / same_pr_mitigatable / future_trigger
      arc: str — substring match on arc slug
      limit: int — tail window size (default 20, max 100)
    """
    reject = _reject_unknown_query_params(
        request, _GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER
    )
    if reject is not None:
        return reject

    payload: Dict[str, Any] = {'action': 'list'}
    if 'session' in request.GET:
        payload['session'] = request.GET.get('session')
    if 'classification' in request.GET:
        payload['classification'] = request.GET.get('classification')
    if 'arc' in request.GET:
        payload['arc'] = request.GET.get('arc')
    if 'limit' in request.GET:
        payload['limit'] = request.GET.get('limit')

    try:
        result = _call_zoom_out_tool(
            request, payload, trace_id='governance-zoom-out-ledger'
        )
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"Zoom-out ledger error: {e}")
        return JsonResponse({
            'items': [],
            'count': 0,
            'total_rows': 0,
            'log_exists': False,
            'is_gate': False,
            'error': str(e),
        })
