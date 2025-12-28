"""
ML Model Retrainer - Session 24
Automatic model retraining system that learns from evaluated predictions
"""

import logging
import joblib
import pandas as pd
from datetime import timedelta
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, log_loss
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class ModelRetrainer:
    """
    Retrains ML models using evaluated predictions

    Features:
    - Checks if retraining needed (performance thresholds)
    - Collects evaluated predictions as training data
    - Trains new model with updated data
    - Validates performance before deployment
    - Manages model versions
    """

    def __init__(self):
        self.ml_engine = None
        self.min_predictions_for_retrain = 100
        self.accuracy_threshold = 0.55  # Retrain if below 55%
        self.calibration_threshold = 0.15  # Retrain if error > 15%
        self.improvement_threshold = 0.02  # Deploy if +2% better
        self.model_dir = Path("ml/trained_models")

        # Ensure model directories exist
        for sport in ['nfl', 'nba', 'mlb', 'nhl']:
            (self.model_dir / sport).mkdir(parents=True, exist_ok=True)

    def should_retrain(self, sport_type: str) -> Tuple[bool, str]:
        """
        Check if model needs retraining

        Criteria:
        1. At least 100 new evaluated predictions since last training
        2. OR accuracy dropped below 55%
        3. OR calibration error > 15%

        Args:
            sport_type: 'nfl', 'nba', 'mlb', or 'nhl'

        Returns:
            (should_retrain: bool, reason: str)
        """
        try:
            from sports.models import MLPrediction
            from sports.prediction_evaluator import PredictionEvaluator

            # Check if enough evaluated predictions exist
            evaluated_count = MLPrediction.objects.filter(
                sport_type=sport_type,
                was_correct__isnull=False
            ).count()

            if evaluated_count < self.min_predictions_for_retrain:
                return False, f"Only {evaluated_count} evaluated predictions (need {self.min_predictions_for_retrain})"

            # Calculate current accuracy
            evaluator = PredictionEvaluator()
            metrics = evaluator.calculate_sport_accuracy(sport_type)

            if not metrics:
                return True, "No performance metrics available - initial training needed"

            current_accuracy = metrics.get('win_rate', 0.0)

            # Check accuracy threshold
            if current_accuracy < self.accuracy_threshold:
                return True, f"Accuracy {current_accuracy:.1%} below threshold {self.accuracy_threshold:.1%}"

            # Check calibration error
            calibration_error = metrics.get('calibration_error', 0.0)
            if calibration_error > self.calibration_threshold:
                return True, f"Calibration error {calibration_error:.1%} exceeds threshold {self.calibration_threshold:.1%}"

            # Check if we have enough new predictions since last retrain
            try:
                from ml.models import MLModelVersion
                latest_version = MLModelVersion.objects.filter(
                    sport_type=sport_type,
                    is_active=True
                ).first()

                if latest_version:
                    new_predictions_count = MLPrediction.objects.filter(
                        sport_type=sport_type,
                        was_correct__isnull=False,
                        prediction_time__gte=latest_version.trained_date
                    ).count()

                    if new_predictions_count >= self.min_predictions_for_retrain:
                        return True, f"{new_predictions_count} new evaluated predictions available"
            except Exception as e:
                logger.warning(f"Could not check model version: {e}")

            return False, f"No retraining needed (accuracy: {current_accuracy:.1%}, {evaluated_count} predictions)"

        except Exception as e:
            logger.error(f"Error checking retraining needs for {sport_type}: {e}")
            return False, f"Error: {str(e)}"

    def collect_training_data(self, sport_type: str) -> Optional[Tuple[pd.DataFrame, pd.Series]]:
        """
        Collect evaluated predictions and prepare training data

        Args:
            sport_type: 'nfl', 'nba', 'mlb', or 'nhl'

        Returns:
            (X: features DataFrame, y: labels Series) or None if insufficient data
        """
        try:
            from sports.models import MLPrediction

            # Get all evaluated predictions for this sport
            predictions = MLPrediction.objects.filter(
                sport_type=sport_type,
                was_correct__isnull=False
            ).select_related('game', 'game__home_team', 'game__away_team').order_by('prediction_time')

            if predictions.count() < self.min_predictions_for_retrain:
                logger.warning(f"Not enough data for {sport_type}: {predictions.count()} predictions")
                return None

            logger.info(f"Collecting {predictions.count()} evaluated predictions for {sport_type}")

            # Extract features and labels
            features_list = []
            labels_list = []

            for pred in predictions:
                game = pred.game

                # Extract features (same as original training)
                features = self._extract_game_features(game, sport_type)

                # Label: 1 if home team won, 0 if away team won
                label = 1 if pred.was_correct and pred.predicted_winner == game.home_team.name else 0
                if not pred.was_correct and pred.predicted_winner == game.away_team.name:
                    label = 1
                if not pred.was_correct and pred.predicted_winner == game.home_team.name:
                    label = 0

                features_list.append(features)
                labels_list.append(label)

            # Convert to DataFrame
            X = pd.DataFrame(features_list)
            y = pd.Series(labels_list)

            logger.info(f"Prepared training data: {len(X)} samples, {len(X.columns)} features")

            return X, y

        except Exception as e:
            logger.error(f"Error collecting training data for {sport_type}: {e}")
            return None

    def _extract_game_features(self, game, sport_type: str) -> Dict[str, float]:
        """
        Extract features from a game (same as original training)

        Args:
            game: Game model instance
            sport_type: Sport type

        Returns:
            Dictionary of feature values
        """
        features = {}

        try:
            # Basic features
            features['home_win_streak'] = getattr(game, 'home_win_streak', 0)
            features['away_win_streak'] = getattr(game, 'away_win_streak', 0)
            features['home_form'] = getattr(game, 'home_form', 0.5)
            features['away_form'] = getattr(game, 'away_form', 0.5)

            # Sport-specific features
            if sport_type == 'nfl':
                features['home_pass_yards_avg'] = getattr(game, 'home_pass_yards_avg', 250)
                features['away_pass_yards_avg'] = getattr(game, 'away_pass_yards_avg', 250)
                features['home_rush_yards_avg'] = getattr(game, 'home_rush_yards_avg', 120)
                features['away_rush_yards_avg'] = getattr(game, 'away_rush_yards_avg', 120)
            elif sport_type == 'nba':
                features['home_ppg'] = getattr(game, 'home_ppg', 110)
                features['away_ppg'] = getattr(game, 'away_ppg', 110)
                features['home_3pt_pct'] = getattr(game, 'home_3pt_pct', 0.35)
                features['away_3pt_pct'] = getattr(game, 'away_3pt_pct', 0.35)
            elif sport_type == 'mlb':
                features['home_era'] = getattr(game, 'home_era', 4.0)
                features['away_era'] = getattr(game, 'away_era', 4.0)
                features['home_batting_avg'] = getattr(game, 'home_batting_avg', 0.250)
                features['away_batting_avg'] = getattr(game, 'away_batting_avg', 0.250)
            elif sport_type == 'nhl':
                features['home_goals_pg'] = getattr(game, 'home_goals_pg', 3.0)
                features['away_goals_pg'] = getattr(game, 'away_goals_pg', 3.0)
                features['home_save_pct'] = getattr(game, 'home_save_pct', 0.910)
                features['away_save_pct'] = getattr(game, 'away_save_pct', 0.910)

            # Odds (if available)
            features['home_odds'] = getattr(game, 'home_odds', 1.95)
            features['away_odds'] = getattr(game, 'away_odds', 1.95)

        except Exception as e:
            logger.warning(f"Error extracting features: {e}")

        return features

    def train_new_model(self, X_train: pd.DataFrame, y_train: pd.Series, sport_type: str) -> Tuple[Any, StandardScaler]:
        """
        Train a new model with the data

        Args:
            X_train: Training features
            y_train: Training labels
            sport_type: Sport type

        Returns:
            (trained_model, scaler)
        """
        logger.info(f"Training new {sport_type.upper()} model with {len(X_train)} samples")

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        # Train ensemble model (Random Forest + Gradient Boosting)
        # Random Forest for robustness
        rf_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train_scaled, y_train)

        logger.info(f"Model training complete for {sport_type.upper()}")

        return rf_model, scaler

    def validate_model(self, model, scaler, X_test: pd.DataFrame, y_test: pd.Series, sport_type: str) -> Dict[str, float]:
        """
        Validate model performance on test set

        Args:
            model: Trained model
            scaler: Feature scaler
            X_test: Test features
            y_test: Test labels
            sport_type: Sport type

        Returns:
            Dictionary of performance metrics
        """
        logger.info(f"Validating {sport_type.upper()} model on {len(X_test)} test samples")

        # Scale test features
        X_test_scaled = scaler.transform(X_test)

        # Make predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)

        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)

        # Calibration score (log loss)
        try:
            calibration = log_loss(y_test, y_pred_proba)
        except:
            calibration = 0.5

        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'calibration_score': calibration,
            'test_samples': len(X_test)
        }

        logger.info(f"Validation metrics for {sport_type.upper()}: Accuracy={accuracy:.1%}, Precision={precision:.1%}, Recall={recall:.1%}")

        return metrics

    def should_deploy_new_model(self, new_metrics: Dict[str, float], sport_type: str) -> Tuple[bool, str]:
        """
        Decide if new model should replace current model

        Criteria:
        - New accuracy >= old accuracy + 2%
        - OR (same accuracy AND better calibration)

        Args:
            new_metrics: New model metrics
            sport_type: Sport type

        Returns:
            (should_deploy: bool, reason: str)
        """
        try:
            from ml.models import MLModelVersion

            current_version = MLModelVersion.objects.filter(
                sport_type=sport_type,
                is_active=True
            ).first()

            if not current_version:
                return True, "No active model - deploying new model"

            old_accuracy = current_version.test_accuracy
            new_accuracy = new_metrics['accuracy']

            # Check if significantly better
            if new_accuracy >= old_accuracy + self.improvement_threshold:
                improvement = (new_accuracy - old_accuracy) * 100
                return True, f"Accuracy improved by {improvement:.1f}% ({old_accuracy:.1%} → {new_accuracy:.1%})"

            # Check if same accuracy but better calibration
            if abs(new_accuracy - old_accuracy) < 0.01:
                old_calibration = current_version.calibration_score
                new_calibration = new_metrics['calibration_score']

                if new_calibration < old_calibration:
                    return True, f"Same accuracy but better calibration ({old_calibration:.3f} → {new_calibration:.3f})"

            return False, f"New model not better enough (old: {old_accuracy:.1%}, new: {new_accuracy:.1%})"

        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            return False, f"Error: {str(e)}"

    def save_model_version(self, model, scaler, metrics: Dict[str, float], sport_type: str,
                          training_samples: int, deploy: bool = True) -> Optional[int]:
        """
        Save model as new version

        Args:
            model: Trained model
            scaler: Feature scaler
            metrics: Performance metrics
            sport_type: Sport type
            training_samples: Number of training samples
            deploy: Whether to activate this version

        Returns:
            Version number or None if failed
        """
        try:
            from ml.models import MLModelVersion
            from django.utils import timezone

            # Get next version number
            latest_version = MLModelVersion.objects.filter(
                sport_type=sport_type
            ).order_by('-version').first()

            next_version = (latest_version.version + 1) if latest_version else 1

            # Save model and scaler to disk
            model_filename = f"{sport_type}_predictor_v{next_version}.joblib"
            scaler_filename = f"{sport_type}_scaler_v{next_version}.joblib"

            model_path = self.model_dir / sport_type / model_filename
            scaler_path = self.model_dir / sport_type / scaler_filename

            joblib.dump(model, model_path)
            joblib.dump(scaler, scaler_path)

            logger.info(f"Saved {sport_type.upper()} model v{next_version} to {model_path}")

            # Create database record
            model_version = MLModelVersion.objects.create(
                sport_type=sport_type,
                model_name=f"{sport_type}_predictor",
                version=next_version,
                training_samples=training_samples,
                training_start_date=timezone.now().date() - timedelta(days=90),
                training_end_date=timezone.now().date(),
                validation_accuracy=metrics['accuracy'],
                test_accuracy=metrics['accuracy'],
                calibration_score=metrics['calibration_score'],
                precision=metrics.get('precision', 0.0),
                recall=metrics.get('recall', 0.0),
                model_file_path=str(model_path),
                training_metadata={
                    'scaler_path': str(scaler_path),
                    'test_samples': metrics.get('test_samples', 0),
                    'trained_by': 'ModelRetrainer',
                    'training_date': timezone.now().isoformat()
                }
            )

            if deploy:
                model_version.activate()
                logger.info(f"Activated {sport_type.upper()} model v{next_version}")

            return next_version

        except Exception as e:
            logger.error(f"Error saving model version: {e}")
            return None

    def retrain_model(self, sport_type: str, force: bool = False) -> Dict[str, Any]:
        """
        Complete retraining workflow

        Steps:
        1. Check if retraining needed
        2. Collect training data
        3. Split train/test
        4. Train new model
        5. Validate performance
        6. Compare to current model
        7. Deploy if better

        Args:
            sport_type: 'nfl', 'nba', 'mlb', or 'nhl'
            force: Force retraining even if criteria not met

        Returns:
            Result dictionary with status and metrics
        """
        result = {
            'sport_type': sport_type,
            'success': False,
            'message': '',
            'metrics': {},
            'version': None,
            'deployed': False
        }

        try:
            logger.info(f"=== Starting retraining for {sport_type.upper()} ===")

            # Step 1: Check if needed
            if not force:
                should_retrain, reason = self.should_retrain(sport_type)
                if not should_retrain:
                    result['message'] = f"Retraining not needed: {reason}"
                    logger.info(result['message'])
                    return result
                logger.info(f"Retraining needed: {reason}")
            else:
                logger.info("Force retraining enabled")

            # Step 2: Collect data
            training_data = self.collect_training_data(sport_type)
            if training_data is None:
                result['message'] = "Insufficient training data"
                logger.error(result['message'])
                return result

            X, y = training_data

            # Step 3: Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            logger.info(f"Split data: {len(X_train)} train, {len(X_test)} test")

            # Step 4: Train model
            model, scaler = self.train_new_model(X_train, y_train, sport_type)

            # Step 5: Validate
            metrics = self.validate_model(model, scaler, X_test, y_test, sport_type)
            result['metrics'] = metrics

            # Step 6: Compare to current
            should_deploy, deploy_reason = self.should_deploy_new_model(metrics, sport_type)
            logger.info(f"Deployment decision: {deploy_reason}")

            # Step 7: Save and deploy
            version = self.save_model_version(
                model, scaler, metrics, sport_type,
                training_samples=len(X_train),
                deploy=should_deploy
            )

            if version:
                result['success'] = True
                result['version'] = version
                result['deployed'] = should_deploy
                result['message'] = f"Model v{version} trained successfully. {deploy_reason}"
                logger.info(f"✅ {result['message']}")
            else:
                result['message'] = "Failed to save model"
                logger.error(result['message'])

            logger.info(f"=== Retraining complete for {sport_type.upper()} ===")

        except Exception as e:
            result['message'] = f"Retraining failed: {str(e)}"
            logger.error(result['message'], exc_info=True)

        return result