"""Session 3029 (S3028 Fold A codification): mutation-style convergence.

Before S3029, three of five canonical-promotion paths called
`AgentDecisionSummary.promote_to_canonical(promoted_by=...)` (single view,
bulk view, PA tool handler) but two duplicated the field mutation inline:
- `AIDecisionPromoterService.promote_decision` (with `transaction.atomic()`)
- `DecisionPromotionRules.promote_decision` (no transaction wrapper)

S3029 converges both services on the model method. Per-service transaction
semantics are intentionally preserved (AI wraps; Rules doesn't; a future
harmonization would need explicit evidence-backed deliberation).

This suite pins the convergence via **spy tests** (Rigby A1 REVISE #2:
patch with `wraps=` so the original method still runs — the existing
`refresh_from_db` assertions stay meaningful, but the spy also proves the
model method was called). Any future refactor that re-duplicates the
mutation inline would fail these tests.
"""
from __future__ import annotations

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


class AIPromoterCallsModelMethodTest(TestCase):
    """`AIDecisionPromoterService.promote_decision` must delegate to
    `AgentDecisionSummary.promote_to_canonical` — not duplicate the
    mutation inline."""

    def test_ai_promoter_delegates_to_model_method(self) -> None:
        from core.services.ai_decision_promoter import AIDecisionPromoterService
        d = _make_draft(topic="ai-delegates")

        # Spy pattern (Rigby A1 REVISE #2): side_effect delegates to the
        # real bound method so the mutation + save actually run, but the
        # mock records the call for assertion. If a future refactor
        # re-inlines the field mutation, the spy's call_count stays 0 and
        # the assertion fails. `autospec=True` + explicit `side_effect`
        # (rather than `wraps=`) avoids the unbound-method binding trap
        # where `wraps=Class.method` receives `self` twice.
        original = AgentDecisionSummary.promote_to_canonical
        with (
            patch("redis.Redis") as mock_redis_cls,
            patch.object(
                AgentDecisionSummary, "promote_to_canonical",
                autospec=True,
                side_effect=lambda self, promoted_by='human': original(self, promoted_by=promoted_by),
            ) as spy,
        ):
            mock_redis_cls.from_url.return_value.publish.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            ok = AIDecisionPromoterService().promote_decision(d, promoter="AI-Test-S3029")

        self.assertTrue(ok)
        # Mutation actually ran (spy preserved behavior).
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")
        self.assertEqual(d.promoted_by, "AI-Test-S3029")
        # Model method was invoked exactly once with the promoter kwarg.
        self.assertEqual(spy.call_count, 1)
        _, args, kwargs = spy.mock_calls[0]
        # autospec=True → first positional is the instance (self); kwargs
        # carries the promoter under the model method's `promoted_by` param.
        self.assertEqual(kwargs.get("promoted_by"), "AI-Test-S3029")


class RulesPromoterCallsModelMethodTest(TestCase):
    """`DecisionPromotionRules.promote_decision` must delegate to
    `AgentDecisionSummary.promote_to_canonical`."""

    def test_rules_promoter_delegates_to_model_method(self) -> None:
        from core.services.decision_promotion_rules import DecisionPromotionRules
        d = _make_draft(topic="rules-delegates")

        original = AgentDecisionSummary.promote_to_canonical
        with (
            patch("redis.Redis") as mock_redis_cls,
            patch.object(
                AgentDecisionSummary, "promote_to_canonical",
                autospec=True,
                side_effect=lambda self, promoted_by='human': original(self, promoted_by=promoted_by),
            ) as spy,
        ):
            mock_redis_cls.from_url.return_value.publish.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            ok = DecisionPromotionRules().promote_decision(d, promoted_by="rules-test-s3029")

        self.assertTrue(ok)
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")
        self.assertEqual(d.promoted_by, "rules-test-s3029")
        self.assertEqual(spy.call_count, 1)
        _, args, kwargs = spy.mock_calls[0]
        self.assertEqual(kwargs.get("promoted_by"), "rules-test-s3029")
