#!/usr/bin/env python
"""
Quick WebSocket data test
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_neural_orchestra():
    uri = "ws://localhost:8000/ws/neural-orchestra/"
    print(f"\n🎭 Testing Neural Orchestra WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected")

            # Send data requests
            await websocket.send(json.dumps({'type': 'get_data', 'component': 'neural_orchestra'}))
            await websocket.send(json.dumps({'type': 'get_orchestra_data'}))
            print(f"📤 Sent data requests")

            # Receive messages for 5 seconds
            timeout = 5
            start_time = datetime.now()
            messages = []

            while (datetime.now() - start_time).seconds < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')

                    print(f"📨 Received: {msg_type}")

                    if msg_type == 'orchestra_update':
                        agents = data.get('agents', [])
                        advisors = data.get('advisors', [])
                        connections = data.get('connections', [])
                        print(f"   ✅ Data: {len(agents)} agents, {len(advisors)} advisors, {len(connections)} connections")
                        if agents:
                            print(f"   → First agent: {agents[0].get('name', 'Unknown')}")
                    elif msg_type == 'connection':
                        print(f"   → Status: {data.get('status')}, Message: {data.get('message')}")
                    elif msg_type == 'error':
                        print(f"   ❌ Error: {data.get('message')}")

                    messages.append(data)

                except asyncio.TimeoutError:
                    continue

            print(f"\n📊 Summary: Received {len(messages)} messages")
            orchestra_updates = [m for m in messages if m.get('type') == 'orchestra_update']
            if orchestra_updates:
                print(f"✅ Got {len(orchestra_updates)} orchestra updates with real data!")
            else:
                print(f"❌ No orchestra updates received")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

async def test_income_builder():
    uri = "ws://localhost:8000/ws/income-builder/"
    print(f"\n💰 Testing Income Builder WebSocket...")

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected")

            # Send data request
            await websocket.send(json.dumps({'type': 'get_data', 'component': 'income_builder'}))
            print(f"📤 Sent data request")

            # Receive messages for 5 seconds
            timeout = 5
            start_time = datetime.now()
            messages = []

            while (datetime.now() - start_time).seconds < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')

                    print(f"📨 Received: {msg_type}")

                    if msg_type == 'opportunities_analysis':
                        opportunities = data.get('top_opportunities', [])
                        print(f"   ✅ Data: {len(opportunities)} opportunities")
                        if opportunities:
                            print(f"   → First opportunity: {opportunities[0].get('title', 'Unknown')}")
                    elif msg_type == 'connection':
                        print(f"   → Status: {data.get('status')}, Message: {data.get('message')}")

                    messages.append(data)

                except asyncio.TimeoutError:
                    continue

            print(f"\n📊 Summary: Received {len(messages)} messages")
            opportunity_updates = [m for m in messages if m.get('type') == 'opportunities_analysis']
            if opportunity_updates:
                print(f"✅ Got {len(opportunity_updates)} opportunity updates with real data!")
            else:
                print(f"❌ No opportunity updates received")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

async def main():
    print("="*60)
    print("WEBSOCKET DATA TEST")
    print("="*60)

    await test_neural_orchestra()
    await test_income_builder()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())