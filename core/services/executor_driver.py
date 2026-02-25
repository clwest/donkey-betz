"""
Session 1074: Executor Driver — per-run ephemeral execution.

Clones the repo, creates a working branch, runs plan steps, captures artifacts.
MVP uses subprocess. Docker can replace this later without API changes.

See: docs/decisions/ADR-0001-execution-per-run-ephemeral-containers.md
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

from django.conf import settings

from core.services.executor_policy import classify_command

logger = logging.getLogger(__name__)


class ExecutorDriver:
    """Per-run ephemeral executor using subprocess."""

    def __init__(self, run) -> None:
        self.run = run
        self.workdir: Path | None = None
        self.log_lines: list[str] = []
        self.timeout = settings.EXECUTOR_MAX_RUN_SECONDS

    def execute(self) -> None:
        """Full execution lifecycle: setup, run steps, capture artifacts, cleanup."""
        try:
            self.run.start()
            self._log(f'Starting execution run {self.run.id}')
            self._post_status('Executor run started', f'{self.run.plan_summary}\n\nSteps: {self.run.steps_total}')

            self._setup_workspace()
            self._create_working_branch()
            self._run_plan_steps()
            self._capture_artifacts()

            self._log('Execution completed successfully')
            diff = self._get_diff()
            changed = self._get_changed_files()
            self.run.succeed(
                diff=diff,
                changed=changed,
                log='\n'.join(self.log_lines),
            )

        except ExecutorTimeout as e:
            self._log(f'TIMEOUT: {e}')
            self.run.fail(error=str(e), log='\n'.join(self.log_lines))
        except ExecutorBlocked as e:
            self._log(f'BLOCKED: {e}')
            self.run.fail(error=str(e), log='\n'.join(self.log_lines))
        except Exception as e:
            self._log(f'ERROR: {e}')
            self.run.fail(error=str(e), log='\n'.join(self.log_lines))
        finally:
            self._cleanup()

    # ── Setup ────────────────────────────────────────────────────────────

    def _setup_workspace(self) -> None:
        """Clone or fetch the repo into a temporary workspace."""
        root = Path(settings.EXECUTOR_WORKDIR_ROOT)
        root.mkdir(parents=True, exist_ok=True)
        self.workdir = root / str(self.run.id)

        if self.workdir.exists():
            shutil.rmtree(self.workdir)

        self._log(f'Cloning {self.run.repo_url} (branch: {self.run.base_branch})')
        self._shell(
            f'git clone --depth 50 --branch {self.run.base_branch} '
            f'{self.run.repo_url} {self.workdir}',
            cwd=str(root),
        )

    def _create_working_branch(self) -> None:
        """Create and checkout the working branch."""
        branch = self.run.generate_working_branch()
        self._log(f'Creating working branch: {branch}')
        self._shell(f'git checkout -b {branch}', cwd=str(self.workdir))

    # ── Execution ────────────────────────────────────────────────────────

    def _run_plan_steps(self) -> None:
        """Execute each plan step, enforcing policy."""
        steps = self.run.plan_json or []
        self.run.steps_total = len(steps)
        self.run.save(update_fields=['steps_total'])

        start_time = time.time()

        for i, step in enumerate(steps):
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                raise ExecutorTimeout(
                    f'Run exceeded {self.timeout}s timeout at step {i}'
                )

            cmd = step.get('command', '')
            desc = step.get('description', f'Step {i}')

            # Policy check
            policy = classify_command(cmd)
            if policy.tier == 'C':
                raise ExecutorBlocked(
                    f'Step {i} blocked by policy: {cmd!r} — {policy.reason}'
                )
            if policy.tier == 'B':
                # For MVP: if not pre-approved, block
                if not self.run.approved_at:
                    self.run.approval_required_steps = self.run.approval_required_steps or []
                    if i not in self.run.approval_required_steps:
                        self.run.approval_required_steps.append(i)
                        self.run.save(update_fields=['approval_required_steps'])
                    self.run.request_approval()
                    raise ExecutorBlocked(
                        f'Step {i} requires approval: {cmd!r} — {policy.reason}'
                    )

            self._log(f'[Step {i}/{len(steps)}] {desc}')
            self._log(f'  $ {cmd}')

            self.run.current_step = desc
            self.run.steps_completed = i
            self.run.save(update_fields=['current_step', 'steps_completed'])

            remaining = self.timeout - (time.time() - start_time)
            result = self._shell(
                cmd,
                cwd=str(self.workdir),
                timeout=int(max(remaining, 10)),
            )
            if result.returncode != 0:
                error_msg = f'Step {i} failed (exit {result.returncode}): {cmd}'
                self._log(f'  FAILED: exit {result.returncode}')
                raise RuntimeError(error_msg)

            self._log(f'  OK (exit {result.returncode})')

        self.run.steps_completed = len(steps)
        self.run.save(update_fields=['steps_completed'])

    # ── Artifact capture ─────────────────────────────────────────────────

    def _capture_artifacts(self) -> None:
        """Capture diff and changed files after execution."""
        self._log('Capturing artifacts...')

    def _get_diff(self) -> str:
        if not self.workdir:
            return ''
        try:
            result = self._shell('git diff HEAD', cwd=str(self.workdir))
            return result.stdout[:500_000]  # Cap at 500KB
        except Exception:
            return ''

    def _get_changed_files(self) -> list[str]:
        if not self.workdir:
            return []
        try:
            result = self._shell(
                'git status --porcelain', cwd=str(self.workdir)
            )
            return [
                line[3:].strip()
                for line in result.stdout.splitlines()
                if line.strip()
            ]
        except Exception:
            return []

    # ── Cleanup ──────────────────────────────────────────────────────────

    def _cleanup(self) -> None:
        """Remove the working directory."""
        if self.workdir and self.workdir.exists():
            try:
                shutil.rmtree(self.workdir)
                self._log(f'Cleaned up workspace: {self.workdir}')
            except Exception as e:
                logger.warning(f'Failed to clean up {self.workdir}: {e}')

    # ── Helpers ──────────────────────────────────────────────────────────

    def _shell(
        self,
        cmd: str,
        cwd: str | None = None,
        timeout: int | None = None,
    ) -> subprocess.CompletedProcess:
        """Run a shell command and capture output."""
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout or self.timeout,
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'},
        )
        # Log output
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines()[:50]:
                self._log(f'    {line}')
        if result.stderr.strip():
            for line in result.stderr.strip().splitlines()[:20]:
                self._log(f'    [stderr] {line}')
        return result

    def _log(self, msg: str) -> None:
        self.log_lines.append(msg)
        logger.info(f'[Executor {self.run.id}] {msg}')

    def _post_status(self, title: str, body: str) -> None:
        """Post a STATUS message to the linked conversation."""
        if not self.run.conversation_id or not self.run.created_by:
            return
        try:
            from core.services.collaboration_protocol import post_structured_message
            post_structured_message(
                user=self.run.created_by,
                conversation_id=self.run.conversation_id,
                msg_type='STATUS',
                title=title,
                body=body,
                source='pa',
                metadata={'run_id': str(self.run.id)},
            )
        except Exception:
            logger.exception('[Executor %s] Failed to post status', self.run.id)


# ── Exceptions ────────────────────────────────────────────────────────────────

class ExecutorTimeout(Exception):
    pass


class ExecutorBlocked(Exception):
    pass
