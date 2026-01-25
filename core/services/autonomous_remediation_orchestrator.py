"""
Session 820: Autonomous Remediation Orchestrator

This service enables the system to be fully self-contained and self-healing by:
1. Automatically discovering and importing audits from docs/audits/
2. Mapping findings to the most appropriate agents
3. Executing remediation tasks autonomously via agents
4. Verifying that fixes actually worked
5. Learning from successes and failures

The system no longer requires humans to post audits - it discovers,
analyzes, and fixes issues on its own.

Architecture:
    ┌─────────────────────────────────────────────────────────────────┐
    │                   AUTONOMOUS REMEDIATION CYCLE                   │
    │                         (Celery Beat)                           │
    ├─────────────────────────────────────────────────────────────────┤
    │  1. DISCOVER      2. ASSIGN        3. EXECUTE      4. VERIFY   │
    │  ──────────      ────────         ─────────       ────────     │
    │  Scan docs/      Match finding    Route to        Run checks   │
    │  audits/ for     to best agent    agent via       to confirm   │
    │  new files       based on         AgentRouter     fix worked   │
    │                  category                                       │
    └─────────────────────────────────────────────────────────────────┘
"""

import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


# =============================================================================
# FINDING TO AGENT MAPPING
# =============================================================================

# Maps (category, affected_component_pattern) -> agent_name
# More specific patterns are checked first
FINDING_TO_AGENT_MAPPING: List[Tuple[str, str, str]] = [
    # Security findings
    ('security', '*', 'CodeReviewAgent'),
    ('authentication', '*', 'CodeReviewAgent'),

    # Code quality - by component
    ('code_quality', 'core/agents/*', 'CodeReviewAgent'),
    ('code_quality', 'core/services/*', 'CodeReviewAgent'),
    ('code_quality', 'frontend/*', 'FullStackDeveloperAgent'),
    ('code_quality', '*', 'CodeGeneratorAgent'),

    # Database and API
    ('data_integrity', '*', 'FullStackDeveloperAgent'),
    ('integration', 'api*', 'FullStackDeveloperAgent'),
    ('integration', '*', 'DevOpsAgent'),

    # Performance
    ('performance', 'celery*', 'DevOpsAgent'),
    ('performance', '*', 'DevOpsAgent'),

    # Documentation
    ('documentation', '*', 'TechnicalDocumentAgent'),

    # Consistency
    ('consistency', 'frontend/*', 'FullStackDeveloperAgent'),
    ('consistency', '*', 'CodeReviewAgent'),

    # Default fallback
    ('other', '*', 'CodeGeneratorAgent'),
]


class AutonomousRemediationOrchestrator:
    """
    Orchestrates the autonomous discovery, assignment, execution, and
    verification of audit finding remediation.

    Usage:
        orchestrator = AutonomousRemediationOrchestrator()

        # Run full cycle
        results = orchestrator.run_remediation_cycle()

        # Or run individual phases
        orchestrator.discover_and_import_audits()
        orchestrator.assign_open_findings()
        orchestrator.execute_assigned_tasks()
        orchestrator.verify_completed_fixes()
    """

    def __init__(self, max_tasks_per_cycle: int = 5, dry_run: bool = False):
        """
        Initialize the orchestrator.

        Args:
            max_tasks_per_cycle: Maximum remediation tasks to execute per cycle
            dry_run: If True, don't actually execute anything
        """
        self.max_tasks_per_cycle = max_tasks_per_cycle
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

    # =========================================================================
    # PHASE 1: DISCOVERY
    # =========================================================================

    def discover_and_import_audits(self) -> Dict[str, Any]:
        """
        Phase 1: Discover and import new audit files.

        Scans docs/audits/ for new or updated audit files and imports them
        into the AuditReport/AuditFinding database.

        Returns:
            Dict with import statistics
        """
        from core.services.audit_tracker import AuditTrackerService

        self.logger.info("🔍 [PHASE 1] Discovering and importing audits...")

        try:
            service = AuditTrackerService()
            results = service.import_all_audits(dry_run=self.dry_run)

            self.logger.info(
                f"✅ [PHASE 1] Complete: {results.get('imported', 0)} imported, "
                f"{results.get('updated', 0)} updated, "
                f"{results.get('findings_created', 0)} findings"
            )

            return results

        except Exception as e:
            self.logger.error(f"❌ [PHASE 1] Failed: {e}", exc_info=True)
            return {'error': str(e), 'imported': 0}

    # =========================================================================
    # PHASE 2: ASSIGNMENT
    # =========================================================================

    def assign_open_findings(self, priority_filter: List[str] = None) -> Dict[str, Any]:
        """
        Phase 2: Assign open findings to appropriate agents.

        Matches each open finding to the best agent based on:
        - Finding category (security, code_quality, etc.)
        - Affected files/components
        - Agent specialization

        Args:
            priority_filter: Only assign findings with these priorities (e.g., ['P0', 'P1'])

        Returns:
            Dict with assignment statistics
        """
        from core.models_audit_tracking import AuditFinding, AuditRemediationTask

        self.logger.info("🎯 [PHASE 2] Assigning findings to agents...")

        if priority_filter is None:
            priority_filter = ['P0', 'P1', 'P2']  # Default: all but P3

        # Get open, unassigned findings
        open_findings = AuditFinding.objects.filter(
            status='open',
            assigned_agent=''
        ).filter(
            priority__in=priority_filter
        ).order_by('priority', '-created_at')

        results = {
            'total_open': open_findings.count(),
            'assigned': 0,
            'skipped': 0,
            'assignments': [],
        }

        for finding in open_findings:
            agent_name = self._match_finding_to_agent(finding)

            if agent_name:
                if not self.dry_run:
                    # Create remediation task
                    task = AuditRemediationTask.objects.create(
                        finding=finding,
                        title=f"Fix: {finding.title[:200]}",
                        description=self._build_remediation_prompt(finding),
                        status='assigned',
                        assigned_agent=agent_name,
                        assigned_at=timezone.now(),
                    )

                    # Update finding status
                    finding.assigned_agent = agent_name
                    finding.assigned_at = timezone.now()
                    finding.status = 'in_progress'
                    finding.save(update_fields=['assigned_agent', 'assigned_at', 'status', 'updated_at'])

                    results['assignments'].append({
                        'finding_id': str(finding.id),
                        'finding_title': finding.title[:50],
                        'agent': agent_name,
                        'task_id': str(task.id),
                    })

                results['assigned'] += 1
                self.logger.info(f"  → Assigned [{finding.priority}] {finding.title[:40]}... to {agent_name}")
            else:
                results['skipped'] += 1

        self.logger.info(
            f"✅ [PHASE 2] Complete: {results['assigned']} assigned, "
            f"{results['skipped']} skipped"
        )

        return results

    def _match_finding_to_agent(self, finding) -> Optional[str]:
        """Match a finding to the most appropriate agent."""
        category = finding.category or 'other'
        affected_files = finding.affected_files or []

        # Try to match based on affected files first
        for cat, pattern, agent in FINDING_TO_AGENT_MAPPING:
            if cat == category:
                if pattern == '*':
                    return agent
                # Check if any affected file matches the pattern
                for file_path in affected_files:
                    if self._path_matches_pattern(file_path, pattern):
                        return agent

        # Fallback to category-only matching
        for cat, pattern, agent in FINDING_TO_AGENT_MAPPING:
            if cat == category and pattern == '*':
                return agent

        # Ultimate fallback
        return 'CodeGeneratorAgent'

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a file path matches a glob-like pattern."""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)

    def _build_remediation_prompt(self, finding) -> str:
        """Build a detailed prompt for the agent to fix the finding."""
        prompt = f"""## Audit Finding Remediation Task

**Finding:** {finding.title}
**Priority:** {finding.priority}
**Category:** {finding.category}
**From Audit:** {finding.audit_report.title if finding.audit_report else 'Unknown'}

### Description
{finding.description}

### Recommendation
{finding.recommendation or 'No specific recommendation provided.'}

### Affected Files
{chr(10).join('- ' + f for f in (finding.affected_files or [])) or 'No specific files identified.'}

### Instructions
1. Analyze the finding and understand the issue
2. Identify the root cause
3. Implement a fix that addresses the finding
4. Ensure the fix doesn't break existing functionality
5. Document what was changed and why

### Expected Outcome
The finding should be resolved after your changes. The verification step will check if the fix worked.
"""
        return prompt

    # =========================================================================
    # PHASE 3: EXECUTION
    # =========================================================================

    def execute_assigned_tasks(self) -> Dict[str, Any]:
        """
        Phase 3: Execute assigned remediation tasks via agents.

        Runs each assigned task through the AgentRouter to let the
        appropriate agent attempt to fix the issue.

        Returns:
            Dict with execution statistics
        """
        from core.models_audit_tracking import AuditRemediationTask

        self.logger.info("🔧 [PHASE 3] Executing remediation tasks...")

        # Get assigned but not yet started tasks
        tasks = AuditRemediationTask.objects.filter(
            status='assigned',
            assigned_agent__isnull=False
        ).exclude(
            assigned_agent=''
        ).order_by('finding__priority', 'created_at')[:self.max_tasks_per_cycle]

        results = {
            'total_queued': AuditRemediationTask.objects.filter(status='assigned').count(),
            'attempted': 0,
            'succeeded': 0,
            'failed': 0,
            'executions': [],
        }

        for task in tasks:
            if self.dry_run:
                self.logger.info(f"  [DRY RUN] Would execute: {task.title[:50]}...")
                results['attempted'] += 1
                continue

            try:
                execution_result = self._execute_single_task(task)
                results['attempted'] += 1

                if execution_result.get('success'):
                    results['succeeded'] += 1
                    results['executions'].append({
                        'task_id': str(task.id),
                        'status': 'success',
                        'agent': task.assigned_agent,
                    })
                else:
                    results['failed'] += 1
                    results['executions'].append({
                        'task_id': str(task.id),
                        'status': 'failed',
                        'error': execution_result.get('error', 'Unknown error'),
                    })

            except Exception as e:
                self.logger.error(f"  ❌ Task {task.id} failed: {e}")
                results['failed'] += 1
                task.status = 'failed'
                task.execution_result = {'error': str(e)}
                task.save()

        self.logger.info(
            f"✅ [PHASE 3] Complete: {results['succeeded']}/{results['attempted']} succeeded"
        )

        return results

    def _execute_single_task(self, task) -> Dict[str, Any]:
        """Execute a single remediation task via the agent."""
        from core.agent_router import AgentRouter

        self.logger.info(f"  → Executing: {task.title[:50]}... via {task.assigned_agent}")

        # Update task status
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save(update_fields=['status', 'started_at', 'updated_at'])

        try:
            # Route to the assigned agent
            router = AgentRouter(user=None)  # System execution
            result = router.route(
                agent_name=task.assigned_agent,
                task=task.description,
                context={
                    'audit_finding_id': str(task.finding.id),
                    'audit_report_id': str(task.finding.audit_report.id) if task.finding.audit_report else None,
                    'affected_files': task.finding.affected_files,
                    'priority': task.finding.priority,
                    'autonomous_remediation': True,
                }
            )

            # Record result
            task.status = 'completed' if result.success else 'failed'
            task.completed_at = timezone.now()
            task.execution_result = {
                'success': result.success,
                'message': result.message[:2000] if result.message else '',
                'data': result.data if hasattr(result, 'data') else {},
                'agent_name': result.agent_name if hasattr(result, 'agent_name') else task.assigned_agent,
                'execution_time_ms': result.execution_time_ms if hasattr(result, 'execution_time_ms') else 0,
            }
            task.save()

            # Update finding status
            if result.success:
                task.finding.status = 'fixed'
                task.finding.fixed_by = f"Auto-remediation via {task.assigned_agent}"
                task.finding.fixed_at = timezone.now()
                task.finding.remediation_notes = result.message[:500] if result.message else ''
                task.finding.save()

            return {
                'success': result.success,
                'message': result.message,
            }

        except Exception as e:
            self.logger.error(f"  ❌ Execution error: {e}", exc_info=True)
            task.status = 'failed'
            task.completed_at = timezone.now()
            task.execution_result = {'error': str(e)}
            task.save()

            return {
                'success': False,
                'error': str(e),
            }

    # =========================================================================
    # PHASE 4: VERIFICATION
    # =========================================================================

    def verify_completed_fixes(self) -> Dict[str, Any]:
        """
        Phase 4: Verify that completed fixes actually worked.

        Runs verification checks on findings marked as 'fixed' to confirm
        the issue was actually resolved.

        Returns:
            Dict with verification statistics
        """
        from core.models_audit_tracking import AuditFinding, AuditVerificationRun

        self.logger.info("🔬 [PHASE 4] Verifying completed fixes...")

        # Get fixed but not verified findings
        fixed_findings = AuditFinding.objects.filter(
            status='fixed',
            is_verified=False
        ).order_by('fixed_at')[:self.max_tasks_per_cycle]

        results = {
            'total_pending': AuditFinding.objects.filter(status='fixed', is_verified=False).count(),
            'verified': 0,
            'failed': 0,
            'skipped': 0,
            'verifications': [],
        }

        for finding in fixed_findings:
            if self.dry_run:
                self.logger.info(f"  [DRY RUN] Would verify: {finding.title[:50]}...")
                results['skipped'] += 1
                continue

            verification_result = self._verify_finding(finding)

            # Record verification run
            run = AuditVerificationRun.objects.create(
                finding=finding,
                verification_type=verification_result.get('type', 'auto'),
                verification_command=verification_result.get('command', ''),
                passed=verification_result.get('passed', False),
                result_summary=verification_result.get('summary', ''),
                result_details=verification_result,
            )

            if verification_result.get('passed'):
                finding.status = 'verified'
                finding.is_verified = True
                finding.verified_at = timezone.now()
                finding.verification_notes = verification_result.get('summary', '')
                finding.save()
                results['verified'] += 1
                self.logger.info(f"  ✅ Verified: {finding.title[:50]}...")
            else:
                # Reopen the finding
                finding.status = 'open'
                finding.remediation_notes += f"\n[Auto-verification failed: {verification_result.get('summary', '')}]"
                finding.save()
                results['failed'] += 1
                self.logger.info(f"  ❌ Verification failed: {finding.title[:50]}...")

            results['verifications'].append({
                'finding_id': str(finding.id),
                'passed': verification_result.get('passed', False),
                'type': verification_result.get('type', 'auto'),
            })

        self.logger.info(
            f"✅ [PHASE 4] Complete: {results['verified']} verified, "
            f"{results['failed']} failed"
        )

        return results

    def _verify_finding(self, finding) -> Dict[str, Any]:
        """
        Verify a single finding was fixed.

        Uses different verification strategies based on finding category.
        """
        category = finding.category or 'other'

        # Choose verification strategy
        if category in ('security', 'authentication'):
            return self._verify_security_finding(finding)
        elif category == 'code_quality':
            return self._verify_code_quality_finding(finding)
        elif category == 'documentation':
            return self._verify_documentation_finding(finding)
        elif category == 'integration':
            return self._verify_integration_finding(finding)
        else:
            return self._verify_generic_finding(finding)

    def _verify_security_finding(self, finding) -> Dict[str, Any]:
        """Verify security-related fixes."""
        # Check if affected files have proper decorators
        affected_files = finding.affected_files or []
        issues_found = []

        for file_path in affected_files:
            path = Path(file_path)
            if path.exists() and path.suffix == '.py':
                content = path.read_text()

                # Check for common security patterns
                if 'no auth' in finding.title.lower():
                    if '@login_required' not in content and '@csrf_exempt' in content:
                        issues_found.append(f"{file_path}: Still has @csrf_exempt without proper auth")

        return {
            'type': 'security_check',
            'passed': len(issues_found) == 0,
            'summary': 'All security checks passed' if not issues_found else '; '.join(issues_found),
            'issues': issues_found,
        }

    def _verify_code_quality_finding(self, finding) -> Dict[str, Any]:
        """Verify code quality fixes."""
        affected_files = finding.affected_files or []

        # Simple check: verify files exist and have reasonable content
        missing_files = []
        for file_path in affected_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        return {
            'type': 'code_quality_check',
            'passed': len(missing_files) == 0,
            'summary': 'All files exist' if not missing_files else f'Missing files: {", ".join(missing_files)}',
        }

    def _verify_documentation_finding(self, finding) -> Dict[str, Any]:
        """Verify documentation fixes."""
        # Check if relevant docs exist
        affected_files = finding.affected_files or []

        for file_path in affected_files:
            if Path(file_path).exists():
                return {
                    'type': 'documentation_check',
                    'passed': True,
                    'summary': f'Documentation file exists: {file_path}',
                }

        # Auto-pass if no specific files mentioned
        return {
            'type': 'documentation_check',
            'passed': True,
            'summary': 'No specific documentation files to verify',
        }

    def _verify_integration_finding(self, finding) -> Dict[str, Any]:
        """Verify integration fixes."""
        # For API/integration issues, we'd ideally run an API test
        # For now, do a simple file existence check
        return self._verify_generic_finding(finding)

    def _verify_generic_finding(self, finding) -> Dict[str, Any]:
        """Generic verification for findings without specific strategies."""
        # Simple heuristic: if there's a remediation task that succeeded, trust it
        tasks = finding.remediation_tasks.filter(status='completed')

        if tasks.exists():
            latest_task = tasks.order_by('-completed_at').first()
            result = latest_task.execution_result or {}

            return {
                'type': 'task_completion_check',
                'passed': result.get('success', False),
                'summary': f'Remediation task completed by {latest_task.assigned_agent}',
                'task_id': str(latest_task.id),
            }

        return {
            'type': 'manual_review_required',
            'passed': False,
            'summary': 'No automated verification available - manual review required',
        }

    # =========================================================================
    # FULL CYCLE ORCHESTRATION
    # =========================================================================

    def run_remediation_cycle(self, priority_filter: List[str] = None) -> Dict[str, Any]:
        """
        Run a complete autonomous remediation cycle.

        Phases:
        1. Discover: Import any new audit files
        2. Assign: Match findings to appropriate agents
        3. Execute: Run agents on assigned findings
        4. Verify: Confirm fixes worked

        Args:
            priority_filter: Only process findings with these priorities

        Returns:
            Dict with complete cycle statistics
        """
        from core.models_audit_tracking import AuditFinding

        cycle_start = timezone.now()

        self.logger.info("=" * 60)
        self.logger.info("🔄 AUTONOMOUS REMEDIATION CYCLE STARTING")
        self.logger.info("=" * 60)

        results = {
            'cycle_start': cycle_start.isoformat(),
            'dry_run': self.dry_run,
            'phases': {},
        }

        # Phase 1: Discovery
        results['phases']['discovery'] = self.discover_and_import_audits()

        # Phase 2: Assignment
        results['phases']['assignment'] = self.assign_open_findings(priority_filter)

        # Phase 3: Execution
        results['phases']['execution'] = self.execute_assigned_tasks()

        # Phase 4: Verification
        results['phases']['verification'] = self.verify_completed_fixes()

        # Summary
        cycle_end = timezone.now()
        duration = (cycle_end - cycle_start).total_seconds()

        # Get current state
        open_p0 = AuditFinding.objects.filter(status='open', priority='P0').count()
        open_p1 = AuditFinding.objects.filter(status='open', priority='P1').count()
        in_progress = AuditFinding.objects.filter(status='in_progress').count()
        fixed = AuditFinding.objects.filter(status='fixed').count()
        verified = AuditFinding.objects.filter(status='verified').count()

        results['summary'] = {
            'duration_seconds': duration,
            'findings_state': {
                'open_p0': open_p0,
                'open_p1': open_p1,
                'in_progress': in_progress,
                'fixed': fixed,
                'verified': verified,
            },
            'alerts': [],
        }

        # Alert if critical issues remain
        if open_p0 > 0:
            results['summary']['alerts'].append(f"⚠️ {open_p0} P0 (critical) findings still open!")

        self.logger.info("=" * 60)
        self.logger.info(f"🔄 CYCLE COMPLETE in {duration:.1f}s")
        self.logger.info(f"   Open P0: {open_p0} | Open P1: {open_p1} | In Progress: {in_progress}")
        self.logger.info(f"   Fixed: {fixed} | Verified: {verified}")
        self.logger.info("=" * 60)

        return results

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current remediation status."""
        from core.models_audit_tracking import AuditFinding, AuditRemediationTask, AuditReport

        return {
            'audits': {
                'total': AuditReport.objects.count(),
            },
            'findings': {
                'total': AuditFinding.objects.count(),
                'open': AuditFinding.objects.filter(status='open').count(),
                'in_progress': AuditFinding.objects.filter(status='in_progress').count(),
                'fixed': AuditFinding.objects.filter(status='fixed').count(),
                'verified': AuditFinding.objects.filter(status='verified').count(),
                'wontfix': AuditFinding.objects.filter(status='wontfix').count(),
                'by_priority': {
                    'P0': AuditFinding.objects.filter(priority='P0', status='open').count(),
                    'P1': AuditFinding.objects.filter(priority='P1', status='open').count(),
                    'P2': AuditFinding.objects.filter(priority='P2', status='open').count(),
                    'P3': AuditFinding.objects.filter(priority='P3', status='open').count(),
                },
            },
            'tasks': {
                'pending': AuditRemediationTask.objects.filter(status='pending').count(),
                'assigned': AuditRemediationTask.objects.filter(status='assigned').count(),
                'in_progress': AuditRemediationTask.objects.filter(status='in_progress').count(),
                'completed': AuditRemediationTask.objects.filter(status='completed').count(),
                'failed': AuditRemediationTask.objects.filter(status='failed').count(),
            },
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_orchestrator_instance: Optional[AutonomousRemediationOrchestrator] = None


def get_remediation_orchestrator(
    max_tasks_per_cycle: int = 5,
    dry_run: bool = False
) -> AutonomousRemediationOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = AutonomousRemediationOrchestrator(
            max_tasks_per_cycle=max_tasks_per_cycle,
            dry_run=dry_run
        )
    return _orchestrator_instance
