from unittest.mock import patch

from django.test import SimpleTestCase


class SpiderNetworkGovernanceTest(SimpleTestCase):
    def test_governance_lookup_failure_skips_spider_network(self):
        from core.tasks_spiders import _impl_run_spider_network

        with patch('core.models_governance.GovernanceState') as mock_governance, \
             patch('ai_core.spiders.spider_registry.SpiderRegistry') as mock_registry:
            mock_governance.objects.filter.side_effect = Exception('governance db unavailable')

            result = _impl_run_spider_network(None)

        self.assertEqual(
            result,
            {
                'skipped': True,
                'reason': 'governance_lookup_failed',
                'error': 'Exception',
            },
        )
        mock_registry.assert_not_called()
