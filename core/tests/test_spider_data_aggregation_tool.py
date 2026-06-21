"""
Session 1189 Item 3: tests for spider_data_aggregation_tool v1.

Builds real SpiderData fixtures (not mocks — Rigby's spec called for
real DB fixtures because correctness hinges on ORM aggregation /
group-by behavior, and mocking the ORM would just re-validate our
own mock).

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_spider_data_aggregation_tool -v2 --keepdb
"""

import uuid
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import SpiderData
from core.services.spider_data_aggregation_tool import (
    DAYS_BACK_MAX,
    TOP_SPIDERS_LIMIT_MAX,
    aggregate_spider_data,
    handle_spider_data_aggregation,
)


def _make_spider_row(
    data_type: str,
    spider_name: str,
    is_actionable: bool = True,
    days_ago: int = 1,
) -> SpiderData:
    """Tight fixture builder — only sets fields the aggregation reads."""
    created_at = timezone.now() - timedelta(days=days_ago)
    row = SpiderData.objects.create(
        spider_name=spider_name,
        source_url=f'https://example.com/{uuid.uuid4().hex[:8]}',
        data_type=data_type,
        is_actionable=is_actionable,
        raw_data={},
        processed_data={},
    )
    # created_at is auto_now_add — overwrite for windowed tests
    SpiderData.objects.filter(pk=row.pk).update(created_at=created_at)
    row.refresh_from_db()
    return row


class AggregateSpiderDataTests(TestCase):
    """Pure-function tests against real DB rows."""

    @classmethod
    def setUpTestData(cls):
        # 5 in-window financial rows from 3 spiders (2 actionable per top spider)
        for _ in range(3):
            _make_spider_row('financial', 'finnhub', is_actionable=True, days_ago=2)
        for _ in range(2):
            _make_spider_row('financial', 'yahoo_finance', is_actionable=True, days_ago=3)
        _make_spider_row('financial', 'polygon', is_actionable=False, days_ago=4)

        # 2 in-window ai_ml rows from 1 spider
        for _ in range(2):
            _make_spider_row('ai_ml', 'huggingface', is_actionable=True, days_ago=1)

        # 1 in-window design row, NOT actionable
        _make_spider_row('design', 'dribbble', is_actionable=False, days_ago=5)

        # 1 stale ai_ml row OUTSIDE the 30d window — must never appear
        _make_spider_row('ai_ml', 'kaggle', is_actionable=True, days_ago=60)

    def test_actionable_only_excludes_non_actionable_buckets(self):
        result = aggregate_spider_data(days_back=30, actionable_only=True)
        types_returned = {b['data_type'] for b in result['by_data_type']}
        # design only has non-actionable rows in-window → excluded
        self.assertNotIn('design', types_returned)
        # financial + ai_ml both have actionable rows
        self.assertIn('financial', types_returned)
        self.assertIn('ai_ml', types_returned)

    def test_actionable_false_includes_design(self):
        result = aggregate_spider_data(days_back=30, actionable_only=False)
        types_returned = {b['data_type'] for b in result['by_data_type']}
        self.assertIn('design', types_returned)

    def test_window_excludes_stale_rows(self):
        # 30d window excludes the 60-day-old ai_ml row from kaggle
        result = aggregate_spider_data(days_back=30, actionable_only=True)
        ai_ml = next(b for b in result['by_data_type'] if b['data_type'] == 'ai_ml')
        self.assertEqual(ai_ml['actionable_count'], 2)
        self.assertEqual(ai_ml['total_count'], 2)
        # Stretching the window picks up the stale row
        long_result = aggregate_spider_data(days_back=90, actionable_only=True)
        long_ai_ml = next(
            b for b in long_result['by_data_type'] if b['data_type'] == 'ai_ml'
        )
        self.assertEqual(long_ai_ml['actionable_count'], 3)

    def test_data_types_filter_narrows_results(self):
        result = aggregate_spider_data(
            days_back=30, data_types=['ai_ml'], actionable_only=True
        )
        types_returned = {b['data_type'] for b in result['by_data_type']}
        self.assertEqual(types_returned, {'ai_ml'})

    def test_spider_names_filter_narrows_results(self):
        result = aggregate_spider_data(
            days_back=30, spider_names=['finnhub'], actionable_only=True
        )
        # Only finnhub's financial rows should appear
        self.assertEqual(len(result['by_data_type']), 1)
        bucket = result['by_data_type'][0]
        self.assertEqual(bucket['data_type'], 'financial')
        self.assertEqual(bucket['actionable_count'], 3)

    def test_top_spiders_limit_respected_and_sorted(self):
        result = aggregate_spider_data(
            days_back=30, actionable_only=True,
            include_top_spiders=True, top_spiders_limit=1,
        )
        financial = next(
            b for b in result['by_data_type'] if b['data_type'] == 'financial'
        )
        self.assertEqual(len(financial['top_spiders']), 1)
        # finnhub (3 actionable) ranks above yahoo_finance (2)
        self.assertEqual(financial['top_spiders'][0]['spider_name'], 'finnhub')
        self.assertEqual(financial['top_spiders'][0]['actionable_count'], 3)

    def test_include_top_spiders_false_omits_top_spiders_key(self):
        result = aggregate_spider_data(
            days_back=30, actionable_only=True, include_top_spiders=False
        )
        for bucket in result['by_data_type']:
            self.assertNotIn('top_spiders', bucket)

    def test_totals_block_present_and_correct(self):
        result = aggregate_spider_data(days_back=30, actionable_only=True)
        totals = result['totals']
        # 3 finnhub + 2 yahoo + 2 huggingface = 7 actionable in-window
        self.assertEqual(totals['actionable_count'], 7)
        # plus 1 polygon (non-actionable financial) + 1 dribbble (non-actionable design) = 9 total
        self.assertEqual(totals['total_count'], 9)
        # 3 distinct data_types in-window: financial, ai_ml, design
        self.assertEqual(totals['distinct_data_types'], 3)
        # 4 distinct spiders in-window: finnhub, yahoo_finance, polygon, huggingface, dribbble = 5
        self.assertEqual(totals['distinct_spiders'], 5)

    def test_include_totals_false_omits_totals_block(self):
        result = aggregate_spider_data(days_back=30, include_totals=False)
        self.assertNotIn('totals', result)

    def test_response_contract_shape(self):
        result = aggregate_spider_data(days_back=30)
        for key in ('window', 'filters', 'by_data_type', 'generated_at', 'totals'):
            self.assertIn(key, result)
        for key in ('days_back', 'start_ts', 'end_ts'):
            self.assertIn(key, result['window'])
        for key in ('actionable_only', 'data_types', 'spider_names'):
            self.assertIn(key, result['filters'])

    def test_days_back_clamped_to_max(self):
        result = aggregate_spider_data(days_back=DAYS_BACK_MAX + 50)
        self.assertEqual(result['window']['days_back'], DAYS_BACK_MAX)

    def test_top_spiders_limit_clamped_to_max(self):
        # Doesn't matter that we don't have that many spiders — just
        # confirm the clamp doesn't blow up the query.
        aggregate_spider_data(
            days_back=30, top_spiders_limit=TOP_SPIDERS_LIMIT_MAX + 10
        )


class HandleSpiderDataAggregationTests(TestCase):
    """Dispatcher-entry tests for the v1 handler."""

    def test_unknown_action_returns_structured_error(self):
        result = handle_spider_data_aggregation(
            'spider_data_aggregation_tool',
            {'action': 'samples'},
            user_id=None, trace_id='test',
        )
        self.assertFalse(result['ok'])
        self.assertIn("'samples'", result['error'])

    def test_default_action_resolves_to_aggregate(self):
        result = handle_spider_data_aggregation(
            'spider_data_aggregation_tool', {}, user_id=None, trace_id='test',
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'aggregate')
        self.assertIn('by_data_type', result)

    def test_handler_coerces_scalar_data_types_to_list(self):
        _make_spider_row('ai_ml', 'huggingface', is_actionable=True, days_ago=1)
        result = handle_spider_data_aggregation(
            'spider_data_aggregation_tool',
            {'action': 'aggregate', 'data_types': 'ai_ml'},
            user_id=None, trace_id='test',
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['filters']['data_types'], ['ai_ml'])
