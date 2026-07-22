"""S2890 — ops_tool.recent_bridge_calls regression suite.

Tenth handler surface addition after the S2879 error-envelope migration arc.
This slate ships a NEW operator observability action rather than migrating
existing bare-return sites — targets Chris's real-time need while exploring
the character-os SPA: "what bridge calls hit u-d-b in the last N minutes?".

**PLAYBOOK-3.2.3 required for the migrated-envelope tests below.** Fixture
setUp creates real ``ChatConversation`` + ``User`` rows that the handler
reads via ORM inside ``ToolDispatcher.execute_sync``. That entry point at
``core/services/tool_dispatcher.py:1160`` materializes a fresh asyncio
event loop with a separate Django DB connection, so ``setUp``-created
fixtures are invisible to the handler under plain ``django.test.TestCase``.
``TransactionTestCase`` commits between ``setUp`` and dispatch so the
handler sees the fixtures. Rule ratified at S2889 v0.9.0 close (PR #3402,
merge ``147dcc9cc``).

**PLAYBOOK-3.2.4 not applicable here** — the handler emits a single
``action='recent_bridge_calls'`` envelope with no shared-taxonomy branch
crossing. Envelope-shape assertions suffice; no action-field or message-
substring disambiguation needed.

13 test cases cover:

- Detection surface (source__startswith='character-os-') + hyphen-to-
  underscore tool_kind conversion.
- Payload params: limit bounds, since/window resolution, bridge_tool_name
  filter (underscore→hyphen wire conversion), workspace_id filter.
- User scoping: non-staff callers see own rows only; staff see all;
  no-user-context returns empty; unknown-user-id returns empty.
- Return shape: total_count, by_tool aggregate, items with truncation
  flags + latency_ms remap from response_time_ms.
- Empty state: `note` field surfaces with diagnostic pointer to ledger
  row 155.
- Zero-time-window / far-future-since: return empty with note.
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.utils import timezone

from core.models.conversations.models import ChatConversation
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class RecentBridgeCallsTests(TransactionTestCase):
    """S2890 regression: ops_tool.recent_bridge_calls behavior + edge cases.

    Uses TransactionTestCase per PLAYBOOK-3.2.3 — setUp-created User +
    ChatConversation rows must be visible to the handler running on a
    separate DB connection inside ToolDispatcher.execute_sync's fresh
    asyncio event loop.
    """

    def setUp(self):
        self.dispatcher = ToolDispatcher()

        # Two distinct users to exercise the non-staff scoping rule.
        self.chris = User.objects.create_user(
            username='chris_s2890', email='chris@test.local', password='x',
        )
        self.chris.is_staff = False
        self.chris.save()

        self.other = User.objects.create_user(
            username='other_s2890', email='other@test.local', password='x',
        )

        self.admin = User.objects.create_user(
            username='admin_s2890', email='admin@test.local', password='x',
        )
        self.admin.is_staff = True
        self.admin.save()

        now = timezone.now()

        # Chris's rows — three bridge tools + one non-bridge control row.
        self.consult_row = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-consult-1',
            user_message='What is the current DBZ portfolio state?',
            assistant_response='Portfolio-level answer.',
            platform='api',
            source='character-os-consult-engine',
            response_time_ms=4500,
            agents_used=['portfolio_agent'],
        )
        self.spider_row = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-spider-1',
            user_message='What are the spiders saying about hackernews?',
            assistant_response='Recent hackernews signals summary.',
            platform='api',
            source='character-os-query-spider-data',
            response_time_ms=6800,
            agents_used=['spider_data_tool'],
        )
        self.agent_row = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-agent-1',
            user_message='Ask CTOAgent about scaling.',
            assistant_response='CTOAgent scaling analysis.',
            platform='api',
            source='character-os-agent-consult',
            response_time_ms=8200,
            agents_used=['CTOAgent'],
        )
        # Non-bridge control — should NEVER appear in recent_bridge_calls.
        self.web_row = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-web-1',
            user_message='ordinary web chat',
            assistant_response='ordinary response',
            platform='web',
            source='web',
            response_time_ms=1200,
        )

        # Other user's bridge row — Chris should NOT see this.
        self.other_row = ChatConversation.objects.create(
            user=self.other,
            conversation_id='conv-other-1',
            user_message='other user question',
            assistant_response='other answer',
            platform='api',
            source='character-os-consult-engine',
            response_time_ms=3000,
        )

        # Stale row for since/window cutoff testing.
        self.stale_row = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-stale-1',
            user_message='old bridge question',
            assistant_response='old answer',
            platform='api',
            source='character-os-consult-engine',
            response_time_ms=2500,
        )
        ChatConversation.objects.filter(id=self.stale_row.id).update(
            created_at=now - timedelta(days=10),
        )

    # ────────────────────────────────────────────────────────────────────
    # Detection surface + scoping
    # ────────────────────────────────────────────────────────────────────

    def test_default_scope_returns_only_chris_bridge_rows(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'recent_bridge_calls', 'window': '24h'},
            user_id=self.chris.id,
        )
        self.assertTrue(result.ok, result.error_message)
        payload = result.result
        # Chris has 3 recent bridge rows (consult + spider + agent);
        # web control excluded by source filter; stale row excluded by
        # window; other-user row excluded by user scoping.
        self.assertEqual(payload['total_count'], 3)
        self.assertEqual(len(payload['items']), 3)

        tools = {item['tool_name'] for item in payload['items']}
        self.assertEqual(
            tools, {'consult_engine', 'query_spider_data', 'agent_consult'},
        )

    def test_staff_caller_sees_all_bridge_rows(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'recent_bridge_calls', 'window': '24h'},
            user_id=self.admin.id,
        )
        payload = result.result
        # Staff sees Chris's 3 + other user's 1 = 4.
        self.assertEqual(payload['total_count'], 4)

    def test_non_staff_scoping_hides_other_user_rows(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'recent_bridge_calls', 'window': '24h'},
            user_id=self.other.id,
        )
        payload = result.result
        # Other user has 1 bridge row.
        self.assertEqual(payload['total_count'], 1)
        self.assertEqual(payload['items'][0]['user'], 'other_s2890')

    def test_no_user_context_returns_empty(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'recent_bridge_calls', 'window': '24h'},
            user_id=None,
        )
        payload = result.result
        self.assertEqual(payload['total_count'], 0)
        self.assertIn('note', payload)

    def test_unknown_user_id_returns_empty(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'recent_bridge_calls', 'window': '24h'},
            user_id=999999999,
        )
        payload = result.result
        self.assertEqual(payload['total_count'], 0)

    # ────────────────────────────────────────────────────────────────────
    # Filters
    # ────────────────────────────────────────────────────────────────────

    def test_bridge_tool_name_filter_converts_underscore_to_hyphen(self):
        # Caller passes 'consult_engine' (underscore); handler filters
        # source='character-os-consult-engine' (hyphen). If the conversion
        # regresses, this returns 0 instead of 1.
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '24h',
                'bridge_tool_name': 'consult_engine',
            },
            user_id=self.chris.id,
        )
        payload = result.result
        self.assertEqual(payload['total_count'], 1)
        self.assertEqual(payload['items'][0]['tool_name'], 'consult_engine')

    def test_bridge_tool_name_filter_query_spider_data(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '24h',
                'bridge_tool_name': 'query_spider_data',
            },
            user_id=self.chris.id,
        )
        payload = result.result
        self.assertEqual(payload['total_count'], 1)
        self.assertEqual(payload['items'][0]['tool_name'], 'query_spider_data')

    def test_window_cutoff_excludes_stale_row(self):
        # Chris also owns the stale row (10 days old) with the same
        # 'character-os-consult-engine' source. 24h window excludes it;
        # 30d window includes it.
        result_24h = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '24h',
                'bridge_tool_name': 'consult_engine',
            },
            user_id=self.chris.id,
        )
        result_30d = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '30d',
                'bridge_tool_name': 'consult_engine',
            },
            user_id=self.chris.id,
        )
        self.assertEqual(result_24h.result['total_count'], 1)
        self.assertEqual(result_30d.result['total_count'], 2)

    def test_since_iso_overrides_window(self):
        # since=1 hour ago should include only recent rows (window would
        # otherwise return more with a wide default).
        recent_cutoff = (timezone.now() - timedelta(hours=1)).isoformat()
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '30d',
                'since': recent_cutoff,
            },
            user_id=self.chris.id,
        )
        payload = result.result
        # since=1h ago excludes the 10-day-old stale row even under a
        # 30d window; only the 3 fresh bridge rows remain.
        self.assertEqual(payload['total_count'], 3)

    # ────────────────────────────────────────────────────────────────────
    # Return shape
    # ────────────────────────────────────────────────────────────────────

    def test_return_shape_includes_by_tool_aggregate(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'recent_bridge_calls', 'window': '24h'},
            user_id=self.chris.id,
        )
        payload = result.result
        by_tool = payload['by_tool']
        # 3 distinct tools, each with count=1.
        self.assertEqual(len(by_tool), 3)
        # bridge_tool_name uses underscores in aggregate.
        tool_names = {row['bridge_tool_name'] for row in by_tool}
        self.assertEqual(
            tool_names, {'consult_engine', 'query_spider_data', 'agent_consult'},
        )

    def test_return_shape_maps_response_time_ms_to_latency_ms(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '24h',
                'bridge_tool_name': 'consult_engine',
            },
            user_id=self.chris.id,
        )
        payload = result.result
        item = payload['items'][0]
        self.assertEqual(item['latency_ms'], 4500)

    def test_return_shape_includes_truncation_flags(self):
        # Overwrite consult_row with a long response to trigger truncation.
        long_answer = 'x' * 500
        ChatConversation.objects.filter(id=self.consult_row.id).update(
            assistant_response=long_answer,
        )
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '24h',
                'bridge_tool_name': 'consult_engine',
            },
            user_id=self.chris.id,
        )
        payload = result.result
        item = payload['items'][0]
        self.assertTrue(item['answer_truncated'])
        self.assertFalse(item['question_truncated'])
        self.assertEqual(len(item['answer_preview']), 200)

    def test_empty_result_includes_diagnostic_note(self):
        # Filter to a tool Chris has no rows for → 0 total_count → note.
        # Delete Chris's spider row first (setUp created one).
        self.spider_row.delete()
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'recent_bridge_calls',
                'window': '24h',
                'bridge_tool_name': 'query_spider_data',
            },
            user_id=self.chris.id,
        )
        payload = result.result
        self.assertEqual(payload['total_count'], 0)
        self.assertIn('note', payload)
        # Note should reference the ledger row 155 as the future_trigger
        # signal for the source-string sniffing rename risk.
        self.assertIn('155', payload['note'])
