# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test Sports API endpoints to verify betting page functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"
os.environ["TOKEN"] = "<redacted-424a4828-2026-04-20>"

def test_endpoint(endpoint, description):
    """Test a sports API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {os.environ.get('TOKEN', 'test-token')}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            print(f"✅ {description}: SUCCESS ({count} items)")
            return True
        else:
            print(f"❌ {description}: Failed with status {response.status_code}")
            if response.text:
                print(f"   Error: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description}: Exception - {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("SPORTS API ENDPOINT TEST")
    print("="*60)
    
    endpoints = [
        ("/v1/sports/leagues/", "Leagues List"),
        ("/v1/sports/games/", "Games List"),
        ("/v1/sports/games/?status=live", "Live Games"),
        ("/v1/sports/summary/", "Sports Summary"),
        ("/v1/sports/games/?sport_type=ncaaf", "NCAAF Games"),
        ("/v1/sports/markets/", "Betting Markets"),
    ]
    
    results = []
    for endpoint, description in endpoints:
        results.append(test_endpoint(endpoint, description))
    
    success_rate = sum(results) / len(results) * 100 if results else 0
    
    print("\n" + "="*60)
    print(f"Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)} passed)")
    
    if success_rate == 100:
        print("✅ All sports endpoints are working correctly!")
        print("\nThe betting page should now work. Make sure to:")
        print("1. Restart the frontend dev server: cd frontend && npm run dev")
        print("2. Clear browser cache and reload the page")
        print("3. Check that you're logged in (token in localStorage)")
    else:
        print("⚠️  Some endpoints are failing. Check the backend logs.")

if __name__ == "__main__":
    main()