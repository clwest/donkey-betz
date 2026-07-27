"""
Doc-research finding endpoints — S2989 Phase B.

Endpoints:
- GET  /api/repo/doc-research-findings/       — list with filters
- POST /api/repo/doc-research-findings/<id>/mark/         — status change
- POST /api/repo/doc-research-findings/<id>/send-to-rigby/ — spec-shape
      Deliverable via briefing_spec_generator (Phase A)

Reuses:
- Phase A `generate_spec_body` for LLM spec generation
- `deliverable_factory.create_deliverable` for the persistence contract
- `IsAuthenticated` DRF pattern from views_repo_canonical_briefing so
  auth failures land as JSON 401/403, not the 302 HTML redirect
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes as drf_permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRFResponse

from core.models_audit_findings import DocResearchFinding
from core.views_repo_canonical_briefing import (
    BRIEFING_ACTION_ITEM_CATEGORY,
    BRIEFING_ACTION_ITEM_TITLE_MAX,
    BRIEFING_ACTION_ITEM_TYPE,
    DONKEY_BETZ_WORKSPACE_ID,
    _derive_title,
)

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

VALID_MARK_STATUSES = {
    DocResearchFinding.STATUS_OPEN,
    DocResearchFinding.STATUS_FIXED,
    DocResearchFinding.STATUS_DISMISSED,
}

VALID_CLOSE_MODES = {choice for choice, _ in DocResearchFinding.CLOSE_MODE_CHOICES}
VALID_FINDING_TYPES = {choice for choice, _ in DocResearchFinding.FINDING_TYPE_CHOICES}
VALID_STALENESS = {choice for choice, _ in DocResearchFinding.STALENESS_CHOICES}


def _serialize_finding(f: DocResearchFinding) -> Dict[str, Any]:
    return {
        "id": str(f.id),
        "doc_path": f.doc_path,
        "domain_slug": f.domain_slug,
        "source_type": f.source_type,
        "source_heading": f.source_heading,
        "text": f.text,
        "confidence": f.confidence,
        "tags": list(f.tags or []),
        "status": f.status,
        "resolved_at": f.resolved_at.isoformat() if f.resolved_at else None,
        "resolved_by": (
            f.resolved_by.username if f.resolved_by is not None else None
        ),
        "resolution_note": f.resolution_note,
        "close_mode": f.close_mode,
        "finding_type": f.finding_type,
        "staleness": f.staleness,
        "deliverable_id": f.deliverable_id or None,
        "first_seen_at": f.first_seen_at.isoformat() if f.first_seen_at else None,
        "last_seen_at": f.last_seen_at.isoformat() if f.last_seen_at else None,
        "metadata": dict(f.metadata or {}),
    }


@api_view(["GET"])
@drf_permission_classes([IsAuthenticated])
def doc_research_findings_list_view(request):
    """GET /api/repo/doc-research-findings/

    Query params:
        status         — open | fixed | dismissed (default: open)
        domain_slug    — exact match
        source_type    — audit | canonical_summary | implementation_debt
        confidence     — high | medium | low
        min_confidence — high | medium | low (inclusive floor)
        search         — case-insensitive substring in text
        page           — 1-based
        page_size      — default 50, max 200
    """
    qs = DocResearchFinding.objects.all().order_by(
        "-confidence", "domain_slug", "doc_path", "first_seen_at"
    )
    status = (request.GET.get("status") or "open").strip().lower()
    if status not in ("all", ""):
        qs = qs.filter(status=status)
    domain_slug = (request.GET.get("domain_slug") or "").strip()
    if domain_slug:
        qs = qs.filter(domain_slug=domain_slug)
    source_type = (request.GET.get("source_type") or "").strip()
    if source_type:
        qs = qs.filter(source_type=source_type)
    confidence = (request.GET.get("confidence") or "").strip()
    if confidence:
        qs = qs.filter(confidence=confidence)
    finding_type = (request.GET.get("finding_type") or "").strip()
    if finding_type and finding_type in VALID_FINDING_TYPES:
        qs = qs.filter(finding_type=finding_type)
    staleness = (request.GET.get("staleness") or "").strip()
    if staleness and staleness in VALID_STALENESS:
        qs = qs.filter(staleness=staleness)
    min_confidence = (request.GET.get("min_confidence") or "").strip()
    if min_confidence == "high":
        qs = qs.filter(confidence="high")
    elif min_confidence == "medium":
        qs = qs.filter(confidence__in=["high", "medium"])
    search = (request.GET.get("search") or "").strip()
    if search:
        qs = qs.filter(text__icontains=search)

    try:
        page = max(int(request.GET.get("page") or 1), 1)
    except ValueError:
        page = 1
    try:
        page_size = int(request.GET.get("page_size") or DEFAULT_PAGE_SIZE)
    except ValueError:
        page_size = DEFAULT_PAGE_SIZE
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    rows = qs.select_related("resolved_by")[start:end]

    return DRFResponse({
        "total": total,
        "page": page,
        "page_size": page_size,
        "findings": [_serialize_finding(f) for f in rows],
    })


@api_view(["POST"])
@drf_permission_classes([IsAuthenticated])
def doc_research_findings_mark_view(request, finding_id: str):
    """POST /api/repo/doc-research-findings/<uuid>/mark/

    Body::
        {"status": "fixed"|"dismissed"|"open", "note": "optional"}
    """
    try:
        body: Dict[str, Any] = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return DRFResponse({"error": "Invalid JSON body"}, status=400)

    new_status = (body.get("status") or "").strip().lower()
    if new_status not in VALID_MARK_STATUSES:
        return DRFResponse(
            {"error": f"status must be one of {sorted(VALID_MARK_STATUSES)}"},
            status=400,
        )
    note = str(body.get("note") or "").strip()[:2000]

    close_mode_raw = body.get("close_mode")
    if close_mode_raw is None or close_mode_raw == "":
        close_mode_new = None
        close_mode_provided = "close_mode" in body
    else:
        close_mode_new = str(close_mode_raw).strip().lower()
        close_mode_provided = True
        if close_mode_new not in VALID_CLOSE_MODES:
            return DRFResponse(
                {"error": f"close_mode must be one of {sorted(VALID_CLOSE_MODES)} or null"},
                status=400,
            )

    try:
        finding = DocResearchFinding.objects.get(id=finding_id)
    except DocResearchFinding.DoesNotExist:
        return DRFResponse({"error": "finding not found"}, status=404)

    finding.status = new_status
    finding.resolution_note = note or finding.resolution_note
    update_fields = ["status", "resolution_note", "resolved_at", "resolved_by", "last_seen_at"]
    if close_mode_provided:
        finding.close_mode = close_mode_new
        update_fields.append("close_mode")
    if new_status in (DocResearchFinding.STATUS_FIXED, DocResearchFinding.STATUS_DISMISSED):
        finding.resolved_at = timezone.now()
        if request.user.is_authenticated:
            finding.resolved_by = request.user
    else:
        finding.resolved_at = None
        finding.resolved_by = None
    finding.save(update_fields=update_fields)
    return DRFResponse({"finding": _serialize_finding(finding)})


@api_view(["POST"])
@drf_permission_classes([IsAuthenticated])
def doc_research_findings_send_to_rigby_view(request, finding_id: str):
    """POST /api/repo/doc-research-findings/<uuid>/send-to-rigby/

    Route the finding through Phase A `generate_spec_body` and persist a
    `briefing_action_item` Deliverable in the Donkey Betz workspace. Store
    the resulting `deliverable_id` on the finding so the UI can link back.
    """
    try:
        finding = DocResearchFinding.objects.get(id=finding_id)
    except DocResearchFinding.DoesNotExist:
        return DRFResponse({"error": "finding not found"}, status=404)

    citations: List[Dict[str, Any]] = [
        {
            "path": finding.doc_path,
            "snippet": finding.text[:400],
        }
    ]
    section_title = finding.source_heading or finding.source_type
    section_key = finding.source_type or "finding"

    try:
        from core.services.briefing_spec_generator import generate_spec_body
        from core.services.deliverable_factory import (
            create_deliverable,
            DeliverableGatedError,
        )
        from core.models_skin_layer import ProjectWorkspace
    except ImportError:
        logger.exception("send_to_rigby(finding): import failed")
        return DRFResponse({"error": "Deliverable subsystem unavailable"}, status=500)

    # S2997 v2 item #8: pipe stale-ref call-out into the spec so
    # downstream executors see the drift. Only when the ingest-time
    # detector actually flagged this finding — a `fresh` finding
    # doesn't need the injection and shouldn't get a spurious
    # "Staleness note" section.
    failed_refs: List[str] = []
    if finding.staleness == DocResearchFinding.STALENESS_SUSPECTED:
        raw_refs = (finding.metadata or {}).get("staleness_failed_refs") or []
        if isinstance(raw_refs, list):
            failed_refs = [str(r) for r in raw_refs if isinstance(r, str) and r.strip()]

    content, spec_extras = generate_spec_body(
        bullet_text=finding.text,
        section_key=section_key,
        section_title=section_title,
        anchor_path=finding.doc_path,
        citations=citations,
        finding_type=finding.finding_type,
        staleness_failed_refs=failed_refs or None,
    )

    try:
        workspace = ProjectWorkspace.objects.get(id=DONKEY_BETZ_WORKSPACE_ID)
    except ProjectWorkspace.DoesNotExist:
        return DRFResponse(
            {"error": "Target workspace missing — contact operator"},
            status=500,
        )

    title = _derive_title(finding.text)[:BRIEFING_ACTION_ITEM_TITLE_MAX]

    try:
        deliverable = create_deliverable(
            title=title,
            content=content,
            agent_name="doc_research_finding_send_to_rigby",
            category=BRIEFING_ACTION_ITEM_CATEGORY,
            deliverable_type=BRIEFING_ACTION_ITEM_TYPE,
            user=request.user if request.user.is_authenticated else None,
            workspace_id=str(workspace.id),
            workspace=workspace,
            tags=[
                "briefing-action",
                "doc-research-finding",
                finding.domain_slug or "unknown",
                finding.source_type,
            ],
            content_format="markdown",
            metadata={
                "source": "doc_research_finding_send_to_rigby",
                "trigger_source": "pa_tool",
                "finding_id": str(finding.id),
                "anchor_path": finding.doc_path,
                "section_key": section_key,
                "section_title": section_title,
                "source_type": finding.source_type,
                "domain_slug": finding.domain_slug,
                **spec_extras,
            },
            preserve_title=True,
            raise_on_gated=True,
            status="ready",
        )
    except DeliverableGatedError as exc:
        logger.warning("send_to_rigby(finding): gated (%s: %s)", exc.reason_code, exc.reason)
        return DRFResponse(
            {
                "error": "Deliverable was rejected by the quality gate",
                "reason_code": exc.reason_code,
                "reason": exc.reason,
            },
            status=422,
        )
    except Exception:
        logger.exception(
            "send_to_rigby(finding): failed finding_id=%s doc=%s",
            finding.id, finding.doc_path,
        )
        return DRFResponse({"error": "Failed to create deliverable"}, status=500)

    if deliverable is None:
        return DRFResponse({"error": "Deliverable factory returned no row"}, status=500)

    finding.deliverable_id = str(deliverable.id)
    finding.save(update_fields=["deliverable_id", "last_seen_at"])

    return DRFResponse(
        {
            "deliverable_id": str(deliverable.id),
            "workspace_id": str(workspace.id),
            "title": deliverable.title,
            "deliverable_type": deliverable.deliverable_type,
            "finding": _serialize_finding(finding),
        },
        status=201,
    )
