"""
Session 1191: Backfill last_activity_at on Initiative rows that were
born NULL.

Pairs with the populate_initiatives_api fix (which now calls
`update_activity(reason='auto_populate_create')` at creation time) and
the `initiative_activity_tick` beat task (which keeps activity fresh
post-creation). This one-shot covers the historical rows created
before either of those landed.

Strategy: where `last_activity_at IS NULL`, set it to `created_at`.
That preserves the "this row hasn't seen real signal yet" semantics
(activity_tick will move it up the next time a linked deliverable or
action item updates) without lying about recent activity.

Idempotent. Safe to re-run.
"""
from django.core.management.base import BaseCommand
from django.db.models import F


class Command(BaseCommand):
    help = 'Backfill Initiative.last_activity_at = created_at for rows where last_activity_at IS NULL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show how many rows would change without writing',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative

        dry_run = options['dry_run']

        null_qs = Initiative.objects.filter(last_activity_at__isnull=True)
        total = null_qs.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS(
                'No Initiative rows with NULL last_activity_at. Nothing to do.'
            ))
            return

        self.stdout.write(
            f"Found {total} Initiative rows with last_activity_at IS NULL"
        )

        if dry_run:
            sample = list(null_qs.values('id', 'name', 'created_at')[:5])
            self.stdout.write('[DRY] Sample of rows that would be backfilled:')
            for row in sample:
                self.stdout.write(
                    f"  id={row['id']} created_at={row['created_at']} "
                    f"name={row['name'][:60]!r}"
                )
            self.stdout.write(self.style.WARNING(
                f"[DRY] Would set last_activity_at = created_at on {total} rows"
            ))
            return

        updated = null_qs.update(last_activity_at=F('created_at'))
        self.stdout.write(self.style.SUCCESS(
            f"Backfilled last_activity_at = created_at on {updated} Initiative rows"
        ))
