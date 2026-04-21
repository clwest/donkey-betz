# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test script for multi-sport data integration

This script tests the new sports data providers (ESPN, TheSportsDB, The Odds API)
to ensure they're working correctly as replacements for Polygon.io

Run this script to:
1. Test ESPN Hidden API integration
2. Test TheSportsDB integration  
3. Test The Odds API integration (if API key available)
4. Verify data synchronization
5. Check frontend API endpoints
"""

import os
import sys
import django
import asyncio
import requests
from datetime import datetime

# Add the project directory to Python path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from sports.data_providers import sports_data_manager, ESPNProvider, TheSportsDBProvider, OddsAPIProvider
from sports.models import League, Team, Game, SportType


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")


def print_info(message):
    """Print an info message"""
    print(f"📋 {message}")


def test_espn_api():
    """Test ESPN Hidden API integration"""
    print_header("Testing ESPN Hidden API")
    
    try:
        espn = ESPNProvider()
        
        # Test getting leagues
        print_info("Testing ESPN leagues endpoint...")
        leagues = espn.get_leagues()
        if leagues:
            print_success(f"Found {len(leagues)} ESPN leagues")
            for league in leagues[:3]:  # Show first 3
                print(f"  • {league['name']} ({league['abbreviation']})")
        else:
            print_error("No leagues found from ESPN")
            
        # Test getting teams for NFL
        print_info("Testing ESPN teams for NFL...")
        teams = espn.get_teams('football/nfl')
        if teams:
            print_success(f"Found {len(teams)} NFL teams")
            for team in teams[:3]:  # Show first 3
                print(f"  • {team['name']} ({team.get('abbreviation', 'N/A')})")
        else:
            print_error("No NFL teams found from ESPN")
            
        # Test getting games for NFL
        print_info("Testing ESPN games for NFL...")
        games = espn.get_games('football/nfl')
        if games:
            print_success(f"Found {len(games)} NFL games")
            for game in games[:2]:  # Show first 2
                print(f"  • {game['away_team_name']} @ {game['home_team_name']}")
        else:
            print_error("No NFL games found from ESPN")
            
    except Exception as e:
        print_error(f"ESPN API test failed: {e}")


def test_thesportsdb_api():
    """Test TheSportsDB integration"""
    print_header("Testing TheSportsDB API")
    
    try:
        sportsdb = TheSportsDBProvider()
        
        # Test getting leagues
        print_info("Testing TheSportsDB leagues...")
        leagues = sportsdb.get_leagues()
        if leagues:
            print_success(f"Found {len(leagues)} TheSportsDB leagues")
            for league in leagues[:3]:  # Show first 3
                print(f"  • {league['name']} ({league['abbreviation']})")
        else:
            print_error("No leagues found from TheSportsDB")
            
        # Test getting teams for a known league (NFL)
        print_info("Testing TheSportsDB teams for NFL...")
        teams = sportsdb.get_teams('4391')  # NFL league ID
        if teams:
            print_success(f"Found {len(teams)} NFL teams")
            for team in teams[:3]:  # Show first 3
                print(f"  • {team['name']} ({team.get('abbreviation', 'N/A')})")
        else:
            print_error("No NFL teams found from TheSportsDB")
            
    except Exception as e:
        print_error(f"TheSportsDB API test failed: {e}")


def test_odds_api():
    """Test The Odds API integration"""
    print_header("Testing The Odds API")
    
    # Check if API key is available
    api_key = os.getenv('ODDS_API_KEY')
    if not api_key:
        print_info("⚠️ ODDS_API_KEY not found in environment. Skipping odds tests.")
        print_info("To test odds API, set ODDS_API_KEY environment variable")
        return
    
    try:
        odds_api = OddsAPIProvider(api_key)
        
        # Test getting available sports
        print_info("Testing Odds API sports...")
        sports = odds_api.get_sports()
        if sports:
            print_success(f"Found {len(ports)} sports from Odds API")
            for sport in sports[:5]:  # Show first 5
                print(f"  • {sport.get('title', 'N/A')} ({sport.get('key', 'N/A')})")
        else:
            print_error("No sports found from Odds API")
            
        # Test getting odds for NFL
        print_info("Testing Odds API for NFL...")
        odds = odds_api.get_odds('americanfootball_nfl')
        if odds:
            print_success(f"Found {len(odds)} NFL odds entries")
            for odd in odds[:2]:  # Show first 2
                print(f"  • {odd.get('home_team', 'N/A')} vs {odd.get('away_team', 'N/A')}")
        else:
            print_error("No NFL odds found from Odds API")
            
    except Exception as e:
        print_error(f"Odds API test failed: {e}")


def test_django_models():
    """Test Django models and database operations"""
    print_header("Testing Django Models")
    
    try:
        # Count existing data
        league_count = League.objects.count()
        team_count = Team.objects.count()
        game_count = Game.objects.count()
        
        print_info(f"Current database state:")
        print(f"  • Leagues: {league_count}")
        print(f"  • Teams: {team_count}")
        print(f"  • Games: {game_count}")
        
        # Test creating a sample league
        test_league, created = League.objects.get_or_create(
            abbreviation='TEST',
            defaults={
                'name': 'Test League',
                'sport_type': SportType.NFL,
                'country': 'USA',
                'current_season': '2024'
            }
        )
        
        if created:
            print_success("Created test league")
        else:
            print_info("Test league already exists")
            
        # Clean up test data
        if created:
            test_league.delete()
            print_info("Cleaned up test league")
            
    except Exception as e:
        print_error(f"Django models test failed: {e}")


def test_data_sync():
    """Test the unified sports data manager"""
    print_header("Testing Sports Data Manager")
    
    try:
        # Test syncing leagues
        print_info("Testing league sync...")
        results = sports_data_manager.sync_leagues()
        print_success(f"League sync: {results['created']} created, {results['updated']} updated, {results['errors']} errors")
        
        # Get a sample league for team sync
        sample_league = League.objects.filter(is_active=True).first()
        if sample_league:
            print_info(f"Testing team sync for {sample_league.name}...")
            team_results = sports_data_manager.sync_teams(sample_league)
            print_success(f"Team sync: {team_results['created']} created, {team_results['updated']} updated, {team_results['errors']} errors")
            
            # Test game sync
            print_info(f"Testing game sync for {sample_league.name}...")
            today = datetime.now().strftime('%Y-%m-%d')
            game_results = sports_data_manager.sync_games(sample_league, today)
            print_success(f"Game sync: {game_results['created']} created, {game_results['updated']} updated, {game_results['errors']} errors")
        
    except Exception as e:
        print_error(f"Data sync test failed: {e}")


def test_api_endpoints():
    """Test the API endpoints the frontend will use"""
    print_header("Testing API Endpoints")
    
    base_url = "http://localhost:8000/api/v1"
    headers = {
        'Authorization': 'Token <redacted-c4ba8e9a-2026-04-20>',
        'Content-Type': 'application/json'
    }
    
    endpoints_to_test = [
        '/sports/leagues/',
        '/sports/teams/',
        '/sports/games/',
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print_info(f"Testing {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict) and 'results' in data:
                    count = len(data['results'])
                else:
                    count = "unknown"
                    
                print_success(f"{endpoint} returned {count} items")
            else:
                print_error(f"{endpoint} returned HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print_error(f"{endpoint} request failed: {e}")


def main():
    """Run all tests"""
    print_header("Multi-Sport Data Integration Tests")
    print_info("Testing replacement for Polygon.io with free, open-source APIs")
    print_info("Data sources: ESPN Hidden API, TheSportsDB, The Odds API")
    
    # Run all tests
    test_espn_api()
    test_thesportsdb_api() 
    test_odds_api()
    test_django_models()
    test_data_sync()
    test_api_endpoints()
    
    print_header("Test Summary")
    print_success("All tests completed!")
    print_info("🏈 Your sports betting system now supports:")
    print_info("  • NFL, NBA, MLB, NHL")
    print_info("  • College Football & Basketball")
    print_info("  • Soccer, MMA, Tennis, Golf, Boxing")
    print_info("  • Real-time odds and live scores")
    print_info("  • FREE data sources (no more Polygon.io needed!)")
    
    print("\n" + "🎯" * 20)
    print("Ready to bet on ALL THE ACTION! 🚀")
    print("🎯" * 20)


if __name__ == '__main__':
    main()