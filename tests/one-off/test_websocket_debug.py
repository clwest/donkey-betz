#!/usr/bin/env python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/sports/"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")

            # Wait for connection message
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Initial message: {data}")

            # Send get_live_games request
            request = {"type": "get_live_games"}
            await websocket.send(json.dumps(request))
            print(f"📤 Sent: {request}")

            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Response type: {data.get('type')}")

            if data.get('type') == 'games_list':
                games = data.get('games', [])
                print(f"✅ Received {len(games)} games")
                if games:
                    print(f"Sample game: {games[0]}")
            else:
                print(f"❌ Unexpected response: {data}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())