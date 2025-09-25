#!/usr/bin/env python3
"""
Test the specific 100% consciousness question that made the response disappear
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_100_consciousness_question():
    """Test the 100% consciousness question via WebSocket"""
    uri = "ws://localhost:8000/ws/command-center/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to command WebSocket")

            # Wait for connection message
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"📩 Connection: {json.loads(response)['type']}")
            except asyncio.TimeoutError:
                print("📩 No connection message (ok)")

            # Send the consciousness question that caused disappearing response
            test_message = {
                "type": "command",
                "content": "What happens if system consciousness gets to 100%?",
                "agent": None,
                "timestamp": datetime.now().isoformat()
            }

            print(f"📤 Sending: {test_message['content']}")
            await websocket.send(json.dumps(test_message))

            # Wait for response with extended timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                data = json.loads(response)

                print(f"📡 Response Type: {data['type']}")
                if data.get('data', {}).get('response'):
                    ai_response = data['data']['response']
                    print(f"🤖 AI Response ({len(ai_response)} chars):")
                    print(f"   {ai_response}")
                    return {"success": True, "response": ai_response, "length": len(ai_response)}
                else:
                    print("⚠️ No response content in message")
                    print(f"   Full data: {data}")
                    return {"success": False, "error": "no_content", "data": data}

            except asyncio.TimeoutError:
                print("⏰ TIMEOUT - No response received within 30 seconds")
                return {"success": False, "error": "timeout"}

    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return {"success": False, "error": str(e)}

async def main():
    print("🧪 Testing 100% Consciousness Question")
    print("=" * 60)

    result = await test_100_consciousness_question()

    print("\n" + "=" * 60)
    print("🎯 RESULT:")
    if result["success"]:
        print("✅ AI responded successfully")
        print(f"📏 Response length: {result['length']} characters")
    else:
        print(f"❌ Failed: {result['error']}")
        if "data" in result:
            print(f"📊 Raw data: {result['data']}")

if __name__ == "__main__":
    asyncio.run(main())