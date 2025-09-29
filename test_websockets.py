#!/usr/bin/env python
"""
Test WebSocket connections for all new pages
"""

import asyncio
import websockets
import json

async def test_websocket(url, test_message):
    """Test a single WebSocket connection"""
    try:
        async with websockets.connect(url) as websocket:
            # Wait for connection message
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✅ Connected to {url}")
            print(f"   Response: {data.get('type', 'unknown')} - {data.get('message', '')}")

            # Send test message
            await websocket.send(json.dumps(test_message))

            # Get response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   Test response: {data.get('type', 'unknown')}")

            return True

    except Exception as e:
        print(f"❌ Failed to connect to {url}")
        print(f"   Error: {str(e)}")
        return False

async def main():
    """Test all WebSocket endpoints"""
    tests = [
        {
            'url': 'ws://localhost:8000/ws/sports/',
            'message': {'type': 'get_live_scores'}
        },
        {
            'url': 'ws://localhost:8000/ws/personal-assistant/',
            'message': {'type': 'chat_message', 'message': 'Hello', 'user_id': '1'}
        },
        {
            'url': 'ws://localhost:8000/ws/ai-nexus/',
            'message': {'type': 'get_status'}
        },
        {
            'url': 'ws://localhost:8000/ws/dbao/',
            'message': {'type': 'get_metrics'}
        },
        {
            'url': 'ws://localhost:8000/ws/profile/',
            'message': {'type': 'get_profile', 'user_id': '1'}
        },
        {
            'url': 'ws://localhost:8000/ws/notifications/',
            'message': {'type': 'get_notifications', 'user_id': '1'}
        }
    ]

    print("=" * 60)
    print("TESTING WEBSOCKET CONNECTIONS")
    print("=" * 60)
    print()

    successful = 0
    failed = 0

    for test in tests:
        success = await test_websocket(test['url'], test['message'])
        if success:
            successful += 1
        else:
            failed += 1
        print()

    print("=" * 60)
    print(f"RESULTS: {successful} successful, {failed} failed")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())