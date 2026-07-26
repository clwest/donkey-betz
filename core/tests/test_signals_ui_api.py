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


def _make_spider_row(
    *,
    spider_name: str = 'reddit',
    data_type: str = 'news',
    is_actionable: bool = True,
    days_ago: int = 1,
    embedding_text: str = 'sample embedding text',
    source_url: Optional[str] = None,
    raw_data: Optional[dict] = None,
) -> LegacySpiderData:
    created_at = timezone.now() - timedelta(days=days_ago)
    row = LegacySpiderData.objects.create(
        spider_name=spider_name,
        source_url=source_url or f'https://example.com/{uuid.uuid4().hex[:8]}',
        data_type=data_type,
        is_actionable=is_actionable,
        raw_data=raw_data or {'title': f'{spider_name} item'},
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
                'total_entries': 100, 'with_embedding': 40, 'marked_empty': 5,
                'pending': 55, 'searchable': 40, 'coverage_percent': 40.0,
                'recent_24h': {'total': 10, 'with_embedding': 4},
            }
            resp = self.client.get('/api/signals/embedding-coverage/')
        assert resp.status_code == 200, resp.content
        body = resp.json()
        assert body['coverage_percent'] == 40.0

    def test_all_endpoints_require_auth(self):
        anon = APIClient()
        for path in [
            '/api/signals/aggregate/',
            '/api/signals/feed/',
            '/api/signals/embedding-coverage/',
        ]:
            resp = anon.get(path)
            assert resp.status_code in (401, 403), f'{path}: {resp.status_code}'


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
