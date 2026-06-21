"""
Session 1185 F2: execution_history_tool reverse-link tests.
============================================================

Surfaced by Section 6 forensic validation on conversation pa-10df024c0bd8
(Session 1184 close): `execution_history_tool action=detail id=<exec_uuid>`
returned `output_data` only — no surface of deliverables the execution had
produced. Forward link (deliverable→execution) was already exposed via
`deliverable_tool.detail.provenance.origin_execution_id` (Session 1184
PR #2362). Reverse link required a separate DB query.

Fix: added `deliverables` field to the detail response, populated from
`Deliverable.objects.filter(parent_object_id=execution.id,
parent_object_type='agent_execution')[:25]`.

Acceptance criteria from deliverable 6523a071-1142-4ae1-9eed-4b247ab887d5:
    AC1: detail response includes a `deliverables` field
    AC2: for executions that produced deliverables, the field contains the
         list with title + ID + created_at
    AC3: for executions with no produced deliverables, the field is an empty
         list (not null, not missing key)
    AC4: limit 25 entries to bound payload; documented in tool schema
    AC5: dispatch an agent, get execution_id, call detail, assert produced
         deliverable_id appears in the deliverables list

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_execution_history_reverse_link -v2 --keepdb
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_deliverables import Deliverable
from core.models_unified_system import Agent, AgentExecution
from core.services.td_handlers_content import ContentHandlersMixin


User = get_user_model()


class _HandlerHost(ContentHandlersMixin):
    """Bare mixin host for direct handler invocation in tests."""
    pass


class ExecutionHistoryReverseLinkTests(TestCase):
    """F2 — reverse-link from execution to produced deliverables."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='exec-history-rev', email='ehr@example.com',
            password='x',
        )
        cls.agent, _ = Agent.objects.get_or_create(
            name='ContentWriterAgent',
            defaults={'agent_type': 'routable', 'description': 'test',
                      'specialization': '', 'is_active': True},
        )

    def setUp(self):
        self.host = _HandlerHost()

    def _make_execution(self, task='Test dispatch'):
        return AgentExecution.objects.create(
            agent=self.agent, user=self.user,
            task=task, status='completed',
            trace_id=uuid.uuid4(), owner_agent='ContentWriterAgent',
        )

    def _make_deliverable(self, execution, title, category='Test'):
        return Deliverable.objects.create(
            user=self.user, agent_name='ContentWriterAgent',
            title=title, content='## body ' * 50,
            category=category, deliverable_type='document',
            content_format='markdown',
            parent_object_type='agent_execution',
            parent_object_id=execution.id,
        )

    def _call_detail(self, exec_id):
        return self.host._handle_execution_history(
            tool_name='execution_history_tool',
            payload={'action': 'detail', 'id': str(exec_id)},
            user_id=self.user.id,
            trace_id=str(uuid.uuid4()),
        )

    # ── AC1 + AC2 ──────────────────────────────────────────────────────────
    def test_detail_includes_deliverables_when_present(self):
        execution = self._make_execution(task='Produces one deliverable')
        deliverable = self._make_deliverable(execution, 'Reverse-link target')

        result = self._call_detail(execution.id)

        self.assertIn('deliverables', result, 'AC1: field must be present')
        self.assertEqual(len(result['deliverables']), 1, 'AC2: one produced')

        row = result['deliverables'][0]
        self.assertEqual(str(row['id']), str(deliverable.id), 'AC5: id matches')
        self.assertEqual(row['title'], 'Reverse-link target', 'AC2: title present')
        self.assertIn('created_at', row, 'AC2: created_at present')
        self.assertIn('category', row, 'AC2: category present')
        self.assertIn('is_saved', row, 'AC2: is_saved present')

    # ── AC3 ────────────────────────────────────────────────────────────────
    def test_detail_returns_empty_list_when_no_deliverables(self):
        execution = self._make_execution(task='Produces nothing')

        result = self._call_detail(execution.id)

        self.assertIn('deliverables', result, 'AC3: key must be present')
        self.assertEqual(result['deliverables'], [],
                         'AC3: empty list, not null, not missing')

    # ── AC4 ────────────────────────────────────────────────────────────────
    def test_detail_caps_deliverables_at_25(self):
        execution = self._make_execution(task='Produces 30')
        for i in range(30):
            self._make_deliverable(execution, f'Deliverable {i:02d}')

        result = self._call_detail(execution.id)

        self.assertEqual(len(result['deliverables']), 25,
                         'AC4: cap at 25 to bound payload')

    # ── AC5 ────────────────────────────────────────────────────────────────
    def test_only_matching_parent_type_surfaces(self):
        """Deliverables with parent_object_id matching but parent_object_type
        differing (e.g., legacy / future linkage) must not leak into the
        reverse-link. The provenance contract is keyed on the tuple."""
        execution = self._make_execution(task='Mixed parent types')
        self._make_deliverable(execution, 'Real produced output')

        wrong_type = Deliverable.objects.create(
            user=self.user, agent_name='ContentWriterAgent',
            title='Different parent type', content='x',
            category='Test', deliverable_type='document',
            content_format='markdown',
            parent_object_type='deliberation_session',
            parent_object_id=execution.id,
        )

        result = self._call_detail(execution.id)

        titles = [r['title'] for r in result['deliverables']]
        self.assertIn('Real produced output', titles)
        self.assertNotIn('Different parent type', titles,
                         'must filter on parent_object_type=agent_execution')
        self.assertEqual(len(result['deliverables']), 1)
        # silence unused-var warning while keeping the wrong_type fixture
        # legible in the test body
        self.assertIsNotNone(wrong_type.id)
