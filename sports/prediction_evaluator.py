"""
Sports Prediction Evaluation System

Automatically evaluates ML predictions when games complete.
This is the core of the agent learning loop - tracking prediction accuracy
so models can learn and improve over time.

Created: Session 23 - Agent-ML Learning Integration
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count, Avg

from sports.models import Game, MLPrediction, GameStatus

logger = logging.getLogger(__name__)


class PredictionEvaluator:
    """
    Evaluates ML predictions against actual game outcomes

    This is the first step in the learning loop:
    1. Find completed games
    2. Evaluate their predictions
    3. Update statistics
    4. Provide data for model retraining
    """

    def __init__(self):
        self.evaluated_count = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.errors = []

    def evaluate_completed_games(self, hours_back: int = 24, feed_to_learning_loop: bool = True) -> Dict:
        """
        Find games that completed recently and evaluate their predictions

        NEW (Session 37-A): Integrated with core learning loop!
        Predictions now flow to UnifiedLearningPipeline for cross-domain intelligence.

        Args:
            hours_back: How many hours back to check for completed games
            feed_to_learning_loop: Whether to send results to core learning loop (default: True)

        Returns:
            dict with evaluation results and statistics
        """
        logger.info(f"Starting prediction evaluation for last {hours_back} hours")

        # Find games that completed in the last N hours
        cutoff_time = timezone.now() - timedelta(hours=hours_back)

        completed_games = Game.objects.filter(
            status=GameStatus.FINAL,
            scheduled_start__gte=cutoff_time
        ).select_related('home_team', 'away_team', 'league')

        logger.info(f"Found {completed_games.count()} completed games to evaluate")

        # Reset counters
        self.evaluated_count = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.errors = []
        self.evaluated_predictions = []  # Store for learning loop integration

        # Evaluate each game's predictions
        for game in completed_games:
            self._evaluate_game_predictions(game)

        # Calculate statistics
        stats = self._calculate_evaluation_stats()

        logger.info(
            f"Evaluation complete: {self.evaluated_count} predictions evaluated, "
            f"{self.correct_count} correct, {self.incorrect_count} incorrect"
        )

        # NEW: Feed results into core learning loop
        learning_loop_result = None
        if feed_to_learning_loop and self.evaluated_predictions:
            learning_loop_result = self._feed_to_learning_loop(self.evaluated_predictions)

        return {
            'evaluated': self.evaluated_count,
            'correct': self.correct_count,
            'incorrect': self.incorrect_count,
            'accuracy': stats['accuracy'],
            'by_sport': stats['by_sport'],
            'by_model': stats['by_model'],
            'errors': self.errors,
            'learning_loop_integration': learning_loop_result  # NEW
        }

    def _evaluate_game_predictions(self, game: Game) -> None:
        """
        Evaluate all predictions for a specific game

        Args:
            game: Completed Game instance
        """
        # Find all predictions for this game that haven't been evaluated
        predictions = MLPrediction.objects.filter(
            game=game,
            was_correct__isnull=True  # Only unevaluated predictions
        )

        if not predictions.exists():
            logger.debug(f"No unevaluated predictions for game {game.id}")
            return

        logger.info(f"Evaluating {predictions.count()} predictions for game {game.id}")

        # Determine actual outcome
        actual_winner, outcome_type = self._determine_actual_winner(game)

        if actual_winner is None:
            logger.warning(f"Cannot determine winner for game {game.id} - tie or invalid scores")
            return

        # Evaluate each prediction
        for prediction in predictions:
            try:
                self._evaluate_single_prediction(prediction, game, actual_winner, outcome_type)
                self.evaluated_count += 1
            except Exception as e:
                error_msg = f"Error evaluating prediction {prediction.id}: {str(e)}"
                logger.error(error_msg)
                self.errors.append(error_msg)

    def _determine_actual_winner(self, game: Game) -> Tuple[Optional['Team'], str]:
        """
        Determine the actual winner of a completed game

        Args:
            game: Completed Game instance

        Returns:
            Tuple of (winning Team, outcome_type)
            outcome_type: 'home_win', 'away_win', 'tie', or 'invalid'
        """
        if game.home_score is None or game.away_score is None:
            return None, 'invalid'

        if game.home_score > game.away_score:
            return game.home_team, 'home_win'
        elif game.away_score > game.home_score:
            return game.away_team, 'away_win'
        else:
            return None, 'tie'  # Ties not evaluated (rare in most sports)

    def _evaluate_single_prediction(
        self,
        prediction: MLPrediction,
        game: Game,
        actual_winner,
        outcome_type: str
    ) -> None:
        """
        Evaluate a single prediction against actual outcome

        Args:
            prediction: MLPrediction instance to evaluate
            game: The completed Game
            actual_winner: The winning Team
            outcome_type: Type of outcome ('home_win', 'away_win', etc.)
        """
        # Check if prediction was correct
        was_correct = (prediction.predicted_winner == actual_winner)

        # Calculate prediction quality metrics
        confidence_calibration = self._calculate_confidence_calibration(
            prediction, was_correct
        )

        # Update prediction with evaluation results
        with transaction.atomic():
            prediction.was_correct = was_correct
            prediction.evaluated_at = timezone.now()

            # Closing odds fallback: use odds_at_prediction if no closing snapshot
            if prediction.closing_odds is None and prediction.odds_at_prediction is not None:
                prediction.closing_odds = prediction.odds_at_prediction

            # Store evaluation details in inherited metadata JSONField
            prediction.metadata = {
                'outcome_type': outcome_type,
                'actual_winner': actual_winner.name,
                'predicted_confidence': float(prediction.confidence),
                'confidence_calibration': confidence_calibration,
                'home_score': game.home_score,
                'away_score': game.away_score,
                'evaluation_timestamp': timezone.now().isoformat()
            }

            prediction.save()

        # NEW: Store evaluated prediction for learning loop integration
        self.evaluated_predictions.append(prediction)

        # Update counters
        if was_correct:
            self.correct_count += 1
            logger.info(
                f"✅ Prediction {prediction.id} CORRECT: "
                f"Predicted {prediction.predicted_winner.name}, "
                f"Actual {actual_winner.name} "
                f"(Confidence: {prediction.confidence:.1f}%)"
            )
        else:
            self.incorrect_count += 1
            logger.info(
                f"❌ Prediction {prediction.id} INCORRECT: "
                f"Predicted {prediction.predicted_winner.name}, "
                f"Actual {actual_winner.name} "
                f"(Confidence: {prediction.confidence:.1f}%)"
            )

    def _calculate_confidence_calibration(
        self,
        prediction: MLPrediction,
        was_correct: bool
    ) -> float:
        """
        Calculate how well-calibrated the prediction confidence was

        A well-calibrated model should be correct X% of the time when it
        predicts with X% confidence.

        Args:
            prediction: The prediction being evaluated
            was_correct: Whether prediction was correct

        Returns:
            float: Calibration score (0-1, higher is better)
        """
        # Get the predicted probability for the outcome that occurred
        if prediction.predicted_winner == prediction.game.home_team:
            predicted_prob = prediction.home_win_probability / 100.0
        else:
            predicted_prob = prediction.away_win_probability / 100.0

        # For correct predictions, calibration is how close predicted_prob is to 1.0
        # For incorrect predictions, calibration is how close predicted_prob is to 0.0
        if was_correct:
            calibration = predicted_prob  # Higher confidence = better calibration
        else:
            calibration = 1.0 - predicted_prob  # Lower confidence = better calibration

        return calibration

    def _calculate_evaluation_stats(self) -> Dict:
        """
        Calculate overall evaluation statistics

        Returns:
            dict with accuracy metrics broken down by sport and model
        """
        # Overall accuracy
        accuracy = (
            (self.correct_count / self.evaluated_count * 100)
            if self.evaluated_count > 0
            else 0.0
        )

        # Accuracy by sport
        by_sport = self._calculate_accuracy_by_sport()

        # Accuracy by model
        by_model = self._calculate_accuracy_by_model()

        return {
            'accuracy': round(accuracy, 2),
            'by_sport': by_sport,
            'by_model': by_model
        }

    def _calculate_accuracy_by_sport(self) -> Dict[str, float]:
        """Calculate accuracy broken down by sport type"""
        # Get all evaluated predictions grouped by sport
        sports_stats = MLPrediction.objects.filter(
            was_correct__isnull=False
        ).values('sport_type').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(was_correct=True))
        )

        result = {}
        for stat in sports_stats:
            sport = stat['sport_type']
            total = stat['total']
            correct = stat['correct']
            accuracy = (correct / total * 100) if total > 0 else 0
            result[sport] = {
                'accuracy': round(accuracy, 2),
                'total': total,
                'correct': correct,
                'incorrect': total - correct
            }

        return result

    def _calculate_accuracy_by_model(self) -> Dict[str, float]:
        """Calculate accuracy broken down by model type"""
        # Get all evaluated predictions grouped by model
        model_stats = MLPrediction.objects.filter(
            was_correct__isnull=False
        ).values('model_used').annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(was_correct=True))
        )

        result = {}
        for stat in model_stats:
            model = stat['model_used']
            total = stat['total']
            correct = stat['correct']
            accuracy = (correct / total * 100) if total > 0 else 0
            result[model] = {
                'accuracy': round(accuracy, 2),
                'total': total,
                'correct': correct,
                'incorrect': total - correct
            }

        return result

    def get_model_performance_summary(
        self,
        sport_type: Optional[str] = None,
        days_back: int = 30
    ) -> Dict:
        """
        Get comprehensive model performance summary

        Args:
            sport_type: Optional filter by sport ('nfl', 'nba', 'mlb', 'nhl')
            days_back: Number of days to look back

        Returns:
            dict with performance metrics
        """
        cutoff_date = timezone.now() - timedelta(days=days_back)

        # Base query
        query = MLPrediction.objects.filter(
            was_correct__isnull=False,
            created_at__gte=cutoff_date
        )

        # Filter by sport if specified
        if sport_type:
            query = query.filter(sport_type=sport_type)

        # Calculate metrics
        total = query.count()
        correct = query.filter(was_correct=True).count()
        accuracy = (correct / total * 100) if total > 0 else 0

        # Average confidence
        avg_confidence = query.aggregate(Avg('confidence'))['confidence__avg'] or 0

        # Confidence calibration
        # (comparing actual accuracy to predicted confidence)
        calibration_score = abs(accuracy - avg_confidence)

        return {
            'sport_type': sport_type or 'all',
            'days_analyzed': days_back,
            'total_predictions': total,
            'correct_predictions': correct,
            'incorrect_predictions': total - correct,
            'accuracy_percent': round(accuracy, 2),
            'average_confidence': round(avg_confidence, 2),
            'calibration_score': round(calibration_score, 2),
            'is_well_calibrated': calibration_score < 10.0  # Within 10% = good
        }

    def identify_retraining_candidates(self) -> List[str]:
        """
        Identify sports/models that need retraining

        Models need retraining if:
        1. Accuracy has dropped below 55% in last 30 days
        2. Have at least 50 evaluated predictions
        3. Calibration score > 15% (poorly calibrated)

        Returns:
            List of sport types that need retraining
        """
        candidates = []

        for sport in ['nfl', 'nba', 'mlb', 'nhl']:
            performance = self.get_model_performance_summary(sport, days_back=30)

            # Check retraining criteria
            needs_retraining = (
                performance['total_predictions'] >= 50 and
                (
                    performance['accuracy_percent'] < 55.0 or
                    performance['calibration_score'] > 15.0
                )
            )

            if needs_retraining:
                candidates.append(sport)
                logger.warning(
                    f"⚠️ {sport.upper()} model needs retraining: "
                    f"Accuracy={performance['accuracy_percent']}%, "
                    f"Calibration={performance['calibration_score']}"
                )

        return candidates

    def _feed_to_learning_loop(self, predictions: List[MLPrediction]) -> Dict:
        """
        Feed evaluated predictions into core learning loop (NEW - Session 37-A Integration)

        This is the KEY integration point between sports betting and core learning!
        Prediction results flow into the unified learning pipeline where they become
        available to ALL agents and advisors for cross-domain intelligence.

        Args:
            predictions: List of evaluated MLPrediction instances

        Returns:
            Dict with integration results
        """
        logger.info(f"Feeding {len(predictions)} predictions to core learning loop")

        try:
            from core.learning_bridges.sports_betting_bridge import SportsBettingLearningBridge

            # Import learning loop if available
            try:
                from ai_core.intelligence.learning_loop import learning_loop
                has_learning_loop = True
            except ImportError:
                logger.warning("ai_core.intelligence.learning_loop not available - skipping feedback")
                has_learning_loop = False

            results = {
                'success': True,
                'predictions_processed': 0,
                'feedback_items_created': 0,
                'errors': []
            }

            bridge = SportsBettingLearningBridge()

            for prediction in predictions:
                try:
                    # Create feedback item from prediction
                    feedback = bridge.create_feedback_from_prediction(prediction)

                    # Store feedback if learning loop available
                    if has_learning_loop:
                        learning_loop._store_feedback(feedback)
                        results['feedback_items_created'] += 1

                    results['predictions_processed'] += 1

                except Exception as e:
                    error_msg = f"Error processing prediction {prediction.id}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)

            logger.info(
                f"Learning loop integration complete: "
                f"{results['predictions_processed']} predictions processed, "
                f"{results['feedback_items_created']} feedback items created"
            )

            return results

        except Exception as e:
            logger.error(f"Error feeding to learning loop: {e}")
            return {
                'success': False,
                'error': str(e),
                'predictions_processed': 0
            }