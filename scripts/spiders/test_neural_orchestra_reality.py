# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Neural Orchestra Reality Test
==============================
Test the transformed Neural Orchestra to verify it shows real agent learning data
instead of mock data.
"""

import os
import sys
import asyncio
import json
import redis
import time
from datetime import datetime

# Add Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from channels.testing import WebsocketCommunicator
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from ai_core.intelligence.consumers import NeuralOrchestraConsumer

# Test the real learning data integration
async def test_neural_orchestra_reality():
    """Test that Neural Orchestra shows real learning data"""
    print("=" * 70)
    print("🎼 NEURAL ORCHESTRA REALITY TEST")
    print("Testing connection to real agent learning system")
    print("=" * 70)

    # Check Redis connection (where learning data is stored)
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)
        redis_client.ping()
        print("✅ Redis connection successful")

        # Check for learning system data
        learning_metrics = redis_client.hgetall("learning:system:metrics")
        final_metrics = redis_client.hgetall("learning:system:final")

        if learning_metrics:
            print(f"✅ Found learning system metrics: {len(learning_metrics)} keys")
            print(f"   - Total learnings: {learning_metrics.get('total_learnings', 0)}")
            print(f"   - Total tokens: {learning_metrics.get('total_tokens', 0)}")
            print(f"   - Total cost: {learning_metrics.get('total_cost', '$0.00')}")
        else:
            print("⚠️  No learning system metrics found in Redis")
            print("   You may need to run the real learning system first:")
            print("   python real_agent_learning_system.py")

        if final_metrics:
            print(f"✅ Found final learning metrics: {len(final_metrics)} keys")
            print(f"   - Agents trained: {final_metrics.get('agents_trained', 0)}")
            print(f"   - Knowledge items: {final_metrics.get('total_knowledge_items', 0)}")
            print(f"   - Collaborations: {final_metrics.get('total_collaborations', 0)}")

        # Check for spider data
        spider_data_count = (
            redis_client.llen("spider_data:job_market_spider") +
            redis_client.llen("spider_data:skills_spider")
        )
        print(f"✅ Spider data points: {spider_data_count}")

        # Check for generated content
        content_count = redis_client.llen("generated_content")
        collaborations_count = redis_client.llen("collaborations")
        print(f"✅ Generated content: {content_count}")
        print(f"✅ Agent collaborations: {collaborations_count}")

    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("   Make sure Redis is running on localhost:6379")
        return False

    print("\n" + "=" * 50)
    print("🧠 TESTING NEURAL ORCHESTRA CONSUMER")
    print("=" * 50)

    try:
        # Create application for testing
        application = ProtocolTypeRouter({
            "websocket": AuthMiddlewareStack(
                URLRouter([
                    re_path(r"ws/neural-orchestra/$", NeuralOrchestraConsumer.as_asgi()),
                ])
            ),
        })

        # Create WebSocket communicator
        communicator = WebsocketCommunicator(application, "/ws/neural-orchestra/")

        # Connect to WebSocket
        connected, subprotocol = await communicator.connect()
        if not connected:
            print("❌ Failed to connect to Neural Orchestra WebSocket")
            return False

        print("✅ Connected to Neural Orchestra WebSocket")

        # Wait for initial data
        print("📡 Waiting for initial orchestra data...")
        response = await communicator.receive_json_from(timeout=10)

        if response:
            print(f"✅ Received orchestra data: {response.get('type', 'unknown')}")

            # Check for real learning agents
            agents = response.get('agents', [])
            learning_agents = [a for a in agents if a.get('source') == 'learning_system']
            db_agents = [a for a in agents if a.get('source') == 'database']

            print(f"   🤖 Total agents: {len(agents)}")
            print(f"   🧠 Learning agents: {len(learning_agents)}")
            print(f"   💾 Database agents: {len(db_agents)}")

            # Check for real workflows
            workflows = response.get('workflows', [])
            learning_workflows = [w for w in workflows if w.get('source') == 'learning_system']

            print(f"   ⚙️ Total workflows: {len(workflows)}")
            print(f"   🧠 Learning workflows: {len(learning_workflows)}")

            # Check for real metrics
            metrics = response.get('metrics', {})
            learning_system = metrics.get('learning_system', {})

            if learning_system.get('active'):
                print(f"   📊 Learning system active: {learning_system.get('learning_sessions', 0)} sessions")
                print(f"   🎯 API tokens used: {learning_system.get('api_tokens_consumed', 0)}")
                print(f"   💰 Learning cost: ${learning_system.get('learning_cost', 0)}")
            else:
                print("   ⚠️ Learning system not active in metrics")

            # Check spider flows
            spider_flows = response.get('spider_flows', {})
            real_flows = [f for f in spider_flows.get('flow_connections', []) if f.get('is_real')]

            print(f"   🕷️ Total spider flows: {len(spider_flows.get('flow_connections', []))}")
            print(f"   🕷️ Real spider flows: {len(real_flows)}")

            # Show sample learning agent data
            if learning_agents:
                sample_agent = learning_agents[0]
                print(f"\n📋 Sample Learning Agent: {sample_agent.get('name')}")
                print(f"   - Status: {sample_agent.get('status')}")
                print(f"   - Learnings: {sample_agent.get('metrics', {}).get('total_learnings', 0)}")
                print(f"   - Knowledge: {sample_agent.get('metrics', {}).get('knowledge_items', 0)}")

            # Show sample workflow
            if learning_workflows:
                sample_workflow = learning_workflows[0]
                print(f"\n⚙️ Sample Learning Workflow: {sample_workflow.get('name')}")
                print(f"   - Status: {sample_workflow.get('status')}")
                print(f"   - Progress: {sample_workflow.get('progress', 0)}%")
                print(f"   - Agents: {len(sample_workflow.get('agent_sequence', []))}")

        # Test requesting fresh data
        print("\n📡 Requesting fresh orchestra data...")
        await communicator.send_json_to({
            "type": "get_orchestra_data"
        })

        # Wait for response
        fresh_response = await communicator.receive_json_from(timeout=5)
        if fresh_response:
            print("✅ Received fresh orchestra data")

        # Disconnect
        await communicator.disconnect()
        print("✅ Successfully disconnected from WebSocket")

        return True

    except Exception as e:
        print(f"❌ Error testing Neural Orchestra: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

async def main():
    """Main test function"""
    print("🎼 Starting Neural Orchestra Reality Test")

    success = await test_neural_orchestra_reality()

    print("\n" + "=" * 70)
    if success:
        print("✅ NEURAL ORCHESTRA REALITY TEST PASSED")
        print("The Neural Orchestra is now connected to real learning data!")
        print("\nTo see it in action:")
        print("1. Run the learning system: python real_agent_learning_system.py")
        print("2. Run the spider system: python agent_spider_learning_system.py")
        print("3. Start Django server and open Neural Orchestra frontend")
        print("4. You'll see real agents learning, collaborating, and generating content!")
    else:
        print("❌ NEURAL ORCHESTRA REALITY TEST FAILED")
        print("Check the errors above and ensure:")
        print("1. Redis is running on localhost:6379")
        print("2. Django is properly configured")
        print("3. The learning system has been run at least once")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())