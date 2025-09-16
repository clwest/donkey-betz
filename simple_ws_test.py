#!/usr/bin/env python3
"""
Simple WebSocket Connection Test
===============================

Test WebSocket connections without complex timeout parameters
to identify the root cause of frontend data flow issues.
"""

import asyncio
import websockets
import json
import time

async def test_basic_connection():
    """Test basic WebSocket connection to key endpoints"""

    endpoints = [
        "ws://localhost:8000/ws/income-builder/",
        "ws://localhost:8000/ws/revenue-dashboard/",
        "ws://localhost:8000/ws/neural-orchestra/",
        "ws://localhost:8000/ws/decision-command/",
    ]

    print("🔍 Testing WebSocket connections to key frontend components...\n")

    for endpoint in endpoints:
        component_name = endpoint.split('/')[-2].replace('-', ' ').title()
        print(f"Testing {component_name}: {endpoint}")

        try:
            # Simple connection without timeout parameter
            websocket = await websockets.connect(endpoint)
            print(f"✅ Connected successfully to {component_name}")

            # Try to send a basic message
            test_message = {"type": "get_data", "component": component_name.lower().replace(' ', '_')}
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent test message: {test_message}")

            # Wait for response (simple timeout using asyncio.wait_for)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"📨 Received response: {response[:100]}...")

                # Try to parse JSON
                try:
                    data = json.loads(response)
                    print(f"📊 Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                except json.JSONDecodeError:
                    print(f"⚠️ Non-JSON response received")

            except asyncio.TimeoutError:
                print(f"⏱️ No response received within 3 seconds")

            await websocket.close()
            print(f"🔌 Closed connection to {component_name}")

        except ConnectionRefusedError:
            print(f"❌ Connection refused - {component_name} endpoint not available")
        except websockets.exceptions.InvalidURI:
            print(f"❌ Invalid WebSocket URI for {component_name}")
        except websockets.exceptions.InvalidStatusCode as e:
            print(f"❌ Invalid status code for {component_name}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error for {component_name}: {type(e).__name__}: {e}")

        print("-" * 50)

async def main():
    """Run comprehensive WebSocket connectivity test"""
    print("🚀 Frontend Data Flow Resurrector - WebSocket Connectivity Test")
    print("=" * 60)

    # Test main endpoints
    await test_basic_connection()

if __name__ == "__main__":
    asyncio.run(main())
