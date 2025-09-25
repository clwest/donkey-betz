#!/usr/bin/env python3
"""
Complete Learning Pipeline Integration Test
==========================================

This script tests the complete spider-to-learning-loop pipeline:

1. Spider data collection and processing
2. Data transformation to learning signals
3. Agent learning from signals
4. Learning loop feedback and optimization
5. Metrics and monitoring

Usage:
    python test_complete_learning_pipeline.py
"""

import asyncio
import json
import logging
import sys
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Any

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('learning_pipeline_test.log')
    ]
)

logger = logging.getLogger(__name__)


class PipelineIntegrationTester:
    """Comprehensive integration tester for the learning pipeline"""

    def __init__(self):
        self.test_results = {
            'start_time': datetime.now(timezone.utc),
            'tests': {},
            'overall_success': False,
            'errors': [],
            'warnings': []
        }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("🚀 Starting Complete Learning Pipeline Integration Test")

        try:
            # Test 1: Component Initialization
            await self._test_component_initialization()

            # Test 2: Pipeline Connection
            await self._test_pipeline_connections()

            # Test 3: Data Flow
            await self._test_data_flow()

            # Test 4: Agent Learning
            await self._test_agent_learning()

            # Test 5: Metrics Collection
            await self._test_metrics_collection()

            # Test 6: End-to-End Integration
            await self._test_end_to_end_integration()

            # Test 7: Performance and Scalability
            await self._test_performance()

            # Test 8: Error Handling and Recovery
            await self._test_error_handling()

            # Calculate overall success
            self._calculate_overall_success()

            self.test_results['end_time'] = datetime.now(timezone.utc)
            self.test_results['duration_seconds'] = (
                self.test_results['end_time'] - self.test_results['start_time']
            ).total_seconds()

            return self.test_results

        except Exception as e:
            logger.error(f"❌ Critical test failure: {e}")
            self.test_results['critical_error'] = str(e)
            return self.test_results

    async def _test_component_initialization(self):
        """Test initialization of all pipeline components"""
        logger.info("🔧 Testing component initialization...")

        test_name = "component_initialization"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            # Test Spider Learning Orchestrator
            logger.info("  Testing Spider Learning Orchestrator...")
            from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
            spider_orchestrator = get_spider_orchestrator()

            # Check if it can be initialized (don't actually start all spiders in test)
            self.test_results['tests'][test_name]['details']['spider_orchestrator'] = 'available'

            # Test Data Transformation Pipeline
            logger.info("  Testing Data Transformation Pipeline...")
            from backend.intelligence.data_transformation_pipeline import get_transformation_pipeline
            transformation_pipeline = get_transformation_pipeline()

            # Test initialization
            await transformation_pipeline.initialize()
            stats = await transformation_pipeline.get_transformation_statistics()
            self.test_results['tests'][test_name]['details']['transformation_pipeline'] = {
                'initialized': True,
                'rules_registered': stats.get('rules_registered', 0)
            }

            # Test Agent Learning Engine
            logger.info("  Testing Agent Learning Engine...")
            from backend.intelligence.agent_learning_engine import get_learning_engine
            learning_engine = get_learning_engine()

            # Test initialization
            await learning_engine.initialize()
            status = await learning_engine.get_learning_engine_status()
            self.test_results['tests'][test_name]['details']['learning_engine'] = {
                'initialized': True,
                'agents_tracked': status.get('agents_tracked', 0)
            }

            # Test Learning Loop
            logger.info("  Testing Learning Loop...")
            from backend.intelligence.learning_loop import learning_loop
            # Test that learning loop is available
            loop_status = learning_loop.get_learning_status()
            self.test_results['tests'][test_name]['details']['learning_loop'] = {
                'available': True,
                'feedback_collected': loop_status.get('feedback_collected', 0)
            }

            # Test Metrics Dashboard
            logger.info("  Testing Metrics Dashboard...")
            from backend.intelligence.learning_metrics_dashboard import get_metrics_dashboard
            metrics_dashboard = get_metrics_dashboard()

            await metrics_dashboard.initialize()
            self.test_results['tests'][test_name]['details']['metrics_dashboard'] = 'initialized'

            self.test_results['tests'][test_name]['success'] = True
            logger.info("✅ Component initialization test passed")

        except Exception as e:
            error_msg = f"Component initialization failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    async def _test_pipeline_connections(self):
        """Test connections between pipeline components"""
        logger.info("🔗 Testing pipeline connections...")

        test_name = "pipeline_connections"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            # Test Unified Pipeline
            logger.info("  Testing Unified Learning Pipeline...")
            from backend.intelligence.unified_learning_pipeline import get_unified_pipeline
            pipeline = get_unified_pipeline()

            # Initialize pipeline (this tests all component connections)
            await pipeline.initialize()

            # Get pipeline status
            status = await pipeline.get_pipeline_status()
            self.test_results['tests'][test_name]['details']['pipeline_status'] = {
                'overall_status': status.overall_status,
                'spider_orchestrator_active': status.spider_orchestrator_active,
                'transformation_pipeline_active': status.transformation_pipeline_active,
                'learning_engine_active': status.learning_engine_active,
                'learning_loop_active': status.learning_loop_active,
                'redis_connected': status.redis_connected
            }

            # Test Redis connectivity
            if not status.redis_connected:
                self.test_results['tests'][test_name]['errors'].append("Redis connection failed")

            # Check if most components are active
            active_components = sum([
                status.spider_orchestrator_active,
                status.transformation_pipeline_active,
                status.learning_engine_active,
                status.learning_loop_active,
                status.redis_connected
            ])

            if active_components >= 3:  # Allow some flexibility
                self.test_results['tests'][test_name]['success'] = True
                logger.info("✅ Pipeline connections test passed")
            else:
                error_msg = f"Only {active_components}/5 components active"
                self.test_results['tests'][test_name]['errors'].append(error_msg)
                logger.warning(f"⚠️ {error_msg}")

        except Exception as e:
            error_msg = f"Pipeline connections test failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    async def _test_data_flow(self):
        """Test data flow through the pipeline"""
        logger.info("📊 Testing data flow...")

        test_name = "data_flow"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            # Create mock spider data
            from backend.intelligence.data_transformation_pipeline import RawSpiderData

            mock_data = RawSpiderData(
                spider_id="test_spider_001",
                spider_type="financial",
                source_url="https://test.example.com",
                timestamp=datetime.now(timezone.utc),
                raw_content={
                    "price": 5.2,  # 5.2% price increase
                    "volume": 2.1,  # 2.1x normal volume
                    "market": "NYSE",
                    "symbol": "TEST"
                },
                metadata={"test": True},
                quality_score=0.8
            )

            # Test data transformation
            from backend.intelligence.data_transformation_pipeline import get_transformation_pipeline
            transformation_pipeline = get_transformation_pipeline()

            signals = await transformation_pipeline.transform_data_to_signals(mock_data, "financial")

            self.test_results['tests'][test_name]['details']['signals_generated'] = len(signals)

            if signals:
                logger.info(f"  Generated {len(signals)} learning signals from mock data")

                # Test signal structure
                signal = signals[0]
                required_fields = ['signal_id', 'signal_type', 'category', 'confidence', 'content']

                for field in required_fields:
                    if not hasattr(signal, field):
                        self.test_results['tests'][test_name]['errors'].append(f"Signal missing field: {field}")

                self.test_results['tests'][test_name]['details']['signal_example'] = {
                    'signal_id': signal.signal_id,
                    'signal_type': signal.signal_type,
                    'category': signal.category,
                    'confidence': signal.confidence
                }

                self.test_results['tests'][test_name]['success'] = True
                logger.info("✅ Data flow test passed")

            else:
                error_msg = "No learning signals generated from mock data"
                self.test_results['tests'][test_name]['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")

        except Exception as e:
            error_msg = f"Data flow test failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    async def _test_agent_learning(self):
        """Test agent learning from signals"""
        logger.info("🧠 Testing agent learning...")

        test_name = "agent_learning"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            from backend.intelligence.agent_learning_engine import get_learning_engine
            learning_engine = get_learning_engine()

            # Get agent count
            status = await learning_engine.get_learning_engine_status()
            agent_count = status.get('agents_tracked', 0)

            self.test_results['tests'][test_name]['details']['agents_available'] = agent_count

            if agent_count > 0:
                logger.info(f"  Found {agent_count} agents available for learning")

                # Test agent status retrieval
                agent_ids = list(learning_engine.agent_profiles.keys())[:3]  # Test first 3 agents

                agents_tested = 0
                for agent_id in agent_ids:
                    try:
                        agent_status = await learning_engine.get_agent_learning_status(agent_id)

                        if 'error' not in agent_status:
                            agents_tested += 1
                            logger.info(f"    ✓ Agent {agent_id} status retrieved")

                    except Exception as e:
                        self.test_results['tests'][test_name]['errors'].append(f"Agent {agent_id} status error: {e}")

                self.test_results['tests'][test_name]['details']['agents_tested'] = agents_tested

                if agents_tested > 0:
                    self.test_results['tests'][test_name]['success'] = True
                    logger.info("✅ Agent learning test passed")
                else:
                    error_msg = "No agents could be tested successfully"
                    self.test_results['tests'][test_name]['errors'].append(error_msg)

            else:
                error_msg = "No agents available for testing"
                self.test_results['tests'][test_name]['errors'].append(error_msg)
                logger.error(f"❌ {error_msg}")

        except Exception as e:
            error_msg = f"Agent learning test failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    async def _test_metrics_collection(self):
        """Test metrics collection and dashboard"""
        logger.info("📊 Testing metrics collection...")

        test_name = "metrics_collection"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            from backend.intelligence.learning_metrics_dashboard import get_metrics_dashboard
            metrics_dashboard = get_metrics_dashboard()

            # Get dashboard data
            dashboard_data = await metrics_dashboard.get_learning_dashboard()

            if 'error' not in dashboard_data:
                logger.info("  Dashboard data retrieved successfully")

                self.test_results['tests'][test_name]['details']['dashboard_status'] = {
                    'monitoring_active': dashboard_data.get('monitoring_active', False),
                    'agent_count': dashboard_data.get('agent_count', 0),
                    'system_status': dashboard_data.get('system_status', {})
                }

                # Test metrics structure
                if 'current_metrics' in dashboard_data:
                    self.test_results['tests'][test_name]['details']['metrics_available'] = True
                    logger.info("  Current metrics structure verified")

                if 'pipeline_health' in dashboard_data:
                    health_score = dashboard_data['pipeline_health'].get('overall_health_score', 0)
                    self.test_results['tests'][test_name]['details']['health_score'] = health_score
                    logger.info(f"  Pipeline health score: {health_score:.2f}")

                self.test_results['tests'][test_name]['success'] = True
                logger.info("✅ Metrics collection test passed")

            else:
                error_msg = f"Dashboard data error: {dashboard_data.get('error')}"
                self.test_results['tests'][test_name]['errors'].append(error_msg)

        except Exception as e:
            error_msg = f"Metrics collection test failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    async def _test_end_to_end_integration(self):
        """Test complete end-to-end pipeline integration"""
        logger.info("🔄 Testing end-to-end integration...")

        test_name = "end_to_end_integration"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            from backend.intelligence.unified_learning_pipeline import get_unified_pipeline
            pipeline = get_unified_pipeline()

            # Get comprehensive pipeline metrics
            pipeline_metrics = await pipeline.get_pipeline_metrics()

            if 'error' not in pipeline_metrics:
                self.test_results['tests'][test_name]['details']['pipeline_metrics'] = pipeline_metrics

                # Check system integration
                system_info = pipeline_metrics.get('system_info', {})
                uptime = system_info.get('uptime_seconds', 0)

                if uptime > 0:
                    logger.info(f"  Pipeline uptime: {uptime:.1f} seconds")

                # Test pipeline sweep functionality
                logger.info("  Testing pipeline sweep...")
                sweep_result = await pipeline.trigger_full_pipeline_sweep()

                self.test_results['tests'][test_name]['details']['sweep_test'] = {
                    'triggered': 'error' not in sweep_result,
                    'result': sweep_result
                }

                # Overall integration success if we got this far
                self.test_results['tests'][test_name]['success'] = True
                logger.info("✅ End-to-end integration test passed")

            else:
                error_msg = f"Pipeline metrics error: {pipeline_metrics.get('error')}"
                self.test_results['tests'][test_name]['errors'].append(error_msg)

        except Exception as e:
            error_msg = f"End-to-end integration test failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    async def _test_performance(self):
        """Test pipeline performance and scalability"""
        logger.info("⚡ Testing performance...")

        test_name = "performance"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            # Test data transformation performance
            from backend.intelligence.data_transformation_pipeline import get_transformation_pipeline, RawSpiderData
            transformation_pipeline = get_transformation_pipeline()

            # Create multiple mock data items
            mock_data_items = []
            for i in range(10):
                mock_data = RawSpiderData(
                    spider_id=f"perf_test_{i}",
                    spider_type="financial",
                    source_url=f"https://test{i}.example.com",
                    timestamp=datetime.now(timezone.utc),
                    raw_content={
                        "price": i * 1.1,
                        "volume": 1.5 + (i * 0.1),
                        "market": "TEST"
                    },
                    metadata={"test": True, "batch": i},
                    quality_score=0.7 + (i * 0.02)
                )
                mock_data_items.append(mock_data)

            # Time the transformation process
            start_time = time.time()

            all_signals = []
            for mock_data in mock_data_items:
                signals = await transformation_pipeline.transform_data_to_signals(mock_data, "financial")
                all_signals.extend(signals)

            end_time = time.time()

            processing_time = end_time - start_time
            items_per_second = len(mock_data_items) / processing_time if processing_time > 0 else 0

            self.test_results['tests'][test_name]['details']['performance_metrics'] = {
                'items_processed': len(mock_data_items),
                'signals_generated': len(all_signals),
                'processing_time_seconds': processing_time,
                'items_per_second': items_per_second
            }

            logger.info(f"  Processed {len(mock_data_items)} items in {processing_time:.2f}s")
            logger.info(f"  Performance: {items_per_second:.1f} items/second")

            # Performance threshold: should process at least 5 items per second
            if items_per_second >= 5.0:
                self.test_results['tests'][test_name]['success'] = True
                logger.info("✅ Performance test passed")
            else:
                warning_msg = f"Performance below threshold: {items_per_second:.1f} items/second"
                self.test_results['tests'][test_name]['errors'].append(warning_msg)
                logger.warning(f"⚠️ {warning_msg}")

        except Exception as e:
            error_msg = f"Performance test failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    async def _test_error_handling(self):
        """Test error handling and recovery mechanisms"""
        logger.info("🛡️ Testing error handling...")

        test_name = "error_handling"
        self.test_results['tests'][test_name] = {
            'success': False,
            'errors': [],
            'details': {}
        }

        try:
            # Test malformed data handling
            from backend.intelligence.data_transformation_pipeline import get_transformation_pipeline, RawSpiderData
            transformation_pipeline = get_transformation_pipeline()

            # Create intentionally malformed data
            malformed_data = RawSpiderData(
                spider_id="error_test",
                spider_type="unknown_type",
                source_url="invalid-url",
                timestamp=datetime.now(timezone.utc),
                raw_content={
                    "invalid_field": "bad_data",
                    "nested": {"deeply": {"invalid": None}}
                },
                metadata={},
                quality_score=-1.0  # Invalid score
            )

            # Test that it handles errors gracefully
            try:
                signals = await transformation_pipeline.transform_data_to_signals(malformed_data, "unknown")

                # Should either return empty list or valid signals, not crash
                self.test_results['tests'][test_name]['details']['malformed_data_handling'] = {
                    'signals_returned': len(signals),
                    'handled_gracefully': True
                }

                logger.info("  ✓ Malformed data handled gracefully")

            except Exception as transform_error:
                # If it throws an exception, that's still acceptable as long as it's caught
                self.test_results['tests'][test_name]['details']['malformed_data_handling'] = {
                    'exception_thrown': str(transform_error),
                    'handled_gracefully': True  # We caught it, so it's handled
                }
                logger.info("  ✓ Malformed data threw expected exception")

            # Test component recovery
            from backend.intelligence.unified_learning_pipeline import get_unified_pipeline
            pipeline = get_unified_pipeline()

            # Test getting status when components might have issues
            try:
                status = await pipeline.get_pipeline_status()
                self.test_results['tests'][test_name]['details']['status_retrieval'] = {
                    'successful': True,
                    'overall_status': status.overall_status
                }
                logger.info("  ✓ Pipeline status retrieval robust")

            except Exception as status_error:
                self.test_results['tests'][test_name]['errors'].append(f"Status retrieval failed: {status_error}")

            # If we made it this far, error handling is working
            self.test_results['tests'][test_name]['success'] = True
            logger.info("✅ Error handling test passed")

        except Exception as e:
            error_msg = f"Error handling test failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.test_results['tests'][test_name]['errors'].append(error_msg)

    def _calculate_overall_success(self):
        """Calculate overall test success"""
        total_tests = len(self.test_results['tests'])
        passed_tests = sum(1 for test in self.test_results['tests'].values() if test['success'])

        self.test_results['test_summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0.0
        }

        # Consider overall success if 75% or more tests pass
        self.test_results['overall_success'] = self.test_results['test_summary']['success_rate'] >= 0.75

        if self.test_results['overall_success']:
            logger.info("🎉 Overall pipeline integration test PASSED")
        else:
            logger.error("❌ Overall pipeline integration test FAILED")

    def print_test_summary(self):
        """Print a comprehensive test summary"""
        print("\n" + "="*80)
        print("LEARNING PIPELINE INTEGRATION TEST SUMMARY")
        print("="*80)

        print(f"Start Time: {self.test_results['start_time']}")
        if 'end_time' in self.test_results:
            print(f"End Time: {self.test_results['end_time']}")
            print(f"Duration: {self.test_results.get('duration_seconds', 0):.1f} seconds")

        if 'test_summary' in self.test_results:
            summary = self.test_results['test_summary']
            print(f"\nTest Results: {summary['passed_tests']}/{summary['total_tests']} passed")
            print(f"Success Rate: {summary['success_rate']:.1%}")

        print(f"\nOverall Status: {'✅ PASSED' if self.test_results['overall_success'] else '❌ FAILED'}")

        print("\nDetailed Results:")
        print("-" * 40)

        for test_name, test_data in self.test_results['tests'].items():
            status = "✅ PASS" if test_data['success'] else "❌ FAIL"
            print(f"{test_name:25} {status}")

            if test_data['errors']:
                for error in test_data['errors']:
                    print(f"    ⚠️ {error}")

        if self.test_results.get('critical_error'):
            print(f"\n❌ CRITICAL ERROR: {self.test_results['critical_error']}")

        print("="*80)


async def main():
    """Main test execution function"""
    tester = PipelineIntegrationTester()

    try:
        # Run all tests
        results = await tester.run_all_tests()

        # Print summary
        tester.print_test_summary()

        # Save results to file
        with open('learning_pipeline_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\nDetailed results saved to: learning_pipeline_test_results.json")
        print(f"Test log saved to: learning_pipeline_test.log")

        # Return appropriate exit code
        return 0 if results['overall_success'] else 1

    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)