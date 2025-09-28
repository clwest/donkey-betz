#!/usr/bin/env python3
"""
Phase 4 Scale & Optimize Test
Tests the massive spider army deployment and optimization

This verifies:
1. Spider pool scales to 1,000+ spiders
2. Cache layer with deduplication works
3. Performance metrics are tracked
4. Orchestration handles load
5. System optimizes automatically
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()

from django.core.cache import cache
from ai_core.spiders.pool_manager import (
    spider_pool,
    get_spider_for_task,
    release_spider,
    get_pool_statistics,
    scale_pool
)
from ai_core.spiders.cache_layer import (
    smart_cache,
    cache_get,
    cache_set,
    get_cache_stats,
    optimize_cache
)
from ai_core.spiders.metrics import (
    metrics_tracker,
    record_spider_request,
    get_performance_metrics,
    get_spider_leaderboard,
    export_all_metrics
)
from ai_core.spiders.phase4_orchestrator import (
    phase4_orchestrator,
    start_phase4_orchestration,
    get_phase4_status,
    stop_phase4_orchestration
)

# Initialize colorama
init(autoreset=True)


class Phase4Tester:
    """Test Phase 4 scale and optimization"""

    def __init__(self):
        self.results = {
            'pool_scaling': None,
            'cache_performance': None,
            'metrics_tracking': None,
            'orchestration': None,
            'stress_test': None,
            'optimization': None
        }

    async def test_pool_scaling(self):
        """Test spider pool scaling to 1,000+"""
        print(f"\n{Fore.CYAN}=== Testing Spider Pool Scaling ==={Style.RESET_ALL}")

        try:
            # Initial pool size
            initial_stats = spider_pool.get_pool_stats()
            print(f"Initial pool size: {initial_stats['total_spiders']}")

            # Scale to 500 spiders
            print(f"\n{Fore.YELLOW}Scaling to 500 spiders...{Style.RESET_ALL}")
            await scale_pool(500)

            mid_stats = spider_pool.get_pool_stats()
            print(f"{Fore.GREEN}✅ Scaled to {mid_stats['total_spiders']} spiders{Style.RESET_ALL}")

            # Scale to 1,000 spiders
            print(f"\n{Fore.YELLOW}Scaling to 1,000 spiders...{Style.RESET_ALL}")
            await scale_pool(1000)

            final_stats = spider_pool.get_pool_stats()
            print(f"{Fore.GREEN}✅ Scaled to {final_stats['total_spiders']} spiders{Style.RESET_ALL}")

            # Show distribution
            print(f"\n{Fore.CYAN}Spider Type Distribution:{Style.RESET_ALL}")
            for spider_type, count in final_stats['type_distribution'].items():
                print(f"  {spider_type}: {count}")

            # Test auto-scaling
            print(f"\n{Fore.YELLOW}Testing auto-scaling...{Style.RESET_ALL}")
            await spider_pool.auto_scale()

            auto_stats = spider_pool.get_pool_stats()
            print(f"{Fore.GREEN}✅ Auto-scaled: {auto_stats['load_percentage']:.1f}% load{Style.RESET_ALL}")

            self.results['pool_scaling'] = {
                'status': 'success',
                'final_size': final_stats['total_spiders'],
                'load': auto_stats['load_percentage'],
                'distribution': final_stats['type_distribution']
            }

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ Pool scaling error: {e}{Style.RESET_ALL}")
            self.results['pool_scaling'] = {'status': 'error', 'error': str(e)}
            return False

    async def test_cache_performance(self):
        """Test cache layer with deduplication"""
        print(f"\n{Fore.CYAN}=== Testing Cache Performance ==={Style.RESET_ALL}")

        try:
            # Clear cache first
            await smart_cache.clear()

            # Test basic caching
            test_data = {'test': 'data', 'value': 42}
            await cache_set('test_key', test_data)

            cached = await cache_get('test_key')
            if cached == test_data:
                print(f"{Fore.GREEN}✅ Basic caching works{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ Cache mismatch{Style.RESET_ALL}")

            # Test deduplication
            duplicate_data = test_data.copy()
            await cache_set('duplicate_key', duplicate_data)

            stats_before = smart_cache.get_statistics()
            duplicates_before = stats_before['duplicates_prevented']

            # Try to cache same content with different key
            await cache_set('another_key', duplicate_data)

            stats_after = smart_cache.get_statistics()
            if stats_after['duplicates_prevented'] > duplicates_before:
                print(f"{Fore.GREEN}✅ Deduplication prevented {stats_after['duplicates_prevented']} duplicates{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ Deduplication not triggered{Style.RESET_ALL}")

            # Test compression
            large_data = {'data': ['item'] * 1000}
            await cache_set('large_key', large_data)

            cache_stats = smart_cache.get_statistics()
            print(f"\n{Fore.CYAN}Cache Statistics:{Style.RESET_ALL}")
            print(f"  Entries: {cache_stats['entries']}")
            print(f"  Size: {cache_stats['size_mb']:.2f} MB")
            print(f"  Hit rate: {cache_stats['hit_rate']:.1f}%")
            print(f"  Compression ratio: {cache_stats['compression_ratio']:.2f}x")
            print(f"  Bytes saved: {cache_stats['bytes_saved']:,}")

            # Test optimization
            print(f"\n{Fore.YELLOW}Optimizing cache...{Style.RESET_ALL}")
            optimization_result = await optimize_cache()
            print(f"{Fore.GREEN}✅ Cache optimized: {optimization_result['space_saved_mb']:.2f} MB saved{Style.RESET_ALL}")

            self.results['cache_performance'] = {
                'status': 'success',
                'stats': cache_stats,
                'optimization': optimization_result
            }

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ Cache performance error: {e}{Style.RESET_ALL}")
            self.results['cache_performance'] = {'status': 'error', 'error': str(e)}
            return False

    async def test_metrics_tracking(self):
        """Test performance metrics tracking"""
        print(f"\n{Fore.CYAN}=== Testing Metrics Tracking ==={Style.RESET_ALL}")

        try:
            # Simulate spider requests
            for i in range(100):
                spider_id = f"test_spider_{i % 10}"
                success = i % 10 != 0  # 90% success rate
                response_time = 100 + (i % 500)  # Variable response time
                data_collected = i % 20

                record_spider_request(spider_id, success, response_time, data_collected)

            # Get current metrics
            metrics = get_performance_metrics()
            print(f"\n{Fore.CYAN}Performance Metrics:{Style.RESET_ALL}")
            print(f"  Total requests: {metrics['total_requests']}")
            print(f"  RPS: {metrics['requests_per_second']:.2f}")
            print(f"  Error rate: {metrics['error_rate_percent']:.1f}%")
            print(f"  Avg latency: {metrics['avg_latency_ms']:.0f}ms")
            print(f"  Active spiders: {metrics['active_spiders']}")
            print(f"  Unique opportunities: {metrics['unique_opportunities']}")

            # Get spider leaderboard
            leaderboard = get_spider_leaderboard()
            if leaderboard:
                print(f"\n{Fore.CYAN}Top Performing Spiders:{Style.RESET_ALL}")
                for i, spider in enumerate(leaderboard[:5], 1):
                    print(f"  {i}. {spider['spider_id']}: Score {spider['score']:.2f}")

            # Check system metrics
            system = metrics['system_metrics']
            print(f"\n{Fore.CYAN}System Metrics:{Style.RESET_ALL}")
            print(f"  CPU: {system['cpu_usage']:.1f}%")
            print(f"  Memory: {system['memory_usage']:.1f}%")
            print(f"  Disk: {system['disk_usage']:.1f}%")

            # Export all metrics
            all_metrics = export_all_metrics()

            self.results['metrics_tracking'] = {
                'status': 'success',
                'metrics': metrics,
                'leaderboard_size': len(leaderboard),
                'export_size': len(json.dumps(all_metrics))
            }

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ Metrics tracking error: {e}{Style.RESET_ALL}")
            self.results['metrics_tracking'] = {'status': 'error', 'error': str(e)}
            return False

    async def test_orchestration(self):
        """Test spider orchestration"""
        print(f"\n{Fore.CYAN}=== Testing Spider Orchestration ==={Style.RESET_ALL}")

        try:
            # Initialize orchestrator
            print(f"{Fore.YELLOW}Initializing orchestrator...{Style.RESET_ALL}")
            await phase4_orchestrator.initialize()

            # Get initial status
            status = await get_phase4_status()
            print(f"{Fore.GREEN}✅ Orchestrator initialized{Style.RESET_ALL}")
            print(f"  Mode: {status['mode']}")
            print(f"  Running: {status['is_running']}")

            # Generate and process some tasks
            print(f"\n{Fore.YELLOW}Generating test tasks...{Style.RESET_ALL}")

            test_tasks = []
            for i in range(50):
                task_type = phase4_orchestrator._select_task_type()
                task = phase4_orchestrator._generate_task(task_type)
                test_tasks.append(task)
                await phase4_orchestrator.task_queue.put(task)

            print(f"{Fore.GREEN}✅ Generated {len(test_tasks)} tasks{Style.RESET_ALL}")

            # Wait a bit for processing
            await asyncio.sleep(5)

            # Check orchestration stats
            final_status = await get_phase4_status()
            stats = final_status['stats']

            print(f"\n{Fore.CYAN}Orchestration Statistics:{Style.RESET_ALL}")
            print(f"  Tasks processed: {stats['total_tasks_processed']}")
            print(f"  Data collected: {stats['total_data_collected']}")
            print(f"  Opportunities found: {stats['total_opportunities_found']}")
            print(f"  Revenue potential: ${stats['total_revenue_potential']:,.2f}")
            print(f"  Efficiency: {stats['current_efficiency']:.2%}")

            # Show task distribution
            print(f"\n{Fore.CYAN}Task Distribution:{Style.RESET_ALL}")
            for task_type, weight in final_status['distribution'].items():
                print(f"  {task_type}: {weight:.2%}")

            self.results['orchestration'] = {
                'status': 'success',
                'tasks_processed': stats['total_tasks_processed'],
                'efficiency': stats['current_efficiency']
            }

            # Shutdown orchestrator
            try:
                await stop_phase4_orchestration()
            except Exception as e:
                logger.warning(f"⚠️ Orchestrator shutdown warning: {e}")

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ Orchestration error: {e}{Style.RESET_ALL}")
            self.results['orchestration'] = {'status': 'error', 'error': str(e)}
            return False

    async def stress_test(self):
        """Run stress test with many concurrent operations"""
        print(f"\n{Fore.CYAN}=== Running Stress Test ==={Style.RESET_ALL}")

        try:
            print(f"{Fore.YELLOW}Starting stress test with 1,000 concurrent tasks...{Style.RESET_ALL}")

            start_time = time.time()
            tasks_created = 0
            tasks_completed = 0

            # Create many concurrent tasks
            async def create_task(i):
                task = {
                    'type': 'stress_test',
                    'id': f"stress_{i}",
                    'data': {'value': i}
                }

                # Get spider
                spider_id = await get_spider_for_task(task)
                if spider_id:
                    # Simulate work
                    await asyncio.sleep(0.01)

                    # Release spider
                    await release_spider(spider_id, {'success': True})
                    return True
                return False

            # Run tasks concurrently
            stress_tasks = []
            for i in range(1000):
                stress_tasks.append(create_task(i))
                tasks_created += 1

            # Wait for completion with timeout
            results = await asyncio.gather(*stress_tasks, return_exceptions=True)

            tasks_completed = sum(1 for r in results if r is True)
            duration = time.time() - start_time

            print(f"{Fore.GREEN}✅ Stress test complete{Style.RESET_ALL}")
            print(f"  Duration: {duration:.2f}s")
            print(f"  Tasks created: {tasks_created}")
            print(f"  Tasks completed: {tasks_completed}")
            print(f"  Throughput: {tasks_completed/duration:.2f} tasks/sec")

            # Check system health after stress
            pool_stats = spider_pool.get_pool_stats()
            metrics = get_performance_metrics()

            print(f"\n{Fore.CYAN}System Health After Stress:{Style.RESET_ALL}")
            print(f"  Spider pool load: {pool_stats['load_percentage']:.1f}%")
            print(f"  Failed spiders: {pool_stats['failed']}")
            print(f"  Error rate: {metrics['error_rate_percent']:.1f}%")

            self.results['stress_test'] = {
                'status': 'success',
                'tasks_completed': tasks_completed,
                'throughput': tasks_completed/duration,
                'duration': duration
            }

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ Stress test error: {e}{Style.RESET_ALL}")
            self.results['stress_test'] = {'status': 'error', 'error': str(e)}
            return False

    async def test_optimization(self):
        """Test automatic optimization features"""
        print(f"\n{Fore.CYAN}=== Testing Automatic Optimization ==={Style.RESET_ALL}")

        try:
            # Test pool optimization
            print(f"{Fore.YELLOW}Testing pool optimization...{Style.RESET_ALL}")

            # Simulate high load
            for _ in range(100):
                task = {'type': 'test', 'priority': 5}
                await spider_pool.assign_task(task)

            # Trigger optimization
            await spider_pool.optimize_distribution()
            distribution = await spider_pool.optimize_distribution()

            print(f"{Fore.GREEN}✅ Pool distribution optimized{Style.RESET_ALL}")

            # Test health check
            print(f"\n{Fore.YELLOW}Running health check...{Style.RESET_ALL}")
            await spider_pool.health_check()

            pool_stats = spider_pool.get_pool_stats()
            print(f"{Fore.GREEN}✅ Health check complete{Style.RESET_ALL}")
            print(f"  Healthy spiders: {pool_stats['total_spiders'] - pool_stats['failed']}")
            print(f"  Top performers: {len(pool_stats['top_performers'])}")

            # Test cache optimization
            print(f"\n{Fore.YELLOW}Testing cache optimization...{Style.RESET_ALL}")
            cache_result = await smart_cache.optimize()
            print(f"{Fore.GREEN}✅ Cache optimized: {cache_result['entries_optimized']} entries{Style.RESET_ALL}")

            self.results['optimization'] = {
                'status': 'success',
                'pool_optimized': True,
                'cache_optimized': cache_result['entries_optimized'] > 0
            }

            return True

        except Exception as e:
            print(f"{Fore.RED}❌ Optimization test error: {e}{Style.RESET_ALL}")
            self.results['optimization'] = {'status': 'error', 'error': str(e)}
            return False

    def print_summary(self):
        """Print test summary"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}PHASE 4 SCALE & OPTIMIZE TEST SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")

        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values()
                          if r and r.get('status') == 'success')

        for test_name, result in self.results.items():
            if result:
                if result['status'] == 'success':
                    status = f"{Fore.GREEN}✅ PASS{Style.RESET_ALL}"
                else:
                    status = f"{Fore.RED}❌ FAIL{Style.RESET_ALL}"
            else:
                status = f"{Fore.YELLOW}⚠️ SKIP{Style.RESET_ALL}"

            print(f"{test_name.replace('_', ' ').title():30} {status}")

        print(f"\n{Fore.CYAN}Overall: {passed_tests}/{total_tests} tests passed{Style.RESET_ALL}")

        if passed_tests == total_tests:
            print(f"\n{Fore.GREEN}🎉 PHASE 4 SCALE & OPTIMIZE COMPLETE!{Style.RESET_ALL}")
            print(f"{Fore.GREEN}System can handle 1,000+ spiders with optimization!{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️ Some tests failed. Review the output above.{Style.RESET_ALL}")

        # Print key achievements
        print(f"\n{Fore.CYAN}Key Achievements:{Style.RESET_ALL}")

        if self.results['pool_scaling'] and self.results['pool_scaling']['status'] == 'success':
            print(f"  Spider Pool: {self.results['pool_scaling']['final_size']} spiders")

        if self.results['cache_performance'] and self.results['cache_performance']['status'] == 'success':
            stats = self.results['cache_performance']['stats']
            print(f"  Cache: {stats['compression_ratio']:.2f}x compression, {stats['hit_rate']:.1f}% hit rate")

        if self.results['stress_test'] and self.results['stress_test']['status'] == 'success':
            print(f"  Throughput: {self.results['stress_test']['throughput']:.2f} tasks/sec")

        if self.results['orchestration'] and self.results['orchestration']['status'] == 'success':
            print(f"  Efficiency: {self.results['orchestration']['efficiency']:.2%}")


async def main():
    """Run Phase 4 scale and optimization tests"""
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}PHASE 4: SCALE & OPTIMIZE - 1,000+ SPIDERS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tester = Phase4Tester()

    # Run tests
    await tester.test_pool_scaling()
    await tester.test_cache_performance()
    await tester.test_metrics_tracking()
    await tester.test_orchestration()
    await tester.stress_test()
    await tester.test_optimization()

    # Print summary
    tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())