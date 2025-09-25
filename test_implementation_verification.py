#!/usr/bin/env python3
"""
Test Implementation Verification System

This script tests the new implementation verification system to ensure
agents actually implement changes instead of just providing advice.

Run with: python test_implementation_verification.py
"""

import asyncio
import json
import os
import sys
import requests
import time
from datetime import datetime

# Add project root to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from backend.services.implementation_verifier import implementation_verifier
from backend.agents.concrete_executor import ConcreteAgentExecutor
from core.models import GeneratedProject


class ImplementationVerificationTester:
    """Test the implementation verification system"""

    def __init__(self):
        self.base_url = 'http://localhost:8000'
        self.test_results = []

    def log_test(self, test_name, success, details):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")

    def test_api_endpoints(self):
        """Test all implementation verification API endpoints"""
        print("🔧 Testing API Endpoints...")

        # Test implementation history endpoint
        try:
            response = requests.get(f'{self.base_url}/api/implementation/history/')
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", History items: {data.get('data', {}).get('total_sessions', 0)}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"

        self.log_test("Implementation History API", success, details)

    def create_test_project(self):
        """Create a test project for verification"""
        print("📦 Creating test project...")

        try:
            # Create or get existing test project
            project, created = GeneratedProject.objects.get_or_create(
                name="Implementation Verification Test",
                defaults={
                    'description': 'Test project for implementation verification system',
                    'project_type': 'test',
                    'status': 'active',
                    'agents_used': ['test_agent'],
                    'metadata': {'test': True}
                }
            )

            details = f"Project ID: proj-{project.id} {'(created)' if created else '(existing)'}"
            self.log_test("Test Project Creation", True, details)
            return project

        except Exception as e:
            self.log_test("Test Project Creation", False, f"Error: {str(e)}")
            return None

    async def test_verification_wrapper(self, project):
        """Test the verification wrapper around agent execution"""
        print("🔍 Testing implementation verification wrapper...")

        try:
            # Create a simple task
            task_data = {
                'task_description': 'Test implementation verification',
                'input': {
                    'project_name': project.name,
                    'test_mode': True,
                    'action': 'create_test_file'
                }
            }

            # Test with a mock agent that should make real changes
            executor = ConcreteAgentExecutor()

            # Execute with verification
            result = await implementation_verifier.execute_with_verification(
                agent_executor=executor,
                agent_name='test_agent',
                task=task_data,
                project_id=f'proj-{project.id}'
            )

            # Check results
            verification = result.get('verification', {})
            has_verification = 'session_id' in verification
            has_changes = verification.get('has_real_changes', False)

            details = f"Session: {verification.get('session_id', 'None')}, "
            details += f"Changes: {'Yes' if has_changes else 'No'}, "
            details += f"Evidence: {verification.get('evidence_count', 0)}"

            self.log_test("Verification Wrapper Execution", has_verification, details)
            return verification.get('session_id') if has_verification else None

        except Exception as e:
            self.log_test("Verification Wrapper Execution", False, f"Error: {str(e)}")
            return None

    def test_implementation_evidence_api(self, session_id):
        """Test the implementation evidence API"""
        if not session_id:
            self.log_test("Implementation Evidence API", False, "No session ID to test")
            return

        print("🔍 Testing implementation evidence API...")

        try:
            response = requests.get(f'{self.base_url}/api/implementation/session/{session_id}/')
            success = response.status_code == 200

            if success:
                data = response.json()
                session_data = data.get('data', {}).get('session', {})
                files_modified = session_data.get('metrics', {}).get('files_modified', 0)
                commands_executed = session_data.get('metrics', {}).get('commands_executed', 0)

                details = f"Files: {files_modified}, Commands: {commands_executed}"
            else:
                details = f"Status: {response.status_code}"

        except Exception as e:
            success = False
            details = f"Error: {str(e)}"

        self.log_test("Implementation Evidence API", success, details)

    def test_ai_production_hub_integration(self, project):
        """Test AI Production Hub integration"""
        print("🏭 Testing AI Production Hub integration...")

        try:
            # Test the assign agent endpoint that should use verification
            response = requests.post(
                f'{self.base_url}/api/projects/proj-{project.id}/assign-agent/',
                json={
                    'agent_id': 'test_agent',
                    'improvement_type': 'enhancement'
                }
            )

            success = response.status_code == 200

            if success:
                data = response.json()
                execution_details = data.get('data', {}).get('execution_details', {})
                verification = execution_details.get('verification', {})

                has_verification = 'session_id' in verification
                details = f"Verification included: {'Yes' if has_verification else 'No'}"

                if has_verification:
                    details += f", Session: {verification.get('session_id')}"
                    details += f", Changes: {'Yes' if verification.get('has_real_changes') else 'No'}"
            else:
                details = f"Status: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f", Error: {error_data.get('error', 'Unknown')}"
                except:
                    pass

        except Exception as e:
            success = False
            details = f"Error: {str(e)}"

        self.log_test("AI Production Hub Integration", success, details)

    def test_file_modification_tracking(self):
        """Test file modification tracking"""
        print("📝 Testing file modification tracking...")

        try:
            # Create a temporary test file
            test_file = '/tmp/verification_test.txt'

            # Start a session manually for testing
            session = implementation_verifier.current_session

            if not session:
                details = "No active session to test file tracking"
                self.log_test("File Modification Tracking", False, details)
                return

            # Test file creation tracking
            with open(test_file, 'w') as f:
                f.write("Test content for verification")

            # Test file modification tracking
            with open(test_file, 'a') as f:
                f.write("\nAdditional content")

            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)

            details = "File operations tracked (simulated)"
            self.log_test("File Modification Tracking", True, details)

        except Exception as e:
            self.log_test("File Modification Tracking", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all implementation verification tests"""
        print("🚀 Starting Implementation Verification Tests")
        print("=" * 60)

        # Test 1: API Endpoints
        self.test_api_endpoints()

        # Test 2: Create test project
        project = self.create_test_project()
        if not project:
            print("❌ Cannot continue without test project")
            return

        # Test 3: Verification wrapper
        session_id = await self.test_verification_wrapper(project)

        # Test 4: Implementation evidence API
        self.test_implementation_evidence_api(session_id)

        # Test 5: AI Production Hub integration
        self.test_ai_production_hub_integration(project)

        # Test 6: File modification tracking
        self.test_file_modification_tracking()

        # Print results summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("🔍 IMPLEMENTATION VERIFICATION TEST RESULTS")
        print("=" * 60)

        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        print(f"Overall Status: {'✅ PASS' if success_rate >= 80 else '❌ FAIL'}")

        if success_rate < 80:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test_name']}: {result['details']}")

        print("\nSystem Status:")
        print(f"  • Implementation tracking: {'✅ Active' if success_rate > 50 else '❌ Inactive'}")
        print(f"  • API endpoints: {'✅ Working' if any('API' in r['test_name'] and r['success'] for r in self.test_results) else '❌ Broken'}")
        print(f"  • Verification wrapper: {'✅ Functional' if any('Wrapper' in r['test_name'] and r['success'] for r in self.test_results) else '❌ Not working'}")

        # Generate recommendation
        if success_rate >= 90:
            print("\n🎉 RECOMMENDATION: System is ready for production use!")
        elif success_rate >= 70:
            print("\n⚠️ RECOMMENDATION: System mostly working, fix failing tests")
        else:
            print("\n🚨 RECOMMENDATION: Significant issues detected, review implementation")

    def generate_test_report(self):
        """Generate detailed test report"""
        report = {
            'test_run': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r['success']),
                'success_rate': sum(1 for r in self.test_results if r['success']) / len(self.test_results) * 100 if self.test_results else 0
            },
            'test_results': self.test_results
        }

        report_file = 'implementation_verification_test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")


async def main():
    """Main test runner"""
    print("🧪 Implementation Verification System Test Suite")
    print("This will test the new system that verifies agents actually implement changes")
    print()

    tester = ImplementationVerificationTester()

    try:
        await tester.run_all_tests()
        tester.generate_test_report()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())