"""
Session 2971: Signal Intelligence UI backend endpoint tests.

Covers:
  - core/services/spider_feed.query_spider_feed / get_spider_feed_detail
  - core/views/signals_ui.signals_aggregate / signals_feed / signals_embedding_coverage
  - Extended SignalClusterViewSet filters (window_hours, min_confidence,
    source_spider, query) at /api/v1/signal-clusters/

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_signals_ui_api -v2 --keepdb
"""

import uuid
from datetime import timedelta
from typing import Optional
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models_signal_intelligence import SignalCluster
from core.models_unified_system import LegacySpiderData
from core.services.spider_feed import (
    _embedding_status,
    get_spider_feed_detail,
    query_spider_feed,
)


User = get_user_model()


_UNSET = object()


def _make_spider_row(
    *,
    spider_name: str = 'reddit',
    data_type: str = 'news',
    is_actionable: bool = True,
    days_ago: int = 1,
    embedding_text: str = 'sample embedding text',
    source_url: Optional[str] = None,
    raw_data=_UNSET,
) -> LegacySpiderData:
    created_at = timezone.now() - timedelta(days=days_ago)
    # `raw_data or {...}` would treat `{}` as unset — S2975 tests need to
    # write literally-empty raw_data to model the ghost-row state, so use
    # a sentinel to distinguish "caller passed nothing" from "caller passed {}".
    if raw_data is _UNSET:
        raw_data = {'title': f'{spider_name} item'}
    row = LegacySpiderData.objects.create(
        spider_name=spider_name,
        source_url=source_url or f'https://example.com/{uuid.uuid4().hex[:8]}',
        data_type=data_type,
        is_actionable=is_actionable,
        raw_data=raw_data,
        processed_data={},
        embedding_text=embedding_text,
    )
    LegacySpiderData.objects.filter(pk=row.pk).update(created_at=created_at)
    row.refresh_from_db()
    return row


class QuerySpiderFeedTests(TestCase):
    """Pure-function tests over LegacySpiderData."""

    @classmethod
    def setUpTestData(cls):
        # 4 recent rows spanning multiple types + spiders
        _make_spider_row(spider_name='reddit', data_type='news', days_ago=1)
        _make_spider_row(spider_name='reddit', data_type='news', days_ago=2)
        _make_spider_row(spider_name='finnhub', data_type='financial', days_ago=1)
        _make_spider_row(spider_name='huggingface', data_type='ai_ml', days_ago=1)
        # marked-empty
        _make_spider_row(spider_name='reddit', data_type='news', days_ago=1,
                         embedding_text='[NO_ITEMS]')
        # missing embedding
        _make_spider_row(spider_name='reddit', data_type='news', days_ago=1,
                         embedding_text='')
        # stale row (outside typical windows)
        _make_spider_row(spider_name='reddit', data_type='news', days_ago=60,
                         embedding_text='stale row')

    def test_default_returns_all_rows_within_max(self):
        result = query_spider_feed()
        assert result['total'] == 7
        assert len(result['items']) == 7
        assert result['has_more'] is False

    def test_pagination_shape(self):
        result = query_spider_feed(limit=2, offset=0)
        assert result['limit'] == 2
        assert result['offset'] == 0
        assert len(result['items']) == 2
        assert result['total'] == 7
        assert result['has_more'] is True
        # Order: newest first
        assert result['items'][0]['created_at'] >= result['items'][1]['created_at']

    def test_data_types_filter(self):
        result = query_spider_feed(data_types=['financial'])
        assert result['total'] == 1
        assert result['items'][0]['data_type'] == 'financial'

    def test_spider_name_icontains(self):
        result = query_spider_feed(spider_name='REDDIT')  # icontains
        assert result['total'] == 5  # 5 reddit rows (incl. marked_empty + missing + stale)

    def test_window_hours_excludes_stale(self):
        # 72h window keeps all recent rows (days_ago<=2) and drops days_ago=60.
        # 48h would race against boundary rows because query time > fixture time.
        result = query_spider_feed(window_hours=72)
        assert result['total'] == 6  # 7 total - 1 stale

    def test_embedding_status_present_filter(self):
        # Excludes marked_empty ('[NO_ITEMS]') AND missing ('')
        result = query_spider_feed(embedding_status='present')
        assert result['total'] == 5

    def test_embedding_status_marked_empty_filter(self):
        result = query_spider_feed(embedding_status='marked_empty')
        assert result['total'] == 1
        assert result['items'][0]['embedding_status'] == 'marked_empty'

    def test_embedding_status_missing_filter(self):
        result = query_spider_feed(embedding_status='missing')
        assert result['total'] == 1
        assert result['items'][0]['embedding_status'] == 'empty'  # empty string in DB

    def test_actionable_only(self):
        _make_spider_row(spider_name='reddit', is_actionable=False, days_ago=1)
        result = query_spider_feed(actionable_only=True)
        assert all(item['is_actionable'] for item in result['items'])

    def test_item_shape(self):
        result = query_spider_feed(limit=1)
        item = result['items'][0]
        assert set(item.keys()) >= {
            'id', 'spider_name', 'data_type', 'source_url',
            'is_actionable', 'embedding_status', 'embedding_text',
            'preview', 'created_at',
        }

    def test_embedding_status_bucketing(self):
        assert _embedding_status(None) == 'missing'
        assert _embedding_status('') == 'empty'
        assert _embedding_status('[NO_ITEMS]') == 'marked_empty'
        assert _embedding_status('real content') == 'present'


class GetSpiderFeedDetailTests(TestCase):
    def test_returns_full_row(self):
        row = _make_spider_row(raw_data={'x': 1}, embedding_text='hello')
        detail = get_spider_feed_detail(str(row.id))
        assert detail is not None
        assert detail['id'] == str(row.id)
        assert detail['raw_data'] == {'x': 1}
        assert detail['embedding_text'] == 'hello'

    def test_returns_none_for_missing(self):
        assert get_spider_feed_detail(str(uuid.uuid4())) is None


class SignalsEndpointTests(TestCase):
    """Wire-through smoke: authenticated user hits each endpoint + shape holds."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='signals_tester', password='pw')  # type: ignore[attr-defined]
        _make_spider_row(spider_name='reddit', data_type='news', days_ago=1)
        _make_spider_row(spider_name='finnhub', data_type='financial', days_ago=1)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_aggregate_returns_by_data_type(self):
        resp = self.client.get('/api/signals/aggregate/', {'days_back': 7})
        assert resp.status_code == 200, resp.content
        body = resp.json()
        assert 'by_data_type' in body
        assert 'window' in body

    def test_aggregate_default_data_types(self):
        # No data_types param → 4 default primary feeds applied
        resp = self.client.get('/api/signals/aggregate/')
        assert resp.status_code == 200
        assert resp.json()['filters']['data_types'] == ['news', 'financial', 'tech', 'ai_ml']

    def test_feed_returns_paginated_items(self):
        resp = self.client.get('/api/signals/feed/', {'limit': 5})
        assert resp.status_code == 200, resp.content
        body = resp.json()
        assert 'items' in body
        assert 'total' in body
        assert 'has_more' in body

    def test_feed_filter_by_data_type(self):
        resp = self.client.get('/api/signals/feed/', {'data_types': 'financial'})
        assert resp.status_code == 200
        body = resp.json()
        assert all(item['data_type'] == 'financial' for item in body['items'])

    def test_feed_detail_404_for_missing(self):
        resp = self.client.get(f'/api/signals/feed/{uuid.uuid4()}/')
        assert resp.status_code == 404

    def test_feed_detail_returns_row(self):
        row = _make_spider_row(spider_name='reddit', raw_data={'y': 2})
        resp = self.client.get(f'/api/signals/feed/{row.id}/')
        assert resp.status_code == 200, resp.content
        assert resp.json()['id'] == str(row.id)

    def test_embedding_coverage_returns_stats_shape(self):
        with mock.patch('core.services.spider_semantic_search.get_spider_semantic_search') as m:
            m.return_value.get_embedding_stats.return_value = {
                # S2972 new fields
                'total': 100, 'present': 40, 'pending_eligible': 5,
                'ineligible_empty': 55, 'embeddable_total': 45,
                'embeddable_coverage_percent': 88.9,
                # legacy compat
                'total_entries': 100, 'with_embedding': 40, 'marked_empty': 0,
                'pending': 60, 'searchable': 40, 'coverage_percent': 40.0,
                'recent_24h': {
                    'total': 10, 'embedded': 4, 'marked_no_items': 3,
                    'still_pending': 3, 'no_items_rate': 30.0,
                    'with_embedding': 4,
                },
            }
            resp = self.client.get('/api/signals/embedding-coverage/')
        assert resp.status_code == 200, resp.content
        body = resp.json()
        # Both new + legacy shapes surface end-to-end.
        assert body['coverage_percent'] == 40.0
        assert body['embeddable_coverage_percent'] == 88.9
        assert body['pending_eligible'] == 5
        assert body['ineligible_empty'] == 55
        assert body['recent_24h']['no_items_rate'] == 30.0

    def test_all_endpoints_require_auth(self):
        anon = APIClient()
        for path in [
            '/api/signals/aggregate/',
            '/api/signals/feed/',
            '/api/signals/embedding-coverage/',
        ]:
            resp = anon.get(path)
            assert resp.status_code in (401, 403), f'{path}: {resp.status_code}'


class EmbeddingCoverageStatsTests(TestCase):
    """S2972: `SpiderSemanticSearch.get_embedding_stats` bucket split.

    Isolated TestCase (no shared setUpTestData) so we don't collide with
    LegacySpiderData rows the SignalsEndpointTests fixtures create.
    """

    def test_pending_eligible_excludes_marked_no_items(self):
        """The primary S2972 assertion: `pending_eligible` counts NULL
        embeddings NOT flagged [NO_ITEMS] — i.e., the actual backfill
        queue. `ineligible_empty` counts NULL rows already visited by
        backfill and marked empty."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        # 1 present (has embedding vector)
        present_row = _make_spider_row(spider_name='reddit', embedding_text='real content')
        LegacySpiderData.objects.filter(pk=present_row.pk).update(
            embedding=[0.1] * 1536,
        )
        # 1 pending_eligible (NULL embedding, NOT [NO_ITEMS])
        _make_spider_row(spider_name='reddit', embedding_text='pending content')
        # 1 ineligible_empty (NULL embedding, marked [NO_ITEMS])
        _make_spider_row(spider_name='reddit', embedding_text='[NO_ITEMS]')

        stats = get_spider_semantic_search().get_embedding_stats()

        assert stats['total'] == 3
        assert stats['present'] == 1
        assert stats['pending_eligible'] == 1
        assert stats['ineligible_empty'] == 1
        assert stats['embeddable_total'] == 2
        # embeddable coverage = 1 present / (1 present + 1 pending_eligible) = 50%
        assert stats['embeddable_coverage_percent'] == 50.0

    def test_pending_invariant_equals_split_sum(self):
        """Rigby T1 fold invariant: legacy `pending` equals
        `pending_eligible + ineligible_empty + stale_empty_raw_data_total`.
        Locks the backward-compat contract in place so future edits can't
        silently drift the sum. S2975 extended the sum with a stale bucket."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        _make_spider_row(embedding_text='real content')  # pending_eligible
        _make_spider_row(embedding_text='another one')   # pending_eligible
        _make_spider_row(embedding_text='[NO_ITEMS]')    # ineligible_empty
        _make_spider_row(embedding_text='[NO_ITEMS]')    # ineligible_empty
        _make_spider_row(embedding_text='[NO_ITEMS]')    # ineligible_empty
        # S2975 stale-ghost rows
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]', raw_data={})
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]', raw_data={})

        stats = get_spider_semantic_search().get_embedding_stats()

        assert stats['pending'] == (
            stats['pending_eligible']
            + stats['ineligible_empty']
            + stats['stale_empty_raw_data_total']
        )
        # Legacy fields still equal new ones exactly (no more sampling drift).
        assert stats['with_embedding'] == stats['present']
        assert stats['searchable'] == stats['present']
        assert stats['total_entries'] == stats['total']

    def test_embeddable_coverage_100_percent_when_no_eligible(self):
        """S2972: when there's no eligible pending queue, embeddable coverage
        reads 100% (not 0/0 crash). Prevents the 'coverage regressed from
        25% to 0%' misread that motivated this arc — the OLD `coverage_percent`
        still reports 0% for the same state so both perspectives coexist."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        # Only [NO_ITEMS] rows — nothing embeddable.
        _make_spider_row(embedding_text='[NO_ITEMS]')
        _make_spider_row(embedding_text='[NO_ITEMS]')

        stats = get_spider_semantic_search().get_embedding_stats()
        assert stats['pending_eligible'] == 0
        assert stats['embeddable_total'] == 0
        # No embeddable rows → treat as fully covered (0/0 doesn't degrade).
        assert stats['embeddable_coverage_percent'] == 100.0
        # But total coverage is still 0% (no rows have embeddings).
        assert stats['coverage_percent'] == 0

    def test_recent_24h_bucketing(self):
        """S2972 last-24h intake quality: split fresh rows into embedded /
        marked_no_items / still_pending, plus the no_items_rate that the UI
        needs to signal a pipeline-health regression."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        # 4 rows created 1 day ago (inside 24h window)
        r1 = _make_spider_row(embedding_text='embedded', days_ago=0)
        LegacySpiderData.objects.filter(pk=r1.pk).update(embedding=[0.1] * 1536)
        _make_spider_row(embedding_text='[NO_ITEMS]', days_ago=0)
        _make_spider_row(embedding_text='[NO_ITEMS]', days_ago=0)
        _make_spider_row(embedding_text='still pending', days_ago=0)
        # Old row outside window
        _make_spider_row(embedding_text='old', days_ago=10)

        stats = get_spider_semantic_search().get_embedding_stats()
        r24 = stats['recent_24h']
        assert r24['total'] == 4
        assert r24['embedded'] == 1
        assert r24['marked_no_items'] == 2
        assert r24['still_pending'] == 1
        assert r24['no_items_rate'] == 50.0  # 2 of 4
        # Legacy alias still populated.
        assert r24['with_embedding'] == 1


class NoItemsPolicyTests(TestCase):
    """S2973: `no_items_policy` module + `get_embedding_stats` breakdown."""

    def test_policy_defaults_are_conservative(self):
        """The policy list must stay small — false exclusions HIDE bugs.
        Locks the conservative default so a bulk-add can't sneak through
        without an explicit test update.

        S2975 added `discord_training` after sampling confirmed the
        statistics-rollup shape.
        """
        from core.services.no_items_policy import (
            EXCLUDED_DATA_TYPES,
            EXCLUDED_SPIDER_NAMES,
        )

        assert EXCLUDED_SPIDER_NAMES == frozenset({
            'betting_coordinator',
            'discord_training',
            'openmeteo',
        })
        assert EXCLUDED_DATA_TYPES == frozenset()

    def test_policy_excluded_total_counts_by_spider_name(self):
        """`policy_excluded_total` counts rows whose spider is on the exclusion
        list, regardless of embedding status."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        # 3 rows from excluded spiders + 2 from non-excluded.
        _make_spider_row(spider_name='betting_coordinator', embedding_text='rollup')
        _make_spider_row(spider_name='betting_coordinator', embedding_text='[NO_ITEMS]')
        _make_spider_row(spider_name='openmeteo', embedding_text='weather')
        _make_spider_row(spider_name='reddit', embedding_text='real content')
        _make_spider_row(spider_name='reddit', embedding_text='[NO_ITEMS]')

        stats = get_spider_semantic_search().get_embedding_stats()
        assert stats['policy_excluded_total'] == 3

    def test_stats_shape_stable_when_breakdown_disabled(self):
        """The legacy shape must not gain the breakdown block unless
        `include_breakdown=True` is passed. Prevents accidental payload
        bloat for callers that don't ask for it."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        _make_spider_row(embedding_text='content')
        stats = get_spider_semantic_search().get_embedding_stats()
        assert 'no_items_breakdown' not in stats

    def test_breakdown_ranks_no_items_by_spider_and_data_type(self):
        """When `include_breakdown=True`, top 10 spiders + top 10 data_types
        producing [NO_ITEMS] within the window are ranked descending by
        count. Also asserts the policy-reflection fields are populated
        for UI 'Excludes: X, Y' rendering (Rigby T1 refinement)."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        # 3 theodds [NO_ITEMS] + 2 openmeteo [NO_ITEMS] + 1 reddit embeddable.
        for _ in range(3):
            _make_spider_row(spider_name='theodds', data_type='sports_odds',
                             embedding_text='[NO_ITEMS]', days_ago=0)
        for _ in range(2):
            _make_spider_row(spider_name='openmeteo', data_type='weather',
                             embedding_text='[NO_ITEMS]', days_ago=0)
        _make_spider_row(spider_name='reddit', embedding_text='real', days_ago=0)

        stats = get_spider_semantic_search().get_embedding_stats(
            include_breakdown=True, breakdown_window_hours=24,
        )
        assert 'no_items_breakdown' in stats
        b = stats['no_items_breakdown']
        assert b['window_hours'] == 24
        assert b['total_rows'] == 6
        assert b['no_items_total'] == 5
        assert b['no_items_rate'] == round(5 / 6 * 100, 1)
        # Ranked descending
        assert b['by_spider'][0] == {'spider_name': 'theodds', 'count': 3}
        assert b['by_spider'][1] == {'spider_name': 'openmeteo', 'count': 2}
        # Policy reflection (Rigby T1 refinement — UI reads these directly).
        assert b['excluded_spider_names'] == [
            'betting_coordinator', 'discord_training', 'openmeteo',
        ]
        assert b['excluded_data_types'] == []

    def test_breakdown_window_excludes_older_rows(self):
        """The window filter correctly excludes rows outside the window
        (e.g., a 24h breakdown does not count 7-day-old [NO_ITEMS])."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        _make_spider_row(spider_name='theodds', embedding_text='[NO_ITEMS]', days_ago=0)
        _make_spider_row(spider_name='theodds', embedding_text='[NO_ITEMS]', days_ago=10)

        b24 = get_spider_semantic_search().get_embedding_stats(
            include_breakdown=True, breakdown_window_hours=24,
        )['no_items_breakdown']
        b720 = get_spider_semantic_search().get_embedding_stats(
            include_breakdown=True, breakdown_window_hours=720,  # 30d
        )['no_items_breakdown']

        assert b24['no_items_total'] == 1
        assert b720['no_items_total'] == 2


class SignalsBreakdownEndpointTests(TestCase):
    """S2973: `?include_breakdown=1&window=N` param on embedding-coverage."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='breakdown_user', password='pw')  # type: ignore[attr-defined]

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_include_breakdown_returns_new_block(self):
        _make_spider_row(spider_name='theodds', embedding_text='[NO_ITEMS]', days_ago=0)
        resp = self.client.get('/api/signals/embedding-coverage/',
                               {'include_breakdown': '1', 'window': '24'})
        assert resp.status_code == 200, resp.content
        body = resp.json()
        assert 'no_items_breakdown' in body
        assert body['no_items_breakdown']['window_hours'] == 24

    def test_default_omits_breakdown(self):
        resp = self.client.get('/api/signals/embedding-coverage/')
        assert resp.status_code == 200
        assert 'no_items_breakdown' not in resp.json()

    def test_invalid_window_clamps_to_default(self):
        """Bogus window values fall back to 24h — no 400, no surprise."""
        resp = self.client.get('/api/signals/embedding-coverage/',
                               {'include_breakdown': '1', 'window': '999'})
        assert resp.status_code == 200
        assert resp.json()['no_items_breakdown']['window_hours'] == 24


class SignalClusterFilterTests(TestCase):
    """S2971 extensions to SignalClusterViewSet.get_queryset()."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='cluster_tester', password='pw')  # type: ignore[attr-defined]
        # cluster A: recent, high confidence, reddit-heavy, keyword "persona"
        cls.a = SignalCluster.objects.create(
            name='Persona research spike',
            pattern_type='demand_spike',
            confidence=0.85,
            source_breakdown={'reddit': 12, 'bluesky': 3},
            keywords=['persona', 'user research'],
        )
        # cluster B: recent, low confidence, finnhub-only
        cls.b = SignalCluster.objects.create(
            name='Market movement in AI',
            pattern_type='market_movement',
            confidence=0.3,
            source_breakdown={'finnhub': 8},
            keywords=['ai', 'earnings'],
        )
        # cluster C: recent, high confidence, no keyword match
        cls.c = SignalCluster.objects.create(
            name='Weather trend',
            pattern_type='trend_emergence',
            confidence=0.7,
            source_breakdown={'noaa_weather': 5},
            keywords=['weather', 'climate'],
        )
        # Backdate cluster A so we can test window_hours cutoff
        SignalCluster.objects.filter(pk=cls.a.pk).update(
            detected_at=timezone.now() - timedelta(days=10)
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_returns_new_fields(self):
        resp = self.client.get('/api/v1/signal-clusters/')
        assert resp.status_code == 200, resp.content
        results = resp.json()['results']
        assert results, 'expected at least one cluster in list'
        row = results[0]
        for key in ('signal_count', 'total_signals', 'source_breakdown', 'keywords'):
            assert key in row, f'missing new list field: {key}'

    def test_window_hours_cutoff(self):
        # 48h window drops cluster A (backdated 10 days)
        resp = self.client.get('/api/v1/signal-clusters/', {'window_hours': 48})
        assert resp.status_code == 200
        ids = [r['id'] for r in resp.json()['results']]
        assert str(self.a.pk) not in ids
        assert str(self.b.pk) in ids

    def test_min_confidence_filter(self):
        resp = self.client.get('/api/v1/signal-clusters/', {'min_confidence': '0.5'})
        assert resp.status_code == 200
        ids = [r['id'] for r in resp.json()['results']]
        assert str(self.a.pk) in ids  # 0.85 >= 0.5
        assert str(self.c.pk) in ids  # 0.7 >= 0.5
        assert str(self.b.pk) not in ids  # 0.3 < 0.5

    def test_source_spider_filter(self):
        resp = self.client.get('/api/v1/signal-clusters/', {'source_spider': 'reddit'})
        assert resp.status_code == 200
        ids = [r['id'] for r in resp.json()['results']]
        assert str(self.a.pk) in ids  # reddit key present
        assert str(self.b.pk) not in ids  # finnhub only

    def test_query_matches_name(self):
        resp = self.client.get('/api/v1/signal-clusters/', {'query': 'Persona'})
        assert resp.status_code == 200
        ids = [r['id'] for r in resp.json()['results']]
        assert str(self.a.pk) in ids
        assert str(self.b.pk) not in ids

    def test_query_matches_keyword(self):
        resp = self.client.get('/api/v1/signal-clusters/', {'query': 'earnings'})
        assert resp.status_code == 200
        ids = [r['id'] for r in resp.json()['results']]
        assert str(self.b.pk) in ids

    def test_empty_filters_are_no_op(self):
        # Confirm blank params don't 500
        resp = self.client.get('/api/v1/signal-clusters/', {
            'window_hours': '',
            'min_confidence': '',
            'source_spider': '',
            'query': '',
        })
        assert resp.status_code == 200

    def test_invalid_min_confidence_ignored(self):
        resp = self.client.get('/api/v1/signal-clusters/', {'min_confidence': 'garbage'})
        assert resp.status_code == 200


class GetSearchableTextExtractorTests(TestCase):
    """S2974: extractor now supports wrapped-item shape (legislation) in
    addition to flat huggingface/kaggle/rss shape without regression."""

    def _row(self, raw_data):
        return LegacySpiderData.objects.create(
            spider_name='test',
            source_url='https://example.com/x',
            data_type='test',
            raw_data=raw_data,
            processed_data={},
            embedding_text='',
        )

    def test_flat_huggingface_shape_still_extracts(self):
        row = self._row({
            'items': [
                {'title': 'meta-llama/Llama-3.1-8B',
                 'description': 'AI model for text-generation.',
                 'tags': ['ai', 'llm']},
                {'modelId': 'stabilityai/stable-diffusion-3',
                 'description': 'AI model for text-to-image.'},
            ]
        })
        text = row.get_searchable_text()
        assert 'meta-llama/Llama-3.1-8B' in text
        assert 'stabilityai/stable-diffusion-3' in text
        assert 'text-generation' in text

    def test_wrapped_legislation_shape_uses_item_embedding_text(self):
        row = self._row({
            'items': [{
                'data_type': 'bill_summary',
                'platform': 'legislation',
                'tags': ['legislation', 'ri'],
                'embedding_text': 'H7030. Establishes the healthcare worker platform '
                                   'act requiring registration by 2027.',
                'raw_data': {'bill_number': 'H7030', 'title': 'Healthcare Worker Platform Act'},
            }]
        })
        text = row.get_searchable_text()
        assert 'H7030' in text
        assert 'healthcare worker platform' in text

    def test_wrapped_shape_falls_back_to_nested_raw_data(self):
        row = self._row({
            'items': [{
                'data_type': 'bill_summary',
                'platform': 'legislation',
                'raw_data': {
                    'bill_number': 'S1234',
                    'title': 'Some Bill Title',
                    'description': 'A description of the bill contents here.',
                },
            }]
        })
        text = row.get_searchable_text()
        assert 'Some Bill Title' in text
        assert 'A description of the bill' in text

    def test_item_embedding_text_sentinel_rejected(self):
        row = self._row({
            'items': [{
                'embedding_text': '[NO_ITEMS]',
                'raw_data': {'title': 'Fallback Title', 'description': 'Fallback desc.'},
            }]
        })
        text = row.get_searchable_text()
        assert '[NO_ITEMS]' not in text
        assert 'Fallback Title' in text

    def test_item_embedding_text_short_requires_title_fallback(self):
        row = self._row({
            'items': [
                {'embedding_text': 'short', 'raw_data': {}},  # no title-like → dropped
                {'embedding_text': 'short', 'title': 'X'},     # has title → kept
            ]
        })
        text = row.get_searchable_text()
        assert text.count('short') == 1

    def test_flat_item_missing_title_contributes_zero_text(self):
        row = self._row({
            'items': [{'description': 'only description', 'tags': ['x']}]
        })
        assert row.get_searchable_text() == ''

    def test_empty_items_returns_empty_string(self):
        assert self._row({'items': []}).get_searchable_text() == ''
        assert self._row({}).get_searchable_text() == ''

    def test_non_dict_item_skipped_without_error(self):
        row = self._row({'items': ['string_item', None, {'title': 'ok'}]})
        text = row.get_searchable_text()
        assert 'ok' in text

    def test_per_item_text_length_capped(self):
        long_text = 'a' * 5000
        row = self._row({'items': [{'embedding_text': long_text}]})
        text = row.get_searchable_text()
        # Per-item cap = 1000; global cap = 4000
        assert len(text) <= 4000
        assert len(text) <= 1000  # single item


class StaleNoItemsPolicyTests(TestCase):
    """S2975: stale-empty-raw-data sentinel handling.

    Verifies that historical ghost rows flagged by cleanup_stale_no_items
    are correctly bucketed as their own observable count (not NO_ITEMS)
    and stay skipped by backfill.
    """

    def test_backfill_skip_sentinels_helper_covers_both(self):
        """Centralized helper must contain both sentinels — this is the
        single source of truth the coverage endpoint and backfill share
        (Rigby T1 mitigation: no scattered string literals)."""
        from core.services.no_items_policy import (
            BACKFILL_SKIP_SENTINELS,
            NO_ITEMS_SENTINEL,
            STALE_EMPTY_SENTINEL,
        )

        assert NO_ITEMS_SENTINEL == '[NO_ITEMS]'
        assert STALE_EMPTY_SENTINEL == '[NO_ITEMS_STALE_EMPTY_RAW]'
        assert BACKFILL_SKIP_SENTINELS == frozenset({
            '[NO_ITEMS]', '[NO_ITEMS_STALE_EMPTY_RAW]',
        })

    def test_stale_bucket_reported_separately_from_no_items(self):
        """Stale rows are counted in `stale_empty_raw_data_total` and NOT
        in `ineligible_empty`. This is the core observability contract."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        # 2 legit NO_ITEMS + 3 stale ghosts
        _make_spider_row(embedding_text='[NO_ITEMS]')
        _make_spider_row(embedding_text='[NO_ITEMS]')
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]', raw_data={})
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]', raw_data={})
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]', raw_data={})

        stats = get_spider_semantic_search().get_embedding_stats()
        assert stats['ineligible_empty'] == 2
        assert stats['stale_empty_raw_data_total'] == 3

    def test_stale_rows_do_not_pollute_pending_eligible(self):
        """Stale rows have `embedding__isnull=True` but must NOT appear in
        the backfill queue (pending_eligible) — else the next backfill
        pass would re-mark them and undo cleanup."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        _make_spider_row(embedding_text='real content')
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]', raw_data={})
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]', raw_data={})

        stats = get_spider_semantic_search().get_embedding_stats()
        assert stats['pending_eligible'] == 1  # only the real-content row
        assert stats['stale_empty_raw_data_total'] == 2

    def test_stale_rows_do_not_pollute_recent_still_pending(self):
        """Same guarantee for the last-24h `still_pending` bucket."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        _make_spider_row(embedding_text='fresh eligible', days_ago=0)
        _make_spider_row(embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]',
                         raw_data={}, days_ago=0)

        r24 = get_spider_semantic_search().get_embedding_stats()['recent_24h']
        assert r24['still_pending'] == 1

    def test_breakdown_surfaces_stale_bucket(self):
        """`no_items_breakdown` includes a `stale_empty_raw_data_total`
        so dashboards can render 'N historical artifacts' alongside the
        active NO_ITEMS rate."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        _make_spider_row(spider_name='theodds', embedding_text='[NO_ITEMS]',
                         days_ago=0)
        _make_spider_row(spider_name='legislation',
                         embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]',
                         raw_data={}, days_ago=0)
        _make_spider_row(spider_name='legislation',
                         embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]',
                         raw_data={}, days_ago=0)

        b = get_spider_semantic_search().get_embedding_stats(
            include_breakdown=True, breakdown_window_hours=24,
        )['no_items_breakdown']

        assert b['no_items_total'] == 1  # theodds only — stale excluded
        assert b['stale_empty_raw_data_total'] == 2

    def test_stale_sentinel_excluded_from_breakdown_by_spider(self):
        """The `by_spider` ranking must NOT include stale-sentinel rows —
        else legislation would still dominate the 30d breakdown after
        cleanup, defeating the whole point."""
        from core.services.spider_semantic_search import get_spider_semantic_search

        # 50 legislation stale ghosts + 3 theodds real NO_ITEMS
        for _ in range(50):
            _make_spider_row(spider_name='legislation',
                             embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]',
                             raw_data={}, days_ago=0)
        for _ in range(3):
            _make_spider_row(spider_name='theodds', embedding_text='[NO_ITEMS]',
                             days_ago=0)

        b = get_spider_semantic_search().get_embedding_stats(
            include_breakdown=True, breakdown_window_hours=24,
        )['no_items_breakdown']

        spiders = [r['spider_name'] for r in b['by_spider']]
        assert 'legislation' not in spiders
        assert spiders[0] == 'theodds'


class CleanupStaleNoItemsCommandTests(TestCase):
    """S2975: `cleanup_stale_no_items` management command."""

    def _stale_row(self, *, days_ago: int, spider_name: str = 'legislation',
                   raw_data: Optional[dict] = None, embedding_text: str = '[NO_ITEMS]'):
        return _make_spider_row(
            spider_name=spider_name,
            days_ago=days_ago,
            embedding_text=embedding_text,
            raw_data=raw_data if raw_data is not None else {},
        )

    def test_dry_run_reports_candidates_without_modifying(self):
        """Dry-run is the default. It must count matches but never write."""
        from io import StringIO
        from django.core.management import call_command

        # 3 candidates (raw_data={} + NO_ITEMS + old) + 1 non-candidate (recent)
        self._stale_row(days_ago=60)
        self._stale_row(days_ago=45)
        self._stale_row(days_ago=30)
        self._stale_row(days_ago=1)  # too recent — excluded by default cutoff

        buf = StringIO()
        call_command('cleanup_stale_no_items', stdout=buf)
        output = buf.getvalue()

        assert 'DRY RUN' in output
        assert 'candidates:  3' in output or 'candidates:  3\n' in output
        # No modifications
        stale_count = LegacySpiderData.objects.filter(
            embedding_text='[NO_ITEMS_STALE_EMPTY_RAW]',
        ).count()
        assert stale_count == 0

    def test_apply_bumps_sentinel(self):
        """`--apply` bumps `embedding_text` to the stale sentinel."""
        from io import StringIO
        from django.core.management import call_command

        rows = [self._stale_row(days_ago=45) for _ in range(3)]

        buf = StringIO()
        call_command('cleanup_stale_no_items', '--apply', stdout=buf)

        for r in rows:
            r.refresh_from_db()
            assert r.embedding_text == '[NO_ITEMS_STALE_EMPTY_RAW]'

    def test_excludes_recent_rows(self):
        """Rows created AFTER the cutoff must not be touched — those are
        current NO_ITEMS worth investigating, not historical ghosts."""
        from django.core.management import call_command

        old = self._stale_row(days_ago=60)
        recent = self._stale_row(days_ago=1)  # after default cutoff

        call_command('cleanup_stale_no_items', '--apply', verbosity=0)

        old.refresh_from_db()
        recent.refresh_from_db()
        assert old.embedding_text == '[NO_ITEMS_STALE_EMPTY_RAW]'
        assert recent.embedding_text == '[NO_ITEMS]'  # untouched

    def test_excludes_rows_with_populated_raw_data(self):
        """Rows with real `raw_data` are current [NO_ITEMS] (extractor
        misses / rollups) — cleanup must not silently flag them."""
        from django.core.management import call_command

        empty = self._stale_row(days_ago=60, raw_data={})
        populated = self._stale_row(days_ago=60, raw_data={'items': [{'title': 'x'}]})

        call_command('cleanup_stale_no_items', '--apply', verbosity=0)

        empty.refresh_from_db()
        populated.refresh_from_db()
        assert empty.embedding_text == '[NO_ITEMS_STALE_EMPTY_RAW]'
        assert populated.embedding_text == '[NO_ITEMS]'

    def test_spider_scope_filter(self):
        """`--spider X` only touches rows for that spider."""
        from django.core.management import call_command

        leg = self._stale_row(days_ago=45, spider_name='legislation')
        rok = self._stale_row(days_ago=45, spider_name='remoteok')

        call_command('cleanup_stale_no_items', '--spider', 'legislation',
                     '--apply', verbosity=0)

        leg.refresh_from_db()
        rok.refresh_from_db()
        assert leg.embedding_text == '[NO_ITEMS_STALE_EMPTY_RAW]'
        assert rok.embedding_text == '[NO_ITEMS]'  # untouched

    def test_custom_before_cutoff_accepts_iso_date(self):
        """`--before YYYY-MM-DD` overrides the default cutoff; qualifying set
        is `created_at < cutoff`."""
        from django.core.management import call_command

        # Row 5 days old — AFTER the default cutoff (2026-07-19) so untouched
        # by defaults, but qualifies under a wide-open override.
        row = self._stale_row(days_ago=5)

        # Cutoff before the row's created_at → row does NOT qualify.
        strict_cutoff = (timezone.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        call_command('cleanup_stale_no_items', '--before', strict_cutoff,
                     '--apply', verbosity=0)
        row.refresh_from_db()
        assert row.embedding_text == '[NO_ITEMS]'  # untouched

        # Cutoff after the row's created_at → row DOES qualify.
        wide_cutoff = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        call_command('cleanup_stale_no_items', '--before', wide_cutoff,
                     '--apply', verbosity=0)
        row.refresh_from_db()
        assert row.embedding_text == '[NO_ITEMS_STALE_EMPTY_RAW]'

    def test_invalid_before_raises_command_error(self):
        """Malformed --before must raise, not silently proceed."""
        from django.core.management import call_command
        from django.core.management.base import CommandError

        try:
            call_command('cleanup_stale_no_items', '--before', 'not-a-date',
                         verbosity=0)
        except CommandError as e:
            assert 'YYYY-MM-DD' in str(e)
        else:  # pragma: no cover
            raise AssertionError('expected CommandError')

    def test_limit_caps_flagged_count(self):
        """`--limit N` caps how many rows get flagged; the rest stay [NO_ITEMS]."""
        from django.core.management import call_command

        rows = [self._stale_row(days_ago=45) for _ in range(5)]

        call_command('cleanup_stale_no_items', '--apply', '--limit', '2',
                     verbosity=0)

        flagged = sum(
            1 for r in rows
            if LegacySpiderData.objects.get(pk=r.pk).embedding_text == '[NO_ITEMS_STALE_EMPTY_RAW]'
        )
        assert flagged == 2
