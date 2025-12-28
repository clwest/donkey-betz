"""
Management command for manual model retraining - Session 24
"""

from django.core.management.base import BaseCommand
from ml.training.model_retrainer import ModelRetrainer
from ml.models import MLModelVersion


class Command(BaseCommand):
    help = 'Manually retrain ML models using evaluated predictions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sport',
            type=str,
            choices=['nfl', 'nba', 'mlb', 'nhl'],
            help='Retrain specific sport model'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Retrain all sport models'
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Check retraining status for all sports'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force retraining even if criteria not met'
        )
        parser.add_argument(
            '--versions',
            action='store_true',
            help='Show version history for all sports'
        )

    def handle(self, *args, **options):
        retrainer = ModelRetrainer()

        # Show version history
        if options['versions']:
            self.show_versions()
            return

        # Check status
        if options['status']:
            self.check_status(retrainer)
            return

        # Retrain all sports
        if options['all']:
            self.retrain_all(retrainer, options['force'])
            return

        # Retrain specific sport
        if options['sport']:
            self.retrain_sport(retrainer, options['sport'], options['force'])
            return

        # No arguments - show help
        self.stdout.write(self.style.WARNING(
            "Please specify --sport, --all, --status, or --versions"
        ))
        self.stdout.write("\nExamples:")
        self.stdout.write("  python manage.py retrain_models --sport nfl")
        self.stdout.write("  python manage.py retrain_models --all")
        self.stdout.write("  python manage.py retrain_models --status")
        self.stdout.write("  python manage.py retrain_models --versions")
        self.stdout.write("  python manage.py retrain_models --sport nfl --force")

    def check_status(self, retrainer):
        """Check retraining status for all sports"""
        self.stdout.write(self.style.SUCCESS("\n=== Retraining Status ===\n"))

        sports = ['nfl', 'nba', 'mlb', 'nhl']

        for sport in sports:
            should_retrain, reason = retrainer.should_retrain(sport)

            if should_retrain:
                self.stdout.write(
                    self.style.WARNING(f"✓ {sport.upper()}: {reason}")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {sport.upper()}: {reason}")
                )

    def show_versions(self):
        """Show version history for all sports"""
        self.stdout.write(self.style.SUCCESS("\n=== Model Version History ===\n"))

        sports = ['nfl', 'nba', 'mlb', 'nhl']

        for sport in sports:
            self.stdout.write(self.style.HTTP_INFO(f"\n{sport.upper()}:"))

            versions = MLModelVersion.get_version_history(sport)

            if not versions.exists():
                self.stdout.write("  No versions found")
                continue

            for version in versions:
                active_str = " [ACTIVE]" if version.is_active else ""
                improvement = version.improvement_over_previous

                improvement_str = ""
                if improvement is not None:
                    if improvement > 0:
                        improvement_str = f" (+{improvement:.1f}%)"
                    else:
                        improvement_str = f" ({improvement:.1f}%)"

                self.stdout.write(
                    f"  v{version.version}: {version.accuracy_percentage} accuracy"
                    f"{improvement_str} - {version.training_samples} samples"
                    f"{active_str}"
                )

                if version.days_active is not None:
                    self.stdout.write(f"    Active for {version.days_active} days")

    def retrain_sport(self, retrainer, sport_type, force):
        """Retrain a specific sport model"""
        self.stdout.write(
            self.style.HTTP_INFO(f"\n=== Retraining {sport_type.upper()} Model ===\n")
        )

        # Check if needed (unless forced)
        if not force:
            should_retrain, reason = retrainer.should_retrain(sport_type)
            self.stdout.write(f"Status: {reason}")

            if not should_retrain:
                self.stdout.write(self.style.WARNING(
                    "\nRetraining not needed. Use --force to retrain anyway."
                ))
                return

        # Perform retraining
        self.stdout.write("\nStarting retraining...")

        result = retrainer.retrain_model(sport_type, force=force)

        # Display results
        self.stdout.write("\n" + "="*60)

        if result['success']:
            self.stdout.write(self.style.SUCCESS(
                f"\n✓ {sport_type.upper()} Model v{result['version']} trained successfully!"
            ))

            # Show metrics
            metrics = result['metrics']
            self.stdout.write(f"\nMetrics:")
            self.stdout.write(f"  Accuracy: {metrics['accuracy']:.1%}")
            self.stdout.write(f"  Precision: {metrics.get('precision', 0):.1%}")
            self.stdout.write(f"  Recall: {metrics.get('recall', 0):.1%}")
            self.stdout.write(f"  Calibration: {metrics['calibration_score']:.3f}")
            self.stdout.write(f"  Test Samples: {metrics.get('test_samples', 0)}")

            # Deployment status
            if result['deployed']:
                self.stdout.write(self.style.SUCCESS(
                    f"\n✓ Model deployed: {result['message']}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"\n⚠ Model not deployed: {result['message']}"
                ))

        else:
            self.stdout.write(self.style.ERROR(
                f"\n✗ Retraining failed: {result['message']}"
            ))

    def retrain_all(self, retrainer, force):
        """Retrain all sport models"""
        self.stdout.write(self.style.HTTP_INFO(
            "\n=== Retraining All Sport Models ===\n"
        ))

        sports = ['nfl', 'nba', 'mlb', 'nhl']
        results = {}

        for sport in sports:
            self.stdout.write(f"\n{sport.upper()}:")
            self.stdout.write("-" * 40)

            result = retrainer.retrain_model(sport, force=force)
            results[sport] = result

            if result['success']:
                if result['deployed']:
                    self.stdout.write(self.style.SUCCESS(
                        f"✓ v{result['version']} deployed - {result['metrics']['accuracy']:.1%} accuracy"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"⚠ v{result['version']} trained but not deployed"
                    ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"✗ Failed: {result['message']}"
                ))

        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.HTTP_INFO("\nSummary:"))

        successful = sum(1 for r in results.values() if r['success'])
        deployed = sum(1 for r in results.values() if r.get('deployed', False))

        self.stdout.write(f"  Total Sports: {len(sports)}")
        self.stdout.write(f"  Successful: {successful}")
        self.stdout.write(f"  Deployed: {deployed}")

        if successful == len(sports):
            self.stdout.write(self.style.SUCCESS(
                "\n✓ All models retrained successfully!"
            ))
        elif successful > 0:
            self.stdout.write(self.style.WARNING(
                f"\n⚠ {successful}/{len(sports)} models retrained"
            ))
        else:
            self.stdout.write(self.style.ERROR(
                "\n✗ No models successfully retrained"
            ))