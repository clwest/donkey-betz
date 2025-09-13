#!/usr/bin/env python3
"""
Test WebSocket connection to verify the fix for reconnection loops.
This script will test the /ws/live-sports/ endpoint.
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_live_sports_websocket():
    """Test the live sports WebSocket connection"""
    uri = "ws://localhost:8000/ws/live-sports/"
    
    try:
        print(f"[{datetime.now()}] Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now()}] ✅ Connected successfully!")
            
            # Wait for connection established message
            try:
                welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"[{datetime.now()}] Welcome message: {welcome_msg}")
            except asyncio.TimeoutError:
                print(f"[{datetime.now()}] ⚠️  No welcome message received within 5 seconds")
            
            # Send a ping message
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print(f"[{datetime.now()}] 📤 Sent ping message")
            
            # Wait for pong response
            try:
                pong_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"[{datetime.now()}] 📥 Received: {pong_msg}")
            except asyncio.TimeoutError:
                print(f"[{datetime.now()}] ⚠️  No pong response received within 5 seconds")
            
            # Subscribe to sports updates
            subscribe_msg = {"type": "subscribe_sport", "sport": "nfl"}
            await websocket.send(json.dumps(subscribe_msg))
            print(f"[{datetime.now()}] 📤 Sent subscription message")
            
            # Wait for subscription confirmation
            try:
                sub_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"[{datetime.now()}] 📥 Subscription response: {sub_msg}")
            except asyncio.TimeoutError:
                print(f"[{datetime.now()}] ⚠️  No subscription response received within 5 seconds")
            
            # Keep connection alive for 10 seconds to test stability
            print(f"[{datetime.now()}] 🔍 Testing connection stability for 10 seconds...")
            
            end_time = asyncio.get_event_loop().time() + 10
            while asyncio.get_event_loop().time() < end_time:
                try:
                    # Check if connection is still alive
                    await asyncio.sleep(1)
                    
                    # Send periodic ping every 3 seconds
                    if int(asyncio.get_event_loop().time()) % 3 == 0:
                        await websocket.send(json.dumps({"type": "ping"}))
                        print(f"[{datetime.now()}] ❤️  Heartbeat sent")
                        
                        # Check for any incoming messages
                        try:
                            msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                            print(f"[{datetime.now()}] 📥 Received: {msg}")
                        except asyncio.TimeoutError:
                            pass  # No message received, continue
                            
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"[{datetime.now()}] ❌ Connection closed unexpectedly: {e}")
                    return False
                except Exception as e:
                    print(f"[{datetime.now()}] ❌ Unexpected error: {e}")
                    return False
            
            print(f"[{datetime.now()}] ✅ Connection remained stable for 10 seconds!")
            return True
            
    except websockets.exceptions.ConnectionRefused:
        print(f"[{datetime.now()}] ❌ Connection refused. Is the server running on port 8000?")
        return False
    except websockets.exceptions.InvalidURI:
        print(f"[{datetime.now()}] ❌ Invalid WebSocket URI: {uri}")
        return False
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Unexpected error: {e}")
        return False


async def test_reconnection_behavior():
    """Test reconnection behavior by simulating multiple connection attempts"""
    uri = "ws://localhost:8000/ws/live-sports/"
    
    print(f"\n[{datetime.now()}] 🔄 Testing reconnection behavior...")
    
    for attempt in range(3):
        print(f"\n[{datetime.now()}] === Connection Attempt {attempt + 1} ===")
        
        try:
            async with websockets.connect(uri) as websocket:
                print(f"[{datetime.now()}] ✅ Connected on attempt {attempt + 1}")
                
                # Send a quick ping and wait for response
                await websocket.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"[{datetime.now()}] 📥 Received: {response}")
                
                # Wait 2 seconds then close
                await asyncio.sleep(2)
                print(f"[{datetime.now()}] 🔌 Closing connection {attempt + 1}")
                
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Connection {attempt + 1} failed: {e}")
        
        # Wait 1 second between attempts
        await asyncio.sleep(1)
    
    print(f"\n[{datetime.now()}] ✅ Reconnection test completed")


async def main():
    """Main test function"""
    print("🚀 WebSocket Connection Test Suite")
    print("==================================")
    
    # Test 1: Basic connection and stability
    print("\n📡 Test 1: Basic WebSocket Connection")
    success = await test_live_sports_websocket()
    
    if success:
        print("\n✅ Basic connection test PASSED")
    else:
        print("\n❌ Basic connection test FAILED")
        return
    
    # Test 2: Reconnection behavior
    print("\n📡 Test 2: Reconnection Behavior")
    await test_reconnection_behavior()
    
    print("\n🏁 All tests completed!")
    print("\nIf you see stable connections without rapid reconnect loops,")
    print("the WebSocket fix has been successful! 🎉")


if __name__ == "__main__":
    asyncio.run(main())