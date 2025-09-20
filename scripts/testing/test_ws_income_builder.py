#!/usr/bin/env python3
"""
Test script to verify Income Builder WebSocket is returning real opportunities
"""

import asyncio
import json
import websockets
import time

async def test_income_builder_ws():
    """Test the Income Builder WebSocket connection and data flow"""

    uri = "ws://localhost:8000/ws/income-builder/"

    print("🔌 Connecting to Income Builder WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")

            # Wait for initial connection message
            initial = await websocket.recv()
            print(f"📥 Initial message: {json.loads(initial)['type']}")

            # Wait for initial opportunities data
            print("\n⏳ Waiting for initial opportunities...")

            opportunities_received = False
            for i in range(10):  # Wait up to 10 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    if data['type'] == 'opportunities_update':
                        opportunities = data.get('opportunities', [])
                        print(f"\n✅ Received {len(opportunities)} opportunities!")

                        if opportunities:
                            print("\n📋 First 3 opportunities:")
                            for i, opp in enumerate(opportunities[:3], 1):
                                print(f"\n{i}. {opp.get('title', 'Unknown')}")
                                print(f"   Type: {opp.get('stream_type', 'Unknown')}")
                                print(f"   Potential: {opp.get('potential_monthly', 'Unknown')}")
                                print(f"   Difficulty: {opp.get('difficulty', 'Unknown')}")
                                print(f"   Time to Income: {opp.get('time_to_income', 'Unknown')}")

                            opportunities_received = True
                        else:
                            print("⚠️  Received empty opportunities array!")

                    elif data['type'] == 'bridge_status':
                        print(f"🌉 Bridge status: {data.get('status', {})}")
                    elif data['type'] == 'revenue_update':
                        print(f"💰 Revenue data received")
                    else:
                        print(f"📦 Other message: {data['type']}")

                except asyncio.TimeoutError:
                    continue

            # Now send analyze_opportunities request with profile
            print("\n📤 Sending analyze_opportunities request...")
            profile = {
                'id': 'test_user',
                'skills': ['python', 'ai', 'writing', 'marketing'],
                'skill_level': 'intermediate',
                'available_hours': 20,
                'current_balance': 100
            }

            await websocket.send(json.dumps({
                'type': 'analyze_opportunities',
                'profile': profile
            }))

            print("⏳ Waiting for analysis response...")

            # Wait for analysis response
            for i in range(10):  # Wait up to 10 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)

                    if data['type'] == 'opportunities_analysis':
                        opportunities = data.get('top_opportunities', [])
                        print(f"\n🎯 Analysis returned {len(opportunities)} opportunities!")

                        if opportunities:
                            print("\n📊 Top analyzed opportunities:")
                            for i, opp in enumerate(opportunities[:3], 1):
                                print(f"\n{i}. {opp.get('title', 'Unknown')}")
                                print(f"   Match reasons: {', '.join(opp.get('match_reasons', ['None']))}")

                            # Check data source
                            print(f"\n📍 Data source: {data.get('source', 'unknown')}")
                            print(f"🔢 Total opportunities: {data.get('total_opportunities', 0)}")

                            if data.get('is_real'):
                                print("✅ Using REAL data!")
                            else:
                                print("⚠️  Using mock data")

                            opportunities_received = True
                        else:
                            print("❌ Analysis returned empty opportunities!")

                        break

                    elif data['type'] == 'opportunities_update':
                        opportunities = data.get('opportunities', [])
                        print(f"📥 Update: Received {len(opportunities)} opportunities")
                        if opportunities:
                            opportunities_received = True

                    elif data['type'] == 'error':
                        print(f"❌ Error: {data.get('message', 'Unknown error')}")
                        break

                except asyncio.TimeoutError:
                    continue

            # Final verdict
            print("\n" + "="*50)
            if opportunities_received:
                print("✅ SUCCESS: Income Builder is sending opportunities!")
            else:
                print("❌ FAILURE: No opportunities received from Income Builder")

            print("="*50)

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure the server is running with: make unified-dev")
        return False

    return opportunities_received

if __name__ == "__main__":
    print("🚀 Testing Income Builder WebSocket Connection")
    print("="*50)

    # Run the test
    result = asyncio.run(test_income_builder_ws())

    if result:
        print("\n🎉 Test PASSED! Income Builder WebSocket is working!")
    else:
        print("\n😞 Test FAILED! Check the logs for details.")

    print("\nℹ️  To see server logs, check the terminal running 'make unified-dev'")