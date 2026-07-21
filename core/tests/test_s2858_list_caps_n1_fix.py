"""Session 2858 PR#2 — workspace_budget_tool.list_caps N+1 fix.

Locks the batch ProjectWorkspace name lookup in the include_defaults=False
branch of list_caps. Was: 1 ProjectWorkspace.objects.get() per row
(classic N+1). Now: single .filter(id__in=[...]).values_list('id','name')
into a dict, then dict lookup per row.

Semantic contract preserved:
- workspace_id in the output is the ORIGINAL string from list_workspace_caps
  (not the parsed UUID) — external callers may depend on the wire shape.
- If a row's UUID doesn't resolve to a ProjectWorkspace (deleted row,
  invalid uuid), workspace_name is None (same as pre-refactor
  DoesNotExist / ValueError branch).
- scoped_ids filter behavior unchanged.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from core.models_diagnostic_pipeline import AutopilotAction
from core.models_skin_layer import ProjectWorkspace
from core.services.ops_autopilot.budget import BudgetController
from core.services.td_handlers_ops import OpsHandlersMixin


User = get_user_model()


class _OpsProxy(OpsHandlersMixin):
    pass


class _BaseListCapsCase(TestCase):
    """Staff user + 5 workspaces with explicit $10 caps."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2858list',
            email='s2858list@test.com',
            password='pw',
        )
        self.user.is_staff = True
        self.user.save()
        self.workspaces = []
        controller = BudgetController()
        for i in range(5):
            ws = ProjectWorkspace.objects.create(
                user=self.user,
                name=f'S2858 List Workspace {i}',
            )
            controller.set_workspace_daily_cap(
                ws.id, daily_cap_usd=10.0, actor_user_id=self.user.id,
            )
            self.workspaces.append(ws)
        AutopilotAction.objects.all().delete()

    def _call(self):
        proxy = _OpsProxy()
        # Patch compute_workspace_spend so we don't need real LLMCallLog
        # rows — the N+1 we're testing is the ProjectWorkspace lookup, not
        # spend computation.
        with patch.object(
            BudgetController,
            'compute_workspace_spend',
            return_value={
                'daily_total': 0.0,
                'daily_calls': 0,
                'hourly_total': 0.0,
                'hourly_calls': 0,
            },
        ):
            return proxy._handle_workspace_budget(
                tool_name='workspace_budget_tool',
                payload={
                    'action': 'list_caps',
                    'include_defaults': False,
                },
                user_id=self.user.id,
                trace_id='s2858-test',
            )


class ListCapsN1QueryCountTests(_BaseListCapsCase):
    """The N+1 fix: name lookups collapse to a single filter() query."""

    def test_single_query_for_names_regardless_of_row_count(self):
        # 5 workspaces. Pre-fix: 5 x ProjectWorkspace.objects.get() +
        # per-row is_frozen + is_downgraded (SystemConfiguration reads).
        # Post-fix: 1 x ProjectWorkspace.objects.filter().values_list().
        # We count ProjectWorkspace queries specifically.
        with CaptureQueriesContext(connection) as ctx:
            r = self._call()
        self.assertEqual(r['count'], 5)
        ws_table = ProjectWorkspace._meta.db_table
        ws_reads = [
            q for q in ctx.captured_queries
            if ws_table in q['sql'] and q['sql'].strip().upper().startswith('SELECT')
        ]
        # Expected reads on ProjectWorkspace:
        #   - 1 for scoped_ids (values_list('id') filter by user_id)
        #   - 1 for the batched name lookup (filter id__in + values_list)
        # Pre-fix would have been ~7 (2 above + 5 individual .get()s).
        self.assertLessEqual(
            len(ws_reads), 3,
            f'Expected <=3 ProjectWorkspace SELECTs, got {len(ws_reads)}:\n'
            + '\n'.join(q['sql'] for q in ws_reads),
        )


class ListCapsSemanticPreservationTests(_BaseListCapsCase):
    """Response shape + values unchanged after the batching refactor."""

    def test_all_rows_have_correct_names(self):
        r = self._call()
        names = {row['workspace_name'] for row in r['workspaces']}
        expected = {ws.name for ws in self.workspaces}
        self.assertEqual(names, expected)

    def test_workspace_id_field_is_original_string_shape(self):
        # list_workspace_caps() returns workspace_id as a str; the emitted
        # response should carry that str through unchanged (not the parsed
        # UUID object).
        r = self._call()
        for row in r['workspaces']:
            self.assertIsInstance(row['workspace_id'], str)

    def test_all_expected_fields_present(self):
        r = self._call()
        for row in r['workspaces']:
            self.assertIn('cap', row)
            self.assertIn('effective_cap', row)
            self.assertEqual(row['cap_source'], 'explicit')
            self.assertIn('daily_total', row)
            self.assertIn('is_frozen', row)
            self.assertIn('is_downgraded', row)


class ListCapsDeletedWorkspaceTests(TestCase):
    """When list_workspace_caps returns a workspace_id that no longer has
    a matching ProjectWorkspace row (was deleted after cap was written),
    workspace_name is None — matches pre-refactor DoesNotExist behavior.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2858ghost',
            email='s2858ghost@test.com',
            password='pw',
        )
        self.user.is_staff = True
        self.user.save()

    def test_missing_workspace_yields_none_name(self):
        proxy = _OpsProxy()

        # Simulate a "ghost" workspace_id — one that list_workspace_caps
        # returns but that ProjectWorkspace can't resolve. Use a valid
        # UUID string that isn't in the DB.
        ghost_uuid = '00000000-0000-4000-8000-000000000042'

        with patch.object(
            BudgetController,
            'list_workspace_caps',
            return_value=[{'workspace_id': ghost_uuid, 'cap': 5.0}],
        ), patch.object(
            BudgetController,
            'compute_workspace_spend',
            return_value={
                'daily_total': 0.0,
                'daily_calls': 0,
                'hourly_total': 0.0,
                'hourly_calls': 0,
            },
        ):
            r = proxy._handle_workspace_budget(
                tool_name='workspace_budget_tool',
                payload={
                    'action': 'list_caps',
                    'include_defaults': False,
                },
                user_id=self.user.id,
                trace_id='s2858-test',
            )

        self.assertEqual(r['count'], 1)
        self.assertEqual(r['workspaces'][0]['workspace_id'], ghost_uuid)
        self.assertIsNone(r['workspaces'][0]['workspace_name'])
        # Cap + explicit source still emitted (row came from
        # list_workspace_caps).
        self.assertEqual(r['workspaces'][0]['cap'], 5.0)
        self.assertEqual(r['workspaces'][0]['cap_source'], 'explicit')


class ListCapsScopedIdsFilterTests(TestCase):
    """Non-staff user sees only own workspaces — scoped_ids filter path
    still works after the batch refactor.
    """

    def setUp(self):
        # Two users, two workspaces each
        self.user_a = User.objects.create_user(
            username='s2858usera',
            email='s2858a@test.com',
            password='pw',
        )
        self.user_b = User.objects.create_user(
            username='s2858userb',
            email='s2858b@test.com',
            password='pw',
        )
        controller = BudgetController()
        # user_a workspaces have explicit caps
        for i in range(2):
            ws = ProjectWorkspace.objects.create(
                user=self.user_a,
                name=f'A-Workspace-{i}',
            )
            controller.set_workspace_daily_cap(
                ws.id, daily_cap_usd=10.0, actor_user_id=self.user_a.id,
            )
        # user_b workspaces also have explicit caps
        for i in range(2):
            ws = ProjectWorkspace.objects.create(
                user=self.user_b,
                name=f'B-Workspace-{i}',
            )
            controller.set_workspace_daily_cap(
                ws.id, daily_cap_usd=10.0, actor_user_id=self.user_b.id,
            )
        AutopilotAction.objects.all().delete()

    def test_user_a_sees_only_own_workspaces(self):
        proxy = _OpsProxy()
        with patch.object(
            BudgetController,
            'compute_workspace_spend',
            return_value={
                'daily_total': 0.0,
                'daily_calls': 0,
                'hourly_total': 0.0,
                'hourly_calls': 0,
            },
        ):
            r = proxy._handle_workspace_budget(
                tool_name='workspace_budget_tool',
                payload={
                    'action': 'list_caps',
                    'include_defaults': False,
                },
                user_id=self.user_a.id,
                trace_id='s2858-test',
            )
        names = {row['workspace_name'] for row in r['workspaces']}
        self.assertEqual(names, {'A-Workspace-0', 'A-Workspace-1'})
        self.assertNotIn('B-Workspace-0', names)
        self.assertNotIn('B-Workspace-1', names)
