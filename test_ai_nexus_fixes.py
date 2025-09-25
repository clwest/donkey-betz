#!/usr/bin/env python3
"""
Test script to verify AI Nexus fixes
"""
import asyncio
import websockets
import json
import requests
from datetime import datetime

async def test_consciousness_websocket():
    """Test consciousness WebSocket data"""
    uri = "ws://localhost:8000/ws/consciousness/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to consciousness WebSocket")

            # Wait for consciousness update
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)

            print(f"📡 Received: {data['type']}")
            if data.get('data'):
                consciousness_level = data['data'].get('consciousness_level', 'Unknown')
                active_spiders = data['data'].get('active_spiders', 'Unknown')
                print(f"🧠 Consciousness Level: {consciousness_level}%")
                print(f"🕷️ Active Spiders: {active_spiders}")

                return {
                    'consciousness_ws': True,
                    'consciousness_level': consciousness_level,
                    'active_spiders': active_spiders
                }
            else:
                print("⚠️ No consciousness data received")
                return {'consciousness_ws': True, 'data': False}

    except Exception as e:
        print(f"❌ Consciousness WebSocket failed: {e}")
        return {'consciousness_ws': False, 'error': str(e)}

async def test_command_websocket():
    """Test command WebSocket AI functionality"""
    uri = "ws://localhost:8000/ws/command-center/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to command WebSocket")

            # Wait for connection message
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"📩 Connection message: {json.loads(response)['type']}")
            except:
                pass  # No connection message is ok

            # Send AI command
            test_message = {
                "type": "command",
                "content": "What is the current date and time in MST?",
                "agent": None,
                "timestamp": datetime.now().isoformat()
            }

            await websocket.send(json.dumps(test_message))
            print("📤 Sent time query to AI")

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(response)

            print(f"📡 AI Response Type: {data['type']}")
            if data.get('data', {}).get('response'):
                ai_response = data['data']['response']
                print(f"🤖 AI Said: {ai_response[:100]}...")

                # Check if response includes time/date info
                has_time = any(word in ai_response.lower() for word in ['time', 'date', 'mst', 'mountain', '2024', '2025'])

                return {
                    'command_ws': True,
                    'ai_responded': True,
                    'has_time_info': has_time,
                    'response_length': len(ai_response)
                }
            else:
                print("⚠️ No AI response received")
                return {'command_ws': True, 'ai_responded': False}

    except Exception as e:
        print(f"❌ Command WebSocket failed: {e}")
        return {'command_ws': False, 'error': str(e)}

def test_http_endpoint():
    """Test HTTP fallback endpoint"""
    try:
        response = requests.post('http://localhost:8000/api/command/',
                               json={'command': 'What time is it?', 'agent': None},
                               timeout=10)

        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            print(f"✅ HTTP API working, response length: {len(ai_response)}")

            # Check if response has time info
            has_time = any(word in ai_response.lower() for word in ['time', 'date', 'mst', 'mountain'])

            return {
                'http_api': True,
                'has_time_info': has_time,
                'response': ai_response[:100] + '...' if len(ai_response) > 100 else ai_response
            }
        else:
            print(f"❌ HTTP API returned {response.status_code}")
            return {'http_api': False, 'status_code': response.status_code}

    except Exception as e:
        print(f"❌ HTTP API failed: {e}")
        return {'http_api': False, 'error': str(e)}

async def main():
    """Run all tests"""
    print("🧪 Testing AI Nexus fixes...")
    print("=" * 50)

    results = {}

    # Test consciousness WebSocket
    print("\n1. Testing Consciousness WebSocket...")
    results['consciousness'] = await test_consciousness_websocket()

    # Test command WebSocket
    print("\n2. Testing Command WebSocket...")
    results['command'] = await test_command_websocket()

    # Test HTTP fallback
    print("\n3. Testing HTTP Fallback...")
    results['http'] = test_http_endpoint()

    # Summary
    print("\n" + "=" * 50)
    print("🎯 TEST RESULTS SUMMARY:")
    print("=" * 50)

    # Consciousness WebSocket
    if results['consciousness'].get('consciousness_ws'):
        spiders = results['consciousness'].get('active_spiders', 'Unknown')
        level = results['consciousness'].get('consciousness_level', 'Unknown')
        print(f"✅ Consciousness WebSocket: {level}% consciousness, {spiders} spiders")
    else:
        print("❌ Consciousness WebSocket: Failed")

    # Command WebSocket
    if results['command'].get('command_ws') and results['command'].get('ai_responded'):
        has_time = results['command'].get('has_time_info', False)
        status = "✅ Working with time info" if has_time else "⚠️ Working but no time info"
        print(f"{status}: Command WebSocket AI")
    else:
        print("❌ Command WebSocket AI: Failed")

    # HTTP API
    if results['http'].get('http_api'):
        has_time = results['http'].get('has_time_info', False)
        status = "✅ Working with time info" if has_time else "⚠️ Working but no time info"
        print(f"{status}: HTTP API")
    else:
        print("❌ HTTP API: Failed")

    return results

if __name__ == "__main__":
    asyncio.run(main())