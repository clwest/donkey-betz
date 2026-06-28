"""
ToolDispatcher mixin for ``rigby_work_item`` PA tool actions (Session
1250 PR 7).

Surface: ``rigby_work_item`` tool with four actions:
- ``list`` — paginated read with filters
  (status / decision / priority_min / since).
- ``acknowledge`` — transition ``open → acknowledged``.
- ``resolve`` — transition any non-resolved state → ``resolved`` with
  closed-vocab ``outcome``.
- ``ignore`` — transition any non-ignored state → ``ignored`` with
  required ``reason``.

Every state transition writes an ``OpsRunEvent`` row on the parent
``MissionRun`` (per §14 design — Option A from PR 7 spec). The audit
trail lives in the existing MissionRun timeline; no separate
transition table.

Guardrails:
- No human notification surface called from this module.
- No agent dispatch.
- No initiative / tool dispatch.
- Gated by ``settings.RIGBY_WORK_QUEUE_REVIEW_ENABLED`` (default
  False). When OFF, the handler short-circuits to a structured
  "tools disabled" response.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime


logger = logging.getLogger(__name__)


# Closed vocabulary for the rigby_work_item.resolve outcome field.
RESOLVE_OUTCOME_VOCAB: frozenset[str] = frozenset(
    {"acted", "delegated_externally", "no_action_needed"}
)

# Status vocab (mirrors RigbyWorkItem.STATUS_CHOICES).
STATUS_OPEN = "open"
STATUS_ACKNOWLEDGED = "acknowledged"
STATUS_RESOLVED = "resolved"
STATUS_IGNORED = "ignored"
TERMINAL_STATUSES: frozenset[str] = frozenset({STATUS_RESOLVED, STATUS_IGNORED})


# Stable lifecycle labels written into OpsRunEvent (parent MissionRun
# timeline). Future PRs that add more transitions must keep these
# stable.
LABEL_ACKNOWLEDGED = "work_item_acknowledged"
LABEL_RESOLVED = "work_item_resolved"
LABEL_IGNORED = "work_item_ignored"


def _disabled_response(action: str) -> dict[str, Any]:
    """Standard response when the review flag is OFF."""
    return {
        "ok": False,
        "action": action,
        "gateway": "rigby_work_item",
        "error": "rigby_work_item review tools are disabled (flag off)",
        "flag": "RIGBY_WORK_QUEUE_REVIEW_ENABLED",
    }


def _serialize_work_item(item) -> dict[str, Any]:
    """Stable serialization for list/transition responses."""
    return {
        "id": str(item.id),
        "source_event_ref": item.source_event_ref,
        "source_mission_run_id": str(item.source_mission_run_id),
        "decision": item.decision,
        "severity": item.severity,
        "mission_impact": item.mission_impact,
        "priority": item.priority,
        "status": item.status,
        "title": item.title,
        "summary": item.summary,
        "recommended_next_action": item.recommended_next_action,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "resolved_at": (
            item.resolved_at.isoformat() if item.resolved_at else None
        ),
    }


def _write_transition_event(
    *,
    work_item,
    label: str,
    from_status: str,
    to_status: str,
    detail_extra: Optional[dict[str, Any]] = None,
) -> None:
    """Append an OpsRunEvent on the parent MissionRun for this
    transition. Option-A design — single authoritative record."""
    from core.models_ops_runs import OpsRunEvent

    detail: dict[str, Any] = {
        "work_item_id": str(work_item.id),
        "from_status": from_status,
        "to_status": to_status,
    }
    if detail_extra:
        detail.update(detail_extra)
    # event_type: 'info' for acknowledge, 'step_pass' for resolve,
    # 'info' for ignore (matches the established convention from PR 4).
    event_type = "step_pass" if label == LABEL_RESOLVED else "info"
    OpsRunEvent.objects.create(
        run_id=work_item.source_mission_run_id,
        event_type=event_type,
        label=label,
        detail=detail,
    )


class RigbyWorkQueueReviewMixin:
    """Mixin providing the ``rigby_work_item`` tool handler.

    Registered in ``ToolDispatcher.__init__`` only when
    ``settings.RIGBY_WORK_QUEUE_REVIEW_ENABLED`` is True. When False,
    the dispatcher exposes a thin gatekeeper handler that returns a
    standard "tools disabled" response so the LLM gets a clear signal
    without the dispatcher falling through to its generic
    "unknown tool" path.
    """

    # ----------------------------------------------------------------
    # Entrypoint dispatcher (per-action routing)
    # ----------------------------------------------------------------

    def _handle_rigby_work_item(
        self, tool_name, payload, user_id, trace_id
    ) -> dict[str, Any]:
        action = (payload or {}).get("action", "list") if isinstance(payload, dict) else "list"

        if not getattr(settings, "RIGBY_WORK_QUEUE_REVIEW_ENABLED", False):
            return _disabled_response(action)

        if action == "list":
            return self._rigby_work_item_list(payload, user_id, trace_id)
        if action == "acknowledge":
            return self._rigby_work_item_acknowledge(payload, user_id, trace_id)
        if action == "resolve":
            return self._rigby_work_item_resolve(payload, user_id, trace_id)
        if action == "ignore":
            return self._rigby_work_item_ignore(payload, user_id, trace_id)

        return {
            "ok": False,
            "action": action,
            "gateway": "rigby_work_item",
            "error": f"Unknown action {action!r}. Supported: list / acknowledge / resolve / ignore.",
        }

    # ----------------------------------------------------------------
    # Action: list
    # ----------------------------------------------------------------

    def _rigby_work_item_list(self, payload, user_id, trace_id) -> dict[str, Any]:
        from core.models_rigby_work_items import RigbyWorkItem

        p = payload or {}
        qs = RigbyWorkItem.objects.all()

        # Filters
        status = p.get("status")
        if status:
            qs = qs.filter(status=status)
        decision = p.get("decision")
        if decision:
            qs = qs.filter(decision=decision)
        priority_min = p.get("priority_min")
        if isinstance(priority_min, int) and priority_min > 0:
            qs = qs.filter(priority__gte=priority_min)
        since = p.get("since")
        if since:
            if isinstance(since, str):
                since_dt = parse_datetime(since)
            elif isinstance(since, datetime):
                since_dt = since
            else:
                since_dt = None
            if since_dt is not None:
                qs = qs.filter(created_at__gte=since_dt)

        # Pagination — cap at 100, default 25.
        try:
            limit = int(p.get("limit", 25))
        except (TypeError, ValueError):
            limit = 25
        limit = max(1, min(limit, 100))
        try:
            offset = int(p.get("offset", 0))
        except (TypeError, ValueError):
            offset = 0
        offset = max(0, offset)

        # Ordering — already on Meta but be explicit for the API
        # contract: priority DESC, created_at DESC.
        qs = qs.order_by("-priority", "-created_at")
        total = qs.count()
        rows = [_serialize_work_item(it) for it in qs[offset : offset + limit]]

        return {
            "ok": True,
            "action": "list",
            "gateway": "rigby_work_item",
            "rows": rows,
            "total": total,
            "limit": limit,
            "offset": offset,
            "applied_filters": {
                "status": status,
                "decision": decision,
                "priority_min": priority_min if (isinstance(priority_min, int) and priority_min > 0) else None,
                "since": since,
            },
        }

    # ----------------------------------------------------------------
    # Action: acknowledge
    # ----------------------------------------------------------------

    def _rigby_work_item_acknowledge(self, payload, user_id, trace_id) -> dict[str, Any]:
        from core.models_rigby_work_items import RigbyWorkItem

        p = payload or {}
        work_item_id = p.get("work_item_id") or p.get("id")
        if not work_item_id:
            return {
                "ok": False,
                "action": "acknowledge",
                "gateway": "rigby_work_item",
                "error": "work_item_id is required",
            }
        note = (p.get("note") or "").strip()

        try:
            item = RigbyWorkItem.objects.get(id=work_item_id)
        except RigbyWorkItem.DoesNotExist:
            return {
                "ok": False,
                "action": "acknowledge",
                "gateway": "rigby_work_item",
                "error": f"RigbyWorkItem {work_item_id} not found",
            }

        # Terminal items can't be re-opened or re-acknowledged.
        if item.status in TERMINAL_STATUSES:
            return {
                "ok": False,
                "action": "acknowledge",
                "gateway": "rigby_work_item",
                "error": (
                    f"Cannot acknowledge a {item.status} work item. "
                    f"Allowed source states: open, acknowledged."
                ),
                "work_item": _serialize_work_item(item),
            }

        # Idempotent: already acknowledged → no-op, no new audit row.
        if item.status == STATUS_ACKNOWLEDGED:
            return {
                "ok": True,
                "action": "acknowledge",
                "gateway": "rigby_work_item",
                "no_op": True,
                "work_item": _serialize_work_item(item),
            }

        from_status = item.status
        with transaction.atomic():
            item.status = STATUS_ACKNOWLEDGED
            item.save(update_fields=["status", "updated_at"])
            _write_transition_event(
                work_item=item,
                label=LABEL_ACKNOWLEDGED,
                from_status=from_status,
                to_status=STATUS_ACKNOWLEDGED,
                detail_extra={"note": note} if note else {"note": ""},
            )

        return {
            "ok": True,
            "action": "acknowledge",
            "gateway": "rigby_work_item",
            "work_item": _serialize_work_item(item),
            "transition": {
                "from": from_status,
                "to": STATUS_ACKNOWLEDGED,
                "note": note,
            },
        }

    # ----------------------------------------------------------------
    # Action: resolve
    # ----------------------------------------------------------------

    def _rigby_work_item_resolve(self, payload, user_id, trace_id) -> dict[str, Any]:
        from core.models_rigby_work_items import RigbyWorkItem

        p = payload or {}
        work_item_id = p.get("work_item_id") or p.get("id")
        outcome = (p.get("outcome") or "").strip()
        note = (p.get("note") or "").strip()

        if not work_item_id:
            return {
                "ok": False,
                "action": "resolve",
                "gateway": "rigby_work_item",
                "error": "work_item_id is required",
            }
        if outcome not in RESOLVE_OUTCOME_VOCAB:
            return {
                "ok": False,
                "action": "resolve",
                "gateway": "rigby_work_item",
                "error": (
                    f"outcome is required and must be one of "
                    f"{sorted(RESOLVE_OUTCOME_VOCAB)}; got {outcome!r}"
                ),
            }

        try:
            item = RigbyWorkItem.objects.get(id=work_item_id)
        except RigbyWorkItem.DoesNotExist:
            return {
                "ok": False,
                "action": "resolve",
                "gateway": "rigby_work_item",
                "error": f"RigbyWorkItem {work_item_id} not found",
            }

        if item.status == STATUS_RESOLVED:
            # Idempotent: already resolved, no new audit row.
            return {
                "ok": True,
                "action": "resolve",
                "gateway": "rigby_work_item",
                "no_op": True,
                "work_item": _serialize_work_item(item),
            }
        if item.status == STATUS_IGNORED:
            return {
                "ok": False,
                "action": "resolve",
                "gateway": "rigby_work_item",
                "error": (
                    "Cannot resolve an ignored work item. Allowed source "
                    "states: open, acknowledged."
                ),
                "work_item": _serialize_work_item(item),
            }

        from_status = item.status
        with transaction.atomic():
            item.status = STATUS_RESOLVED
            item.resolved_at = timezone.now()
            item.save(update_fields=["status", "resolved_at", "updated_at"])
            _write_transition_event(
                work_item=item,
                label=LABEL_RESOLVED,
                from_status=from_status,
                to_status=STATUS_RESOLVED,
                detail_extra={"outcome": outcome, "note": note},
            )

        return {
            "ok": True,
            "action": "resolve",
            "gateway": "rigby_work_item",
            "work_item": _serialize_work_item(item),
            "transition": {
                "from": from_status,
                "to": STATUS_RESOLVED,
                "outcome": outcome,
                "note": note,
            },
        }

    # ----------------------------------------------------------------
    # Action: ignore
    # ----------------------------------------------------------------

    def _rigby_work_item_ignore(self, payload, user_id, trace_id) -> dict[str, Any]:
        from core.models_rigby_work_items import RigbyWorkItem

        p = payload or {}
        work_item_id = p.get("work_item_id") or p.get("id")
        reason = (p.get("reason") or "").strip()

        if not work_item_id:
            return {
                "ok": False,
                "action": "ignore",
                "gateway": "rigby_work_item",
                "error": "work_item_id is required",
            }
        if not reason:
            return {
                "ok": False,
                "action": "ignore",
                "gateway": "rigby_work_item",
                "error": "reason is required and must be a non-empty string",
            }

        try:
            item = RigbyWorkItem.objects.get(id=work_item_id)
        except RigbyWorkItem.DoesNotExist:
            return {
                "ok": False,
                "action": "ignore",
                "gateway": "rigby_work_item",
                "error": f"RigbyWorkItem {work_item_id} not found",
            }

        if item.status == STATUS_IGNORED:
            return {
                "ok": True,
                "action": "ignore",
                "gateway": "rigby_work_item",
                "no_op": True,
                "work_item": _serialize_work_item(item),
            }
        if item.status == STATUS_RESOLVED:
            return {
                "ok": False,
                "action": "ignore",
                "gateway": "rigby_work_item",
                "error": (
                    "Cannot ignore a resolved work item. Allowed source "
                    "states: open, acknowledged."
                ),
                "work_item": _serialize_work_item(item),
            }

        from_status = item.status
        with transaction.atomic():
            item.status = STATUS_IGNORED
            item.save(update_fields=["status", "updated_at"])
            _write_transition_event(
                work_item=item,
                label=LABEL_IGNORED,
                from_status=from_status,
                to_status=STATUS_IGNORED,
                detail_extra={"reason": reason},
            )

        return {
            "ok": True,
            "action": "ignore",
            "gateway": "rigby_work_item",
            "work_item": _serialize_work_item(item),
            "transition": {
                "from": from_status,
                "to": STATUS_IGNORED,
                "reason": reason,
            },
        }
