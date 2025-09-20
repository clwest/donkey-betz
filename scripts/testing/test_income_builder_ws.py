#!/usr/bin/env python
"""
Test Income Builder WebSocket Connection with Real Opportunities
================================================================

This script tests that the Income Builder WebSocket:
1. Connects successfully
2. Sends analyze_opportunities message
3. Receives real opportunities (not empty arrays)
"""

import asyncio
import json
import websockets
import sys

async def test_income_builder():
    """Test Income Builder WebSocket connection"""
    uri = "ws://localhost:8000/ws/income-builder/"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to Income Builder WebSocket")

            # Send analyze_opportunities request
            profile = {
                "id": "test_user",
                "skills": ["python", "ai", "automation", "data analysis"],
                "skill_level": "intermediate",
                "current_balance": 0,
                "available_hours": 20
            }

            message = {
                "type": "analyze_opportunities",
                "profile": profile
            }

            await websocket.send(json.dumps(message))
            print(f"📤 Sent: {message['type']}")

            # Listen for responses
            timeout = 10  # seconds
            start_time = asyncio.get_event_loop().time()
            opportunities_received = False

            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)

                    print(f"\n📨 Received message type: {data.get('type', 'unknown')}")

                    if data.get('type') == 'opportunities_analysis':
                        opportunities = data.get('top_opportunities', [])
                        print(f"   Top opportunities count: {len(opportunities)}")
                        print(f"   Source: {data.get('source', 'unknown')}")
                        print(f"   Is real data: {data.get('is_real', False)}")
                        print(f"   Job count: {data.get('job_count', 0)}")

                        if opportunities:
                            print("\n   First 3 opportunities:")
                            for i, opp in enumerate(opportunities[:3], 1):
                                print(f"   {i}. {opp.get('title', 'Unknown')}")
                                print(f"      Stream type: {opp.get('stream_type', 'Unknown')}")
                                print(f"      Potential: {opp.get('potential_monthly', 'Unknown')}")
                                if opp.get('company'):
                                    print(f"      Company: {opp.get('company')}")
                                if opp.get('source'):
                                    print(f"      Source: {opp.get('source')}")
                            opportunities_received = True
                        else:
                            print("   ⚠️ EMPTY opportunities array!")

                        if data.get('earnings_projection'):
                            print(f"\n   Earnings projection: {data.get('earnings_projection')}")

                    elif data.get('type') == 'opportunities_update':
                        opportunities = data.get('opportunities', [])
                        print(f"   Opportunities count: {len(opportunities)}")
                        print(f"   Source: {data.get('source', 'unknown')}")

                        if opportunities:
                            print("   ✅ Received real opportunities via update message")
                            opportunities_received = True

                    elif data.get('type') == 'error':
                        print(f"   ❌ Error: {data.get('message', 'Unknown error')}")

                except asyncio.TimeoutError:
                    continue

            # Final verdict
            print("\n" + "="*60)
            if opportunities_received:
                print("✅ SUCCESS: Income Builder is receiving REAL opportunities!")
            else:
                print("❌ FAILURE: Income Builder is NOT receiving opportunities")
                print("   The WebSocket may be sending empty arrays or not responding")
            print("="*60)

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    return opportunities_received

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Income Builder WebSocket Real Opportunities")
    print("="*60 + "\n")

    success = asyncio.run(test_income_builder())
    sys.exit(0 if success else 1)