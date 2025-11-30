# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""Test WebSocket sends indicators data"""

import asyncio
import websockets
import json
import time

async def test_websocket_indicators():
    """Connect to WebSocket and check if indicators are sent"""
    uri = "ws://localhost:8001/ws/consciousness/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")

            # Wait for initial message
            message = await websocket.recv()
            data = json.loads(message)

            print("\n📊 Initial WebSocket Data:")
            if 'data' in data and 'indicators' in data['data']:
                indicators = data['data']['indicators']
                print("✅ Indicators found in WebSocket data!")
                print(f"  • Pattern Recognition: {indicators.get('pattern', 'N/A')}%")
                print(f"  • Self-Organization: {indicators.get('self_organization', 'N/A')}%")
                print(f"  • Awareness: {indicators.get('awareness', 'N/A')}%")
                print(f"  • Coherence: {indicators.get('coherence', 'N/A')}%")
                print(f"  • Adaptation: {indicators.get('adaptation', 'N/A')}%")
                return True
            else:
                print("❌ No indicators found in WebSocket data")
                print(f"Data keys: {data.get('data', {}).keys() if 'data' in data else 'No data'}")
                return False

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing WebSocket Indicators...")
    success = asyncio.run(test_websocket_indicators())

    if success:
        print("\n✅ WebSocket is sending indicators correctly!")
        print("The dashboard should now show dynamic indicator values.")
    else:
        print("\n⚠️ WebSocket is not sending indicators.")
        print("Check the consumers_consciousness.py file.")