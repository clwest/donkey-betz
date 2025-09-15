#!/usr/bin/env python3
"""
Test WebSocket connection to verify Decision Command is working
"""

import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test WebSocket connection to income-builder endpoint"""
    uri = "ws://localhost:8000/ws/income-builder/"

    try:
        logger.info(f"🔌 Connecting to WebSocket: {uri}")

        async with websockets.connect(uri) as websocket:
            logger.info("✅ WebSocket connected successfully!")

            # Send test message to trigger analyze_opportunities
            test_message = {
                "type": "analyze_opportunities",
                "profile": {
                    "id": "test_user",
                    "current_balance": 100.0,
                    "skills": ["writing", "ai", "python"],
                    "skill_level": "intermediate",
                    "available_hours": 20
                }
            }

            logger.info(f"📤 Sending test message: {test_message}")
            await websocket.send(json.dumps(test_message))

            # Wait for response
            logger.info("⏳ Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=30)

            logger.info(f"📥 Received response: {response}")
            response_data = json.loads(response)

            if response_data.get('type') == 'opportunities_analysis':
                logger.info("🎉 SUCCESS! Decision Command analyze_opportunities is working!")
                logger.info(f"📊 Found {len(response_data.get('top_opportunities', []))} opportunities")

                # Test opportunity selection
                if response_data.get('top_opportunities'):
                    first_opportunity = response_data['top_opportunities'][0]
                    select_message = {
                        "type": "select_opportunity",
                        "opportunity_id": first_opportunity.get('id', 'content_writing')
                    }

                    logger.info("🎯 Testing opportunity selection...")
                    await websocket.send(json.dumps(select_message))

                    plan_response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    plan_data = json.loads(plan_response)

                    if plan_data.get('type') == 'action_plan':
                        logger.info("🏆 SUCCESS! Action plan creation is working!")
                    else:
                        logger.error(f"❌ Action plan failed: {plan_data}")

            else:
                logger.error(f"❌ Unexpected response type: {response_data.get('type')}")

    except websockets.exceptions.ConnectionRefused:
        logger.error("❌ Connection refused - WebSocket server not running on port 8000")
    except asyncio.TimeoutError:
        logger.error("❌ Timeout waiting for response from WebSocket")
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")

async def main():
    print("🧪 DECISION COMMAND WEBSOCKET TEST")
    print("=" * 50)
    await test_websocket_connection()

if __name__ == "__main__":
    asyncio.run(main())