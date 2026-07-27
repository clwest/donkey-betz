"""
Workspace Home APIs — Session 2983 (snapshot) + Session 2984 PR4 (shift-brief).

Endpoints:
- GET /api/workspaces/<uuid:workspace_id>/home/          — snapshot for the
  Home tab (NOW / ACTIVE WORK / LIBRARY modules) — Spec §3.1.
- POST /api/workspaces/<uuid:workspace_id>/shift-brief/  — Guided Action
  "Run Shift Brief" — invokes core.services.rigby_shift_brief.build_shift_brief
  and returns the result. Owner-only auth via _get_workspace.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.views_workspace_templates import _get_workspace

logger = logging.getLogger(__name__)


NOW_WINDOW_HOURS = 24
SECTION_LIST_CAP = 20
TIMELINE_CAP = 20


def _serialize_deliverable_card(deliverable) -> dict:
    """Deliverable payload for library/needs_review lists — matches spec §2.3 AC-LIB-3."""
    initiative_id = deliverable.initiative_id
    return {
        "id": str(deliverable.id),
        "title": deliverable.title,
        "type": deliverable.deliverable_type,
        "status": deliverable.status,
        "is_pinned": bool(deliverable.is_pinned),
        "updated_at": deliverable.updated_at.isoformat() if deliverable.updated_at else None,
        "initiative_id": str(initiative_id) if initiative_id else None,
    }


def _build_now(workspace, cutoff) -> dict:
    """NOW module — activity summary + timeline over last 24h."""
    from core.models_deliverables import Deliverable
    from core.models_unified_system import AgentExecution

    deliverables_qs = Deliverable.objects.filter(workspace=workspace)
    new_deliverables = deliverables_qs.filter(created_at__gte=cutoff)
    updated_deliverables = deliverables_qs.filter(updated_at__gte=cutoff).exclude(
        created_at__gte=cutoff
    )

    initiative_ids = list(
        deliverables_qs.exclude(initiative__isnull=True)
        .values_list("initiative_id", flat=True)
        .distinct()
    )
    runs_qs = AgentExecution.objects.filter(
        parent_object_id__in=initiative_ids,
        created_at__gte=cutoff,
    ) if initiative_ids else AgentExecution.objects.none()
    failures_qs = runs_qs.filter(status="failed")

    timeline: list[dict] = []
    for d in new_deliverables.order_by("-created_at")[:TIMELINE_CAP]:
        timeline.append(
            {
                "kind": "deliverable_created",
                "id": str(d.id),
                "title": d.title,
                "at": d.created_at.isoformat() if d.created_at else None,
            }
        )
    for d in updated_deliverables.order_by("-updated_at")[:TIMELINE_CAP]:
        timeline.append(
            {
                "kind": "deliverable_updated",
                "id": str(d.id),
                "title": d.title,
                "at": d.updated_at.isoformat() if d.updated_at else None,
            }
        )
    for run in failures_qs.select_related("agent").order_by("-created_at")[:TIMELINE_CAP]:
        agent_name = run.agent.name if run.agent_id else ""
        timeline.append(
            {
                "kind": "agent_run_failed",
                "id": str(run.id),
                "agent": agent_name,
                "at": (run.completed_at or run.created_at).isoformat(),
            }
        )
    timeline.sort(key=lambda item: item.get("at") or "", reverse=True)

    return {
        "window_hours": NOW_WINDOW_HOURS,
        "runs_count": runs_qs.count(),
        "failures_count": failures_qs.count(),
        "new_deliverables_count": new_deliverables.count(),
        "updated_deliverables_count": updated_deliverables.count(),
        "timeline": timeline[:TIMELINE_CAP],
    }


def _build_active_work(workspace) -> dict:
    """ACTIVE WORK module — initiatives, action items, needs-review."""
    from core.models_deliverables import Deliverable
    from core.models_document_registry import Initiative, InitiativeActionItem

    # Initiatives: ACTIVE first per spec AC-ACTIVE-1.
    initiatives_qs = Initiative.objects.filter(target_workspace=workspace)
    active_first = list(
        initiatives_qs.filter(status=Initiative.Status.ACTIVE).order_by("-updated_at")[
            :SECTION_LIST_CAP
        ]
    )
    remaining_slots = max(0, SECTION_LIST_CAP - len(active_first))
    other_stages = list(
        initiatives_qs.exclude(status=Initiative.Status.ACTIVE).order_by("-updated_at")[
            :remaining_slots
        ]
    ) if remaining_slots else []

    initiatives_out = []
    for init in active_first + other_stages:
        initiatives_out.append(
            {
                "id": str(init.id),
                "name": init.name,
                "status": init.status,
                "stage": init.current_stage,
                "updated_at": init.updated_at.isoformat() if init.updated_at else None,
                "next_action": init.next_action or "",
                "action_items_count": init.action_items.filter(
                    status__in=(
                        InitiativeActionItem.Status.PENDING,
                        InitiativeActionItem.Status.IN_PROGRESS,
                    )
                ).count(),
            }
        )

    # Action items — priority-weighted (CRITICAL > HIGH > MEDIUM > LOW).
    priority_order = ["critical", "high", "medium", "low"]
    action_items_qs = InitiativeActionItem.objects.filter(
        initiative__target_workspace=workspace,
        status__in=(
            InitiativeActionItem.Status.PENDING,
            InitiativeActionItem.Status.IN_PROGRESS,
        ),
    ).select_related("initiative")

    action_items_out: list[dict] = []
    for prio in priority_order:
        for item in action_items_qs.filter(priority=prio).order_by("order", "created_at"):
            if len(action_items_out) >= SECTION_LIST_CAP:
                break
            action_items_out.append(
                {
                    "id": str(item.id),
                    "title": item.title,
                    "priority": item.priority,
                    "status": item.status,
                    "initiative_id": str(item.initiative_id),
                    "initiative_name": item.initiative.name,
                }
            )
        if len(action_items_out) >= SECTION_LIST_CAP:
            break

    # Needs review — ready deliverables (pending_decisions left as [] for PR1).
    ready_deliverables = list(
        Deliverable.objects.filter(workspace=workspace, status="ready")
        .order_by("-updated_at")[:SECTION_LIST_CAP]
    )

    return {
        "initiatives": initiatives_out,
        "action_items": action_items_out,
        "needs_review": {
            "ready_deliverables": [_serialize_deliverable_card(d) for d in ready_deliverables],
            "pending_decisions": [],
        },
    }


def _build_library(workspace) -> dict:
    """LIBRARY module — pinned first, then recently updated (excluding pinned)."""
    from core.models_deliverables import Deliverable

    workspace_qs = Deliverable.objects.filter(workspace=workspace)

    pinned = list(
        workspace_qs.filter(is_pinned=True).order_by("-updated_at")[:SECTION_LIST_CAP]
    )
    pinned_ids = {d.id for d in pinned}
    recent = list(
        workspace_qs.exclude(id__in=pinned_ids).order_by("-updated_at")[:SECTION_LIST_CAP]
    )

    return {
        "pinned": [_serialize_deliverable_card(d) for d in pinned],
        "recent": [_serialize_deliverable_card(d) for d in recent],
    }


def _empty_now() -> dict:
    return {
        "window_hours": NOW_WINDOW_HOURS,
        "runs_count": 0,
        "failures_count": 0,
        "new_deliverables_count": 0,
        "updated_deliverables_count": 0,
        "timeline": [],
    }


def _empty_active_work() -> dict:
    return {
        "initiatives": [],
        "action_items": [],
        "needs_review": {"ready_deliverables": [], "pending_decisions": []},
    }


def _empty_library() -> dict:
    return {"pinned": [], "recent": []}


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def workspace_home_snapshot(request, workspace_id):
    """
    Workspace Home snapshot endpoint (spec §3.1).

    Returns NOW / ACTIVE WORK / LIBRARY sections for the workspace Home tab.
    Each section is computed in isolation; failures log a warning and return
    empty defaults so partial rendering is possible (spec §"Implementation
    notes").
    """
    from core.models_skin_layer import ProjectWorkspace

    try:
        workspace = _get_workspace(workspace_id, request.user)
    except ProjectWorkspace.DoesNotExist:
        return Response({"success": False, "error": "Workspace not found"}, status=404)

    cutoff = timezone.now() - timedelta(hours=NOW_WINDOW_HOURS)

    try:
        now_payload = _build_now(workspace, cutoff)
    except Exception:
        logger.warning("workspace_home.now section failed", exc_info=True, extra={"workspace_id": str(workspace_id)})
        now_payload = _empty_now()

    try:
        active_work_payload = _build_active_work(workspace)
    except Exception:
        logger.warning("workspace_home.active_work section failed", exc_info=True, extra={"workspace_id": str(workspace_id)})
        active_work_payload = _empty_active_work()

    try:
        library_payload = _build_library(workspace)
    except Exception:
        logger.warning("workspace_home.library section failed", exc_info=True, extra={"workspace_id": str(workspace_id)})
        library_payload = _empty_library()

    return Response(
        {
            "workspace": {
                "id": str(workspace.id),
                "name": workspace.name,
            },
            "now": now_payload,
            "active_work": active_work_payload,
            "library": library_payload,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def workspace_shift_brief(request, workspace_id):
    """
    Guided Action §2.4 "Run Shift Brief".

    Invokes core.services.rigby_shift_brief.build_shift_brief synchronously
    (bounded by SUB_TOOL_TIMEOUT_SECONDS per parallel sub-tool per the
    service) and returns the result dict.

    Workspace is validated for owner access via _get_workspace but v1 does
    NOT scope the brief itself to the workspace — build_shift_brief takes
    conversation_id, not workspace_id (Rigby T1 SIGN REVISE ship
    recommendation for PR4 MVP; workspace-scoping wrapper deferred to a
    follow-up if the surface proves useful).
    """
    from core.models_skin_layer import ProjectWorkspace
    from core.services.rigby_shift_brief import build_shift_brief

    try:
        workspace = _get_workspace(workspace_id, request.user)
    except ProjectWorkspace.DoesNotExist:
        return Response({"success": False, "error": "Workspace not found"}, status=404)

    try:
        brief = build_shift_brief(user_id=request.user.id, conversation_id=None, window="24h")
    except Exception:
        logger.warning(
            "workspace_shift_brief failed",
            exc_info=True,
            extra={"workspace_id": str(workspace_id)},
        )
        return Response(
            {"ok": False, "error": "shift_brief_failed", "workspace_id": str(workspace.id)},
            status=502,
        )

    return Response(
        {
            "ok": bool(brief.get("ok")),
            "summary_text": brief.get("summary_text", ""),
            "traffic_light": brief.get("traffic_light", "GREEN"),
            "sections": brief.get("sections", {}),
            "metadata": brief.get("metadata", {}),
            "workspace_id": str(workspace.id),
            "generated_at": timezone.now().isoformat(),
        }
    )
