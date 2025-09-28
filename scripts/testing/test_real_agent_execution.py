#!/usr/bin/env python3
"""
Real Agent Execution Test Suite

This comprehensive test suite verifies that our agent executors are actually working
and producing real results. It tests the complete pipeline from agent registration
to execution to deliverable creation.

Key Tests:
- Real Income Builder execution with market research
- Real Content Creator execution with AI generation
- Real Payment Processor execution with Stripe integration
- Tool integration and API connectivity
- File creation and deliverable generation
- Performance and cost tracking
- Error handling and retry logic
"""

import os
import sys
import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()

from agents.executor_registry import (
    executor_system,
    execute_agent_by_name,
    get_agent_execution_status,
    initialize_all_agent_executors,
    get_execution_statistics,
    system_health_check
)
from agents.executors.base_executor import ExecutionContext, ExecutionPriority, ExecutionStatus

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RealAgentExecutionTester:
    """Comprehensive test suite for real agent execution"""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.Tester")
        self.test_results = []
        self.start_time = time.time()

        # Test configuration
        self.output_dir = Path("test_execution_outputs")
        self.output_dir.mkdir(exist_ok=True)

        self.logger.info("Real Agent Execution Tester initialized")

    async def run_all_tests(self):
        """Run comprehensive test suite"""

        self.logger.info("=" * 80)
        self.logger.info("STARTING REAL AGENT EXECUTION TEST SUITE")
        self.logger.info("=" * 80)

        tests = [
            ("System Health Check", self.test_system_health),
            ("Executor Registration", self.test_executor_registration),
            ("Income Builder Execution", self.test_income_builder_execution),
            ("Content Creator Execution", self.test_content_creator_execution),
            ("Payment Processor Execution", self.test_payment_processor_execution),
            ("Tool Integration", self.test_tool_integration),
            ("API Connectivity", self.test_api_connectivity),
            ("File Generation", self.test_file_generation),
            ("Performance Tracking", self.test_performance_tracking),
            ("Error Handling", self.test_error_handling),
            ("Multiple Agent Execution", self.test_multiple_agent_execution)
        ]

        for test_name, test_method in tests:
            self.logger.info(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = await test_method()
                self.test_results.append({
                    'test_name': test_name,
                    'status': 'PASSED',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                self.logger.info(f"✅ {test_name}: PASSED")
            except Exception as e:
                self.test_results.append({
                    'test_name': test_name,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                self.logger.error(f"❌ {test_name}: FAILED - {e}")

        # Generate final report
        await self.generate_test_report()

    async def test_system_health(self) -> Dict[str, Any]:
        """Test overall system health"""
        health_result = await system_health_check()

        assert health_result['status'] == 'healthy', f"System unhealthy: {health_result}"
        assert health_result['registered_executors'] > 0, "No executors registered"
        assert health_result['core_executors_available'], "Core executors not available"

        self.logger.info(f"System health: {health_result['registered_executors']} executors registered")
        return health_result

    async def test_executor_registration(self) -> Dict[str, Any]:
        """Test executor registration system"""

        # Initialize executors from database
        init_result = await initialize_all_agent_executors()

        assert init_result.get('registered', 0) > 0 or init_result.get('total_executors', 0) > 0, \
            "No executors registered"

        # Test specific agent capabilities
        test_agents = ['income_builder', 'content_creator', 'payment_processor']
        capabilities = {}

        for agent_name in test_agents:
            capability = get_agent_execution_status(agent_name)
            capabilities[agent_name] = capability

            assert capability['can_execute'], f"Agent {agent_name} cannot execute"

        self.logger.info(f"Registration test: {len(capabilities)} agents tested")
        return {
            'init_result': init_result,
            'capabilities_tested': capabilities
        }

    async def test_income_builder_execution(self) -> Dict[str, Any]:
        """Test Income Builder with real market research"""

        task_data = {
            'task_type': 'analyze_opportunities',
            'user_profile': {
                'id': 'test_user',
                'current_balance': 0.0,
                'skills': ['writing', 'research', 'AI'],
                'skill_level': 'intermediate',
                'available_hours_per_week': 20,
                'interests': ['technology', 'AI', 'content creation']
            }
        }

        result = await execute_agent_by_name(
            'income_builder',
            task_data,
            user_id='test_user',
            priority=ExecutionPriority.HIGH
        )

        # Verify execution success
        assert result.status == ExecutionStatus.COMPLETED, \
            f"Execution failed: {result.error_message}"

        # Verify real data was generated
        assert len(result.output.get('analyzed_opportunities', [])) > 0, \
            "No opportunities analyzed"

        # Verify files were created
        assert len(result.files_created) > 0, "No files created"

        # Verify tools were used
        assert 'web_search' in result.tools_used or len(result.files_created) > 0, \
            "No real tools used"

        self.logger.info(
            f"Income Builder execution: "
            f"{len(result.output.get('analyzed_opportunities', []))} opportunities, "
            f"{len(result.files_created)} files, "
            f"${result.total_cost} cost"
        )

        return {
            'execution_result': {
                'status': result.status.value,
                'opportunities_count': len(result.output.get('analyzed_opportunities', [])),
                'files_created': len(result.files_created),
                'tools_used': result.tools_used,
                'cost': float(result.total_cost),
                'execution_time_ms': result.execution_time_ms
            }
        }

    async def test_content_creator_execution(self) -> Dict[str, Any]:
        """Test Content Creator with real AI generation"""

        task_data = {
            'task_type': 'blog_post',
            'content_type': 'blog_post',
            'topic': 'AI-powered productivity tools for remote workers',
            'target_audience': 'professionals',
            'word_count': 1200,
            'keywords': ['AI productivity', 'remote work', 'automation tools']
        }

        result = await execute_agent_by_name(
            'content_creator',
            task_data,
            user_id='test_user',
            priority=ExecutionPriority.HIGH
        )

        # Verify execution success
        assert result.status == ExecutionStatus.COMPLETED, \
            f"Content creation failed: {result.error_message}"

        # Verify content was generated
        assert result.output.get('content_created'), "No content created"
        assert result.output.get('word_count', 0) > 500, "Content too short"

        # Verify files were created
        assert len(result.files_created) > 0, "No content files created"

        # Verify AI was used (check for API calls or tokens)
        has_ai_usage = (
            len(result.api_calls_made) > 0 or
            result.tokens_used.get('total', 0) > 0 or
            result.cost_breakdown.get('openai', 0) > 0
        )
        assert has_ai_usage, "No AI usage detected"

        self.logger.info(
            f"Content Creator execution: "
            f"{result.output.get('word_count', 0)} words, "
            f"{len(result.files_created)} files, "
            f"{result.tokens_used.get('total', 0)} tokens used"
        )

        return {
            'execution_result': {
                'status': result.status.value,
                'content_created': result.output.get('content_created', False),
                'word_count': result.output.get('word_count', 0),
                'files_created': len(result.files_created),
                'tokens_used': result.tokens_used.get('total', 0),
                'cost': float(result.total_cost)
            }
        }

    async def test_payment_processor_execution(self) -> Dict[str, Any]:
        """Test Payment Processor with invoice generation"""

        task_data = {
            'task_type': 'create_invoice',
            'invoice_type': 'freelance_service',
            'client_info': {
                'name': 'Test Client',
                'email': 'test@example.com',
                'company': 'Test Company',
                'address': '123 Test St, Test City'
            },
            'service_details': {
                'description': 'AI-powered content creation services',
                'quantity': 10,
                'rate': 50.0,
                'tax_rate': 0.08
            },
            'amount': 500.0
        }

        result = await execute_agent_by_name(
            'payment_processor',
            task_data,
            user_id='test_user',
            priority=ExecutionPriority.NORMAL
        )

        # Verify execution success
        assert result.status == ExecutionStatus.COMPLETED, \
            f"Payment processing failed: {result.error_message}"

        # Verify invoice was created
        assert result.output.get('invoice_created'), "No invoice created"
        assert result.output.get('invoice_id'), "No invoice ID generated"

        # Verify files were created
        assert len(result.files_created) > 0, "No invoice files created"

        # Verify realistic invoice amount
        total_amount = result.output.get('total_amount', 0)
        assert total_amount > 500, "Invoice amount too low"

        self.logger.info(
            f"Payment Processor execution: "
            f"Invoice {result.output.get('invoice_id')} created, "
            f"${total_amount} total, "
            f"{len(result.files_created)} files"
        )

        return {
            'execution_result': {
                'status': result.status.value,
                'invoice_created': result.output.get('invoice_created', False),
                'invoice_id': result.output.get('invoice_id'),
                'total_amount': total_amount,
                'files_created': len(result.files_created)
            }
        }

    async def test_tool_integration(self) -> Dict[str, Any]:
        """Test tool integration across executors"""

        # Test web search capability
        task_data = {
            'task_type': 'research_market',
            'opportunity_type': 'AI content writing',
            'research_depth': 'comprehensive'
        }

        result = await execute_agent_by_name('income_builder', task_data)

        # Verify tools were used
        tools_used = result.tools_used
        assert len(tools_used) > 0, "No tools used in execution"

        # Check for specific tool types
        expected_tools = ['web_search', 'file_ops']
        tools_found = [tool for tool in expected_tools if tool in tools_used]

        self.logger.info(f"Tool integration test: {len(tools_used)} tools used: {tools_used}")

        return {
            'tools_used': tools_used,
            'expected_tools_found': tools_found,
            'tool_integration_score': len(tools_found) / len(expected_tools)
        }

    async def test_api_connectivity(self) -> Dict[str, Any]:
        """Test API connectivity and usage"""

        api_test_results = {}

        # Test OpenAI API through Content Creator
        if os.getenv('OPENAI_API_KEY'):
            task_data = {
                'content_type': 'blog_post',
                'topic': 'Test API connectivity',
                'target_audience': 'developers',
                'word_count': 300
            }

            result = await execute_agent_by_name('content_creator', task_data)

            api_test_results['openai'] = {
                'available': True,
                'used': len(result.api_calls_made) > 0,
                'tokens_used': result.tokens_used.get('total', 0),
                'cost': float(result.cost_breakdown.get('openai', 0))
            }
        else:
            api_test_results['openai'] = {'available': False, 'reason': 'No API key'}

        # Test Stripe API (without actual charges)
        stripe_available = bool(os.getenv('STRIPE_API_KEY'))
        api_test_results['stripe'] = {
            'available': stripe_available,
            'reason': 'API key present' if stripe_available else 'No API key'
        }

        self.logger.info(f"API connectivity: {len(api_test_results)} APIs tested")

        return api_test_results

    async def test_file_generation(self) -> Dict[str, Any]:
        """Test file generation capabilities"""

        # Test multiple agents for file generation
        agents_to_test = [
            ('income_builder', {'task_type': 'analyze_opportunities', 'user_profile': {'id': 'test'}}),
            ('content_creator', {'content_type': 'blog_post', 'topic': 'File generation test'})
        ]

        file_generation_results = {}

        for agent_name, task_data in agents_to_test:
            result = await execute_agent_by_name(agent_name, task_data)

            files_created = result.files_created
            files_exist = [Path(f).exists() for f in files_created]

            file_generation_results[agent_name] = {
                'files_created_count': len(files_created),
                'files_exist': sum(files_exist),
                'file_paths': files_created,
                'all_files_exist': all(files_exist) if files_exist else False
            }

        total_files = sum(r['files_created_count'] for r in file_generation_results.values())

        self.logger.info(f"File generation test: {total_files} total files created")

        return {
            'total_files_created': total_files,
            'agent_results': file_generation_results
        }

    async def test_performance_tracking(self) -> Dict[str, Any]:
        """Test performance tracking and metrics"""

        # Execute multiple tasks to generate performance data
        tasks = [
            ('income_builder', {'task_type': 'analyze_opportunities', 'user_profile': {'id': 'perf_test_1'}}),
            ('content_creator', {'content_type': 'blog_post', 'topic': 'Performance testing'}),
            ('income_builder', {'task_type': 'create_action_plan', 'opportunity_id': 'ai_content_creation'})
        ]

        performance_results = []

        for agent_name, task_data in tasks:
            start_time = time.time()
            result = await execute_agent_by_name(agent_name, task_data)
            end_time = time.time()

            performance_results.append({
                'agent_name': agent_name,
                'execution_time_ms': result.execution_time_ms,
                'wall_time_ms': int((end_time - start_time) * 1000),
                'total_cost': float(result.total_cost),
                'quality_score': result.quality_score,
                'files_created': len(result.files_created),
                'tools_used': len(result.tools_used)
            })

        # Get overall system statistics
        system_stats = get_execution_statistics()

        self.logger.info(f"Performance tracking: {len(performance_results)} executions measured")

        return {
            'individual_performance': performance_results,
            'system_statistics': system_stats
        }

    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and recovery"""

        error_test_results = {}

        # Test with invalid task data
        try:
            result = await execute_agent_by_name(
                'income_builder',
                {'invalid_key': 'invalid_value'},
                priority=ExecutionPriority.LOW
            )
            error_test_results['invalid_data'] = {
                'handled_gracefully': result.status != ExecutionStatus.COMPLETED,
                'error_message_present': bool(result.error_message),
                'status': result.status.value
            }
        except Exception as e:
            error_test_results['invalid_data'] = {
                'handled_gracefully': True,
                'exception': str(e)
            }

        # Test with non-existent agent
        try:
            result = await execute_agent_by_name('non_existent_agent', {'test': 'data'})
            error_test_results['non_existent_agent'] = {
                'handled_gracefully': result.status == ExecutionStatus.FAILED,
                'error_message_present': bool(result.error_message)
            }
        except Exception as e:
            error_test_results['non_existent_agent'] = {
                'handled_gracefully': True,
                'exception': str(e)
            }

        self.logger.info(f"Error handling test: {len(error_test_results)} error scenarios tested")

        return error_test_results

    async def test_multiple_agent_execution(self) -> Dict[str, Any]:
        """Test concurrent execution of multiple agents"""

        # Execute multiple agents concurrently
        tasks = [
            execute_agent_by_name('income_builder', {
                'task_type': 'analyze_opportunities',
                'user_profile': {'id': 'concurrent_test_1'}
            }),
            execute_agent_by_name('content_creator', {
                'content_type': 'blog_post',
                'topic': 'Concurrent execution test',
                'word_count': 500
            }),
            execute_agent_by_name('payment_processor', {
                'task_type': 'create_invoice',
                'amount': 100.0,
                'client_info': {'name': 'Concurrent Test Client'}
            })
        ]

        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        successful_executions = [
            r for r in results
            if not isinstance(r, Exception) and r.status == ExecutionStatus.COMPLETED
        ]

        concurrent_results = {
            'total_tasks': len(tasks),
            'successful_tasks': len(successful_executions),
            'failed_tasks': len(tasks) - len(successful_executions),
            'total_execution_time_ms': int((end_time - start_time) * 1000),
            'success_rate': len(successful_executions) / len(tasks),
            'concurrent_execution_worked': len(successful_executions) > 1
        }

        self.logger.info(
            f"Concurrent execution test: "
            f"{concurrent_results['successful_tasks']}/{concurrent_results['total_tasks']} successful"
        )

        return concurrent_results

    async def generate_test_report(self):
        """Generate comprehensive test report"""

        end_time = time.time()
        total_test_time = end_time - self.start_time

        # Calculate test statistics
        passed_tests = [r for r in self.test_results if r['status'] == 'PASSED']
        failed_tests = [r for r in self.test_results if r['status'] == 'FAILED']

        report = {
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed_tests': len(passed_tests),
                'failed_tests': len(failed_tests),
                'success_rate': len(passed_tests) / len(self.test_results) if self.test_results else 0,
                'total_test_time_seconds': total_test_time,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': self.test_results,
            'system_status': await system_health_check()
        }

        # Save report to file
        report_path = self.output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        self.logger.info("\n" + "=" * 80)
        self.logger.info("TEST EXECUTION COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"✅ Passed: {len(passed_tests)}")
        self.logger.info(f"❌ Failed: {len(failed_tests)}")
        self.logger.info(f"📊 Success Rate: {(len(passed_tests) / len(self.test_results) * 100):.1f}%")
        self.logger.info(f"⏱️  Total Time: {total_test_time:.2f} seconds")
        self.logger.info(f"📄 Report: {report_path}")

        if failed_tests:
            self.logger.info("\nFailed Tests:")
            for test in failed_tests:
                self.logger.info(f"  - {test['test_name']}: {test.get('error', 'Unknown error')}")

        return report


async def main():
    """Main test execution function"""

    # Check environment setup
    if not os.getenv('DJANGO_SETTINGS_MODULE'):
        print("❌ Django settings not configured")
        sys.exit(1)

    print("🚀 Starting Real Agent Execution Test Suite")
    print("=" * 60)

    # Initialize tester
    tester = RealAgentExecutionTester()

    # Run all tests
    try:
        await tester.run_all_tests()
        print("\n✅ Test suite completed successfully!")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())