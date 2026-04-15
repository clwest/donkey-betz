#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)

"""
🔌 TEST WEBSOCKET CONNECTION (FIXED FOR COMPATIBILITY)
Test WebSocket connection using actual configured endpoints
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

# List of actual WebSocket endpoints from routing.py
WEBSOCKET_ENDPOINTS = [
    "ws://localhost:8000/ws/test/echo/",
    "ws://localhost:8000/ws/dashboard/",
    "ws://localhost:8000/ws/agents/",
    "ws://localhost:8000/ws/notifications/",
    "ws://localhost:8000/ws/assistant/",
]

async def test_websocket_endpoint(uri):
    """Test a specific WebSocket endpoint"""
    
    try:
        print(f"  Testing: {uri}")
        
        # Try to connect to WebSocket (no timeout parameter for compatibility)
        async with websockets.connect(uri) as websocket:
            print(f"    ✅ Connected successfully!")
            
            # Send a test message
            test_message = {
                "type": "ping",
                "message": "Testing WebSocket",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            
            # Try to receive response with asyncio timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                print(f"    📥 Response received")
                return True
            except asyncio.TimeoutError:
                print(f"    ⏱️ No response (but connected)")
                return True
            
    except ConnectionRefusedError:
        print(f"    ❌ Connection refused")
        return False
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"    ❌ HTTP {e.status_code}: WebSocket not supported (use Daphne!)")
        return False
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

async def test_all_endpoints():
    """Test all configured WebSocket endpoints"""
    
    print("="*60)
    print("🔌 TESTING WEBSOCKET ENDPOINTS")
    print("="*60)
    print(f"Testing WebSocket endpoints on port 8000")
    print("-"*60)
    
    working_endpoints = []
    failed_endpoints = []
    
    for endpoint in WEBSOCKET_ENDPOINTS:
        result = await test_websocket_endpoint(endpoint)
        if result:
            working_endpoints.append(endpoint)
        else:
            failed_endpoints.append(endpoint)
        print()
    
    print("="*60)
    print("📊 RESULTS SUMMARY")
    print("="*60)
    
    if working_endpoints:
        print(f"\n✅ Working endpoints ({len(working_endpoints)}):")
        for endpoint in working_endpoints:
            print(f"  • {endpoint}")
    
    if failed_endpoints:
        print(f"\n❌ Failed endpoints ({len(failed_endpoints)}):")
        for endpoint in failed_endpoints:
            print(f"  • {endpoint}")
    
    if working_endpoints:
        print(f"\n✅ WebSocket is WORKING on port 8000!")
        print(f"   {len(working_endpoints)} out of {len(WEBSOCKET_ENDPOINTS)} endpoints are responsive")
        return True
    else:
        print(f"\n❌ No WebSocket endpoints are working")
        print("\nPossible issues:")
        print("1. Server is running with 'runserver' instead of Daphne")
        print("2. WebSocket consumers not properly configured")
        print("3. Missing Django Channels installation")
        return False

def check_server_type():
    """Try to determine if server is running with Daphne or runserver"""
    import socket
    import http.client
    
    try:
        # Check server headers
        conn = http.client.HTTPConnection("localhost", 8000, timeout=2)
        conn.request("GET", "/")
        response = conn.getresponse()
        server_header = response.getheader('Server', '')
        conn.close()
        
        if 'daphne' in server_header.lower():
            print("✅ Server is running with Daphne (WebSocket support)")
            return True
        else:
            print("⚠️  Server appears to be running with runserver (no WebSocket support)")
            print("   For WebSocket support, use:")
            print("   daphne -b 0.0.0.0 -p 8000 backend.asgi:application")
            return False
    except Exception as _e:
        logger.warning(
            "test_websocket_fixed.check_server_type: swallowed (%s: %s) — returning default",
            type(_e).__name__, _e,
        )
        return None

def main():
    """Main test function"""
    print("\n" + "🔌"*20)
    print("WEBSOCKET ENDPOINT VERIFICATION")
    print("🔌"*20)
    
    print("\n📋 Configuration Check:")
    print("  HTTP Server: http://localhost:8000")
    print("  WebSocket endpoints configured in core/routing.py")
    print("  Using Django Channels with Daphne ASGI server\n")
    
    # Check if server is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result != 0:
        print("❌ Server is NOT running on port 8000")
        print("\nTo start the server with WebSocket support:")
        print("  Option 1: daphne -b 0.0.0.0 -p 8000 backend.asgi:application")
        print("  Option 2: python manage.py runserver (NO WebSocket)")
        print("  Option 3: make unified-dev-ws (uses Daphne)")
        sys.exit(1)
    
    print("✅ Server is running on port 8000\n")
    
    # Check server type
    check_server_type()
    print()
    
    # Run WebSocket tests
    print("🧪 Testing WebSocket endpoints...\n")
    
    try:
        success = asyncio.run(test_all_endpoints())
        
        if success:
            print("\n" + "🎉"*20)
            print("SUCCESS! WebSocket is working on port 8000")
            print("🎉"*20)
            
            print("\n📌 NOTE: The generic /ws/ endpoint doesn't exist.")
            print("   Use specific endpoints like:")
            print("   - /ws/dashboard/")
            print("   - /ws/agents/")
            print("   - /ws/assistant/")
            
            sys.exit(0)
        else:
            print("\n" + "⚠️"*20)
            print("WebSocket endpoints not responding")
            print("\n🔧 SOLUTION:")
            print("Stop the current server and restart with Daphne:")
            print("\n1. Press Ctrl+C to stop current server")
            print("2. Run: daphne -b 0.0.0.0 -p 8000 backend.asgi:application")
            print("\nOr use the fixed Makefile command:")
            print("make unified-dev-ws")
            print("\n⚠️"*20)
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
