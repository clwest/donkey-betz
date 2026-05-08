from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import sys
import types

from django.test import SimpleTestCase
from django.utils import timezone
import core.models_unified_system as models_unified_system


class PilotMetricsTest(SimpleTestCase):
    def test_query_failures_add_error_metadata_and_keep_zero_fallbacks(self):
        from core.tasks import collect_pilot_metrics

        decision = SimpleNamespace(decision_type='strategy', impact_area='product')
        pilot = SimpleNamespace(started_at=timezone.now() - timedelta(hours=2), kill_switch_triggered=False)

        mock_concern = MagicMock()
        mock_concern.objects.filter.side_effect = Exception('concerns query failed')

        mock_memory = MagicMock()
        mock_memory.objects.filter.side_effect = Exception('memory query failed')

        mock_conversation = MagicMock()
        mock_conversation.objects.filter.side_effect = Exception('conversation query failed')

        mock_concerns_module = types.ModuleType('core.models_concerns')
        mock_concerns_module.Concern = mock_concern

        with patch.dict(sys.modules, {'core.models_concerns': mock_concerns_module}), \
             patch.object(models_unified_system, 'AgentMemory', mock_memory), \
             patch.object(models_unified_system, 'AgentConversation', mock_conversation):
            metrics = collect_pilot_metrics(decision, pilot)

        self.assertEqual(metrics['concerns_during_pilot'], 0)
        self.assertEqual(metrics['agent_memories_created'], 0)
        self.assertEqual(metrics['conversations_during_pilot'], 0)
        self.assertEqual(metrics['concerns_during_pilot_error'], 'concerns query failed')
        self.assertEqual(metrics['agent_memories_created_error'], 'memory query failed')
        self.assertEqual(metrics['conversations_during_pilot_error'], 'conversation query failed')
