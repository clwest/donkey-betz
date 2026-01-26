"""
Management command to clean up bloated AgentSolution records.

Session 830: Created to address pgvector 80% storage warning.

The AgentSolution table grew to 35GB because code_snippet was storing
full JSON dumps of spider data. The spider_data_id is already in metrics,
so we can safely truncate code_snippet fields to reclaim space.

Usage:
    python manage.py cleanup_agent_solutions --dry-run  # Preview
    python manage.py cleanup_agent_solutions            # Actually clean
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Clean up bloated AgentSolution code_snippet fields to reclaim disk space'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without actually doing it',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to update per batch (default: 1000)',
        )
        parser.add_argument(
            '--min-snippet-size',
            type=int,
            default=500,
            help='Only clean code_snippets larger than this many characters (default: 500)',
        )
        parser.add_argument(
            '--older-than-days',
            type=int,
            default=0,
            help='Only clean records older than N days (default: 0 = all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = options['batch_size']
        min_size = options['min_snippet_size']
        older_than_days = options['older_than_days']

        self.stdout.write(self.style.WARNING(
            f"{'[DRY RUN] ' if dry_run else ''}Analyzing AgentSolution table..."
        ))

        with connection.cursor() as cursor:
            # Check current table size and stats
            cursor.execute('''
                SELECT
                    COUNT(*) as total_rows,
                    pg_size_pretty(pg_total_relation_size('core_agentsolution')) as total_size,
                    COUNT(*) FILTER (WHERE LENGTH(code_snippet) > %s) as bloated_rows,
                    SUM(LENGTH(code_snippet)) FILTER (WHERE LENGTH(code_snippet) > %s) as bloated_bytes
                FROM core_agentsolution;
            ''', [min_size, min_size])

            row = cursor.fetchone()
            total_rows, total_size, bloated_rows, bloated_bytes = row

            bloated_bytes = bloated_bytes or 0
            bloated_rows = bloated_rows or 0

            self.stdout.write(f"\nCurrent state:")
            self.stdout.write(f"  Total rows: {total_rows:,}")
            self.stdout.write(f"  Table size: {total_size}")
            self.stdout.write(f"  Rows with code_snippet > {min_size} chars: {bloated_rows:,}")
            self.stdout.write(f"  Estimated bloat: {self._format_bytes(bloated_bytes)}")

            if bloated_rows == 0:
                self.stdout.write(self.style.SUCCESS("\nNo bloated records found."))
                return

            # Build date filter if specified
            date_filter = ""
            date_params = [min_size]
            if older_than_days > 0:
                cutoff = timezone.now() - timedelta(days=older_than_days)
                date_filter = " AND created_at < %s"
                date_params.append(cutoff)
                self.stdout.write(f"  Only cleaning records older than {older_than_days} days")

            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f"\n[DRY RUN] Would truncate code_snippet in ~{bloated_rows:,} records"
                ))
                self.stdout.write(f"[DRY RUN] Estimated space savings: {self._format_bytes(bloated_bytes)}")
                self.stdout.write("\nRun without --dry-run to actually clean up.")
                return

            # Perform the cleanup in batches
            self.stdout.write(self.style.WARNING(
                f"\nTruncating code_snippet fields (batch size: {batch_size})..."
            ))

            total_updated = 0
            batch_num = 0

            while True:
                batch_num += 1
                # Use a subquery to limit updates per batch
                cursor.execute(f'''
                    UPDATE core_agentsolution
                    SET code_snippet = SUBSTRING(code_snippet, 1, 200) || '... [truncated - see spider_data_id in metrics]'
                    WHERE id IN (
                        SELECT id FROM core_agentsolution
                        WHERE LENGTH(code_snippet) > %s {date_filter}
                        LIMIT %s
                    );
                ''', date_params + [batch_size])

                updated = cursor.rowcount
                total_updated += updated

                if updated > 0:
                    self.stdout.write(f"  Batch {batch_num}: Updated {updated} records (total: {total_updated:,})")

                if updated < batch_size:
                    break

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(f"Cleaned {total_updated:,} records"))

            # Run VACUUM to reclaim space
            self.stdout.write("\nRunning VACUUM FULL on core_agentsolution to reclaim space...")
            self.stdout.write("(This may take a while for large tables)")

            try:
                # VACUUM FULL requires autocommit
                cursor.execute("COMMIT;")
                old_isolation = connection.connection.isolation_level
                connection.connection.set_isolation_level(0)
                cursor.execute("VACUUM FULL core_agentsolution;")
                connection.connection.set_isolation_level(old_isolation)
                self.stdout.write(self.style.SUCCESS("  VACUUM FULL complete"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f"  Note: VACUUM FULL may need to be run separately: {e}"
                ))
                self.stdout.write("  Run: VACUUM FULL core_agentsolution;")

            # Check new size
            cursor.execute('''
                SELECT pg_size_pretty(pg_total_relation_size('core_agentsolution')) as new_size;
            ''')
            new_size = cursor.fetchone()[0]

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(f"Table size: {total_size} -> {new_size}"))

    def _format_bytes(self, bytes_val):
        """Format bytes as human readable string."""
        if bytes_val is None:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"
