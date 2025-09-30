"""
Universal Sport Model Training Command

Train prediction models for any sport (NFL, NBA, MLB, NHL).

Usage:
    python manage.py train_sport_model --sport nfl
    python manage.py train_sport_model --sport nba --test-split 0.2
    python manage.py train_sport_model --all
"""

from django.core.management.base import BaseCommand
from sports.models import Game
from ml.core.ml_engine import MLEngine
from ml.core.sport_configs import SPORT_CONFIGS, get_all_sports
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.neural_network import MLPRegressor


class Command(BaseCommand):
    help = 'Train prediction model for any sport'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sport',
            type=str,
            choices=['nfl', 'nba', 'mlb', 'nhl'],
            help='Sport to train (nfl, nba, mlb, nhl)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Train models for all sports'
        )
        parser.add_argument(
            '--test-split',
            type=float,
            default=0.2,
            help='Test set size as decimal (default: 0.2 = 20%%)'
        )
        parser.add_argument(
            '--min-games',
            type=int,
            default=None,
            help='Override minimum training games threshold'
        )

    def handle(self, *args, **options):
        if options['all']:
            sports_to_train = get_all_sports()
        elif options['sport']:
            sports_to_train = [options['sport']]
        else:
            self.stdout.write(self.style.ERROR(
                "❌ Must specify --sport <type> or --all"
            ))
            return

        for sport in sports_to_train:
            self.train_sport(sport, options['test_split'], options.get('min_games'))

    def train_sport(self, sport_type: str, test_split: float, min_games_override: int = None):
        """Train model for a specific sport"""
        config = SPORT_CONFIGS[sport_type]

        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS(f"  Training {config.name} Prediction Model"))
        self.stdout.write(f"{'='*70}\n")

        # Get completed games for this sport
        games = Game.objects.filter(
            league__sport_type=sport_type,
            status='final',
            home_score__isnull=False,
            away_score__isnull=False
        ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start')

        total_games = games.count()
        min_required = min_games_override if min_games_override else config.min_training_games

        self.stdout.write(f"📊 Found {total_games} completed {config.name} games")

        if total_games < min_required:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠️  Only {total_games} games found "
                    f"(minimum recommended: {min_required})\n"
                    f"   Import more historical data first:\n"
                    f"   python manage.py import_nfl_historical_data\n"
                )
            )
            if total_games < 50:
                self.stdout.write(self.style.ERROR(
                    "❌ Too few games to train model. Need at least 50 games.\n"
                ))
                return

            self.stdout.write(self.style.WARNING(
                "⚠️  Proceeding with limited dataset (model may underperform)...\n"
            ))

        # Initialize ML engine
        ml_engine = MLEngine()

        # Extract features
        X = []
        y = []

        self.stdout.write("🔍 Extracting features from games...")

        errors = 0
        for i, game in enumerate(games):
            try:
                features = ml_engine._extract_sport_features(game, config)
                X.append(features)

                # Binary classification: 1 if home team won, 0 if away team won
                home_won = game.home_score > game.away_score
                y.append(1.0 if home_won else 0.0)

                if (i + 1) % 100 == 0:
                    self.stdout.write(f"   Processed {i + 1}/{total_games} games...")

            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    self.stdout.write(
                        self.style.WARNING(f"   ⚠️  Error processing game {game.id}: {e}")
                    )

        if errors > 5:
            self.stdout.write(
                self.style.WARNING(f"   ⚠️  ... and {errors - 5} more errors")
            )

        X = np.array(X)
        y = np.array(y)

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Extracted {len(X)} training examples")
        )
        self.stdout.write(f"   Features per game: {X.shape[1]}")
        self.stdout.write(f"   Home wins: {int(y.sum())} ({y.mean():.1%})")
        self.stdout.write(f"   Away wins: {len(y) - int(y.sum())} ({1-y.mean():.1%})")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_split, random_state=42, stratify=y
        )

        self.stdout.write(f"\n📊 Dataset Split:")
        self.stdout.write(f"   Training set: {len(X_train)} games ({(1-test_split)*100:.0f}%)")
        self.stdout.write(f"   Test set:     {len(X_test)} games ({test_split*100:.0f}%)")

        # Create and train model
        # Use Random Forest for NHL (better with imbalanced data)
        # Use MLP for other sports
        if sport_type == 'nhl':
            from sklearn.ensemble import RandomForestClassifier
            self.stdout.write(f"\n🚀 Training {config.name} model...")
            self.stdout.write("   Architecture: Random Forest Classifier")
            self.stdout.write("   Trees: 200")
            self.stdout.write("   Max depth: 10")
            self.stdout.write("   Class weights: balanced\n")

            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                min_samples_split=20,
                min_samples_leaf=10,
                max_features='sqrt',
                class_weight='balanced',  # Handle class imbalance
                random_state=42,
                n_jobs=-1
            )

            model.fit(X_train, y_train)
        else:
            self.stdout.write(f"\n🚀 Training {config.name} model...")
            self.stdout.write("   Architecture: MLPRegressor (128→64→32)")
            self.stdout.write("   Activation: ReLU")
            self.stdout.write("   Optimizer: Adam")
            self.stdout.write("   Max iterations: 500\n")

            model = MLPRegressor(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42,
                verbose=False
            )

            model.fit(X_train, y_train)
        self.stdout.write(self.style.SUCCESS("✅ Model training complete!\n"))

        # Evaluate model
        self.stdout.write(f"{'='*70}")
        self.stdout.write("  Model Evaluation")
        self.stdout.write(f"{'='*70}\n")

        # Training set performance
        if sport_type == 'nhl':
            # Random Forest returns class labels directly
            y_train_pred_binary = model.predict(X_train)
            y_test_pred_binary = model.predict(X_test)
        else:
            # MLP Regressor returns continuous values
            y_train_pred = model.predict(X_train)
            y_train_pred_binary = (y_train_pred > 0.5).astype(int)
            y_test_pred = model.predict(X_test)
            y_test_pred_binary = (y_test_pred > 0.5).astype(int)

        train_accuracy = accuracy_score(y_train, y_train_pred_binary)
        test_accuracy = accuracy_score(y_test, y_test_pred_binary)

        # Baseline (always predict home win)
        baseline_accuracy = y_test.mean()

        self.stdout.write(f"📈 Accuracy Metrics:")
        self.stdout.write(f"   Training accuracy: {train_accuracy:.2%}")
        self.stdout.write(f"   Test accuracy:     {test_accuracy:.2%}")
        self.stdout.write(f"   Baseline (home):   {baseline_accuracy:.2%}")
        self.stdout.write(f"   Improvement:       {(test_accuracy - baseline_accuracy)*100:+.2f} percentage points")

        # Classification report
        self.stdout.write(f"\n📊 Detailed Classification Report:\n")
        report = classification_report(
            y_test,
            y_test_pred_binary,
            target_names=['Away Win', 'Home Win'],
            digits=3
        )
        self.stdout.write(report)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_test_pred_binary)
        self.stdout.write(f"🎯 Confusion Matrix:")
        self.stdout.write(f"                 Predicted")
        self.stdout.write(f"   Actual    Away    Home")
        self.stdout.write(f"   Away      {cm[0][0]:4d}    {cm[0][1]:4d}")
        self.stdout.write(f"   Home      {cm[1][0]:4d}    {cm[1][1]:4d}\n")

        # Save model
        ml_engine.sport_models[sport_type][config.model_name] = model
        ml_engine.save_sport_models()

        self.stdout.write(f"{'='*70}")
        self.stdout.write(self.style.SUCCESS(
            f"✅ {config.name} model trained and saved successfully!"
        ))
        self.stdout.write(f"   Model file: {config.model_name}.joblib")
        self.stdout.write(f"   Test accuracy: {test_accuracy:.2%}")
        self.stdout.write(f"{'='*70}\n")

        # Show sample predictions
        self._show_sample_predictions(ml_engine, sport_type, config, games[:5])

    def _show_sample_predictions(self, ml_engine, sport_type, config, sample_games):
        """Show predictions for sample games"""
        self.stdout.write(f"\n🎲 Sample Predictions:")
        self.stdout.write(f"{'='*70}\n")

        for game in sample_games:
            try:
                prediction = ml_engine.predict_game(str(game.id), sport_type)

                winner_symbol = "🏆" if prediction['winner'] == game.home_team.name else "⚠️"

                self.stdout.write(
                    f"{winner_symbol} {game.away_team.abbreviation} @ {game.home_team.abbreviation}: "
                    f"Predicted {prediction['winner_abbr']} "
                    f"({prediction['home_win_probability']:.1%} home)"
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠️  Could not predict game {game.id}: {e}")
                )

        self.stdout.write("")