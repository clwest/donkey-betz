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
