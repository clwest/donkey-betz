# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
API Endpoint Verification Script
Tests all updated API endpoints to ensure they're working correctly
"""

import requests
import json
import os
from typing import Dict, List, Tuple
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')
AUTH_TOKEN = os.getenv('TEST_AUTH_TOKEN', '<redacted-424a4828-2026-04-20>')

if not AUTH_TOKEN:
    print("WARNING: No TEST_AUTH_TOKEN found in environment.")
    print("Please set TEST_AUTH_TOKEN in your .env file.")
    print("You can get a token by running: python manage.py create_test_token")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Token {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Define endpoints to test
ENDPOINTS = [
    # Root level endpoints (should work at /api/)
    ("GET", "/api/status/", "Platform Status"),
    ("GET", "/api/info/", "Platform Info"),
    
    # App-specific endpoints (should work at /api/v1/)
    ("GET", "/api/v1/agents/", "Agents List"),
    ("GET", "/api/v1/sports/leagues/", "Sports Leagues"),
    ("GET", "/api/v1/sports/games/", "Sports Games"),
    ("GET", "/api/v1/content/documents/", "Content Documents"),
    ("GET", "/api/v1/self-awareness/capabilities/", "Self-Awareness Capabilities"),
]

def test_endpoint(method: str, path: str, description: str) -> Tuple[bool, str]:
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, json={}, timeout=5)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code == 200:
            return True, f"✅ {description}: SUCCESS"
        elif response.status_code == 404:
            return False, f"❌ {description}: NOT FOUND (404)"
        elif response.status_code == 401:
            return False, f"⚠️  {description}: UNAUTHORIZED (401)"
        else:
            return False, f"❌ {description}: ERROR ({response.status_code})"
    except requests.exceptions.ConnectionError:
        return False, f"🔌 {description}: CONNECTION FAILED (Is the backend running?)"
    except requests.exceptions.Timeout:
        return False, f"⏱️  {description}: TIMEOUT"
    except Exception as e:
        return False, f"❌ {description}: {str(e)}"

def main():
    """Main verification function"""
    print("=" * 60)
    print("API ENDPOINT VERIFICATION")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Auth Token: {AUTH_TOKEN[:10]}...")
    print("-" * 60)
    
    results = []
    for method, path, description in ENDPOINTS:
        success, message = test_endpoint(method, path, description)
        results.append((success, message))
        print(message)
    
    print("-" * 60)
    
    # Summary
    successful = sum(1 for success, _ in results if success)
    failed = len(results) - successful
    
    print(f"\nSUMMARY: {successful}/{len(results)} endpoints working")
    
    if failed > 0:
        print("\n⚠️  Some endpoints are not working.")
        print("Make sure the backend is running with: make run-backend")
        return 1
    else:
        print("\n✅ All endpoints are working correctly!")
        return 0

if __name__ == "__main__":
    sys.exit(main())