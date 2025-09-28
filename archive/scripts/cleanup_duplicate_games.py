#!/usr/bin/env python
"""
Clean up duplicate games in the database
"""
import os
import sys
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from sports.models import Game
from django.db.models import Count

def cleanup_duplicate_games():
    """Remove duplicate games that have same teams and similar times"""
    
    print("=" * 60)
    print("CLEANING UP DUPLICATE GAMES")
    print("=" * 60)
    
    # Find all games grouped by home_team, away_team, and date
    games = Game.objects.filter(is_active=True).order_by('scheduled_start')
    
    # Track duplicates
    seen_games = {}
    duplicates_removed = 0
    
    for game in games:
        # Create a key based on teams and date (ignoring exact time)
        game_date = game.scheduled_start.date()
        key = (game.home_team_id, game.away_team_id, game_date)
        
        if key in seen_games:
            # Check if this is a duplicate (within 2 hours of the seen game)
            existing_game = seen_games[key]
            time_diff = abs((game.scheduled_start - existing_game.scheduled_start).total_seconds())
            
            if time_diff < 7200:  # Within 2 hours
                print(f"❌ Duplicate found: {game.away_team.name} @ {game.home_team.name}")
                print(f"   Game 1: {existing_game.scheduled_start} (ID: {existing_game.id})")
                print(f"   Game 2: {game.scheduled_start} (ID: {game.id})")
                
                # Keep the one with more data (markets, etc.) or the earlier one
                if existing_game.markets.count() >= game.markets.count():
                    # Delete the current game
                    print(f"   ➡️ Keeping game 1, deleting game 2")
                    game.delete()
                else:
                    # Delete the existing game and update our tracker
                    print(f"   ➡️ Keeping game 2, deleting game 1")
                    existing_game.delete()
                    seen_games[key] = game
                
                duplicates_removed += 1
        else:
            seen_games[key] = game
    
    print(f"\n✅ Cleanup complete!")
    print(f"   Duplicates removed: {duplicates_removed}")
    
    # Show summary of remaining games
    remaining_count = Game.objects.filter(is_active=True).count()
    print(f"   Total games remaining: {remaining_count}")
    
    # Show games by league
    from django.db.models import Count
    league_counts = Game.objects.filter(is_active=True).values('league__name').annotate(count=Count('id')).order_by('-count')
    
    print(f"\n📊 Games by league:")
    for league in league_counts[:10]:
        print(f"   {league['league__name']}: {league['count']} games")

if __name__ == "__main__":
    cleanup_duplicate_games()