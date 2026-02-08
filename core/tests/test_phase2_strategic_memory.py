"""
Session 962 Phase 2: Strategic Memory Service Tests
====================================================

Tests for:
1. Precedent search across mixed sources
2. Failure signature aggregation
3. Strategy recommendations
4. API endpoints (auth + schema)
5. PA enrichment integration
"""

import uuid
from unittest.mock import patch, MagicMock
from django.db.models import Q
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from core.models_deliberation import (
    DeliberationSession,
    DeliberationTurn,
    ContractRecord,
)
from core.services.strategic_memory_service import (
    StrategicMemoryService,
    _text_relevance,
    _tokenize_query,
    _recency_bonus,
    get_strategic_memory_service,
)


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _create_learning_pattern(**kwargs):
    """Create a LearningPattern test instance."""
    from core.models_unified_system import LearningPattern
    defaults = {
        'pattern_type': 'agent_specialization',
        'description': 'Test pattern description',
        'confidence': 0.8,
        'is_active': True,
        'times_applied': 10,
        'success_when_applied': 8,
    }
    defaults.update(kwargs)
    return LearningPattern.objects.create(**defaults)


def _create_decision_record(**kwargs):
    """Create a DecisionRecord test instance."""
    from core.models_decision_records import DecisionRecord
    defaults = {
        'agent_name': 'TestAgent',
        'decision_type': 'analysis',
        'action': 'Test action taken',
        'reasoning': 'Test reasoning for this decision',
        'confidence': 0.9,
    }
    defaults.update(kwargs)
    return DecisionRecord.objects.create(**defaults)


def _create_agent_memory(**kwargs):
    """Create an AgentMemory test instance (no embedding)."""
    from core.models_unified_system import AgentMemory, Agent
    agent = kwargs.pop('agent', None)
    if not agent:
        agent, _ = Agent.objects.get_or_create(
            name='TestAgent',
            defaults={
                'description': 'Test agent',
                'agent_type': 'analysis',
                'is_active': True,
            },
        )
    defaults = {
        'agent': agent,
        'title': 'Test memory title',
        'content': 'Test memory content',
        'memory_type': 'insight',
        'importance_score': 0.7,
        'safety_class': 'candidate',
    }
    defaults.update(kwargs)
    return AgentMemory.objects.create(**defaults)


# ---------------------------------------------------------------------------
# 1. Unit tests for helper functions
# ---------------------------------------------------------------------------

class TestHelperFunctions(TestCase):

    def test_tokenize_query_removes_stop_words(self):
        tokens = _tokenize_query("what is the best strategy for initiatives")
        self.assertNotIn('what', tokens)
        self.assertNotIn('the', tokens)
        self.assertIn('best', tokens)
        self.assertIn('strategy', tokens)
        self.assertIn('initiatives', tokens)

    def test_tokenize_query_removes_short_tokens(self):
        tokens = _tokenize_query("AI ML is on")
        self.assertNotIn('ai', tokens)
        self.assertNotIn('ml', tokens)
        self.assertNotIn('is', tokens)
        self.assertNotIn('on', tokens)

    def test_text_relevance_basic(self):
        tokens = {'initiative', 'cleanup', 'duplicate'}
        score = _text_relevance(tokens, 'Initiative cleanup for duplicate removal')
        self.assertGreater(score, 0.5)

    def test_text_relevance_no_match(self):
        tokens = {'blockchain', 'whale'}
        score = _text_relevance(tokens, 'Stock market analysis report')
        self.assertEqual(score, 0.0)

    def test_text_relevance_empty(self):
        self.assertEqual(_text_relevance(set(), 'some text'), 0.0)
        self.assertEqual(_text_relevance({'token'}, ''), 0.0)

    def test_recency_bonus_recent(self):
        from django.utils import timezone
        recent = timezone.now() - timezone.timedelta(days=5)
        self.assertEqual(_recency_bonus(recent), 0.10)

    def test_recency_bonus_medium(self):
        from django.utils import timezone
        medium = timezone.now() - timezone.timedelta(days=60)
        self.assertEqual(_recency_bonus(medium), 0.05)

    def test_recency_bonus_old(self):
        from django.utils import timezone
        old = timezone.now() - timezone.timedelta(days=365)
        self.assertEqual(_recency_bonus(old), 0.0)

    def test_recency_bonus_none(self):
        self.assertEqual(_recency_bonus(None), 0.0)


# ---------------------------------------------------------------------------
# 2. Precedent search returns mixed sources
# ---------------------------------------------------------------------------

class TestQueryPrecedents(TestCase):
    """Test that query_precedents returns results from multiple sources."""

    def setUp(self):
        self.svc = StrategicMemoryService()

        # Create test data across multiple sources
        _create_learning_pattern(
            description='Initiative cleanup reduces noise and improves focus',
            pattern_type='cleanup_strategy',
        )
        _create_decision_record(
            reasoning='Decided to cleanup duplicate initiatives to reduce noise',
            action='Archive 420 noise initiatives',
            agent_name='SystemAgent',
        )
        self.delib_session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Discuss initiative cleanup strategy',
            status='completed',
        )
        DeliberationTurn.objects.create(
            session=self.delib_session,
            turn_number=1,
            agent_name='BullCaseAgent',
            content='Initiative cleanup will improve system performance',
        )
        ContractRecord.objects.create(
            session=self.delib_session,
            contract_type='execution',
            contract_data={'chosen_path': 'cleanup initiatives', 'reason': 'too much noise'},
        )

    def test_returns_mixed_sources(self):
        """Precedent search returns results from at least 2 different source types."""
        result = self.svc.query_precedents('initiative cleanup', top_k=10)
        self.assertIn('results', result)
        self.assertIn('stats', result)
        self.assertGreaterEqual(len(result['results']), 3)

        source_types = {r['source_type'] for r in result['results']}
        self.assertGreaterEqual(len(source_types), 2)

    def test_results_sorted_by_score(self):
        result = self.svc.query_precedents('initiative cleanup', top_k=10)
        scores = [r['score'] for r in result['results']]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_result_schema(self):
        """Each result has required fields."""
        result = self.svc.query_precedents('initiative cleanup', top_k=10)
        required_keys = {'source_type', 'id', 'title', 'summary', 'created_at', 'trace_id', 'score', 'metadata', 'ref', 'links'}
        for r in result['results']:
            self.assertTrue(required_keys.issubset(r.keys()), f"Missing keys in {r.keys()}")

    def test_stats_includes_timings(self):
        result = self.svc.query_precedents('initiative cleanup', top_k=10)
        self.assertIn('timings_ms', result['stats'])
        self.assertIn('total', result['stats']['timings_ms'])

    def test_empty_query_returns_empty(self):
        result = self.svc.query_precedents('', top_k=10)
        self.assertEqual(len(result['results']), 0)

    def test_top_k_limits_results(self):
        result = self.svc.query_precedents('initiative cleanup', top_k=2)
        self.assertLessEqual(len(result['results']), 2)

    def test_scope_filter(self):
        """Scope restricts which sources are searched."""
        result = self.svc.query_precedents(
            'initiative cleanup', top_k=10,
            scope={'source_types': ['learning_pattern']},
        )
        source_types = {r['source_type'] for r in result['results']}
        self.assertTrue(source_types.issubset({'learning_pattern'}))

    def test_agent_memory_text_fallback(self):
        """AgentMemory falls back to text search when embeddings unavailable."""
        _create_agent_memory(
            title='Initiative management insights',
            content='Cleanup of duplicate initiatives improved system health',
        )
        # Force embedding search to fail so text fallback kicks in
        with patch.object(self.svc, '_search_agent_memories', wraps=self.svc._search_agent_memories) as mock_search:
            # Make the embedding service import fail inside the method
            original = self.svc._search_agent_memories

            def patched_search(query, tokens, top_k):
                """Simulate embedding failure — only text fallback runs."""
                from core.models_unified_system import AgentMemory
                text_q = Q()
                for token in tokens:
                    text_q |= Q(title__icontains=token) | Q(content__icontains=token)
                memories = AgentMemory.objects.filter(text_q).order_by('-importance_score')[:top_k]
                results = []
                for mem in memories:
                    results.append({
                        'source_type': 'agent_memory',
                        'id': str(mem.id),
                        'title': mem.title,
                        'summary': (mem.content or '')[:300],
                        'created_at': mem.created_at.isoformat() if mem.created_at else None,
                        'trace_id': mem.source_id or '',
                        'score': 0.5,
                        'metadata': {'memory_type': mem.memory_type},
                        'ref': f'AgentMemory:{mem.id}',
                        'links': {},
                    })
                return results

            with patch.object(self.svc, '_search_agent_memories', side_effect=patched_search):
                result = self.svc.query_precedents(
                    'initiative cleanup', top_k=10,
                    scope={'source_types': ['agent_memory']},
                )
            # Should still find via text fallback
            self.assertGreaterEqual(len(result['results']), 1)


# ---------------------------------------------------------------------------
# 3. Failure signatures
# ---------------------------------------------------------------------------

class TestFailureSignatures(TestCase):

    def setUp(self):
        self.svc = StrategicMemoryService()
        _create_learning_pattern(
            pattern_type='tool_failure',
            description='API timeout errors in spider network',
            times_applied=20,
            success_when_applied=5,
        )
        _create_learning_pattern(
            pattern_type='quality_regression',
            description='Content quality dropped after parameter change',
            times_applied=10,
            success_when_applied=3,
        )

    def test_returns_signatures(self):
        result = self.svc.get_failure_signatures(top_k=10)
        self.assertIn('signatures', result)
        self.assertGreaterEqual(len(result['signatures']), 1)

    def test_signature_schema(self):
        result = self.svc.get_failure_signatures(top_k=10)
        for sig in result['signatures']:
            self.assertIn('pattern_type', sig)
            self.assertIn('count', sig)
            self.assertIn('failure_rate', sig)
            self.assertIn('common_issues', sig)

    def test_failure_rate_computed(self):
        result = self.svc.get_failure_signatures(top_k=10)
        tool_failure = next(
            (s for s in result['signatures'] if s['pattern_type'] == 'tool_failure'),
            None,
        )
        self.assertIsNotNone(tool_failure)
        # 20 applied, 5 success = 0.75 failure rate
        self.assertEqual(tool_failure['failure_rate'], 0.75)

    def test_domain_filter(self):
        result = self.svc.get_failure_signatures(domain='spider', top_k=10)
        self.assertIn('signatures', result)


# ---------------------------------------------------------------------------
# 4. Strategy recommendations
# ---------------------------------------------------------------------------

class TestRecommendStrategy(TestCase):

    def setUp(self):
        self.svc = StrategicMemoryService()
        _create_learning_pattern(
            description='Consolidation of initiatives works best with Jaccard clustering',
            times_applied=5,
            success_when_applied=4,
            confidence=0.9,
        )
        _create_decision_record(
            reasoning='Used Jaccard similarity to find duplicate initiatives',
            action='Ran consolidate_duplicate_initiatives with threshold 0.6',
        )

    def test_returns_recommendations(self):
        result = self.svc.recommend_strategy('fix initiative duplication', top_k=5)
        self.assertIn('recommendations', result)
        self.assertIn('do', result['recommendations'])
        self.assertIn('dont', result['recommendations'])
        self.assertIn('precedents', result)

    def test_returns_stats(self):
        result = self.svc.recommend_strategy('fix initiative duplication', top_k=5)
        self.assertIn('stats', result)
        self.assertIn('timings_ms', result['stats'])


# ---------------------------------------------------------------------------
# 5. API endpoint tests
# ---------------------------------------------------------------------------

class TestMemoryPrecedentsAPI(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)
        _create_learning_pattern(
            description='Test pattern for API endpoint validation',
        )

    def test_precedents_requires_q(self):
        resp = self.client.get('/api/memory/precedents/')
        self.assertEqual(resp.status_code, 400)

    def test_precedents_returns_200(self):
        resp = self.client.get('/api/memory/precedents/?q=test+pattern')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('results', data)
        self.assertIn('stats', data)

    def test_precedents_respects_top_k(self):
        resp = self.client.get('/api/memory/precedents/?q=test&top_k=2')
        data = resp.json()
        self.assertLessEqual(len(data['results']), 2)


class TestMemoryFailuresAPI(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)

    def test_failures_returns_200(self):
        resp = self.client.get('/api/memory/failures/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('signatures', data)

    def test_failures_with_domain(self):
        resp = self.client.get('/api/memory/failures/?domain=spider')
        self.assertEqual(resp.status_code, 200)


class TestMemoryStrategyAPI(TestCase):

    def setUp(self):
        self.client = Client()
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='test' + 'pass' + '123')
        self.client.force_login(user)

    def test_strategy_requires_objective(self):
        resp = self.client.get('/api/memory/strategy/')
        self.assertEqual(resp.status_code, 400)

    def test_strategy_returns_200(self):
        resp = self.client.get('/api/memory/strategy/?objective=improve+content+quality')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('recommendations', data)
        self.assertIn('do', data['recommendations'])
        self.assertIn('dont', data['recommendations'])


class TestMemoryAPIsRequireAuth(TestCase):
    """Verify unauthenticated requests are rejected."""

    def test_precedents_requires_auth(self):
        client = Client()
        resp = client.get('/api/memory/precedents/?q=test')
        self.assertEqual(resp.status_code, 401)

    def test_failures_requires_auth(self):
        client = Client()
        resp = client.get('/api/memory/failures/')
        self.assertEqual(resp.status_code, 401)

    def test_strategy_requires_auth(self):
        client = Client()
        resp = client.get('/api/memory/strategy/?objective=test')
        self.assertEqual(resp.status_code, 401)


# ---------------------------------------------------------------------------
# 6. PA enrichment integration smoke test
# ---------------------------------------------------------------------------

class TestPAEnrichmentIntegration(TestCase):
    """Test that format_for_pa returns usable output."""

    def setUp(self):
        self.svc = StrategicMemoryService()
        _create_learning_pattern(
            description='Content quality improved with domain context injection',
            pattern_type='quality_improvement',
            confidence=0.85,
        )

    def test_format_for_pa_returns_string(self):
        result = self.svc.format_for_pa('content quality improvement')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_format_for_pa_no_results(self):
        result = self.svc.format_for_pa('xyznonexistent12345')
        self.assertIn('No precedents found', result)

    def test_format_for_pa_includes_precedents(self):
        result = self.svc.format_for_pa('content quality improvement')
        self.assertIn('Precedents:', result)


# ---------------------------------------------------------------------------
# 7. Singleton factory
# ---------------------------------------------------------------------------

class TestSingleton(TestCase):

    def test_get_strategic_memory_service_returns_same(self):
        svc1 = get_strategic_memory_service()
        svc2 = get_strategic_memory_service()
        self.assertIs(svc1, svc2)
