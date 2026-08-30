"""
Implementation Verification Service

Wraps agent execution to track REAL changes and provide proof of implementation.
No more agents just giving advice - we verify they actually DO something.
"""

import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from django.utils import timezone

from ai_core.models.implementation_tracking import (
    ImplementationSession,
    FileModification,
    CommandExecution,
    start_implementation_session,
    complete_implementation_session
)


class ImplementationVerifier:
    """Verifies that agents actually implement changes, not just provide advice"""

    def __init__(self, project_root: str = "/Users/donkeyking/Donkey_Betz/unified-donkey-betz"):
        self.project_root = project_root
        self.current_session: Optional[ImplementationSession] = None

    async def execute_with_verification(self, agent_executor, agent_name: str, task: Dict[str, Any], project_id: str, user=None) -> Dict[str, Any]:
        """Execute agent with full implementation verification"""

        # Start implementation tracking
        session = start_implementation_session(
            project_id=project_id,
            agent_name=agent_name,
            task_description=json.dumps(task, indent=2)
        )
        self.current_session = session

        print(f"🔍 Starting implementation verification session {session.id}")
        print(f"📊 Pre-state: Git {session.git_commit_before[:8]}, {len(session.file_tree_before)} files")

        try:
            # Execute the agent with monitoring
            agent_result = await self._execute_with_monitoring(agent_executor, agent_name, task, user)

            # Complete session and analyze changes
            verification_result = complete_implementation_session(session, agent_result.get('output', ''))

            # Generate comprehensive report
            report = self._generate_verification_report(verification_result)

            return {
                **agent_result,
                'verification': {
                    'session_id': session.id,
                    'has_real_changes': verification_result['has_real_changes'],
                    'evidence_count': verification_result['evidence_count'],
                    'changes_verified': verification_result['changes'],
                    'rollback_available': verification_result['rollback_available'],
                    'implementation_report': report
                }
            }

        except Exception as e:
            # Mark session as failed
            session.status = 'failed'
            session.completed_at = timezone.now()
            session.save()

            return {
                'success': False,
                'error': str(e),
                'verification': {
                    'session_id': session.id,
                    'has_real_changes': False,
                    'error': f'Implementation verification failed: {str(e)}'
                }
            }

    async def _execute_with_monitoring(self, agent_executor, agent_name: str, task: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Execute agent while monitoring for actual changes"""

        # Monkey-patch file operations and command execution to track changes
        original_open = open
        original_subprocess_run = subprocess.run

        def tracked_open(filename, mode='r', *args, **kwargs):
            """Track file operations"""
            if 'w' in mode or 'a' in mode:  # Writing to file
                self._track_file_modification(filename, 'before_write')

            result = original_open(filename, mode, *args, **kwargs)

            if 'w' in mode or 'a' in mode:  # Writing to file
                self._track_file_modification(filename, 'after_write')

            return result

        def tracked_subprocess_run(*args, **kwargs):
            """Track command execution"""
            if self.current_session:
                return self._track_command_execution(original_subprocess_run, *args, **kwargs)
            return original_subprocess_run(*args, **kwargs)

        # Apply monitoring patches
        __builtins__['open'] = tracked_open
        subprocess.run = tracked_subprocess_run

        try:
            # Execute the actual agent
            result = await agent_executor.execute_agent(agent_name, task, user)
            return result

        finally:
            # Restore original functions
            __builtins__['open'] = original_open
            subprocess.run = original_subprocess_run

    def _track_file_modification(self, filename: str, stage: str) -> None:
        """Track when files are modified"""
        if not self.current_session:
            return

        try:
            abs_path = os.path.abspath(filename)
            rel_path = os.path.relpath(abs_path, self.project_root)

            # Skip tracking non-project files and temporary files
            if rel_path.startswith('..') or '/tmp/' in rel_path:
                return

            if stage == 'before_write':
                # Record file state before modification
                content_before = ''
                size_before = 0
                if os.path.exists(abs_path):
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as f:
                            content_before = f.read()
                        size_before = os.path.getsize(abs_path)
                    except:
                        pass

                # Store in session cache for later retrieval
                if not hasattr(self.current_session, '_file_cache'):
                    self.current_session._file_cache = {}

                self.current_session._file_cache[rel_path] = {
                    'content_before': content_before,
                    'size_before': size_before,
                    'exists_before': os.path.exists(abs_path)
                }

            elif stage == 'after_write':
                # Record file state after modification
                if hasattr(self.current_session, '_file_cache') and rel_path in self.current_session._file_cache:
                    cache = self.current_session._file_cache[rel_path]

                    content_after = ''
                    size_after = 0
                    exists_after = os.path.exists(abs_path)

                    if exists_after:
                        try:
                            with open(abs_path, 'r', encoding='utf-8') as f:
                                content_after = f.read()
                            size_after = os.path.getsize(abs_path)
                        except:
                            pass

                    # Determine modification type
                    if not cache['exists_before'] and exists_after:
                        mod_type = 'created'
                    elif cache['exists_before'] and not exists_after:
                        mod_type = 'deleted'
                    elif cache['content_before'] != content_after:
                        mod_type = 'modified'
                    else:
                        return  # No real change

                    # Calculate diff
                    diff_output = ''
                    lines_changed = 0
                    if mod_type == 'modified':
                        diff_output = self._generate_file_diff(cache['content_before'], content_after)
                        lines_changed = abs(len(content_after.split('\n')) - len(cache['content_before'].split('\n')))

                    # Record the modification
                    FileModification.objects.create(
                        session=self.current_session,
                        file_path=rel_path,
                        modification_type=mod_type,
                        content_before=cache['content_before'],
                        content_after=content_after,
                        diff_output=diff_output,
                        size_before=cache['size_before'],
                        size_after=size_after,
                        lines_changed=lines_changed
                    )

                    print(f"📝 Tracked file {mod_type}: {rel_path} ({lines_changed} lines changed)")

        except Exception as e:
            print(f"⚠️ Error tracking file modification {filename}: {e}")

    def _track_command_execution(self, original_run, *args, **kwargs) -> subprocess.CompletedProcess:
        """Track command execution with full output capture"""
        if not self.current_session:
            return original_run(*args, **kwargs)

        command_str = ' '.join(args[0]) if isinstance(args[0], list) else str(args[0])
        working_dir = kwargs.get('cwd', os.getcwd())

        # Create command execution record
        cmd_record = CommandExecution.objects.create(
            session=self.current_session,
            command=command_str,
            working_directory=working_dir
        )

        print(f"🔧 Executing command: {command_str}")

        try:
            # Execute with output capture
            if 'capture_output' not in kwargs:
                kwargs['capture_output'] = True
            if 'text' not in kwargs:
                kwargs['text'] = True

            result = original_run(*args, **kwargs)

            # Record results
            cmd_record.completed_at = timezone.now()
            cmd_record.exit_code = result.returncode
            cmd_record.stdout_output = result.stdout if hasattr(result, 'stdout') else ''
            cmd_record.stderr_output = result.stderr if hasattr(result, 'stderr') else ''
            cmd_record.success = result.returncode == 0
            cmd_record.save()

            print(f"✅ Command completed: exit code {result.returncode}")

            return result

        except Exception as e:
            cmd_record.completed_at = timezone.now()
            cmd_record.success = False
            cmd_record.stderr_output = str(e)
            cmd_record.save()

            print(f"❌ Command failed: {e}")
            raise

    def _generate_file_diff(self, before: str, after: str) -> str:
        """Generate diff between file contents"""
        import difflib

        before_lines = before.splitlines(keepends=True)
        after_lines = after.splitlines(keepends=True)

        diff = difflib.unified_diff(
            before_lines,
            after_lines,
            fromfile='before',
            tofile='after',
            lineterm=''
        )

        return ''.join(diff)

    def _generate_verification_report(self, verification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive implementation verification report"""
        session = verification_result['session']
        changes = verification_result['changes']

        report = {
            'session_summary': {
                'id': session.id,
                'agent': session.agent_name,
                'project': session.project_id,
                'duration': str(session.completed_at - session.started_at) if session.completed_at else None,
                'status': session.status
            },
            'implementation_metrics': {
                'files_modified': session.files_modified,
                'lines_added': session.lines_added,
                'lines_removed': session.lines_removed,
                'commands_executed': session.commands_executed,
                'database_changes': session.database_changes
            },
            'evidence_summary': {
                'git_changes': bool(session.git_commit_before != session.git_commit_after),
                'file_modifications': session.file_changes.count(),
                'command_executions': session.commands.count(),
                'database_changes': session.db_changes.count(),
                'total_evidence_items': len(changes['evidence'])
            },
            'change_details': changes['verified_changes'],
            'rollback_info': {
                'available': session.can_rollback,
                'script_length': len(session.rollback_script) if session.rollback_script else 0
            },
            'verification_status': {
                'real_implementation': verification_result['has_real_changes'],
                'evidence_count': verification_result['evidence_count'],
                'confidence': 'high' if verification_result['has_real_changes'] else 'low'
            }
        }

        return report

    def rollback_implementation(self, session_id: int) -> Dict[str, Any]:
        """Rollback implementation changes"""
        try:
            session = ImplementationSession.objects.get(id=session_id)

            if not session.can_rollback or not session.rollback_script:
                return {
                    'success': False,
                    'error': 'No rollback script available for this session'
                }

            # Execute rollback script
            script_path = f'/tmp/rollback_{session_id}.sh'
            with open(script_path, 'w') as f:
                f.write(session.rollback_script)

            os.chmod(script_path, 0o755)

            result = subprocess.run(['/bin/bash', script_path],
                                  capture_output=True, text=True,
                                  cwd=self.project_root)

            if result.returncode == 0:
                session.status = 'rollback'
                session.save()

                return {
                    'success': True,
                    'message': f'Implementation {session_id} rolled back successfully',
                    'output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': f'Rollback failed: {result.stderr}',
                    'exit_code': result.returncode
                }

        except ImplementationSession.DoesNotExist:
            return {
                'success': False,
                'error': 'Implementation session not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Rollback error: {str(e)}'
            }

    def get_implementation_history(self, project_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get implementation history with verification status"""
        query = ImplementationSession.objects.all()

        if project_id:
            query = query.filter(project_id=project_id)

        sessions = query.order_by('-started_at')[:limit]

        history = []
        for session in sessions:
            history.append({
                'id': session.id,
                'agent': session.agent_name,
                'project': session.project_id,
                'started_at': session.started_at.isoformat(),
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'status': session.status,
                'files_modified': session.files_modified,
                'commands_executed': session.commands_executed,
                'has_real_changes': session.files_modified > 0 or session.commands_executed > 0,
                'can_rollback': session.can_rollback
            })

        return history


# Global instance
implementation_verifier = ImplementationVerifier()