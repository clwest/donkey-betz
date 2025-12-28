"""
Sports Prediction Tracking Utilities
Helper functions for saving predictions and calculating win rates
"""

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


def save_ml_prediction(game, prediction, sport_type):
    """
    Save an ML prediction to the database

    Args:
        game: Game model instance
        prediction: dict from ML Engine with keys: winner, confidence, home_win_probability, etc.
        sport_type: str like 'nfl', 'mlb', 'nba', 'nhl'

    Returns:
        MLPrediction instance
    """
    from sports.models import MLPrediction

    # Determine predicted winner team
    winner_name = prediction['winner']
    if winner_name == game.home_team.name or winner_name == game.home_team.abbreviation:
        predicted_winner_team = game.home_team
    else:
        predicted_winner_team = game.away_team

    # Check if prediction already exists for this game/model/today
    existing = MLPrediction.objects.filter(
        game=game,
        model_used=prediction.get('model_used', f'{sport_type}_predictor'),
        created_at__date=timezone.now().date()
    ).first()

    if existing:
        # Update existing prediction
        existing.predicted_winner = predicted_winner_team
        existing.confidence = prediction['confidence'] * 100
        existing.home_win_probability = prediction.get('home_win_probability', 0.5) * 100
        existing.away_win_probability = prediction.get('away_win_probability', 0.5) * 100
        existing.predicted_spread = prediction.get('predicted_spread')
        existing.key_factors = prediction.get('key_factors', [])
        existing.ai_reasoning = '; '.join(prediction.get('key_factors', [])[:3])
        existing.shown_to_users += 1
        existing.save()
        logger.info(f"Updated prediction for game {game.id}")
        return existing
    else:
        # Create new prediction
        ml_prediction = MLPrediction.objects.create(
            game=game,
            predicted_winner=predicted_winner_team,
            confidence=prediction['confidence'] * 100,
            home_win_probability=prediction.get('home_win_probability', 0.5) * 100,
            away_win_probability=prediction.get('away_win_probability', 0.5) * 100,
            model_used=prediction.get('model_used', f'{sport_type}_predictor'),
            sport_type=sport_type,
            predicted_spread=prediction.get('predicted_spread'),
            key_factors=prediction.get('key_factors', []),
            ai_reasoning='; '.join(prediction.get('key_factors', [])[:3]),
            shown_to_users=1
        )
        logger.info(f"Created new prediction for game {game.id}: {ml_prediction}")
        return ml_prediction


def calculate_today_stats():
    """
    Calculate real win rate and profit from today's evaluated predictions

    Returns:
        dict with keys: win_rate, profit, total_evaluated
    """
    from sports.models import MLPrediction

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Get today's evaluated predictions
    today_predictions = MLPrediction.objects.filter(
        created_at__gte=today_start,
        was_correct__isnull=False  # Only evaluated predictions
    )

    if today_predictions.count() == 0:
        # No evaluated predictions today yet
        return {
            'win_rate': 0.0,
            'profit': 0.0,
            'total_evaluated': 0
        }

    correct = today_predictions.filter(was_correct=True).count()
    total = today_predictions.count()
    win_rate = (correct / total * 100) if total > 0 else 0.0

    # Calculate profit (simplified: 1 unit per bet, -110 odds)
    # Win = +0.91 units (bet $1.10 to win $1.00)
    # Loss = -1.00 units
    wins = correct
    losses = total - correct
    profit = (wins * 0.91) - (losses * 1.0)

    return {
        'win_rate': round(win_rate, 1),
        'profit': round(profit, 1),
        'total_evaluated': total
    }


def format_prediction_for_frontend(game, prediction, ml_prediction, sport_type):
    """
    Format a prediction for frontend display

    Args:
        game: Game model instance
        prediction: dict from ML Engine
        ml_prediction: MLPrediction model instance
        sport_type: str like 'nfl', 'mlb', etc.

    Returns:
        dict formatted for frontend
    """
    key_factors = prediction.get('key_factors', [])
    reasoning = '; '.join(key_factors[:2]) if key_factors else 'Statistical analysis of team performance metrics'

    return {
        'game_id': str(game.id),
        'prediction_id': str(ml_prediction.id),
        'game': f"{game.away_team.name} @ {game.home_team.name}",
        'sport': sport_type.upper(),
        'pick': prediction['winner'],
        'confidence': round(prediction['confidence'] * 100, 1),
        'ai_reasoning': reasoning,
        'home_win_prob': round(prediction.get('home_win_probability', 0.5) * 100, 1),
        'away_win_prob': round(prediction.get('away_win_probability', 0.5) * 100, 1),
        'predicted_home_score': 0,  # Not available from current model
        'predicted_away_score': 0   # Not available from current model
    }