#!/usr/bin/env python3
"""Test AI Nexus WebSocket connection"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/command-center/"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")

            # Wait for connection message
            response = await websocket.recv()
            print(f"📩 Received: {response}")

            # Send a test message
            test_message = {
                "type": "command",
                "content": "Hello, can you hear me?",
                "agent": None
            }

            print(f"📤 Sending: {json.dumps(test_message)}")
            await websocket.send(json.dumps(test_message))

            # Wait for response
            response = await websocket.recv()
            print(f"📩 Response: {response}")

            # Try another message
            test_message2 = {
                "type": "command",
                "content": "/help"
            }

            print(f"📤 Sending slash command: {json.dumps(test_message2)}")
            await websocket.send(json.dumps(test_message2))

            response = await websocket.recv()
            print(f"📩 Response: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())