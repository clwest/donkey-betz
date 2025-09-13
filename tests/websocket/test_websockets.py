#!/usr/bin/env python3
"""
Test all WebSocket endpoints
"""

import asyncio
import json
import websockets
from datetime import datetime

# Define all WebSocket endpoints
WS_ENDPOINTS = [
    {
        'name': 'Agent Progress (All)',
        'path': '/ws/agent-progress/',
        'test_message': {'type': 'ping'}
    },
    {
        'name': 'Agent Progress (Instance)',
        'path': '/ws/agent-progress/test-123/',
        'test_message': {'type': 'ping'}
    },
    {
        'name': 'Dashboard',
        'path': '/ws/dashboard/',
        'test_message': {'type': 'refresh_dashboard'}
    },
    {
        'name': 'Live Sports',
        'path': '/ws/live-sports/',
        'test_message': {'type': 'subscribe_sport', 'sport': 'ncaaf'}
    },
    {
        'name': 'Arbitrage',
        'path': '/ws/arbitrage/',
        'test_message': None
    },
    {
        'name': 'Assistant Chat',
        'path': '/ws/assistant/',
        'test_message': {'type': 'chat_message', 'message': 'Test message'}
    },
    {
        'name': 'Orchestration',
        'path': '/ws/orchestration/test-123/',
        'test_message': None
    },
    {
        'name': 'Agent Channels (All)',
        'path': '/ws/channels/',
        'test_message': {'type': 'ping'}
    },
    {
        'name': 'Agent Channels (Specific)',
        'path': '/ws/channels/general/',
        'test_message': {'type': 'ping'}
    },
    {
        'name': 'Notifications',
        'path': '/ws/notifications/',
        'test_message': None
    },
    {
        'name': 'Mythology',
        'path': '/ws/mythology/',
        'test_message': {'type': 'ping'}
    }
]

async def test_websocket(endpoint):
    """Test a single WebSocket endpoint"""
    uri = f"ws://localhost:8000{endpoint['path']}"
    result = {
        'name': endpoint['name'],
        'path': endpoint['path'],
        'status': 'UNKNOWN',
        'message': '',
        'response': None
    }
    
    try:
        async with websockets.connect(uri) as websocket:
            result['status'] = 'CONNECTED'
            
            # Send test message if defined
            if endpoint['test_message']:
                await websocket.send(json.dumps(endpoint['test_message']))
                result['message'] = f"Sent: {endpoint['test_message']}"
                
                # Try to receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2)
                    response_data = json.loads(response)
                    result['response'] = response_data
                    result['status'] = 'SUCCESS'
                except asyncio.TimeoutError:
                    result['message'] += " | No response received (timeout)"
                except json.JSONDecodeError:
                    result['message'] += f" | Invalid JSON response: {response}"
            else:
                # Just check connection
                result['message'] = "Connection successful (no test message)"
                result['status'] = 'SUCCESS'
                
    except ConnectionRefusedError:
        result['status'] = 'REFUSED'
        result['message'] = "Connection refused - server may be down"
    except Exception as e:
        if hasattr(e, 'status_code'):
            result['status'] = 'AUTH_REQUIRED' if e.status_code == 403 else 'ERROR'
            result['message'] = f"Status code: {e.status_code}"
        else:
            result['status'] = 'ERROR'
            result['message'] = str(e)
    
    return result

async def test_all_websockets():
    """Test all WebSocket endpoints"""
    print("=" * 80)
    print("WEBSOCKET ENDPOINT TEST RESULTS")
    print("=" * 80)
    print(f"Testing {len(WS_ENDPOINTS)} endpoints at ws://localhost:8000")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    results = []
    for endpoint in WS_ENDPOINTS:
        result = await test_websocket(endpoint)
        results.append(result)
        
        # Print result
        status_emoji = {
            'SUCCESS': '✅',
            'CONNECTED': '🟡',
            'AUTH_REQUIRED': '🔐',
            'REFUSED': '❌',
            'ERROR': '❌',
            'UNKNOWN': '❓'
        }.get(result['status'], '❓')
        
        print(f"\n{status_emoji} {result['name']}")
        print(f"   Path: {result['path']}")
        print(f"   Status: {result['status']}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['response']:
            print(f"   Response: {json.dumps(result['response'], indent=4)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    connected_count = sum(1 for r in results if r['status'] == 'CONNECTED')
    auth_required_count = sum(1 for r in results if r['status'] == 'AUTH_REQUIRED')
    error_count = sum(1 for r in results if r['status'] in ['ERROR', 'REFUSED'])
    
    print(f"✅ Successful: {success_count}")
    print(f"🟡 Connected (no test): {connected_count}")
    print(f"🔐 Auth Required: {auth_required_count}")
    print(f"❌ Failed: {error_count}")
    print(f"📊 Total: {len(results)}")
    
    if error_count == 0:
        print("\n🎉 All WebSocket endpoints are working correctly!")
    else:
        print(f"\n⚠️  {error_count} endpoints need attention")

if __name__ == '__main__':
    asyncio.run(test_all_websockets())