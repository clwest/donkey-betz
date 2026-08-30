# Session 728: Migrated from agents/agent_testing_system.py
"""
Comprehensive Agent Testing System
==================================
This system tests all 157 agents to identify which are working and which need fixes.
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from agents.proper_agent_executor import ProperAgentExecutor
from core.models import GeneratedProject

logger = logging.getLogger(__name__)

@dataclass
class AgentTestResult:
    agent_name: str
    display_name: str
    executor_name: str
    status: str  # 'success', 'registry_error', 'execution_error', 'timeout'
    error_message: str = ""
    execution_time: float = 0.0
    task_type: str = ""
    output_created: bool = False
    registry_found: bool = False


class AgentTestingSystem:
    """
    Comprehensive testing system for all agents in the registry.
    """

    def __init__(self):
        self.test_results: List[AgentTestResult] = []
        self.test_project = None
        self._executor = None

    @property
    def executor(self):
        """Lazy load executor to avoid initialization issues"""
        if self._executor is None:
            self._executor = ProperAgentExecutor()
        return self._executor

    async def create_test_project(self) -> GeneratedProject:
        """Create a test project for agent execution"""
        from asgiref.sync import sync_to_async

        @sync_to_async
        def create_project():
            return GeneratedProject.objects.create(
                name="Agent_Testing_Project",
                project_type="testing",
                description="Automated testing of all agents",
                status='generating',
                agents_used=[],
                metadata={'test_run': True, 'timestamp': str(datetime.now())}
            )

        return await create_project()

    def get_all_agent_names(self) -> List[str]:
        """Get all 157 agent display names from the proper_agent_executor"""
        agent_tasks = self.executor._get_all_agent_tasks()
        return sorted(list(agent_tasks.keys()))

    def get_registry_status(self) -> Dict[str, Any]:
        """Get current registry status"""
        try:
            # Ensure executor is initialized
            executor = self.executor

            registry_info = {
                'has_agent_classes': hasattr(executor.executor, 'agent_classes'),
                'total_agents': 0,
                'available_agents': []
            }

            if hasattr(executor.executor, 'agent_classes') and executor.executor.agent_classes:
                registry_info['total_agents'] = len(executor.executor.agent_classes)
                registry_info['available_agents'] = sorted([k for k in executor.executor.agent_classes.keys() if k])

            return registry_info
        except Exception as e:
            logger.error(f"Error getting registry status: {e}")
            return {
                'has_agent_classes': False,
                'total_agents': 0,
                'available_agents': [],
                'error': str(e)
            }

    async def test_single_agent(self, agent_name: str, timeout_seconds: int = 30) -> AgentTestResult:
        """Test a single agent execution"""
        start_time = asyncio.get_event_loop().time()

        # Get the expected executor name
        executor_agent_name = agent_name.lower().replace(' ', '_')

        # Check registry mapping first
        registry_info = self.get_registry_status()
        registry_found = executor_agent_name in registry_info.get('available_agents', [])

        # Get task configuration
        agent_tasks = self.executor._get_all_agent_tasks()
        task_config = agent_tasks.get(agent_name, {})

        test_result = AgentTestResult(
            agent_name=agent_name,
            display_name=agent_name,
            executor_name=executor_agent_name,
            status='unknown',
            task_type=task_config.get('task', 'unknown'),
            registry_found=registry_found
        )

        try:
            # Create test project if needed
            if not self.test_project:
                self.test_project = await self.create_test_project()

            # Test task configuration
            task_config_test = {
                'project_type': 'testing',
                'project_description': f'Testing {agent_name} capabilities',
                'key_features': ['automated_testing'],
                'target_audience': 'developers',
                'requirements': {'test_mode': True},
                'ml_features': []
            }

            # Execute with timeout
            try:
                result = await asyncio.wait_for(
                    self.executor.execute_agent_task(agent_name, self.test_project, task_config_test),
                    timeout=timeout_seconds
                )

                execution_time = asyncio.get_event_loop().time() - start_time

                if result.get('success'):
                    test_result.status = 'success'
                    test_result.execution_time = execution_time
                    test_result.output_created = bool(result.get('file_created'))
                    logger.info(f"✅ {agent_name} - SUCCESS ({execution_time:.2f}s)")
                else:
                    test_result.status = 'execution_error'
                    test_result.error_message = result.get('error', 'Unknown execution error')
                    test_result.execution_time = execution_time
                    logger.warning(f"⚠️ {agent_name} - EXECUTION ERROR: {test_result.error_message}")

            except asyncio.TimeoutError:
                test_result.status = 'timeout'
                test_result.error_message = f'Execution timeout after {timeout_seconds} seconds'
                test_result.execution_time = timeout_seconds
                logger.warning(f"⏰ {agent_name} - TIMEOUT")

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            test_result.execution_time = execution_time

            error_str = str(e)
            if 'not found in registry' in error_str:
                test_result.status = 'registry_error'
                test_result.error_message = f'Agent not found in registry: {executor_agent_name}'
                logger.error(f"❌ {agent_name} - REGISTRY ERROR: {executor_agent_name} not found")
            else:
                test_result.status = 'execution_error'
                test_result.error_message = error_str
                logger.error(f"💥 {agent_name} - ERROR: {error_str}")

        return test_result

    async def test_all_agents(self, max_concurrent: int = 5, timeout_per_agent: int = 30) -> List[AgentTestResult]:
        """Test all agents with concurrency control"""
        agent_names = self.get_all_agent_names()
        logger.info(f"🚀 Starting comprehensive test of {len(agent_names)} agents")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def test_with_semaphore(agent_name: str):
            async with semaphore:
                return await self.test_single_agent(agent_name, timeout_per_agent)

        # Execute all tests with concurrency control
        self.test_results = await asyncio.gather(
            *[test_with_semaphore(name) for name in agent_names],
            return_exceptions=True
        )

        # Handle any exceptions
        valid_results = []
        for i, result in enumerate(self.test_results):
            if isinstance(result, Exception):
                # Create error result for failed test
                valid_results.append(AgentTestResult(
                    agent_name=agent_names[i],
                    display_name=agent_names[i],
                    executor_name=agent_names[i].lower().replace(' ', '_'),
                    status='test_error',
                    error_message=str(result)
                ))
            else:
                valid_results.append(result)

        self.test_results = valid_results
        return self.test_results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.test_results:
            return {'error': 'No test results available'}

        # Categorize results
        success_agents = [r for r in self.test_results if r.status == 'success']
        registry_errors = [r for r in self.test_results if r.status == 'registry_error']
        execution_errors = [r for r in self.test_results if r.status == 'execution_error']
        timeout_errors = [r for r in self.test_results if r.status == 'timeout']
        test_errors = [r for r in self.test_results if r.status == 'test_error']

        # Registry analysis
        registry_info = self.get_registry_status()

        # Performance stats
        successful_times = [r.execution_time for r in success_agents if r.execution_time > 0]
        avg_execution_time = sum(successful_times) / len(successful_times) if successful_times else 0

        report = {
            'test_summary': {
                'total_agents_tested': len(self.test_results),
                'successful': len(success_agents),
                'registry_errors': len(registry_errors),
                'execution_errors': len(execution_errors),
                'timeouts': len(timeout_errors),
                'test_errors': len(test_errors),
                'success_rate': f"{len(success_agents) / len(self.test_results) * 100:.1f}%" if self.test_results else "0%",
                'average_execution_time': f"{avg_execution_time:.2f}s"
            },
            'registry_status': registry_info,
            'successful_agents': [
                {
                    'name': r.agent_name,
                    'executor_name': r.executor_name,
                    'task_type': r.task_type,
                    'execution_time': f"{r.execution_time:.2f}s",
                    'output_created': r.output_created
                }
                for r in success_agents
            ],
            'registry_errors': [
                {
                    'name': r.agent_name,
                    'executor_name': r.executor_name,
                    'error': r.error_message,
                    'registry_found': r.registry_found
                }
                for r in registry_errors
            ],
            'execution_errors': [
                {
                    'name': r.agent_name,
                    'executor_name': r.executor_name,
                    'task_type': r.task_type,
                    'error': r.error_message,
                    'execution_time': f"{r.execution_time:.2f}s"
                }
                for r in execution_errors
            ],
            'timeout_errors': [
                {
                    'name': r.agent_name,
                    'executor_name': r.executor_name,
                    'task_type': r.task_type
                }
                for r in timeout_errors
            ],
            'fix_recommendations': self._generate_fix_recommendations(registry_errors, execution_errors)
        }

        return report

    def _generate_fix_recommendations(self, registry_errors: List[AgentTestResult],
                                    execution_errors: List[AgentTestResult]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for fixing agent issues"""
        recommendations = []

        if registry_errors:
            registry_info = self.get_registry_status()
            available_agents = set(registry_info.get('available_agents', []))

            for error in registry_errors:
                # Try to find similar agent names
                similar_agents = [
                    agent for agent in available_agents
                    if any(word in agent for word in error.executor_name.split('_'))
                ]

                recommendations.append({
                    'type': 'registry_mapping',
                    'agent': error.agent_name,
                    'issue': f"'{error.executor_name}' not found in registry",
                    'suggested_mappings': similar_agents[:3],  # Top 3 matches
                    'action': f"Update name mapping for '{error.agent_name}' in proper_agent_executor.py"
                })

        if execution_errors:
            recommendations.append({
                'type': 'execution_debugging',
                'issue': f"{len(execution_errors)} agents have execution errors",
                'action': "Review ConcreteAgentExecutor implementation and LLM integration"
            })

        return recommendations

    def print_console_report(self):
        """Print formatted report to console"""
        if not self.test_results:
            print("❌ No test results available")
            return

        report = self.generate_report()
        summary = report['test_summary']

        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE AGENT TESTING REPORT")
        print("="*80)
        print(f"📊 SUMMARY:")
        print(f"   Total Agents: {summary['total_agents_tested']}")
        print(f"   ✅ Successful: {summary['successful']} ({summary['success_rate']})")
        print(f"   ❌ Registry Errors: {summary['registry_errors']}")
        print(f"   ⚠️  Execution Errors: {summary['execution_errors']}")
        print(f"   ⏰ Timeouts: {summary['timeouts']}")
        print(f"   💥 Test Errors: {summary['test_errors']}")
        print(f"   ⚡ Avg Execution: {summary['average_execution_time']}")

        if report['successful_agents']:
            print(f"\n✅ WORKING AGENTS ({len(report['successful_agents'])}):")
            for agent in report['successful_agents'][:10]:  # Show top 10
                print(f"   • {agent['name']} → {agent['executor_name']} ({agent['execution_time']})")
            if len(report['successful_agents']) > 10:
                print(f"   ... and {len(report['successful_agents']) - 10} more")

        if report['registry_errors']:
            print(f"\n❌ REGISTRY ERRORS ({len(report['registry_errors'])}):")
            for error in report['registry_errors'][:5]:  # Show top 5
                print(f"   • {error['name']} → '{error['executor_name']}' not found")

        if report['execution_errors']:
            print(f"\n⚠️  EXECUTION ERRORS ({len(report['execution_errors'])}):")
            for error in report['execution_errors'][:5]:  # Show top 5
                print(f"   • {error['name']}: {error['error'][:60]}...")

        print(f"\n🔧 RECOMMENDATIONS:")
        for rec in report['fix_recommendations'][:3]:  # Show top 3
            print(f"   • {rec['action']}")

        print("="*80)


# Django views for web interface
@csrf_exempt
@require_http_methods(["POST"])
def run_agent_tests(request):
    """Run comprehensive agent tests via API"""
    try:
        data = json.loads(request.body or b"{}") if request.body else {}
        max_concurrent = data.get('max_concurrent', 3)
        timeout_per_agent = data.get('timeout_per_agent', 30)
        test_specific = data.get('agents', [])  # Test specific agents only

        # Debug: Check ConcreteAgentExecutor directly
        from ai_core.agents.concrete_executor import ConcreteAgentExecutor
        debug_executor = ConcreteAgentExecutor()
        logger.info(f"DEBUG: Direct ConcreteAgentExecutor has {len(debug_executor.agent_classes)} agents")
        logger.info(f"DEBUG: Agent classes keys: {list(debug_executor.agent_classes.keys())[:10]}")

        async def run_tests():
            tester = AgentTestingSystem()

            # Debug: Check tester's executor
            logger.info(f"DEBUG: Tester executor has {len(tester.executor.executor.agent_classes)} agents")

            if test_specific:
                # Test only specific agents
                results = []
                for agent_name in test_specific:
                    result = await tester.test_single_agent(agent_name, timeout_per_agent)
                    results.append(result)
                tester.test_results = results
            else:
                # Test all agents
                await tester.test_all_agents(max_concurrent, timeout_per_agent)

            return tester.generate_report()

        # Run async test in current thread to maintain Django context
        import asyncio

        # Try to get current loop first
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            if loop.is_running():
                # If loop is running, use create_task
                import threading
                result_holder = {}
                error_holder = {}

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result_holder['result'] = new_loop.run_until_complete(run_tests())
                    except Exception as e:
                        error_holder['error'] = e
                    finally:
                        new_loop.close()

                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()

                if 'error' in error_holder:
                    raise error_holder['error']
                report = result_holder['result']
            else:
                report = loop.run_until_complete(run_tests())
        finally:
            # Don't close the main loop
            pass

        return JsonResponse({
            'success': True,
            'report': report
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_agent_test_status(request):
    """Get current agent testing capabilities"""
    try:
        tester = AgentTestingSystem()
        agent_names = tester.get_all_agent_names()
        registry_info = tester.get_registry_status()

        return JsonResponse({
            'success': True,
            'total_agents_to_test': len(agent_names),
            'registry_status': registry_info,
            'sample_agents': agent_names[:10]  # First 10 for preview
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Command line interface
if __name__ == "__main__":
    import django
    import os
    import sys

    # Setup Django
    sys.path.append('/Users/donkeyking/Donkey_Betz/unified-donkey-betz')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    async def main():
        print("🧪 Starting Comprehensive Agent Testing...")
        tester = AgentTestingSystem()

        # Quick test of 5 agents first
        print("\n🔍 Running quick test on 5 agents...")
        sample_agents = tester.get_all_agent_names()[:5]
        for agent in sample_agents:
            result = await tester.test_single_agent(agent, timeout_seconds=15)
            print(f"   {result.status}: {result.agent_name}")

        print(f"\n🚀 Would you like to test all {len(tester.get_all_agent_names())} agents? (y/n)")
        # For script execution, just run a few more
        print("Running extended test on 15 agents...")

        extended_agents = tester.get_all_agent_names()[:15]
        tester.test_results = []
        for agent in extended_agents:
            result = await tester.test_single_agent(agent, timeout_seconds=20)
            tester.test_results.append(result)

        # Generate and display report
        tester.print_console_report()

        print("\n💾 Full test results available via API at /api/agents/run-tests/")

    asyncio.run(main())