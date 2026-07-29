"""Session 3032 — Rigby Tool Gap Ledger: AgentDecisionSummary allowlist entry.

Live trigger at S3030 T1 SIGN: Rigby needed to run the canonical-drift
probe (`filter(status='canonical', is_canonical=False).count()`) but
`AgentDecisionSummary` wasn't in the `orm_inspect_tool` allowlist,
forcing a fallback to Django shell via Claude. This suite pins the
S3032 allowlist expansion so the same probe can now be run entirely on
Rigby's tool surface.

Contract pinned by this suite:

1. `list_models` includes `AgentDecisionSummary` and reports it as
   non-sensitive.
2. `describe_model` returns the expected field shape (topic, status,
   is_canonical, promoted_at, promoted_by + JSONField flags on
   key_insights + participants).
3. `filter` action executes the exact S3030 T1 drift probe end-to-end
   (`status='canonical'` AND `is_canonical=False`) and returns rows.
4. `contains` lookups on `recommended_stance` / `suggested_feature` /
   `rationale` are rejected per the expensive_text_fields policy so
   the tool can't accidentally do full-text scans on long content.
5. `contains` on `topic` (CharField(255)) is allowed — proves the
   policy is field-scoped, not model-scoped.
"""
from __future__ import annotations

from django.test import TestCase

from core.models_unified_system import AgentDecisionSummary
from core.services.tool_dispatcher import get_tool_dispatcher


def _run(payload):
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers['orm_inspect_tool']
    return handler(
        tool_name='orm_inspect_tool',
        payload=payload,
        user_id=None,
        trace_id='test-trace-s3032',
    )


def _make_draft(topic: str) -> AgentDecisionSummary:
    return AgentDecisionSummary.objects.create(
        topic=topic,
        decision_type='experiment',
        impact_area='agents',
        rationale='r',
        recommended_stance='s',
        status='draft',
    )


class AgentDecisionSummaryAllowlistTests(TestCase):
    def test_list_models_includes_agent_decision_summary_as_non_sensitive(self):
        result = _run({'action': 'list_models'})
        self.assertTrue(result['ok'])
        by_name = {m['name']: m for m in result['models']}
        self.assertIn('AgentDecisionSummary', by_name)
        entry = by_name['AgentDecisionSummary']
        self.assertEqual(entry['app_label'], 'core')
        self.assertFalse(entry['sensitive'])
        # Expensive text fields explicitly enumerated.
        self.assertEqual(
            set(entry['expensive_text_fields']),
            {'recommended_stance', 'suggested_feature', 'rationale'},
        )

    def test_describe_model_returns_expected_shape(self):
        result = _run({
            'action': 'describe_model',
            'model': 'AgentDecisionSummary',
        })
        self.assertTrue(result['ok'])
        by_name = {f['name']: f for f in result['fields']}

        # Core canonical-decision fields present.
        for field in ('topic', 'status', 'is_canonical', 'promoted_at',
                      'promoted_by', 'decision_type', 'impact_area',
                      'created_at', 'updated_at'):
            self.assertIn(field, by_name, f'missing field: {field}')

        # JSONField flags correct.
        self.assertTrue(by_name['key_insights']['is_json'])
        self.assertTrue(by_name['participants']['is_json'])
        self.assertFalse(by_name['topic']['is_json'])
        self.assertFalse(by_name['status']['is_json'])

    def test_filter_runs_the_s3030_canonical_drift_probe(self):
        """The exact ORM probe Rigby couldn't run at S3030 T1: which
        rows have status='canonical' but is_canonical=False. This test
        pins that it works via the tool surface end-to-end."""
        # Setup: 2 drift rows (mimics pre-S3029 bug), 1 healthy canonical,
        # 1 draft. Only the 2 drift rows should match the probe filter.
        drift_a = _make_draft('drift-a')
        drift_b = _make_draft('drift-b')
        AgentDecisionSummary.objects.filter(
            pk__in=[drift_a.pk, drift_b.pk]
        ).update(status='canonical')

        healthy = _make_draft('healthy')
        healthy.promote_to_canonical(promoted_by='human')

        _make_draft('draft-c')

        result = _run({
            'action': 'filter',
            'model': 'AgentDecisionSummary',
            'filter_kwargs': {
                'status': 'canonical',
                'is_canonical': False,
            },
            'limit': 10,
        })

        self.assertTrue(result['ok'], result.get('error'))
        self.assertEqual(result['total_matching'], 2)
        returned_topics = {row['topic'] for row in result['rows']}
        self.assertEqual(returned_topics, {'drift-a', 'drift-b'})

    def test_contains_rejected_on_expensive_text_fields(self):
        """The three expensive TextFields should refuse contains scans."""
        _make_draft('t')
        for field in ('recommended_stance', 'suggested_feature', 'rationale'):
            result = _run({
                'action': 'filter',
                'model': 'AgentDecisionSummary',
                'filter_kwargs': {f'{field}__contains': 'x'},
                'limit': 5,
            })
            self.assertFalse(
                result['ok'],
                f'{field}__contains should have been rejected but succeeded',
            )
            self.assertIn('expensive', result['error'].lower())

    def test_contains_allowed_on_topic_charfield(self):
        """`topic` is CharField(255) — safe for contains lookups. Proves
        the expensive-field policy is field-scoped, not model-scoped."""
        _make_draft('unique-topic-marker')
        _make_draft('other-topic')
        result = _run({
            'action': 'filter',
            'model': 'AgentDecisionSummary',
            'filter_kwargs': {'topic__contains': 'unique-topic-marker'},
            'limit': 5,
        })
        self.assertTrue(result['ok'], result.get('error'))
        self.assertEqual(result['total_matching'], 1)
        self.assertEqual(result['rows'][0]['topic'], 'unique-topic-marker')
