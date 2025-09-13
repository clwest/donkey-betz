#!/usr/bin/env python
"""
Test script to verify real-time updates are working in the frontend
This will trigger orchestration and show if WebSocket updates are flowing
"""

import requests
import time
import asyncio
import websockets
import json
from datetime import datetime

async def monitor_websocket():
    """Monitor WebSocket for real-time updates"""
    print("🔗 Connecting to WebSocket to monitor real-time updates...")
    
    try:
        uri = "ws://localhost:8000/ws/agents/"
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Subscribe to game updates
            game_id = "6f15d777-dc29-4f5c-8760-9d41ef16f211"
            await websocket.send(json.dumps({
                "type": "subscribe", 
                "game_id": game_id
            }))
            print(f"📡 Subscribed to game: {game_id}")
            
            # Listen for updates
            update_count = 0
            start_time = time.time()
            
            while time.time() - start_time < 60:  # Listen for 60 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    
                    if data.get('type') == 'agent_progress':
                        update_count += 1
                        agent_data = data.get('data', {})
                        print(f"📥 Update {update_count}: {agent_data.get('agent_name', 'Unknown Agent')}")
                        print(f"   Status: {agent_data.get('status', 'unknown')}")
                        print(f"   Message: {agent_data.get('content', 'no content')}")
                        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                        print("-" * 50)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            print(f"📊 Total updates received: {update_count}")
            if update_count > 0:
                print("✅ Real-time updates are working!")
            else:
                print("⚠️ No updates received - orchestration may not be running")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

def trigger_orchestration():
    """Trigger agent orchestration"""
    print("🚀 Triggering agent orchestration...")
    
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
            "kelly-bet-sizing",
            "injury-analyzer"
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Orchestration started successfully")
                return True
            else:
                print(f"❌ Orchestration failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error triggering orchestration: {e}")
    
    return False

async def run_test():
    """Run the complete test"""
    print("=" * 70)
    print("🧪 REAL-TIME UPDATES TEST")
    print("=" * 70)
    print("This will:")
    print("1. Connect to WebSocket")
    print("2. Trigger agent orchestration") 
    print("3. Monitor for real-time updates")
    print("4. Report if updates are working")
    print("=" * 70)
    
    # Start WebSocket monitoring in background
    monitor_task = asyncio.create_task(monitor_websocket())
    
    # Give WebSocket time to connect
    await asyncio.sleep(2)
    
    # Trigger orchestration in background
    loop = asyncio.get_event_loop()
    orchestration_task = loop.run_in_executor(None, trigger_orchestration)
    
    # Wait for monitoring to complete
    await monitor_task
    
    # Cancel orchestration if still running
    try:
        await orchestration_task
    except:
        pass
    
    print("=" * 70)
    print("🏁 Test completed!")
    print("✅ If you saw updates above, real-time updates are working")
    print("⚠️ If no updates, check that:")
    print("   - Backend is running on port 8000")
    print("   - Celery workers are running")
    print("   - Frontend is on the betting game page")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_test())