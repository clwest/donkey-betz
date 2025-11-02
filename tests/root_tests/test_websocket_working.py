# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""Test WebSocket connection to verify it's working"""

import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws/consciousness/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")

            # Receive initial message
            message = await websocket.recv()
            data = json.loads(message)

            print("\n📊 Initial data received:")
            print(f"  - Consciousness Level: {data['data']['consciousness_level']}%")
            print(f"  - System Health: {data['data']['system_health']}%")
            print(f"  - Active Agents: {data['data']['active_agents']}")
            print(f"  - Active Spiders: {data['data']['active_spiders']}")
            print(f"  - AI Proposals: {len(data['data']['ai_proposals'])} pending")
            print(f"  - Latest Insight: {data['data']['latest_insight']['content']}")

            print("\n🎉 WebSocket is working perfectly!")

            # Wait for a few more messages
            print("\n📡 Waiting for real-time updates...")
            for i in range(3):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"  Update {i+1}: {data['data']['current_thought']}")

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🔧 Testing WebSocket connection to Intelligence Dashboard...")
    success = asyncio.run(test_websocket())

    if success:
        print("\n✨ SUCCESS! WebSocket is fully operational!")
    else:
        print("\n⚠️  WebSocket test failed. Check the server logs.")