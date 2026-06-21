"""
Session 1189 Item 1: AC instrumentation for the SpiderContextBuilder →
AgentExecution.input_data['spider_context'] write path.

Background: Session 1188 PRs #2380 (explicit Hot-agent keys) and #2382
(retune ImageAgent/ResearchAgent to real data_type values) shipped with
7d AC watches that need per-category visibility. Without instrumentation
those ACs aren't verifiable. Rigby's PR-prep recon is in deliverable
`d36b8e54-90ca-416c-88c5-e99568952d94`.

This PR has two coupled changes both covered here:

1. `SpiderContextBuilder.build_context_for_agent` now populates
   `items_returned_by_category` and `has_data_by_category` during the
   per-category trending-topics loop. Purely additive — existing
   callers see the same keys plus two new ones.

2. `agent_router.build_spider_context_ac_blob` (new helper) extracts a
   compact AC-ready dict from any spider_context dict. The router call
   site writes it onto `AgentExecution.input_data['spider_context']`
   after `_create_execution_record`. Persistence path is fail-open and
   exercised end-to-end below.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_spider_context_instrumentation -v2 --keepdb
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from core.agent_router import build_spider_context_ac_blob
from core.models_unified_system import Agent, AgentExecution
from core.services.spider_context_builder import SpiderContextBuilder


User = get_user_model()


class BuildContextPerCategoryBreakdownTests(SimpleTestCase):
    """SpiderContextBuilder must populate items_returned_by_category +
    has_data_by_category during the trending-topics loop."""

    def setUp(self):
        self.builder = SpiderContextBuilder()

    def test_per_category_counts_track_intelligence_service_returns(self):
        # Map category -> what intelligence_service.get_trending_topics returns
        per_category_returns = {
            'tech': [{'topic': 'a', 'sources': []}, {'topic': 'b', 'sources': []}],
            'news': [{'topic': 'c', 'sources': []}],
            'science': [],
            'financial': [],
        }

        def fake_trending(category, hours, limit, max_entries):
            return per_category_returns.get(category, [])

        fake_service = type('FakeIntel', (), {
            'get_trending_topics': staticmethod(fake_trending),
            'get_tech_trends': staticmethod(lambda **kw: None),
            'get_creative_trends': staticmethod(lambda **kw: None),
            'get_market_insights': staticmethod(lambda **kw: None),
            'get_job_market_summary': staticmethod(lambda **kw: None),
            'search_spider_data': staticmethod(lambda **kw: None),
        })()
        # Bypass the lazy-load property by setting the underlying attribute
        self.builder._intelligence_service = fake_service

        ctx = self.builder.build_context_for_agent(
            agent_name='ThinkingAgent', task='reason about something',
        )

        self.assertIn('items_returned_by_category', ctx)
        self.assertIn('has_data_by_category', ctx)
        # All 4 ThinkingAgent categories from PR-1 must be present
        for cat in ('tech', 'news', 'science', 'financial'):
            self.assertIn(cat, ctx['items_returned_by_category'])
            self.assertIn(cat, ctx['has_data_by_category'])
        self.assertEqual(ctx['items_returned_by_category']['tech'], 2)
        self.assertEqual(ctx['items_returned_by_category']['news'], 1)
        self.assertEqual(ctx['items_returned_by_category']['science'], 0)
        self.assertTrue(ctx['has_data_by_category']['tech'])
        self.assertTrue(ctx['has_data_by_category']['news'])
        self.assertFalse(ctx['has_data_by_category']['science'])
        self.assertFalse(ctx['has_data_by_category']['financial'])

    def test_per_category_breakdown_handles_intelligence_service_errors(self):
        def fake_trending(category, hours, limit, max_entries):
            if category == 'tech':
                raise RuntimeError('upstream timeout')
            return [{'topic': 'ok', 'sources': []}]

        fake_service = type('FakeIntel', (), {
            'get_trending_topics': staticmethod(fake_trending),
            'get_tech_trends': staticmethod(lambda **kw: None),
            'get_creative_trends': staticmethod(lambda **kw: None),
            'get_market_insights': staticmethod(lambda **kw: None),
            'get_job_market_summary': staticmethod(lambda **kw: None),
            'search_spider_data': staticmethod(lambda **kw: None),
        })()
        self.builder._intelligence_service = fake_service

        ctx = self.builder.build_context_for_agent(
            agent_name='ThinkingAgent', task='x',
        )

        # Tech raised → 0 / False (not missing from dict)
        self.assertEqual(ctx['items_returned_by_category']['tech'], 0)
        self.assertFalse(ctx['has_data_by_category']['tech'])


class BuildSpiderContextAcBlobTests(SimpleTestCase):
    """The router helper must extract the AC-ready blob from a
    spider_context dict (without requiring DB access)."""

    def test_returns_none_for_non_dict_input(self):
        self.assertIsNone(build_spider_context_ac_blob(None))
        self.assertIsNone(build_spider_context_ac_blob('not a dict'))
        self.assertIsNone(build_spider_context_ac_blob([]))

    def test_returns_blob_with_per_category_breakdowns(self):
        spider_ctx = {
            'categories_queried': ['ai_ml', 'design', 'video'],
            'items_returned_by_category': {'ai_ml': 7, 'design': 2, 'video': 0},
            'has_data_by_category': {'ai_ml': True, 'design': True, 'video': False},
            'has_data': True,
            'build_ms': 42,
        }
        blob = build_spider_context_ac_blob(spider_ctx)

        self.assertEqual(blob['enabled'], True)
        self.assertEqual(blob['requested_categories'], ['ai_ml', 'design', 'video'])
        self.assertEqual(blob['resolved_categories'], ['ai_ml', 'design', 'video'])
        self.assertEqual(blob['items_returned_total'], 9)
        self.assertEqual(blob['items_returned_by_category']['ai_ml'], 7)
        self.assertEqual(blob['has_data_by_category']['ai_ml'], True)
        self.assertEqual(blob['has_data_by_category']['video'], False)
        self.assertEqual(blob['has_data'], True)
        self.assertEqual(blob['build_ms'], 42)

    def test_blob_reports_disabled_when_no_categories(self):
        blob = build_spider_context_ac_blob({})
        self.assertEqual(blob['enabled'], False)
        self.assertEqual(blob['requested_categories'], [])
        self.assertEqual(blob['items_returned_total'], 0)
        self.assertEqual(blob['has_data'], False)

    def test_blob_reports_alias_divergence(self):
        """PR-3A: when CATEGORY_ALIASES expanded a value (e.g., `creative`
        → `[design, visual_trends, video]`), the spider_context dict
        carries BOTH `categories_requested` (pre-alias) and
        `categories_queried` (post-alias). The blob must surface the
        divergence so AC consumers can see what was asked vs what
        actually got queried."""
        spider_ctx = {
            'categories_requested': ['creative', 'tech'],
            'categories_queried': ['design', 'visual_trends', 'video', 'tech'],
            'items_returned_by_category': {'design': 2, 'video': 0, 'tech': 5, 'visual_trends': 1},
            'has_data_by_category': {'design': True, 'video': False, 'tech': True, 'visual_trends': True},
            'has_data': True,
            'build_ms': 33,
        }
        blob = build_spider_context_ac_blob(spider_ctx)
        self.assertEqual(blob['requested_categories'], ['creative', 'tech'])
        self.assertEqual(
            blob['resolved_categories'],
            ['design', 'visual_trends', 'video', 'tech'],
        )

    def test_blob_falls_back_when_categories_requested_missing(self):
        """Backward compat: pre-PR-3A spider_context dicts only had
        `categories_queried`. The blob should default `requested_categories`
        to the queried list when `categories_requested` is absent."""
        spider_ctx = {
            'categories_queried': ['tech', 'news'],
            'has_data': True,
            'items_returned_by_category': {},
            'has_data_by_category': {},
        }
        blob = build_spider_context_ac_blob(spider_ctx)
        self.assertEqual(blob['requested_categories'], ['tech', 'news'])
        self.assertEqual(blob['resolved_categories'], ['tech', 'news'])


class BlobPersistsOnAgentExecutionTests(TestCase):
    """Persistence check: blob written into AgentExecution.input_data
    survives save() + refresh_from_db. Exercises the same write pattern
    the router uses without going through a full dispatch (which would
    require LLM calls)."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='spider-ac', email='ac@example.com', password='x',
        )
        cls.agent, _ = Agent.objects.get_or_create(
            name='ThinkingAgent',
            defaults={'agent_type': 'routable', 'description': 'test',
                      'specialization': '', 'is_active': True},
        )

    def test_blob_round_trips_through_input_data(self):
        execution = AgentExecution.objects.create(
            agent=self.agent, user=self.user,
            task='instrumentation persistence test',
            status='in_progress',
            trace_id=uuid.uuid4(),
            owner_agent='ThinkingAgent',
            input_data={'something_else': 'preserved'},
        )

        spider_ctx = {
            'categories_queried': ['ai_ml', 'design'],
            'items_returned_by_category': {'ai_ml': 5, 'design': 3},
            'has_data_by_category': {'ai_ml': True, 'design': True},
            'has_data': True,
            'build_ms': 11,
        }
        blob = build_spider_context_ac_blob(spider_ctx)
        execution.input_data['spider_context'] = blob
        execution.save(update_fields=['input_data'])

        execution.refresh_from_db()
        # Pre-existing keys must not be clobbered
        self.assertEqual(execution.input_data['something_else'], 'preserved')
        # Blob round-tripped intact
        persisted = execution.input_data['spider_context']
        self.assertEqual(persisted['requested_categories'], ['ai_ml', 'design'])
        self.assertEqual(persisted['items_returned_by_category']['ai_ml'], 5)
        self.assertEqual(persisted['has_data_by_category']['design'], True)
        self.assertEqual(persisted['items_returned_total'], 8)
        self.assertEqual(persisted['build_ms'], 11)
