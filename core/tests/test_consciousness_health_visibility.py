from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from ai_core.spiders.consciousness import ConsciousnessBridge, Capability, SystemInsight, ImprovementProposal


class FakeRedis:
    def __init__(self, initial=None):
        self.store = dict(initial or {})

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value
        return True

    def scard(self, key):
        return int(self.store.get(key, 0))


class RaisingManager:
    def __init__(self, exc):
        self.exc = exc

    def count(self):
        raise self.exc

    def filter(self, *args, **kwargs):
        raise self.exc


class RaisingModel:
    objects = RaisingManager(RuntimeError('db unavailable'))


class ConsciousnessHealthVisibilityTests(SimpleTestCase):
    def _make_bridge(self):
        redis_client = FakeRedis({
            'consciousness:awakening_time': '2026-05-04T00:00:00',
            'active_spiders': 3,
            'consciousness:ws_connections_hour': '12',
            'consciousness:api_calls_hour': '8',
        })
        return ConsciousnessBridge(redis_client=redis_client)

    def test_resource_probe_failure_marks_degraded_and_resource_failed(self):
        bridge = self._make_bridge()
        bridge.capabilities = {
            'agent': Capability(name='agent', type='agent', description='agent', file_path='x')
        }
        bridge.insights = [SystemInsight(
            discovery_time=datetime(2026, 5, 4),
            category='pattern',
            description='ok',
            evidence={},
            confidence=0.9,
            importance=0.8,
        )]
        bridge.proposals = [ImprovementProposal(
            proposal_id='p1',
            title='Improve',
            description='Improve',
            category='optimization',
            impact_score=1.0,
            complexity_score=1.0,
            roi_estimate=1.0,
            implementation_steps=['step'],
            affected_components=['x'],
            risks=[],
            benefits=[],
        )]
        bridge.memory_crystal = {'k': {'value': 1}}

        with patch.object(bridge, '_detect_emergent_behaviors', return_value=[{'name': 'emergent'}]), \
             patch('ai_core.spiders.consciousness.psutil.cpu_percent', side_effect=RuntimeError('cpu unavailable')):
            health = bridge.get_system_health()

        self.assertTrue(health['resource_probe_failed'])
        self.assertTrue(health['health_degraded'])
        self.assertTrue(health['fallback_used'])
        self.assertIn('resource_probe_failed', health['fallback_reasons'])

    def test_consciousness_fallback_marks_fallback_used(self):
        bridge = self._make_bridge()
        bridge.capabilities = {}
        bridge.insights = []
        bridge.proposals = []
        bridge.memory_crystal = {}

        with patch.object(bridge, '_detect_emergent_behaviors', return_value=[]), \
             patch('ai_core.spiders.consciousness.psutil.cpu_percent', return_value=10), \
             patch('ai_core.spiders.consciousness.psutil.virtual_memory', return_value=SimpleNamespace(percent=10)), \
             patch('ai_core.spiders.consciousness.psutil.disk_usage', return_value=SimpleNamespace(percent=10)), \
             patch('core.models_unified_system.Agent', RaisingModel), \
             patch('core.models_unified_system.AgentLearning', RaisingModel), \
             patch('core.models_unified_system.KnowledgeTransfer', RaisingModel), \
             patch('core.models_unified_system.AgentMemory', RaisingModel), \
             patch('core.models_unified_system.AgentExecution', RaisingModel):
            health = bridge.get_system_health()

        self.assertTrue(health['consciousness_score_fallback_used'])
        self.assertTrue(health['fallback_used'])
        self.assertTrue(health['health_degraded'])
        self.assertGreaterEqual(len(health['fallback_reasons']), 3)

    def test_successful_health_path_remains_non_degraded(self):
        bridge = self._make_bridge()
        bridge.capabilities = {
            'agent': Capability(name='agent', type='agent', description='agent', file_path='x')
        }
        bridge.insights = [SystemInsight(
            discovery_time=datetime(2026, 5, 4),
            category='pattern',
            description='ok',
            evidence={},
            confidence=0.9,
            importance=0.8,
        )]
        bridge.proposals = [ImprovementProposal(
            proposal_id='p1',
            title='Improve',
            description='Improve',
            category='optimization',
            impact_score=1.0,
            complexity_score=1.0,
            roi_estimate=1.0,
            implementation_steps=['step'],
            affected_components=['x'],
            risks=[],
            benefits=[],
        )]
        bridge.memory_crystal = {'k': {'value': 1}}

        with patch.object(bridge, '_detect_emergent_behaviors', return_value=[{'name': 'emergent'}]), \
             patch('ai_core.spiders.consciousness.psutil.cpu_percent', return_value=10), \
             patch('ai_core.spiders.consciousness.psutil.virtual_memory', return_value=SimpleNamespace(percent=10)), \
             patch('ai_core.spiders.consciousness.psutil.disk_usage', return_value=SimpleNamespace(percent=10)):
            health = bridge.get_system_health()

        self.assertFalse(health['resource_probe_failed'])
        self.assertFalse(health['fallback_used'])
        self.assertFalse(health['health_degraded'])
        self.assertEqual(health['fallback_reasons'], [])
        self.assertFalse(health['consciousness_score_fallback_used'])
