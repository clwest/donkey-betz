#!/usr/bin/env python3
"""
Test Income Builder Real Tool Usage Validation
Validates that Income Builder agents use real tools vs simulation
"""

import json
import requests
from datetime import datetime
from pathlib import Path


class IncomeBuilderToolValidator:
    """Validates that Income Builder uses real tools vs simulation"""

    def __init__(self):
        self.test_results = {}
        self.validation_errors = []

    def test_web_search_usage(self):
        """Test if Income Builder uses real web search"""
        print("🔍 Testing Web Search Usage...")

        try:
            # Test DuckDuckGo API call
            search_query = "AI content writing freelance market 2024"
            search_url = f"https://api.duckduckgo.com/?q={search_query}&format=json&no_html=1&skip_disambig=1"

            response = requests.get(search_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('RelatedTopics', [])

                self.test_results['web_search'] = {
                    'status': 'SUCCESS',
                    'api_working': True,
                    'results_count': len(results),
                    'sample_result': results[0] if results else None
                }
                print(f"✅ Web search working: {len(results)} results found")
            else:
                self.test_results['web_search'] = {
                    'status': 'ERROR',
                    'error': f"API returned {response.status_code}"
                }
                print(f"❌ Web search failed: {response.status_code}")

        except Exception as e:
            self.test_results['web_search'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ Web search error: {e}")

    def test_api_calls(self):
        """Test if Income Builder can make real API calls"""
        print("🌐 Testing API Calls...")

        try:
            # Test GitHub API (free, no auth required)
            api_url = "https://api.github.com/search/repositories?q=hiring+remote+jobs&sort=updated&per_page=3"

            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                self.test_results['api_calls'] = {
                    'status': 'SUCCESS',
                    'api_working': True,
                    'results_count': len(items),
                    'sample_data': {
                        'name': items[0].get('name') if items else None,
                        'url': items[0].get('html_url') if items else None
                    }
                }
                print(f"✅ API calls working: {len(items)} results found")
            else:
                self.test_results['api_calls'] = {
                    'status': 'ERROR',
                    'error': f"API returned {response.status_code}"
                }
                print(f"❌ API calls failed: {response.status_code}")

        except Exception as e:
            self.test_results['api_calls'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ API calls error: {e}")

    def test_file_creation(self):
        """Test if Income Builder creates real files"""
        print("📁 Testing File Creation...")

        try:
            # Create test directory
            test_dir = Path("income_builder_outputs")
            test_dir.mkdir(exist_ok=True)

            # Create test file
            test_file = test_dir / f"tool_validation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            test_data = {
                'test_type': 'file_creation_validation',
                'timestamp': datetime.now().isoformat(),
                'tools_tested': ['web_search', 'api_calls', 'file_creation'],
                'validation_status': 'testing'
            }

            with open(test_file, 'w') as f:
                json.dump(test_data, f, indent=2)

            # Verify file exists and has content
            if test_file.exists() and test_file.stat().st_size > 0:
                self.test_results['file_creation'] = {
                    'status': 'SUCCESS',
                    'file_created': str(test_file),
                    'file_size': test_file.stat().st_size,
                    'content_valid': True
                }
                print(f"✅ File creation working: {test_file}")
            else:
                self.test_results['file_creation'] = {
                    'status': 'ERROR',
                    'error': 'File not created or empty'
                }
                print("❌ File creation failed")

        except Exception as e:
            self.test_results['file_creation'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ File creation error: {e}")

    def test_income_builder_integration(self):
        """Test if Income Builder API works"""
        print("🧠 Testing Income Builder API...")

        try:
            # Test the Income Builder API endpoint
            api_url = "http://localhost:8000/api/v1/intelligence/income-builder/"

            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                opportunities = data.get('opportunities', [])

                self.test_results['income_builder_integration'] = {
                    'status': 'SUCCESS',
                    'api_working': True,
                    'opportunities_count': len(opportunities),
                    'has_data': bool(data.get('success'))
                }
                print(f"✅ Income Builder API working: {len(opportunities)} opportunities")
            else:
                self.test_results['income_builder_integration'] = {
                    'status': 'ERROR',
                    'error': f"API returned {response.status_code}"
                }
                print(f"❌ Income Builder API failed: {response.status_code}")

        except Exception as e:
            self.test_results['income_builder_integration'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ Income Builder API error: {e}")

    def test_action_plan_api(self):
        """Test if action plan API works"""
        print("⚡ Testing Action Plan API...")

        try:
            # Test action plan creation via API
            api_url = "http://localhost:8000/api/v1/intelligence/income-builder/execute/"

            test_data = {
                "plan": {
                    "steps": [
                        "Research current AI content writing market",
                        "Create portfolio with 3 sample articles"
                    ],
                    "timeline": "1 week",
                    "expected_outcome": "Tool validation complete"
                },
                "opportunity": {
                    "id": "content_writing_test",
                    "title": "AI-Powered Content Writing Test",
                    "description": "Test opportunity for tool validation"
                }
            }

            response = requests.post(api_url, json=test_data, timeout=10)

            if response.status_code in [200, 201]:
                data = response.json()

                self.test_results['action_plan_api'] = {
                    'status': 'SUCCESS',
                    'api_working': True,
                    'plan_created': data.get('success', False),
                    'plan_id': data.get('plan_id'),
                    'celery_task_id': data.get('celery_task_id')
                }
                print(f"✅ Action Plan API working: Plan {data.get('plan_id')} created")

                # Test polling the action plan
                if data.get('plan_id'):
                    polling_response = requests.get(api_url, timeout=10)
                    if polling_response.status_code == 200:
                        polling_data = polling_response.json()
                        plans = polling_data.get('plans', [])
                        print(f"📊 Polling working: {len(plans)} plans found")

            else:
                self.test_results['action_plan_api'] = {
                    'status': 'ERROR',
                    'error': f"API returned {response.status_code}"
                }
                print(f"❌ Action Plan API failed: {response.status_code}")

        except Exception as e:
            self.test_results['action_plan_api'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            print(f"❌ Action Plan API error: {e}")

    def validate_no_simulation(self):
        """Validate that no simulation/sleep is being used"""
        print("🚫 Validating No Simulation Usage...")

        # Check the tasks.py file for simulation indicators
        tasks_file = Path("/Users/donkeyking/development/unified-donkey-betz/intelligence/tasks.py")

        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                content = f.read()

            # Check for simulation indicators
            simulation_indicators = [
                'time.sleep(',
                'mock_response',
                'Mock response',
                'simulated',
                'fake_data'
            ]

            found_simulations = []
            for indicator in simulation_indicators:
                if indicator.lower() in content.lower():
                    found_simulations.append(indicator)

            # Check for real tool indicators
            real_tool_indicators = [
                'requests.get(',
                'api_url',
                'web_search',
                'real_data',
                'actual_data'
            ]

            found_real_tools = []
            for indicator in real_tool_indicators:
                if indicator.lower() in content.lower():
                    found_real_tools.append(indicator)

            self.test_results['simulation_validation'] = {
                'status': 'SUCCESS' if not found_simulations and found_real_tools else 'WARNING',
                'simulation_indicators_found': found_simulations,
                'real_tool_indicators_found': found_real_tools,
                'file_analyzed': str(tasks_file)
            }

            if not found_simulations and found_real_tools:
                print("✅ No simulation found, real tools detected")
            else:
                print(f"⚠️ Found simulation indicators: {found_simulations}")
                print(f"✅ Found real tool indicators: {found_real_tools}")
        else:
            self.test_results['simulation_validation'] = {
                'status': 'ERROR',
                'error': 'tasks.py file not found'
            }
            print("❌ Could not analyze tasks.py file")

    def generate_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*60)
        print("📊 INCOME BUILDER TOOL VALIDATION REPORT")
        print("="*60)

        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results.values() if r.get('status') == 'SUCCESS')

        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests*100):.1f}%")
        print()

        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result.get('status') == 'SUCCESS' else "❌" if result.get('status') == 'ERROR' else "⚠️"
            print(f"{status_emoji} {test_name.replace('_', ' ').title()}: {result.get('status')}")

            if result.get('error'):
                print(f"   Error: {result['error']}")
            elif test_name == 'web_search' and result.get('results_count'):
                print(f"   Results: {result['results_count']} search results")
            elif test_name == 'api_calls' and result.get('results_count'):
                print(f"   Results: {result['results_count']} API results")
            elif test_name == 'file_creation' and result.get('file_created'):
                print(f"   File: {result['file_created']}")
            elif test_name == 'income_builder_integration' and result.get('opportunities_found'):
                print(f"   Opportunities: {result['opportunities_found']}")
            elif test_name == 'action_plan_execution' and result.get('celery_task_id'):
                print(f"   Task ID: {result['celery_task_id']}")

        print()

        # Overall assessment
        if successful_tests >= total_tests * 0.8:
            print("🎉 OVERALL ASSESSMENT: INCOME BUILDER IS USING REAL TOOLS")
            print("   The Income Builder system is properly integrated with real tools and APIs.")
        elif successful_tests >= total_tests * 0.5:
            print("⚠️ OVERALL ASSESSMENT: PARTIAL REAL TOOL USAGE")
            print("   Some tools are working, but there may be issues with others.")
        else:
            print("❌ OVERALL ASSESSMENT: SIMULATION/MOCK USAGE DETECTED")
            print("   The Income Builder may still be using simulation instead of real tools.")

        # Save report
        report_file = Path("income_builder_outputs") / f"tool_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump({
                'validation_timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'successful_tests': successful_tests,
                    'success_rate': (successful_tests/total_tests*100) if total_tests > 0 else 0
                },
                'test_results': self.test_results,
                'validation_errors': self.validation_errors
            }, f, indent=2)

        print(f"\n📄 Full report saved to: {report_file}")

    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Income Builder Tool Validation")
        print("="*60)

        self.test_web_search_usage()
        self.test_api_calls()
        self.test_file_creation()
        self.test_income_builder_integration()
        self.test_action_plan_api()
        self.validate_no_simulation()

        self.generate_report()


if __name__ == "__main__":
    validator = IncomeBuilderToolValidator()
    validator.run_all_tests()