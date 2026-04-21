# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Comprehensive test to verify all API endpoint fixes
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"
os.environ["TOKEN"] = "<redacted-424a4828-2026-04-20>"

def test_endpoint(endpoint, description, method="GET", data=tests/verification/verify_all_fixes.py):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {os.environ.get('TOKEN', 'test-token')}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        else:
            return False, f"Unsupported method: {method}"
        
        if response.status_code in [200, 201]:
            return True, "SUCCESS"
        else:
            return False, f"Status {response.status_code}"
    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE API ENDPOINT VERIFICATION")
    print("="*70)
    
    test_suites = {
        "Core APIs": [
            ("/v1/health/", "Health Check"),
            ("/v1/status/", "Platform Status"),
            ("/v1/info/", "Platform Info"),
            ("/v1/auth/user/", "User Authentication"),
        ],
        "Agent Orchestra APIs": [
            ("/v1/agents/list/", "Agent List"),
            ("/v1/agents/health/", "Agent Health"),
            ("/v1/agents/discovery/stats/", "Agent Discovery"),
            ("/v1/orchestrations/", "Orchestrations"),
        ],
        "Sports/Betting APIs": [
            ("/v1/sports/leagues/", "Sports Leagues"),
            ("/v1/sports/games/", "Sports Games"),
            ("/v1/sports/games/?status=live", "Live Games"),
            ("/v1/sports/summary/", "Sports Summary"),
            ("/v1/sports/games/?sport_type=ncaaf", "NCAAF Games"),
            ("/v1/sports/markets/", "Betting Markets"),
        ],
        "Odds APIs": [
            ("/v1/odds/expected-value/", "Expected Value", "POST", {
                "odds": 2.5,
                "win_probability": 0.45,
                "stake": 100
            }),
            ("/v1/odds/kelly-criterion/", "Kelly Criterion", "POST", {
                "american_odds": "+150",
                "win_probability": 0.45,
                "bankroll": 1000,
                "kelly_fraction": 0.25
            }),
        ],
        "Assistant APIs": [
            ("/v1/assistant/context/", "Assistant Context"),
        ],
    }
    
    total_passed = 0
    total_tests = 0
    
    for suite_name, endpoints in test_suites.items():
        print(f"\n📋 Testing {suite_name}...")
        suite_passed = 0
        
        for test_config in endpoints:
            endpoint = test_config[0]
            description = test_config[1]
            method = test_config[2] if len(test_config) > 2 else "GET"
            data = test_config[3] if len(test_config) > 3 else None
            
            success, message = test_endpoint(endpoint, description, method, data)
            total_tests += 1
            
            if success:
                print(f"  ✅ {description}: {message}")
                suite_passed += 1
                total_passed += 1
            else:
                print(f"  ❌ {description}: {message}")
        
        print(f"  → {suite_passed}/{len(endpoints)} passed")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"Overall Success Rate: {success_rate:.1f}% ({total_passed}/{total_tests} tests passed)")
    
    if success_rate == 100:
        print("\n✅ ALL TESTS PASSED! The system is fully operational.")
        print("\n🎯 Next Steps:")
        print("1. Restart the frontend: cd frontend && npm run dev")
        print("2. Visit http://localhost:3000/betting")
        print("3. The betting page should now work correctly!")
    elif success_rate >= 90:
        print("\n✅ SYSTEM IS MOSTLY OPERATIONAL")
        print("Minor issues detected but the betting page should work.")
    elif success_rate >= 70:
        print("\n⚠️  PARTIAL FUNCTIONALITY")
        print("Some features may not work correctly.")
    else:
        print("\n❌ CRITICAL ISSUES DETECTED")
        print("Many endpoints are failing. Check backend logs.")
    
    return 0 if success_rate == 100 else 1

if __name__ == "__main__":
    sys.exit(main())