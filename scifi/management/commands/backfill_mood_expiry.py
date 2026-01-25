# scifi/management/commands/backfill_mood_expiry.py
"""
Management command to backfill AgentMood.mood_expires_at for rows where it's NULL.

Usage:
    python manage.py backfill_mood_expiry

The command processes rows in batches, uses transactions, and performs bulk_update
to avoid N+1 updates. It uses settings.SCIFI_MOOD_TTL_DAYS (default 30).
"""

from datetime import timedelta
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from scifi.models import AgentMood

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfill AgentMood.mood_expires_at for rows where it's NULL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of rows to process per database transaction/batch.",
        )

    def handle(self, *args, **options):
        batch_size = options.get("batch_size") or 1000
        try:
            ttl_days = int(getattr(settings, "SCIFI_MOOD_TTL_DAYS", 30))
        except Exception as exc:
            raise CommandError(f"Invalid SCIFI_MOOD_TTL_DAYS: {exc}")

        delta = timedelta(days=ttl_days)

        qs = AgentMood.objects.filter(mood_expires_at__isnull=True).order_by("pk")
        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No AgentMood rows require backfill."))
            return

        self.stdout.write(
            f"Starting backfill for {total} AgentMood rows (TTL={ttl_days} days) "
            f"in batches of {batch_size}..."
        )

        updated_total = 0

        try:
            # Process in batches using slicing to avoid loading entire table.
            start = 0
            while start < total:
                end = start + batch_size
                batch_qs = list(qs[start:end])  # evaluate slice
                if not batch_qs:
                    break

                for inst in batch_qs:
                    base_time = inst.created_at or timezone.now()
                    inst.mood_expires_at = base_time + delta

                # Use transaction per batch to keep operations atomic.
                try:
                    with transaction.atomic():
                        AgentMood.objects.bulk_update(batch_qs, ["mood_expires_at"])
                except Exception:
                    # Log and reraise to surface error to caller/process.
                    logger.exception("Failed to update batch starting at %d", start)
                    raise

                updated_total += len(batch_qs)
                self.stdout.write(f"Backfilled batch {start}-{end - 1}: {len(batch_qs)} rows")
                start = end

        except Exception as exc:
            # Provide meaningful CLI output and a non-zero exit via CommandError.
            logger.exception("Error occurred during backfill: %s", exc)
            raise CommandError(f"Backfill failed: {exc}")

        self.stdout.write(self.style.SUCCESS(f"Backfill complete. Updated {updated_total} rows."))