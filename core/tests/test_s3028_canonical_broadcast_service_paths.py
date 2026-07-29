"""Session 3028 (S3027 helper de-layered): the S3027
`emit_canonical_promotion_broadcast` helper moved to
`core/services/canonical_decision_broadcast.py` so all 5 promotion paths
can call it without reverse-layering.

The two view-layer paths (`promote_decision` single + `bulk_promote_decisions`)
are covered by `test_s3026_promote_decision_fold_c.py` + `test_s3027_bulk_promote_broadcast_parity.py`.

This suite adds one focused test per newly-wired service-layer path
(Rigby A1 REVISE #4 — combined test too easy to accidentally stop
covering a specific path later):

1. **PA tool handler** (`AgentHandlersMixin._handle_boardroom` action
   `promote_decision` in `core/services/td_handlers_agents.py`).
2. **AI-AutoPromoter service**
   (`AIDecisionPromoterService.promote_decision` in
   `core/services/ai_decision_promoter.py`).
3. **Session 589 auto-promotion rules service**
   (`DecisionPromotionRules.promote_decision` in
   `core/services/decision_promotion_rules.py`).

Each test asserts:
* `redis.Redis.from_url(...).publish(...)` was invoked exactly once
  with the `agent_learning` channel.
* Broadcast failure does NOT roll back the promotion — status still
  flips to canonical + service call returns True.

Deferred (Rigby A1): mutation-style refactor (all 3 services calling
`decision.promote_to_canonical(...)` model method instead of duplicating
field mutation) is separate cleanup axis — different transaction
semantics per service.
"""
from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_unified_system import AgentDecisionSummary


User = get_user_model()


def _make_staff(username: str) -> "User":
    user = User.objects.create_user(
        username=username, email=f"{username}@example.com", password="test-pw"
    )
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    return user


def _make_draft(
    *,
    topic: str = "Draft",
    rationale: str = "A rationale",
    recommended_stance: str = "A stance",
    decision_type: str = "product",
    impact_area: str = "agents",
    status: str = "draft",
) -> AgentDecisionSummary:
    return AgentDecisionSummary.objects.create(
        conversation=None,
        hive_session=None,
        topic=topic,
        decision_type=decision_type,
        impact_area=impact_area,
        rationale=rationale,
        recommended_stance=recommended_stance,
        status=status,
    )


def _assert_agent_learning_publish(mock_pub, decision_topic: str) -> None:
    """Shared helper: assert a single publish() call to `agent_learning`
    carrying the S3026 event shape for the given decision topic."""
    assert mock_pub.call_count == 1, f"expected 1 publish, got {mock_pub.call_count}"
    channel, payload = mock_pub.call_args.args
    assert channel == "agent_learning", channel
    outer = json.loads(payload)
    assert outer["type"] == "canonical_policy_created"
    event = outer["data"]
    # S3036: bumped 1→2 to signal presence of `actor` field.
    assert event["schema_version"] == 2
    assert event["type"] == "canonical_decision_promoted"
    assert event["topic"] == decision_topic
    assert "participants" in event
    assert "agents_involved" in event


class PAToolHandlerBroadcastTest(TestCase):
    """PA tool `boardroom` action `promote_decision` — silent since S940."""

    def test_pa_promote_decision_emits_canonical_broadcast(self) -> None:
        from core.services.tool_dispatcher import ToolDispatcher
        user = _make_staff("pa_promote_s3028")
        d = _make_draft(topic="pa-path-broadcast")

        dispatcher = ToolDispatcher()
        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            result = dispatcher._handle_boardroom(
                tool_name="boardroom",
                payload={"action": "promote_decision", "id": str(d.id), "promoted_by": "PA"},
                user_id=user.id,
                trace_id="test-s3028",
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["new_status"], "canonical")
        _assert_agent_learning_publish(mock_pub, "pa-path-broadcast")

    def test_pa_promote_survives_redis_broadcast_failure(self) -> None:
        """Redis-down does NOT roll back the PA-path promotion —
        `promote_to_canonical` runs before the broadcast attempt, so
        the status flip is durable regardless of broadcast outcome."""
        from core.services.tool_dispatcher import ToolDispatcher
        user = _make_staff("pa_promote_survives_s3028")
        d = _make_draft(topic="pa-redis-down")

        dispatcher = ToolDispatcher()
        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.side_effect = RuntimeError("redis unreachable")
            result = dispatcher._handle_boardroom(
                tool_name="boardroom",
                payload={"action": "promote_decision", "id": str(d.id), "promoted_by": "PA"},
                user_id=user.id,
                trace_id="test-s3028",
            )

        self.assertTrue(result["success"])
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")


class AIDecisionPromoterServiceBroadcastTest(TestCase):
    """AI-AutoPromoter service — silent since S658."""

    def test_ai_promote_emits_canonical_broadcast(self) -> None:
        from core.services.ai_decision_promoter import AIDecisionPromoterService
        d = _make_draft(topic="ai-path-broadcast")

        service = AIDecisionPromoterService()
        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            ok = service.promote_decision(d, promoter="AI-AutoPromoter-Test")

        self.assertTrue(ok)
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")
        self.assertEqual(d.promoted_by, "AI-AutoPromoter-Test")
        _assert_agent_learning_publish(mock_pub, "ai-path-broadcast")

    def test_ai_promote_survives_redis_broadcast_failure(self) -> None:
        """Broadcast happens OUTSIDE the transaction — Redis-down must not
        roll back the field-mutation transaction."""
        from core.services.ai_decision_promoter import AIDecisionPromoterService
        d = _make_draft(topic="ai-redis-down")

        service = AIDecisionPromoterService()
        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.side_effect = RuntimeError("redis unreachable")
            ok = service.promote_decision(d, promoter="AI-AutoPromoter-Test")

        self.assertTrue(ok, "field mutation must succeed even when broadcast fails")
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")


class DecisionPromotionRulesBroadcastTest(TestCase):
    """Session 589 auto-promotion rules service — silent since S589."""

    def test_rules_promote_emits_canonical_broadcast(self) -> None:
        from core.services.decision_promotion_rules import DecisionPromotionRules
        d = _make_draft(topic="rules-path-broadcast")

        service = DecisionPromotionRules()
        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            ok = service.promote_decision(d, promoted_by="auto-promotion-rules-test")

        self.assertTrue(ok)
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")
        self.assertEqual(d.promoted_by, "auto-promotion-rules-test")
        _assert_agent_learning_publish(mock_pub, "rules-path-broadcast")

    def test_rules_promote_survives_redis_broadcast_failure(self) -> None:
        from core.services.decision_promotion_rules import DecisionPromotionRules
        d = _make_draft(topic="rules-redis-down")

        service = DecisionPromotionRules()
        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.side_effect = RuntimeError("redis unreachable")
            ok = service.promote_decision(d, promoted_by="auto-promotion-rules-test")

        self.assertTrue(ok)
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")
