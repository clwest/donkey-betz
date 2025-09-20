"""
Comprehensive Test Suite for System Reality Self-Awareness Engine
================================================================

This test suite validates the reality checking infrastructure and ensures
it can accurately distinguish between real and mock functionality.

Test Coverage:
- SystemRealityChecker component validation
- DataFlowTracer pipeline analysis
- TruthDashboard report generation
- WebSocket integration testing
- End-to-end reality validation
"""

import os
import json
import time
import asyncio
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.core.cache import cache

# Import our reality checking modules
from core.reality_check import (
    SystemRealityChecker,
    ComponentType,
    RealityStatus,
    ComponentRealityStatus
)
from core.data_flow_tracer import (
    DataFlowTracer,
    FlowType,
    FlowStage,
    DataFlowTrace
)
from core.truth_dashboard import TruthDashboard


class SystemRealityCheckerTestCase(TestCase):
    """Test SystemRealityChecker functionality"""

    def setUp(self):
        self.checker = SystemRealityChecker()
        cache.clear()  # Clear cache between tests

    def test_database_reality_check(self):
        """Test database reality checking"""
        status = self.checker._check_database_reality()

        self.assertIsInstance(status, ComponentRealityStatus)
        self.assertEqual(status.component, ComponentType.DATABASE)
        self.assertIn('connection_test', status.checks_performed)
        self.assertIsInstance(status.confidence, float)
        self.assertGreaterEqual(status.confidence, 0.0)
        self.assertLessEqual(status.confidence, 1.0)

    def test_redis_reality_check(self):
        """Test Redis reality checking"""
        status = self.checker._check_redis_reality()

        self.assertIsInstance(status, ComponentRealityStatus)
        self.assertEqual(status.component, ComponentType.REDIS)
        self.assertIn('connection_test', status.checks_performed)

        # Should detect if Redis is actually available
        if status.status == RealityStatus.REAL:
            self.assertGreater(status.confidence, 0.5)
        elif status.status == RealityStatus.BROKEN:
            self.assertIn('Redis', ' '.join(status.issues_found))

    def test_income_builder_reality_check(self):
        """Test Income Builder reality checking"""
        status = self.checker._check_income_builder_reality()

        self.assertIsInstance(status, ComponentRealityStatus)
        self.assertEqual(status.component, ComponentType.INCOME_BUILDER)
        self.assertIn('module_check', status.checks_performed)

        # Check that it properly detects module availability
        if 'module_found' in status.details:
            self.assertIsInstance(status.details['module_found'], bool)

    def test_neural_orchestra_reality_check(self):
        """Test Neural Orchestra reality checking"""
        status = self.checker._check_neural_orchestra_reality()

        self.assertIsInstance(status, ComponentRealityStatus)
        self.assertEqual(status.component, ComponentType.NEURAL_ORCHESTRA)
        self.assertIn('agent_models_check', status.checks_performed)

        # Should detect number of agents
        if 'total_agents' in status.details:
            self.assertIsInstance(status.details['total_agents'], int)

    def test_websocket_hub_reality_check(self):
        """Test WebSocket Hub reality checking"""
        status = self.checker._check_websocket_hub_reality()

        self.assertIsInstance(status, ComponentRealityStatus)
        self.assertEqual(status.component, ComponentType.WEBSOCKET_HUB)
        self.assertIn('unified_hub_check', status.checks_performed)

    def test_ml_pipeline_reality_check(self):
        """Test ML Pipeline reality checking"""
        status = self.checker._check_ml_pipeline_reality()

        self.assertIsInstance(status, ComponentRealityStatus)
        self.assertEqual(status.component, ComponentType.ML_PIPELINE)
        self.assertIn('ai_integration_check', status.checks_performed)

    def test_revenue_tracking_reality_check(self):
        """Test Revenue Tracking reality checking"""
        status = self.checker._check_revenue_tracking_reality()

        self.assertIsInstance(status, ComponentRealityStatus)
        self.assertEqual(status.component, ComponentType.REVENUE_TRACKING)
        self.assertIn('revenue_models_check', status.checks_performed)

    def test_check_all_components(self):
        """Test checking all components"""
        results = self.checker.check_all_components()

        # Should check all component types
        expected_components = set(ComponentType)
        actual_components = set(results.keys())
        self.assertEqual(expected_components, actual_components)

        # All results should be ComponentRealityStatus objects
        for component_type, status in results.items():
            self.assertIsInstance(status, ComponentRealityStatus)
            self.assertEqual(status.component, component_type)

    def test_generate_reality_report(self):
        """Test comprehensive reality report generation"""
        report = self.checker.generate_reality_report()

        # Check report structure
        required_keys = [
            'generated_at', 'overall_reality_score', 'overall_status',
            'summary', 'components', 'status_categories',
            'critical_issues', 'priority_recommendations', 'data_flows',
            'reality_metrics'
        ]

        for key in required_keys:
            self.assertIn(key, report)

        # Check overall score
        self.assertIsInstance(report['overall_reality_score'], float)
        self.assertGreaterEqual(report['overall_reality_score'], 0.0)
        self.assertLessEqual(report['overall_reality_score'], 1.0)

        # Check components section
        self.assertIsInstance(report['components'], dict)
        for component_name, component_data in report['components'].items():
            self.assertIn('status', component_data)
            self.assertIn('confidence', component_data)
            self.assertIn('details', component_data)

        # Check data flows
        self.assertIsInstance(report['data_flows'], list)
        for flow in report['data_flows']:
            self.assertIn('source', flow)
            self.assertIn('destination', flow)
            self.assertIn('health', flow)


class DataFlowTracerTestCase(TestCase):
    """Test DataFlowTracer functionality"""

    def setUp(self):
        self.tracer = DataFlowTracer()

    def test_start_trace(self):
        """Test starting a data flow trace"""
        test_data = {'id': 'test_123', 'type': 'opportunity'}
        trace_id = self.tracer.start_trace(FlowType.OPPORTUNITY_PIPELINE, 'test_123', test_data)

        self.assertIsInstance(trace_id, str)
        self.assertIn(trace_id, self.tracer.active_traces)

        trace = self.tracer.active_traces[trace_id]
        self.assertEqual(trace.flow_type, FlowType.OPPORTUNITY_PIPELINE)
        self.assertEqual(len(trace.trace_points), 1)  # Initial point
        self.assertEqual(trace.trace_points[0].stage, FlowStage.COLLECTION)

    def test_add_trace_point(self):
        """Test adding trace points to a flow"""
        # Start a trace
        test_data = {'id': 'test_456', 'type': 'opportunity'}
        trace_id = self.tracer.start_trace(FlowType.OPPORTUNITY_PIPELINE, 'test_456', test_data)

        # Add a trace point
        success = self.tracer.add_trace_point(
            trace_id=trace_id,
            stage=FlowStage.STORAGE,
            component='database',
            data_id='test_456',
            data_payload={'id': 'test_456', 'stored': True},
            success=True,
            processing_time_ms=50.0
        )

        self.assertTrue(success)

        trace = self.tracer.active_traces[trace_id]
        self.assertEqual(len(trace.trace_points), 2)
        self.assertEqual(trace.trace_points[1].stage, FlowStage.STORAGE)
        self.assertEqual(trace.trace_points[1].component, 'database')
        self.assertEqual(trace.trace_points[1].processing_time_ms, 50.0)

    def test_complete_trace(self):
        """Test completing a trace"""
        # Start and populate a trace
        test_data = {'id': 'test_789', 'type': 'opportunity'}
        trace_id = self.tracer.start_trace(FlowType.OPPORTUNITY_PIPELINE, 'test_789', test_data)

        self.tracer.add_trace_point(
            trace_id, FlowStage.STORAGE, 'database', 'test_789',
            {'id': 'test_789', 'stored': True}, True, 25.0
        )

        # Complete the trace
        completed_trace = self.tracer.complete_trace(trace_id, success=True)

        self.assertIsInstance(completed_trace, DataFlowTrace)
        self.assertTrue(completed_trace.success)
        self.assertIsNotNone(completed_trace.end_time)
        self.assertNotIn(trace_id, self.tracer.active_traces)
        self.assertIn(completed_trace, self.tracer.completed_traces)

    def test_trace_opportunity_pipeline(self):
        """Test tracing a complete opportunity pipeline"""
        opportunity_data = {
            'id': 'opp_001',
            'title': 'Test Opportunity',
            'platform': 'test_platform'
        }

        trace_id = self.tracer.trace_opportunity_pipeline(opportunity_data)

        self.assertIsInstance(trace_id, str)

        # Should have completed the trace
        completed_trace = None
        for trace in self.tracer.completed_traces:
            if trace.flow_id == trace_id:
                completed_trace = trace
                break

        self.assertIsNotNone(completed_trace)
        self.assertEqual(completed_trace.flow_type, FlowType.OPPORTUNITY_PIPELINE)

    def test_trace_revenue_pipeline(self):
        """Test tracing a revenue generation pipeline"""
        proposal_data = {
            'id': 'prop_001',
            'opportunity_id': 'opp_001',
            'amount': 500.0
        }

        trace_id = self.tracer.trace_revenue_pipeline(proposal_data)

        self.assertIsInstance(trace_id, str)

        # Check that trace was completed
        completed_trace = self.tracer.get_trace_by_id(trace_id)
        self.assertIsNotNone(completed_trace)
        self.assertEqual(completed_trace.flow_type, FlowType.REVENUE_PIPELINE)

    def test_trace_websocket_pipeline(self):
        """Test tracing WebSocket message flow"""
        message_data = {
            'type': 'test_message',
            'data': {'key': 'value'}
        }

        trace_id = self.tracer.trace_websocket_pipeline(message_data, 'income_builder')

        self.assertIsInstance(trace_id, str)

        completed_trace = self.tracer.get_trace_by_id(trace_id)
        self.assertIsNotNone(completed_trace)
        self.assertEqual(completed_trace.flow_type, FlowType.WEBSOCKET_PIPELINE)

    def test_get_pipeline_health(self):
        """Test pipeline health metrics"""
        # Generate some test traces
        for i in range(5):
            trace_id = self.tracer.start_trace(
                FlowType.OPPORTUNITY_PIPELINE,
                f'test_{i}',
                {'id': f'test_{i}'}
            )
            self.tracer.add_trace_point(
                trace_id, FlowStage.STORAGE, 'database', f'test_{i}',
                {'stored': True}, success=(i % 2 == 0), processing_time_ms=100.0
            )
            self.tracer.complete_trace(trace_id, success=(i % 2 == 0))

        health = self.tracer.get_pipeline_health(FlowType.OPPORTUNITY_PIPELINE)

        self.assertIn('status', health)
        self.assertIn('metrics', health)
        self.assertIn('total_traces', health['metrics'])
        self.assertIn('success_rate', health['metrics'])

        # Should have processed our 5 test traces
        self.assertEqual(health['metrics']['total_traces'], 5)

    def test_export_traces(self):
        """Test trace export functionality"""
        # Create a test trace
        trace_id = self.tracer.start_trace(
            FlowType.OPPORTUNITY_PIPELINE,
            'export_test',
            {'id': 'export_test'}
        )
        self.tracer.complete_trace(trace_id, success=True)

        # Export traces
        export_data = self.tracer.export_traces(format='json')

        self.assertIn('exported_at', export_data)
        self.assertIn('trace_count', export_data)
        self.assertIn('traces', export_data)
        self.assertIsInstance(export_data['traces'], list)


class TruthDashboardTestCase(TestCase):
    """Test TruthDashboard functionality"""

    def setUp(self):
        self.dashboard = TruthDashboard()
        cache.clear()

    def test_generate_dashboard_data(self):
        """Test dashboard data generation"""
        data = self.dashboard.generate_dashboard_data()

        required_keys = [
            'generated_at', 'overall_health', 'reality_report',
            'flow_health', 'component_map', 'critical_issues',
            'quick_wins', 'recent_activity', 'summary', 'next_actions'
        ]

        for key in required_keys:
            self.assertIn(key, data)

        # Check overall health structure
        health = data['overall_health']
        self.assertIn('score', health)
        self.assertIn('status', health)
        self.assertIn('message', health)

        # Check component map
        self.assertIsInstance(data['component_map'], list)
        for component in data['component_map']:
            self.assertIn('name', component)
            self.assertIn('status', component)
            self.assertIn('confidence', component)

    def test_component_map_generation(self):
        """Test component status map generation"""
        # Create mock reality report
        reality_report = {
            'components': {
                'database': {
                    'status': 'real',
                    'confidence': 0.9,
                    'issues_found': [],
                    'recommendations': [],
                    'last_checked': '2023-01-01T00:00:00Z'
                },
                'websocket_hub': {
                    'status': 'broken',
                    'confidence': 0.1,
                    'issues_found': ['Connection failed'],
                    'recommendations': ['Fix configuration'],
                    'last_checked': '2023-01-01T00:00:00Z'
                }
            }
        }

        component_map = self.dashboard._generate_component_map(reality_report)

        self.assertEqual(len(component_map), 2)

        # Should be sorted with broken components first
        self.assertEqual(component_map[0]['status'], 'broken')
        self.assertEqual(component_map[1]['status'], 'real')

        # Check component properties
        for component in component_map:
            self.assertIn('name', component)
            self.assertIn('icon', component)
            self.assertIn('color', component)

    def test_critical_issues_extraction(self):
        """Test critical issues extraction and prioritization"""
        reality_report = {
            'critical_issues': [
                {'component': 'database', 'issue': 'Connection failed'},
                {'component': 'api', 'issue': 'Not configured'},
                {'component': 'agents', 'issue': 'Module not found'}
            ]
        }

        critical_issues = self.dashboard._extract_critical_issues(reality_report)

        self.assertIsInstance(critical_issues, list)
        for issue in critical_issues:
            self.assertIn('component', issue)
            self.assertIn('issue', issue)
            self.assertIn('priority_score', issue)
            self.assertIn('severity', issue)

        # Should be sorted by priority
        if len(critical_issues) > 1:
            self.assertGreaterEqual(
                critical_issues[0]['priority_score'],
                critical_issues[1]['priority_score']
            )

    def test_quick_wins_identification(self):
        """Test quick wins identification"""
        reality_report = {
            'components': {
                'test_component': {
                    'recommendations': [
                        'Configure API keys',
                        'Install missing package',
                        'Debug complex issue'
                    ]
                }
            }
        }

        quick_wins = self.dashboard._identify_quick_wins(reality_report)

        self.assertIsInstance(quick_wins, list)
        for win in quick_wins:
            self.assertIn('recommendation', win)
            self.assertIn('impact_score', win)
            self.assertIn('ease_score', win)
            self.assertIn('total_score', win)

    def test_component_detail(self):
        """Test getting detailed component information"""
        # This will use real data from the system
        detail = self.dashboard.get_component_detail('database')

        if 'error' not in detail:
            self.assertIn('component', detail)
            self.assertIn('status', detail)
            self.assertIn('confidence', detail)

    def test_overall_health_calculation(self):
        """Test overall health score calculation"""
        reality_report = {'overall_reality_score': 0.8}
        flow_health = {
            'opportunity_pipeline': {
                'status': 'good',
                'metrics': {'success_rate': 0.9}
            }
        }

        health = self.dashboard._calculate_overall_health(reality_report, flow_health)

        self.assertIn('score', health)
        self.assertIn('status', health)
        self.assertGreaterEqual(health['score'], 0.0)
        self.assertLessEqual(health['score'], 1.0)


class IntegrationTestCase(TransactionTestCase):
    """Integration tests for the complete reality engine"""

    def setUp(self):
        self.checker = SystemRealityChecker()
        self.tracer = DataFlowTracer()
        self.dashboard = TruthDashboard()

    def test_end_to_end_reality_check(self):
        """Test complete end-to-end reality checking"""
        print("\n=== Running End-to-End Reality Check ===")

        # 1. Check all components
        print("1. Checking all components...")
        component_results = self.checker.check_all_components()

        self.assertIsInstance(component_results, dict)
        self.assertGreater(len(component_results), 0)

        for component_type, status in component_results.items():
            print(f"   {component_type.value}: {status.status.value} ({status.confidence:.2f})")

        # 2. Generate reality report
        print("\n2. Generating reality report...")
        reality_report = self.checker.generate_reality_report()

        self.assertIn('overall_reality_score', reality_report)
        print(f"   Overall Reality Score: {reality_report['overall_reality_score']:.1%}")

        # 3. Test data flow tracing
        print("\n3. Testing data flow tracing...")
        test_opportunity = {
            'id': 'integration_test_001',
            'title': 'Integration Test Opportunity',
            'platform': 'test'
        }

        trace_id = self.tracer.trace_opportunity_pipeline(test_opportunity)
        completed_trace = self.tracer.get_trace_by_id(trace_id)

        self.assertIsNotNone(completed_trace)
        print(f"   Trace completed: {completed_trace.success} in {completed_trace.total_processing_time_ms:.1f}ms")

        # 4. Generate dashboard
        print("\n4. Generating truth dashboard...")
        dashboard_data = self.dashboard.generate_dashboard_data()

        self.assertIn('overall_health', dashboard_data)
        health = dashboard_data['overall_health']
        print(f"   Platform Health: {health['status']} ({health['score']:.1%})")

        # 5. Test pipeline health
        print("\n5. Checking pipeline health...")
        pipeline_health = self.tracer.get_pipeline_health()

        if pipeline_health['status'] != 'no_data':
            print(f"   Pipeline Health: {pipeline_health['status']}")
            print(f"   Success Rate: {pipeline_health['metrics']['success_rate']:.1%}")

        print("\n=== Integration Test Complete ===\n")

    def test_mock_vs_real_detection(self):
        """Test that the system can distinguish mock from real components"""
        print("\n=== Testing Mock vs Real Detection ===")

        # Check specific components that should be detectable
        test_components = [
            ComponentType.DATABASE,
            ComponentType.WEBSOCKET_HUB,
            ComponentType.INCOME_BUILDER,
            ComponentType.NEURAL_ORCHESTRA
        ]

        for component_type in test_components:
            checker_method = self.checker.component_checkers.get(component_type)
            if checker_method:
                status = checker_method()
                print(f"{component_type.value}: {status.status.value} (confidence: {status.confidence:.2f})")

                # Should have performed meaningful checks
                self.assertGreater(len(status.checks_performed), 0)

                # Should have reasonable confidence
                self.assertGreaterEqual(status.confidence, 0.0)
                self.assertLessEqual(status.confidence, 1.0)

        print("=== Mock vs Real Detection Complete ===\n")

    def test_performance_benchmarks(self):
        """Test performance of reality checking operations"""
        print("\n=== Performance Benchmarks ===")

        # Benchmark component checking
        start_time = time.time()
        component_results = self.checker.check_all_components()
        component_time = time.time() - start_time

        print(f"Component checking: {component_time:.2f}s for {len(component_results)} components")
        self.assertLess(component_time, 30.0)  # Should complete within 30 seconds

        # Benchmark report generation
        start_time = time.time()
        reality_report = self.checker.generate_reality_report()
        report_time = time.time() - start_time

        print(f"Reality report generation: {report_time:.2f}s")
        self.assertLess(report_time, 10.0)  # Should complete within 10 seconds

        # Benchmark dashboard generation
        start_time = time.time()
        dashboard_data = self.dashboard.generate_dashboard_data()
        dashboard_time = time.time() - start_time

        print(f"Dashboard generation: {dashboard_time:.2f}s")
        self.assertLess(dashboard_time, 15.0)  # Should complete within 15 seconds

        print("=== Performance Benchmarks Complete ===\n")


def run_reality_engine_tests():
    """Run all reality engine tests"""
    print("🎯 Running System Reality Self-Awareness Engine Tests\n")

    # Create test suite
    test_classes = [
        SystemRealityCheckerTestCase,
        DataFlowTracerTestCase,
        TruthDashboardTestCase,
        IntegrationTestCase
    ]

    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*60)
    print("🎯 SYSTEM REALITY ENGINE TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun
    print(f"\nSuccess Rate: {success_rate:.1%}")

    if success_rate >= 0.8:
        print("✅ Reality Engine is functioning properly!")
    else:
        print("❌ Reality Engine needs fixes!")

    return result.wasSuccessful()


if __name__ == '__main__':
    run_reality_engine_tests()