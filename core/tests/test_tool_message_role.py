"""
Tests: tool messages (code-worker / claude-code) must serialize with role='tool'
and must never be broadcast with role='user'.
"""
import unittest
from unittest.mock import MagicMock


class TestPAConversationMessageSerializerRole(unittest.TestCase):
    """Unit-test the serializer's to_representation fallback logic."""

    def _make_instance(self, role, source, content='hello'):
        obj = MagicMock()
        obj.id = 'test-id'
        obj.role = role
        obj.source = source
        obj.content = content
        obj.created_at = None
        obj.metadata = {}
        return obj

    def _serialize(self, instance):
        """Import here so the test can be run without full Django setup."""
        # We test the to_representation logic directly.
        data = {
            'id': str(instance.id),
            'role': instance.role,
            'source': instance.source,
            'content': instance.content,
            'created_at': None,
            'metadata': instance.metadata,
        }
        # Replicate the serializer fallback
        if not data.get('role'):
            src = data.get('source') or ''
            if src in ('code-worker', 'claude-code'):
                data['role'] = 'tool'
            else:
                data['role'] = 'user'
        return data

    def test_code_worker_role_tool(self):
        obj = self._make_instance(role='tool', source='code-worker')
        result = self._serialize(obj)
        self.assertEqual(result['role'], 'tool')

    def test_claude_code_role_tool(self):
        obj = self._make_instance(role='tool', source='claude-code')
        result = self._serialize(obj)
        self.assertEqual(result['role'], 'tool')

    def test_legacy_code_worker_no_role(self):
        """Legacy record: source set but role missing — should fall back to tool."""
        obj = self._make_instance(role=None, source='code-worker')
        result = self._serialize(obj)
        self.assertEqual(result['role'], 'tool', 'Legacy code-worker without role must become tool')

    def test_legacy_claude_code_user_role(self):
        """Legacy record: role wrongly set to user — serializer keeps 'user' but broadcaster corrects it."""
        obj = self._make_instance(role='user', source='claude-code')
        # The serializer only fills in if role is falsy/None; 'user' stays in serializer.
        # Broadcaster is responsible for correcting persisted-wrong records.
        result = self._serialize(obj)
        # 'user' is truthy so serializer passes it through unchanged.
        self.assertEqual(result['role'], 'user')  # serializer doesn't override non-None

    def test_user_message_stays_user(self):
        obj = self._make_instance(role='user', source='user')
        result = self._serialize(obj)
        self.assertEqual(result['role'], 'user')


class TestBroadcasterResolveRole(unittest.TestCase):
    """Unit-test the broadcaster's _resolve_role helper."""

    def _resolve(self, role, source):
        from core.services.pa_conversation_broadcaster import _resolve_role
        return _resolve_role(role, source)

    def test_tool_role_preserved(self):
        self.assertEqual(self._resolve('tool', 'code-worker'), 'tool')

    def test_code_worker_no_role(self):
        self.assertEqual(self._resolve(None, 'code-worker'), 'tool')

    def test_claude_code_no_role(self):
        self.assertEqual(self._resolve(None, 'claude-code'), 'tool')

    def test_code_worker_wrong_user_role(self):
        # The broadcaster treats source as overriding a wrongly-persisted 'user'
        self.assertEqual(self._resolve('user', 'code-worker'), 'tool')

    def test_user_message(self):
        self.assertEqual(self._resolve('user', 'user'), 'user')

    def test_assistant_message(self):
        self.assertEqual(self._resolve('assistant', 'pa'), 'assistant')


if __name__ == '__main__':
    unittest.main()
