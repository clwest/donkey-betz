"""
Tests for the public changelog endpoint (Session 1116, Integration #4).

Covers token gating (shared with the intel endpoint), publish_intent
filtering, status='published' filter, 30-day window, and the field
redaction contract (no workspace_id, no initiative_id, no full content).
"""
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_deliverables import Deliverable, PublishIntent


@override_settings(PUBLIC_INTEL_TOKEN='test-token-abc')
class PublicChangelogRecentViewTests(TestCase):
    """Token-gated endpoint exposing curated Deliverable slice."""

    url = '/api/public/changelog/recent/'

    def setUp(self):
        # SAFE: publish_candidate, published, recent — should appear
        self.candidate = Deliverable.objects.create(
            title='New AI Market Report',
            slug='new-ai-market-report',
            deliverable_type='report',
            publish_intent=PublishIntent.PUBLISH_CANDIDATE,
            status='published',
            category='Markets',
            tags=['ai', 'markets', 'q2-2026'],
            agent_name='ContentWriterAgent',
            content='# Market Report\n\nQ2 2026 saw a remarkable shift in AI market dynamics. '
                    'New entrants, established players reshuffling, and a noticeable acceleration '
                    'in spend on agent-based products across mid-market enterprises.',
        )
        # SAFE: publish_required, published, recent — should appear
        Deliverable.objects.create(
            title='Compliance Brief Q2',
            slug='compliance-brief-q2',
            deliverable_type='document',
            publish_intent=PublishIntent.PUBLISH_REQUIRED,
            status='published',
            category='Legal',
            agent_name='LegalDocDrafterAgent',
            content='Quarterly compliance brief covering new regulatory shifts.',
        )

        # SHOULD NOT appear — publish_intent=internal_only
        Deliverable.objects.create(
            title='Internal Diagnostic — must not leak',
            slug='internal-diagnostic',
            deliverable_type='analysis',
            publish_intent=PublishIntent.INTERNAL_ONLY,
            status='published',
            agent_name='COOAgent',
            content='Confidential internal: workspace ironwood spent 84% of LLM budget...',
        )
        # SHOULD NOT appear — status=draft
        Deliverable.objects.create(
            title='Draft Report',
            slug='draft-report',
            deliverable_type='report',
            publish_intent=PublishIntent.PUBLISH_CANDIDATE,
            status='draft',
            agent_name='ContentWriterAgent',
            content='Work in progress',
        )
        # SHOULD NOT appear — outside 30-day window
        old = Deliverable.objects.create(
            title='Old Report',
            slug='old-report',
            deliverable_type='report',
            publish_intent=PublishIntent.PUBLISH_CANDIDATE,
            status='published',
            agent_name='ContentWriterAgent',
            content='Old report content',
        )
        Deliverable.objects.filter(pk=old.pk).update(
            created_at=timezone.now() - timedelta(days=45)
        )

    def test_token_required_when_token_configured(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)

    def test_wrong_token_rejected(self):
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='wrong')
        self.assertEqual(resp.status_code, 401)

    def test_valid_token_returns_payload(self):
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('as_of', data)
        self.assertEqual(data['window_days'], 30)
        self.assertIn('stats', data)
        self.assertIn('deliverables', data)

    def test_filters_to_publishable_intent_only(self):
        """internal_only deliverables NEVER appear in the changelog."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        titles = [d['title'] for d in data['deliverables']]
        self.assertIn('New AI Market Report', titles)
        self.assertIn('Compliance Brief Q2', titles)
        self.assertNotIn('Internal Diagnostic — must not leak', titles)
        self.assertNotIn('Draft Report', titles)  # status=draft filtered
        self.assertNotIn('Old Report', titles)     # outside window

    def test_internal_content_never_leaks(self):
        """Paranoid second-pass: confidential text from an internal-only
        deliverable must not appear anywhere in the response body."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        body = resp.content.decode('utf-8')
        self.assertNotIn('Internal Diagnostic', body)
        self.assertNotIn('ironwood spent 84%', body)
        self.assertNotIn('Confidential internal', body)

    def test_no_workspace_initiative_user_ids_leak(self):
        """Deliverable rows have FKs to workspace, initiative, user — none
        of those internal IDs may appear in the response."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        for deliv in data['deliverables']:
            self.assertNotIn('workspace', deliv)
            self.assertNotIn('workspace_id', deliv)
            self.assertNotIn('initiative', deliv)
            self.assertNotIn('initiative_id', deliv)
            self.assertNotIn('user', deliv)
            self.assertNotIn('user_id', deliv)
            self.assertNotIn('trace_id', deliv)
            self.assertNotIn('parent_object_id', deliv)
            self.assertNotIn('content', deliv)  # only excerpt should appear
            self.assertNotIn('content_hash', deliv)
            self.assertNotIn('agent_name', deliv)  # implementation detail
            self.assertNotIn('slug', deliv)

    def test_payload_shape_matches_contract(self):
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        deliv = next(d for d in data['deliverables'] if d['title'] == 'New AI Market Report')
        self.assertEqual(set(deliv.keys()), {
            'id', 'title', 'deliverable_type', 'type_label',
            'category', 'tags', 'excerpt', 'published_at', 'created_at',
        })
        self.assertEqual(deliv['deliverable_type'], 'report')
        self.assertEqual(deliv['type_label'], 'Report')
        self.assertEqual(deliv['category'], 'Markets')
        self.assertEqual(deliv['tags'], ['ai', 'markets', 'q2-2026'])

    def test_excerpt_truncated_and_stripped(self):
        """Excerpt strips markdown noise and caps length."""
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        deliv = next(d for d in data['deliverables'] if d['title'] == 'New AI Market Report')
        self.assertFalse(deliv['excerpt'].startswith('#'))
        self.assertLessEqual(len(deliv['excerpt']), 230)  # 220 + a few for "…"

    def test_tags_truncated_and_capped(self):
        Deliverable.objects.create(
            title='Long tags test',
            slug='long-tags-test',
            deliverable_type='document',
            publish_intent=PublishIntent.PUBLISH_CANDIDATE,
            status='published',
            tags=['a' * 100] + [f'tag-{i}' for i in range(10)],
            agent_name='ContentWriterAgent',
            content='test',
        )
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        deliv = next(d for d in data['deliverables'] if d['title'] == 'Long tags test')
        self.assertLessEqual(len(deliv['tags']), 6)
        for tag in deliv['tags']:
            self.assertLessEqual(len(tag), 40)

    def test_stats_aggregates_top_types(self):
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='test-token-abc')
        data = resp.json()
        self.assertGreaterEqual(data['stats']['total_published_30d'], 2)
        self.assertGreater(len(data['stats']['top_types']), 0)


class PublicChangelogRecentViewDisabledTests(TestCase):
    """When PUBLIC_INTEL_TOKEN is empty, the endpoint is default-off."""

    url = '/api/public/changelog/recent/'

    @override_settings(PUBLIC_INTEL_TOKEN='')
    def test_endpoint_rejects_all_requests_when_disabled(self):
        resp = self.client.get(self.url, HTTP_X_INTEL_TOKEN='any-token')
        self.assertEqual(resp.status_code, 401)

    @override_settings(PUBLIC_INTEL_TOKEN='')
    def test_endpoint_rejects_no_token_when_disabled(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 401)
