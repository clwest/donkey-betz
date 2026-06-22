"""Session 1198 — §6.2 Phase 2 inference cascade.

Pure function that maps ``(payload, tool_context, owner_agent) → initiative_id``
when callers omit ``initiative_id`` from a deliverable create call.
Used by ``deliverable_factory.create_deliverable()`` BEFORE the
orphan-detection / Phase 1 diagnostic / Phase 2 hard-reject path.

Design memo: docs/specs/INITIATIVES_FIRST_BACKBONE.md §6.2 (full
write-up lands in PR1E). Locked in conversation
``pa-ea12236c83eb4826`` with Rigby.

Cascade (§6.2):

  Step 1 — payload initiative_id   (explicit, confidence 1.00)
  Step 2 — tool_context initiative (propagated, confidence 0.95)
  Step 3 — agent affinity map      (kind-policy-aware, confidence ≥ 0.90 for project / ≥ 0.70 for investigation)
  Step 4 — heuristics              (PR3 — stubbed, returns None)
  Step 5 — fall through            (caller decides: Phase 1 diagnostic or Phase 2 reject)

All steps share kind-aware policy: ``recurring_artifact`` and
``spec_backlog`` kinds NEVER receive inferred attachments via Steps 3-4
(explicit attachment via Steps 1-2 is still allowed because the caller
opted in). Cross-workspace is a hard stop at every step.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from django.utils import timezone


# --------------------------------------------------------------------- #
# Constants — kind-aware thresholds                                     #
# --------------------------------------------------------------------- #

PROJECT_RECENCY_DAYS = 7
INVESTIGATION_RECENCY_DAYS = 30

PROJECT_CONFIDENCE_FLOOR = 0.90
INVESTIGATION_CONFIDENCE_FLOOR = 0.70

INFERENCE_AUTHORITATIVE_SOURCES = {"static_seed", "manual_pin"}
KINDS_BLOCKED_FROM_INFERENCE = {"recurring_artifact", "spec_backlog"}


# --------------------------------------------------------------------- #
# Result shape                                                          #
# --------------------------------------------------------------------- #


@dataclass
class InferenceResult:
    initiative_id: UUID | str | None
    trace: dict[str, Any] = field(default_factory=dict)

    def as_tuple(self) -> tuple[UUID | str | None, dict[str, Any]]:
        return self.initiative_id, self.trace


# --------------------------------------------------------------------- #
# Entry point                                                           #
# --------------------------------------------------------------------- #


def infer_initiative_id(
    *,
    payload: dict[str, Any],
    tool_context: dict[str, Any] | None = None,
    owner_agent: str | None = None,
    now: datetime | None = None,
) -> tuple[UUID | str | None, dict[str, Any]]:
    """Run the §6.2 cascade. Returns ``(initiative_id_or_none, trace)``.

    Trace is always populated with at least ``step`` and ``reason`` keys
    so callers can emit ``[INFERENCE-MATCH]`` log lines for observability.

    Args:
        payload: Deliverable create payload. Must include ``workspace_id``
            (required by the no-orphan contract). MAY include
            ``initiative_id``.
        tool_context: Optional dict carrying propagated context from the
            tool call chain. MAY include ``initiative_id``.
        owner_agent: Canonical agent name (matches
            ``AgentExecution.owner_agent``).  Used by Step 3 affinity
            lookup.
        now: Override "current time" for tests. Defaults to
            ``timezone.now()``.

    Returns:
        Tuple of ``(initiative_id, trace_dict)``. ``initiative_id`` is
        ``None`` when cascade falls through to Step 5 (caller handles
        Phase 1 diagnostic or Phase 2 reject).
    """
    now = now or timezone.now()
    workspace_id = payload.get("workspace_id")
    if not workspace_id:
        return None, {"step": "guard", "reason": "no_workspace_id_in_payload"}

    # Step 1 — explicit payload initiative_id (authoritative)
    explicit = payload.get("initiative_id")
    if explicit:
        result = _resolve_explicit(explicit, workspace_id, step=1, confidence=1.00)
        if result.initiative_id or result.trace.get("reason") != "workspace_mismatch":
            return result.as_tuple()
        # workspace mismatch on explicit id → record and continue cascade

    # Step 2 — tool_context initiative_id (propagated)
    if tool_context and tool_context.get("initiative_id"):
        ctx_id = tool_context["initiative_id"]
        result = _resolve_explicit(ctx_id, workspace_id, step=2, confidence=0.95)
        if result.initiative_id or result.trace.get("reason") != "workspace_mismatch":
            return result.as_tuple()

    # Step 3 — agent affinity (kind-policy-aware)
    if owner_agent:
        result = _resolve_affinity(owner_agent, workspace_id, now)
        if result.initiative_id:
            return result.as_tuple()
        affinity_trace = result.trace
    else:
        affinity_trace = {"step": 3, "reason": "no_owner_agent_provided"}

    # Step 4 — heuristics (PR3, not yet implemented)
    # Stub: returns None + reason. PR3 will replace this with a real
    # topic-overlap scorer.
    heuristic_trace = {"step": 4, "reason": "heuristics_not_yet_implemented"}

    # Step 5 — fall through to caller (Phase 1 diagnostic or Phase 2 reject)
    return None, {
        "step": 5,
        "reason": "no_inference_match",
        "step_3_trace": affinity_trace,
        "step_4_trace": heuristic_trace,
    }


# --------------------------------------------------------------------- #
# Step 1 / 2 — explicit + propagated initiative_id                      #
# --------------------------------------------------------------------- #


def _resolve_explicit(
    initiative_id: UUID | str,
    workspace_id: UUID | str,
    *,
    step: int,
    confidence: float,
) -> InferenceResult:
    """Resolve an explicit/propagated initiative_id against workspace + kind."""
    from core.models_document_registry import Initiative

    init = Initiative.objects.filter(id=initiative_id).first()
    if not init:
        return InferenceResult(
            None,
            {"step": step, "confidence": confidence, "reason": "initiative_not_found",
             "tried_initiative_id": str(initiative_id)},
        )

    # Cross-workspace is a hard stop. Caller decides whether to proceed.
    if init.target_workspace_id and str(init.target_workspace_id) != str(workspace_id):
        return InferenceResult(
            None,
            {"step": step, "confidence": confidence, "reason": "workspace_mismatch",
             "tried_initiative_id": str(initiative_id),
             "initiative_workspace": str(init.target_workspace_id),
             "payload_workspace": str(workspace_id)},
        )

    # Explicit attaches DO allow kind=recurring_artifact / spec_backlog
    # (the caller opted in by setting initiative_id). Kind block only
    # applies to Steps 3-4 inference.

    return InferenceResult(
        str(init.id),
        {"step": step, "confidence": confidence, "reason": "explicit_match",
         "initiative_id": str(init.id), "kind": init.kind},
    )


# --------------------------------------------------------------------- #
# Step 3 — agent affinity                                               #
# --------------------------------------------------------------------- #


def _resolve_affinity(
    owner_agent: str,
    workspace_id: UUID | str,
    now: datetime,
) -> InferenceResult:
    """Query AgentInitiativeAffinity + apply kind-policy gates.

    Per Rigby's §6.2 design (locked in pa-ea12236c83eb4826):
    - Authoritative sources only: static_seed + manual_pin
      (learned_suggestion surfaces in reports but doesn't auto-attach)
    - Kind-aware strictness:
        project       → 1 candidate, recency ≤ 7d, conf ≥ 0.90
        investigation → 1 candidate, recency ≤ 30d, conf ≥ 0.70
        recurring_artifact / spec_backlog → never auto-attach
    - Multiple candidates → fall through (don't pick arbitrarily)
    """
    from core.models_inference import AgentInitiativeAffinity

    rows = (
        AgentInitiativeAffinity.objects
        .filter(
            workspace_id=workspace_id,
            agent_name=owner_agent,
            source__in=INFERENCE_AUTHORITATIVE_SOURCES,
        )
        .filter(
            # expires_at is NULL OR > now
            models_q_unexpired(now)
        )
        .select_related("initiative")
    )
    rows = list(rows)

    if not rows:
        return InferenceResult(
            None,
            {"step": 3, "reason": "no_affinity_rows",
             "owner_agent": owner_agent, "workspace_id": str(workspace_id)},
        )

    # Filter to valid candidates: kind allowed + recency OK + confidence floor
    valid_candidates = []
    rejection_reasons: list[dict[str, Any]] = []

    for row in rows:
        init = row.initiative
        kind = init.kind

        if kind in KINDS_BLOCKED_FROM_INFERENCE:
            rejection_reasons.append({
                "affinity_id": str(row.id), "kind": kind,
                "reason": "kind_blocked_from_inference",
            })
            continue

        # Cross-workspace defense (target_workspace can be NULL — accept those)
        if init.target_workspace_id and str(init.target_workspace_id) != str(workspace_id):
            rejection_reasons.append({
                "affinity_id": str(row.id), "kind": kind,
                "reason": "initiative_workspace_mismatch",
            })
            continue

        if kind == "project":
            recency_floor = now - timedelta(days=PROJECT_RECENCY_DAYS)
            conf_floor = PROJECT_CONFIDENCE_FLOOR
        elif kind == "investigation":
            recency_floor = now - timedelta(days=INVESTIGATION_RECENCY_DAYS)
            conf_floor = INVESTIGATION_CONFIDENCE_FLOOR
        else:
            # Unknown kind — fail closed
            rejection_reasons.append({
                "affinity_id": str(row.id), "kind": kind,
                "reason": "unknown_kind_no_policy",
            })
            continue

        if init.updated_at < recency_floor:
            rejection_reasons.append({
                "affinity_id": str(row.id), "kind": kind,
                "reason": "recency_stale",
                "initiative_updated_at": init.updated_at.isoformat(),
                "floor": recency_floor.isoformat(),
            })
            continue

        if row.confidence < conf_floor:
            rejection_reasons.append({
                "affinity_id": str(row.id), "kind": kind,
                "reason": "confidence_below_floor",
                "confidence": row.confidence, "floor": conf_floor,
            })
            continue

        valid_candidates.append(row)

    if len(valid_candidates) != 1:
        return InferenceResult(
            None,
            {"step": 3, "reason": "wrong_candidate_count",
             "owner_agent": owner_agent,
             "valid_count": len(valid_candidates),
             "total_rows": len(rows),
             "rejections": rejection_reasons[:5]},
        )

    winner = valid_candidates[0]
    return InferenceResult(
        str(winner.initiative_id),
        {"step": 3, "reason": "affinity_match",
         "owner_agent": owner_agent,
         "affinity_id": str(winner.id),
         "initiative_id": str(winner.initiative_id),
         "kind": winner.initiative.kind,
         "confidence": winner.confidence,
         "source": winner.source},
    )


def models_q_unexpired(now: datetime):
    """Q-expression: expires_at IS NULL OR expires_at > now."""
    from django.db.models import Q
    return Q(expires_at__isnull=True) | Q(expires_at__gt=now)
