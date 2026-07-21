"""
S2872 — Rigby Tool Gap Ledger #22b: broader raw_data_dict sweep.

Extends S2871 #22 (the property). This sweep migrates ~44 external callsites
across 30 files that previously used the ``raw = X.raw_data or {}`` pattern
on LegacySpiderData readers. That pattern silently failed on list-form rows
(``[] or {}`` returns ``[]``, then ``.get()`` on the list raises
AttributeError). All migrated sites now use ``X.raw_data_dict``.

Also adds Rigby's Q4 zoom-out fold: the property now emits rate-limited debug
telemetry when it falls back to ``{}``, so schema drift is observable rather
than silently trading crash-visibility for data-drop-invisibility.

Run::

    python manage.py test core.tests.test_s2872_ledger_22b_raw_data_dict_sweep -v2
"""

import logging
import uuid
from unittest import mock

from django.test import TestCase

from core.models_unified_system import (
    LegacySpiderData,
    _NON_DICT_RAW_DATA_COUNTER,
    _record_non_dict_raw_data,
)


# ═══════════════════════════════════════════════════════════════════════════
# Test 1 — Migrated callsites no longer crash on list-form raw_data
# ═══════════════════════════════════════════════════════════════════════════


class MigratedCallsitesListFormTests(TestCase):
    """Spot-check that a sample of migrated call paths no longer raises
    AttributeError when a LegacySpiderData row holds list-form raw_data.

    Prior to #22b, each of these paths would crash on the exact code line
    surveyed in the S2872 pre-code SIGN. This test seeds a list-form row and
    invokes the migrated helpers to prove the pattern is dead.
    """

    def _list_form_row(self, spider_name, data_type='test'):
        return LegacySpiderData.objects.create(
            spider_name=spider_name,
            data_type=data_type,
            source_url='https://example.com',
            raw_data=[{'a': 1}, {'b': 2}],
        )

    def test_situation_trigger_evaluate_on_list_form(self):
        """core/models_situation_triggers.py:298 migration — evaluate() no
        longer crashes when spider_data.raw_data is list-form."""
        from core.models_situation_triggers import SituationTrigger

        row = self._list_form_row('reddit')
        # Construct in-memory (avoid FK setup); evaluate() only reads
        # spider_data.raw_data via the property.
        trigger = SituationTrigger(
            name='test',
            trigger_type='threshold',
            target_field='items.0.price',
            target_spiders=['reddit'],
            operator='gt',
            threshold_value=0,
            is_active=True,
        )
        matches, value = trigger.evaluate(row)
        # No AttributeError. Result may be False/None; we assert no crash.
        self.assertIsNotNone(matches)  # bool result — either True or False

    def test_signal_aggregation_url_extraction_on_list_form(self):
        """core/services/signal_aggregation_service.py:366 migration —
        _extract_url_from_spider_data no longer crashes."""
        from core.services.signal_aggregation_service import SignalAggregationService

        row = self._list_form_row('hackernews')
        svc = SignalAggregationService()
        # Method reads sd.raw_data via the property; list-form → falls
        # through to empty string, no crash.
        url = svc._extract_url_from_spider_data(row)
        self.assertEqual(url, '')

    def test_signal_aggregation_text_extraction_on_list_form(self):
        """core/services/signal_aggregation_service.py:397 migration."""
        from core.services.signal_aggregation_service import SignalAggregationService

        row = self._list_form_row('bluesky')
        svc = SignalAggregationService()
        text = svc._extract_text_from_spider_data(row)
        # Empty (no dict fields to extract from a list-form row), but no crash.
        self.assertIsInstance(text, str)


# ═══════════════════════════════════════════════════════════════════════════
# Test 2 — Dict-form correctness (no regression on the happy path)
# ═══════════════════════════════════════════════════════════════════════════


class DictFormNoRegressionTests(TestCase):
    """Migrating from ``X.raw_data or {}`` to ``X.raw_data_dict`` must
    preserve behaviour on dict-form rows (the common case)."""

    def _dict_row(self, spider_name='test', raw_data=None):
        return LegacySpiderData.objects.create(
            spider_name=spider_name,
            data_type='test',
            source_url='https://example.com/x',
            raw_data=raw_data or {'title': 'hello', 'items': [{'k': 'v'}]},
        )

    def test_situation_trigger_dict_form(self):
        from core.models_situation_triggers import SituationTrigger

        row = self._dict_row(
            spider_name='reddit',
            raw_data={'items': [{'price': 42}]},
        )
        trigger = SituationTrigger(
            name='t',
            trigger_type='threshold',
            target_field='price',
            target_spiders=['reddit'],
            operator='gt',
            threshold_value=10,
            is_active=True,
        )
        matches, value = trigger.evaluate(row)
        self.assertTrue(matches)
        self.assertEqual(value, 42)

    def test_signal_aggregation_url_dict_form(self):
        from core.services.signal_aggregation_service import SignalAggregationService

        row = self._dict_row(raw_data={'url': 'https://example.com/live'})
        svc = SignalAggregationService()
        self.assertEqual(svc._extract_url_from_spider_data(row), 'https://example.com/live')


# ═══════════════════════════════════════════════════════════════════════════
# Test 3 — Telemetry fold (Rigby Q4 zoom-out)
# ═══════════════════════════════════════════════════════════════════════════


class NonDictTelemetryTests(TestCase):
    """The property now emits a rate-limited debug log + increments a
    per-spider counter when it falls back to ``{}``. This is the Rigby Q4
    fold: schema drift is observable rather than silent."""

    def setUp(self):
        _NON_DICT_RAW_DATA_COUNTER.clear()

    def test_counter_increments_on_list_form(self):
        row = LegacySpiderData.objects.create(
            spider_name='s2872-telemetry-list',
            data_type='test',
            source_url='https://example.com',
            raw_data=[{'x': 1}],
        )
        _ = row.raw_data_dict
        self.assertEqual(_NON_DICT_RAW_DATA_COUNTER['s2872-telemetry-list'], 1)

    def test_counter_does_not_increment_on_dict_form(self):
        row = LegacySpiderData.objects.create(
            spider_name='s2872-telemetry-dict',
            data_type='test',
            source_url='https://example.com',
            raw_data={'x': 1},
        )
        _ = row.raw_data_dict
        self.assertNotIn('s2872-telemetry-dict', _NON_DICT_RAW_DATA_COUNTER)

    def test_first_fallback_emits_debug_log(self):
        row = LegacySpiderData.objects.create(
            spider_name='s2872-telemetry-log',
            data_type='test',
            source_url='https://example.com',
            raw_data=['a', 'b'],
        )
        with self.assertLogs('core.models_unified_system', level='DEBUG') as cm:
            _ = row.raw_data_dict
        joined = '\n'.join(cm.output)
        self.assertIn('raw_data_dict fallback', joined)
        self.assertIn('s2872-telemetry-log', joined)
        self.assertIn('list', joined)  # type name

    def test_repeated_fallbacks_rate_limited(self):
        """Only 1st + every 100th fallback logs; the rest just bump the
        counter silently. Uses list-form raw_data (DB has NOT NULL on the
        column, but list is legitimate JSON per the S2869 fixture class)."""
        row = LegacySpiderData.objects.create(
            spider_name='s2872-rate-limit',
            data_type='test',
            source_url='https://example.com',
            raw_data=['list', 'form'],
        )
        with self.assertLogs('core.models_unified_system', level='DEBUG') as cm:
            for _ in range(101):
                _ = row.raw_data_dict
        # First hit (count=1) + 100th hit (count=100) = 2 log lines.
        drift_lines = [ln for ln in cm.output if 'raw_data_dict fallback' in ln]
        self.assertEqual(len(drift_lines), 2)
        self.assertEqual(_NON_DICT_RAW_DATA_COUNTER['s2872-rate-limit'], 101)

    def test_none_form_recorded_with_nonetype(self):
        """None-form raw_data can only arise in-memory (unsaved instance) —
        the DB column is NOT NULL — but the property must still guard against
        it because callers may hold pre-save instances."""
        row = LegacySpiderData(
            spider_name='s2872-none',
            data_type='test',
            source_url='https://example.com',
            raw_data=None,
        )
        with self.assertLogs('core.models_unified_system', level='DEBUG') as cm:
            _ = row.raw_data_dict
        self.assertIn('NoneType', '\n'.join(cm.output))

    def test_helper_direct_invocation(self):
        """Guard against future refactors that bypass the property but
        still want the counter to work."""

        class Fake:
            spider_name = 'direct-invoke'

        _record_non_dict_raw_data(Fake(), [1, 2, 3])
        self.assertEqual(_NON_DICT_RAW_DATA_COUNTER['direct-invoke'], 1)
