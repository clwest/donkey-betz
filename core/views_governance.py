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
    'since_session',
    'until_session',
    'classification',
    'arc',
    'limit',
    'include',
})


# S2794 N23: tenant boundary health endpoint. Currently no query params;
# frozenset stays empty but is kept explicit so future extensions must
# opt-in via allowlist edit (not silently accept a new key).
_GOVERNANCE_ALLOWED_PARAMS__TENANT_BOUNDARY_HEALTH: frozenset[str] = frozenset()


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
      since_session: int — inclusive lower bound on originating session (S2793 N22 v2)
      until_session: int — inclusive upper bound on originating session (S2793 N22 v2)
      classification: enum — same_pr_actionable / same_pr_mitigatable / future_trigger
      arc: str — substring match on arc slug
      limit: int — tail window size (default 20, max 100)
      include: str — comma-separated opt-in blocks (e.g., 'aggregations')

    Note: since_session/until_session narrow items[] only. Aggregations
    remain computed over ALL rows to preserve longitudinal-signal semantics.
    """
    reject = _reject_unknown_query_params(
        request, _GOVERNANCE_ALLOWED_PARAMS__ZOOM_OUT_LEDGER
    )
    if reject is not None:
        return reject

    payload: Dict[str, Any] = {'action': 'list'}
    if 'session' in request.GET:
        payload['session'] = request.GET.get('session')
    if 'since_session' in request.GET:
        payload['since_session'] = request.GET.get('since_session')
    if 'until_session' in request.GET:
        payload['until_session'] = request.GET.get('until_session')
    if 'classification' in request.GET:
        payload['classification'] = request.GET.get('classification')
    if 'arc' in request.GET:
        payload['arc'] = request.GET.get('arc')
    if 'limit' in request.GET:
        payload['limit'] = request.GET.get('limit')
    if 'include' in request.GET:
        payload['include'] = request.GET.get('include')

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


# ── S2794 N23: Tenant Boundary Health ────────────────────────────────────

_TENANT_BOUNDARY_ADVISORY: str = (
    "Advisory signal — not a launch gate. "
    "Human approval required to open the alpha cohort, flip runtime flags, "
    "or promote the platform out of single-user pre-prod. "
    "Report data is longitudinal; treat green results as one input among many."
)


@require_GET
@login_required
@_governance_staff_only
def tenant_boundary_health(request):
    """GET /api/governance/tenant-boundary-health/ — RUR-C1 readiness surface.

    Returns the latest ``TenantBoundaryHealthReport`` (if any) plus the
    advisory posture, launch-approval policy, and known-gaps list.

    Response shape::

        {
          "advisory": "Advisory signal — not a launch gate. …",
          "is_gate": false,
          "policy": {"launch_approval": "Manual (Chris)"},
          "latest_report": {
            "id": "…",
            "created_at": "2026-…",
            "env": "local",
            "git_sha": "…",
            "runner_identity": "…",
            "elapsed_secs": 262.2,
            "total_tests": 324,
            "passed": 324,
            "failed": 0,
            "errored": 0,
            "skipped": 0,
            "failing_test_ids": [],
            "coverage_metadata": {"sync_http_bucket_a_public_endpoints": "covered", …},
            "overall_status": "green"
          } | null,
          "coverage_metadata": {…},  # canonical from service
          "known_gaps": [
            "Async Celery task boundary — I-0303 has scoping but no P2+ …",
            "WebSocket consumer boundary — I-0303 not opened; no coverage",
            …
          ]
        }

    Advisory posture (S2794 F1 mitigation): the response NEVER contains
    a gate/toggle/flag. Consumers that treat overall_status='green' as
    permission to open the alpha cohort violate the campaign posture.
    """
    reject = _reject_unknown_query_params(
        request, _GOVERNANCE_ALLOWED_PARAMS__TENANT_BOUNDARY_HEALTH
    )
    if reject is not None:
        return reject

    from core.models import TenantBoundaryHealthReport
    from core.services.cross_tenant_regression_service import (
        COVERAGE_METADATA,
        KNOWN_GAPS,
    )

    latest = (
        TenantBoundaryHealthReport.objects
        .order_by('-created_at')
        .first()
    )

    latest_payload = None
    if latest is not None:
        latest_payload = {
            'id': str(latest.id),
            'created_at': latest.created_at.isoformat() if latest.created_at else None,
            'env': latest.env,
            'git_sha': latest.git_sha,
            'runner_identity': latest.runner_identity,
            'elapsed_secs': latest.elapsed_secs,
            'total_tests': latest.total_tests,
            'passed': latest.passed,
            'failed': latest.failed,
            'errored': latest.errored,
            'skipped': latest.skipped,
            'failing_test_ids': latest.failing_test_ids or [],
            'coverage_metadata': latest.coverage_metadata or {},
            'overall_status': latest.overall_status,
        }

    return JsonResponse({
        'advisory': _TENANT_BOUNDARY_ADVISORY,
        'is_gate': False,
        'policy': {
            'launch_approval': 'Manual (Chris)',
            'reason': (
                'RUR-C1 CAMPAIGN.md — parent closes only when I-0301 + I-0302 + '
                'I-0303 all pass shared cross-tenant regression. Even at 100% '
                'pass, alpha cohort open requires explicit Chris ratification.'
            ),
        },
        'latest_report': latest_payload,
        'coverage_metadata': dict(COVERAGE_METADATA),
        'known_gaps': list(KNOWN_GAPS),
    })
