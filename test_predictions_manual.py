#!/usr/bin/env python3
"""Manual test for AI predictions WebSocket"""
import asyncio
import websockets
import json

async def test_predictions():
    uri = "ws://localhost:8000/ws/sports/"

    async with websockets.connect(uri) as websocket:
        print("✓ Connected to WebSocket")

        # Send get_predictions request
        msg = {"type": "get_predictions"}
        print(f"\n📤 Sending: {json.dumps(msg)}")
        await websocket.send(json.dumps(msg))

        # Wait for multiple responses (connection_established, then actual predictions)
        print("⏳ Waiting for responses...")
        for i in range(5):  # Read up to 5 messages
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                data = json.loads(response)

                print(f"\n📨 Received message {i+1}:")
                print(json.dumps(data, indent=2))

                # Check if this is the predictions response
                if data.get('type') == 'ai_predictions':
                    picks = data.get('data', {}).get('top_picks', [])
                    print(f"\n✓ Got {len(picks)} predictions!")
                    for pick in picks[:5]:
                        print(f"  - {pick['game']}: {pick['pick']} ({pick['confidence']}% confidence)")
                        print(f"    Reasoning: {pick.get('ai_reasoning', 'N/A')}")
                    break
                elif data.get('type') == 'error':
                    print(f"\n❌ Error: {data.get('message')}")
                    break
            except asyncio.TimeoutError:
                print(f"\n⏱️  Timeout waiting for message {i+1}")
                break

if __name__ == "__main__":
    asyncio.run(test_predictions())