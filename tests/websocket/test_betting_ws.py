# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test WebSocket connection for betting/sports updates
"""
import asyncio
import websockets
import json

async def test_betting_websocket():
    """Test WebSocket connection for betting updates"""
    
    game_id = "6f15d777-dc29-4f5c-8760-9d41ef16f211"
    uri = f"ws://localhost:8000/ws/sports/games/{game_id}/"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")
            
            # Send a ping message to keep alive
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            print(f"📤 Sent ping message")
            
            # Listen for messages for 10 seconds
            print("👂 Listening for updates (10 seconds)...")
            
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(message)
                    print(f"📥 Received: {json.dumps(data, indent=2)}")
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - no messages received in 10 seconds")
            
    except websockets.exceptions.InvalidStatus as e:
        print(f"❌ Connection failed: {e}")
        print("   WebSocket endpoint may not be configured")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("BETTING WEBSOCKET TEST")
    print("=" * 60)
    
    asyncio.run(test_betting_websocket())