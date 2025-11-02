# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test the TestEchoConsumer to isolate WebSocket issues
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_echo_consumer():
    """Test the echo WebSocket consumer"""
    uri = "ws://localhost:8000/ws/test/echo/"
    
    try:
        print(f"[{datetime.now()}] Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now()}] ✅ Connected!")
            
            # Wait for welcome message
            try:
                welcome = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                print(f"[{datetime.now()}] 📥 Welcome: {welcome}")
            except asyncio.TimeoutError:
                print(f"[{datetime.now()}] ⏰ No welcome message")
            
            # Send test messages
            test_messages = [
                "Hello World",
                json.dumps({"type": "ping"}),
                json.dumps({"test": "message"})
            ]
            
            for msg in test_messages:
                print(f"[{datetime.now()}] 📤 Sending: {msg}")
                await websocket.send(msg)
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    print(f"[{datetime.now()}] 📥 Echo: {response}")
                except asyncio.TimeoutError:
                    print(f"[{datetime.now()}] ⏰ No echo response")
                    
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_echo_consumer())