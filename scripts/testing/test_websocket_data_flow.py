#!/usr/bin/env python
"""
Test WebSocket data flow to verify Revenue Dashboard receives real data
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

async def test_revenue_dashboard_ws():
    """Test Revenue Dashboard WebSocket connection and data flow"""
    uri = "ws://localhost:8000/ws/revenue-dashboard/"

    print(f"[{datetime.now()}] Connecting to Revenue Dashboard WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now()}] ✓ Connected successfully!")

            # Wait for initial connection message
            print(f"[{datetime.now()}] Waiting for initial data...")

            # Listen for messages for 10 seconds
            timeout = 10
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    print(f"\n[{datetime.now()}] Received message:")
                    print(f"  Type: {data.get('type')}")

                    if data.get('type') == 'metrics_update':
                        metrics = data.get('metrics', {})
                        print(f"  📊 Metrics received:")
                        print(f"    - Total Revenue: ${metrics.get('total_revenue', 0):,.2f}")
                        print(f"    - Proposals: {metrics.get('proposals_submitted', 0)}")
                        print(f"    - Conversions: {metrics.get('conversions', 0)}")
                        print(f"    - Is Real Data: {data.get('is_real', False)}")
                        print(f"    - Source: {data.get('source', 'unknown')}")

                    elif data.get('type') == 'connection_status':
                        print(f"  📡 Connection Status: {data.get('status')}")
                        print(f"  Component: {data.get('component')}")

                    elif data.get('type') == 'heartbeat':
                        print(f"  💓 Heartbeat received")
                        # Respond to heartbeat
                        await websocket.send(json.dumps({
                            'type': 'ping',
                            'timestamp': data.get('timestamp')
                        }))

                    else:
                        print(f"  Data: {json.dumps(data, indent=2)[:200]}")

                except asyncio.TimeoutError:
                    # No message received in 1 second, send a request
                    print(f"[{datetime.now()}] Sending refresh_metrics request...")
                    await websocket.send(json.dumps({
                        'type': 'refresh_metrics'
                    }))

                except Exception as e:
                    print(f"[{datetime.now()}] Error receiving message: {e}")

            print(f"\n[{datetime.now()}] Test completed!")

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Connection failed: {e}")
        return False

    return True

async def test_income_builder_ws():
    """Test Income Builder WebSocket connection"""
    uri = "ws://localhost:8000/ws/income-builder/"

    print(f"\n[{datetime.now()}] Testing Income Builder WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{datetime.now()}] ✓ Income Builder connected!")

            # Send request for data
            await websocket.send(json.dumps({
                'type': 'get_opportunities'
            }))

            # Wait for response
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            print(f"[{datetime.now()}] Income Builder response: {data.get('type')}")

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Income Builder connection failed: {e}")
        return False

    return True

async def main():
    """Run all WebSocket tests"""
    print("=" * 60)
    print("WebSocket Data Flow Test")
    print("=" * 60)

    # Test Revenue Dashboard
    revenue_success = await test_revenue_dashboard_ws()

    # Test Income Builder
    income_success = await test_income_builder_ws()

    # Summary
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"  Revenue Dashboard: {'✓ PASS' if revenue_success else '✗ FAIL'}")
    print(f"  Income Builder: {'✓ PASS' if income_success else '✗ FAIL'}")
    print("=" * 60)

    return revenue_success and income_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)