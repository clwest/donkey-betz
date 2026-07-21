"""
S2873 slate — Rigby Tool Gap Ledger wish-list #2 + #3.

Extends the ``orm_inspect_tool`` ``_MODEL_POLICIES`` allowlist from 9 to 11
models by adding:

* ``persistence.SpiderData`` (Ledger wish-list #2) — the canonical
  spider-persistence model (116K+ rows) with public-web-content sensitivity
  and ``expensive_text_fields=('content', 'raw_html')`` to block ``contains``
  scans on oversized article bodies + raw HTML.
* ``core.Opportunity`` (Ledger wish-list #3) — the revenue-side
  opportunities model (2.6K+ rows, user-facing) with
  ``expensive_text_fields=('description',)``.

Follows the S2871 Ledger #23 (LegacySpiderData) precedent for shape.

Run::

    python manage.py test core.tests.test_s2873_orm_inspect_spider_data_opportunity -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_unified_system import Opportunity
from core.services.tool_dispatcher import ToolDispatcher
from persistence.models import SpiderData


User = get_user_model()


class OrmInspectToolSpiderDataAllowlistTests(TestCase):
    """Wish-list #2: persistence.SpiderData is inspectable via orm_inspect_tool."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f's2873-sd-{uuid.uuid4().hex[:8]}',
            email='s2873-sd@example.com',
            password='x',
        )
        cls.row_alpha = SpiderData.objects.create(
            spider_name='s2873_sd_alpha',
            source_url='https://example.com/alpha',
            source_platform='example',
            title='alpha row',
            content='alpha article body',
            raw_html='<html>alpha</html>',
            data_type='article',
            category='ai',
            content_hash=uuid.uuid4().hex,
        )
        cls.row_beta = SpiderData.objects.create(
            spider_name='s2873_sd_beta',
            source_url='https://example.com/beta',
            source_platform='example',
            title='beta row',
            content='beta article body',
            raw_html='<html>beta</html>',
            data_type='article',
            category='ai',
            content_hash=uuid.uuid4().hex,
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_orm_inspect(
            'orm_inspect_tool', payload, self.user.id, 'test-trace-s2873-sd',
        )

    def test_list_models_includes_spider_data(self):
        result = self._dispatch(action='list_models')
        self.assertTrue(result.get('ok'), result)
        names = {m['name'] for m in result['models']}
        self.assertIn('SpiderData', names)
        sd_entry = next(m for m in result['models'] if m['name'] == 'SpiderData')
        self.assertEqual(sd_entry['app_label'], 'persistence')
        self.assertFalse(sd_entry['sensitive'])
        self.assertEqual(
            sorted(sd_entry['expensive_text_fields']),
            ['content', 'raw_html'],
        )

    def test_describe_model_returns_fields(self):
        result = self._dispatch(action='describe_model', model='SpiderData')
        self.assertTrue(result.get('ok'), result)
        field_names = {f['name'] for f in result['fields']}
        for expected in ('spider_name', 'content', 'raw_html', 'metadata', 'opportunity_score'):
            self.assertIn(expected, field_names)

    def test_get_by_pk_returns_seeded_row(self):
        result = self._dispatch(action='get', model='SpiderData', pk=str(self.row_alpha.pk))
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(result['row']['spider_name'], 's2873_sd_alpha')

    def test_filter_returns_seeded_row(self):
        result = self._dispatch(
            action='filter',
            model='SpiderData',
            filter_kwargs={'spider_name': 's2873_sd_alpha'},
            limit=5,
        )
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['spider_name'], 's2873_sd_alpha')

    def test_count_by_spider_name(self):
        result = self._dispatch(
            action='count_by',
            model='SpiderData',
            field='spider_name',
            filter_kwargs={'spider_name__in': ['s2873_sd_alpha', 's2873_sd_beta']},
        )
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(result['total_matching'], 2)
        groups = {g['value']: g['count'] for g in result['groups']}
        self.assertEqual(groups.get('s2873_sd_alpha'), 1)
        self.assertEqual(groups.get('s2873_sd_beta'), 1)

    def test_content_expensive_field_rejects_contains(self):
        """Policy guard: content is on expensive_text_fields — contains rejected."""
        result = self._dispatch(
            action='filter',
            model='SpiderData',
            filter_kwargs={'content__icontains': 'anything'},
        )
        self.assertFalse(result.get('ok'), result)
        self.assertIn('expensive', result.get('error', '').lower())

    def test_raw_html_expensive_field_rejects_contains(self):
        result = self._dispatch(
            action='filter',
            model='SpiderData',
            filter_kwargs={'raw_html__icontains': '<html>'},
        )
        self.assertFalse(result.get('ok'), result)
        self.assertIn('expensive', result.get('error', '').lower())


class OrmInspectToolOpportunityAllowlistTests(TestCase):
    """Wish-list #3: core.Opportunity is inspectable via orm_inspect_tool."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f's2873-op-{uuid.uuid4().hex[:8]}',
            email='s2873-op@example.com',
            password='x',
        )
        cls.opp_alpha = Opportunity.objects.create(
            user=cls.user,
            title='alpha opportunity',
            opportunity_type='content',
            source='s2873_source_alpha',
            description='alpha opportunity description',
        )
        cls.opp_beta = Opportunity.objects.create(
            user=cls.user,
            title='beta opportunity',
            opportunity_type='content',
            source='s2873_source_beta',
            description='beta opportunity description',
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_orm_inspect(
            'orm_inspect_tool', payload, self.user.id, 'test-trace-s2873-op',
        )

    def test_list_models_includes_opportunity(self):
        result = self._dispatch(action='list_models')
        self.assertTrue(result.get('ok'), result)
        names = {m['name'] for m in result['models']}
        self.assertIn('Opportunity', names)
        op_entry = next(m for m in result['models'] if m['name'] == 'Opportunity')
        self.assertEqual(op_entry['app_label'], 'core')
        self.assertFalse(op_entry['sensitive'])
        self.assertEqual(list(op_entry['expensive_text_fields']), ['description'])

    def test_describe_model_returns_fields(self):
        result = self._dispatch(action='describe_model', model='Opportunity')
        self.assertTrue(result.get('ok'), result)
        field_names = {f['name'] for f in result['fields']}
        for expected in ('title', 'source', 'description', 'user', 'spider_data'):
            self.assertIn(expected, field_names)

    def test_fk_fields_emit_as_id_on_get(self):
        """FK emit-as-*_id convention: 'user' FK returns user_id, not the object."""
        result = self._dispatch(action='get', model='Opportunity', pk=str(self.opp_alpha.pk))
        self.assertTrue(result.get('ok'), result)
        # FK values are surfaced under the FK field name (per _serialize_row) as the id
        self.assertEqual(result['row']['user'], self.user.id)

    def test_filter_by_source(self):
        result = self._dispatch(
            action='filter',
            model='Opportunity',
            filter_kwargs={'source': 's2873_source_alpha'},
            limit=5,
        )
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['source'], 's2873_source_alpha')

    def test_count_by_source(self):
        result = self._dispatch(
            action='count_by',
            model='Opportunity',
            field='source',
            filter_kwargs={'source__in': ['s2873_source_alpha', 's2873_source_beta']},
        )
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(result['total_matching'], 2)
        groups = {g['value']: g['count'] for g in result['groups']}
        self.assertEqual(groups.get('s2873_source_alpha'), 1)
        self.assertEqual(groups.get('s2873_source_beta'), 1)

    def test_description_expensive_field_rejects_contains(self):
        result = self._dispatch(
            action='filter',
            model='Opportunity',
            filter_kwargs={'description__icontains': 'anything'},
        )
        self.assertFalse(result.get('ok'), result)
        self.assertIn('expensive', result.get('error', '').lower())
