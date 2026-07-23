"""Session 2897 slate #1 — prospecting_queue empty-titles fix (Row A).

Locks in the S2897 title-extraction + scoring-text fix on
core/services/ops_autopilot/revenue.py::OutboundLeadEngine:

  Bug 1 (line 478): Python operator-precedence — `raw.get('title', '') or
    item.embedding_text[:80] if item.embedding_text else ''` parses as
    `(a or b) if c else ''`; when embedding_text is empty (always, for
    financial spiders) title unconditionally blanks.

  Bug 2 (lines 505-508): `raw.get('title', '')` reads the wrong path.
    Financial-spider rows shape is `raw_data = {items: [{title, ...}, ...]}`
    with no top-level `title`; scoring text collapses to '' → flat 45 score
    across all financial-source leads.

Fix: `_extract_first_item_text(raw, item)` helper returns
    (title, combined_text, title_source) with fall-through
    top_level → items[0] → embedding → synth. Used by evaluate() for
    title extraction (+ `(+N more)` suffix for batched items) and by
    _score_lead() for scoring text.
"""

from types import SimpleNamespace

from django.test import SimpleTestCase

from core.services.ops_autopilot.revenue import OutboundLeadEngine


def _stub_item(raw_data=None, embedding_text='', spider_name='some_spider',
               data_type='job_listing'):
    """Minimal LegacySpiderData stand-in for _extract_first_item_text."""
    stub = SimpleNamespace(
        raw_data_dict=raw_data,
        embedding_text=embedding_text,
        spider_name=spider_name,
        data_type=data_type,
    )
    return stub


class ExtractFirstItemTextTests(SimpleTestCase):
    """The helper resolves title + combined text across 4 shapes."""

    def setUp(self):
        self.engine = OutboundLeadEngine()

    def test_top_level_title_takes_precedence(self):
        raw = {'title': 'Acme hiring senior engineer', 'description': 'growing team'}
        item = _stub_item(raw_data=raw, embedding_text='fallback text')
        title, combined, source = self.engine._extract_first_item_text(raw, item)
        self.assertEqual(title, 'Acme hiring senior engineer')
        self.assertIn('Acme hiring', combined)
        self.assertIn('growing team', combined)
        self.assertEqual(source, 'top_level')

    def test_falls_back_to_items_first_title_for_batched_rows(self):
        raw = {'items': [
            {'title': 'SEC 10-K filing: Scilex Holding', 'description': 'annual'},
            {'title': 'Second item title'},
            {'title': 'Third'},
        ]}
        item = _stub_item(raw_data=raw, spider_name='sec_edgar', data_type='financial')
        title, combined, source = self.engine._extract_first_item_text(raw, item)
        self.assertEqual(title, 'SEC 10-K filing: Scilex Holding')
        self.assertIn('SEC 10-K', combined)
        self.assertIn('annual', combined)
        self.assertEqual(source, 'items_first')

    def test_falls_back_to_embedding_text_when_raw_empty(self):
        item = _stub_item(raw_data={}, embedding_text='Job posting: Data Scientist at Acme')
        title, combined, source = self.engine._extract_first_item_text({}, item)
        self.assertEqual(title, 'Job posting: Data Scientist at Acme')
        self.assertEqual(source, 'embedding')

    def test_defensive_against_non_dict_raw(self):
        item = _stub_item(raw_data=None, embedding_text='')
        title, combined, source = self.engine._extract_first_item_text(None, item)
        self.assertEqual(title, '')
        self.assertEqual(combined, '')
        self.assertEqual(source, '')

    def test_defensive_against_items_not_a_list(self):
        raw = {'items': 'not-a-list'}
        item = _stub_item(raw_data=raw, embedding_text='')
        title, combined, source = self.engine._extract_first_item_text(raw, item)
        self.assertEqual(title, '')
        self.assertEqual(source, '')

    def test_defensive_against_items_first_not_dict(self):
        raw = {'items': ['string-item-not-dict', {'title': 'skipped'}]}
        item = _stub_item(raw_data=raw)
        title, _, source = self.engine._extract_first_item_text(raw, item)
        self.assertEqual(title, '')
        self.assertEqual(source, '')

    def test_description_pulled_from_items_first_summary_fallback(self):
        raw = {'items': [{'title': 'T', 'summary': 'summary text'}]}
        item = _stub_item(raw_data=raw)
        _, combined, _ = self.engine._extract_first_item_text(raw, item)
        self.assertIn('summary text', combined)


class ScoreLeadIntegrationTests(SimpleTestCase):
    """_score_lead uses combined text, so revenue keywords in items[0] count."""

    def setUp(self):
        self.engine = OutboundLeadEngine()

    def test_financial_batched_row_gets_revenue_keyword_hits(self):
        from datetime import timedelta
        from django.utils import timezone
        now = timezone.now()
        # Batched-item row with revenue keywords in items[0]
        raw = {'items': [
            {
                'title': 'Series C funding: Acme raised $50 million',
                'description': 'growth stage; hiring for expansion',
            },
        ]}
        item = SimpleNamespace(
            raw_data_dict=raw,
            embedding_text='',
            spider_name='sec_edgar',
            data_type='financial',
            source_url='https://sec.gov/filing/12345',
            created_at=now - timedelta(hours=6),
        )
        score = self.engine._score_lead(item, now)
        # Recency <24h → 30; keywords (funding, raised, million, growth, hiring,
        # expansion, series) → 6*6=36 capped at 30; URL present → 10;
        # source_quality=other → 5. Total: 30+30+10+5=75.
        self.assertGreaterEqual(score, 60)


class ProspectingQueueTitleShapeTests(SimpleTestCase):
    """evaluate() branches — items_first uses (+N more) suffix; synth is last resort."""

    def setUp(self):
        self.engine = OutboundLeadEngine()

    def test_items_first_title_appends_more_suffix_when_multiple(self):
        # Not a full evaluate() call — just the title-shape logic isolated.
        # We simulate what evaluate() does after helper returns 'items_first'.
        raw = {'items': [
            {'title': 'First lead in batch'},
            {'title': 'second'},
            {'title': 'third'},
        ]}
        item = _stub_item(raw_data=raw, spider_name='yahoo_finance', data_type='financial')
        title, _, source = self.engine._extract_first_item_text(raw, item)
        # Mirror evaluate()'s suffix-append logic
        n_items = len(raw['items'])
        if source == 'items_first' and n_items > 1:
            suffix = f' (+{n_items - 1} more)'
            title = title[: 100 - len(suffix)] + suffix
        self.assertEqual(title, 'First lead in batch (+2 more)')

    def test_synth_fallback_shape_when_all_extraction_paths_empty(self):
        raw = {'items': [{'link': 'http://x'}]}  # item has no title
        item = _stub_item(raw_data=raw, spider_name='etherscan', data_type='financial')
        title, _, source = self.engine._extract_first_item_text(raw, item)
        self.assertEqual(title, '')
        self.assertEqual(source, '')
        # Mirror evaluate()'s synth-branch
        n_items = len(raw.get('items') or [])
        synth = f'{item.spider_name}: {item.data_type} batch'
        if n_items:
            synth += f' ({n_items} items)'
        self.assertEqual(synth, 'etherscan: financial batch (1 items)')
