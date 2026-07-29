"""Sessions 3028 (promotion) + 3034 (rejection): canonical-lifecycle Redis
broadcast — single source of truth for the `agent_learning` channel events
fired when an `AgentDecisionSummary` transitions to a terminal lifecycle
state (`canonical` or `rejected`).

**Meta-invariant (S3034):** any production code path that transitions an
`AgentDecisionSummary` to a terminal lifecycle state MUST emit the matching
lifecycle broadcast via a helper defined here. Bypassing these helpers (raw
`.status = 'canonical'` or `.status = 'rejected'` writes without an emit) is
a hardening-class drift signal and MUST be closed same-arc per the
PLAYBOOK-7.7.5 sweep discipline.

Originally introduced at S3027 inside `core/views_agent_learning.py` to
share the broadcast between `promote_decision` (single) and
`bulk_promote_decisions`. S3028 moved it here so service-layer callers
(PA tool handler, AI-AutoPromoter Celery task, Session 589 auto-promotion
rules service) can invoke it without reverse-layering (services must not
import from views). S3034 adds the deprecation-side companion helper
`emit_canonical_rejection_broadcast()` for lifecycle-broadcast symmetry.

Promotion callers (6 sites, per S3029 close):
- `core/views_agent_learning.py:promote_decision` (single, `human`)
- `core/views_agent_learning.py:bulk_promote_decisions` (bulk, `human-bulk`)
- `core/services/td_handlers_agents.py` PA tool `promote_decision` action
- `core/services/ai_decision_promoter.py:AIDecisionPromoterService.promote_decision`
- `core/services/decision_promotion_rules.py:DecisionPromotionRules.promote_decision`
- `core/tasks_ops.py:_impl_auto_approve_boardroom_items` (S3029 4th-site discovery)

Rejection callers (4 sites, per S3034 close):
- `core/views_agent_learning.py:reject_decision` (single, `human`)
- `core/views_agent_learning.py:bulk_reject_decisions` (bulk, `human-bulk`)
- `core/services/td_handlers_agents.py` PA tool `reject_decision` action
- `core/views_agent_learning.py:update_gate_status` action=='decline' (S3034 gate-decline site, caught by Rigby T1 PLAYBOOK-7.7.5 sweep — Pushback #1 `same_pr_actionable`)

Contract: best-effort, non-fatal. Any exception (Redis unavailable, JSON
encode error, etc.) is caught, logged with `decision_id` + optional
`request_id`, and returns False. Never raises to caller — Redis-down
must not fail promotion or rejection.

S3035 addition: after `r.publish(...)`, both helpers also `LPUSH` the
same event dict into the bounded ring `canonical_decisions:recent`
(capped at 20 via `LTRIM 0 19`). This is a **non-authoritative** UI
activity buffer — for audit or forensics, query `AgentDecisionSummary`
directly. The ring is populated by ALL production callers of both
helpers (not just boardroom mutation endpoints), so consumers rendering
it should frame entries as "recent lifecycle events" rather than
"boardroom actions" (AI-service auto-promotions, ops-task auto-
approvals, PA-tool actions all appear alongside human boardroom
clicks). LPUSH/LTRIM failures are swallowed same as publish — the
persistence side-effect must not fail promotion or rejection either.
"""
from __future__ import annotations

import json
import logging
import os

from django.utils import timezone

logger = logging.getLogger(__name__)


def emit_canonical_promotion_broadcast(decision, *, request_id: str | None = None) -> bool:
    """Publish a `canonical_policy_created` event to the `agent_learning`
    Redis channel for a freshly-promoted `AgentDecisionSummary`.

    Returns True iff `r.publish(...)` completed without raising. Any
    exception is logged + swallowed → returns False. This is transport,
    not domain logic — Redis-down must not fail promotion.
    """
    import redis

    try:
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
        # S3026 A2 REVISE: dual-emit participants (canonical going forward)
        # + agents_involved (S657-source back-compat alias) for one
        # compatibility window. `schema_version: 1` lets subscribers gate
        # on shape as it evolves.
        participants_list = decision.participants or []
        event = {
            'schema_version': 1,
            'type': 'canonical_decision_promoted',
            'timestamp': timezone.now().isoformat(),
            'decision_id': str(decision.id),
            'topic': decision.topic[:100],
            'decision_type': decision.decision_type,
            'summary': (decision.rationale or decision.recommended_stance or '')[:200],
            # Canonical key going forward.
            'participants': participants_list,
            # Back-compat alias for any subscriber coded against the S657
            # source. Remove once observability confirms zero readers of
            # the old key.
            'agents_involved': participants_list,
        }
        r.publish('agent_learning', json.dumps({
            'type': 'canonical_policy_created',
            'data': event,
        }))
        r.incr('canonical_decisions:total')
        # S3035: also record into bounded ring for UI activity feed.
        # Failures swallowed same as publish — non-authoritative buffer.
        try:
            r.lpush('canonical_decisions:recent', json.dumps(event))
            r.ltrim('canonical_decisions:recent', 0, 19)
        except Exception as ring_err:
            logger.warning(
                "[S3035] Redis ring push failed decision_id=%s request_id=%s: %s",
                decision.id, request_id, ring_err,
            )
        logger.info(
            "🧠 [S3028] Broadcast canonical decision decision_id=%s request_id=%s",
            decision.id, request_id,
        )
        return True
    except Exception as redis_err:
        logger.warning(
            "[S3028] Redis broadcast failed decision_id=%s request_id=%s: %s",
            decision.id, request_id, redis_err,
        )
        return False


def emit_canonical_rejection_broadcast(decision, *, request_id: str | None = None) -> bool:
    """S3034: Publish a `canonical_policy_rejected` event to the
    `agent_learning` Redis channel for a freshly-rejected
    `AgentDecisionSummary`.

    Mirror of `emit_canonical_promotion_broadcast()` for the deprecation
    side of the lifecycle. Returns True iff `r.publish(...)` completed
    without raising. Any exception is logged + swallowed → returns False.
    This is transport, not domain logic — Redis-down must not fail
    rejection.

    Payload keys mirror the promotion event so subscribers can branch on
    `data.type` without divergent shape handling. `schema_version: 1` lets
    subscribers gate on shape as it evolves.
    """
    import redis

    try:
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
        participants_list = decision.participants or []
        event = {
            'schema_version': 1,
            'type': 'canonical_decision_rejected',
            'timestamp': timezone.now().isoformat(),
            'decision_id': str(decision.id),
            'topic': decision.topic[:100],
            'decision_type': decision.decision_type,
            'summary': (decision.rationale or decision.recommended_stance or '')[:200],
            'participants': participants_list,
            'agents_involved': participants_list,
        }
        r.publish('agent_learning', json.dumps({
            'type': 'canonical_policy_rejected',
            'data': event,
        }))
        r.incr('canonical_decisions:rejected_total')
        # S3035: also record into bounded ring for UI activity feed.
        # Failures swallowed same as publish — non-authoritative buffer.
        try:
            r.lpush('canonical_decisions:recent', json.dumps(event))
            r.ltrim('canonical_decisions:recent', 0, 19)
        except Exception as ring_err:
            logger.warning(
                "[S3035] Redis ring push failed decision_id=%s request_id=%s: %s",
                decision.id, request_id, ring_err,
            )
        logger.info(
            "🚫 [S3034] Broadcast canonical decision rejection decision_id=%s request_id=%s",
            decision.id, request_id,
        )
        return True
    except Exception as redis_err:
        logger.warning(
            "[S3034] Redis rejection broadcast failed decision_id=%s request_id=%s: %s",
            decision.id, request_id, redis_err,
        )
        return False
