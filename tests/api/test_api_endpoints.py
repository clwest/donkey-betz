# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test API Endpoints to verify they're correctly configured

NOTE: This is a script requiring live server. Run with:
    python tests/api/test_api_endpoints.py
"""
import pytest
pytestmark = pytest.mark.skip(reason="Integration script requiring live server - run manually")

import requests
import json
from typing import Dict, Any

# Base URL
BASE_URL = "http://localhost:8000/api"

# Test endpoints
ENDPOINTS = {
    "agents_list": "/agents/templates/",
    "agents_suggest": "/agents/suggest/",
    "agents_route": "/agents/route/",
    "agents_execute": "/agents/execute/",
    "agents_orchestrate": "/agents/orchestrate/",
    "agents_health": "/agents/health/",
    "instances": "/instances/",
    "orchestrations": "/orchestrations/",
}

def test_endpoint(name: str, path: str, method: str = "GET", data: Dict[str, Any] = None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    print(f"\n🔍 Testing {name}: {method} {url}")
    
    # Add authentication token if available
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token <redacted-4b9facbb-2026-04-20>"  # Admin token
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        if response.status_code == 200:
            print(f"✅ Success: {response.status_code}")
            # Print first 200 chars of response
            content = response.text[:200]
            if len(response.text) > 200:
                content += "..."
            print(f"   Response: {content}")
            return True
        elif response.status_code == 404:
            print(f"❌ Not Found: {response.status_code}")
            return False
        elif response.status_code == 405:
            print(f"⚠️  Method Not Allowed: {response.status_code}")
            return False
        else:
            print(f"⚠️  Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test all endpoints"""
    print("=" * 60)
    print("🚀 API Endpoint Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test GET endpoints
    for name, path in ENDPOINTS.items():
        if name in ["agents_suggest", "agents_route", "agents_execute", "agents_orchestrate"]:
            # These require POST with data
            continue
        results[name] = test_endpoint(name, path)
    
    # Test POST endpoints with sample data
    print("\n--- Testing POST Endpoints ---")
    
    # Test suggest endpoint
    results["agents_suggest"] = test_endpoint(
        "agents_suggest",
        ENDPOINTS["agents_suggest"],
        "POST",
        {"task_description": "I need to write a blog post about AI"}
    )
    
    # Test route endpoint
    results["agents_route"] = test_endpoint(
        "agents_route",
        ENDPOINTS["agents_route"],
        "POST",
        {"task_description": "Analyze sales data and create a report"}
    )
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name:20} : {status}")
    
    all_passed = all(results.values())
    print("=" * 60)
    if all_passed:
        print("✅ All endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints are not working. Please check:")
        print("  1. Ensure the Django server is running")
        print("  2. Check the URL patterns in core/urls.py")
        print("  3. Verify the view functions are properly imported")

if __name__ == "__main__":
    main()