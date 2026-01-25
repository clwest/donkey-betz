"""
Backfill Deliverables Command - Session 819: Deliverables Marketplace

Converts existing WorkspaceOperations into Deliverable objects.
This allows the new Deliverables Marketplace to display historical
agent outputs.

Usage:
    python manage.py backfill_deliverables
    python manage.py backfill_deliverables --dry-run
    python manage.py backfill_deliverables --limit 100
    python manage.py backfill_deliverables --agent ContentWriterAgent
"""

import logging
from django.core.management.base import BaseCommand
from django.db.models import Q

from core.models_skin_layer import WorkspaceOperation
from core.models_deliverables import Deliverable
from core.services.deliverable_envelope import DeliverableEnvelopeService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill Deliverable objects from existing WorkspaceOperations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be created without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of operations to process',
        )
        parser.add_argument(
            '--agent',
            type=str,
            default=None,
            help='Only process operations from a specific agent',
        )
        parser.add_argument(
            '--since-days',
            type=int,
            default=30,
            help='Only process operations from the last N days (default: 30)',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            default=True,
            help='Skip operations that already have deliverables (default: True)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        agent_filter = options['agent']
        since_days = options['since_days']
        skip_existing = options['skip_existing']

        self.stdout.write(
            self.style.NOTICE(f"Starting deliverables backfill...")
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN - no changes will be made")
            )

        # Build queryset
        queryset = WorkspaceOperation.objects.filter(
            success=True  # Only successful operations
        )

        # Filter by agent
        if agent_filter:
            queryset = queryset.filter(agent_name=agent_filter)
            self.stdout.write(f"Filtering by agent: {agent_filter}")

        # Filter by date
        if since_days:
            from django.utils import timezone
            from datetime import timedelta
            cutoff = timezone.now() - timedelta(days=since_days)
            queryset = queryset.filter(created_at__gte=cutoff)
            self.stdout.write(f"Filtering operations since {cutoff.date()}")

        # Skip operations that already have deliverables
        if skip_existing:
            existing_op_ids = Deliverable.objects.exclude(
                source_operation__isnull=True
            ).values_list('source_operation_id', flat=True)
            queryset = queryset.exclude(id__in=existing_op_ids)

        # Apply limit
        if limit:
            queryset = queryset[:limit]
            self.stdout.write(f"Limiting to {limit} operations")

        # Count operations
        total = queryset.count()
        self.stdout.write(f"Found {total} operations to process")

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("No operations to process.")
            )
            return

        # Initialize service
        service = DeliverableEnvelopeService()

        # Process operations
        created = 0
        skipped = 0
        failed = 0

        for i, operation in enumerate(queryset.iterator(), 1):
            try:
                # Check if deliverable already exists
                if Deliverable.objects.filter(source_operation=operation).exists():
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        f"[DRY RUN] Would create deliverable from: "
                        f"{operation.agent_name} - {operation.file_path or operation.command[:50]}"
                    )
                    created += 1
                    continue

                # Create deliverable
                deliverable = service.wrap_from_operation(
                    operation=operation,
                    user=operation.user
                )

                if deliverable:
                    created += 1
                    self.stdout.write(
                        f"[{i}/{total}] Created: {deliverable.title[:60]}"
                    )
                else:
                    skipped += 1

                # Progress update
                if i % 50 == 0:
                    self.stdout.write(
                        f"Progress: {i}/{total} processed, "
                        f"{created} created, {skipped} skipped, {failed} failed"
                    )

            except Exception as e:
                failed += 1
                logger.error(
                    f"Failed to create deliverable from operation {operation.id}: {e}"
                )
                self.stdout.write(
                    self.style.ERROR(f"Failed: {operation.id} - {str(e)[:100]}")
                )

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Backfill Complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"  Total processed: {total}")
        self.stdout.write(f"  Created: {created}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Failed: {failed}")

        if dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("This was a dry run. Run without --dry-run to apply changes.")
            )
