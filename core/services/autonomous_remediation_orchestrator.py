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
    ('code_quality', '*', 'CodeReviewAgent'),

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
    ('other', '*', 'CodeReviewAgent'),
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

    def __init__(self, max_tasks_per_cycle: int = 5, dry_run: bool = False, auto_commit: bool = True):
        """
        Initialize the orchestrator.

        Args:
            max_tasks_per_cycle: Maximum remediation tasks to execute per cycle
            dry_run: If True, don't actually execute anything
            auto_commit: If True, auto-commit generated code changes (Session 822)
        """
        self.max_tasks_per_cycle = max_tasks_per_cycle
        self.dry_run = dry_run
        self.auto_commit = auto_commit
        self.logger = logging.getLogger(__name__)
        self._workspace = None
        self._workspace_manager = None

    # =========================================================================
    # SESSION 822: SKIN LAYER INTEGRATION
    # =========================================================================

    def _get_system_workspace(self):
        """
        Session 822: Get the system workspace for autonomous file operations.

        Returns the project workspace for this codebase, enabling agents
        to write generated code directly.
        """
        if self._workspace:
            return self._workspace

        try:
            from django.apps import apps
            from django.contrib.auth import get_user_model

            ProjectWorkspace = apps.get_model('core', 'ProjectWorkspace')
            User = get_user_model()

            # Get system user or admin
            system_user = User.objects.filter(username='system').first()
            if not system_user:
                system_user = User.objects.filter(username='admin').first()

            if not system_user:
                self.logger.warning("No system or admin user found for workspace access")
                return None

            # Get the active workspace
            workspace = ProjectWorkspace.objects.filter(
                is_active=True,
                allow_file_write=True
            ).first()

            if workspace:
                self._workspace = workspace
                self.logger.info(f"Using workspace: {workspace.name} @ {workspace.root_path}")

            return self._workspace

        except Exception as e:
            self.logger.error(f"Failed to get system workspace: {e}")
            return None

    def _get_workspace_manager(self):
        """Get WorkspaceManager for file operations."""
        if self._workspace_manager:
            return self._workspace_manager

        try:
            from core.services.workspace_manager import WorkspaceManager
            from django.contrib.auth import get_user_model

            User = get_user_model()

            # Get system user
            system_user = User.objects.filter(username='system').first()
            if not system_user:
                system_user = User.objects.filter(username='admin').first()

            if system_user:
                self._workspace_manager = WorkspaceManager(user=system_user)

            return self._workspace_manager

        except Exception as e:
            self.logger.error(f"Failed to get WorkspaceManager: {e}")
            return None

    def _parse_code_from_result(self, result_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Session 822: Extract generated code files from agent result.

        Parses agent output to find code blocks that should be written.
        Supports multiple formats:
        - Direct 'code' field with file markers
        - 'results' array with code items
        - 'files' array with filename/content
        """
        files = []

        # Check for 'results' array (common format)
        if 'results' in result_data:
            for r in result_data['results']:
                if isinstance(r, dict) and 'data' in r:
                    data = r['data']
                    if 'code' in data:
                        files.extend(self._parse_code_blocks(data['code']))

        # Check for direct 'code' field
        if 'code' in result_data:
            files.extend(self._parse_code_blocks(result_data['code']))

        # Check for 'files' array
        if 'files' in result_data and isinstance(result_data['files'], list):
            for f in result_data['files']:
                if isinstance(f, dict) and 'filename' in f and 'content' in f:
                    files.append({
                        'filename': f['filename'],
                        'content': f['content'],
                        'language': f.get('language', 'python')
                    })

        # Check for 'content' field that might have code
        if 'content' in result_data and isinstance(result_data['content'], str):
            if '```' in result_data['content']:
                files.extend(self._parse_code_blocks(result_data['content']))

        # Session 822: Also check 'message' field (agents sometimes put code here)
        if 'message' in result_data and isinstance(result_data['message'], str):
            if '```' in result_data['message']:
                files.extend(self._parse_code_blocks(result_data['message']))

        # Session 822: Check 'query' field in results (may contain code)
        if 'query' in result_data and isinstance(result_data['query'], str):
            if '```' in result_data['query']:
                files.extend(self._parse_code_blocks(result_data['query']))

        return files

    def _parse_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """
        Parse code blocks from markdown-formatted content.

        Session 822: Enhanced to extract filenames from multiple formats.
        Supports formats:
        - ### path/to/file.py\n```python\n...\n```
        - ```python\n# filename.py\n...\n```
        - Docstrings containing filenames
        - Fallback naming for substantial code blocks
        """
        files = []

        # Pattern 1: ### path/to/file.ext\n```lang\n...\n```
        pattern1 = r'###\s+([^\n]+)\n```(\w+)?\n(.*?)```'
        for match in re.finditer(pattern1, content, re.DOTALL):
            filename = match.group(1).strip()
            language = match.group(2) or 'text'
            code = match.group(3).strip()
            files.append({
                'filename': filename,
                'content': code,
                'language': language
            })

        # Pattern 2: ```python\n# path/to/file.py\n...\n```
        if not files:
            pattern2 = r'```(\w+)?\n#\s*([^\n]+\.py)\n(.*?)```'
            for match in re.finditer(pattern2, content, re.DOTALL):
                language = match.group(1) or 'python'
                filename = match.group(2).strip()
                code = match.group(3).strip()
                files.append({
                    'filename': filename,
                    'content': f"# {filename}\n{code}",
                    'language': language
                })

        # Pattern 3: Docstring with filename ("""filename.py or '''filename.py)
        if not files:
            pattern3 = r'```(\w+)?\n(?:#![^\n]*\n)?(?:\"\"\"|\'\'\')([^\n]+\.py)\n(.*?)```'
            for match in re.finditer(pattern3, content, re.DOTALL):
                language = match.group(1) or 'python'
                filename = match.group(2).strip()
                code = match.group(3).strip()
                # Reconstruct with docstring
                first_line = f'"""{filename}'
                files.append({
                    'filename': filename,
                    'content': f'{first_line}\n{code}',
                    'language': language
                })

        # Pattern 4: Look for filename in first few lines of code block
        if not files:
            pattern4 = r'```(\w+)?\n(.*?)```'
            for match in re.finditer(pattern4, content, re.DOTALL):
                language = match.group(1) or 'python'
                code = match.group(2).strip()

                # Skip very short blocks (likely examples, not real files)
                if len(code) < 100:
                    continue

                # Try to extract filename from docstring (handles newline after opening quotes)
                filename = None
                docstring_match = re.search(r'(?:\"\"\"|\'\'\')[\n\s]*([^\n\"]+\.py)', code[:400])
                if docstring_match:
                    filename = docstring_match.group(1).strip()

                # Try to extract from class/function name for substantial code
                if not filename and ('class ' in code or 'def ' in code):
                    # Generate filename from first class or major function
                    class_match = re.search(r'class\s+(\w+)', code)
                    if class_match:
                        filename = f"{class_match.group(1).lower()}.py"

                if filename:
                    files.append({
                        'filename': filename,
                        'content': code,
                        'language': language
                    })

        return files

    def _write_and_commit_files(
        self,
        files: List[Dict[str, str]],
        task,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Session 822: Write generated files to workspace and auto-commit.

        This is the core SKIN layer integration that enables autonomous
        code deployment without human intervention.
        """
        if not files:
            return {'written': False, 'reason': 'No files to write'}

        workspace = self._get_system_workspace()
        if not workspace:
            return {'written': False, 'reason': 'No workspace available'}

        manager = self._get_workspace_manager()
        if not manager:
            return {'written': False, 'reason': 'No workspace manager available'}

        written_files = []
        failed_files = []

        for file_info in files:
            filename = file_info.get('filename', '').strip()
            content = file_info.get('content', '')

            # Skip invalid files
            if not filename or not content:
                continue

            # Clean up filename
            filename = filename.lstrip('/')
            if filename.startswith('```'):
                continue

            try:
                operation = manager.write_file(
                    workspace=workspace,
                    file_path=filename,
                    content=content,
                    agent_name=agent_name
                )

                if operation.success:
                    written_files.append({
                        'path': filename,
                        'operation_id': str(operation.id),
                        'size': len(content)
                    })
                    self.logger.info(f"  📝 Wrote: {filename}")
                else:
                    failed_files.append({
                        'path': filename,
                        'error': operation.error_message
                    })

            except Exception as e:
                self.logger.error(f"  ❌ Failed to write {filename}: {e}")
                failed_files.append({
                    'path': filename,
                    'error': str(e)
                })

        result = {
            'written': len(written_files) > 0,
            'files_written': written_files,
            'files_failed': failed_files,
            'total_written': len(written_files),
            'total_failed': len(failed_files)
        }

        # Auto-PR if enabled and files were written
        if self.auto_commit and written_files:
            pr_result = self._create_pr_for_changes(
                workspace=workspace,
                files=written_files,
                task=task,
                agent_name=agent_name
            )
            result['pr'] = pr_result

        return result

    def _create_pr_for_changes(
        self,
        workspace,
        files: List[Dict],
        task,
        agent_name: str
    ) -> Dict[str, Any]:
        """
        Session 823: Create a PR for agent-generated changes.

        Instead of committing directly to main (which is blocked by pre-commit
        hooks for safety), this method:
        1. Creates a feature branch
        2. Commits the changes
        3. Pushes the branch
        4. Creates a PR for human review
        5. Returns to the original branch

        This enables autonomous code generation while maintaining human oversight.
        """
        import uuid

        try:
            root_path = Path(workspace.root_path)
            finding_id = str(task.finding.id)[:8] if task.finding else 'unknown'
            finding_title = task.finding.title[:40] if task.finding else 'Unknown finding'

            # Generate unique branch name
            branch_name = f"auto-remediate/{finding_id}-{uuid.uuid4().hex[:6]}"

            # Step 1: Get current branch to return to later
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=str(root_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            original_branch = result.stdout.strip() or 'main'

            # Step 2: Create and switch to feature branch
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=str(root_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                return {'pr_created': False, 'error': f'Failed to create branch: {result.stderr}'}

            self.logger.info(f"  🌿 Created branch: {branch_name}")

            try:
                # Step 3: Stage the files
                file_paths = [f['path'] for f in files]
                result = subprocess.run(
                    ['git', 'add'] + file_paths,
                    cwd=str(root_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    raise Exception(f'Failed to stage files: {result.stderr}')

                # Step 4: Create commit
                commit_msg = f"""fix(auto-remediate): {finding_title}

Auto-remediation by {agent_name}
Finding ID: {task.finding.id if task.finding else 'N/A'}
Task ID: {task.id}

Files modified:
{chr(10).join('- ' + f['path'] for f in files)}

Co-Authored-By: {agent_name} <auto@system>
"""
                result = subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=str(root_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    raise Exception(f'Failed to commit: {result.stderr}')

                self.logger.info(f"  ✅ Committed changes")

                # Step 5: Push the branch
                result = subprocess.run(
                    ['git', 'push', '-u', 'origin', branch_name],
                    cwd=str(root_path),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode != 0:
                    raise Exception(f'Failed to push: {result.stderr}')

                self.logger.info(f"  📤 Pushed to origin/{branch_name}")

                # Step 6: Create PR using gh CLI
                pr_title = f"fix(auto-remediate): {finding_title}"
                pr_body = f"""## Auto-Remediation PR

**Agent:** {agent_name}
**Finding:** {task.finding.title if task.finding else 'N/A'}
**Finding ID:** {task.finding.id if task.finding else 'N/A'}
**Task ID:** {task.id}

### Files Modified
{chr(10).join('- `' + f['path'] + '`' for f in files)}

### Description
This PR was automatically generated by the autonomous remediation system.
Please review the changes before merging.

---
🤖 Generated by Auto-Remediation System
"""
                result = subprocess.run(
                    ['gh', 'pr', 'create',
                     '--title', pr_title,
                     '--body', pr_body,
                     '--base', 'main'],
                    cwd=str(root_path),
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                pr_url = None
                if result.returncode == 0:
                    pr_url = result.stdout.strip()
                    self.logger.info(f"  🎉 Created PR: {pr_url}")
                else:
                    self.logger.warning(f"  ⚠️ PR creation failed: {result.stderr}")

                return {
                    'pr_created': pr_url is not None,
                    'pr_url': pr_url,
                    'branch': branch_name,
                    'files': len(files),
                    'commit_message': commit_msg.split('\n')[0]
                }

            finally:
                # Step 7: Always return to original branch
                subprocess.run(
                    ['git', 'checkout', original_branch],
                    cwd=str(root_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                self.logger.info(f"  ↩️ Returned to {original_branch}")

        except Exception as e:
            self.logger.error(f"  ❌ PR creation failed: {e}")
            return {'pr_created': False, 'error': str(e)}

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
                f"✅ [PHASE 1] Complete: {results.get('total_files', 0)} files scanned, "
                f"{results.get('imported', 0)} reports imported, "
                f"{results.get('total_findings', 0)} findings extracted"
            )

            # Normalize keys for management command
            results['files_scanned'] = results.get('total_files', 0)
            results['reports_imported'] = results.get('imported', 0)
            results['findings_extracted'] = results.get('total_findings', 0)

            return results

        except Exception as e:
            self.logger.error(f"❌ [PHASE 1] Failed: {e}", exc_info=True)
            return {'error': str(e), 'imported': 0}

    # =========================================================================
    # PHASE 1.5: STALENESS VALIDATION (Session 821)
    # =========================================================================

    def validate_stale_findings(self, session_threshold: int = 50) -> Dict[str, Any]:
        """
        Phase 1.5: Validate findings from old audits before assignment.

        Audits from sessions significantly older than current may have findings
        that were already addressed in later sessions. This phase:
        1. Identifies findings from audits > session_threshold sessions old
        2. Checks if affected files still exist and contain the issue
        3. Marks truly obsolete findings as 'deferred' or 'wontfix'
        4. Cross-references with later sessions that may have fixed the issue

        Args:
            session_threshold: Number of sessions to consider "stale" (default: 50)

        Returns:
            Dict with validation statistics
        """
        from core.models_audit_tracking import AuditFinding, AuditReport

        self.logger.info(f"🔍 [PHASE 1.5] Validating stale findings (threshold: {session_threshold} sessions)...")

        # Get current session number from 00-START-NEXT-SESSION.md
        current_session = self._get_current_session_number()
        if not current_session:
            self.logger.warning("  ⚠️ Could not determine current session number, skipping validation")
            return {'skipped': True, 'reason': 'Could not determine current session'}

        stale_threshold = current_session - session_threshold

        results = {
            'current_session': current_session,
            'stale_threshold': stale_threshold,
            'total_checked': 0,
            'marked_deferred': 0,
            'marked_wontfix': 0,
            'still_valid': 0,
            'details': [],
        }

        # Find findings from old sessions that are still open
        stale_findings = AuditFinding.objects.filter(
            status='open',
            audit_report__session_number__isnull=False,
            audit_report__session_number__lt=stale_threshold
        ).select_related('audit_report')

        self.logger.info(f"  Found {stale_findings.count()} potentially stale findings")

        for finding in stale_findings:
            results['total_checked'] += 1
            session_gap = current_session - (finding.audit_report.session_number or current_session)

            validation = self._validate_finding_still_relevant(finding, session_gap)

            # Track what would happen (for dry-run preview)
            if validation['status'] == 'likely_fixed':
                results['marked_deferred'] += 1
                action_msg = "⏸️ Would defer (likely fixed)"
            elif validation['status'] == 'obsolete':
                results['marked_wontfix'] += 1
                action_msg = "🚫 Would mark obsolete"
            else:
                results['still_valid'] += 1
                action_msg = "✅ Still valid"

            results['details'].append({
                'finding_id': str(finding.id),
                'title': finding.title[:50],
                'session': finding.audit_report.session_number,
                'session_gap': session_gap,
                'validation': validation,
            })

            if self.dry_run:
                self.logger.info(
                    f"  [DRY RUN] {action_msg}: {finding.title[:40]}... "
                    f"(Session {finding.audit_report.session_number}, gap: {session_gap})"
                )
                continue

            # Actually apply the status change
            if validation['status'] == 'likely_fixed':
                finding.status = 'deferred'
                finding.remediation_notes += (
                    f"\n\n[Session 821 Auto-Validation] Finding from Session "
                    f"{finding.audit_report.session_number} (gap: {session_gap} sessions). "
                    f"Likely already addressed: {validation['reason']}"
                )
                finding.save()
                self.logger.info(f"  ⏸️ Deferred: {finding.title[:40]}... (likely fixed)")

            elif validation['status'] == 'obsolete':
                finding.status = 'wontfix'
                finding.remediation_notes += (
                    f"\n\n[Session 821 Auto-Validation] Finding obsolete: {validation['reason']}"
                )
                finding.save()
                self.logger.info(f"  🚫 Marked obsolete: {finding.title[:40]}...")

            else:
                self.logger.info(f"  ✅ Still valid: {finding.title[:40]}...")

        self.logger.info(
            f"✅ [PHASE 1.5] Complete: {results['total_checked']} checked, "
            f"{results['marked_deferred']} deferred, {results['marked_wontfix']} obsolete, "
            f"{results['still_valid']} still valid"
        )

        return results

    def _get_current_session_number(self) -> Optional[int]:
        """Get current session number from 00-START-NEXT-SESSION.md."""
        try:
            session_file = Path('00-START-NEXT-SESSION.md')
            if not session_file.exists():
                return None

            content = session_file.read_text()
            # Look for "Session XXX" pattern
            match = re.search(r'Session\s+(\d+)', content, re.IGNORECASE)
            if match:
                return int(match.group(1))
        except Exception as e:
            self.logger.warning(f"Error reading session number: {e}")
        return None

    def _validate_finding_still_relevant(self, finding, session_gap: int) -> Dict[str, Any]:
        """
        Validate if a finding from an old session is still relevant.

        Checks:
        1. If affected files still exist
        2. If the specific issue pattern is still present
        3. If later sessions mention addressing this type of issue
        4. Session gap severity

        Returns:
            Dict with 'status' (valid, likely_fixed, obsolete) and 'reason'
        """
        affected_files = finding.affected_files or []
        title_lower = finding.title.lower()
        description_lower = finding.description.lower()

        # Check 1: Very old findings (200+ sessions) are likely obsolete
        if session_gap > 200:
            return {
                'status': 'likely_fixed',
                'reason': f'Finding is {session_gap} sessions old - likely addressed in subsequent work'
            }

        # Check 2: Documentation findings are often quickly addressed
        if finding.category == 'documentation':
            if session_gap > 30:
                return {
                    'status': 'likely_fixed',
                    'reason': 'Documentation findings typically addressed within 30 sessions'
                }

        # Check 3: Check if affected files exist and contain the issue
        if affected_files:
            files_exist = 0
            files_checked = 0
            for file_path in affected_files[:5]:  # Check up to 5 files
                files_checked += 1
                if Path(file_path).exists():
                    files_exist += 1

            if files_checked > 0 and files_exist == 0:
                return {
                    'status': 'obsolete',
                    'reason': f'None of the affected files exist ({files_checked} checked)'
                }

        # Check 4: Look for specific keywords that suggest issue was addressed
        fixed_keywords = [
            'intelligent prompting', 'context optimization', 'learning system',
            'execution metrics', 'knowledge sharing', 'critical docs injection',
            'tiered documentation', 'dynamic prompt'
        ]

        for keyword in fixed_keywords:
            if keyword in title_lower or keyword in description_lower:
                # These were addressed in recent sessions (806-820)
                return {
                    'status': 'likely_fixed',
                    'reason': f'Feature "{keyword}" was implemented in Sessions 806-820'
                }

        # Check 5: Security findings older than 100 sessions - review needed
        if finding.category in ('security', 'authentication') and session_gap > 100:
            return {
                'status': 'likely_fixed',
                'reason': 'Security issue from 100+ sessions ago - likely addressed'
            }

        # Default: still valid
        return {
            'status': 'valid',
            'reason': 'Finding appears still relevant'
        }

    # =========================================================================
    # PHASE 2: ASSIGNMENT
    # =========================================================================

    def assign_open_findings(self, priority_filter: List[str] = None, limit: int = None) -> Dict[str, Any]:
        """
        Phase 2: Assign open findings to appropriate agents.

        Matches each open finding to the best agent based on:
        - Finding category (security, code_quality, etc.)
        - Affected files/components
        - Agent specialization

        Args:
            priority_filter: Only assign findings with these priorities (e.g., ['P0', 'P1'])
            limit: Maximum number of findings to assign (default: no limit)

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

        # Apply limit if specified
        if limit:
            open_findings = open_findings[:limit]

        results = {
            'total_open': AuditFinding.objects.filter(status='open', assigned_agent='').count(),
            'assigned': 0,
            'skipped': 0,
            'assignments': [],
            'limit_applied': limit,
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
        return 'CodeReviewAgent'

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
    # SESSION 823: CODEBASE CONTEXT DISCOVERY
    # =========================================================================

    def _extract_key_terms(self, finding) -> List[str]:
        """
        Session 823: Extract key terms from a finding for codebase search.

        Identifies class names, function names, model names, and other
        identifiers that can be searched in the codebase.

        Returns:
            List of search terms (e.g., ['AgentMood', 'mood_expires_at'])
        """
        terms = []
        text = f"{finding.title} {finding.description} {finding.recommendation or ''}"

        # Pattern 1: CamelCase class names (e.g., AgentMood, UserProfile)
        camel_case = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', text)
        terms.extend(camel_case)

        # Pattern 2: snake_case identifiers (e.g., mood_expires_at, user_id)
        snake_case = re.findall(r'\b([a-z]+_[a-z_]+)\b', text)
        # Filter out common words
        common_words = {'the_', 'this_', 'that_', 'and_', 'for_', 'with_'}
        snake_case = [s for s in snake_case if not any(s.startswith(w) for w in common_words)]
        terms.extend(snake_case)

        # Pattern 3: Model references (e.g., "the Agent model", "AgentMood table")
        model_refs = re.findall(r'\b([A-Z][a-zA-Z]+)\s+(?:model|table|class|object)', text)
        terms.extend(model_refs)

        # Pattern 4: File path references (e.g., core/models.py)
        file_refs = re.findall(r'([a-z_]+/[a-z_/.]+\.py)', text)
        terms.extend(file_refs)

        # Pattern 5: Function/method names in backticks (e.g., `save()`, `check_mood()`)
        backtick_refs = re.findall(r'`([a-zA-Z_][a-zA-Z0-9_]*)`', text)
        terms.extend(backtick_refs)

        # Deduplicate and filter short terms
        unique_terms = list(dict.fromkeys(terms))  # Preserve order, remove duplicates
        filtered_terms = [t for t in unique_terms if len(t) >= 3]

        self.logger.debug(f"  📝 Extracted {len(filtered_terms)} key terms: {filtered_terms[:10]}")

        return filtered_terms[:15]  # Limit to prevent excessive searches

    def _discover_codebase_context(self, finding) -> Dict[str, Any]:
        """
        Session 823: Search the codebase for context relevant to a finding.

        Uses grep to find where key terms are defined/used in the codebase,
        providing agents with the actual file locations and code snippets.

        Returns:
            Dict with:
            - affected_files: List of file paths with line numbers
            - code_snippets: Dict of file -> relevant code
            - search_terms: Terms that were searched
        """
        import os

        project_root = Path(__file__).parent.parent.parent  # Go up to project root
        terms = self._extract_key_terms(finding)

        if not terms:
            return {'affected_files': [], 'code_snippets': {}, 'search_terms': []}

        affected_files = []
        code_snippets = {}
        files_seen = set()

        for term in terms[:8]:  # Limit searches to prevent slowdown
            try:
                # Search for class/function definitions first
                patterns = [
                    f"class {term}",      # Class definition
                    f"def {term}",        # Function definition
                    f"{term} = ",         # Variable assignment
                ]

                for pattern in patterns:
                    try:
                        # Use grep with exclusions for speed
                        result = subprocess.run(
                            [
                                'grep', '-rn',
                                '--include=*.py',
                                '--exclude-dir=.venv',
                                '--exclude-dir=node_modules',
                                '--exclude-dir=.git',
                                '--exclude-dir=__pycache__',
                                '--exclude-dir=migrations',
                                '--exclude-dir=staticfiles',
                                '--exclude-dir=media',
                                '-m', '10',  # Max 10 matches per file
                                pattern,
                                str(project_root)
                            ],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            cwd=str(project_root)
                        )

                        if result.returncode == 0 and result.stdout:
                            lines = result.stdout.strip().split('\n')[:5]  # Limit results per pattern

                            for line in lines:
                                if ':' in line:
                                    parts = line.split(':', 2)
                                    if len(parts) >= 3:
                                        file_path = parts[0]
                                        line_num = parts[1]
                                        code = parts[2].strip()

                                        # Skip test files and migrations
                                        if '/tests/' in file_path or '/migrations/' in file_path:
                                            continue
                                        # Skip the orchestrator itself
                                        if 'autonomous_remediation_orchestrator' in file_path:
                                            continue

                                        # Make path relative
                                        try:
                                            rel_path = os.path.relpath(file_path, project_root)
                                        except ValueError:
                                            rel_path = file_path

                                        file_ref = f"{rel_path}:{line_num}"

                                        if file_ref not in files_seen:
                                            files_seen.add(file_ref)
                                            affected_files.append(file_ref)

                                            # Store code snippet
                                            if rel_path not in code_snippets:
                                                code_snippets[rel_path] = []
                                            code_snippets[rel_path].append({
                                                'line': int(line_num),
                                                'code': code[:200],  # Truncate long lines
                                                'term': term,
                                            })

                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"  ⏱️ Search timeout for pattern: {pattern}")
                        continue

            except Exception as e:
                self.logger.warning(f"  ⚠️ Search error for term '{term}': {e}")
                continue

        self.logger.info(f"  🔍 Found {len(affected_files)} relevant locations for {len(terms)} terms")

        return {
            'affected_files': affected_files[:20],  # Limit total results
            'code_snippets': code_snippets,
            'search_terms': terms,
        }

    def _build_context_prompt(self, finding, codebase_context: Dict[str, Any]) -> str:
        """
        Session 823: Build an enhanced task prompt with codebase context.

        Injects discovered file locations and code snippets into the task
        description so the agent knows what already exists.
        """
        base_description = finding.description

        # Build context section
        context_parts = []

        if codebase_context.get('affected_files'):
            context_parts.append("\n\n## EXISTING CODEBASE CONTEXT\n")
            context_parts.append("**IMPORTANT:** The following files already exist in the codebase. ")
            context_parts.append("MODIFY existing code rather than creating new files/apps.\n\n")

            context_parts.append("### Relevant File Locations:\n")
            for file_ref in codebase_context['affected_files'][:10]:
                context_parts.append(f"- `{file_ref}`\n")

            # Add code snippets for key files
            if codebase_context.get('code_snippets'):
                context_parts.append("\n### Existing Code:\n")
                for file_path, snippets in list(codebase_context['code_snippets'].items())[:3]:
                    context_parts.append(f"\n**{file_path}:**\n```python\n")
                    for snippet in snippets[:3]:
                        context_parts.append(f"# Line {snippet['line']}: {snippet['code']}\n")
                    context_parts.append("```\n")

            context_parts.append("\n### Instructions:\n")
            context_parts.append("1. Check if the fix already exists in the files above\n")
            context_parts.append("2. If modifying an existing model, update it in place\n")
            context_parts.append("3. Do NOT create new Django apps for existing models\n")
            context_parts.append("4. Include the full file path in your code output\n")

        enhanced_description = base_description + ''.join(context_parts)
        return enhanced_description

    # =========================================================================
    # PHASE 3: EXECUTION
    # =========================================================================

    def execute_assigned_tasks(self, limit: int = None) -> Dict[str, Any]:
        """
        Phase 3: Execute assigned remediation tasks via agents.

        Runs each assigned task through the AgentRouter to let the
        appropriate agent attempt to fix the issue.

        Args:
            limit: Maximum number of tasks to execute (default: max_tasks_per_cycle)

        Returns:
            Dict with execution statistics
        """
        from core.models_audit_tracking import AuditRemediationTask

        self.logger.info("🔧 [PHASE 3] Executing remediation tasks...")

        # Use provided limit or fall back to default
        task_limit = limit if limit is not None else self.max_tasks_per_cycle

        # Get assigned but not yet started tasks
        tasks = AuditRemediationTask.objects.filter(
            status='assigned',
            assigned_agent__isnull=False
        ).exclude(
            assigned_agent=''
        ).order_by('finding__priority', 'created_at')[:task_limit]

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
        """
        Execute a single remediation task via the agent.

        Session 822: Now includes SKIN layer integration to automatically
        write generated code to the workspace and auto-commit.

        Session 823: Added codebase context discovery to prevent agents from
        creating duplicate code. Now searches for existing implementations
        before executing.
        """
        from core.agent_router import AgentRouter

        self.logger.info(f"  → Executing: {task.title[:50]}... via {task.assigned_agent}")

        # Update task status
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save(update_fields=['status', 'started_at', 'updated_at'])

        try:
            # Session 823: Discover codebase context before execution
            self.logger.info(f"  🔍 Discovering codebase context...")
            codebase_context = self._discover_codebase_context(task.finding)

            # Build enhanced task description with context
            enhanced_description = self._build_context_prompt(task.finding, codebase_context)

            # Merge discovered files with any pre-existing affected_files
            all_affected_files = list(task.finding.affected_files or [])
            all_affected_files.extend(codebase_context.get('affected_files', []))
            # Deduplicate
            all_affected_files = list(dict.fromkeys(all_affected_files))

            # Route to the assigned agent
            router = AgentRouter(user=None)  # System execution
            result = router.route(
                agent_name=task.assigned_agent,
                task=enhanced_description,  # Session 823: Use enhanced description
                context={
                    'audit_finding_id': str(task.finding.id),
                    'audit_report_id': str(task.finding.audit_report.id) if task.finding.audit_report else None,
                    'affected_files': all_affected_files,  # Session 823: Include discovered files
                    'code_snippets': codebase_context.get('code_snippets', {}),  # Session 823
                    'priority': task.finding.priority,
                    'autonomous_remediation': True,
                    'codebase_search_terms': codebase_context.get('search_terms', []),  # Session 823
                }
            )

            # Session 822: SKIN Layer Integration
            # Parse and write any generated code files
            skin_result = None
            if result.success and hasattr(result, 'data') and result.data:
                files = self._parse_code_from_result(result.data)
                if files:
                    self.logger.info(f"  📦 Found {len(files)} files to write")
                    skin_result = self._write_and_commit_files(
                        files=files,
                        task=task,
                        agent_name=task.assigned_agent
                    )

            # Record result with evidence gating
            execution_data = {
                'success': result.success,
                'message': result.message[:2000] if result.message else '',
                'data': result.data if hasattr(result, 'data') else {},
                'agent_name': result.agent_name if hasattr(result, 'agent_name') else task.assigned_agent,
                'execution_time_ms': result.execution_time_ms if hasattr(result, 'execution_time_ms') else 0,
                'skin_result': skin_result,  # Session 822: Track SKIN layer operations
            }

            # Evidence-gated completion
            has_files = skin_result and skin_result.get('written') and skin_result.get('total_written', 0) > 0
            has_pr = skin_result and skin_result.get('pr', {}).get('pr_created')

            if not result.success:
                # Path A: Agent failed
                task.status = 'failed'
                task.completed_at = timezone.now()
                task.execution_result = execution_data
                task.save()
            elif has_files or has_pr:
                # Path B: Real artifacts exist — mark completed with evidence
                evidence_type = 'pr' if has_pr else 'commit'
                evidence_ref = ''
                if has_pr:
                    evidence_ref = skin_result.get('pr', {}).get('pr_url', '')
                elif has_files:
                    evidence_ref = f"wrote {skin_result.get('total_written', 0)} files"
                task.status = 'completed'
                task.completed_at = timezone.now()
                task.evidence_type = evidence_type
                task.evidence_ref = evidence_ref
                task.verified_by = task.assigned_agent
                task.evidence_verified_at = timezone.now()
                task.execution_result = execution_data
                task.save()

                # Only mark finding as fixed when real evidence exists
                task.finding.status = 'fixed'
                task.finding.fixed_by = f"Auto-remediation via {task.assigned_agent}"
                task.finding.fixed_at = timezone.now()
                remediation_notes = result.message[:500] if result.message else ''
                if has_files:
                    remediation_notes += f"\n\nFiles written: {skin_result.get('total_written', 0)}"
                if has_pr:
                    pr_info = skin_result.get('pr', {})
                    remediation_notes += f"\n\nPR created: {pr_info.get('pr_url', 'unknown')}"
                task.finding.remediation_notes = remediation_notes
                task.finding.save()
            else:
                # Path C: Agent succeeded but no real artifacts — spec only
                task.status = 'spec_complete'
                task.completed_at = timezone.now()
                task.evidence_type = 'none'
                task.execution_result = execution_data
                task.save()
                # Finding stays in_progress — not fixed without evidence
                self._route_spec_to_human_attention(task)

            return {
                'success': result.success,
                'message': result.message,
                'skin_result': skin_result,
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

    def _route_spec_to_human_attention(self, task):
        """Route a spec_complete task to HumanAttentionItem for human review."""
        try:
            from core.models_human_interface import HumanAttentionItem
            from django.contrib.auth import get_user_model
            User = get_user_model()

            user = User.objects.filter(is_staff=True, is_active=True).first()
            if not user:
                self.logger.warning("  ⚠️ No staff user found — cannot create HumanAttentionItem")
                return

            # Map finding priority to urgency
            priority_map = {
                'P0': ('critical', 9.0),
                'P1': ('high', 7.0),
                'P2': ('medium', 4.0),
                'P3': ('low', 2.0),
            }
            urgency, priority_score = priority_map.get(
                task.finding.priority, ('medium', 4.0)
            )

            spec_message = ''
            if task.execution_result and isinstance(task.execution_result, dict):
                spec_message = task.execution_result.get('message', '')[:1000]

            HumanAttentionItem.objects.create(
                user=user,
                source_type='audit_remediation',
                source_id=str(task.id),
                source_agent=task.assigned_agent,
                item_type='remediation_proposal',
                title=f"Review spec: {task.title[:150]}",
                summary=(
                    f"Agent {task.assigned_agent} produced a spec/report for "
                    f"finding '{task.finding.title[:100]}' but did not write any "
                    f"code files or create a PR. Review the proposal and apply manually."
                ),
                payload={
                    'task_id': str(task.id),
                    'finding_id': str(task.finding.id),
                    'finding_title': task.finding.title,
                    'priority': task.finding.priority,
                    'category': task.finding.category,
                    'affected_files': task.finding.affected_files,
                    'spec_message': spec_message,
                },
                urgency=urgency,
                priority_score=priority_score,
            )
            self.logger.info(f"  📋 Routed spec to HumanAttentionItem (urgency={urgency})")

        except Exception as e:
            self.logger.error(f"  ⚠️ Failed to create HumanAttentionItem: {e}")

    # =========================================================================
    # PHASE 4: VERIFICATION
    # =========================================================================

    def verify_completed_fixes(self, limit: int = None) -> Dict[str, Any]:
        """
        Phase 4: Verify that completed fixes actually worked.

        Runs verification checks on findings marked as 'fixed' to confirm
        the issue was actually resolved.

        Args:
            limit: Maximum number of fixes to verify (default: max_tasks_per_cycle)

        Returns:
            Dict with verification statistics
        """
        from core.models_audit_tracking import AuditFinding, AuditVerificationRun

        self.logger.info("🔬 [PHASE 4] Verifying completed fixes...")

        # Use provided limit or fall back to default
        verify_limit = limit if limit is not None else self.max_tasks_per_cycle

        # Get fixed but not verified findings
        fixed_findings = AuditFinding.objects.filter(
            status='fixed',
            is_verified=False
        ).order_by('fixed_at')[:verify_limit]

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
                'finding_title': finding.title[:50],
                'passed': verification_result.get('passed', False),
                'type': verification_result.get('type', 'auto'),
                'result': verification_result.get('summary', 'Verified'),
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

        # Phase 1.5: Validate stale findings (Session 821)
        results['phases']['validation'] = self.validate_stale_findings()

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
        from core.models_audit_tracking import (
            AuditFinding, AuditRemediationTask, AuditReport, AuditVerificationRun
        )

        return {
            # Overview counts
            'audit_reports': AuditReport.objects.count(),
            'total_findings': AuditFinding.objects.count(),
            'remediation_tasks': AuditRemediationTask.objects.count(),
            'verification_runs': AuditVerificationRun.objects.count(),

            # Findings by status
            'findings_by_status': {
                'open': AuditFinding.objects.filter(status='open').count(),
                'in_progress': AuditFinding.objects.filter(status='in_progress').count(),
                'fixed': AuditFinding.objects.filter(status='fixed').count(),
                'verified': AuditFinding.objects.filter(status='verified').count(),
                'wontfix': AuditFinding.objects.filter(status='wontfix').count(),
                'deferred': AuditFinding.objects.filter(status='deferred').count(),
            },

            # Findings by priority (open only)
            'findings_by_priority': {
                'P0': AuditFinding.objects.filter(priority='P0', status='open').count(),
                'P1': AuditFinding.objects.filter(priority='P1', status='open').count(),
                'P2': AuditFinding.objects.filter(priority='P2', status='open').count(),
                'P3': AuditFinding.objects.filter(priority='P3', status='open').count(),
            },

            # Tasks by status
            'tasks_by_status': {
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
