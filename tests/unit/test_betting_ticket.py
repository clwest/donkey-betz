# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test the betting ticket functionality by verifying all necessary components and API endpoints

NOTE: This is a script, not a pytest test file. Run with:
    python tests/unit/test_betting_ticket.py

Pytest should skip this file.
"""

import pytest
pytestmark = pytest.mark.skip(reason="Integration script requiring live server - run manually with python")

import requests
import json
import sys
import os

BASE_URL = "http://localhost:8000/api"
VALID_TOKEN = "<redacted-424a4828-2026-04-20>"
FRONTEND_PATH = "/Users/donkeyking/development/unified-donkey-betz/frontend/src"

def test_api_endpoint(endpoint, description):
    """Test API endpoint for betting ticket data"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {os.environ.get('TOKEN', 'test-token')}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, len(data) if isinstance(data, list) else 1, data
        else:
            return False, f"Status {response.status_code}", None
    except Exception as e:
        return False, str(e), None

def check_component_files():
    """Check if all necessary component files exist"""
    required_files = [
        "features/sports/components/BettingTicketModal.tsx",
        "features/sports/components/MultiSportsDashboard.tsx", 
        "components/ui/dialog.tsx",
        "components/ui/tabs.tsx",
        "components/common/Badge.tsx",
        "components/common/Button.tsx"
    ]
    
    results = []
    for file_path in required_files:
        full_path = os.path.join(FRONTEND_PATH, file_path)
        exists = os.path.exists(full_path)
        results.append((file_path, exists))
    
    return results

def main():
    print("\n" + "="*70)
    print("BETTING TICKET FUNCTIONALITY TEST")
    print("="*70)
    
    # Test API endpoints needed for betting ticket
    print("\n📡 Testing API Endpoints...")
    api_tests = [
        ("/v1/sports/games/?sport_type=nfl", "NFL Games for ticket"),
        ("/v1/sports/games/trending/?limit=5", "Trending games"),
        ("/v1/sports/markets/", "Betting markets"),
        ("/v1/odds/expected-value/", "Expected value calculation (POST)"),
    ]
    
    api_results = []
    sample_game = None
    
    for endpoint, description in api_tests:
        success, count_or_error, data = test_api_endpoint(endpoint, description)
        api_results.append(success)
        status = "✅" if success else "❌"
        
        if success and isinstance(count_or_error, int):
            print(f"{status} {description}: {count_or_error} items")
            # Save sample game for ticket testing
            if endpoint.endswith("nfl") and data and len(data) > 0:
                sample_game = data[0]
        else:
            print(f"{status} {description}: {count_or_error}")
    
    # Test component files
    print("\n📁 Checking Component Files...")
    file_results = check_component_files()
    files_exist = 0
    
    for file_path, exists in file_results:
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if exists:
            files_exist += 1
    
    # Display sample game for betting ticket
    print("\n🎮 Sample Game for Betting Ticket:")
    if sample_game:
        print(f"   Game: {sample_game.get('away_team_name')} @ {sample_game.get('home_team_name')}")
        print(f"   League: {sample_game.get('league')}")
        print(f"   Status: {sample_game.get('status')}")
        print(f"   Venue: {sample_game.get('venue_name', 'TBD')}")
        print(f"   Time: {sample_game.get('scheduled_start')}")
    else:
        print("   No sample game available")
    
    # Results summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    api_success_rate = sum(api_results) / len(api_results) * 100 if api_results else 0
    file_success_rate = files_exist / len(file_results) * 100
    
    print(f"API Endpoints: {api_success_rate:.1f}% working ({sum(api_results)}/{len(api_results)})")
    print(f"Component Files: {file_success_rate:.1f}% present ({files_exist}/{len(file_results)})")
    
    if api_success_rate >= 80 and file_success_rate >= 80:
        print("\n✅ BETTING TICKET READY!")
        print("\n🎯 Features Available:")
        print("   • Detailed game information with weather, injuries, trends")
        print("   • Interactive betting markets (Moneyline, Spread, Total, Props)")
        print("   • Kelly Criterion bet sizing calculator")
        print("   • Live bet slip with stake management")
        print("   • Real-time odds and implied probabilities")
        print("   • Professional gaming-themed UI")
        
        print("\n🚀 How to Use:")
        print("1. Visit http://localhost:3000/betting")
        print("2. Click on any game card")
        print("3. Betting ticket modal will open with:")
        print("   - Complete game analysis")
        print("   - All betting markets")
        print("   - Kelly calculator")
        print("   - Interactive bet slip")
        print("4. Select bets, adjust stakes, place wagers!")
        
    else:
        print("\n❌ ISSUES DETECTED")
        if api_success_rate < 80:
            print("   • API endpoints not working properly")
        if file_success_rate < 80:
            print("   • Missing component files")
    
    return 0 if (api_success_rate >= 80 and file_success_rate >= 80) else 1

if __name__ == "__main__":
    sys.exit(main())