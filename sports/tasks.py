"""
Celery tasks for sports prediction tracking and evaluation
"""

import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='sports.evaluate_completed_predictions')
def evaluate_completed_predictions(hours_back=24):
    """
    Evaluate predictions for games that have completed

    This task:
    1. Finds all predictions for games with status=FINAL
    2. Evaluates each prediction (checks if predicted winner was correct)
    3. Updates the prediction with was_correct=True/False
    4. Logs accuracy statistics
    5. Identifies models that need retraining

    Should be run periodically (e.g., every hour)

    Args:
        hours_back: How many hours back to check for completed games (default: 24)

    Returns:
        dict with evaluation results and statistics
    """
    from sports.prediction_evaluator import PredictionEvaluator

    logger.info(f"🔍 Starting prediction evaluation task (last {hours_back} hours)")

    # Use the new PredictionEvaluator system
    evaluator = PredictionEvaluator()
    results = evaluator.evaluate_completed_games(hours_back=hours_back)

    # Log detailed results
    logger.info(
        f"✅ Evaluation complete: {results['evaluated']} predictions evaluated, "
        f"{results['correct']} correct ({results['accuracy']:.1f}% accuracy)"
    )

    # Log sport-specific results
    if results['by_sport']:
        logger.info("📊 Sport-specific accuracy:")
        for sport, stats in results['by_sport'].items():
            logger.info(
                f"  {sport.upper()}: {stats['correct']}/{stats['total']} "
                f"({stats['accuracy']:.1f}%)"
            )

    # Log model-specific results
    if results['by_model']:
        logger.info("🤖 Model-specific accuracy:")
        for model, stats in results['by_model'].items():
            logger.info(
                f"  {model}: {stats['correct']}/{stats['total']} "
                f"({stats['accuracy']:.1f}%)"
            )

    # Check for models that need retraining
    retraining_candidates = evaluator.identify_retraining_candidates()
    if retraining_candidates:
        logger.warning(
            f"⚠️  Models need retraining: {', '.join([s.upper() for s in retraining_candidates])}"
        )
        results['needs_retraining'] = retraining_candidates
    else:
        logger.info("✅ All models performing within acceptable range")
        results['needs_retraining'] = []

    # Log any errors
    if results['errors']:
        logger.error(f"❌ {len(results['errors'])} errors during evaluation:")
        for error in results['errors']:
            logger.error(f"  - {error}")

    return results


@shared_task(name='sports.settle_user_bets')
def settle_user_bets():
    """
    Settle user bets for games that have completed

    This task:
    1. Finds all pending bets for games with status=FINAL
    2. Settles each bet (calculates profit/loss)
    3. Updates bet status to WON/LOST/PUSH
    4. Logs settlement statistics

    Should be run periodically (e.g., every 15 minutes)
    """
    from sports.models import UserBet, BetStatus, GameStatus

    logger.info("Starting bet settlement task")

    # Get all pending bets for completed games
    pending_bets = UserBet.objects.filter(
        status=BetStatus.PENDING,
        game__status=GameStatus.FINAL
    ).select_related('game', 'user', 'selected_team')

    total_settled = 0
    total_won = 0
    total_lost = 0
    total_push = 0
    total_profit = 0.0

    for bet in pending_bets:
        try:
            bet.settle()
            total_settled += 1

            if bet.status == BetStatus.WON:
                total_won += 1
                total_profit += float(bet.profit_loss or 0)
                logger.info(
                    f"✓ Bet WON: {bet.user.username} - {bet.bet_amount} units on "
                    f"{bet.selected_team.abbreviation} → Profit: {bet.profit_loss} units"
                )
            elif bet.status == BetStatus.LOST:
                total_lost += 1
                total_profit += float(bet.profit_loss or 0)
                logger.info(
                    f"✗ Bet LOST: {bet.user.username} - {bet.bet_amount} units on "
                    f"{bet.selected_team.abbreviation} → Loss: {bet.profit_loss} units"
                )
            elif bet.status == BetStatus.PUSH:
                total_push += 1
                logger.info(
                    f"= Bet PUSH: {bet.user.username} - {bet.bet_amount} units on "
                    f"{bet.selected_team.abbreviation} → Refunded"
                )
        except Exception as e:
            logger.error(f"Error settling bet {bet.id}: {e}")
            continue

    if total_settled > 0:
        logger.info(
            f"Settled {total_settled} bets: {total_won} won, {total_lost} lost, "
            f"{total_push} push → Net profit: {total_profit:.2f} units"
        )
    else:
        logger.info("No completed games with pending bets found")

    return {
        'settled': total_settled,
        'won': total_won,
        'lost': total_lost,
        'push': total_push,
        'profit': round(total_profit, 2)
    }


@shared_task(name='sports.update_game_scores')
def update_game_scores():
    """
    Update game scores from external API (placeholder for future implementation)

    This task would:
    1. Query external sports data API for completed games
    2. Update game scores in database
    3. Update game status to FINAL
    4. Trigger prediction evaluation

    Currently just a placeholder - implement when API access is available
    """
    logger.info("Game score update task - Not yet implemented (requires external API)")
    logger.info("Manual score updates can be done via Django admin")

    return {
        'status': 'not_implemented',
        'message': 'Requires external sports data API integration'
    }


@shared_task(name='sports.generate_accuracy_report')
def generate_accuracy_report():
    """
    Generate accuracy report for all models and sports

    This task:
    1. Calculates accuracy for each sport/model combination
    2. Identifies best performing models
    3. Logs comprehensive report

    Should be run daily
    """
    from sports.models import MLPrediction

    logger.info("=" * 80)
    logger.info("SPORTS PREDICTION ACCURACY REPORT")
    logger.info("=" * 80)

    sports = ['nfl', 'nba', 'mlb', 'nhl']
    overall_stats = {
        'total_predictions': 0,
        'total_correct': 0,
        'by_sport': {}
    }

    for sport in sports:
        # Last 7 days accuracy
        stats_7d = MLPrediction.calculate_accuracy(sport_type=sport, days=7)

        # Last 30 days accuracy
        stats_30d = MLPrediction.calculate_accuracy(sport_type=sport, days=30)

        # All time accuracy
        stats_all = MLPrediction.calculate_accuracy(sport_type=sport, days=365)

        overall_stats['by_sport'][sport] = {
            '7_days': stats_7d,
            '30_days': stats_30d,
            'all_time': stats_all
        }

        overall_stats['total_predictions'] += stats_all['total_predictions']
        overall_stats['total_correct'] += stats_all['correct_predictions']

        logger.info(f"\n{sport.upper()} Prediction Accuracy:")
        logger.info(f"  Last 7 days:  {stats_7d['total_predictions']:3d} predictions, "
                   f"{stats_7d['correct_predictions']:3d} correct ({stats_7d['accuracy_percentage']:5.1f}%)")
        logger.info(f"  Last 30 days: {stats_30d['total_predictions']:3d} predictions, "
                   f"{stats_30d['correct_predictions']:3d} correct ({stats_30d['accuracy_percentage']:5.1f}%)")
        logger.info(f"  All time:     {stats_all['total_predictions']:3d} predictions, "
                   f"{stats_all['correct_predictions']:3d} correct ({stats_all['accuracy_percentage']:5.1f}%)")

    if overall_stats['total_predictions'] > 0:
        overall_accuracy = (overall_stats['total_correct'] / overall_stats['total_predictions']) * 100
        logger.info(f"\n{'='*80}")
        logger.info(f"OVERALL: {overall_stats['total_predictions']} predictions, "
                   f"{overall_stats['total_correct']} correct ({overall_accuracy:.1f}% accuracy)")
        logger.info(f"{'='*80}\n")
    else:
        logger.info("\nNo predictions have been evaluated yet")
        logger.info("="*80 + "\n")

    return overall_stats


@shared_task(name='sports.cleanup_old_predictions')
def cleanup_old_predictions(days=90):
    """
    Clean up old prediction data

    This task:
    1. Deletes predictions older than specified days
    2. Keeps a summary for historical analysis

    Should be run weekly

    Args:
        days: Keep predictions from last N days (default: 90)
    """
    from sports.models import MLPrediction

    cutoff_date = timezone.now() - timedelta(days=days)

    old_predictions = MLPrediction.objects.filter(created_at__lt=cutoff_date)
    count = old_predictions.count()

    if count > 0:
        # Could save summary statistics before deleting
        # For now, just delete
        old_predictions.delete()
        logger.info(f"Cleaned up {count} predictions older than {days} days")
    else:
        logger.info(f"No predictions older than {days} days found")

    return {
        'deleted': count,
        'cutoff_days': days
    }