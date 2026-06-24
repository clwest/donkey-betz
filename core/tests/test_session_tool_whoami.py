"""Session 1226 — session_tool.whoami tests.

Closes the ownership-verification gap Rigby filed at Session 1225 close.
Verifies whoami returns identity + conversation-owner-match facts.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import ChatConversation
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _dispatch_whoami(user_id, payload):
    """Invoke session_tool.whoami via the dispatcher entry point."""
    dispatcher = ToolDispatcher()
    return dispatcher._handle_session(  # type: ignore[attr-defined]
        tool_name='session_tool',
        payload={'action': 'whoami', **payload},
        user_id=user_id,
        trace_id='test-whoami',
    )


class SessionToolWhoamiTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice', password='x', email='alice@example.com',
        )
        self.bob = User.objects.create_user(
            username='bob', password='x', email='bob@example.com',
        )
        # Alice owns this conversation
        self.alice_conv_id = 'pa-test-alice-1'
        ChatConversation.objects.create(
            conversation_id=self.alice_conv_id,
            user_id=self.alice.id,
            session_title='Alice thread',
            user_message='hi',
            assistant_response='hello',
        )

    def test_whoami_returns_identity(self):
        result = _dispatch_whoami(self.alice.id, {})
        self.assertEqual(result['action'], 'whoami')
        self.assertEqual(result['user_id'], self.alice.id)
        self.assertEqual(result['username'], 'alice')
        self.assertEqual(result['email'], 'alice@example.com')
        self.assertFalse(result['is_staff'])
        self.assertFalse(result['is_superuser'])

    def test_whoami_owner_match_true(self):
        result = _dispatch_whoami(
            self.alice.id, {'conversation_id': self.alice_conv_id},
        )
        self.assertTrue(result['conversation_owner_match'])
        self.assertEqual(result['conversation_owner_username'], 'alice')
        self.assertEqual(result['conversation_owner_user_id'], self.alice.id)

    def test_whoami_owner_match_false(self):
        # Bob asks whoami about Alice's conversation → match=False but with full owner info
        result = _dispatch_whoami(
            self.bob.id, {'conversation_id': self.alice_conv_id},
        )
        self.assertEqual(result['username'], 'bob')
        self.assertFalse(result['conversation_owner_match'])
        self.assertEqual(result['conversation_owner_username'], 'alice')
        self.assertEqual(result['conversation_owner_user_id'], self.alice.id)

    def test_whoami_unknown_conversation(self):
        # Conversation that doesn't exist → owner fields are None, no crash
        result = _dispatch_whoami(
            self.alice.id, {'conversation_id': 'pa-never-existed'},
        )
        self.assertEqual(result['username'], 'alice')
        self.assertIsNone(result['conversation_owner_match'])
        self.assertIsNone(result['conversation_owner_username'])
        self.assertIsNone(result['conversation_owner_user_id'])

    def test_whoami_no_conversation_id(self):
        # No conversation_id supplied and no _current_conversation_id on dispatcher
        result = _dispatch_whoami(self.alice.id, {})
        self.assertEqual(result['username'], 'alice')
        # Owner fields are None because there's nothing to compare to
        self.assertIsNone(result['conversation_owner_match'])
        self.assertEqual(result['conversation_id'], '')

    def test_whoami_unknown_user_id(self):
        # auth corruption case: user_id doesn't exist in auth_user
        result = _dispatch_whoami(999999, {})
        self.assertEqual(result['action'], 'whoami')
        self.assertIn('error', result)
        self.assertEqual(result['authenticated_user_id'], 999999)
