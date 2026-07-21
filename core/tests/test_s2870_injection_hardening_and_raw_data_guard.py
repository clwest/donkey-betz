"""
S2870 slate — Rigby Tool Gap Ledger #20 + #21 grouped.

#20: `intelligence_tool.signal_clusters` filter injection hardening —
`pattern_type` schema now uses `anyOf: [enum, null]` shape so GPT-5.2 has
a proper 'no filter' path. Descriptions on all three filter params
(pattern_type, min_confidence, window_hours) explicitly forbid default-fill.
Handler already tolerates None/empty — these tests protect that regression path.

#21: `spider_data_bridge._safe_dict` guard — 5 callsites in
`core/learning_bridges/spider_data_bridge.py` now route `raw_data` through
`_safe_dict()` so list-form `raw_data` (surfaced by S2869 test fixture 6)
no longer crashes with AttributeError.

Run::

    python manage.py test core.tests.test_s2870_injection_hardening_and_raw_data_guard -v2
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import LegacySpiderData
from core.models import SignalCluster
from core.services.tool_dispatcher import ToolDispatcher
from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
from core.learning_bridges.spider_data_bridge import (
    _safe_dict,
    SpiderDataLearningLoop,
)


User = get_user_model()


class SignalClustersInjectionHardeningTests(TestCase):
    """Ledger #20: schema anyOf-null on pattern_type + handler tolerates
    None/empty on all three filter params."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f's2870-inj-{uuid.uuid4().hex[:8]}',
            email='s2870-inj@example.com',
            password='x',
        )
        now = timezone.now()
        # Two clusters with different pattern_types + confidences so filters
        # can be exercised without any cluster surviving all three defaults.
        cls.cluster_lo = SignalCluster.objects.create(
            name='s2870 low-conf cluster',
            pattern_type='trend_emergence',
            confidence=0.3,
            keywords=['s2870-inj'],
            detected_at=now - timedelta(hours=1),
            source_breakdown={'hackernews': 3},
            spider_data_ids=[],
        )
        cls.cluster_hi = SignalCluster.objects.create(
            name='s2870 hi-conf cluster',
            pattern_type='demand_spike',
            confidence=0.9,
            keywords=['s2870-inj'],
            detected_at=now - timedelta(hours=2),
            source_breakdown={'hackernews': 5},
            spider_data_ids=[],
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **kwargs):
        payload = {'action': 'signal_clusters', 'query': 's2870-inj', 'limit': 30, **kwargs}
        result = self.dispatcher._handle_intelligence(
            'intelligence_tool', payload, self.user.id, 'test-trace-s2870',
        )
        self.assertEqual(result.get('action'), 'signal_clusters')
        return result

    def test_pattern_type_schema_has_anyof_null_shape(self):
        """Schema-side hardening: pattern_type must accept null (anyOf shape)."""
        tool = next(
            (t for t in PA_TOOL_SCHEMAS if t.get('name') == 'intelligence_tool'),
            None,
        )
        self.assertIsNotNone(tool, "intelligence_tool must be in PA_TOOL_SCHEMAS")
        props = tool['parameters']['properties']
        pt = props.get('pattern_type', {})
        any_of = pt.get('anyOf')
        self.assertIsInstance(any_of, list, "pattern_type must use anyOf shape")
        types = {branch.get('type') for branch in any_of if isinstance(branch, dict)}
        self.assertIn('null', types, "pattern_type anyOf must include null branch")
        self.assertIn('string', types, "pattern_type anyOf must retain string enum branch")

    def test_pattern_type_none_treated_as_no_filter(self):
        """Regression: handler already treats None as no-op — protect that."""
        result = self._dispatch(pattern_type=None)
        # Both clusters have s2870-inj keyword; no pattern filter → both visible.
        self.assertEqual(result['count'], 2)

    def test_pattern_type_empty_string_treated_as_no_filter(self):
        """Regression: empty string is falsy — no filter applied."""
        result = self._dispatch(pattern_type='')
        self.assertEqual(result['count'], 2)

    def test_min_confidence_none_treated_as_no_filter(self):
        """Regression: None min_confidence → no filter."""
        result = self._dispatch(min_confidence=None)
        self.assertEqual(result['count'], 2)

    def test_min_confidence_zero_treated_as_no_filter(self):
        """Regression: 0.0 confidence gte → matches all rows (effective no-op)."""
        result = self._dispatch(min_confidence=0.0)
        self.assertEqual(result['count'], 2)

    def test_window_hours_none_treated_as_no_filter(self):
        """Regression: None window_hours → no filter."""
        result = self._dispatch(window_hours=None)
        self.assertEqual(result['count'], 2)

    def test_window_hours_zero_treated_as_no_filter(self):
        """Regression: 0 window_hours is falsy — no filter."""
        result = self._dispatch(window_hours=0)
        self.assertEqual(result['count'], 2)

    def test_all_three_omitted_returns_both_clusters(self):
        """The core scenario Ledger #20 fixes: omit all 3 filters, get all
        matching clusters (not zero from injected defaults). Handler tolerance
        was always correct; schema fix removes the model injection driver."""
        result = self._dispatch()  # no pattern_type, min_confidence, or window_hours
        self.assertEqual(result['count'], 2)

    def test_pattern_type_explicitly_set_still_filters(self):
        """Verify anyOf-null shape didn't break explicit filtering."""
        result = self._dispatch(pattern_type='demand_spike')
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['clusters'][0]['pattern_type'], 'demand_spike')


class SpiderDataBridgeSafeDictTests(TestCase):
    """Ledger #21: _safe_dict helper + 5 callsite migration in
    core/learning_bridges/spider_data_bridge.py."""

    def test_safe_dict_returns_dict_unchanged(self):
        d = {'items': [{'title': 'x'}]}
        self.assertIs(_safe_dict(d), d)

    def test_safe_dict_returns_empty_for_list(self):
        """The bug fix: list-form raw_data returns {} instead of crashing."""
        self.assertEqual(_safe_dict([{'a': 1}]), {})

    def test_safe_dict_returns_empty_for_none(self):
        self.assertEqual(_safe_dict(None), {})

    def test_safe_dict_returns_empty_for_str(self):
        self.assertEqual(_safe_dict('some string'), {})

    def test_safe_dict_returns_empty_for_int(self):
        self.assertEqual(_safe_dict(42), {})

    def test_extract_patterns_no_crash_on_list_raw_data(self):
        """Integration: _extract_patterns on a LegacySpiderData with list-form
        raw_data must not raise AttributeError (was the crash surface)."""
        row = LegacySpiderData.objects.create(
            spider_name='s2870_list_form',
            data_type='test',
            raw_data=[{'title': 'ignored because list not dict'}],
        )
        loop = SpiderDataLearningLoop()
        # _extract_patterns is where the historical crash originated (line 92).
        # It must complete and return item_count == 0 (since we can't extract).
        patterns = loop._extract_patterns(row)
        self.assertEqual(patterns['item_count'], 0)
        self.assertEqual(patterns['spider_name'], 's2870_list_form')

    def test_calculate_completeness_no_crash_on_list_raw_data(self):
        """Line 280 callsite: _calculate_completeness with list raw_data."""
        row = LegacySpiderData.objects.create(
            spider_name='s2870_list_completeness',
            data_type='test',
            source_url='https://example.com',
            raw_data=[{'noop': True}],
        )
        loop = SpiderDataLearningLoop()
        score = loop._calculate_completeness(row)
        # source_url adds 0.25; no items detectable → no items bonus.
        self.assertAlmostEqual(score, 0.25, places=2)

    def test_evaluate_actionability_no_crash_on_list_raw_data(self):
        """Line 376 callsite (@staticmethod evaluate_actionability)."""
        row = LegacySpiderData.objects.create(
            spider_name='s2870_list_actionable',
            data_type='test',
            relevance_score=75,
            raw_data=[{'ignored': True}],
        )
        # list raw_data → items = [] → not actionable (no items).
        result = SpiderDataLearningLoop.evaluate_actionability(row)
        self.assertFalse(result)

    def test_extract_patterns_dict_raw_data_unchanged(self):
        """Regression: dict-form raw_data path still works."""
        row = LegacySpiderData.objects.create(
            spider_name='s2870_dict_form',
            data_type='test',
            raw_data={'items': [{'title': 'a'}, {'title': 'b'}, {'title': 'c'}]},
        )
        loop = SpiderDataLearningLoop()
        patterns = loop._extract_patterns(row)
        self.assertEqual(patterns['item_count'], 3)
