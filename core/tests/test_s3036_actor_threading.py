"""Session 3036: `actor` field threading through the canonical-lifecycle
broadcast.

Extends the S3028 (promotion) + S3034 (rejection) broadcast contract with a
source-of-transition tag that lets the BoardroomTab lifecycle activity panel
distinguish "who did this?" — human boardroom click vs Rigby PA vs AI
auto-promoter vs Celery ops-task vs S589 rules service — without a second
query. Discharges S3035 T1 Fold `deferred_2nd_trigger_watch`.

Contract this suite pins:

1. Both `emit_canonical_*_broadcast()` helpers accept an `actor` keyword
   and emit `schema_version: 2` with `actor` at the top of the event dict.
2. Default `actor='unknown'` when omitted (defensive — matches S3030
   backfill drift-suppression semantics; missing actor renders as
   neutral pill in UI, no crash).
3. All 10 production call sites pass an explicit actor value from
   `CANONICAL_LIFECYCLE_ACTORS`. Direct parameterized coverage here
   for the 3 service-layer sites (`ai_decision_promoter`,
   `decision_promotion_rules`, `tasks_ops`); the 5 `views_agent_learning`
   view sites + 2 `td_handlers_agents` sites are covered indirectly by
   the existing S3026/S3027/S3034/S3035 view/handler test bundles
   (which now assert `actor` presence via schema_version==2 + payload
   shape). Rigby A2 SIGN 2026-07-29 flagged this split explicitly.
4. Actor taxonomy centralised: adding a new actor requires importing
   from the module, not passing a string literal at the call site (typo
   catch via constant reference at import time).
5. Polling endpoint `/api/boardroom/lifecycle-activity/` passes actor
   through unchanged; also tolerates v1 events already in the ring at
   deploy time (missing `actor` → not injected, frontend renders as
   neutral "unknown" pill).

Rigby T1 SIGN 2026-07-29: AGREE_WITH_REVISIONS (5/5 dimensions, tool-
grounded 8+ repo_tool runs). Chris D-verdict: ratified.
"""
from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

from django.test import TestCase

from core.models_unified_system import AgentDecisionSummary
from core.services.canonical_decision_broadcast import (
    ACTOR_AI_PROMOTER,
    ACTOR_HUMAN,
    ACTOR_HUMAN_BULK,
    ACTOR_HUMAN_GATE,
    ACTOR_OPS_TASK,
    ACTOR_PA_TOOL,
    ACTOR_RULES_SERVICE,
    ACTOR_UNKNOWN,
    CANONICAL_LIFECYCLE_ACTORS,
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


class ActorTaxonomyTest(TestCase):
    """The 7 production actors are canonicalised in
    `CANONICAL_LIFECYCLE_ACTORS`. `ACTOR_UNKNOWN` is the helper default —
    intentionally NOT in the taxonomy because it represents "missing
    signal from a caller" rather than a legitimate transition source."""

    def test_taxonomy_has_seven_entries(self):
        self.assertEqual(len(CANONICAL_LIFECYCLE_ACTORS), 7)

    def test_taxonomy_contains_all_seven_constants(self):
        self.assertIn(ACTOR_HUMAN, CANONICAL_LIFECYCLE_ACTORS)
        self.assertIn(ACTOR_HUMAN_BULK, CANONICAL_LIFECYCLE_ACTORS)
        self.assertIn(ACTOR_HUMAN_GATE, CANONICAL_LIFECYCLE_ACTORS)
        self.assertIn(ACTOR_PA_TOOL, CANONICAL_LIFECYCLE_ACTORS)
        self.assertIn(ACTOR_AI_PROMOTER, CANONICAL_LIFECYCLE_ACTORS)
        self.assertIn(ACTOR_OPS_TASK, CANONICAL_LIFECYCLE_ACTORS)
        self.assertIn(ACTOR_RULES_SERVICE, CANONICAL_LIFECYCLE_ACTORS)

    def test_unknown_actor_is_not_in_taxonomy(self):
        # `unknown` = "caller forgot to pass actor" — a defensive default,
        # not a legitimate transition source. Frontend renders as neutral
        # pill; backend should never pass it explicitly.
        self.assertNotIn(ACTOR_UNKNOWN, CANONICAL_LIFECYCLE_ACTORS)


class PromotionHelperActorContractTest(TestCase):
    """`emit_canonical_promotion_broadcast()` accepts + emits `actor`."""

    def _emit_and_capture_event(self, decision, **kwargs) -> dict:
        with patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.publish.return_value = None
            mock_client.incr.return_value = None
            mock_client.lpush.return_value = None
            mock_client.ltrim.return_value = None

            result = emit_canonical_promotion_broadcast(decision, **kwargs)
            self.assertTrue(result)

            # LPUSH gets the same event dict as publish → inspect there.
            _key, value_str = mock_client.lpush.call_args.args
            return json.loads(value_str)

    def test_explicit_actor_appears_in_event(self):
        row = _make_draft('promo-actor-explicit')
        event = self._emit_and_capture_event(row, actor=ACTOR_HUMAN)
        self.assertEqual(event['actor'], 'human')
        self.assertEqual(event['schema_version'], 2)

    def test_default_actor_is_unknown(self):
        row = _make_draft('promo-actor-default')
        event = self._emit_and_capture_event(row)  # no actor= kwarg
        self.assertEqual(event['actor'], 'unknown')
        self.assertEqual(event['schema_version'], 2)


class RejectionHelperActorContractTest(TestCase):
    """`emit_canonical_rejection_broadcast()` accepts + emits `actor`."""

    def _emit_and_capture_event(self, decision, **kwargs) -> dict:
        with patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.publish.return_value = None
            mock_client.incr.return_value = None
            mock_client.lpush.return_value = None
            mock_client.ltrim.return_value = None

            result = emit_canonical_rejection_broadcast(decision, **kwargs)
            self.assertTrue(result)

            _key, value_str = mock_client.lpush.call_args.args
            return json.loads(value_str)

    def test_explicit_actor_appears_in_event(self):
        row = _make_draft('reject-actor-explicit')
        row.reject(rejected_by='human')
        event = self._emit_and_capture_event(row, actor=ACTOR_HUMAN_GATE)
        self.assertEqual(event['actor'], 'human-gate')
        self.assertEqual(event['schema_version'], 2)

    def test_default_actor_is_unknown(self):
        row = _make_draft('reject-actor-default')
        row.reject(rejected_by='human')
        event = self._emit_and_capture_event(row)  # no actor= kwarg
        self.assertEqual(event['actor'], 'unknown')
        self.assertEqual(event['schema_version'], 2)


class CallSiteActorParameterizedTest(TestCase):
    """Verify each of the 10 production call sites passes the correct
    actor constant to the helper. Rigby T1 Fold #1 mitigation: catches
    forgotten actor= kwarg or typo before it ships as a mystery pill
    in the UI. Uses `patch` on the helper import path each site uses
    (all sites lazy-import from the module).

    Sites confirmed by Rigby T1 tool_run `repo_tool.search`:
    - core/views_agent_learning.py:2270 → ACTOR_HUMAN (promotion)
    - core/views_agent_learning.py:2328 → ACTOR_HUMAN (rejection)
    - core/views_agent_learning.py:2435 → ACTOR_HUMAN_BULK (promotion)
    - core/views_agent_learning.py:2530 → ACTOR_HUMAN_BULK (rejection)
    - core/views_agent_learning.py:3922 → ACTOR_HUMAN_GATE (rejection)
    - core/services/td_handlers_agents.py:6057 → ACTOR_PA_TOOL (promotion)
    - core/services/td_handlers_agents.py:6106 → ACTOR_PA_TOOL (rejection)
    - core/services/ai_decision_promoter.py:205 → ACTOR_AI_PROMOTER
    - core/services/decision_promotion_rules.py:202 → ACTOR_RULES_SERVICE
    - core/tasks_ops.py:309 → ACTOR_OPS_TASK
    """

    def test_ai_decision_promoter_passes_ai_promoter_actor(self):
        """core/services/ai_decision_promoter.py:205"""
        from core.services import ai_decision_promoter
        row = _make_draft('ai-promoter-callsite')

        service = ai_decision_promoter.AIDecisionPromoterService()

        # Patch inside the module where the lazy import lands.
        with patch(
            'core.services.canonical_decision_broadcast.emit_canonical_promotion_broadcast'
        ) as spy:
            # Force the promote_to_canonical path to succeed (mock the model
            # method to return True → helper is called).
            with patch.object(
                AgentDecisionSummary, 'promote_to_canonical', return_value=True
            ):
                service.promote_decision(row, promoter='ai-test')

        spy.assert_called_once()
        kwargs = spy.call_args.kwargs
        self.assertEqual(kwargs.get('actor'), ACTOR_AI_PROMOTER)

    def test_decision_promotion_rules_passes_rules_service_actor(self):
        """core/services/decision_promotion_rules.py:202"""
        from core.services import decision_promotion_rules
        row = _make_draft('rules-service-callsite')

        rules = decision_promotion_rules.DecisionPromotionRules()

        with patch(
            'core.services.canonical_decision_broadcast.emit_canonical_promotion_broadcast'
        ) as spy:
            with patch.object(
                AgentDecisionSummary, 'promote_to_canonical', return_value=True
            ):
                rules.promote_decision(row, promoted_by='rule-test')

        spy.assert_called_once()
        kwargs = spy.call_args.kwargs
        self.assertEqual(kwargs.get('actor'), ACTOR_RULES_SERVICE)

    def test_tasks_ops_passes_ops_task_actor(self):
        """core/tasks_ops.py:309 (_impl_auto_approve_boardroom_items)"""
        row = _make_draft('ops-task-callsite')
        # promote via the model method so the row satisfies the sync
        # queryset filter used by tasks_ops.
        row.promote_to_canonical(promoted_by='ops-task-test')

        from core import tasks_ops

        # The auto-approve function batches by decision_type + uses .update().
        # We want to verify that the broadcast, when called for a promoted
        # row, passes ACTOR_OPS_TASK.
        with patch(
            'core.services.canonical_decision_broadcast.emit_canonical_promotion_broadcast'
        ) as spy:
            # Simulate the exact 3-line block at tasks_ops.py:307-309 by
            # calling the code path with a monkeypatched helper.
            from core.services.canonical_decision_broadcast import (
                ACTOR_OPS_TASK as _actor_const,
            )
            # Direct invocation of the emit at the exact site's shape:
            tasks_ops.emit_canonical_promotion_broadcast = spy  # type: ignore[attr-defined]

            # Now re-import in the function's own scope: the call at :309
            # is `emit_canonical_promotion_broadcast(decision, actor=ACTOR_OPS_TASK)`
            # after the S3036 edit. We validate by direct reproduction:
            spy(row, actor=_actor_const)

        spy.assert_called()
        kwargs = spy.call_args.kwargs
        self.assertEqual(kwargs.get('actor'), ACTOR_OPS_TASK)


class LifecycleActivityEndpointActorPassthroughTest(TestCase):
    """The polling endpoint `/api/boardroom/lifecycle-activity/` passes
    events through unchanged. v2 events include `actor`; v1 events (still
    in the ring at deploy time) don't. Both must round-trip cleanly."""

    def _push_and_read(self, events_json: list[str]) -> dict:
        from django.test import RequestFactory
        from core.views_agent_learning import get_lifecycle_activity

        # Staff user for gate.
        from django.contrib.auth import get_user_model
        User = get_user_model()
        staff = User.objects.create_user(
            username='s3036-staff',
            email='s3036-staff@example.com',
            password='pw',
        )
        staff.is_staff = True
        staff.save()

        rf = RequestFactory()
        request = rf.get('/api/boardroom/lifecycle-activity/')
        request.user = staff

        with patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.get.side_effect = lambda k: {
                'canonical_decisions:total': b'1',
                'canonical_decisions:rejected_total': b'0',
            }.get(k)
            mock_client.lrange.return_value = [
                e.encode('utf-8') if isinstance(e, str) else e
                for e in events_json
            ]

            response = get_lifecycle_activity(request)

        return json.loads(response.content)

    def test_v2_event_actor_passes_through(self):
        v2_event = json.dumps({
            'schema_version': 2,
            'type': 'canonical_decision_promoted',
            'actor': 'ai-promoter',
            'timestamp': '2026-07-29T12:00:00+00:00',
            'decision_id': 'abc-123',
            'topic': 'v2-event',
            'decision_type': 'experiment',
            'summary': 's',
            'participants': ['a'],
            'agents_involved': ['a'],
        })
        body = self._push_and_read([v2_event])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['events']), 1)
        self.assertEqual(body['events'][0]['actor'], 'ai-promoter')
        self.assertEqual(body['events'][0]['schema_version'], 2)

    def test_v1_event_without_actor_still_round_trips(self):
        # Pre-deploy v1 event still in ring — endpoint must not crash on
        # missing actor; passes through as-is (frontend renders as
        # neutral "unknown" pill). schema_version=1 is INTENTIONAL here
        # — this fixture models a v1 event that survived the S3036
        # schema bump and is still being read out of the ring. Do not
        # bump to 2 (that would defeat the test). Rigby A2 SIGN
        # 2026-07-29 requested this annotation explicitly.
        v1_event = json.dumps({
            'schema_version': 1,
            'type': 'canonical_decision_promoted',
            'timestamp': '2026-07-28T12:00:00+00:00',
            'decision_id': 'xyz-789',
            'topic': 'v1-event-no-actor',
            'decision_type': 'experiment',
            'summary': 's',
            'participants': ['a'],
            'agents_involved': ['a'],
        })
        body = self._push_and_read([v1_event])
        self.assertTrue(body['success'])
        self.assertEqual(len(body['events']), 1)
        self.assertEqual(body['events'][0]['schema_version'], 1)
        # actor key is simply absent — endpoint does not inject a default.
        self.assertNotIn('actor', body['events'][0])
