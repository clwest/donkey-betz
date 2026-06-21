"""
Gateway Smoke Tests — Session 1079
====================================

Verifies all 6 gateway tools dispatch correctly through ToolDispatcher.
Each test calls a non-mutating action and asserts a valid response shape.

Run: python manage.py test core.tests.test_gateway_smoke -v2
"""

import unittest

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


class GatewaySmokeTestBase(TestCase):
    """Shared setup for gateway smoke tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()
        cls.user_id = 1
        cls.trace_id = 'test-gateway-smoke'

    def _call(self, tool_name: str, payload: dict) -> dict:
        """Synchronous dispatch helper. Returns the inner result dict."""
        tool_result = self.dispatcher.execute_sync(tool_name, payload, self.user_id)
        self.assertTrue(tool_result.ok, f"{tool_name} failed: {tool_result.error_message}")
        result = tool_result.result
        self.assertIsInstance(result, dict, f"{tool_name} returned {type(result)}, expected dict")
        return result


class TestOpsToolGateway(GatewaySmokeTestBase):
    """ops_tool gateway smoke tests."""

    def test_version(self):
        result = self._call('ops_tool', {'action': 'version'})
        self.assertIn('action', result)
        self.assertEqual(result['action'], 'version')

    def test_slo_status(self):
        result = self._call('ops_tool', {'action': 'slo_status'})
        self.assertIn('action', result)

    def test_failure_signatures(self):
        result = self._call('ops_tool', {'action': 'failure_signatures'})
        self.assertIn('action', result)

    def test_tool_migration_report(self):
        result = self._call('ops_tool', {'action': 'tool_migration_report', 'window': '7d'})
        self.assertIn('action', result)
        self.assertEqual(result['action'], 'tool_migration_report')
        self.assertIn('summary', result)
        self.assertIn('silent_removed_tools', result)


class TestWorkToolGateway(GatewaySmokeTestBase):
    """work_tool gateway smoke tests."""

    def test_initiative_list(self):
        result = self._call('work_tool', {'action': 'initiative_list'})
        self.assertIsInstance(result, dict)
        # Should have gateway tag
        self.assertEqual(result.get('gateway'), 'work_tool')

    def test_action_item_list(self):
        result = self._call('work_tool', {'action': 'action_item_list'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'work_tool')


class TestContentToolGateway(GatewaySmokeTestBase):
    """content_tool gateway smoke tests."""

    def test_content_stats(self):
        result = self._call('content_tool', {'action': 'content_stats'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'content_tool')

    def test_content_list(self):
        result = self._call('content_tool', {'action': 'content_list'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'content_tool')

    def test_deliverable_list(self):
        result = self._call('content_tool', {'action': 'deliverable_list'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'content_tool')

    def test_deliverable_stats(self):
        result = self._call('content_tool', {'action': 'deliverable_stats'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'content_tool')


class TestGovernanceToolGateway(GatewaySmokeTestBase):
    """governance_tool gateway smoke tests."""

    def test_inbox(self):
        result = self._call('governance_tool', {'action': 'inbox'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'governance_tool')

    def test_decisions_list(self):
        result = self._call('governance_tool', {'action': 'decisions_list'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'governance_tool')

    def test_decisions_stats(self):
        result = self._call('governance_tool', {'action': 'decisions_stats'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'governance_tool')


class TestIntelligenceToolGateway(GatewaySmokeTestBase):
    """intelligence_tool gateway smoke tests."""

    def test_overview(self):
        result = self._call('intelligence_tool', {'action': 'overview'})
        self.assertIsInstance(result, dict)
        self.assertIn('desks', result)
        self.assertEqual(result.get('gateway'), 'intelligence_tool')

    def test_search_kb(self):
        result = self._call('intelligence_tool', {'action': 'search', 'source': 'kb', 'query': 'test'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'intelligence_tool')

    def test_search_spider(self):
        result = self._call('intelligence_tool', {'action': 'search', 'source': 'spider', 'query': 'test'})
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get('gateway'), 'intelligence_tool')


class TestStudioToolGateway(GatewaySmokeTestBase):
    """studio_tool gateway smoke tests (non-mutating actions only)."""

    def test_media_list(self):
        result = self._call('studio_tool', {'action': 'media_list'})
        self.assertIsInstance(result, dict)

    def test_media_stats(self):
        result = self._call('studio_tool', {'action': 'media_stats'})
        self.assertIsInstance(result, dict)


class TestLegacyToGatewayMapping(GatewaySmokeTestBase):
    """Verify REMOVED_TOOL_ALIASES map covers all expected removed tools."""

    def test_all_removed_tools_mapped(self):
        expected_legacy = {
            'initiative_tool', 'content_review_tool', 'generate_blog_tool',
            'deliverables_tool', 'boardroom_tool', 'human_decisions_tool',
            'stock_intelligence_tool', 'sports_betting_tool', 'legislation_tool',
            'rag_query_tool', 'spider_data_tool', 'web_search',
            'system_health_tool', 'error_summary_tool',
        }
        self.assertEqual(set(self.dispatcher.REMOVED_TOOL_ALIASES.keys()), expected_legacy)

    def test_all_gateways_registered(self):
        for gw in self.dispatcher.GATEWAY_TOOLS:
            self.assertIn(gw, self.dispatcher._tool_handlers,
                          f"Gateway {gw} not registered in ToolDispatcher")

    def test_legacy_tools_not_registered(self):
        """Legacy tools must NOT be registered (removed in PR2)."""
        # web_search is excluded — it's a standalone primitive kept intentionally
        legacy_only = set(self.dispatcher.REMOVED_TOOL_ALIASES.keys()) - {'web_search'}
        for legacy_name in legacy_only:
            self.assertNotIn(legacy_name, self.dispatcher._tool_handlers,
                             f"Legacy tool {legacy_name} should have been removed in PR2")

    def test_all_legacy_mappings_point_to_valid_gateways(self):
        for legacy_name, (gw, action) in self.dispatcher.REMOVED_TOOL_ALIASES.items():
            self.assertIn(gw, self.dispatcher.GATEWAY_TOOLS,
                          f"{legacy_name} maps to unknown gateway {gw}")


class TestRemovedToolGuard(TestCase):
    """CI guard: removed tools must never reappear in handlers or PA schemas.

    Prevents accidental reintroduction of the 13 removed legacy tools.
    If this test fails, someone re-registered a removed tool — use the
    gateway equivalent instead.
    """

    REMOVED_TOOLS = frozenset([
        'boardroom_tool', 'initiative_tool', 'content_review_tool',
        'generate_blog_tool', 'deliverables_tool', 'human_decisions_tool',
        'stock_intelligence_tool', 'sports_betting_tool', 'legislation_tool',
        'rag_query_tool', 'spider_data_tool', 'system_health_tool',
        'error_summary_tool',
    ])

    def test_removed_tools_not_in_handlers(self):
        """No removed tool may be registered as a ToolDispatcher handler."""
        dispatcher = ToolDispatcher()
        for tool_name in self.REMOVED_TOOLS:
            self.assertNotIn(
                tool_name, dispatcher._tool_handlers,
                f"GUARD FAILURE: {tool_name} re-registered as handler — "
                f"use gateway equivalent instead"
            )

    def test_removed_tools_not_in_pa_schemas(self):
        """No removed tool may appear in PA_TOOL_SCHEMAS sent to GPT."""
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        schema_names = {t['name'] for t in PA_TOOL_SCHEMAS}
        for tool_name in self.REMOVED_TOOLS:
            self.assertNotIn(
                tool_name, schema_names,
                f"GUARD FAILURE: {tool_name} re-added to PA_TOOL_SCHEMAS — "
                f"use gateway equivalent instead"
            )

    def test_removed_handler_methods_not_directly_callable(self):
        """Kept handler methods (for gateway delegation) must not be accessible
        via ToolDispatcher.execute_sync() — only gateways may invoke them."""
        dispatcher = ToolDispatcher()
        # These methods exist but must NOT be registered as tools
        kept_methods = [
            'boardroom_tool', 'human_decisions_tool', 'initiative_tool',
            'content_review_tool', 'generate_blog_tool', 'deliverables_tool',
            'stock_intelligence_tool', 'sports_betting_tool', 'legislation_tool',
            'spider_data_tool', 'rag_query_tool',
        ]
        for tool_name in kept_methods:
            result = dispatcher.execute_sync(tool_name, {}, user_id=1)
            self.assertFalse(
                result.ok,
                f"BOUNDARY FAILURE: {tool_name} is callable via execute_sync() — "
                f"it should only be invoked internally by gateway handlers"
            )


class TestWebSearchHandlerLimitPassthrough(unittest.TestCase):
    """Session 1183 PR A2: _handle_web_search must honor caller-supplied
    `limit` (gateway convention) and `num_results` (legacy convention), clamped
    to 10. Prevents silent regression when ResearchAgent (or any other caller)
    migrates from `web_search` to `intelligence_tool.search`.

    Uses unittest.TestCase (not django.test.TestCase) so the test doesn't pull
    in pytest-django DB setup — handler logic is mocked at the WebSearchTool
    boundary and needs no DB.
    """

    def _invoke_handler(self, payload):
        """Invoke _handle_web_search with WebSearchTool mocked to capture
        max_results without making a real Serper call."""
        from unittest.mock import patch, MagicMock
        from core.services.tool_dispatcher import ToolDispatcher

        captured = {}
        mock_tool = MagicMock()

        def fake_execute(*, query, max_results, search_type):
            captured['query'] = query
            captured['max_results'] = max_results
            captured['search_type'] = search_type
            return {'success': True, 'data': {'results': []}}

        mock_tool.execute = fake_execute
        with patch('core.tools.web_search.WebSearchTool', return_value=mock_tool):
            ToolDispatcher()._handle_web_search(
                'web_search', payload, user_id=1, trace_id='test'
            )
        return captured

    def test_limit_param_honored(self):
        captured = self._invoke_handler({'query': 'x', 'limit': 8})
        self.assertEqual(captured['max_results'], 8)

    def test_num_results_param_honored_for_legacy_callers(self):
        captured = self._invoke_handler({'query': 'x', 'num_results': 7})
        self.assertEqual(captured['max_results'], 7)

    def test_limit_takes_precedence_over_num_results(self):
        captured = self._invoke_handler(
            {'query': 'x', 'limit': 9, 'num_results': 3}
        )
        self.assertEqual(captured['max_results'], 9)

    def test_neither_param_falls_back_to_5(self):
        captured = self._invoke_handler({'query': 'x'})
        self.assertEqual(captured['max_results'], 5)

    def test_oversized_limit_clamped_to_10(self):
        captured = self._invoke_handler({'query': 'x', 'limit': 100})
        self.assertEqual(captured['max_results'], 10)

    def test_invalid_limit_falls_back_to_5(self):
        captured = self._invoke_handler({'query': 'x', 'limit': 'bogus'})
        self.assertEqual(captured['max_results'], 5)
