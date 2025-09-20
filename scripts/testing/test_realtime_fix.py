#!/usr/bin/env python
"""
Test real-time update fixes
"""

import asyncio
import json
import websocket
import time
from datetime import datetime

def test_neural_orchestra():
    """Test Neural Orchestra real-time updates"""
    print("\n🎭 Testing Neural Orchestra WebSocket...")

    messages = []

    def on_message(ws, message):
        data = json.loads(message)
        msg_type = data.get('type', 'unknown')
        timestamp = datetime.now().strftime('%H:%M:%S')

        print(f"  [{timestamp}] Received: {msg_type}")

        if msg_type == 'orchestra_update':
            agents = data.get('agents', [])
            advisors = data.get('advisors', [])
            connections = data.get('connections', [])
            print(f"    ✅ Orchestra Update: {len(agents)} agents, {len(advisors)} advisors, {len(connections)} connections")
            print(f"    → Is Real: {data.get('is_real', False)}")
            print(f"    → Is Initial: {data.get('is_initial', False)}")
            print(f"    → Is Periodic: {data.get('is_periodic', False)}")

            if len(agents) > 0:
                print(f"    → Sample Agent: {agents[0].get('name', 'Unknown')}")
        elif msg_type == 'connection':
            print(f"    → Message: {data.get('message', '')}")
        elif msg_type == 'error':
            print(f"    ❌ Error: {data.get('message', 'Unknown error')}")

        messages.append(data)

    def on_error(ws, error):
        print(f"  ❌ Error: {error}")

    def on_open(ws):
        print("  ✅ Connected to Neural Orchestra")
        # Request data
        ws.send(json.dumps({'type': 'get_data', 'component': 'neural_orchestra'}))
        ws.send(json.dumps({'type': 'get_orchestra_data'}))

    def on_close(ws, close_status_code, close_msg):
        print("  🔌 Disconnected")

    # Connect
    ws = websocket.WebSocketApp(
        'ws://localhost:8000/ws/neural-orchestra/',
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Run for 15 seconds
    import threading
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

    print("  ⏳ Monitoring for 15 seconds...")
    time.sleep(15)

    ws.close()

    # Analysis
    print("\n  📊 Analysis:")
    orchestra_updates = [m for m in messages if m.get('type') == 'orchestra_update']
    print(f"    • Total messages: {len(messages)}")
    print(f"    • Orchestra updates: {len(orchestra_updates)}")

    if orchestra_updates:
        print(f"    • First update had {len(orchestra_updates[0].get('agents', []))} agents")
        print(f"    • All were real data: {all(u.get('is_real') for u in orchestra_updates)}")
    else:
        print("    ❌ No orchestra updates received!")

    return len(orchestra_updates) > 0

def test_income_builder():
    """Test Income Builder real-time updates"""
    print("\n💰 Testing Income Builder WebSocket...")

    messages = []

    def on_message(ws, message):
        data = json.loads(message)
        msg_type = data.get('type', 'unknown')
        timestamp = datetime.now().strftime('%H:%M:%S')

        print(f"  [{timestamp}] Received: {msg_type}")

        if msg_type == 'opportunities_analysis':
            opportunities = data.get('top_opportunities', [])
            print(f"    ✅ Opportunities: {len(opportunities)} items")
            print(f"    → Is Real: {data.get('is_real', False)}")

            if opportunities:
                print(f"    → Sample: {opportunities[0].get('title', 'Unknown')}")
        elif msg_type == 'connection':
            print(f"    → Message: {data.get('message', '')}")

        messages.append(data)

    def on_error(ws, error):
        print(f"  ❌ Error: {error}")

    def on_open(ws):
        print("  ✅ Connected to Income Builder")
        ws.send(json.dumps({'type': 'get_data', 'component': 'income_builder'}))

    def on_close(ws, close_status_code, close_msg):
        print("  🔌 Disconnected")

    # Connect
    ws = websocket.WebSocketApp(
        'ws://localhost:8000/ws/income-builder/',
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Run for 15 seconds
    import threading
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

    print("  ⏳ Monitoring for 15 seconds...")
    time.sleep(15)

    ws.close()

    # Analysis
    print("\n  📊 Analysis:")
    opportunity_updates = [m for m in messages if m.get('type') == 'opportunities_analysis']
    print(f"    • Total messages: {len(messages)}")
    print(f"    • Opportunity updates: {len(opportunity_updates)}")

    if opportunity_updates:
        print(f"    • First update had {len(opportunity_updates[0].get('top_opportunities', []))} opportunities")
    else:
        print("    ❌ No opportunity updates received!")

    return len(opportunity_updates) > 0

def main():
    print("="*60)
    print("REAL-TIME UPDATE FIX VERIFICATION")
    print("="*60)

    # Test each component
    neural_ok = test_neural_orchestra()
    income_ok = test_income_builder()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if neural_ok and income_ok:
        print("✅ ALL REAL-TIME UPDATES WORKING!")
    else:
        print("❌ Some components not receiving real-time updates:")
        if not neural_ok:
            print("  • Neural Orchestra needs fixing")
        if not income_ok:
            print("  • Income Builder needs fixing")

if __name__ == "__main__":
    main()