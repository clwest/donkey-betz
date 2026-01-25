"""
Auto Remediate Command - Session 820/821: Self-Healing Orchestration System

Runs the autonomous remediation cycle to discover audits, validate findings,
assign to agents, execute fixes, and verify results. The system can heal itself
without human intervention.

Session 821: Added staleness validation phase to check if findings from old
sessions are still relevant before assigning them to agents.

Usage:
    python manage.py auto_remediate                    # Run full cycle
    python manage.py auto_remediate --discover        # Phase 1: Discover/import audits
    python manage.py auto_remediate --validate        # Phase 1.5: Validate stale findings
    python manage.py auto_remediate --assign          # Phase 2: Assign findings to agents
    python manage.py auto_remediate --execute         # Phase 3: Execute remediation tasks
    python manage.py auto_remediate --verify          # Phase 4: Verify completed fixes
    python manage.py auto_remediate --status          # Show remediation status
    python manage.py auto_remediate --dry-run         # Preview without making changes
"""

import logging
from django.core.management.base import BaseCommand

from core.services.autonomous_remediation_orchestrator import AutonomousRemediationOrchestrator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run autonomous remediation cycle - self-healing for audit findings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be done without making changes',
        )
        parser.add_argument(
            '--discover',
            action='store_true',
            help='Phase 1 only: Discover and import new audit files',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Phase 1.5 only: Validate stale findings from old sessions',
        )
        parser.add_argument(
            '--assign',
            action='store_true',
            help='Phase 2 only: Assign open findings to appropriate agents',
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Phase 3 only: Execute assigned remediation tasks via agents',
        )
        parser.add_argument(
            '--verify',
            action='store_true',
            help='Phase 4 only: Verify that completed fixes actually worked',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current remediation status without running any phase',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Maximum number of items to process per phase (default: 10)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each operation',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        verbose = options['verbose']

        # Determine which phases to run
        phases = {
            'discover': options['discover'],
            'validate': options['validate'],
            'assign': options['assign'],
            'execute': options['execute'],
            'verify': options['verify'],
            'status': options['status'],
        }

        # If no specific phase selected, run full cycle (unless --status)
        run_full_cycle = not any(phases.values())

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN - no changes will be made")
            )

        orchestrator = AutonomousRemediationOrchestrator()

        if phases['status'] or run_full_cycle:
            self._show_status(orchestrator)
            if phases['status']:
                return

        if run_full_cycle:
            self._run_full_cycle(orchestrator, dry_run, limit, verbose)
        else:
            if phases['discover']:
                self._run_discover(orchestrator, dry_run, verbose)
            if phases['validate']:
                self._run_validate(orchestrator, dry_run, verbose)
            if phases['assign']:
                self._run_assign(orchestrator, dry_run, limit, verbose)
            if phases['execute']:
                self._run_execute(orchestrator, dry_run, limit, verbose)
            if phases['verify']:
                self._run_verify(orchestrator, dry_run, limit, verbose)

    def _show_status(self, orchestrator):
        """Display current remediation status."""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("  AUTONOMOUS REMEDIATION STATUS"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        try:
            status = orchestrator.get_status()

            # Overview
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Overview:"))
            self.stdout.write(f"  Audit Reports: {status.get('audit_reports', 0)}")
            self.stdout.write(f"  Total Findings: {status.get('total_findings', 0)}")
            self.stdout.write(f"  Remediation Tasks: {status.get('remediation_tasks', 0)}")
            self.stdout.write(f"  Verification Runs: {status.get('verification_runs', 0)}")

            # Findings by status
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Findings by Status:"))
            by_status = status.get('findings_by_status', {})
            for stat, count in sorted(by_status.items()):
                emoji = self._status_emoji(stat)
                self.stdout.write(f"  {emoji} {stat}: {count}")

            # Findings by priority
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Findings by Priority:"))
            by_priority = status.get('findings_by_priority', {})
            for priority in ['P0', 'P1', 'P2', 'P3']:
                count = by_priority.get(priority, 0)
                if count > 0:
                    color = self.style.ERROR if priority == 'P0' else self.style.WARNING if priority == 'P1' else self.stdout.write
                    self.stdout.write(f"  {priority}: {count}")

            # Remediation progress
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Remediation Tasks:"))
            task_status = status.get('tasks_by_status', {})
            for stat, count in sorted(task_status.items()):
                self.stdout.write(f"  {stat}: {count}")

            # Actionable items
            self.stdout.write("")
            pending_assign = by_status.get('open', 0)
            pending_execute = task_status.get('assigned', 0)
            pending_verify = task_status.get('completed', 0)

            if pending_assign > 0 or pending_execute > 0 or pending_verify > 0:
                self.stdout.write(self.style.WARNING("Pending Actions:"))
                if pending_assign > 0:
                    self.stdout.write(f"  {pending_assign} findings ready to assign")
                if pending_execute > 0:
                    self.stdout.write(f"  {pending_execute} tasks ready to execute")
                if pending_verify > 0:
                    self.stdout.write(f"  {pending_verify} fixes ready to verify")
            else:
                self.stdout.write(self.style.SUCCESS("No pending actions - system is clean!"))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error getting status: {e}")
            )
            logger.exception("Error in auto_remediate status")

    def _status_emoji(self, status):
        """Return emoji for finding status."""
        return {
            'open': '📋',
            'in_progress': '🔄',
            'fixed': '✅',
            'verified': '🏆',
            'wontfix': '⏭️',
            'deferred': '📅',
        }.get(status, '❓')

    def _run_full_cycle(self, orchestrator, dry_run, limit, verbose):
        """Run all 4 phases of the remediation cycle."""
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Running Full Remediation Cycle..."))
        self.stdout.write("")

        try:
            if dry_run:
                self.stdout.write("Phase 1: Would discover and import audits")
                self.stdout.write("Phase 2: Would assign open findings to agents")
                self.stdout.write("Phase 3: Would execute remediation tasks")
                self.stdout.write("Phase 4: Would verify completed fixes")
                return

            results = orchestrator.run_remediation_cycle(max_items_per_phase=limit)

            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("=" * 70))
            self.stdout.write(self.style.SUCCESS("  REMEDIATION CYCLE COMPLETE"))
            self.stdout.write(self.style.SUCCESS("=" * 70))

            # Phase 1 results
            discover = results.get('phase_1_discover', {})
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Phase 1 - Discover:"))
            self.stdout.write(f"  Files scanned: {discover.get('files_scanned', 0)}")
            self.stdout.write(f"  Reports imported: {discover.get('reports_imported', 0)}")
            self.stdout.write(f"  Findings extracted: {discover.get('findings_extracted', 0)}")

            # Phase 2 results
            assign = results.get('phase_2_assign', {})
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Phase 2 - Assign:"))
            self.stdout.write(f"  Findings processed: {assign.get('findings_processed', 0)}")
            self.stdout.write(f"  Tasks created: {assign.get('tasks_created', 0)}")

            # Phase 3 results
            execute = results.get('phase_3_execute', {})
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Phase 3 - Execute:"))
            self.stdout.write(f"  Tasks executed: {execute.get('tasks_executed', 0)}")
            self.stdout.write(f"  Successful: {execute.get('successful', 0)}")
            self.stdout.write(f"  Failed: {execute.get('failed', 0)}")

            # Phase 4 results
            verify = results.get('phase_4_verify', {})
            self.stdout.write("")
            self.stdout.write(self.style.NOTICE("Phase 4 - Verify:"))
            self.stdout.write(f"  Fixes verified: {verify.get('verified', 0)}")
            self.stdout.write(f"  Still pending: {verify.get('pending', 0)}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error in remediation cycle: {e}")
            )
            logger.exception("Error in auto_remediate full cycle")

    def _run_discover(self, orchestrator, dry_run, verbose):
        """Run Phase 1: Discover and import audits."""
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Phase 1: Discovering Audit Files..."))

        try:
            if dry_run:
                self.stdout.write("Would scan docs/audits/ for new audit files")
                return

            results = orchestrator.discover_and_import_audits()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Scanned {results.get('files_scanned', 0)} files, "
                    f"imported {results.get('reports_imported', 0)} reports, "
                    f"extracted {results.get('findings_extracted', 0)} findings"
                )
            )

            if verbose:
                for imported in results.get('imported', []):
                    self.stdout.write(f"  + {imported}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error in discover phase: {e}")
            )

    def _run_validate(self, orchestrator, dry_run, verbose):
        """Run Phase 1.5: Validate stale findings from old sessions."""
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Phase 1.5: Validating Stale Findings..."))

        try:
            if dry_run:
                self.stdout.write("Would validate findings from old sessions for staleness")
                orchestrator.dry_run = True

            results = orchestrator.validate_stale_findings()

            if results.get('skipped'):
                self.stdout.write(
                    self.style.WARNING(f"Skipped: {results.get('reason', 'Unknown')}")
                )
                return

            self.stdout.write(
                self.style.SUCCESS(
                    f"Checked {results.get('total_checked', 0)} stale findings: "
                    f"{results.get('marked_deferred', 0)} deferred, "
                    f"{results.get('marked_wontfix', 0)} obsolete, "
                    f"{results.get('still_valid', 0)} still valid"
                )
            )

            if verbose:
                for detail in results.get('details', []):
                    status = detail['validation']['status']
                    icon = '⏸️' if status == 'likely_fixed' else '🚫' if status == 'obsolete' else '✅'
                    self.stdout.write(
                        f"  {icon} Session {detail['session']}: {detail['title']}"
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error in validate phase: {e}")
            )
            logger.exception("Error in validate phase")

    def _run_assign(self, orchestrator, dry_run, limit, verbose):
        """Run Phase 2: Assign findings to agents."""
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Phase 2: Assigning Findings to Agents..."))

        try:
            if dry_run:
                self.stdout.write(f"Would assign up to {limit} open findings to agents")
                return

            results = orchestrator.assign_open_findings(limit=limit)

            assigned = results.get('assigned', 0)
            tasks_created = len(results.get('assignments', []))

            self.stdout.write(
                self.style.SUCCESS(
                    f"Assigned {assigned} findings, "
                    f"created {tasks_created} remediation tasks"
                )
            )

            if verbose:
                for assignment in results.get('assignments', []):
                    self.stdout.write(
                        f"  {assignment.get('finding_title', 'Unknown')} -> {assignment['agent']}"
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error in assign phase: {e}")
            )

    def _run_execute(self, orchestrator, dry_run, limit, verbose):
        """Run Phase 3: Execute remediation tasks."""
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Phase 3: Executing Remediation Tasks..."))

        try:
            if dry_run:
                self.stdout.write(f"Would execute up to {limit} assigned tasks via agents")
                return

            results = orchestrator.execute_assigned_tasks(limit=limit)

            successful = results.get('successful', 0)
            failed = results.get('failed', 0)
            total = results.get('tasks_executed', 0)

            if successful > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"Executed {total} tasks: {successful} successful, {failed} failed")
                )
            else:
                self.stdout.write(
                    f"Executed {total} tasks: {successful} successful, {failed} failed"
                )

            if verbose:
                for execution in results.get('executions', []):
                    status = "✅" if execution['success'] else "❌"
                    self.stdout.write(
                        f"  {status} {execution['task']} by {execution['agent']}"
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error in execute phase: {e}")
            )

    def _run_verify(self, orchestrator, dry_run, limit, verbose):
        """Run Phase 4: Verify completed fixes."""
        self.stdout.write("")
        self.stdout.write(self.style.NOTICE("Phase 4: Verifying Completed Fixes..."))

        try:
            if dry_run:
                self.stdout.write(f"Would verify up to {limit} completed fixes")
                return

            results = orchestrator.verify_completed_fixes(limit=limit)

            verified = results.get('verified', 0)
            pending = results.get('pending', 0)

            if verified > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"Verified {verified} fixes, {pending} still pending")
                )
            else:
                self.stdout.write(f"Verified {verified} fixes, {pending} still pending")

            if verbose:
                for verification in results.get('verifications', []):
                    status = "✅" if verification['passed'] else "❌"
                    self.stdout.write(
                        f"  {status} {verification['finding']}: {verification['result']}"
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error in verify phase: {e}")
            )
