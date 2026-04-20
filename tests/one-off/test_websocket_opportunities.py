#!/usr/bin/env python
"""
Test WebSocket connection to revenue opportunities
"""

import asyncio
import websockets
import json

async def test_opportunities_websocket():
    """Test the revenue opportunities WebSocket"""

    print("\n🧪 Testing Revenue Opportunities WebSocket...")

    uri = "ws://localhost:8000/ws/revenue-opportunities/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")

            # Wait for initial message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)

                print(f"📨 Received message type: {data.get('type')}")

                if data.get('type') == 'opportunities_update':
                    opportunities = data.get('opportunities', [])
                    print(f"✅ Got {len(opportunities)} opportunities!")

                    if opportunities:
                        # Show first opportunity
                        first_opp = opportunities[0]
                        print(f"\n🎯 First opportunity:")
                        print(f"   Title: {first_opp.get('title')}")
                        print(f"   Company: {first_opp.get('company')}")
                        print(f"   Source: {first_opp.get('source')}")
                        print(f"   ID: {first_opp.get('id')}")

                        # Test stats
                        stats = data.get('stats', {})
                        print(f"\n📊 Stats:")
                        print(f"   Active Count: {stats.get('activeCount')}")
                        print(f"   Total Value: ${stats.get('totalValue', 0):,}")

                    return True
                else:
                    print(f"❌ Unexpected message type: {data.get('type')}")
                    return False

            except asyncio.TimeoutError:
                print("❌ No message received within 10 seconds")
                return False

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_opportunities_websocket())
    print(f"\n{'✅ SUCCESS' if result else '❌ FAILED'}")