#!/usr/bin/env python3
"""
Frontend-Backend Integration Test Script
Tests all major API endpoints and WebSocket connections
"""

import requests
import json
import asyncio
import websockets
from datetime import datetime
from typing import Dict, Any

# Security fix: Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:8000/api"
WS_BASE_URL = "ws://localhost:8000"
AUTH_TOKEN = os.getenv("TEST_AUTH_TOKEN", "")
if not AUTH_TOKEN:
    print("WARNING: No TEST_AUTH_TOKEN found. Please set it in .env file.")
    import sys
    sys.exit(1)  # chris token

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log(message: str, status: str = "INFO"):
    """Pretty print log messages"""
    colors = {
        "SUCCESS": GREEN,
        "ERROR": RED,
        "WARNING": YELLOW,
        "INFO": BLUE
    }
    color = colors.get(status, RESET)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] [{status}] {message}{RESET}")


def test_api_endpoint(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> bool:
    """Test a single API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            log(f"Unsupported method: {method}", "ERROR")
            return False
        
        if response.status_code in [200, 201]:
            log(f"✓ {method} {endpoint} - Status: {response.status_code}", "SUCCESS")
            if response.content:
                try:
                    data = response.json()
                    log(f"  Response preview: {str(data)[:100]}...", "INFO")
                except:
                    log(f"  Response: {response.text[:100]}...", "INFO")
            return True
        else:
            log(f"✗ {method} {endpoint} - Status: {response.status_code}", "ERROR")
            log(f"  Error: {response.text[:200]}", "ERROR")
            return False
    except Exception as e:
        log(f"✗ {method} {endpoint} - Exception: {str(e)}", "ERROR")
        return False


async def test_websocket(endpoint: str) -> bool:
    """Test WebSocket connection"""
    url = f"{WS_BASE_URL}/ws{endpoint}/?token={AUTH_TOKEN}"
    
    try:
        async with websockets.connect(url) as websocket:
            log(f"✓ WebSocket connected to {endpoint}", "SUCCESS")
            
            # Send a test message
            test_message = json.dumps({
                "type": "test",
                "message": "Integration test ping"
            })
            await websocket.send(test_message)
            log(f"  Sent: {test_message}", "INFO")
            
            # Try to receive a response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                log(f"  Received: {response[:100]}...", "INFO")
            except asyncio.TimeoutError:
                log(f"  No response received (timeout)", "WARNING")
            
            await websocket.close()
            return True
    except Exception as e:
        log(f"✗ WebSocket {endpoint} - Exception: {str(e)}", "ERROR")
        return False


def main():
    """Run all integration tests"""
    log("=" * 60, "INFO")
    log("UNIFIED DONKEY BETZ - INTEGRATION TEST SUITE", "INFO")
    log("=" * 60, "INFO")
    
    # Track results
    results = {"passed": 0, "failed": 0}
    
    # Test Core APIs
    log("\n📋 Testing Core APIs...", "INFO")
    core_endpoints = [
        ("/v1/health/", "GET", None),
        ("/v1/status/", "GET", None),
        ("/v1/info/", "GET", None),
        ("/v1/auth/user/", "GET", None),
    ]
    
    for endpoint, method, data in core_endpoints:
        if test_api_endpoint(endpoint, method, data):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test Assistant APIs
    log("\n🤖 Testing Assistant APIs...", "INFO")
    assistant_endpoints = [
        ("/v1/assistant/context/", "GET", None),
        ("/v1/assistant/chat/", "POST", {
            "message": "Hello, this is an integration test!",
            "use_personal_assistant": True
        }),
    ]
    
    for endpoint, method, data in assistant_endpoints:
        if test_api_endpoint(endpoint, method, data):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test Agent Orchestra APIs
    log("\n🎭 Testing Agent Orchestra APIs...", "INFO")
    agent_endpoints = [
        ("/v1/agents/list/", "GET", None),
        ("/v1/agents/health/", "GET", None),
        ("/v1/agents/discovery/stats/", "GET", None),
    ]
    
    for endpoint, method, data in agent_endpoints:
        if test_api_endpoint(endpoint, method, data):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test Odds/Sports APIs
    log("\n🏈 Testing Sports/Odds APIs...", "INFO")
    odds_endpoints = [
        ("/v1/odds/convert-odds/", "POST", {"american_odds": "+150"}),
        ("/v1/odds/expected-value/", "POST", {
            "odds": 2.5,
            "win_probability": 0.45,
            "stake": 100
        }),
    ]
    
    for endpoint, method, data in odds_endpoints:
        if test_api_endpoint(endpoint, method, data):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test WebSocket connections
    log("\n🔌 Testing WebSocket Connections...", "INFO")
    websocket_endpoints = [
        "/assistant",
        "/agent-updates",
    ]
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for endpoint in websocket_endpoints:
        try:
            if loop.run_until_complete(test_websocket(endpoint)):
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            log(f"WebSocket test failed: {e}", "ERROR")
            results["failed"] += 1
    
    loop.close()
    
    # Summary
    log("\n" + "=" * 60, "INFO")
    log("TEST SUMMARY", "INFO")
    log("=" * 60, "INFO")
    total = results["passed"] + results["failed"]
    success_rate = (results["passed"] / total * 100) if total > 0 else 0
    
    if results["failed"] == 0:
        log(f"✅ ALL TESTS PASSED! ({results['passed']}/{total})", "SUCCESS")
    else:
        log(f"⚠️  Some tests failed:", "WARNING")
        log(f"  Passed: {results['passed']}/{total} ({success_rate:.1f}%)", "INFO")
        log(f"  Failed: {results['failed']}/{total}", "ERROR")
    
    log("\nFrontend-Backend integration is", "INFO")
    if success_rate >= 80:
        log("✅ WORKING WELL! Most connections are established.", "SUCCESS")
    elif success_rate >= 50:
        log("⚠️  PARTIALLY WORKING. Some endpoints need attention.", "WARNING")
    else:
        log("❌ NEEDS FIXING. Many connections are failing.", "ERROR")
    
    return results["failed"] == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)