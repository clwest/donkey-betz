#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Executes all cross-system workflow tests and generates unified report
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime

# Add project path and setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

# Import test modules
from test_cross_system_workflows import CrossSystemWorkflowTester
from test_workflow_scenarios import WorkflowScenarioTester
from test_websocket_agent_integration import WebSocketAgentIntegrationTester

# Import Django components for database verification
from django.db import connection
from agents.models import UnifiedAgentTemplate, AgentRegistry
from sports.models import League, Team, Game, Sportsbook
from content.models import Document


class ComprehensiveTestRunner:
    """Orchestrates all test suites and generates unified report"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.test_suite_results = {}
        self.unified_report = {}
        
    async def verify_system_readiness(self):
        """Verify system components are ready for testing"""
        print("🔍 Verifying system readiness...")
        
        readiness_checks = {
            "database_connection": False,
            "agent_registry_exists": False,
            "sports_agents_registered": False,
            "test_data_accessible": False
        }
        
        try:
            from asgiref.sync import sync_to_async
            
            # Database connection
            def check_database():
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
            readiness_checks["database_connection"] = await sync_to_async(check_database)()
            
            # Agent registry
            def check_registry():
                return AgentRegistry.objects.filter(
                    registry_name="unified_agent_registry"
                ).exists()
            readiness_checks["agent_registry_exists"] = await sync_to_async(check_registry)()
            
            # Sports agents
            def check_sports_agents():
                return UnifiedAgentTemplate.objects.filter(
                    domain_tags__contains=["sports"],
                    is_active=True
                ).count()
            sports_agents = await sync_to_async(check_sports_agents)()
            if sports_agents > 0:
                readiness_checks["sports_agents_registered"] = True
                print(f"   Found {sports_agents} active sports agents")
            
            # Test data accessibility
            def check_test_data():
                leagues = League.objects.count()
                teams = Team.objects.count()
                return leagues > 0 or teams > 0
            readiness_checks["test_data_accessible"] = await sync_to_async(check_test_data)()
            
        except Exception as e:
            print(f"   ⚠️  System readiness check error: {e}")
        
        # Report readiness
        ready_count = sum(readiness_checks.values())
        total_checks = len(readiness_checks)
        
        print(f"   System Readiness: {ready_count}/{total_checks} checks passed")
        for check, status in readiness_checks.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {check.replace('_', ' ').title()}")
        
        if ready_count < total_checks:
            print("\n⚠️  Some readiness checks failed. Tests may have limited functionality.")
            print("Consider running: python manage.py migrate && python manage.py register_sports_agents")
        
        return readiness_checks, ready_count == total_checks
    
    async def run_all_test_suites(self):
        """Execute all test suites"""
        print("\n🚀 Starting Comprehensive Cross-System Workflow Testing...")
        print("="*80)
        
        self.start_time = time.time()
        
        # Test Suite 1: Core Cross-System Workflows
        print("\n📋 Test Suite 1: Core Cross-System Workflows")
        try:
            from asgiref.sync import sync_to_async
            
            workflow_tester = CrossSystemWorkflowTester()
            await sync_to_async(workflow_tester.setup_test_data)()
            
            # Run all workflow tests
            await workflow_tester.test_agent_discovery_and_routing()
            await workflow_tester.test_sports_betting_orchestration()
            await workflow_tester.test_content_generation_with_betting_data()
            await workflow_tester.test_arbitrage_detection_workflow()
            await workflow_tester.test_cross_domain_workflow_best_opportunities()
            await workflow_tester.test_websocket_integration()
            await workflow_tester.test_performance_benchmarks()
            
            self.test_suite_results['core_workflows'] = workflow_tester.generate_comprehensive_report()
            
        except Exception as e:
            print(f"❌ Core workflows test suite failed: {e}")
            self.test_suite_results['core_workflows'] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Test Suite 2: Specific Workflow Scenarios
        print("\n🎯 Test Suite 2: Specific Workflow Scenarios")
        try:
            from asgiref.sync import sync_to_async
            
            scenario_tester = WorkflowScenarioTester()
            
            # Run scenario tests
            await scenario_tester.scenario_1_generate_article_best_opportunities()
            await scenario_tester.scenario_2_analyze_team_performance_predictive_content()
            await scenario_tester.scenario_3_generate_betting_strategy_guide()
            await scenario_tester.scenario_4_personal_assistant_orchestration()
            
            self.test_suite_results['workflow_scenarios'] = scenario_tester.generate_scenario_report()
            
        except Exception as e:
            print(f"❌ Workflow scenarios test suite failed: {e}")
            self.test_suite_results['workflow_scenarios'] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Test Suite 3: WebSocket Integration
        print("\n🌐 Test Suite 3: WebSocket Agent Integration")
        try:
            websocket_tester = WebSocketAgentIntegrationTester()
            
            await websocket_tester.setup_test_environment()
            await websocket_tester.test_agent_execution_websocket_updates()
            await websocket_tester.test_real_time_sports_data_updates()
            await websocket_tester.test_multi_agent_coordination_websocket()
            await websocket_tester.test_content_generation_websocket_stream()
            
            self.test_suite_results['websocket_integration'] = websocket_tester.generate_websocket_test_report()
            
        except Exception as e:
            print(f"❌ WebSocket integration test suite failed: {e}")
            self.test_suite_results['websocket_integration'] = {
                "status": "failed",
                "error": str(e)
            }
        
        self.end_time = time.time()
    
    def generate_unified_report(self):
        """Generate comprehensive unified test report"""
        total_duration = self.end_time - self.start_time
        
        # Calculate overall statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        for suite_name, suite_result in self.test_suite_results.items():
            if isinstance(suite_result, dict) and 'summary' in suite_result:
                total_tests += suite_result['summary'].get('total_tests', 0)
                total_passed += suite_result['summary'].get('passed_tests', 0)
                total_failed += suite_result['summary'].get('failed_tests', 0)
            elif isinstance(suite_result, dict):
                # Handle different result structures
                if 'total_tests' in suite_result:
                    total_tests += suite_result['total_tests']
                    total_passed += suite_result.get('passed', 0)
                    total_failed += suite_result.get('failed', 0)
                elif 'total_scenarios' in suite_result:
                    total_tests += suite_result['total_scenarios']
                    total_passed += suite_result.get('passed', 0)
                    total_failed += suite_result.get('failed', 0)
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Working cross-domain workflows summary
        working_workflows = []
        integration_issues = []
        
        for suite_name, suite_result in self.test_suite_results.items():
            if isinstance(suite_result, dict) and suite_result.get('status') != 'failed':
                if 'working_workflows' in suite_result:
                    working_workflows.extend(suite_result['working_workflows'])
                
                # Check for specific workflow successes
                if 'test_results' in suite_result:
                    for test in suite_result['test_results']:
                        if test.get('status') == 'passed' and 'workflow' in test.get('test', ''):
                            working_workflows.append(test['test'].replace('_', ' ').title())
                
                if 'detailed_results' in suite_result:
                    for result in suite_result['detailed_results']:
                        if result.get('status') == 'PASSED':
                            working_workflows.append(result['scenario'].replace('_', ' ').title())
                        elif result.get('status') == 'FAILED':
                            integration_issues.append({
                                "workflow": result['scenario'].replace('_', ' ').title(),
                                "error": result.get('error', 'Unknown error')
                            })
        
        # Performance metrics summary
        all_performance_metrics = {}
        for suite_name, suite_result in self.test_suite_results.items():
            if isinstance(suite_result, dict) and 'performance_metrics' in suite_result:
                for metric, value in suite_result['performance_metrics'].items():
                    all_performance_metrics[f"{suite_name}_{metric}"] = value
        
        # Generate unified report
        self.unified_report = {
            "test_execution_summary": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "total_duration_seconds": total_duration,
                "test_suites_executed": len(self.test_suite_results)
            },
            "overall_results": {
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "success_rate_percentage": overall_success_rate
            },
            "cross_domain_workflows": {
                "working_workflows": list(set(working_workflows)),
                "total_working": len(set(working_workflows)),
                "integration_issues": integration_issues
            },
            "performance_metrics": all_performance_metrics,
            "test_suite_details": self.test_suite_results,
            "system_capabilities": {
                "agent_discovery_and_routing": self._check_capability('agent_discovery'),
                "sports_data_integration": self._check_capability('sports'),
                "content_generation_with_analytics": self._check_capability('content'),
                "websocket_real_time_updates": self._check_capability('websocket'),
                "multi_agent_orchestration": self._check_capability('orchestration'),
                "cross_system_coordination": self._check_capability('coordination')
            },
            "recommendations": self._generate_recommendations()
        }
        
        return self.unified_report
    
    def _check_capability(self, capability_type):
        """Check if specific capability is working"""
        for suite_result in self.test_suite_results.values():
            if isinstance(suite_result, dict):
                if 'test_results' in suite_result:
                    for test in suite_result['test_results']:
                        if (capability_type in test.get('test', '') and 
                            test.get('status') == 'passed'):
                            return True
                
                if 'detailed_results' in suite_result:
                    for result in suite_result['detailed_results']:
                        if (capability_type in result.get('scenario', '') and 
                            result.get('status') == 'PASSED'):
                            return True
        
        return False
    
    def _generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check overall success rate - handle missing key gracefully
        success_rate = self.unified_report.get('overall_results', {}).get('success_rate_percentage', 0)
        if success_rate >= 90:
            recommendations.append("Excellent test results - system ready for production deployment")
        elif success_rate >= 75:
            recommendations.append("Good test results - address failed tests before production")
        else:
            recommendations.append("Multiple test failures - significant work needed before production")
        
        # Check for specific issues
        system_capabilities = self.unified_report.get('system_capabilities', {})
        if not system_capabilities.get('agent_discovery_and_routing', False):
            recommendations.append("Agent discovery system needs attention - verify agent registration")
        
        if not system_capabilities.get('websocket_real_time_updates', False):
            recommendations.append("WebSocket integration issues - check server configuration")
        
        cross_domain_workflows = self.unified_report.get('cross_domain_workflows', {})
        if len(cross_domain_workflows.get('integration_issues', [])) > 0:
            recommendations.append("Cross-domain workflow issues detected - review agent orchestration")
        
        # Performance recommendations
        performance_metrics = self.unified_report.get('performance_metrics', {})
        avg_performance = sum(performance_metrics.values()) / len(performance_metrics) if performance_metrics else 0
        if avg_performance > 10:
            recommendations.append("Performance optimization needed - workflows taking >10s average")
        
        if not recommendations:
            recommendations.append("All systems operational - consider implementing continuous testing")
        
        return recommendations
    
    def print_unified_report(self):
        """Print comprehensive unified report"""
        print("\n" + "="*100)
        print("📊 UNIFIED CROSS-SYSTEM WORKFLOW TEST REPORT")
        print("="*100)
        
        # Execution Summary
        print(f"\n🕒 EXECUTION SUMMARY:")
        print(f"   Start Time: {self.unified_report['test_execution_summary']['start_time']}")
        print(f"   End Time: {self.unified_report['test_execution_summary']['end_time']}")
        print(f"   Total Duration: {self.unified_report['test_execution_summary']['total_duration_seconds']:.1f} seconds")
        print(f"   Test Suites: {self.unified_report['test_execution_summary']['test_suites_executed']}")
        
        # Overall Results
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {self.unified_report['overall_results']['total_tests']}")
        print(f"   Passed: {self.unified_report['overall_results']['passed_tests']} ✅")
        print(f"   Failed: {self.unified_report['overall_results']['failed_tests']} ❌")
        print(f"   Success Rate: {self.unified_report['overall_results']['success_rate_percentage']:.1f}%")
        
        # Working Cross-Domain Workflows
        print(f"\n✅ WORKING CROSS-DOMAIN WORKFLOWS ({self.unified_report['cross_domain_workflows']['total_working']}):")
        for workflow in self.unified_report['cross_domain_workflows']['working_workflows']:
            print(f"   • {workflow}")
        
        # System Capabilities
        print(f"\n🔧 SYSTEM CAPABILITIES:")
        for capability, status in self.unified_report['system_capabilities'].items():
            status_icon = "✅" if status else "❌"
            capability_name = capability.replace('_', ' ').title()
            print(f"   {status_icon} {capability_name}")
        
        # Performance Metrics
        print(f"\n⚡ PERFORMANCE METRICS:")
        for metric, value in self.unified_report['performance_metrics'].items():
            metric_name = metric.replace('_', ' ').title()
            print(f"   {metric_name}: {value:.3f}s")
        
        # Integration Issues
        if self.unified_report['cross_domain_workflows']['integration_issues']:
            print(f"\n⚠️  INTEGRATION ISSUES:")
            for issue in self.unified_report['cross_domain_workflows']['integration_issues']:
                print(f"   • {issue['workflow']}: {issue['error']}")
        
        # Test Suite Breakdown
        print(f"\n📋 TEST SUITE BREAKDOWN:")
        for suite_name, suite_result in self.test_suite_results.items():
            suite_display_name = suite_name.replace('_', ' ').title()
            if isinstance(suite_result, dict) and suite_result.get('status') == 'failed':
                print(f"   ❌ {suite_display_name}: FAILED ({suite_result.get('error', 'Unknown error')})")
            else:
                success_rate = 0
                if isinstance(suite_result, dict):
                    if 'summary' in suite_result and 'success_rate' in suite_result['summary']:
                        success_rate = suite_result['summary']['success_rate']
                    elif 'success_rate' in suite_result:
                        success_rate = suite_result['success_rate']
                
                status_icon = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                print(f"   {status_icon} {suite_display_name}: {success_rate:.1f}% success rate")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        for recommendation in self.unified_report['recommendations']:
            print(f"   • {recommendation}")
        
        # Example Workflow Results
        print(f"\n🌟 EXAMPLE SUCCESSFUL WORKFLOWS:")
        example_workflows = [
            "Generate article about today's best betting opportunities",
            "Analyze team performance and create predictive content", 
            "Generate betting strategy guide using historical data",
            "Personal Assistant orchestrates complex multi-agent workflow"
        ]
        
        for workflow in example_workflows:
            if any(workflow.lower() in w.lower() for w in self.unified_report['cross_domain_workflows']['working_workflows']):
                print(f"   ✅ {workflow}")
            else:
                print(f"   ❌ {workflow}")
        
        print("\n" + "="*100)
    
    def save_reports(self):
        """Save all reports to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save unified report
        with open(f'unified_test_report_{timestamp}.json', 'w') as f:
            json.dump(self.unified_report, f, indent=2, default=str)
        
        # Save individual test suite reports
        for suite_name, suite_result in self.test_suite_results.items():
            with open(f'{suite_name}_report_{timestamp}.json', 'w') as f:
                json.dump(suite_result, f, indent=2, default=str)
        
        print(f"\n📄 All reports saved with timestamp: {timestamp}")
        print(f"   • unified_test_report_{timestamp}.json")
        for suite_name in self.test_suite_results.keys():
            print(f"   • {suite_name}_report_{timestamp}.json")


async def main():
    """Main test execution"""
    runner = ComprehensiveTestRunner()
    
    # Verify system readiness
    readiness_checks, fully_ready = await runner.verify_system_readiness()
    
    if not fully_ready:
        print("\n⚠️  Continuing with limited system readiness...")
    
    # Run all test suites
    await runner.run_all_test_suites()
    
    # Generate and display unified report
    unified_report = runner.generate_unified_report()
    runner.print_unified_report()
    
    # Save all reports
    runner.save_reports()
    
    # Return summary for any calling code
    return {
        "success_rate": unified_report['overall_results']['success_rate_percentage'],
        "total_tests": unified_report['overall_results']['total_tests'],
        "working_workflows": unified_report['cross_domain_workflows']['total_working'],
        "fully_ready": fully_ready
    }


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print(f"\n🏁 Test execution completed!")
        print(f"   Overall Success Rate: {result['success_rate']:.1f}%")
        print(f"   Working Cross-Domain Workflows: {result['working_workflows']}")
        
        # Exit with appropriate code
        exit_code = 0 if result['success_rate'] >= 80 else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚡ Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)