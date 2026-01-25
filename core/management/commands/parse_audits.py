"""
Parse Audits Command - Session 819: Audit Tracking System

Imports audit markdown files from docs/audits/ into the database,
extracting structured findings that can be tracked and remediated.

Usage:
    python manage.py parse_audits
    python manage.py parse_audits --dry-run
    python manage.py parse_audits --file docs/audits/SESSION_736_COMPREHENSIVE_SYSTEM_AUDIT.md
    python manage.py parse_audits --reparse
"""

import logging
from django.core.management.base import BaseCommand

from core.services.audit_tracker import AuditTrackerService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse and import audit markdown files into the Audit Tracking System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be imported without making changes',
        )
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Import a specific audit file (path relative to project root)',
        )
        parser.add_argument(
            '--reparse',
            action='store_true',
            help='Re-parse and update existing audits (default: skip existing)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed parsing output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        single_file = options['file']
        reparse = options['reparse']
        verbose = options['verbose']

        self.stdout.write(
            self.style.NOTICE("Starting audit import...")
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN - no changes will be made")
            )

        service = AuditTrackerService()

        if single_file:
            # Import a single file
            self._import_single_file(service, single_file, dry_run, verbose)
        else:
            # Import all audits
            self._import_all_audits(service, dry_run, reparse, verbose)

    def _import_single_file(self, service, file_path, dry_run, verbose):
        """Import a single audit file."""
        self.stdout.write(f"Importing: {file_path}")

        try:
            if dry_run:
                # Parse without saving
                parsed = service.parse_audit_file(file_path)
                self._display_parsed(parsed, verbose)
                self.stdout.write(
                    self.style.WARNING("DRY RUN - would import this audit")
                )
            else:
                report = service.import_audit(file_path)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Imported: {report.title} "
                        f"({report.total_findings} findings, "
                        f"{report.p0_findings} P0, {report.p1_findings} P1)"
                    )
                )
                if verbose:
                    for finding in report.findings.all():
                        self.stdout.write(
                            f"  [{finding.priority}] {finding.title}"
                        )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File not found: {file_path}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error importing {file_path}: {e}")
            )
            logger.exception(f"Error importing audit file: {file_path}")

    def _import_all_audits(self, service, dry_run, reparse, verbose):
        """Import all audit files from docs/audits/."""
        try:
            results = service.import_all_audits(dry_run=dry_run)

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(self.style.SUCCESS("Audit Import Complete!"))
            self.stdout.write(self.style.SUCCESS("=" * 60))
            self.stdout.write(f"  Files scanned: {results.get('files_scanned', 0)}")
            self.stdout.write(f"  Reports imported: {results.get('reports_imported', 0)}")
            self.stdout.write(f"  Findings extracted: {results.get('findings_extracted', 0)}")
            self.stdout.write(f"  Skipped (existing): {results.get('skipped', 0)}")
            self.stdout.write(f"  Failed: {results.get('failed', 0)}")

            # Summary by priority
            priority_counts = results.get('priority_counts', {})
            if priority_counts:
                self.stdout.write("")
                self.stdout.write("Findings by Priority:")
                for priority, count in sorted(priority_counts.items()):
                    self.stdout.write(f"  {priority}: {count}")

            if dry_run:
                self.stdout.write("")
                self.stdout.write(
                    self.style.WARNING(
                        "This was a dry run. Run without --dry-run to apply changes."
                    )
                )

            # Show open P0 findings
            if not dry_run:
                self._show_open_p0_findings(service)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error importing audits: {e}")
            )
            logger.exception("Error in audit import")

    def _display_parsed(self, parsed, verbose):
        """Display parsed audit data."""
        self.stdout.write(f"  Title: {parsed.get('title', 'Unknown')}")
        self.stdout.write(f"  Type: {parsed.get('audit_type', 'other')}")
        self.stdout.write(f"  Session: {parsed.get('session_number', 'N/A')}")
        self.stdout.write(f"  Findings: {len(parsed.get('findings', []))}")

        if verbose:
            for finding in parsed.get('findings', []):
                self.stdout.write(
                    f"    [{finding.get('priority', 'P2')}] "
                    f"{finding.get('title', 'Untitled')}"
                )

    def _show_open_p0_findings(self, service):
        """Show summary of open P0 findings that need attention."""
        try:
            summary = service.get_finding_summary()
            p0_open = summary.get('by_priority', {}).get('P0', {}).get('open', 0)

            if p0_open > 0:
                self.stdout.write("")
                self.stdout.write(
                    self.style.WARNING(f"⚠️  {p0_open} CRITICAL (P0) findings need attention!")
                )
                self.stdout.write(
                    "Run: curl http://localhost:8000/api/audit-tracking/findings/p0/"
                )
        except Exception:
            pass  # Non-critical, don't fail the command
