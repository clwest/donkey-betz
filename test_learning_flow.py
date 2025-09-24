#!/usr/bin/env python3
"""
Test script to verify the complete learning metrics flow:
1. Execute an agent
2. Check Redis for updated stats
3. Verify API returns updated metrics
4. Check WebSocket broadcast
"""

import json
import requests
import redis
import time
import asyncio
import websockets
from datetime import datetime

def execute_agent():
    """Execute an agent and verify learning is tracked"""
    print("\n🚀 Executing test agent...")

    # Execute the business agent
    url = "http://localhost:8000/api/agents/execute/"
    payload = {
        "agent_type": "business_agent",
        "task": "test_learning_flow"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Agent executed: {result.get('agent')}")
            print(f"   Success: {result.get('success')}")
            print(f"   AI Used: {result.get('ai_used')}")
            return result
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error executing agent: {e}")
        return None


def check_redis_stats():
    """Check Redis for updated learning stats"""
    print("\n📊 Checking Redis stats...")

    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    # Check business agent stats
    stats = r.hgetall('agent:business_agent:stats')
    if stats:
        print(f"✅ Redis stats for business_agent:")
        print(f"   Real executions: {stats.get('real_executions', 0)}")
        print(f"   Last task: {stats.get('last_real_task', 'none')}")
        print(f"   Quality score: {stats.get('last_quality_score', 0)}")
        print(f"   Total lines: {stats.get('total_lines', 0)}")
        return True
    else:
        print("❌ No stats found in Redis")
        return False


def check_api_metrics():
    """Check if API returns updated metrics"""
    print("\n🌐 Checking API metrics...")

    response = requests.get("http://localhost:8000/api/learning/stats/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API metrics:")
        print(f"   Total real executions: {data.get('total_real_executions', 0)}")
        print(f"   Active agents: {data.get('active_agents', 0)}")
        print(f"   Average quality: {data.get('average_quality_score', 0)}")

        # Find business agent in list
        agents = data.get('agents', [])
        for agent in agents:
            if 'business' in agent.get('name', '').lower():
                print(f"   Business agent executions: {agent.get('real_executions', 0)}")
                break
        return True
    else:
        print(f"❌ API failed with status {response.status_code}")
        return False


async def check_websocket():
    """Check WebSocket for real-time updates"""
    print("\n🔌 Checking WebSocket updates...")

    try:
        async with websockets.connect('ws://localhost:8000/ws/ai-training/') as websocket:
            print("✅ Connected to WebSocket")

            # Send a ping
            await websocket.send(json.dumps({
                'type': 'ping',
                'timestamp': datetime.now().isoformat()
            }))

            # Listen for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)

            if data.get('type') == 'pong':
                print("✅ WebSocket responsive (got pong)")
            elif data.get('type') == 'connection':
                print("✅ WebSocket connection established")
            else:
                print(f"📦 Received: {data.get('type', 'unknown')}")

            return True

    except asyncio.TimeoutError:
        print("⏱️ WebSocket timeout (no real-time updates)")
        return False
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False


def main():
    """Run complete test flow"""
    print("=" * 60)
    print("🧪 TESTING LEARNING METRICS DATA FLOW")
    print("=" * 60)

    # Get initial Redis stats
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    initial_stats = r.hgetall('agent:business_agent:stats')
    initial_executions = int(initial_stats.get('real_executions', 0))
    print(f"\n📈 Initial real executions: {initial_executions}")

    # Execute agent
    result = execute_agent()

    if result:
        # Wait for async processing
        print("\n⏳ Waiting for data propagation...")
        time.sleep(2)

        # Check Redis
        check_redis_stats()

        # Verify execution count increased
        new_stats = r.hgetall('agent:business_agent:stats')
        new_executions = int(new_stats.get('real_executions', 0))

        if new_executions > initial_executions:
            print(f"\n✅ Learning tracked! Executions: {initial_executions} → {new_executions}")
        else:
            print(f"\n⚠️ Execution count unchanged: {new_executions}")

        # Check API
        check_api_metrics()

        # Check WebSocket
        asyncio.run(check_websocket())

    print("\n" + "=" * 60)
    print("✨ TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()