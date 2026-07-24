"""S2930 — pagination + total_count contract for /api/v1/agents/unified-executions/.

Backs the Workspace "Agent Runs" tab. Locks in:

* ``limit`` + ``offset`` slice returns the right rows.
* ``total_count`` reflects the full filtered queryset, not the sliced page.
* ``has_more`` flips false on the last page.
* ``agent_name`` icontains + ``status`` exact filters work.
* Cross-user rows are excluded (per ``scope_queryset_agent_execution``).
* Superuser sees null-user rows (system Celery runs).

Run: python manage.py test core.tests.test_agent_runs_list_endpoint -v2
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.models_unified_system import Agent, AgentExecution


User = get_user_model()

LIST_URL = '/api/v1/agents/unified-executions/'


class AgentRunsListEndpointTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='runs-owner', password='x')
        cls.other = User.objects.create_user(username='runs-other', password='x')
        cls.super = User.objects.create_superuser(
            username='runs-super', password='x', email='s@x.io'
        )
        cls.agent_alpha, _ = Agent.objects.get_or_create(
            name='AlphaTestAgent',
            defaults={'description': 't', 'specialization': 't'},
        )
        cls.agent_beta, _ = Agent.objects.get_or_create(
            name='BetaTestAgent',
            defaults={'description': 't', 'specialization': 't'},
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.owner)
        # Baseline: 5 owner rows on alpha, 3 on beta, 2 for other user, 1 null-user
        for i in range(5):
            AgentExecution.objects.create(
                agent=self.agent_alpha, user=self.owner,
                task=f'alpha task {i}', status='completed',
            )
        for i in range(3):
            AgentExecution.objects.create(
                agent=self.agent_beta, user=self.owner,
                task=f'beta task {i}',
                status='failed' if i == 0 else 'completed',
            )
        for i in range(2):
            AgentExecution.objects.create(
                agent=self.agent_alpha, user=self.other,
                task='other task', status='completed',
            )
        AgentExecution.objects.create(
            agent=self.agent_alpha, user=None,
            task='system celery run', status='completed',
        )

    def test_scoping_excludes_other_users(self):
        resp = self.client.get(LIST_URL, {'limit': 100})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['total_count'], 8)  # 5 alpha + 3 beta, no other/null
        agent_names = {ex['agent_name'] for ex in data['executions']}
        self.assertEqual(agent_names, {'AlphaTestAgent', 'BetaTestAgent'})

    def test_superuser_sees_null_user_rows(self):
        self.client.force_authenticate(user=self.super)
        resp = self.client.get(LIST_URL, {'limit': 100})
        self.assertEqual(resp.status_code, 200)
        # Superuser sees own (0) + null-user (1) = 1 row.
        # NOT other users' rows.
        self.assertEqual(resp.json()['data']['total_count'], 1)

    def test_pagination_limit_and_offset(self):
        resp = self.client.get(LIST_URL, {'limit': 3, 'offset': 0})
        page1 = resp.json()['data']
        self.assertEqual(len(page1['executions']), 3)
        self.assertEqual(page1['total_count'], 8)
        self.assertEqual(page1['offset'], 0)
        self.assertEqual(page1['limit'], 3)
        self.assertTrue(page1['has_more'])

        resp2 = self.client.get(LIST_URL, {'limit': 3, 'offset': 3})
        page2 = resp2.json()['data']
        self.assertEqual(len(page2['executions']), 3)
        self.assertTrue(page2['has_more'])

        resp3 = self.client.get(LIST_URL, {'limit': 3, 'offset': 6})
        page3 = resp3.json()['data']
        self.assertEqual(len(page3['executions']), 2)  # 8 total - 6 offset
        self.assertFalse(page3['has_more'])

        # No overlap between pages.
        ids = (
            [e['id'] for e in page1['executions']]
            + [e['id'] for e in page2['executions']]
            + [e['id'] for e in page3['executions']]
        )
        self.assertEqual(len(ids), len(set(ids)))

    def test_limit_clamped_to_max_200(self):
        resp = self.client.get(LIST_URL, {'limit': 10000})
        self.assertEqual(resp.json()['data']['limit'], 200)

    def test_filter_by_agent_name_icontains(self):
        resp = self.client.get(LIST_URL, {'limit': 100, 'agent_name': 'beta'})
        data = resp.json()['data']
        self.assertEqual(data['total_count'], 3)
        for ex in data['executions']:
            self.assertEqual(ex['agent_name'], 'BetaTestAgent')

    def test_filter_by_status(self):
        resp = self.client.get(LIST_URL, {'limit': 100, 'status': 'failed'})
        data = resp.json()['data']
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['executions'][0]['status'], 'failed')

    def test_ordered_desc_by_created_at(self):
        resp = self.client.get(LIST_URL, {'limit': 100})
        rows = resp.json()['data']['executions']
        created = [r['created_at'] for r in rows]
        self.assertEqual(created, sorted(created, reverse=True))
