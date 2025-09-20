#!/usr/bin/env python
"""
Simple WebSocket test to isolate the unified hub issues
"""

import asyncio
import websockets
import json
import sys


async def test_specific_endpoint(url, component_name):
    """Test a specific WebSocket endpoint"""
    print(f"\nTesting {component_name} at {url}")
    try:
        async with websockets.connect(url) as websocket:
            print(f"✅ Connected to {component_name}")

            # Wait for initial message
            initial_msg = await asyncio.wait_for(websocket.recv(), timeout=3)
            initial_data = json.loads(initial_msg)
            print(f"📦 Initial: {initial_data.get('type', 'unknown')}")

            # Send test message
            test_msg = {
                "type": "request",
                "action": "get_data",
                "test": True
            }
            await websocket.send(json.dumps(test_msg))
            print(f"📤 Sent test message")

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=3)
            response_data = json.loads(response)
            print(f"📥 Response: {response_data.get('type', 'unknown')}")

            return True

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed: {e}")
        return False
    except asyncio.TimeoutError:
        print(f"❌ Timeout connecting to {component_name}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    print("🔧 Simple WebSocket Test for Unified Platform")
    print("=" * 50)

    # Test endpoints one by one
    endpoints = [
        ("ws://localhost:8000/ws/income-builder/", "Income Builder"),
        ("ws://localhost:8000/ws/revenue-dashboard/", "Revenue Dashboard"),
        ("ws://localhost:8000/ws/decision-command/", "Decision Command"),
        ("ws://localhost:8000/ws/neural-orchestra/", "Neural Orchestra"),
        ("ws://localhost:8000/ws/control-center/", "Control Center"),
    ]

    results = []
    for url, name in endpoints:
        result = await test_specific_endpoint(url, name)
        results.append((name, result))
        await asyncio.sleep(0.5)  # Small delay between tests

    print("\n" + "=" * 50)
    print("RESULTS:")
    working = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")

    print(f"\nWorking: {working}/{total} components")
    return working, total


if __name__ == "__main__":
    try:
        working, total = asyncio.run(main())
        sys.exit(0 if working == total else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
        sys.exit(1)