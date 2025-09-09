#!/usr/bin/env python3
"""
WebSocket Connection Test Script

Tests WebSocket connectivity to the Unified Donkey Betz Platform.
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime

async def test_websocket_endpoint(uri, test_name):
    """Test a single WebSocket endpoint"""
    print(f"\n=== Testing {test_name} ===")
    print(f"URI: {uri}")
    
    try:
        # Connect to WebSocket
        print("Attempting connection...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")
            
            # Send a ping message
            ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
            await websocket.send(json.dumps(ping_message))
            print(f"📤 Sent: {ping_message}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                print(f"📥 Received: {response_data}")
                
                # Check if we got a pong response
                if response_data.get("type") == "pong":
                    print("✅ Ping-pong test successful!")
                    return True
                elif response_data.get("type") == "error":
                    print(f"❌ Server returned error: {response_data.get('message')}")
                    return False
                else:
                    print(f"ℹ️  Received different response type: {response_data.get('type')}")
                    return True
                    
            except asyncio.TimeoutError:
                print("⚠️  No response received within timeout")
                return False
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Connection closed: {e}")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False
    except websockets.exceptions.InvalidURI as e:
        print(f"❌ Invalid URI: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

async def main():
    """Test all WebSocket endpoints"""
    print("🚀 Starting WebSocket Connectivity Tests")
    print("=" * 50)
    
    base_url = "ws://localhost:8000"
    
    # Test endpoints to check
    test_endpoints = [
        # Test endpoint (no auth)
        (f"{base_url}/ws/test/echo/", "Echo Test (No Auth)"),
        
        # Content Management WebSockets
        (f"{base_url}/ws/content/processing/", "Content Processing"),
        (f"{base_url}/ws/content/analytics/", "Content Analytics"),
        
        # Agent System WebSockets
        (f"{base_url}/ws/agents/execution/", "Agent Execution"),
        (f"{base_url}/ws/agents/orchestration/", "Agent Orchestration"),
        
        # Sports Analytics WebSockets
        (f"{base_url}/ws/sports/arbitrage/", "Sports Arbitrage"),
        (f"{base_url}/ws/sports/recommendations/", "Sports Recommendations"),
        (f"{base_url}/ws/sports/dashboard/", "Sports Dashboard"),
    ]
    
    results = {}
    
    for uri, test_name in test_endpoints:
        success = await test_websocket_endpoint(uri, test_name)
        results[test_name] = success
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🏁 WebSocket Test Results Summary")
    print("=" * 50)
    
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if success:
            successful_tests += 1
    
    print("-" * 50)
    print(f"Results: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All WebSocket endpoints are working!")
        sys.exit(0)
    elif successful_tests > 0:
        print("⚠️  Some WebSocket endpoints are working")
        sys.exit(1)
    else:
        print("💥 No WebSocket endpoints are working")
        sys.exit(2)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test script failed: {e}")
        sys.exit(1)