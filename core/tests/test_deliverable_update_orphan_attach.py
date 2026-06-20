"""
Session 1168 — bug #2 regression: orphan newsletter attach via update.
=======================================================================

Bug #2 from chris-personal Known Bugs Queue (deliverable f92ab8bb):
``deliverable_tool.update(id=<orphan>, workspace_id=<target>)`` failed
with "Deliverable <id> not found" because payload.workspace_id was
double-used as both (a) the scope filter on base_qs and (b) the new
value to assign. For orphan deliverables (workspace_id=NULL), the
scope filter excluded them before the workspace-assignment logic ever
ran.

These tests cover:

    1. Orphan deliverable can be attached to a workspace via update
       (the exact bug repro).
    2. A deliverable can be moved from workspace A to workspace B
       via update (same code path, different starting state).
    3. Non-staff users can still NOT update other users' deliverables
       (security regression check).
    4. Update without workspace_id still uses the original base_qs
       behavior (no behavior change for non-attach updates).

Run::

    python manage.py test core.tests.test_deliverable_update_orphan_attach -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class OrphanNewsletterAttachTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'attach-test-{uuid.uuid4().hex[:8]}',
            email='attach@example.com',
            password='x',
            is_superuser=True,
        )
        cls.other_user = User.objects.create_user(
            username=f'attach-other-{uuid.uuid4().hex[:8]}',
            email='attach-other@example.com',
            password='x',
            is_superuser=False,
            is_staff=False,
        )
        cls.workspace_a = ProjectWorkspace.objects.create(
            user=cls.user, name='Workspace A',
            allow_autonomous_writes=True,
        )
        cls.workspace_b = ProjectWorkspace.objects.create(
            user=cls.user, name='Workspace B',
            allow_autonomous_writes=True,
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()
        self.trace_id = str(uuid.uuid4())

    def _make_orphan(self, **overrides):
        defaults = dict(
            title='Orphan newsletter',
            content='# Newsletter content\n\nSubstantial body. ' * 20,
            agent_name='NewsletterTool',
            category='Newsletter',
            deliverable_type='document',
            user=self.user,
            workspace_id=None,  # ← orphan
        )
        defaults.update(overrides)
        return Deliverable.objects.create(**defaults)

    # ── Bug #2 repro: attach orphan to workspace ────────────────────────

    def test_attach_orphan_to_workspace_via_update(self):
        """The exact bug repro: deliverable_tool.update(id=<orphan>,
        workspace_id=<target>) used to fail with 'not found'. Should
        now succeed and attach the orphan to the target workspace."""
        orphan = self._make_orphan()
        self.assertIsNone(orphan.workspace_id)

        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'update',
                'id': str(orphan.id),
                'workspace_id': str(self.workspace_a.id),
            },
            self.user.id,
            self.trace_id,
        )
        self.assertIsInstance(result, dict)
        self.assertNotIn('error', result, msg=f'expected success, got {result}')
        self.assertEqual(result['action'], 'update')
        self.assertEqual(result['id'], str(orphan.id))
        self.assertIn('workspace', result.get('updated_fields', []))

        orphan.refresh_from_db()
        self.assertEqual(str(orphan.workspace_id), str(self.workspace_a.id))

    def test_move_deliverable_between_workspaces_via_update(self):
        """Same code path: a deliverable currently in workspace A can be
        moved to workspace B via update(workspace_id=B). Pre-fix this
        also failed because base_qs filtered to A so the deliverable
        wasn't findable when payload said B."""
        d = self._make_orphan(workspace_id=str(self.workspace_a.id))
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'update',
                'id': str(d.id),
                'workspace_id': str(self.workspace_b.id),
            },
            self.user.id,
            self.trace_id,
        )
        self.assertNotIn('error', result, msg=f'expected success, got {result}')
        d.refresh_from_db()
        self.assertEqual(str(d.workspace_id), str(self.workspace_b.id))

    # ── Safety: non-staff still can't touch other users' deliverables ──

    def test_nonstaff_cannot_attach_other_users_orphan(self):
        """The attach-aware lookup re-applies the user-ownership scope
        for non-staff users. A non-staff user trying to attach another
        user's orphan should still get 'not found'."""
        other_orphan = self._make_orphan(
            title="Another user's orphan",
            user=self.user,  # owned by self.user, not other_user
        )
        # _resolve_deliverable raises ValueError directly; in production
        # the dispatcher catches it and returns {'error': '...'} (Rigby's
        # bug #2 repro showed exactly that shape). For the unit test we
        # assert the raw exception that propagates from the handler.
        with self.assertRaises(ValueError) as cm:
            self.dispatcher._handle_deliverables(
                'deliverables_tool',
                {
                    'action': 'update',
                    'id': str(other_orphan.id),
                    'workspace_id': str(self.workspace_a.id),
                },
                self.other_user.id,
                self.trace_id,
            )
        self.assertIn('not found', str(cm.exception).lower())

        other_orphan.refresh_from_db()
        self.assertIsNone(other_orphan.workspace_id)  # unchanged

    # ── No-behavior-change sanity for update without workspace_id ──────

    def test_update_without_workspace_id_keeps_existing_behavior(self):
        """When payload has no workspace_id, the original base_qs path
        is still used. Sanity check that we didn't accidentally rewire
        non-attach updates."""
        d = self._make_orphan(workspace_id=str(self.workspace_a.id))
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'update',
                'id': str(d.id),
                'title': 'New title (no workspace change)',
            },
            self.user.id,
            self.trace_id,
        )
        self.assertNotIn('error', result, msg=f'expected success, got {result}')
        d.refresh_from_db()
        self.assertEqual(d.title, 'New title (no workspace change)')
        self.assertEqual(str(d.workspace_id), str(self.workspace_a.id))  # unchanged
