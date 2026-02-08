"""
Session 962 Phase 1: Deliberation API Endpoint Tests
=====================================================

Tests the read-only API endpoints for deliberation sessions, turns, contracts,
and doc versions.
"""

import uuid
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from core.models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
    DocVersion,
)


class TestDeliberationSessionsAPI(TestCase):
    """Tests for /api/deliberation/sessions/ endpoints."""

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)
        self.session1 = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Debate AI regulation',
            participants=[
                {'agent_name': 'BullCaseAgent', 'role': 'advocate'},
                {'agent_name': 'BearCaseAgent', 'role': 'critic'},
            ],
            status='completed',
            trace_id='trace-abc-123',
        )
        self.session2 = DeliberationSession.objects.create(
            session_type='agent',
            objective='Solo analysis task',
            status='active',
        )

    def test_list_sessions(self):
        resp = self.client.get('/api/deliberation/sessions/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 2)
        self.assertIn('sessions', data)

    def test_list_sessions_filter_status(self):
        resp = self.client.get('/api/deliberation/sessions/?status=completed')
        data = resp.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['sessions'][0]['status'], 'completed')

    def test_list_sessions_filter_type(self):
        resp = self.client.get('/api/deliberation/sessions/?session_type=agent')
        data = resp.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['sessions'][0]['session_type'], 'agent')

    def test_list_sessions_search(self):
        resp = self.client.get('/api/deliberation/sessions/?q=regulation')
        data = resp.json()
        self.assertEqual(data['count'], 1)

    def test_list_sessions_limit(self):
        resp = self.client.get('/api/deliberation/sessions/?limit=1')
        data = resp.json()
        self.assertEqual(data['count'], 1)

    def test_session_detail(self):
        resp = self.client.get(f'/api/deliberation/sessions/{self.session1.id}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['id'], str(self.session1.id))
        self.assertEqual(data['session_type'], 'hivemind')
        self.assertEqual(data['objective'], 'Debate AI regulation')
        self.assertEqual(len(data['participants']), 2)

    def test_session_detail_not_found(self):
        fake_id = uuid.uuid4()
        resp = self.client.get(f'/api/deliberation/sessions/{fake_id}/')
        self.assertEqual(resp.status_code, 404)

    def test_session_list_includes_counts(self):
        DeliberationTurn.objects.create(
            session=self.session1, turn_number=1,
            agent_name='Agent1', content='Turn 1',
        )
        ContractRecord.objects.create(
            session=self.session1, contract_type='execution',
            contract_data={'test': True},
        )
        resp = self.client.get('/api/deliberation/sessions/')
        data = resp.json()
        session_data = next(
            s for s in data['sessions'] if s['id'] == str(self.session1.id)
        )
        self.assertEqual(session_data['turn_count'], 1)
        self.assertEqual(session_data['contract_count'], 1)


class TestDeliberationTurnsAPI(TestCase):
    """Tests for /api/deliberation/sessions/<uuid>/turns/ endpoint."""

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)
        self.session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Turn API test',
            status='completed',
        )
        for i in range(1, 4):
            DeliberationTurn.objects.create(
                session=self.session,
                turn_number=i,
                agent_name=f'Agent{i}',
                role='advocate' if i % 2 else 'critic',
                content=f'Full content for turn {i} with lots of detail ' * 20,
            )

    def test_list_turns(self):
        resp = self.client.get(f'/api/deliberation/sessions/{self.session.id}/turns/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 3)
        # Default truncates to 500 chars
        self.assertLessEqual(len(data['turns'][0]['content']), 500)

    def test_list_turns_full(self):
        resp = self.client.get(
            f'/api/deliberation/sessions/{self.session.id}/turns/?full=1'
        )
        data = resp.json()
        # Full content should be longer than 500
        self.assertGreater(len(data['turns'][0]['content']), 500)

    def test_turns_ordered(self):
        resp = self.client.get(f'/api/deliberation/sessions/{self.session.id}/turns/')
        data = resp.json()
        turn_numbers = [t['turn_number'] for t in data['turns']]
        self.assertEqual(turn_numbers, [1, 2, 3])


class TestDeliberationContractsAPI(TestCase):
    """Tests for /api/deliberation/sessions/<uuid>/contracts/ endpoint."""

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)
        self.session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Contract API test',
            status='completed',
        )
        ContractRecord.objects.create(
            session=self.session,
            contract_type='execution',
            contract_data={
                'chosen_path': 'Buy AAPL',
                'reason': 'Strong fundamentals',
            },
        )
        ContractRecord.objects.create(
            session=self.session,
            contract_type='synthesis',
            contract_data={'claims': ['Claim A']},
        )

    def test_list_contracts(self):
        resp = self.client.get(
            f'/api/deliberation/sessions/{self.session.id}/contracts/'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 2)

    def test_contract_data_included(self):
        resp = self.client.get(
            f'/api/deliberation/sessions/{self.session.id}/contracts/'
        )
        data = resp.json()
        types = {c['contract_type'] for c in data['contracts']}
        self.assertEqual(types, {'execution', 'synthesis'})


class TestDocVersionsAPI(TestCase):
    """Tests for /api/docs/versions/ endpoints."""

    def setUp(self):
        self.client = Client()
        self.dv1 = DocVersion.objects.create(
            doc_path='docs/architecture.md',
            version_number=1,
            content_hash='hash1',
            content_snapshot='Architecture v1 content',
            author_agent='FullStackDeveloperAgent',
        )
        self.dv2 = DocVersion.objects.create(
            doc_path='docs/architecture.md',
            version_number=2,
            content_hash='hash2',
            content_snapshot='Architecture v2 content',
            author_agent='EditorAgent',
            change_reason='Updated structure section',
        )

    def test_list_versions(self):
        resp = self.client.get('/api/docs/versions/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 2)

    def test_list_versions_filter_by_path(self):
        DocVersion.objects.create(
            doc_path='docs/agents.md', version_number=1,
            content_hash='h3', content_snapshot='other',
        )
        resp = self.client.get('/api/docs/versions/?doc_path=architecture')
        data = resp.json()
        self.assertEqual(data['count'], 2)

    def test_version_detail(self):
        resp = self.client.get(f'/api/docs/versions/{self.dv2.id}/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['version_number'], 2)
        self.assertEqual(data['content_snapshot'], 'Architecture v2 content')
        self.assertEqual(data['author_agent'], 'EditorAgent')
        self.assertEqual(data['change_reason'], 'Updated structure section')

    def test_version_detail_not_found(self):
        resp = self.client.get('/api/docs/versions/99999/')
        self.assertEqual(resp.status_code, 404)
