"""Session 3034: rejection broadcast symmetry for the canonical-decision
lifecycle. Closes the deprecation-side gap left after the S3026 → S3032
canonical-promotion arc: promotion emitted `canonical_decision_promoted`
via a single helper across all 6 paths; rejection had zero broadcast
across 4 paths. First real-world exercise of PLAYBOOK-7.7.5 (ratified
S3033) — Rigby T1 sweep caught a 4th rejection production site
(`update_gate_status` action='decline') that the initial Verified
Premises undercounted.

Contract this suite pins:

1. `AgentDecisionSummary.reject()` returns `did_reject: bool` — mirrors
   `promote_to_canonical` idempotency: first call transitions, second
   call no-ops (updated_at NOT bumped on the no-op).
2. `bulk_reject_decisions` iterates per-row and gates broadcast on
   `did_reject`, replacing the S3023 U4-H `.update()` shape. Two calls
   on the same row = one broadcast.
3. PA tool `reject_decision` action gates its broadcast on `did_reject`.
4. Gate-decline path (`update_gate_status` action='decline') routes the
   linked decision through `.reject()` + gated broadcast — S3034 T1 4th
   site catch (Rigby PLAYBOOK-7.7.5 sweep Pushback #1
   `same_pr_actionable`).
5. Rejection broadcast payload shape mirrors promotion payload keys
   (`schema_version:1`, `type='canonical_decision_rejected'`, same
   `decision_id`/`topic`/`decision_type`/`summary`/`participants`/
   `agents_involved` back-compat alias) so subscribers can branch on
   `data.type` without divergent shape handling.
"""
from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from core.models_unified_system import AgentDecisionSummary
from core.services.canonical_decision_broadcast import (
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


class RejectMethodIdempotencyTest(TestCase):
    def test_first_call_returns_true_and_transitions_status(self):
        row = _make_draft('reject-first')
        self.assertEqual(row.status, 'draft')

        result = row.reject(rejected_by='human')

        self.assertTrue(result, "first call must return True (did the transition)")
        row.refresh_from_db()
        self.assertEqual(row.status, 'rejected')

    def test_second_call_returns_false_and_is_noop(self):
        row = _make_draft('reject-idempotent')
        row.reject(rejected_by='first-caller')
        row.refresh_from_db()
        first_updated_at = row.updated_at

        result = row.reject(rejected_by='racing-caller')

        self.assertFalse(result, "second call on rejected row must return False (no-op)")
        row.refresh_from_db()
        # No save happened → auto_now didn't bump updated_at. Same
        # invariant that S3031 codified for promote_to_canonical.
        self.assertEqual(row.updated_at, first_updated_at)


class RejectionBroadcastPayloadShapeTest(TestCase):
    def test_payload_mirrors_promotion_payload_keys(self):
        """Wire shape symmetry: rejection event carries the same keys as
        promotion event so subscribers can branch on `data.type` without
        divergent shape handling. Both emit `schema_version:1` and the
        S3026 A2 `participants` + `agents_involved` back-compat alias."""
        row = _make_draft('shape')
        row.reject(rejected_by='human')

        # Mirror the S3028 promotion-broadcast test patch pattern: the
        # helper does `import redis` inside the function body, so patch
        # `redis.Redis` at module level rather than the (non-existent)
        # module-attribute `canonical_decision_broadcast.redis`.
        with patch('redis.Redis') as mock_redis_cls:
            mock_client = mock_redis_cls.from_url.return_value
            mock_client.publish.return_value = None
            mock_client.incr.return_value = None
            result = emit_canonical_rejection_broadcast(row, request_id='req-1')

        self.assertTrue(result)
        publish_calls = mock_client.publish.call_args_list
        self.assertEqual(len(publish_calls), 1)
        channel, payload_str = publish_calls[0].args
        self.assertEqual(channel, 'agent_learning')

        envelope = json.loads(payload_str)
        self.assertEqual(envelope['type'], 'canonical_policy_rejected')
        data = envelope['data']
        # Same schema_version + shape as promotion.
        # S3036: bumped 1→2 to signal presence of `actor` field.
        self.assertEqual(data['schema_version'], 2)
        self.assertEqual(data['type'], 'canonical_decision_rejected')
        self.assertEqual(data['decision_id'], str(row.id))
        self.assertEqual(data['topic'], row.topic)
        self.assertEqual(data['decision_type'], row.decision_type)
        # S3026 A2 dual-emit: canonical `participants` + S657 back-compat
        # alias `agents_involved` — both keys must be present.
        self.assertEqual(data['participants'], ['agent_a', 'agent_b'])
        self.assertEqual(data['agents_involved'], ['agent_a', 'agent_b'])


class BulkRejectPerRowBroadcastTest(TestCase):
    def test_bulk_reject_iterates_per_row_and_gates_broadcast_on_did_reject(self):
        """S3034 replaces the S3023 U4-H `queryset.update(status='rejected',
        updated_at=...)` shape with a per-row loop mirroring
        `bulk_promote_decisions`. Each row's broadcast is gated on
        `did_reject` so a row that's already rejected between filter and
        loop iter doesn't double-broadcast."""
        from core.views_agent_learning import bulk_reject_decisions

        row1 = _make_draft('bulk-1')
        row2 = _make_draft('bulk-2')

        rf = RequestFactory()
        req = rf.post(
            '/api/boardroom/decisions/bulk-reject/',
            data=json.dumps({'decision_ids': [str(row1.id), str(row2.id)]}),
            content_type='application/json',
        )
        # Bypass the staff-gate for this test (same pattern used across
        # existing bulk-decision suites).
        with patch(
            'core.views_agent_learning._require_boardroom_staff',
            return_value=None,
        ), patch(
            'core.services.canonical_decision_broadcast.emit_canonical_rejection_broadcast'
        ) as spy:
            spy.return_value = True
            response = bulk_reject_decisions(req)

        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(body['count'], 2)
        self.assertEqual(body['broadcasts_succeeded'], 2)
        self.assertEqual(body['broadcasts_failed'], 0)
        # Broadcast called once per row.
        self.assertEqual(spy.call_count, 2)

        row1.refresh_from_db()
        row2.refresh_from_db()
        self.assertEqual(row1.status, 'rejected')
        self.assertEqual(row2.status, 'rejected')


class BulkRejectRaceDoesNotDoubleBroadcastTest(TestCase):
    def test_row_already_rejected_between_filter_and_loop_does_not_broadcast(self):
        """The gating on `did_reject` prevents a race where a row is
        rejected by a competing path between the filter and the loop iter.
        Two bulk calls on the same row = one broadcast total."""
        from core.views_agent_learning import bulk_reject_decisions

        row = _make_draft('race')

        rf = RequestFactory()
        req = rf.post(
            '/api/boardroom/decisions/bulk-reject/',
            data=json.dumps({'decision_ids': [str(row.id)]}),
            content_type='application/json',
        )

        with patch(
            'core.views_agent_learning._require_boardroom_staff',
            return_value=None,
        ), patch(
            'core.services.canonical_decision_broadcast.emit_canonical_rejection_broadcast'
        ) as spy:
            spy.return_value = True
            # First call: performs the transition + broadcasts.
            bulk_reject_decisions(req)
            # Second call: row is already rejected (filter is
            # `status='draft'` so the queryset is empty this time OR the
            # `.reject()` no-op catches a mid-loop race). Broadcast MUST
            # NOT fire again.
            bulk_reject_decisions(req)

        self.assertEqual(spy.call_count, 1)


class PaHandlerRejectBroadcastTest(TestCase):
    def test_pa_reject_decision_action_emits_broadcast_via_helper(self):
        """PA tool `boardroom` action `reject_decision` gates its broadcast
        on `did_reject` per S3034. Mirrors the S3028 promote_decision test
        shape (dispatcher._handle_boardroom entry + spy on the helper)."""
        from core.services.tool_dispatcher import ToolDispatcher

        row = _make_draft('pa-reject')

        dispatcher = ToolDispatcher()
        with patch(
            'core.services.canonical_decision_broadcast.emit_canonical_rejection_broadcast'
        ) as spy:
            spy.return_value = True
            result = dispatcher._handle_boardroom(
                tool_name='boardroom',
                payload={'action': 'reject_decision', 'id': str(row.id), 'reason': 'test'},
                user_id=None,
                trace_id='test-s3034',
            )

        self.assertEqual(result['success'], True)
        self.assertEqual(result['new_status'], 'rejected')
        self.assertEqual(spy.call_count, 1)


class GateDeclineRejectionBroadcastTest(TestCase):
    """S3034 T1 Rigby sweep 4th-site catch (`same_pr_actionable`
    Pushback #1). The gate-decline path in `update_gate_status` rejects
    the linked decision — MUST route through `.reject()` and gate
    broadcast on `did_reject`, same discipline as the other 3 rejection
    sites. `update_gate_status` is `@token_auth_required` so we
    force-login a session user (S2789 pattern)."""

    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.user = U.objects.create_user(
            username='s3034-gate-decline-fixture',
            email='s3034-gate-decline@donkeybetz.test',
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_gate_decline_routes_through_reject_method_and_gates_broadcast(self):
        from core.models_pilot_readiness import PilotReadinessGate

        decision = _make_draft('gate-decline')
        gate = PilotReadinessGate.objects.create(
            decision=decision,
            summary='test gate',
        )

        url = f'/api/pilot-gates/{gate.id}/status/'
        body = json.dumps({'action': 'decline', 'notes': 'not needed'})

        with patch(
            'core.services.canonical_decision_broadcast.emit_canonical_rejection_broadcast'
        ) as spy:
            spy.return_value = True
            response = self.client.post(url, data=body, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        decision.refresh_from_db()
        self.assertEqual(decision.status, 'rejected')
        # Broadcast fired exactly once (did_reject=True).
        self.assertEqual(spy.call_count, 1)

        # Second decline call is a no-op — decision is already rejected
        # (idempotent .reject() returns False) so broadcast MUST NOT fire
        # again. Note: gate.status is already 'declined' from the first
        # call, but the decline branch still runs; the invariant is the
        # broadcast count stays at 1 across both calls.
        with patch(
            'core.services.canonical_decision_broadcast.emit_canonical_rejection_broadcast'
        ) as spy2:
            spy2.return_value = True
            response2 = self.client.post(url, data=body, content_type='application/json')

        self.assertEqual(response2.status_code, 200)
        self.assertEqual(spy2.call_count, 0)
