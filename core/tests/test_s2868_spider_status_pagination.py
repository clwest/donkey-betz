"""
S2868 slate #2 — `spider_status_tool.list` pagination + registry union.

Rigby Tool Gap Ledger deliverable
`5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` entry #1: prior behavior returned
the full population as one array with no limit/offset/total controls;
the downstream tool-response layer truncated to ~44 mid-flight producing
false-negative "spider not found" reports (S2845). Fix adds explicit
pagination + registry union so callers see the true total and can
iterate the full inventory.

Uses TestCase with fixture rows scoped to test spider_names — the live
DB has real spider data that would confuse assertions. Registry
membership is read from the runtime singleton so the tests verify the
handler's union logic without mocking.

Local-run pgbouncer note from
`test_deliverable_initiative_diagnostics.py:19-33` applies.

Run::

    python manage.py test core.tests.test_s2868_spider_status_pagination -v2
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import LegacySpiderData
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class SpiderStatusPaginationEnvelopeTests(TestCase):
    """Envelope shape + pagination math verification. Uses a small
    fixture set so we can compute the expected totals exactly."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f's2868-spider-{uuid.uuid4().hex[:8]}',
            email='s2868-spider@example.com',
            password='x',
        )
        # Create 5 fixture spider_names with varying row counts + ages.
        # Using deliberately-unique names to avoid collision with any
        # live-DB spider_names when the test database is a snapshot copy.
        now = timezone.now()
        fixture_specs = [
            ('s2868_test_alpha', 3, now - timedelta(hours=1)),
            ('s2868_test_bravo', 2, now - timedelta(hours=6)),
            ('s2868_test_charlie', 1, now - timedelta(hours=50)),  # stale
            ('s2868_test_delta', 1, now - timedelta(days=10)),  # stale
            ('s2868_test_echo', 1, now - timedelta(minutes=5)),
        ]
        for spider_name, count, most_recent_ts in fixture_specs:
            for i in range(count):
                LegacySpiderData.objects.create(
                    spider_name=spider_name,
                    data_type='test',
                    source_url=f'https://test.example.com/{spider_name}/{i}',
                    raw_data={'items': []},
                    processed_data={},
                    embedding_text=f'{spider_name} row {i}',
                    created_at=most_recent_ts - timedelta(minutes=i),
                )

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _list(self, **payload_extras):
        payload = {'action': 'list', **payload_extras}
        return self.dispatcher._handle_spider_status(
            'spider_status_tool', payload, self.user.id, 'test-trace-s2868',
        )

    def test_p1_envelope_contains_pagination_keys(self):
        """New pagination envelope keys are present."""
        result = self._list()
        for key in ('limit', 'offset', 'total', 'has_more',
                    'total_spiders', 'active', 'stale', 'never_run',
                    'include_registry', 'include_orphans',
                    'registered_count', 'spiders'):
            self.assertIn(key, result, f'envelope missing key: {key}')

    def test_p2_total_spiders_matches_total_backward_compat(self):
        """`total_spiders` alias preserved for pre-S2868 callers."""
        result = self._list()
        self.assertEqual(result['total_spiders'], result['total'])

    def test_p3_default_limit_and_offset(self):
        result = self._list()
        self.assertEqual(result['offset'], 0)
        # default limit is 30 (per handler)
        self.assertEqual(result['limit'], 30)

    def test_p4_limit_slice_respected(self):
        """Response `spiders` array respects limit."""
        result = self._list(limit=2)
        self.assertLessEqual(len(result['spiders']), 2)
        self.assertEqual(result['limit'], 2)

    def test_p5_offset_slice_respected(self):
        """offset skips the first N rows; combined with limit produces
        a distinct slice from offset=0."""
        page1 = self._list(limit=2, offset=0)
        page2 = self._list(limit=2, offset=2)
        page1_names = [s['spider_name'] for s in page1['spiders']]
        page2_names = [s['spider_name'] for s in page2['spiders']]
        # Disjoint pages
        self.assertEqual(set(page1_names) & set(page2_names), set())

    def test_p6_has_more_computed_correctly(self):
        """has_more=True when offset+limit < total; False on last page."""
        result = self._list(limit=2, offset=0)
        if result['total'] > 2:
            self.assertTrue(result['has_more'])
        result_last = self._list(limit=1000, offset=0)
        self.assertFalse(result_last['has_more'])

    def test_p7_limit_capped_at_500(self):
        result = self._list(limit=10000)
        self.assertEqual(result['limit'], 500)

    def test_p8_offset_clamped_at_zero(self):
        result = self._list(offset=-100)
        self.assertEqual(result['offset'], 0)

    def test_p9_active_stale_computed_on_full_population(self):
        """Summary counts reflect ALL rows, not just the paginated slice —
        so operators see accurate active/stale ratios regardless of
        window position."""
        page1 = self._list(limit=1, offset=0)
        page_last = self._list(limit=1, offset=100)
        self.assertEqual(page1['active'], page_last['active'])
        self.assertEqual(page1['stale'], page_last['stale'])
        self.assertEqual(page1['never_run'], page_last['never_run'])

    def test_p10_include_registry_default_true(self):
        """Default surfaces registered-but-never-run spiders."""
        result = self._list()
        self.assertTrue(result['include_registry'])
        # registered_count > 0 (registry has ~80 spiders)
        self.assertGreater(result['registered_count'], 0)

    def test_p11_include_registry_false_excludes_never_run(self):
        result = self._list(include_registry=False, limit=500)
        self.assertFalse(result['include_registry'])
        self.assertEqual(result['never_run'], 0,
                         "include_registry=false must exclude never-run rows")
        for spider in result['spiders']:
            self.assertNotEqual(spider['status'], 'never_run')

    def test_p12_include_orphans_false_excludes_non_registered(self):
        """include_orphans=false drops rows whose spider_name is NOT in
        the runtime registry (legacy names)."""
        # First get the current registry so we can assert against it.
        try:
            from ai_core.spiders.spider_registry import spider_registry
            registered = set(spider_registry.spider_classes.keys())
        except Exception:
            self.skipTest("spider_registry unavailable")

        result = self._list(include_orphans=False, limit=500)
        self.assertFalse(result['include_orphans'])
        for spider in result['spiders']:
            self.assertTrue(
                spider['in_registry'] or spider['status'] == 'never_run',
                f"include_orphans=false must exclude {spider['spider_name']!r} "
                "(not in registry)",
            )

    def test_p13_spider_entry_shape(self):
        """Each spider dict has the expected keys including the new
        `in_registry` boolean added in S2868."""
        result = self._list(limit=1)
        if not result['spiders']:
            self.skipTest("no fixture rows returned")
        spider = result['spiders'][0]
        for key in ('spider_name', 'in_registry', 'total_runs',
                    'runs_24h', 'runs_7d', 'total_items', 'items_24h',
                    'items_7d', 'last_run_at', 'first_seen', 'age_hours',
                    'status', 'count_note'):
            self.assertIn(key, spider,
                          f'spider entry missing key: {key}')

    def test_p14_never_run_entry_shape(self):
        """Never-run entries have status='never_run' + zero counts +
        null timestamps."""
        result = self._list(limit=500)
        never_run_rows = [s for s in result['spiders']
                          if s['status'] == 'never_run']
        if not never_run_rows:
            self.skipTest("no never-run spiders in the current registry")
        entry = never_run_rows[0]
        self.assertEqual(entry['status'], 'never_run')
        self.assertEqual(entry['total_runs'], 0)
        self.assertEqual(entry['runs_24h'], 0)
        self.assertEqual(entry['runs_7d'], 0)
        self.assertIsNone(entry['last_run_at'])
        self.assertIsNone(entry['first_seen'])
        self.assertIsNone(entry['age_hours'])
        self.assertTrue(entry['in_registry'])
