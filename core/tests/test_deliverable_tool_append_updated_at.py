"""Session 1231 P3 — deliverable_tool.append must bump updated_at.

Closes the audit-trail gap captured in tracking deliverable
``61f4312b-9f54-447e-abf2-641e082386ba`` (Session 1230 P2 discovery).

Django's ``auto_now=True`` is silenced when ``save(update_fields=[...])``
is called without the field listed. The append and update-content
handlers previously saved only ``['content', 'preview_content']``,
which meant `updated_at` never advanced — breaking the canonical
last-touched signal for governance metrics, dedupe windows, and
content-freshness queries.

Run::

    python manage.py test core.tests.test_deliverable_tool_append_updated_at -v2
"""

import time
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class DeliverableToolAppendUpdatedAtTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'p3-test-{uuid.uuid4().hex[:8]}',
            email='p3@example.com',
            password='x',
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='P3 Test Workspace',
            allow_autonomous_writes=True,
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()
        self.trace_id = str(uuid.uuid4())

    def _make_deliverable(self, **overrides):
        defaults = dict(
            title='P3 baseline deliverable',
            content='# Initial content\n\nBody text.',
            agent_name='TestAgent',
            category='Test',
            deliverable_type='document',
            user=self.user,
            workspace_id=str(self.workspace.id),
        )
        defaults.update(overrides)
        return Deliverable.objects.create(**defaults)

    # ── append action ──────────────────────────────────────────────────

    def test_append_action_bumps_updated_at(self):
        d = self._make_deliverable()
        before = d.updated_at
        time.sleep(0.05)
        self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'append',
                'id': str(d.id),
                'content': '\n[appended chunk]',
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        d.refresh_from_db()
        self.assertGreater(
            d.updated_at, before,
            msg='append must bump updated_at (auto_now=True is silenced '
                'when omitted from update_fields)',
        )
        self.assertIn('[appended chunk]', d.content)

    # ── update action: append/prepend sub-modes ────────────────────────

    def test_update_action_append_subform_bumps_updated_at(self):
        d = self._make_deliverable()
        before = d.updated_at
        time.sleep(0.05)
        self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'update',
                'id': str(d.id),
                'append': '[via update.append]',
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        d.refresh_from_db()
        self.assertGreater(d.updated_at, before)
        self.assertIn('[via update.append]', d.content)

    def test_update_action_prepend_subform_bumps_updated_at(self):
        d = self._make_deliverable()
        before = d.updated_at
        time.sleep(0.05)
        self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'update',
                'id': str(d.id),
                'prepend': '[via update.prepend]',
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        d.refresh_from_db()
        self.assertGreater(d.updated_at, before)
        self.assertTrue(d.content.startswith('[via update.prepend]'))

    def test_update_action_replace_content_bumps_updated_at(self):
        d = self._make_deliverable()
        before = d.updated_at
        time.sleep(0.05)
        self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'update',
                'id': str(d.id),
                'content': 'Replaced body.',
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        d.refresh_from_db()
        self.assertGreater(d.updated_at, before)
        self.assertEqual(d.content, 'Replaced body.')

    # ── source-level guard: regression sentinel ────────────────────────

    def test_source_level_guard_append_handler_lists_updated_at(self):
        """Lock the wiring so a future revert of the fix is caught at
        test-time rather than via downstream analytics drift."""
        import re
        from pathlib import Path
        src = Path('core/services/td_handlers_agents.py').read_text()
        # The dedicated append action's save call must include updated_at.
        match = re.search(
            r"obj\.save\(update_fields=\['content', 'preview_content', 'updated_at'\]\)",
            src,
        )
        self.assertIsNotNone(
            match,
            msg='deliverable_tool.append handler must save updated_at '
                'alongside content + preview_content. Reverting this '
                'reintroduces the audit-trail gap from tracking '
                'deliverable 61f4312b-….',
        )
        # The update action's append/prepend + replace branches must
        # also extend update_fields with updated_at.
        extends = re.findall(
            r"update_fields\.extend\(\['content', 'preview_content', 'updated_at'\]\)",
            src,
        )
        self.assertGreaterEqual(
            len(extends), 2,
            msg='deliverable_tool.update content-mutating branches '
                '(append/prepend sub-mode AND replace sub-mode) must '
                'each include updated_at in extend().',
        )
