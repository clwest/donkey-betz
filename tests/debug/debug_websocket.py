# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Debug WebSocket ping/pong to identify why pong responses aren't working.
"""

import asyncio
import websockets
import json
from datetime import datetime


async def debug_ping_pong():
    """Debug ping/pong behavior"""
    uri = "ws://localhost:8000/ws/live-sports/"
    
    try:
        print(f"[{datetime.now()}] Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now()}] ✅ Connected!")
            
            # Send ping and listen for immediate response
            print(f"[{datetime.now()}] 📤 Sending ping...")
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Listen for multiple messages with timeout
            for i in range(3):
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    print(f"[{datetime.now()}] 📥 Response {i+1}: {response}")
                except asyncio.TimeoutError:
                    print(f"[{datetime.now()}] ⏰ Timeout waiting for response {i+1}")
                    break
            
            # Test different message types
            messages = [
                {"type": "subscribe_sport", "sport": "nfl"},
                {"type": "unknown_type"},
                {"invalid": "json_without_type"}
            ]
            
            for msg in messages:
                print(f"[{datetime.now()}] 📤 Sending: {msg}")
                await websocket.send(json.dumps(msg))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    print(f"[{datetime.now()}] 📥 Response: {response}")
                except asyncio.TimeoutError:
                    print(f"[{datetime.now()}] ⏰ No response")
                    
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(debug_ping_pong())