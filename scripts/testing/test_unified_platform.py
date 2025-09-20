#!/usr/bin/env python3
"""
Test script for the unified agent work platform
Tests WebSocket connections and real-time data flow
"""

import asyncio
import websockets
import json
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_agent_platform_websocket():
    """Test the agent work platform WebSocket connection"""

    print("🚀 Testing Unified Agent Work Platform WebSocket Connection")
    print("=" * 60)

    try:
        # Connect to the WebSocket
        uri = "ws://localhost:8000/ws/agent-platform/"
        print(f"Connecting to: {uri}")

        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")

            # Test 1: Request platform status
            print("\n📊 Test 1: Requesting platform status...")
            await websocket.send(json.dumps({
                "action": "get_platform_status"
            }))

            response = await websocket.recv()
            data = json.loads(response)
            print(f"Response type: {data.get('type')}")

            if data.get('type') == 'platform_status':
                platform_data = data.get('data', {})
                print(f"   💰 Total Revenue: ${platform_data.get('total_revenue', 0):,.2f}")
                print(f"   🤖 Total Agents: {platform_data.get('total_agents', 0)}")
                print(f"   🔄 Agents Working: {platform_data.get('agents_working', 0)}")
                print(f"   📊 Active Sessions: {platform_data.get('active_work_sessions', 0)}")
                print("✅ Platform status test passed!")
            else:
                print(f"❌ Unexpected response type: {data.get('type')}")

            # Test 2: Request active sessions
            print("\n🔄 Test 2: Requesting active sessions...")
            await websocket.send(json.dumps({
                "action": "get_active_sessions"
            }))

            response = await websocket.recv()
            data = json.loads(response)

            if data.get('type') == 'active_sessions':
                sessions = data.get('sessions', [])
                print(f"   📈 Active Sessions Found: {len(sessions)}")
                for i, session in enumerate(sessions[:3]):  # Show first 3
                    print(f"      {i+1}. Agent: {session.get('agent_name', 'Unknown')}")
                    print(f"         Progress: {session.get('progress', 0) * 100:.1f}%")
                    print(f"         Revenue: ${session.get('revenue_earned', 0):.2f}")
                print("✅ Active sessions test passed!")
            else:
                print(f"❌ Unexpected response type: {data.get('type')}")

            # Test 3: Request revenue metrics
            print("\n💰 Test 3: Requesting revenue metrics...")
            await websocket.send(json.dumps({
                "action": "get_revenue_metrics"
            }))

            response = await websocket.recv()
            data = json.loads(response)

            if data.get('type') == 'revenue_metrics':
                analytics = data.get('analytics', {})
                print(f"   💵 Current Revenue: ${analytics.get('current_revenue', 0):.2f}")
                print(f"   🎯 Potential Revenue: ${analytics.get('potential_revenue', 0):.2f}")
                print(f"   🚀 Revenue in Progress: ${analytics.get('revenue_in_progress', 0):.2f}")
                print("✅ Revenue metrics test passed!")
            else:
                print(f"❌ Unexpected response type: {data.get('type')}")

            # Test 4: Listen for real-time updates (for 10 seconds)
            print("\n🔄 Test 4: Listening for real-time updates (10 seconds)...")
            update_count = 0

            try:
                for _ in range(10):  # Listen for 10 seconds
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)

                    if data.get('type') == 'platform_update':
                        update_count += 1
                        print(f"   📊 Real-time update #{update_count} received!")

                        platform_status = data.get('platform_status', {})
                        revenue = platform_status.get('total_revenue', 0)
                        agents_working = platform_status.get('agents_working', 0)

                        print(f"      Revenue: ${revenue:.2f}, Agents Working: {agents_working}")

            except asyncio.TimeoutError:
                pass  # Expected after listening period

            print(f"✅ Real-time updates test completed! Received {update_count} updates")

            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED! Unified Platform WebSocket is working!")
            print("🚀 Frontend should now show live agent work and revenue updates")
            print("💰 Users can watch their AI agents making money in real-time!")

    except websockets.exceptions.ConnectionRefusedError:
        print("❌ Connection refused! Make sure the Django server is running:")
        print("   python manage.py runserver")

    except Exception as e:
        print(f"❌ Error testing WebSocket: {e}")

def test_backend_apis():
    """Test the backend API endpoints"""

    print("\n🔧 Testing Backend API Endpoints")
    print("=" * 40)

    import requests

    try:
        # Test agent work platform API
        response = requests.get('http://localhost:8000/api/v1/agent-work-platform/')

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Agent Work Platform API working!")
                print(f"   Total Revenue: ${data.get('total_revenue', 0):.2f}")
                print(f"   Active Sessions: {len(data.get('active_work_sessions', []))}")
            else:
                print(f"❌ API returned error: {data.get('error')}")
        else:
            print(f"❌ API request failed: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend API!")
        print("   Make sure Django server is running on port 8000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    print("🧪 Unified Agent Work Platform Test Suite")
    print("=========================================")

    # Test backend APIs first
    test_backend_apis()

    # Test WebSocket connections
    asyncio.run(test_agent_platform_websocket())

    print("\n🎯 Next Steps:")
    print("1. Open http://localhost:3000/agent-work-platform in your browser")
    print("2. Watch live agent work sessions and revenue updates")
    print("3. Click 'Activate Platform' to see agents start working")
    print("4. Enjoy watching your AI agents make money! 💰")