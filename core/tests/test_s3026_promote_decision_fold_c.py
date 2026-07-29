"""Session 3026 Fold C fix (S3023 forward-carry): remove structurally-broken
KnowledgeTransfer side-effect from `promote_decision` + fix + verify Redis
broadcast.

**Discovery during S3026 Fold C investigation:** S3023's Fold C description
identified `decision.summary` as the source of the masked AttributeError.
Test-driven exploration revealed a deeper problem: the S657
`KnowledgeTransfer.objects.create(...)` call in `promote_decision` was
passing kwargs (`source_agent`, `target_agent`, `title`, `content`,
`applied`) that don't exist on the only `KnowledgeTransfer` model
(`core.models_unified_system:785`, whose real fields are
`source_knowledge`, `transfer_summary`, `was_applied`, `was_useful`, etc.).
Every promotion since S657 hit `TypeError: KnowledgeTransfer() got
unexpected keyword arguments` inside the broad `except Exception as
learn_err` block — the `decision.summary` AttributeError never even fired
because control never reached that line. Both bugs were silently masked
for years.

**Option C fix (per Rigby A1 approval):** remove the broken KT.create
entirely; keep + fix the Redis broadcast (its accessor also referenced
`decision.summary` — fixed to `rationale or recommended_stance`); return
`learning_created: False` honestly + a `learning_reason` diagnostic.

This suite pins the post-fix contract:
* Endpoint still returns 200 with `success: true` and honest
  `learning_created: false` + `learning_reason: 'knowledge_transfer_model_mismatch_deferred'`.
* No `KnowledgeTransfer` row is created (the endpoint no longer attempts
  to write one).
* Redis broadcast is invoked with the correct event payload — no
  AttributeError on `decision.summary` — using the rationale/stance
  accessor cascade.
"""
from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models import KnowledgeTransfer
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


class PromoteDecisionFoldCTests(TestCase):
    """POST /api/boardroom/decisions/<uuid>/promote/ — single-promote path."""

    def setUp(self) -> None:
        self.user = _make_staff("promote_decision_s3026")
        self.client = Client()
        self.client.force_login(self.user)

    def _post(self, decision_id: str):
        return self.client.post(f"/api/boardroom/decisions/{decision_id}/promote/")

    def test_returns_honest_learning_created_false_with_diagnostic(self) -> None:
        """Post-Option-C: `learning_created` is deterministically False
        and `learning_reason` names why. The prior contract silently
        returned False because the KT.create raised TypeError; the new
        contract makes the deferral explicit."""
        d = _make_draft(topic="Fold C fix")

        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.return_value.publish.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            response = self._post(str(d.id))

        self.assertEqual(response.status_code, 200, response.content)
        body = json.loads(response.content)
        self.assertTrue(body["success"], body)
        self.assertFalse(body["learning_created"])
        self.assertEqual(
            body["learning_reason"], "knowledge_transfer_model_mismatch_deferred"
        )

    def test_does_not_create_knowledge_transfer_row(self) -> None:
        """The broken KT.create call is removed. No row is written.
        Regression guard: if a future refactor re-introduces the call
        against the current KT schema, this test will fail with
        TypeError (or, if the schema-mismatched call is somehow made
        to succeed, this row-count assertion catches the write)."""
        d = _make_draft(topic="no-KT-write")
        before = KnowledgeTransfer.objects.count()

        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.return_value.publish.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            response = self._post(str(d.id))

        self.assertEqual(response.status_code, 200)
        after = KnowledgeTransfer.objects.count()
        self.assertEqual(
            after, before,
            f"KT row count should not change; before={before} after={after}",
        )

    def test_redis_broadcast_uses_rationale_stance_accessor(self) -> None:
        """The Redis event payload's `summary` field was previously
        computed via `decision.summary` (AttributeError). Post-fix it
        uses `decision.rationale or decision.recommended_stance` — same
        accessor pattern as views_platform_command.py:814."""
        d = _make_draft(
            topic="broadcast-check",
            rationale="Because we said so",
            recommended_stance="Ship it",
        )

        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            response = self._post(str(d.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mock_pub.call_count, 1)
        channel, payload = mock_pub.call_args.args
        self.assertEqual(channel, "agent_learning")
        outer = json.loads(payload)
        self.assertEqual(outer["type"], "canonical_policy_created")
        event = outer["data"]
        self.assertEqual(event["type"], "canonical_decision_promoted")
        self.assertEqual(event["topic"], "broadcast-check")
        # Rationale wins the accessor cascade — verifies no AttributeError
        # on the removed summary field AND that the fallback isn't stance.
        self.assertEqual(event["summary"], "Because we said so")
        # S3026 A2 REVISE: schema_version + agents_involved back-compat.
        # S3036: bumped 1→2 to signal presence of `actor` field.
        self.assertEqual(event["schema_version"], 2)
        # `participants` is the canonical key going forward; `agents_involved`
        # is the S657-source back-compat alias. Both emit the same list for
        # one compatibility window.
        self.assertIn("participants", event)
        self.assertIn("agents_involved", event)
        self.assertEqual(event["agents_involved"], event["participants"])

    def test_redis_broadcast_falls_back_to_stance_when_no_rationale(self) -> None:
        """Accessor cascade — rationale > recommended_stance > empty string."""
        d = _make_draft(
            topic="stance-fallback", rationale="", recommended_stance="Ship it"
        )

        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            self._post(str(d.id))

        payload = json.loads(mock_pub.call_args.args[1])
        self.assertEqual(payload["data"]["summary"], "Ship it")

    def test_endpoint_survives_redis_broadcast_failure(self) -> None:
        """Redis unavailability is not fatal to promotion. The endpoint
        must return 200 + set canonical status even if the broadcast
        publish raises. Preserves the S657 defensive posture."""
        d = _make_draft(topic="redis-down")

        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.side_effect = RuntimeError("redis unreachable")
            response = self._post(str(d.id))

        self.assertEqual(response.status_code, 200, response.content)
        body = json.loads(response.content)
        self.assertTrue(body["success"])
        d.refresh_from_db()
        self.assertEqual(d.status, "canonical")
