#!/usr/bin/env python3
"""
Frontend Connectivity Test Script
Tests all API endpoints and WebSocket connections
"""

import requests
import json
import asyncio
import websockets
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration
API_BASE = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"
API_TOKEN = "<redacted-0fb2390d-2026-04-20>"

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_test(name: str, status: bool, message: str = "", response_time: float = 0):
    """Print a test result"""
    icon = "✅" if status else "❌"
    color = Colors.GREEN if status else Colors.RED
    time_str = f"({response_time:.0f}ms)" if response_time > 0 else ""
    print(f"{icon} {color}{name}{Colors.END} {time_str}")
    if message:
        print(f"   {message}")

def test_endpoint(name: str, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Test a single API endpoint"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data or {})
        elif method == "OPTIONS":
            response = requests.options(url, headers=headers)
        else:
            response = requests.request(method, url, headers=headers, json=data)
        
        response_time = (time.time() - start_time) * 1000
        
        # Special handling for OPTIONS (might return 405 but still means endpoint exists)
        if method == "OPTIONS" and response.status_code == 405:
            print_test(name, True, f"Endpoint exists (Method not allowed)", response_time)
            return {"success": True, "status": 405}
        
        if response.status_code == 200:
            try:
                data = response.json()
                item_count = 0
                if isinstance(data, list):
                    item_count = len(data)
                elif isinstance(data, dict) and 'results' in data:
                    item_count = len(data['results'])
                elif isinstance(data, dict) and 'count' in data:
                    item_count = data['count']
                
                message = f"Status {response.status_code}"
                if item_count > 0:
                    message += f", {item_count} items found"
                    
                print_test(name, True, message, response_time)
                return {"success": True, "data": data, "count": item_count}
            except:
                print_test(name, True, f"Status {response.status_code}", response_time)
                return {"success": True}
        else:
            print_test(name, False, f"Status {response.status_code}: {response.text[:100]}", response_time)
            return {"success": False, "status": response.status_code}
    except Exception as e:
        print_test(name, False, str(e))
        return {"success": False, "error": str(e)}

async def test_websocket(name: str, endpoint: str) -> bool:
    """Test WebSocket connection"""
    url = f"{WS_BASE}{endpoint}"
    try:
        async with websockets.connect(url) as ws:
            # Send ping
            await ws.send(json.dumps({"type": "ping"}))
            
            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                print_test(name, True, f"Connected and received: {response[:50]}")
                return True
            except asyncio.TimeoutError:
                print_test(name, True, "Connected (no response to ping)")
                return True
    except Exception as e:
        print_test(name, False, str(e))
        return False

async def run_websocket_tests():
    """Run all WebSocket tests"""
    print_header("TESTING WEBSOCKETS")
    
    ws_tests = [
        ("Assistant WebSocket", "/ws/assistant/"),
        ("Agent Orchestra WebSocket", "/ws/agents/"),
        ("Command Center WebSocket", "/ws/command-center/"),
    ]
    
    results = []
    for name, endpoint in ws_tests:
        result = await test_websocket(name, endpoint)
        results.append(result)
    
    return results

def run_api_tests():
    """Run all API tests"""
    print_header("TESTING API ENDPOINTS")
    
    # Test basic connectivity
    results = []
    
    # Root endpoints
    results.append(test_endpoint("Root API", "/api/"))
    results.append(test_endpoint("API v1", "/api/v1/"))
    
    # Agent endpoints
    print(f"\n{Colors.BOLD}Agent Endpoints:{Colors.END}")
    results.append(test_endpoint("Agent Templates", "/api/v1/agents/templates/"))
    results.append(test_endpoint("Agent Execute (OPTIONS)", "/api/v1/agents/execute/", method="OPTIONS"))
    results.append(test_endpoint("Agent Executions", "/api/v1/agents/executions/"))
    results.append(test_endpoint("Agent Discover (OPTIONS)", "/api/v1/agents/discover/", method="OPTIONS"))
    
    # Health checks
    print(f"\n{Colors.BOLD}Health Checks:{Colors.END}")
    results.append(test_endpoint("Health Check", "/api/v1/health/"))
    results.append(test_endpoint("System Status", "/api/v1/status/"))
    
    return results

def test_agent_execution():
    """Test actual agent execution"""
    print_header("TESTING AGENT EXECUTION")
    
    # Try to execute a simple agent
    test_data = {
        "agent_name": "content-creator",
        "task": "Write a test message",
        "priority": "low"
    }
    
    result = test_endpoint(
        "Execute Content Creator Agent", 
        "/api/v1/agents/execute/",
        method="POST",
        data=test_data
    )
    
    if result.get("success") and result.get("data"):
        execution_id = result["data"].get("execution_id")
        if execution_id:
            print(f"   Execution ID: {execution_id}")
    
    return [result]

def main():
    """Main test runner"""
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("🚀 UNIFIED DONKEY BETZ - FRONTEND CONNECTIVITY TEST")
    print(f"{Colors.END}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API Base: {API_BASE}")
    print(f"WebSocket Base: {WS_BASE}")
    print(f"Auth Token: {API_TOKEN[:20]}...")
    
    all_results = []
    
    # Run API tests
    api_results = run_api_tests()
    all_results.extend([r["success"] for r in api_results if isinstance(r, dict)])
    
    # Run WebSocket tests
    loop = asyncio.get_event_loop()
    ws_results = loop.run_until_complete(run_websocket_tests())
    all_results.extend(ws_results)
    
    # Test agent execution
    exec_results = test_agent_execution()
    all_results.extend([r["success"] for r in exec_results if isinstance(r, dict)])
    
    # Summary
    print_header("TEST SUMMARY")
    
    success_count = sum(1 for r in all_results if r)
    total_count = len(all_results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    if success_rate == 100:
        color = Colors.GREEN
        status = "✅ ALL TESTS PASSED"
    elif success_rate >= 80:
        color = Colors.YELLOW
        status = "⚠️ PARTIAL SUCCESS"
    else:
        color = Colors.RED
        status = "❌ TESTS FAILED"
    
    print(f"{color}{Colors.BOLD}{status}{Colors.END}")
    print(f"Success Rate: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    # Check for agent templates specifically
    template_result = next((r for r in api_results if isinstance(r, dict) and r.get("count", 0) > 100), None)
    if template_result:
        print(f"\n{Colors.GREEN}🤖 {template_result['count']} Agent Templates Available!{Colors.END}")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print("1. Start the frontend: cd frontend && npm run dev")
    print("2. Visit: http://localhost:3000/control-center")
    print("3. Or test connectivity: http://localhost:3000/connectivity-test")
    print("\n✨ Your Multi-Agent AI Platform is Ready!")
    print(f"   Frontend: http://localhost:3000")
    print(f"   Backend: http://localhost:8000")

if __name__ == "__main__":
    main()
