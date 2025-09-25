#!/usr/bin/env python3
"""
Debug consciousness data structure
"""
import asyncio
import websockets
import json

async def test_data_structure():
    uri = "ws://localhost:8000/ws/consciousness/"

    try:
        async with websockets.connect(uri) as websocket:
            print("🔌 Connected to consciousness WebSocket")

            # Get initial message
            message = await websocket.recv()
            data = json.loads(message)

            print("📊 Raw Data Structure:")
            print(json.dumps(data, indent=2))

            print("\n🔍 Data Fields Analysis:")
            if 'data' in data:
                d = data['data']
                print(f"  consciousness_level: {d.get('consciousness_level', 'MISSING')}")
                print(f"  system_health: {d.get('system_health', 'MISSING')}")
                print(f"  active_agents: {d.get('active_agents', 'MISSING')}")
                print(f"  memory_crystals: {d.get('memory_crystals', 'MISSING')}")
                print(f"  latest_insight: {d.get('latest_insight', 'MISSING')}")
            else:
                print("  No 'data' field found!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_data_structure())