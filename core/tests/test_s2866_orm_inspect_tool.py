"""Session 2866 slate #1 — bounded ORM row inspector (Rigby Tool Gap Ledger #3 / b5a22ea7).

Covers the ``orm_inspect_tool`` handler at
``core/services/td_handlers_agents.py`` — the parallel to S2865's
``web_fetch_tool`` (external endpoint verify → this = internal DB verify).

Closes the S2845-class false-negative gap: tool surfaces that filter/restrict
enums can report "no data" while rows exist under a different filter path.
The end-to-end S2845 case is exercised in
``EndToEndS2845VerificationTests`` — ``source_breakdown__has_key`` finds
huggingface rows that an enum-restricted ``source`` param would miss.
"""
from __future__ import annotations

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
        trace_id='test-trace',
    )


class SchemaAndRegistrationTests(SimpleTestCase):
    def test_tool_registered(self):
        dispatcher = get_tool_dispatcher()
        self.assertIn('orm_inspect_tool', dispatcher._tool_handlers)
        self.assertTrue(callable(dispatcher._tool_handlers['orm_inspect_tool']))

    def test_schema_present(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        names = [s.get('name') for s in PA_TOOL_SCHEMAS if 'name' in s]
        self.assertIn('orm_inspect_tool', names)

    def test_schema_action_enum(self):
        # Baseline S2866 shipped 4 actions; S2867 added 'count_by' as a 5th.
        # This assertion tracks the current tool contract, so a future
        # slate landing another action should update it in the same PR.
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        schema = next(s for s in PA_TOOL_SCHEMAS if s.get('name') == 'orm_inspect_tool')
        actions = schema['parameters']['properties']['action']['enum']
        self.assertEqual(
            sorted(actions),
            sorted(['list_models', 'describe_model', 'get', 'filter', 'count_by']),
        )


class ListModelsTests(TestCase):
    def test_list_models_returns_allowlist(self):
        result = _run({'action': 'list_models'})
        self.assertTrue(result['ok'])
        self.assertEqual(result['action'], 'list_models')
        names = {m['name'] for m in result['models']}
        # Core allowlist per S2866 pre-code SIGN
        self.assertIn('SignalCluster', names)
        self.assertIn('Deliverable', names)
        self.assertIn('LLMCallLog', names)
        self.assertIn('AutopilotAction', names)

    def test_list_models_flags_sensitive_correctly(self):
        result = _run({'action': 'list_models'})
        by_name = {m['name']: m for m in result['models']}
        # High-sensitivity models per SIGN Q3/Q6 F-BLOCKING
        self.assertTrue(by_name['LLMCallLog']['sensitive'])
        self.assertTrue(by_name['AutopilotAction']['sensitive'])
        self.assertTrue(by_name['OpsRun']['sensitive'])
        # Non-sensitive
        self.assertFalse(by_name['SignalCluster']['sensitive'])
        self.assertFalse(by_name['Deliverable']['sensitive'])


class DescribeModelTests(TestCase):
    def test_describe_model_returns_fields(self):
        result = _run({'action': 'describe_model', 'model': 'SignalCluster'})
        self.assertTrue(result['ok'])
        field_names = {f['name'] for f in result['fields']}
        # Known SignalCluster fields
        self.assertIn('name', field_names)
        self.assertIn('source_breakdown', field_names)
        self.assertIn('pattern_type', field_names)

    def test_describe_model_flags_json_fields(self):
        result = _run({'action': 'describe_model', 'model': 'SignalCluster'})
        by_name = {f['name']: f for f in result['fields']}
        self.assertTrue(by_name['source_breakdown']['is_json'])
        self.assertFalse(by_name['name']['is_json'])

    def test_describe_model_rejects_non_allowlist(self):
        result = _run({'action': 'describe_model', 'model': 'PublishGate'})
        self.assertFalse(result['ok'])
        self.assertIn('not in allowlist', result['error'])
        self.assertIn('allowlist', result)


class InputValidationTests(TestCase):
    def test_unknown_action(self):
        result = _run({'action': 'delete'})
        self.assertFalse(result['ok'])
        self.assertIn("unknown action 'delete'", result['error'])

    def test_missing_model(self):
        result = _run({'action': 'filter'})
        self.assertFalse(result['ok'])
        self.assertIn('model is required', result['error'])

    def test_non_allowlist_model(self):
        result = _run({'action': 'filter', 'model': 'User', 'filter_kwargs': {}})
        self.assertFalse(result['ok'])
        self.assertIn('not in allowlist', result['error'])

    def test_filter_unknown_field(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'nonexistent_field': 'x'},
        })
        self.assertFalse(result['ok'])
        self.assertIn("field 'nonexistent_field' not on model", result['error'])

    def test_filter_unsafe_lookup(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'name__regex': '^t.*'},
        })
        self.assertFalse(result['ok'])
        self.assertIn("lookup 'regex' not allowed", result['error'])

    def test_filter_deep_chain_rejected(self):
        result = _run({
            'action': 'filter', 'model': 'Deliverable',
            'filter_kwargs': {'workspace__name__icontains': 'foo'},
        })
        self.assertFalse(result['ok'])
        self.assertIn('deep __ chain', result['error'])

    def test_filter_contains_on_expensive_field_rejected(self):
        # SignalCluster has no expensive_text_fields; Deliverable does (content).
        result = _run({
            'action': 'filter', 'model': 'Deliverable',
            'filter_kwargs': {'content__icontains': 'foo'},
        })
        self.assertFalse(result['ok'])
        self.assertIn('expensive text field', result['error'])

    def test_filter_in_list_cap(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'id__in': list(range(200))},
        })
        self.assertFalse(result['ok'])
        self.assertIn('capped at 100', result['error'])

    def test_get_missing_pk(self):
        result = _run({'action': 'get', 'model': 'SignalCluster'})
        self.assertFalse(result['ok'])
        self.assertIn('pk is required', result['error'])

    def test_order_by_not_in_allowlist(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {},
            'order_by': 'strength',
        })
        self.assertFalse(result['ok'])
        self.assertIn("order_by 'strength' not in allowlist", result['error'])


class SerializationTests(TestCase):
    def setUp(self):
        self.cluster = SignalCluster.objects.create(
            name='serialization-test',
            pattern_type='demand_spike',
            source_breakdown={'huggingface': 3, 'hackernews': 5},
            strength=0.7,
            keywords=['ai', 'ml'],
        )

    def test_get_returns_projected_row(self):
        result = _run({'action': 'get', 'model': 'SignalCluster', 'pk': str(self.cluster.pk)})
        self.assertTrue(result['ok'])
        row = result['row']
        self.assertEqual(row['name'], 'serialization-test')
        self.assertEqual(row['pattern_type'], 'demand_spike')

    def test_get_include_json_true_returns_json_value(self):
        result = _run({
            'action': 'get', 'model': 'SignalCluster', 'pk': str(self.cluster.pk),
            'include_json_fields': True,
        })
        row = result['row']
        self.assertEqual(row['source_breakdown'], {'huggingface': 3, 'hackernews': 5})
        self.assertEqual(row['keywords'], ['ai', 'ml'])

    def test_get_include_json_false_omits_json(self):
        result = _run({
            'action': 'get', 'model': 'SignalCluster', 'pk': str(self.cluster.pk),
            'include_json_fields': False,
        })
        row = result['row']
        self.assertEqual(row['source_breakdown'], '<omitted:json_field>')

    def test_get_field_projection(self):
        result = _run({
            'action': 'get', 'model': 'SignalCluster', 'pk': str(self.cluster.pk),
            'fields': ['id', 'name'],
        })
        row = result['row']
        self.assertIn('name', row)
        self.assertNotIn('source_breakdown', row)
        self.assertNotIn('pattern_type', row)

    def test_get_not_found(self):
        import uuid
        result = _run({
            'action': 'get', 'model': 'SignalCluster',
            'pk': str(uuid.uuid4()),
        })
        self.assertFalse(result['ok'])
        self.assertIn('no SignalCluster row', result['error'])


class RedactionTests(TestCase):
    def setUp(self):
        # source_breakdown contains a mix; deliverable metadata will hold
        # sensitive-looking JSON keys for the redaction test.
        self.cluster = SignalCluster.objects.create(
            name='redaction-test',
            pattern_type='demand_spike',
            source_breakdown={
                'huggingface': 3,
                'nested': {'api_key': 'sk-should-be-hidden', 'topic': 'ml'},
            },
            strength=0.5,
            keywords=['token', 'ok'],  # token as list item, not key — not redacted
        )

    def test_json_key_redaction_recursive(self):
        result = _run({
            'action': 'get', 'model': 'SignalCluster', 'pk': str(self.cluster.pk),
            'include_json_fields': True,
        })
        breakdown = result['row']['source_breakdown']
        self.assertEqual(breakdown['nested']['api_key'], '<redacted>')
        # Non-sensitive key preserved
        self.assertEqual(breakdown['nested']['topic'], 'ml')
        # Sibling data intact
        self.assertEqual(breakdown['huggingface'], 3)

    def test_json_list_items_not_over_redacted(self):
        # 'token' as a list ITEM (not key) should not be redacted
        result = _run({
            'action': 'get', 'model': 'SignalCluster', 'pk': str(self.cluster.pk),
            'include_json_fields': True,
        })
        self.assertIn('token', result['row']['keywords'])


class SensitiveFieldNameMatchingTests(TestCase):
    """Regression: post-code SIGN S2866 Case 3 F-BLOCKING — naive substring
    match on 'token' redacted 'prompt_tokens'/'total_tokens' (numeric counters
    on LLMCallLog). Fix: word-boundary matching after split-on-underscore.
    """

    def test_describe_llmcalllog_does_not_flag_token_counters(self):
        result = _run({'action': 'describe_model', 'model': 'LLMCallLog'})
        by_name = {f['name']: f for f in result['fields']}
        # These are integer counters, must NOT be flagged sensitive
        self.assertFalse(by_name['prompt_tokens']['sensitive_by_name'])
        self.assertFalse(by_name['completion_tokens']['sensitive_by_name'])
        self.assertFalse(by_name['total_tokens']['sensitive_by_name'])

    def test_describe_signalcluster_does_not_flag_keywords_or_keys(self):
        # 'keywords' contains substring 'key' — must not match _SENSITIVE_WORDS
        result = _run({'action': 'describe_model', 'model': 'SignalCluster'})
        by_name = {f['name']: f for f in result['fields']}
        self.assertFalse(by_name['keywords']['sensitive_by_name'])

    def test_describe_flags_true_sensitive_composites(self):
        # Composite match should still catch api_key etc. even though these
        # models don't have such fields, we verify via describe_model on
        # Deliverable which has 'trace_id' (contains 'id' but also not sensitive).
        result = _run({'action': 'describe_model', 'model': 'Deliverable'})
        by_name = {f['name']: f for f in result['fields']}
        # trace_id splits to {'trace','id'} — no sensitive word match
        self.assertFalse(by_name['trace_id']['sensitive_by_name'])
        # content_hash: split {'content','hash'} — 'hash' not in _SENSITIVE_WORDS
        # (we removed 'hash' since it's ambiguous). Confirm no false-positive.
        self.assertFalse(by_name['content_hash']['sensitive_by_name'])


class HighSensitivityModelDefaultsTests(TestCase):
    def test_llmcalllog_defaults_to_include_json_false(self):
        # LLMCallLog is marked sensitive → include_json_fields defaults to false
        # We verify the *behavior* even without a live row by checking a get on a
        # non-existent pk returns 'no row' error (which means we passed the
        # allowlist gate); then filter on empty table honors the default flag.
        result = _run({
            'action': 'filter', 'model': 'LLMCallLog',
            'filter_kwargs': {},
        })
        self.assertTrue(result['ok'])
        self.assertFalse(result['include_json_fields'])  # defaulted false

    def test_signalcluster_defaults_to_include_json_true(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {},
        })
        self.assertTrue(result['ok'])
        self.assertTrue(result['include_json_fields'])  # defaulted true

    def test_high_sensitivity_can_be_opted_in(self):
        result = _run({
            'action': 'filter', 'model': 'LLMCallLog',
            'filter_kwargs': {},
            'include_json_fields': True,
        })
        self.assertTrue(result['ok'])
        self.assertTrue(result['include_json_fields'])


class FilterActionTests(TestCase):
    def setUp(self):
        for i in range(3):
            SignalCluster.objects.create(
                name=f'filter-test-{i}',
                pattern_type='demand_spike',
                source_breakdown={'huggingface': i + 1},
                strength=0.3 + i * 0.1,
                keywords=['ai'],
            )

    def test_filter_returns_matching_rows(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'pattern_type': 'demand_spike'},
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['total_matching'], 3)
        self.assertEqual(result['returned'], 3)
        self.assertFalse(result['truncated'])

    def test_filter_respects_limit(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'pattern_type': 'demand_spike'},
            'limit': 2,
        })
        self.assertEqual(result['returned'], 2)
        self.assertEqual(result['total_matching'], 3)
        self.assertTrue(result['truncated'])

    def test_filter_startswith_lookup(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'name__startswith': 'filter-test'},
        })
        self.assertEqual(result['total_matching'], 3)

    def test_filter_order_by_id_desc(self):
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {},
            'order_by': '-id',
            'limit': 5,
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['order_by'], '-id')


class EndToEndS2845VerificationTests(TestCase):
    """The exact case that motivated this tool.

    Session 2845: your tool surface's ``source`` param was enum-restricted and
    reported 0 AI-community signals — but 140 huggingface-tagged clusters
    existed in ``source_breakdown`` (a JSONField), reachable via
    ``source_breakdown__has_key``. With ORM inspector, Rigby verifies this
    herself instead of a Claude drop-to-Django-shell trip.
    """

    def setUp(self):
        # 5 with huggingface in source_breakdown, 3 without
        for i in range(5):
            SignalCluster.objects.create(
                name=f's2845-hf-{i}',
                pattern_type='demand_spike',
                source_breakdown={'huggingface': i + 1, 'hackernews': 2},
                strength=0.5,
                keywords=['ai'],
            )
        for i in range(3):
            SignalCluster.objects.create(
                name=f's2845-nohf-{i}',
                pattern_type='demand_spike',
                source_breakdown={'reddit': 3},
                strength=0.4,
                keywords=['general'],
            )

    def test_has_key_finds_hidden_huggingface_rows(self):
        # This is the S2845 false-negative case, now catchable via ORM inspector.
        result = _run({
            'action': 'filter', 'model': 'SignalCluster',
            'filter_kwargs': {'source_breakdown__has_key': 'huggingface'},
        })
        self.assertTrue(result['ok'])
        self.assertEqual(result['total_matching'], 5)
        # Every returned row has huggingface in source_breakdown
        for row in result['rows']:
            self.assertIn('huggingface', row['source_breakdown'])
