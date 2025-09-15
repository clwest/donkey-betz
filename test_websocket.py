#!/usr/bin/env python
"""
Test WebSocket connectivity for Income Builder and Revenue Income endpoints
"""

import websocket
import json
from datetime import datetime

def test_websocket_connection(url, name):
    """Test a WebSocket connection"""
    print(f"\nTesting {name} WebSocket at: {url}")
    print("-" * 50)

    try:
        ws = websocket.WebSocket()
        ws.connect(url)
        print(f"✅ Connected successfully!")

        # Wait for initial connection message
        response = ws.recv()
        data = json.loads(response)
        print(f"📨 Initial message: {data}")

        # Send a ping
        ws.send(json.dumps({
            'type': 'ping',
            'timestamp': datetime.now().isoformat()
        }))

        # Wait for response
        response = ws.recv()
        data = json.loads(response)
        print(f"📨 Ping response: {data}")

        ws.close()
        print(f"✅ {name} WebSocket test passed!")
        return True

    except Exception as e:
        print(f"❌ {name} WebSocket test failed: {e}")
        return False

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════╗
║   WEBSOCKET CONNECTION TEST              ║
╚═══════════════════════════════════════════╝
    """)

    # Test Income Builder WebSocket
    income_builder_passed = test_websocket_connection(
        "ws://localhost:8000/ws/income-builder/",
        "Income Builder"
    )

    # Test Revenue Income WebSocket
    revenue_income_passed = test_websocket_connection(
        "ws://localhost:8000/ws/revenue-income/",
        "Revenue Income"
    )

    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print("=" * 50)
    print(f"Income Builder WebSocket: {'✅ PASSED' if income_builder_passed else '❌ FAILED'}")
    print(f"Revenue Income WebSocket: {'✅ PASSED' if revenue_income_passed else '❌ FAILED'}")

    if income_builder_passed and revenue_income_passed:
        print("\n🎉 All WebSocket tests passed!")
    else:
        print("\n⚠️ Some WebSocket tests failed. Check the server logs.")