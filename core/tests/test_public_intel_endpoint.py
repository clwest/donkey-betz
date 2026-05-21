"""
Tests for the public intelligence endpoint (Session 1116).

Covers token gating, the default-off safety when PUBLIC_INTEL_TOKEN is
unset, the pattern-type whitelist, and the field redaction contract
(no spider_data_ids, no sample_signals leaked).
"""
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_signal_intelligence import SignalCluster


@override_settings(PUBLIC_INTEL_TOKEN='test-token-abc')
class PublicIntelligenceNowViewTests(TestCase):
    """Token-gated endpoint exposing curated SignalCluster slice."""

    url = '/api/public/intelligence/now/'

    def setUp(self):
        # Whitelisted pattern type — should appear in payload
        self.public_cluster = SignalCluster.objects.create(
            name='Test demand spike',
            pattern_type='demand_spike',
            status='active',
            strength=0.9,
            confidence=0.8,
            novelty=0.7,
            urgency=0.6,
            source_breakdown={'reddit': 12, 'bluesky': 4},
            keywords=['ai', 'agents', 'orchestration'],
            spider_data_ids=['must-not-leak-1', 'must-not-leak-2'],
            sample_signals=[{'text': 'private excerpt, must not leak'}],
        )
        # Non-whitelisted pattern type — should be filtered out
        SignalCluster.objects.create(
            name='Knowledge gap (private)',
            pattern_type='knowledge_gap',
            status='active',
            strength=0.95,
        )
        # Whitelisted but inactive — should be filtered out
        SignalCluster.objects.create(
            name='Old stale cluster',
            pattern_type='trend_emergence',
            status='archived',
            strength=0.85,
        )
        # Whitelisted, active, but outside 24h window — filtered out
        old_active = SignalCluster.objects.create(
            name='Stale active',
            pattern_type='market_movement',
            status='active',
            strength=0.5,
        )
        SignalCluster.objects.filter(pk=old_active.pk).update(
            detected_at=timezone.now() - timedelta(hours=48)
        )

    def test_token_required_when_token_configured(self):
        """Missing X-Intel-Token returns 401."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)

    def test_wrong_token_rejected(self):
        """Bad token returns 401."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='wrong')
        self.assertEqual(resp.status_code, 401)

    def test_valid_token_returns_payload(self):
        """Correct token returns 200 with structured payload."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('as_of', data)
        self.assertEqual(data['window_hours'], 24)
        self.assertIn('stats', data)
        self.assertIn('clusters', data)

    def test_payload_filters_to_whitelist_and_window(self):
        """Only whitelisted active patterns from last 24h appear."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        names = [c['name'] for c in data['clusters']]
        self.assertIn('Test demand spike', names)
        self.assertNotIn('Knowledge gap (private)', names)  # pattern not whitelisted
        self.assertNotIn('Old stale cluster', names)         # status archived
        self.assertNotIn('Stale active', names)              # outside 24h window

    def test_no_internal_fields_leak(self):
        """spider_data_ids and sample_signals must never appear in response."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        for cluster in data['clusters']:
            self.assertNotIn('spider_data_ids', cluster)
            self.assertNotIn('sample_signals', cluster)
            self.assertNotIn('trigger_event_ids', cluster)
        # Also check the raw response body — a paranoid second pass
        body = resp.content.decode('utf-8')
        self.assertNotIn('must-not-leak', body)
        self.assertNotIn('private excerpt', body)

    def test_payload_shape_matches_contract(self):
        """The hand-shaped cluster dict matches the public contract."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        cluster = next(c for c in data['clusters'] if c['name'] == 'Test demand spike')
        self.assertEqual(set(cluster.keys()), {
            'id', 'name', 'pattern_type', 'pattern_label',
            'strength', 'novelty', 'confidence', 'urgency',
            'detected_at', 'source_breakdown', 'keywords',
        })
        self.assertEqual(cluster['pattern_type'], 'demand_spike')
        self.assertEqual(cluster['pattern_label'], 'Demand Spike')
        self.assertEqual(cluster['strength'], 0.9)
        self.assertEqual(cluster['source_breakdown'], {'reddit': 12, 'bluesky': 4})
        self.assertEqual(cluster['keywords'], ['ai', 'agents', 'orchestration'])

    def test_keywords_truncated_and_capped(self):
        """Defense in depth: ≤6 keywords, each ≤40 chars."""
        SignalCluster.objects.create(
            name='Long keywords test',
            pattern_type='demand_spike',
            status='active',
            strength=0.5,
            keywords=['a' * 100] + [f'kw-{i}' for i in range(10)],
        )
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        cluster = next(c for c in data['clusters'] if c['name'] == 'Long keywords test')
        self.assertLessEqual(len(cluster['keywords']), 6)
        for kw in cluster['keywords']:
            self.assertLessEqual(len(kw), 40)

    def test_stats_aggregates_top_patterns(self):
        """Stats block reports aggregate counts and top patterns."""
        SignalCluster.objects.create(
            name='Another demand spike',
            pattern_type='demand_spike',
            status='active',
            strength=0.5,
        )
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        self.assertGreaterEqual(data['stats']['total_signals_24h'], 2)
        self.assertGreater(len(data['stats']['top_patterns']), 0)
        self.assertGreater(data['stats']['sources_watched'], 0)


class PublicIntelligenceNowViewDisabledTests(TestCase):
    """When PUBLIC_INTEL_TOKEN is empty, the endpoint is default-off."""

    url = '/api/public/intelligence/now/'

    @override_settings(PUBLIC_INTEL_TOKEN='')
    def test_endpoint_rejects_all_requests_when_disabled(self):
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='any-token')
        self.assertEqual(resp.status_code, 401)

    @override_settings(PUBLIC_INTEL_TOKEN='')
    def test_endpoint_rejects_no_token_when_disabled(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
