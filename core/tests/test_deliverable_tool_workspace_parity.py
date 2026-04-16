"""Session 1092: Regression guard for deliverable_tool list/detail workspace parity.

Bug history: `deliverable_tool.detail` in core/services/td_handlers_agents.py
omitted workspace_id and workspace__name from its return projection. Since
_sanitize_deliverable computes `is_orphan = d.get('workspace_id') is None`,
detail always reported is_orphan=true even for workspace-linked deliverables.
The list path was correct, so consumers comparing the two surfaces saw
contradictory orphan markers and broke the workspace-flow-canary flow.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


class TestDeliverableToolWorkspaceParity(TestCase):
    """list and detail must agree on workspace_id and is_orphan."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='canary-test',
            email='canary-test@example.com',
            password='x',
        )
        self.workspace = ProjectWorkspace.objects.create(
            name='canary-test-ws',
            user=self.user,
        )
        self.assigned = Deliverable.objects.create(
            user=self.user,
            workspace=self.workspace,
            title='Assigned canary deliverable',
            content='body',
            agent_name='TestAgent',
            deliverable_type='document',
        )
        self.orphan = Deliverable.objects.create(
            user=self.user,
            workspace=None,
            title='Orphan canary deliverable',
            content='body',
            agent_name='TestAgent',
            deliverable_type='document',
        )
        self.handler = ToolDispatcher()._tool_handlers['deliverable_tool']

    def _detail(self, did):
        return self.handler(
            'deliverable_tool',
            {'action': 'detail', 'id': str(did)},
            self.user.id,
            'parity-test',
        )

    def test_assigned_detail_returns_workspace_fields(self):
        res = self._detail(self.assigned.id)
        self.assertEqual(str(res.get('workspace_id')), str(self.workspace.id))
        self.assertEqual(res.get('workspace__name'), 'canary-test-ws')
        self.assertEqual(res.get('workspace_name'), 'canary-test-ws')
        self.assertFalse(res.get('is_orphan'))

    def test_orphan_detail_marks_is_orphan_true(self):
        res = self._detail(self.orphan.id)
        self.assertIsNone(res.get('workspace_id'))
        self.assertIsNone(res.get('workspace__name'))
        self.assertTrue(res.get('is_orphan'))

    def test_list_and_detail_agree_on_workspace_and_orphan(self):
        list_res = self.handler(
            'deliverable_tool',
            {'action': 'list', 'workspace_id': str(self.workspace.id), 'limit': 10},
            self.user.id,
            'parity-test-list',
        )
        # list path returns id as UUID (from .values()); detail returns it as
        # str. Compare via str() on both sides.
        list_match = next(
            (it for it in list_res.get('items', []) if str(it.get('id')) == str(self.assigned.id)),
            None,
        )
        self.assertIsNotNone(
            list_match,
            f'Assigned deliverable {self.assigned.id} should be in list of '
            f'{len(list_res.get("items", []))} items: '
            f'{[str(i.get("id")) for i in list_res.get("items", [])]}',
        )

        detail_res = self._detail(self.assigned.id)

        # Parity assertions — these are the ones the canary actually needs.
        self.assertEqual(
            str(list_match.get('workspace_id')),
            str(detail_res.get('workspace_id')),
            'list and detail must report the same workspace_id',
        )
        self.assertEqual(
            list_match.get('is_orphan'),
            detail_res.get('is_orphan'),
            'list and detail must agree on is_orphan',
        )
        self.assertEqual(
            list_match.get('workspace__name'),
            detail_res.get('workspace__name'),
            'list and detail must agree on workspace__name',
        )
