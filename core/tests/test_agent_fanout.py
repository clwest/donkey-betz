"""S3047: shared fanout helper + REST detail view lineage contract tests.

Discharges S3047 PLAYBOOK-7.7.1 spec: pins the compute_fanout helper (extracted
from _handle_agent_job_status at S3047) and the execution_detail REST view
extension so both surfaces stay locked to the same lineage semantics.

- Helper tests: direct invocation of compute_fanout(execution). TestCase is
  sufficient because we are not going through the async ToolDispatcher.
- View test: uses APIClient to hit /api/v1/agents/execution/<id>/ and asserts
  the 7 fanout fields land on data.execution, including the children_truncated
  invariant (Rigby T1 SIGN fold: children_truncated tracks child_count > 20).
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models_unified_system import Agent, AgentExecution
from core.services.agent_fanout import CHILDREN_CAP, compute_fanout


User = get_user_model()


class ComputeFanoutHelperTests(TestCase):
    """Direct-invocation tests for core/services/agent_fanout.compute_fanout."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s3047_helper_test', email='s3047h@test.local', password='x',
        )
        self.parent_agent, _ = Agent.objects.get_or_create(
            name='S3047ParentAgent', defaults={'description': 't', 'specialization': 't'},
        )
        self.child_agent, _ = Agent.objects.get_or_create(
            name='S3047ChildAgent', defaults={'description': 't', 'specialization': 't'},
        )

    def _make_execution(self, agent, **kwargs):
        kwargs.setdefault('task', 't')
        kwargs.setdefault('status', 'completed')
        return AgentExecution.objects.create(agent=agent, user=self.user, **kwargs)

    def test_leaf_row_zero_children_zero_subtree(self):
        row = self._make_execution(self.parent_agent)
        result = compute_fanout(row)

        self.assertTrue(result['fanout_available'])
        self.assertIsNone(result['parent_execution_id'])
        self.assertIsNone(result['root_execution_id'])
        self.assertEqual(result['child_count'], 0)
        self.assertEqual(result['subtree_count'], 0)
        self.assertEqual(result['children'], [])
        self.assertFalse(result['children_truncated'])

    def test_children_under_cap_render_full_list(self):
        parent = self._make_execution(self.parent_agent)
        AgentExecution.objects.filter(id=parent.id).update(root_execution_id=parent.id)
        parent.refresh_from_db()
        for i in range(5):
            self._make_execution(
                self.child_agent, task=f'c{i}',
                parent_execution_id=parent.id, root_execution_id=parent.id,
                execution_time_ms=100 * (i + 1),
            )

        result = compute_fanout(parent)

        self.assertEqual(result['child_count'], 5)
        self.assertEqual(result['subtree_count'], 5)
        self.assertEqual(len(result['children']), 5)
        self.assertFalse(result['children_truncated'])
        # Projection shape locked — must match PA tool response.
        self.assertEqual(set(result['children'][0].keys()), {
            'execution_id', 'agent_name', 'status',
            'created_at', 'completed_at', 'duration_ms',
        })

    def test_children_over_cap_truncates_list_but_keeps_true_count(self):
        parent = self._make_execution(self.parent_agent)
        AgentExecution.objects.filter(id=parent.id).update(root_execution_id=parent.id)
        parent.refresh_from_db()
        for i in range(CHILDREN_CAP + 7):
            self._make_execution(
                self.child_agent, task=f'c{i}',
                parent_execution_id=parent.id, root_execution_id=parent.id,
            )

        result = compute_fanout(parent)

        self.assertEqual(result['child_count'], CHILDREN_CAP + 7)
        self.assertEqual(len(result['children']), CHILDREN_CAP)
        self.assertTrue(result['children_truncated'])

    def test_legacy_null_root_falls_back_to_self_id(self):
        """Pre-migration-0336 rows have parent=root=NULL; subtree query must
        anchor on self.id, not query for NULL root (which would leak globally)."""
        legacy = self._make_execution(self.parent_agent)  # parent=root both NULL
        # An unrelated legacy row must NOT show up in the subtree.
        self._make_execution(self.parent_agent)

        result = compute_fanout(legacy)

        self.assertIsNone(result['parent_execution_id'])
        self.assertIsNone(result['root_execution_id'])
        self.assertEqual(result['subtree_count'], 0)


class ExecutionDetailViewFanoutTests(TestCase):
    """Pin the S3047 REST view extension — the 7 fields must land on data.execution."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s3047_view_test', email='s3047v@test.local',
            password='x', is_superuser=True, is_staff=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.parent_agent, _ = Agent.objects.get_or_create(
            name='S3047ViewParent', defaults={'description': 't', 'specialization': 't'},
        )
        self.child_agent, _ = Agent.objects.get_or_create(
            name='S3047ViewChild', defaults={'description': 't', 'specialization': 't'},
        )

    def test_view_surfaces_all_seven_fanout_fields_on_data_execution(self):
        parent = AgentExecution.objects.create(
            agent=self.parent_agent, user=self.user, task='p', status='completed',
        )
        AgentExecution.objects.filter(id=parent.id).update(root_execution_id=parent.id)
        parent.refresh_from_db()
        for i in range(3):
            AgentExecution.objects.create(
                agent=self.child_agent, user=self.user, task=f'c{i}', status='completed',
                parent_execution_id=parent.id, root_execution_id=parent.id,
            )

        response = self.client.get(f'/api/v1/agents/execution/{parent.id}/')
        self.assertEqual(response.status_code, 200)

        execution = response.json()['data']['execution']
        for field in (
            'parent_execution_id', 'root_execution_id',
            'child_count', 'subtree_count',
            'children', 'children_truncated', 'fanout_available',
        ):
            self.assertIn(field, execution, f'missing {field} on data.execution')

        self.assertTrue(execution['fanout_available'])
        self.assertEqual(execution['child_count'], 3)
        self.assertEqual(execution['subtree_count'], 3)
        self.assertEqual(len(execution['children']), 3)

    def test_view_children_truncated_flag_tracks_child_count_over_cap(self):
        """Rigby T1 SIGN fold: children_truncated is the observable contract
        the UI relies on to render the '+N more' hint. Must flip iff
        child_count > CHILDREN_CAP."""
        parent = AgentExecution.objects.create(
            agent=self.parent_agent, user=self.user, task='p', status='completed',
        )
        AgentExecution.objects.filter(id=parent.id).update(root_execution_id=parent.id)
        parent.refresh_from_db()
        for i in range(CHILDREN_CAP + 3):
            AgentExecution.objects.create(
                agent=self.child_agent, user=self.user, task=f'c{i}', status='completed',
                parent_execution_id=parent.id, root_execution_id=parent.id,
            )

        response = self.client.get(f'/api/v1/agents/execution/{parent.id}/')
        execution = response.json()['data']['execution']

        self.assertEqual(execution['child_count'], CHILDREN_CAP + 3)
        self.assertEqual(len(execution['children']), CHILDREN_CAP)
        self.assertTrue(execution['children_truncated'])
