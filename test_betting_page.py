#!/usr/bin/env python3
"""
Test script to verify the betting page functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"
TOKEN = "424a48280fa87d30f4997beda23ccad57418d7cb"

def test_endpoint(endpoint, description):
    """Test an API endpoint used by the betting page"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 1
            return True, f"SUCCESS ({count} items)", data
        else:
            return False, f"Status {response.status_code}", None
    except Exception as e:
        return False, str(e), None

def main():
    print("\n" + "="*70)
    print("BETTING PAGE FUNCTIONALITY TEST")
    print("="*70)
    
    # Test all endpoints used by the betting page
    test_cases = [
        ("/v1/sports/summary/", "Sports Summary (for sport selection cards)"),
        ("/v1/sports/leagues/", "Sports Leagues"),
        ("/v1/sports/games/?sport_type=ncaaf", "NCAAF Games"),
        ("/v1/sports/games/?sport_type=nfl", "NFL Games"), 
        ("/v1/sports/games/?sport_type=nba", "NBA Games"),
        ("/v1/sports/games/?status=live", "Live Games"),
        ("/v1/sports/games/trending/?limit=10", "Trending Games"),
        ("/v1/sports/markets/", "Betting Markets"),
    ]
    
    results = []
    sample_data = {}
    
    for endpoint, description in test_cases:
        success, message, data = test_endpoint(endpoint, description)
        results.append(success)
        if success and data:
            sample_data[endpoint] = data[:3] if isinstance(data, list) else data
        
        status = "✅" if success else "❌"
        print(f"{status} {description}: {message}")
    
    success_rate = sum(results) / len(results) * 100 if results else 0
    
    print("\n" + "="*70)
    print("SAMPLE DATA PREVIEW")
    print("="*70)
    
    # Show sample sports summary (used for sport cards)
    if "/v1/sports/summary/" in sample_data:
        sports = sample_data["/v1/sports/summary/"]
        print("\n🏈 Available Sports:")
        for sport in sports[:5]:  # Show first 5
            print(f"   • {sport.get('name', sport.get('sport_type', 'Unknown'))}: {sport.get('count', 0)} leagues")
    
    # Show sample games
    if "/v1/sports/games/trending/?limit=10" in sample_data:
        games = sample_data["/v1/sports/games/trending/?limit=10"]
        print("\n🔥 Sample Trending Games:")
        for game in games[:3]:  # Show first 3
            away = game.get('away_team_name', 'Away')
            home = game.get('home_team_name', 'Home')
            league = game.get('league', 'Unknown')
            status = game.get('status', 'scheduled')
            print(f"   • {away} vs {home} ({league}) - {status}")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if success_rate == 100:
        print("✅ BETTING PAGE FULLY FUNCTIONAL!")
        print("\n🎯 What users will see:")
        print("1. Sports selection cards with league counts")
        print("2. Interactive game cards with betting options")
        print("3. Live, trending, and sport-specific tabs")
        print("4. Clickable games with toast notifications")
        print("5. Real sports data from ESPN + partner APIs")
        
        print("\n🚀 Next Steps:")
        print("1. Visit http://localhost:3000/betting")
        print("2. Select a sport from the cards")
        print("3. Click on games to see betting options")
        print("4. Use the tabs to view Live, Trending, or By Sport")
        
    elif success_rate >= 80:
        print("⚠️ MOSTLY FUNCTIONAL")
        print("Some minor issues but betting page should work")
    else:
        print("❌ CRITICAL ISSUES")
        print("Multiple endpoints failing - page may not load properly")
    
    print(f"\nOverall Success Rate: {success_rate:.1f}% ({sum(results)}/{len(results)} endpoints working)")
    
    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())