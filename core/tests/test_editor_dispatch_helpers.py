"""Session 1092: Tests for the shared editor_dispatch_helpers module.

Both the PA tool dispatcher and the conversation action dispatcher now
use this shared gatherer. Lock in the behavior so the LLM-driven
"EditorAgent: synthesize the briefs" pattern doesn't regress to 9
"No content provided" failures per day.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.editor_dispatch_helpers import (
    gather_workspace_content_for_editor,
)

User = get_user_model()


class TestGatherWorkspaceContentForEditor(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='editor-gather-test',
            email='editor-gather-test@example.com',
            password='x',
        )
        self.workspace = ProjectWorkspace.objects.create(
            name='editor-gather-ws', user=self.user, is_active=True,
        )

    def _make_deliverable(self, title, body, **kwargs):
        return Deliverable.objects.create(
            user=self.user,
            workspace=self.workspace,
            title=title,
            content=body,
            agent_name=kwargs.get('agent_name', 'CTOAgent'),
            deliverable_type=kwargs.get('deliverable_type', 'analysis'),
        )

    def test_gathers_workspace_deliverables_into_section_dict(self):
        self._make_deliverable('Source 1', 'Body 1 ' * 30)
        self._make_deliverable('Source 2', 'Body 2 ' * 30)
        self._make_deliverable('Source 3', 'Body 3 ' * 30)

        gathered = gather_workspace_content_for_editor(
            workspace_id=str(self.workspace.id),
            task_text='Synthesize sources into a brief',
        )
        self.assertIsNotNone(gathered)
        self.assertIn('Executive Brief', gathered['title'])
        self.assertEqual(len(gathered['sections']), 3)
        # Most-recent first per .order_by('-created_at')
        self.assertEqual(gathered['sections'][0]['heading'], 'Source 3')

    def test_excludes_editor_self_output(self):
        """Don't feed EditorAgent's own prior outputs back to it."""
        self._make_deliverable('Source 1', 'real content ' * 30)
        self._make_deliverable(
            'EditorAgent: enhanced version', 'editor output ' * 30,
        )
        gathered = gather_workspace_content_for_editor(
            workspace_id=str(self.workspace.id),
            task_text='synthesize',
        )
        self.assertIsNotNone(gathered)
        headings = [s['heading'] for s in gathered['sections']]
        self.assertIn('Source 1', headings)
        self.assertFalse(any(h.startswith('EditorAgent:') for h in headings))

    def test_excludes_prior_blog_posts(self):
        """Don't feed blog-post deliverables either — keeps Editor focused on
        upstream artifacts (briefs, analyses) instead of looping."""
        self._make_deliverable('Source A', 'real ' * 30)
        self._make_deliverable(
            'blog_post: Q4 review', 'old blog ' * 30, deliverable_type='blog_post',
        )
        gathered = gather_workspace_content_for_editor(
            workspace_id=str(self.workspace.id),
            task_text='synthesize',
        )
        headings = [s['heading'] for s in gathered['sections']]
        self.assertIn('Source A', headings)
        self.assertFalse(any('blog_post' in h for h in headings))

    def test_returns_none_for_empty_or_missing_workspace(self):
        empty_ws = ProjectWorkspace.objects.create(
            name='empty-gather-ws', user=self.user, is_active=False,
        )
        self.assertIsNone(
            gather_workspace_content_for_editor(
                workspace_id=str(empty_ws.id), task_text='x',
            )
        )
        self.assertIsNone(
            gather_workspace_content_for_editor(
                workspace_id=None, task_text='x',
            )
        )

    def test_skips_empty_content_deliverables(self):
        """Deliverables with empty content shouldn't show up as zero-byte
        sections that just inflate the section count."""
        self._make_deliverable('Empty source', '')
        self._make_deliverable('Whitespace source', '   \n\n   ')
        self._make_deliverable('Real source', 'meaningful body ' * 30)
        gathered = gather_workspace_content_for_editor(
            workspace_id=str(self.workspace.id),
            task_text='synthesize',
        )
        self.assertIsNotNone(gathered)
        self.assertEqual(len(gathered['sections']), 1)
        self.assertEqual(gathered['sections'][0]['heading'], 'Real source')

    def test_caps_section_count_and_per_section_length(self):
        # Make 10 deliverables — should be capped at 6
        for i in range(10):
            self._make_deliverable(f'D{i}', 'X' * 5000)
        gathered = gather_workspace_content_for_editor(
            workspace_id=str(self.workspace.id),
            task_text='synthesize',
        )
        self.assertIsNotNone(gathered)
        self.assertLessEqual(len(gathered['sections']), 6)
        for s in gathered['sections']:
            self.assertLessEqual(len(s['content']), 3000)
