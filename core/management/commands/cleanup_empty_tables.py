"""
Management command to clean up empty tables that are consuming disk space.

Session 830: Created to address pgvector 80% storage warning.

Usage:
    python manage.py cleanup_empty_tables --dry-run  # Preview what will be cleaned
    python manage.py cleanup_empty_tables            # Actually clean up
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Clean up empty tables that are consuming disk space'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually doing it',
        )
        parser.add_argument(
            '--min-size-mb',
            type=int,
            default=1,
            help='Minimum table size in MB to consider for cleanup (default: 1)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        min_size_mb = options['min_size_mb']
        min_size_bytes = min_size_mb * 1024 * 1024

        self.stdout.write(self.style.WARNING(
            f"{'[DRY RUN] ' if dry_run else ''}Scanning for empty tables with size > {min_size_mb}MB..."
        ))

        with connection.cursor() as cursor:
            # Find empty tables with significant size
            cursor.execute('''
                SELECT
                    relname as table_name,
                    pg_total_relation_size(relid) as total_bytes,
                    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
                    n_live_tup as row_count
                FROM pg_stat_user_tables
                WHERE n_live_tup = 0
                AND pg_total_relation_size(relid) > %s
                ORDER BY pg_total_relation_size(relid) DESC;
            ''', [min_size_bytes])

            empty_tables = cursor.fetchall()

            if not empty_tables:
                self.stdout.write(self.style.SUCCESS("No empty tables found needing cleanup."))
                return

            total_bytes = 0
            self.stdout.write("\nEmpty tables consuming space:")
            self.stdout.write("=" * 60)

            for table_name, size_bytes, size_pretty, row_count in empty_tables:
                total_bytes += size_bytes
                self.stdout.write(f"  {table_name:40} | {size_pretty:>10}")

            self.stdout.write("=" * 60)
            self.stdout.write(f"  {'TOTAL':40} | {self._format_bytes(total_bytes):>10}")
            self.stdout.write("")

            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f"[DRY RUN] Would reclaim {self._format_bytes(total_bytes)} by truncating {len(empty_tables)} tables."
                ))
                self.stdout.write("\nRun without --dry-run to actually clean up.")
                return

            # Actually truncate the tables
            self.stdout.write(self.style.WARNING(f"\nTruncating {len(empty_tables)} empty tables..."))

            cleaned = 0
            failed = []

            for table_name, size_bytes, size_pretty, row_count in empty_tables:
                try:
                    # Use TRUNCATE with CASCADE to handle foreign key constraints
                    cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE;')
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Truncated {table_name} ({size_pretty})"))
                    cleaned += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Failed {table_name}: {str(e)[:50]}"))
                    failed.append((table_name, str(e)))

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(f"Cleaned {cleaned}/{len(empty_tables)} tables"))

            if failed:
                self.stdout.write(self.style.WARNING(f"Failed: {len(failed)} tables"))
                for table_name, error in failed:
                    self.stdout.write(f"  - {table_name}: {error[:80]}")

            # Run VACUUM to update statistics
            self.stdout.write("\nRunning VACUUM ANALYZE to update statistics...")
            try:
                # Need to be outside transaction for VACUUM
                connection.cursor().execute("COMMIT;")
                cursor.execute("VACUUM ANALYZE;")
                self.stdout.write(self.style.SUCCESS("  ✓ VACUUM ANALYZE complete"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Note: VACUUM may need to be run separately: {e}"))

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(
                f"🎉 Reclaimed approximately {self._format_bytes(total_bytes)} of disk space!"
            ))

    def _format_bytes(self, bytes_val):
        """Format bytes as human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"
