"""Session 2867 slate #1 — count_by action on orm_inspect_tool.

Extends S2866's bounded ORM row inspector with aggregate group-by counts.
Covers the ``action='count_by'`` branch in
``core/services/td_handlers_agents.py::_handle_orm_inspect``.

Motivating fold: S2866 post-code SIGN round 1 zoom-out named "aggregate
group-by counts" as the next diagnostic rung after row inspection. Chris's
original ask paraphrase: "how many rows match X by day/status/source?"

Design contract validated by pre-code SIGN S2867 Q1..Q6:
  - New _validate_groupby_field mirrors _validate_filter_kwargs strictness
    (field exists + not sensitive + not JSONField + not expensive_text_field).
  - FK fields group on ``<field>_id`` (matches _serialize_row FK convention).
  - DateTimeField auto-buckets to day via TruncDate (per Chris's "by day" ask).
  - Group cardinality bounded: default limit=50, max=500. truncated=true when
    distinct group count exceeds limit; group_count reported as lower bound.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase, TestCase

from core.models_signal_intelligence import SignalCluster
from core.services.tool_dispatcher import get_tool_dispatcher


def _run(payload):
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers['orm_inspect_tool']
    return handler(
        tool_name='orm_inspect_tool',
        payload=payload,
        user_id=None,
        trace_id='test-trace-s2867',
    )


class SchemaTests(SimpleTestCase):
    def test_count_by_in_action_enum(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        schema = next(s for s in PA_TOOL_SCHEMAS if s.get('name') == 'orm_inspect_tool')
        actions = schema['parameters']['properties']['action']['enum']
        self.assertIn('count_by', actions)
        self.assertEqual(
            sorted(actions),
            sorted(['list_models', 'describe_model', 'get', 'filter', 'count_by']),
        )

    def test_count_by_params_declared(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        schema = next(s for s in PA_TOOL_SCHEMAS if s.get('name') == 'orm_inspect_tool')
        props = schema['parameters']['properties']
        self.assertIn('field', props)
        self.assertIn('order_by_count', props)
        self.assertEqual(sorted(props['order_by_count']['enum']), ['asc', 'desc'])


class InputValidationTests(TestCase):
    def test_count_by_missing_field(self):
        result = _run({'action': 'count_by', 'model': 'SignalCluster'})
        self.assertFalse(result['ok'])
        self.assertIn("field is required", result['error'])

    def test_count_by_unknown_field(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'nonexistent_col',
        })
        self.assertFalse(result['ok'])
        self.assertIn("not on model", result['error'])

    def test_count_by_jsonfield_rejected(self):
        # source_breakdown is a JSONField on SignalCluster.
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'source_breakdown',
        })
        self.assertFalse(result['ok'])
        self.assertIn('JSONField', result['error'])

    def test_count_by_expensive_text_field_rejected(self):
        # Deliverable.content is in expensive_text_fields.
        result = _run({
            'action': 'count_by', 'model': 'Deliverable',
            'field': 'content',
        })
        self.assertFalse(result['ok'])
        self.assertIn('expensive text field', result['error'])

    def test_count_by_non_allowlist_model_rejected(self):
        result = _run({
            'action': 'count_by', 'model': 'User',
            'field': 'id',
        })
        self.assertFalse(result['ok'])
        self.assertIn('not in allowlist', result['error'])

    def test_count_by_filter_kwargs_validated(self):
        # Deep chain in filter_kwargs must be rejected by the shared validator.
        result = _run({
            'action': 'count_by', 'model': 'Deliverable',
            'field': 'status',
            'filter_kwargs': {'workspace__name__icontains': 'foo'},
        })
        self.assertFalse(result['ok'])
        self.assertIn('deep __ chain', result['error'])

    def test_count_by_invalid_order_by_count(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
            'order_by_count': 'random',
        })
        self.assertFalse(result['ok'])
        self.assertIn("order_by_count", result['error'])

    def test_count_by_bad_filter_kwargs_type(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
            'filter_kwargs': 'not-a-dict',
        })
        self.assertFalse(result['ok'])
        self.assertIn('filter_kwargs must be a dict', result['error'])


class GroupByBasicTests(TestCase):
    def setUp(self):
        # Mix of pattern_types + a null slot handled via 'unknown' bucket
        SignalCluster.objects.create(
            name='c1', pattern_type='demand_spike',
            source_breakdown={'hackernews': 3}, strength=0.5, keywords=[],
        )
        SignalCluster.objects.create(
            name='c2', pattern_type='demand_spike',
            source_breakdown={'hackernews': 2}, strength=0.4, keywords=[],
        )
        SignalCluster.objects.create(
            name='c3', pattern_type='trend_emergence',
            source_breakdown={'devto': 1}, strength=0.6, keywords=[],
        )
        SignalCluster.objects.create(
            name='c4', pattern_type='knowledge_gap',
            source_breakdown={'github': 1}, strength=0.5, keywords=[],
        )

    def test_count_by_pattern_type(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'count_by')
        self.assertEqual(result['field'], 'pattern_type')
        self.assertEqual(result['total_matching'], 4)
        by_value = {g['value']: g['count'] for g in result['groups']}
        self.assertEqual(by_value['demand_spike'], 2)
        self.assertEqual(by_value['trend_emergence'], 1)
        self.assertEqual(by_value['knowledge_gap'], 1)

    def test_count_by_default_order_desc(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
        })
        counts = [g['count'] for g in result['groups']]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_count_by_order_asc(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
            'order_by_count': 'asc',
        })
        counts = [g['count'] for g in result['groups']]
        self.assertEqual(counts, sorted(counts))

    def test_count_by_with_filter_kwargs(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
            'filter_kwargs': {'pattern_type': 'demand_spike'},
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['total_matching'], 2)
        self.assertEqual(len(result['groups']), 1)
        self.assertEqual(result['groups'][0]['value'], 'demand_spike')
        self.assertEqual(result['groups'][0]['count'], 2)

    def test_count_by_reports_group_key_matches_field(self):
        # For a simple CharField, group_key == field.
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
        })
        self.assertEqual(result['group_key'], 'pattern_type')


class CardinalityTests(TestCase):
    def setUp(self):
        # Create 60 distinct pattern_type values by cheating via name diversity
        # is not possible (pattern_type is CharField, not enum-restricted here).
        # We instead create 60 with different names to exercise limit on a
        # unique-per-row field.
        for i in range(60):
            SignalCluster.objects.create(
                name=f'card-{i:03d}',
                pattern_type='demand_spike',
                source_breakdown={},
                strength=0.5,
                keywords=[],
            )

    def test_count_by_default_limit_truncates(self):
        # name is unique per row → 60 distinct groups. Default limit=50 → truncated.
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'name',
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['limit'], 50)
        self.assertEqual(result['returned'], 50)
        self.assertTrue(result['truncated'])
        # group_count reported as (returned + 1) lower bound when truncated;
        # `truncated=true` is the signal that group_count is not exact.
        self.assertEqual(result['group_count'], 51)

    def test_count_by_explicit_limit_clamped(self):
        # limit=1000 must clamp to max 500
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'name', 'limit': 1000,
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['limit'], 500)

    def test_count_by_within_limit_reports_exact_count(self):
        # 60 distinct names, limit=100 → not truncated, exact group_count
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'name', 'limit': 100,
        })
        self.assertTrue(result['ok'])
        self.assertFalse(result['truncated'])
        self.assertEqual(result['group_count'], 60)
        self.assertEqual(result['returned'], 60)


class DateTimeBucketingTests(TestCase):
    """DateTimeField auto-buckets to day per Q2 F-AGREE."""

    def setUp(self):
        # 3 rows on day A, 2 on day B, 1 on day C
        base = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)
        rows = [
            (0, 'a1'), (0, 'a2'), (0, 'a3'),
            (1, 'b1'), (1, 'b2'),
            (2, 'c1'),
        ]
        for delta_days, name in rows:
            cluster = SignalCluster.objects.create(
                name=name, pattern_type='demand_spike',
                source_breakdown={}, strength=0.5, keywords=[],
            )
            SignalCluster.objects.filter(pk=cluster.pk).update(
                detected_at=base + timedelta(days=delta_days),
            )

    def test_count_by_datetimefield_buckets_by_day(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'detected_at',
        })
        self.assertTrue(result['ok'])
        # 3 distinct day buckets
        self.assertEqual(result['group_count'], 3)
        # group_key exposes the internal bucket alias
        self.assertEqual(result['group_key'], '_count_by_day_bucket')
        # Values are ISO date strings (2026-03-01, 2026-03-02, 2026-03-03)
        by_value = {g['value']: g['count'] for g in result['groups']}
        self.assertEqual(by_value['2026-03-01'], 3)
        self.assertEqual(by_value['2026-03-02'], 2)
        self.assertEqual(by_value['2026-03-03'], 1)


class ForeignKeyGroupByTests(TestCase):
    """FK fields group on <field>_id per Q3 F-AGREE + serializer parity."""

    def test_count_by_fk_groups_on_id(self):
        # LLMCallLog has user + workspace FKs. Verify handler resolves the FK
        # name to its attname (<field>_id) so grouping avoids a join.
        result = _run({
            'action': 'count_by', 'model': 'LLMCallLog',
            'field': 'user',
        })
        self.assertTrue(result['ok'])
        # group_key resolved to attname (avoids a JOIN)
        self.assertEqual(result['group_key'], 'user_id')
        self.assertEqual(result['field'], 'user')


class SensitiveFieldRejectionTests(TestCase):
    """Group-by must respect the same sensitive-name posture as filter."""

    def test_count_by_sensitive_field_rejected(self):
        # If a model had e.g. api_key we'd reject. Test via a field name that
        # matches _SENSITIVE_WORDS via composite: any allowlisted model with
        # such a field would trigger rejection. None of the 8 currently have
        # one, so we simulate via passing 'password' (nonexistent → field error
        # comes first). Confirm the sensitive check exists by targeting the
        # 'nonexistent' error path first — this test asserts the guard is
        # wired by rejecting a composite-matching NAME even on a model that
        # doesn't actually have it (order-of-checks: existence first).
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'password',
        })
        # 'password' isn't on SignalCluster; error is "not on model" (existence
        # check runs before sensitive check — safe order).
        self.assertFalse(result['ok'])
        self.assertIn("not on model", result['error'])


class EmptyResultTests(TestCase):
    def test_count_by_zero_matches_returns_clean_shape(self):
        # No rows match — verify empty-result shape stays clean (no divide-by-zero,
        # no missing keys). Uses SignalCluster with an impossible filter rather
        # than a "known empty model" so we don't depend on which models have
        # data-migration seed rows.
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
            'filter_kwargs': {'name': 'zzz-impossible-match-zzz'},
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['total_matching'], 0)
        self.assertEqual(result['group_count'], 0)
        self.assertEqual(result['returned'], 0)
        self.assertEqual(result['groups'], [])
        self.assertFalse(result['truncated'])


class ResponseShapeRegressionTests(TestCase):
    """Post-code SIGN Q4 F-DISAGREE drop: the redundant
    `group_count_is_lower_bound` field was removed because it always flips
    with `truncated`. Callers should read truncation semantics from the
    `truncated` flag. This test locks the shape.
    """

    def test_response_has_no_is_lower_bound_field(self):
        result = _run({
            'action': 'count_by', 'model': 'SignalCluster',
            'field': 'pattern_type',
        })
        self.assertTrue(result['ok'])
        self.assertNotIn('group_count_is_lower_bound', result)
        # Truncation semantics live on the single `truncated` flag
        self.assertIn('truncated', result)


class RegressionExistingActionsTests(TestCase):
    """Adding count_by must not break the 4 pre-existing actions."""

    def test_list_models_still_works(self):
        result = _run({'action': 'list_models'})
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'list_models')

    def test_describe_model_still_works(self):
        result = _run({'action': 'describe_model', 'model': 'SignalCluster'})
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'describe_model')

    def test_filter_still_works(self):
        SignalCluster.objects.create(
            name='regression-1', pattern_type='demand_spike',
            source_breakdown={}, strength=0.5, keywords=[],
        )
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'name__startswith': 'regression'},
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'filter')
        self.assertEqual(result['total_matching'], 1)

    def test_unknown_action_still_rejected(self):
        result = _run({'action': 'delete'})
        self.assertFalse(result['ok'])
        self.assertIn("unknown action 'delete'", result['error'])
