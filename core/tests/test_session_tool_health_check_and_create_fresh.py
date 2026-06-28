"""Session 1247 — session_tool.health_check + create_fresh fixes.

Two bugs surfaced at S1247 open and filed as findings 1 + 2 in deliverable
`6103e35c-9914-4028-82cb-2866169d580e`:

  Finding 1 — `session_tool.health_check` ignored explicit `conversation_id`
    Root cause: PA entrypoint unconditionally overrode the argument via
    `arguments['conversation_id'] = self.conversation_id`. Explicit caller
    intent was silently stomped. Fix: switch the entrypoint to `setdefault`
    so the LLM's value wins when passed.

  Finding 2 — `session_tool.create_fresh` returned empty `starter_prompt`
    Root cause: handler read `self._current_conversation_id` which is never
    assigned anywhere in the codebase, AND `carry_forward_summary` was only
    used in the first message body — never as the returned starter_prompt.
    Fix: prefer the explicit carry_forward_summary; fall back to the active
    conversation's auto-summary via payload.conversation_id.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import ChatConversation
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _dispatch_session(user_id, payload):
    """Invoke session_tool via the dispatcher entry point."""
    dispatcher = ToolDispatcher()
    return dispatcher._handle_session(  # type: ignore[attr-defined]
        tool_name='session_tool',
        payload=payload,
        user_id=user_id,
        trace_id='test-session',
    )


class SessionToolHealthCheckExplicitConversationIdTests(TestCase):
    """Finding 1 — health_check must honor explicit conversation_id."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )
        self.active_conv_id = 'pa-test-active'
        self.target_conv_id = 'pa-test-target'
        for cid, title, msg in [
            (self.active_conv_id, 'Active thread', 'active-msg'),
            (self.target_conv_id, 'Target thread', 'target-msg'),
        ]:
            for _ in range(5):
                ChatConversation.objects.create(
                    conversation_id=cid,
                    user_id=self.alice.id,
                    session_title=title,
                    user_message=msg,
                    assistant_response='ack',
                )

    def test_health_check_honors_explicit_conversation_id(self):
        result = _dispatch_session(
            self.alice.id,
            {'action': 'health_check', 'conversation_id': self.target_conv_id},
        )
        self.assertEqual(result['conversation_id'], self.target_conv_id)

    def test_health_check_explicit_id_differs_from_active(self):
        active = _dispatch_session(
            self.alice.id,
            {'action': 'health_check', 'conversation_id': self.active_conv_id},
        )
        target = _dispatch_session(
            self.alice.id,
            {'action': 'health_check', 'conversation_id': self.target_conv_id},
        )
        self.assertEqual(active['conversation_id'], self.active_conv_id)
        self.assertEqual(target['conversation_id'], self.target_conv_id)
        self.assertNotEqual(active['conversation_id'], target['conversation_id'])

    def test_health_check_missing_conversation_id_errors_cleanly(self):
        result = _dispatch_session(
            self.alice.id, {'action': 'health_check'},
        )
        self.assertIn('error', result)
        self.assertIn('No conversation_id', result['error'])


class SessionToolCreateFreshStarterPromptTests(TestCase):
    """Finding 2 — create_fresh must populate starter_prompt from carry_forward_summary."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )

    def test_create_fresh_uses_carry_forward_as_starter_prompt(self):
        carry = "S1247 context: morning_brief P1 verification 13:00 UTC tomorrow"
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'create_fresh',
                'title': 'S1247 fresh',
                'carry_forward_summary': carry,
            },
        )
        self.assertEqual(result['starter_prompt'], carry)
        self.assertTrue(result['conversation_id'].startswith('pa-'))
        self.assertEqual(result['title'], 'S1247 fresh')

    def test_create_fresh_empty_carry_forward_falls_back_to_prior_conversation(self):
        old_conv_id = 'pa-test-prior'
        for _ in range(8):
            ChatConversation.objects.create(
                conversation_id=old_conv_id,
                user_id=self.alice.id,
                session_title='Prior thread',
                user_message='prior content',
                assistant_response='ack',
            )
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'create_fresh',
                'title': 'fallback test',
                'conversation_id': old_conv_id,
            },
        )
        self.assertEqual(result['action'], 'create_fresh')
        self.assertNotEqual(result['conversation_id'], old_conv_id)

    def test_create_fresh_no_carry_no_prior_returns_empty_starter(self):
        result = _dispatch_session(
            self.alice.id,
            {'action': 'create_fresh', 'title': 'standalone'},
        )
        self.assertEqual(result['starter_prompt'], '')
        self.assertEqual(result['title'], 'standalone')


class PaEntrypointConversationIdSetdefaultTests(TestCase):
    """Finding 1 root-cause fix — entrypoint must use setdefault for conversation_id."""

    def test_setdefault_preserves_explicit_caller_value(self):
        from core.services import unified_pa_entrypoint
        import inspect

        source = inspect.getsource(unified_pa_entrypoint)
        self.assertIn(
            "arguments.setdefault('conversation_id', self.conversation_id)",
            source,
            msg=(
                "Entrypoint must use setdefault so explicit conversation_id from the LLM "
                "is preserved. See Session 1247 finding 1."
            ),
        )
        self.assertNotIn(
            "arguments['conversation_id'] = self.conversation_id",
            source,
            msg=(
                "Unconditional override of conversation_id was the Session 1247 finding 1 "
                "root cause — must not regress."
            ),
        )
