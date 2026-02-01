"""
Session 897: Fix pilots with NULL started_at to unblock experiment pipeline.

Root Cause: 875 pilots have started_at=NULL, making them ineligible for
evaluation by `evaluate_and_complete_pilots` task.

Fix: Backfill started_at using:
1. The linked experiment's started_at (if available)
2. The pilot's created_at timestamp (fallback)
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Fix pilots with NULL started_at to unblock experiment evaluation pipeline'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        from core.models_pilot_readiness import PilotExecution
        dry_run = options['dry_run']

        # Find pilots missing started_at
        missing_started = PilotExecution.objects.filter(
            status='running',
            started_at__isnull=True
        ).select_related('experiment')

        total = missing_started.count()
        self.stdout.write(f"\n=== Pilots Missing started_at: {total} ===")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("No pilots need fixing!"))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] Would fix the following:\n"))

        fixed = 0
        used_experiment_time = 0
        used_created_at = 0

        for pilot in missing_started:
            # Try to use experiment's started_at first
            if hasattr(pilot, 'experiment') and pilot.experiment and pilot.experiment.started_at:
                new_started = pilot.experiment.started_at
                used_experiment_time += 1
                source = "experiment.started_at"
            elif pilot.created_at:
                new_started = pilot.created_at
                used_created_at += 1
                source = "created_at"
            else:
                # Last resort - use now minus 2 hours
                new_started = timezone.now() - timedelta(hours=2)
                source = "default (now - 2h)"

            if dry_run:
                self.stdout.write(f"  {pilot.name[:50]}... -> {new_started} ({source})")
            else:
                pilot.started_at = new_started
                pilot.save(update_fields=['started_at'])
                fixed += 1

            if fixed % 100 == 0 and not dry_run:
                self.stdout.write(f"  Fixed {fixed}/{total}...")

        if dry_run:
            self.stdout.write(f"\n[DRY RUN] Would fix {total} pilots:")
            self.stdout.write(f"  - {used_experiment_time} using experiment.started_at")
            self.stdout.write(f"  - {used_created_at} using pilot.created_at")
        else:
            self.stdout.write(self.style.SUCCESS(f"\n=== Fixed {fixed} pilots ==="))
            self.stdout.write(f"  - {used_experiment_time} using experiment.started_at")
            self.stdout.write(f"  - {used_created_at} using pilot.created_at")

        # Verify the fix
        if not dry_run:
            still_missing = PilotExecution.objects.filter(
                status='running',
                started_at__isnull=True
            ).count()
            self.stdout.write(f"\n=== Remaining pilots with NULL started_at: {still_missing} ===")

            if still_missing == 0:
                self.stdout.write(self.style.SUCCESS(
                    "\nAll pilots now have started_at! "
                    "The evaluate_and_complete_pilots task should now work."
                ))
