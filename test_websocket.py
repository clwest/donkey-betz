#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_command():
    uri = "ws://localhost:8000/ws/command-center/"
    async with websockets.connect(uri) as websocket:
        # Wait for connection message
        message = await websocket.recv()
        print("Received connection:", json.loads(message))

        # Send the /system status command
        command = {
            "type": "command",
            "content": "/system status",
            "agent": None
        }
        print("\nSending command:", command)
        await websocket.send(json.dumps(command))

        # Wait for response
        response = await websocket.recv()
        response_data = json.loads(response)
        print("\nReceived response:", response_data)

        if 'data' in response_data and 'response' in response_data['data']:
            print("\n--- Response Content ---")
            print(response_data['data']['response'])

asyncio.run(test_command())