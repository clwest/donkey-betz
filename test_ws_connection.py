#!/usr/bin/env python3
"""
Test WebSocket connection to Neural Orchestra and plan review handler
"""

import asyncio
import json
import websockets
import time

async def test_neural_orchestra():
    print("Testing Neural Orchestra WebSocket connection...")

    try:
        uri = "ws://localhost:8000/ws/neural-orchestra/"

        async with websockets.connect(uri) as websocket:
            print("✅ Connected to Neural Orchestra WebSocket!")

            # Test 1: Send test message
            test_msg = {
                "type": "test",
                "message": "Hello Neural Orchestra!"
            }
            await websocket.send(json.dumps(test_msg))
            print("➡️  Sent test message")

            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"⬅️  Received: {response[:100]}...")
            except asyncio.TimeoutError:
                print("⚠️  No response to test message (timeout)")

            # Test 2: Send plan review request
            plan_review_msg = {
                "type": "get_plan_review",
                "plan_id": "test_plan_123"
            }
            await websocket.send(json.dumps(plan_review_msg))
            print("➡️  Sent plan review request")

            # Wait for plan review response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                if data.get('type') == 'plan_review':
                    print("✅ Received plan review response!")
                    if data.get('review'):
                        print(f"   - Advisor: {data['review'].get('advisor_name', 'Unknown')}")
                        print(f"   - Success Probability: {data['review'].get('success_probability', 0)}")
                else:
                    print(f"⬅️  Received: {data.get('type', 'unknown')} message")
            except asyncio.TimeoutError:
                print("⚠️  No response to plan review request (timeout)")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")

            print("\n✅ WebSocket connection test completed successfully!")

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket connection failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("NEURAL ORCHESTRA WEBSOCKET CONNECTION TEST")
    print("=" * 60)
    print()
    asyncio.run(test_neural_orchestra())
    print("\n" + "=" * 60)