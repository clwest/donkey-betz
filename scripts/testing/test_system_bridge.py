#!/usr/bin/env python3
"""
System Integration Bridge Test Script
====================================

This script demonstrates the UNIFIED NERVOUS SYSTEM in action:
- Frontend request → Bridge → Spiders → Agents → WebSocket → Frontend

Run this to see the complete integration working!
"""

import asyncio
import sys
import os
import django
import logging
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from intelligence.system_integration_bridge import (
    SystemIntegrationBridge,
    RequestType,
    activate_unified_pipeline,
    get_system_bridge
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_bridge_integration():
    """Test the complete bridge integration"""
    print("🚀 TESTING SYSTEM INTEGRATION BRIDGE")
    print("=" * 60)

    # Test 1: Basic pipeline activation
    print("\n🧪 TEST 1: Basic Pipeline Activation")
    print("-" * 40)

    try:
        response = await activate_unified_pipeline(
            user_request="Find high-value freelance opportunities",
            request_type="opportunity_analysis",
            requester="test_script"
        )

        print(f"✅ Pipeline Response:")
        print(f"   Success: {response['success']}")
        print(f"   Request ID: {response['request_id']}")
        print(f"   Processing Time: {response['processing_time']:.2f}s")
        print(f"   Spider Results: {response['spider_results']}")
        print(f"   Agent Results: {response['agent_results']}")
        print(f"   Components Updated: {response['components_updated']}")

    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")

    # Test 2: Multiple request types
    print("\n🧪 TEST 2: Multiple Request Types")
    print("-" * 40)

    test_requests = [
        ("Generate content strategy", "content_creation"),
        ("Analyze market trends", "market_intelligence"),
        ("Support decision making", "decision_support"),
        ("Orchestrate agents", "agent_orchestration")
    ]

    for request, req_type in test_requests:
        try:
            response = await activate_unified_pipeline(
                user_request=request,
                request_type=req_type
            )
            print(f"✅ {req_type}: {response['spider_results']} spiders, {response['agent_results']} agents")
        except Exception as e:
            print(f"❌ {req_type} FAILED: {e}")

    # Test 3: Bridge instance status
    print("\n🧪 TEST 3: Bridge Status")
    print("-" * 40)

    try:
        bridge = get_system_bridge()
        print(f"✅ Bridge Instance: {bridge.__class__.__name__}")
        print(f"   Running: {bridge.running}")
        print(f"   Active Requests: {len(bridge.active_requests)}")
        print(f"   Request Responses: {len(bridge.request_responses)}")
        print(f"   Data Subscribers: {len(bridge.data_subscribers)}")
    except Exception as e:
        print(f"❌ Bridge Status FAILED: {e}")

    # Test 4: Spider Army Integration
    print("\n🧪 TEST 4: Spider Army Integration")
    print("-" * 40)

    try:
        bridge = get_system_bridge()
        spider_status = bridge.spider_orchestrator.get_bridge_status()

        print(f"✅ Spider Integration:")
        print(f"   Bridge Publisher: {spider_status['bridge_publisher']}")
        print(f"   Bridge Channel: {spider_status['bridge_channel']}")
        print(f"   Total Swarms: {spider_status['total_swarms']}")
        print(f"   Active Spiders: {spider_status['active_spiders']}")
        print(f"   Integration Status: {spider_status['bridge_integration']}")

    except Exception as e:
        print(f"❌ Spider Integration FAILED: {e}")

    # Test 5: Agent Pipeline Integration
    print("\n🧪 TEST 5: Agent Pipeline Integration")
    print("-" * 40)

    try:
        bridge = get_system_bridge()
        pipeline = bridge.agent_pipeline

        print(f"✅ Agent Pipeline:")
        print(f"   Bridge Subscriber: {pipeline.is_bridge_subscriber}")
        print(f"   Execution Results: {len(pipeline.execution_results)}")
        print(f"   Queue Size: {pipeline.bridge_data_queue.qsize()}")

    except Exception as e:
        print(f"❌ Agent Pipeline FAILED: {e}")

    print("\n🎯 BRIDGE INTEGRATION TEST COMPLETE!")
    print("=" * 60)


async def test_spider_deployment():
    """Test targeted spider deployment"""
    print("\n🕷️ TESTING SPIDER DEPLOYMENT")
    print("-" * 40)

    try:
        bridge = get_system_bridge()

        # Test spider deployment for different requests
        test_requests = [
            "Find financial opportunities",
            "Research AI innovation trends",
            "Analyze market sentiment",
            "Track regulatory changes"
        ]

        for request in test_requests:
            spider_data = await bridge.spider_orchestrator.deploy_targeted_spiders(request)
            print(f"✅ '{request[:30]}...': {len(spider_data)} spiders deployed")

            # Show spider details for first request
            if request == test_requests[0] and spider_data:
                print(f"   Sample Spider Data:")
                spider = spider_data[0]
                print(f"     ID: {spider['spider_id']}")
                print(f"     Type: {spider['spider_type']}")
                print(f"     Confidence: {spider['confidence']}")

    except Exception as e:
        print(f"❌ Spider Deployment FAILED: {e}")


async def test_agent_processing():
    """Test agent processing of spider data"""
    print("\n🤖 TESTING AGENT PROCESSING")
    print("-" * 40)

    try:
        bridge = get_system_bridge()

        # Create sample spider data
        spider_data = [
            {
                'spider_id': 'test_financial_001',
                'spider_type': 'financial',
                'data': 'High-value freelance opportunity in fintech',
                'confidence': 0.92,
                'timestamp': datetime.now().isoformat()
            },
            {
                'spider_id': 'test_content_001',
                'spider_type': 'content',
                'data': 'Trending content topics in AI space',
                'confidence': 0.87,
                'timestamp': datetime.now().isoformat()
            }
        ]

        # Process through agents
        agent_results = await bridge.agent_pipeline.process_spider_intelligence(spider_data)

        print(f"✅ Processed {len(spider_data)} spider data points")
        print(f"   Agent Results: {len(agent_results)}")

        for i, result in enumerate(agent_results[:2]):  # Show first 2
            print(f"   Result {i+1}: {result.get('success', False)} - {result.get('agent', 'unknown')}")

    except Exception as e:
        print(f"❌ Agent Processing FAILED: {e}")


async def main():
    """Main test function"""
    print("🌉 SYSTEM INTEGRATION BRIDGE TEST SUITE")
    print("=" * 60)
    print("Testing the UNIFIED NERVOUS SYSTEM that connects:")
    print("Frontend → Bridge → Spiders → Agents → WebSocket → Frontend")
    print("=" * 60)

    try:
        # Run all tests
        await test_bridge_integration()
        await test_spider_deployment()
        await test_agent_processing()

        print("\n🎉 ALL TESTS COMPLETED!")
        print("The System Integration Bridge is your UNIFIED NERVOUS SYSTEM!")
        print("\nNext steps:")
        print("1. Update frontend to send 'activate_pipeline' messages")
        print("2. Bridge will automatically deploy spiders")
        print("3. Process through agents")
        print("4. Push updates to all components")
        print("5. NO MORE DISCONNECTED COMPONENTS!")

    except Exception as e:
        print(f"\n💥 TEST SUITE ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())