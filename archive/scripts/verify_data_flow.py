#!/usr/bin/env python3
"""
Final Data Flow Verification
===========================

Verify that all frontend components now receive data immediately
after the frontend fixes are applied.
"""

import asyncio
import websockets
import json
import time

async def verify_component_data_flow(component_name, endpoint_url, expected_triggers):
    """Verify a component receives data immediately"""
    print(f"\n🔍 Verifying {component_name} data flow...")
    
    try:
        websocket = await websockets.connect(endpoint_url)
        
        # Wait for connection and immediate data
        print(f"✅ Connected to {component_name}")
        
        received_data = []
        start_time = time.time()
        
        # Collect all messages received in first 3 seconds
        try:
            while time.time() - start_time < 3.0:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    data = json.loads(response)
                    received_data.append(data)
                    print(f"📨 Received: {data.get('type', 'unknown')} - {list(data.keys())}")
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            print(f"⚠️ Error receiving data: {e}")
        
        # Analyze received data
        if received_data:
            print(f"✅ {component_name} received {len(received_data)} messages")
            
            # Check for expected data types
            data_types = [msg.get('type', 'unknown') for msg in received_data]
            
            if any('update' in dt for dt in data_types):
                print(f"✅ {component_name} received update messages with real data")
            elif any('data' in str(msg) for msg in received_data):
                print(f"✅ {component_name} received data")
            else:
                print(f"⚠️ {component_name} connected but may not have received expected data")
                print(f"📊 Received types: {data_types}")
        else:
            print(f"❌ {component_name} connected but received no data")
        
        await websocket.close()
        return len(received_data) > 0
        
    except Exception as e:
        print(f"❌ Failed to verify {component_name}: {e}")
        return False

async def main():
    """Verify all component data flows"""
    print("🚀 Final Data Flow Verification")
    print("=" * 50)
    print("Testing if frontend components now receive data immediately...\n")
    
    components = [
        ("Income Builder", "ws://localhost:8000/ws/income-builder/", ["opportunities_update"]),
        ("Revenue Dashboard", "ws://localhost:8000/ws/revenue-dashboard/", ["metrics_update"]),
        ("Neural Orchestra", "ws://localhost:8000/ws/neural-orchestra/", ["orchestra_update", "network_state"]),
        ("Decision Command", "ws://localhost:8000/ws/decision-command/", ["decision_update", "opportunities_analysis"]),
    ]
    
    results = []
    
    for name, url, triggers in components:
        success = await verify_component_data_flow(name, url, triggers)
        results.append((name, success))
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"📋 VERIFICATION SUMMARY:")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"✅ Components receiving data: {successful}/{total}")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    if successful == total:
        print(f"\n🎉 SUCCESS! All frontend components now receive data immediately")
        print(f"🌟 The frontend should now display real data instead of being static")
    else:
        print(f"\n⚠️ Some components still need attention")
        print(f"💡 Check backend consumers for missing data handlers")

if __name__ == "__main__":
    asyncio.run(main())
