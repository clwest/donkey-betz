#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/agent-monitor/"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")

            # Send request for agent status
            await websocket.send(json.dumps({"type": "request_agent_status"}))
            print("Sent request_agent_status")

            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data['type']}")

            if 'agents' in data:
                print(f"Number of agents: {len(data['agents'])}")
                for agent in data['agents'][:5]:  # Show first 5 agents
                    print(f"  - {agent['name']}: {agent['status']} - {agent.get('currentTask', 'no task')}")

            # Keep connection open for a moment
            await asyncio.sleep(2)

    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_websocket())