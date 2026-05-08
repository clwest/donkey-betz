from unittest.mock import patch

from django.test import SimpleTestCase


class StockFinancialTaskTest(SimpleTestCase):
    def test_run_stock_financial_agents_delegates_to_stock_audit_cycle(self):
        from core.tasks import run_stock_financial_agents

        expected = {'status': 'ok', 'total_alerts': 3}
        with patch('core.tasks.run_stock_audit_cycle', return_value=expected) as mock_audit:
            result = run_stock_financial_agents()

        self.assertEqual(result, expected)
        mock_audit.assert_called_once_with()
