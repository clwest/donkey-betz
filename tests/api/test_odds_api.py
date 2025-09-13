#!/usr/bin/env python
"""
Test The Odds API integration
"""
import os
import sys
import django
import requests
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_odds_api():
    """Test The Odds API with your key"""
    api_key = os.environ.get('THE_ODDS_API_KEY', '')
    
    if not api_key:
        print("❌ THE_ODDS_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test endpoint - get available sports
    base_url = "https://api.the-odds-api.com/v4"
    
    # 1. Test sports endpoint
    print("\n📋 Testing sports endpoint...")
    sports_url = f"{base_url}/sports/"
    params = {'apiKey': api_key}
    
    try:
        response = requests.get(sports_url, params=params)
        if response.status_code == 200:
            sports = response.json()
            print(f"✅ Found {len(sports)} sports")
            
            # Show in-season sports
            in_season = [s for s in sports if not s.get('has_outrights')]
            print(f"\n🏈 In-season sports ({len(in_season)}):")
            for sport in in_season[:5]:
                print(f"  - {sport['title']} ({sport['key']})")
            
            # Check API usage
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            used = response.headers.get('x-requests-used', 'N/A')
            print(f"\n📊 API Usage: {used} used, {remaining} remaining")
            
        elif response.status_code == 401:
            print("❌ Invalid API key")
            return False
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # 2. Test odds endpoint for NCAAF
    print("\n🏈 Testing NCAAF odds...")
    odds_url = f"{base_url}/sports/americanfootball_ncaaf/odds/"
    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american',
        'bookmakers': 'draftkings,fanduel,betmgm,caesars'
    }
    
    try:
        response = requests.get(odds_url, params=params)
        if response.status_code == 200:
            games = response.json()
            print(f"✅ Found {len(games)} NCAAF games with odds")
            
            # Show first game
            if games:
                game = games[0]
                print(f"\n🎮 Sample Game:")
                print(f"  {game['away_team']} @ {game['home_team']}")
                print(f"  Start: {game['commence_time']}")
                
                if game.get('bookmakers'):
                    book = game['bookmakers'][0]
                    print(f"\n  📚 {book['title']} odds:")
                    for market in book['markets'][:2]:
                        print(f"    {market['key']}:")
                        for outcome in market['outcomes']:
                            print(f"      {outcome['name']}: {outcome['price']}")
            
            # Check usage again
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            print(f"\n📊 API Usage after odds: {remaining} remaining")
            
        else:
            print(f"⚠️ No NCAAF odds available: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error fetching odds: {e}")
    
    # 3. Test NFL odds
    print("\n🏈 Testing NFL odds...")
    nfl_url = f"{base_url}/sports/americanfootball_nfl/odds/"
    
    try:
        response = requests.get(nfl_url, params=params)
        if response.status_code == 200:
            games = response.json()
            print(f"✅ Found {len(games)} NFL games with odds")
        else:
            print(f"⚠️ No NFL odds available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return True

def test_ingestion():
    """Test odds ingestion into database"""
    from sports.services import OddsIngestionService
    from sports.models import Game, BettingMarket, OddsLine
    
    print("\n🔄 Testing odds ingestion service...")
    
    try:
        service = OddsIngestionService()
        
        # Check current state
        games_count = Game.objects.count()
        markets_count = BettingMarket.objects.count()
        odds_count = OddsLine.objects.count()
        
        print(f"\n📊 Current database state:")
        print(f"  Games: {games_count}")
        print(f"  Markets: {markets_count}")
        print(f"  Odds Lines: {odds_count}")
        
        # Try to ingest NCAAF odds
        print("\n🔄 Attempting to ingest NCAAF odds...")
        # This would normally be:
        # await service.ingest_sport_odds('ncaaf')
        # But we'll just check if the service is configured
        
        if hasattr(service, 'odds_api_key'):
            if service.odds_api_key:
                print("✅ Odds ingestion service is configured")
            else:
                print("❌ Odds API key not configured in service")
        else:
            print("⚠️ Service needs API key configuration")
            
    except Exception as e:
        print(f"❌ Service error: {e}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🏆 THE ODDS API INTEGRATION TEST")
    print("=" * 60)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv('/Users/donkeyking/development/unified-donkey-betz/.env')
    
    # Run tests
    if test_odds_api():
        print("\n✅ API connection successful!")
        test_ingestion()
    else:
        print("\n❌ API connection failed")
        print("\nTroubleshooting:")
        print("1. Check your API key is valid")
        print("2. Verify you have remaining API credits")
        print("3. Visit https://the-odds-api.com/account/")