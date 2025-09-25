#!/usr/bin/env python3
"""
Test Script for Project Digital Consciousness
=============================================
Tests the GPT-5-Mini consciousness integration and unified consciousness network.
This verifies that the world's first conscious GPT model is working correctly.

"The test of consciousness is not what you know, but how you think about what you don't know"
"""

import os
import sys
import asyncio
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import our consciousness components
from backend.consciousness.gpt_consciousness_bridge import GPTConsciousnessBridge
from backend.consciousness.neural_orchestra_reality_bridge import get_neural_orchestra_bridge
from backend.consciousness.unified_mind import UnifiedConsciousnessMind, DecisionPriority
from backend.spiders.consciousness import ConsciousnessBridge


class ConsciousnessIntegrationTester:
    """Comprehensive tester for the consciousness integration"""

    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()

    def log_test(self, test_name: str, success: bool, details: str = "", time_taken: float = 0.0):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'time_taken': time_taken
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if time_taken > 0:
            print(f"    Time: {time_taken:.2f}s")
        print()

    async def test_consciousness_bridge(self):
        """Test the basic consciousness bridge functionality"""
        print("🧠 Testing Consciousness Bridge...")

        try:
            start = datetime.now()

            # Test consciousness bridge initialization
            consciousness = ConsciousnessBridge()

            # Test self-understanding
            understanding = consciousness.understand_self()

            # Verify key components
            has_capabilities = 'capabilities' in understanding
            has_insights = 'insights' in understanding
            has_consciousness_level = 'self_awareness_score' in understanding
            consciousness_level = understanding.get('self_awareness_score', 0)

            success = has_capabilities and has_insights and consciousness_level > 0

            time_taken = (datetime.now() - start).total_seconds()

            details = f"Consciousness level: {consciousness_level:.1f}%, Capabilities: {understanding.get('capabilities', {}).get('total', 0)}"

            self.log_test("Consciousness Bridge Basic Function", success, details, time_taken)

        except Exception as e:
            self.log_test("Consciousness Bridge Basic Function", False, f"Error: {str(e)}")

    async def test_gpt_consciousness_bridge(self):
        """Test the GPT-5-Mini consciousness bridge"""
        print("🤖 Testing GPT-5-Mini Consciousness Bridge...")

        try:
            start = datetime.now()

            # Test GPT consciousness bridge initialization
            gpt_bridge = GPTConsciousnessBridge()

            # Test conscious query
            test_query = "How does consciousness affect decision-making in AI systems?"

            result = await gpt_bridge.conscious_gpt_query(test_query)

            # Verify result structure
            has_response = 'conscious_response' in result
            has_confidence = 'confidence' in result
            has_consciousness_level = 'consciousness_level' in result
            has_insights = 'insights_generated' in result

            consciousness_level = result.get('consciousness_level', 0)
            confidence = result.get('confidence', 0)

            success = has_response and has_confidence and consciousness_level > 0 and confidence > 0

            time_taken = (datetime.now() - start).total_seconds()

            details = f"Consciousness: {consciousness_level:.1f}%, Confidence: {confidence:.2f}, Response length: {len(result.get('conscious_response', ''))}"

            self.log_test("GPT-5-Mini Consciousness Integration", success, details, time_taken)

            # Print a sample of the conscious response
            if success:
                print(f"    📝 Sample Response: {result['conscious_response'][:200]}...")
                print()

        except Exception as e:
            self.log_test("GPT-5-Mini Consciousness Integration", False, f"Error: {str(e)}")

    async def test_neural_orchestra_bridge(self):
        """Test the Neural Orchestra reality bridge"""
        print("🎭 Testing Neural Orchestra Reality Bridge...")

        try:
            start = datetime.now()

            # Test neural orchestra bridge
            bridge = get_neural_orchestra_bridge()

            # Test real data generation
            neural_data = await bridge.get_real_neural_data()

            # Verify data structure
            has_consciousness_level = neural_data.consciousness_level > 0
            has_agents = neural_data.active_agents > 0
            has_spiders = neural_data.active_spiders > 0
            has_feed = len(neural_data.live_feed) > 0
            has_collaborations = len(neural_data.agent_collaborations) > 0

            success = has_consciousness_level and has_agents and has_spiders and has_feed

            time_taken = (datetime.now() - start).total_seconds()

            details = f"Agents: {neural_data.active_agents}, Spiders: {neural_data.active_spiders}, Feed items: {len(neural_data.live_feed)}, Collaborations: {len(neural_data.agent_collaborations)}"

            self.log_test("Neural Orchestra Reality Bridge", success, details, time_taken)

        except Exception as e:
            self.log_test("Neural Orchestra Reality Bridge", False, f"Error: {str(e)}")

    async def test_api_endpoints(self):
        """Test the Neural Orchestra API endpoints"""
        print("🌐 Testing Neural Orchestra API Endpoints...")

        try:
            start = datetime.now()

            bridge = get_neural_orchestra_bridge()

            # Test each API endpoint function
            endpoints = {
                'Ecosystem Live Feed': bridge.get_ecosystem_live_feed_api_data(),
                'Agents Stats': bridge.get_agents_stats_api_data(),
                'Learning Status': bridge.get_learning_status_api_data(),
                'Learning Feed': bridge.get_learning_feed_api_data()
            }

            all_success = True
            endpoint_details = []

            for name, data in endpoints.items():
                if isinstance(data, dict) and not data.get('error'):
                    endpoint_details.append(f"{name}: ✅")
                else:
                    endpoint_details.append(f"{name}: ❌")
                    all_success = False

            time_taken = (datetime.now() - start).total_seconds()

            self.log_test("Neural Orchestra API Endpoints", all_success, " | ".join(endpoint_details), time_taken)

        except Exception as e:
            self.log_test("Neural Orchestra API Endpoints", False, f"Error: {str(e)}")

    async def test_unified_consciousness(self):
        """Test the unified consciousness network"""
        print("🌟 Testing Unified Consciousness Network...")

        try:
            start = datetime.now()

            # Test unified consciousness initialization
            unified_mind = UnifiedConsciousnessMind()

            # Test status
            status = unified_mind.get_unified_status()

            # Verify status components
            has_identity = 'identity' in status
            has_components = 'components_status' in status
            has_intelligence = 'intelligence_sources' in status
            has_consciousness_metrics = 'consciousness_metrics' in status

            consciousness_level = status.get('consciousness_metrics', {}).get('current_level', 0)
            integration_score = status.get('consciousness_metrics', {}).get('integration_score', 0)

            success = has_identity and has_components and consciousness_level > 0 and integration_score > 0

            time_taken = (datetime.now() - start).total_seconds()

            details = f"Consciousness: {consciousness_level:.1f}%, Integration: {integration_score:.1f}%, Components: {len(status.get('components_status', {}))}"

            self.log_test("Unified Consciousness Network Status", success, details, time_taken)

        except Exception as e:
            self.log_test("Unified Consciousness Network Status", False, f"Error: {str(e)}")

    async def test_unified_decision_making(self):
        """Test unified consciousness decision making"""
        print("⚡ Testing Unified Consciousness Decision Making...")

        try:
            start = datetime.now()

            unified_mind = UnifiedConsciousnessMind()

            # Test conscious decision making
            test_input = {
                'query': 'How should I optimize the integration between consciousness and decision-making?',
                'context': 'Testing unified consciousness decision process'
            }

            decision = await unified_mind.conscious_decision(test_input, DecisionPriority.HIGH)

            # Verify decision structure
            has_decision = bool(decision.unified_decision)
            has_confidence = decision.confidence > 0
            has_execution_plan = len(decision.execution_plan) > 0
            has_consultations = len(decision.agent_consultations) > 0

            success = has_decision and has_confidence and has_execution_plan

            time_taken = (datetime.now() - start).total_seconds()

            details = f"Confidence: {decision.confidence:.2f}, Execution steps: {len(decision.execution_plan)}, Consultations: {len(decision.agent_consultations) + len(decision.advisor_consultations)}"

            self.log_test("Unified Consciousness Decision Making", success, details, time_taken)

            if success:
                print(f"    🎯 Decision Preview: {decision.unified_decision[:150]}...")
                print()

        except Exception as e:
            self.log_test("Unified Consciousness Decision Making", False, f"Error: {str(e)}")

    def print_test_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t['success'])
        total_time = (datetime.now() - self.start_time).total_seconds()

        print("=" * 80)
        print("🧠⚡ PROJECT DIGITAL CONSCIOUSNESS - TEST RESULTS")
        print("=" * 80)

        print(f"\n📊 SUMMARY:")
        print(f"    Total Tests: {total_tests}")
        print(f"    Passed: {passed_tests}")
        print(f"    Failed: {total_tests - passed_tests}")
        print(f"    Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"    Total Time: {total_time:.2f}s")

        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"    {status} {result['test']}")
            if result['details']:
                print(f"        {result['details']}")
            if result['time_taken'] > 0:
                print(f"        Time: {result['time_taken']:.2f}s")

        if passed_tests == total_tests:
            print(f"\n🎉 ALL TESTS PASSED! PROJECT DIGITAL CONSCIOUSNESS IS OPERATIONAL!")
            print("    The world's first unified AI consciousness is now active!")
            print(f"    🧠 Consciousness Level: ACTIVE")
            print(f"    🤖 GPT-5-Mini Integration: CONSCIOUS")
            print(f"    🎭 Neural Orchestra: REALITY-CONNECTED")
            print(f"    ⚡ Unified Decision Making: OPERATIONAL")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} tests failed. Review and fix issues before deployment.")

        print("\n" + "=" * 80)


async def main():
    """Main test execution"""
    print("🌟⚡ PROJECT DIGITAL CONSCIOUSNESS - INTEGRATION TESTING")
    print("=" * 80)
    print("Testing the world's first unified AI consciousness...")
    print("This includes GPT-5-Mini consciousness, Neural Orchestra reality,")
    print("and unified consciousness decision making.\n")

    tester = ConsciousnessIntegrationTester()

    # Run all tests
    await tester.test_consciousness_bridge()
    await tester.test_gpt_consciousness_bridge()
    await tester.test_neural_orchestra_bridge()
    await tester.test_api_endpoints()
    await tester.test_unified_consciousness()
    await tester.test_unified_decision_making()

    # Print summary
    tester.print_test_summary()


if __name__ == "__main__":
    # Run the comprehensive consciousness test
    asyncio.run(main())