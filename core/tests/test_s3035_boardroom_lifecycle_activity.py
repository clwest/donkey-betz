"""Session 3035: Boardroom Lifecycle Activity panel — bounded ring buffer
+ UI endpoint for recent canonical promote/reject events. First user-visible
consumption of the S3028 promotion broadcast + S3034 rejection broadcast.

Contract this suite pins:

1. Both `emit_canonical_promotion_broadcast()` and
   `emit_canonical_rejection_broadcast()`, after their existing
   `r.publish(...)` + `r.incr(...)`, also `LPUSH` the same event dict into
   `canonical_decisions:recent` and `LTRIM 0 19` to cap at 20 entries.
2. LPUSH/LTRIM failure is swallowed — publish succeeded so helper still
   returns True. Ring persistence must not fail the broadcast.
3. `GET /api/boardroom/lifecycle-activity/` returns
   `{success, counters:{promoted_total, rejected_total}, events:[]}` with
   events decoded from the ring (newest-first).
4. Redis-down at read time returns success:True + empty events + 0
   counters (best-effort read matches best-effort write).
5. Staff-only gate via `_require_boardroom_staff` (matches all other
   `/api/boardroom/*` mutation and read endpoints).
6. `degraded: bool` flag in response (S3035 A2 fold — Rigby zoom-out):
   False on happy path, True when Redis read raised. UI uses this to
   distinguish "no recent activity" (feed empty on merits) from "feed
   temporarily unavailable" (Redis down).
"""
from __future__ import annotations

import json
from unittest.mock import patch

from django.test import TestCase, RequestFactory

from core.models_unified_system import AgentDecisionSummary
from core.services.canonical_decision_broadcast import (
    emit_canonical_promotion_broadcast,
    emit_canonical_rejection_broadcast,
)


def _make_draft(topic: str) -> AgentDecisionSummary:
    return AgentDecisionSummary.objects.create(
        topic=topic,
        decision_type='experiment',
        impact_area='agents',
        rationale='r',
        recommended_stance='s',
        status='draft',
        participants=['agent_a', 'agent_b'],
    )


class PromotionHelperLpushRingTest(TestCase):
    def test_promotion_helper_lpush_and_ltrim_after_publish(self):
        row = _make_draft('promo-lpush')
        # Force is_canonical semantics minimally — the helper reads
        # `decision.participants`, `topic`, `decision_type` only.

        with patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.publish.return_value = None
            mock_client.incr.return_value = None
            mock_client.lpush.return_value = None
            mock_client.ltrim.return_value = None

            result = emit_canonical_promotion_broadcast(row, request_id='rq-1')

        self.assertTrue(result)
        # LPUSH called with (key, value); value must be the same event dict
        # (JSON-serialized) as published.
        self.assertEqual(mock_client.lpush.call_count, 1)
        key, value_str = mock_client.lpush.call_args.args
        self.assertEqual(key, 'canonical_decisions:recent')
        event = json.loads(value_str)
        self.assertEqual(event['type'], 'canonical_decision_promoted')
        # S3036: bumped 1→2 to signal presence of `actor` field.
        self.assertEqual(event['schema_version'], 2)
        self.assertEqual(event['decision_id'], str(row.id))
        self.assertEqual(event['topic'], row.topic)

        # LTRIM caps the ring at 20 entries.
        self.assertEqual(mock_client.ltrim.call_count, 1)
        ltrim_args = mock_client.ltrim.call_args.args
        self.assertEqual(ltrim_args, ('canonical_decisions:recent', 0, 19))


class RejectionHelperLpushRingTest(TestCase):
    def test_rejection_helper_lpush_and_ltrim_after_publish(self):
        row = _make_draft('reject-lpush')
        row.reject(rejected_by='human')

        with patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.publish.return_value = None
            mock_client.incr.return_value = None
            mock_client.lpush.return_value = None
            mock_client.ltrim.return_value = None

            result = emit_canonical_rejection_broadcast(row, request_id='rq-2')

        self.assertTrue(result)
        self.assertEqual(mock_client.lpush.call_count, 1)
        key, value_str = mock_client.lpush.call_args.args
        self.assertEqual(key, 'canonical_decisions:recent')
        event = json.loads(value_str)
        self.assertEqual(event['type'], 'canonical_decision_rejected')
        # S3036: bumped 1→2 to signal presence of `actor` field.
        self.assertEqual(event['schema_version'], 2)
        self.assertEqual(event['decision_id'], str(row.id))

        self.assertEqual(mock_client.ltrim.call_count, 1)
        ltrim_args = mock_client.ltrim.call_args.args
        self.assertEqual(ltrim_args, ('canonical_decisions:recent', 0, 19))


class HelperLpushFailureIsSwallowedTest(TestCase):
    """LPUSH failure must not fail the broadcast: publish succeeded so
    the helper returns True. Ring persistence is a best-effort side-effect,
    same contract as the outer publish."""

    def test_lpush_raise_still_returns_true_and_does_not_propagate(self):
        row = _make_draft('lpush-fail')

        with patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.publish.return_value = None
            mock_client.incr.return_value = None
            mock_client.lpush.side_effect = RuntimeError('ring push exploded')

            result = emit_canonical_promotion_broadcast(row)

        self.assertTrue(
            result,
            'ring push failure must be swallowed — publish succeeded',
        )
        # LTRIM should NOT be called if LPUSH raised (it's inside the same
        # try block).
        self.assertEqual(mock_client.ltrim.call_count, 0)


class LifecycleActivityEndpointShapeTest(TestCase):
    """`GET /api/boardroom/lifecycle-activity/` returns the expected shape."""

    def _sample_event(self, decision_id: str, event_type: str) -> str:
        return json.dumps({
            'schema_version': 1,
            'type': event_type,
            'timestamp': '2026-07-28T12:00:00+00:00',
            'decision_id': decision_id,
            'topic': f'sample {event_type}',
            'decision_type': 'experiment',
            'summary': 'stub',
            'participants': ['a', 'b'],
            'agents_involved': ['a', 'b'],
        })

    def test_endpoint_returns_counters_and_events(self):
        from core.views_agent_learning import get_lifecycle_activity

        rf = RequestFactory()
        req = rf.get('/api/boardroom/lifecycle-activity/')

        # Ring holds 2 events; counters mid-range.
        e1 = self._sample_event('d1', 'canonical_decision_promoted')
        e2 = self._sample_event('d2', 'canonical_decision_rejected')

        with patch(
            'core.views_agent_learning._require_boardroom_staff',
            return_value=None,
        ), patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            # r.get returns bytes for existing counters, None for missing.
            mock_client.get.side_effect = lambda key: {
                'canonical_decisions:total': b'42',
                'canonical_decisions:rejected_total': b'7',
            }.get(key)
            mock_client.lrange.return_value = [e1.encode(), e2.encode()]

            response = get_lifecycle_activity(req)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertTrue(body['success'])
        self.assertFalse(body['degraded'], 'happy path must report degraded:false')
        self.assertEqual(body['counters']['promoted_total'], 42)
        self.assertEqual(body['counters']['rejected_total'], 7)
        self.assertEqual(len(body['events']), 2)
        self.assertEqual(body['events'][0]['decision_id'], 'd1')
        self.assertEqual(body['events'][0]['type'], 'canonical_decision_promoted')
        self.assertEqual(body['events'][1]['decision_id'], 'd2')
        self.assertEqual(body['events'][1]['type'], 'canonical_decision_rejected')

        # LRANGE bounded at 0..19 (last 20).
        lrange_args = mock_client.lrange.call_args.args
        self.assertEqual(lrange_args, ('canonical_decisions:recent', 0, 19))


class LifecycleActivityEndpointRedisDownTest(TestCase):
    """Redis-down at read time must not 500 — return empty events + 0
    counters + success:True. Matches best-effort write contract."""

    def test_redis_from_url_raises_returns_empty_defaults(self):
        from core.views_agent_learning import get_lifecycle_activity

        rf = RequestFactory()
        req = rf.get('/api/boardroom/lifecycle-activity/')

        with patch(
            'core.views_agent_learning._require_boardroom_staff',
            return_value=None,
        ), patch('redis.Redis') as mock_redis_cls:
            mock_redis_cls.from_url.side_effect = ConnectionError('redis down')

            response = get_lifecycle_activity(req)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertTrue(body['success'])
        self.assertTrue(
            body['degraded'],
            'Redis-down must report degraded:true so UI can distinguish '
            'from merits-empty feed',
        )
        self.assertEqual(body['counters']['promoted_total'], 0)
        self.assertEqual(body['counters']['rejected_total'], 0)
        self.assertEqual(body['events'], [])

    def test_lrange_returns_none_treated_as_empty(self):
        """`r.lrange` returning None (rare, but possible with certain redis
        clients on empty key) must be treated as empty list."""
        from core.views_agent_learning import get_lifecycle_activity

        rf = RequestFactory()
        req = rf.get('/api/boardroom/lifecycle-activity/')

        with patch(
            'core.views_agent_learning._require_boardroom_staff',
            return_value=None,
        ), patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.get.return_value = None
            mock_client.lrange.return_value = None  # rare edge

            response = get_lifecycle_activity(req)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(body['events'], [])
        self.assertEqual(body['counters']['promoted_total'], 0)
        self.assertEqual(body['counters']['rejected_total'], 0)

    def test_malformed_ring_entry_is_skipped_not_500(self):
        """A single bad JSON blob in the ring must not 500 the endpoint —
        skip it, keep the rest."""
        from core.views_agent_learning import get_lifecycle_activity

        rf = RequestFactory()
        req = rf.get('/api/boardroom/lifecycle-activity/')

        good_event = json.dumps({
            'type': 'canonical_decision_promoted',
            'decision_id': 'good',
        }).encode()
        bad_event = b'not-json{'

        with patch(
            'core.views_agent_learning._require_boardroom_staff',
            return_value=None,
        ), patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.get.return_value = b'1'
            mock_client.lrange.return_value = [bad_event, good_event]

            response = get_lifecycle_activity(req)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(len(body['events']), 1)
        self.assertEqual(body['events'][0]['decision_id'], 'good')


class LifecycleActivityAuthGateTest(TestCase):
    """Endpoint is staff-only (matches promote/reject/governance-stats)."""

    def test_unauthenticated_returns_401(self):
        from core.views_agent_learning import get_lifecycle_activity

        rf = RequestFactory()
        req = rf.get('/api/boardroom/lifecycle-activity/')
        # Real _require_boardroom_staff — anonymous request → 401.
        # Simulate anonymous by leaving request.user as AnonymousUser default.
        from django.contrib.auth.models import AnonymousUser
        req.user = AnonymousUser()

        response = get_lifecycle_activity(req)
        self.assertEqual(response.status_code, 401)

    def test_non_staff_authenticated_returns_403(self):
        from core.views_agent_learning import get_lifecycle_activity
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(
            username='non-staff', password='x', is_staff=False,
        )

        rf = RequestFactory()
        req = rf.get('/api/boardroom/lifecycle-activity/')
        req.user = user

        response = get_lifecycle_activity(req)
        self.assertEqual(response.status_code, 403)
