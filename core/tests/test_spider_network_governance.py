from types import SimpleNamespace
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

    def test_spider_batch_marks_missing_or_failed_spiders_as_failures(self):
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry = SimpleNamespace()
        fake_registry.list_spiders = lambda: {
            'missing_spider': {'config': {'category': 'general'}, 'category': 'general'},
            'adapter_spider': {'config': {'category': 'general'}, 'category': 'general'},
            'successful_spider': {'config': {'category': 'general'}, 'category': 'general'},
        }
        fake_registry.get_spider_class = lambda name: object() if name != 'missing_spider' else None

        def fake_create_spider_instance(spider_class, spider_name):
            return object()

        def fake_run_spider_adapter(spider, spider_name):
            if spider_name == 'adapter_spider':
                raise RuntimeError('adapter exploded')
            return {
                'items': [{'id': 1}],
                'source': spider_name,
            }

        fake_governance = SimpleNamespace(
            objects=SimpleNamespace(
                filter=lambda *args, **kwargs: SimpleNamespace(
                    first=lambda: SimpleNamespace(effective_mode='normal')
                )
            )
        )

        with patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('core.tasks_spiders._create_spider_instance', side_effect=fake_create_spider_instance), \
             patch('core.tasks_spiders._run_spider_adapter', side_effect=fake_run_spider_adapter), \
             patch('core.tasks_spiders._collect_spider_data_sync') as mock_collect, \
             patch('core.services.spider_deduplication.deduplicate_spider_items') as mock_dedup, \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.SpiderData') as mock_spider_data, \
             patch('redis.Redis.from_url') as mock_redis_from_url, \
             patch('core.tasks_spiders.datetime') as mock_datetime:
            mock_collect.return_value = {'item_count': 1}
            mock_dedup.return_value = ([{'id': 1}], {'duplicates': 0, 'total': 1})
            mock_exec_log.start_execution.return_value = SimpleNamespace(
                source_urls_attempted=[],
                complete_success=lambda *args, **kwargs: None,
                complete_error=lambda *args, **kwargs: None,
            )
            mock_spider_data.objects.create.return_value = SimpleNamespace(id=123)
            mock_redis_from_url.return_value.publish.return_value = 1
            mock_datetime.now.return_value.isoformat.return_value = '2026-05-04T00:00:00'

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='task-1')))

        spider_results = {entry['spider']: entry for entry in result['spider_results']}

        self.assertEqual(result['spiders_run'], 1)
        self.assertEqual(result['errors'], 0)
        self.assertEqual(result['partial_failure'], True)
        self.assertEqual(result['failure_count'], 2)
        self.assertEqual(result['failed_spiders'], ['missing_spider', 'adapter_spider'])
        self.assertEqual(spider_results['missing_spider']['success'], False)
        self.assertEqual(spider_results['missing_spider']['failure_type'], 'missing_spider')
        self.assertEqual(spider_results['adapter_spider']['success'], False)
        self.assertEqual(spider_results['adapter_spider']['failure_type'], 'adapter_failure')
        self.assertEqual(spider_results['successful_spider']['success'], True)

    def test_spider_batch_clean_success_keeps_top_level_success_summary_clean(self):
        from core.tasks_spiders import _impl_run_spider_network

        fake_registry = SimpleNamespace()
        fake_registry.list_spiders = lambda: {
            'successful_spider': {'config': {'category': 'general'}, 'category': 'general'},
        }
        fake_registry.get_spider_class = lambda name: object()

        fake_governance = SimpleNamespace(
            objects=SimpleNamespace(
                filter=lambda *args, **kwargs: SimpleNamespace(
                    first=lambda: SimpleNamespace(effective_mode='normal')
                )
            )
        )

        with patch('core.models_governance.GovernanceState', fake_governance), \
             patch('ai_core.spiders.spider_registry.SpiderRegistry', return_value=fake_registry), \
             patch('core.tasks_spiders._create_spider_instance', return_value=object()), \
             patch('core.tasks_spiders._run_spider_adapter', return_value={'items': [{'id': 1}], 'source': 'successful_spider'}), \
             patch('core.tasks_spiders._collect_spider_data_sync') as mock_collect, \
             patch('core.services.spider_deduplication.deduplicate_spider_items') as mock_dedup, \
             patch('core.models_unified_system.SpiderExecutionLog') as mock_exec_log, \
             patch('core.models_unified_system.SpiderData') as mock_spider_data, \
             patch('redis.Redis.from_url') as mock_redis_from_url, \
             patch('core.tasks_spiders.datetime') as mock_datetime:
            mock_collect.return_value = {'item_count': 1}
            mock_dedup.return_value = ([{'id': 1}], {'duplicates': 0, 'total': 1})
            mock_exec_log.start_execution.return_value = SimpleNamespace(
                source_urls_attempted=[],
                complete_success=lambda *args, **kwargs: None,
                complete_error=lambda *args, **kwargs: None,
            )
            mock_spider_data.objects.create.return_value = SimpleNamespace(id=123)
            mock_redis_from_url.return_value.publish.return_value = 1
            mock_datetime.now.return_value.isoformat.return_value = '2026-05-04T00:00:00'

            result = _impl_run_spider_network(SimpleNamespace(request=SimpleNamespace(id='task-2')))

        self.assertEqual(result['spiders_run'], 1)
        self.assertEqual(result['errors'], 0)
        self.assertEqual(result['partial_failure'], False)
        self.assertEqual(result['failure_count'], 0)
        self.assertEqual(result['failed_spiders'], [])
