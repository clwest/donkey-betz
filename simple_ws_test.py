#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_connection():
    uri = "ws://localhost:8000/ws/income-builder/"
    print(f"🔌 Connecting to: {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Listen for initial message
            initial = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"📥 Initial: {initial}")

            # Send test message
            test_msg = {
                "type": "analyze_opportunities",
                "profile": {"id": "test", "skills": ["writing"]}
            }
            print(f"📤 Sending: {test_msg}")
            await websocket.send(json.dumps(test_msg))

            # Get response
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            print(f"📥 Response: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())