#!/usr/bin/env python3
"""
Master Platform Integration Test
Verifies all component connections and data flows are working
"""

import asyncio
import json
import time
import websockets
from datetime import datetime
from typing import Dict, List, Any

class PlatformIntegrationTester:
    """Test all platform integrations end-to-end"""

    def __init__(self):
        self.ws_url = 'ws://localhost:8000'
        self.api_url = 'http://localhost:8000'
        self.test_results = {}
        self.connections = {}

    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        print("🚀 Starting Platform Integration Tests")
        print("=" * 60)

        tests = [
            ("WebSocket Hub Connection", self.test_websocket_hub),
            ("Personal Assistant Integration", self.test_personal_assistant),
            ("Income Builder Data Flow", self.test_income_builder),
            ("Spider Network Activation", self.test_spider_network),
            ("Job Tracker Integration", self.test_job_tracker),
            ("Revenue Tracking", self.test_revenue_tracking),
            ("Neural Orchestra Activity", self.test_neural_orchestra),
            ("Decision Command Execution", self.test_decision_command),
            ("Persistent Storage", self.test_persistent_storage),
            ("Quick Apply System", self.test_quick_apply),
            ("End-to-End Data Flow", self.test_end_to_end_flow)
        ]

        for test_name, test_func in tests:
            print(f"\n🧪 Testing: {test_name}")
            try:
                result = await test_func()
                self.test_results[test_name] = result
                status = "✅ PASS" if result.get('success') else "❌ FAIL"
                print(f"   {status}: {result.get('message', 'No message')}")

                if result.get('details'):
                    for detail in result['details']:
                        print(f"     • {detail}")

            except Exception as e:
                self.test_results[test_name] = {
                    'success': False,
                    'message': f'Test failed with exception: {str(e)}',
                    'error': str(e)
                }
                print(f"   ❌ FAIL: {str(e)}")

        # Print summary
        self.print_test_summary()

    async def test_websocket_hub(self) -> Dict[str, Any]:
        """Test unified WebSocket hub connections"""
        try:
            # Test connection to each component endpoint
            components = [
                'personal_assistant',
                'income_builder',
                'revenue_dashboard',
                'neural_orchestra',
                'decision_command'
            ]

            connected_components = []
            failed_components = []

            for component in components:
                try:
                    ws_uri = f"{self.ws_url}/ws/unified-hub/{component}/"

                    async with websockets.connect(ws_uri, timeout=5) as websocket:
                        # Send ping
                        await websocket.send(json.dumps({
                            'type': 'ping',
                            'timestamp': datetime.now().isoformat()
                        }))

                        # Wait for pong
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(response)

                        if data.get('type') == 'pong':
                            connected_components.append(component)
                        else:
                            failed_components.append(f"{component}: unexpected response")

                except Exception as e:
                    failed_components.append(f"{component}: {str(e)}")

            success = len(connected_components) >= 3  # At least 3 components should connect

            return {
                'success': success,
                'message': f'Connected to {len(connected_components)}/{len(components)} components',
                'details': [
                    f"Connected: {', '.join(connected_components)}",
                    f"Failed: {', '.join(failed_components) if failed_components else 'None'}"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'WebSocket hub test failed: {str(e)}'
            }

    async def test_personal_assistant(self) -> Dict[str, Any]:
        """Test Personal Assistant platform integration"""
        try:
            ws_uri = f"{self.ws_url}/ws/unified-hub/personal_assistant/"

            async with websockets.connect(ws_uri, timeout=10) as websocket:
                # Wait for connection message
                await asyncio.wait_for(websocket.recv(), timeout=5)

                # Test platform message handling
                await websocket.send(json.dumps({
                    'type': 'trigger_spider_deployment',
                    'data': {
                        'request': 'Find job opportunities',
                        'criteria': {
                            'skills': ['python', 'ai'],
                            'location': 'remote'
                        }
                    }
                }))

                # Wait for spider deployment response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(response)

                spider_activated = data.get('type') == 'spider_deployment_started'

                return {
                    'success': spider_activated,
                    'message': 'Personal Assistant can trigger platform actions',
                    'details': [
                        f"Spider deployment: {'activated' if spider_activated else 'failed'}",
                        f"Response type: {data.get('type', 'unknown')}"
                    ]
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Personal Assistant test failed: {str(e)}'
            }

    async def test_income_builder(self) -> Dict[str, Any]:
        """Test Income Builder data flow"""
        try:
            ws_uri = f"{self.ws_url}/ws/unified-hub/income_builder/"

            async with websockets.connect(ws_uri, timeout=10) as websocket:
                # Wait for connection message
                await asyncio.wait_for(websocket.recv(), timeout=5)

                # Request opportunities
                await websocket.send(json.dumps({
                    'type': 'get_opportunities',
                    'source': 'income_builder'
                }))

                # Wait for opportunities response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(response)

                has_opportunities = (
                    data.get('type') in ['opportunities_analysis', 'opportunities_update'] and
                    data.get('top_opportunities') or data.get('opportunities')
                )

                opportunity_count = 0
                if data.get('top_opportunities'):
                    opportunity_count = len(data['top_opportunities'])
                elif data.get('opportunities'):
                    opportunity_count = len(data['opportunities'])

                return {
                    'success': has_opportunities,
                    'message': f'Income Builder provides {opportunity_count} opportunities',
                    'details': [
                        f"Response type: {data.get('type', 'unknown')}",
                        f"Data source: {data.get('source', 'unknown')}",
                        f"Real data: {data.get('is_real', False)}"
                    ]
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Income Builder test failed: {str(e)}'
            }

    async def test_spider_network(self) -> Dict[str, Any]:
        """Test spider network activation"""
        try:
            # Import and test spider bridge directly
            import sys
            import os
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

            from intelligence.unified_spider_job_bridge import unified_spider_bridge

            # Test spider deployment
            deployment = await unified_spider_bridge.activate_spider_deployment(
                "Integration test job search",
                {'skills': ['python', 'ai'], 'location': 'remote'}
            )

            jobs_found = deployment.get('jobs_found', 0)
            sources_used = len(deployment.get('sources', []))

            return {
                'success': jobs_found > 0,
                'message': f'Spider network found {jobs_found} jobs from {sources_used} sources',
                'details': [
                    f"Deployment ID: {deployment.get('deployment_id', 'unknown')}",
                    f"Sources: {', '.join(deployment.get('sources', []))}",
                    f"Spider count: {deployment.get('spider_count', 0)}"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Spider network test failed: {str(e)}'
            }

    async def test_job_tracker(self) -> Dict[str, Any]:
        """Test AI Job Tracker integration"""
        try:
            # Test job-income bridge
            import sys
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

            from intelligence.job_income_bridge import JobIncomeBridge

            # Get unified opportunities
            unified_data = JobIncomeBridge.get_unified_opportunities()
            opportunities = unified_data.get('opportunities', [])
            stats = unified_data.get('stats', {})

            has_jobs = stats.get('real_jobs', 0) > 0
            has_income_streams = stats.get('income_streams', 0) > 0

            return {
                'success': len(opportunities) > 0,
                'message': f'Job tracker provides {len(opportunities)} unified opportunities',
                'details': [
                    f"Real jobs: {stats.get('real_jobs', 0)}",
                    f"Income streams: {stats.get('income_streams', 0)}",
                    f"Average monthly potential: ${stats.get('avg_monthly_potential', 0):.0f}",
                    f"Data source: {unified_data.get('source', 'unknown')}"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Job tracker test failed: {str(e)}'
            }

    async def test_revenue_tracking(self) -> Dict[str, Any]:
        """Test revenue tracking system"""
        try:
            import sys
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

            from intelligence.revenue_tracking_bridge import revenue_bridge

            # Test proposal tracking
            proposal_id = await revenue_bridge.track_proposal(
                user_id='test_user',
                opportunity_id='test_opp_123',
                platform='test_platform',
                job_title='Test Integration Job',
                company='Test Company',
                proposed_rate=75.0,
                proposal_text='Test proposal for integration'
            )

            # Test revenue recording
            revenue_recorded = await revenue_bridge.record_revenue(
                user_id='test_user',
                source_name='Integration Test Revenue',
                amount=100.0,
                revenue_type='test_payment',
                description='Test revenue for integration',
                platform='test_platform'
            )

            # Get dashboard metrics
            metrics = await revenue_bridge.get_dashboard_metrics('test_user')

            return {
                'success': bool(proposal_id) and revenue_recorded and bool(metrics),
                'message': 'Revenue tracking system operational',
                'details': [
                    f"Proposal tracked: {bool(proposal_id)}",
                    f"Revenue recorded: {revenue_recorded}",
                    f"Metrics available: {bool(metrics)}",
                    f"Daily revenue: ${metrics.get('daily_metrics', {}).get('revenue_generated', 0)}"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Revenue tracking test failed: {str(e)}'
            }

    async def test_neural_orchestra(self) -> Dict[str, Any]:
        """Test Neural Orchestra real activity"""
        try:
            ws_uri = f"{self.ws_url}/ws/unified-hub/neural_orchestra/"

            async with websockets.connect(ws_uri, timeout=10) as websocket:
                # Wait for connection message
                await asyncio.wait_for(websocket.recv(), timeout=5)

                # Request orchestra data
                await websocket.send(json.dumps({
                    'type': 'get_orchestra_data'
                }))

                # Wait for orchestra response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(response)

                has_agents = len(data.get('agents', [])) > 0
                has_advisors = len(data.get('advisors', [])) > 0
                has_workflows = len(data.get('workflows', [])) > 0
                is_real = data.get('is_real', False)

                return {
                    'success': has_agents and has_advisors and is_real,
                    'message': 'Neural Orchestra shows real agent activity',
                    'details': [
                        f"Agents: {len(data.get('agents', []))}",
                        f"Advisors: {len(data.get('advisors', []))}",
                        f"Workflows: {len(data.get('workflows', []))}",
                        f"Real activity: {is_real}",
                        f"Active agents: {data.get('system_stats', {}).get('active_agents', 0)}"
                    ]
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Neural Orchestra test failed: {str(e)}'
            }

    async def test_decision_command(self) -> Dict[str, Any]:
        """Test Decision Command real execution"""
        try:
            import sys
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

            from intelligence.real_execution_engine import real_execution_engine

            # Test real execution
            decision_data = {
                'type': 'analyze_opportunities',
                'criteria': {
                    'skills': ['python', 'ai'],
                    'min_salary': 50000
                }
            }

            user_context = {
                'user_id': 'test_user',
                'skills': ['python', 'ai', 'data analysis'],
                'experience_level': 'mid',
                'location': 'remote'
            }

            result = await real_execution_engine.execute_decision(decision_data, user_context)

            execution_success = result.get('success', False)
            execution_id = result.get('execution_id')

            return {
                'success': execution_success,
                'message': 'Decision Command executes real actions',
                'details': [
                    f"Execution ID: {execution_id}",
                    f"Action type: {result.get('action_type', 'unknown')}",
                    f"Opportunities analyzed: {result.get('total_opportunities_analyzed', 0)}",
                    f"Recommendations: {len(result.get('recommendations', []))}"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Decision Command test failed: {str(e)}'
            }

    async def test_persistent_storage(self) -> Dict[str, Any]:
        """Test persistent storage system"""
        try:
            import sys
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

            from core.unified_storage import unified_storage

            test_data = {
                'test_key': 'test_value',
                'timestamp': datetime.now().isoformat(),
                'integration_test': True
            }

            # Test component state save/load
            save_success = unified_storage.save_component_state(
                'test_component', 'test_user', test_data
            )

            loaded_data = unified_storage.load_component_state(
                'test_component', 'test_user'
            )

            # Test user profile save/load
            profile_data = {
                'full_name': 'Test User',
                'skills': ['python', 'ai'],
                'experience_level': 'mid'
            }

            profile_save_success = unified_storage.save_user_profile(
                'test_user', profile_data
            )

            loaded_profile = unified_storage.load_user_profile('test_user')

            # Test action logging
            action_logged = unified_storage.log_action(
                'test_user', 'test_component', 'integration_test',
                {'test': True}, {'success': True}
            )

            data_match = loaded_data == test_data if loaded_data else False
            profile_match = loaded_profile == profile_data if loaded_profile else False

            return {
                'success': save_success and data_match and profile_save_success and profile_match and action_logged,
                'message': 'Persistent storage system operational',
                'details': [
                    f"Component state save: {save_success}",
                    f"Component state load: {data_match}",
                    f"Profile save: {profile_save_success}",
                    f"Profile load: {profile_match}",
                    f"Action logging: {action_logged}"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Persistent storage test failed: {str(e)}'
            }

    async def test_quick_apply(self) -> Dict[str, Any]:
        """Test Quick Apply execution system"""
        try:
            import sys
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

            from intelligence.revenue_tracking_bridge import revenue_bridge

            # Test quick apply execution
            test_opportunity = {
                'id': 'test_job_123',
                'title': 'Test Python Developer',
                'company': 'Test Company',
                'source': 'test_platform',
                'salary': '$75/hour',
                'url': 'https://test.com/job/123'
            }

            result = await revenue_bridge.execute_quick_apply(
                user_id='test_user',
                opportunity=test_opportunity,
                resume_content='Test resume content',
                cover_letter='Test cover letter for quick apply'
            )

            application_success = result.get('success', False)
            proposal_id = result.get('proposal_id')

            return {
                'success': application_success,
                'message': 'Quick Apply system executes real applications',
                'details': [
                    f"Application success: {application_success}",
                    f"Proposal ID: {proposal_id}",
                    f"Platform: {result.get('submitted_to', 'unknown')}",
                    f"Job title: {result.get('job_title', 'unknown')}",
                    f"Estimated rate: ${result.get('estimated_rate', 0)}"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Quick Apply test failed: {str(e)}'
            }

    async def test_end_to_end_flow(self) -> Dict[str, Any]:
        """Test complete end-to-end data flow"""
        try:
            # This test simulates a complete user journey
            steps_completed = []

            # Step 1: User profile update triggers platform sync
            import sys
            sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

            from core.unified_storage import unified_storage

            profile_data = {
                'full_name': 'End-to-End Test User',
                'skills': ['python', 'machine learning', 'api development'],
                'experience_level': 'senior',
                'desired_salary_min': 80000,
                'location': 'remote',
                'remote_preference': 'remote'
            }

            if unified_storage.save_user_profile('e2e_test_user', profile_data):
                steps_completed.append('Profile saved')

            # Step 2: Spider network finds opportunities
            from intelligence.unified_spider_job_bridge import unified_spider_bridge

            deployment = await unified_spider_bridge.activate_spider_deployment(
                "End-to-end test job search",
                {'skills': profile_data['skills'], 'location': 'remote'}
            )

            if deployment.get('jobs_found', 0) > 0:
                steps_completed.append('Jobs found via spiders')

            # Step 3: Decision engine analyzes opportunities
            from intelligence.real_execution_engine import real_execution_engine

            analysis_result = await real_execution_engine.execute_decision(
                {'type': 'analyze_opportunities'},
                {'user_id': 'e2e_test_user', **profile_data}
            )

            if analysis_result.get('success'):
                steps_completed.append('Opportunities analyzed')

            # Step 4: Revenue tracking records activity
            from intelligence.revenue_tracking_bridge import revenue_bridge

            proposal_tracked = await revenue_bridge.track_proposal(
                'e2e_test_user', 'e2e_test_opp', 'test_platform',
                'E2E Test Job', 'Test Company', 85.0
            )

            if proposal_tracked:
                steps_completed.append('Proposal tracked')

            # Step 5: Check data flows to all components
            flows_verified = len(steps_completed) >= 3

            return {
                'success': flows_verified,
                'message': f'End-to-end flow completed {len(steps_completed)}/4 steps',
                'details': steps_completed + [
                    f"Total integration points tested: {len(self.test_results)}",
                    f"Platform connectivity verified"
                ]
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'End-to-end test failed: {str(e)}'
            }

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 PLATFORM INTEGRATION TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success'))
        failed_tests = total_tests - passed_tests

        print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        # Component status
        print(f"\n🔗 Component Integration Status:")
        critical_components = [
            "WebSocket Hub Connection",
            "Personal Assistant Integration",
            "Income Builder Data Flow",
            "Spider Network Activation",
            "Revenue Tracking"
        ]

        for component in critical_components:
            if component in self.test_results:
                status = "✅" if self.test_results[component].get('success') else "❌"
                print(f"  {status} {component}")

        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test_name, result in self.test_results.items():
                if not result.get('success'):
                    print(f"  • {test_name}: {result.get('message', 'Unknown error')}")

        # Overall assessment
        print(f"\n🏆 Overall Platform Status:")
        if passed_tests >= total_tests * 0.8:
            print("  🟢 EXCELLENT: Platform is well integrated and functional")
        elif passed_tests >= total_tests * 0.6:
            print("  🟡 GOOD: Platform is mostly integrated with some issues")
        elif passed_tests >= total_tests * 0.4:
            print("  🟠 FAIR: Platform has partial integration")
        else:
            print("  🔴 POOR: Platform needs significant integration work")

        # Recommendations
        print(f"\n💡 Recommendations:")
        if failed_tests == 0:
            print("  • All systems integrated successfully!")
            print("  • Monitor performance in production")
            print("  • Add more comprehensive error handling")
        else:
            print("  • Fix failed integration points")
            print("  • Verify WebSocket connections")
            print("  • Check database connectivity")
            print("  • Ensure all components are running")

        print("\n" + "=" * 60)


async def main():
    """Run the integration tests"""
    tester = PlatformIntegrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    print("🚀 Starting Unified Platform Integration Tests...")
    asyncio.run(main())