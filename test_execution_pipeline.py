#!/usr/bin/env python3
"""
Test the execution pipeline end-to-end
"""

import asyncio
import json
import websockets
import time


async def test_execution():
    """Test the execution pipeline"""
    uri = "ws://localhost:8000/ws/neural_orchestra/"

    async with websockets.connect(uri) as websocket:
        print("✅ Connected to WebSocket")

        # Wait for connection
        await asyncio.sleep(1)

        # Create a test execution request
        execution_request = {
            "type": "start_execution",
            "data": {
                "plan_id": "test_plan_001",
                "team": {
                    "lead_agent": "orchestrator",
                    "core_agents": ["content_creator", "market_analyzer"],
                    "specialist_agents": ["seo_optimizer"]
                },
                "advisor_id": "sal_khan_advisor",
                "budget_estimate": 2500,
                "success_probability": 0.75,
                "immediate_actions": [
                    "Analyze market opportunities",
                    "Create content strategy",
                    "Deploy initial campaigns"
                ]
            }
        }

        # Send execution request
        print(f"📤 Sending execution request for plan: {execution_request['data']['plan_id']}")
        await websocket.send(json.dumps(execution_request))

        # Listen for responses
        print("👂 Listening for execution updates...")

        for i in range(10):  # Listen for 10 messages or 10 seconds
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(response)

                if data.get('type') == 'execution_started':
                    print(f"🚀 Execution started: {data.get('message')}")
                    print(f"   Team: {data.get('team')}")
                elif data.get('type') == 'execution_update':
                    print(f"📊 Progress: {data.get('progress', 0) * 100:.0f}%")
                    print(f"   Active agents: {data.get('agents_active', [])}")
                elif data.get('type') == 'execution_error':
                    print(f"❌ Error: {data.get('error')}")
                else:
                    print(f"📨 Received: {data.get('type', 'unknown')}")

            except asyncio.TimeoutError:
                print(".", end="", flush=True)
            except Exception as e:
                print(f"❌ Error: {e}")
                break

        print("\n✅ Test complete!")


if __name__ == "__main__":
    print("🧪 Testing Execution Pipeline")
    print("-" * 50)

    try:
        asyncio.run(test_execution())
    except KeyboardInterrupt:
        print("\n⛔ Test interrupted")
    except Exception as e:
        print(f"❌ Test failed: {e}")