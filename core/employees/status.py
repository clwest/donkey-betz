"""
AI Employee status + evidence derivation (Session 1253 PR 3).

Pure-function helpers for the daily-read status surface exposed via
``employee_tool action=status`` and ``employee_tool
action=evidence_for_mission``.

Hard constraints (per PR 3 plan + Rigby SIGN-WITH-EDITS):

  * No new model. No migration. Trust ratio is **derived on read**,
    never persisted.
  * `evidence_for_mission` is a separate action — not inlined in
    status. If `status` is called with `mission_id`, it returns a
    pointer telling the caller to use `evidence_for_mission`.
  * `verbose=false` (the default for `evidence_for_mission`) returns
    `error_tail_preview` (last 30 lines) + `has_full_error_tail`.
    `verbose=true` returns the full `error_tail`.
  * Deferred verdicts are neutral for trust math:
    `trust_ratio = certified / (certified + rejected)`; null when
    denominator is zero. `missions.total` includes everything.
  * `trust_status='under_review'` when there are ≥3 rejected missions
    in the LAST 7 DAYS, regardless of the caller-requested window.
  * Surfaces stale-pin evidence on `latest_mission` when an escalation
    PA post is correlated: `pa_post.conversation_id`,
    `settings_primary_pin`, `pin_matches_settings`.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.utils import timezone


# Last-N-lines error-tail preview (Rigby amendment 2).
ERROR_TAIL_PREVIEW_LINES = 30

# Under-review trip-wire (Rigby amendment 4 — keep at 7 days regardless
# of caller-requested window).
UNDER_REVIEW_WINDOW_DAYS = 7
UNDER_REVIEW_REJECTED_THRESHOLD = 3

# OpsRun.summary verdict values produced by the docs_cascade task +
# mission_verdict helper. Mirrors core/employees/mission_verdict.py
# without importing it (keeps this module test-light).
VERDICT_CERTIFIED = "certified"
VERDICT_REJECTED = "rejected"
VERDICT_DEFERRED = "deferred"


def derive_status(
    *,
    employee_handle: str,
    employee_display_name: str,
    job_key: str,
    job_display_name: str,
    mission_run_kind: str,
    window_days: int,
    mission_id_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """Compute the read-only status response for one (employee, job).

    Pure ORM aggregation against ``OpsRun(domain='mission',
    run_kind=mission_run_kind)``. No writes. No new model.

    ``mission_id_hint`` is the optional opt-in pointer redirect — when
    the caller passes ``mission_id`` to the status action, we surface
    a pointer to ``evidence_for_mission`` rather than inlining the
    evidence here.
    """
    from core.models_ops_runs import OpsRun

    now = timezone.now()
    window_start = now - timedelta(days=window_days)
    short_window_start = now - timedelta(days=UNDER_REVIEW_WINDOW_DAYS)

    # Caller window — the lens.
    base_qs = OpsRun.objects.filter(
        domain="mission",
        run_kind=mission_run_kind,
        started_at__gte=window_start,
    ).order_by("-started_at")

    # Materialize fields we need; avoid N+1 by reading summary JSON in
    # Python rather than another query per row.
    rows = list(
        base_qs.values(
            "id",
            "status",
            "triggered_by",
            "started_at",
            "finished_at",
            "summary",
        )
    )

    total = len(rows)
    certified = 0
    rejected = 0
    deferred = 0
    in_progress = 0
    last_certified_at = None
    last_escalation_at = None
    wall_times: List[int] = []
    drift_counts: List[int] = []
    degraded_evidence_count = 0
    last_drift_count: Optional[int] = None

    for row in rows:
        verdict = (row["summary"] or {}).get("verdict")
        if verdict == VERDICT_CERTIFIED:
            certified += 1
            if last_certified_at is None:
                last_certified_at = row["started_at"]
        elif verdict == VERDICT_REJECTED:
            rejected += 1
        elif verdict == VERDICT_DEFERRED:
            deferred += 1
        if row["status"] in ("running", "pending"):
            in_progress += 1

        summary = row["summary"] or {}
        if summary.get("escalation_deliverable_id"):
            if last_escalation_at is None:
                last_escalation_at = row["started_at"]
        wall = summary.get("wall_time_ms")
        if isinstance(wall, (int, float)):
            wall_times.append(int(wall))
        drift = summary.get("drift_count")
        if isinstance(drift, int):
            drift_counts.append(drift)
            if last_drift_count is None:
                last_drift_count = drift
        if summary.get("degraded_evidence") is True:
            degraded_evidence_count += 1

    # Trust ratio — Rigby amendment 3.
    denom = certified + rejected
    if denom == 0:
        trust_ratio: Optional[float] = None
    else:
        trust_ratio = round(certified / denom, 4)

    # Trust status — fixed 7d trip-wire (Rigby amendment 4).
    if total == 0:
        trust_status = "no_data"
    else:
        recent_rejected = OpsRun.objects.filter(
            domain="mission",
            run_kind=mission_run_kind,
            started_at__gte=short_window_start,
            summary__verdict=VERDICT_REJECTED,
        ).count()
        if recent_rejected >= UNDER_REVIEW_REJECTED_THRESHOLD:
            trust_status = "under_review"
        else:
            trust_status = "healthy"

    # Streak — walk most-recent-first, count consecutive matching verdict.
    if rows:
        latest_verdict = (rows[0]["summary"] or {}).get("verdict")
        streak = 0
        if latest_verdict in (
            VERDICT_CERTIFIED, VERDICT_REJECTED, VERDICT_DEFERRED
        ):
            for row in rows:
                if (row["summary"] or {}).get("verdict") == latest_verdict:
                    streak += 1
                else:
                    break
        current_streak = streak
        current_streak_kind = latest_verdict if streak > 0 else "none"
    else:
        current_streak = 0
        current_streak_kind = "none"

    avg_wall_time = (
        int(sum(wall_times) / len(wall_times)) if wall_times else None
    )
    p95_wall_time = _percentile(wall_times, 95) if wall_times else None
    avg_drift_count = (
        int(sum(drift_counts) / len(drift_counts))
        if drift_counts
        else None
    )

    latest_mission = (
        _shape_latest_mission(rows[0]) if rows else None
    )

    response: Dict[str, Any] = {
        "ok": True,
        "action": "status",
        "employee": employee_handle,
        "employee_display_name": employee_display_name,
        "job": job_key,
        "job_display_name": job_display_name,
        "window_days": window_days,
        "window_start": window_start.isoformat(),
        "window_end": now.isoformat(),
        "as_of": now.isoformat(),
        "missions": {
            "total": total,
            "certified": certified,
            "rejected": rejected,
            "deferred": deferred,
            "in_progress": in_progress,
        },
        "trust": {
            "ratio": trust_ratio,
            "status": trust_status,
            "current_streak": current_streak,
            "current_streak_kind": current_streak_kind,
        },
        "timing": {
            "last_mission_at": (
                rows[0]["started_at"].isoformat() if rows else None
            ),
            "last_certified_at": (
                last_certified_at.isoformat() if last_certified_at else None
            ),
            "last_escalation_at": (
                last_escalation_at.isoformat()
                if last_escalation_at
                else None
            ),
            "avg_wall_time_ms": avg_wall_time,
            "p95_wall_time_ms": p95_wall_time,
        },
        "drift": {
            "last_drift_count": last_drift_count,
            "avg_drift_count": avg_drift_count,
            "degraded_evidence_count": degraded_evidence_count,
        },
        "latest_mission": latest_mission,
    }

    if mission_id_hint:
        response["requested_mission_pointer"] = {
            "mission_id": mission_id_hint,
            "evidence_action": "evidence_for_mission",
            "note": (
                "status does not inline evidence; call "
                "employee_tool action=evidence_for_mission "
                f"mission_id={mission_id_hint} to retrieve."
            ),
        }

    return response


def _shape_latest_mission(row: Dict[str, Any]) -> Dict[str, Any]:
    """Project a single OpsRun row into the latest_mission shape.

    Includes the stale-pin evidence block (Rigby amendment 5) for the
    escalation, when one exists.
    """
    summary = row["summary"] or {}
    escalation_deliverable_id = summary.get("escalation_deliverable_id")
    has_escalation = bool(escalation_deliverable_id)

    pa_post_block: Optional[Dict[str, Any]] = None
    settings_pin = getattr(settings, "RIGBY_PRIMARY_PA_PIN", "") or None
    if has_escalation and summary.get("escalation_pa_post_id"):
        pa_post_block = _resolve_pa_post_pin(
            summary.get("escalation_pa_post_id"), settings_pin
        )

    return {
        "mission_id": str(row["id"]),
        "triggered_by": row["triggered_by"],
        "status": row["status"],
        "verdict": summary.get("verdict"),
        "verdict_confidence": summary.get("verdict_confidence"),
        "started_at": (
            row["started_at"].isoformat() if row["started_at"] else None
        ),
        "finished_at": (
            row["finished_at"].isoformat()
            if row["finished_at"]
            else None
        ),
        "wall_time_ms": summary.get("wall_time_ms"),
        "failed_step": summary.get("failed_step"),
        "error_signature": summary.get("error_signature"),  # nullable
        "has_escalation": has_escalation,
        "escalation_deliverable_id": escalation_deliverable_id,
        "pa_post": pa_post_block,
    }


def _resolve_pa_post_pin(
    chat_pk_str: Any, settings_pin: Optional[str]
) -> Dict[str, Any]:
    """Resolve the PA post pk to its actual conversation_id pin.

    Surfaces the stale-pin scenario where the worker posted to the
    contract-constant pin while ``settings.RIGBY_PRIMARY_PA_PIN`` was
    pointing somewhere else. ``pin_matches_settings`` is:

      * ``true``  — actual pin equals settings pin (env override worked)
      * ``false`` — actual pin differs from settings (stale-pin post)
      * ``null``  — couldn't resolve (settings unset OR PA post not found)
    """
    from core.models import ChatConversation

    try:
        chat_pk = int(chat_pk_str)
    except (TypeError, ValueError):
        return {
            "chat_pk": chat_pk_str,
            "conversation_id": None,
            "settings_primary_pin": settings_pin,
            "pin_matches_settings": None,
            "note": "Could not parse escalation_pa_post_id as int.",
        }

    try:
        chat = ChatConversation.objects.only(
            "id", "conversation_id"
        ).get(pk=chat_pk)
    except ChatConversation.DoesNotExist:
        return {
            "chat_pk": chat_pk,
            "conversation_id": None,
            "settings_primary_pin": settings_pin,
            "pin_matches_settings": None,
            "note": "ChatConversation row not found.",
        }

    actual_pin = chat.conversation_id
    if settings_pin is None or actual_pin is None:
        matches = None
    else:
        matches = actual_pin == settings_pin

    return {
        "chat_pk": chat_pk,
        "conversation_id": actual_pin,
        "settings_primary_pin": settings_pin,
        "pin_matches_settings": matches,
    }


def evidence_for_mission(
    *, mission_id: str, verbose: bool = False
) -> Dict[str, Any]:
    """Join the 5+ evidence tables for one mission.

    Pure read. Returns a structured evidence dump for postmortem.
    ``verbose=False`` (default) returns ``error_tail_preview`` (last
    ``ERROR_TAIL_PREVIEW_LINES`` lines of the full tail) plus
    ``has_full_error_tail``. ``verbose=True`` returns the full
    ``error_tail``.
    """
    from core.models import ChatConversation
    from core.models_deliverables import Deliverable, DeliverableEvent
    from core.models_llm_telemetry import LLMCallEvent
    from core.models_ops_runs import OpsRun, OpsRunEvent
    from core.models_tool_calls import ToolCallRecord

    try:
        run = OpsRun.objects.get(id=mission_id)
    except (OpsRun.DoesNotExist, ValueError):
        return {
            "ok": False,
            "error": "mission_not_found",
            "mission_id": mission_id,
        }

    summary = dict(run.summary or {})
    full_tail = summary.get("error_tail")

    if not verbose and isinstance(full_tail, str):
        preview = _last_n_lines(full_tail, ERROR_TAIL_PREVIEW_LINES)
        summary["error_tail_preview"] = preview
        summary["has_full_error_tail"] = full_tail != preview
        summary.pop("error_tail", None)
    elif not verbose:
        summary["error_tail_preview"] = None
        summary["has_full_error_tail"] = False
        summary.pop("error_tail", None)

    events = [
        {"created_at": ev.created_at.isoformat(), "label": ev.label}
        for ev in OpsRunEvent.objects.filter(run=run).order_by("created_at")
    ]

    escalation = {
        "deliverable": None,
        "deliverable_events": [],
        "pa_post": None,
    }
    escalation_deliverable_id = (run.summary or {}).get(
        "escalation_deliverable_id"
    )
    if escalation_deliverable_id:
        try:
            deliv = Deliverable.objects.only(
                "id",
                "status",
                "publish_intent",
                "title",
                "created_at",
            ).get(id=escalation_deliverable_id)
            escalation["deliverable"] = {
                "id": str(deliv.id),
                "status": deliv.status,
                "publish_intent": deliv.publish_intent,
                "title": deliv.title,
                "created_at": deliv.created_at.isoformat(),
            }
        except Deliverable.DoesNotExist:
            escalation["deliverable"] = {
                "id": escalation_deliverable_id,
                "error": "deliverable_not_found",
            }

    # DeliverableEvent rows correlated by ctx.ops_run_id in metadata.
    de_qs = DeliverableEvent.objects.filter(
        event_type="status_transition",
        source="DocsManager",
        metadata__ctx__ops_run_id=str(run.id),
    ).order_by("created_at")
    for de in de_qs:
        ctx = (de.metadata or {}).get("ctx") or {}
        escalation["deliverable_events"].append({
            "created_at": de.created_at.isoformat(),
            "event_type": de.event_type,
            "source": de.source,
            "ctx": {
                "previous_status": ctx.get("previous_status"),
                "new_status": ctx.get("new_status"),
                "ops_run_id": ctx.get("ops_run_id"),
                "error_signature": ctx.get("error_signature"),
            },
        })

    pa_post_pk = (run.summary or {}).get("escalation_pa_post_id")
    if pa_post_pk:
        try:
            chat = ChatConversation.objects.only(
                "id", "conversation_id", "created_at"
            ).get(pk=int(pa_post_pk))
            escalation["pa_post"] = {
                "chat_pk": chat.id,
                "conversation_id": chat.conversation_id,
                "created_at": chat.created_at.isoformat(),
            }
        except (ChatConversation.DoesNotExist, TypeError, ValueError):
            escalation["pa_post"] = {
                "chat_pk": pa_post_pk,
                "error": "chat_conversation_not_found",
            }

    # LLMCallEvent — correlated by metadata.ops_run_id when present.
    # docs_cascade doesn't emit any today; future-proof empty list.
    llm_calls = []
    for evt in LLMCallEvent.objects.filter(
        metadata__ops_run_id=str(run.id)
    ).order_by("started_at"):
        llm_calls.append({
            "call_id": str(evt.call_id),
            "agent_name": evt.agent_name,
            "provider": evt.provider,
            "model": evt.model,
            "status": evt.status,
        })

    # ToolCallRecord — no native ops_run column; correlate via parameters
    # JSON if any future cascade step records one. Empty for v0.
    tool_calls = []
    for rec in ToolCallRecord.objects.filter(
        parameters__ops_run_id=str(run.id)
    ).order_by("created_at"):
        tool_calls.append({
            "id": str(rec.id),
            "agent_name": rec.agent_name,
            "tool_name": rec.tool_name,
            "success": rec.success,
        })

    return {
        "ok": True,
        "action": "evidence_for_mission",
        "verbose": verbose,
        "mission_id": str(run.id),
        "ops_run": {
            "id": str(run.id),
            "domain": run.domain,
            "run_kind": run.run_kind,
            "status": run.status,
            "triggered_by": run.triggered_by,
            "started_at": (
                run.started_at.isoformat() if run.started_at else None
            ),
            "finished_at": (
                run.finished_at.isoformat() if run.finished_at else None
            ),
            "summary": summary,
        },
        "events": events,
        "escalation": escalation,
        "llm_calls": llm_calls,
        "tool_calls": tool_calls,
    }


def _last_n_lines(text: str, n: int) -> str:
    """Return the last `n` lines of `text` (preserves trailing newline)."""
    if not text:
        return text
    lines = text.splitlines()
    if len(lines) <= n:
        return text
    return "\n".join(lines[-n:])


def _percentile(values: List[int], pct: int) -> Optional[int]:
    """Naive p_n percentile — sufficient for v0 (~100 rows max)."""
    if not values:
        return None
    sorted_vals = sorted(values)
    k = max(0, min(len(sorted_vals) - 1, (len(sorted_vals) * pct) // 100))
    return sorted_vals[k]
