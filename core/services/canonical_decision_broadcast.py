"""Session 3028 (S3027 helper de-layered): canonical-promotion Redis
broadcast — single source of truth for the `agent_learning` channel
event fired when an `AgentDecisionSummary` is promoted to canonical
policy status.

Originally introduced at S3027 inside `core/views_agent_learning.py` to
share the broadcast between `promote_decision` (single) and
`bulk_promote_decisions`. S3028 moves it here so service-layer callers
(PA tool handler, AI-AutoPromoter Celery task, Session 589 auto-promotion
rules service) can invoke it without reverse-layering (services must not
import from views).

Callers today (all 5 promotion paths):
- `core/views_agent_learning.py:promote_decision` (single, `human`)
- `core/views_agent_learning.py:bulk_promote_decisions` (bulk, `human-bulk`)
- `core/services/td_handlers_agents.py` PA tool `promote_decision` action
- `core/services/ai_decision_promoter.py:AIDecisionPromoterService.promote_decision`
- `core/services/decision_promotion_rules.py:DecisionPromotionRules.promote_decision`

Contract: best-effort, non-fatal. Any exception (Redis unavailable, JSON
encode error, etc.) is caught, logged with `decision_id` + optional
`request_id`, and returns False. Never raises to caller — Redis-down
must not fail promotion.
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
