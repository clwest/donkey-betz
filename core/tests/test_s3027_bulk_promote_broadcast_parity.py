"""Session 3027 (S3023 Fold B re-scope): bulk_promote_decisions now emits
the S3026-shaped canonical-promotion broadcast per row, via the same
`emit_canonical_promotion_broadcast` helper the single endpoint calls.
(S3028 moved the helper to `core/services/canonical_decision_broadcast`
+ renamed to drop the private prefix now that it's a public services API.)

S3026 Fold C fix removed the broken KT.create side-effect from single
promote and fixed the Redis broadcast. Bulk promote (`Session 942`) was
never wired to that broadcast — this suite pins the parity contract:

* Bulk promote invokes the helper once per successfully-promoted row.
* Each broadcast uses the same event shape as single promote
  (`schema_version: 1`, dual-key `participants` + `agents_involved`,
  rationale/stance accessor cascade).
* Broadcast failure (Redis down) is NOT fatal to promotion — status
  still flips to canonical + response reports
  `broadcasts_failed` count.
* Single + bulk endpoints publish structurally-identical events for
  the same decision (regression guard against future drift).
"""
from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_unified_system import AgentDecisionSummary


User = get_user_model()

BULK_URL = "/api/boardroom/decisions/bulk-promote/"


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


class BulkPromoteBroadcastTests(TestCase):
    """POST /api/boardroom/decisions/bulk-promote/ — broadcast parity."""

    def setUp(self) -> None:
        self.user = _make_staff("bulk_promote_broadcast_s3027")
        self.client = Client()
        self.client.force_login(self.user)

    def _post(self, payload: dict):
        return self.client.post(BULK_URL, data=json.dumps(payload), content_type="application/json")

    def test_bulk_promote_emits_broadcast_per_row(self) -> None:
        """3 draft decisions promoted → helper called 3 times → 3 publish()
        calls to `agent_learning` channel. Each event carries the row's
        decision_id + topic + the S3026 event shape."""
        drafts = [_make_draft(topic=f"row-{i}", rationale=f"reason-{i}") for i in range(3)]

        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            resp = self._post({"decision_ids": [str(d.id) for d in drafts]})

        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["count"], 3)
        self.assertEqual(body["broadcasts_succeeded"], 3)
        self.assertEqual(body["broadcasts_failed"], 0)

        # 3 publish() calls, one per row.
        self.assertEqual(mock_pub.call_count, 3)
        published_channels = {call.args[0] for call in mock_pub.call_args_list}
        self.assertEqual(published_channels, {"agent_learning"})

        # Each event carries the S3026 shape.
        seen_decision_ids = set()
        for call in mock_pub.call_args_list:
            _channel, payload = call.args
            outer = json.loads(payload)
            self.assertEqual(outer["type"], "canonical_policy_created")
            event = outer["data"]
            # S3036: bumped 1→2 to signal presence of `actor` field.
            self.assertEqual(event["schema_version"], 2)
            self.assertEqual(event["type"], "canonical_decision_promoted")
            self.assertIn("participants", event)
            self.assertIn("agents_involved", event)
            self.assertEqual(event["agents_involved"], event["participants"])
            seen_decision_ids.add(event["decision_id"])
        self.assertEqual(seen_decision_ids, {str(d.id) for d in drafts})

    def test_broadcast_failure_isolated_from_promotion_success(self) -> None:
        """Redis publish raising RuntimeError does NOT fail promotion.
        All rows still flip to canonical status; response reports
        `broadcasts_failed=N` so ops can alert."""
        drafts = [_make_draft(topic=f"redis-down-{i}") for i in range(3)]

        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.return_value.publish.side_effect = RuntimeError("redis unreachable")
            mock_redis_cls.from_url.return_value.incr.return_value = None
            resp = self._post({"decision_ids": [str(d.id) for d in drafts]})

        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["count"], 3)
        self.assertEqual(body["broadcasts_succeeded"], 0)
        self.assertEqual(body["broadcasts_failed"], 3)

        # All 3 decisions actually promoted despite broadcast failure.
        for d in drafts:
            d.refresh_from_db()
            self.assertEqual(d.status, "canonical")
            self.assertIsNotNone(d.promoted_at)

    def test_bulk_and_single_emit_structurally_identical_events(self) -> None:
        """Regression guard against drift resurfacing: single-promote and
        bulk-promote MUST publish events with identical shape for the
        same decision inputs. Compares payloads by dropping fields we
        expect to differ (timestamp) + by taking one decision through
        each endpoint."""

        def _post_single(decision_id):
            return self.client.post(f"/api/boardroom/decisions/{decision_id}/promote/")

        d1 = _make_draft(topic="parity-single", rationale="same-reason")
        d2 = _make_draft(topic="parity-bulk", rationale="same-reason")

        # Capture the single-promote event.
        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            _post_single(str(d1.id))
        single_payload = json.loads(mock_pub.call_args.args[1])
        single_event = single_payload["data"]

        # Capture the bulk-promote event.
        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            self._post({"decision_ids": [str(d2.id)]})
        bulk_payload = json.loads(mock_pub.call_args.args[1])
        bulk_event = bulk_payload["data"]

        # Envelope structure identical.
        self.assertEqual(single_payload["type"], bulk_payload["type"])
        self.assertEqual(set(single_payload.keys()), set(bulk_payload.keys()))

        # Event key set identical (drift-guard).
        self.assertEqual(set(single_event.keys()), set(bulk_event.keys()))

        # Every field EXCEPT timestamp + decision_id + topic + actor (which
        # vary by design across rows/callers — actor added S3036, differs
        # by design between single='human' and bulk='human-bulk') matches
        # between single and bulk.
        stable_fields = set(single_event.keys()) - {
            "timestamp", "decision_id", "topic", "actor",
        }
        for field in stable_fields:
            self.assertEqual(
                single_event[field],
                bulk_event[field],
                f"Field '{field}' drifted between single/bulk broadcast: "
                f"single={single_event[field]!r} bulk={bulk_event[field]!r}",
            )
        # S3036: verify actor DOES differentiate by design.
        self.assertEqual(single_event["actor"], "human")
        self.assertEqual(bulk_event["actor"], "human-bulk")

    def test_bulk_promote_response_includes_broadcast_counts(self) -> None:
        """Response contract: `broadcasts_succeeded` + `broadcasts_failed`
        are always present + non-negative integers, additive to the
        existing S942 contract (`success`, `count`, `message`)."""
        drafts = [_make_draft(topic=f"contract-{i}") for i in range(2)]

        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.return_value.publish.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            resp = self._post({"decision_ids": [str(d.id) for d in drafts]})

        body = resp.json()
        # Existing S942 fields preserved (additive-only contract).
        self.assertIn("success", body)
        self.assertIn("count", body)
        self.assertIn("message", body)
        # New S3027 fields.
        self.assertIn("broadcasts_succeeded", body)
        self.assertIn("broadcasts_failed", body)
        self.assertIsInstance(body["broadcasts_succeeded"], int)
        self.assertIsInstance(body["broadcasts_failed"], int)
        self.assertGreaterEqual(body["broadcasts_succeeded"], 0)
        self.assertGreaterEqual(body["broadcasts_failed"], 0)
        # Broadcasts total <= promoted count (bulk skips broadcast for
        # rows whose promote_to_canonical raised).
        self.assertLessEqual(
            body["broadcasts_succeeded"] + body["broadcasts_failed"],
            body["count"],
        )

    def test_empty_queryset_still_returns_broadcast_counts(self) -> None:
        """Zero-match case returns count=0 + broadcasts_succeeded=0 +
        broadcasts_failed=0 (contract stays additive even in edge case)."""
        # Nothing draft exists → count=0.
        resp = self._post({"decision_ids": ["00000000-0000-0000-0000-000000000000"]})
        body = resp.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["count"], 0)
        self.assertEqual(body["broadcasts_succeeded"], 0)
        self.assertEqual(body["broadcasts_failed"], 0)
