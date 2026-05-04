from unittest.mock import patch

from django.test import SimpleTestCase


class LegalPlatformCollectionTest(SimpleTestCase):
    def test_courtlistener_request_failure_returns_degraded_item(self):
        from core.tasks import _collect_legal_platform

        with patch('requests.get', side_effect=Exception('network down')):
            items = _collect_legal_platform('courtlistener')

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['status'], 'degraded')
        self.assertEqual(items[0]['reason'], 'courtlistener_request_failed')
        self.assertEqual(items[0]['error'], 'Exception')
        self.assertEqual(items[0]['type'], 'legal_research')
        self.assertEqual(items[0]['message'], 'CourtListener spider degraded')
