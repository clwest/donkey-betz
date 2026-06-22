"""Session 1196 — Plan C side-quest: manual sweep entry point.

Wraps ``core.tasks.sweep_diagnostic_initiatives`` so operators can trigger
the diagnostic-Initiative archive sweep without waiting for the 3:55 AM
Denver beat tick. Useful for backfill after PRs land mid-day, for
verifying behavior in dev/local, and for one-off cleanups.

Usage:
    python manage.py sweep_diagnostic_initiatives --dry-run
    python manage.py sweep_diagnostic_initiatives
    python manage.py sweep_diagnostic_initiatives --max-per-run 100

Beat schedule: ``sweep-diagnostic-initiatives`` in ``core/celery.py``.
Spec: docs/specs/INITIATIVES_FIRST_BACKBONE.md §3.C / §6.1.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Archive TTL-expired diagnostic Initiatives "
        "(Session 1196 Plan C side-quest sweep). Mirrors the daily beat task; "
        "use --dry-run to preview."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help="Log what would be archived without writing to the DB.",
        )
        parser.add_argument(
            '--max-per-run', type=int, default=1000,
            help="Safety cap on rows touched per invocation (default 1000; "
                 "set 0 to disable).",
        )

    def handle(self, *args, **opts):
        from core.tasks import sweep_diagnostic_initiatives

        result = sweep_diagnostic_initiatives(
            dry_run=opts['dry_run'],
            max_per_run=opts['max_per_run'],
        )
        verb = "Would archive" if opts['dry_run'] else "Archived"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} {result['archived']} of {result['candidates']} candidates "
            f"(max_per_run={result['max_per_run']}, "
            f"capped={result['capped']}, sample={result['sample_ids']})"
        ))
