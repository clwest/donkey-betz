"""
Train NFL prediction model using historical game data

Usage: python manage.py train_nfl_model
"""

from django.core.management.base import BaseCommand
from sports.models import Game
from ml.core.ml_engine import MLEngine
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os


class Command(BaseCommand):
    help = 'Train NFL prediction model on historical games'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-games',
            type=int,
            default=100,
            help='Minimum number of games required for training (default: 100)'
        )
        parser.add_argument(
            '--test-split',
            type=float,
            default=0.2,
            help='Test set size as decimal (default: 0.2 = 20%)'
        )

    def handle(self, *args, **options):
        min_games = options['min_games']
        test_split = options['test_split']

        self.stdout.write("Initializing ML Engine...")
        ml_engine = MLEngine()

        # Get all completed games with scores
        games = Game.objects.filter(
            league__sport_type='nfl',
            status='final',
            home_score__isnull=False,
            away_score__isnull=False
        ).select_related('home_team', 'away_team').order_by('scheduled_start')

        total_games = games.count()

        if total_games < min_games:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Only {total_games} games found (minimum: {min_games})\n"
                    f"Import more data with: python manage.py import_nfl_historical_data\n"
                )
            )
            if total_games < 20:
                self.stdout.write(self.style.ERROR("Not enough data to train. Need at least 20 games."))
                return

        self.stdout.write(f"Found {total_games} completed games")

        # Extract features and labels
        X = []  # Features
        y = []  # Labels (1 = home win, 0 = away win)
        game_info = []  # For debugging

        self.stdout.write("Extracting features...")

        for i, game in enumerate(games):
            try:
                features = ml_engine._extract_nfl_game_features(game)
                X.append(features)

                # Label: 1 if home team won, 0 otherwise
                home_won = game.home_score > game.away_score
                y.append(1.0 if home_won else 0.0)

                game_info.append({
                    'away': game.away_team.name,
                    'home': game.home_team.name,
                    'score': f"{game.away_score}-{game.home_score}",
                    'winner': 'home' if home_won else 'away'
                })

                if (i + 1) % 100 == 0:
                    self.stdout.write(f"  Processed {i + 1}/{total_games} games...")

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Error processing game {game.id}: {e}")
                )

        X = np.array(X)
        y = np.array(y)

        self.stdout.write(f"\n✅ Extracted {len(X)} training examples")
        self.stdout.write(f"Feature dimensions: {X.shape}")

        # Check for NaN or Inf
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            self.stdout.write(self.style.WARNING("⚠️  Found NaN or Inf values, cleaning..."))
            X = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=-1.0)

        # Split into train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_split, random_state=42, stratify=y
        )

        self.stdout.write(f"\nTrain set: {len(X_train)} games")
        self.stdout.write(f"Test set: {len(X_test)} games")

        # Display class distribution
        home_wins = np.sum(y_train)
        away_wins = len(y_train) - home_wins
        self.stdout.write(f"\nClass distribution:")
        self.stdout.write(f"  Home wins: {int(home_wins)} ({home_wins/len(y_train)*100:.1f}%)")
        self.stdout.write(f"  Away wins: {int(away_wins)} ({away_wins/len(y_train)*100:.1f}%)")

        # Train model
        self.stdout.write("\n🚀 Training model...")
        model = ml_engine.models['sports_crypto_lstm']

        try:
            model.fit(X_train, y_train)
            self.stdout.write(self.style.SUCCESS("✅ Model training complete!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Training failed: {e}"))
            return

        # Evaluate on test set
        self.stdout.write("\n📊 Evaluating model...")

        y_pred = model.predict(X_test)
        y_pred_binary = (y_pred > 0.5).astype(int)

        accuracy = accuracy_score(y_test, y_pred_binary)

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(self.style.SUCCESS(f"Test Accuracy: {accuracy:.2%}"))
        self.stdout.write(f"{'='*50}")

        # Detailed metrics
        self.stdout.write("\nClassification Report:")
        report = classification_report(
            y_test,
            y_pred_binary,
            target_names=['Away Win', 'Home Win'],
            zero_division=0
        )
        self.stdout.write(report)

        # Baseline comparison
        # Always predict home team wins (most common)
        baseline_accuracy = np.sum(y_test) / len(y_test)
        improvement = (accuracy - baseline_accuracy) * 100

        self.stdout.write(f"\n📈 Model Performance:")
        self.stdout.write(f"  Model accuracy: {accuracy:.2%}")
        self.stdout.write(f"  Baseline (always home): {baseline_accuracy:.2%}")
        self.stdout.write(f"  Improvement: {improvement:+.1f} percentage points")

        # Save model
        self.stdout.write("\n💾 Saving model...")
        try:
            ml_engine.save_models()
            self.stdout.write(self.style.SUCCESS("✅ Model saved successfully!"))

            # Show model location
            model_path = os.path.join(ml_engine.config.model_cache_dir, 'sports_crypto_lstm.joblib')
            self.stdout.write(f"Model saved to: {model_path}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to save model: {e}"))

        # Sample predictions
        self.stdout.write("\n🎯 Sample Predictions (first 5 test games):")
        for i in range(min(5, len(X_test))):
            pred_prob = y_pred[i]
            actual = "Home" if y_test[i] == 1 else "Away"
            predicted = "Home" if pred_prob > 0.5 else "Away"
            correct = "✅" if (predicted == actual) else "❌"

            self.stdout.write(
                f"  {correct} Actual: {actual:5s} | Predicted: {predicted:5s} "
                f"(confidence: {max(pred_prob, 1-pred_prob):.1%})"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Training complete! Model ready for predictions.\n"
                f"Test with: python manage.py shell\n"
                f"  >>> from ml.core.ml_engine import MLEngine\n"
                f"  >>> ml = MLEngine()\n"
                f"  >>> ml.predict_nfl_game('game_id')\n"
            )
        )