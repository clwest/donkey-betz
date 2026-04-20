#!/usr/bin/env python
"""
Test all WebSocket endpoints to see what data each component is returning
This helps us identify what's real vs mock data
"""
import asyncio
import json
import websockets
from datetime import datetime


async def test_endpoint(endpoint_name, ws_url, messages_to_send):
    """Test a single WebSocket endpoint"""
    print(f"\n{'='*80}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {ws_url}")
    print(f"{'='*80}")

    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✓ Connected to {endpoint_name}")

            # Wait for initial connection message
            try:
                initial_msg = await asyncio.wait_for(websocket.recv(), timeout=3)
                print(f"\n📨 Initial message:")
                print(json.dumps(json.loads(initial_msg), indent=2))
            except asyncio.TimeoutError:
                print("⏳ No initial message received")

            # Send test messages
            for msg in messages_to_send:
                print(f"\n📤 Sending: {json.dumps(msg)}")
                await websocket.send(json.dumps(msg))

                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    response_data = json.loads(response)
                    print(f"\n📨 Response received ({response_data.get('type', 'unknown')}):")

                    # Pretty print with size limit
                    response_str = json.dumps(response_data, indent=2)
                    if len(response_str) > 2000:
                        print(response_str[:2000] + "\n... (truncated)")
                    else:
                        print(response_str)

                    # Analyze the response
                    analyze_response(endpoint_name, response_data)

                except asyncio.TimeoutError:
                    print("⏳ No response received (timeout)")
                except Exception as e:
                    print(f"❌ Error parsing response: {e}")

            print(f"\n✓ {endpoint_name} test complete")

    except Exception as e:
        print(f"❌ Failed to connect to {endpoint_name}: {e}")


def analyze_response(endpoint_name, data):
    """Analyze response to determine if it's real or mock data"""
    print(f"\n🔍 Analysis:")

    # Check for obvious mock data indicators
    mock_indicators = []
    real_indicators = []

    # Convert to string for searching
    data_str = json.dumps(data).lower()

    # Mock data indicators
    if 'mock' in data_str or 'demo' in data_str or 'test' in data_str:
        mock_indicators.append("Contains 'mock', 'demo', or 'test' keywords")
    if 'lorem ipsum' in data_str:
        mock_indicators.append("Contains 'lorem ipsum'")
    if 'example' in data_str:
        mock_indicators.append("Contains 'example'")

    # Real data indicators
    if 'uuid' in data_str or 'id' in data_str:
        real_indicators.append("Contains IDs/UUIDs")
    if 'timestamp' in data_str or 'created_at' in data_str or 'updated_at' in data_str:
        real_indicators.append("Contains timestamps")
    if isinstance(data, dict) and len(data.get('data', {})) > 0:
        real_indicators.append("Has data payload")

    # Check for empty/minimal data
    if isinstance(data, dict):
        data_content = data.get('data', {})
        if isinstance(data_content, dict) and len(data_content) == 0:
            mock_indicators.append("Empty data object")
        elif isinstance(data_content, list) and len(data_content) == 0:
            mock_indicators.append("Empty data array")

    if mock_indicators:
        print("⚠️  MOCK DATA INDICATORS:")
        for indicator in mock_indicators:
            print(f"   - {indicator}")

    if real_indicators:
        print("✅ REAL DATA INDICATORS:")
        for indicator in real_indicators:
            print(f"   - {indicator}")

    if not mock_indicators and not real_indicators:
        print("❓ UNCLEAR - needs manual inspection")


async def main():
    """Test all unified platform WebSocket endpoints"""

    endpoints = [
        {
            'name': 'Revenue Dashboard',
            'url': 'ws://localhost:8000/ws/revenue/',
            'messages': [
                {'type': 'get_revenue_data'},
                {'type': 'get_earnings_history'},
            ]
        },
        {
            'name': 'Income Builder',
            'url': 'ws://localhost:8000/ws/income-builder/',
            'messages': [
                {'type': 'get_opportunities'},
                {'type': 'analyze_skills'},
            ]
        },
        {
            'name': 'Decision Command',
            'url': 'ws://localhost:8000/ws/decision-command/',
            'messages': [
                {'type': 'get_opportunities'},
                {'type': 'get_decisions'},
            ]
        },
        {
            'name': 'Neural Orchestra',
            'url': 'ws://localhost:8000/ws/neural-orchestra/',
            'messages': [
                {'type': 'get_agents'},
                {'type': 'get_workflows'},
            ]
        },
        {
            'name': 'Control Center',
            'url': 'ws://localhost:8000/ws/control-center/',
            'messages': [
                {'type': 'get_system_stats'},
                {'type': 'get_health'},
            ]
        },
        {
            'name': 'Revenue Opportunities',
            'url': 'ws://localhost:8000/ws/revenue-opportunities/',
            'messages': [
                {'type': 'get_opportunities'},
                {'type': 'analyze_opportunity'},
            ]
        },
    ]

    print("="*80)
    print("UNIFIED PLATFORM FRONTEND INTEGRATION TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    for endpoint in endpoints:
        await test_endpoint(
            endpoint['name'],
            endpoint['url'],
            endpoint['messages']
        )
        await asyncio.sleep(1)  # Brief pause between tests

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
    print("\nSummary:")
    print("- Check the analysis sections above to see which endpoints return real vs mock data")
    print("- Endpoints with mock data need to be connected to real data sources")
    print("- Endpoints with real data may need frontend display verification")


if __name__ == '__main__':
    asyncio.run(main())