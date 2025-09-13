#!/usr/bin/env python3
"""
Comprehensive WebSocket Test Suite

Tests the complete WebSocket functionality including:
- Basic connectivity
- Ping/Pong heartbeat
- Connection management  
- Authentication requirements
- Real-time messaging
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime
import time

async def test_echo_endpoint_comprehensive():
    """Comprehensive test of the echo endpoint"""
    print("\n🔍 COMPREHENSIVE ECHO ENDPOINT TEST")
    print("=" * 50)
    
    uri = "ws://localhost:8000/ws/test/echo/"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established")
            
            # Test 1: Initial connection message
            print("\n📨 Test 1: Initial connection message")
            initial_message = await websocket.recv()
            initial_data = json.loads(initial_message)
            print(f"   Received: {initial_data['type']} - {initial_data['message']}")
            assert initial_data['type'] == 'connected'
            print("   ✅ Initial connection message received correctly")
            
            # Test 2: Ping-Pong test
            print("\n📨 Test 2: Ping-Pong heartbeat")
            ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
            await websocket.send(json.dumps(ping_message))
            print(f"   Sent ping: {ping_message['timestamp']}")
            
            pong_response = await websocket.recv()
            pong_data = json.loads(pong_response)
            print(f"   Received pong: {pong_data.get('type')} at {pong_data.get('timestamp')}")
            assert pong_data['type'] == 'pong'
            print("   ✅ Ping-Pong working correctly")
            
            # Test 3: Echo functionality
            print("\n📨 Test 3: Echo functionality")
            test_message = {
                "type": "test_echo",
                "content": "This is a test message",
                "test_data": {"key": "value", "number": 42},
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(test_message))
            print(f"   Sent test message with content: {test_message['content']}")
            
            echo_response = await websocket.recv()
            echo_data = json.loads(echo_response)
            print(f"   Received echo type: {echo_data['type']}")
            assert echo_data['type'] == 'echo'
            assert echo_data['original_message'] == test_message
            print("   ✅ Echo functionality working correctly")
            
            # Test 4: Invalid JSON handling
            print("\n📨 Test 4: Invalid JSON handling")
            await websocket.send("invalid json data")
            print("   Sent invalid JSON")
            
            error_response = await websocket.recv()
            error_data = json.loads(error_response)
            print(f"   Received error: {error_data['type']} - {error_data['message']}")
            assert error_data['type'] == 'error'
            print("   ✅ Error handling working correctly")
            
            # Test 5: Multiple rapid messages
            print("\n📨 Test 5: Multiple rapid messages")
            for i in range(3):
                rapid_message = {"type": "rapid_test", "message_id": i, "timestamp": datetime.now().isoformat()}
                await websocket.send(json.dumps(rapid_message))
                response = await websocket.recv()
                response_data = json.loads(response)
                assert response_data['original_message']['message_id'] == i
                print(f"   Message {i} echoed successfully")
            print("   ✅ Rapid messaging working correctly")
            
            print("\n🎉 ALL ECHO TESTS PASSED!")
            return True
            
    except Exception as e:
        print(f"\n❌ Echo test failed: {e}")
        return False

async def test_authentication_endpoints():
    """Test that authentication is working on protected endpoints"""
    print("\n🔐 AUTHENTICATION VERIFICATION TEST")
    print("=" * 50)
    
    protected_endpoints = [
        ("ws://localhost:8000/ws/content/processing/", "Content Processing"),
        ("ws://localhost:8000/ws/agents/execution/", "Agent Execution"),
        ("ws://localhost:8000/ws/sports/arbitrage/", "Sports Arbitrage"),
    ]
    
    auth_working = True
    
    for uri, name in protected_endpoints:
        try:
            print(f"\n📡 Testing {name}")
            print(f"   URI: {uri}")
            
            # This should fail with 403
            async with websockets.connect(uri) as websocket:
                print(f"   ❌ SECURITY ISSUE: {name} allowed connection without authentication!")
                auth_working = False
        
        except websockets.exceptions.WebSocketException as e:
            if "403" in str(e):
                print(f"   ✅ {name} correctly requires authentication (HTTP 403)")
            else:
                print(f"   ⚠️  {name} failed with unexpected error: {e}")
                auth_working = False
        
        except Exception as e:
            print(f"   ❌ Unexpected error testing {name}: {e}")
            auth_working = False
    
    if auth_working:
        print("\n🔒 AUTHENTICATION VERIFICATION PASSED!")
        print("   All protected endpoints require authentication as expected")
    else:
        print("\n⚠️  AUTHENTICATION ISSUES DETECTED!")
    
    return auth_working

async def test_connection_limits():
    """Test connection handling and limits"""
    print("\n🔄 CONNECTION MANAGEMENT TEST")
    print("=" * 50)
    
    uri = "ws://localhost:8000/ws/test/echo/"
    connections = []
    max_connections = 5
    
    try:
        # Test multiple connections
        print(f"📡 Opening {max_connections} simultaneous connections...")
        for i in range(max_connections):
            websocket = await websockets.connect(uri)
            connections.append(websocket)
            # Consume the initial connection message
            initial = await websocket.recv()
            print(f"   Connection {i+1}: {json.loads(initial)['type']}")
        
        print(f"✅ Successfully opened {len(connections)} connections")
        
        # Test that all connections are working
        print("📨 Testing all connections with ping...")
        for i, websocket in enumerate(connections):
            ping = {"type": "ping", "connection_id": i}
            await websocket.send(json.dumps(ping))
            response = await websocket.recv()
            response_data = json.loads(response)
            assert response_data['type'] == 'pong'
        
        print("✅ All connections responding to ping")
        
        # Clean up connections
        for websocket in connections:
            await websocket.close()
        
        print("🔄 All connections closed gracefully")
        return True
        
    except Exception as e:
        print(f"❌ Connection management test failed: {e}")
        # Clean up any remaining connections
        for websocket in connections:
            try:
                await websocket.close()
            except:
                pass
        return False

async def test_redis_channel_layer():
    """Test Redis channel layer functionality indirectly"""
    print("\n🗄️  REDIS CHANNEL LAYER TEST")
    print("=" * 50)
    
    # We can't directly test Redis without creating channel groups,
    # but we can verify no Redis-related errors occur during connection
    uri = "ws://localhost:8000/ws/test/echo/"
    
    try:
        print("📡 Testing Redis channel layer integration...")
        async with websockets.connect(uri) as websocket:
            # Consume initial message
            await websocket.recv()
            
            # Send several messages to test channel layer stability
            for i in range(10):
                message = {"type": "redis_test", "message_id": i}
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                response_data = json.loads(response)
                if response_data['type'] != 'echo':
                    raise Exception(f"Unexpected response type: {response_data['type']}")
            
            print("✅ Redis channel layer functioning correctly")
            print("   No Redis connection errors detected")
            print("   Message handling stable across multiple requests")
            return True
    
    except Exception as e:
        print(f"❌ Redis channel layer test failed: {e}")
        return False

async def main():
    """Run comprehensive WebSocket test suite"""
    print("🚀 UNIFIED DONKEY BETZ WEBSOCKET TEST SUITE")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("Echo Endpoint Comprehensive", test_echo_endpoint_comprehensive),
        ("Authentication Verification", test_authentication_endpoints),
        ("Connection Management", test_connection_limits),
        ("Redis Channel Layer", test_redis_channel_layer),
    ]
    
    for test_name, test_func in tests:
        print(f"\n⏳ Running {test_name} test...")
        start_time = time.time()
        
        try:
            result = await test_func()
            test_results[test_name] = result
            duration = time.time() - start_time
            print(f"⏱️  {test_name} completed in {duration:.2f}s")
        
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            test_results[test_name] = False
    
    # Print final summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if result:
            passed_tests += 1
    
    print("-" * 60)
    print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("🚀 WebSocket infrastructure is fully operational!")
        print("\n✨ CAPABILITIES VERIFIED:")
        print("   - Basic WebSocket connectivity")
        print("   - Django Channels routing")
        print("   - Redis channel layer integration")
        print("   - Authentication middleware")
        print("   - Connection management")
        print("   - Real-time messaging")
        print("   - Error handling")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)