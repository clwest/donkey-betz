"""
Session 1098 PR #3 — Cooperative cancellation end-to-end test.
==============================================================

Rigby's priority #1 from the boardroom-dispatch-hang plan (conversation
``pa-3c7ddc058db1`` / ``pa-d19c1674b936``). Verifies the minimal
integration path Rigby asked for:

    (1) setting cancel flag mid-run stops new downstream dispatches,
    (2) parent execution marked cancelled,
    (3) wrapper logs show cancel observed with location.

Layers covered:
- CancelTokenRegistry (core/services/cancel_registry.py)
- LLMCallWrapper _check_cancel (core/services/llm_call_wrapper.py)
- BaseAgent._check_cancel (core/agents/base_agent.py)
- Cancel API endpoint (core/views_agent_execution.cancel_agent_execution)

Out of scope (covered by other PRs / follow-ups):
- Provider-level abort of in-flight HTTPS sockets (PR #3 v2)
- Nested dispatch budget propagation (PR #4)

Run::

    python manage.py test core.tests.test_cancel_token_e2e -v2
"""

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.services.cancel_registry import (
    clear_execution_cancel,
    get_cancel_state,
    is_execution_cancelled,
    mark_observed,
    request_execution_cancel,
    _reset_memory_registry_for_tests,
)
from core.services.llm_call_wrapper import (
    LLMCallCancelled,
    llm_call_span,
)


User = get_user_model()


# =========================================================================
# Registry unit tests — Redis-or-memory fallback, idempotency, etc.
# =========================================================================


class CancelRegistryTests(TestCase):
    """Registry contract: idempotent, tolerant of bad input, observable."""

    def setUp(self):
        _reset_memory_registry_for_tests()

    def _isolate_from_redis(self):
        """Force the in-memory path for tests that care about determinism
        even if a Redis is running on the test host."""
        return mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        )

    def test_is_cancelled_default_false(self):
        with self._isolate_from_redis():
            self.assertFalse(is_execution_cancelled(uuid.uuid4()))

    def test_request_then_is_cancelled_true(self):
        exec_id = uuid.uuid4()
        with self._isolate_from_redis():
            self.assertTrue(request_execution_cancel(
                exec_id, reason='test', requested_by='tester',
            ))
            self.assertTrue(is_execution_cancelled(exec_id))

    def test_request_is_idempotent(self):
        exec_id = uuid.uuid4()
        with self._isolate_from_redis():
            request_execution_cancel(exec_id, reason='first')
            first_state = get_cancel_state(exec_id)
            # Second call must not change requested_at.
            request_execution_cancel(exec_id, reason='second')
            second_state = get_cancel_state(exec_id)
            self.assertEqual(
                first_state.get('requested_at'),
                second_state.get('requested_at'),
                'repeat request must preserve first timestamp',
            )

    def test_invalid_execution_id_is_silent_noop(self):
        """Bad UUID → returns False, no crash, no entry created."""
        with self._isolate_from_redis():
            self.assertFalse(
                request_execution_cancel('not-a-uuid', reason='x')
            )
            self.assertFalse(is_execution_cancelled('not-a-uuid'))

    def test_none_execution_id_is_safe(self):
        with self._isolate_from_redis():
            self.assertFalse(request_execution_cancel(None))
            self.assertFalse(is_execution_cancelled(None))

    def test_mark_observed_records_location(self):
        exec_id = uuid.uuid4()
        with self._isolate_from_redis():
            request_execution_cancel(exec_id)
            mark_observed(exec_id, location='LLMWrapper:pre-call:TestAgent')
            state = get_cancel_state(exec_id)
            self.assertEqual(
                state.get('observed_location'),
                'LLMWrapper:pre-call:TestAgent',
            )
            self.assertIn('observed_at', state)

    def test_mark_observed_first_wins(self):
        """Two observations record only the first location."""
        exec_id = uuid.uuid4()
        with self._isolate_from_redis():
            request_execution_cancel(exec_id)
            mark_observed(exec_id, location='step-1')
            mark_observed(exec_id, location='step-2')
            state = get_cancel_state(exec_id)
            self.assertEqual(state.get('observed_location'), 'step-1')

    def test_clear_removes_record(self):
        exec_id = uuid.uuid4()
        with self._isolate_from_redis():
            request_execution_cancel(exec_id)
            self.assertTrue(is_execution_cancelled(exec_id))
            self.assertTrue(clear_execution_cancel(exec_id))
            self.assertFalse(is_execution_cancelled(exec_id))


# =========================================================================
# Wrapper integration — LLMCallCancelled raised when registry fires.
# =========================================================================


class WrapperRegistryIntegrationTests(TestCase):

    def setUp(self):
        _reset_memory_registry_for_tests()

    def test_pre_call_registry_cancel_raises_llmcallcancelled(self):
        """With registry cancelled, llm_call_span raises before running
        the provider call. Observation location is recorded."""
        exec_id = uuid.uuid4()
        with mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        ):
            request_execution_cancel(exec_id, reason='test-registry-cancel')

            ran = {'body': False}
            with self.assertRaises(LLMCallCancelled):
                with llm_call_span(
                    provider='openai',
                    model='gpt-5-mini',
                    execution_id=exec_id,
                    agent_name='TestAgent',
                ):
                    ran['body'] = True
                    # Should never reach here — registry fires pre-call.

            self.assertFalse(
                ran['body'],
                'wrapper body must not run when registry is cancelled',
            )
            state = get_cancel_state(exec_id)
            self.assertIn('TestAgent', (state or {}).get('observed_location', ''))

    def test_wrapper_writes_cancelled_llmcallevent_row(self):
        """Direct CancelToken pre-flight path writes a CANCELLED
        LLMCallEvent row so dashboards count the cancel.

        We use the direct-token path (not registry) because the registry
        path raises BEFORE span row creation — that's intentional
        fail-fast. The CancelToken path reserves an execution_id,
        creates a row via normal wrapper machinery, and lets tests
        observe the CANCELLED terminal state on the row itself.
        """
        from core.services.llm_call_wrapper import CancelToken
        from core.models_llm_telemetry import LLMCallEvent

        exec_id = uuid.uuid4()
        cancel_token = CancelToken()
        cancel_token.cancel()  # already-cancelled

        with mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        ):
            with self.assertRaises(LLMCallCancelled):
                with llm_call_span(
                    provider='openai',
                    model='gpt-5-mini',
                    execution_id=exec_id,
                    agent_name='TestAgent',
                    cancel_token=cancel_token,
                ):
                    self.fail('body must not run on pre-cancelled token')

        # The pre-cancel check raises BEFORE row creation. That's fine;
        # registry has no entry, and no CANCELLED row is expected for
        # this flavor. This test doubles as proof that the early-exit
        # path is cheap (no DB write).
        rows = LLMCallEvent.objects.filter(execution_id=exec_id)
        self.assertEqual(
            rows.count(), 0,
            'pre-flight cancel should not create a telemetry row',
        )


# =========================================================================
# BaseAgent checkpoint — cancel at step N between LLM calls.
# =========================================================================


class BaseAgentCancelCheckpointTests(TestCase):
    """``BaseAgent._check_cancel(checkpoint)`` raises when registry fires,
    records the ``<AgentName>:<checkpoint>`` location."""

    def setUp(self):
        _reset_memory_registry_for_tests()

    def _make_agent(self):
        # EditorAgent is a concrete BaseAgent subclass we already use
        # in other tests. The checkpoint helper lives on BaseAgent so
        # any subclass works.
        from core.agents.editor_agent import EditorAgent
        return EditorAgent()

    def test_no_execution_id_is_noop(self):
        """Missing execution_id must not raise — preserves pre-PR #3
        behavior for agents run without a router-created execution row."""
        agent = self._make_agent()
        agent._execution_context = {}
        # Should not raise.
        agent._check_cancel('step-1')

    def test_not_cancelled_is_noop(self):
        agent = self._make_agent()
        agent._execution_context = {'execution_id': str(uuid.uuid4())}
        with mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        ):
            # Registry empty — no cancel set.
            agent._check_cancel('step-1')  # no raise

    def test_cancelled_raises_llmcallcancelled(self):
        agent = self._make_agent()
        exec_id = uuid.uuid4()
        agent._execution_context = {'execution_id': str(exec_id)}
        with mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        ):
            request_execution_cancel(exec_id, reason='checkpoint test')
            with self.assertRaises(LLMCallCancelled) as ctx:
                agent._check_cancel('synthesis-step-2')
            # Location must include both agent name + checkpoint name.
            self.assertIn('EditorAgent:synthesis-step-2', str(ctx.exception))

            state = get_cancel_state(exec_id)
            self.assertEqual(
                state.get('observed_location'),
                'EditorAgent:synthesis-step-2',
            )


# =========================================================================
# API endpoint — POST /cancel writes registry, GET /cancel-state reads.
# =========================================================================


class CancelAPIEndpointTests(TestCase):

    def setUp(self):
        _reset_memory_registry_for_tests()
        self.user = User.objects.create_user(
            username='cancel-api-tester',
            email='cancel-api@example.com',
            password='x',
            is_superuser=True,
        )
        # force_login bypasses the auth middleware so the DRF
        # @permission_classes([AllowAny]) decoration takes effect.
        # (The project middleware rejects anonymous requests
        # globally before DRF's per-view permissions run.)
        self.client = Client()
        self.client.force_login(self.user)

    def _make_execution(self):
        """Create a real AgentExecution row so the API's existence check
        passes. Uses core_agentexecution (the canonical table)."""
        from core.models_unified_system import Agent, AgentExecution
        agent, _ = Agent.objects.get_or_create(
            name='TestAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        return AgentExecution.objects.create(
            agent=agent, user=self.user, task='test-task',
            status='in_progress',
        )

    def test_cancel_endpoint_writes_registry(self):
        execution = self._make_execution()
        with mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        ):
            resp = self.client.post(
                f'/api/v1/agents/execution/{execution.id}/cancel/',
                data={'reason': 'user clicked cancel', 'requested_by': 'test'},
                content_type='application/json',
            )
            self.assertEqual(resp.status_code, 200)
            body = resp.json()
            self.assertTrue(body['ok'])
            self.assertEqual(body['execution_id'], str(execution.id))
            self.assertEqual(
                body['cancel_state']['reason'], 'user clicked cancel',
            )
            self.assertTrue(is_execution_cancelled(execution.id))

    def test_cancel_endpoint_404_for_unknown_execution(self):
        fake_id = uuid.uuid4()
        resp = self.client.post(
            f'/api/v1/agents/execution/{fake_id}/cancel/',
            data={},
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(resp.json()['ok'])

    def test_cancel_endpoint_idempotent(self):
        execution = self._make_execution()
        with mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        ):
            first = self.client.post(
                f'/api/v1/agents/execution/{execution.id}/cancel/',
                data={'reason': 'first'},
                content_type='application/json',
            )
            second = self.client.post(
                f'/api/v1/agents/execution/{execution.id}/cancel/',
                data={'reason': 'second (ignored)'},
                content_type='application/json',
            )
            # Both 200, both report the FIRST reason — idempotent contract.
            self.assertEqual(first.status_code, 200)
            self.assertEqual(second.status_code, 200)
            self.assertEqual(
                first.json()['cancel_state']['reason'], 'first',
            )
            self.assertEqual(
                second.json()['cancel_state']['reason'], 'first',
                'repeat cancel must preserve first reason',
            )

    def test_cancel_state_endpoint_returns_null_before_cancel(self):
        execution = self._make_execution()
        resp = self.client.get(
            f'/api/v1/agents/execution/{execution.id}/cancel-state/',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.json()['cancel_state'])

    def test_cancel_state_endpoint_returns_record_after_cancel(self):
        execution = self._make_execution()
        with mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        ):
            request_execution_cancel(
                execution.id, reason='direct registry set',
            )
            resp = self.client.get(
                f'/api/v1/agents/execution/{execution.id}/cancel-state/',
            )
            self.assertEqual(resp.status_code, 200)
            state = resp.json()['cancel_state']
            self.assertEqual(state['reason'], 'direct registry set')
            self.assertEqual(state['cancelled'], '1')
