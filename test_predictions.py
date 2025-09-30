#!/usr/bin/env python
"""
Test script to verify AI predictions work end-to-end
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from sports.models import Game, GameStatus
from ml.core.ml_engine import MLEngine

print("=" * 60)
print("Testing AI Prediction System")
print("=" * 60)

# Get a sample scheduled game
games = Game.objects.filter(status=GameStatus.SCHEDULED).select_related('home_team', 'away_team', 'league')[:3]
print(f"\nFound {games.count()} scheduled games to test")

# Initialize ML engine
ml_engine = MLEngine()
print("\n✓ ML Engine initialized")

# Test predictions for each game
for i, game in enumerate(games, 1):
    print(f"\n{'-' * 60}")
    print(f"Test {i}: {game.away_team.name} @ {game.home_team.name}")
    print(f"League: {game.league.name if game.league else 'Unknown'}")
    print(f"Sport: {game.league.sport_type if game.league else 'Unknown'}")

    try:
        # Determine sport type
        sport_type = game.league.sport_type.lower() if game.league else 'nfl'

        # Get prediction
        prediction = ml_engine.predict_game(str(game.id), sport_type)

        print(f"\n✅ Prediction successful!")
        print(f"   Winner: {prediction['predicted_winner']}")
        print(f"   Confidence: {prediction['confidence'] * 100:.1f}%")
        print(f"   Home Win Prob: {prediction.get('home_win_probability', 0) * 100:.1f}%")
        print(f"   Away Win Prob: {prediction.get('away_win_probability', 0) * 100:.1f}%")

        if 'predicted_home_score' in prediction:
            print(f"   Predicted Score: {prediction['predicted_home_score']:.1f} - {prediction['predicted_away_score']:.1f}")

    except Exception as e:
        print(f"\n❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)