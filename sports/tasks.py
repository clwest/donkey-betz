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
        # Session 1064: Dispatch retraining instead of just logging
        # Guards: dedup candidates, cooldown window (6h), structured logging
        try:
            from django.core.cache import cache
            from ml.tasks import retrain_sport_model
            dispatched = []
            for sport in set(retraining_candidates):  # dedup
                cooldown_key = f'retrain_cooldown:{sport}'
                if cache.get(cooldown_key):
                    logger.info(f"Skipping retrain for {sport}: cooldown active")
                    continue
                retrain_sport_model.delay(sport)
                cache.set(cooldown_key, True, timeout=6 * 3600)  # 6h cooldown
                dispatched.append(sport)
                logger.info(
                    f"retrain_dispatched: sport={sport} "
                    f"accuracy={results['by_sport'].get(sport, {}).get('accuracy', 'N/A')}%"
                )
            results['retrain_dispatched'] = dispatched
        except Exception as e:
            logger.error(f"Failed to dispatch retraining: {e}")
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
    Fetch final scores from The Odds API and update Game rows.

    1. Build reverse map: league abbreviation → Odds API sport_key
    2. Find non-FINAL Games from last 3 days that have predictions
    3. Group by sport_key, call TheOddsSpider.fetch_scores() per group
    4. Match by external_id, set home_score/away_score/status=FINAL
    """
    from collections import defaultdict
    from core.agents.markets.game_predictor import GamePredictor
    from ai_core.spiders.specialized.theodds_spider import TheOddsSpider
    from sports.models import Game, GameStatus

    # Build reverse map: league abbreviation → sport_key
    abbr_to_sport_key = {}
    for sport_key, (_, abbr, _) in GamePredictor.SPORT_KEY_LEAGUE.items():
        abbr_to_sport_key[abbr] = sport_key

    # Non-final games from last 3 days that have predictions
    cutoff = timezone.now() - timedelta(days=3)
    pending_games = (
        Game.objects.filter(
            scheduled_start__gte=cutoff,
            ml_predictions__isnull=False,
        )
        .exclude(status=GameStatus.FINAL)
        .select_related('league')
        .distinct()
    )

    if not pending_games.exists():
        logger.info("No pending games with predictions to update")
        return {'games_checked': 0, 'games_updated': 0, 'api_calls': 0}

    # Group games by sport_key
    games_by_sport_key = defaultdict(list)
    for game in pending_games:
        sport_key = abbr_to_sport_key.get(game.league.abbreviation)
        if sport_key:
            games_by_sport_key[sport_key].append(game)
        else:
            logger.debug(f"No sport_key mapping for league {game.league.abbreviation}")

    spider = TheOddsSpider()
    total_checked = 0
    total_updated = 0
    api_calls = 0
    errors = []

    for sport_key, games in games_by_sport_key.items():
        try:
            scores = spider.fetch_scores(sport_key, days_from=3)
            api_calls += 1
        except Exception as e:
            errors.append(f"{sport_key}: {e}")
            logger.error(f"Error fetching scores for {sport_key}: {e}")
            continue

        # Index scores by event_id for fast lookup
        score_map = {s['event_id']: s for s in scores if s.get('completed')}

        for game in games:
            total_checked += 1
            score_data = score_map.get(game.external_id)
            if not score_data:
                continue

            game.home_score = score_data['home_score']
            game.away_score = score_data['away_score']
            game.status = GameStatus.FINAL
            game.save(update_fields=['home_score', 'away_score', 'status', 'updated_at'])
            total_updated += 1
            logger.info(
                f"Updated {game.external_id}: "
                f"{game.home_team_id} {game.home_score} - "
                f"{game.away_team_id} {game.away_score} FINAL"
            )

            # Snapshot closing odds on predictions for CLV calculation
            try:
                from sports.models import MLPrediction
                preds = MLPrediction.objects.filter(
                    game=game, closing_odds__isnull=True
                )
                for pred in preds:
                    # Use the last known odds from the event data
                    if pred.predicted_winner_id == game.home_team_id:
                        closing = score_data.get('home_odds')
                    else:
                        closing = score_data.get('away_odds')
                    if closing is not None:
                        pred.closing_odds = int(closing)
                        pred.save(update_fields=['closing_odds', 'updated_at'])
            except Exception as e:
                logger.warning(f"Could not snapshot closing odds for {game.external_id}: {e}")

    logger.info(
        f"Score update complete: {total_checked} checked, "
        f"{total_updated} updated, {api_calls} API calls"
    )

    return {
        'games_checked': total_checked,
        'games_updated': total_updated,
        'api_calls': api_calls,
        'errors': errors,
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


@shared_task(name='sports.generate_game_predictions')
def generate_game_predictions():
    """
    Run GamePredictor to generate MLPrediction rows from current odds.

    Fetches odds for priority-1 sports (NFL, NBA, MLB, NHL, NCAAB, NCAAF,
    EPL, La Liga, MLS, etc.), generates win-probability predictions, and
    stores them in MLPrediction. Duplicates are skipped automatically by
    GamePredictor._store_predictions().
    """
    from core.agents.markets.game_predictor import GamePredictor

    logger.info("Starting scheduled prediction generation")

    predictor = GamePredictor()
    result = predictor.execute(
        task="Scheduled prediction run: generate predictions for upcoming games",
        context={},
    )

    stored = result.data.get('predictions_stored', 0) if result.data else 0
    total = result.data.get('predictions_generated', 0) if result.data else 0

    logger.info(
        f"Prediction generation complete: {total} generated, "
        f"{stored} stored (success={result.success})"
    )

    return {
        'success': result.success,
        'predictions_generated': total,
        'predictions_stored': stored,
        'total_games': result.data.get('total_games', 0) if result.data else 0,
    }


@shared_task(name='sports.verify_betting_outcomes')
def verify_betting_outcomes():
    """
    Verify outcomes for pending PlacedWager legs and watching arb items.

    Fetches scores for games that should have finished, settles wager legs
    (won/lost/push), settles parent wagers (parlays), and verifies arb items.
    """
    from core.services.betting_outcome_verifier import BettingOutcomeVerifier

    logger.info("Starting betting outcome verification")

    verifier = BettingOutcomeVerifier()
    summary = verifier.verify_all_pending()

    logger.info(
        f"Outcome verification complete: "
        f"{summary['wagers_settled']} wagers settled, "
        f"{summary['legs_settled']} legs settled, "
        f"{summary['arb_items_verified']} arb items verified"
    )

    if summary['errors']:
        logger.error(f"{len(summary['errors'])} errors during verification")
        for err in summary['errors'][:5]:
            logger.error(f"  - {err}")

    return summary


@shared_task(name='sports.run_market_analysis')
def run_market_analysis():
    """
    Session 1088: Run LineMovementAnalyzer and SharpActionDetector to detect
    sharp money movements and professional betting patterns.

    Called after GamePredictor generates predictions, so there's fresh odds
    data to analyze for line movements and sharp action signals.
    """
    from core.agents.markets.line_movement_analyzer import LineMovementAnalyzer
    from core.agents.markets.sharp_action_detector import SharpActionDetector

    results = {}

    # 1. Line Movement Analysis
    try:
        analyzer = LineMovementAnalyzer()
        lm_result = analyzer.execute(
            task="Detect reverse line movements, steam moves, and stale lines across active games",
            context={},
        )
        results['line_movement'] = {
            'success': lm_result.success,
            'signals': len(lm_result.data.get('movements', [])) if lm_result.data else 0,
        }
        logger.info(
            f"LineMovementAnalyzer: success={lm_result.success}, "
            f"signals={results['line_movement']['signals']}"
        )
    except Exception as e:
        logger.error(f"LineMovementAnalyzer failed: {e}")
        results['line_movement'] = {'success': False, 'error': str(e)}

    # 2. Sharp Action Detection
    try:
        detector = SharpActionDetector()
        sa_result = detector.execute(
            task="Identify sharp vs public book divergences and syndicate betting patterns",
            context={},
        )
        results['sharp_action'] = {
            'success': sa_result.success,
            'signals': len(sa_result.data.get('signals', [])) if sa_result.data else 0,
        }
        logger.info(
            f"SharpActionDetector: success={sa_result.success}, "
            f"signals={results['sharp_action']['signals']}"
        )
    except Exception as e:
        logger.error(f"SharpActionDetector failed: {e}")
        results['sharp_action'] = {'success': False, 'error': str(e)}

    return results