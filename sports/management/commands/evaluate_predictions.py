"""
Management command to manually evaluate ML predictions

Usage:
    python manage.py evaluate_predictions
    python manage.py evaluate_predictions --hours 48
    python manage.py evaluate_predictions --sport nfl
    python manage.py evaluate_predictions --performance

Created: Session 23 - Agent-ML Learning Integration
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from sports.prediction_evaluator import PredictionEvaluator


class Command(BaseCommand):
    help = 'Evaluate ML predictions for completed games'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='How many hours back to check for completed games (default: 24)'
        )

        parser.add_argument(
            '--sport',
            type=str,
            choices=['nfl', 'nba', 'mlb', 'nhl'],
            help='Filter by specific sport'
        )

        parser.add_argument(
            '--performance',
            action='store_true',
            help='Show comprehensive performance summary'
        )

        parser.add_argument(
            '--retraining-check',
            action='store_true',
            help='Check which models need retraining'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        sport = options['sport']
        show_performance = options['performance']
        check_retraining = options['retraining_check']

        evaluator = PredictionEvaluator()

        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("🔍 PREDICTION EVALUATION SYSTEM"))
        self.stdout.write("=" * 80)
        self.stdout.write("")

        # Show performance summary if requested
        if show_performance:
            self._show_performance_summary(evaluator, sport)
            return

        # Check retraining needs if requested
        if check_retraining:
            self._check_retraining_needs(evaluator)
            return

        # Standard evaluation
        self._run_evaluation(evaluator, hours, sport)

    def _run_evaluation(self, evaluator, hours, sport_filter=None):
        """Run standard prediction evaluation"""
        self.stdout.write(f"Evaluating predictions from last {hours} hours...")
        if sport_filter:
            self.stdout.write(f"Filtering by sport: {sport_filter.upper()}")
        self.stdout.write("")

        # Run evaluation
        results = evaluator.evaluate_completed_games(hours_back=hours)

        # Display results
        self.stdout.write(self.style.SUCCESS(f"✅ Evaluation Complete!"))
        self.stdout.write("")
        self.stdout.write(f"Total Evaluated: {results['evaluated']}")
        self.stdout.write(self.style.SUCCESS(f"  ✓ Correct: {results['correct']}"))
        self.stdout.write(self.style.ERROR(f"  ✗ Incorrect: {results['incorrect']}"))
        self.stdout.write(f"  Accuracy: {results['accuracy']:.1f}%")
        self.stdout.write("")

        # Sport-specific breakdown
        if results['by_sport']:
            self.stdout.write("📊 " + self.style.NOTICE("Sport-Specific Accuracy:"))
            for sport, stats in results['by_sport'].items():
                # Apply filter if specified
                if sport_filter and sport != sport_filter:
                    continue

                accuracy_str = f"{stats['accuracy']:.1f}%"
                if stats['accuracy'] >= 55:
                    accuracy_style = self.style.SUCCESS(accuracy_str)
                elif stats['accuracy'] >= 50:
                    accuracy_style = self.style.WARNING(accuracy_str)
                else:
                    accuracy_style = self.style.ERROR(accuracy_str)

                self.stdout.write(
                    f"  {sport.upper():4s}: {stats['correct']:3d}/{stats['total']:3d} = {accuracy_style}"
                )
            self.stdout.write("")

        # Model-specific breakdown
        if results['by_model']:
            self.stdout.write("🤖 " + self.style.NOTICE("Model-Specific Accuracy:"))
            for model, stats in results['by_model'].items():
                accuracy_str = f"{stats['accuracy']:.1f}%"
                if stats['accuracy'] >= 55:
                    accuracy_style = self.style.SUCCESS(accuracy_str)
                elif stats['accuracy'] >= 50:
                    accuracy_style = self.style.WARNING(accuracy_str)
                else:
                    accuracy_style = self.style.ERROR(accuracy_str)

                self.stdout.write(
                    f"  {model:20s}: {stats['correct']:3d}/{stats['total']:3d} = {accuracy_style}"
                )
            self.stdout.write("")

        # Check for errors
        if results['errors']:
            self.stdout.write(self.style.ERROR(f"❌ {len(results['errors'])} Errors:"))
            for error in results['errors']:
                self.stdout.write(f"  - {error}")
            self.stdout.write("")

        self.stdout.write("=" * 80)

    def _show_performance_summary(self, evaluator, sport_filter=None):
        """Show comprehensive performance summary"""
        self.stdout.write("📊 " + self.style.SUCCESS("MODEL PERFORMANCE SUMMARY"))
        self.stdout.write("=" * 80)
        self.stdout.write("")

        sports = [sport_filter] if sport_filter else ['nfl', 'nba', 'mlb', 'nhl']

        for sport in sports:
            # Get 30-day performance
            performance = evaluator.get_model_performance_summary(sport, days_back=30)

            if performance['total_predictions'] == 0:
                self.stdout.write(f"{sport.upper()}: No predictions yet")
                self.stdout.write("")
                continue

            self.stdout.write(self.style.NOTICE(f"{sport.upper()} - Last 30 Days:"))
            self.stdout.write(f"  Total Predictions: {performance['total_predictions']}")
            self.stdout.write(f"  Correct: {performance['correct_predictions']}")
            self.stdout.write(f"  Incorrect: {performance['incorrect_predictions']}")

            # Color-code accuracy
            accuracy = performance['accuracy_percent']
            if accuracy >= 55:
                accuracy_style = self.style.SUCCESS(f"{accuracy:.1f}%")
            elif accuracy >= 50:
                accuracy_style = self.style.WARNING(f"{accuracy:.1f}%")
            else:
                accuracy_style = self.style.ERROR(f"{accuracy:.1f}%")

            self.stdout.write(f"  Accuracy: {accuracy_style}")
            self.stdout.write(f"  Avg Confidence: {performance['average_confidence']:.1f}%")

            # Calibration
            calibration = performance['calibration_score']
            if performance['is_well_calibrated']:
                calibration_style = self.style.SUCCESS(f"{calibration:.1f}% (Well Calibrated)")
            else:
                calibration_style = self.style.WARNING(f"{calibration:.1f}% (Needs Calibration)")

            self.stdout.write(f"  Calibration: {calibration_style}")
            self.stdout.write("")

        self.stdout.write("=" * 80)

    def _check_retraining_needs(self, evaluator):
        """Check which models need retraining"""
        self.stdout.write("🔧 " + self.style.NOTICE("RETRAINING CHECK"))
        self.stdout.write("=" * 80)
        self.stdout.write("")

        candidates = evaluator.identify_retraining_candidates()

        if candidates:
            self.stdout.write(self.style.WARNING(f"⚠️  {len(candidates)} model(s) need retraining:"))
            for sport in candidates:
                performance = evaluator.get_model_performance_summary(sport, days_back=30)
                self.stdout.write(f"  {sport.upper()}: Accuracy={performance['accuracy_percent']:.1f}%, Calibration={performance['calibration_score']:.1f}%")
            self.stdout.write("")
            self.stdout.write("Retraining recommended for these models.")
        else:
            self.stdout.write(self.style.SUCCESS("✅ All models performing within acceptable range!"))
            self.stdout.write("")
            self.stdout.write("No retraining needed at this time.")

        self.stdout.write("")
        self.stdout.write("=" * 80)