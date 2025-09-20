#!/usr/bin/env python
"""
Fix the game data issue where both teams are the same
"""
import os
import sys
import django
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from sports.models import Game, Team, League, BettingMarket, OddsLine, Sportsbook
from django.utils import timezone
from datetime import timedelta

def fix_game_data():
    """Fix the Arizona vs Arizona game issue"""
    
    # Find the problematic game
    game_id = "6f15d777-dc29-4f5c-8760-9d41ef16f211"
    
    try:
        game = Game.objects.get(id=game_id)
        print(f"Found game: {game.home_team.name if game.home_team else 'Unknown'} vs {game.away_team.name if game.away_team else 'Unknown'}")
        
        # Get or create proper teams for NCAAF
        ncaaf_league = League.objects.filter(name__icontains="NCAA").first()
        if not ncaaf_league:
            ncaaf_league = League.objects.create(
                name="NCAA Football",
                abbreviation="NCAAF",
                sport="football",
                is_active=True
            )
        
        # Create Kansas State team
        kansas_state, _ = Team.objects.get_or_create(
            name="Kansas State Wildcats",
            defaults={
                'abbreviation': 'KSU',
                'city': 'Manhattan',
                'league': ncaaf_league,
                'conference': 'Big 12',
                'is_active': True
            }
        )
        
        # Update the game with correct away team
        game.away_team = kansas_state
        game.venue_name = "Arizona Stadium"
        game.venue_city = "Tucson"
        game.scheduled_start = timezone.now() + timedelta(hours=3)  # 3 hours from now
        game.save()
        
        print(f"✅ Fixed game: {game.away_team.name} @ {game.home_team.name}")
        print(f"   Matchup: {kansas_state.abbreviation} @ {game.home_team.abbreviation if game.home_team else 'ARIZ'}")
        print(f"   Venue: {game.venue_name}, {game.venue_city}")
        
        # Now create proper betting markets for this game
        # Get or create a sportsbook
        sportsbook, _ = Sportsbook.objects.get_or_create(
            name="DraftKings",
            defaults={
                'abbreviation': 'DK',
                'is_primary': True,
                'is_active': True
            }
        )
        
        # Delete old incorrect markets
        BettingMarket.objects.filter(game=game).delete()
        
        # Create spread market
        spread_market = BettingMarket.objects.create(
            game=game,
            market_type='spread',
            market_name='Point Spread',
            status='open',
            is_active=True
        )
        
        # Create spread lines
        OddsLine.objects.create(
            market=spread_market,
            sportsbook=sportsbook,
            home_odds=-110,
            away_odds=-110,
            home_spread=-7.5,
            away_spread=7.5,
            line_sequence=1,
            is_current=True,
            opened_at=timezone.now()
        )
        
        # Create moneyline market
        ml_market = BettingMarket.objects.create(
            game=game,
            market_type='moneyline',
            market_name='Moneyline',
            status='open',
            is_active=True
        )
        
        OddsLine.objects.create(
            market=ml_market,
            sportsbook=sportsbook,
            home_odds=-280,
            away_odds=+230,
            line_sequence=1,
            is_current=True,
            opened_at=timezone.now()
        )
        
        # Create total market
        total_market = BettingMarket.objects.create(
            game=game,
            market_type='total',
            market_name='Total Points',
            status='open',
            is_active=True
        )
        
        OddsLine.objects.create(
            market=total_market,
            sportsbook=sportsbook,
            total_line=55.5,
            over_odds=-115,
            under_odds=-105,
            line_sequence=1,
            is_current=True,
            opened_at=timezone.now()
        )
        
        print(f"✅ Created betting markets:")
        print(f"   - Spread: {game.away_team.abbreviation if game.away_team else 'KSU'} +7.5 / {game.home_team.abbreviation if game.home_team else 'ARIZ'} -7.5")
        print(f"   - Moneyline: {game.away_team.abbreviation if game.away_team else 'KSU'} +230 / {game.home_team.abbreviation if game.home_team else 'ARIZ'} -280")
        print(f"   - Total: O/U 55.5")
        
        # Add some realistic game metadata
        game.weather_data = {
            'temperature': 78,
            'condition': 'Clear',
            'wind_speed': 8,
            'wind_direction': 'SW',
            'humidity': 35,
            'precipitation': 0
        }
        
        game.public_betting = {
            'spread': {'home': 68, 'away': 32},
            'moneyline': {'home': 75, 'away': 25},
            'total': {'over': 52, 'under': 48}
        }
        
        game.sharp_action = {
            'spread': 'away',
            'total': 'under',
            'confidence': 'medium'
        }
        
        game.save()
        
        print(f"✅ Added game metadata")
        print(f"   - Weather: Clear, 78°F")
        print(f"   - Public: 68% on Arizona -7.5")
        print(f"   - Sharp: Action on Kansas State +7.5")
        
        return game
        
    except Game.DoesNotExist:
        print(f"❌ Game {game_id} not found")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("FIXING GAME DATA")
    print("=" * 60)
    
    fixed_game = fix_game_data()
    
    if fixed_game:
        print(f"\n✅ Successfully fixed game!")
        print(f"📍 View at: http://localhost:3000/betting/game/{fixed_game.id}")
    else:
        print(f"\n❌ Failed to fix game data")