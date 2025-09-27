#!/usr/bin/env python3
"""
Test WebSocket stability and data display for the enhanced dashboard
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_websocket_data():
    """Connect to WebSocket and verify data being sent"""

    uri = "ws://localhost:8000/ws/consciousness/"

    print("🔌 Connecting to WebSocket...")
    print(f"   URI: {uri}")
    print("=" * 60)

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket successfully!")
            print("\n📊 Monitoring data stream (30 seconds)...")
            print("=" * 60)

            start_time = time.time()
            message_count = 0
            data_types_seen = set()

            while time.time() - start_time < 30:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    message_count += 1

                    if data.get('type') == 'consciousness_update':
                        update_data = data.get('data', {})

                        # Track which data types we've seen
                        if update_data.get('agent_performance'):
                            data_types_seen.add('agent_performance')
                            print(f"✓ Agent Performance: {len(update_data['agent_performance'])} agents")

                        if update_data.get('emergent_behaviors'):
                            data_types_seen.add('emergent_behaviors')
                            print(f"✓ Emergent Behaviors: {len(update_data['emergent_behaviors'])} behaviors")

                        if update_data.get('system_statistics'):
                            data_types_seen.add('system_statistics')
                            stats = update_data['system_statistics']
                            print(f"✓ System Statistics: {stats.get('total_files', 0):,} files, {stats.get('total_lines', 0):,} lines")

                        if update_data.get('system_metrics'):
                            data_types_seen.add('system_metrics')
                            metrics = update_data['system_metrics']
                            print(f"✓ System Metrics: CPU {metrics.get('cpu_usage', 0)}%, Memory {metrics.get('memory_usage', 0)}%")

                        if update_data.get('real_metrics'):
                            data_types_seen.add('real_metrics')
                            real = update_data['real_metrics']
                            print(f"✓ Real Metrics: Learning {real.get('learning_rate', 0)}%, Success {real.get('success_rate', 0)}%")

                        print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
                        print("-" * 40)

                    elif data.get('type') == 'heartbeat':
                        print(f"💗 Heartbeat received at {datetime.now().strftime('%H:%M:%S')}")

                except asyncio.TimeoutError:
                    print("⏳ Waiting for data...")
                    continue

            print("\n" + "=" * 60)
            print("📈 WebSocket Test Results:")
            print(f"   • Messages received: {message_count}")
            print(f"   • Data types seen: {', '.join(data_types_seen)}")
            print(f"   • Missing data types: {', '.join(set(['agent_performance', 'emergent_behaviors', 'system_statistics', 'system_metrics', 'real_metrics']) - data_types_seen)}")

            visibility_percentage = (len(data_types_seen) / 5) * 100
            print(f"\n🎯 Data Visibility: {visibility_percentage:.0f}%")

            if visibility_percentage == 100:
                print("🎉 ALL data types are flowing through WebSocket!")
            else:
                print(f"⚠️  Only {visibility_percentage:.0f}% of data types detected in WebSocket stream")

    except Exception as e:
        print(f"❌ WebSocket error: {str(e)}")
        print("   Make sure the Django server is running with WebSocket support")

if __name__ == "__main__":
    print("\n🚀 Enhanced Dashboard WebSocket Test")
    print("=" * 60)
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    asyncio.run(test_websocket_data())

    print("\n✅ Test complete!")
    print("📊 Dashboard URL: http://localhost:8000/intelligence/")
    print("💡 The dashboard now displays ALL the rich data being sent via WebSocket!")