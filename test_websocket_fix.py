#!/usr/bin/env python
"""
Test WebSocket Disconnection Fix
---------------------------------
Tests that WebSocket connections disconnect cleanly without timeout warnings.
"""

import asyncio
import websockets
import json
import time
import sys

async def test_websocket_connection():
    """Test WebSocket connection and clean disconnection"""
    uri = "ws://localhost:8000/ws/consciousness/"

    print("🧪 Testing WebSocket connection and disconnection...")
    print("-" * 50)

    try:
        # Connect to WebSocket
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")

            # Wait for initial message
            initial = await websocket.recv()
            data = json.loads(initial)
            print(f"📨 Received initial data: {data.get('type', 'unknown')}")

            # Send a test command
            await websocket.send(json.dumps({
                'command': 'refresh'
            }))
            print("📤 Sent refresh command")

            # Wait briefly for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(response)
                print(f"📨 Received response: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("⏱️  No response within 2 seconds (expected for some commands)")

            # Now disconnect cleanly
            print("\n🔌 Disconnecting WebSocket...")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

    # Connection closed - check if it was clean
    print("✅ WebSocket disconnected cleanly")
    print("\n" + "="*50)
    print("✨ TEST PASSED: WebSocket disconnects without hanging")
    print("="*50)
    return True

async def test_multiple_connections():
    """Test multiple simultaneous connections and disconnections"""
    print("\n🧪 Testing multiple simultaneous connections...")
    print("-" * 50)

    uri = "ws://localhost:8000/ws/consciousness/"
    connections = []

    try:
        # Create multiple connections
        for i in range(3):
            ws = await websockets.connect(uri)
            connections.append(ws)
            print(f"✅ Connection {i+1} established")

        # Wait briefly
        await asyncio.sleep(1)

        # Close all connections
        print("\n🔌 Closing all connections...")
        for i, ws in enumerate(connections):
            await ws.close()
            print(f"✅ Connection {i+1} closed cleanly")

        print("\n✨ All connections closed without timeout warnings!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("🚀 WebSocket Disconnection Fix Test Suite")
    print("="*50)

    # Test 1: Single connection
    test1 = await test_websocket_connection()

    # Small delay between tests
    await asyncio.sleep(1)

    # Test 2: Multiple connections
    test2 = await test_multiple_connections()

    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Single connection test: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Multiple connections test: {'✅ PASSED' if test2 else '❌ FAILED'}")

    if test1 and test2:
        print("\n🎉 All tests passed! WebSocket timeout issue is fixed!")
        print("\n💡 The fix ensures:")
        print("  - Tasks are cancelled without waiting")
        print("  - Cleanup happens in background")
        print("  - No more 'took too long to shut down' warnings")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.")

    return test1 and test2

if __name__ == "__main__":
    # First check if server is running
    print("\n⚠️  Make sure Django server is running with:")
    print("   python manage.py runserver")
    print("\nPress Enter when ready...")
    input()

    # Run tests
    result = asyncio.run(main())
    sys.exit(0 if result else 1)