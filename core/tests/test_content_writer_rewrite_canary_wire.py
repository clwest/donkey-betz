"""
Session 1098 canary wire-up — ContentWriterAgent._execute_rewrite.

Covers the caller-side plumbing that makes the canary fire for real:

    1. context['append_to_deliverable_id'] threads from execute() →
       _execute_rewrite() param → _save_to_deliverable(append_to_deliverable_id=...)
    2. When the param is None (normal rewrite), no save call happens
       (preserves pre-canary behavior).
    3. If _save_to_deliverable raises inside the canary save block,
       the rewrite still returns successfully (canary is best-effort).

Run::

    python manage.py test core.tests.test_content_writer_rewrite_canary_wire -v2
"""

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.agents.content_writer_agent import ContentWriterAgent


User = get_user_model()


class ContentWriterRewriteCanaryWireTests(TestCase):
    """Verify the wire — does NOT exercise the gate (that's the
    canary-gate test suite). Here we confirm the param threads through
    and _save_to_deliverable gets called with the right kwargs when the
    caller opts in."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='cw-canary-wire',
            email='cw-canary-wire@example.com',
            password='x',
        )

    def _make_agent(self):
        return ContentWriterAgent(user=self.user)

    def _fake_llm_response(self, text='REWRITTEN ARTICLE TEXT\n\nBody...'):
        """Build an OpenAI-shaped response object for patching."""
        msg = mock.Mock()
        msg.content = text
        choice = mock.Mock()
        choice.message = msg
        choice.finish_reason = 'stop'
        resp = mock.Mock()
        resp.choices = [choice]
        resp.usage = mock.Mock(prompt_tokens=100, completion_tokens=200)
        return resp

    def test_append_id_present_calls_save_with_correct_kwargs(self):
        """Caller passes append_to_deliverable_id=X + expected_initiative_id=Y
        → _save_to_deliverable gets both, plus append_chunk_index=0."""
        agent = self._make_agent()
        fake_resp = self._fake_llm_response('REWRITTEN CONTENT')

        with mock.patch(
            'core.services.openai_client_factory.get_openai_client'
        ) as mocked_factory, mock.patch.object(
            ContentWriterAgent, '_save_to_deliverable'
        ) as mocked_save:
            mocked_factory.return_value.chat.completions.create.return_value = fake_resp

            result = agent._execute_rewrite(
                original_draft='draft text',
                review_feedback='feedback',
                workspace_brief={'topic': 'T', 'audience': 'A', 'tone': 'neutral'},
                task='rewrite the thing',
                start_time=0.0,
                append_to_deliverable_id='deliv-abc',
                expected_initiative_id='init-xyz',
            )

        self.assertTrue(result.success)
        mocked_save.assert_called_once()
        _, kwargs = mocked_save.call_args
        self.assertEqual(kwargs.get('append_to_deliverable_id'), 'deliv-abc')
        self.assertEqual(kwargs.get('expected_initiative_id'), 'init-xyz')
        self.assertEqual(kwargs.get('append_chunk_index'), 0)

    def test_no_append_id_skips_save_call(self):
        """No append_to_deliverable_id → no save call inside rewrite.
        Preserves pre-canary behavior where the pipeline caller handles
        persistence."""
        agent = self._make_agent()
        fake_resp = self._fake_llm_response('REWRITE')

        with mock.patch(
            'core.services.openai_client_factory.get_openai_client'
        ) as mocked_factory, mock.patch.object(
            ContentWriterAgent, '_save_to_deliverable'
        ) as mocked_save:
            mocked_factory.return_value.chat.completions.create.return_value = fake_resp

            result = agent._execute_rewrite(
                original_draft='draft',
                review_feedback='feedback',
                workspace_brief={'topic': 'X', 'audience': 'Y', 'tone': 'neutral'},
                task='rewrite',
                start_time=0.0,
                # no append_to_deliverable_id — default path
            )

        self.assertTrue(result.success)
        mocked_save.assert_not_called()

    def test_save_failure_does_not_fail_rewrite(self):
        """Canary save is best-effort. If _save_to_deliverable raises,
        the rewrite still returns success with the rewritten text."""
        agent = self._make_agent()
        fake_resp = self._fake_llm_response('REWRITTEN')

        with mock.patch(
            'core.services.openai_client_factory.get_openai_client'
        ) as mocked_factory, mock.patch.object(
            ContentWriterAgent, '_save_to_deliverable',
            side_effect=RuntimeError('simulated save failure'),
        ):
            mocked_factory.return_value.chat.completions.create.return_value = fake_resp

            result = agent._execute_rewrite(
                original_draft='draft',
                review_feedback='feedback',
                workspace_brief={'topic': 'X', 'audience': 'Y', 'tone': 'neutral'},
                task='rewrite',
                start_time=0.0,
                append_to_deliverable_id='deliv-fail',
            )

        self.assertTrue(
            result.success,
            'rewrite must return success even when canary save raises',
        )
        # The rewritten text is still returned to the caller.
        self.assertIn('REWRITTEN', result.data['content']['full_text'])
