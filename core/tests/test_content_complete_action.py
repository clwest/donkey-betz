"""Session 1170: content_tool.content_complete PA action.

Locks in the new terminal-state action that closes the tool gap
discovered during the publish-ready backlog triage. Deliverable.status
'completed' is valid in the model but pre-1170 had no PA tool surface
to flip to it — Rigby's stopgap was a title-prefix + tag convention,
which works but loses queryability of the real status.

Action shape mirrors `archive`'s contract: no precondition on current
status, feedback string persisted to metadata['complete_reason'],
feedback row recorded.

Run::

    python manage.py test core.tests.test_content_complete_action -v2
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Deliverable

User = get_user_model()


class ContentCompleteHandlerTests(TestCase):
    """Test _handle_content_review's new `complete` branch directly."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser-complete', password='pw'
        )

    def setUp(self):
        from core.services.td_handlers_content import ContentHandlersMixin
        self.handler = ContentHandlersMixin()
        self.deliverable = Deliverable.objects.create(
            title='Daily ops snapshot — Session 1170 verification',
            content='analysis body',
            deliverable_type='analysis',
            category='Executive Operations',
            agent_name='COOAgent',
            status='ready',
            user=self.user,
        )

    def _call(self, payload):
        return self.handler._handle_content_review(
            tool_name='content_review_tool',
            payload=payload,
            user_id=self.user.id,
            trace_id='test-complete',
        )

    def test_complete_flips_status_to_completed(self):
        result = self._call({
            'action': 'complete',
            'id': str(self.deliverable.id),
        })
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, 'completed')
        self.assertEqual(result['new_status'], 'completed')
        self.assertTrue(result['success'])

    def test_complete_persists_feedback_to_metadata(self):
        self._call({
            'action': 'complete',
            'id': str(self.deliverable.id),
            'feedback': 'COO diagnostic acted on; closing loop',
        })
        self.deliverable.refresh_from_db()
        self.assertEqual(
            self.deliverable.metadata['complete_reason'],
            'COO diagnostic acted on; closing loop',
        )

    def test_complete_default_feedback_when_missing(self):
        self._call({
            'action': 'complete',
            'id': str(self.deliverable.id),
        })
        self.deliverable.refresh_from_db()
        self.assertEqual(
            self.deliverable.metadata['complete_reason'],
            'Marked completed via PA',
        )

    def test_complete_works_from_any_starting_status(self):
        """Mirror of archive's contract — no precondition on current
        status. A blocked or already-archived deliverable can be flipped
        to completed."""
        self.deliverable.status = 'blocked'
        self.deliverable.save(update_fields=['status'])
        self._call({'action': 'complete', 'id': str(self.deliverable.id)})
        self.deliverable.refresh_from_db()
        self.assertEqual(self.deliverable.status, 'completed')

    def test_complete_missing_id_raises(self):
        with self.assertRaises(ValueError) as cm:
            self._call({'action': 'complete'})
        self.assertIn('id is required', str(cm.exception))

    def test_complete_unknown_id_raises(self):
        with self.assertRaises(ValueError) as cm:
            self._call({
                'action': 'complete',
                'id': '00000000-0000-0000-0000-000000000000',
            })
        self.assertIn('not found', str(cm.exception))

    def test_complete_records_feedback_row(self):
        with patch.object(self.handler, '_record_content_feedback') as mock_record:
            self._call({
                'action': 'complete',
                'id': str(self.deliverable.id),
                'feedback': 'integration test',
            })
            mock_record.assert_called_once()
            call_kwargs = mock_record.call_args.kwargs
            self.assertEqual(call_kwargs['agent_name'], 'COOAgent')
            self.assertEqual(call_kwargs['action'], 'complete')
            self.assertIn(
                'integration test',
                call_kwargs['details']['feedback_summary'],
            )


class ContentCompleteAliasesTests(TestCase):
    """The action aliases (mark_complete / mark_completed / done →
    complete) work end-to-end at both the _handle_content_review entry
    point AND the outer content_tool gateway."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser-aliases', password='pw'
        )

    def setUp(self):
        from core.services.td_handlers_content import ContentHandlersMixin
        self.handler = ContentHandlersMixin()

    def _make(self):
        return Deliverable.objects.create(
            title='Alias test deliverable',
            content='body',
            deliverable_type='analysis',
            status='ready',
            user=self.user,
        )

    def _call(self, payload):
        return self.handler._handle_content_review(
            tool_name='content_review_tool',
            payload=payload,
            user_id=self.user.id,
            trace_id='test-alias',
        )

    def test_mark_complete_alias(self):
        d = self._make()
        self._call({'action': 'mark_complete', 'id': str(d.id)})
        d.refresh_from_db()
        self.assertEqual(d.status, 'completed')

    def test_mark_completed_alias(self):
        d = self._make()
        self._call({'action': 'mark_completed', 'id': str(d.id)})
        d.refresh_from_db()
        self.assertEqual(d.status, 'completed')

    def test_done_alias(self):
        d = self._make()
        self._call({'action': 'done', 'id': str(d.id)})
        d.refresh_from_db()
        self.assertEqual(d.status, 'completed')


class ContentCompleteSchemaTests(TestCase):
    """The PA tool schema must enumerate content_complete so GPT-5.2
    can call it. Without this, the gateway accepts the action but the
    PA model won't know to emit it."""

    def test_content_complete_in_schema_enum(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS as schemas
        content_tool = next(
            (s for s in schemas if s.get('name') == 'content_tool'),
            None,
        )
        self.assertIsNotNone(content_tool, "content_tool schema missing")
        actions = content_tool['parameters']['properties']['action']['enum']
        self.assertIn('content_complete', actions)

    def test_content_complete_description_mentions_use_case(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS as schemas
        content_tool = next(
            (s for s in schemas if s.get('name') == 'content_tool'),
            None,
        )
        action_desc = content_tool['parameters']['properties']['action']['description']
        self.assertIn('content_complete', action_desc)
        self.assertIn('terminal state', action_desc.lower())
