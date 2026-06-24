"""
Outreach inbox REST endpoints — Session 1224 P1.

Browser-facing wrappers around OutreachSequencer + OpportunityDraftGenerator.
Mirrors the existing `cockpit_autopilot_*` view pattern from
`views_diagnostics.py`.

Endpoints:
  GET  /api/cockpit/outreach/inbox/           — pending drafts list
  POST /api/cockpit/outreach/<draft_id>/approve/
  POST /api/cockpit/outreach/<draft_id>/reject/
  POST /api/cockpit/outreach/generate/        — on-demand touch-1 generation
  GET  /api/cockpit/outreach/metrics/         — conversion funnel

Tracking deliverable: 329165f4-d5c1-420c-a6ea-d5393ec3e343
"""
from __future__ import annotations

import json
import logging

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def _json_body(request) -> dict:
    try:
        return json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return {}


@csrf_exempt
@require_http_methods(['GET'])
def outreach_inbox(request):
    """Pending OutreachDraft list + funnel counts."""
    from core.services.ops_autopilot import OutreachSequencer

    sequencer = OutreachSequencer()
    report = sequencer.get_inbox(timezone.now())
    return JsonResponse(report)


@csrf_exempt
@require_http_methods(['POST'])
def outreach_approve(request, draft_id):
    """Approve a draft. Optional body: {edited_text}."""
    from core.services.ops_autopilot import OutreachSequencer

    body = _json_body(request)
    edited_text = body.get('edited_text', '')

    sequencer = OutreachSequencer()
    result = sequencer.approve_draft(draft_id, edited_text)
    status = 200 if 'error' not in result else 404
    return JsonResponse(result, status=status)


@csrf_exempt
@require_http_methods(['POST'])
def outreach_reject(request, draft_id):
    """Reject a draft. Optional body: {reason}."""
    from core.services.ops_autopilot import OutreachSequencer

    body = _json_body(request)
    reason = body.get('reason', '')

    sequencer = OutreachSequencer()
    result = sequencer.reject_draft(draft_id, reason)
    status = 200 if 'error' not in result else 404
    return JsonResponse(result, status=status)


@csrf_exempt
@require_http_methods(['POST'])
def outreach_generate(request):
    """On-demand touch=1 draft generation. Optional body: {limit, scope, offers}."""
    from core.services.ops_autopilot import OpportunityDraftGenerator

    body = _json_body(request)
    limit = body.get('limit')
    scope = body.get('scope', 'all')
    offers = body.get('offers')
    if isinstance(offers, str):
        offers = [o.strip() for o in offers.split(',') if o.strip()]

    result = OpportunityDraftGenerator.generate(
        limit=int(limit) if limit is not None else None,
        scope=scope,
        offers=offers,
    )
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(['GET'])
def outreach_metrics(request):
    """Conversion funnel."""
    from core.services.ops_autopilot import OutreachSequencer

    sequencer = OutreachSequencer()
    report = sequencer.get_metrics_report(timezone.now())
    return JsonResponse(report)
