"""S3046: agent_job_status fanout visibility contract test.

Discharges S3045 substrate ledger row `3f77850d-...` (coordinator-provenance-fanout
Option B trigger) by pinning the new lineage + fanout response shape returned by
_handle_agent_job_status.

Uses TransactionTestCase per PLAYBOOK-3.2.3 — setUp-created AgentExecution rows
must be visible to the handler running on a separate DB connection inside
ToolDispatcher.execute_sync's fresh asyncio event loop.

PLAYBOOK-3.2.4 not applicable — this is a single-entrypoint tool (no `action`
enum, no shared-taxonomy branch); envelope-shape assertions suffice.
"""

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from core.models_unified_system import Agent, AgentExecution
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class AgentJobStatusFanoutTests(TransactionTestCase):
    """Pin the S3046 lineage + fanout response contract."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

        self.user = User.objects.create_user(
            username='s3046_fanout_test', email='s3046@test.local', password='x',
        )

        self.parent_agent, _ = Agent.objects.get_or_create(
            name='AiSeriesWorkflowAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        self.child_agent, _ = Agent.objects.get_or_create(
            name='ResearchAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )
        self.other_agent, _ = Agent.objects.get_or_create(
            name='TrendAnalysisAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )

        self.parent = AgentExecution.objects.create(
            agent=self.parent_agent, user=self.user,
            task='coordinator dispatch', status='in_progress',
        )
        # Coordinator writes its own id as its root when it dispatches children.
        AgentExecution.objects.filter(id=self.parent.id).update(
            root_execution_id=self.parent.id,
        )
        self.parent.refresh_from_db()

        # Three direct children with lineage threaded correctly.
        self.child_a = AgentExecution.objects.create(
            agent=self.child_agent, user=self.user,
            task='child a', status='completed',
            parent_execution_id=self.parent.id,
            root_execution_id=self.parent.id,
            execution_time_ms=1200,
        )
        self.child_b = AgentExecution.objects.create(
            agent=self.other_agent, user=self.user,
            task='child b', status='in_progress',
            parent_execution_id=self.parent.id,
            root_execution_id=self.parent.id,
        )
        self.child_c = AgentExecution.objects.create(
            agent=self.child_agent, user=self.user,
            task='child c', status='queued',
            parent_execution_id=self.parent.id,
            root_execution_id=self.parent.id,
        )

        # Grandchild under child_a — belongs to subtree_count but not child_count.
        self.grandchild = AgentExecution.objects.create(
            agent=self.other_agent, user=self.user,
            task='grandchild', status='completed',
            parent_execution_id=self.child_a.id,
            root_execution_id=self.parent.id,
        )

        # Unrelated execution under a different root — must not leak.
        self.unrelated = AgentExecution.objects.create(
            agent=self.child_agent, user=self.user,
            task='unrelated', status='completed',
        )

    def _invoke(self, payload):
        result = self.dispatcher.execute_sync(
            'agent_job_status', payload, user_id=self.user.id,
        )
        self.assertTrue(result.ok, result.error_message)
        return result.result

    def test_parent_response_reports_child_and_subtree_counts(self):
        response = self._invoke({'execution_id': str(self.parent.id)})

        self.assertTrue(response['ok'])
        self.assertTrue(response['fanout_available'])
        self.assertEqual(response['execution_id'], str(self.parent.id))
        self.assertIsNone(response['parent_execution_id'])
        self.assertEqual(response['root_execution_id'], str(self.parent.id))
        self.assertEqual(response['child_count'], 3)
        self.assertEqual(response['subtree_count'], 4)  # 3 children + 1 grandchild
        self.assertEqual(len(response['children']), 3)
        self.assertFalse(response['children_truncated'])

        child_names = {c['agent_name'] for c in response['children']}
        self.assertEqual(child_names, {'ResearchAgent', 'TrendAnalysisAgent'})

        first_child = response['children'][0]
        self.assertEqual(set(first_child.keys()), {
            'execution_id', 'agent_name', 'status',
            'created_at', 'completed_at', 'duration_ms',
        })

    def test_child_reports_parent_and_root_lineage(self):
        response = self._invoke({'execution_id': str(self.child_a.id)})

        self.assertTrue(response['fanout_available'])
        self.assertEqual(response['parent_execution_id'], str(self.parent.id))
        self.assertEqual(response['root_execution_id'], str(self.parent.id))
        self.assertEqual(response['child_count'], 1)  # only the grandchild
        self.assertEqual(response['subtree_count'], 4)  # entire tree minus self
        self.assertEqual(len(response['children']), 1)
        self.assertEqual(response['children'][0]['agent_name'], 'TrendAnalysisAgent')

    def test_leaf_reports_zero_fanout(self):
        response = self._invoke({'execution_id': str(self.grandchild.id)})

        self.assertTrue(response['fanout_available'])
        self.assertEqual(response['parent_execution_id'], str(self.child_a.id))
        self.assertEqual(response['root_execution_id'], str(self.parent.id))
        self.assertEqual(response['child_count'], 0)
        self.assertEqual(response['subtree_count'], 4)
        self.assertEqual(response['children'], [])

    def test_legacy_null_root_falls_back_to_self_id(self):
        """Pre-migration-0336 rows have parent=root=NULL; subtree query must
        fall back to self.id, not query for NULL root."""
        response = self._invoke({'execution_id': str(self.unrelated.id)})

        self.assertTrue(response['fanout_available'])
        self.assertIsNone(response['parent_execution_id'])
        self.assertIsNone(response['root_execution_id'])
        self.assertEqual(response['child_count'], 0)
        self.assertEqual(response['subtree_count'], 0)

    def test_missing_lookup_keys_still_reports_fanout_available_false(self):
        result = self.dispatcher.execute_sync(
            'agent_job_status', {}, user_id=self.user.id,
        )
        self.assertTrue(result.ok, result.error_message)
        response = result.result
        self.assertFalse(response['ok'])
        self.assertFalse(response['fanout_available'])
        self.assertIn('requires execution_id OR task_id', response['error'])

    def test_unknown_task_id_reports_fanout_available_false(self):
        result = self.dispatcher.execute_sync(
            'agent_job_status',
            {'task_id': '00000000-0000-0000-0000-000000000000'},
            user_id=self.user.id,
        )
        self.assertTrue(result.ok, result.error_message)
        response = result.result
        # unknown branch either flips to pending (if celery.AsyncResult claims
        # any active state) or to unknown; both must carry fanout_available=false.
        self.assertFalse(response['fanout_available'])

    def test_children_capped_at_20(self):
        """child_count reports true total; children list caps at 20; truncated flag flips."""
        # Add 25 more direct children to push past the cap.
        for i in range(25):
            AgentExecution.objects.create(
                agent=self.child_agent, user=self.user,
                task=f'extra child {i}', status='queued',
                parent_execution_id=self.parent.id,
                root_execution_id=self.parent.id,
            )

        response = self._invoke({'execution_id': str(self.parent.id)})

        self.assertEqual(response['child_count'], 3 + 25)  # true count
        self.assertEqual(len(response['children']), 20)  # capped list
        self.assertTrue(response['children_truncated'])
