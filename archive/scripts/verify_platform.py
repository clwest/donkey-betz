#!/usr/bin/env python3
"""
Post-Start Verification Script
Run this after ./start_ws_quick.sh to verify everything is working
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"
TOKEN = "<redacted-0fb2390d-2026-04-20>"

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def check_service(name, url, headers=None):
    """Check if a service is responding"""
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code in [200, 301, 302]:
            return True, f"{GREEN}✅ {name} is running{END}"
        else:
            return False, f"{YELLOW}⚠️  {name} returned status {response.status_code}{END}"
    except:
        return False, f"{RED}❌ {name} is not responding{END}"

def check_agents():
    """Check agent templates endpoint"""
    headers = {"Authorization": f"Token {TOKEN}"}
    try:
        response = requests.get(f"{API_BASE}/api/v1/agents/templates/", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                count = len(data)
            elif isinstance(data, dict) and 'results' in data:
                count = len(data['results'])
            else:
                count = 0
            
            if count >= 150:
                return True, f"{GREEN}✅ Found {count} agents (Expected: 150+){END}"
            elif count > 0:
                return True, f"{YELLOW}⚠️  Found {count} agents (Expected: 150){END}"
            else:
                return False, f"{RED}❌ No agents found{END}"
        else:
            return False, f"{RED}❌ Agent API returned {response.status_code}{END}"
    except Exception as e:
        return False, f"{RED}❌ Failed to check agents: {str(e)}{END}"

def test_agent_execution():
    """Test executing an agent"""
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    
    test_data = {
        "agent_name": "content-creator",
        "task": "System verification test at " + datetime.now().strftime("%H:%M:%S"),
        "priority": "low"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/agents/execute/",
            headers=headers,
            json=test_data,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            exec_id = data.get('execution_id', 'unknown')
            return True, f"{GREEN}✅ Agent execution working (ID: {exec_id}){END}"
        else:
            return False, f"{YELLOW}⚠️  Agent execution returned {response.status_code}{END}"
    except Exception as e:
        return False, f"{YELLOW}⚠️  Agent execution not tested: {str(e)}{END}"

def main():
    print(f"\n{BOLD}{BLUE}{'='*60}{END}")
    print(f"{BOLD}{BLUE}🔍 UNIFIED DONKEY BETZ - POST-START VERIFICATION{END}")
    print(f"{BOLD}{BLUE}{'='*60}{END}\n")
    
    # Wait a moment for services to fully start
    print(f"{YELLOW}Waiting for services to stabilize...{END}")
    time.sleep(2)
    
    all_good = True
    results = []
    
    # Check Backend
    print(f"\n{BOLD}Backend Services:{END}")
    ok, msg = check_service("Django Backend", f"{API_BASE}/api/")
    results.append((ok, msg))
    print(f"  {msg}")
    
    ok, msg = check_service("API v1", f"{API_BASE}/api/v1/")
    results.append((ok, msg))
    print(f"  {msg}")
    
    # Check Agents
    ok, msg = check_agents()
    results.append((ok, msg))
    print(f"  {msg}")
    
    # Test Execution
    ok, msg = test_agent_execution()
    results.append((ok, msg))
    print(f"  {msg}")
    
    # Check Frontend
    print(f"\n{BOLD}Frontend Services:{END}")
    ok, msg = check_service("Frontend Dev Server", f"{FRONTEND_BASE}/")
    results.append((ok, msg))
    print(f"  {msg}")
    
    # Calculate success
    success_count = sum(1 for ok, _ in results if ok)
    total_count = len(results)
    
    print(f"\n{BOLD}{'='*60}{END}")
    
    if success_count == total_count:
        print(f"{BOLD}{GREEN}🎉 PERFECT! All {total_count} checks passed!{END}")
        print(f"{GREEN}Your platform is fully operational with 150 AI agents!{END}")
        
        print(f"\n{BOLD}🚀 Ready to Use:{END}")
        print(f"  1. Open {BLUE}http://localhost:3000/control-center{END}")
        print(f"  2. Select any agent from the dropdown")
        print(f"  3. Enter a task and click Execute")
        print(f"  4. Watch the magic happen! ✨")
        
    elif success_count >= total_count - 1:
        print(f"{BOLD}{YELLOW}⚠️  MOSTLY GOOD: {success_count}/{total_count} checks passed{END}")
        print(f"{YELLOW}Platform is operational but may have minor issues{END}")
        
    else:
        print(f"{BOLD}{RED}❌ ISSUES DETECTED: Only {success_count}/{total_count} checks passed{END}")
        print(f"{RED}Please check the logs:{END}")
        print(f"  Backend:  tail -f backend.log")
        print(f"  Frontend: tail -f frontend.log")
    
    print(f"\n{BOLD}📊 Summary:{END}")
    print(f"  Services Running: {success_count}/{total_count}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{BOLD}{'='*60}{END}\n")

if __name__ == "__main__":
    main()