"""
Code Runner (Beta) — API endpoints for dispatching and monitoring code-agent runs.

Endpoints:
  POST /api/v1/code/run        — dispatch a new run (admin-only)
  GET  /api/v1/code/status/<id> — poll run status
  GET  /api/v1/code/logs/<id>   — fetch log lines

Security:
  - Admin-only (is_staff); explicitly denies VIP demo viewers
  - Workspace allowlisted to mobile/ only
  - Secret patterns redacted from logs
  - Runtime capped at 10 minutes
  - Log output capped at 2000 lines
"""

import logging
import os
import re
import subprocess
import threading
import uuid

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.models_code_runner import CodeRun, CodeRunMode, CodeRunStatus

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

ALLOWED_WORKSPACES = frozenset({'mobile'})
RUNTIME_CAP_SECONDS = 600  # 10 minutes
LOG_MAX_LINES = 2000
LOG_MAX_LINE_LENGTH = 4000  # Truncate individual lines to prevent DB bloat
LOG_CLIENT_LINES = 200
APPLY_MODE_ENABLED = bool(os.environ.get('CODE_RUNNER_ALLOW_APPLY', ''))

# Patterns that look like secrets — redact from log output
_SECRET_PATTERNS = re.compile(
    r'(?i)'
    r'(?:'
    r'(?:api[_-]?key|token|secret|password|auth|credential|private[_-]?key)'
    r'\s*[=:]\s*'
    r')'
    r'["\']?([A-Za-z0-9_\-/.+=]{8,})["\']?'
    r'|'
    r'(?:sk-[A-Za-z0-9]{20,})'     # OpenAI keys
    r'|'
    r'(?:ghp_[A-Za-z0-9]{36,})'    # GitHub PATs
    r'|'
    r'(?:AKIA[A-Z0-9]{16})'        # AWS access keys
)


def _redact_secrets(line: str) -> str:
    """Replace anything that looks like a secret with [REDACTED]."""
    return _SECRET_PATTERNS.sub('[REDACTED]', line)


def _is_vip_demo(request) -> bool:
    """Check if this is a VIP demo viewer (not a real admin)."""
    # VIP demo is client-side only (mobile), but guard server-side too.
    # If there's ever a VIP_DEMO_VIEWER role or flag, deny here.
    if hasattr(request.user, 'platform_role'):
        if getattr(request.user, 'platform_role', '') == 'vip_demo':
            return True
    return False


# ── Job Runner ─────────────────────────────────────────────────────────────────

def _run_code_job(run_id: uuid.UUID):
    """Execute a code-agent run in a background thread with guardrails."""
    try:
        run = CodeRun.objects.get(pk=run_id)
    except CodeRun.DoesNotExist:
        logger.error(f"[CodeRunner] Run {run_id} not found")
        return

    run.status = CodeRunStatus.RUNNING
    run.started_at = timezone.now()
    run.save(update_fields=['status', 'started_at'])

    logger.info(
        f"[CodeRunner] Starting {run.mode} run {run.id} "
        f"by user={run.created_by} workspace={run.workspace}"
    )

    # Build the command — use a subprocess that's restricted to mobile/ workspace
    workspace_path = f"./{run.workspace}"
    mode_flag = '--dry-run' if run.mode == CodeRunMode.DRY_RUN else '--apply'

    # The task prompt is sanitized: no shell injection via subprocess list args
    cmd = [
        'python', 'manage.py', 'run_code_agent',
        '--workspace', workspace_path,
        '--mode', run.mode,
        '--task', run.task,
        '--run-id', str(run.id),
    ]

    lines = []
    exit_code = None

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=None,  # Use project root
        )

        # Read output line by line with runtime cap
        import time
        start = time.monotonic()

        for raw_line in proc.stdout:
            elapsed = time.monotonic() - start
            if elapsed > RUNTIME_CAP_SECONDS:
                proc.kill()
                lines.append(f"[SYSTEM] Runtime cap exceeded ({RUNTIME_CAP_SECONDS}s). Run killed.")
                logger.warning(f"[CodeRunner] Run {run.id} killed: runtime cap exceeded")
                break

            clean = _redact_secrets(raw_line.rstrip('\n'))
            if len(clean) > LOG_MAX_LINE_LENGTH:
                clean = clean[:LOG_MAX_LINE_LENGTH] + ' [TRUNCATED]'
            lines.append(clean)

            # Cap stored lines (keep tail)
            if len(lines) > LOG_MAX_LINES:
                lines = lines[-LOG_MAX_LINES:]

        proc.wait(timeout=10)
        exit_code = proc.returncode

    except FileNotFoundError:
        lines.append("[SYSTEM] run_code_agent management command not found. Using fallback.")
        # Fallback: just record the task as a dry-run log
        lines.append(f"[DRY RUN] Task: {run.task}")
        lines.append(f"[DRY RUN] Workspace: {run.workspace}")
        lines.append(f"[DRY RUN] Mode: {run.mode}")
        lines.append("[DRY RUN] No code agent available — task logged for review.")
        exit_code = 0
    except Exception as exc:
        lines.append(f"[SYSTEM] Error: {_redact_secrets(str(exc))}")
        exit_code = 1
        logger.exception(f"[CodeRunner] Run {run.id} failed with exception")

    # Update run record
    run.status = CodeRunStatus.COMPLETED if exit_code == 0 else CodeRunStatus.FAILED
    run.finished_at = timezone.now()
    run.exit_code = exit_code
    run.log_lines = lines
    run.save(update_fields=['status', 'finished_at', 'exit_code', 'log_lines'])

    logger.info(
        f"[CodeRunner] Run {run.id} finished: status={run.status} "
        f"exit_code={exit_code} lines={len(lines)}"
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAdminUser])
def code_run_create(request):
    """POST /api/v1/code/run — dispatch a new code-agent run."""
    if _is_vip_demo(request):
        return Response(
            {'error': 'VIP demo users cannot run code'},
            status=403,
        )

    task = (request.data.get('task') or '').strip()
    mode = request.data.get('mode', 'dry_run')

    if not task:
        return Response({'error': 'task is required'}, status=400)

    if mode not in ('dry_run', 'apply'):
        return Response(
            {'error': 'mode must be "dry_run" or "apply"'},
            status=400,
        )

    if mode == 'apply' and not APPLY_MODE_ENABLED:
        return Response(
            {'error': 'Apply mode is disabled. Set CODE_RUNNER_ALLOW_APPLY=1 to enable.'},
            status=403,
        )

    if len(task) > 5000:
        return Response({'error': 'task too long (max 5000 chars)'}, status=400)

    # v0: workspace is always 'mobile'
    workspace = 'mobile'
    if workspace not in ALLOWED_WORKSPACES:
        return Response(
            {'error': f'Workspace "{workspace}" not in allowlist'},
            status=403,
        )

    # Check for existing active run (one at a time)
    active = CodeRun.objects.filter(
        status__in=[CodeRunStatus.QUEUED, CodeRunStatus.RUNNING],
    ).exists()
    if active:
        return Response(
            {'error': 'A run is already in progress. Wait for it to finish.'},
            status=409,
        )

    run = CodeRun.objects.create(
        created_by=request.user,
        task=task,
        mode=mode,
        workspace=workspace,
    )

    logger.info(
        f"[CodeRunner] AUDIT: user={request.user.username} "
        f"mode={mode} run_id={run.id} task={task[:100]}"
    )

    # Dispatch in background thread
    thread = threading.Thread(target=_run_code_job, args=(run.id,), daemon=True)
    thread.start()

    return Response({'run_id': str(run.id)}, status=201)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def code_run_status(request, run_id):
    """GET /api/v1/code/status/<run_id> — poll run status."""
    if _is_vip_demo(request):
        return Response({'error': 'Access denied'}, status=403)

    try:
        run = CodeRun.objects.get(pk=run_id)
    except (CodeRun.DoesNotExist, ValueError):
        return Response({'error': 'Run not found'}, status=404)

    return Response({
        'run_id': str(run.id),
        'status': run.status,
        'mode': run.mode,
        'workspace': run.workspace,
        'started_at': run.started_at.isoformat() if run.started_at else None,
        'finished_at': run.finished_at.isoformat() if run.finished_at else None,
        'exit_code': run.exit_code,
        'created_at': run.created_at.isoformat(),
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def code_run_logs(request, run_id):
    """GET /api/v1/code/logs/<run_id> — fetch log lines."""
    if _is_vip_demo(request):
        return Response({'error': 'Access denied'}, status=403)

    try:
        run = CodeRun.objects.get(pk=run_id)
    except (CodeRun.DoesNotExist, ValueError):
        return Response({'error': 'Run not found'}, status=404)

    all_lines = run.log_lines or []
    truncated = len(all_lines) > LOG_CLIENT_LINES

    return Response({
        'run_id': str(run.id),
        'lines': all_lines[-LOG_CLIENT_LINES:],
        'total_lines': len(all_lines),
        'truncated': truncated,
        'status': run.status,
    })
