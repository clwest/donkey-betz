"""Session 1169 — symmetric attach-aware lookup for id-based mutations.

Session 1168 PR #2311 added the attach-aware lookup queryset to
`deliverable_tool.update` only. This module covers the proactive
symmetric fix for the rest of the id-based actions (detail, save,
unsave, append, delete) — they all need to find orphans
(``workspace_id=NULL``) the user owns even when an AssistantProfile
or payload sets a workspace scope.

(``link_initiative`` in ``td_handlers_content.py`` already uses an
unscoped ``Deliverable.objects.get(id=...)``; that path has a
different — auth — issue and is intentionally not touched here.)

(``export_pdf`` is omitted because it calls into an external PDF
export service; the orphan-inclusive lookup change applies the same
way but exercising it would require mocking the export pipeline.)

Run::

    python manage.py test core.tests.test_deliverable_orphan_mutations_symmetric -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class OrphanMutationsSymmetricTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Non-staff user — this is the case where the bug previously
        # fired. Staff/superuser had a bypass that made orphans findable.
        cls.user = User.objects.create_user(
            username=f'sym-test-{uuid.uuid4().hex[:8]}',
            email='sym@example.com',
            password='x',
            is_superuser=False,
            is_staff=False,
        )
        cls.other_user = User.objects.create_user(
            username=f'sym-other-{uuid.uuid4().hex[:8]}',
            email='sym-other@example.com',
            password='x',
            is_superuser=False,
            is_staff=False,
        )
        cls.workspace = ProjectWorkspace.objects.create(
            user=cls.user, name='Sym Workspace',
            allow_autonomous_writes=True,
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()
        self.trace_id = str(uuid.uuid4())

    def _make_orphan(self, **overrides):
        defaults = dict(
            title='Orphan newsletter for symmetric tests',
            content='# Newsletter content\n\nSubstantial body. ' * 20,
            agent_name='NewsletterTool',
            category='Newsletter',
            deliverable_type='document',
            user=self.user,
            workspace_id=None,  # ← orphan
        )
        defaults.update(overrides)
        return Deliverable.objects.create(**defaults)

    # ── detail (read action — was findable for staff but not non-staff) ──

    def test_detail_finds_orphan_for_non_staff_owner(self):
        """When payload includes workspace_id (or AssistantProfile sets
        one), pre-fix this excluded the orphan from base_qs. The new
        _id_lookup_qs ignores workspace scoping; orphan is findable."""
        orphan = self._make_orphan()
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'detail',
                'id': str(orphan.id),
                'workspace_id': str(self.workspace.id),  # forces ws_scope
            },
            self.user.id,
            self.trace_id,
        )
        self.assertEqual(result.get('action'), 'detail')
        self.assertEqual(result.get('id'), str(orphan.id))
        self.assertTrue(result.get('is_orphan'))

    # ── save / unsave ──────────────────────────────────────────────────

    def test_save_finds_orphan_for_non_staff_owner(self):
        orphan = self._make_orphan(is_saved=False)
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'save',
                'id': str(orphan.id),
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        self.assertEqual(result.get('action'), 'save')
        self.assertEqual(result.get('saved'), True)
        orphan.refresh_from_db()
        self.assertTrue(orphan.is_saved)

    def test_unsave_finds_orphan_for_non_staff_owner(self):
        orphan = self._make_orphan(is_saved=True)
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'unsave',
                'id': str(orphan.id),
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        self.assertEqual(result.get('action'), 'unsave')
        self.assertEqual(result.get('saved'), False)
        orphan.refresh_from_db()
        self.assertFalse(orphan.is_saved)

    # ── append ─────────────────────────────────────────────────────────

    def test_append_finds_orphan_for_non_staff_owner(self):
        """Pre-fix: deliverable_tool.append on an orphan failed for
        non-staff users with workspace context. Post-fix: append works."""
        orphan = self._make_orphan(content='Original body.')
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'append',
                'id': str(orphan.id),
                'content': '\n[APPENDED]',
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        self.assertEqual(result.get('action'), 'append')
        self.assertEqual(result.get('id'), str(orphan.id))
        orphan.refresh_from_db()
        self.assertIn('[APPENDED]', orphan.content)

    # ── delete ─────────────────────────────────────────────────────────

    def test_delete_finds_orphan_for_non_staff_owner(self):
        orphan = self._make_orphan()
        orphan_id = orphan.id
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {
                'action': 'delete',
                'id': str(orphan_id),
                'workspace_id': str(self.workspace.id),
            },
            self.user.id,
            self.trace_id,
        )
        self.assertEqual(result.get('action'), 'delete')
        self.assertEqual(result.get('id'), str(orphan_id))
        self.assertFalse(
            Deliverable.objects.filter(id=orphan_id).exists(),
            msg='orphan should have been deleted',
        )

    # ── Security: non-staff cannot touch other users' orphans ─────────

    def test_non_staff_cannot_detail_other_users_orphan(self):
        other_orphan = self._make_orphan(user=self.user)  # owned by self.user
        with self.assertRaises(ValueError) as cm:
            self.dispatcher._handle_deliverables(
                'deliverables_tool',
                {'action': 'detail', 'id': str(other_orphan.id)},
                self.other_user.id,
                self.trace_id,
            )
        self.assertIn('not found', str(cm.exception).lower())

    def test_non_staff_cannot_delete_other_users_orphan(self):
        other_orphan = self._make_orphan(user=self.user)
        with self.assertRaises(ValueError) as cm:
            self.dispatcher._handle_deliverables(
                'deliverables_tool',
                {'action': 'delete', 'id': str(other_orphan.id)},
                self.other_user.id,
                self.trace_id,
            )
        self.assertIn('not found', str(cm.exception).lower())
        # And the orphan still exists
        self.assertTrue(Deliverable.objects.filter(id=other_orphan.id).exists())

    def test_non_staff_cannot_append_to_other_users_orphan(self):
        other_orphan = self._make_orphan(user=self.user, content='Untouched.')
        with self.assertRaises(ValueError) as cm:
            self.dispatcher._handle_deliverables(
                'deliverables_tool',
                {
                    'action': 'append',
                    'id': str(other_orphan.id),
                    'content': '[HACK ATTEMPT]',
                },
                self.other_user.id,
                self.trace_id,
            )
        self.assertIn('not found', str(cm.exception).lower())
        other_orphan.refresh_from_db()
        self.assertEqual(other_orphan.content, 'Untouched.')

    # ── Unowned (user__isnull=True) orphans remain accessible ──────────

    def test_non_staff_can_act_on_unowned_orphans(self):
        """Per the existing `Q(user_id=user_id) | Q(user__isnull=True)`
        rule, unowned (user=None) deliverables are accessible to any
        non-staff user. The _id_lookup_qs helper preserves that —
        regression guard so the safety fix doesn't break unowned access."""
        unowned = self._make_orphan(user=None)
        result = self.dispatcher._handle_deliverables(
            'deliverables_tool',
            {'action': 'detail', 'id': str(unowned.id)},
            self.user.id,
            self.trace_id,
        )
        self.assertEqual(result.get('id'), str(unowned.id))
