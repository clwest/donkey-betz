#!/usr/bin/env python3
"""
Test LiveSportsConsumer with authentication handling
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_live_sports_auth():
    """Test live sports with different auth scenarios"""
    
    # Test 1: No authentication
    print("=== Test 1: No Authentication ===")
    uri = "ws://localhost:8000/ws/live-sports/"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected without auth")
            
            # Check for any immediate messages
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"📥 Received: {msg}")
            except asyncio.TimeoutError:
                print("⏰ No immediate message")
            
            # Try sending a simple message  
            await websocket.send(json.dumps({"type": "ping"}))
            print("📤 Sent ping")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"📥 Response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response to ping")
                
            # Keep connection alive briefly
            await asyncio.sleep(2)
            print("✅ Connection stayed alive")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n=== Test 2: Check Server Response ===")
    # Test if server is responding at all to the endpoint
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Try HTTP request to see if route exists
            try:
                async with session.get('http://localhost:8000/ws/live-sports/') as resp:
                    print(f"HTTP response status: {resp.status}")
                    text = await resp.text()
                    print(f"HTTP response: {text[:200]}...")
            except Exception as e:
                print(f"HTTP test failed: {e}")
    except ImportError:
        print("aiohttp not available, skipping HTTP test")


if __name__ == "__main__":
    asyncio.run(test_live_sports_auth())