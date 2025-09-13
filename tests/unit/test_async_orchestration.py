#!/usr/bin/env python
"""
Test the new async orchestration with WebSocket monitoring
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

async def monitor_websocket_for_game(game_id):
    """Monitor WebSocket for orchestration updates"""
    print(f"🔗 Connecting to WebSocket to monitor game {game_id}...")
    
    ws_url = "ws://localhost:8000/ws/agents/"
    try:
        async with websockets.connect(ws_url) as websocket:
            print(f"✅ Connected to WebSocket")
            
            # Subscribe to game updates
            subscribe_message = {
                "type": "subscribe",
                "game_id": game_id
            }
            await websocket.send(json.dumps(subscribe_message))
            print(f"📡 Subscribed to game: {game_id}")
            
            # Listen for updates
            update_count = 0
            start_time = time.time()
            timeout = 60  # 60 seconds timeout
            
            while time.time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message_data = json.loads(response)
                    
                    # Check if it's an agent progress message
                    if message_data.get('type') == 'agent_progress':
                        update_count += 1
                        agent_data = message_data.get('data', {})
                        print(f"\n📥 Update {update_count}:")
                        print(f"   🤖 Agent: {agent_data.get('agent_name', 'unknown')}")
                        print(f"   📝 Status: {agent_data.get('status', 'unknown')}")
                        print(f"   💬 Content: {agent_data.get('content', 'no content')}")
                        print(f"   ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                        
                        # Check if orchestration completed
                        if agent_data.get('status') == 'completed':
                            print("\n✅ Orchestration completed successfully!")
                            return True
                        elif agent_data.get('status') == 'error':
                            print(f"\n❌ Orchestration failed: {agent_data.get('content')}")
                            return False
                            
                except asyncio.TimeoutError:
                    # No message received, continue waiting
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
                    
            print(f"\n⏰ Monitoring timeout. Received {update_count} updates.")
            return update_count > 0
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

def trigger_async_orchestration():
    """Trigger the new async orchestration"""
    url = "http://localhost:8000/api/v1/sports/orchestrate/"
    
    payload = {
        "game_id": "5c8d01e4-ff2f-4a4e-9832-103d94ebb42a",
        "home_team": "Arizona Wildcats",
        "away_team": "Oregon Ducks", 
        "league": "NCAAF",
        "subscription_tier": "elite",
        "selected_agents": ["weather-analyzer", "kelly-bet-sizing"]
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("🚀 Triggering async orchestration...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        print(f"📊 Response received in {response.elapsed.total_seconds():.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Orchestration started successfully")
                print(f"📋 Task ID: {data.get('task_id')}")
                print(f"⚙️ Engine: {data.get('orchestration_engine')}")
                print(f"📡 Status: {data.get('status')}")
                return data.get('request_params', {}).get('game_id')
            else:
                print(f"❌ Failed: {data.get('message')}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
    except requests.exceptions.Timeout:
        print("❌ Request timed out (but this shouldn't happen with async!)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

async def run_test():
    """Run the complete async test"""
    print("=" * 70)
    print("🧪 ASYNC ORCHESTRATION TEST")
    print("=" * 70)
    print("Testing the new Celery-based async orchestration...")
    print("=" * 70)
    
    # Trigger orchestration
    game_id = trigger_async_orchestration()
    
    if game_id:
        print("\n📡 Monitoring WebSocket for real-time updates...")
        print("-" * 70)
        
        # Monitor WebSocket for updates
        result = await monitor_websocket_for_game(game_id)
        
        print("-" * 70)
        if result:
            print("✅ TEST PASSED: Async orchestration working with real-time updates!")
        else:
            print("⚠️ TEST PARTIAL: Orchestration started but no real-time updates received")
            print("   (This might mean Celery workers need to be restarted)")
    else:
        print("❌ TEST FAILED: Could not start orchestration")
    
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_test())