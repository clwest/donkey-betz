"""
Session 1175 PR-2b-2 — schedule_followup return-shape stability
================================================================

Rigby's PR-2b-1 review (Session 1174 handoff line 110-114) flagged that the
``schedule_followup`` tool returned the full standard keys on success paths
(``mode``, ``subscription_id``, ``state``, ``expires_at``, ``after_seconds``,
``execution_id``, ``execution_status``, ``message``) but only
``{success: false, error: <msg>}`` on error paths. Callers couldn't treat
the response shape as stable.

PR-2b-2 unifies every return through ``_make_followup_response()``. This
test pins the 11-key contract: ``success, mode, subscription_id,
execution_id, execution_status, state, expires_at, fired_at,
after_seconds, message, error`` — always present, None where not
applicable.

Run::

    python manage.py test core.tests.test_schedule_followup_response_shape -v2
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_unified_system import (
    Agent,
    AgentExecution,
    AgentFollowupSubscription,
)
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


STABLE_KEYS = {
    'success', 'mode', 'subscription_id', 'execution_id', 'execution_status',
    'state', 'expires_at', 'fired_at', 'after_seconds', 'message', 'error',
}


class ScheduleFollowupReturnShapeTests(TestCase):
    """Every return path emits the full 11-key contract."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='followup-shape-test', email='shape@example.com', password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='ResearchAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        self.dispatcher = ToolDispatcher()
        self.conversation_id = 'pa-shape-test-abc123'

    def _invoke(self, payload):
        return self.dispatcher._handle_schedule_followup(
            tool_name='schedule_followup',
            payload=payload,
            user_id=self.user.id,
            trace_id='shape-trace',
        )

    def _assert_stable_shape(self, response):
        self.assertIsInstance(response, dict)
        self.assertEqual(
            set(response.keys()), STABLE_KEYS,
            f"Response shape drifted from stable contract. Got keys: {set(response.keys())!r}",
        )

    # --- Error paths ---

    def test_missing_conversation_id_emits_full_shape(self):
        result = self._invoke({'execution_id': 'whatever'})
        self._assert_stable_shape(result)
        self.assertFalse(result['success'])
        self.assertIn('conversation_id', result['error'].lower())
        # Every standard success key is present-as-None.
        for k in ('mode', 'subscription_id', 'execution_id', 'execution_status',
                  'state', 'expires_at', 'fired_at', 'after_seconds', 'message'):
            self.assertIsNone(result[k], f"key {k!r} should be None on this error path")

    def test_missing_execution_and_task_id_emits_full_shape(self):
        result = self._invoke({'conversation_id': self.conversation_id})
        self._assert_stable_shape(result)
        self.assertFalse(result['success'])
        self.assertIn('execution_id', result['error'].lower())

    def test_unknown_execution_id_emits_full_shape(self):
        result = self._invoke({
            'conversation_id': self.conversation_id,
            'execution_id': '00000000-0000-0000-0000-000000000000',
        })
        self._assert_stable_shape(result)
        self.assertFalse(result['success'])
        self.assertIn('no agentexecution', result['error'].lower())

    def test_null_conversation_id_on_execution_emits_full_shape(self):
        # Non-PA dispatch: execution has no conversation_id stamped.
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='non-pa',
            status='in_progress',
        )
        result = self._invoke({
            'conversation_id': self.conversation_id,
            'execution_id': str(execution.id),
        })
        self._assert_stable_shape(result)
        self.assertFalse(result['success'])
        self.assertEqual(result['execution_id'], str(execution.id))
        self.assertEqual(result['execution_status'], 'in_progress')
        self.assertIn('not dispatched from a pa', result['error'].lower())

    def test_cross_conversation_emits_full_shape(self):
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id='pa-other-conv-xyz',
        )
        result = self._invoke({
            'conversation_id': self.conversation_id,
            'execution_id': str(execution.id),
        })
        self._assert_stable_shape(result)
        self.assertFalse(result['success'])
        self.assertEqual(result['execution_id'], str(execution.id))
        self.assertIn('cross-conversation', result['error'].lower())

    # --- Success paths ---

    def test_normal_subscribe_emits_full_shape(self):
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id=self.conversation_id,
        )
        result = self._invoke({
            'conversation_id': self.conversation_id,
            'execution_id': str(execution.id),
            'after_seconds': 120,
        })
        self._assert_stable_shape(result)
        self.assertTrue(result['success'])
        self.assertEqual(result['mode'], 'subscribed')
        self.assertEqual(result['state'], AgentFollowupSubscription.STATE_ARMED)
        self.assertEqual(result['after_seconds'], 120)
        self.assertIsNotNone(result['subscription_id'])
        self.assertIsNotNone(result['expires_at'])
        self.assertIsNone(result['fired_at'])
        self.assertIsNone(result['error'])

    def test_after_seconds_cap_enforced(self):
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id=self.conversation_id,
        )
        result = self._invoke({
            'conversation_id': self.conversation_id,
            'execution_id': str(execution.id),
            'after_seconds': 999999,
        })
        self._assert_stable_shape(result)
        self.assertTrue(result['success'])
        # Session 1178 follow-up: cap pulled from the model constant so a
        # future bump propagates automatically. Both Phase 1 explicit and
        # Phase 2 implicit must read from the same source of truth.
        self.assertEqual(
            result['after_seconds'],
            AgentFollowupSubscription.MAX_TTL_SECONDS,
        )

    def test_default_after_seconds_matches_model_constant(self):
        """Cross-path invariant — when the caller passes no `after_seconds`,
        the explicit `schedule_followup` default MUST equal the model's
        `DEFAULT_TTL_SECONDS`. Phase 2 auto-wake reads the same constant; if
        these two ever drift again, dispatches that don't call
        `schedule_followup` will get a different window than dispatches that
        do — exactly the silent-failure mode the Session 1178 hotfix closed
        (PR #2347, model constants on AgentFollowupSubscription)."""
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user, task='pa-task',
            status='in_progress', conversation_id=self.conversation_id,
        )
        # No after_seconds in payload → handler uses its default.
        result = self._invoke({
            'conversation_id': self.conversation_id,
            'execution_id': str(execution.id),
        })
        self._assert_stable_shape(result)
        self.assertTrue(result['success'])
        self.assertEqual(
            result['after_seconds'],
            AgentFollowupSubscription.DEFAULT_TTL_SECONDS,
            'Phase 1 explicit-tool default drifted from the model constant. '
            'Both Phase 1 and Phase 2 read from AgentFollowupSubscription.DEFAULT_TTL_SECONDS — '
            'if you changed one without updating the other, this test caught the bug.',
        )
