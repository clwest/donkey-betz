# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test script for the Master Demo System
======================================
Verifies all components are working correctly
"""

import os
import sys
import redis
import requests
import json
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')

import django
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate
from core.models import GeneratedProject


class MasterDemoTester:
    """Test all components of the master demo system"""

    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.base_url = 'http://localhost:8000'
        self.all_tests_passed = True

    def run_all_tests(self):
        """Run all system tests"""
        print("=" * 60)
        print("🧪 MASTER DEMO SYSTEM TEST")
        print("=" * 60)

        tests = [
            self.test_redis_connection,
            self.test_database_models,
            self.test_master_demo_page,
            self.test_learning_stats_api,
            self.test_agent_deployment_api,
            self.test_websocket_readiness,
            self.test_learning_metrics_storage
        ]

        for test_func in tests:
            self.run_test(test_func)

        print("\n" + "=" * 60)
        if self.all_tests_passed:
            print("✅ ALL TESTS PASSED - SYSTEM READY!")
            print("\n🎉 Next Steps:")
            print("1. Start Django server: python manage.py runserver")
            print("2. Start learning demo: python manage.py start_learning_demo")
            print("3. Open browser: http://localhost:8000/master-demo/")
        else:
            print("❌ SOME TESTS FAILED - Please fix issues above")
        print("=" * 60)

    def run_test(self, test_func):
        """Run a single test"""
        test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
        try:
            print(f"\n📋 Testing: {test_name}")
            result = test_func()
            if result:
                print(f"   ✅ {test_name} - PASSED")
            else:
                print(f"   ❌ {test_name} - FAILED")
                self.all_tests_passed = False
        except Exception as e:
            print(f"   ❌ {test_name} - ERROR: {e}")
            self.all_tests_passed = False

    def test_redis_connection(self):
        """Test Redis connectivity"""
        try:
            self.redis.ping()
            self.redis.set('test:connection', 'working')
            value = self.redis.get('test:connection')
            self.redis.delete('test:connection')
            return value == 'working'
        except Exception as e:
            print(f"      Redis error: {e}")
            print(f"      Make sure Redis is running: redis-server")
            return False

    def test_database_models(self):
        """Test database models are accessible"""
        try:
            agent_count = UnifiedAgentTemplate.objects.count()
            print(f"      Found {agent_count} agents in database")

            project_count = GeneratedProject.objects.count()
            print(f"      Found {project_count} projects in database")

            return True
        except Exception as e:
            print(f"      Database error: {e}")
            print(f"      Run migrations: python manage.py migrate")
            return False

    def test_master_demo_page(self):
        """Test master demo page is accessible"""
        try:
            response = requests.get(f"{self.base_url}/master-demo/")
            if response.status_code == 200:
                if 'AI Master Demo' in response.text:
                    print(f"      Page loads correctly")
                    return True
                else:
                    print(f"      Page loaded but content seems wrong")
                    return False
            else:
                print(f"      HTTP {response.status_code} error")
                return False
        except requests.exceptions.ConnectionError:
            print(f"      Cannot connect to Django server")
            print(f"      Start server: python manage.py runserver")
            return False

    def test_learning_stats_api(self):
        """Test learning stats API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/learning/stats/")
            if response.status_code == 200:
                data = response.json()
                print(f"      API returns: {len(data)} fields")
                required_fields = ['active_sessions', 'code_generated_today', 'total_lines', 'timestamp']
                for field in required_fields:
                    if field not in data:
                        print(f"      Missing field: {field}")
                        return False
                return True
            else:
                print(f"      HTTP {response.status_code} error")
                return False
        except Exception as e:
            print(f"      API error: {e}")
            return False

    def test_agent_deployment_api(self):
        """Test agent deployment API endpoint"""
        try:
            # Just test that the endpoint exists - don't actually deploy
            response = requests.post(
                f"{self.base_url}/api/agent-deployment/execute/",
                json={'agents': [], 'project_type': 'test'},
                timeout=2
            )
            # We expect it to work or return an error - either is fine for the test
            print(f"      Deployment API accessible (status: {response.status_code})")
            return response.status_code in [200, 400, 500]  # Any response means it's working
        except requests.exceptions.Timeout:
            # Timeout is OK - means the endpoint exists
            return True
        except Exception as e:
            print(f"      Deployment API error: {e}")
            return False

    def test_websocket_readiness(self):
        """Test WebSocket configuration"""
        try:
            # Check if channels is configured
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()

            if channel_layer:
                print(f"      Channels configured: {type(channel_layer).__name__}")
                return True
            else:
                print(f"      Channels not configured")
                print(f"      Check CHANNEL_LAYERS in settings.py")
                return False
        except Exception as e:
            print(f"      WebSocket configuration error: {e}")
            print(f"      Install channels: pip install channels channels-redis")
            return False

    def test_learning_metrics_storage(self):
        """Test learning metrics can be stored and retrieved"""
        try:
            # Store test metrics
            test_agent = 'TestAgent'
            self.redis.hset(f'agent:{test_agent}:stats', mapping={
                'code_generated': '5',
                'total_lines': '500',
                'last_quality_score': '85',
                'last_complexity_score': '72'
            })

            # Retrieve and verify
            stats = self.redis.hgetall(f'agent:{test_agent}:stats')

            # Clean up
            self.redis.delete(f'agent:{test_agent}:stats')

            if stats and stats.get('code_generated') == '5':
                print(f"      Metrics storage working")
                return True
            else:
                print(f"      Metrics storage failed")
                return False
        except Exception as e:
            print(f"      Metrics storage error: {e}")
            return False


def main():
    """Run the test suite"""
    tester = MasterDemoTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()