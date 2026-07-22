"""S2891 — ops_tool.bridge_activity_digest regression suite.

Follows the S2890 recent_bridge_calls test shape. This slate ships a new
Rigby-narratable digest wrapper on top of the existing recent_bridge_calls
handler — same qs computation + scoping, different response shape
(narrative + structured_facts, no items[]).

**PLAYBOOK-3.2.3 required.** setUp creates real ``ChatConversation`` +
``User`` rows that the delegated ``_ops_recent_bridge_calls`` handler reads
via ORM inside ``ToolDispatcher.execute_sync``. Same reasoning as
``test_s2890_recent_bridge_calls.py``: ``execute_sync`` materializes a
fresh asyncio event loop with a separate DB connection, so plain
``TestCase`` setUp fixtures are invisible under the wrapping transaction.
``TransactionTestCase`` commits between setUp and dispatch.

**PLAYBOOK-3.2.4 not applicable.** Single ``action='bridge_activity_digest'``
envelope, no shared-taxonomy branch crossing.
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.utils import timezone

from core.models.conversations.models import ChatConversation
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class BridgeActivityDigestTests(TransactionTestCase):
    """S2891 regression: bridge_activity_digest narrative + structured_facts."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

        self.chris = User.objects.create_user(
            username='chris_s2891', email='chris@test.local', password='x',
        )
        self.chris.is_staff = False
        self.chris.save()

        now = timezone.now()

        # Three bridge rows for Chris — two consult_engine, one query_spider_data.
        # Latencies chosen so median-of-three = 5000ms.
        self.consult_1 = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-consult-1',
            user_message='What is the current DBZ portfolio state?',
            assistant_response='Portfolio-level answer.',
            platform='api',
            source='character-os-consult-engine',
            response_time_ms=3000,
            agents_used=['portfolio_agent'],
        )
        self.consult_2 = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-consult-2',
            user_message='Second consult question',
            assistant_response='Second consult answer.',
            platform='api',
            source='character-os-consult-engine',
            response_time_ms=5000,
            agents_used=['portfolio_agent'],
        )
        self.spider_1 = ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-spider-1',
            user_message='hackernews signal check',
            assistant_response='hackernews answer',
            platform='api',
            source='character-os-query-spider-data',
            response_time_ms=7000,
            agents_used=['spider_data_tool'],
        )

    # ────────────────────────────────────────────────────────────────────
    # Narrative shape
    # ────────────────────────────────────────────────────────────────────

    def test_narrative_names_total_and_by_tool_breakdown(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        self.assertTrue(result.ok, result.error_message)
        narrative = result.result['narrative']
        self.assertIn('3 times', narrative)
        self.assertIn('consult_engine', narrative)
        self.assertIn('query_spider_data', narrative)
        # by_tool counts should appear (2 consult_engine, 1 query_spider_data).
        self.assertIn('2 consult_engine', narrative)
        self.assertIn('1 query_spider_data', narrative)

    def test_narrative_singular_time_for_single_call(self):
        # Delete two rows so total_count == 1.
        self.consult_2.delete()
        self.spider_1.delete()
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        narrative = result.result['narrative']
        self.assertIn('1 time', narrative)
        self.assertNotIn('1 times', narrative)

    def test_narrative_includes_median_latency(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        # Median of [3000, 5000, 7000] = 5000.
        self.assertIn('Median latency 5000ms', result.result['narrative'])

    def test_narrative_names_most_recent_tool_and_question(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        narrative = result.result['narrative']
        # spider_1 was created last, so most_recent tool = query_spider_data.
        self.assertIn('via query_spider_data', narrative)
        self.assertIn('hackernews signal check', narrative)
        self.assertIn('user chris_s2891', narrative)

    def test_empty_state_narrative(self):
        ChatConversation.objects.all().delete()
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        payload = result.result
        self.assertEqual(
            payload['narrative'],
            'No character-os bridge calls in the last 24h.',
        )
        self.assertEqual(payload['structured_facts']['total_count'], 0)
        self.assertIsNone(payload['structured_facts']['most_recent'])
        self.assertIsNone(payload['structured_facts']['median_latency_ms'])

    # ────────────────────────────────────────────────────────────────────
    # structured_facts shape
    # ────────────────────────────────────────────────────────────────────

    def test_structured_facts_shape_populated(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        facts = result.result['structured_facts']
        # Required top-level keys.
        self.assertEqual(
            set(facts.keys()),
            {'total_count', 'by_tool', 'most_recent', 'median_latency_ms', 'window'},
        )
        self.assertEqual(facts['total_count'], 3)
        self.assertEqual(facts['window'], '24h')
        # by_tool minimal shape (name + count only, no full source string).
        for row in facts['by_tool']:
            self.assertEqual(set(row.keys()), {'bridge_tool_name', 'count'})

    def test_structured_facts_most_recent_field_list(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        most_recent = result.result['structured_facts']['most_recent']
        # Per Rigby Q1c tweak: include workspace_id + conversation_id for drilldown.
        self.assertEqual(
            set(most_recent.keys()),
            {
                'tool_name', 'question_preview', 'minutes_ago',
                'latency_ms', 'user', 'workspace_id', 'conversation_id',
            },
        )
        self.assertEqual(most_recent['tool_name'], 'query_spider_data')
        self.assertEqual(most_recent['conversation_id'], 'conv-spider-1')
        self.assertEqual(most_recent['latency_ms'], 7000)

    def test_median_latency_defined_over_returned_items(self):
        # Add a fourth row so median of 4 is (5000+7000)/2 = 6000 — not
        # median of full population but median of the returned items only.
        # Two-element average path.
        ChatConversation.objects.create(
            user=self.chris,
            conversation_id='conv-agent-1',
            user_message='agent consult',
            assistant_response='agent answer',
            platform='api',
            source='character-os-agent-consult',
            response_time_ms=9000,
        )
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        # Sorted latencies: [3000, 5000, 7000, 9000] → median = (5000+7000)//2 = 6000.
        self.assertEqual(result.result['structured_facts']['median_latency_ms'], 6000)

    def test_no_error_count_field_in_response(self):
        # Rigby Q1d verified: ChatConversation has no error/status field.
        # The digest MUST NOT invent one.
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        payload = result.result
        self.assertNotIn('error_count', payload)
        self.assertNotIn('error_count', payload['structured_facts'])

    # ────────────────────────────────────────────────────────────────────
    # Scoping + filters delegate correctly
    # ────────────────────────────────────────────────────────────────────

    def test_bridge_tool_name_filter_delegates(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {
                'action': 'bridge_activity_digest',
                'window': '24h',
                'bridge_tool_name': 'consult_engine',
            },
            user_id=self.chris.id,
        )
        payload = result.result
        # Only 2 consult_engine rows in fixture.
        self.assertEqual(payload['structured_facts']['total_count'], 2)
        by_tool_names = {row['bridge_tool_name'] for row in payload['structured_facts']['by_tool']}
        self.assertEqual(by_tool_names, {'consult_engine'})

    def test_no_user_context_returns_empty_narrative(self):
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=None,
        )
        # Empty-state narrative regardless of underlying data.
        self.assertEqual(result.result['structured_facts']['total_count'], 0)
        self.assertIn('No character-os bridge calls', result.result['narrative'])

    def test_window_cutoff_delegates(self):
        # Push all rows to 10 days ago; 24h window returns empty.
        old = timezone.now() - timedelta(days=10)
        ChatConversation.objects.all().update(created_at=old)
        result_24h = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        result_30d = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '30d'},
            user_id=self.chris.id,
        )
        self.assertEqual(result_24h.result['structured_facts']['total_count'], 0)
        self.assertEqual(result_30d.result['structured_facts']['total_count'], 3)

    def test_question_preview_truncated_at_80_chars(self):
        # Overwrite spider_1 (most-recent row) with a long question.
        long_q = 'x' * 200
        ChatConversation.objects.filter(id=self.spider_1.id).update(
            user_message=long_q,
        )
        result = self.dispatcher.execute_sync(
            'ops_tool',
            {'action': 'bridge_activity_digest', 'window': '24h'},
            user_id=self.chris.id,
        )
        preview = result.result['structured_facts']['most_recent']['question_preview']
        # 80 chars + ellipsis marker.
        self.assertEqual(len(preview), 81)
        self.assertTrue(preview.endswith('…'))
