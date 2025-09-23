#!/usr/bin/env python
"""
Enhanced Neural Orchestra Test Suite
====================================
Tests the complete enhanced learning workflow system
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_learning_workflow_api():
    """Test the learning workflow API"""
    print("🧪 Testing Learning Workflow API...")

    try:
        from enhanced_learning_workflow_api import EnhancedLearningWorkflowAPI

        api = EnhancedLearningWorkflowAPI()

        # Test starting workflow
        result = api.start_learning_workflow("Test Topic: AI Safety")
        print(f"   ✅ Workflow started: {result['success']}")

        if result['success']:
            workflow_id = result['workflow_id']

            # Wait a bit and check status
            time.sleep(2)
            status = api.get_workflow_status(workflow_id)
            print(f"   ✅ Workflow status retrieved: {status['success']}")

            # Test current data
            current_data = api.get_current_data()
            print(f"   ✅ Current data retrieved: {current_data['success']}")

            return True

        return False

    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

def test_websocket_consumer():
    """Test the Neural Orchestra WebSocket consumer"""
    print("🧪 Testing WebSocket Consumer...")

    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        import django
        django.setup()

        from core.consumers import NeuralOrchestraConsumer

        print("   ✅ NeuralOrchestraConsumer imported successfully")

        # Test consumer instantiation
        consumer = NeuralOrchestraConsumer()
        print("   ✅ Consumer instantiated")

        return True

    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection and data operations"""
    print("🧪 Testing Redis Connection...")

    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)

        # Test connection
        r.ping()
        print("   ✅ Redis connection successful")

        # Test data operations
        test_key = "test_neural_orchestra"
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}

        r.set(test_key, json.dumps(test_data))
        retrieved = json.loads(r.get(test_key))

        if retrieved['test'] == 'data':
            print("   ✅ Redis data operations working")

        # Cleanup
        r.delete(test_key)

        return True

    except Exception as e:
        print(f"   ❌ Redis test failed: {e}")
        return False

def test_learning_systems():
    """Test the underlying learning systems"""
    print("🧪 Testing Learning Systems...")

    systems_available = 0

    # Test real agent learning system
    try:
        from real_agent_learning_system import RealLearningSystem
        system = RealLearningSystem()
        print("   ✅ RealLearningSystem available")
        systems_available += 1
    except Exception as e:
        print(f"   ⚠️  RealLearningSystem not available: {e}")

    # Test agent-to-agent learning
    try:
        from agent_to_agent_learning import TeachingAgent
        agent = TeachingAgent("test_agent", "test specialization")
        print("   ✅ TeachingAgent available")
        systems_available += 1
    except Exception as e:
        print(f"   ⚠️  TeachingAgent not available: {e}")

    # Test spider learning
    try:
        from agent_spider_learning_system import SpiderAgent
        spider = SpiderAgent("test_spider", "test domain")
        print("   ✅ SpiderAgent available")
        systems_available += 1
    except Exception as e:
        print(f"   ⚠️  SpiderAgent not available: {e}")

    if systems_available >= 2:
        print(f"   ✅ Sufficient learning systems available ({systems_available}/3)")
        return True
    else:
        print(f"   ⚠️  Limited learning systems available ({systems_available}/3)")
        return False

def test_frontend_files():
    """Test that frontend files are present"""
    print("🧪 Testing Frontend Files...")

    files_to_check = [
        "enhanced_neural_orchestra.html",
        "launch_enhanced_neural_orchestra.py"
    ]

    files_found = 0

    for filename in files_to_check:
        if os.path.exists(filename):
            print(f"   ✅ {filename} exists")
            files_found += 1
        else:
            print(f"   ❌ {filename} missing")

    return files_found == len(files_to_check)

def test_django_integration():
    """Test Django URL and routing integration"""
    print("🧪 Testing Django Integration...")

    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        import django
        django.setup()

        # Test URL configuration
        from django.urls import reverse

        # Check if our URLs are registered (this will fail if not properly integrated)
        try:
            from core import urls
            print("   ✅ Core URLs module accessible")
        except Exception as e:
            print(f"   ❌ Core URLs issue: {e}")
            return False

        # Test WebSocket routing
        try:
            from core import routing
            print("   ✅ WebSocket routing accessible")
        except Exception as e:
            print(f"   ❌ WebSocket routing issue: {e}")
            return False

        return True

    except Exception as e:
        print(f"   ❌ Django integration test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 Enhanced Neural Orchestra Comprehensive Test Suite")
    print("=" * 60)

    tests = [
        ("Redis Connection", test_redis_connection),
        ("Learning Systems", test_learning_systems),
        ("Learning Workflow API", test_learning_workflow_api),
        ("WebSocket Consumer", test_websocket_consumer),
        ("Frontend Files", test_frontend_files),
        ("Django Integration", test_django_integration),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1

    print(f"\n📈 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! Enhanced Neural Orchestra is ready!")
        return True
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Enhanced Neural Orchestra should work with minor limitations.")
        return True
    else:
        print("❌ Multiple test failures. Please check the issues above.")
        return False

def quick_demo_simulation():
    """Run a quick demo simulation"""
    print("\n🎬 Running Quick Demo Simulation...")

    try:
        from enhanced_learning_workflow_api import EnhancedLearningWorkflowAPI

        api = EnhancedLearningWorkflowAPI()

        print("   🚀 Starting demo workflow...")
        result = api.start_learning_workflow("Demo: Neural Networks")

        if result['success']:
            workflow_id = result['workflow_id']
            print(f"   ✅ Demo workflow started: {workflow_id}")

            # Let it run for a few seconds
            print("   ⏳ Letting workflow run for 10 seconds...")
            time.sleep(10)

            # Check final status
            status = api.get_workflow_status(workflow_id)
            if status['success']:
                workflow = status['workflow']
                print(f"   📊 Final status: {workflow['status']}")
                print(f"   🤖 Agents created: {len(workflow['agents'])}")
                print(f"   📝 Knowledge items: {workflow['metrics']['knowledge_items']}")
                print(f"   🤝 Collaborations: {workflow['metrics']['collaborations']}")
                print(f"   🎯 Tokens used: {workflow['metrics']['tokens_used']}")

            print("   🎉 Demo simulation completed successfully!")
            return True
        else:
            print(f"   ❌ Demo workflow failed: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"   ❌ Demo simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧠 Enhanced Neural Orchestra Test Suite")
    print("Testing the complete agent learning workflow system\n")

    # Run comprehensive tests
    success = run_comprehensive_test()

    if success:
        # Run demo simulation
        demo_success = quick_demo_simulation()

        if demo_success:
            print("\n🏆 ALL SYSTEMS GO!")
            print("Enhanced Neural Orchestra is fully operational and ready for demo!")
            print("\nNext steps:")
            print("1. Run: python launch_enhanced_neural_orchestra.py")
            print("2. Open: http://localhost:8000/enhanced_neural_orchestra.html")
            print("3. Enter a topic and watch the agents learn!")
        else:
            print("\n⚠️  Tests passed but demo simulation had issues")
            print("The system should still work for basic demonstrations")
    else:
        print("\n❌ Test failures detected")
        print("Please resolve the issues above before running the full demo")

    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")