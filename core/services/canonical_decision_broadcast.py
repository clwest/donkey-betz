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

S3036 addition: both helpers accept an optional `actor` field (default
`'unknown'`) that identifies the source-of-transition for the event.
The value is passed through into the event dict at the top level so
UI consumers (BoardroomTab lifecycle panel) can render "who did this?"
without a follow-up query. `schema_version` is bumped `1 → 2` to mark
the presence of `actor`. Subscribers coded against v1 should tolerate
missing `actor` (default to `'unknown'`) and accept `schema_version in
{1, 2}` — no strict `== 1` gating exists in-repo today (Rigby T1 SIGN
tool-verified) and old v1 events already in the ring at deploy time
drain within ~10-20 lifecycle events. Actor value taxonomy is
authoritative in `CANONICAL_LIFECYCLE_ACTORS` below; callers should
import the constant rather than pass string literals so typos become
lint/test failures instead of "unknown" pill regressions in the UI.

Callers that deliberately do NOT emit (e.g., `backfill_canonical_drift`
management command backfilling historical drift) are OUT of the actor
taxonomy — there is no `'backfill'` actor. Silence is the correct
signal that a code path is out-of-scope for the lifecycle broadcast.
"""
from __future__ import annotations

import json
import logging
import os

from django.utils import timezone

logger = logging.getLogger(__name__)


# S3036: authoritative actor taxonomy for the canonical-lifecycle
# broadcast. Callers import from here rather than pass string literals
# so a typo at a call site surfaces at import time (NameError) rather
# than as a mystery "unknown" pill in the BoardroomTab UI. Adding a
# new actor = adding a constant here + updating the frontend palette
# in `frontend/src/pages/workspace/tabs/BoardroomTab.tsx`.
#
# Test coverage (`core/tests/test_s3036_actor_threading.py`):
#   - `ActorTaxonomyTest` (3): pins the frozenset shape + membership.
#   - `PromotionHelperActorContractTest` + `RejectionHelperActorContractTest`
#     (4): explicit + default actor in emitted event.
#   - `CallSiteActorParameterizedTest` (3): direct-invocation tests for
#     the 3 service-layer call sites (`ai_decision_promoter`,
#     `decision_promotion_rules`, `tasks_ops`). The 5 `views_agent_learning`
#     sites + 2 `td_handlers_agents` sites are covered indirectly by the
#     existing S3026/S3027/S3034/S3035 view/handler test bundles which
#     assert the emitted event shape (including `actor` post-S3036).
#   - `LifecycleActivityEndpointActorPassthroughTest` (2): v1/v2
#     round-trip tolerance at the polling endpoint.
ACTOR_HUMAN = 'human'                # single boardroom endpoint click (views_agent_learning 2270 + 2328)
ACTOR_HUMAN_BULK = 'human-bulk'      # bulk boardroom endpoints (views_agent_learning 2435 + 2530)
ACTOR_HUMAN_GATE = 'human-gate'      # gate-decline path (views_agent_learning 3922 update_gate_status action=='decline')
ACTOR_PA_TOOL = 'pa-tool'            # Rigby PA tool handler (td_handlers_agents 6057 + 6106)
ACTOR_AI_PROMOTER = 'ai-promoter'    # AIDecisionPromoterService (ai_decision_promoter 205)
ACTOR_OPS_TASK = 'ops-task'          # Celery auto-approve boardroom items (tasks_ops 309)
ACTOR_RULES_SERVICE = 'rules-service'  # S589 automated rules service (decision_promotion_rules 202)

CANONICAL_LIFECYCLE_ACTORS = frozenset({
    ACTOR_HUMAN,
    ACTOR_HUMAN_BULK,
    ACTOR_HUMAN_GATE,
    ACTOR_PA_TOOL,
    ACTOR_AI_PROMOTER,
    ACTOR_OPS_TASK,
    ACTOR_RULES_SERVICE,
})

ACTOR_UNKNOWN = 'unknown'  # helper default; not in taxonomy but rendered as neutral pill by UI


def emit_canonical_promotion_broadcast(
    decision, *, request_id: str | None = None, actor: str = ACTOR_UNKNOWN,
) -> bool:
    """Publish a `canonical_policy_created` event to the `agent_learning`
    Redis channel for a freshly-promoted `AgentDecisionSummary`.

    Returns True iff `r.publish(...)` completed without raising. Any
    exception is logged + swallowed → returns False. This is transport,
    not domain logic — Redis-down must not fail promotion.

    `actor` (S3036) identifies the source-of-transition. Callers must
    import and pass one of `ACTOR_HUMAN`, `ACTOR_HUMAN_BULK`,
    `ACTOR_HUMAN_GATE`, `ACTOR_PA_TOOL`, `ACTOR_AI_PROMOTER`,
    `ACTOR_OPS_TASK`, `ACTOR_RULES_SERVICE`. Default `'unknown'`
    preserves backfill drift-suppression semantics (missing = neutral
    pill in UI, no crash) but every production call site is expected
    to pass an explicit value. See the module docstring "Test coverage"
    section above for how the 10 call sites are enforced (3 direct
    parameterized tests + 7 via the existing S3026/S3027/S3034/S3035
    view/handler regression bundles).
    """
    import redis

    try:
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
        # S3026 A2 REVISE: dual-emit participants (canonical going forward)
        # + agents_involved (S657-source back-compat alias) for one
        # compatibility window. `schema_version` lets subscribers gate
        # on shape as it evolves — bumped 1→2 at S3036 to signal `actor`.
        participants_list = decision.participants or []
        event = {
            'schema_version': 2,
            'type': 'canonical_decision_promoted',
            'actor': actor,
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


def emit_canonical_rejection_broadcast(
    decision, *, request_id: str | None = None, actor: str = ACTOR_UNKNOWN,
) -> bool:
    """S3034: Publish a `canonical_policy_rejected` event to the
    `agent_learning` Redis channel for a freshly-rejected
    `AgentDecisionSummary`.

    Mirror of `emit_canonical_promotion_broadcast()` for the deprecation
    side of the lifecycle. Returns True iff `r.publish(...)` completed
    without raising. Any exception is logged + swallowed → returns False.
    This is transport, not domain logic — Redis-down must not fail
    rejection.

    Payload keys mirror the promotion event so subscribers can branch on
    `data.type` without divergent shape handling. `schema_version` lets
    subscribers gate on shape as it evolves — bumped 1→2 at S3036 to
    signal presence of `actor`. See promotion helper docstring for the
    `actor` contract; same taxonomy applies here.
    """
    import redis

    try:
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
        participants_list = decision.participants or []
        event = {
            'schema_version': 2,
            'type': 'canonical_decision_rejected',
            'actor': actor,
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
