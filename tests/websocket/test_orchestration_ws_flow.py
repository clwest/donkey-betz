# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test the WebSocket flow end-to-end for orchestration
This tests both the orchestration broadcast and WebSocket delivery
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

async def test_websocket_flow():
    print("🔗 Testing WebSocket connection and message flow...")
    
    # First, connect to the WebSocket
    ws_url = "ws://localhost:8000/ws/agents/"
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ Connected to WebSocket: {ws_url}")
            
            # Send ping to test basic connectivity
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping")
            
            # Wait for pong response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(response)
                print(f"📥 Received: {pong_data}")
                
                if pong_data.get('type') == 'pong':
                    print("✅ Ping/Pong successful")
                else:
                    print(f"⚠️ Unexpected response: {pong_data}")
            except asyncio.TimeoutError:
                print("❌ No pong response received within 5 seconds")
                return False
            
            # Subscribe to a specific game
            game_id = "6f15d777-dc29-4f5c-8760-9d41ef16f211"  # From user's testing
            subscribe_message = {
                "type": "subscribe",
                "game_id": game_id
            }
            await websocket.send(json.dumps(subscribe_message))
            print(f"📤 Subscribed to game: {game_id}")
            
            # Now trigger an orchestration in another thread/process
            print("🚀 Triggering orchestration in parallel...")
            
            # Start listening for messages
            message_count = 0
            start_time = time.time()
            timeout = 30  # 30 seconds timeout
            
            while time.time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message_data = json.loads(response)
                    message_count += 1
                    
                    print(f"📥 Message {message_count}: {message_data.get('type', 'unknown')}")
                    
                    # Check if it's an agent progress message
                    if message_data.get('type') == 'agent_progress':
                        agent_data = message_data.get('data', {})
                        print(f"   🤖 Agent: {agent_data.get('agent_name', 'unknown')}")
                        print(f"   📝 Status: {agent_data.get('status', 'unknown')}")
                        print(f"   💬 Content: {agent_data.get('content', 'no content')}")
                        
                        # If we get real agent progress, that's success
                        if agent_data.get('game_id') == game_id:
                            print("✅ Received matching agent progress message!")
                            return True
                            
                except asyncio.TimeoutError:
                    # No message received, continue waiting
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
                    
            print(f"⏰ Timeout reached. Received {message_count} messages total.")
            return message_count > 0
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

def trigger_orchestration():
    """Trigger the orchestration API call"""
    url = "http://localhost:8000/api/v1/sports/orchestrate/"
    
    payload = {
        "game_id": "6f15d777-dc29-4f5c-8760-9d41ef16f211",
        "home_team": "Colorado Buffaloes",
        "away_team": "Houston Cougars", 
        "league": "NCAAF",
        "subscription_tier": "elite",
        "selected_agents": [
            "betting-intelligence-analyzer", 
            "weather-analyzer",
            "kelly-bet-sizing"
        ]
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("🚀 Triggering orchestration...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"📊 Orchestration response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Orchestration started: {data.get('success', False)}")
        else:
            print(f"❌ Orchestration failed: {response.text}")
    except Exception as e:
        print(f"❌ Orchestration API error: {e}")

async def run_test():
    """Run the complete test"""
    print("=" * 60)
    print("🧪 WEBSOCKET FLOW TEST")
    print("=" * 60)
    
    # Start the WebSocket listener and orchestration trigger concurrently
    ws_task = asyncio.create_task(test_websocket_flow())
    
    # Give WebSocket time to connect and subscribe
    await asyncio.sleep(2)
    
    # Trigger orchestration in a separate task
    loop = asyncio.get_event_loop()
    orchestration_task = loop.run_in_executor(None, trigger_orchestration)
    
    # Wait for both to complete
    ws_result = await ws_task
    await orchestration_task
    
    print("=" * 60)
    if ws_result:
        print("✅ TEST PASSED: WebSocket flow working correctly")
    else:
        print("❌ TEST FAILED: WebSocket flow not working")
    print("=" * 60)
    
    return ws_result

if __name__ == "__main__":
    asyncio.run(run_test())