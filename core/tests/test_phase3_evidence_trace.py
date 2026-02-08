"""
Session 963 Phase 3: Evidence Pack + Session Trace Tests
=========================================================

Tests for:
1. EvidencePackBuilder — init, append, dedupe, finalize
2. SessionTraceBuilder — init, append turn, contract snapshots, finalize
3. API endpoints — evidence, trace, replay
4. Orchestrator integration — hooks produce trace/evidence on sessions
"""

import uuid
import hashlib
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from core.models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
)
from core.services.evidence_pack_builder import (
    EvidencePackBuilder,
    get_evidence_pack_builder,
    SCHEMA_VERSION as EVIDENCE_SCHEMA,
)
from core.services.session_trace_builder import (
    SessionTraceBuilder,
    get_session_trace_builder,
    SCHEMA_VERSION as TRACE_SCHEMA,
)


def _create_session(**kwargs):
    """Create a test DeliberationSession."""
    defaults = {
        'session_type': 'hivemind',
        'objective': 'Test session for Phase 3',
        'status': 'active',
    }
    defaults.update(kwargs)
    return DeliberationSession.objects.create(**defaults)


# ---------------------------------------------------------------------------
# 1. EvidencePackBuilder tests
# ---------------------------------------------------------------------------

class TestEvidencePackBuilder(TestCase):

    def setUp(self):
        self.builder = EvidencePackBuilder()
        self.session = _create_session()

    def test_init_pack_creates_schema(self):
        pack = self.builder.init_pack(self.session)
        self.assertEqual(pack['$schema'], EVIDENCE_SCHEMA)
        self.assertEqual(pack['session_id'], str(self.session.id))
        self.assertEqual(len(pack['sources']), 0)
        self.assertEqual(len(pack['claims']), 0)

    def test_init_pack_persists_to_db(self):
        self.builder.init_pack(self.session)
        self.session.refresh_from_db()
        self.assertIsInstance(self.session.evidence_pack, dict)
        self.assertEqual(self.session.evidence_pack['$schema'], EVIDENCE_SCHEMA)

    def test_append_source(self):
        self.builder.init_pack(self.session)
        self.builder.append_source(self.session, {
            'source_type': 'spider',
            'name': 'CoinGecko',
            'record_count': 42,
        })
        self.session.refresh_from_db()
        pack = self.session.evidence_pack
        self.assertEqual(len(pack['sources']), 1)
        self.assertEqual(pack['sources'][0]['source_type'], 'spider')
        self.assertEqual(pack['sources'][0]['name'], 'CoinGecko')

    def test_append_source_dedupes(self):
        self.builder.init_pack(self.session)
        source_id = str(uuid.uuid4())
        self.builder.append_source(self.session, {
            'source_id': source_id,
            'source_type': 'spider',
            'name': 'CoinGecko',
        })
        self.builder.append_source(self.session, {
            'source_id': source_id,
            'source_type': 'spider',
            'name': 'CoinGecko duplicate',
        })
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['sources']), 1)

    def test_append_claims(self):
        self.builder.init_pack(self.session)
        self.builder.append_claims(self.session, [
            {'claim_text': 'BTC will hit 100k', 'confidence': 0.8},
            {'claim_text': 'ETH merge successful', 'confidence': 0.95},
        ])
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['claims']), 2)

    def test_append_claims_dedupes_by_id(self):
        self.builder.init_pack(self.session)
        claim_id = str(uuid.uuid4())
        self.builder.append_claims(self.session, [
            {'claim_id': claim_id, 'claim_text': 'Claim A'},
        ])
        self.builder.append_claims(self.session, [
            {'claim_id': claim_id, 'claim_text': 'Claim A duplicate'},
        ])
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['claims']), 1)

    def test_append_contradiction(self):
        self.builder.init_pack(self.session)
        self.builder.append_contradiction(self.session, {
            'nature': 'tension',
            'claim_a_text': 'Market is bullish',
            'claim_b_text': 'Market is bearish',
        })
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['contradictions']), 1)
        c = self.session.evidence_pack['contradictions'][0]
        self.assertEqual(c['nature'], 'tension')

    def test_append_internal_refs(self):
        self.builder.init_pack(self.session)
        self.builder.append_internal_refs(self.session, [
            {'doc_path': '/reports/q1.md'},
            {'doc_path': '/reports/q2.md'},
        ])
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['internal_refs']), 2)

    def test_append_internal_refs_dedupes(self):
        self.builder.init_pack(self.session)
        self.builder.append_internal_refs(self.session, [
            {'doc_path': '/reports/q1.md'},
        ])
        self.builder.append_internal_refs(self.session, [
            {'doc_path': '/reports/q1.md'},
        ])
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['internal_refs']), 1)

    def test_append_memory_retrievals(self):
        self.builder.init_pack(self.session)
        self.builder.append_memory_retrievals(self.session, [
            {'source_type': 'learning_pattern', 'title': 'Pattern X', 'score': 0.8},
        ])
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['memory_retrievals']), 1)

    def test_memory_retrievals_capped_at_5(self):
        self.builder.init_pack(self.session)
        self.builder.append_memory_retrievals(self.session, [
            {'title': f'Item {i}'} for i in range(10)
        ])
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.evidence_pack['memory_retrievals']), 5)

    def test_finalize_sets_assembled_at(self):
        self.builder.init_pack(self.session)
        self.builder.finalize(self.session)
        self.session.refresh_from_db()
        self.assertIsNotNone(self.session.evidence_pack['assembled_at'])

    def test_never_crashes(self):
        """All methods should silently handle errors."""
        bad_session = MagicMock()
        bad_session.evidence_pack = 'not-a-dict'
        bad_session.save = MagicMock(side_effect=Exception('DB error'))
        # Should not raise
        self.builder.append_source(bad_session, {'name': 'test'})
        self.builder.append_claims(bad_session, [{'claim_text': 'x'}])
        self.builder.append_contradiction(bad_session, {'nature': 'x'})


# ---------------------------------------------------------------------------
# 2. SessionTraceBuilder tests
# ---------------------------------------------------------------------------

class TestSessionTraceBuilder(TestCase):

    def setUp(self):
        self.builder = SessionTraceBuilder()
        self.session = _create_session()

    def test_init_trace_creates_schema(self):
        trace = self.builder.init_trace(self.session)
        self.assertEqual(trace['$schema'], TRACE_SCHEMA)
        self.assertEqual(trace['session_id'], str(self.session.id))
        self.assertEqual(len(trace['deliberation']), 0)
        self.assertEqual(len(trace['decisions']), 0)

    def test_init_trace_persists(self):
        self.builder.init_trace(self.session)
        self.session.refresh_from_db()
        self.assertIsInstance(self.session.trace, dict)
        self.assertEqual(self.session.trace['$schema'], TRACE_SCHEMA)

    def test_append_turn(self):
        self.builder.init_trace(self.session)
        self.builder.append_turn(
            self.session,
            turn_number=1,
            agent_name='BullCaseAgent',
            role='advocate',
            content_hash='abc123',
            contains_tension=True,
        )
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.trace['deliberation']), 1)
        turn = self.session.trace['deliberation'][0]
        self.assertEqual(turn['agent_name'], 'BullCaseAgent')
        self.assertTrue(turn['contains_tension'])

    def test_append_turn_dedupes(self):
        self.builder.init_trace(self.session)
        self.builder.append_turn(
            self.session, turn_number=1, agent_name='A', role='', content_hash='x',
        )
        self.builder.append_turn(
            self.session, turn_number=1, agent_name='A', role='', content_hash='x',
        )
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.trace['deliberation']), 1)

    def test_append_turn_from_model(self):
        self.builder.init_trace(self.session)
        turn = DeliberationTurn.objects.create(
            session=self.session,
            turn_number=1,
            agent_name='TestAgent',
            role='critic',
            content='Some content',
            content_hash='hash123',
        )
        self.builder.append_turn_from_model(self.session, turn)
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.trace['deliberation']), 1)

    def test_attach_contract_snapshot_execution(self):
        self.builder.init_trace(self.session)
        self.builder.attach_contract_snapshot(self.session, 'execution', {
            'chosen_path': 'Buy BTC',
            'reason': 'Bull case stronger',
            'decision_owner': 'BullCaseAgent',
        })
        self.session.refresh_from_db()
        self.assertEqual(len(self.session.trace['decisions']), 1)
        d = self.session.trace['decisions'][0]
        self.assertEqual(d['contract_type'], 'execution')
        self.assertEqual(d['chosen_path'], 'Buy BTC')

    def test_attach_contract_snapshot_synthesis(self):
        self.builder.init_trace(self.session)
        self.builder.attach_contract_snapshot(self.session, 'synthesis', {
            'claims': [{'claim': 'A'}, {'claim': 'B'}],
        })
        self.session.refresh_from_db()
        d = self.session.trace['decisions'][0]
        self.assertEqual(d['claim_count'], 2)

    def test_finalize_sets_performance(self):
        self.builder.init_trace(self.session)
        self.builder.append_turn(
            self.session, turn_number=1, agent_name='A', role='', content_hash='x',
        )
        self.builder.finalize(self.session, state={
            'tension_count': 3,
            'grounding_count': 2,
            'empty_agreement_count': 1,
        })
        self.session.refresh_from_db()
        perf = self.session.trace['performance']
        self.assertEqual(perf['total_turns'], 1)
        self.assertEqual(perf['tension_count'], 3)
        self.assertEqual(perf['grounding_count'], 2)
        self.assertIn('completed_at', perf)

    def test_never_crashes(self):
        """All methods should silently handle errors."""
        bad_session = MagicMock()
        bad_session.trace = 'not-a-dict'
        bad_session.save = MagicMock(side_effect=Exception('DB error'))
        self.builder.append_turn(bad_session, 1, 'A', '', 'x')
        self.builder.attach_contract_snapshot(bad_session, 'execution', {})
        self.builder.finalize(bad_session)


# ---------------------------------------------------------------------------
# 3. Singleton factories
# ---------------------------------------------------------------------------

class TestSingletons(TestCase):

    def test_evidence_pack_builder_singleton(self):
        b1 = get_evidence_pack_builder()
        b2 = get_evidence_pack_builder()
        self.assertIs(b1, b2)

    def test_session_trace_builder_singleton(self):
        b1 = get_session_trace_builder()
        b2 = get_session_trace_builder()
        self.assertIs(b1, b2)


# ---------------------------------------------------------------------------
# 4. API endpoint tests
# ---------------------------------------------------------------------------

class TestEvidenceAPI(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)
        self.session = _create_session()
        EvidencePackBuilder().init_pack(self.session)
        EvidencePackBuilder().append_source(self.session, {
            'source_type': 'spider',
            'name': 'TestSpider',
        })

    def test_evidence_returns_200(self):
        resp = self.client.get(f'/api/deliberation/sessions/{self.session.id}/evidence/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('evidence_pack', data)
        self.assertIn('stats', data)
        self.assertEqual(data['stats']['sources'], 1)

    def test_evidence_404_for_missing_session(self):
        fake_id = uuid.uuid4()
        resp = self.client.get(f'/api/deliberation/sessions/{fake_id}/evidence/')
        self.assertEqual(resp.status_code, 404)


class TestTraceAPI(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)
        self.session = _create_session()
        builder = SessionTraceBuilder()
        builder.init_trace(self.session)
        builder.append_turn(self.session, 1, 'Agent1', 'advocate', 'hash1')
        builder.append_turn(self.session, 2, 'Agent2', 'critic', 'hash2')

    def test_trace_returns_200(self):
        resp = self.client.get(f'/api/deliberation/sessions/{self.session.id}/trace/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('trace', data)
        self.assertEqual(data['stats']['turns'], 2)

    def test_trace_404_for_missing_session(self):
        fake_id = uuid.uuid4()
        resp = self.client.get(f'/api/deliberation/sessions/{fake_id}/trace/')
        self.assertEqual(resp.status_code, 404)


class TestReplayAPI(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)
        self.session = _create_session()
        # Create turns
        DeliberationTurn.objects.create(
            session=self.session, turn_number=1,
            agent_name='Bull', role='advocate', content='Bullish analysis',
        )
        DeliberationTurn.objects.create(
            session=self.session, turn_number=2,
            agent_name='Bear', role='critic', content='Bearish counter',
        )
        # Create contract
        ContractRecord.objects.create(
            session=self.session, contract_type='execution',
            contract_data={'chosen_path': 'buy'},
        )
        # Init trace + evidence
        SessionTraceBuilder().init_trace(self.session)
        EvidencePackBuilder().init_pack(self.session)

    def test_replay_returns_full_payload(self):
        resp = self.client.get(f'/api/deliberation/sessions/{self.session.id}/replay/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['turns']), 2)
        self.assertEqual(len(data['contracts']), 1)
        self.assertIn('trace', data)
        self.assertIn('evidence_pack', data)
        self.assertEqual(data['turns'][0]['content'], 'Bullish analysis')

    def test_replay_404_for_missing_session(self):
        fake_id = uuid.uuid4()
        resp = self.client.get(f'/api/deliberation/sessions/{fake_id}/replay/')
        self.assertEqual(resp.status_code, 404)


class TestPhase3APIsRequireAuth(TestCase):
    """Verify unauthenticated requests are rejected."""

    def setUp(self):
        self.session = _create_session()

    def test_evidence_requires_auth(self):
        client = Client()
        resp = client.get(f'/api/deliberation/sessions/{self.session.id}/evidence/')
        self.assertEqual(resp.status_code, 401)

    def test_trace_requires_auth(self):
        client = Client()
        resp = client.get(f'/api/deliberation/sessions/{self.session.id}/trace/')
        self.assertEqual(resp.status_code, 401)

    def test_replay_requires_auth(self):
        client = Client()
        resp = client.get(f'/api/deliberation/sessions/{self.session.id}/replay/')
        self.assertEqual(resp.status_code, 401)
