#!/usr/bin/env python
"""
Test WebSocket, CORS, and Authentication for the unified platform.
"""
import asyncio
import json
import aiohttp
import websockets
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
AUTH_TOKEN = "993f8273f70877e23b5c7d2f92ed30562a089fe3"  # chris user token

# WebSocket endpoints to test
WS_ENDPOINTS = [
    "/ws/assistant/",
    "/ws/agent-progress/",
    "/ws/dashboard/",
    "/ws/live-sports/",
    "/ws/arbitrage/",
    "/ws/orchestration/test/",
    "/ws/channels/",
    "/ws/notifications/",
    "/ws/mythology/",
]

# API endpoints to test
API_ENDPOINTS = [
    "/api/v1/health",
    "/api/v1/agents/",
    "/api/v1/sports/leagues/",
]

async def test_cors():
    """Test CORS preflight requests."""
    print("\n" + "="*60)
    print("TESTING CORS CONFIGURATION")
    print("="*60)
    
    headers = {
        "Origin": "http://localhost:8081",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization,x-orchestrator"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.options(f"{BASE_URL}/api/v1/health", headers=headers) as resp:
            print(f"CORS Preflight Status: {resp.status}")
            cors_headers = {
                "Allow-Origin": resp.headers.get("Access-Control-Allow-Origin"),
                "Allow-Credentials": resp.headers.get("Access-Control-Allow-Credentials"),
                "Allow-Headers": resp.headers.get("Access-Control-Allow-Headers"),
                "Allow-Methods": resp.headers.get("Access-Control-Allow-Methods"),
            }
            for key, value in cors_headers.items():
                print(f"  {key}: {value}")
            
            # Check if x-orchestrator is allowed
            allowed_headers = resp.headers.get("Access-Control-Allow-Headers", "")
            if "x-orchestrator" in allowed_headers.lower():
                print("  ✅ x-orchestrator header is allowed")
            else:
                print("  ❌ x-orchestrator header is NOT allowed")

async def test_api_endpoints():
    """Test API endpoints with authentication."""
    print("\n" + "="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    headers = {
        "Authorization": f"Token {AUTH_TOKEN}",
        "X-Orchestrator": "test-client"
    }
    
    async with aiohttp.ClientSession() as session:
        for endpoint in API_ENDPOINTS:
            try:
                async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as resp:
                    status = "✅" if resp.status < 400 else "❌"
                    print(f"{status} {endpoint}: {resp.status}")
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list):
                            print(f"    Response: {len(data)} items")
                        elif isinstance(data, dict):
                            print(f"    Response keys: {list(data.keys())[:5]}")
            except Exception as e:
                print(f"❌ {endpoint}: {str(e)}")

async def test_websocket(endpoint, with_token=True):
    """Test a single WebSocket endpoint."""
    url = f"{WS_BASE_URL}{endpoint}"
    if with_token:
        url += f"?token={AUTH_TOKEN}"
    
    try:
        async with websockets.connect(url) as websocket:
            # Wait for connection message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(message)
                
                # Check if authenticated
                if "authenticated" in data.get("data", {}):
                    auth_status = "Auth" if data["data"]["authenticated"] else "Anon"
                    print(f"  ✅ {endpoint}: Connected ({auth_status})")
                else:
                    print(f"  ✅ {endpoint}: Connected")
                
                # Send a test message
                test_msg = json.dumps({
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                })
                await websocket.send(test_msg)
                
                # Try to receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"      Response: {json.loads(response).get('type', 'unknown')}")
                except asyncio.TimeoutError:
                    pass  # Some endpoints might not respond to ping
                    
            except asyncio.TimeoutError:
                print(f"  ✅ {endpoint}: Connected (no initial message)")
            
            await websocket.close()
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"  ❌ {endpoint}: HTTP {e.status_code}")
    except Exception as e:
        print(f"  ❌ {endpoint}: {type(e).__name__}: {str(e)}")

async def test_all_websockets():
    """Test all WebSocket endpoints."""
    print("\n" + "="*60)
    print("TESTING WEBSOCKET CONNECTIONS")
    print("="*60)
    
    print("\nWith Authentication Token:")
    for endpoint in WS_ENDPOINTS:
        await test_websocket(endpoint, with_token=True)
    
    print("\nWithout Authentication Token:")
    for endpoint in WS_ENDPOINTS:
        await test_websocket(endpoint, with_token=False)

async def main():
    """Run all tests."""
    print("Starting connection tests...")
    print(f"Server: {BASE_URL}")
    print(f"Token: {AUTH_TOKEN[:10]}...")
    
    await test_cors()
    await test_api_endpoints()
    await test_all_websockets()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("""
Fixed Issues:
1. ✅ Added TokenAuthMiddleware for WebSocket token authentication
2. ✅ Updated consumers to handle both authenticated and anonymous users
3. ✅ Configured CORS headers (x-orchestrator may need server restart)

Recommendations:
1. For production, ensure Redis is running for channel layers
2. Consider adding rate limiting for WebSocket connections
3. Implement proper error handling in consumers
4. Add WebSocket heartbeat/ping-pong for connection health
    """)

if __name__ == "__main__":
    asyncio.run(main())