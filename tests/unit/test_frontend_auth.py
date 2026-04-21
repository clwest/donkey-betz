# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test script to verify frontend authentication is working correctly

NOTE: This is a script, not a pytest test file. Run with:
    python tests/unit/test_frontend_auth.py

Pytest should skip this file.
"""

import pytest
pytestmark = pytest.mark.skip(reason="Integration script requiring live server - run manually with python")

import requests
import json

# Test configurations
BASE_URL = "http://localhost:8000/api"
VALID_TOKEN = "<redacted-424a4828-2026-04-20>"  # Alice Writer's token
INVALID_TOKEN = "<redacted-e7d2ae96-2026-04-20>"  # Chris's invalid token

def test_token(token, description):
    """Test a specific token against various endpoints"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Token: {token[:20]}...")
    print(f"{'='*60}")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # Test endpoints
    endpoints = [
        ("/v1/auth/user/", "User Info"),
        ("/v1/agents/list/", "Agent List"),
        ("/v1/agents/health/", "Agent Health"),
        ("/v1/agents/discovery/stats/", "Agent Discovery Stats"),
    ]
    
    results = []
    for endpoint, name in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: SUCCESS")
                results.append(True)
            elif response.status_code == 401:
                print(f"❌ {name}: UNAUTHORIZED (401)")
                results.append(False)
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: ERROR - {str(e)}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100 if results else 0
    print(f"\nSuccess Rate: {success_rate:.1f}% ({sum(results)}/{len(results)} passed)")
    return success_rate

def main():
    print("\n" + "="*60)
    print("FRONTEND AUTHENTICATION TEST")
    print("="*60)
    print("\nThis test verifies that the authentication tokens are working correctly.")
    print("The frontend should be using Alice Writer's token for all API calls.")
    
    # Test the valid token
    valid_rate = test_token(VALID_TOKEN, "Alice Writer's Token (VALID)")
    
    # Test the invalid token
    invalid_rate = test_token(INVALID_TOKEN, "Chris King's Token (INVALID)")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if valid_rate == 100 and invalid_rate == 0:
        print("✅ Authentication is properly configured!")
        print("   - Valid token works for all endpoints")
        print("   - Invalid token is properly rejected")
        print("\n👍 The frontend should now work correctly with the updated token.")
    elif valid_rate == 100:
        print("⚠️  Valid token works, but invalid token had unexpected behavior")
    else:
        print("❌ Authentication issues detected")
        print("   Please check the token configuration")
    
    print("\nFRONTEND CONFIGURATION:")
    print("1. The frontend .env file has been updated with the valid token")
    print("2. The agent-orchestra.service.ts now dynamically reads the token from localStorage")
    print("3. Restart the frontend dev server to apply the changes:")
    print("   cd frontend && npm run dev")

if __name__ == "__main__":
    main()