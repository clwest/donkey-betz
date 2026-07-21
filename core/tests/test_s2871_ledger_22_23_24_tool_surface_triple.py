"""
S2871 slate — Rigby Tool Gap Ledger #22 + #23 + #24 grouped.

#22: `LegacySpiderData.raw_data_dict` @property promoted from the S2870
file-local `_safe_dict` helper. Callers doing ``instance.raw_data.get(...)``
now route through the property; list-form ``raw_data`` no longer crashes
with AttributeError. Also: the model's own ``get_searchable_text()`` was
migrated to use the property (previously would have crashed on the same
model instance it's a method of).

#23: `LegacySpiderData` added to the ``orm_inspect_tool`` ``_MODEL_POLICIES``
allowlist. ``sensitive=False`` (spider data is public web content),
``expensive_text_fields=('embedding_text',)``. Unblocks the S2870 Q4
verification path where Rigby couldn't quantify list-form prevalence
because the model wasn't inspectable.

#24: `repo_tool` search action gets conditional wall-clock timeouts:
narrowed searches (caller supplied ``path`` and/or ``file_type``) get
30s/10s budgets; repo-wide default searches keep the tight 10s/5s cap.
Timeout errors now return structured error codes + narrowing hints.

Run::

    python manage.py test core.tests.test_s2871_ledger_22_23_24_tool_surface_triple -v2
"""

import subprocess
import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_unified_system import LegacySpiderData
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


# ═══════════════════════════════════════════════════════════════════════════
# Ledger #22 — LegacySpiderData.raw_data_dict property
# ═══════════════════════════════════════════════════════════════════════════


class LegacySpiderDataRawDataDictPropertyTests(TestCase):
    """Ledger #22: @property raw_data_dict guarantees a dict, guards
    against AttributeError on list-form / null / non-dict rows."""

    def _row(self, raw_data):
        return LegacySpiderData.objects.create(
            spider_name=f's2871-{uuid.uuid4().hex[:8]}',
            data_type='test',
            source_url='https://example.com',
            raw_data=raw_data,
        )

    def test_dict_form_returns_same_dict(self):
        d = {'items': [{'title': 'x'}]}
        row = self._row(d)
        self.assertEqual(row.raw_data_dict, d)

    def test_list_form_returns_empty_dict(self):
        """Regression: the S2869 fixture-6 crash class. Must return {},
        not the list."""
        row = self._row([{'a': 1}, {'b': 2}])
        self.assertEqual(row.raw_data_dict, {})

    def test_string_form_returns_empty_dict(self):
        row = self._row('literally a string')
        self.assertEqual(row.raw_data_dict, {})

    def test_int_form_returns_empty_dict(self):
        row = self._row(42)
        self.assertEqual(row.raw_data_dict, {})

    def test_get_on_list_form_does_not_crash(self):
        """The bug this property fixes: reader code doing .get() on list-form
        raw_data no longer raises AttributeError."""
        row = self._row(['not', 'a', 'dict'])
        self.assertEqual(row.raw_data_dict.get('items', []), [])
        self.assertIsNone(row.raw_data_dict.get('missing'))

    def test_get_searchable_text_does_not_crash_on_list_form(self):
        """The model's own get_searchable_text() method was itself a crash
        site (line 3806) — now routed through the property."""
        row = self._row([{'ignored': True}])
        self.assertEqual(row.get_searchable_text(), '')

    def test_get_searchable_text_dict_path_unchanged(self):
        """Regression: dict-form searchable-text extraction still works."""
        row = self._row({'items': [{'title': 'hello', 'description': 'world'}]})
        text = row.get_searchable_text()
        self.assertIn('hello', text)
        self.assertIn('world', text)


# ═══════════════════════════════════════════════════════════════════════════
# Ledger #23 — LegacySpiderData in orm_inspect_tool allowlist
# ═══════════════════════════════════════════════════════════════════════════


class OrmInspectToolLegacySpiderDataAllowlistTests(TestCase):
    """Ledger #23: LegacySpiderData now inspectable via orm_inspect_tool,
    unblocking S2870 Q4 verification path for spider-data questions."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f's2871-orm-{uuid.uuid4().hex[:8]}',
            email='s2871-orm@example.com',
            password='x',
        )
        # Seed one dict-form + one list-form so both count and search work.
        LegacySpiderData.objects.create(
            spider_name='s2871_orm_dict',
            data_type='test',
            source_url='https://example.com/dict',
            raw_data={'items': [{'title': 'dict-form row'}]},
        )
        LegacySpiderData.objects.create(
            spider_name='s2871_orm_list',
            data_type='test',
            source_url='https://example.com/list',
            raw_data=[{'title': 'list-form row'}],
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_orm_inspect(
            'orm_inspect_tool', payload, self.user.id, 'test-trace-s2871',
        )

    def test_describe_model_returns_fields(self):
        result = self._dispatch(action='describe_model', model='LegacySpiderData')
        self.assertTrue(result.get('ok'), result)
        field_names = {f['name'] for f in result['fields']}
        # Core schema fields must be present.
        self.assertIn('spider_name', field_names)
        self.assertIn('raw_data', field_names)
        self.assertIn('processed_data', field_names)

    def test_filter_returns_seeded_dict_form_row(self):
        result = self._dispatch(
            action='filter',
            model='LegacySpiderData',
            filter_kwargs={'spider_name': 's2871_orm_dict'},
            limit=5,
        )
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['spider_name'], 's2871_orm_dict')

    def test_filter_returns_seeded_list_form_row(self):
        """Regression: LegacySpiderData rows with list-form raw_data are
        still returnable via orm_inspect_tool (the tool uses JSON-safe
        serialization, so list raw_data doesn't crash the serializer)."""
        result = self._dispatch(
            action='filter',
            model='LegacySpiderData',
            filter_kwargs={'spider_name': 's2871_orm_list'},
            limit=5,
            include_json_fields=True,
        )
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['spider_name'], 's2871_orm_list')

    def test_count_by_spider_name_returns_seeded_rows(self):
        result = self._dispatch(
            action='count_by',
            model='LegacySpiderData',
            field='spider_name',
            filter_kwargs={'spider_name__in': ['s2871_orm_dict', 's2871_orm_list']},
        )
        self.assertTrue(result.get('ok'), result)
        self.assertEqual(result['total_matching'], 2)
        groups = {g['value']: g['count'] for g in result['groups']}
        self.assertEqual(groups.get('s2871_orm_dict'), 1)
        self.assertEqual(groups.get('s2871_orm_list'), 1)

    def test_embedding_text_expensive_field_rejects_contains_lookup(self):
        """Policy guard: expensive_text_fields=('embedding_text',) must
        block contains/icontains lookups per S2866 pre-code SIGN Q3."""
        result = self._dispatch(
            action='filter',
            model='LegacySpiderData',
            filter_kwargs={'embedding_text__icontains': 'anything'},
        )
        self.assertFalse(result.get('ok'), result)
        self.assertIn('expensive', result.get('error', '').lower())


# ═══════════════════════════════════════════════════════════════════════════
# Ledger #24 — repo_tool conditional timeout + structured errors
# ═══════════════════════════════════════════════════════════════════════════


class RepoToolConditionalTimeoutTests(TestCase):
    """Ledger #24: repo_tool search uses tight 10s/5s budget by default;
    narrowed searches (path or file_type provided) unlock 30s/10s.
    Timeout errors return structured error_code + narrowing hint."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()
        self.user = User.objects.create_user(
            username=f's2871-repo-{uuid.uuid4().hex[:8]}',
            email='s2871-repo@example.com',
            password='x',
        )

    def _search(self, **payload):
        payload.setdefault('action', 'search')
        payload.setdefault('query', 'unlikely_needle_s2871')
        return self.dispatcher._handle_repo(
            'repo_tool', payload, self.user.id, 'test-trace-s2871-repo',
        )

    def test_repo_wide_timeout_returns_structured_error(self):
        """Repo-wide (no path, no file_type) TimeoutExpired → error_code
        + suggested_paths in narrowing_hint."""
        with mock.patch(
            'subprocess.run',
            side_effect=subprocess.TimeoutExpired(cmd='grep', timeout=10),
        ):
            result = self._search()  # no path, no file_type
        self.assertEqual(result.get('error_code'), 'search_timeout_repo_wide')
        self.assertEqual(result.get('timeout_seconds'), 10)
        hint = result.get('narrowing_hint') or {}
        self.assertTrue(hint.get('add_path'))
        self.assertTrue(hint.get('add_file_type'))
        self.assertIn('core/', hint.get('suggested_paths', []))

    def test_narrowed_search_uses_30s_budget_on_timeout(self):
        """Narrowed (path or file_type given) TimeoutExpired → 30s cap
        error, tells caller to narrow further."""
        with mock.patch(
            'subprocess.run',
            side_effect=subprocess.TimeoutExpired(cmd='grep', timeout=30),
        ):
            result = self._search(path='core/', file_type='py')
        self.assertEqual(result.get('error_code'), 'search_timeout_narrowed')
        self.assertEqual(result.get('timeout_seconds'), 30)
        # Narrowed error message should NOT contain the repo-wide hint.
        self.assertNotIn('narrowing_hint', result)

    def test_path_only_counts_as_narrowed(self):
        """Path alone (without file_type) should unlock the 30s budget."""
        with mock.patch(
            'subprocess.run',
            side_effect=subprocess.TimeoutExpired(cmd='grep', timeout=30),
        ):
            result = self._search(path='core/')
        self.assertEqual(result.get('error_code'), 'search_timeout_narrowed')
        self.assertEqual(result.get('timeout_seconds'), 30)

    def test_file_type_only_counts_as_narrowed(self):
        """file_type alone (without path) should unlock the 30s budget."""
        with mock.patch(
            'subprocess.run',
            side_effect=subprocess.TimeoutExpired(cmd='grep', timeout=30),
        ):
            result = self._search(file_type='py')
        self.assertEqual(result.get('error_code'), 'search_timeout_narrowed')
        self.assertEqual(result.get('timeout_seconds'), 30)

    def test_query_required(self):
        """Sanity: empty query still errors before touching timeout logic."""
        result = self._search(query='')
        self.assertIn('error', result)
        self.assertIn('query is required', result['error'])
