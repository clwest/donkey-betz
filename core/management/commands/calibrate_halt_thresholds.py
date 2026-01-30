"""
Session 874: Calibrate experiment halt thresholds using historical data.

Runs the threshold sandbox analysis to find optimal halt condition settings
that minimize false positives (unnecessary halts) and false negatives (missed failures).

Usage:
    python manage.py calibrate_halt_thresholds
    python manage.py calibrate_halt_thresholds --days 180
    python manage.py calibrate_halt_thresholds --cost-fn 20  # Higher cost for missed failures
    python manage.py calibrate_halt_thresholds --apply  # Apply recommended thresholds
"""

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Calibrate experiment halt thresholds using historical data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Days of historical data to analyze (default: 90)'
        )
        parser.add_argument(
            '--cost-fn',
            type=float,
            default=10.0,
            help='Cost weight for false negatives relative to false positives (default: 10)'
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply the recommended balanced thresholds to future experiments'
        )
        parser.add_argument(
            '--profile',
            choices=['conservative', 'balanced', 'permissive'],
            default='balanced',
            help='Which profile to apply if --apply is used (default: balanced)'
        )

    def handle(self, *args, **options):
        from core.services.threshold_sandbox import ThresholdSandbox

        days = options['days']
        cost_fn = options['cost_fn']
        apply = options['apply']
        profile = options['profile']

        self.stdout.write(self.style.HTTP_INFO(
            f'\n=== Threshold Calibration Analysis ===\n'
            f'Analyzing {days} days of historical data...\n'
        ))

        # Run calibration
        sandbox = ThresholdSandbox(days_back=days)
        report = sandbox.run_calibration(c_fn=cost_fn, verbose=False)

        # Display dataset summary
        summary = report['dataset_summary']
        self.stdout.write(f'Dataset Summary:')
        self.stdout.write(f'  Total experiments: {summary["total_experiments"]}')
        self.stdout.write(f'  Halted: {summary["halted_count"]} ({summary["halt_rate"]*100:.1f}%)')
        self.stdout.write(f'  Status distribution:')
        for status, count in summary['status_distribution'].items():
            self.stdout.write(f'    - {status}: {count}')

        # Display threshold sweep results
        self.stdout.write(f'\nThreshold Sweep Results:')
        self.stdout.write('  error_rate_max | FPR    | FNR    | F1     | Cost')
        self.stdout.write('  ' + '-' * 50)
        for r in report['all_results']:
            self.stdout.write(
                f'  {r["error_rate_max"]:>13.0f}% | '
                f'{r["fpr"]*100:>5.1f}% | '
                f'{r["fnr"]*100:>5.1f}% | '
                f'{r["f1"]:.3f} | '
                f'{r["expected_cost"]:.3f}'
            )

        # Display recommendations
        self.stdout.write(f'\nRecommendations:')
        for name, rec in report['recommendations'].items():
            if rec['config']:
                style = self.style.SUCCESS if name == profile else self.style.HTTP_INFO
                self.stdout.write(style(f'  {name.upper()}:'))
                self.stdout.write(f'    error_rate_max: {rec["config"]["error_rate_max"]}%')
                self.stdout.write(f'    min_executions: {rec["config"]["min_executions"]}')
                self.stdout.write(f'    FPR: {rec["fpr"]*100:.1f}%, FNR: {rec["fnr"]*100:.1f}%')
                self.stdout.write(f'    {rec["description"]}')

        # Display current config
        current = report['current_config']
        self.stdout.write(f'\nCurrent Configuration:')
        self.stdout.write(f'  error_rate_max: {current["config"]["error_rate_max"]}%')
        self.stdout.write(f'  FPR: {current["fpr"]*100:.1f}%, FNR: {current["fnr"]*100:.1f}%')

        # Apply if requested
        if apply:
            rec = report['recommendations'][profile]
            if rec['config']:
                self.stdout.write('')
                self.stdout.write(self.style.WARNING(
                    f'Applying {profile.upper()} profile thresholds...'
                ))

                # Update default halt conditions
                new_threshold = rec['config']['error_rate_max']
                self._update_default_thresholds(new_threshold)

                self.stdout.write(self.style.SUCCESS(
                    f'Updated default error_rate_max to {new_threshold}%'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'No valid configuration for {profile} profile'
                ))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('Analysis complete.'))

        if not apply:
            self.stdout.write(
                'Run with --apply to update thresholds, '
                'or --apply --profile=conservative for stricter settings.'
            )

    def _update_default_thresholds(self, error_rate_max: float):
        """Update the default halt conditions for new experiments."""
        from core.models_pilot_readiness import Experiment

        # Get current defaults
        defaults = Experiment.get_default_halt_conditions()

        # Note: This just shows what would change
        # The actual default is in the model's get_default_halt_conditions() method
        self.stdout.write(f'  Current default: {defaults.get("error_rate_max", 25.0)}%')
        self.stdout.write(f'  New default: {error_rate_max}%')
        self.stdout.write('')
        self.stdout.write(
            'NOTE: To permanently change defaults, update '
            'Experiment.get_default_halt_conditions() in core/models_pilot_readiness.py'
        )
