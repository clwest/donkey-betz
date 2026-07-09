"""Session 1248 — session_tool.retire / set_active / seed + dispatcher gate.

Closes the ~$3.60/day stale-thread dispatch waste documented in deliverable
777d9cd8-… (S1212 audit). Three new PA tool actions land in this PR plus a
ChatConversation.session_active gate inside conversation_action_dispatcher
that refuses to fire next_steps into retired threads.

Design Qs were routed through Rigby on pa-3901b70e61934df7 before the diff;
her sign-off picks (Q1c / Q2c / Q3a / Q4a) are captured at the top of each
action's handler block in `td_handlers_core.py`.
"""
from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import ChatConversation
from core.services.conversation_action_dispatcher import (
    ConversationActionDispatcher,
)
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _dispatch_session(user_id, payload):
    """Invoke session_tool via the dispatcher entry point."""
    dispatcher = ToolDispatcher()
    return dispatcher._handle_session(  # type: ignore[attr-defined]
        tool_name='session_tool',
        payload=payload,
        user_id=user_id,
        trace_id='test-session-1248',
    )


class SessionToolRetireTests(TestCase):
    """Q1(c) — bulk-flip session_active=False, gate the bound thread."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )
        self.target = 'pa-test-retire-target'
        self.bound = 'pa-test-retire-bound'
        for cid, title in [(self.target, 'target'), (self.bound, 'bound')]:
            for _ in range(4):
                ChatConversation.objects.create(
                    conversation_id=cid,
                    user_id=self.alice.id,
                    session_title=title,
                    user_message='m',
                    assistant_response='ack',
                )

    def test_retire_happy_path_flips_all_rows(self):
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'retire',
                'conversation_id': self.target,
                '_bound_conversation_id': self.bound,
            },
        )
        self.assertTrue(result['retired'])
        self.assertEqual(result['updated_count'], 4)
        self.assertTrue(result['previously_active'])
        self.assertFalse(result['is_current_bound'])
        self.assertEqual(
            ChatConversation.objects.filter(
                conversation_id=self.target, session_active=True,
            ).count(),
            0,
        )

    def test_retire_currently_bound_without_force_blocks(self):
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'retire',
                'conversation_id': self.bound,
                '_bound_conversation_id': self.bound,
            },
        )
        self.assertFalse(result['retired'])
        self.assertTrue(result['is_current_bound'])
        self.assertIn('error', result)
        self.assertIn('force=true', result['error'])
        # All rows still active — no side effect from the blocked attempt.
        self.assertEqual(
            ChatConversation.objects.filter(
                conversation_id=self.bound, session_active=True,
            ).count(),
            4,
        )

    def test_retire_currently_bound_with_force_succeeds_with_notice(self):
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'retire',
                'conversation_id': self.bound,
                '_bound_conversation_id': self.bound,
                'force': True,
            },
        )
        self.assertTrue(result['retired'])
        self.assertTrue(result['is_current_bound'])
        self.assertIn('pin_rotation_notice', result)
        self.assertIn(self.bound, result['pin_rotation_notice'])

    def test_retire_idempotent_second_call_zero_update(self):
        # Session 2728 F-S-6 patch — second retire on an already-retired
        # target now returns `retired: False + reason: "already_retired"`
        # instead of the prior misleading `retired: True + updated_count: 0`.
        # Chris ratified option (b) at Batch A tool 2 close: distinguish
        # not_found from already_retired via an existence check.
        first = _dispatch_session(
            self.alice.id,
            {
                'action': 'retire',
                'conversation_id': self.target,
                '_bound_conversation_id': self.bound,
            },
        )
        self.assertTrue(first['retired'])
        self.assertGreater(first['updated_count'], 0)
        second = _dispatch_session(
            self.alice.id,
            {
                'action': 'retire',
                'conversation_id': self.target,
                '_bound_conversation_id': self.bound,
            },
        )
        # Second call is a no-op — rows exist but none session_active=True.
        self.assertFalse(second['retired'])
        self.assertEqual(second['updated_count'], 0)
        self.assertFalse(second['previously_active'])
        self.assertEqual(second['reason'], 'already_retired')
        self.assertIn('already retired', second.get('message', ''))

    def test_retire_missing_conversation_id_errors(self):
        result = _dispatch_session(
            self.alice.id,
            {'action': 'retire', '_bound_conversation_id': self.bound},
        )
        self.assertIn('error', result)
        self.assertIn('requires conversation_id', result['error'])


class SessionToolSetActiveTests(TestCase):
    """Q2(c) — un-retire, scoped to symmetric inverse of retire."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )
        self.retired_cid = 'pa-test-setactive-retired'
        for _ in range(3):
            ChatConversation.objects.create(
                conversation_id=self.retired_cid,
                user_id=self.alice.id,
                session_title='retired thread',
                user_message='m',
                assistant_response='ack',
                session_active=False,
            )

    def test_set_active_reactivates_all_rows(self):
        result = _dispatch_session(
            self.alice.id,
            {'action': 'set_active', 'conversation_id': self.retired_cid},
        )
        self.assertTrue(result['reactivated'])
        self.assertEqual(result['updated_count'], 3)
        self.assertTrue(result['previously_retired'])
        self.assertEqual(
            ChatConversation.objects.filter(
                conversation_id=self.retired_cid, session_active=True,
            ).count(),
            3,
        )

    def test_set_active_idempotent_when_already_active(self):
        _dispatch_session(
            self.alice.id,
            {'action': 'set_active', 'conversation_id': self.retired_cid},
        )
        second = _dispatch_session(
            self.alice.id,
            {'action': 'set_active', 'conversation_id': self.retired_cid},
        )
        self.assertTrue(second['reactivated'])
        self.assertEqual(second['updated_count'], 0)
        self.assertFalse(second['previously_retired'])

    def test_set_active_unknown_conversation_errors(self):
        result = _dispatch_session(
            self.alice.id,
            {'action': 'set_active', 'conversation_id': 'pa-does-not-exist'},
        )
        self.assertIn('error', result)
        self.assertIn('No conversation found', result['error'])

    def test_set_active_missing_conversation_id_errors(self):
        result = _dispatch_session(self.alice.id, {'action': 'set_active'})
        self.assertIn('error', result)
        self.assertIn('requires conversation_id', result['error'])


class SessionToolSeedTests(TestCase):
    """Q3(a) — append [SYSTEM SEED] message, source='pa', content REQUIRED."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )
        self.existing_cid = 'pa-test-seed-existing'
        ChatConversation.objects.create(
            conversation_id=self.existing_cid,
            user_id=self.alice.id,
            session_title='seedable thread',
            user_message='m',
            assistant_response='ack',
        )

    def test_seed_happy_path_appends_marker_row(self):
        before = ChatConversation.objects.filter(
            conversation_id=self.existing_cid,
        ).count()
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'seed',
                'conversation_id': self.existing_cid,
                'content': 'S1248 carry-forward context for next thread',
            },
        )
        self.assertTrue(result['seeded'])
        self.assertEqual(result['marker'], '[SYSTEM SEED]')
        self.assertEqual(
            result['content_length'],
            len('S1248 carry-forward context for next thread'),
        )
        after = ChatConversation.objects.filter(
            conversation_id=self.existing_cid,
        ).count()
        self.assertEqual(after, before + 1)
        seeded_row = ChatConversation.objects.get(id=result['seed_message_id'])
        self.assertTrue(seeded_row.user_message.startswith('[SYSTEM SEED]'))
        self.assertEqual(seeded_row.source, 'pa')

    def test_seed_empty_content_rejected(self):
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'seed',
                'conversation_id': self.existing_cid,
                'content': '',
            },
        )
        self.assertIn('error', result)
        self.assertIn('non-empty content', result['error'])

    def test_seed_whitespace_only_content_rejected(self):
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'seed',
                'conversation_id': self.existing_cid,
                'content': '   \n\t  ',
            },
        )
        self.assertIn('error', result)
        self.assertIn('non-empty content', result['error'])

    def test_seed_unknown_conversation_rejected(self):
        result = _dispatch_session(
            self.alice.id,
            {
                'action': 'seed',
                'conversation_id': 'pa-does-not-exist',
                'content': 'whatever',
            },
        )
        self.assertIn('error', result)
        self.assertIn('No conversation found', result['error'])


class DispatcherRetiredThreadGateTests(TestCase):
    """Session 1248 — conversation_action_dispatcher session_active gate."""

    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )
        self.retired_cid = 'pa-test-gate-retired'
        self.active_cid = 'pa-test-gate-active'
        ChatConversation.objects.create(
            conversation_id=self.retired_cid,
            user_id=self.alice.id,
            session_title='retired',
            user_message='m',
            assistant_response='ack',
            session_active=False,
        )
        ChatConversation.objects.create(
            conversation_id=self.active_cid,
            user_id=self.alice.id,
            session_title='active',
            user_message='m',
            assistant_response='ack',
            session_active=True,
        )

    def test_dispatcher_blocks_retired_thread(self):
        dispatcher = ConversationActionDispatcher()
        result = dispatcher.dispatch_actions(
            conversation_id=self.retired_cid,
            decision_summary={'next_steps': ['ResearchAgent: do thing']},
            participants=['ResearchAgent'],
        )
        self.assertGreaterEqual(result.skipped_count, 1)
        self.assertEqual(result.dispatched_count, 0)
        self.assertTrue(any('Refusing to dispatch into retired thread' in e for e in result.errors))

    def test_dispatcher_allow_retired_context_bypasses_gate(self):
        dispatcher = ConversationActionDispatcher()
        # Stub parse_next_step + downstream dispatch — we just need to verify
        # the gate doesn't return early when allow_retired=True. The full
        # parse/validate/dispatch path is exercised by existing tests.
        with patch.object(dispatcher, 'parse_next_step', return_value=None):
            result = dispatcher.dispatch_actions(
                conversation_id=self.retired_cid,
                decision_summary={'next_steps': ['ResearchAgent: do thing']},
                participants=['ResearchAgent'],
                context={'allow_retired': True},
            )
        # Gate passed: errors no longer contain the gate's refusal message.
        self.assertFalse(any('Refusing to dispatch into retired thread' in e for e in result.errors))

    def test_dispatcher_active_thread_passes_gate(self):
        dispatcher = ConversationActionDispatcher()
        with patch.object(dispatcher, 'parse_next_step', return_value=None):
            result = dispatcher.dispatch_actions(
                conversation_id=self.active_cid,
                decision_summary={'next_steps': ['ResearchAgent: do thing']},
                participants=['ResearchAgent'],
            )
        self.assertFalse(any('Refusing to dispatch into retired thread' in e for e in result.errors))

    def test_dispatcher_unknown_conversation_passes_gate(self):
        # No ChatConversation rows for this id → gate sees has_any=False → no block.
        dispatcher = ConversationActionDispatcher()
        with patch.object(dispatcher, 'parse_next_step', return_value=None):
            result = dispatcher.dispatch_actions(
                conversation_id='pa-totally-unknown-id',
                decision_summary={'next_steps': ['ResearchAgent: do thing']},
                participants=['ResearchAgent'],
            )
        self.assertFalse(any('Refusing to dispatch into retired thread' in e for e in result.errors))


class SessionToolSchemaTests(TestCase):
    """Schema must advertise the three new actions to the LLM."""

    def test_schema_enum_includes_new_actions(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        session_schema = next(
            s for s in PA_TOOL_SCHEMAS if s.get('name') == 'session_tool'
        )
        enum_values = session_schema['parameters']['properties']['action']['enum']
        for new_action in ('retire', 'set_active', 'seed'):
            self.assertIn(new_action, enum_values)

    def test_schema_declares_force_and_content_params(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS

        session_schema = next(
            s for s in PA_TOOL_SCHEMAS if s.get('name') == 'session_tool'
        )
        props = session_schema['parameters']['properties']
        self.assertIn('force', props)
        self.assertEqual(props['force']['type'], 'boolean')
        self.assertIn('content', props)
        self.assertEqual(props['content']['type'], 'string')

    def test_invalid_action_lists_new_actions_in_error(self):
        alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )
        result = _dispatch_session(
            alice.id, {'action': 'totally_invalid'},
        )
        self.assertIn('error', result)
        for new_action in ('retire', 'set_active', 'seed'):
            self.assertIn(new_action, result['error'])
