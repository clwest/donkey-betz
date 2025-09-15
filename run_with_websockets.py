#!/usr/bin/env python3
"""
Start the Unified Donkey Betz platform with WebSocket support.

The Decision Command feature requires WebSocket connections which are not supported
by Django's development server. This script uses Daphne (ASGI server) to enable
full WebSocket functionality.
"""

import os
import sys
import subprocess
import time
import signal

def check_port_availability(port=8000):
    """Check if the specified port is available"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False

def kill_existing_servers():
    """Kill any existing Django or Daphne servers on port 8000"""
    try:
        # Kill any runserver processes
        subprocess.run(['pkill', '-f', 'runserver'], check=False, capture_output=True)
        # Kill any daphne processes
        subprocess.run(['pkill', '-f', 'daphne'], check=False, capture_output=True)
        time.sleep(2)
    except Exception:
        pass

def main():
    print("🚀 UNIFIED DONKEY BETZ - WebSocket Enabled Server")
    print("=" * 60)

    # Check if port is available
    if not check_port_availability():
        print("⚠️  Port 8000 is in use. Attempting to free it...")
        kill_existing_servers()

        if not check_port_availability():
            print("❌ Could not free port 8000. Please stop any running servers manually.")
            return 1

    print("✅ Port 8000 is available")

    # Start Daphne ASGI server
    print("🌐 Starting ASGI server with WebSocket support...")
    print("   - Decision Command WebSockets: ws://localhost:8000/ws/income-builder/")
    print("   - HTTP APIs: http://localhost:8000/api/v1/")
    print("   - Admin: http://localhost:8000/admin/")
    print()

    try:
        # Start the server
        cmd = [
            sys.executable, '-m', 'daphne',
            '-b', '127.0.0.1',
            '-p', '8000',
            'backend.asgi:application'
        ]

        print("💡 Press Ctrl+C to stop the server")
        print("=" * 60)

        # Run the server
        process = subprocess.Popen(cmd)

        # Wait for server to start
        time.sleep(3)

        print("🎯 Testing Decision Command WebSocket...")

        # Test WebSocket connection
        test_result = test_websocket_connection()
        if test_result:
            print("✅ Decision Command is operational!")
            print("   You can now use 'Analyze Opportunities' in the frontend")
        else:
            print("⚠️  WebSocket test failed, but server is running")

        print("=" * 60)

        # Keep running until interrupted
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ Server stopped")

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1

    return 0

def test_websocket_connection():
    """Test WebSocket connection to verify it's working"""
    try:
        import asyncio
        import websockets
        import json

        async def test():
            try:
                async with websockets.connect('ws://localhost:8000/ws/income-builder/') as ws:
                    # Get initial message
                    await asyncio.wait_for(ws.recv(), timeout=3)

                    # Send test message
                    test_msg = {"type": "ping", "timestamp": "test"}
                    await ws.send(json.dumps(test_msg))

                    # Get response
                    await asyncio.wait_for(ws.recv(), timeout=3)
                    return True

            except Exception:
                return False

        return asyncio.run(test())

    except ImportError:
        print("⚠️  websockets package not available for testing")
        return False
    except Exception:
        return False

if __name__ == "__main__":
    sys.exit(main())