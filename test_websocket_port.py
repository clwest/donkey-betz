#!/usr/bin/env python3
"""
🔌 TEST WEBSOCKET CONNECTION
Verify that WebSocket is working on port 8000 (not 8001)
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_websocket_connection():
    """Test WebSocket connection on the correct port"""
    
    # Correct WebSocket URL (port 8000, not 8001)
    uri = "ws://localhost:8000/ws/"
    
    print("="*60)
    print("🔌 TESTING WEBSOCKET CONNECTION")
    print("="*60)
    print(f"Timestamp: {datetime.now()}")
    print(f"WebSocket URI: {uri}")
    print("-"*60)
    
    try:
        print("📡 Attempting to connect...")
        
        # Try to connect to WebSocket
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Send a test message
            test_message = {
                "type": "ping",
                "message": "Testing WebSocket on port 8000",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"\n📤 Sending: {json.dumps(test_message, indent=2)}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"\n📥 Received: {response}")
                
                # Parse response if it's JSON
                try:
                    response_data = json.loads(response)
                    print("\n📊 Parsed response:")
                    print(json.dumps(response_data, indent=2))
                except json.JSONDecodeError:
                    print("(Response is not JSON)")
                
                print("\n✅ WebSocket test PASSED!")
                
            except asyncio.TimeoutError:
                print("\n⚠️ No response received (timeout after 5 seconds)")
                print("This might be normal if the server doesn't echo messages")
                print("But the connection was successful!")
            
            return True
            
    except ConnectionRefusedError:
        print("\n❌ Connection refused on port 8000")
        print("\nPossible causes:")
        print("1. Django server is not running")
        print("2. WebSocket is not configured")
        print("3. Daphne is not being used (try: daphne -b 0.0.0.0 -p 8000 backend.asgi:application)")
        return False
        
    except Exception as e:
        print(f"\n❌ WebSocket test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    
    finally:
        print("-"*60)


def check_server_running():
    """Check if Django server is running on port 8000"""
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print("✅ Server is running on port 8000")
        return True
    else:
        print("❌ Server is NOT running on port 8000")
        print("\nTo start the server with WebSocket support:")
        print("  Option 1: python manage.py runserver")
        print("  Option 2: daphne -b 0.0.0.0 -p 8000 backend.asgi:application")
        print("  Option 3: make unified-dev")
        return False


def main():
    """Main test function"""
    print("\n" + "🔌"*20)
    print("WEBSOCKET PORT VERIFICATION")
    print("🔌"*20)
    
    print("\n📋 Configuration Check:")
    print("  - HTTP Server: http://localhost:8000")
    print("  - WebSocket: ws://localhost:8000/ws/")
    print("  - Using Daphne: Both on same port (CORRECT)")
    print("  - Old config (8001): DEPRECATED\n")
    
    # First check if server is running
    if not check_server_running():
        print("\n⚠️ Start the server first before testing WebSocket")
        sys.exit(1)
    
    # Run WebSocket test
    print("\n🧪 Running WebSocket test...")
    
    try:
        success = asyncio.run(test_websocket_connection())
        
        if success:
            print("\n" + "🎉"*20)
            print("SUCCESS! WebSocket is working on port 8000")
            print("🎉"*20)
            sys.exit(0)
        else:
            print("\n" + "⚠️"*20)
            print("WebSocket connection failed - check configuration")
            print("⚠️"*20)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
        
    except ImportError:
        print("\n⚠️ websockets module not installed")
        print("Install it with: pip install websockets")
        sys.exit(1)


if __name__ == "__main__":
    main()
