"""
Session 1098 PR-A — ContentDeliberationRunner._rewrite_draft context keys.

Pre-PR bug: _rewrite_draft stuffed draft + feedback into task_str only,
so ContentWriterAgent's REWRITE MODE detector (which keys off
context['review_feedback'] + context['original_draft']) never fired.
Rewrites silently fell through to the generic writer path.

PR-A asserts both keys are present in the context dict passed to
ContentWriterAgent.execute().

Run::

    python manage.py test core.tests.test_content_deliberation_rewrite_context -v2
"""

from unittest import mock

from django.test import SimpleTestCase

from core.services.content_deliberation_runner import ContentDeliberationRunner


class RewriteDraftContextKeysTests(SimpleTestCase):

    def _make_review_results(self):
        return [{
            'verdict': 'FAIL',
            'required_changes': ['Tighten lede', 'Add a source for claim 3'],
        }]

    def test_rewrite_sets_original_draft_and_review_feedback(self):
        """_rewrite_draft must pass original_draft + review_feedback as
        explicit context keys so ContentWriterAgent enters REWRITE MODE."""
        runner = ContentDeliberationRunner()
        fake_result = mock.Mock()
        fake_result.success = True
        fake_result.data = {'content': {'full_text': 'REWRITE OUTPUT', 'word_count': 10}}

        with mock.patch(
            'core.agents.content_writer_agent.ContentWriterAgent'
        ) as MockAgent:
            MockAgent.return_value.execute.return_value = fake_result

            result = runner._rewrite_draft(
                topic='canary topic',
                draft_text='original blog draft text here',
                review_results=self._make_review_results(),
                claims_pack=None,
                voice='professional',
            )

        self.assertIsNotNone(result)
        _, call_kwargs = MockAgent.return_value.execute.call_args
        context = call_kwargs['context']
        self.assertEqual(context['original_draft'], 'original blog draft text here')
        self.assertIn('Tighten lede', context['review_feedback'])
        self.assertIn('Add a source for claim 3', context['review_feedback'])
        self.assertEqual(context['content_type'], 'blog_post')
        self.assertEqual(context['topic'], 'canary topic')

    def test_rewrite_returns_none_when_no_feedback(self):
        """Sanity: no required_changes → nothing to rewrite."""
        runner = ContentDeliberationRunner()
        result = runner._rewrite_draft(
            topic='x',
            draft_text='draft',
            review_results=[{'verdict': 'PASS', 'required_changes': []}],
            claims_pack=None,
            voice=None,
        )
        self.assertIsNone(result)
