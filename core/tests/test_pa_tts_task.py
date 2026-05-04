from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase


class ProcessPaTtsTaskTest(SimpleTestCase):
    def test_tts_generation_failure_returns_explicit_failure_payload(self):
        from core.tasks import process_pa_tts_task

        fake_user = object()
        mock_user_model = MagicMock()
        mock_user_model.objects.get.return_value = fake_user

        mock_pa = MagicMock()
        mock_pa._generate_audio.side_effect = Exception('tts backend down')

        with patch('django.contrib.auth.get_user_model', return_value=mock_user_model), \
             patch('core.services.unified_pa_entrypoint.UnifiedPAEntrypoint', return_value=mock_pa):
            result = process_pa_tts_task(user_id=123, text='hello', conversation_id='conv-1', trace_id='trace-1')

        self.assertEqual(
            result,
            {
                'status': 'failed',
                'reason': 'tts_generation_failed',
                'error': 'tts backend down',
            },
        )
