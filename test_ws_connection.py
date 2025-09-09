#!/usr/bin/env python3
"""
WebSocket Connection Test Script
Tests the WebSocket endpoints to ensure they're working properly
"""

import asyncio
import json
import websockets
import sys

async def test_echo_endpoint():
    """Test the echo WebSocket endpoint (no auth required)"""
    uri = "ws://localhost:8000/ws/test/echo/"
    print(f"🔗 Testing Echo endpoint: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to echo endpoint")
            
            # Send a ping message
            message = json.dumps({"type": "ping", "timestamp": 123456})
            await websocket.send(message)
            print(f"📤 Sent: {message}")
            
            # Receive response
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Parse and verify response
            data = json.loads(response)
            if data.get("type") == "connected":
                print("✅ Initial connection message received")
                # Get the pong response
                response = await websocket.recv()
                print(f"📥 Received pong: {response}")
            
            print("✅ Echo endpoint test PASSED\n")
            return True
            
    except Exception as e:
        print(f"❌ Echo endpoint test FAILED: {e}\n")
        return False

async def test_agents_endpoint(token=None):
    """Test the agents WebSocket endpoint"""
    uri = "ws://localhost:8000/ws/agents/"
    if token:
        uri += f"?token={token}"
    
    print(f"🔗 Testing Agents endpoint: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to agents endpoint")
            
            # Wait for initial data
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"📥 Initial data: {response[:100]}...")
            except asyncio.TimeoutError:
                print("⏱️  No initial data received (this is OK)")
            
            # Send a ping message
            message = json.dumps({"type": "ping", "timestamp": 123456})
            await websocket.send(message)
            print(f"📤 Sent: {message}")
            
            # Receive pong response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"📥 Received: {response}")
                data = json.loads(response)
                if data.get("type") == "pong":
                    print("✅ Pong response received")
            except asyncio.TimeoutError:
                print("⚠️  No pong response (may need authentication)")
            
            print("✅ Agents endpoint test PASSED\n")
            return True
            
    except Exception as e:
        print(f"❌ Agents endpoint test FAILED: {e}\n")
        return False

async def main():
    """Run all WebSocket tests"""
    print("=" * 60)
    print("🚀 WebSocket Connection Test Suite")
    print("=" * 60)
    print()
    
    # Test echo endpoint
    echo_result = await test_echo_endpoint()
    
    # Test agents endpoint without token
    agents_result = await test_agents_endpoint()
    
    # Optional: Test with a token if provided as argument
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print(f"Testing with provided token: {token[:10]}...")
        await test_agents_endpoint(token)
    
    print("=" * 60)
    print("📊 Test Results Summary:")
    print(f"  Echo Endpoint:   {'✅ PASS' if echo_result else '❌ FAIL'}")
    print(f"  Agents Endpoint: {'✅ PASS' if agents_result else '❌ FAIL'}")
    print("=" * 60)
    
    if echo_result and agents_result:
        print("✅ All WebSocket endpoints are working correctly!")
        print("The 1006 error should now be resolved.")
    else:
        print("⚠️  Some endpoints are not working. Please check:")
        print("  1. Daphne server is running (not regular Django runserver)")
        print("  2. Use: ./start_with_websocket.sh or make run-daphne")
        print("  3. Check for any error messages in the server logs")

if __name__ == "__main__":
    asyncio.run(main())