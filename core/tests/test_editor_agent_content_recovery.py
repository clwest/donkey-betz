"""Session 1092: EditorAgent caller-bug regression tests.

CTOAgent's platform analysis surfaced 9 EditorAgent failures in 24h, all
"No content provided. Include 'blog_id' or 'content' in context."

EditorAgent's job is to EDIT, not generate — so failing fast when the
caller doesn't pass content is the CORRECT behavior. The fix lives in
the callers, not the agent. The only minor recovery we add: parse a
blog_id buried in the task text, since real callers were doing
"Enhance the blog (blog_id=<uuid>) ..." and expecting the agent to
parse it.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.agents.editor_agent import EditorAgent

User = get_user_model()


class TestEditorAgentRequiresContent(TestCase):
    """EditorAgent's job is editing — it must fail loudly when caller
    doesn't pass content. The dispatcher's Session 1090 workspace-gather
    fallback is the right place for caller-convenience defaults; the
    agent itself should not hide caller bugs by generating from thin air.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='editor-test', email='editor-test@example.com', password='x'
        )
        self.agent = EditorAgent(user=self.user)

    def test_empty_context_returns_no_content_error(self):
        """No blog_id, no content, no recovery path → fail loudly."""
        result = self.agent.execute(
            task='Synthesize the Platform Audit, CTO Analysis, and COO Analysis '
                 'into a publish-ready Executive Brief.',
            context={},
            scifi_context={},
            spider_context={},
        )
        self.assertFalse(result.success)
        self.assertIn('No content provided', result.error or '')

    def test_blog_id_recovered_from_task_text(self):
        """Caller convenience: 'blog_id=<uuid>' in task text gets parsed.
        Resulting lookup will fail (the test uuid doesn't exist), but the
        agent should advance past the 'No content provided' gate to the
        'Blog not found' error — proving the parser ran.
        """
        result = self.agent.execute(
            task='Enhance the blog (blog_id=12345678-1234-1234-1234-123456789abc) structure',
            context={},
            scifi_context={},
            spider_context={},
        )
        self.assertFalse(result.success)
        # Either "Blog not found" (id parsed, lookup failed) — both prove
        # we got past the original "No content provided" gate.
        self.assertNotIn('No content provided', result.error or '')
