"""
Session 855: Update experiment halt condition thresholds.

Updates existing experiments to use the new, more lenient thresholds that prevent
premature auto-halts due to small sample sizes.

Changes:
- error_rate_max: 25% -> 35% (more tolerant of early failures)
- MIN_EXECUTIONS_FOR_ERROR_RATE: 10 -> 20 (in experiment_metrics.py)
- MIN_AGE_MINUTES: 10 -> 30 (in experiment_metrics.py)

Usage:
    python manage.py update_experiment_thresholds
    python manage.py update_experiment_thresholds --dry-run
    python manage.py update_experiment_thresholds --running-only
"""

from django.core.management.base import BaseCommand
from core.models_pilot_readiness import Experiment


class Command(BaseCommand):
    help = 'Update experiment halt condition thresholds to prevent premature auto-halts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--running-only',
            action='store_true',
            help='Only update running experiments',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        running_only = options['running_only']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made'))

        # Get experiments to update
        queryset = Experiment.objects.all()
        if running_only:
            queryset = queryset.filter(status='running', is_halted=False)
            self.stdout.write(f'Filtering to running experiments only')

        # New default thresholds
        new_defaults = Experiment.get_default_halt_conditions()

        self.stdout.write(f'\n=== New Default Thresholds ===')
        for key, value in new_defaults.items():
            self.stdout.write(f'  {key}: {value}')

        # Count experiments that need updates
        needs_update = []
        for exp in queryset:
            conditions = exp.halt_conditions or {}
            old_error_max = conditions.get('error_rate_max', 25.0)

            # Check if using old threshold
            if old_error_max <= 25.0:
                needs_update.append({
                    'id': str(exp.id)[:8],
                    'name': exp.name[:50],
                    'status': exp.status,
                    'old_threshold': old_error_max,
                })

        self.stdout.write(f'\n=== Experiments Needing Update ===')
        self.stdout.write(f'Found {len(needs_update)} experiments with old thresholds')

        if not needs_update:
            self.stdout.write(self.style.SUCCESS('All experiments already have updated thresholds'))
            return

        # Show what will be updated
        for exp_info in needs_update[:10]:  # Show first 10
            self.stdout.write(
                f"  - {exp_info['id']} [{exp_info['status']}] {exp_info['name']} "
                f"(error_rate_max: {exp_info['old_threshold']}% -> 35%)"
            )
        if len(needs_update) > 10:
            self.stdout.write(f"  ... and {len(needs_update) - 10} more")

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run complete - no changes made'))
            return

        # Perform updates
        updated_count = 0
        for exp in queryset:
            conditions = exp.halt_conditions or {}
            old_error_max = conditions.get('error_rate_max', 25.0)

            if old_error_max <= 25.0:
                # Update to new thresholds
                conditions['error_rate_max'] = 35.0
                exp.halt_conditions = conditions
                exp.save(update_fields=['halt_conditions'])
                updated_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} experiments'))

        # Resume any halted experiments that were halted due to old threshold
        if not running_only:
            halted_for_error = Experiment.objects.filter(
                is_halted=True,
                halt_reason__icontains='error rate'
            )
            halted_count = halted_for_error.count()

            if halted_count > 0:
                self.stdout.write(f'\n=== Halted Experiments (Error Rate) ===')
                self.stdout.write(f'Found {halted_count} experiments halted for error rate')
                self.stdout.write(
                    'Consider reviewing these and manually resuming if appropriate:'
                )
                for exp in halted_for_error[:5]:
                    self.stdout.write(f"  - {exp.name}: {exp.halt_reason}")
