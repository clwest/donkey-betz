"""Session 1227 PR4 — deliverable_tool `normalize` action.

Closes Session 1226 audit `e2964e4a-…` §4.6 item 5 (optional) — gives
Rigby a dry-run preview surface to detect agent_name alias drift before
it accumulates. Uses the same canonical alias map that
`deliverable_factory._canonicalize_agent_name` enforces at write time.

Stacks on PR3 (#2564) → PR2 (#2563) → PR1 (#2562).

Belt-and-suspenders safety: dry_run defaults to True; writes require
BOTH `dry_run=false` AND `confirm=true` (Rigby D4 design call —
protects against LLM autofilling `dry_run=false`).
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.services.deliverable_aliases import AGENT_NAME_ALIASES
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


def _norm(user_id, payload):
    dispatcher = ToolDispatcher()
    return dispatcher._handle_deliverables(  # type: ignore[attr-defined]
        tool_name='deliverable_tool',
        payload={'action': 'normalize', **payload},
        user_id=user_id,
        trace_id='test-norm',
    )


class _NormalizeBase(TestCase):
    """Shared setUp — seeds the two aliases the map currently knows."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s1227-norm', password='x', is_staff=True,
        )
        # 'rigby' → 'Rigby': seed 2 rows under the variant. BYPASS the
        # factory canonicalizer by writing directly via the ORM so the
        # alias survives setUp.
        self.rigby_rows = [
            Deliverable.objects.create(
                title=f'Norm probe Rigby {i}',
                content='x' * 200,
                agent_name='rigby',
                user=self.user,
                status='ready',
            )
            for i in range(2)
        ]
        # 'ClaudeCode' → 'claude-code': seed 1 row.
        self.cc_row = Deliverable.objects.create(
            title='Norm probe CC',
            content='x' * 200,
            agent_name='ClaudeCode',
            user=self.user,
            status='ready',
        )
        # Canonical row that should NEVER be touched.
        self.canonical_row = Deliverable.objects.create(
            title='Norm probe canonical',
            content='x' * 200,
            agent_name='Rigby',
            user=self.user,
            status='ready',
        )


class DryRunDefaultTests(_NormalizeBase):
    """Default behavior: preview, no writes, no rows touched."""

    def test_default_is_dry_run_with_preview(self):
        result = _norm(self.user.id, {'show_all': True})
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['rows_changed'], 0)
        # 2 'rigby' + 1 'ClaudeCode' = 3 rows would be normalized.
        self.assertEqual(result['total_rows_affected'], 3)

    def test_preview_lists_each_alias_with_count(self):
        result = _norm(self.user.id, {'show_all': True})
        preview = {row['from_value']: row for row in result['preview']}
        self.assertEqual(preview['rigby']['to_value'], 'Rigby')
        self.assertEqual(preview['rigby']['count'], 2)
        self.assertEqual(preview['ClaudeCode']['to_value'], 'claude-code')
        self.assertEqual(preview['ClaudeCode']['count'], 1)

    def test_preview_sample_ids_capped_at_5(self):
        # Create 7 more 'rigby' rows so we have 9 total — sample should cap at 5.
        for i in range(7):
            Deliverable.objects.create(
                title=f'Norm probe Rigby extra {i}',
                content='x' * 200,
                agent_name='rigby',
                user=self.user,
            )
        result = _norm(self.user.id, {'show_all': True})
        preview = {row['from_value']: row for row in result['preview']}
        self.assertLessEqual(len(preview['rigby']['sample_ids']), 5)

    def test_dry_run_does_not_write(self):
        _norm(self.user.id, {'show_all': True})
        # All seeded rows untouched.
        for r in self.rigby_rows:
            r.refresh_from_db()
            self.assertEqual(r.agent_name, 'rigby')
        self.cc_row.refresh_from_db()
        self.assertEqual(self.cc_row.agent_name, 'ClaudeCode')


class BeltAndSuspendersWriteTests(_NormalizeBase):
    """Both dry_run=false AND confirm=true required to write."""

    def test_dry_run_false_alone_is_still_dry_run(self):
        """LLM-autofill safety — dry_run=false WITHOUT confirm stays dry_run."""
        result = _norm(self.user.id, {'show_all': True, 'dry_run': False})
        self.assertTrue(result['dry_run'])  # still preview-only
        self.assertEqual(result['rows_changed'], 0)
        # Rows still untouched.
        self.rigby_rows[0].refresh_from_db()
        self.assertEqual(self.rigby_rows[0].agent_name, 'rigby')

    def test_confirm_true_alone_is_still_dry_run(self):
        """confirm=true alone (default dry_run=true) is preview-only."""
        result = _norm(self.user.id, {'show_all': True, 'confirm': True})
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['rows_changed'], 0)

    def test_both_dry_run_false_and_confirm_true_writes(self):
        result = _norm(self.user.id, {
            'show_all': True,
            'dry_run': False,
            'confirm': True,
        })
        self.assertFalse(result['dry_run'])
        self.assertEqual(result['rows_changed'], 3)
        # Variants are now canonical.
        for r in self.rigby_rows:
            r.refresh_from_db()
            self.assertEqual(r.agent_name, 'Rigby')
        self.cc_row.refresh_from_db()
        self.assertEqual(self.cc_row.agent_name, 'claude-code')
        # Canonical row was never variant; still 'Rigby'.
        self.canonical_row.refresh_from_db()
        self.assertEqual(self.canonical_row.agent_name, 'Rigby')


class ScopeAndFieldTests(_NormalizeBase):
    """workspace_id required by default; show_all=true for global."""

    def test_unscoped_call_raises(self):
        with self.assertRaises(ValueError) as ctx:
            _norm(self.user.id, {})  # no workspace_id, no show_all
        self.assertIn('workspace_id', str(ctx.exception))
        self.assertIn('show_all', str(ctx.exception))

    def test_unknown_field_raises(self):
        with self.assertRaises(ValueError) as ctx:
            _norm(self.user.id, {'show_all': True, 'field': 'category'})
        self.assertIn("field='agent_name'", str(ctx.exception))

    def test_default_field_is_agent_name(self):
        result = _norm(self.user.id, {'show_all': True})
        self.assertEqual(result['field'], 'agent_name')

    def test_response_includes_alias_map_and_scope(self):
        result = _norm(self.user.id, {'show_all': True})
        self.assertEqual(result['alias_map_used'], AGENT_NAME_ALIASES)
        self.assertEqual(result['scope'], 'global')

    def test_workspace_scope_only_touches_in_scope_rows(self):
        # Use ws_scope through the user_id+payload path: AssistantProfile
        # isn't set up in tests, so we pass workspace_id explicitly.
        # Need a workspace for the test.
        from core.models_skin_layer import ProjectWorkspace
        ws = ProjectWorkspace.objects.create(
            name='Norm test workspace',
            user=self.user,
            workspace_type='other',
        )
        # Reassign one rigby row to this workspace, leave the others orphan.
        scoped_row = self.rigby_rows[0]
        scoped_row.workspace = ws
        scoped_row.save(update_fields=['workspace'])

        result = _norm(self.user.id, {
            'workspace_id': str(ws.id),
            'dry_run': False, 'confirm': True,
        })
        # Only the scoped 'rigby' row was rewritten.
        self.assertEqual(result['rows_changed'], 1)
        scoped_row.refresh_from_db()
        self.assertEqual(scoped_row.agent_name, 'Rigby')
        # The non-scoped variant rows are still 'rigby' / 'ClaudeCode'.
        other_rigby = self.rigby_rows[1]
        other_rigby.refresh_from_db()
        self.assertEqual(other_rigby.agent_name, 'rigby')


class AppliedFiltersAndMessageTests(_NormalizeBase):
    """Response surfaces applied_filters + an operator-readable message."""

    def test_applied_filters_records_dry_run(self):
        result = _norm(self.user.id, {'show_all': True})
        af = result.get('applied_filters', {})
        self.assertEqual(af.get('field'), 'agent_name')
        self.assertTrue(af.get('dry_run'))
        self.assertTrue(af.get('show_all'))

    def test_message_mentions_preview_in_dry_run(self):
        result = _norm(self.user.id, {'show_all': True})
        self.assertIn('Preview', result['message'])
        self.assertIn('3 row', result['message'])

    def test_message_mentions_applied_after_write(self):
        result = _norm(self.user.id, {
            'show_all': True, 'dry_run': False, 'confirm': True,
        })
        self.assertIn('Applied', result['message'])
        self.assertIn('3 row', result['message'])
