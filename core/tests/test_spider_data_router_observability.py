import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from django.test import SimpleTestCase

import ai_core.spiders.spider_data_router as router_module
from ai_core.spiders.spider_data_router import (
    ConnectionMapping,
    ConnectionStatus,
    DataFlowPriority,
    SpiderDataRouter,
    SpiderType,
)


class FakeRedis:
    def __init__(self, *args, **kwargs):
        self.values = {}


class FakeAsyncRedis:
    async def publish(self, *args, **kwargs):
        return 1

    async def lpush(self, *args, **kwargs):
        return 1

    async def ltrim(self, *args, **kwargs):
        return True

    async def setex(self, *args, **kwargs):
        return True

    async def ping(self):
        return True

    def pubsub(self):
        raise AssertionError("pubsub should not be called in these tests")


class SpiderDataRouterObservabilityTests(SimpleTestCase):
    def _make_router(self):
        fake_army = SimpleNamespace(
            swarm_configs={},
            get_army_status=lambda: {
                'is_running': True,
                'army_stats': {
                    'total_spiders': 0,
                    'active_spiders': 0,
                },
            },
            shutdown_army=AsyncMock(),
        )
        fake_pipeline = SimpleNamespace(
            get_status=lambda: {'is_running': True},
            shutdown=AsyncMock(),
        )
        with patch.object(router_module, 'SpiderArmyOrchestrator', return_value=fake_army), \
             patch.object(router_module, 'RealTimeDataPipeline', return_value=fake_pipeline), \
             patch.object(router_module, 'get_agent_registry', create=True, return_value=SimpleNamespace()), \
             patch.object(router_module, 'get_advisor_registry', create=True, return_value=SimpleNamespace()), \
             patch.object(router_module.redis, 'Redis', return_value=FakeRedis()):
            router = SpiderDataRouter()
        router.redis_async = FakeAsyncRedis()
        return router

    def test_malformed_message_records_route_outcome_and_counters(self):
        router = self._make_router()

        outcome = asyncio.run(
            router._route_spider_message({
                'channel': b'spider_intelligence:test_channel',
                'data': b'not-json',
            })
        )
        status = router.get_router_status()

        self.assertEqual(outcome['route_status'], 'malformed_message')
        self.assertEqual(outcome['failure_type'], 'malformed_message')
        self.assertEqual(outcome['channel'], 'spider_intelligence:test_channel')
        self.assertEqual(status['malformed_message_count'], 1)
        self.assertEqual(status['router_loop_errors'], 0)
        self.assertFalse(status['metrics_stale'])
        self.assertEqual(status['last_route_outcome']['route_status'], 'malformed_message')

    def test_filter_rejections_are_visible_in_status(self):
        router = self._make_router()
        router.connection_mappings = {
            'spider_1:agent:consumer1': ConnectionMapping(
                spider_id='spider_1',
                spider_type=SpiderType.FINANCIAL,
                consumer_type='agent',
                consumer_id='consumer1',
                priority=DataFlowPriority.NORMAL,
                data_types=['news'],
                filters={'keywords': ['python']},
                status=ConnectionStatus.ACTIVE,
            )
        }

        outcome = asyncio.run(
            router._route_spider_message({
                'channel': b'spider_intelligence:test_channel',
                'data': b'{"spider_id": "spider_1", "content": {"text": "hello world"}, "data_type": "news", "quality_score": 1.0}',
            })
        )
        status = router.get_router_status()

        self.assertEqual(outcome['route_status'], 'filtered_out')
        self.assertEqual(outcome['failure_type'], 'filter_rejection')
        self.assertEqual(outcome['consumer_count'], 1)
        self.assertEqual(status['filter_rejection_reasons']['keyword_miss'], 1)
        self.assertEqual(status['last_route_outcome']['route_status'], 'filtered_out')

    def test_delivery_failures_and_stale_metrics_are_visible(self):
        router = self._make_router()
        router.connection_mappings = {
            'spider_1:agent:consumer1': ConnectionMapping(
                spider_id='spider_1',
                spider_type=SpiderType.FINANCIAL,
                consumer_type='agent',
                consumer_id='consumer1',
                priority=DataFlowPriority.NORMAL,
                data_types=['news'],
                filters={},
                status=ConnectionStatus.ACTIVE,
            )
        }
        router.redis_async = FakeAsyncRedis()
        router.redis_async.publish = AsyncMock(side_effect=RuntimeError('publish failed'))
        router.metrics.last_updated = datetime.now(timezone.utc) - timedelta(minutes=10)

        outcome = asyncio.run(
            router._route_spider_message({
                'channel': b'spider_intelligence:test_channel',
                'data': b'{"spider_id": "spider_1", "content": {"text": "hello world"}, "data_type": "news", "quality_score": 1.0}',
            })
        )
        status = router.get_router_status()

        self.assertEqual(outcome['route_status'], 'partial_failure')
        self.assertEqual(outcome['failure_type'], 'delivery_failure')
        self.assertEqual(outcome['delivery_failure_count'], 1)
        self.assertEqual(status['delivery_failure_count'], 1)
        self.assertIsNotNone(status['last_delivery_failure'])
        self.assertTrue(status['metrics_stale'])
