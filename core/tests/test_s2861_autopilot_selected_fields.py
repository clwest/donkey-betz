"""Session 2861 slate #1 — autopilot_tool.history selected_fields projection.

Locks in the S2861 read-surface addition on td_handlers_ops.py:
  - `_handle_autopilot(action='history', include_evidence=True,
    selected_fields=['evidence.<key>', 'result.<key>'])` projects the
    returned evidence + result JSONFields to only the requested top-level
    keys. Top-level only in v1 — nested dicts/lists returned whole.
    Ignored unless include_evidence=true.
"""

from django.test import TestCase

from core.models_diagnostic_pipeline import AutopilotAction
from core.services.td_handlers_ops import OpsHandlersMixin


class _OpsProxy(OpsHandlersMixin):
    """Same instantiation pattern as core/views_ops_console.py:133."""
    pass


class AutopilotHistorySelectedFieldsTests(TestCase):
    """The `history` action gains an opt-in `selected_fields` projection."""

    def setUp(self):
        # Flat scalar row (majority pattern — workspace_budget_freeze etc.)
        AutopilotAction.objects.create(
            action_type='workspace_budget_freeze',
            agent_name='BudgetController',
            policy='workspace_budget_controller',
            dry_run=False,
            evidence={
                'trigger': 'operator_set_cap_immediate',
                'actor_user_id': '42',
                'cap': 5.0,
                'daily_total': 5.25,
                'workspace_id': 'ws-abc',
            },
            result={
                'workspace_id': 'ws-abc',
                'daily_spend': 5.25,
                'cap': 5.0,
                'reason': 'cap_exceeded',
            },
        )

    def _call(self, payload):
        proxy = _OpsProxy()
        return proxy._handle_autopilot(
            tool_name='autopilot_tool',
            payload={'action': 'history', 'limit': 5, **payload},
            user_id=None,
            trace_id='s2861-test',
        )

    def test_projects_only_requested_evidence_keys(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': ['evidence.actor_user_id', 'evidence.trigger'],
        })
        row = response['actions'][0]
        self.assertEqual(
            row['evidence'],
            {'actor_user_id': '42', 'trigger': 'operator_set_cap_immediate'},
        )
        # result had no requested paths → projected to empty dict
        self.assertEqual(row['result'], {})

    def test_projects_only_requested_result_keys(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': ['result.reason', 'result.cap'],
        })
        row = response['actions'][0]
        self.assertEqual(row['result'], {'reason': 'cap_exceeded', 'cap': 5.0})
        # evidence had no requested paths → projected to empty dict
        self.assertEqual(row['evidence'], {})

    def test_projects_across_both_prefixes(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': [
                'evidence.actor_user_id', 'result.reason', 'result.cap',
            ],
        })
        row = response['actions'][0]
        self.assertEqual(row['evidence'], {'actor_user_id': '42'})
        self.assertEqual(row['result'], {'reason': 'cap_exceeded', 'cap': 5.0})

    def test_ignored_when_include_evidence_false(self):
        response = self._call({
            'include_evidence': False,
            'selected_fields': ['evidence.actor_user_id', 'result.reason'],
        })
        # Same shape as no-selected_fields path: evidence+result absent entirely
        self.assertFalse(response['include_evidence'])
        self.assertEqual(response['selected_fields'], [])
        for row in response['actions']:
            self.assertNotIn('evidence', row)
            self.assertNotIn('result', row)

    def test_missing_path_silently_omitted(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': [
                'evidence.actor_user_id',
                'evidence.does_not_exist',
                'result.reason',
                'result.also_missing',
            ],
        })
        row = response['actions'][0]
        self.assertEqual(row['evidence'], {'actor_user_id': '42'})
        self.assertEqual(row['result'], {'reason': 'cap_exceeded'})
        # Echoed selected_fields still contains missing paths — echo shows
        # what the server ACCEPTED (validation-passed), not what actually
        # resolved to a value. Documented in the schema description.
        self.assertIn('evidence.does_not_exist', response['selected_fields'])
        self.assertIn('result.also_missing', response['selected_fields'])

    def test_invalid_prefix_silently_ignored(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': [
                'evidence.trigger',
                'foo.bar',
                'verification_result.source',
                'agent_name',
            ],
        })
        row = response['actions'][0]
        self.assertEqual(row['evidence'], {'trigger': 'operator_set_cap_immediate'})
        # Invalid prefixes / bare keys not echoed as accepted
        self.assertEqual(response['selected_fields'], ['evidence.trigger'])

    def test_path_without_dot_silently_ignored(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': ['evidence', 'result', 'evidence.trigger'],
        })
        row = response['actions'][0]
        self.assertEqual(row['evidence'], {'trigger': 'operator_set_cap_immediate'})
        self.assertEqual(response['selected_fields'], ['evidence.trigger'])

    def test_empty_selected_fields_returns_full_json(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': [],
        })
        row = response['actions'][0]
        # Full evidence + result returned unchanged
        self.assertEqual(row['evidence']['actor_user_id'], '42')
        self.assertEqual(row['evidence']['cap'], 5.0)
        self.assertEqual(row['result']['reason'], 'cap_exceeded')
        self.assertEqual(row['result']['workspace_id'], 'ws-abc')
        self.assertEqual(response['selected_fields'], [])

    def test_missing_selected_fields_returns_full_json(self):
        response = self._call({'include_evidence': True})
        row = response['actions'][0]
        self.assertEqual(row['evidence']['actor_user_id'], '42')
        self.assertEqual(row['result']['reason'], 'cap_exceeded')
        self.assertEqual(response['selected_fields'], [])

    def test_max_cap_enforced_at_20_paths(self):
        # 25 evidence paths — cap should truncate to first 20
        many = [f'evidence.key_{i}' for i in range(25)]
        response = self._call({
            'include_evidence': True,
            'selected_fields': many,
        })
        self.assertEqual(len(response['selected_fields']), 20)
        self.assertEqual(response['selected_fields'][0], 'evidence.key_0')
        self.assertEqual(response['selected_fields'][-1], 'evidence.key_19')

    def test_non_list_selected_fields_treated_as_no_op(self):
        # Rigby autofill risk: agent passes a string instead of a list
        response = self._call({
            'include_evidence': True,
            'selected_fields': 'evidence.trigger',
        })
        row = response['actions'][0]
        # Full evidence returned (projection disabled)
        self.assertEqual(row['evidence']['trigger'], 'operator_set_cap_immediate')
        self.assertEqual(row['evidence']['actor_user_id'], '42')
        self.assertEqual(response['selected_fields'], [])

    def test_response_echoes_server_accepted_fields(self):
        # Mix valid + invalid + duplicates + cap-overflow to verify echo
        # reflects what the server actually accepted
        response = self._call({
            'include_evidence': True,
            'selected_fields': [
                'evidence.trigger',       # valid
                'garbage.key',            # invalid prefix — dropped
                'evidence.actor_user_id',  # valid
                'no_dot',                 # no dot — dropped
                'result.reason',          # valid
            ],
        })
        self.assertEqual(
            response['selected_fields'],
            ['evidence.trigger', 'evidence.actor_user_id', 'result.reason'],
        )

    # ── S2896 (Rigby Tool Gap Ledger Row C) — wipe-location diagnostics ──
    # When `selected_fields` echoes `[]` after a non-empty send, the
    # operator can't tell whether per-item validation dropped every path
    # or something upstream of the handler wiped the list. The response
    # now also echoes `selected_fields_dropped` (paths rejected by per-
    # item validation) and `selected_fields_received_count` (list length
    # as the handler saw it pre-truncation) so the wipe location is
    # unambiguous.

    def test_dropped_paths_surfaced_in_echo(self):
        response = self._call({
            'include_evidence': True,
            'selected_fields': [
                'evidence.trigger',      # valid — kept
                'garbage.key',           # invalid prefix — dropped
                'no_dot',                # no dot — dropped
                'result.reason',         # valid — kept
            ],
        })
        self.assertEqual(
            response['selected_fields'],
            ['evidence.trigger', 'result.reason'],
        )
        self.assertEqual(
            response['selected_fields_dropped'],
            ['garbage.key', 'no_dot'],
        )
        self.assertEqual(response['selected_fields_received_count'], 4)

    def test_upstream_wipe_signature(self):
        # When the handler receives `selected_fields=[]` but the caller
        # believed they sent a non-empty list, the response looks like
        # this: kept=[], dropped=[], received_count=0. The `_count=0`
        # marker is the diagnostic — operator retries with a shorter
        # list to isolate whether the wipe is upstream (schema/JSON
        # parse/OpenAI arg validation) or handler-side.
        response = self._call({
            'include_evidence': True,
            'selected_fields': [],
        })
        self.assertEqual(response['selected_fields'], [])
        self.assertEqual(response['selected_fields_dropped'], [])
        self.assertEqual(response['selected_fields_received_count'], 0)

    def test_all_paths_dropped_distinguishable_from_wipe(self):
        # Contrast case: caller sent 4 paths, all invalid → dropped=[4],
        # received_count=4. This IS distinguishable from an upstream
        # wipe (received_count=0) because both counts are surfaced.
        response = self._call({
            'include_evidence': True,
            'selected_fields': [
                'foo.bar', 'baz.qux', 'no_dot_here', 'evidence',
            ],
        })
        self.assertEqual(response['selected_fields'], [])
        self.assertEqual(len(response['selected_fields_dropped']), 4)
        self.assertEqual(response['selected_fields_received_count'], 4)

    def test_received_count_reflects_pre_truncation_length(self):
        # 25 paths sent; 20 applied (cap); received_count echoes the
        # pre-truncation length so operators can spot silent truncation.
        many = [f'evidence.key_{i}' for i in range(25)]
        response = self._call({
            'include_evidence': True,
            'selected_fields': many,
        })
        self.assertEqual(len(response['selected_fields']), 20)
        self.assertEqual(response['selected_fields_dropped'], [])
        self.assertEqual(response['selected_fields_received_count'], 25)

    def test_non_list_received_count_is_zero(self):
        # Non-list selected_fields (e.g., string autofill) → treated as
        # no-op; received_count=0 signals "no valid list seen".
        response = self._call({
            'include_evidence': True,
            'selected_fields': 'evidence.trigger',
        })
        self.assertEqual(response['selected_fields'], [])
        self.assertEqual(response['selected_fields_dropped'], [])
        self.assertEqual(response['selected_fields_received_count'], 0)

    def test_include_evidence_false_still_surfaces_received_count(self):
        # With include_evidence=false, no projection happens, but the
        # received_count still reflects what was sent — useful for
        # detecting a caller who forgot to set include_evidence=true.
        response = self._call({
            'include_evidence': False,
            'selected_fields': ['evidence.trigger', 'result.reason'],
        })
        self.assertEqual(response['selected_fields'], [])
        self.assertEqual(response['selected_fields_dropped'], [])
        self.assertEqual(response['selected_fields_received_count'], 2)

    def test_nested_value_returned_whole(self):
        # Simulates cycle-log rows (core.py:353) where evidence contains
        # nested per-policy result dicts. Option C: v1 returns nested value
        # verbatim when top-level key is selected.
        AutopilotAction.objects.create(
            action_type='dry_run',
            agent_name='',
            policy='cycle_evaluation',
            dry_run=True,
            evidence={
                'timeout_spike': {'agents_over_threshold': 3, 'window_min': 10},
                'blocked_hygiene': {'stale_blocks': 1},
            },
            result={
                'cycle_id': 'abc-123',
                'actions_taken': 0,
                'nested_summary': {'ok': True, 'details': ['a', 'b']},
            },
        )
        # Order-by -created_at (Meta.ordering) means the new row is first
        response = self._call({
            'include_evidence': True,
            'selected_fields': [
                'evidence.timeout_spike',
                'result.nested_summary',
            ],
            'limit': 1,
        })
        row = response['actions'][0]
        self.assertEqual(
            row['evidence']['timeout_spike'],
            {'agents_over_threshold': 3, 'window_min': 10},
        )
        self.assertEqual(
            row['result']['nested_summary'],
            {'ok': True, 'details': ['a', 'b']},
        )
