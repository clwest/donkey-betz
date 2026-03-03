"""
Gateway Smoke Tests — Session 1079
====================================

Verifies all 6 gateway tools dispatch correctly through ToolDispatcher.
Each test calls a non-mutating action and asserts a valid response shape.

Run: python manage.py test core.tests.test_gateway_smoke -v2
"""

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
        self.assertIn('safe_to_deprecate', result)


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
    """Verify LEGACY_TO_GATEWAY map covers all expected legacy tools."""

    def test_all_legacy_tools_mapped(self):
        expected_legacy = {
            'initiative_tool', 'content_review_tool', 'generate_blog_tool',
            'deliverables_tool', 'boardroom_tool', 'human_decisions_tool',
            'stock_intelligence_tool', 'sports_betting_tool', 'legislation_tool',
            'rag_query_tool', 'spider_data_tool', 'web_search',
            'system_health_tool', 'error_summary_tool',
        }
        self.assertEqual(set(self.dispatcher.LEGACY_TO_GATEWAY.keys()), expected_legacy)

    def test_all_gateways_registered(self):
        for gw in self.dispatcher.GATEWAY_TOOLS:
            self.assertIn(gw, self.dispatcher._tool_handlers,
                          f"Gateway {gw} not registered in ToolDispatcher")

    def test_legacy_tools_not_registered(self):
        """Legacy tools must NOT be registered (removed in PR2)."""
        # web_search is excluded — it's a standalone primitive kept intentionally
        legacy_only = set(self.dispatcher.LEGACY_TO_GATEWAY.keys()) - {'web_search'}
        for legacy_name in legacy_only:
            self.assertNotIn(legacy_name, self.dispatcher._tool_handlers,
                             f"Legacy tool {legacy_name} should have been removed in PR2")

    def test_all_legacy_mappings_point_to_valid_gateways(self):
        for legacy_name, (gw, action) in self.dispatcher.LEGACY_TO_GATEWAY.items():
            self.assertIn(gw, self.dispatcher.GATEWAY_TOOLS,
                          f"{legacy_name} maps to unknown gateway {gw}")
