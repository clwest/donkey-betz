"""
WorkspaceManager Service - SKIN Layer Central Orchestrator

This is the main interface between agents and the file system.
It manages project workspaces, handles file operations, and maintains
the audit trail for all changes.

Human Body Metaphor:
    This service IS the SKIN - the boundary where AI touches reality.

Session: 695
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from core.models_skin_layer import (
    ProjectWorkspace,
    WorkspaceContext,
    WorkspaceOperation,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class FileWriter:
    """
    Handles safe file writing with rollback support.
    All file operations are logged for audit trail.
    """

    def _sanitize_file_path(self, file_path: str) -> str:
        """
        Session 918: Sanitize file paths to prevent absolute path issues.

        Ensures file_path is always relative, not absolute.
        Strips leading slashes and any /Users/, /home/, /app/ prefixes.
        """
        if not file_path:
            return file_path

        # Convert to Path for easier manipulation
        path = Path(file_path)

        # If it's an absolute path, make it relative
        if path.is_absolute():
            # Get just the parts after common root prefixes
            parts = path.parts

            # Find where the actual relative path starts
            # Skip: /, Users, username, development, project-name, etc.
            skip_prefixes = {'/', 'Users', 'home', 'app', 'var', 'tmp'}
            start_idx = 0
            for i, part in enumerate(parts):
                if part in skip_prefixes or part.startswith('.'):
                    start_idx = i + 1
                elif i > 0 and parts[i-1] == 'Users':
                    # Skip the username after /Users/
                    start_idx = i + 1
                elif i > 0 and parts[i-1] == 'home':
                    # Skip the username after /home/
                    start_idx = i + 1
                elif i > 2 and parts[i-1] == 'development':
                    # Skip project name after /Users/x/development/
                    start_idx = i + 1
                    break
                else:
                    break

            # Reconstruct the relative path
            if start_idx < len(parts):
                file_path = str(Path(*parts[start_idx:]))
            else:
                # Fallback: just use the filename
                file_path = path.name

            logger.warning(
                f"⚠️ Session 918: Converted absolute path to relative: "
                f"{path} -> {file_path}"
            )

        # Remove any leading slashes
        file_path = file_path.lstrip('/')

        return file_path

    def write_file(
        self,
        workspace: ProjectWorkspace,
        file_path: str,
        content: str,
        agent_name: str,
        agent_task: str = ""
    ) -> WorkspaceOperation:
        """
        Write a file with full audit trail.

        Args:
            workspace: Target workspace
            file_path: Relative path from workspace root
            content: Content to write
            agent_name: Which agent is writing
            agent_task: Task description

        Returns:
            WorkspaceOperation record
        """
        start_time = time.time()

        # Session 918: Sanitize file path to prevent absolute path issues
        file_path = self._sanitize_file_path(file_path)

        full_path = Path(workspace.root_path) / file_path

        # Capture before state for rollback
        content_before = ''
        size_before = None
        operation_type = 'file_create'

        if full_path.exists():
            try:
                content_before = full_path.read_text(encoding='utf-8')
                size_before = full_path.stat().st_size
                operation_type = 'file_modify'
            except Exception as e:
                logger.warning(f"Could not read existing file {file_path}: {e}")

        # Create parent directories
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return self._create_failed_operation(
                workspace, agent_name, agent_task, operation_type,
                file_path, f"Failed to create directories: {e}"
            )

        # Write file
        try:
            full_path.write_text(content, encoding='utf-8')
            size_after = full_path.stat().st_size
            success = True
            error = ''
            logger.info(f"✅ Wrote {file_path} ({size_after} bytes)")
        except Exception as e:
            success = False
            error = str(e)
            size_after = None
            logger.error(f"❌ Failed to write {file_path}: {e}")

        execution_time = int((time.time() - start_time) * 1000)

        # Create operation record
        operation = WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name=agent_name,
            agent_task=agent_task,
            operation_type=operation_type,
            file_path=file_path,
            file_content_before=content_before,
            file_content_after=content if success else '',
            file_size_before=size_before,
            file_size_after=size_after,
            success=success,
            error_message=error,
            execution_time_ms=execution_time,
            requires_review=workspace.require_human_review,
        )

        # Update workspace stats
        if success:
            workspace.total_files_written += 1
            workspace.total_operations += 1
            workspace.last_operation_at = timezone.now()
            workspace.save(update_fields=[
                'total_files_written', 'total_operations', 'last_operation_at'
            ])

        return operation

    def delete_file(
        self,
        workspace: ProjectWorkspace,
        file_path: str,
        agent_name: str,
        agent_task: str = ""
    ) -> WorkspaceOperation:
        """Delete a file with audit trail."""
        if not workspace.allow_file_delete:
            return self._create_failed_operation(
                workspace, agent_name, agent_task, 'file_delete',
                file_path, "File deletion not allowed on this workspace"
            )

        start_time = time.time()
        full_path = Path(workspace.root_path) / file_path

        # Capture before state
        content_before = ''
        size_before = None

        if full_path.exists():
            try:
                content_before = full_path.read_text(encoding='utf-8')
                size_before = full_path.stat().st_size
            except Exception:
                pass

            try:
                full_path.unlink()
                success = True
                error = ''
                logger.info(f"🗑️ Deleted {file_path}")
            except Exception as e:
                success = False
                error = str(e)
                logger.error(f"❌ Failed to delete {file_path}: {e}")
        else:
            success = False
            error = "File does not exist"

        execution_time = int((time.time() - start_time) * 1000)

        operation = WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name=agent_name,
            agent_task=agent_task,
            operation_type='file_delete',
            file_path=file_path,
            file_content_before=content_before,
            file_content_after='',
            file_size_before=size_before,
            file_size_after=None,
            success=success,
            error_message=error,
            execution_time_ms=execution_time,
        )

        if success:
            workspace.total_operations += 1
            workspace.last_operation_at = timezone.now()
            workspace.save(update_fields=['total_operations', 'last_operation_at'])

        return operation

    def rollback_operation(self, operation: WorkspaceOperation) -> WorkspaceOperation:
        """
        Rollback a file operation to its previous state.

        Args:
            operation: The operation to rollback

        Returns:
            New WorkspaceOperation record for the rollback
        """
        if not operation.can_rollback:
            raise ValueError("This operation cannot be rolled back")

        if operation.rolled_back:
            raise ValueError("This operation has already been rolled back")

        workspace = operation.workspace
        full_path = Path(workspace.root_path) / operation.file_path

        try:
            if operation.operation_type == 'file_create':
                # Delete the created file
                if full_path.exists():
                    full_path.unlink()
                logger.info(f"⏪ Rolled back file creation: {operation.file_path}")

            elif operation.operation_type == 'file_modify':
                # Restore previous content
                full_path.write_text(operation.file_content_before, encoding='utf-8')
                logger.info(f"⏪ Rolled back file modification: {operation.file_path}")

            elif operation.operation_type == 'file_delete':
                # Recreate the deleted file
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(operation.file_content_before, encoding='utf-8')
                logger.info(f"⏪ Rolled back file deletion: {operation.file_path}")

            success = True
            error = ''

        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"❌ Rollback failed: {e}")

        # Mark original operation as rolled back
        operation.rolled_back = True
        operation.save(update_fields=['rolled_back'])

        # Create rollback operation record
        rollback_op = WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name='system_rollback',
            agent_task=f'Rollback of operation {operation.id}',
            operation_type=operation.operation_type,
            file_path=operation.file_path,
            file_content_before=operation.file_content_after,
            file_content_after=operation.file_content_before,
            success=success,
            error_message=error,
            can_rollback=False,  # Rollbacks can't be rolled back
        )

        operation.rollback_operation = rollback_op
        operation.save(update_fields=['rollback_operation'])

        return rollback_op

    def _create_failed_operation(
        self,
        workspace: ProjectWorkspace,
        agent_name: str,
        agent_task: str,
        operation_type: str,
        file_path: str,
        error: str
    ) -> WorkspaceOperation:
        """Create a failed operation record."""
        return WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name=agent_name,
            agent_task=agent_task,
            operation_type=operation_type,
            file_path=file_path,
            success=False,
            error_message=error,
            can_rollback=False,
        )


class GitIntegrator:
    """Handles git operations on workspaces."""

    def status(self, workspace: ProjectWorkspace) -> Dict[str, Any]:
        """Get git status of the workspace."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=workspace.root_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

            return {
                'success': True,
                'branch': self._get_current_branch(workspace),
                'modified': [l[3:] for l in lines if l.startswith(' M')],
                'added': [l[3:] for l in lines if l.startswith('A ')],
                'untracked': [l[3:] for l in lines if l.startswith('??')],
                'deleted': [l[3:] for l in lines if l.startswith(' D')],
                'staged': [l[3:] for l in lines if l[0] in 'MADRC'],
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Git status timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def commit(
        self,
        workspace: ProjectWorkspace,
        message: str,
        agent_name: str
    ) -> WorkspaceOperation:
        """Create a git commit."""
        if not workspace.allow_git_operations:
            return self._create_git_operation(
                workspace, agent_name, 'git_commit',
                f'git commit -m "{message}"',
                success=False, error="Git operations not allowed"
            )

        start_time = time.time()

        try:
            # Stage all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=workspace.root_path,
                capture_output=True,
                timeout=30
            )

            # Create commit with agent attribution
            full_message = f"{message}\n\n🤖 Generated by {agent_name}"
            result = subprocess.run(
                ['git', 'commit', '-m', full_message],
                cwd=workspace.root_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            if success:
                workspace.total_commits += 1
                workspace.save(update_fields=['total_commits'])
                logger.info(f"✅ Git commit: {message[:50]}...")

        except subprocess.TimeoutExpired:
            success = False
            output = "Git commit timed out"
        except Exception as e:
            success = False
            output = str(e)

        execution_time = int((time.time() - start_time) * 1000)

        return self._create_git_operation(
            workspace, agent_name, 'git_commit',
            f'git commit -m "{message}"',
            success=success,
            output=output,
            exit_code=result.returncode if 'result' in locals() else -1,
            execution_time=execution_time
        )

    def create_branch(
        self,
        workspace: ProjectWorkspace,
        branch_name: str,
        agent_name: str = "workspace_manager"
    ) -> WorkspaceOperation:
        """Create and switch to a new branch."""
        if not workspace.allow_git_operations:
            return self._create_git_operation(
                workspace, agent_name, 'git_branch',
                f'git checkout -b {branch_name}',
                success=False, error="Git operations not allowed"
            )

        start_time = time.time()

        try:
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=workspace.root_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            if success:
                workspace.current_branch = branch_name
                workspace.save(update_fields=['current_branch'])
                logger.info(f"✅ Created branch: {branch_name}")

        except subprocess.TimeoutExpired:
            success = False
            output = "Git branch creation timed out"
        except Exception as e:
            success = False
            output = str(e)

        execution_time = int((time.time() - start_time) * 1000)

        return self._create_git_operation(
            workspace, agent_name, 'git_branch',
            f'git checkout -b {branch_name}',
            success=success,
            output=output,
            exit_code=result.returncode if 'result' in locals() else -1,
            execution_time=execution_time
        )

    def _get_current_branch(self, workspace: ProjectWorkspace) -> str:
        """Get the current git branch."""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=workspace.root_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except Exception:
            return 'unknown'

    def _create_git_operation(
        self,
        workspace: ProjectWorkspace,
        agent_name: str,
        operation_type: str,
        command: str,
        success: bool = False,
        output: str = '',
        error: str = '',
        exit_code: int = -1,
        execution_time: int = 0
    ) -> WorkspaceOperation:
        """Create a git operation record."""
        workspace.total_operations += 1
        workspace.last_operation_at = timezone.now()
        workspace.save(update_fields=['total_operations', 'last_operation_at'])

        return WorkspaceOperation.objects.create(
            workspace=workspace,
            user=workspace.user,
            agent_name=agent_name,
            operation_type=operation_type,
            command=command,
            command_output=output,
            command_error=error if not success else '',
            exit_code=exit_code,
            success=success,
            error_message=error if not success else '',
            execution_time_ms=execution_time,
            can_rollback=False,  # Git operations can't be easily rolled back
        )


class WorkspaceScanner:
    """Scans and analyzes project structure."""

    # Directories to always skip
    SKIP_DIRS = {
        'node_modules', '__pycache__', '.git', '.venv', 'venv',
        '.idea', '.vscode', 'dist', 'build', '.next', '.nuxt',
        'coverage', '.pytest_cache', '.mypy_cache', 'eggs',
        '*.egg-info', '.tox', '.cache'
    }

    # File extensions to count
    CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.vue', '.svelte',
        '.html', '.css', '.scss', '.sass', '.less',
        '.json', '.yaml', '.yml', '.toml', '.md',
        '.sql', '.graphql', '.prisma'
    }

    # ── Self-healing clone for git_remote workspaces ────────────────────

    CLONE_TIMEOUT = 120  # seconds
    STALE_LOCK_TTL_SECONDS = 600  # 10 minutes

    def _get_workspace_paths(self, workspace: ProjectWorkspace) -> tuple:
        """Return (base_path, ws_dir, repo_dir, lock_path) for a workspace."""
        from django.conf import settings
        debug = getattr(settings, 'DEBUG', False)

        base_dir = os.environ.get('WORKSPACE_BASE_DIR', '/app/workspaces')
        base_path = Path(base_dir)

        if not base_path.exists():
            try:
                base_path.mkdir(parents=True, exist_ok=True)
            except OSError:
                if debug:
                    base_path = Path('/tmp/workspaces')
                    base_path.mkdir(parents=True, exist_ok=True)
                else:
                    raise ValueError(
                        f"WORKSPACE_BASE_DIR ({base_dir}) is not writable. "
                        "Configure a Railway volume at /app/workspaces."
                    )

        # Verify write access (Railway volumes mount as root:root)
        if not os.access(str(base_path), os.W_OK):
            if debug:
                base_path = Path('/tmp/workspaces')
                base_path.mkdir(parents=True, exist_ok=True)
            else:
                raise ValueError(
                    f"WORKSPACE_BASE_DIR ({base_dir}) exists but is not writable "
                    f"by the current process (uid={os.getuid()}). "
                    "Fix volume permissions: chown appuser:appuser /app/workspaces"
                )

        ws_dir = base_path / str(workspace.id)
        repo_dir = ws_dir / 'repo'
        lock_path = ws_dir / '.clone.lock'
        return base_path, ws_dir, repo_dir, lock_path

    def _is_repo_ready(self, repo_dir: Path, ws_dir: Path) -> bool:
        """Check if repo is cloned and no clone is in progress."""
        return (
            repo_dir.exists()
            and (repo_dir / '.git').exists()
            and not (ws_dir / '.clone.in_progress').exists()
        )

    def _cleanup_stale_lock(self, ws_dir: Path, lock_path: Path) -> bool:
        """Remove stale lock + in_progress if older than TTL. Returns True if cleaned."""
        in_progress = ws_dir / '.clone.in_progress'
        if not in_progress.exists():
            # Lock exists but no sentinel — stale, clean it
            logger.warning(f"🔒 Stale clone lock (no sentinel): {lock_path}")
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass
            return True

        try:
            import json
            data = json.loads(in_progress.read_text())
            from datetime import datetime, timezone
            started = datetime.fromisoformat(data['started_at'])
            age = (datetime.now(timezone.utc) - started).total_seconds()
            if age > self.STALE_LOCK_TTL_SECONDS:
                logger.warning(
                    f"🔒 Stale clone lock ({age:.0f}s old, TTL={self.STALE_LOCK_TTL_SECONDS}s): {lock_path}"
                )
                lock_path.unlink(missing_ok=True)
                in_progress.unlink(missing_ok=True)
                return True
        except Exception:
            # Can't parse sentinel — treat as stale
            logger.warning(f"🔒 Unparseable clone sentinel, cleaning: {lock_path}")
            lock_path.unlink(missing_ok=True)
            in_progress.unlink(missing_ok=True)
            return True
        return False

    def _write_sentinel(self, ws_dir: Path, name: str, data: dict) -> None:
        """Write a JSON sentinel file."""
        import json
        path = ws_dir / name
        path.write_text(json.dumps(data, default=str))

    def _remove_sentinel(self, ws_dir: Path, name: str) -> None:
        """Remove a sentinel file if it exists."""
        try:
            (ws_dir / name).unlink(missing_ok=True)
        except OSError:
            pass

    def ensure_repo_present(self, workspace: ProjectWorkspace) -> None:
        """
        Ensure a git_remote workspace has its repo on disk.

        If the repo directory is missing (e.g. after a Railway deploy with
        ephemeral filesystem), reclone from git_remote_url into the
        canonical path: <WORKSPACE_BASE_DIR>/<workspace_uuid>/repo.
        Updates workspace.root_path on success.
        """
        if workspace.workspace_type != 'git_remote':
            return

        if not workspace.git_remote_url:
            raise ValueError(
                "Workspace is type 'git_remote' but has no git_remote_url. "
                "Update the workspace with a valid Git URL."
            )

        if not workspace.allow_git_operations:
            raise ValueError(
                "Git operations are disabled for this workspace."
            )

        root = Path(workspace.root_path)
        if root.exists() and root.is_dir() and (root / '.git').exists():
            return  # repo already present

        _, ws_dir, repo_dir, lock_path = self._get_workspace_paths(workspace)
        ws_dir.mkdir(parents=True, exist_ok=True)

        if self._is_repo_ready(repo_dir, ws_dir):
            # Repo exists at canonical path but root_path was stale — fix it
            workspace.root_path = str(repo_dir)
            workspace.save(update_fields=['root_path'])
            logger.info(
                f"📂 Workspace {workspace.name}: updated stale root_path "
                f"to canonical {repo_dir}"
            )
            return

        # Auto-clean invalid repo dir (exists but no .git)
        if repo_dir.exists() and not (repo_dir / '.git').exists():
            import shutil
            logger.warning(f"🧹 Removing invalid repo dir (no .git): {repo_dir}")
            shutil.rmtree(repo_dir, ignore_errors=True)

        # Acquire clone lock (prevent concurrent clones)
        lock_fd = None
        try:
            lock_fd = os.open(
                str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY
            )
        except FileExistsError:
            # Check for stale lock
            if self._cleanup_stale_lock(ws_dir, lock_path):
                try:
                    lock_fd = os.open(
                        str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY
                    )
                except FileExistsError:
                    raise ValueError(
                        "A clone operation is already in progress for this workspace. "
                        "Please retry in a few minutes."
                    )
            else:
                raise ValueError(
                    "A clone operation is already in progress for this workspace. "
                    "Please retry in a few minutes."
                )

        try:
            # Write clone-in-progress sentinel
            from datetime import datetime, timezone
            self._write_sentinel(ws_dir, '.clone.in_progress', {
                'workspace_id': str(workspace.id),
                'started_at': datetime.now(timezone.utc).isoformat(),
                'repo_dir': str(repo_dir),
                'git_remote_url': workspace.git_remote_url,
                'pid': os.getpid(),
            })

            # Inject GitHub token for private repos
            clone_url = workspace.git_remote_url
            github_token = os.environ.get('GITHUB_TOKEN', '')
            if github_token:
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(clone_url)
                if parsed.hostname == 'github.com' and parsed.scheme == 'https':
                    authed = parsed._replace(
                        netloc=f'x-access-token:{github_token}@{parsed.hostname}'
                        + (f':{parsed.port}' if parsed.port else '')
                    )
                    clone_url = urlunparse(authed)

            # Build clone command
            branch = workspace.current_branch or None
            cmd = ['git', 'clone', '--depth', '1']
            if branch:
                cmd += ['--branch', branch, '--single-branch']
            cmd += [clone_url, str(repo_dir)]

            logger.info(
                f"📥 Cloning {workspace.git_remote_url} → {repo_dir}"
                + (" (with GITHUB_TOKEN)" if github_token else "")
            )
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.CLONE_TIMEOUT,
            )

            if result.returncode != 0:
                stderr_tail = (result.stderr or '')[-2048:]
                # Clean up partial clone
                import shutil
                if repo_dir.exists():
                    shutil.rmtree(repo_dir, ignore_errors=True)
                self._write_sentinel(ws_dir, '.clone.error', {
                    'error': stderr_tail,
                    'git_remote_url': workspace.git_remote_url,
                })
                self._remove_sentinel(ws_dir, '.clone.in_progress')
                raise ValueError(
                    f"Failed to clone {workspace.git_remote_url}: "
                    f"{stderr_tail}"
                )

            # Success — write .clone.ok, remove .clone.in_progress
            head_sha = ''
            try:
                head_sha = subprocess.run(
                    ['git', '-C', str(repo_dir), 'rev-parse', 'HEAD'],
                    capture_output=True, text=True, timeout=5,
                ).stdout.strip()
            except Exception:
                pass

            self._write_sentinel(ws_dir, '.clone.ok', {
                'ok_at': datetime.now(timezone.utc).isoformat(),
                'head_sha': head_sha,
            })
            self._remove_sentinel(ws_dir, '.clone.in_progress')

            # Update workspace root_path to canonical location
            workspace.root_path = str(repo_dir)
            workspace.save(update_fields=['root_path'])
            logger.info(
                f"✅ Cloned {workspace.name} to {repo_dir}, "
                f"root_path updated"
            )

        except subprocess.TimeoutExpired:
            import shutil
            if repo_dir.exists():
                shutil.rmtree(repo_dir, ignore_errors=True)
            self._write_sentinel(ws_dir, '.clone.error', {
                'error': f'Timed out after {self.CLONE_TIMEOUT}s',
                'git_remote_url': workspace.git_remote_url,
            })
            self._remove_sentinel(ws_dir, '.clone.in_progress')
            raise ValueError(
                f"Git clone timed out after {self.CLONE_TIMEOUT}s. "
                "The repository may be too large for shallow clone."
            )
        finally:
            # Release lock
            if lock_fd is not None:
                os.close(lock_fd)
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass

    def ensure_repo_present_or_wait(
        self,
        workspace: ProjectWorkspace,
        wait_seconds: float = 20.0,
        poll_interval: float = 0.5,
    ) -> dict:
        """
        Ensure repo is present, waiting up to wait_seconds for a concurrent clone.

        Returns:
            {'ready': True} if repo is ready to scan.
            {'ready': False, 'clone_started_at': <str|None>} if still cloning.
        Raises on hard clone failure or validation errors.
        """
        if workspace.workspace_type != 'git_remote':
            return {'ready': True}

        if not workspace.git_remote_url or not workspace.allow_git_operations:
            # Let ensure_repo_present raise the appropriate error
            self.ensure_repo_present(workspace)
            return {'ready': True}

        root = Path(workspace.root_path)
        if root.exists() and root.is_dir() and (root / '.git').exists():
            return {'ready': True}

        _, ws_dir, repo_dir, lock_path = self._get_workspace_paths(workspace)
        ws_dir.mkdir(parents=True, exist_ok=True)

        if self._is_repo_ready(repo_dir, ws_dir):
            # Fix stale root_path
            workspace.root_path = str(repo_dir)
            workspace.save(update_fields=['root_path'])
            return {'ready': True}

        # Try to acquire lock — if we get it, we do the clone inline
        lock_fd = None
        try:
            lock_fd = os.open(
                str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY
            )
        except FileExistsError:
            # Someone else is cloning — check for stale lock
            if self._cleanup_stale_lock(ws_dir, lock_path):
                try:
                    lock_fd = os.open(
                        str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY
                    )
                except FileExistsError:
                    lock_fd = None
            else:
                lock_fd = None

        if lock_fd is not None:
            # We own the lock — release it and let ensure_repo_present do the clone
            os.close(lock_fd)
            try:
                lock_path.unlink(missing_ok=True)
            except OSError:
                pass
            self.ensure_repo_present(workspace)
            return {'ready': True}

        # Another process is cloning — poll for readiness
        import time as _time
        elapsed = 0.0
        while elapsed < wait_seconds:
            _time.sleep(poll_interval)
            elapsed += poll_interval
            if self._is_repo_ready(repo_dir, ws_dir):
                # Clone finished while we waited — fix root_path
                workspace.refresh_from_db()
                return {'ready': True}

        # Still not ready after waiting — return 202 info
        clone_started_at = None
        in_progress = ws_dir / '.clone.in_progress'
        if in_progress.exists():
            try:
                import json
                data = json.loads(in_progress.read_text())
                clone_started_at = data.get('started_at')
            except Exception:
                pass

        return {'ready': False, 'clone_started_at': clone_started_at}

    # ── Scan ──────────────────────────────────────────────────────────

    def scan_workspace(
        self,
        workspace: ProjectWorkspace,
        max_depth: int = 5
    ) -> WorkspaceContext:
        """
        Scan workspace and create/update WorkspaceContext.

        For git_remote workspaces, auto-clones the repo if missing.

        Args:
            workspace: The workspace to scan
            max_depth: How deep to scan directories

        Returns:
            Updated WorkspaceContext
        """
        # Self-heal: ensure git_remote repos are cloned
        self.ensure_repo_present(workspace)

        start_time = time.time()
        root = Path(workspace.root_path)

        if not root.exists() or not root.is_dir():
            raise ValueError(
                f"Workspace path not found on server: {workspace.root_path}. "
                "This workspace may have been registered with a local path; "
                "register using a server-side clone or update root_path."
            )

        file_tree = {}
        key_files = {}
        file_type_counts = {}
        total_files = 0
        total_directories = 0
        total_lines = 0

        def should_skip(path: Path) -> bool:
            """Check if path should be skipped."""
            return any(
                part in self.SKIP_DIRS or part.startswith('.')
                for part in path.parts
            )

        def scan_directory(path: Path, depth: int = 0):
            nonlocal total_files, total_directories, total_lines

            if depth > max_depth:
                return

            try:
                for item in path.iterdir():
                    rel_path = item.relative_to(root)

                    if should_skip(rel_path):
                        continue

                    if item.is_dir():
                        total_directories += 1
                        scan_directory(item, depth + 1)

                    elif item.is_file():
                        total_files += 1
                        dir_path = str(rel_path.parent)
                        filename = rel_path.name

                        # Build file tree
                        if dir_path not in file_tree:
                            file_tree[dir_path] = []
                        file_tree[dir_path].append(filename)

                        # Count file types
                        ext = item.suffix.lower()
                        if ext:
                            file_type_counts[ext] = file_type_counts.get(ext, 0) + 1

                        # Count lines for code files
                        if ext in self.CODE_EXTENSIONS:
                            try:
                                content = item.read_text(encoding='utf-8', errors='ignore')
                                total_lines += len(content.split('\n'))
                            except Exception:
                                pass

                        # Identify key files
                        self._identify_key_file(rel_path, key_files)

            except (PermissionError, FileNotFoundError, NotADirectoryError):
                pass

        scan_directory(root)

        # Detect tech stack
        tech_stack = self._detect_tech_stack(root, file_tree)

        # Update workspace tech stack if not set
        if not workspace.tech_stack:
            workspace.tech_stack = tech_stack
            workspace.save(update_fields=['tech_stack'])

        # Detect coding patterns
        coding_patterns = self._detect_coding_patterns(file_tree, key_files)

        # Detect dependencies
        dependencies = self._detect_dependencies(root)

        # Detect import aliases
        import_aliases = self._detect_import_aliases(root)

        # Infer directory purposes
        directory_purposes = self._infer_directory_purposes(file_tree)

        scan_duration = int((time.time() - start_time) * 1000)

        # Create or update context
        context, created = WorkspaceContext.objects.update_or_create(
            workspace=workspace,
            defaults={
                'file_tree': file_tree,
                'key_files': key_files,
                'coding_patterns': coding_patterns,
                'dependencies': dependencies,
                'import_aliases': import_aliases,
                'directory_purposes': directory_purposes,
                'total_files': total_files,
                'total_directories': total_directories,
                'total_lines_of_code': total_lines,
                'file_type_counts': file_type_counts,
                'scan_depth': max_depth,
                'scan_duration_ms': scan_duration,
                'excluded_patterns': list(self.SKIP_DIRS),
            }
        )

        action = "Created" if created else "Updated"
        logger.info(
            f"📊 {action} workspace context: {total_files} files, "
            f"{total_directories} dirs, {total_lines} lines ({scan_duration}ms)"
        )

        return context

    def _identify_key_file(self, rel_path: Path, key_files: Dict[str, str]):
        """Identify if a file is a key file."""
        name = rel_path.name.lower()
        path_str = str(rel_path)

        # Entry points
        if name in ('app.tsx', 'app.jsx', 'app.js', 'main.tsx', 'main.ts'):
            key_files['main_entry'] = path_str
        elif name in ('index.tsx', 'index.jsx') and 'pages' not in path_str:
            if 'main_entry' not in key_files:
                key_files['main_entry'] = path_str

        # Routes
        if name in ('routes.tsx', 'router.tsx', 'routes.ts', 'router.ts'):
            key_files['routes'] = path_str
        elif 'app/routes' in path_str.lower() or 'pages' in path_str.lower():
            if 'routes_dir' not in key_files:
                key_files['routes_dir'] = str(rel_path.parent)

        # Django files
        if name == 'urls.py':
            key_files['urls'] = path_str
        elif name == 'models.py' and 'migrations' not in path_str:
            if 'models' not in key_files:
                key_files['models'] = path_str
        elif name == 'settings.py':
            key_files['settings'] = path_str
        elif name == 'views.py':
            if 'views' not in key_files:
                key_files['views'] = path_str

        # API client
        if name in ('client.ts', 'api.ts', 'client.js', 'api.js'):
            if 'api' in path_str.lower():
                key_files['api_client'] = path_str

        # Config files
        if name == 'package.json':
            key_files['package_json'] = path_str
        elif name in ('tsconfig.json', 'jsconfig.json'):
            key_files['tsconfig'] = path_str
        elif name == 'tailwind.config.js' or name == 'tailwind.config.ts':
            key_files['tailwind_config'] = path_str
        elif name == 'requirements.txt':
            key_files['requirements'] = path_str
        elif name == 'pyproject.toml':
            key_files['pyproject'] = path_str

        # Infrastructure files
        if name == 'procfile':
            key_files['procfile'] = path_str
        elif name == 'makefile':
            key_files['makefile'] = path_str
        elif name in ('docker-compose.yml', 'docker-compose.yaml'):
            key_files['docker_compose'] = path_str
        elif name == 'dockerfile':
            key_files['dockerfile'] = path_str

        # Session/project docs
        if name == 'claude.md':
            key_files['claude_md'] = path_str
        elif name.startswith('00-start-'):
            key_files['session_entry'] = path_str

        # Agent system files
        if name == 'base_agent.py' and 'agents' in path_str:
            key_files['base_agent'] = path_str
        elif name == 'agent_router.py':
            key_files['agent_router'] = path_str
        elif name.endswith('_agent.py') and 'agents' in path_str:
            # Count agent files
            count = int(key_files.get('agent_file_count', '0')) + 1
            key_files['agent_file_count'] = str(count)
            if count == 1:
                key_files['agent_example'] = path_str

        # Service layer files
        if name == 'tasks.py' and 'migrations' not in path_str:
            key_files['celery_tasks'] = path_str
        elif name == 'tool_dispatcher.py':
            key_files['tool_dispatcher'] = path_str
        elif name == 'unified_pa_entrypoint.py':
            key_files['pa_entrypoint'] = path_str

        # Celery config
        if name == 'celery.py' and 'migrations' not in path_str:
            key_files['celery_config'] = path_str

    def _detect_tech_stack(
        self,
        root: Path,
        file_tree: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Auto-detect the tech stack of a project."""
        tech_stack = {}

        # Check package.json (fallback to frontend/ subdirectory)
        package_json = root / 'package.json'
        if not package_json.exists():
            package_json = root / 'frontend' / 'package.json'
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text())
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

                if 'react' in deps or 'react-dom' in deps:
                    tech_stack['frontend'] = 'react'
                elif 'vue' in deps:
                    tech_stack['frontend'] = 'vue'
                elif 'svelte' in deps:
                    tech_stack['frontend'] = 'svelte'
                elif 'next' in deps:
                    tech_stack['frontend'] = 'nextjs'
                elif '@angular/core' in deps:
                    tech_stack['frontend'] = 'angular'

                if 'express' in deps:
                    tech_stack['backend_js'] = 'express'
                elif 'fastify' in deps:
                    tech_stack['backend_js'] = 'fastify'
                elif 'nestjs' in deps or '@nestjs/core' in deps:
                    tech_stack['backend_js'] = 'nestjs'

                if 'tailwindcss' in deps:
                    tech_stack['styling'] = 'tailwind'
                elif 'styled-components' in deps:
                    tech_stack['styling'] = 'styled-components'

                if 'typescript' in deps:
                    tech_stack['language'] = 'typescript'

            except Exception:
                pass

        # Check Python
        if (root / 'manage.py').exists():
            tech_stack['backend'] = 'django'

        # Parse requirements.txt for framework and infrastructure libs
        requirements_file = root / 'requirements.txt'
        if requirements_file.exists():
            try:
                reqs = requirements_file.read_text().lower()
                if 'backend' not in tech_stack:
                    if 'django' in reqs:
                        tech_stack['backend'] = 'django'
                    elif 'fastapi' in reqs:
                        tech_stack['backend'] = 'fastapi'
                    elif 'flask' in reqs:
                        tech_stack['backend'] = 'flask'

                # Infrastructure libs
                infra_map = {
                    'celery': ('task_queue', 'celery'),
                    'redis': ('cache', 'redis'),
                    'scrapy': ('scraping', 'scrapy'),
                    'pgvector': ('vector_db', 'pgvector'),
                    'channels': ('websockets', 'django-channels'),
                    'daphne': ('asgi_server', 'daphne'),
                    'sentence-transformers': ('embeddings', 'sentence-transformers'),
                    'psycopg': ('database', 'postgresql'),
                    'djangorestframework': ('api_framework', 'django-rest-framework'),
                }
                for lib, (key, value) in infra_map.items():
                    if lib in reqs and key not in tech_stack:
                        tech_stack[key] = value
            except Exception:
                pass

        # Check for databases via docker-compose
        if (root / 'docker-compose.yml').exists() or (root / 'docker-compose.yaml').exists():
            tech_stack['containerization'] = 'docker'
            try:
                compose_file = root / 'docker-compose.yml'
                if not compose_file.exists():
                    compose_file = root / 'docker-compose.yaml'
                compose = compose_file.read_text().lower()
                if 'postgres' in compose:
                    tech_stack['database'] = 'postgresql'
                elif 'mysql' in compose:
                    tech_stack['database'] = 'mysql'
                elif 'mongo' in compose:
                    tech_stack['database'] = 'mongodb'
                if 'redis' in compose and 'cache' not in tech_stack:
                    tech_stack['cache'] = 'redis'
            except Exception:
                pass

        # Check Procfile for worker/server detection
        procfile = root / 'Procfile'
        if procfile.exists():
            try:
                proc_content = procfile.read_text().lower()
                if 'daphne' in proc_content and 'asgi_server' not in tech_stack:
                    tech_stack['asgi_server'] = 'daphne'
                if 'celery' in proc_content and 'task_queue' not in tech_stack:
                    tech_stack['task_queue'] = 'celery'
                tech_stack['deployment'] = 'procfile'
            except Exception:
                pass

        return tech_stack

    def _detect_coding_patterns(
        self,
        file_tree: Dict[str, List[str]],
        key_files: Dict[str, str]
    ) -> Dict[str, str]:
        """Detect coding patterns used in the project."""
        patterns = {}

        agent_files = 0
        service_dirs = 0
        spider_files = 0
        task_files = 0
        serializer_files = 0
        model_split_files = 0

        # Check for component patterns
        for dir_path, files in file_tree.items():
            tsx_files = [f for f in files if f.endswith('.tsx')]

            if tsx_files and 'components' in dir_path.lower():
                # Check naming convention
                pascal_case = sum(1 for f in tsx_files if f[0].isupper())
                if pascal_case > len(tsx_files) / 2:
                    patterns['component_naming'] = 'PascalCase'

            if 'hooks' in dir_path.lower():
                hook_files = [f for f in files if f.startswith('use')]
                if hook_files:
                    patterns['hook_pattern'] = 'use*.ts in hooks/'

            # Agent pattern: *_agent.py files in agents/ dirs
            dir_name = Path(dir_path).name.lower()
            if dir_name == 'agents':
                agent_files += sum(1 for f in files if f.endswith('_agent.py'))

            # Service layer: services/ dirs with many .py files
            if dir_name == 'services':
                py_count = sum(1 for f in files if f.endswith('.py'))
                if py_count > 10:
                    service_dirs += 1

            # Spider pattern
            if dir_name == 'spiders':
                spider_files += sum(1 for f in files if f.endswith('.py') and f != '__init__.py')

            # Celery tasks: tasks.py files outside migrations
            if 'migrations' not in dir_path:
                task_files += sum(1 for f in files if f == 'tasks.py')

            # DRF serializers
            serializer_files += sum(1 for f in files if 'serializer' in f.lower() and f.endswith('.py'))

            # Model split pattern: models_*.py files
            model_split_files += sum(1 for f in files if f.startswith('models_') and f.endswith('.py'))

        # Check for test patterns
        for dir_path, files in file_tree.items():
            test_files = [f for f in files if 'test' in f.lower() or 'spec' in f.lower()]
            if test_files:
                if any(f.startswith('test_') for f in test_files):
                    patterns['test_pattern'] = 'test_*.py (pytest style)'
                elif any('.test.' in f or '.spec.' in f for f in test_files):
                    patterns['test_pattern'] = '*.test.ts/*.spec.ts (Jest style)'
                break

        # Record detected patterns
        if agent_files > 0:
            patterns['agent_pattern'] = f'{agent_files} *_agent.py files in agents/ dirs'
        if service_dirs > 0:
            patterns['service_layer'] = f'{service_dirs} services/ dir(s) with 10+ Python files'
        if spider_files > 0:
            patterns['spider_pattern'] = f'{spider_files} spider files in spiders/ dirs'
        if task_files > 0:
            patterns['celery_tasks'] = f'{task_files} tasks.py file(s) for background processing'
        if serializer_files > 0:
            patterns['drf_serializers'] = f'{serializer_files} serializer file(s) (Django REST Framework)'
        if model_split_files > 0:
            patterns['model_organization'] = f'{model_split_files} models_*.py files (split model pattern)'

        return patterns

    def _detect_dependencies(self, root: Path) -> Dict[str, Dict[str, str]]:
        """Detect project dependencies."""
        dependencies = {}

        # Frontend dependencies
        package_json = root / 'package.json'
        if package_json.exists():
            try:
                pkg = json.loads(package_json.read_text())
                deps = pkg.get('dependencies', {})
                # Get top 10 most important deps
                important_deps = {
                    k: v for k, v in list(deps.items())[:10]
                }
                if important_deps:
                    dependencies['frontend'] = important_deps
            except Exception:
                pass

        # Python dependencies
        requirements = root / 'requirements.txt'
        if requirements.exists():
            try:
                lines = requirements.read_text().strip().split('\n')
                py_deps = {}
                for line in lines[:10]:  # Top 10
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split('==')
                        name = parts[0].split('>=')[0].split('<=')[0].strip()
                        version = parts[1] if len(parts) > 1 else 'latest'
                        py_deps[name] = version
                if py_deps:
                    dependencies['backend'] = py_deps
            except Exception:
                pass

        return dependencies

    def _detect_import_aliases(self, root: Path) -> Dict[str, str]:
        """Detect import aliases from tsconfig/jsconfig."""
        aliases = {}

        for config_name in ['tsconfig.json', 'jsconfig.json']:
            config_path = root / config_name
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text())
                    paths = config.get('compilerOptions', {}).get('paths', {})
                    base_url = config.get('compilerOptions', {}).get('baseUrl', '.')

                    for alias, targets in paths.items():
                        # Remove wildcard
                        clean_alias = alias.rstrip('/*')
                        if targets:
                            clean_target = targets[0].rstrip('/*')
                            aliases[clean_alias] = clean_target

                except Exception:
                    pass

        return aliases

    def _infer_directory_purposes(
        self,
        file_tree: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Infer the purpose of each directory."""
        purposes = {}

        # Full-path matching (most specific, checked first)
        path_purpose_map = {
            'core/agents': 'AI agent implementations (routable agents)',
            'core/services': 'Business logic services (134+ service classes)',
            'core/management/commands': 'Django management commands',
            'core/management': 'Django management module',
            'core/migrations': 'Core app database migrations',
            'core/templatetags': 'Django custom template tags',
            'ai_core/spiders': 'Data collection spiders (Scrapy)',
            'ai_core/intelligence': 'AI intelligence services (learning loop, shared memory)',
            'ai_core/migrations': 'AI core database migrations',
            'docs/topics': 'Embedding-optimized subsystem documentation',
            'docs/handoffs': 'Session handoff documents (build history)',
            'frontend/src': 'Frontend source code (React/TypeScript)',
            'frontend/src/pages': 'Route page components',
            'frontend/src/components': 'Reusable UI components',
            'frontend/src/hooks': 'Custom React hooks',
            'frontend/src/api': 'API client and endpoints',
            'frontend/src/types': 'TypeScript type definitions',
            'frontend/src/styles': 'CSS/SCSS stylesheets',
            'frontend/src/store': 'State management',
            'frontend/src/context': 'React context providers',
            'frontend/src/assets': 'Static assets (images, fonts)',
            'intelligence': 'Intelligence subsystem (opportunities, action plans)',
            'intelligence/migrations': 'Intelligence app database migrations',
            'ml': 'Machine learning models and training',
            'ml/migrations': 'ML app database migrations',
            'sports': 'Sports betting predictions and analytics',
            'sports/migrations': 'Sports app database migrations',
            'persistence': 'Legacy persistence layer',
            'persistence/migrations': 'Persistence app database migrations',
            'generated_content': 'Agent-generated output files',
        }

        # Leaf-name matching (less specific, fallback)
        purpose_map = {
            'components': 'Reusable UI components',
            'pages': 'Route page components',
            'views': 'Django views or page components',
            'hooks': 'Custom React hooks',
            'utils': 'Utility functions',
            'lib': 'Library code and utilities',
            'services': 'Business logic services',
            'api': 'API client and endpoints',
            'models': 'Data models',
            'store': 'State management (Redux/Zustand)',
            'context': 'React context providers',
            'types': 'TypeScript type definitions',
            'styles': 'CSS/SCSS stylesheets',
            'assets': 'Static assets (images, fonts)',
            'tests': 'Test files',
            '__tests__': 'Test files',
            'migrations': 'Database migrations',
            'templates': 'HTML templates',
            'agents': 'AI agent implementations',
            'spiders': 'Data collection spiders',
            'management': 'Django management module',
            'commands': 'Django management commands',
            'middleware': 'Django/Express middleware',
            'serializers': 'DRF serializers',
            'fixtures': 'Test/seed data fixtures',
            'advisors': 'AI advisor implementations',
            'blockchain': 'Blockchain integration',
            'security': 'Security utilities',
            'narrative': 'Narrative/story generation',
            'podcast': 'Podcast generation',
            'static': 'Static files served by web server',
            'media': 'User-uploaded media files',
            'locale': 'Internationalization translations',
            'docs': 'Documentation',
            'scripts': 'Utility scripts',
            'config': 'Configuration files',
            'deploy': 'Deployment configuration',
            'logs': 'Log files',
        }

        for dir_path in file_tree.keys():
            # Normalize to forward slashes for matching
            normalized = dir_path.replace('\\', '/')

            # Try full-path match first (more specific)
            matched = False
            for path_key, purpose in path_purpose_map.items():
                if normalized == path_key:
                    purposes[dir_path] = purpose
                    matched = True
                    break

            if matched:
                continue

            # Fall back to leaf-name exact match
            dir_name = Path(dir_path).name.lower()
            for key, purpose in purpose_map.items():
                if dir_name == key:
                    purposes[dir_path] = purpose
                    break

        return purposes


class WorkspaceManager:
    """
    Central service for managing project workspaces.
    This is the main interface between agents and the file system.

    Usage:
        manager = WorkspaceManager(user)
        workspace = manager.register_workspace('/path/to/project')
        manager.set_active_workspace(workspace.id)

        # Later, when an agent generates code:
        result = manager.execute_agent_output(
            workspace=workspace,
            agent_name='FullStackDeveloperAgent',
            agent_result={'files': [...]},
            auto_apply=True
        )
    """

    def __init__(self, user: User):
        self.user = user
        self.file_writer = FileWriter()
        self.git_integrator = GitIntegrator()
        self.scanner = WorkspaceScanner()

    # ==================== Workspace Management ====================

    def register_workspace(
        self,
        root_path: str,
        name: str = None,
        set_active: bool = True
    ) -> ProjectWorkspace:
        """
        Register an existing project directory as a workspace.
        Scans and understands the project structure.

        Args:
            root_path: Path to the project directory
            name: Optional name (defaults to directory name)
            set_active: Whether to set this as the active workspace

        Returns:
            Created ProjectWorkspace
        """
        path = Path(root_path).resolve()

        if not path.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")

        # Check if already registered
        existing = ProjectWorkspace.objects.filter(
            user=self.user,
            root_path=str(path)
        ).first()

        if existing:
            logger.info(f"Workspace already registered: {existing.name}")
            if set_active:
                self.set_active_workspace(existing.id)
            return existing

        # Detect git remote if available
        git_remote = ''
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                git_remote = result.stdout.strip()
        except Exception:
            pass

        # Get current branch
        current_branch = ''
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=str(path),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                current_branch = result.stdout.strip()
        except Exception:
            pass

        # Create workspace
        workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name=name or path.name,
            root_path=str(path),
            workspace_type='local',
            git_remote_url=git_remote,
            current_branch=current_branch,
            is_active=set_active,
            protected_paths=['.env', '.env.local', 'secrets/', 'credentials/'],
        )

        # Scan project structure
        self.scanner.scan_workspace(workspace)

        logger.info(f"✅ Registered workspace: {workspace.name} at {workspace.root_path}")

        return workspace

    def get_active_workspace(self) -> Optional[ProjectWorkspace]:
        """
        Get the user's currently active workspace.

        Session 855: For system_autonomous user, creates a default workspace
        if none exists (for autonomous agent operations).

        Session 858: For ANY user without a workspace, creates a personal workspace.
        This ensures agents can always write files without "No active workspace" errors.

        Session 907: Order by total_operations DESC to prefer the established/primary
        workspace when multiple are active. This ensures consistent workspace selection.
        """
        workspace = ProjectWorkspace.objects.filter(
            user=self.user,
            is_active=True
        ).order_by('-total_operations', '-created_at').first()

        # Session 1085: Superusers can see any active workspace
        if not workspace and self.user.is_superuser:
            workspace = ProjectWorkspace.objects.filter(
                is_active=True
            ).order_by('-total_operations', '-created_at').first()

        # Session 855: Create default workspace for system user if needed
        if not workspace and self.user.username == 'system_autonomous':
            workspace = self._ensure_system_workspace()

        # Session 858: Create personal workspace for any user without one
        if not workspace and self.user:
            workspace = self._ensure_personal_workspace()

        return workspace

    def _ensure_system_workspace(self) -> Optional[ProjectWorkspace]:
        """
        Session 855: Create or get default workspace for autonomous operations.

        Returns:
            ProjectWorkspace for system operations, or None if creation fails
        """
        try:
            # Check if system workspace already exists
            workspace = ProjectWorkspace.objects.filter(
                user=self.user,
                name='System Autonomous Workspace'
            ).first()

            if workspace:
                workspace.is_active = True
                workspace.save(update_fields=['is_active'])
                return workspace

            # Create system workspace pointing to the project root
            import os
            from pathlib import Path

            # Use the Django project root as the workspace
            project_root = Path(__file__).parent.parent.parent  # core/services -> core -> project root
            output_dir = project_root / 'generated_content'

            # Create output directory if it doesn't exist
            output_dir.mkdir(parents=True, exist_ok=True)

            workspace = ProjectWorkspace.objects.create(
                user=self.user,
                name='System Autonomous Workspace',
                root_path=str(output_dir),
                workspace_type='local',
                is_active=True,
                allow_file_write=True,
                protected_paths=['.env', '.env.local', 'secrets/', 'credentials/'],
            )

            logger.info(f"🤖 Created system autonomous workspace at {output_dir}")
            return workspace

        except Exception as e:
            logger.warning(f"Could not ensure system workspace: {e}")
            return None

    def _ensure_personal_workspace(self) -> Optional[ProjectWorkspace]:
        """
        Session 858: Create or get default personal workspace for a user.

        Every user gets a personal workspace in generated_content/users/{username}/
        This ensures agents can always write files without "No active workspace" errors.

        Returns:
            ProjectWorkspace for user operations, or None if creation fails
        """
        try:
            workspace_name = f'{self.user.username}-personal'

            # Check if personal workspace already exists
            workspace = ProjectWorkspace.objects.filter(
                user=self.user,
                name=workspace_name
            ).first()

            if workspace:
                workspace.is_active = True
                workspace.save(update_fields=['is_active'])
                logger.debug(f"👤 Reactivated personal workspace for {self.user.username}")
                return workspace

            # Create personal workspace
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent  # core/services -> core -> project root
            user_dir = project_root / 'generated_content' / 'users' / self.user.username

            # Create user directory if it doesn't exist
            user_dir.mkdir(parents=True, exist_ok=True)

            workspace = ProjectWorkspace.objects.create(
                user=self.user,
                name=workspace_name,
                root_path=str(user_dir),
                workspace_type='local',
                is_active=True,
                allow_file_write=True,
                allow_file_delete=False,  # Safe default
                allow_git_operations=False,
                description=f'Personal workspace for {self.user.username}',
                protected_paths=['.env', '.env.local', 'secrets/', 'credentials/'],
            )

            logger.info(f"👤 [Session 858] Created personal workspace for {self.user.username} at {user_dir}")
            return workspace

        except Exception as e:
            logger.warning(f"Could not create personal workspace for {self.user.username}: {e}")
            return None

    def get_codebase_workspace(self) -> Optional[ProjectWorkspace]:
        """
        Session 884: Get the codebase workspace for code maintenance operations.

        The codebase workspace points to the actual project source code, allowing
        CodeGeneratorAgent and CodeReviewAgent to read and modify the real codebase.

        This is different from sandbox workspaces (generated_content/) which are
        for agent-generated content.

        Returns:
            ProjectWorkspace pointing to the codebase, or None if not configured
        """
        # Look for codebase workspace (created by setup_codebase_workspace command)
        codebase_workspace = ProjectWorkspace.objects.filter(
            workspace_type='codebase',
            is_active=True
        ).first()

        if codebase_workspace:
            logger.debug(f"📂 Found codebase workspace: {codebase_workspace.name} at {codebase_workspace.root_path}")
            return codebase_workspace

        # Fallback: Look by name pattern
        codebase_workspace = ProjectWorkspace.objects.filter(
            name__icontains='codebase',
            is_active=True
        ).first()

        if codebase_workspace:
            logger.debug(f"📂 Found codebase workspace by name: {codebase_workspace.name}")
            return codebase_workspace

        logger.debug("📂 No codebase workspace found. Run 'python manage.py setup_codebase_workspace' to create one.")
        return None

    def set_active_workspace(self, workspace_id: UUID) -> ProjectWorkspace:
        """Set a workspace as the active target for operations.

        Superusers can activate any workspace; regular users can only
        activate their own workspaces.
        """
        if self.user.is_superuser:
            workspace = ProjectWorkspace.objects.get(id=workspace_id)
        else:
            workspace = ProjectWorkspace.objects.get(id=workspace_id, user=self.user)
        workspace.is_active = True
        workspace.save()  # This triggers deactivation of others via save()

        logger.info(f"🎯 Active workspace: {workspace.name} (by {self.user.username})")
        return workspace

    def list_workspaces(self) -> List[ProjectWorkspace]:
        """List all workspaces for the user. Superusers see all."""
        if self.user.is_superuser:
            return list(ProjectWorkspace.objects.all())
        return list(ProjectWorkspace.objects.filter(user=self.user))

    def rescan_workspace(self, workspace: ProjectWorkspace) -> WorkspaceContext:
        """Rescan a workspace to update its context."""
        return self.scanner.scan_workspace(workspace)

    # ==================== Agent Interface ====================

    def execute_agent_output(
        self,
        workspace: ProjectWorkspace,
        agent_name: str,
        agent_result: Dict[str, Any],
        agent_task: str = "",
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Take an agent's output and apply it to the workspace.
        This is the KEY BRIDGE between agents and file system.

        Args:
            workspace: Target workspace
            agent_name: Which agent produced this output
            agent_result: The agent's return value with 'files' or 'code'
            agent_task: Description of what the agent was doing
            auto_apply: If True, write immediately. If False, queue for review.

        Returns:
            Execution result with operations performed
        """
        if not workspace.allow_file_write:
            return {
                'success': False,
                'error': 'File writing not allowed on this workspace',
                'operations': []
            }

        operations = []

        # Extract files from agent result
        files_to_write = self._extract_files_from_result(agent_result)

        if not files_to_write:
            return {
                'success': True,
                'message': 'No files to write',
                'operations': []
            }

        for file_info in files_to_write:
            # Determine target path using workspace context
            target_path = self._resolve_file_path(workspace, file_info)

            # Check if path is protected
            if self._is_protected_path(workspace, target_path):
                operations.append({
                    'file': target_path,
                    'status': 'blocked',
                    'reason': 'Path is protected',
                    'success': False
                })
                continue

            if auto_apply or not workspace.require_human_review:
                # Write immediately
                operation = self.file_writer.write_file(
                    workspace=workspace,
                    file_path=target_path,
                    content=file_info['content'],
                    agent_name=agent_name,
                    agent_task=agent_task
                )
                operations.append({
                    'file': target_path,
                    'status': 'written' if operation.success else 'failed',
                    'operation_id': str(operation.id),
                    'success': operation.success,
                    'error': operation.error_message if not operation.success else None,
                    'lines': len(file_info['content'].split('\n'))
                })
            else:
                # Queue for human review
                operation = WorkspaceOperation.objects.create(
                    workspace=workspace,
                    user=workspace.user,
                    agent_name=agent_name,
                    agent_task=agent_task,
                    operation_type='file_create' if not (Path(workspace.root_path) / target_path).exists() else 'file_modify',
                    file_path=target_path,
                    file_content_after=file_info['content'],
                    success=False,  # Not applied yet
                    requires_review=True,
                    can_rollback=True,
                )
                operations.append({
                    'file': target_path,
                    'status': 'pending_review',
                    'operation_id': str(operation.id),
                    'success': True,
                    'lines': len(file_info['content'].split('\n'))
                })

        return {
            'success': all(op.get('success', False) for op in operations),
            'operations': operations,
            'workspace': workspace.name,
            'agent': agent_name,
            'files_processed': len(operations),
            'files_written': len([op for op in operations if op.get('status') == 'written']),
            'files_pending': len([op for op in operations if op.get('status') == 'pending_review']),
            'files_blocked': len([op for op in operations if op.get('status') == 'blocked']),
        }

    def get_workspace_context_for_agent(
        self,
        workspace: ProjectWorkspace,
        agent_name: str,
        task: str
    ) -> Dict[str, Any]:
        """
        Get relevant workspace context for an agent to use.
        Agents call this to understand WHERE to put their output.

        Args:
            workspace: The workspace
            agent_name: Which agent is asking
            task: What the agent is trying to do

        Returns:
            Context dict with project structure info
        """
        try:
            context = workspace.context
        except WorkspaceContext.DoesNotExist:
            # Scan if no context exists
            context = self.scanner.scan_workspace(workspace)

        return {
            'workspace_name': workspace.name,
            'root_path': workspace.root_path,
            'tech_stack': workspace.tech_stack,
            'key_files': context.key_files,
            'file_tree': context.file_tree,
            'coding_patterns': context.coding_patterns,
            'dependencies': context.dependencies,
            'import_aliases': context.import_aliases,
            'directory_purposes': context.directory_purposes,
            'protected_paths': workspace.protected_paths,
            'total_files': context.total_files,
        }

    # ==================== File Operations ====================

    def read_file(self, workspace: ProjectWorkspace, file_path: str) -> Optional[str]:
        """Read a file from the workspace."""
        # Session 918: Sanitize file path to prevent absolute path issues
        file_path = self.file_writer._sanitize_file_path(file_path)
        full_path = Path(workspace.root_path) / file_path
        if full_path.exists():
            try:
                return full_path.read_text(encoding='utf-8')
            except Exception as e:
                logger.error(f"Failed to read {file_path}: {e}")
        return None

    def write_file(
        self,
        workspace: ProjectWorkspace,
        file_path: str,
        content: str,
        agent_name: str,
        agent_task: str = ""
    ) -> WorkspaceOperation:
        """Write a file to the workspace with audit logging."""
        if self._is_protected_path(workspace, file_path):
            return self.file_writer._create_failed_operation(
                workspace, agent_name, agent_task, 'file_create',
                file_path, "Path is protected"
            )
        return self.file_writer.write_file(
            workspace, file_path, content, agent_name, agent_task
        )

    def delete_file(
        self,
        workspace: ProjectWorkspace,
        file_path: str,
        agent_name: str
    ) -> WorkspaceOperation:
        """Delete a file from the workspace."""
        if self._is_protected_path(workspace, file_path):
            return self.file_writer._create_failed_operation(
                workspace, agent_name, '', 'file_delete',
                file_path, "Path is protected"
            )
        return self.file_writer.delete_file(workspace, file_path, agent_name)

    def list_files(
        self,
        workspace: ProjectWorkspace,
        pattern: str = "**/*"
    ) -> List[str]:
        """List files in the workspace matching a pattern."""
        root = Path(workspace.root_path)
        files = []
        for p in root.glob(pattern):
            if p.is_file():
                rel = str(p.relative_to(root))
                # Skip common ignore patterns
                if not any(skip in rel for skip in ['node_modules', '__pycache__', '.git']):
                    files.append(rel)
        return files[:1000]  # Limit to 1000 files

    # ==================== Git Operations ====================

    def git_status(self, workspace: ProjectWorkspace) -> Dict[str, Any]:
        """Get git status of the workspace."""
        return self.git_integrator.status(workspace)

    def git_commit(
        self,
        workspace: ProjectWorkspace,
        message: str,
        agent_name: str
    ) -> WorkspaceOperation:
        """Create a git commit."""
        return self.git_integrator.commit(workspace, message, agent_name)

    def git_create_branch(
        self,
        workspace: ProjectWorkspace,
        branch_name: str
    ) -> WorkspaceOperation:
        """Create a new branch for agent work."""
        return self.git_integrator.create_branch(workspace, branch_name)

    # ==================== Review Operations ====================

    def get_pending_reviews(self, workspace: ProjectWorkspace = None) -> List[WorkspaceOperation]:
        """Get operations pending human review."""
        qs = WorkspaceOperation.objects.filter(
            user=self.user,
            requires_review=True,
            reviewed_by_human=False
        )
        if workspace:
            qs = qs.filter(workspace=workspace)
        return list(qs.order_by('-created_at'))

    def approve_operation(
        self,
        operation: WorkspaceOperation,
        feedback: str = ""
    ) -> WorkspaceOperation:
        """
        Approve a pending operation.

        Note: The file is already written to disk when the operation was created.
        This method just marks the operation as reviewed/approved.
        We do NOT call write_file again as that would create a duplicate
        pending operation in an infinite loop.
        """
        if not operation.requires_review:
            raise ValueError("Operation does not require review")

        if operation.reviewed_by_human:
            raise ValueError("Operation already reviewed")

        # Session 780 Fix: File is already written to disk when operation was created.
        # We just mark it as approved - do NOT call write_file again or it creates
        # a new pending operation in an infinite loop.

        operation.reviewed_by_human = True
        operation.human_approved = True
        operation.human_feedback = feedback
        operation.reviewed_at = timezone.now()
        operation.save()

        logger.info(f"✅ Approved operation: {operation.file_path}")
        return operation

    def reject_operation(
        self,
        operation: WorkspaceOperation,
        feedback: str = ""
    ) -> WorkspaceOperation:
        """Reject a pending operation."""
        operation.reviewed_by_human = True
        operation.human_approved = False
        operation.human_feedback = feedback
        operation.reviewed_at = timezone.now()
        operation.can_rollback = False
        operation.save()

        logger.info(f"❌ Rejected operation: {operation.file_path}")
        return operation

    def rollback_operation(self, operation: WorkspaceOperation) -> WorkspaceOperation:
        """Rollback an operation."""
        return self.file_writer.rollback_operation(operation)

    # ==================== History ====================

    def get_operation_history(
        self,
        workspace: ProjectWorkspace = None,
        limit: int = 50
    ) -> List[WorkspaceOperation]:
        """Get operation history."""
        qs = WorkspaceOperation.objects.filter(user=self.user)
        if workspace:
            qs = qs.filter(workspace=workspace)
        return list(qs.order_by('-created_at')[:limit])

    def get_file_history(
        self,
        workspace: ProjectWorkspace,
        file_path: str
    ) -> List[WorkspaceOperation]:
        """Get history of operations on a specific file."""
        return list(WorkspaceOperation.objects.filter(
            workspace=workspace,
            file_path=file_path
        ).order_by('-created_at'))

    # ==================== Internal Methods ====================

    def _extract_files_from_result(self, agent_result: Dict) -> List[Dict]:
        """Extract file information from an agent's result."""
        files = []

        # Handle 'files' key (list of file dicts)
        if 'files' in agent_result:
            for f in agent_result['files']:
                if isinstance(f, dict):
                    files.append({
                        'filename': f.get('filename', f.get('path', 'unknown')),
                        'content': f.get('content', f.get('code', '')),
                        'language': f.get('language', 'auto')
                    })

        # Handle 'code' key with file parsing
        elif 'code' in agent_result and isinstance(agent_result['code'], str):
            # Try to parse multiple files from code block
            code = agent_result['code']
            parsed_files = self._parse_files_from_code(code)
            if parsed_files:
                files.extend(parsed_files)
            else:
                # Single code block
                files.append({
                    'filename': agent_result.get('filename', 'generated_code'),
                    'content': code,
                    'language': 'auto'
                })

        # Handle 'data' -> 'results' pattern from some agents
        elif 'data' in agent_result:
            data = agent_result['data']
            if isinstance(data, dict) and 'results' in data:
                for result in data['results']:
                    if isinstance(result, dict) and 'data' in result:
                        inner = result['data']
                        if isinstance(inner, dict) and 'files' in inner:
                            files.extend(inner['files'])

        return files

    def _parse_files_from_code(self, code: str) -> List[Dict]:
        """Parse multiple files from a code string with ### markers."""
        import re
        files = []

        # Pattern: ### path/to/file.ext
        pattern = r'###\s+([^\n]+)\n```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, code, re.DOTALL)

        for filename, language, content in matches:
            files.append({
                'filename': filename.strip(),
                'language': language or 'auto',
                'content': content.strip()
            })

        return files

    def _resolve_file_path(self, workspace: ProjectWorkspace, file_info: Dict) -> str:
        """
        Intelligently determine where a file should go based on:
        - Filename/extension
        - Workspace structure
        - Existing patterns
        """
        filename = file_info['filename']

        # If it's already a path, use it
        if '/' in filename:
            return filename

        try:
            context = workspace.context
        except WorkspaceContext.DoesNotExist:
            return filename

        # Use context to find the right directory
        ext = Path(filename).suffix.lower()
        suggested_dir = context.get_directory_for_file_type(ext)

        if suggested_dir and suggested_dir != '.':
            return f"{suggested_dir}/{filename}"

        return filename

    def _is_protected_path(self, workspace: ProjectWorkspace, file_path: str) -> bool:
        """Check if a path is protected."""
        for protected in workspace.protected_paths:
            if file_path.startswith(protected) or file_path == protected:
                return True
            # Also check if the protected pattern appears anywhere
            if protected.endswith('/'):
                if protected.rstrip('/') in file_path:
                    return True
        return False


# ==================== Singleton Instance ====================

_workspace_manager_instances: Dict[int, WorkspaceManager] = {}


def get_workspace_manager(user: User) -> WorkspaceManager:
    """Get or create a WorkspaceManager for a user."""
    # Session 800: Handle None user (system/scheduled tasks have no user context)
    if user is None:
        # Return a manager with no workspaces for system tasks
        if 0 not in _workspace_manager_instances:
            # Create a dummy manager - will have no active workspace
            from django.contrib.auth import get_user_model
            User = get_user_model()
            system_user = User.objects.filter(is_superuser=True).first()
            if system_user:
                _workspace_manager_instances[0] = WorkspaceManager(system_user)
            else:
                # No superuser exists, raise a more helpful error
                raise ValueError("No user provided and no superuser exists for system workspace")
        return _workspace_manager_instances[0]

    user_id = user.id
    if user_id not in _workspace_manager_instances:
        _workspace_manager_instances[user_id] = WorkspaceManager(user)
    return _workspace_manager_instances[user_id]
