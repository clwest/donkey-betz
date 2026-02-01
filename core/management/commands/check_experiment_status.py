"""
Session 896: Quick status check for experiments and pilots.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Check experiment and pilot status distribution'

    def handle(self, *args, **options):
        from core.models_pilot_readiness import Experiment, PilotExecution

        self.stdout.write("\n=== Experiment Status ===")
        exp_status = dict(Experiment.objects.values_list('status').annotate(c=Count('id')))
        for status, count in sorted(exp_status.items(), key=lambda x: -x[1]):
            self.stdout.write(f"  {status}: {count}")
        self.stdout.write(f"  TOTAL: {sum(exp_status.values())}")

        self.stdout.write("\n=== Pilot Status ===")
        pilot_status = dict(PilotExecution.objects.values_list('status').annotate(c=Count('id')))
        for status, count in sorted(pilot_status.items(), key=lambda x: -x[1]):
            self.stdout.write(f"  {status}: {count}")
        self.stdout.write(f"  TOTAL: {sum(pilot_status.values())}")

        # Orphan experiments
        orphan_exp = Experiment.objects.filter(pilot__isnull=True).count()
        self.stdout.write(f"\n=== Orphan Experiments (no pilot): {orphan_exp} ===")

        # Running experiments age
        now = timezone.now()
        old_running = Experiment.objects.filter(
            status='running',
            started_at__lt=now - timedelta(hours=24)
        )
        self.stdout.write(f"\n=== Running experiments > 24h old: {old_running.count()} ===")

        if old_running.exists():
            oldest = old_running.order_by('started_at').first()
            age_hours = (now - oldest.started_at).total_seconds() / 3600
            self.stdout.write(f"  Oldest: {age_hours:.1f} hours ({oldest.name[:50]}...)")

        # Running pilots age
        old_pilots = PilotExecution.objects.filter(
            status='running',
            started_at__lt=now - timedelta(hours=24)
        )
        self.stdout.write(f"\n=== Running pilots > 24h old: {old_pilots.count()} ===")

        if old_pilots.exists():
            oldest_pilot = old_pilots.order_by('started_at').first()
            pilot_age = (now - oldest_pilot.started_at).total_seconds() / 3600
            self.stdout.write(f"  Oldest: {pilot_age:.1f} hours ({oldest_pilot.name[:50]}...)")

        # Session 897: Additional diagnostics for stuck pipeline
        self.stdout.write("\n=== Pilot Pipeline Blockers ===")

        # 1. Pilots with NULL started_at (can't be evaluated)
        null_started = PilotExecution.objects.filter(
            status='running',
            started_at__isnull=True
        ).count()
        self.stdout.write(f"  Pilots with NULL started_at: {null_started}")

        # 2. Running pilots by outcome (must be 'pending' to be eligible)
        pilot_outcomes = dict(
            PilotExecution.objects.filter(status='running')
            .values_list('outcome')
            .annotate(c=Count('id'))
        )
        self.stdout.write(f"  Running pilots by outcome:")
        for outcome, count in sorted(pilot_outcomes.items(), key=lambda x: -x[1]):
            self.stdout.write(f"    {outcome or 'NULL'}: {count}")

        # 3. Running pilots eligible for evaluation (running, >1h old, pending)
        eligible = PilotExecution.objects.filter(
            status='running',
            started_at__lte=now - timedelta(hours=1),
            outcome='pending'
        ).count()
        self.stdout.write(f"  Eligible for evaluation (>1h, pending): {eligible}")

        # 4. Running experiments without linked pilots
        exp_without_pilot = Experiment.objects.filter(
            status='running'
        ).exclude(
            pilot__isnull=False
        ).count()
        self.stdout.write(f"  Running experiments without pilot link: {exp_without_pilot}")

        # 5. Show a few stuck experiments for investigation
        self.stdout.write("\n=== Sample Stuck Experiments (5 oldest) ===")
        stuck = Experiment.objects.filter(
            status='running',
            started_at__lt=now - timedelta(hours=24)
        ).order_by('started_at')[:5]
        for exp in stuck:
            age = (now - exp.started_at).total_seconds() / 3600
            has_pilot = hasattr(exp, 'pilot') and exp.pilot is not None
            self.stdout.write(
                f"  [{age:.0f}h] {exp.name[:40]}... | "
                f"Pilot: {'Yes' if has_pilot else 'No'}"
            )
