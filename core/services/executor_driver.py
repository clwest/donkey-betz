"""
Session 1074/1075: Executor Driver — per-run ephemeral execution.

Clones the repo, creates a working branch, runs PlanV1 steps, captures artifacts.
Supports shell and apply_patch step types with step-level approval gating.

MVP uses subprocess. Docker can replace this later without API changes.

See: docs/decisions/ADR-0001-execution-per-run-ephemeral-containers.md
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from django.conf import settings

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
            # Only call start() on first execution (not resume)
            if self.run.status != 'running':
                self.run.start()
            self._log(f'Starting execution run {self.run.id}')
            self._post_status(
                'Executor run started',
                f'{self.run.plan_summary}\n\nSteps: {self.run.steps_total}',
            )

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

        except ExecutorAwaitingApproval:
            # Not a failure — run is paused, awaiting human approval.
            self._log(f'Paused for approval at step: {self.run.awaiting_approval_step_id}')
            self.run.log_text = '\n'.join(self.log_lines)
            self.run.save(update_fields=['log_text'])
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
        """Execute PlanV1 steps with step-level approval gating."""
        plan = self.run.plan_json or {}
        steps = plan.get('steps', [])
        self.run.steps_total = len(steps)
        self.run.save(update_fields=['steps_total'])

        start_time = time.time()
        start_index = self.run.current_step_index or 0
        approved_steps = set(self.run.approved_steps or [])
        classifier_enabled = getattr(settings, 'EXECUTOR_CLASSIFIER_GATING_ENABLED', False)

        for i in range(start_index, len(steps)):
            step = steps[i]
            step_id = step.get('id', f's{i}')
            step_type = step.get('type', 'shell')
            desc = f"Step {step_id} ({step_type})"

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                raise ExecutorTimeout(
                    f'Run exceeded {self.timeout}s timeout at step {step_id}'
                )

            # ── Approval gating (precedence: explicit > network:on > classifier) ──
            needs_approval = self._step_needs_approval(
                step, step_id, approved_steps, classifier_enabled
            )
            if needs_approval:
                self.run.current_step_index = i
                self.run.current_step = desc
                self.run.save(update_fields=['current_step_index', 'current_step'])
                self.run.request_approval(step_id=step_id)
                self._post_status(
                    'Executor run needs approval',
                    f'Paused at {desc}.\n\nReason: {needs_approval}',
                )
                raise ExecutorAwaitingApproval(
                    f'{desc} requires approval: {needs_approval}'
                )

            # ── Execute step ──
            self._log(f'[Step {i + 1}/{len(steps)}] {desc}')
            self.run.current_step = desc
            self.run.steps_completed = i
            self.run.current_step_index = i
            self.run.save(update_fields=['current_step', 'steps_completed', 'current_step_index'])

            remaining = self.timeout - (time.time() - start_time)

            if step_type == 'shell':
                self._execute_shell_step(step, remaining)
            elif step_type == 'apply_patch':
                self._execute_patch_step(step)
            else:
                raise ExecutorBlocked(f'Unknown step type: {step_type!r}')

            self._log(f'  OK')

        self.run.steps_completed = len(steps)
        self.run.current_step_index = len(steps)
        self.run.save(update_fields=['steps_completed', 'current_step_index'])

    def _step_needs_approval(
        self,
        step: dict,
        step_id: str,
        approved_steps: set[str],
        classifier_enabled: bool,
    ) -> str:
        """Check if a step needs approval. Returns reason string or empty string."""
        # Already approved — skip all checks
        if step_id in approved_steps:
            return ''

        # 1) Explicit requires_approval flag (highest precedence)
        if step.get('requires_approval'):
            return 'Step has requires_approval=true'

        # 2) network:on auto-requires approval
        if step.get('network') == 'on':
            return 'Step has network=on (network egress requires approval)'

        # 3) Classifier-based Tier B gating (only if enabled)
        if classifier_enabled and step.get('type') == 'shell':
            from core.services.executor_policy import classify_command
            cmd = step.get('cmd', '')
            policy = classify_command(cmd)
            if policy.tier == 'C':
                raise ExecutorBlocked(
                    f'Step {step_id} blocked by policy: {cmd!r} — {policy.reason}'
                )
            if policy.tier == 'B':
                return f'Classifier Tier B: {policy.reason}'

        return ''

    # ── Step executors ───────────────────────────────────────────────────

    def _execute_shell_step(self, step: dict, remaining: float) -> None:
        """Execute a shell step."""
        cmd = step.get('cmd', '')
        cwd = step.get('cwd', '.')

        # Resolve cwd relative to workdir
        if self.workdir and cwd != '.':
            effective_cwd = str(self.workdir / cwd)
        else:
            effective_cwd = str(self.workdir) if self.workdir else None

        self._log(f'  $ {cmd}')
        result = self._shell(
            cmd,
            cwd=effective_cwd,
            timeout=int(max(remaining, 10)),
        )
        if result.returncode != 0:
            error_msg = f'Shell step failed (exit {result.returncode}): {cmd}'
            self._log(f'  FAILED: exit {result.returncode}')
            raise RuntimeError(error_msg)

    def _execute_patch_step(self, step: dict) -> None:
        """Execute an apply_patch step."""
        patch_text = step.get('patch', '')
        self._log(f'  Applying patch ({len(patch_text)} bytes)')

        if not self.workdir:
            raise RuntimeError('No workspace available for apply_patch')

        # Write patch to temp file and apply
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.patch', dir=str(self.workdir), delete=False
        ) as f:
            f.write(patch_text)
            patch_path = f.name

        try:
            result = self._shell(
                f'git apply --verbose {patch_path}',
                cwd=str(self.workdir),
            )
            if result.returncode != 0:
                self._log(f'  FAILED: git apply exit {result.returncode}')
                raise RuntimeError(f'Patch apply failed (exit {result.returncode})')
        finally:
            try:
                os.unlink(patch_path)
            except OSError:
                pass

    # ── Artifact capture ─────────────────────────────────────────────────

    def _capture_artifacts(self) -> None:
        """Capture diff and changed files after execution."""
        self._log('Capturing artifacts...')

    def _get_diff(self) -> str:
        if not self.workdir:
            return ''
        try:
            result = self._shell('git diff HEAD', cwd=str(self.workdir))
            return result.stdout[:500_000]
        except Exception as _e:
            logger.warning(
                "executor_driver._get_diff: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
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
        except Exception as _e:
            logger.warning(
                "executor_driver._get_changed_files: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
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


class ExecutorAwaitingApproval(Exception):
    """Raised when a step needs approval — NOT a failure."""
    pass
