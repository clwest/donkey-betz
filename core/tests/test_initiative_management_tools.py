"""Session 1202 — Connectivity Roadmap §A.1 regression tests.

Covers the two new ``work_tool`` actions wired in Session 1202:

- ``initiative_update`` — patch ``target_workspace_id`` / ``description`` /
  ``kind`` on an Initiative. Idempotent; no-op write returns
  ``updated_fields=[]``.
- ``initiative_link`` — write bidirectional ``related_initiatives`` entry
  per INITIATIVES_FIRST_BACKBONE.md §6.4. Mirror direction computed
  automatically. Idempotent on the (parent, child, relation) tuple.

Acceptance criteria mapping (from CONNECTIVITY_COMPLETION_ROADMAP.md §A.1):
- "Rigby can spawn an Initiative + bind workspace + create bidirectional
  link without calling Claude" — covered by ``test_update_binds_workspace``
  and ``test_link_writes_both_sides_spawns``.
- "Re-running update with same value = no-op" — ``test_update_idempotent_noop``.
- "Reject invalid relation values with clear error" — ``test_link_invalid_relation``.

Local-run note (carryover from Session 1196): pgbouncer transaction pool
on :5433 cannot proxy CREATE DATABASE. Point ``DJANGO_TEST_DATABASE_URL``
at a direct (non-pooled) Postgres DSN to run locally, or rely on CI.

Run::

    python manage.py test core.tests.test_initiative_management_tools -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from core.models_document_registry import Initiative
from core.models_skin_layer import ProjectWorkspace
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


# NOTE: TransactionTestCase rather than TestCase because ToolDispatcher
# routes sync handlers through a thread-pool executor, which uses a
# distinct DB connection. TestCase's transaction-wrapped fixtures are
# invisible to the executor thread; TransactionTestCase commits between
# tests so the dispatched handler can read them.
class InitiativeManagementToolsTestBase(TransactionTestCase):
    """Shared fixtures: one user + one workspace + two initiatives."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()
        cls.trace_id = 'session-1202-initiative-management'

    def setUp(self):
        suffix = uuid.uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f'init-mgmt-{suffix}',
            email=f'init-mgmt-{suffix}@example.com',
            password='x',
        )
        self.user_id = self.user.id
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name=f'Init Mgmt Workspace {suffix}',
            root_path=f'/tmp/init-mgmt-{suffix}',
            is_active=True,
        )
        self.parent = Initiative.objects.create(
            name=f'Parent Initiative {suffix}',
            description='Original parent description.',
            status='ACTIVE',
            kind=Initiative.Kind.PROJECT,
        )
        self.child = Initiative.objects.create(
            name=f'Child Initiative {suffix}',
            description='Original child description.',
            status='ACTIVE',
            kind=Initiative.Kind.PROJECT,
        )

    def _call(self, payload: dict) -> dict:
        """Synchronous dispatch through ``work_tool`` gateway."""
        tool_result = self.dispatcher.execute_sync('work_tool', payload, self.user_id)
        self.assertTrue(
            tool_result.ok,
            f"work_tool failed: {tool_result.error_message}",
        )
        result = tool_result.result
        self.assertIsInstance(result, dict)
        return result


class TestInitiativeUpdate(InitiativeManagementToolsTestBase):

    def test_update_binds_workspace(self):
        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'target_workspace_id': str(self.workspace.id),
        })
        self.assertEqual(result['action'], 'initiative_update')
        self.assertEqual(result.get('gateway'), 'work_tool')
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), ['target_workspace'])
        self.assertEqual(result.get('target_workspace_id'), str(self.workspace.id))
        self.assertEqual(result.get('target_workspace_name'), self.workspace.name)

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.target_workspace_id, self.workspace.id)

    def test_update_empty_string_is_noop_for_target_workspace(self):
        """Session 1202 v2: empty string must NOT unbind workspace.

        GPT-5.2 emits ``target_workspace_id: ""`` as a default for unset
        params, never as a deliberate unbind. The v2 contract makes both
        ``None`` and ``""`` no-ops for this field. Unbinding via the
        tool is not supported; if the workflow ever needs it, add an
        explicit ``unbind_workspace: true`` sentinel.
        """
        self.parent.target_workspace = self.workspace
        self.parent.save(update_fields=['target_workspace'])

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'target_workspace_id': '',
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), [])
        self.assertEqual(result.get('changes'), {})

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.target_workspace_id, self.workspace.id)

    def test_update_description_and_kind(self):
        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'description': 'Rewritten description for §A.1 coverage.',
            'kind': Initiative.Kind.INVESTIGATION,
        })
        self.assertTrue(result.get('success'))
        self.assertCountEqual(result.get('updated_fields') or [], ['description', 'kind'])

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.description, 'Rewritten description for §A.1 coverage.')
        self.assertEqual(self.parent.kind, Initiative.Kind.INVESTIGATION)

    def test_update_idempotent_noop(self):
        # First write
        self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'description': 'Same value, written twice.',
        })
        # Second write — same value — should be a no-op
        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'description': 'Same value, written twice.',
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), [])
        self.assertEqual(result.get('changes'), {})

    def test_update_none_is_noop_for_description(self):
        """Session 1202 follow-up: ``description: None`` must NOT clear."""
        self.parent.description = 'Pre-existing description that must survive.'
        self.parent.save(update_fields=['description'])

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'description': None,
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), [])
        self.assertEqual(result.get('changes'), {})

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.description, 'Pre-existing description that must survive.')

    def test_update_none_is_noop_for_target_workspace(self):
        """Session 1202 follow-up: ``target_workspace_id: None`` must NOT unbind."""
        self.parent.target_workspace = self.workspace
        self.parent.save(update_fields=['target_workspace'])

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'target_workspace_id': None,
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), [])
        self.assertEqual(result.get('changes'), {})

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.target_workspace_id, self.workspace.id)

    def test_update_none_is_noop_for_kind(self):
        """Session 1202 follow-up: ``kind: None`` must NOT raise or change."""
        original_kind = self.parent.kind

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'kind': None,
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), [])

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.kind, original_kind)

    def test_update_none_with_other_field_only_writes_intended(self):
        """null on unrelated field + real value on intended field — only the intended field writes."""
        self.parent.description = 'Survives the call.'
        self.parent.save(update_fields=['description'])

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'description': None,  # GPT-5.2 happens to include null
            'kind': Initiative.Kind.INVESTIGATION,
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), ['kind'])

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.description, 'Survives the call.')
        self.assertEqual(self.parent.kind, Initiative.Kind.INVESTIGATION)

    def test_update_empty_string_is_noop_for_description(self):
        """Session 1202 v2: empty string must NOT clear description.

        v1 treated ``""`` as deliberate clear, which was the same bug
        Rigby caught on PR #2443 — GPT-5.2 emits ``""`` as a default
        for unset string params, never as a deliberate clear. v2
        contract: both ``None`` and ``""`` are no-ops; deliberate
        clearing is not supported via the tool.
        """
        self.parent.description = 'About to survive.'
        self.parent.save(update_fields=['description'])

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'description': '',
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), [])
        self.assertEqual(result.get('changes'), {})

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.description, 'About to survive.')

    def test_update_empty_string_is_noop_for_kind(self):
        """Session 1202 v2: empty string must NOT raise or change kind.

        v1 raised ValueError on ``kind: ""`` because empty string failed
        the enum check. v2 treats empty string as no-op for ergonomic
        symmetry with description + target_workspace_id.
        """
        original_kind = self.parent.kind

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'kind': '',
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), [])

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.kind, original_kind)

    def test_update_rigby_smoke_payload_no_collateral_clears(self):
        """Reproduces the exact GPT-5.2 payload shape that bit Rigby.

        Rigby passed all 18 schema params on every initiative_update
        call (the FC-keys-bloat pattern logged at celery-pa.log:2580
        et al.). With the v1 contract, ``description: ""`` + intent
        ``kind: investigation`` cleared the description as a side
        effect. With v2, only ``kind`` writes.
        """
        self.parent.description = 'Survives the LLM payload bloat.'
        self.parent.target_workspace = self.workspace
        self.parent.save(update_fields=['description', 'target_workspace'])

        result = self._call({
            'action': 'initiative_update',
            'id': str(self.parent.id),
            'name': '',                 # GPT bloat
            'description': '',          # GPT bloat (v1 footgun)
            'status': '',               # GPT bloat
            'priority': '',             # GPT bloat
            'initiative_id': '',        # GPT bloat
            'owner': '',                # GPT bloat
            'notes': '',                # GPT bloat
            'target_workspace_id': '',  # GPT bloat (v1 footgun)
            'kind': Initiative.Kind.INVESTIGATION,  # real intent
            'parent_id': '',            # GPT bloat
            'child_id': '',             # GPT bloat
            'relation': '',             # GPT bloat
            'note': '',                 # GPT bloat
        })
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('updated_fields'), ['kind'])

        self.parent.refresh_from_db()
        self.assertEqual(self.parent.description, 'Survives the LLM payload bloat.')
        self.assertEqual(self.parent.target_workspace_id, self.workspace.id)
        self.assertEqual(self.parent.kind, Initiative.Kind.INVESTIGATION)

    def test_update_invalid_kind_raises(self):
        tool_result = self.dispatcher.execute_sync(
            'work_tool',
            {
                'action': 'initiative_update',
                'id': str(self.parent.id),
                'kind': 'not_a_real_kind',
            },
            self.user_id,
        )
        self.assertFalse(tool_result.ok)
        self.assertIn('Invalid kind', tool_result.error_message or '')

    def test_update_missing_id_raises(self):
        tool_result = self.dispatcher.execute_sync(
            'work_tool',
            {'action': 'initiative_update', 'description': 'orphan'},
            self.user_id,
        )
        self.assertFalse(tool_result.ok)
        self.assertIn("'id' is required", tool_result.error_message or '')

    def test_update_unknown_initiative_raises(self):
        tool_result = self.dispatcher.execute_sync(
            'work_tool',
            {
                'action': 'initiative_update',
                'id': str(uuid.uuid4()),
                'description': 'nope',
            },
            self.user_id,
        )
        self.assertFalse(tool_result.ok)
        self.assertIn('not found', tool_result.error_message or '')

    def test_update_unknown_workspace_raises(self):
        tool_result = self.dispatcher.execute_sync(
            'work_tool',
            {
                'action': 'initiative_update',
                'id': str(self.parent.id),
                'target_workspace_id': str(uuid.uuid4()),
            },
            self.user_id,
        )
        self.assertFalse(tool_result.ok)
        self.assertIn('ProjectWorkspace', tool_result.error_message or '')
        self.assertIn('not found', tool_result.error_message or '')


class TestInitiativeLink(InitiativeManagementToolsTestBase):

    def test_link_writes_both_sides_spawns(self):
        result = self._call({
            'action': 'initiative_link',
            'parent_id': str(self.parent.id),
            'child_id': str(self.child.id),
            'relation': 'spawns',
            'note': 'parent led to child in Session 1202 §A.1',
        })
        self.assertEqual(result['action'], 'initiative_link')
        self.assertTrue(result.get('success'))
        self.assertEqual(result.get('relation'), 'spawns')
        self.assertEqual(result.get('mirror_relation'), 'spawned_from')
        self.assertTrue(result.get('wrote_parent'))
        self.assertTrue(result.get('wrote_child'))
        self.assertFalse(result.get('idempotent_noop'))

        self.parent.refresh_from_db()
        self.child.refresh_from_db()
        self.assertEqual(len(self.parent.related_initiatives), 1)
        self.assertEqual(len(self.child.related_initiatives), 1)
        self.assertEqual(self.parent.related_initiatives[0]['id'], str(self.child.id))
        self.assertEqual(self.parent.related_initiatives[0]['relation'], 'spawns')
        self.assertEqual(self.parent.related_initiatives[0]['note'], 'parent led to child in Session 1202 §A.1')
        self.assertEqual(self.child.related_initiatives[0]['id'], str(self.parent.id))
        self.assertEqual(self.child.related_initiatives[0]['relation'], 'spawned_from')

    def test_link_writes_inverse_when_spawned_from(self):
        result = self._call({
            'action': 'initiative_link',
            'parent_id': str(self.parent.id),
            'child_id': str(self.child.id),
            'relation': 'spawned_from',
        })
        self.assertEqual(result.get('relation'), 'spawned_from')
        self.assertEqual(result.get('mirror_relation'), 'spawns')

        self.parent.refresh_from_db()
        self.child.refresh_from_db()
        self.assertEqual(self.parent.related_initiatives[0]['relation'], 'spawned_from')
        self.assertEqual(self.child.related_initiatives[0]['relation'], 'spawns')

    def test_link_idempotent_noop(self):
        # First write
        self._call({
            'action': 'initiative_link',
            'parent_id': str(self.parent.id),
            'child_id': str(self.child.id),
            'relation': 'spawns',
        })
        # Second write — same tuple — should be a no-op
        result = self._call({
            'action': 'initiative_link',
            'parent_id': str(self.parent.id),
            'child_id': str(self.child.id),
            'relation': 'spawns',
        })
        self.assertTrue(result.get('success'))
        self.assertFalse(result.get('wrote_parent'))
        self.assertFalse(result.get('wrote_child'))
        self.assertTrue(result.get('idempotent_noop'))

        self.parent.refresh_from_db()
        self.child.refresh_from_db()
        self.assertEqual(len(self.parent.related_initiatives), 1)
        self.assertEqual(len(self.child.related_initiatives), 1)

    def test_link_invalid_relation(self):
        tool_result = self.dispatcher.execute_sync(
            'work_tool',
            {
                'action': 'initiative_link',
                'parent_id': str(self.parent.id),
                'child_id': str(self.child.id),
                'relation': 'consumes',
            },
            self.user_id,
        )
        self.assertFalse(tool_result.ok)
        self.assertIn('Invalid relation', tool_result.error_message or '')

    def test_link_rejects_self_loop(self):
        tool_result = self.dispatcher.execute_sync(
            'work_tool',
            {
                'action': 'initiative_link',
                'parent_id': str(self.parent.id),
                'child_id': str(self.parent.id),
                'relation': 'spawns',
            },
            self.user_id,
        )
        self.assertFalse(tool_result.ok)
        self.assertIn('must differ', tool_result.error_message or '')

    def test_link_missing_ids(self):
        for payload in (
            {'action': 'initiative_link', 'child_id': str(self.child.id)},
            {'action': 'initiative_link', 'parent_id': str(self.parent.id)},
        ):
            tool_result = self.dispatcher.execute_sync('work_tool', payload, self.user_id)
            self.assertFalse(tool_result.ok)
            self.assertIn('is required', tool_result.error_message or '')

    def test_link_unknown_initiative(self):
        tool_result = self.dispatcher.execute_sync(
            'work_tool',
            {
                'action': 'initiative_link',
                'parent_id': str(self.parent.id),
                'child_id': str(uuid.uuid4()),
                'relation': 'spawns',
            },
            self.user_id,
        )
        self.assertFalse(tool_result.ok)
        self.assertIn('not found', tool_result.error_message or '')
